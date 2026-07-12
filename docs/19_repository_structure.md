# Repository Structure and File Ownership

The repository is organized by responsibility. Do not place temporary files at the root. Create a
Jira task before adding a new top-level directory.

```text
medical-ontology-retrieval/
├── .devcontainer/
│   └── devcontainer.json              # VS Code standardized container
├── .github/
│   ├── workflows/ci.yml               # Remote format/lint/test gate
│   ├── CODEOWNERS.template             # Copy to CODEOWNERS after handles are known
│   └── pull_request_template.md
├── .vscode/
│   ├── extensions.json                 # Recommended/unwanted extensions
│   ├── launch.json                     # Debug launch profiles
│   ├── settings.json                   # Auto Save + Ruff + pytest workspace standard
│   └── tasks.json                      # Common VS Code tasks
├── artifacts/
│   ├── embeddings/                     # Generated; never commit full files
│   ├── indexes/                        # Exact/sparse/HNSW artifacts
│   └── README.md
├── config/
│   ├── default.yaml                    # Shared baseline
│   ├── local.example.yaml              # Copy to ignored local.yaml
│   ├── docker.yaml
│   ├── colab.yaml
│   ├── test.yaml
│   └── README.md
├── data/
│   ├── raw/
│   │   ├── icd10_vi_2026/SOURCE.md     # Official Vietnamese source provenance
│   │   └── rxnorm_2026/SOURCE.md       # Exact pinned RxNorm release provenance
│   ├── interim/                        # Generated extraction/cleaning outputs
│   ├── processed/                      # Versioned schemas and approved core JSONL
│   ├── candidates/                     # LLM/weak aliases awaiting review
│   ├── eval/                           # QA-owned queries, snippets, and ground truth
│   └── README.md
├── docs/
│   ├── 00_documentation_index.md       # Documentation entry point
│   ├── 01_project_workflow.md
│   ├── ...                             # Numbered process/technical manuals
│   ├── 23_troubleshooting.md
│   ├── adr/                            # Architecture Decision Records
│   └── problem_statement/
│       ├── original/                   # Untouched PDF/Markdown from organizer
│       └── derived/                    # Team summary, schema, metrics, assumptions
├── examples/                           # Small demo inputs safe to commit
├── experiments/                        # Metrics, benchmark outputs, error analyses
├── logs/                               # Runtime logs; ignored except README/.gitkeep
├── notebooks/
│   └── colab_ollama_streamlit.ipynb    # Three-cell weak-machine runtime
├── output/                             # Submission JSON and ZIP; ignored
├── prompts/
│   ├── extraction_system.txt
│   ├── extraction_examples.jsonl
│   └── reranker_system.txt
├── references/
│   ├── source_registry.md
│   ├── source_registry.jsonl
│   ├── data_sources.md
│   ├── algorithms.md
│   ├── tooling.md
│   ├── reading_list.md
│   ├── report_references.bib
│   └── competition/
├── reports/
│   ├── latex/                          # Versioned report source
│   ├── drafts/
│   └── final/
├── schemas/
│   ├── entity.schema.json
│   ├── output.schema.json
│   ├── alias.schema.json
│   └── ground_truth.schema.json
├── scripts/
│   ├── parse_icd10_vi.py
│   ├── parse_rxnorm_2026.py
│   ├── generate_icd_aliases.py
│   ├── generate_rxnorm_aliases.py
│   ├── validate_aliases.py
│   ├── build_indexes.py
│   ├── evaluate_retrieval.py
│   ├── evaluate_e2e.py
│   ├── package_output.py
│   ├── check_environment.py
│   └── pre_pr.py
├── slides/
│   ├── outline.md
│   ├── figures/
│   ├── pptx/
│   └── exports/
├── src/medical_ontology/
│   ├── clients/                        # Ollama HTTP client
│   ├── data/                           # Loading and normalization
│   ├── extraction/                     # Rule/LLM extraction and assertions
│   ├── retrieval/                      # Exact, sparse, RRF, HNSW, embeddings
│   ├── mapping/                        # Alias collapse, fusion, code mapping/reranking
│   ├── validation/                     # Entity/candidate/final gates
│   ├── indexing/                       # Offline index artifacts
│   ├── evaluation/                     # Reusable deterministic metrics
│   ├── pipeline/                       # End-to-end orchestration and formatting
│   ├── utils/
│   ├── config.py
│   ├── schema.py
│   └── infer.py
├── tests/
│   ├── unit/                           # Fast, isolated, no external service
│   ├── integration/                    # Multiple modules, no Ollama by default
│   ├── e2e/                            # Complete controlled workflow
│   ├── fixtures/
│   └── conftest.py
├── videos/
│   ├── script.md
│   ├── demo_checklist.md
│   ├── raw/
│   ├── edited/
│   └── final/
├── app.py                              # Thin Streamlit UI only
├── pyproject.toml                      # Package, Ruff, pytest, coverage settings
├── requirements*.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── DATA_NOTICE.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Ownership by path

| Path | Accountable role | Required reviewer |
|---|---|---|
| `data/`, data parsers, source manifests | Data | Data QA or Tech Lead |
| `extraction/`, `retrieval/`, `mapping/` | Model | Model peer or Tech Lead |
| `pipeline/`, CLI, Streamlit, config | Pipeline | Tech Lead or QA |
| `validation/`, `evaluation/`, `tests/` | QA | Relevant implementation owner |
| `.github/`, Docker, Dev Container, tooling | Tech Lead/Infrastructure | One developer |
| `reports/`, `slides/`, `videos/` | Deliverable owner | Tech Lead and QA |
| task statement and references | Tech Lead/Data | QA |

Copy `.github/CODEOWNERS.template` to `.github/CODEOWNERS` only after the team creates GitHub
handles. Do not leave invented handles in a live file.

## Commit policy by file type

Commit:

- source code and tests;
- small fixtures and reviewed eval records;
- configuration templates;
- source manifests/checksums;
- report/slide/video source documents;
- reproducible experiment summaries.

Do not commit:

- full raw RxNorm/ICD archives unless redistribution is explicitly approved;
- Ollama model files;
- full embedding matrices and HNSW pickles;
- logs, output ZIPs, generated PDFs, or personal `.env`/`local.yaml`;
- credentials or private participant data.

## Structure-only scaffold rule

All `.py` files under `src/`, `scripts/`, and `tests/`, plus the root `app.py`, are intentionally empty in this scaffold. The file tree defines ownership and expected locations; it does not provide implementation. Do not treat an empty placeholder as completed work.

## Planning

```text
planning/
├── jira/
│   ├── README.md
│   ├── jira_import_tasks.csv
│   ├── jira_task_catalog.csv
│   └── sprint_calendar.csv
├── meetings/
│   ├── README.md
│   └── 2026-07-12-kickoff.md
└── setup/
    └── team_environment_signoff.csv
```
