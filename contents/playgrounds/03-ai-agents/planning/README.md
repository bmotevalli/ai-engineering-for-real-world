# Lesson 5 — Planning

This playground introduces planning as an explicit, revisable part of agent state.

The main example asks the assistant to plan a half-day outdoors in Melbourne tomorrow. The model creates a concise structured plan using only known actions, the host validates that plan, executes read-only evidence-gathering steps, records observations, and decides whether the remaining plan is still valid.

```text
goal
  ↓
create concise plan
  ↓
validate plan
  ↓
execute next step
  ↓
record observation + status
  ↓
remaining plan still valid?
  ├── yes → continue
  └── no  → revise/skip (bounded)
  ↓
final synthesis
```

## Run the notebook

From the repository root, activate the shared course virtual environment and start Jupyter:

```powershell
.venv\Scripts\Activate.ps1
jupyter lab
```

Open:

`playgrounds/03-ai-agents/planning/lesson-05-planning.ipynb`

The notebook uses the direct OpenAI SDK plus the public Open-Meteo API. Configure `OPENAI_API_KEY` and `OPENAI_MODEL` in the repository `.env` file as in earlier lessons.

## What to observe

Pay attention to the difference between the plan and execution. The model proposes an inspectable task list, but the application owns allowed actions, status transitions, tool execution, and replanning rules.

Try a simple one-tool goal such as `What is tomorrow's weather in Melbourne?` and inspect whether planning adds unnecessary work. Then force or simulate severe rain and observe how new evidence can invalidate the remaining plan.

The key principle is:

> A plan is an explicit, revisable description of intended work — not permission to execute it.
