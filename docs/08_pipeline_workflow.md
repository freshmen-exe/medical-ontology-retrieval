# End-to-End Pipeline Workflow

The Pipeline role turns Data and Model modules into one repeatable program. It owns orchestration and interfaces, not the underlying semantic algorithm choices.

## 1. Runtime stages

```text
load configuration
→ load resources/index manifests
→ receive raw text
→ preserve raw text and create working representation
→ call rule extractor
→ call LLM extractor
→ merge entity proposals
→ align exact spans
→ apply assertion post-processing
→ validate entities
→ route diagnoses/drugs
→ call ontology mappers
→ validate candidates
→ format final output
→ write/log/return result
```

## 2. Initialization

Pipeline initialization should:

- validate configuration;
- check fixed model names;
- load alias/code lookup tables;
- load cached dense/sparse/HNSW artifacts;
- verify artifact manifests match data/model configuration;
- initialize Ollama client lazily or test health explicitly;
- fail with actionable messages.

Do not rebuild embeddings or indexes inside each inference call.

## 3. Raw-text preservation

Maintain two representations:

- `raw_text`: immutable source for positions and final text;
- `working_text`: normalized representation for matching.

All normalization functions must provide a way to map matched spans back to raw text or operate without changing string length where positions are required.

## 4. Merge policy

Entity proposal merging must be deterministic:

1. Align every proposal to raw text.
2. Reject unalignable hallucinated proposals.
3. Deduplicate identical span/type proposals.
4. Prefer the longest span for same-type nested proposals when appropriate.
5. Preserve distinct labels only when the task schema allows them.
6. Resolve rule/LLM conflicts using explicit precedence and confidence rules.
7. Log every discarded conflict for QA analysis.

## 5. Mapping route

```python
if entity.type == "CHẨN_ĐOÁN":
    mapper = icd_mapper
elif entity.type == "THUỐC":
    mapper = rxnorm_mapper
else:
    mapper = None
```

No other label receives candidates.

## 6. Context windows

For optional reranking, extract a bounded raw-text window around the entity. Prefer the containing sentence or clause. Never send the entire ontology or full multi-page note when a local context is sufficient.

## 7. Error handling and fallbacks

- Invalid LLM JSON: retry once, then use rule-only proposals.
- Ollama unavailable: return a controlled error or use configured rule-only mode.
- HNSW unavailable/mismatched: fallback to exact dense search.
- Reranker error: preserve RRF order.
- Invalid candidate: remove it and log.
- Invalid final output: do not write submission file; raise a validation error.

## 8. CLI

Required modes:

```bash
python -m medical_ontology.infer --text "..."
python -m medical_ontology.infer --input note.txt --output note.json
python -m medical_ontology.infer --input-dir test --output-dir output
```

CLI options belong in one parser. Avoid separate scripts with inconsistent behavior.

## 9. Streamlit

`app.py` is UI-only. It may:

- load/cached pipeline resources;
- accept a note;
- run inference;
- display entities, assertions, candidates, timing, warnings, and JSON;
- show configuration/model/index metadata.

It must not reimplement extraction, retrieval, validation, or data loading.

## 10. Batch output

Batch mode:

- sorts inputs deterministically;
- preserves input identifiers;
- writes atomically when possible;
- validates every result before writing;
- produces a manifest of successes/failures/timing;
- refuses to create final ZIP when required outputs are missing or invalid.

## 11. Logging

Use module loggers. Include:

- input ID, not raw sensitive note unless explicitly allowed;
- stage timing;
- number of extracted/validated/mapped entities;
- fallback use;
- validation rejection reasons;
- model/index/data manifest IDs.

Never log secrets or full licensed datasets.
