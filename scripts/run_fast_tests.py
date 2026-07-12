"""Run the deterministic pytest suite only when QA test files exist.

This infrastructure helper prevents a fresh scaffold from failing CI with pytest exit code 5
(no tests collected). Once QA adds non-empty test files, the normal fast suite runs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def has_nonempty_tests(root: Path) -> bool:
    """Return whether the repository contains at least one non-empty pytest file."""
    tests_dir = root / "tests"
    return any(path.stat().st_size > 0 for path in tests_dir.rglob("test_*.py"))


def main() -> int:
    """Run fast pytest markers or exit successfully when QA has not added tests yet."""
    root = Path(__file__).resolve().parents[1]
    if not has_nonempty_tests(root):
        print("No non-empty QA test files exist yet; skipping pytest.")
        return 0

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        "not slow and not ollama and not e2e",
    ]
    return subprocess.call(command, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
