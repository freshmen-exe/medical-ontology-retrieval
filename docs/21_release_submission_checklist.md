# Release and Submission Checklist

## 1. Release stages

### v0.1-mvp

- Repository and environment work.
- CLI skeleton runs.
- Small alias files load.
- At least one extraction and one mapping path run end to end.

### v0.2-core

- Rule and LLM extraction are integrated.
- Exact dense and sparse baselines work.
- Code-level RRF works.
- Validators and batch inference work.
- Core deterministic tests pass.

### v0.3-rc

- HNSW decision is complete.
- Retrieval and E2E metrics are recorded.
- Streamlit demo works.
- No open P0/P1 bugs.
- Output packaging is reproducible.

### v1.0-submission

- Code is frozen.
- Final output package is validated.
- Report, slides, and video are complete.
- Final tag and release notes are created.

## 2. Code freeze: 28 July 2026, 23:00 ICT

After freeze:

- No new feature.
- Only submission-critical bug fixes.
- Every change requires Tech Lead and QA approval.
- Every fix reruns the full deterministic suite and relevant E2E cases.

## 3. Repository checks

- `main` is clean and protected.
- CI passes on the final commit.
- `python scripts/pre_pr.py` passes in the Dev Container.
- No secrets, raw data, model weights, logs, indexes, or large generated files are tracked.
- `requirements.txt`, `pyproject.toml`, and Docker configuration agree.
- README and API documentation match the code.
- Source registry is current.

## 4. Runtime checks

- Fixed models pull successfully.
- Ollama health check passes.
- Alias and index artifacts load without rebuilding unexpectedly.
- Single-text CLI works.
- Batch CLI works.
- Streamlit works locally or in Colab.
- All fallback paths are tested.

## 5. Submission-output checks

- Expected number of JSON files exists.
- Filenames match input identifiers.
- Every JSON file parses.
- Every entity span matches source text.
- Only diagnoses and drugs have candidates.
- Diagnosis candidates belong to Vietnamese ICD-10 data.
- Drug candidates belong to RxNorm 2026 data.
- No duplicate output files.
- ZIP contains the correct root directory structure.

## 6. Report checks

- Problem statement and metric are represented accurately.
- Data sources and versions are cited.
- Architecture matches the implemented system.
- Results are reproducible and not cherry-picked.
- Dense-only, sparse-only, hybrid, and HNSW comparisons are included when available.
- Limitations and failed experiments are stated honestly.
- Tables and figures have captions and source references.

## 7. Slides and video checks

- Slides fit the presentation time.
- Demo input is fixed and tested.
- Video script matches the latest UI and metrics.
- No API key, personal path, or sensitive data appears on screen.
- Audio and screen resolution are understandable.
- Final exported files open on a second machine.

## 8. Git release

```bash
git switch main
git pull --rebase origin main
git tag -a v1.0-submission -m "Final submission release"
git push origin v1.0-submission
```

Create a GitHub Release from the tag with release notes, but do not upload externally restricted datasets or model weights.
