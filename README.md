# Medical Ontology Retrieval

A research-oriented system for extracting medical entities from free-form Vietnamese clinical text, assigning assertion attributes, and mapping diagnoses and drugs to **Vietnamese ICD-10** and **RxNorm 2026** candidates.


> [!IMPORTANT]
> This repository is a **setup-complete implementation scaffold**. Collaboration tooling, VS Code, Docker, Ruff, pytest discovery, pre-commit, CI, Jira import files, documentation paths, and planning files are already configured. The team implements only the domain algorithms, QA tests/data, prompts, and deliverable content. See [`IMPLEMENTATION_BOUNDARY.md`](IMPLEMENTATION_BOUNDARY.md).

The team will implement the core algorithms directly with Python, the standard library, and NumPy. The project does **not** use ready-made vector databases, ANN libraries, retrieval frameworks, or orchestration frameworks for the core solution.

## Scaffold and project status

- Initial team kickoff: **12 July 2026, 09:00 ICT**
- Development window: **12 July 2026 – 28 July 2026**
- Code freeze: **28 July 2026, 23:00 ICT**
- Report, slides, and demo video: **29 July 2026 – 2 August 2026**
- Submission target: **before 3 August 2026**

## Fixed runtime models

| Purpose | Ollama model |
|---|---|
| Clinical entity extraction and optional candidate reranking | `vicuna:7b-v1.5-q5_1` |
| Text embeddings | `bge-m3` |

These two models are project constants unless the Tech Lead records an approved architecture decision.

---

## 1. Final engineering decisions

| Area | Decision |
|---|---|
| Project management | **Jira Scrum**, used as the single source of truth for tasks, bugs, owners, deadlines, and sprints |
| Source control | GitHub repository |
| Branching model | **GitHub Flow** with a protected `main` branch |
| Merge method | Squash merge after review and CI |
| IDE | VS Code |
| Standard environment | Docker + VS Code Dev Container |
| Local fallback | Python 3.13 virtual environment |
| Weak-machine runtime | Google Colab + Ollama + Streamlit + Cloudflare Quick Tunnel |
| Formatter and linter | **Ruff only**; do not install or run Black/isort separately |
| Test framework | pytest |
| Local quality gates | pre-commit and pre-push hooks |
| Remote quality gate | GitHub Actions CI |
| Python package layout | `src/medical_ontology/` with editable installation |
| Core numerical library | NumPy |
| Runtime service | Ollama HTTP API |
| Demo UI | Streamlit |

### Why Jira and GitHub are both used

- Jira manages planning, sprint work, bugs, blockers, deadlines, estimates, and ownership.
- GitHub manages branches, commits, pull requests, reviews, and CI.
- GitHub Projects and GitHub Issues are not used for duplicate task tracking.
- Every branch and pull request includes its Jira key so work remains traceable.

### Why Docker is used

Docker standardizes Python, dependencies, Ruff, pytest, scripts, and Streamlit. Ollama is intentionally kept outside the development container because local GPU and Windows Docker configurations vary. Ollama runs on the host or on Colab.

---

## 2. Documentation map

Start with [`docs/00_documentation_index.md`](docs/00_documentation_index.md).

