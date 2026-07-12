# Google Colab: Git Branch + Ollama + Streamlit + Cloudflare

## 1. Purpose

Use Colab when a team member cannot run the fixed models locally. Colab is a runtime/demo environment, not the main source-control environment. All code still lives in GitHub branches.

## 2. Workflow

```text
local VS Code work
→ commit and push selected branch
→ Colab clones that branch
→ installs project and fixed models
→ runs Streamlit
→ exposes a temporary Cloudflare Quick Tunnel
```

Use the prepared notebook:

```text
notebooks/colab_ollama_streamlit.ipynb
```

## 3. Cell 1 — clone branch, install Ollama/cloudflared, pull models

Set repository and branch values before running.

```python
import os
import shutil
import subprocess
import time
from pathlib import Path

import requests

REPO_URL = "https://github.com/<organization>/medical-ontology-retrieval.git"
BRANCH = "main"  # or feature/MOR-34-code-level-rrf
PROJECT_DIR = Path("/content/medical-ontology-retrieval")
MODELS = ["vicuna:7b-v1.5-q5_1", "bge-m3"]

if PROJECT_DIR.exists():
    shutil.rmtree(PROJECT_DIR)

subprocess.run(
    ["git", "clone", "--depth", "1", "--branch", BRANCH, REPO_URL, str(PROJECT_DIR)],
    check=True,
)
os.chdir(PROJECT_DIR)

cloudflared = PROJECT_DIR / "cloudflared"
if not cloudflared.exists():
    subprocess.run(
        [
            "wget",
            "-q",
            "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "-O",
            str(cloudflared),
        ],
        check=True,
    )
    cloudflared.chmod(0o755)


def ollama_up() -> bool:
    try:
        return requests.get("http://localhost:11434/api/tags", timeout=2).ok
    except requests.RequestException:
        return False


if MODELS:
    subprocess.run(
        "command -v zstd >/dev/null && command -v lspci >/dev/null "
        "|| (sudo apt-get update && sudo apt-get install -y zstd pciutils)",
        shell=True,
        check=True,
        executable="/bin/bash",
    )
    subprocess.run(
        "command -v ollama >/dev/null || curl -fsSL https://ollama.com/install.sh | sh",
        shell=True,
        check=True,
        executable="/bin/bash",
    )

    os.environ["OLLAMA_FLASH_ATTENTION"] = "false"

    if not ollama_up():
        ollama_log = open("/content/ollama.log", "w", encoding="utf-8")
        subprocess.Popen(["ollama", "serve"], stdout=ollama_log, stderr=subprocess.STDOUT)
        for _ in range(30):
            if ollama_up():
                break
            time.sleep(1)

    if not ollama_up():
        raise RuntimeError("Ollama did not start. Check /content/ollama.log")

    installed = subprocess.check_output(["ollama", "list"], text=True)
    for model in MODELS:
        if model not in installed:
            subprocess.run(["ollama", "pull", model], check=True)

print("Repository:", PROJECT_DIR)
print("Branch:", BRANCH)
print("Ollama running:", ollama_up())
```

## 4. Cell 2 — install project dependencies

```python
import os
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/content/medical-ontology-retrieval")
os.chdir(PROJECT_DIR)

subprocess.run(
    ["python", "-m", "pip", "install", "--upgrade", "pip"],
    check=True,
)
subprocess.run(
    ["python", "-m", "pip", "install", "-r", "requirements-colab.txt"],
    check=True,
)
subprocess.run(
    ["python", "-m", "pip", "install", "-e", "."],
    check=True,
)
subprocess.run(["python", "scripts/check_environment.py"], check=True)
```

## 5. Cell 3 — run Streamlit and Cloudflare Quick Tunnel

```python
import os
import subprocess
import time
from pathlib import Path

import requests

PROJECT_DIR = Path("/content/medical-ontology-retrieval")
os.chdir(PROJECT_DIR)


def ollama_up() -> bool:
    try:
        return requests.get("http://localhost:11434/api/tags", timeout=2).ok
    except requests.RequestException:
        return False


if not ollama_up():
    ollama_log = open("/content/ollama.log", "a", encoding="utf-8")
    subprocess.Popen(["ollama", "serve"], stdout=ollama_log, stderr=subprocess.STDOUT)
    time.sleep(5)

if not ollama_up():
    raise RuntimeError("Ollama is not running. Check /content/ollama.log")

streamlit_log = open("/content/streamlit.log", "w", encoding="utf-8")
subprocess.Popen(
    [
        "python",
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        "8501",
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false",
    ],
    stdout=streamlit_log,
    stderr=subprocess.STDOUT,
)

time.sleep(5)
print("Streamlit log: /content/streamlit.log")
print("Ollama running:", ollama_up())
print("Starting temporary Cloudflare Quick Tunnel...")

subprocess.run(
    [str(PROJECT_DIR / "cloudflared"), "tunnel", "--url", "http://localhost:8501"],
    check=True,
)
```

## 6. Why a single `app.py` works with many project files

`app.py` imports reusable logic from the installed package:

```python
from medical_ontology.pipeline.infer_pipeline import InferencePipeline
```

Cell 2 runs `pip install -e .`, so Python can import everything under `src/medical_ontology/`. `app.py` remains a UI entry point rather than containing all project code.

## 7. Branch updates

Colab clones a snapshot. After pushing new commits, rerun Cell 1 or update manually:

```bash
%cd /content/medical-ontology-retrieval
!git fetch origin
!git switch "$BRANCH"
!git pull --rebase origin "$BRANCH"
```

Restart Streamlit after code/config changes when the old process does not reload correctly.

## 8. Security and limitations

- Quick Tunnel URLs are public and temporary.
- Do not paste sensitive clinical data, secrets, or private datasets into a public demo.
- Do not expose the Ollama API port through Cloudflare.
- Quick Tunnels are for testing/demo, not production.
- Colab sessions can stop or lose downloaded models.
