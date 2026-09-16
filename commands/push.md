---
allowed-tools: Bash(git status:*), Bash(git push:*), Bash(git branch:*), Bash(gh pr create:*), Bash(git log:*), Bash(git diff:*), Bash(git remote:*), Bash(vale:*)
description: Create a pull request
---

## Context

- Current branch: !`git branch --show-current`
- Base branch: !`git remote show origin | sed -n 's/.*HEAD branch: //p'`
- Git status: !`git status`
- Commits on this branch: !`git log $(git remote show origin | sed -n 's/.*HEAD branch: //p')..HEAD --oneline`
- Full diff from base: !`git diff $(git remote show origin | sed -n 's/.*HEAD branch: //p')...HEAD`

## Your task

Based on the above changes, create a pull request against the base branch. If the branch hasn't been pushed yet, push it first with -u flag.

If the repo has its own PR workflow (a pr skill, stacked-PR tooling, conventions doc), surface it per the deference protocol in ~/.claude/CLAUDE.md before creating the PR. Remembered resolutions in context/<project>/resolutions.md apply.

Before creating the PR, lint the drafted title and body and fix every error-level alert:

```
vale --ext=.md --path=COMMIT_EDITMSG --no-exit --output=line <<'EOF'
<title>

<body>
EOF
```
