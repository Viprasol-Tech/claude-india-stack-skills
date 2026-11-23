#!/usr/bin/env bash
# Installs every India Stack skill into ~/.claude/skills (Claude Code personal skills).
set -euo pipefail
DEST="${1:-$HOME/.claude/skills}"
SRC="$(cd "$(dirname "$0")" && pwd)/plugins/india-stack/skills"
mkdir -p "$DEST"
for d in "$SRC"/*/; do
  n=$(basename "$d")
  rm -rf "${DEST:?}/$n"
  cp -r "$d" "$DEST/$n"
  echo "installed $n"
done
echo
echo "Done. Restart Claude Code, then try: \"Split GST for an invoice from Maharashtra to Karnataka ...\""
