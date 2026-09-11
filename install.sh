#!/usr/bin/env bash
# Install this Metabase skill for local AI agents (Cursor, Claude Code, Codex, …).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GLOBAL=1
AGENTS=()

usage() {
  cat <<'EOF'
Install the Metabase docs skill for AI coding agents.

Usage:
  ./install.sh                  # copy into every detected user-level skill folder
  ./install.sh --project        # copy into this repo: .cursor/skills/metabase
  ./install.sh --agent cursor   # only Cursor (~/.cursor/skills/metabase)

After install, open a new agent chat and ask a Metabase question.
No slash command required — the agent should pick the skill up from its description.

One-liner from GitHub (any Agent Skills client):
  npx skills add <owner>/<repo> -g -y
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --project) GLOBAL=0; shift ;;
    --agent) AGENTS+=("$2"); shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

copy_skill() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  mkdir -p "$dest"
  rsync -a --delete \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude '.DS_Store' \
    "$ROOT/" "$dest/"
  echo "Installed → $dest"
}

if [[ "$GLOBAL" -eq 0 ]]; then
  copy_skill "$(pwd)/.cursor/skills/metabase"
  copy_skill "$(pwd)/.agents/skills/metabase"
  echo "Project install done. Restart the agent / start a new chat."
  exit 0
fi

declare -a DESTINATIONS=()
if [[ ${#AGENTS[@]} -eq 0 ]]; then
  DESTINATIONS=(
    "$HOME/.cursor/skills/metabase"
    "$HOME/.agents/skills/metabase"
    "$HOME/.claude/skills/metabase"
    "$HOME/.codex/skills/metabase"
    "$HOME/.codeium/windsurf/skills/metabase"
    "$HOME/.gemini/antigravity/skills/metabase"
    "$HOME/.config/opencode/skills/metabase"
  )
else
  for a in "${AGENTS[@]}"; do
    case "$a" in
      cursor) DESTINATIONS+=("$HOME/.cursor/skills/metabase" "$HOME/.agents/skills/metabase") ;;
      claude|claude-code) DESTINATIONS+=("$HOME/.claude/skills/metabase") ;;
      codex) DESTINATIONS+=("$HOME/.codex/skills/metabase") ;;
      *) echo "Unknown --agent $a (use cursor, claude-code, or codex)" >&2; exit 1 ;;
    esac
  done
fi

for dest in "${DESTINATIONS[@]}"; do
  parent="$(dirname "$dest")"
  mkdir -p "$parent"
  copy_skill "$dest"
done

echo
echo "Done. Start a new conversation and ask something like:"
echo "  How do I give each customer only their own rows in Metabase?"
echo "Python 3.9+ is required for scripts/lookup.py (stdlib only)."