| Topic | Document |
|---|---|
| Complete system workflow | [`docs/01_project_workflow.md`](docs/01_project_workflow.md) |
| Environment and tooling | [`docs/02_environment_and_tooling.md`](docs/02_environment_and_tooling.md) |
| Git and GitHub workflow | [`docs/03_github_workflow.md`](docs/03_github_workflow.md) |
| Jira Scrum workflow | [`docs/04_jira_scrum_workflow.md`](docs/04_jira_scrum_workflow.md) |
| Roles, tasks, owners, deadlines | [`docs/05_roles_tasks_deadlines.md`](docs/05_roles_tasks_deadlines.md) |
| Data and ontology workflow | [`docs/06_data_workflow_and_sources.md`](docs/06_data_workflow_and_sources.md) |
| Model and retrieval workflow | [`docs/07_model_workflow.md`](docs/07_model_workflow.md) |
| End-to-end pipeline workflow | [`docs/08_pipeline_workflow.md`](docs/08_pipeline_workflow.md) |
| QA and testing | [`docs/09_testing_and_qa.md`](docs/09_testing_and_qa.md) |
| Colab, Ollama, Streamlit, Cloudflare | [`docs/10_colab_ollama_streamlit.md`](docs/10_colab_ollama_streamlit.md) |
| Docker and Dev Container | [`docs/11_docker_devcontainer.md`](docs/11_docker_devcontainer.md) |
| LaTeX report, slides, and video | [`docs/12_reporting_slides_video.md`](docs/12_reporting_slides_video.md) |
| Planned classes and functions | [`docs/13_api_spec.md`](docs/13_api_spec.md) |
| Python and documentation standards | [`docs/14_coding_standards.md`](docs/14_coding_standards.md) |
| VS Code workspace standard | [`docs/15_vscode_workspace_standard.md`](docs/15_vscode_workspace_standard.md) |
| Git command playbook | [`docs/16_branch_commit_playbook.md`](docs/16_branch_commit_playbook.md) |
| Definition of Ready and Done | [`docs/17_definition_of_done.md`](docs/17_definition_of_done.md) |
| Risks and fallback plans | [`docs/18_risk_fallback_plan.md`](docs/18_risk_fallback_plan.md) |
| Full repository structure | [`docs/19_repository_structure.md`](docs/19_repository_structure.md) |
| Source and citation policy | [`docs/20_source_and_citation_policy.md`](docs/20_source_and_citation_policy.md) |
| Release and submission checklist | [`docs/21_release_submission_checklist.md`](docs/21_release_submission_checklist.md) |
| New-member onboarding | [`docs/22_onboarding_checklist.md`](docs/22_onboarding_checklist.md) |
| Troubleshooting | [`docs/23_troubleshooting.md`](docs/23_troubleshooting.md) |
| Data, algorithm, tooling references | [`references/reading_list.md`](references/reading_list.md) |
| Public API/class contracts | [`docs/13_api_spec.md`](docs/13_api_spec.md) |
| Jira import package | [`planning/jira/README.md`](planning/jira/README.md) |
| Sprint calendar | [`planning/jira/sprint_calendar.csv`](planning/jira/sprint_calendar.csv) |
| Kickoff meeting | [`planning/meetings/2026-07-12-kickoff.md`](planning/meetings/2026-07-12-kickoff.md) |
| Implementation boundary | [`IMPLEMENTATION_BOUNDARY.md`](IMPLEMENTATION_BOUNDARY.md) |

Official task files are stored under:

```text
docs/problem_statement/original/
├── Viettel_AI_Race_2026_Bai_2.pdf
├── Viettel_AI_Race_2026_Bai_2.md
└── SOURCE.md
```

Team-derived summaries are stored separately under `docs/problem_statement/derived/` so the original statement is never overwritten.

---


## 2.1 What a team member must do before coding

The standardized path is intentionally short:

1. Clone the repository.
2. Open it in VS Code.
3. Select **Dev Containers: Reopen in Container**.
4. Wait for the automatic setup to finish.
5. Run `make check-env`.
6. Create or switch to the Jira-linked branch and begin implementation.

The container installs the pinned dependencies, enables shared extensions/settings, installs Git hooks, and verifies the environment. Team members do not configure Ruff, pytest, pre-commit, or package paths manually.

## 3. Complete project workflow

```text
1. Acquire authoritative ontology data
   Vietnamese ICD-10 + RxNorm 2026

2. Parse and normalize source data
   raw files → clean code records

3. Select the project ontology scope
   core diagnosis codes + active RxNorm concepts

4. Generate and validate aliases
   official names + safe normalized variants + reviewed abbreviations

5. Build retrieval indexes
   exact dense index + self-coded sparse index + optional self-coded HNSW

6. Extract entities from clinical text
   rule-based extractor + LLM extractor
   → exact source span + entity type + assertions

7. Validate and align extracted entities
   span, type, assertion, duplicate, and overlap validation

8. Route only mappable entities
   CHẨN_ĐOÁN → Vietnamese ICD-10
   THUỐC → RxNorm 2026

9. Retrieve and rank candidates
   dense search + sparse search
   → group aliases by code
   → code-level Reciprocal Rank Fusion
   → optional constrained LLM reranker

10. Validate and format final output
    candidate-system validation + exact output schema

11. Evaluate and iterate
    deterministic unit tests + retrieval evaluation + E2E evaluation
    → error analysis → targeted fixes

12. Package deliverables
    output JSON files + output.zip + Streamlit demo
    + LaTeX report + slides + demo video
```

Detailed architecture: [`docs/01_project_workflow.md`](docs/01_project_workflow.md).

---

## 4. Scope policy

### Required core

