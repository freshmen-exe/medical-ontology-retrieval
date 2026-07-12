# Assumptions and Clarifications

| ID | Statement | Status | Evidence/action |
|---|---|---|---|
| A-001 | Diagnosis candidates use the organizer-specified Vietnamese ICD-10 source, not ICD-10-CM. | Confirmed by organizer communication reported by the team | Preserve the communication in `references/competition/clarifications.md`; source data from Circular 06/2026/TT-BYT. |
| A-002 | Drug candidates use an official RxNorm 2026 monthly release. | Confirmed by organizer communication reported by the team | Pin exact release date/checksum in `data/raw/rxnorm_2026/SOURCE.md`. |
| A-003 | Positions use Python-style half-open intervals `[start, end)`. | Project implementation assumption | Verify against official examples/evaluator before freeze. |
| A-004 | The LLM and embedding model names are fixed to the two Ollama tags in README. | Team architecture decision | Change only through an ADR and Jira task. |
| A-005 | HNSW is an advanced implementation/benchmark, while exact search remains the correctness fallback. | Team architecture decision | Preserve exact-vs-HNSW evaluation artifacts. |

Unknown or disputed facts must be added here rather than silently encoded in prompts or validators.
