# Python Coding and Documentation Standards

## 1. Language and style

- Python 3.13.
- Ruff is the only formatter/linter/import sorter.
- Line length: 100.
- UTF-8 and LF line endings.
- Type hints on public functions, methods, classes, and reusable internal boundaries.
- Google-style docstrings.
- No wildcard imports.
- No hard-coded absolute paths, secrets, or model names scattered through modules.

## 2. Module design

- One clear responsibility per module.
- Small functions with explicit inputs and outputs.
- Prefer pure functions for normalization, scoring, metrics, and validation.
- Use classes when state/index resources matter.
- Avoid generic `utils.py` dumping grounds; use purpose-specific modules.
- Avoid circular imports by keeping schema/config/IO low in the dependency graph.

## 3. Naming

```text
modules/functions/variables: snake_case
classes/enums: PascalCase
constants: UPPER_SNAKE_CASE
private helpers: _leading_underscore
```

Use full meaningful names. Avoid unexplained `x`, `tmp`, `data2`, or medical abbreviations in code identifiers when a clear name exists.

## 4. Docstrings

Example:

```python
def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[AliasHit]:
    """Return the nearest alias vectors for a normalized query vector.

    Args:
        query_vector: One-dimensional float array with shape ``(dim,)``.
        top_k: Maximum number of results. Must be positive. Defaults to 10.

    Returns:
        Ranked alias hits ordered by descending similarity.

    Raises:
        ValueError: If the query dimension is invalid or ``top_k`` is not positive.
        RuntimeError: If the index has not been built.
    """
```

Do not use JavaDoc `@param` syntax. Python documentation uses `Args`, `Returns`, `Raises`, `Attributes`, and `Examples` sections.

## 5. Comments

Comment the reason, invariant, or trade-off, not syntax.

Good:

```python
# Keep only the best alias rank per code so codes with many aliases do not receive extra votes.
```

Bad:

```python
# Loop through results.
```

TODO comments must contain a Jira key:

```python
# TODO(MOR-72): Compare heuristic neighbor selection against distance-only pruning.
```

## 6. Errors

- Validate public inputs early.
- Raise specific exceptions with actionable messages.
- Do not use bare `except`.
- Do not silently skip invalid data.
- Convert external-service failures into project-specific errors at the client boundary.

## 7. Logging

Use `logging.getLogger(__name__)`. Library modules do not configure global logging. CLI/app entry points configure format and level.

Use structured context in messages:

```python
logger.warning("Falling back to exact search: index=%s reason=%s", index_name, reason)
```

## 8. NumPy rules

- Store embeddings as `float32` unless an experiment proves another need.
- Validate shapes and finite values.
- Normalize once during index build and once per query.
- Document distance/similarity conventions.
- Set random seeds in reproducible experiments.

## 9. Paths and files

Use `pathlib.Path`. Write UTF-8 explicitly. Create parent directories deliberately. Do not change the process working directory inside reusable modules.

## 10. Configuration

Algorithm parameters belong in config or constructors, not module globals. Defaults must be documented and tested.

## 11. Tests

New deterministic logic includes focused tests. Use exact assertions for deterministic output and `pytest.approx` for floating-point comparisons.

## 12. Formatting commands

```bash
python -m ruff check . --fix
python -m ruff format .
```

Never manually reformat another contributor's unrelated files inside a functional PR.
