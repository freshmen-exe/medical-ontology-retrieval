"""Validate repository structure and common policy violations."""

from __future__ import annotations

import os
from pathlib import Path

REQUIRED_PATHS = [
    "README.md",
    "CONTRIBUTING.md",
    "DATA_NOTICE.md",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    ".pre-commit-config.yaml",
    ".github/workflows/ci.yml",
    ".devcontainer/devcontainer.json",
    ".vscode/settings.json",
    "docs/problem_statement/original/SOURCE.md",
    "planning/jira/jira_import_tasks.csv",
    "planning/jira/jira_task_catalog.csv",
    "planning/jira/sprint_calendar.csv",
    "planning/meetings/2026-07-12-kickoff.md",
    "references/source_registry.md",
    "reports/latex",
    "slides",
    "videos",
    "src/medical_ontology",
    "tests",
]

FORBIDDEN_TRACKED_SUFFIXES = {".pyc", ".pkl", ".npy", ".npz", ".zip"}
FORBIDDEN_DIRECTORY_NAMES = {"__pycache__", ".pytest_cache", ".ruff_cache", ".venv"}
FORBIDDEN_DEPENDENCY_NAMES = {
    "faiss",
    "hnswlib",
    "annoy",
    "chromadb",
    "langchain",
    "llama-index",
    "llama_index",
    "scikit-learn",
    "sklearn",
}


def main() -> int:
    """Return non-zero when required setup or repository policy is violated."""
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            errors.append(f"Missing required path: {relative}")

    for path in root.rglob("*"):
        if any(part in FORBIDDEN_DIRECTORY_NAMES for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES:
            errors.append(
                f"Generated/binary file should not be committed: {path.relative_to(root)}"
            )
        if path.is_file() and path.stat().st_size > 2 * 1024 * 1024:
            allowed = (
                "data/raw" in path.as_posix()
                or "docs/problem_statement/original" in path.as_posix()
            )
            if not allowed:
                errors.append(f"File exceeds 2 MiB policy: {path.relative_to(root)}")

    dependency_text = "\n".join(
        (root / filename).read_text(encoding="utf-8", errors="ignore").lower()
        for filename in ("requirements.txt", "requirements-dev.txt", "pyproject.toml")
    )
    for dependency in FORBIDDEN_DEPENDENCY_NAMES:
        if dependency in dependency_text:
            errors.append(f"Forbidden core dependency declared: {dependency}")

    if (
        os.getenv("GITHUB_ACTIONS") == "true"
        and not (root / ".github" / "workflows" / "ci.yml").exists()
    ):
        errors.append("CI workflow is missing in GitHub Actions environment.")

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository structure and policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