- Vietnamese ICD-10 source acquisition and parsing.
- RxNorm 2026 source acquisition and parsing.
- Alias generation and validation.
- Rule-based medical entity extraction.
- LLM-assisted extraction of exact spans, labels, and assertions.
- Exact dense search implemented with NumPy.
- Sparse lexical retrieval implemented by the team.
- Code-level RRF.
- Candidate validation and output validation.
- CLI and batch inference.
- pytest-based deterministic tests.
- Retrieval and end-to-end evaluation.
- Streamlit demo.
- Report, slides, and video.

### Advanced work after the core is stable

- Self-coded HNSW with multi-layer insertion and search.
- LLM candidate reranking constrained to retrieved candidates.
- Larger ontology scope.
- Embedding fine-tuning only if the core is complete early and evaluation proves improvement.

### Explicit non-goals for the core version

- No FAISS, hnswlib, Annoy, ChromaDB, Milvus, Pinecone, or other vector database/ANN implementation.
- No LangChain, LlamaIndex, Haystack, or similar orchestration framework.
- No scikit-learn implementation of TF-IDF, BM25, cosine search, or clustering used as the project algorithm.
- No full LLM fine-tuning in the core schedule.
- No production API service, authentication system, Kubernetes, or cloud production deployment.
- No duplicate task tracking in GitHub Projects.

Development tools such as Ruff, pytest, pre-commit, Docker, VS Code, Streamlit, and GitHub Actions are allowed because they do not implement the research algorithms.

---

## 5. Local setup

### Requirements

- Git
- VS Code
- Docker Desktop for the standard Dev Container workflow
- Python 3.13 for the local fallback workflow
- Ollama when running models locally

### Clone

```bash
git clone https://github.com/<organization>/medical-ontology-retrieval.git
cd medical-ontology-retrieval
code .
```

### Recommended: reopen in the Dev Container

1. Install Docker Desktop.
2. Install the VS Code **Dev Containers** extension.
3. Open the repository in VS Code.
4. Press `Ctrl+Shift+P`.
5. Select `Dev Containers: Reopen in Container`.
6. Wait until the container setup completes.
7. Run `make check-env`.

The repository recommends all VS Code extensions automatically. Workspace settings enable:

- Auto Save on editor focus change.
- Ruff formatting on every save.
- Ruff import organization on explicit and auto saves.
- Ruff safe fixes on explicit saves.
- pytest discovery.
- Pylance basic type checking.

### Local virtual environment fallback

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
pre-commit install --hook-type pre-commit --hook-type pre-push
```

Linux/macOS:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
pre-commit install --hook-type pre-commit --hook-type pre-push
```

### Pull the fixed models locally

```bash
ollama pull vicuna:7b-v1.5-q5_1
ollama pull bge-m3
ollama serve
```

Default Ollama endpoint:

```text
http://localhost:11434
```

Copy `.env.example` to `.env` and adjust only machine-specific values. Never commit `.env`.

---

## 6. Standard commands

```bash
make setup            # install package, dev tools, and Git hooks
make check-env        # verify Python, package imports, files, and Ollama reachability
make format           # apply Ruff fixes, import sorting, and formatting
make lint             # verify Ruff format and lint without changing files
make test             # run fast deterministic tests
make test-all         # run all tests except Ollama-dependent tests
make coverage         # run tests with coverage
make pre-pr           # full local pull-request gate
make build-data       # parse sources and generate validated alias files
make build-index      # show the required explicit index-build command
make eval-retrieval   # show the required QA-query evaluation command
make eval-e2e         # show the required prediction/ground-truth command
make demo             # run Streamlit
make docker-test      # run pre-PR checks in Docker
make zip-output       # create output.zip
```

Manual equivalent before every pull request:

```bash
python -m ruff check . --fix
python -m ruff format .
python -m ruff format . --check
python -m ruff check .
python -m pytest -m "not slow and not ollama and not e2e"
```

---

## 7. Testing ownership and execution

QA owns the curated test cases, ground truth, expected behavior, and defect verification. Developers still write focused tests for deterministic code they add, because code is not ready for QA if it cannot be checked locally.

Test levels:

```text
tests/unit/          one function or class, no external service
tests/integration/   several modules together, no Ollama by default
tests/e2e/           complete pipeline on controlled fixtures
tests/fixtures/      small version-controlled test data
```

Commands:

```bash
python -m pytest tests/unit
python -m pytest -m integration
python -m pytest -m e2e
python -m pytest -m ollama
python -m pytest tests/unit/test_rrf.py -vv
```

GitHub Actions runs deterministic tests only. It never downloads or runs Ollama models.

