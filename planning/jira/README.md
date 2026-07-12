# Jira Scrum Setup and CSV Import

Jira is the single source of truth for tasks, bugs, blockers, owners, estimates, deadlines, and sprint status. GitHub is used for code, branches, commits, pull requests, review, and CI. Do not duplicate the backlog in GitHub Projects.

## Included files

- `jira_import_tasks.csv`: import-ready hierarchy with 98 work items.
- `jira_task_catalog.csv`: human-readable catalog with owners, estimates, dependencies, and evidence paths.
- `sprint_calendar.csv`: sprint names, dates, goals, and planned capacity.

The kickoff meeting at **09:00 ICT on 12 July 2026** is included as work item ID `1001` and is marked `Done`. Change the status before import if it was postponed.

## Required Jira project

Create a Jira Software Scrum project/space with:

- Name: `Medical Ontology Retrieval`
- Key: `MOR`
- Template: Scrum
- Time zone: Asia/Ho_Chi_Minh

Use only these work types:

- Epic
- Task
- Bug
- Sub-task

A Story is not required because most work is technical and deliverable-oriented. Create a Story only when the team later identifies a genuine user-facing capability that benefits from story semantics.

## Workflow statuses

Create or map these statuses:

1. Backlog
2. Selected for Development
3. In Progress
4. Blocked
5. In Review
6. QA / Testing
7. Done

Suggested board mapping:

| Board column | Jira status |
|---|---|
| Backlog | Backlog |
| Ready | Selected for Development |
| In Progress | In Progress |
| Blocked | Blocked |
| Review | In Review |
| QA | QA / Testing |
| Done | Done |

## Components

Create these components before import:

- `data`
- `model`
- `pipeline`
- `qa`
- `infra`
- `docs`
- `demo`

## Versions/releases

Create these versions before import:

- `v0.1-mvp`
- `v0.2-core`
- `v0.3-rc`
- `v1.0-submission`

## Sprints

Create the sprints exactly as named in `sprint_calendar.csv`. Exact names matter if the Sprint column is mapped during import.

## Custom fields

Create only the fields that add real value:

| Field | Type | Purpose |
|---|---|---|
| Planned Owner | Short text | Full-name owner before Jira account IDs/emails are available |
| Start Date | Date/time | Planned start in ICT |
| Deadline | Date/time | Exact task deadline in ICT |

The CSV also contains the built-in Due Date and Original Estimate fields. Original Estimate values are expressed in seconds, as required by Jira CSV import.

Do not create extra custom fields for acceptance criteria, dependencies, or evidence. Those are already embedded in each Description to keep the Jira configuration lean.

## Import method

Use the Jira CSV import path that supports parent-child hierarchy. The ordinary bulk work-item CSV importer cannot map a multi-level hierarchy; use the External System Import or the current import experience that maps Work Item ID and Parent.

Official references:

- https://support.atlassian.com/jira-cloud-administration/docs/import-data-from-a-csv-file/
- https://support.atlassian.com/jira-software-cloud/docs/import-data-to-a-software-project-using-a-csv-file/
- https://support.atlassian.com/jira/kb/keep-issue-parent-child-mapping-during-csv-import-to-jira-cloud/
- https://support.atlassian.com/jira-software-cloud/docs/mapping-csv-data-to-jira-fields/

### Recommended import steps

1. Create the Scrum project/space and all statuses, components, versions, sprints, and custom fields listed above.
2. Open Jira settings and choose the CSV external-system/new import workflow.
3. Upload `jira_import_tasks.csv`.
4. Set the CSV encoding to UTF-8 and delimiter to comma.
5. Set the date/time format to `yyyy-MM-dd HH:mm`.
6. Map the columns exactly as shown below.
7. Enable value mapping for Work Type and Status.
8. Validate before importing.
9. Review the import log before accepting the result.
10. Check one epic, one task, and one sub-task from each workstream.

## Column mapping

| CSV column | Jira field |
|---|---|
| Space Name | Space/Project name |
| Space Key | Space/Project key |
| Work Item ID | Work item ID |
| Parent | Parent |
| Work Type | Work type / Issue type |
| Summary | Summary |
| Description | Description |
| Assignee | Assignee; currently blank |
| Planned Owner | Custom field: Planned Owner |
| Priority | Priority |
| Component | Component/s |
| Sprint | Sprint |
| Start Date | Custom field: Start Date |
| Deadline | Custom field: Deadline |
| Due Date | Due date |
| Original Estimate | Original estimate |
| Fix Version | Fix Version/s |
| Status | Status |
| Labels | Labels; map every repeated Labels column |

## Owner assignment after import

Jira Assignee requires an Atlassian account email or account ID. The import intentionally leaves Assignee blank because the teammates' Jira account identifiers are not known. After all members join Jira:

1. Filter by `Planned Owner`.
2. Bulk assign each member's work items to their Jira account.
3. Keep Planned Owner for auditability or remove it after verification.

## Status rules

- Move to `Selected for Development` only when acceptance criteria, owner, estimate, and deadline are usable.
- Move to `In Progress` when active work begins.
- Move to `Blocked` immediately when the owner cannot continue; state the blocker and required help.
- Move to `In Review` only after a pull request or reviewable artifact exists.
- Move to `QA / Testing` after technical review and before acceptance testing.
- Move to `Done` only after the applicable Definition of Done passes and evidence is linked.

## Bug creation rule

Create a Bug when expected behavior is defined and the system or artifact violates it. A Bug must include:

- observed behavior
- expected behavior
- reproduction steps
- input and output evidence
- severity: P0, P1, P2, or P3
- affected component
- owner
- regression-test requirement

Use Task for new implementation and `type-experiment` label for time-boxed research.

## Jira-GitHub traceability

Use the Jira key in every coding branch and pull request:

- Branch: `feature/MOR-34-code-level-rrf`
- Commit body: `Refs MOR-34`
- Pull request title: `[MOR-34] Implement code-level RRF fusion`

Link the PR in Jira before moving the item to In Review.
