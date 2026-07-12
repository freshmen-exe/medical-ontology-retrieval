# Source Registry

Register a source before using it for data acquisition, implementation decisions, evaluation, or
report claims. Record the exact accessed date and archive checksum in the corresponding
`data/raw/.../SOURCE.md` when downloading a file.

## Competition

| ID | Source | Purpose |
|---|---|---|
| `competition_task_pdf` | Original task PDF stored in `docs/problem_statement/original/` | Authoritative task statement |
| `competition_clarifications` | `references/competition/clarifications.md` | Organizer clarifications and dates |

## Authoritative data sources

| ID | Source | Purpose |
|---|---|---|
| `icd10_vi_tt06_2026` | https://chinhphu.vn/?docid=217536&pageid=27160 | Vietnamese ICD-10 regulation and attachments |
| `icd10_vi_appendix_pdf` | https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt-kem.pdf | Official Vietnamese ICD-10 appendix |
| `icd10_vi_circular_pdf` | https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/4/06-byt.pdf | Circular text and coding rules |
| `icd_kcb_vn` | https://icd.kcb.vn/icd-10/icd10 | Vietnamese lookup and cross-check source |
| `rxnorm_release_files` | https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html | Official RRF format and release documentation |
| `rxnorm_release_endpoint` | https://uts-ws.nlm.nih.gov/releases?releaseType=rxnorm-full-monthly-release | Discover and pin the exact 2026 monthly release |
| `rxnorm_july_2026` | https://www.nlm.nih.gov/pubs/techbull/ja26/brief/ja26_rxnorm_july.html | July 2026 release notice |
| `rxnorm_api` | https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html | Verification API reference |

**Target policy:** diagnosis candidates use the Vietnamese ICD-10 source named by the organizer,
not ICD-10-CM and not an independently translated WHO browser export. Drug candidates use a
pinned official RxNorm 2026 monthly release.

## Algorithms and implementation reading

| ID | Source | Purpose |
|---|---|---|
| `hnsw_paper` | https://arxiv.org/abs/1603.09320 | Original HNSW algorithm |
| `rrf_paper` | https://doi.org/10.1145/1571941.1572114 | Reciprocal Rank Fusion |
| `stanford_ir_book` | https://nlp.stanford.edu/IR-book/ | TF-IDF, cosine similarity, inverted indexes, evaluation |
| `bm25_reference` | https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html | BM25 background |

## Runtime models and APIs

| ID | Source | Purpose |
|---|---|---|
| `ollama_vicuna_tag` | https://ollama.com/library/vicuna:7b-v1.5-q5_1 | Fixed LLM model tag |
| `ollama_bge_m3` | https://ollama.com/library/bge-m3 | Fixed embedding model tag |
| `ollama_generate_api` | https://docs.ollama.com/api/generate | Structured generation client |
| `ollama_embed_api` | https://docs.ollama.com/api/embed | Batch embedding client |

## Engineering tools

| ID | Source | Purpose |
|---|---|---|
| `jira_scrum_backlog` | https://support.atlassian.com/jira-software-cloud/docs/use-your-scrum-backlog/ | Jira Scrum backlog and sprint planning |
| `github_flow` | https://docs.github.com/en/get-started/using-github/github-flow | Branch and PR workflow |
| `github_branch_protection` | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | Protect `main` |
| `github_actions_python` | https://docs.github.com/en/actions/tutorials/build-and-test-code/python | Python CI |
| `vscode_settings` | https://code.visualstudio.com/docs/configure/settings | Workspace settings and Auto Save |
| `vscode_devcontainers` | https://code.visualstudio.com/docs/devcontainers/containers | Dev Container workflow |
| `ruff_docs` | https://docs.astral.sh/ruff/ | Formatting and linting |
| `pytest_docs` | https://docs.pytest.org/en/stable/ | Unit, integration, and marker-based testing |
| `pre_commit_docs` | https://pre-commit.com/ | Local Git hooks |
| `docker_compose_docs` | https://docs.docker.com/compose/ | Container orchestration for app/test services |
| `streamlit_run` | https://docs.streamlit.io/develop/api-reference/cli/run | Demo command |
| `cloudflare_quick_tunnel` | https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/ | Temporary Colab demo tunnel |

## Reporting

| ID | Source | Purpose |
|---|---|---|
| `latex_project_docs` | https://www.latex-project.org/help/documentation/ | LaTeX reference |
| `overleaf_learn` | https://www.overleaf.com/learn | Collaborative report writing reference |

See the topic-specific reading lists in `references/algorithms.md`, `references/data_sources.md`,
`references/tooling.md`, and `references/reading_list.md`.
