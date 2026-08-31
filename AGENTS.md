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

## Course progress

- Current module: Module 03 — AI Agents
- Current lesson: Lesson 2 — Tool Calling from Scratch in Python
- Completed: Lesson 1 — What is an AI Agent?
- Next: Complete the Lesson 2 tool-calling exercise and inspect its protocol trace before introducing the iterative agent loop in Lesson 3.

Keep this section small and update it when a lesson is genuinely completed. It is a continuity marker, not a project-management system.

## Continuing the course

When asked to continue the course, do not restart from the beginning. Before working:

1. Read this file and the progress section above.
2. Read the relevant module documentation under `docs/`.
3. Inspect related playground, project, and test code if present.
4. Continue from the current lesson and preserve useful existing work.

When a useful experiment is completed, consider whether it contains durable learning material worth adding to the module documentation before moving on.

## Documentation rules

The high-level course map lives at `docs/AI_Engineering_Course_Map_2026_07_29.html`. Detailed module material belongs in a dedicated folder such as `docs/module-03-ai-agents/`; its `index.html` is the module landing/training page, with lesson-specific pages and assets added only if the module outgrows one page.

Update documentation incrementally when work creates durable value, such as:

- core concepts or reusable mental models
- architecture diagrams and important design trade-offs
- reusable examples and exercises
- mini-project outcomes and lessons learned
- production and operational considerations

Do not turn every chat or coding session into documentation. Keep the course concise enough to remain a useful long-term reference.

### Lesson pages must be followable on their own

A module page is not an index that points at code. A reader should be able to follow the
whole lesson in the browser without opening an editor.

- Walk through the implementation **in the page**, as the sequence of cells the notebook
  runs: a short explanation, then the actual cell code, then what its output shows.
- Use the real code from the notebook, not paraphrased pseudo-code, and keep the two in the
  same order so a reader can move between them without losing their place.
- Show representative output where the output is the point, such as a tool request, a
  trace, or an error path.
- Then link to the notebook in the repository as the runnable companion, using the absolute
  GitHub URL form described above. The link accompanies the explanation; it does not
  replace it.
- Elide genuinely uninteresting scaffolding, such as long import blocks or fixture data, so
  the page stays readable. The notebook remains the complete version.

The Lesson 2 section of `docs/module-03-ai-agents/index.html` is the reference example of
this shape: numbered steps, each with the real code and the reason it exists, ending with
the command to run and what the output should look like.

When editing documentation:

- Preserve the existing visual style.
- Keep links between the course map, module pages, and examples valid.
- Use relative links **only between pages inside `docs/`**. GitHub Pages publishes `docs/` as
  the site root (see `.github/workflows/publish-docs.yml`), so a relative link that escapes it,
  such as `../../playgrounds/...`, works locally but returns 404 on the published site.
- Link to code outside `docs/` with an absolute GitHub URL, for example
  `https://github.com/bmotevalli/ai-engineering-for-real-world/tree/main/playgrounds/<name>`.
  A directory URL is usually the best target because GitHub renders its `README.md`.
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

Hands-on material is written as Jupyter notebooks. A notebook interleaves explanation, a
small runnable cell, and its output, which is how this course is meant to be followed.

Playgrounds are grouped by module, and the whole course shares one environment:

```text
playgrounds/
    requirements.txt             # shared by every playground; one venv for the course
    <nn>-<module-name>/          # e.g. 03-ai-agents
        <topic>/                 # e.g. tool-calling-from-scratch
            <topic>.ipynb        # primary teaching surface: narrative + runnable cells
            <topic>.py           # optional: logic worth importing, testing, or running headless
            test_<topic>.py      # tests import the .py module, never the notebook
            README.md            # how to run it, and what to observe
```

There is no per-playground `requirements.txt`. When a lesson needs a new dependency, add it
to `playgrounds/requirements.txt` with a comment naming what needs it, so a reader who set up
the environment in Lesson 2 can still run Lesson 9.

Conventions:

- The notebook is the artifact a reader opens first. Order its cells to build up the
  mechanism step by step, with a markdown cell before each code cell explaining what the
  next cell demonstrates and what to look for in the output.
- Keep cells small enough to reason about in isolation. One idea per cell.
- When logic deserves tests or reuse, factor it into a sibling `.py` module and have the
  notebook import it. Do not duplicate the same implementation in both places, and do not
  try to unit-test notebook cells.
- Notebooks read configuration from `.env` like any other code. Never hardcode a key, and
  never commit a notebook whose stored output contains a key, token, or personal data.
- Committing outputs is encouraged when they *are* the lesson — a visible tool call, a
  request/response trace, a token count. Clear outputs that are merely noisy, enormous, or
  nondeterministic churn.
- A plain `.py` script is still the right choice when a piece is genuinely a program rather
  than a lesson, such as a project entry point or a test suite.

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
