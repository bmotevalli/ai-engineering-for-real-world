"""Adapter for the repository-local identity extractor."""
import asyncio
import json
import sys
import time
from pathlib import Path

import httpx

from app.core.config import get_settings


class IdExtractionUnavailable(RuntimeError):
    pass


def extract(image: bytes):
    settings = get_settings()
    if not Path(settings.id_extraction_socket).is_socket():
        raise IdExtractionUnavailable("identity extraction worker is unavailable")
    headers = {"X-API-Key": settings.id_extraction_api_key or ""}
    transport = httpx.HTTPTransport(uds=settings.id_extraction_socket)
    try:
        with httpx.Client(transport=transport, base_url="http://id-extractor",
                         timeout=httpx.Timeout(30, read=900)) as client:
            response = client.post("/jobs", content=image, headers={**headers, "Content-Type": "image/png"})
            response.raise_for_status()
            job_id = response.json()["job_id"]
            deadline = time.monotonic() + 900
            while time.monotonic() < deadline:
                response = client.get(f"/jobs/{job_id}", headers=headers)
                response.raise_for_status()
                body = response.json()
                if body.get("status") == "succeeded":
                    source = Path("/opt/id-extractor/src")
                    if str(source) not in sys.path:
                        sys.path.insert(0, str(source))
                    from local_id_extractor.models import ExtractionResult
                    return ExtractionResult.model_validate(body["result"])
                if body.get("status") == "failed":
                    detail = body.get("error_detail") or body.get("error") or "unknown extraction failure"
                    raise IdExtractionUnavailable(str(detail)[:500])
                time.sleep(2)
    except IdExtractionUnavailable:
        raise
    except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
        raise IdExtractionUnavailable("identity extraction worker request failed") from exc
    raise IdExtractionUnavailable("identity extraction timed out")
