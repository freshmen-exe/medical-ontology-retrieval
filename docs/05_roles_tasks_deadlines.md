# Roles, Ownership, Atomic Tasks, and Deadlines

> **Canonical task source:** `planning/jira/jira_import_tasks.csv`. This document explains ownership; the CSV is the authoritative importable schedule.

All times use ICT (UTC+7). The plan begins with the initial team meeting at 09:00 ICT on 12 July 2026 and implementation work starts immediately after setup, code freezes on 28 July 2026 at 23:00, and final deliverables are completed by 2 August 2026 at 23:00.

## 1. Role map

| Role | Members |
|---|---|
| Tech Lead | Khang |
| Data | Dương Huệ Mẫn, Nguyễn Hoàng Thái, Lương Minh Quân |
| Model | Khang, Võ Huỳnh Quốc Thái |
| Pipeline | Khang, Võ Huỳnh Quốc Thái, Lương Minh Quân |
| QA/Reviewer | Khang, Dương Huệ Mẫn, Nguyễn Hoàng Thái |

A role defines responsibility, not exclusive file ownership. The named owner remains accountable even when another member implements a sub-task.

## Initial kickoff meeting

- Date: **12 July 2026**
- Time: **09:00-10:30 ICT**
- Attendees: all five members
- Agenda and minutes: [`../planning/meetings/2026-07-12-kickoff.md`](../planning/meetings/2026-07-12-kickoff.md)
- Jira import item ID: `1001`

## 2. Work-hour standard

- Weekdays: target 6 hours/person/day.
- Weekends: maximum 7 hours/person/day.
- Daily planning: 10–15 minutes.
- Async update: by 16:00.
- Integration check: 15–25 minutes at night.
- Task larger than 4 focused hours should normally be split.
- Every completed task must produce evidence: commit, PR, file, metric, test output, or documented result.

## 3. Role-first breakdown

### 3.1 Tech Lead — Khang

#### Project governance (Khang)

- Create GitHub organization/repository and protect `main`.
- Create Jira Scrum project `MOR`.
- Configure epics, components, statuses, sprints, and releases.
- Approve repository structure, interfaces, coding standard, and DoD.
- Publish onboarding instructions.

Estimated work: ~5h. Deadline: **13 Jul, 20:00**.

#### Architecture contract (Khang)

- Freeze entity/candidate schemas v0.
- Freeze package/module boundaries.
- Freeze fixed model names and runtime interface.
- Define fallback rules for LLM, embeddings, HNSW, and data parsing.

Estimated work: ~4h. Deadline: **14 Jul, 18:00**.

#### Daily technical leadership (Khang)

- Triage blockers.
- Review cross-component PRs.
- Decide scope cuts and fallback activation.
- Keep Jira and architecture docs synchronized.

Estimated work: ~1h/day. Deadline: **daily, 22:30**.

#### Final integration and submission (Khang)

- Approve release candidate.
- Approve final output package.
- Coordinate report, slides, and demo video.
- Create final Git tag/release.

Estimated work: ~10h total. Deadlines: **28 Jul, 23:00** for code; **2 Aug, 23:00** for all deliverables.

---

### 3.2 Data — Dương Huệ Mẫn, Nguyễn Hoàng Thái, Lương Minh Quân

#### Vietnamese ICD-10 source acquisition (Dương Huệ Mẫn)

- Download official Circular 06/2026/TT-BYT and appendix.
- Record source URLs, access date, local filename, and checksum.
- Cross-check the coding portal.

Estimated work: ~2.5h. Deadline: **14 Jul, 18:00**.

#### RxNorm 2026 source acquisition (Dương Huệ Mẫn)

- Obtain an official 2026 monthly release.
- Record exact release date, license/access conditions, archive checksum, and file layout.

Estimated work: ~3h. Deadline: **14 Jul, 21:00**.

#### ICD parser (Dương Huệ Mẫn, Lương Minh Quân)

- Define raw-column mapping.
- Implement deterministic parsing and line/row issue logging.
- Export normalized JSONL.
- Validate random samples against the official lookup source.

