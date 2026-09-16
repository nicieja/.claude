---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(vale:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Based on the above changes, create one git commit.

If the repo defines commit conventions (a .gitmessage template, a commit doc or skill), follow them and say which you followed.

Before committing, lint the drafted message and fix every error-level alert:

```
vale --ext=.md --path=COMMIT_EDITMSG --no-exit --output=line <<'EOF'
<the message>
EOF
```
