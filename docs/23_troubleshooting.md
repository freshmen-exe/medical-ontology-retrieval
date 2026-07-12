# Troubleshooting

## Python package cannot be imported

```bash
python -m pip install -e .
python -c "import medical_ontology; print(medical_ontology.__file__)"
```

Confirm VS Code selected the same interpreter.

## Ruff does not format on save

1. Confirm the Ruff extension is installed and enabled.
2. Open the repository root, not a nested folder.
3. Check `.vscode/settings.json` is trusted.
4. Run `Ruff: Format Document` from the Command Palette.
5. Run `python -m ruff format .` in the terminal.
6. Disable Black/isort extensions for this workspace.

## Auto Save does not run code actions

`source.organizeImports.ruff` must be set to `always`. `explicit` runs only on Ctrl+S. Formatting still runs through `editor.formatOnSave`.

## Docker cannot reach Ollama on the host

- Windows/macOS: use `http://host.docker.internal:11434`.
- Linux: ensure Compose or Dev Container adds `host.docker.internal:host-gateway`.
- Confirm Ollama listens and `curl http://localhost:11434/api/tags` works on the host.

## Ollama is not running

```bash
ollama serve
ollama list
```

Health check:

```bash
curl http://localhost:11434/api/tags
```

## Model not found

```bash
ollama pull vicuna:7b-v1.5-q5_1
ollama pull bge-m3
ollama list
```

## pytest cannot discover tests

```bash
python -m pytest --collect-only
```

Ensure test files are named `test_*.py` and the package was installed editable.

## Pre-commit changed files and commit failed

This is expected. Review the changes, stage them again, and commit:

```bash
git diff
git add -A
git commit
```

## Pre-push tests fail

Run the failing command directly, fix it, commit the fix, and push again. Do not bypass hooks except during a documented emergency approved by the Tech Lead.

## Rebase conflict

```bash
git status
# edit conflict markers
git add <fixed-file>
git rebase --continue
```

Abort safely:

```bash
git rebase --abort
```

## Accidentally changed the wrong branch

If not committed:

```bash
git stash push -u -m "move work to correct branch"
git switch <correct-branch>
git stash pop
```

If committed locally, create the intended branch at the current commit, then restore the original branch to its remote state only after confirming the new branch contains the work.

## Streamlit imports fail

Run Streamlit from the repository root after editable installation:

```bash
python -m pip install -e .
python -m streamlit run app.py
```

## Colab tunnel does not appear

- Read `/content/streamlit.log`.
- Confirm port 8501 is listening.
- Restart only the Streamlit and Cloudflared processes, not the whole notebook.
- Quick Tunnels are temporary and may occasionally need a new session.

## Raw data parser produces broken rows

- Preserve the raw file unchanged.
- Record the extraction tool and page range.
- Compare random samples with `icd.kcb.vn` or the official source.
- Put uncertain rows in an issues file; do not silently guess.