Estimated work: ~7h. Deadline: **15 Jul, 23:00**.

Sub-tasks:

- Parser specification and source-column notes (Dương Huệ Mẫn), deadline **15 Jul, 12:00**.
- Parser implementation and JSONL writer (Lương Minh Quân), deadline **15 Jul, 20:00**.
- Sample verification and issue log (Dương Huệ Mẫn), deadline **15 Jul, 23:00**.

#### RxNorm parser (Dương Huệ Mẫn, Lương Minh Quân)

- Parse required RRF files.
- Filter selected TTYs and active/non-suppressed concepts.
- Export canonical concept records and source strings.

Estimated work: ~8h. Deadline: **16 Jul, 23:00**.

Sub-tasks:

- TTY/filter specification (Dương Huệ Mẫn), deadline **16 Jul, 11:00**.
- RRF parser implementation (Lương Minh Quân), deadline **16 Jul, 20:00**.
- Quality sample and record counts (Dương Huệ Mẫn), deadline **16 Jul, 23:00**.

#### Core-scope selection (Dương Huệ Mẫn, Khang review)

- Define inclusion/exclusion criteria.
- Select initial diagnosis/drug concept scope.
- Record counts and reasons.

Estimated work: ~3h. Deadline: **17 Jul, 15:00**.

#### Alias generation (Dương Huệ Mẫn, Lương Minh Quân)

- Generate safe mechanical variants.
- Preserve official names.
- Add reviewed abbreviations.
- Separate weak/ambiguous aliases.
- Deduplicate without hiding collisions.

Estimated work: ~7h. Deadline: **18 Jul, 20:00**.

Sub-tasks:

- Alias rules and unsafe-transform list (Dương Huệ Mẫn), deadline **17 Jul, 20:00**.
- ICD alias generator (Lương Minh Quân), deadline **18 Jul, 13:00**.
- RxNorm alias generator (Lương Minh Quân), deadline **18 Jul, 16:00**.
- Data review and weak-alias split (Dương Huệ Mẫn), deadline **18 Jul, 20:00**.

#### Data validation and provenance (Dương Huệ Mẫn, Nguyễn Hoàng Thái)

- Validate schema, duplicates, collisions, missing fields, and source versions.
- Update source registry and data notes.
- File bugs for parser/data defects.

Estimated work: ~5h. Deadline: **19 Jul, 20:00**.

#### Data maintenance from error analysis (Dương Huệ Mẫn, Nguyễn Hoàng Thái)

- Add missing safe aliases.
- Remove noisy aliases.
- Record all changes.
- Verify fixes against regression queries.

Estimated work: ~1h/day. Deadline: **daily 20–28 Jul, 22:00**.

---

### 3.3 Model — Khang, Võ Huỳnh Quốc Thái

#### Extraction specification (Khang, Võ Huỳnh Quốc Thái)

- Define labels, exact-span rule, assertion semantics, overlap policy, and LLM JSON schema.
- Define rule extractor versus LLM extractor responsibilities.

Estimated work: ~4h. Deadline: **15 Jul, 18:00**.

#### Ollama client and structured generation (Võ Huỳnh Quốc Thái)

- Implement health check, generate request, embed request, timeout, retry, and error handling.
- Support constrained JSON output where available.

Estimated work: ~4h. Deadline: **16 Jul, 18:00**.

#### Rule-based extractor (Võ Huỳnh Quốc Thái, Khang review)

- Implement high-precision patterns for medicine/dose, lab/result pairs, and assertion cues.
- Use ontology/abbreviation resources without converting symptoms directly into diagnoses.

Estimated work: ~6h. Deadline: **18 Jul, 20:00**.

Sub-tasks:

- Pattern and precedence specification (Khang), deadline **17 Jul, 12:00**.
- Extractor implementation (Võ Huỳnh Quốc Thái), deadline **18 Jul, 16:00**.
- Rule conflict review (Khang), deadline **18 Jul, 20:00**.

#### LLM extractor (Khang, Võ Huỳnh Quốc Thái)