---

## 8. Jira and GitHub workflow

### Jira is the project-management source of truth

Use a lean Scrum project with key `MOR`.

- Issue types: Epic, Task, Bug, Sub-task.
- Workflow: Backlog → Ready → In Progress → In Review → QA → Done.
- A blocked work item is flagged and commented; `Blocked` is not a separate workflow state.
- Sprints are three days because the project window is short.
- Estimate using hours, not story points.
- Components: Data, Extraction, Retrieval, Pipeline, QA, Infrastructure, Documentation-Demo.

Full instructions: [`docs/04_jira_scrum_workflow.md`](docs/04_jira_scrum_workflow.md).

### GitHub is the code source of truth

`main` is protected and must remain importable, testable, and demo-ready.

Branch format:

```text
<type>/MOR-<jira-number>-<short-kebab-description>
```

Examples:

```text
feature/MOR-21-icd-alias-generator
feature/MOR-34-code-level-rrf
bugfix/MOR-48-span-alignment
experiment/MOR-52-hnsw-neighbor-pruning
test/MOR-57-candidate-validator
docs/MOR-61-colab-guide
infra/MOR-65-devcontainer
```

Create a branch:

```bash
git switch main
git pull --rebase origin main
git switch -c feature/MOR-34-code-level-rrf
```

Commit coherent, importable progress:

```bash
git add src/medical_ontology/retrieval/rrf.py tests/unit/test_rrf.py
git commit -m "feat(retrieval): implement code-level RRF fusion"
```

Small development commits are allowed. Do not commit broken or unrelated changes. GitHub squash-merges the PR into one clean commit after CI and review.

Push and open the PR:

```bash
git push -u origin feature/MOR-34-code-level-rrf
```

PR title:

```text
[MOR-34] Implement code-level RRF fusion
```

Full Git and recovery playbook:

- [`docs/03_github_workflow.md`](docs/03_github_workflow.md)
- [`docs/16_branch_commit_playbook.md`](docs/16_branch_commit_playbook.md)

---

## 9. Run Streamlit

`app.py` is intentionally a thin UI entry point. It imports the package from `src/medical_ontology/`; project logic must never be copied into `app.py`.

```bash
python -m streamlit run app.py
```

Docker:

```bash
docker compose up --build app
```

Open:

```text
http://localhost:8501
```

---

## 10. Run on Google Colab

Use the prepared notebook:

[`notebooks/colab_ollama_streamlit.ipynb`](notebooks/colab_ollama_streamlit.ipynb)

The notebook contains three main cells:

1. Clone any selected Git branch, install Ollama and Cloudflared, start Ollama, and pull the fixed models.
2. Install repository dependencies and the package in editable mode.
3. start Ollama if necessary, run Streamlit from the repository root, and expose port 8501 with a Cloudflare Quick Tunnel.

Quick Tunnels are for temporary development/demo access only. Do not treat the generated URL as production deployment.

Detailed guide: [`docs/10_colab_ollama_streamlit.md`](docs/10_colab_ollama_streamlit.md).

---

## 11. Data sources

### Vietnamese ICD-10 target

The project target is the **Vietnamese ICD-10 list issued under Circular 06/2026/TT-BYT**, not ICD-10-CM and not a generic WHO browser export.

Authoritative starting points:

- Government document page: <https://chinhphu.vn/?docid=217536&pageid=27160>
- Circular PDF: <https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt.pdf>
- Vietnamese ICD-10 appendix PDF: <https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt-kem.pdf>
- Vietnamese clinical coding lookup system for cross-checking: <https://icd.kcb.vn/>

Store source files and provenance under:

```text
data/raw/icd10_vi_2026/
```

### RxNorm 2026 target

Use an official 2026 RxNorm monthly release from the U.S. National Library of Medicine. The release may require a free UMLS Terminology Services account and license acceptance.

Authoritative starting points:

- Release discovery endpoint: <https://uts-ws.nlm.nih.gov/releases?releaseType=rxnorm-full-monthly-release>
- RxNorm file format documentation: <https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html>
- RxNorm API for spot verification: <https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html>
- July 2026 release notice: <https://www.nlm.nih.gov/pubs/techbull/ja26/brief/ja26_rxnorm_july.html>

At source acquisition time, select one exact official 2026 monthly archive, then freeze its release
version and checksum in `data/raw/rxnorm_2026/SOURCE.md`. Never silently replace it with a newer
month during the same experiment cycle.

Store source files and provenance under:

