# Implementation Handoff

This document explains how the team turns the structure-only scaffold into working software without mixing responsibilities.

## Rule

No implementation is added directly to `main`. Every implementation begins with a Jira issue, a task branch, atomic commits, a pull request, CI, review, and QA validation.

## Ownership

- **Data** owns source acquisition, provenance, parsing requirements, ontology selection, alias policy, and approved data artifacts.
- **Model** owns extraction logic, assertion logic, embeddings, dense retrieval, sparse retrieval, RRF, HNSW, candidate ranking, and model-side evaluation runners.
- **Pipeline** owns loading, orchestration, merging, span alignment integration, routing, formatting, CLI, batch processing, Streamlit wiring, and runtime configuration.
- **QA/Reviewer** owns test design, fixtures, mapping queries, ground truth, expected behavior, regression coverage, error analysis, and release acceptance.
- **Tech Lead** owns architecture, interfaces, task decomposition, review policy, scope decisions, integration approval, and final release readiness.

## First implementation sequence

1. QA defines expected behavior and initial fixtures.
2. Data prepares the first approved source and processed-data contracts.
3. Pipeline implements loaders and shared schemas.
4. Model implements deterministic baselines before advanced algorithms.
5. QA adds unit and integration tests against the agreed contracts.
6. Pipeline connects modules only after their interfaces are reviewed.
7. Advanced work such as HNSW and LLM reranking begins only after the baseline is stable.

## Empty-file policy

An empty file is not a completed task. It is a reserved implementation location. The Jira issue and planned API contract determine what must eventually be implemented there.

The team should not change shared setup files without a dedicated `infra` Jira task and Tech Lead review. Normal work should focus on domain source files, QA tests/data, prompts, and deliverable content.