- Build prompts and examples.
- Parse structured output.
- Preserve exact text and reject hallucinated spans.
- Return type and assertions without ontology codes.

Estimated work: ~6h. Deadline: **19 Jul, 20:00**.

#### Exact dense retrieval (Võ Huỳnh Quốc Thái)

- Embed aliases and queries with `bge-m3`.
- Normalize vectors.
- Implement NumPy cosine/dot-product exact search.
- Return alias-level results with metadata.

Estimated work: ~6h. Deadline: **19 Jul, 23:00**.

#### Sparse retrieval (Võ Huỳnh Quốc Thái)

- Implement tokenizer/normalizer.
- Implement BM25 and/or character TF-IDF from scratch.
- Return deterministic ranked aliases.

Estimated work: ~7h. Deadline: **20 Jul, 20:00**.

#### Code grouping and RRF (Võ Huỳnh Quốc Thái)

- Collapse each alias ranking to the best alias per code.
- Implement configurable code-level RRF.
- Return final ranked candidates.

Estimated work: ~4h. Deadline: **21 Jul, 15:00**.

#### HNSW implementation (Võ Huỳnh Quốc Thái; Khang review; Nguyễn Hoàng Thái benchmark)

- Implement random levels, layers, entry point, greedy descent, layer search, insertion, bidirectional edges, neighbor pruning, `M`, `M0`, `ef_construction`, and `ef_search`.
- Compare with exact search.

Estimated work: ~18–22h. Deadlines:

- Data structures and random levels (Võ Huỳnh Quốc Thái), **22 Jul, 13:00**.
- Greedy/layer search (Võ Huỳnh Quốc Thái), **22 Jul, 22:00**.
- Insertion and connections (Võ Huỳnh Quốc Thái), **23 Jul, 17:00**.
- Pruning and parameterization (Võ Huỳnh Quốc Thái), **23 Jul, 23:00**.
- Design review (Khang), **24 Jul, 12:00**.
- Exact-vs-HNSW benchmark (Nguyễn Hoàng Thái), **24 Jul, 22:00**.

#### Optional LLM reranker decision (Khang, Võ Huỳnh Quốc Thái)

- Implement only if core retrieval is stable.
- Constrain selection to retrieved candidates.
- Keep RRF as fallback.

Timebox: ~4h. Decision deadline: **25 Jul, 12:00**.

---

### 3.4 Pipeline — Khang, Võ Huỳnh Quốc Thái, Lương Minh Quân

#### Package, config, and schemas (Lương Minh Quân; Khang review)

- Implement package imports, config loader, dataclasses, and common IO.
- Ensure Streamlit and CLI import the same package.

Estimated work: ~5h. Deadline: **14 Jul, 23:00**.

#### CLI skeleton (Lương Minh Quân)

- Support text, single file, and directory modes.
- Write valid JSON and actionable errors.

Estimated work: ~4h. Deadline: **15 Jul, 18:00**.

#### Index build/load pipeline (Võ Huỳnh Quốc Thái, Lương Minh Quân)

- Build artifact manifests.
- Cache embeddings and sparse indexes.
- Load without rebuilding on each run.

Estimated work: ~6h. Deadline: **21 Jul, 20:00**.

#### Entity orchestration (Lương Minh Quân; Model modules supplied by Quốc Thái/Khang)

- Call rule and LLM extractors.
- Merge outputs.
- Align spans.
- Apply assertion post-processing.
- Validate entities.

Estimated work: ~7h. Deadline: **21 Jul, 23:00**.

#### Mapping orchestration (Lương Minh Quân, Võ Huỳnh Quốc Thái)

- Route diagnosis/drug entities.
- Build query/context payload.
- Call dense/sparse/RRF mapper.
- Add validated candidates.

Estimated work: ~5h. Deadline: **22 Jul, 20:00**.

#### Output validators and formatter (Lương Minh Quân, Nguyễn Hoàng Thái)

- Implement schema, span, routing, candidate, duplicate, and final-output checks.

Estimated work: ~6h. Deadline: **23 Jul, 20:00**.

