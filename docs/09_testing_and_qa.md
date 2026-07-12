# Testing and QA Guide

## 1. Ownership

QA owns test strategy, curated test data, ground truth, acceptance verification, error analysis, and release sign-off. Developers own focused tests for deterministic logic they implement and must deliver code that QA can execute.

## 2. Test layers

### Unit tests

One function/class, no network, no Ollama, tiny fixtures, normally under one second each.

Examples:

- normalization;
- parser field handling;
- alias transformations/collisions;
- vector normalization and exact similarity;
- BM25/TF-IDF scoring;
- RRF;
- HNSW data-structure invariants on tiny vectors;
- span alignment;
- candidate routing/validation;
- formatter and ZIP manifest.

### Integration tests

Multiple modules with deterministic fakes/stubs:

- load aliases → build tiny index → retrieve candidates;
- rule extractor → merge → align → validate;
- pipeline with fake LLM/embed client;
- artifact manifest compatibility.

### E2E tests

Complete pipeline on controlled clinical notes. May use a fake deterministic client in CI and selected real Ollama runs locally/Colab.

### Ollama tests

Marked `ollama`; never required in standard GitHub Actions. Run before release on the fixed model environment.

## 3. Directory layout

```text
tests/
├── conftest.py
├── unit/
├── integration/
├── e2e/
└── fixtures/
    ├── aliases/
    ├── notes/
    ├── expected/
    └── indexes/
```

## 4. Commands

```bash
python scripts/validate_repository.py
python -m pytest tests/unit
python -m pytest -m integration
python -m pytest -m e2e
python -m pytest -m ollama
python -m pytest -m "not slow and not ollama and not e2e"
python -m pytest tests/unit/test_rrf.py -vv
python -m pytest --cov=medical_ontology --cov-report=term-missing
```

## 5. Test-writing pattern

Use Arrange–Act–Assert and descriptive names:

```python
def test_rrf_counts_each_code_once_per_ranking() -> None:
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

Prefer parametrization for related cases. Use fixtures for shared small resources. Do not make unit tests depend on execution order.

## 6. Mapping queries

`mapping_queries.jsonl` is QA evaluation data, not production logic.

Two sets:

- auto-generated smoke queries from safe aliases;
- curated hard queries written/reviewed by QA and Data.

Curated cases include abbreviations, spelling variants, dose/form ambiguity, near-duplicate ICD descriptions, and negative controls.

## 7. Ground truth

Ground-truth records must include:

- exact source text and positions;
- label;
- assertion values;
- expected candidate codes where applicable;
- annotator/reviewer;
- ambiguity notes.

A difficult disagreement is documented; it is not silently forced into a fake certainty.

## 8. Metrics

Retrieval:

- Recall@1/5/10;
- MRR;
- latency distribution;
- HNSW recall versus exact.

Extraction/E2E:

- exact-span entity precision/recall/F1 where feasible;
- label correctness;
- assertion correctness;
- candidate hit@k;
- schema pass rate;
- runtime/fallback count.

## 9. Error analysis taxonomy

```text
EXTRACTION_MISS
EXTRACTION_SPURIOUS
SPAN_MISMATCH
WRONG_LABEL
WRONG_NEGATION
WRONG_FAMILY
WRONG_HISTORY
MISSING_ALIAS
NOISY_ALIAS
WRONG_CANDIDATE
CANDIDATE_SYSTEM_ERROR
DUPLICATE_ENTITY
OVERLAP_ERROR
SCHEMA_ERROR
RUNTIME_ERROR
```

Every issue records input ID, expected, predicted, suspected component, owner, fix PR, and regression result.

## 10. CI policy

GitHub Actions validates repository structure and documentation links, then runs formatting, lint, compilation, and deterministic tests. It does not download models or official datasets. A green CI build is necessary but not sufficient for QA approval.

## 11. Coverage policy

Coverage is a diagnostic, not a target to game. Prioritize deterministic algorithm, validation, and IO boundaries. New core deterministic logic should have tests unless the PR documents why a test is currently impossible and creates a QA follow-up task.

## Structure-only starting state

The test files in this scaffold are intentionally empty. QA owns the curated tests, fixtures, mapping queries, clinical snippets, and ground truth. Implementation owners may add only minimal developer sanity tests for their own module; those do not replace QA-owned acceptance and regression coverage.
