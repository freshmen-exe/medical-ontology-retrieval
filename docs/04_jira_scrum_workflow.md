# Jira Scrum Workflow

## 1. Decision

Jira is the single source of truth for work planning. GitHub is the single source of truth for code and reviews. Do not duplicate tasks in GitHub Projects or GitHub Issues.

Recommended Jira configuration:

```text
Project type: Team-managed software project
Template: Scrum
Project name: Medical Ontology Retrieval
Project key: MOR
Sprint length: 3 days
Estimation: hours
```

A team-managed project is sufficient for a five-person research team and avoids unnecessary administrator configuration.

## 2. Work item types

Use only:

- **Epic**: a large project capability spanning multiple tasks.
- **Task**: an implementable unit of work with a concrete output.
- **Bug**: behavior that contradicts an agreed expectation or previously working result.
- **Sub-task**: a smaller assigned part of a Task or Bug.

Do not add Story, Request, Improvement, Spike, or custom types unless the Tech Lead records a real need. Experiments, documentation, and tests are Tasks with labels/components.

## 3. Epics

Create these epics:

1. Data and Ontology Knowledge Base
2. Entity and Assertion Extraction
3. Hybrid Retrieval and Candidate Mapping
4. Self-Implemented HNSW
5. End-to-End Inference Pipeline
6. QA, Evaluation, and Error Analysis
7. Infrastructure and Team Workflow
8. Report, Slides, Demo, and Submission

## 4. Workflow statuses

```text
Backlog → Ready → In Progress → In Review → QA → Done
```

| Status | Entry rule | Exit rule |
|---|---|---|
| Backlog | Work is known but not ready or not selected | Definition of Ready is satisfied and sprint capacity exists |
| Ready | Owner, output, acceptance criteria, estimate, and deadline exist | Owner starts active work |
| In Progress | Work is actively being done | PR/artifact is ready for review |
| In Review | Reviewer has a complete PR or artifact | Review is approved and QA can verify |
| QA | QA is testing acceptance criteria and regression behavior | Definition of Done is satisfied |
| Done | All acceptance criteria and DoD pass | Reopen only through a linked Bug |

### Blocked work

Blocked is a flag, not a workflow status. A task can be blocked while In Progress, In Review, or QA.

When blocked:

1. Flag the item in Jira.
2. Add label `blocked`.
3. Comment with the exact blocker, required owner, and next check time.
4. Mention the person who can unblock it.
5. Notify the Tech Lead if blocked for more than two working hours.
6. Split, reassign, reduce scope, or use a documented fallback if blocked for six working hours.

## 5. Components

Use Jira Components instead of duplicating component labels:

- Data
- Extraction
- Retrieval
- Pipeline
- QA
- Infrastructure
- Documentation-Demo

A task may have more than one component only when the work genuinely crosses boundaries.

## 6. Labels

Use labels only for cross-cutting classification:

```text
experiment
research
test
documentation
blocked
needs-data
needs-model
needs-pipeline
needs-review
regression
submission-critical
```

Do not create priority labels. Use Jira's native Priority field.

## 7. Priority

- **Highest / P0**: blocks the final pipeline, submission, or multiple people.
- **High / P1**: required for the current milestone.
- **Medium / P2**: valuable but has a fallback.
- **Low / P3**: optional improvement or future work.

Priority is not severity. A rare severe bug may be P1; a simple build break may be P0 because it blocks everyone.

## 8. Required fields for a Task

Every Task must contain:

```text
Goal
Why it matters
Inputs
Expected outputs and exact file paths
Acceptance criteria
Out of scope
Owner
Reviewer
Original estimate
Deadline
Dependencies
Relevant docs and source links
```

A Task longer than one working day should usually be split. A task shorter than 30 minutes may be a checklist item under a parent Task.

## 9. Required fields for a Bug

```text
Observed behavior
Expected behavior
Environment/configuration
Minimal reproduction steps
Input or fixture
Actual output/log
Expected output
Affected commit or PR if known
Priority
Regression: yes/no
Temporary workaround
Owner and verifier
```

QA closes a Bug only after reproducing the fix and checking relevant regression tests.

## 10. Required fields for an Experiment Task

```text
Hypothesis
Baseline
Method
Timebox
Metrics
Success threshold
Failure/fallback decision
Output path for results
```

An experiment does not become production code merely because it runs. It merges only if metrics and stability justify it.

## 11. Sprints and milestones

Recommended plan:

| Sprint | Dates | Goal |
|---|---|---|
| Sprint 0 | 12–14 Jul | Kickoff, environment, source acquisition, and architecture contracts |
| Sprint 1 | 15–17 Jul | Data and extraction MVP |
| Sprint 2 | 18–20 Jul | Retrieval baselines and alias/data validation |
| Sprint 3 | 21–23 Jul | Core integration, RRF, and HNSW implementation |
| Sprint 4 | 24–26 Jul | Hardening, benchmarks, QA expansion, and demo |
| Sprint 5 | 27–28 Jul | Release candidate, final QA, and code freeze |
| Sprint 6 | 29 Jul–2 Aug | Report, slides, video, and submission package |

Use Jira Versions/Releases:

```text
v0.1-mvp
v0.2-core
v0.3-rc
v1.0-submission
```

## 12. Meetings

- Daily planning: 10–15 minutes.
- Async status update: by 16:00 ICT.
- Nightly integration check: 15–25 minutes.
- Sprint review and short retrospective: 30–45 minutes at sprint end.

Daily update:

```text
Done:
Evidence/PR/file:
In progress:
Blocker:
Next task:
Review needed from:
```

Do not debug deeply during the daily meeting. Create a separate technical session with only the needed people.

## 13. Jira–GitHub traceability

Branch:

```text
feature/MOR-34-code-level-rrf
```

PR title:

```text
[MOR-34] Implement code-level RRF fusion
```

PR body includes the Jira URL. If Jira's GitHub integration is available, connect it so commits, branches, and PRs appear in the Jira Development panel. The naming convention remains mandatory even without the integration.

## 14. Definition of Ready and Done

Use [`17_definition_of_done.md`](17_definition_of_done.md). A task cannot move to Ready without a usable output path and acceptance criteria. It cannot move to Done based only on a verbal claim.

## Import-ready backlog

Use [`../planning/jira/README.md`](../planning/jira/README.md) and [`../planning/jira/jira_import_tasks.csv`](../planning/jira/jira_import_tasks.csv). The CSV includes the 12 July 2026 09:00 kickoff meeting, hierarchy, owners, estimates, exact deadlines, sprints, versions, labels, acceptance criteria, evidence paths, and dependencies.
