# ADR 0001: Jira for Planning and GitHub for Code

- Status: Accepted
- Date: 2026-07-12

## Context

The team needs professional sprint planning and professional code review without duplicating work tracking.

## Decision

Use Jira Scrum for epics, tasks, bugs, sprints, owners, estimates, and deadlines. Use GitHub for branches, commits, PRs, reviews, tags, and CI. Do not use GitHub Projects or GitHub Issues for duplicate planning.

## Consequences

- Branches and PRs must contain Jira keys.
- Team members learn two tools, but each has one clear responsibility.
- Jira configuration remains lean to avoid process overhead.
