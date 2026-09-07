"""Runtime-neutral service boundary. No CLI dependencies or file persistence."""
from pathlib import Path
from typing import Protocol

from .images import prepare_image
from .models import ExtractionResult, parse_result
from .prompts import DEFAULT_PROMPT, PROMPTS


class ExtractionError(RuntimeError):
    """Safe error without model output, document values, or image paths."""


class Backend(Protocol):
    def generate(self, image: bytes, prompt: str, schema: dict) -> str: ...


class Extractor:
    def __init__(self, backend: Backend | None = None, *, prompt: str = DEFAULT_PROMPT):
        if backend is None:
            from .ollama import OllamaBackend
            backend = OllamaBackend()
        self.backend = backend
        self.prompt = PROMPTS[prompt]

    def extract(self, image: str | Path | bytes) -> ExtractionResult:
        content = self.backend.generate(
            prepare_image(image), self.prompt, ExtractionResult.model_json_schema()
        )
        try:
            return parse_result(content)
        except (ValueError, TypeError, RecursionError):
            raise ExtractionError("model returned invalid extraction JSON") from None
