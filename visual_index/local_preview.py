from __future__ import annotations


def render_local_preview_runner(port: int = 8765) -> str:
    if not 1024 <= port <= 65535:
        raise ValueError("preview port must be between 1024 and 65535")
    return f'''#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${{BM_PREVIEW_PORT:-{port}}}"
URL="http://127.0.0.1:${{PORT}}/blackmamba-neon-glass-demo.html"

cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required to serve the local preview" >&2
  exit 1
fi

cleanup() {{
  if [[ -n "${{SERVER_PID:-}}" ]]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}}
trap cleanup EXIT INT TERM

python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/blackmamba-neon-glass-preview.log 2>&1 &
SERVER_PID=$!

for _ in {{1..40}}; do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

if ! curl -fsS "$URL" >/dev/null 2>&1; then
  echo "error: preview server did not start; see /tmp/blackmamba-neon-glass-preview.log" >&2
  exit 1
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
  open "$URL"
else
  echo "Open: $URL"
fi

echo "BlackMamba Neon Glass preview: $URL"
echo "Press Ctrl+C to stop."
wait "$SERVER_PID"
'''