#### Streamlit application (Lương Minh Quân)

- Keep `app.py` UI-only.
- Display input, extracted entities, assertions, candidates, internal timing, and final JSON.
- Handle missing Ollama/indexes gracefully.

Estimated work: ~6h. Deadline: **24 Jul, 23:00**.

#### Batch and ZIP packaging (Lương Minh Quân, Nguyễn Hoàng Thái verification)

- Process all input files deterministically.
- Validate before writing and zipping.
- Produce a manifest.

Estimated work: ~4h. Deadline: **26 Jul, 18:00**.

---

### 3.5 QA/Reviewer — Khang, Dương Huệ Mẫn, Nguyễn Hoàng Thái

#### QA plan and fixtures (Nguyễn Hoàng Thái)

- Define unit/integration/E2E coverage.
- Create fixture organization and expected-output conventions.

Estimated work: ~3h. Deadline: **15 Jul, 20:00**.

#### Unit tests (Nguyễn Hoàng Thái; developers support their modules)

- Normalization, alias generation, BM25/TF-IDF, RRF, span alignment, candidate validation, formatter, and packaging.

Estimated work: ~8h total. Milestones:

- First deterministic suite: **18 Jul, 23:00**.
- Core module coverage: **22 Jul, 23:00**.
- Freeze regression suite: **27 Jul, 20:00**.

#### Curated mapping queries (Nguyễn Hoàng Thái, Dương Huệ Mẫn support)

- Create hard queries, abbreviations, ambiguity cases, and negative controls.
- Keep curated queries separate from automatically generated smoke queries.

Estimated work: ~4h. Deadline: **20 Jul, 18:00**.

#### Clinical snippets and ground truth (Nguyễn Hoàng Thái)

- Create 30–50 snippets.
- Fully annotate 15–25 core cases.
- Cover all labels and assertion combinations.

Estimated work: ~10h. Deadline: **22 Jul, 23:00**.

#### Retrieval evaluation (Nguyễn Hoàng Thái, Võ Huỳnh Quốc Thái)

- Measure Recall@1/5/10, MRR, latency, and HNSW recall relative to exact.
- Compare dense, sparse, RRF, and optional reranker.

Estimated work: ~6h. Deadline: **25 Jul, 20:00**.

#### E2E evaluation and error analysis (Nguyễn Hoàng Thái, Dương Huệ Mẫn)

- Classify extraction, type, assertion, span, mapping, duplicate, schema, and runtime failures.
- Create regression tests for fixed deterministic bugs.

Estimated work: ~1.5h/day. Deadline: **daily 21–28 Jul, 22:00**.

#### Release-candidate QA (Nguyễn Hoàng Thái, Khang)

- Reproduce environment.
- Run full non-Ollama and selected Ollama/E2E tests.
- Validate demo, batch output, ZIP, and release checklist.

Estimated work: ~7h. Deadline: **27 Jul, 23:00**.

#### Final freeze verification (Nguyễn Hoàng Thái, Khang)

Estimated work: ~4h. Deadline: **28 Jul, 22:00**.

---

## 4. Person-first summary

### Khang

- Tech leadership and process.
- Architecture and interface approval.
- Model/extraction design.
- HNSW and pipeline review.
- Final QA, report, slides, video, and release.

### Dương Huệ Mẫn

- Official data sources and provenance.
- ICD/RxNorm parsing specification.
- Core subset and alias quality.
- Data QA and data fixes from error analysis.

### Võ Huỳnh Quốc Thái

- Ollama client.
- Rule/LLM extraction implementation.
- Exact dense and sparse retrieval.
- Code-level RRF.
- HNSW and retrieval benchmarks.

### Nguyễn Hoàng Thái

- QA strategy and curated fixtures.
- Unit/integration/E2E tests.
- Mapping queries and ground truth.
- Error analysis, regression verification, and release QA.

### Lương Minh Quân

- Package/config/data loaders.
- Parser implementation support.
- CLI and orchestration.
- Validators/formatter integration.
- Batch output and Streamlit application.
