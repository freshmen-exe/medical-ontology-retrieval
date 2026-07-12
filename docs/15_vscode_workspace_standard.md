# VS Code Workspace Standard

## 1. Required editor

The team uses VS Code. Repository settings are committed under `.vscode/` so formatting, tests, and common tasks behave consistently.

## 2. Save and formatting behavior

The workspace uses:

```json
{
  "files.autoSave": "onFocusChange",
  "editor.formatOnSave": true
}
```

Behavior:

- `Ctrl+S` saves immediately and formats the current Python file.
- Moving focus away from a modified editor automatically saves and formats it.
- Import organization runs on explicit and focus-change saves.
- Ruff safe fixes run on explicit saves only, which prevents aggressive changes while merely switching tabs.

This is preferred over `afterDelay`, which may save and format in the middle of typing, and over `onWindowChange`, which waits until the entire VS Code window loses focus.

## 3. Formatter and linter

Use Ruff only.

- Do not install Black as the project formatter.
- Do not install isort separately.
- Do not add another formatter to personal workspace overrides.
- Project style is defined in `pyproject.toml`.

Manual commands:

```bash
python -m ruff check . --fix
python -m ruff format .
```

Verification:

```bash
python -m ruff format . --check
python -m ruff check .
```

## 4. Recommended extensions

VS Code reads `.vscode/extensions.json` and recommends:

- Python
- Pylance
- Ruff
- Dev Containers
- Docker
- GitHub Pull Requests and Issues
- GitHub Actions
- Atlassian for VS Code
- GitLens
- YAML
- TOML
- EditorConfig
- Markdown All in One
- LaTeX Workshop
- Jupyter

The repository explicitly marks Black Formatter and isort as unwanted recommendations to prevent conflicting formatters.

## 5. Tasks

Open `Terminal → Run Task` or `Ctrl+Shift+P → Tasks: Run Task`.

Available tasks:

- Project: Format
- Project: Lint
- Project: Fast tests
- Project: Pre-PR checks
- Project: Streamlit demo

## 6. Debug configurations

Open Run and Debug:

- `CLI: sample inference`
- `Streamlit demo`

Do not place personal API keys or machine-specific absolute paths in `launch.json`.

## 7. Python interpreter

Inside the Dev Container, VS Code uses `/usr/local/bin/python`.

On Windows local fallback, select:

```text
<repo>/.venv/Scripts/python.exe
```

On Linux/macOS local fallback, select:

```text
<repo>/.venv/bin/python
```

Run `Python: Select Interpreter` if tests or imports use the wrong environment.

## 8. Workspace settings versus personal settings

Repository settings control team-critical behavior. Personal themes, fonts, keyboard shortcuts, and UI preferences stay in User Settings. Do not commit personal settings that change project behavior.

## 9. Before blaming the code

1. Confirm VS Code is opened at the repository root.
2. Confirm the correct interpreter.
3. Confirm `pip install -e .` succeeded.
4. Run `python scripts/check_environment.py`.
5. Rebuild the Dev Container if dependencies or Dockerfile changed.
