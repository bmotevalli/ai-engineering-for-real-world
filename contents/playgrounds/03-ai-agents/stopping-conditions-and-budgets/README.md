# Lesson 7 — Stopping Conditions and Budgets

This playground makes agent termination explicit.

The core principle is:

> The model may decide that it is finished. The application decides whether it is allowed to continue.

The notebook separates step, tool-call, time, token, cost, and progress budgets; detects repeated actions; and returns structured stop reasons instead of treating every termination as an exception.

## Run the notebook

From the repository's `contents/` course root, activate the shared course environment and start Jupyter:

```powershell
.venv\Scripts\Activate.ps1
jupyter lab
```

Open:

`playgrounds/03-ai-agents/stopping-conditions-and-budgets/lesson-07-stopping-conditions-and-budgets.ipynb`

The examples are deterministic and do not require network access or an API key.

## What to observe

A five-step agent is not necessarily cheap or bounded: one step can contain provider retries, multiple tool calls, or expensive model requests. Treat each resource dimension separately.

Also notice that repeated-action detection is different from a simple step limit. An agent can remain within its nominal budget while making no useful progress.

The notebook ends by asking you to integrate the policy with the Lesson 3 travel-agent loop so stopping conditions surround real model and tool boundaries instead of living as a disconnected utility.
