# Tool calling from scratch

This Lesson 2 playground exposes one deterministic, read-only tool to a model through the OpenAI Responses API. It is intentionally a bounded workflow, not a general agent loop:

```text
question -> model -> optional tool request -> host executes -> model -> answer
```

The sample telemetry is local, so only the two model calls need network access. Host-side parsing, validation, dispatch, and tool behavior can be tested offline.

## Notebook walkthrough

The lesson is also available as a real Jupyter notebook so students can read the explanations as Markdown cells, run each code cell independently, and modify the example themselves:

- `lesson-02-tool-calling.ipynb` — executable notebook
- `docs/module-03-ai-agents/lesson-02-tool-calling.html` — browser-friendly notebook-style version

The notebook starts with the problem context before introducing code, then walks through the responsibility split between the model and the host application, the tool schema, model-generated arguments, host-side validation, `call_id`, tool observations, and the final model response.

## Run it

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r playgrounds/requirements.txt
Copy-Item .env.example .env
```

`playgrounds/requirements.txt` is shared by every playground in the course, so this environment only needs to be created once.

Add your API key and a current tool-capable model name to `.env`, then run:

```powershell
python playgrounds/03-ai-agents/tool-calling-from-scratch/tool_calling.py
```

The default question should produce a visible `lookup_service_health` request, the deterministic tool result, and a model-written explanation.

## Test the trusted boundary without an API key

```powershell
python -m unittest discover -s playgrounds/03-ai-agents/tool-calling-from-scratch -p "test_*.py"
```

Try changing the question to one the tool cannot answer. Observe that the model may answer directly or explain its limitation; the host still never grants a capability that is absent from `TOOL_REGISTRY`.
