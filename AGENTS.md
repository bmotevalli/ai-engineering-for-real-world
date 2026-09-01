# Repository Guidance

## Repository purpose

This repository is both a practical AI engineering learning workspace and a living course/reference. Use it to develop modern AI engineering skills through concise explanations, hands-on experiments, small playgrounds, realistic projects, architecture discussions, and production trade-offs.

The emphasis is practical AI engineering. Do not spend time teaching beginner Python, general software engineering, or deep mathematical ML theory unless it is necessary for the current topic.

## Learner profile

The learner is a senior software engineer with strong experience in Python, software architecture, DevOps, cloud platforms, Kubernetes, infrastructure, and a solid machine-learning foundation. Teach and review work at that level: connect new AI concepts to production systems and focus on the parts that are distinctive to AI engineering.

## Learning and teaching style

- Begin with first principles and a clear mental model.
- Prefer a plain Python implementation before introducing a framework.
- Introduce frameworks only after the mechanism they automate is understood.
- Explain architectural choices, boundaries, failure modes, and trade-offs rather than only demonstrating APIs.
- Clearly distinguish deterministic workflows from agentic systems. An LLM call or the presence of tools alone does not make a system agentic.
- Avoid unnecessary abstractions and over-engineered examples.
- Use realistic engineering problems and keep code simple, clean, and production-oriented.
- Discuss reliability, observability, security, cost, latency, testing, deployment, and failure handling when relevant.
- Use the minimum autonomy necessary for the problem.

When a conceptual question arises during an exercise, answer it in the context of the current module and implementation rather than treating it as an unrelated topic.

## Technology preferences

- Python is the primary language.
- React is appropriate when a user interface adds genuine learning or product value.
- Prefer provider SDKs, explicit control flow, and standard-library facilities before frameworks.
- Add dependencies only when they provide clear value; keep experiments easy to inspect and run.
- Frameworks such as LangChain or LangGraph are comparison and orchestration tools, not starting points.

## Course direction and priorities

The broader course should progressively cover running LLMs, OpenAI, Hugging Face, Ollama, LiteLLM, prompt engineering, agents, agentic systems, MCP, embeddings, vector databases, RAG variants, evaluation, production systems, and deployment.

The current priority order is:

1. AI Agents
2. Agentic Systems
3. Model Context Protocol (MCP)
4. Embeddings and Vector Databases
5. RAG
6. Advanced RAG
7. Database RAG
8. Agentic RAG
9. Evaluation
10. Production AI Systems

## Active module: Module 03 — AI Agents

Follow this learning sequence:

1. What an agent is
2. Tool calling
3. The agent loop
4. State and memory
5. Planning
6. Retries and error handling
7. Stopping conditions and budgets
8. Human-in-the-loop
9. Workflows vs agents
10. Build an agent from scratch in Python
11. Compare agent frameworks

Lesson 1 established these durable concepts:

- An LLM call is not automatically an agent.
- Tools alone do not make a system agentic.
- In an agent, an LLM participates in control-flow decisions.
- The basic loop is Observe -> Decide -> Act -> Observe.
- The four core concepts are goal, LLM, tools, and state.
- Deterministic workflows and agents are distinct.
- Autonomy is a spectrum; use the minimum autonomy needed.
- RAG can be one capability or tool available to an agent.

Lesson 2 established:

- Tool definitions are contracts shown to the model, not direct executable access.
- The model proposes actions; the host validates, authorises, dispatches, and executes them.
- Model-generated arguments and tool results both cross trust boundaries.
- `call_id` correlates a tool request with its observation.
- One bounded tool-use turn is not yet a general agent loop.
- Direct provider SDKs are used first so the protocol stays visible before later provider abstraction.

Lesson 3 established:

- The model proposes the next action; the application owns the control loop.
- After each observation, the model can decide to answer or request another action.
- Working state must preserve protocol history and observations across loop iterations.
- Agent loops need explicit host-controlled limits such as `max_steps`; avoid unbounded `while True` loops.
- Tool failures can be returned as observations without surrendering host control.
- Adding tools should not require hard-coding the decision order into the loop.

Lesson 4 introduces:

- State is what the current run needs; memory is what the application deliberately carries into a future run.
- Conversation history is only one part of state; host-owned control metadata should remain structured and authoritative outside the model.
- Most observations are ephemeral working state, not durable memory.
- Durable memory should be selected, scoped, revisable, and deletable.
- Memory only affects a model when the application retrieves it and injects relevant context.
- A large context window is not a substitute for persistence, retrieval, ownership, correction, or deletion.
- Long-term memory creates additional privacy, security, staleness, and prompt-injection risks.

## Course progress

- Current module: Module 03 — AI Agents
- Current lesson: Lesson 4 — State and Memory
- Completed: Lesson 1 — What is an AI Agent?; Lesson 2 — Tool Calling from Scratch in Python; Lesson 3 — The Agent Loop
- Next: Work through the Lesson 4 state-and-memory notebook, compare ephemeral working state with durable travel preferences, then move to Lesson 5 — Planning.

Keep this section small and update it when a lesson is genuinely completed. It is a continuity marker, not a project-management system.

## Continuing the course

When asked to continue the course, do not restart from the beginning. Before working:

