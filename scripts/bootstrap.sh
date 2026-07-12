#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
pre-commit install --hook-type pre-commit --hook-type pre-push

if [[ ! -f config/local.yaml ]]; then
  cp config/local.example.yaml config/local.yaml
fi

python scripts/check_environment.py
