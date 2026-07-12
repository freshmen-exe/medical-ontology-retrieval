# Risk and Fallback Plan

Fallbacks protect the core submission. They are not excuses to skip investigation.

## 1. Official ICD source is difficult to parse

Primary response:

- preserve the official PDF;
- extract into interim rows;
- log page/row failures;
- compare samples with `icd.kcb.vn`.

Fallback:

- use a parse-friendly mirror only to reconstruct rows;
- retain official source as authority;
- cross-check codes/names and record the mirror in provenance.

Never silently translate or substitute ICD-10-CM.

## 2. RxNorm download/access delayed

- Complete UTS account/license steps early.
- Use official API/release metadata for development planning.
- Build parser/tests against tiny permitted fixtures.
- Do not scrape unofficial drug-code sites as the final authority.

## 3. LLM invalid JSON

1. Validate response.
2. Retry once with strict schema/error feedback.
3. Use rule-only extraction for that input if configured.
4. Log failure and continue batch only when final output remains valid.

## 4. LLM misses or mislabels entities

- Improve task definitions/few-shot cases based on QA errors.
- Add high-precision deterministic rules only for repeated safe patterns.
- Do not convert symptoms into diagnoses through aliases.
- Keep prompt/model changes versioned and evaluated.

## 5. Embedding retrieval is weak

- Verify alias quality and query normalization first.
- Strengthen sparse retrieval and exact matching.
- Adjust retrieval depth/RRF after evaluation.
- Consider embedding fine-tuning only after core completion and with a held-out test.

## 6. HNSW is incorrect or slow

- Exact dense search is the correctness fallback.
- Keep HNSW behind configuration.
- Benchmark on controlled data.
- Report the implementation honestly as experimental if it misses release quality.

HNSW must never block core mapping.

## 7. Index artifact mismatch

Every artifact manifest contains model, dimension, data checksum, config, and build commit. Refuse to load an incompatible index and rebuild deliberately.

## 8. Docker/Dev Container failure

- Use Python 3.13 local venv.
- Run pre-PR checks locally.
- Use GitHub Actions as independent verification.
- Use Colab for model runtime if local Ollama remains unavailable.

## 9. Ollama cannot run locally

- Push the branch.
- Clone it in the prepared Colab notebook.
- Run the fixed models and Streamlit there.
- Keep deterministic development/tests local or in Dev Container.

## 10. Cloudflare Quick Tunnel failure

- Verify Streamlit locally in Colab on port 8501.
- inspect logs;
- restart cloudflared;
- use Colab's alternative temporary sharing method only if approved and documented.

Quick Tunnel availability does not block code completion.

## 11. Team-member delay

- 2 working hours blocked: notify owner/Tech Lead.
- 6 working hours blocked: split/reassign/reduce scope.
- 1 day delayed: activate fallback or move task out of current sprint.
- 2 days delayed: cut optional work.

## 12. Scope-cut order

Cut first:

1. LLM reranker.
2. Embedding fine-tuning.
3. Large ontology expansion.
4. Advanced HNSW optimization.
5. UI visual polish.

Do not cut:

- authoritative data provenance;
- valid extraction/output schema;
- span and candidate validation;
- exact/sparse/RRF core mapping;
- batch output packaging;
- QA/error analysis;
- report accuracy.
