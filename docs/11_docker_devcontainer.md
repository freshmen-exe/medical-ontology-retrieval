# Docker and VS Code Dev Container

## 1. Purpose

The Dev Container standardizes Python 3.13, package dependencies, Ruff, pytest, pre-commit, scripts, and Streamlit. It is a development environment, not a production deployment architecture.

Ollama runs on the host or Colab. This avoids forcing every member to solve GPU passthrough and platform-specific model-runtime issues inside Docker.

## 2. Required local software

- Docker Desktop or compatible Docker Engine/Compose.
- VS Code.
- VS Code Dev Containers extension.

On Windows, use WSL 2 backend in Docker Desktop when available.

## 3. Open in container

1. Clone the repository.
2. Open the repository root in VS Code.
3. Run `Dev Containers: Reopen in Container`.
4. Wait for the image build and `postCreateCommand`.
5. Open a new terminal.
6. Run:

```bash
make check-env
make test
```

## 4. Model connection

Default inside the container:

```text
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

The Dev Container adds a host-gateway mapping for Linux. Start Ollama on the host:

```bash
ollama serve
```

Test from the container:

```bash
python -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags', timeout=3).status_code)"
```

## 5. Docker Compose commands

Run tests in a clean container:

```bash
docker compose build
docker compose run --rm test
```

Run Streamlit:

```bash
docker compose up --build app
```

Open `http://localhost:8501`.

Stop:

```bash
docker compose down
```

## 6. Source mounting

Compose and Dev Container mount the repository at `/workspace`. Saved files on the host and container are the same files. Generated artifacts in ignored folders remain local unless deliberately copied elsewhere.

## 7. Dependency changes

When `requirements*.txt`, `pyproject.toml`, or Dockerfile changes:

```bash
docker compose build --no-cache
```

In VS Code use `Dev Containers: Rebuild Container`.

## 8. Docker is not mandatory for model execution

Supported combinations:

```text
Dev Container + host Ollama
Local venv + local Ollama
Dev Container/local code + Colab model/demo validation
Full Colab clone and runtime
```

## 9. What not to add

Do not add Kubernetes, a database service, Redis, a model-serving proxy, or a multi-container microservice architecture unless the core project develops a proven requirement. They do not improve the competition score by themselves.
