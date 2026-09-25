"""Shared HTTP contracts; requires the optional service dependencies."""
import asyncio
from typing import Literal
from uuid import UUID

from fastapi import HTTPException, Request
from pydantic import BaseModel, ConfigDict, model_validator
from starlette.requests import ClientDisconnect

from .images import MAX_BYTES
from .models import ExtractionResult

IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")
NO_STORE = {"Cache-Control": "no-store"}


class ExtractionJob(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID
    status: Literal["processing", "succeeded", "failed"]
    result: ExtractionResult | None
    error: Literal["invalid_image", "extraction_failed"] | None
    error_detail: str | None = None

    @model_validator(mode="after")
    def consistent_state(self):
        if (self.status == "succeeded") != (self.result is not None):
            raise ValueError("result does not match job state")
        if (self.status == "failed") != (self.error is not None):
            raise ValueError("error does not match job state")
        return self


def reject(status: int, detail: str) -> HTTPException:
    headers = dict(NO_STORE)
    if status in (429, 503):
        headers["Retry-After"] = "10"
    return HTTPException(status, detail, headers=headers)


async def read_image_body(request: Request) -> bytes:
    """Bound raw uploads before decoding, without multipart spooling or temp files."""
    if request.query_params:
        raise reject(400, "query_parameters_not_supported")
    if request.headers.get("content-type", "").split(";", 1)[0].lower() not in IMAGE_TYPES:
        raise reject(415, "use_image_jpeg_png_or_webp")
    if request.headers.get("content-encoding", "identity").lower() != "identity":
        raise reject(415, "content_encoding_not_supported")
    lengths = request.headers.getlist("content-length")
    if lengths:
        if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
            raise reject(400, "invalid_content_length")
        if len(lengths[0]) > 10 or int(lengths[0]) > MAX_BYTES:
            raise reject(413, "image_too_large")
    data = bytearray()
    try:
        async with asyncio.timeout(30):
            async for chunk in request.stream():
                if len(data) + len(chunk) > MAX_BYTES:
                    raise reject(413, "image_too_large")
                data.extend(chunk)
    except TimeoutError:
        raise reject(408, "upload_timeout") from None
    except ClientDisconnect:
        raise reject(400, "upload_interrupted") from None
    if not data:
        raise reject(422, "empty_image")
    return bytes(data)
