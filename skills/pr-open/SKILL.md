---
name: pr-open
version: 1.0.0
description: |
  Publish the current branch as a pull request. Before anything leaves the
  machine, it proves the diff and sets aside changes unrelated to the task.
  New commits are small and ordered, under the project's message convention.
  The body runs to about 40 lines, and its Scope section lists what the PR
  leaves out. After asking first, it pushes the branch and opens the PR as a
  draft unless the project opens them ready. Ends with the URL and an offer to
  hand the PR to pr-babysit.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Skill
  - AskUserQuestion
---

# Open a PR

Turn a finished branch into a PR that a reviewer can judge in a few minutes. Each commit makes sense alone, and the body says why the change exists and what it changed. It also states what the PR leaves out on purpose, so the reviewer doesn't go looking for it.

Pushing and opening the PR are outward actions. The skill asks before them unless a steer or the project's escalation file allows them.

## Arguments

- `/pr-open` (bare): the current branch, against the default branch.
- `/pr-open <base>`: against another base, such as the branch below this one in a stack.
- Steers in plain words. `ready` or "not a draft" opens the PR ready for review. `dry run` or `--review` stops after Step 3, with the commits made and the body written, before anything is pushed.

## Cases for another skill

- An open PR to drive to ready-to-merge → `/pr-babysit`.
- A review of the diff before it goes out → `/pr-critique`.
- Proof that the diff works, by running it → `/test-prove`.
- A change that isn't built yet → `/code-build`.
- A separate checkout for the task → `/work-worktree`.

## Instructions

Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm"). Commits are local. The skill makes them and reports them. Pushing the branch and opening the PR are ask-first, unless the stepping-away steer or `~/.claude/context/<project>/escalation.md` widens them. Rewriting commits that already exist waits for the user. Merges and force pushes always wait for the user, and this skill does neither.

### Step 0: Check the tree and prove the diff

1. `<project>` is the directory name of the primary checkout, which gives the same answer inside a linked worktree: `basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"`.
2. Record what the Undo needs:
   - the start SHA, `git rev-parse HEAD`
   - the branch, `git branch --show-current`
   - the default branch, `git symbolic-ref --short refs/remotes/origin/HEAD` (run `git remote set-head origin --auto` once when the ref is missing)
   - whether the branch already has an upstream, `git rev-parse --abbrev-ref @{upstream}`
3. On the default branch, create the task branch first with `git switch -c <name>/<slug>`, where `<name>` is the first word of `git config --global user.name`, lowercased. `<slug>` is a few lowercase words from the task joined by hyphens. The uncommitted changes come along.
4. Run `git status --short` and sort every path into the task's changes and the rest. List the rest for the report, and never stage them. Stage by path, never with `git add -A` or `git add .`.
5. Prove the diff. When `/test-prove` or the project's verify skill (the repo's own, or `~/.claude/context/<project>/verify/SKILL.md`) hasn't run on this diff in the session, run it. When neither fits the change, run at least the linter and the most relevant test, with the test commands from `stack.md`. A failure stops the run. Report it, and push nothing.

### Step 1: Read the project's PR flow

Read two lines from `~/.claude/context/<project>/stack.md`.

- **Code host & PR flow** says whether PRs open as drafts, which base they target, and which stacking tool the project uses. Use a stacking tool only when `stack.md` names it and `<tool> --version` exits 0. Never install one. When the line is missing, the flow is plain git plus `gh`, and PRs open as drafts against the default branch.
- **Commit conventions** points to a `.gitmessage` or a doc. Read it. When the line is missing, `git config commit.template` and the last 20 subjects in `git log --oneline` show the convention. When they show none, use `type(scope): subject`.

When a line is missing, use the default and offer once to add it to `stack.md`, from the template in `~/.claude/context.example/stack.md`.

### Step 2: Commit

Commit the task's staged changes as new commits.

- **Small and ordered.** Each commit is one step a reviewer can read alone. They go in the order the change was built, such as the migration before the code that reads the new column.
- **Each one landable.** The build and the tests pass at every commit, so a bisect or a revert can stop on any of them.
- **The first has the full summary.** Its message body explains the whole change. Later commits describe their own step.
- **The project's convention**, from Step 1.

Leave the commits that were on the branch before the run as they are. Squashing, reordering, or rewording them rewrites history, so propose the new commit list and wait for the user.

### Step 3: Write the body

The title follows the convention, in about 70 characters. The body is about 40 lines at most, with no SHAs, and it ends with the session's PR attribution line. Use these sections in this order, and drop any that would be empty, except Scope:

- **Why**: the problem or the request in two sentences or fewer. Link the issue when there is one.
- **What changed**: the behavior first, then the code behind it. A rename shows both sides, as in `cancel_order → order.cancel`.
- **Scope**: what this PR leaves out on purpose. This section is always present. When the PR leaves out nothing, say that in one line.
- **Tradeoffs**: real ones only, each with the option not taken.
- **What else this touches**: other readers and writers of what changed, such as a nightly job that reads the column or an integration that receives the payload. When `/test-prove` ran, its Risks and Ruled out sections list them.
- **How to test**: manual steps with a result a person can see. "Cancel an order and the refund appears on the order page" is one. Never commands.
- **Verification**: what ran and what it showed. Checks that are only planned go on their own line, marked as planned.

Write the body to a file in the session's scratchpad or a `mktemp` path. Pass it with `--body-file`.

### Step 4: Push and open

Show the user the title, the base, the commits, and the body file, and ask before pushing, unless the push is allowed (see the top of Instructions). After the yes:

1. `git push -u origin <branch>`. A rejected push means the remote branch moved. Stop and report it, and never force it.
2. `gh pr create --draft --base <base> --title "<title>" --body-file <file>`. Drop `--draft` when `stack.md` says the project opens PRs ready, or the user said `ready`. With a stacking tool, use the submit command that `stack.md` names in place of both steps.
3. Record the URL and the PR number from the output. Offer `/pr-babysit` in one line, to take the PR to ready-to-merge.

### Step 5: Report

- **Opened**: the URL and the base, and whether it's a draft.
- **Commits**: one line each, in order.
- **Left out**: the Scope section, plus the unrelated changes still in the tree, unstaged.
- **Verification**: what ran and what it showed, marked measured. List what didn't run.
- **Check**: anything staged that might not belong, such as a lockfile change or a generated file. Add anything in the body the user should confirm, such as a tradeoff stated on their behalf.
- **Undo**: `gh pr close <n>` and `git push origin --delete <branch>`, then `git reset --soft <start-sha>` on the branch, which puts the new commits' changes back in the index. Don't use `gh pr close --delete-branch` here. It also deletes the local branch and switches to the default branch, so the reset would move the wrong branch. When the branch had an upstream before the run, deleting the remote branch isn't the undo. Putting the remote back is a force push, which waits for the user. When Step 0 created the branch, finish with `git switch <default>` and `git branch -D <branch>`.

## Key Rules

1. **Prove before publishing.** A failing lint or test stops the run before the push.
2. **Stage by path.** Changes unrelated to the task are listed and never staged.
3. **New commits only.** Reshaping the commits that were already there rewrites history and waits for the user.
4. **Scope is always in the body**, even when the PR leaves out nothing.
5. **Ask before the push**, unless a steer or `escalation.md` allows it. Never force push, and never merge.
6. **Never install a stacking tool.** Use one only when `stack.md` names it and `<tool> --version` works.
7. **The body goes in a file**, passed with `--body-file`, and ends with the session's PR attribution line.
