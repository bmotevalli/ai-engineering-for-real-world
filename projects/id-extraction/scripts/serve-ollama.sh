#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
umask 077
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$PWD/.runtime/models"
export OLLAMA_NO_CLOUD=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_MAX_QUEUE=1
export OLLAMA_CONTEXT_LENGTH=4096
export OLLAMA_KEEP_ALIVE=5m
export OLLAMA_DEBUG=0
export OLLAMA_DEBUG_LOG_REQUESTS=false
export OLLAMA_NOHISTORY=1
mkdir -p "$OLLAMA_MODELS"
exec .runtime/ollama/bin/ollama serve
