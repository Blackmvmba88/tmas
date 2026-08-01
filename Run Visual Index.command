#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
printf "Project folder to scan: "
read -r PROJECT_PATH
[[ -n "$PROJECT_PATH" ]] || { echo "No project selected."; exit 1; }
python3 -m visual_index "$PROJECT_PATH" --open || python3 "$SCRIPT_DIR/visual_index/cli.py" "$PROJECT_PATH" --open
