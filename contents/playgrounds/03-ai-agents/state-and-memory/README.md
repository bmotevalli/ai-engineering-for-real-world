# Lesson 4 — State and Memory

This playground separates two concepts that are often mixed together in agent frameworks:

- **State** — information needed while the current task is running.
- **Memory** — information deliberately persisted so it can influence a later task or session.

The lesson keeps both mechanisms explicit. It does not introduce a memory framework or vector database yet.

## Examples

### Example 1 — Working state inside an agent run

A travel assistant maintains an `AgentState` containing the current goal, step count, model/tool protocol history, and observations. This shows why the agent loop needs state even when nothing is persisted after the run.

### Example 2 — Durable user preferences across sessions

A tiny JSON-backed `MemoryStore` persists a few explicit travel preferences such as preferred departure time or dietary preference. A later session selectively loads those preferences into context.

The example deliberately does **not** store the entire conversation as permanent memory. That distinction is important for privacy, relevance, cost, and correctness.

## Run the notebook

From the repository root, use the shared course environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r playgrounds/requirements.txt
Copy-Item .env.example .env
jupyter lab
```

Open:

`playgrounds/03-ai-agents/state-and-memory/lesson-04-state-and-memory.ipynb`

Add `OPENAI_API_KEY` and a current tool-capable `OPENAI_MODEL` to `.env` before running the model-backed cells.

The JSON memory file used by the notebook is created in the playground directory for demonstration. Delete it after the exercise if you want to reset the example.

## What to observe

The important boundary is:

```text
current task state
    ├── goal
    ├── protocol history
    ├── tool observations
    └── step counters

selected durable memory
    ├── user preferences
    └── stable facts worth carrying forward
```

A production system should decide explicitly what is ephemeral, what is durable, who may read it, how long it is retained, and how it is corrected or deleted.
