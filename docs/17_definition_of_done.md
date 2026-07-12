# Definition of Ready and Definition of Done

## 1. Definition of Ready

A Jira Task may move to Ready only when:

- goal and reason are clear;
- expected output and exact path are named;
- acceptance criteria are testable;
- owner and reviewer are assigned;
- estimate and deadline exist;
- dependencies are available or explicitly scheduled;
- relevant schema/interface/source is linked;
- out-of-scope behavior is stated for risky tasks.

If implementation begins while basic questions remain unanswered, the item was not Ready.

## 2. Global Definition of Done

A Task is Done only when:

- acceptance criteria pass;
- output exists at the documented path;
- branch is merged through an approved PR;
- CI passes;
- relevant deterministic tests pass;
- manual/metric evidence is attached when required;
- no secrets, personal paths, raw restricted data, or generated large artifacts are committed;
- interface/schema/config/docs are updated in the same PR;
- QA verifies user-visible or scoring-relevant behavior;
- Jira contains the PR/result link and remaining limitations;
- the item has no unresolved sub-task or blocker.

## 3. Data task DoD

- Authoritative source and access conditions recorded.
- Raw file checksum recorded when downloaded.
- Parser is reproducible and does not rely on silent manual edits.
- JSONL/schema validation passes.
- Record counts and rejected-row counts are reported.
- Samples are cross-checked.
- Alias collisions and weak aliases are handled explicitly.
- Data manifest/version is updated.
- Data QA approves.

## 4. Model task DoD

- Public interface follows API spec or approved change.
- Algorithm and assumptions are documented.
- Deterministic parts have focused tests.
- Parameters are configurable.
- Empty/invalid inputs are handled.
- Baseline and metric evidence exist for ranking/index experiments.
- HNSW compares with exact search.
- Fallback behavior is implemented when the feature is optional.
- Model owner and reviewer approve.

## 5. Pipeline task DoD

- Component is integrated through the shared interface.
- CLI/app path works from repository root.
- No duplicate business logic exists in `app.py` or scripts.
- Raw span preservation is verified.
- Validators run before final output.
- Errors are actionable and logged.
- Batch behavior is deterministic when relevant.
- Integration tests pass.

## 6. QA task DoD

- Test objective and expected behavior are documented.
- Fixture/ground truth is committed where permitted.
- Test command is reproducible.
- Failed cases are classified and linked to Bugs.
- Fixed deterministic defects have regression tests.
- Results are reviewed for data/annotation mistakes.
- Release checklist is updated when relevant.

## 7. Documentation/report task DoD

- Content is technically reviewed.
- Sources are registered and cited.
- Links and paths work.
- Figures/tables have generation source or notes.
- Claims match actual implementation/results.
- No placeholder text remains.
- Exported file opens on another machine.

## 8. Infrastructure task DoD

- Clean clone/container setup is tested.
- Commands are documented.
- CI/pre-commit behavior matches local behavior.
- No unnecessary service/tool was added.
- Fallback exists for platform-specific behavior.

## 9. Bug Done rule

A Bug is Done only when QA reproduces the original failure, verifies the fix on the same case, and checks relevant regression behavior. “Cannot reproduce anymore” without environment/input evidence is insufficient.
