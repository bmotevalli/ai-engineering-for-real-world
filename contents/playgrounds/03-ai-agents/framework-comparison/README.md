# Lesson 11 — Compare Agent Frameworks

This playground compares the first-principles orchestration from Lesson 10 with a small LangGraph implementation.

The purpose is **not** to replace the architecture we learned with framework terminology. It is to map familiar concepts onto framework primitives:

| First-principles concept | LangGraph equivalent |
|---|---|
| `AgentState` | graph state schema |
| agent loop | graph edges + repeated node execution |
| model decision step | model node |
| tool dispatch | tool node |
| if/else after model output | conditional edge/router |
| stop condition | route to `END` |
| pause/checkpoint | framework persistence/interrupt capabilities |

LangGraph can be used as a low-level orchestration framework without adopting the full higher-level LangChain agent stack. We keep the OpenAI Responses API explicit so the only major new abstraction is orchestration.

## Run

From the `contents/` course root:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter lab
```

Open:

`playgrounds/03-ai-agents/framework-comparison/lesson-11-framework-comparison.ipynb`

Configure `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env`.

Run deterministic tests from the playground directory:

```powershell
pytest test_framework_agent.py
```

## What to compare

Do not compare line counts alone. Compare responsibilities.

LangGraph helps make state transitions, routing, graph structure, persistence, streaming, and pause/resume orchestration more explicit and reusable. But the framework does **not** decide your security model, tool permissions, retry policy, idempotency rules, approval policy, memory lifecycle, cost budgets, or evaluation strategy.

The useful question is:

> Which orchestration mechanics should a framework own, and which application policies must remain explicit in our code?