1. Read this file and the progress section above.
2. Read the relevant module documentation under `docs/`.
3. Inspect related playground, project, and test code if present.
4. Continue from the current lesson and preserve useful existing work.

When a useful experiment is completed, consider whether it contains durable learning material worth adding to the module documentation before moving on.

## Documentation rules

The high-level course map lives at `docs/AI_Engineering_Course_Map_2026_07_29.html`. Detailed module material belongs in a dedicated folder such as `docs/module-03-ai-agents/`.

The module `index.html` is a concise learning map: it should explain each lesson's core concepts, give a short briefing for examples, and link to the detailed lesson exercise. Do not duplicate a long notebook/code walkthrough inside the module index.

Detailed hands-on lessons should use a dedicated browser page such as `lesson-03-agent-loop.html`. That page mirrors the runnable notebook and is where the full teaching walkthrough belongs.

Update documentation incrementally when work creates durable value, such as:

- core concepts or reusable mental models
- architecture diagrams and important design trade-offs
- reusable examples and exercises
- mini-project outcomes and lessons learned
- production and operational considerations

Do not turn every chat or coding session into documentation. Keep the course concise enough to remain a useful long-term reference.

### Detailed lesson pages must be followable on their own

A lesson-specific HTML page should let a reader follow the whole exercise in the browser without opening an editor.

- Mirror the notebook sequence: short explanation, actual cell code, then what its output demonstrates.
- Use the real notebook code, not unrelated pseudo-code, and keep the browser page and notebook in the same conceptual order.
- Show representative output where the trace or failure path is the lesson.
- Link to the real notebook as the runnable companion.
- Elide genuinely uninteresting scaffolding when that keeps the browser page readable; the notebook remains the complete runnable artifact.
- The Module 03 Lesson 2 and Lesson 3 dedicated HTML pages are the reference pattern for this approach.

When editing documentation:

- Preserve the existing visual style.
- Keep links between the course map, module pages, and examples valid.
- Use relative links only between pages inside `docs/`.
- GitHub Pages publishes `docs/` as the site root, so relative links that escape `docs/` will fail on the published site.
- Link to code/notebooks outside `docs/` with an absolute GitHub URL. Use a raw GitHub URL when the intended action is to download a notebook.
- Keep HTML self-contained unless shared assets clearly improve maintainability.
- Do not rewrite unrelated content.
- Check both narrow and wide layouts when making material visual changes.

## Code organisation

Use these locations as the repository grows:

```text
docs/         # course map and durable module material
playgrounds/  # focused, inspectable experiments
projects/     # realistic multi-file applications and mini-projects
src/          # shared application code, only when reuse justifies it
tests/        # tests for meaningful logic
```

Do not create empty directories for appearance. A lesson may begin with a focused playground; promote code into a project or shared `src/` package only when its scope warrants that structure. Treat any existing `examples/` content as existing work to preserve; place new learning experiments in `playgrounds/` unless nearby conventions make another location clearer.

### Playgrounds and examples are notebook-first

Hands-on material is written as Jupyter notebooks. A notebook interleaves explanation, a small runnable cell, and its output, which is how this course is meant to be followed.

Playgrounds are grouped by module, and the whole course shares one environment:

```text
playgrounds/
    requirements.txt             # shared by every playground; one venv for the course
    <nn>-<module-name>/          # e.g. 03-ai-agents
        <topic>/                 # e.g. tool-calling-from-scratch or agent-loop
            <topic>.ipynb        # primary teaching surface: narrative + runnable cells
            <topic>.py           # optional: logic worth importing, testing, or running headless
            test_<topic>.py      # tests import the .py module, never the notebook
            README.md            # how to run it, and what to observe
```

There is no per-playground `requirements.txt`. When a lesson needs a new dependency, add it to `playgrounds/requirements.txt` with a comment naming what needs it, so a reader who set up the environment in Lesson 2 can still run later lessons.

Conventions:

- The notebook is the artifact a reader opens first. Order its cells to build up the mechanism step by step, with a markdown cell before each code cell explaining what the next cell demonstrates and what to look for in the output.
- Keep cells small enough to reason about in isolation. One idea per cell.
- When logic deserves tests or reuse, factor it into a sibling `.py` module and have the notebook import it. Do not duplicate the same implementation in both places, and do not try to unit-test notebook cells.
- Notebooks read configuration from `.env` like any other code. Never hardcode a key, and never commit a notebook whose stored output contains a key, token, or personal data.
- Committing outputs is encouraged when they are the lesson — a visible tool call, a request/response trace, a token count. Clear outputs that are merely noisy, enormous, or nondeterministic churn.
- A plain `.py` script is still the right choice when a piece is genuinely a program rather than a lesson, such as a project entry point or a test suite.

## Engineering standards

- Write clean Python with type hints where they improve interfaces and comprehension.
- Prefer small, focused functions and explicit data/control flow.
- Handle expected errors explicitly, especially provider, network, parsing, tool, and timeout failures.
- Test meaningful deterministic logic; isolate model calls behind narrow interfaces where practical.
- Load local secrets from `.env`; never commit API keys or credentials.
- Add or update `.env.example` when an exercise introduces required configuration, using placeholders only.
- Avoid unnecessary framework abstractions and dependencies.
- Document important design decisions and non-obvious trade-offs near the relevant code or lesson.
- Make cost, latency, permissions, termination, and failure behavior visible in agentic code.
