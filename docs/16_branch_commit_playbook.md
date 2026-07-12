# Git Command and Recovery Playbook

Use this document before running destructive Git commands. Always inspect `git status`, `git diff`, and the current branch first.

## 1. Daily start

```bash
git switch main
git fetch origin
git pull --rebase origin main
git switch -c feature/MOR-123-short-description
```

Resume an existing branch:

```bash
git switch feature/MOR-123-short-description
git fetch origin
git rebase origin/main
```

## 2. Inspect changes

```bash
git status
git diff
git diff --staged
git log --oneline --decorate -10
```

## 3. Stage

Specific files:

```bash
git add path/to/file.py tests/unit/test_file.py
```

Interactive staging:

```bash
git add -p
```

All changes only after inspection:

```bash
git add -A
```

Unstage while keeping edits:

```bash
git restore --staged path/to/file.py
```

## 4. Commit

```bash
git commit -m "feat(retrieval): implement exact cosine search"
```

Multi-line message:

```bash
git commit
```

A good commit is coherent and importable. Committing after every useful function is acceptable when each commit leaves the branch in a reasonable state. Do not commit syntax errors merely to create more commits.

## 5. Amend the last local commit

Add forgotten changes:

```bash
git add path/to/file.py
git commit --amend --no-edit
```

Edit message:

```bash
git commit --amend
```

If the branch was already pushed:

```bash
git push --force-with-lease
```

Only rewrite your own unmerged branch.

## 6. Stash

Tracked changes:

```bash
git stash push -m "wip MOR-123"
```

Include untracked files:

```bash
git stash push -u -m "wip MOR-123"
```

List/show:

```bash
git stash list
git stash show -p stash@{0}
```

Apply and keep stash:

```bash
git stash apply stash@{0}
```

Apply and remove stash:

```bash
git stash pop
```

Delete a stash only after verifying it is no longer needed:

```bash
git stash drop stash@{0}
```

## 7. Restore uncommitted work

Discard one file's unstaged changes:

```bash
git restore path/to/file.py
```

Restore a file from `main`:

```bash
git restore --source=origin/main -- path/to/file.py
```

Discard all uncommitted tracked edits:

```bash
git restore .
```

This is destructive. Copy or stash valuable work first.

## 8. Rebase

```bash
git fetch origin
git rebase origin/main
```

Resolve conflict:

1. Open files containing conflict markers.
2. Select the intended final content.
3. Run tests for affected code.
4. Stage resolved files.
5. Continue.

```bash
git add <resolved-files>
git rebase --continue
```

Skip the current commit only when you understand why it is redundant:

```bash
git rebase --skip
```

Abort safely:

```bash
git rebase --abort
```

## 9. Interactive squash/reword

```bash
git fetch origin
git rebase -i origin/main
```

Actions:

```text
pick    keep commit
reword  keep but edit message
squash  combine and edit combined message
fixup   combine and discard this message
drop    remove commit
```

GitHub Squash and merge is the default and usually removes the need to manually squash every branch.

## 10. Revert a committed change safely

For a shared/merged commit:

```bash
git revert <commit-sha>
```

This creates a new inverse commit and preserves history. Use this for `main`.

Revert a merge commit only with Tech Lead support:

```bash
git revert -m 1 <merge-commit-sha>
```

## 11. Reset local commits

Keep changes staged:

```bash
git reset --soft HEAD~1
```

Keep changes unstaged:

```bash
git reset HEAD~1
```

Destroy commit and changes:

```bash
git reset --hard HEAD~1
```

`--hard` is destructive. Never use it on shared history unless instructed by the Tech Lead.

## 12. Recover a lost commit

```bash
git reflog
```

Create a rescue branch:

```bash
git switch -c rescue/lost-work <reflog-sha>
```

Do not panic and run multiple resets before checking reflog.

## 13. Cherry-pick

Apply one commit from another branch:

```bash
git cherry-pick <commit-sha>
```

Use only when moving a clearly isolated commit. Prefer normal PR integration for broader work.

## 14. Delete branches

After merge:

```bash
git switch main
git pull --rebase origin main
git branch -d feature/MOR-123-short-description
git fetch --prune
```

Force-delete an unmerged local branch only after verifying work is no longer needed:

```bash
git branch -D branch-name
```

Delete remote:

```bash
git push origin --delete branch-name
```

## 15. Clean untracked files

Preview first:

```bash
git clean -nd
```

Delete previewed untracked files:

```bash
git clean -fd
```

This is destructive and can remove untracked datasets or work. Prefer manual deletion or stash with `-u`.

## 16. Wrong-branch recovery

Uncommitted work:

```bash
git stash push -u -m "move to correct branch"
git switch correct-branch
git stash pop
```

Committed work:

```bash
git branch correct-branch
git switch original-branch
```

Then reset/revert the original branch only after confirming `correct-branch` contains the commit.

## 17. Pull policy

Use:

```bash
git pull --rebase
```

Recommended global configuration:

```bash
git config --global pull.rebase true
git config --global fetch.prune true
git config --global rebase.autoStash true
```

Do not enable global auto-stash if you do not understand its effect; repository documentation still expects clean/stashed work before rebasing.
