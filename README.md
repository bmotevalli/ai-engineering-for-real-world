# AI Engineering for the Real World

This repository combines the AI engineering course with practical applications.

- [Course contents](contents/README.md): documentation, notebooks, playgrounds and course guidance.
- [ID extraction project](projects/id-extraction/README.md): local Ollama-based document extraction.
- [Course progress](contents/AGENTS.md#course-progress): the authoritative course progress record.
- [License](contents/LICENSE).

```text
contents/                 # Existing course material and supporting files
projects/
  id-extraction/          # Local identity-document extraction application
.github/workflows/        # Repository automation; Pages serves contents/docs
```

Run course commands from `contents/` and extraction commands from `projects/id-extraction/`.
Each area keeps its own dependency setup. Private identity documents, extraction results,
virtual environments and downloaded model weights are excluded from Git.

```bash
cd projects/id-extraction
bash scripts/serve-ollama.sh
# In another terminal, from the same directory:
.venv/bin/id-extract /path/to/document.jpg --context 8192
```
