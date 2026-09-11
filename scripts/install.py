#!/usr/bin/env python3
"""Copy this Metabase skill into user-level (or project) agent skill folders.

Works on macOS, Linux, and Windows. Stdlib only.

  python3 scripts/install.py
  python3 scripts/install.py --project
  python3 scripts/install.py --agent cursor
  py -3 scripts/install.py          # Windows launcher
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
IGNORE = shutil.ignore_patterns(".git", ".git/*", "__pycache__", "*.pyc", ".DS_Store", "graph/index.json")

AGENT_DIRS = {
    "cursor": [HOME / ".cursor" / "skills" / "metabase", HOME / ".agents" / "skills" / "metabase"],
    "claude-code": [HOME / ".claude" / "skills" / "metabase"],
    "codex": [HOME / ".codex" / "skills" / "metabase"],
    "gemini": [HOME / ".gemini" / "antigravity" / "skills" / "metabase"],
    "opencode": [HOME / ".config" / "opencode" / "skills" / "metabase"],
    "windsurf": [HOME / ".codeium" / "windsurf" / "skills" / "metabase"],
}

DEFAULT_AGENTS = list(AGENT_DIRS.keys())


def copy_skill(dest: Path) -> None:
    dest = dest.resolve()
    if dest == ROOT.resolve():
        print(f"Skip (already here) → {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ROOT, dest, ignore=IGNORE)
    print(f"Installed → {dest}")


def main() -> int:
    p = argparse.ArgumentParser(description="Install Metabase skill for local AI agents")
    p.add_argument("--project", action="store_true", help="Install into the current project's .cursor/skills")
    p.add_argument(
        "--agent",
        action="append",
        choices=sorted(AGENT_DIRS),
        help="Only these agents (repeatable). Default: all known folders",
    )
    args = p.parse_args()

    if args.project:
        cwd = Path.cwd()
        copy_skill(cwd / ".cursor" / "skills" / "metabase")
        copy_skill(cwd / ".agents" / "skills" / "metabase")
        print("Project install done. Start a new agent chat.")
        return 0

    names = args.agent or DEFAULT_AGENTS
    dests: list[Path] = []
    for name in names:
        dests.extend(AGENT_DIRS[name])
    for dest in dests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy_skill(dest)

    print()
    print("Done. Start a new conversation, for example:")
    print("  How do I give each customer only their own rows in Metabase?")
    print(f"Python in use: {sys.executable} ({sys.version.split()[0]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
