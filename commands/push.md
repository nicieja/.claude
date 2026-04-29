---
allowed-tools: Bash(git status:*), Bash(git push:*), Bash(git branch:*), Bash(gh pr create:*), Bash(git log:*), Bash(git diff:*), Bash(git remote:*)
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
