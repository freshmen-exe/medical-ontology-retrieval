# New-Member Onboarding Checklist

A member is ready to take a Jira task only after completing this checklist.

## Accounts and access

- [ ] Joined the GitHub organization/repository.
- [ ] Joined the Jira project.
- [ ] Can read the shared artifact storage.
- [ ] Git name and email are configured.

```bash
git config --global user.name "Full Name"
git config --global user.email "email@example.com"
```

## Workstation

- [ ] Installed Git.
- [ ] Installed VS Code.
- [ ] Installed Docker Desktop.
- [ ] Installed recommended VS Code extensions.
- [ ] Opened the repository in the Dev Container.
- [ ] Ran `make check-env`.

## Repository understanding

- [ ] Read README.
- [ ] Read project workflow.
- [ ] Read role/task/deadline document.
- [ ] Read Git/GitHub workflow.
- [ ] Read Jira workflow.
- [ ] Read coding standards and DoD.

## Practical exercise

1. Create a small Jira Task assigned by the Tech Lead.
2. Create a correctly named branch.
3. Make a documentation-only change.
4. Commit with a Conventional Commit message.
5. Rebase on `origin/main`.
6. Push and open a PR.
7. Pass CI and address one review comment.
8. Squash-merge and delete the branch.

## Model/data access

- [ ] Can reach Ollama locally or knows the Colab path.
- [ ] Understands that raw licensed data and model weights are not committed.
- [ ] Knows where source manifests and checksums are stored.

## Completion

The Tech Lead or designated reviewer confirms onboarding in Jira. No one learns the workflow for the first time on a submission-critical task.
