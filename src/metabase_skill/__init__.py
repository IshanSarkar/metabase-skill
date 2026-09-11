"""Install the Metabase Agent Skill into local AI agent folders."""

from __future__ import annotations

__version__ = "1.0.0"


def main(argv: list[str] | None = None) -> int:
    from metabase_skill.cli import main as cli_main

    return cli_main(argv)
