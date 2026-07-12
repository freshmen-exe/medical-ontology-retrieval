# Environment and Tooling Standard

## 1. Supported development paths

### Standard path

VS Code opened in the repository Dev Container. This is the team reference environment and the environment used to reproduce PR failures.

### Local fallback

Python 3.13 virtual environment. Use only when Docker is unavailable or unsuitable.

### Model-runtime fallback

Google Colab runs Ollama and Streamlit for members whose local hardware cannot run the fixed models.

## 2. Fixed versions and tools

| Tool | Standard |
|---|---|
| Python | 3.13 baseline |
| Package manager | pip |
| Package installation | editable install, `pip install -e .` |
| Formatter/linter/import sorting | Ruff |
| Test runner | pytest |
| Git hooks | pre-commit |
| Container | Docker / VS Code Dev Container |
| LLM and embedding runtime | Ollama |
| UI | Streamlit |
| CI | GitHub Actions |
| Project management | Jira Scrum |

Do not introduce Poetry, Conda, uv, tox, nox, Black, isort, Flake8, or another task manager without an approved ADR. More tools are not automatically more professional.

## 3. Dependency files

- `pyproject.toml`: package metadata and canonical tool configuration.
- `requirements.txt`: runtime dependency ranges.
- `requirements-dev.txt`: runtime plus QA/development tools.
- `requirements-colab.txt`: dependencies installed by Colab.

Before the release candidate, freeze the tested Dev Container environment to a lock snapshot if reproducibility requires it:

```bash
python -m pip freeze > requirements-lock.txt
```

Do not casually update dependencies after code freeze.

## 4. Allowed libraries

Allowed runtime support:

- standard library;
- NumPy;
- requests;
- PyYAML;
- tqdm;
- Streamlit.

Allowed development support:

- Ruff;
- pytest and pytest-cov;
- pre-commit;
- Docker and GitHub Actions.

Core algorithms must not be delegated to FAISS, hnswlib, scikit-learn retrieval implementations, rank-bm25, vector databases, or RAG frameworks.

## 5. Installation

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pre-commit install --hook-type pre-commit --hook-type pre-push
```

Verify:

```bash
python scripts/check_environment.py
python -m pytest -m "not slow and not ollama and not e2e"
```

## 6. Model runtime

Fixed models:

```text
vicuna:7b-v1.5-q5_1
bge-m3
```

Local installation:

```bash
ollama pull vicuna:7b-v1.5-q5_1
ollama pull bge-m3
ollama serve
```

The Python package communicates with Ollama through HTTP. No Python Ollama SDK is required.

## 7. Environment variables

Copy `.env.example` to `.env` for local use. The application reads values from the process environment or YAML config; `.env` is not automatically committed or treated as public configuration.

Important values:

```text
OLLAMA_BASE_URL
LLM_MODEL
EMBEDDING_MODEL
PROJECT_CONFIG
LOG_LEVEL
```

## 8. Environment parity rule

A PR is not rejected solely because a contributor used local Python, but it must pass one of:

- `python scripts/pre_pr.py` in the Dev Container;
- `docker compose run --rm test`;
- GitHub Actions CI.

## 9. Large artifacts

Model weights, raw licensed datasets, embeddings, and HNSW indexes are not Git-tracked. The repository stores reproducible scripts, manifests, checksums, and small fixtures.

## Python compatibility

Python 3.13 is the canonical Docker, Dev Container, and primary local baseline. New language
features must remain compatible with Python 3.13.
