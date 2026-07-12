# ADR 0003: Ruff as the Only Python Formatter and Linter

- Status: Accepted
- Date: 2026-07-12

## Decision

Use Ruff for formatting, import sorting, linting, and selected safe fixes. Do not run Black or isort separately.

## Consequences

- One configuration lives in `pyproject.toml`.
- VS Code, pre-commit, pre-push checks, and CI use the same tool.
- Personal formatter overrides are not allowed for this workspace.
