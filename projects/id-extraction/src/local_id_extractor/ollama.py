"""Ollama HTTP implementation, restricted to local models and a loopback listener."""
import base64
import json
import urllib.error
import urllib.request
from urllib.parse import urlparse

from .extractor import ExtractionError

DEFAULT_MODEL = "qwen3.5:9b-q4_K_M"
ALLOWED_MODELS = (DEFAULT_MODEL, "qwen3-vl:8b", "qwen3.5:4b-q4_K_M")


class OllamaBackend:
    def __init__(self, model: str = DEFAULT_MODEL, *, timeout: float = 600,
                 context_length: int = 4096, base_url: str = "http://127.0.0.1:11434"):
        if model not in ALLOWED_MODELS:
            raise ValueError("model is not in the local allowlist")
        self.model = model
        if type(context_length) is not int or context_length not in (4096, 8192):
            raise ValueError("context length must be 4096 or 8192")
        self.context_length = context_length
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or parsed.username or parsed.password or parsed.path not in ("", "/"):
            raise ValueError("Ollama base URL must be a plain HTTP origin")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # No environment proxies or HTTP redirects; images cannot be forwarded.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        self._http = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def request(self, path: str, body: dict | None = None) -> dict:
        request = urllib.request.Request(
            self.base_url + "/api/" + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with self._http.open(request, timeout=self.timeout) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("oversized response")
            data = json.loads(raw)
            if not isinstance(data, dict) or "error" in data:
                raise ValueError("invalid response")
            return data
        except (OSError, ValueError, RecursionError, urllib.error.URLError):
            raise ExtractionError("local Ollama request failed; check service, model and timeout") from None

    def metadata(self) -> dict:
        tags = self.request("tags").get("models", [])
        if not isinstance(tags, list) or any(not isinstance(m, dict) for m in tags):
            raise ExtractionError("invalid local model inventory")
        match = next((m for m in tags if m.get("name") == self.model), None)
        if match is None:
            raise ExtractionError("selected local model is not installed; pull it explicitly")
        details = self.request("show", {"model": self.model})
        if details.get("remote_host") or details.get("remote_model"):
            raise ExtractionError("remote models are forbidden")
        capabilities = details.get("capabilities")
        if not isinstance(capabilities, list) or "vision" not in capabilities:
            raise ExtractionError("selected model has no vision capability")
        return {"model": self.model, "digest": match.get("digest"),
                "details": details.get("details"), "ollama_version": self.request("version").get("version")}

    def generate(self, image: bytes, prompt: str, schema: dict) -> str:
        self.metadata()  # Fail before sending an image if the model is not local.
        result = self.request("chat", {
            "model": self.model, "stream": False, "think": False,
            "keep_alive": "5m", "format": schema,
            "options": {"temperature": 0, "seed": 42, "num_ctx": self.context_length, "num_predict": 2048},
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Extract only the information visible in this document.",
                 "images": [base64.b64encode(image).decode("ascii")]},
            ],
        })
        if result.get("done") is not True or result.get("done_reason") == "length":
            raise ExtractionError("model response did not finish within its output budget")
        message = result.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise ExtractionError("model response has no JSON content")
        return content
