import io
import json
from unittest.mock import patch

import pytest
from PIL import Image
from pydantic import ValidationError

from local_id_extractor import ExtractionError, ExtractionResult, Extractor, ImageInputError
from local_id_extractor.images import prepare_image
from local_id_extractor.models import parse_result
from local_id_extractor.ollama import OllamaBackend


def payload():
    return {name: {"value": None, "confidence": 0.0} for name in ExtractionResult.model_fields}


def png():
    stream = io.BytesIO()
    Image.new("RGB", (40, 30)).save(stream, "PNG")
    return stream.getvalue()


@pytest.mark.parametrize("confidence", [-0.01, 1.01, "0.9", True, None, float("nan"), float("inf")])
def test_invalid_confidence(confidence):
    data = payload()
    data["first_name"]["confidence"] = confidence
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate(data)


@pytest.mark.parametrize("value", ["2025-02-29", "01/02/1990", "1990-5-12", "۱۴۰۰-۰۱-۰۱", 19900101])
def test_invalid_date(value):
    data = payload()
    data["date_of_birth"]["value"] = value
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate(data)


def test_no_coercion_missing_or_extra():
    for data in [dict(payload(), unexpected={}), {"first_name": {"value": "X", "confidence": 1}},
                 dict(payload(), passport_number={"value": 123, "confidence": 1})]:
        with pytest.raises(ValidationError):
            ExtractionResult.model_validate(data)


def test_unicode_leading_zero_and_low_confidence_preserved():
    data = payload()
    data["first_name"] = {"value": "علی", "confidence": 0.31}
    data["passport_number"] = {"value": "0012345", "confidence": 0.9}
    result = parse_result(json.dumps(data))
    assert result.first_name.value == "علی"
    assert result.first_name.confidence == 0.31
    assert result.passport_number.value == "0012345"


@pytest.mark.parametrize("raw", ['{"x":1,"x":2}', '```json\n{}\n```', '{} trailing'])
def test_strict_json(raw):
    with pytest.raises(ValueError):
        parse_result(raw)


def test_runtime_neutral_and_redacted_failure():
    class Fake:
        def generate(self, image, prompt, schema):
            assert image.startswith(b"\x89PNG")
            assert "date_of_birth" in schema["properties"]
            return json.dumps(payload())
    assert Extractor(Fake()).extract(png()).address.value is None
    with patch.object(Fake, "generate", return_value='{"private": "sensitive"}'):
        with pytest.raises(ExtractionError) as error:
            Extractor(Fake()).extract(png())
        assert "sensitive" not in str(error.value)


@pytest.mark.parametrize("raw", [b"", b"not an image", b"x" * (15 * 1024 * 1024 + 1)])
def test_invalid_image(raw):
    with pytest.raises(ImageInputError):
        prepare_image(raw)


def test_oversized_pixels():
    with patch("local_id_extractor.images.MAX_PIXELS", 100):
        with pytest.raises(ImageInputError):
            prepare_image(png())


def test_cloud_and_arbitrary_models_rejected():
    for name in ["qwen3.5:cloud", "https://example.com/model", "/tmp/model"]:
        with pytest.raises(ValueError):
            OllamaBackend(name)


def test_remote_model_rejected_before_image():
    backend = OllamaBackend()
    with patch.object(backend, "request", side_effect=[
        {"models": [{"name": backend.model}]}, {"remote_host": "example.com"}
    ]) as request:
        with pytest.raises(ExtractionError):
            backend.generate(png(), "test", {})
        assert all(call.args[0] != "chat" for call in request.call_args_list)


def test_truncated_generation_rejected():
    backend = OllamaBackend()
    with patch.object(backend, "metadata", return_value={}), patch.object(backend, "request", return_value={
        "done": True, "done_reason": "length", "message": {"content": json.dumps(payload())}
    }):
        with pytest.raises(ExtractionError):
            backend.generate(png(), "test", {})


def test_explicit_larger_context_sent_to_runtime():
    backend = OllamaBackend(context_length=8192)
    with patch.object(backend, "metadata", return_value={}), patch.object(backend, "request", return_value={
        "done": True, "message": {"content": json.dumps(payload())}
    }) as request:
        backend.generate(png(), "test", {})
        assert request.call_args.args[1]["options"]["num_ctx"] == 8192
    for context in [True, "8192", 262144]:
        with pytest.raises(ValueError):
            OllamaBackend(context_length=context)


@pytest.mark.parametrize("message", [None, [], "not an object", {"content": 12}])
def test_malformed_message_rejected(message):
    backend = OllamaBackend()
    with patch.object(backend, "metadata", return_value={}), patch.object(backend, "request", return_value={
        "done": True, "message": message
    }):
        with pytest.raises(ExtractionError):
            backend.generate(png(), "test", {})


def test_image_metadata_removed_and_transparency_composited():
    from PIL.PngImagePlugin import PngInfo
    metadata = PngInfo()
    metadata.add_text("private", "do not forward")
    stream = io.BytesIO()
    Image.new("RGBA", (20, 20), (0, 0, 0, 0)).save(stream, "PNG", pnginfo=metadata)
    with Image.open(io.BytesIO(prepare_image(stream.getvalue()))) as normalized:
        assert normalized.info == {}
        assert normalized.getpixel((0, 0)) == (255, 255, 255)


def test_animated_image_rejected():
    stream = io.BytesIO()
    Image.new("RGB", (20, 20), "red").save(
        stream, "PNG", save_all=True, append_images=[Image.new("RGB", (20, 20), "blue")])
    with pytest.raises(ImageInputError):
        prepare_image(stream.getvalue())
