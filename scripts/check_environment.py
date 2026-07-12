"""Validate the shared development environment without running project algorithms."""

from __future__ import annotations

import importlib.metadata
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

REQUIRED_PACKAGES = {
    "numpy": "2.5.1",
    "PyYAML": "6.0.3",
    "requests": "2.34.2",
    "streamlit": "1.59.1",
    "tqdm": "4.68.4",
    "pre-commit": "4.6.0",
    "pytest": "9.1.1",
    "pytest-cov": "7.1.0",
    "ruff": "0.15.21",
}


def package_status() -> list[tuple[str, str, str]]:
    """Return package, installed version, and expected version rows."""
    result: list[tuple[str, str, str]] = []
    for package, expected in REQUIRED_PACKAGES.items():
        try:
            installed = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed = "MISSING"
        result.append((package, installed, expected))
    return result


def command_status(name: str) -> str:
    """Return the absolute command path or a readable missing marker."""
    return shutil.which(name) or "NOT FOUND"


def ollama_status() -> str:
    """Return a non-fatal Ollama API status string."""
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=2) as response:
            payload = json.load(response)
        names = sorted(model.get("name", "") for model in payload.get("models", []))
        return f"reachable at {base_url}; models={names}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return f"not reachable at {base_url} ({exc.__class__.__name__}); local Ollama is optional"


def main() -> int:
    """Print environment diagnostics and fail only for required development tooling."""
    root = Path(__file__).resolve().parents[1]
    print(f"Repository: {root}")
    print(f"Python: {sys.version.split()[0]}")

    version_ok = (3, 13) <= sys.version_info[:2] < (3, 14)
    if not version_ok:
        print("ERROR: Python 3.13 is required.")

    package_ok = True
    print("\nPython packages:")
    for package, installed, expected in package_status():
        marker = "OK" if installed == expected else "MISMATCH"
        print(f"- {package}: {installed} (expected {expected}) [{marker}]")
        package_ok &= installed == expected

    print("\nCommands:")
    for command in ("git", "docker", "ollama"):
        print(f"- {command}: {command_status(command)}")

    required_paths = [
        root / "pyproject.toml",
        root / ".vscode" / "settings.json",
        root / ".devcontainer" / "devcontainer.json",
        root / ".pre-commit-config.yaml",
        root / "planning" / "jira" / "jira_import_tasks.csv",
    ]
    paths_ok = True
    print("\nRequired repository setup:")
    for path in required_paths:
        exists = path.exists()
        print(f"- {path.relative_to(root)}: {'OK' if exists else 'MISSING'}")
        paths_ok &= exists

    print(f"\nOllama: {ollama_status()}")
    print("\nEnvironment status:", "PASS" if version_ok and package_ok and paths_ok else "FAIL")
    return 0 if version_ok and package_ok and paths_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
