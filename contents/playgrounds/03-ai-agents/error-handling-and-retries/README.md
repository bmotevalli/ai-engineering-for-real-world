# Lesson 6 — Error Handling and Retries

This playground makes failure handling explicit before an agent framework hides it.

The central idea is:

> The host classifies failures and owns bounded retry policy. The model may decide what to do after a final failure becomes an observation, but it does not control infrastructure retries.

The notebook covers transient versus permanent failures, bounded exponential backoff, provider retries, tool retries, structured failure observations, idempotency for side effects, and the distinction between retry budgets and agent step budgets.

## Run the notebook

From the repository's `contents/` course root, activate the shared environment and start Jupyter:

```powershell
.venv\Scripts\Activate.ps1
jupyter lab
```

Open:

`playgrounds/03-ai-agents/error-handling-and-retries/lesson-06-error-handling-and-retries.ipynb`

The main retry examples are deterministic and do not require a network call. The optional provider wrapper uses the same OpenAI SDK already introduced in earlier lessons.

## What to observe

A transient timeout may be retried a small number of times. Invalid input should fail immediately. Once recovery is exhausted, the agent gets one structured failure observation rather than seeing every low-level retry attempt as a new reasoning step.

Also pay attention to side effects. Retrying a read-only weather request is very different from retrying a booking, payment, email, deployment, or delete operation. Side-effecting tools need idempotency or explicit status checking before retries are safe.
