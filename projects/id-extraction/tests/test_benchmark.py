import json
import stat
import sys
from unittest.mock import patch

from local_id_extractor import ExtractionError, ExtractionResult
from local_id_extractor.benchmark import main


def test_report_retains_failures_and_compares_explicit_null(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([
        {"id": "good", "image": "good.png", "expected": {"address": None}},
        {"id": "bad", "image": "bad.png"},
    ]))
    output = tmp_path / "report.jsonl"
    result = ExtractionResult.model_validate({
        key: {"value": None, "confidence": 0.0} for key in ExtractionResult.model_fields})
    with patch.object(sys, "argv", ["id-benchmark", str(manifest), "--output", str(output)]), \
         patch("local_id_extractor.benchmark.OllamaBackend.metadata", return_value={"digest": "test"}), \
         patch("local_id_extractor.benchmark.read_image", return_value=b"fixture"), \
         patch("local_id_extractor.benchmark.Extractor.extract", side_effect=[result, ExtractionError("failure")]):
        assert main() == 1
    records = [json.loads(line) for line in output.read_text().splitlines()]
    assert records[0]["comparison"]["address"]["match"] is True
    assert set(records[0]["comparison"]) == {"address"}
    assert records[1]["status"] == "error"
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
