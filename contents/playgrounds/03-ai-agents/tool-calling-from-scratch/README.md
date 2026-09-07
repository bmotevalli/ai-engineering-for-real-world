# Tool calling from scratch

Lesson 2 now uses two examples that teach the same tool-calling protocol from different angles:

1. **Everyday Weather Assistant** — a relatable first example backed by the live Open-Meteo API.
2. **Service Health Assistant** — an engineering-oriented example with stronger emphasis on validation, allowlists, trusted execution, and failure handling.

Both remain intentionally bounded workflows rather than general agent loops:

```text
question -> model -> optional tool request -> host executes -> model -> answer
```

## Notebook walkthroughs

### Example 1 — Everyday Weather Assistant

- `lesson-02-example-01-weather.ipynb` — executable notebook using live weather data
- `docs/module-03-ai-agents/lesson-02-example-01-weather.html` — browser-friendly notebook-style version

The learner asks a familiar question such as `Will I need an umbrella in Melbourne tomorrow?`. The model decides whether the weather capability is relevant, while Python validates the request and calls the public Open-Meteo API.

### Example 2 — Service Health Assistant

- `lesson-02-tool-calling.ipynb` — executable engineering example
- `docs/module-03-ai-agents/lesson-02-tool-calling.html` — browser-friendly notebook-style version

This example applies the same protocol to production-style service telemetry and goes deeper into host-side validation, trusted dispatch, `call_id`, unknown states, and failure boundaries.

## Run the notebooks

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r playgrounds/requirements.txt
Copy-Item .env.example .env
jupyter lab
```

Add your OpenAI API key and a current tool-capable model name to `.env`. Example 1 uses Open-Meteo for weather data and does not require a separate weather API key.

## Existing script and tests

The original service-health implementation is also available as a normal Python script:

```powershell
python playgrounds/03-ai-agents/tool-calling-from-scratch/tool_calling.py
```

Run its offline tests with:

```powershell
python -m unittest discover -s playgrounds/03-ai-agents/tool-calling-from-scratch -p "test_*.py"
```

The key learning point across both examples is the same: the model proposes an action, but the host application owns validation, authorisation, execution, errors, and side effects.
