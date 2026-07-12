# Implementation Boundary

This repository is fully configured for collaboration and development. The team should not spend time setting up formatting, linting, test discovery, pre-commit hooks, CI, Docker, VS Code, Jira task structure, documentation locations, or source registries.

## Already configured

- VS Code workspace settings and recommended extensions
- Auto Save on editor focus change
- Ruff formatting on every save
- Dockerfile and VS Code Dev Container
- pinned runtime and development dependencies
- editable Python package layout
- pre-commit and pre-push hooks
- GitHub Actions CI
- GitHub Flow, commit, pull request, and review rules
- Jira Scrum import files, sprint calendar, and import guide
- source, data, report, slide, video, meeting, and planning paths
- local and Colab runtime documentation
- repository validation and pre-PR infrastructure scripts

## The team implements

- all medical ontology parsing and alias algorithms
- all extraction, assertion, retrieval, RRF, HNSW, mapping, validation, and pipeline logic
- Streamlit application logic
- prompts and examples
- QA test cases, test fixtures, ground truth, and evaluation data
- report, slide, and video content

All domain Python files and QA test files intentionally remain empty. Infrastructure helper scripts are implemented because they are part of the standardized setup, not the research solution.

## Unavoidable account-specific actions

The scaffold cannot perform actions that require the team's private accounts. The Tech Lead must still:

1. Create/invite members to GitHub and Jira.
2. Create the Jira project and import the provided CSV.
3. Replace GitHub handle placeholders in CODEOWNERS after handles are known.
4. Configure protected-branch rules in the GitHub UI.
5. Upload licensed/raw data and local model weights outside Git.
