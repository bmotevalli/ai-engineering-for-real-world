"""One local inference worker, exposed only through a permission-restricted Unix socket."""
import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool

from . import ExtractionError, Extractor, ImageInputError
from .http_contract import NO_STORE, ExtractionJob, read_image_body, reject
from .images import prepare_image
from .ollama import OllamaBackend


class Jobs:
    def __init__(self, extractor: Extractor, *, retention_seconds: int = 300):
        self.extractor = extractor
        self.retention_seconds = retention_seconds
        self.records: dict[UUID, tuple[ExtractionJob, float | None]] = {}
        self.busy = False
        self.tasks: set[asyncio.Task] = set()

    def cleanup(self):
        now = time.monotonic()
        for job_id, (_, expires) in list(self.records.items()):
            if expires is not None and expires <= now:
                del self.records[job_id]

    async def run(self, job_id: UUID, image: bytes):
        try:
            result = await run_in_threadpool(self.extractor.extract, image)
            job = ExtractionJob(job_id=job_id, status="succeeded", result=result, error=None)
        except ImageInputError as exc:
            job = ExtractionJob(job_id=job_id, status="failed", result=None,
                                error="invalid_image", error_detail=str(exc)[:500])
        except Exception as exc:
            job = ExtractionJob(job_id=job_id, status="failed", result=None,
                                error="extraction_failed", error_detail=f"{type(exc).__name__}: {exc}"[:500])
        finally:
            image = b""
            self.busy = False
        self.records[job_id] = (job, time.monotonic() + self.retention_seconds)


def create_app(extractor: Extractor | None = None) -> FastAPI:
    jobs = Jobs(extractor or Extractor(OllamaBackend(context_length=8192)))

    async def expire_results():
        while True:
            await asyncio.sleep(10)
            jobs.cleanup()

    @asynccontextmanager
    async def lifespan(app):
        cleanup = asyncio.create_task(expire_results())
        try:
            yield
        finally:
            cleanup.cancel()
            await asyncio.gather(cleanup, return_exceptions=True)
            if jobs.tasks:
                await asyncio.gather(*jobs.tasks, return_exceptions=True)
            jobs.records.clear()

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.jobs = jobs

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/jobs", response_model=ExtractionJob, status_code=202)
    async def submit(request: Request):
        jobs.cleanup()
        if jobs.busy or len(jobs.records) >= 32:
            raise reject(429, "extractor_busy")
        # All state changes run in this single worker's event loop; no await before reservation.
        jobs.busy = True
        try:
            image = await read_image_body(request)
            # Reject corrupt/oversized decoded images before accepting a job.
            image = await run_in_threadpool(prepare_image, image)
        except ImageInputError:
            jobs.busy = False
            raise reject(422, "invalid_image") from None
        except BaseException:
            jobs.busy = False
            raise
        job_id = uuid4()
        job = ExtractionJob(job_id=job_id, status="processing", result=None, error=None)
        jobs.records[job_id] = (job, None)
        task = asyncio.create_task(jobs.run(job_id, image))
        jobs.tasks.add(task)
        task.add_done_callback(jobs.tasks.discard)
        from fastapi.responses import JSONResponse
        return JSONResponse(job.model_dump(mode="json"), status_code=202, headers=NO_STORE)

    @app.get("/jobs/{job_id}", response_model=ExtractionJob)
    async def retrieve(job_id: UUID):
        jobs.cleanup()
        if job_id not in jobs.records:
            raise reject(404, "job_not_found_or_expired")
        from fastapi.responses import JSONResponse
        return JSONResponse(jobs.records[job_id][0].model_dump(mode="json"), headers=NO_STORE)

    return app


def main():
    import uvicorn
    os.umask(0o077)
    socket = Path(os.environ.get("ID_EXTRACTION_SOCKET", "/run/id-extractor/service.sock"))
    socket.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    uvicorn.run(create_app(), uds=str(socket), access_log=False, log_level="warning",
                workers=1, limit_concurrency=8)


if __name__ == "__main__":
    main()
