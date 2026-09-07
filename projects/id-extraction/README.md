# Local identity-document extraction

Phase 1: local image → Ollama vision model → strict, validated Python result / JSON.
No FastAPI endpoint is implemented. Images and responses are never sent to an external
service by this application. Installation and explicit model downloads require internet.

## Inspected machine (6 September 2026)

| Component | Finding |
| --- | --- |
| OS / kernel | Ubuntu 26.04 LTS / 7.0.0-28-generic |
| CPU | Intel i7-6700K, 4 cores, 8 threads, 4 GHz |
| Memory | 15 GiB total, 9.1 GiB available during inspection; 4 GiB swap, 1.8 GiB used |
| GPU | NVIDIA GeForce GTX 1060 6GB, 6144 MiB VRAM, ~708 MiB occupied by desktop |
| Driver | NVIDIA 580.173.02, host `nvidia-smi` successful |
| CUDA | Driver reports compatibility through CUDA 13.0; no `nvcc` on PATH |
| Disk | 149 GB available before installation |
| Existing Ollama | Not installed / no listener on port 11434 |

The sandbox initially hid `/dev/nvidia*`; a host inspection confirmed the driver
works. No driver, kernel, system service or CUDA toolkit installation was needed.
CUDA reported by `nvidia-smi` is driver compatibility, not an installed toolkit.
The GTX 1060 has compute capability 6.1 and no tensor cores. Ollama's
[GPU support documentation](https://docs.ollama.com/gpu) lists this card and requires
driver 570+ for this generation; the installed driver meets that requirement.

## Model choice

Initial model: **`qwen3.5:9b-q4_K_M`**, explicitly quantized Q4_K_M, with vision.
Its [official tag](https://ollama.com/library/qwen3.5:9b-q4_K_M) is approximately
6.6 GB before runtime/context overhead. It cannot fit entirely in available VRAM.
Expect mixed GPU/CPU execution, slow initial image processing and limited concurrency.
Use a 4096-token context, 2048-token output limit and one request at a time. Avoid
the advertised 256K maximum context on this machine. Close memory-heavy apps if
memory pressure or swapping develops. A timeout fails explicitly; it never becomes
a successful all-null extraction.

This is the requested 9B baseline, not an established accuracy winner. For a smaller
memory footprint, benchmark `qwen3.5:4b-q4_K_M`. `qwen3-vl:8b` is also allowlisted
for a later comparison; it has not been automatically downloaded. Do not assume
family-level benchmark claims establish accuracy on Australian licences or Persian/
Dari/Pashto passport text. Evaluate all jurisdictions, calendars, scripts and image
quality conditions with locally held, appropriately authorised examples.

## Installation

Run from `projects/id-extraction/` on Linux x86_64 (all commands below use that working directory). Requires Python 3.11+, `curl`, `tar`,
`zstd` and a functioning NVIDIA driver for acceleration. The verified environment
uses Python 3.14.4. Runtime, model weights and Python packages live in `.runtime/`
and `.venv/`; no root installation or automatic startup service is configured.

```bash
bash scripts/install-ollama.sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
```

The installer pins Ollama **v0.33.3** and verifies the official release asset's SHA-256
before extraction. See [upstream releases](https://github.com/ollama/ollama/releases/tag/v0.33.3)
and [manual Linux installation](https://docs.ollama.com/linux). The downloaded archive
is retained for reproducibility; it is not needed to run the server.

On this machine `ensurepip` was missing. The environment was bootstrapped locally
without installing Ubuntu packages. If the venv command above fails for that reason:

```bash
python3 -m venv --without-pip .venv
curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/local-id-get-pip.py
.venv/bin/python /tmp/local-id-get-pip.py
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
```

Start the server in a dedicated terminal, then leave it running:

```bash
bash scripts/serve-ollama.sh
```

It binds to **127.0.0.1:11434**, sets `OLLAMA_NO_CLOUD=1`, limits loaded models and
parallelism to one, and uses `.runtime/models`. Stop with Ctrl-C. No port forwarding
or public binding is required. Do not enable debug logging for identity documents.
The first Ollama startup may create its normal per-user key/config files in `~/.ollama`.

In another terminal download the selected model (once):

```bash
OLLAMA_HOST=127.0.0.1:11434 .runtime/ollama/bin/ollama pull qwen3.5:9b-q4_K_M
OLLAMA_HOST=127.0.0.1:11434 .runtime/ollama/bin/ollama show qwen3.5:9b-q4_K_M
```

Model tags can change upstream. Each benchmark records the installed model digest,
runtime version, quantization details, image hash, schema hash, prompt hash and inference options.
Retain the model store and reports when reproducing a measured run.

## Run an extraction

```bash
.venv/bin/id-extract /path/to/document.jpg
```

High-resolution images can exceed the default 4096-token input context. To preserve
the original image resolution, explicitly use the larger context (with higher memory
use) if Ollama reports a context-limit error:

```bash
.venv/bin/id-extract /path/to/document.jpg --context 8192
# The benchmark harness accepts the same --context 8192 option and records it.
```

Successful stdout is JSON only. Errors go to stderr and exit with status 1; no raw
model response or image path is included in application error messages. Nothing is
saved by the extractor. Redirect stdout only to a private destination if needed.

```python
from local_id_extractor import Extractor, ExtractionError, ImageInputError

extractor = Extractor()
result = extractor.extract("/path/to/document.jpg")
# Also accepts bytes, suitable for a future validated upload:
# result = extractor.extract(image_bytes)
print(result.model_dump_json(indent=2))
```

`Extractor` performs image preparation and output validation. The `Backend` protocol
isolates inference; `OllamaBackend` implements local HTTP calls. Prompt/model selection
is operator configuration, restricted to code-owned registries. CLI code is separate.
The call is synchronous and can be slow; a future asynchronous web application should
use a bounded worker/queue and keep inference off its event loop.

## Response contract

All 16 keys are required: `document_type`, `issuing_country`,
`issuing_state_or_territory`, `first_name`, `middle_name`, `last_name`, `full_name`,
`date_of_birth`, `sex`, `nationality`, `document_number`, `licence_number`,
`passport_number`, `address`, `issue_date`, `expiry_date`.

Each key contains exactly `value` and `confidence`:

```json
{
  "value": "1990-05-12",
  "confidence": 0.93
}
```

* `value`: nonempty string up to 1024 characters, or `null`. No implicit numeric
  coercion, whitespace-only values, control characters or extra properties.
* `confidence`: finite JSON number in `[0,1]`; strings and booleans are rejected.
* `document_type`: `driver_licence`, `passport`, or null.
* Dates: real Gregorian calendar dates in `YYYY-MM-DD`, or null. Ambiguous date
  order, centuries or calendar conversion should yield null. Raw date evidence is
  not retained in this minimal schema.
* Names, addresses, identifiers and printed codes preserve Unicode and leading
  zeros. No invented name splitting, translations or nationality inference.

Missing/unreadable/absent/too ambiguous values are null. The prompt asks for confidence
0 for null values: confidence describes a candidate transcription's reliability,
not certainty that a field is absent. The validator accepts any in-range score with
null, preserving the model's estimate. Low-confidence non-null values are preserved
without boosting scores or applying an arbitrary rejection threshold.

Ollama receives Pydantic's JSON Schema via structured output. The application then
independently rejects malformed JSON, duplicate keys, missing fields, invalid values,
extra fields and truncated responses. It does not repair or silently retry output.
An unreadable image can produce a valid all-null result; corrupt/unsupported files
and model failures are separate errors.

**Schema validation cannot establish factual correctness or visibility on the image.**
The prompt expresses those requirements; human-labelled evaluations must measure
hallucinations and incorrect attribution. Confidence is model-estimated uncertainty,
not a statistically calibrated probability. No identity verification, authenticity
detection, MRZ check-digit validation or automated acceptance decision is implemented.

## Tests and comparisons

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/make-fixtures.py
mkdir -p results
.venv/bin/id-benchmark examples/manifest.json --output results/smoke.jsonl
```

Fixtures are locally rendered fictional text and a blank image, not realistic
government-issued document replicas. They exercise OCR, date formatting, null handling,
JSON validation and the end-to-end runtime, not real-world extraction accuracy.

A manifest is a JSON array. Image paths are relative to the manifest. `expected` is
optional; omitted keys are unscored, while an explicit null tests correct abstention:

```json
[
  {
    "id": "case-001",
    "image": "licence-front.jpg",
    "expected": {"first_name": "ALICE", "address": null}
  }
]
```

Keep real documents/manifests under ignored `private/`. Add versioned prompts to
`prompts.py` for controlled experiments. After explicitly pulling comparison models:

```bash
.venv/bin/id-benchmark private/manifest.json --output results/comparison.jsonl \
  --models qwen3.5:9b-q4_K_M qwen3-vl:8b \
  --prompts conservative-v2 label-review-v2 --repeat 2
```

`conservative-v2` is the default; `label-review-v2` adds a label/character review
instruction. Earlier v1 prompts are retained for reproducibility. Neither review
variant is assumed superior without measured results.
The harness runs sequentially, retains every result/failure, timings including model
loading, and exact per-field comparisons. The first request may be much slower than
warm requests. Temperature 0 and seed 42 improve repeatability but do not guarantee
bit-identical GPU output. Confidence scores are recorded, not treated as accuracy.
Compare incorrect non-null predictions, correct/incorrect abstentions and confidence
against held-out labels before choosing thresholds. Include all eight Australian
licence jurisdictions, passport countries, scripts, blur/glare/crops and non-ID images.

Reports intentionally contain extracted personal data and optional expected values.
They are created with mode 0600, refuse overwrite, and are gitignored. Use a private
parent directory; choose retention/deletion deliberately. Ordinary filesystem deletion
does not guarantee secure erasure from snapshots or SSDs.

## Verify GPU use

While a request is running (or within the five-minute keep-alive window):

```bash
OLLAMA_HOST=127.0.0.1:11434 .runtime/ollama/bin/ollama ps
nvidia-smi
curl -fsS http://127.0.0.1:11434/api/ps
```

Look for GPU memory allocated to the Ollama runner, positive `size_vram` in `/api/ps`,
and a GPU share in `ollama ps`; mixed CPU/GPU is expected. Server logs should report
CUDA discovery and offloaded layers. `nvidia-smi` alone proves driver access, not
model offloading. Run on the host if a sandbox hides GPU device nodes. No standalone
CUDA toolkit is required for the prebuilt runtime.

## Measured local validation

Live tests were run on 7 September 2026 with Ollama 0.33.3, Q4_K_M and model digest
`6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`.
The installed GGUF reports 9.7B parameters including the multimodal model components.

* **32 automated tests passed**, covering output validation, Unicode/leading zeros,
  safe failures, bounded image decoding and benchmark reporting.
* Ollama discovered the GTX 1060 through its bundled **CUDA 12** library. Its CUDA 13
  library skipped this older architecture; automatic CUDA 12 selection worked.
* During inference, `ollama ps` reported **36% CPU / 64% GPU**, context 4096.
  `/api/ps` reported `size_vram=3908325866` bytes; `nvidia-smi` showed **5373 MiB** total
  GPU memory use including desktop and other runtime allocations. These are memory
  placement measurements, not a percentage speed-up.
* The initial cold fictional passport request took **80.342 seconds**. The initial
  blank-image request took **51.075 seconds** and returned all 16 fields null.
* The initial v1 prompt incorrectly concatenated a `full_name` from separate name
  fields with confidence 1.0. The comparison harness caught this semantic error even
  though the response passed schema validation. Default v2 explicitly forbids that
  concatenation; its warm passport request took **59.858 seconds** and matched all
  **13 checked fields**, including null `full_name`.
* With the final v2 prompt, the blank image took **47.832 seconds** and matched all
  **16 expected nulls**. Both final requests produced valid, complete JSON.

Raw local comparisons are in ignored `results/smoke.jsonl` and
`results/smoke-v2.jsonl`. These small synthetic tests establish that the local workflow
runs, not accuracy on real Australian licences or Iranian/Afghan passports. No real
identity document was supplied for evaluation. The v1 failure also demonstrates why
even a confidence of 1.0 cannot be treated as a calibrated guarantee.

## Privacy and future integration boundary

The client is fixed to loopback, ignores proxy environment settings, refuses HTTP
redirects, rejects cloud/arbitrary model names and checks local vision-model metadata
before sending an image. The supplied server launcher disables Ollama cloud features.
Do not replace that listener with an untrusted proxy/service. Loopback is not access
control against other local users. Ollama may write operational logs; keep them private.

Input is limited to single-frame PNG/JPEG/WebP, 15 MiB input and normalized-image size,
and 20 million pixels. Pillow decodes the image, applies EXIF orientation, composites
transparency and strips metadata in memory. No temporary image is written. RAM/swap
and process crashes remain OS-level data-handling concerns; this does not promise
secure memory erasure.

Phase 2 remains unimplemented. Before public exposure, add authentication/authorization,
upload limits before reading bodies, bounded concurrency/rate limits, timeout/cancellation
policy and sensitive-data logging/retention controls. Public callers must not select
server endpoints, model paths, prompts, shell commands or runtime configuration. Treat
image text as untrusted instructions and output as untrusted data even after validation.
