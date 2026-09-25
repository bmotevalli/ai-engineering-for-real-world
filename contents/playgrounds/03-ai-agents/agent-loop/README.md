# Lesson 3 — The Agent Loop

This playground turns Lesson 2's bounded tool call into an explicit, host-controlled agent loop.

The main learning artifact is:

- `lesson-03-agent-loop.ipynb` — executable Jupyter notebook
- `docs/module-03-ai-agents/lesson-03-agent-loop.html` — browser-friendly notebook-style walkthrough

## Scenario

The user asks:

> I'm visiting Melbourne tomorrow. Will I need an umbrella, and what time is sunset?

The model can choose between two read-only tools backed by live Open-Meteo APIs:

- `get_weather(city, target_date)`
- `get_sun_times(city, target_date)`

The host repeatedly asks the model what to do next, validates and executes any requested tool, appends the observation, and calls the model again until a final answer is produced or the step budget is exhausted.

```text
goal
  -> model decision
  -> optional tool request
  -> host validation + execution
  -> observation
  -> model decision again
  -> ...
  -> final answer
```

## Run it

From the repository root, use the shared course environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r playgrounds/requirements.txt
Copy-Item .env.example .env
```

Add your OpenAI API key and model to `.env`, then launch Jupyter:

```powershell
jupyter lab playgrounds/03-ai-agents/agent-loop/lesson-03-agent-loop.ipynb
```

No weather API key is required. Open-Meteo is used for live geocoding, forecast, sunrise, and sunset data.

## What to observe

Focus on the trace rather than the exact forecast values:

1. The model chooses an action rather than the Python code prescribing an order.
2. The host validates and executes the requested action.
3. The tool result becomes an observation in `state`.
4. The model sees the updated state and decides again.
5. The host enforces `max_steps` and owns termination.

## Exercises

Try asking for only sunset or only weather and see whether the model finishes earlier. Then set `max_steps=1` for the original two-part goal and observe the budget failure. Finally, add one more safe read-only tool without changing the loop itself.
