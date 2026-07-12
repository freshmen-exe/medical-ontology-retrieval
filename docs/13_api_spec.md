# Planned API Contracts — No Implementation Included

> **Status:** This is a design contract only. The corresponding Python files are intentionally empty. The team must implement, test, review, and revise these interfaces through Jira and pull requests.


This document describes the committed public interfaces in the starter repository. Private helper
methods may change inside a Jira task. Changing a public signature requires tests, a documentation
update, and reviewer approval.

## 1. Shared schemas — `src/medical_ontology/schema.py`

### `EntityType`

A string enum containing exactly:

```text
TRIỆU_CHỨNG
TÊN_XÉT_NGHIỆM
KẾT_QUẢ_XÉT_NGHIỆM
CHẨN_ĐOÁN
THUỐC
```

### `Assertions`

```python
Assertions(
    is_negated: bool = False,
    is_family: bool = False,
    is_historical: bool = False,
)
```

Used only for symptoms, diagnoses, and drugs.

### `Candidate`

```python
Candidate(
    code: str,
    system: str,
    name: str | None = None,
    score: float | None = None,
    matched_alias: str | None = None,
    metadata: dict[str, Any] = {},
)
```

Valid project system identifiers are `ICD10_VI` and `RXNORM_2026`.

### `Entity`

```python
Entity(
    text: str,
    entity_type: EntityType,
    start: int | None = None,
    end: int | None = None,
    assertions: Assertions | None = None,
    candidates: list[Candidate] = [],
    source: str | None = None,
    confidence: float | None = None,
)
```

`text`, `start`, and `end` always refer to the immutable raw note. Internal normalization must never
replace the output text.

### Retrieval result schemas

- `AliasHit`: one alias-level result.
- `CodeHit`: one best-alias-per-code or fused code result.
- `ValidationIssue`: structured validator output.
- `BatchManifest`: total/succeeded/failed counts and failure messages.

## 2. Configuration — `config.py`

```python
load_config(
    path: str | Path = "config/default.yaml",
    local_path: str | Path | None = None,
) -> ProjectConfig
```

Merge order:

1. shared YAML;
2. optional `config/local.yaml` or `PROJECT_CONFIG` path;
3. supported environment variables.

Supported environment variables:

```text
OLLAMA_BASE_URL
LLM_MODEL
EMBEDDING_MODEL
LOG_LEVEL
PROJECT_CONFIG
```

`ProjectConfig.section(name)` returns a defensive dictionary copy.

## 3. Data IO — `data/loaders.py`

```python
load_jsonl(path: str | Path) -> list[dict[str, Any]]
write_jsonl(path: str | Path, records: Iterable[Mapping[str, Any]]) -> None
```

Requirements:

- UTF-8 only;
- malformed JSON reports the file and line;
- blank lines may be skipped;
- no silent skipping of malformed records;
- writers create parent directories and terminate each record with a newline.

## 4. Text normalization — `data/normalization.py`

```python
normalize_spaces(text: str) -> str
remove_vietnamese_accents(text: str) -> str
normalize_match_text(text: str, *, remove_accents: bool = True) -> str
```

These functions create matching representations only. They must never modify raw output spans.

## 5. Ollama client — `clients/ollama_client.py`

```python
OllamaClient(
    base_url: str = "http://localhost:11434",
    timeout_seconds: float = 120.0,
    max_retries: int = 1,
    retry_delay_seconds: float = 1.0,
)
```

Methods:

```python
healthcheck() -> bool
health_check() -> bool
list_models() -> list[str]
generate_json(
    model: str,
    prompt: str,
    *,
    system: str | None = None,
    schema: dict[str, Any] | str = "json",
    options: dict[str, Any] | None = None,
) -> dict[str, Any]
embed(model: str, texts: list[str]) -> list[list[float]]
```

Network/JSON failures raise `RuntimeError` with an actionable message. The pipeline may fall back to
rules or RRF, but the client itself does not hide failures.

## 6. Extraction

### `RuleExtractor` — `extraction/rule_extractor.py`

```python
RuleExtractor(resources: Mapping[str, Any] | None = None)
extract(text: str) -> list[Entity]
build_hints(text: str) -> list[dict[str, Any]]
```

Resources may contain `abbreviations`, `lab_tests`, `symptoms`, `drug_terms`, and `disease_terms`.
The extractor is deterministic and high precision. It does not infer a diagnosis from a symptom.

### `LLMExtractor` — `extraction/llm_extractor.py`

```python
LLMExtractor(
    client: OllamaClient,
    model: str = "vicuna:7b-v1.5-q5_1",
    system_prompt_path: str | Path = "prompts/extraction_system.txt",
    examples_path: str | Path = "prompts/extraction_examples.jsonl",
)
extract(text: str, hints: Sequence[dict[str, Any]] = ()) -> list[Entity]
```

The LLM returns exact entity strings, labels, and assertions. It must not return ontology codes.
Hallucinated/paraphrased strings absent from the raw note are rejected.

### `AssertionPostProcessor` — `extraction/assertion_detector.py`

```python
AssertionPostProcessor(context_chars: int = 60)
apply(text: str, entities: Sequence[Entity]) -> list[Entity]
```

It only corrects explicit local negation, family, and history cues. It is not a second free-form LLM.

## 7. Embeddings — `retrieval/embeddings.py`

```python
OllamaEmbedder(
    base_url: str = "http://localhost:11434",
    model: str = "bge-m3",
    timeout_seconds: float = 120.0,
)
embed(texts: list[str]) -> np.ndarray
```

Return shape is `(n_texts, embedding_dim)`, dtype `float32`.

## 8. Exact dense retrieval — `retrieval/exact_search.py`

