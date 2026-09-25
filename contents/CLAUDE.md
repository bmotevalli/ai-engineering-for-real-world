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
2. **Plain Python implementation** — provider SDK, explicit control flow, no framework,
   built up as notebook cells (see the notebook-first rules in `AGENTS.md`).
3. **Run it / show the trace** — make the mechanism observable (requests, tool calls, state).
4. **Trade-offs** — failure modes, cost, latency, safety, when this breaks in production.
5. **Framework comparison**, only after the mechanism is understood: what it abstracts,
   what the hand-rolled equivalent was, benefits, disadvantages, when not to use it.

Explain as you go in the chat response; put only the durable parts in `docs/`.

The lesson page and the notebook are written together, not sequentially. Decide the cell
sequence first, then write both from it, so the page walks through the same cells in the
same order. If they drift, the page is wrong — it is the surface most readers use.

## Finishing a lesson

Before declaring a lesson done:

- [ ] Working code committed to the right place — `playgrounds/<nn>-<module>/<topic>/`, for
      example `playgrounds/03-ai-agents/tool-calling-from-scratch/` — created only when the
      lesson actually needs it, with no empty scaffolding. The teaching artifact is a
      **notebook**; testable logic lives in a sibling `.py` the notebook imports.
- [ ] The lesson page walks through the notebook's cells inline — explanation, real cell
      code, what the output shows — and *then* links to the notebook. A page that only links
      to code is not finished.
- [ ] `.env.example` updated if the lesson introduced new configuration (placeholders only),
      and any new dependency added to the shared `playgrounds/requirements.txt`.
- [ ] Module documentation updated **only** with durable learning value — concepts, diagrams,
      distinctions, trade-offs, exercises, links to the playground code.
- [ ] `AGENTS.md` progress section updated (completed lesson, current lesson, next step).
- [ ] Links between course map, module page, and code still valid. Relative links **only
      within `docs/`**; link to `playgrounds/`, `projects/`, or any other out-of-`docs/` code
      with an absolute `https://github.com/bmotevalli/ai-engineering-for-real-world/tree/main/...`
      URL, because GitHub Pages publishes `docs/` as the site root and a `../../` escape 404s.

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

## Authoring notebooks

- Create and modify `.ipynb` files with the `NotebookEdit` tool, and read them with `Read`,
  which renders cells and outputs. Do not hand-write notebook JSON with `Write`, and do not
  edit it as text with `Edit` — that corrupts cell ids and output structure.
- Do not fabricate cell outputs. Either execute the notebook and keep the real output, or
  leave the cell unexecuted and say in the chat that it has not been run. A committed output
  is a claim that the code ran.
- Notebook diffs are noisy. Re-running everything before committing churns unrelated cells,
  so re-run only what the change actually affects.

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

## Current context (2026-08-31)

- Active module: **Module 03 — AI Agents**. See the `## Course progress` section of
  `AGENTS.md` for the authoritative lesson state.
- Lesson 2's playground lives at `playgrounds/03-ai-agents/tool-calling-from-scratch/` and is
  currently a script, not a notebook — it predates the notebook-first rule. New playgrounds
  are notebooks; leave this one as it is unless asked to convert it.
- `projects/`, `src/`, and `tests/` do not exist yet. Create them when the first real
  exercise needs them.
- The Lesson 2 walkthrough in the module page was generated by extracting fragments verbatim
  from `tool_calling.py`. If that script changes, the page's code blocks must be updated to
  match — they are presented as pasteable in sequence, and that claim is checkable.

If this section disagrees with `AGENTS.md`, `AGENTS.md` is correct — fix this file.
