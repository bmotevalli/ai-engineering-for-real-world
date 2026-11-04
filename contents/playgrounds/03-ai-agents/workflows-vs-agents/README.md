# Lesson 9 — Deterministic Workflows vs Agents

This playground is about architecture choice rather than another agent mechanism.

The central question is:

> Should this problem be an agent at all?

The lesson compares deterministic workflow, agentic, and hybrid designs for the same hotel-selection and booking problem. The deterministic example is deliberately runnable without an API key; the agentic region is described as a design boundary rather than adding unnecessary provider calls.

## Run the notebook

From the repository's `contents/` course root:

```powershell
.venv\Scripts\Activate.ps1
jupyter lab
```

Open:

`playgrounds/03-ai-agents/workflows-vs-agents/lesson-09-workflows-vs-agents.ipynb`

No network access or API key is required for the core examples.

## What to observe

A model can be useful inside a deterministic pipeline without making the system an agent. The defining question remains: who chooses the next action?

The most useful production pattern is often a deterministic shell around a bounded agentic island:

```text
validation / policy
        ↓
agentic exploration or semantic judgment
        ↓
deterministic constraints
        ↓
approval when needed
        ↓
idempotent side effect
```

This keeps autonomy where it earns its complexity while preserving explicit authority and invariants in application code.
