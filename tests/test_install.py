from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_install_help() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "install.py"), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--project" in proc.stdout
    assert "--agent" in proc.stdout


def test_package_metadata() -> None:
    text = (ROOT / "pyproject.toml").read_text()
    assert 'name = "metabase-skill"' in text
    assert "metabase_skill:main" in text
