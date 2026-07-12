# Demo Video Script

## 0:00–0:20 — Introduction

State the task, team, and two target ontologies.

## 0:20–0:50 — Architecture

Show the pipeline: extraction, validation, routing, hybrid retrieval, RRF, final JSON.

## 0:50–2:20 — Live Streamlit demo

Use one reviewed case containing a diagnosis, drug, symptom, assertion cue, and lab/result. Show:

- exact extracted spans;
- label and assertions;
- candidate codes;
- final JSON;
- no hidden manual edits.

## 2:20–3:00 — Algorithms and evaluation

Show exact versus HNSW latency/Recall@k and dense/sparse/RRF ablation from saved artifacts.

## 3:00–3:30 — Limitations and conclusion

State what is deterministic, what depends on LLM/embeddings, ontology scope, and future work.
