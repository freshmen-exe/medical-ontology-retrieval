# Git and GitHub Workflow

## 1. Branch model

Use GitHub Flow with one long-lived branch:

```text
main
```

`main` must always be importable, CI-passing, and suitable for a demo. Do not create `develop`, permanent feature branches, personal integration branches, or GitFlow release branches.

## 2. Branch naming

```text
<type>/MOR-<jira-number>-<short-kebab-description>
```

Allowed types:

- `feature`
- `bugfix`
- `test`
- `docs`
- `refactor`
- `experiment`
- `infra`
- `chore`

Examples:

```text
feature/MOR-34-code-level-rrf
bugfix/MOR-48-repeated-span-alignment
test/MOR-57-output-validator-cases
docs/MOR-61-colab-guide
experiment/MOR-72-hnsw-neighbor-heuristic
infra/MOR-81-devcontainer
```

## 3. Start work

Confirm the Jira item is Ready and assigned to you.

```bash
git switch main
git fetch origin
git pull --rebase origin main
git switch -c feature/MOR-34-code-level-rrf
```

Never branch from another unfinished feature unless the Tech Lead explicitly approves a dependent stacked-PR workflow.

## 4. Commit policy

Commit coherent progress. A commit should import or compile and should not mix unrelated concerns.

Use Conventional Commits:

```text
<type>(<scope>): <imperative summary>
```

Common types:

```text
feat fix test docs refactor perf data ci chore
```

Common scopes:

```text
data extraction retrieval mapping hnsw pipeline validation qa demo infra docs
```

Examples:

```text
feat(retrieval): implement code-level RRF fusion
fix(validation): align repeated entity mentions deterministically
test(mapping): add ambiguous abbreviation cases
data(icd): normalize Vietnamese ICD code records
docs(colab): document branch-based demo startup
```

Optional body:

```text
Explain the reason, constraints, and non-obvious trade-offs.

Refs MOR-34
```

Small WIP commits are allowed on your own branch. The PR is squash-merged, so the final `main` history stays clean. Do not use meaningless messages such as `update`, `fix`, `done`, or `abc`.

## 5. Stage carefully

Prefer explicit files:

```bash
git status
git diff
git add src/medical_ontology/retrieval/rrf.py tests/unit/test_rrf.py
git diff --staged
git commit -m "feat(retrieval): implement code-level RRF fusion"
```

`git add -A` is acceptable only after reviewing status and diff.

## 6. Keep the branch current

Before opening and before merging a PR:

```bash
git fetch origin
git rebase origin/main
```

Resolve conflicts, test, then update your remote branch:

```bash
git push --force-with-lease
```

Never use plain `--force`. Never force-push `main`.

## 7. Local quality gate

```bash
python scripts/pre_pr.py
```

This checks formatting, lint, compilation, and deterministic tests.

## 8. Open the PR

```bash
git push -u origin feature/MOR-34-code-level-rrf
```

PR title:

```text
[MOR-34] Implement code-level RRF fusion
```

Complete the PR template. Add the Jira URL, test commands, evidence, risk, and fallback.

## 9. Review responsibility

- Author performs a self-review first.
- Reviewer checks behavior, interface, tests, scope, and documentation.
- QA checks acceptance behavior after code review when required.
- Tech Lead reviews architecture-sensitive, submission-critical, or cross-component changes.

Do not approve a PR only because CI is green. CI cannot validate medical-label quality or architecture decisions.

## 10. Merge policy

Use **Squash and merge**. The squash title should be a clean conventional summary with the Jira key, for example:

```text
[MOR-34] feat(retrieval): implement code-level RRF fusion
```

After merge:

```bash
git switch main
git pull --rebase origin main
git branch -d feature/MOR-34-code-level-rrf
git fetch --prune
```

GitHub should automatically delete the remote branch.

## 11. Protected `main`

Configure repository rules to require:

- pull request before merge;
- one approving review;
- `lint-and-test` status check;
- resolved conversations;
- no force push;
- no deletion;
- squash merge only.

## 12. Emergency fixes

Submission-critical bugs still use a branch and PR:

```text
bugfix/MOR-###-short-description
```

The Tech Lead may request an expedited review, but direct pushes to `main` remain prohibited.
