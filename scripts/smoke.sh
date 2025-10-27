#!/usr/bin/env bash
set -euo pipefail

echo "[SMOKE] Checking environment..."
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "[SMOKE][ERROR] OPENAI_API_KEY is not set (in env or .env)." >&2
  exit 1
fi

echo "[SMOKE] 1) Enhance-only test"
python -m lazy_ptt.cli --verbose enhance-text --text "PTT smoke test: enhance-only"

if [[ -n "${SMOKE_AUDIO:-}" ]]; then
  if [[ ! -f "$SMOKE_AUDIO" ]]; then
    echo "[SMOKE][WARN] SMOKE_AUDIO set but file not found: $SMOKE_AUDIO (skipping STT test)" >&2
  else
    echo "[SMOKE] 2) STT + enhance on file: $SMOKE_AUDIO"
    python -m lazy_ptt.cli --verbose process-audio "$SMOKE_AUDIO"
  fi
else
  echo "[SMOKE] Set SMOKE_AUDIO=/path/to/file.wav to run STT test"
fi

echo "[SMOKE] Done"

