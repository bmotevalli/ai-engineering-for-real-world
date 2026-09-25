# Workspace guidance

- Course material and its authoritative progress record live in `contents/`.
  Read `contents/AGENTS.md` before working on the course; its paths are relative to `contents/`.
- Practical applications live under `projects/`. The local identity-document extractor
  is in `projects/id-extraction/`; run its commands and tests from that directory.
- Preserve the separation between course dependencies and project environments.
- Keep private images, extraction results, credentials, environments and model weights out of Git.
- Repository automation stays in `.github/`; GitHub Pages publishes `contents/docs/`.
