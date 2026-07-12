"""Run the local checks required before opening or updating a pull request."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(label: str, command: list[str], root: Path) -> int:
    """Run one command, print a heading, and return its exit code."""
    print(f"\n== {label} ==")
    print(" ".join(command))
    return subprocess.call(command, cwd=root)


def main() -> int:
    """Run formatting, linting, repository validation, and fast QA tests."""
    root = Path(__file__).resolve().parents[1]
    checks = [
        ("Ruff format check", [sys.executable, "-m", "ruff", "format", ".", "--check"]),
        ("Ruff lint", [sys.executable, "-m", "ruff", "check", "."]),
        ("Repository validation", [sys.executable, "scripts/validate_repository.py"]),
        ("Fast QA tests", [sys.executable, "scripts/run_fast_tests.py"]),
    ]
    for label, command in checks:
        code = run(label, command, root)
        if code != 0:
            print(f"\nPre-PR checks failed at: {label}")
            return code
    print("\nAll pre-PR checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
