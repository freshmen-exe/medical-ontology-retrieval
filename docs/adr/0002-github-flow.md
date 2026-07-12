# ADR 0002: GitHub Flow with Protected Main

- Status: Accepted
- Date: 2026-07-12

## Decision

Use one long-lived branch, `main`. All work occurs on short-lived Jira-linked branches and merges through pull requests. Use squash merge and automatically delete merged branches.

## Rationale

Full GitFlow adds `develop`, release, and hotfix branches that are unnecessary for a short research project. GitHub Flow gives review and CI discipline with lower overhead.
