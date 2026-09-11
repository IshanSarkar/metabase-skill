#!/usr/bin/env bash
# Unix wrapper. On Windows use:  py -3 scripts/install.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$ROOT/scripts/install.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$ROOT/scripts/install.py" "$@"
fi
echo "Python 3.9+ is required. Install Python, then run: python3 scripts/install.py" >&2
exit 1
