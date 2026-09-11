"""Run the packaged skill installer (same behavior as scripts/install.py)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "payload"


def main(argv: list[str] | None = None) -> int:
    install_py = PAYLOAD / "scripts" / "install.py"
    if not install_py.is_file():
        sys.stderr.write(
            "Packaged skill files are missing. Install from GitHub until the "
            "package is on PyPI:\n"
            "  pip install \"git+https://github.com/IshanSarkar/metabase-skill.git\"\n"
            "  metabase-skill\n"
        )
        return 1

    saved = sys.argv[:]
    sys.argv = [str(install_py), *(argv if argv is not None else saved[1:])]
    try:
        runpy.run_path(str(install_py), run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    finally:
        sys.argv = saved
    return 0
