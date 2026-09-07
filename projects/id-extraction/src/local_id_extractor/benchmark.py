"""Sequential comparisons. Reports deliberately contain sensitive extracted data."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from . import ExtractionError, ExtractionResult, Extractor, ImageInputError
from .images import read_image
from .ollama import ALLOWED_MODELS, DEFAULT_MODEL, OllamaBackend
from .prompts import DEFAULT_PROMPT, PROMPTS


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(min_length=1)
    image: str
    expected: dict[str, str | None] = Field(default_factory=dict)


def compare(result: ExtractionResult, expected: dict[str, str | None]) -> dict:
    actual = result.model_dump()
    return {field: {"match": actual[field]["value"] == value,
                    "expected": value, "confidence": actual[field]["confidence"]}
            for field, value in expected.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare local models/prompts over a private manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--models", nargs="+", choices=ALLOWED_MODELS, default=[DEFAULT_MODEL])
    parser.add_argument("--prompts", nargs="+", choices=PROMPTS, default=[DEFAULT_PROMPT])
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--context", type=int, choices=(4096, 8192), default=4096)
    args = parser.parse_args()
    try:
        raw = json.loads(args.manifest.read_text())
        if not isinstance(raw, list) or not raw or args.repeat < 1:
            raise ValueError()
        cases = [Case.model_validate(item) for item in raw]
        if len({case.id for case in cases}) != len(cases):
            raise ValueError()
        if any(set(case.expected) - set(ExtractionResult.model_fields) for case in cases):
            raise ValueError()
    except (OSError, ValueError):
        parser.error("invalid manifest; use unique IDs, image paths and known expected fields")
    # Refuse overwrite/symlinks and create private report. Caller chooses its directory.
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    failed = False
    with os.fdopen(fd, "w") as report:
        for model in args.models:
            backend = OllamaBackend(model, context_length=args.context)
            for prompt in args.prompts:
                extractor = Extractor(backend, prompt=prompt)
                for case in cases:
                    for repetition in range(args.repeat):
                        record = {"case_id": case.id, "model": model, "prompt": prompt,
                                  "prompt_sha256": hashlib.sha256(PROMPTS[prompt].encode()).hexdigest(),
                                  "repetition": repetition, "timestamp": datetime.now(timezone.utc).isoformat(),
                                  "options": {"temperature": 0, "seed": 42, "num_ctx": args.context,
                                              "num_predict": 2048, "think": False},
                                  "schema_sha256": hashlib.sha256(json.dumps(
                                      ExtractionResult.model_json_schema(), sort_keys=True).encode()).hexdigest()}
                        start = time.monotonic()
                        try:
                            record["runtime"] = backend.metadata()
                            image = read_image(args.manifest.parent / case.image)
                            record["image_sha256"] = hashlib.sha256(image).hexdigest()
                            result = extractor.extract(image)
                            record.update(status="ok", result=result.model_dump(),
                                          comparison=compare(result, case.expected))
                        except (ExtractionError, ImageInputError) as error:
                            failed = True
                            record.update(status="error", error=str(error))
                        record["seconds"] = round(time.monotonic() - start, 3)
                        report.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                        report.flush()
    return int(failed)
