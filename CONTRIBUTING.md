# Contributing

Jira is the source of truth for work. GitHub is the source of truth for code and review. Do not begin
untracked work except an immediate P0 investigation; create or assign the Jira item as soon as the
system is available.

## Standard contribution flow

1. Move the Jira Task/Bug to `In Progress`.
2. Update local `main`:

   ```bash
   git switch main
   git pull --rebase origin main
   ```

3. Create a short-lived branch:

   ```bash
   git switch -c feature/MOR-34-code-level-rrf
   ```

4. Implement one coherent task with focused developer tests.
5. Save normally in VS Code; Ruff formats Python automatically on save.
6. Commit importable progress using Conventional Commits:

   ```bash
   git add src/medical_ontology/retrieval/rrf.py tests/unit/test_rrf.py
   git commit -m "feat(retrieval): implement code-level RRF fusion"
   ```

7. Rebase on current `main` and run the local PR gate:

   ```bash
   git fetch origin
   git rebase origin/main
   make pre-pr
   ```

8. Push and open a PR titled `[MOR-34] Implement code-level RRF fusion`.
9. Link the Jira item, fill every relevant PR-template section, and move Jira to `In Review`.
10. Address review comments with new commits; do not rewrite a branch while reviewers are actively
    reviewing unless you notify them.
11. After approval and CI, squash merge through GitHub and delete the branch.
12. QA verifies acceptance criteria and moves Jira from `QA` to `Done`.

## Commit expectations

- Commit after a coherent function/class/test slice, not every keystroke.
- A commit must import or compile unless its message clearly marks a temporary local WIP commit that
  will be squashed before review.
- Never mix formatting of unrelated files with a feature.
- Do not commit generated raw data, model files, embeddings, indexes, logs, output ZIPs, credentials,
  or personal configuration.

## Required reading

- `docs/03_github_workflow.md`
- `docs/04_jira_scrum_workflow.md`
- `docs/14_coding_standards.md`
- `docs/16_branch_commit_playbook.md`
- `docs/17_definition_of_done.md`
