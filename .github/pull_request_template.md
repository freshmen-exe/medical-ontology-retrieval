## Jira work item

- Jira key: `MOR-___`
- Link: `<paste Jira URL>`

## Summary

Explain what changed and why.

## Scope

- [ ] One coherent Jira task or bug
- [ ] No unrelated refactor or formatting-only changes

## Verification

List exact commands and results.

```bash
python scripts/pre_pr.py
```

Additional manual checks:

-

## Evidence

Add logs, metrics, screenshots, sample output, or benchmark files when relevant.

## Risk and fallback

- Risk level: Low / Medium / High
- Known limitations:
- Fallback behavior:

## Checklist

- [ ] Branch is rebased on the latest `main`.
- [ ] Ruff formatting passes.
- [ ] Ruff linting passes.
- [ ] Relevant pytest tests pass.
- [ ] No secrets, model files, raw licensed data, generated indexes, or large artifacts are committed.
- [ ] Public interfaces, schemas, configs, and documentation are updated when changed.
- [ ] New deterministic logic has tests or a documented reason why a test is not yet possible.
- [ ] Jira acceptance criteria and Definition of Done are satisfied.
- [ ] Reviewer instructions are clear.
