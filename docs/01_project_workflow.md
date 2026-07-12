# Complete Project Workflow

This document defines the real project architecture, not a throwaway MVP. The project has six major systems: knowledge-base construction, indexing, extraction, mapping, validation/output, and evaluation. Advanced work improves one of these systems; it does not create a separate hidden workflow.

## 1. Offline build workflow

```text
Vietnamese ICD-10 official source          RxNorm 2026 official release
              │                                      │
              ├──────────── acquire and register ─────┤
              │                                      │
              ▼                                      ▼
       parse and normalize                    parse and normalize
              │                                      │
              └──────────────┬───────────────────────┘
                             ▼
                    ontology code records
                             │
                    select core scope
                             │
                    generate safe aliases
                             │
                    validate and deduplicate
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
           ICD alias corpus          RxNorm alias corpus
                │                         │
                ├──── dense embeddings ───┤
                ├──── sparse indexes ─────┤
                └──── optional HNSW ──────┘
                             │
                     cache build artifacts
```

Offline build outputs are stored under `data/processed/` and `artifacts/`. They must not be rebuilt on every inference request.

## 2. Online inference workflow

```text
raw clinical text
  │
  ├─ preserve the exact original text
  ├─ normalize only a working copy
  ▼
rule-based extractor + LLM extractor
  │
  ▼
entity proposals
  │
  ├─ merge duplicate/overlapping proposals
  ├─ align exact spans to raw text
  ├─ post-process clear assertion cues
  └─ validate label and schema
  ▼
validated entities
  │
  ├─ CHẨN_ĐOÁN ───────────────► ICD mapper
  ├─ THUỐC ────────────────────► RxNorm mapper
  └─ all other labels ─────────► no candidates
                                   │
                     dense search + sparse search
                                   │
                         alias results per retriever
                                   │
                         group best alias per code
                                   │
                           code-level RRF fusion
                                   │
                    optional constrained LLM reranker
                                   │
                           candidate validation
                                   │
                                   ▼
                      exact final JSON formatter
```

## 3. Entity extraction contract

The extraction stage returns only:

- exact text copied from the input;
- start/end position;
- one valid entity type;
- assertions where required;
- provenance/confidence for internal debugging.

It does not produce ICD or RxNorm codes.

Valid types:

```text
TRIỆU_CHỨNG
TÊN_XÉT_NGHIỆM
KẾT_QUẢ_XÉT_NGHIỆM
CHẨN_ĐOÁN
THUỐC
```

Assertions:

```text
isNegated
isFamily
isHistorical
```

## 4. Mapping contract

Only two types enter ontology retrieval:

```text
CHẨN_ĐOÁN → Vietnamese ICD-10
THUỐC     → RxNorm 2026 RXCUI
```

The mapper receives an exact mention, its normalized query representation, its type, and a short context window. It never receives an entire ontology or arbitrary code generation authority.

## 5. Hybrid retrieval contract

For each mention:

1. Normalize the query without changing the final output span.
2. Expand only verified abbreviations.
3. Run dense retrieval over alias embeddings.
4. Run sparse lexical retrieval over alias text.
5. Keep a configurable number of aliases from each retriever.
6. Collapse each ranking to the best result per code.
7. Fuse code rankings with RRF.
8. Return a configurable final candidate count.
9. Optionally ask the LLM to reorder only the retrieved candidates.
10. Validate every candidate against the correct ontology lookup table.

## 6. Validation layers

Validation is deterministic wherever possible:

1. **Schema validation** — required fields and valid values.
2. **Span validation** — `raw_text[start:end] == entity.text`.
3. **Entity validation** — type, assertion keys, duplicates, overlap policy.
4. **Routing validation** — only diagnoses and drugs are mapped.
5. **Candidate validation** — code exists in the correct loaded ontology.
6. **Output validation** — final JSON matches competition requirements.

## 7. Evaluation workflow

```text
unit fixtures ─────────────► deterministic module tests
mapping queries ───────────► Recall@1/5/10, MRR, latency
clinical snippets + truth ─► extraction/assertion/E2E evaluation
all failures ──────────────► structured error analysis
error analysis ────────────► targeted data/code/prompt fixes
fixed failures ────────────► regression tests
```

QA owns curated test data and final verification. Developers own focused tests for deterministic code they introduce.

## 8. Packaging workflow

```text
input directory
  → batch inference
  → one JSON per input
  → output validator
  → output.zip

repository results
  → LaTeX report
  → slide deck
  → Streamlit demo
  → recorded demo video
```

## 9. Core versus optional work

Core must be stable before optional work begins.

Core:

- source acquisition and provenance;
- parsers and aliases;
- extraction;
- exact dense retrieval;
- sparse retrieval;
- RRF;
- deterministic validation;
- CLI/batch/demo;
- QA and evaluation.

Optional after core:

- HNSW optimization beyond the theoretically correct implementation;
- LLM reranking;
- ontology expansion;
- embedding fine-tuning;
- visual polish.
