# Tool calling from scratch

This Lesson 2 playground exposes one deterministic, read-only tool to a model
through the OpenAI Responses API. It is intentionally a bounded workflow, not a
general agent loop:

```text
question -> model -> optional tool request -> host executes -> model -> answer
```

The sample telemetry is local, so only the two model calls need network access.
Host-side parsing, validation, dispatch, and tool behavior can be tested offline.

## Run it

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r playgrounds/tool-calling-from-scratch/requirements.txt
Copy-Item .env.example .env
```

Add your API key and a current tool-capable model name to `.env`, then run:

```powershell
python playgrounds/tool-calling-from-scratch/tool_calling.py
```

The default question should produce a visible `lookup_service_health` request,
the deterministic tool result, and a model-written explanation.

## Test the trusted boundary without an API key

```powershell
python -m unittest discover -s playgrounds/tool-calling-from-scratch -p "test_*.py"
```

Try changing the question to one the tool cannot answer. Observe that the model
may answer directly or explain its limitation; the host still never grants a
capability that is absent from `TOOL_REGISTRY`.
