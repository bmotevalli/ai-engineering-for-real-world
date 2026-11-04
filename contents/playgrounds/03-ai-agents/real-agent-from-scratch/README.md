# Lesson 10 — Build a Real Agent from Scratch in Python

This playground integrates the mechanisms introduced across Lessons 2–9 into one small, inspectable agent without an orchestration framework.

The scenario is a travel assistant that can:

- retrieve live weather and sun times from Open-Meteo;
- search a small deterministic activity catalogue;
- use selected user preferences as memory context;
- optionally create a concise external plan;
- iterate through model-selected tool calls;
- retry transient read-only HTTP failures;
- enforce step, tool-call, and repeated-action limits;
- pause before a simulated reservation side effect;
- resume after approval or denial.

The architectural principle is:

> The model owns bounded decisions; the host owns tools, state, budgets, retry policy, validation, approval, and execution authority.

## Files

- `lesson-10-real-agent.ipynb` — primary teaching surface.
- `agent.py` — reusable implementation imported by the notebook.
- `test_agent.py` — deterministic tests for host-owned logic.

## Run

From the `contents/` course root:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter lab
```

Open:

`playgrounds/03-ai-agents/real-agent-from-scratch/lesson-10-real-agent.ipynb`

Configure `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env`. Open-Meteo needs no separate API key.

Run deterministic tests from the playground directory:

```powershell
pytest test_agent.py
```

## What to observe

Do not focus only on the final answer. Inspect the boundaries:

1. the model proposes a tool call;
2. host code validates the tool and arguments;
3. read-only tool execution is retried only for transient network failures;
4. observations are appended to explicit state;
5. budgets are checked outside the model;
6. repeated actions can terminate the run;
7. side effects stop at `WAITING_FOR_APPROVAL`;
8. approval resumes the exact pending call rather than giving the model blanket authority.

This is intentionally more verbose than a framework implementation. Lesson 11 will compare what an orchestration framework can simplify and what architectural responsibilities still remain yours.
