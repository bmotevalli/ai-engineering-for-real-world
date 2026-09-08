"""API-key protected webhook submission for local identity extraction."""
import asyncio
import hashlib
import hmac
import ipaddress
import json
import secrets
import socket
import time
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.services import id_extraction

MAX_IMAGE_BYTES = 15 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
CALLBACK_ATTEMPTS = 3


class AcceptedJob(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID
    status: Literal["accepted"] = "accepted"


class CallbackPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID
    status: Literal["succeeded", "failed"]
    result: dict | None = None
    error: Literal["invalid_image", "extraction_failed"] | None = None
    error_detail: str | None = None


@dataclass
class Job:
    callback_url: str
    callback_secret: str
    image: bytes


def require_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    configured = get_settings().id_extraction_api_key
    if not configured or not x_api_key or not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(401, "invalid_api_key", headers={"Cache-Control": "no-store"})


def _forbidden_address(host: str) -> bool:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local \
        or address.is_reserved or address.is_unspecified


async def validate_callback_url(value: str) -> str:
    parsed = urlparse(value)
    settings = get_settings()
    allowed = {host.strip().lower().rstrip(".") for host in settings.id_extraction_callback_hosts}
    host = parsed.hostname.lower().rstrip(".") if parsed.hostname else ""
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.fragment \
            or parsed.query or not host or host not in allowed or _forbidden_address(host):
        raise HTTPException(400, "callback_url_not_allowed")
    try:
        addresses = await run_in_threadpool(socket.getaddrinfo, host, parsed.port or 443, type=socket.SOCK_STREAM)
    except OSError:
        raise HTTPException(400, "callback_url_not_allowed") from None
    if not addresses or any(_forbidden_address(item[4][0]) for item in addresses):
        raise HTTPException(400, "callback_url_not_allowed")
    return value


async def read_upload(file: UploadFile) -> bytes:
    if (file.content_type or "").lower() not in ALLOWED_TYPES:
        raise HTTPException(415, "use_image_jpeg_png_or_webp")
    data = await file.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(422, "empty_image")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "image_too_large")
    return data


class JobStore:
    def __init__(self):
        self.jobs: dict[UUID, Job] = {}
        self.busy = False
        self.tasks: set[asyncio.Task] = set()

    async def process(self, job_id: UUID, job: Job):
        try:
            try:
                result = await run_in_threadpool(id_extraction.extract, job.image)
                payload = CallbackPayload(job_id=job_id, status="succeeded", result=result.model_dump(mode="json"))
            except Exception as exc:
                payload = CallbackPayload(job_id=job_id, status="failed", error="extraction_failed",
                                          error_detail=f"{type(exc).__name__}: {exc}"[:500])
            await deliver_callback(job.callback_url, job.callback_secret, payload)
        finally:
            job.image = b""
            job.callback_secret = ""
            self.jobs.pop(job_id, None)
            self.busy = False


async def deliver_callback(url: str, secret: str, payload: CallbackPayload) -> None:
    body = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    timestamp = str(int(time.time()))
    signature = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
    headers = {"Content-Type": "application/json", "Cache-Control": "no-store",
               "X-ID-Extraction-Job-ID": str(payload.job_id),
               "X-ID-Extraction-Timestamp": timestamp,
               "X-ID-Extraction-Signature": f"sha256={signature}"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15, connect=5), follow_redirects=False, trust_env=False) as client:
            for attempt in range(CALLBACK_ATTEMPTS):
                try:
                    response = await client.post(url, content=body, headers=headers)
                    if 200 <= response.status_code < 300:
                        return
                except httpx.HTTPError:
                    pass
                if attempt + 1 < CALLBACK_ATTEMPTS:
                    await asyncio.sleep(2 ** attempt)
    except httpx.HTTPError:
        pass


store = JobStore()
router = APIRouter(prefix="/id-extraction", tags=["id-extraction"], dependencies=[Depends(require_api_key)])


@router.post("/jobs", response_model=AcceptedJob, status_code=status.HTTP_202_ACCEPTED)
async def submit(
    file: UploadFile = File(...),
    callback_url: str = Form(..., min_length=1, max_length=2048),
    callback_secret: str | None = Form(None, min_length=32, max_length=512),
):
    if store.busy or len(store.jobs) >= 1:
        raise HTTPException(429, "extractor_busy", headers={"Retry-After": "10"})
    callback_url = await validate_callback_url(callback_url)
    image = await read_upload(file)
    store.busy = True
    job_id = uuid4()
    secret = callback_secret or get_settings().id_extraction_api_key or ""
    job = Job(callback_url=callback_url, callback_secret=secret, image=image)
    store.jobs[job_id] = job
    task = asyncio.create_task(store.process(job_id, job))
    store.tasks.add(task)
    task.add_done_callback(store.tasks.discard)
    return AcceptedJob(job_id=job_id)
