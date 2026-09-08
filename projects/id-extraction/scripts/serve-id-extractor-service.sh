#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
umask 077
mkdir -p .runtime
rm -f .runtime/id-extractor.sock
export ID_EXTRACTION_SOCKET="$PWD/.runtime/id-extractor.sock"
.venv/bin/python -m local_id_extractor.service &
worker_pid=$!
for _ in $(seq 1 50); do
  if [ -S "$ID_EXTRACTION_SOCKET" ]; then
    chmod 600 "$ID_EXTRACTION_SOCKET"
    break
  fi
  sleep 0.1
done
if [ ! -S "$ID_EXTRACTION_SOCKET" ]; then
  kill "$worker_pid" 2>/dev/null || true
  exit 1
fi
wait "$worker_pid"
