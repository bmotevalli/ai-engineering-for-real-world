# Claude Code Guidance

## Read `AGENTS.md` first

`AGENTS.md` is the canonical, assistant-independent guidance for this repository. Read it
before doing any work here. It owns:

- repository purpose and learner profile
- teaching philosophy and first-principles sequencing
- technology preferences and course priority order
- the Module 03 lesson sequence and Lesson 1 outcomes
- **course progress** (the single source of truth)
- documentation rules and code organisation
- engineering standards and secrets handling

Do not restate that material here. This file only covers behaviour that is specific to
working through Claude Code.

## Canonical progress

Course progress lives in **one place**: the `## Course progress` section of `AGENTS.md`.

- Read it at the start of any session that continues the course.
- Update it only when a lesson is genuinely finished, and keep it short.
- Do not create a second progress file, changelog, or status tracker anywhere else.
- `README.md` may reference progress for human readers, but `AGENTS.md` wins on conflict.

## Starting a session

When asked to "continue", "do the next lesson", or "continue AI Agents":

1. Read `CLAUDE.md` (this file) and `AGENTS.md`, including the progress section.
2. Read the active module page, currently [docs/module-03-ai-agents/index.html](docs/module-03-ai-agents/index.html),
   and the relevant part of [the course map](docs/AI_Engineering_Course_Map_2026_07_29.html).
3. Inspect any existing playground/project code for the current module.
4. Resume from the current lesson. **Never restart a module** unless explicitly asked.

State briefly which lesson is being resumed before starting work, so a wrong reading of
progress can be corrected cheaply.

## How to run a lesson

A lesson is a teaching turn, not just a code drop. Shape it as:

1. **Concept** — the mental model and why it matters, at senior-engineer level.
2. **Plain Python implementation** — provider SDK, explicit control flow, no framework.
3. **Run it / show the trace** — make the mechanism observable (requests, tool calls, state).
4. **Trade-offs** — failure modes, cost, latency, safety, when this breaks in production.
5. **Framework comparison**, only after the mechanism is understood: what it abstracts,
   what the hand-rolled equivalent was, benefits, disadvantages, when not to use it.

Explain as you go in the chat response; put only the durable parts in `docs/`.

## Finishing a lesson

Before declaring a lesson done:

- [ ] Working code committed to the right place (`playgrounds/<module>/<NN-topic>/`), created
      only when the lesson actually needs it — no empty scaffolding.
- [ ] `.env.example` updated if the lesson introduced new configuration (placeholders only).
- [ ] Module documentation updated **only** with durable learning value — concepts, diagrams,
      distinctions, trade-offs, exercises, links to the playground code.
- [ ] `AGENTS.md` progress section updated (completed lesson, current lesson, next step).
- [ ] Links between course map, module page, and code still valid and relative.

Do not transcribe the conversation into the docs. Curate.

## Editing the HTML documentation

The course docs are large, hand-styled, self-contained HTML files (the course map is ~220KB).

- Locate sections with Grep/Glob, or read targeted ranges — do not read a whole large file
  into context without reason.
- Use `Edit` for surgical changes. Never regenerate a doc page wholesale.
- Match the existing CSS classes and visual language (`.lesson`, `.card`, `.component`,
  `.compare`, `.principle`, `.exercise`, `.next`, `pre` flow diagrams) rather than inventing
  new styling.
- Each module page ends with a `.next` block describing the following lesson; keep it accurate.
- Check the responsive breakpoints (800px / 520px) if a change is structurally visual.

## Environment notes

- Platform is **Windows / PowerShell**. The Bash tool is Git Bash — use POSIX syntax there
  and PowerShell syntax in the PowerShell tool; do not mix them.
- Prefer Read/Edit/Write/Grep/Glob over shell equivalents for file work.
- Reference files as clickable relative markdown links, e.g. [AGENTS.md](AGENTS.md).

## Claude behaviour in this repository

- **Do not spawn subagents** unless explicitly asked. Lessons are conversational; a subagent
  loses the teaching thread.
- Ask before installing dependencies or adding a framework. Minimal dependencies is a course
  rule, not just a style preference.
- Do not commit or push unless asked. When asked, never commit `.env` or any credential;
  `.env` is git-ignored and only `.env.example` is tracked.
- Never invent API keys, fake model responses, or stub a "working" demo that was not run.
  If a model call could not be executed, say so plainly.
- Default to the current Claude models (`claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5-20251001`)
  when writing Anthropic examples; use the `claude-api` skill rather than recalling API details
  from memory. Provider-neutral lessons may use OpenAI/Ollama/LiteLLM where the lesson calls for it.
- When a lesson produces something worth showing visually (an architecture diagram, a
  comparison table), an Artifact is fine — but the durable version still belongs in `docs/`.

## Current context (2026-08-18)

- Active module: **Module 03 — AI Agents**.
- Completed: Lesson 1 — What is an AI Agent?
- Next learning task: **Lesson 2 — Tool Calling from Scratch in Python**, implementing
  `User -> LLM -> tool request -> Python executes tool -> tool result -> LLM -> final answer`
  directly against a provider SDK, before any agent framework.
- `playgrounds/`, `projects/`, `src/`, and `tests/` do not exist yet. Create them when the
  first real exercise needs them.

If this section disagrees with `AGENTS.md`, `AGENTS.md` is correct — fix this file.