```python
ExactVectorIndex(dim: int)
add(vectors: np.ndarray, metadata: Sequence[dict]) -> None
search(query_vector: np.ndarray, top_k: int = 10) -> list[AliasHit]
save(path: str | Path) -> None
ExactVectorIndex.load(path: str | Path) -> ExactVectorIndex
```

The index stores normalized float32 vectors and uses NumPy matrix multiplication. It is the
correctness baseline for HNSW evaluation.

## 9. Sparse retrieval

### BM25 — `retrieval/bm25.py`

```python
BM25Index(
    k1: float = 1.5,
    b: float = 0.75,
    tokenizer: Callable[[str], list[str]] = default_tokenize,
)
build(aliases: Sequence[dict]) -> None
search(query: str, top_k: int = 50) -> list[AliasHit]
```

### Character TF-IDF — `retrieval/tfidf.py`

```python
CharNgramTfidfIndex(n_min: int = 2, n_max: int = 5)
build(aliases: Sequence[dict]) -> None
search(query: str, top_k: int = 50) -> list[AliasHit]
```

### Sparse facade — `retrieval/sparse_search.py`

```python
SparseIndex()
build(aliases: Sequence[dict]) -> None
search_bm25(query: str, top_k: int = 50) -> list[AliasHit]
search_tfidf(query: str, top_k: int = 50) -> list[AliasHit]
```

## 10. Code-level ranking

### Alias collapse — `mapping/candidate_ranker.py`

```python
collapse_alias_hits(hits: Sequence[AliasHit]) -> list[CodeHit]
```

Keeps the maximum-score alias per code. It never sums all aliases for one code.

### RRF — `retrieval/rrf.py`

```python
rrf_score(rank: int, rrf_k: int = 60) -> float
reciprocal_rank_fusion(
    rankings: Sequence[Sequence[CodeHit]],
    rrf_k: int = 60,
    top_k: int | None = None,
) -> list[CodeHit]
```

A code contributes at most once per input ranking.

### `CodeMapper` — `mapping/code_mapper.py`

```python
CodeMapper(
    system: str,
    search_functions: Sequence[SearchFunction],
    *,
    alias_top_k: int = 50,
    rrf_k: int = 60,
    internal_top_k: int = 10,
)
map_entity(
    entity: Entity,
    context: str | None = None,
    final_top_k: int = 5,
) -> list[Candidate]
```

Each mapper represents one ontology. Routing occurs in the pipeline, not inside a mixed store.

## 11. HNSW — `retrieval/hnsw.py`

```python
HNSWVectorIndex(
    dim: int,
    m: int = 16,
    m0: int | None = None,
    ef_construction: int = 64,
    ef_search: int = 50,
    random_seed: int = 42,
)
```

Public methods:

```python
add(vector: np.ndarray, metadata: dict) -> int
build(vectors: np.ndarray, metadata: Sequence[dict]) -> None
search(
    query_vector: np.ndarray,
    top_k: int = 10,
    ef_search: int | None = None,
) -> list[AliasHit]
save(path: str | Path) -> None
HNSWVectorIndex.load(path: str | Path) -> HNSWVectorIndex
```

The current neighbor selection is a clear baseline. Any heuristic-diversification enhancement must
be benchmarked against exact search and documented rather than assumed better.

## 12. Validation

```python
align_spans(text: str, entities: Sequence[Entity]) -> list[Entity]
validate_entity(text: str, entity: Entity, entity_index: int | None = None) -> list[ValidationIssue]
validate_entities(text: str, entities: Sequence[Entity]) -> list[ValidationIssue]
validate_candidates(entity: Entity, valid_codes=None) -> list[ValidationIssue]
validate_output(text: str, entities: Sequence[Entity], code_lookups=None) -> None
```

`validate_output` is the final deterministic gate and raises `ValueError` on any invalid final
state.

## 13. Pipeline — `pipeline/infer_pipeline.py`

```python
InferencePipeline(
    config: ProjectConfig,
    rule_extractor: RuleExtractor,
    llm_extractor: LLMExtractor | None,
    assertion_processor: AssertionPostProcessor,
    icd_mapper: CodeMapper | None,
    rxnorm_mapper: CodeMapper | None,
)
```

Methods:

```python
run(text: str, input_id: str | None = None) -> list[Entity]
run_file(input_path: str | Path, output_path: str | Path) -> None
run_directory(input_dir: str | Path, output_dir: str | Path) -> BatchManifest
```

Factory and convenience wrapper:

```python
build_pipeline(config: ProjectConfig) -> InferencePipeline
run_pipeline(text: str, config: ProjectConfig) -> list[Entity]
```

The starter factory builds deterministic sparse mappers from available alias JSONL. Offline dense
indexes are built by `scripts/build_indexes.py` and integrated through a dedicated Jira task.

## 14. Formatting and CLI

```python
format_output(text: str, entities: Sequence[Entity]) -> list[dict[str, Any]]
```

CLI:

```bash
medical-ontology --text "..." --config config/default.yaml
medical-ontology --input note.txt --output note.json
medical-ontology --input-dir test --output-dir output
```

## 15. Evaluation

```python
recall_at_k(expected: set[str], ranked: Sequence[str], k: int) -> float
reciprocal_rank(expected: set[str], ranked: Sequence[str]) -> float
precision_recall_f1(predicted: set[tuple], expected: set[tuple]) -> tuple[float, float, float]
evaluate_mapping_queries(records, search_codes, ks=(1, 5, 10)) -> dict[str, float]
evaluate_end_to_end(predicted_records, expected_records) -> dict[str, float]
```

QA owns curated records. Model/Pipeline own reusable runners and deterministic metrics.
