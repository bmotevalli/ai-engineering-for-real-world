#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
umask 077
mkdir -p .runtime/downloads .runtime/ollama
archive=.runtime/downloads/ollama-linux-amd64.tar.zst
if [ ! -f "$archive" ]; then
  curl -fL --retry 3 https://github.com/ollama/ollama/releases/download/v0.33.3/ollama-linux-amd64.tar.zst -o "$archive.part"
  mv "$archive.part" "$archive"
fi
echo 'c13cea8f3389db4145f8a6cb88d1747242a48639d7c13e3bda7c1ebdc6eebb2f  .runtime/downloads/ollama-linux-amd64.tar.zst' | sha256sum -c -
tar --zstd -xf "$archive" -C .runtime/ollama