```text
data/raw/rxnorm_2026/
```

Never commit full raw licensed data, model weights, generated embeddings, or HNSW indexes. Commit source manifests, checksums, schemas, small fixtures, and reproducible scripts.

Complete registry: [`references/source_registry.md`](references/source_registry.md).

---

## 12. Repository outputs

| Deliverable | Path |
|---|---|
| Original task PDF/Markdown | `docs/problem_statement/original/` |
| Parsed ontology records | `data/processed/` |
| Test cases and ground truth | `data/eval/` |
| Cached indexes | `artifacts/` |
| Experiment outputs | `experiments/` |
| Submission JSON/ZIP | `output/` |
| LaTeX report | `reports/latex/` |
| Final report exports | `reports/final/` |
| PowerPoint and slide exports | `slides/` |
| Video script/raw/edit/final | `videos/` |
| Public sources and citations | `references/` |

Full tree: [`docs/19_repository_structure.md`](docs/19_repository_structure.md).

---

## 13. Team roles

| Person | Roles |
|---|---|
| Khang | Tech Lead; Model; Pipeline; QA/Reviewer; final integration and deliverables |
| Dương Huệ Mẫn | Data Lead; Data QA; source and alias quality |
| Võ Huỳnh Quốc Thái | Model Lead; retrieval; RRF; HNSW; benchmarks; mapping logic |
| Nguyễn Hoàng Thái | QA Lead; test design; ground truth; error analysis; release verification |
| Lương Minh Quân | Pipeline Lead; data loading; orchestration; CLI; batch output; Streamlit |

Atomic task ownership, estimates, and deadlines are defined in [`docs/05_roles_tasks_deadlines.md`](docs/05_roles_tasks_deadlines.md).

---

## 14. Merge and release rules

A PR can merge only when:

- Jira acceptance criteria are satisfied.
- The branch is rebased on the latest `main`.
- Ruff formatting and linting pass.
- Relevant deterministic tests pass.
- At least one qualified reviewer approves.
- Conversations are resolved.
- No secrets, raw licensed datasets, model weights, or generated large artifacts are included.
- Public interfaces and documentation are updated when changed.

Repository settings should:

- Protect `main`.
- Require a pull request.
- Require one approval.
- Require the `lint-and-test` CI check.
- Require conversation resolution.
- Block force pushes and branch deletion.
- Allow squash merge only.
- Automatically delete merged branches.

Release milestones:

```text
v0.1-mvp         end-to-end skeleton
v0.2-core        stable extraction and hybrid mapping
v0.3-rc          release candidate and full QA
v1.0-submission  frozen submission package
```

---

## 15. License and data notice

Team-authored source code is licensed under the MIT License. External data, model files, competition material, and ontology files keep their original licenses and terms. Read [`DATA_NOTICE.md`](DATA_NOTICE.md) before distributing data or artifacts.

---

## 16. Authoritative technical references

- GitHub Flow: <https://docs.github.com/en/get-started/using-github/github-flow>
- Protected branches: <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches>
- Jira Scrum backlog: <https://support.atlassian.com/jira-software-cloud/docs/use-your-scrum-backlog/>
- VS Code Dev Containers: <https://code.visualstudio.com/docs/devcontainers/containers>
- VS Code Auto Save: <https://code.visualstudio.com/docs/editing/codebasics>
- Ruff formatter: <https://docs.astral.sh/ruff/formatter/>
- Ruff editor integration: <https://docs.astral.sh/ruff/editors/>
- pytest: <https://docs.pytest.org/>
- pre-commit: <https://pre-commit.com/>
- GitHub Actions for Python: <https://docs.github.com/en/actions/tutorials/build-and-test-code/python>
- Ollama API: <https://docs.ollama.com/api/introduction>
- Ollama embeddings: <https://docs.ollama.com/api/embed>
- Streamlit app execution: <https://docs.streamlit.io/develop/concepts/architecture/run-your-app>
- Cloudflare Quick Tunnels: <https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/>
## 17. Starter-repository validation status

The repository starter contains working deterministic implementations and tests for normalization,
JSONL IO, rule extraction, exact cosine search, BM25, character TF-IDF, code-level RRF, span
alignment, output validation, and a self-coded HNSW baseline. Ollama-dependent behavior remains an
external-runtime concern and is intentionally excluded from CI.

No workflow is permanently perfect. After team use begins, change tooling or process only when a
real recurring problem is documented in Jira and, for architecture/tooling changes, an ADR explains
why the added complexity is justified.
