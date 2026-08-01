#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -m pip install --user --upgrade "$SOURCE_DIR"

BIN_DIR="$(python3 -m site --user-base)/bin"
PATH_LINE="export PATH=\"$BIN_DIR:\$PATH\""
SHELL_RC="${HOME}/.zshrc"

if ! grep -Fq "$PATH_LINE" "$SHELL_RC" 2>/dev/null; then
  printf '\n# BlackMamba local CLI tools\n%s\n' "$PATH_LINE" >> "$SHELL_RC"
fi

echo "Installed: $BIN_DIR/visual-index"
echo "Reload shell: source ~/.zshrc"
echo "Run: visual-index /path/to/project --open"
