$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pre-commit install --hook-type pre-commit --hook-type pre-push

if (-not (Test-Path "config/local.yaml")) {
    Copy-Item "config/local.example.yaml" "config/local.yaml"
}

python scripts/check_environment.py
