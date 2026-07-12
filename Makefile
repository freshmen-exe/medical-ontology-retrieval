.PHONY: setup format lint validate-repo test test-all coverage pre-pr check-env demo docker-build docker-test build-data build-index eval-retrieval eval-e2e zip-output clean

setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt
	python -m pip install -e .
	pre-commit install --hook-type pre-commit --hook-type pre-push

format:
	python -m ruff check . --fix
	python -m ruff format .

lint:
	python -m ruff format . --check
	python -m ruff check .

validate-repo:
	python scripts/validate_repository.py

test:
	python scripts/run_fast_tests.py

test-all:
	python -m pytest -m "not ollama"

coverage:
	python -m pytest -m "not slow and not ollama" --cov=medical_ontology --cov-report=term-missing

pre-pr:
	python scripts/pre_pr.py

check-env:
	python scripts/check_environment.py

demo:
	python -m streamlit run app.py

docker-build:
	docker compose build

docker-test:
	docker compose run --rm test

build-data:
	python scripts/parse_icd10_vi.py
	python scripts/parse_rxnorm_2026.py
	python scripts/generate_icd_aliases.py
	python scripts/generate_rxnorm_aliases.py
	python scripts/validate_aliases.py

build-index:
	@echo "Specify ontology explicitly; see scripts/build_indexes.py --help"

eval-retrieval:
	@echo "Specify aliases, QA queries, and system; see scripts/evaluate_retrieval.py --help"

eval-e2e:
	@echo "Specify predictions and ground truth; see scripts/evaluate_e2e.py --help"

zip-output:
	python scripts/package_output.py --output-dir output --zip-path output.zip

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.ruff_cache', 'htmlcov']]"
