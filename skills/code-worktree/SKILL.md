---
name: code-worktree
version: 1.1.0
description: |
  Give a task that writes code its own git checkout, and keep it until the task
  is done. Start records a completion condition that can pass or fail, creates
  a worktree on a new branch from the freshly fetched default branch, or on an
  existing branch such as an open PR's head, and locks
  it with the task and the condition as the reason. `done` releases the
  checkout only when the condition is met or the user ends the work. It tears
  down the task's runtime and removes the checkout when it is clean and merged,
  keeping the branch. `list` audits every worktree without changing any.
allowed-tools:
  - Read
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Worktree per task

Tasks that share one checkout get in each other's way. One switches the branch while the other is editing, and a teardown in one stops the services the other's tests use. This skill gives each task that writes code its own worktree, and locks it with a reason that states the task and the condition that ends it.

The lock is the record of whose checkout it is. `git worktree remove` and `git worktree prune` refuse a locked worktree, and anyone can read the reason with `git worktree list --porcelain`. The checkout is released when the task is done by the definition recorded at the start. An idle agent or a merged PR doesn't end the task by itself.

## Arguments

- `/code-worktree <task>`: start the task in its own checkout, or resume it when a worktree locked for this task exists.
- `/code-worktree done`: release the task's checkout. It acts on the worktree the session is in, or on the one given as `/code-worktree done <path | branch>`.
- `/code-worktree list`: a read-only audit of every worktree.

## Cases for another skill

- A throwaway prototype → `/idea-prototype`, which uses a separate scratch directory.
- Handing the task to another executor → `/work-delegate`.
- Publishing the branch as a PR → `/pr-open`. Driving that PR to ready-to-merge → `/pr-babysit`.

## Instructions

Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm"). Creating, locking, unlocking, and removing a worktree are local, and one command undoes each, so the skill does them and reports them. Removal keeps the branch, which is what makes it undoable.

Start runs Steps 0 to 4 and 8. `done` runs Steps 0, 5, 6, and 8. `list` runs Steps 0, 7, and 8.

### Step 0: Find the project and its worktree facts

1. The primary checkout is `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`, which gives the same answer from any linked worktree. `<project>` and `<repo>` are its directory name.
2. The default branch is `git symbolic-ref --short refs/remotes/origin/HEAD`, minus the `origin/` prefix. Run `git remote set-head origin --auto` once when the ref is missing.
3. `<name>` is `git config --global user.name | awk '{print tolower($1)}'`.
4. Read three lines from `~/.claude/context/<project>/stack.md`:
   - **Worktrees** gives the path and branch naming, the command that creates a checkout when the task needs services, the teardown, and the checkouts a desktop app manages. The defaults are the path `<primary>/../<repo>.<slug>` and the branch `<name>/<slug>`. Plain `git worktree add` serves every task, the teardown is the runtime's down command, and the app manages no checkouts.
   - **Local runtime** gives the up, down, restart, status, and logs commands for one checkout. Without it, the skill starts and stops no services, and a task that needs them waits for the user to say how.
   - **Test commands** gives how the task runs its tests.

   When a line is missing, use its default and offer once to add it, from the template in `~/.claude/context.example/stack.md`.

### Step 1: Record the task

Read-only work, such as answering a question about the code, uses the current checkout and doesn't need a worktree. Say so and stop.

For work that writes code, record these before creating anything:

- **The task**, in one line.
- **The completion condition**, concrete enough to pass or fail, such as "the PR merged and the deploy verified". When the user gave none, propose one, state it, and let the user correct it. Don't add follow-up nobody asked for. A request to fix a bug doesn't become "fix the bug and clean up the module".
- **The slug**, a few lowercase words from the task joined by hyphens, such as `refund-rounding`.
- **The branch and the path**, from the naming in Step 0. A task on an open PR's head, or on any branch that already exists, keeps that branch. Its slug comes from the branch name.

### Step 2: Check the worktrees that exist

Run `git worktree list --porcelain`. Each entry has a `worktree <path>` line and a `branch refs/heads/<branch>` line, plus a `locked <reason>` line when it's locked.

- **Locked with this task's reason.** The reason equals `<task>: <condition>` exactly. Resume in that worktree and go to Step 4. When the session can't rebuild the reason exactly, such as a resume in a new session with the task worded differently, show the user the lock and ask.
- **Locked for another task.** Leave it alone. Don't unlock it, lock it again, or work in it. A worktree has one lock, and this task gets a separate checkout.
- **Unlocked.** It isn't provably this task's, even on the path this task would use. Leave it.

When the path or the branch is already taken, pick another slug.

### Step 3: Create and lock the checkout

1. `git fetch origin <default>`, or `git fetch origin <branch>` for a branch that already exists.
2. For source-only work, run `git worktree add --no-track -b <branch> <path> origin/<default>`. `--no-track` leaves the new branch without an upstream until `/pr-open` pushes it with `-u`. For a branch that already exists, run `git worktree add <path> <branch>`, which creates the local branch from `origin/<branch>` when there's none. For work that needs services, run the project's command from the Worktrees line, which may create the checkout itself.
3. Lock it right away with `git worktree lock --reason "<task>: <condition>" <path>`.
4. Confirm that `git worktree list --porcelain` shows `locked <task>: <condition>` under the path.

### Step 4: Work in the checkout

- Run every command for the task from the worktree path.
- Start services only when the task needs them, with the Local runtime up command, run from the checkout.
- Run tests with the project's test command. Never run a direct command against a shared database, such as a reset or a migration by hand.
- Never stop the primary checkout or a shared service, such as a database other checkouts use.
- On every resume, read the lock again before the first write. A changed or missing lock stops the work, and the user hears about it.

### Step 5: Check the completion condition (`done`)

1. Find the task's worktree, the one the session is in or the one named. Read its lock. A lock that isn't this task's stops the run.
2. Report four states separately, each marked measured, inferred, or unknown:
   - **Published**: the branch is on the remote and a PR is open, per `gh pr view <branch> --json state,url,isDraft`.
   - **Merged**: the PR's state is `MERGED`.
   - **Deployed**: the change runs where the condition says, per the project's deploy status or the user's word.
   - **Verified**: the check the condition names ran against the deployed change and passed.
3. Release only when the condition is met or the user ends the work. Treat an idle agent, an archived chat, or a merged PR without the rest of the condition as work still in progress. When the condition isn't met, keep the lock, report the missing part, and stop.

### Step 6: Tear down and remove (`done`)

1. Tear down the task's runtime, with the Local runtime down command and the Worktrees teardown, run from the checkout. Leave anything shared, or of unclear ownership, running, and list it.
2. Check that the checkout can be removed. Run `git fetch origin <default>` first.
   - **Clean**: the output of `git -C <path> status --porcelain` is empty. Untracked files make it dirty, and ignored files don't.
   - **Merged**: `git -C <path> merge-base --is-ancestor HEAD origin/<default>` exits 0, or `gh pr view <branch> --json state --jq .state` prints `MERGED`. The PR state counts too, because a squash merge leaves HEAD off the default branch.

   When either check fails, keep the lock and report the dirty files or the unmerged commits. Never reset, clean, stash, or force-remove a checkout to make it removable. The user decides what happens to it.
3. Unlock only this task's lock, with `git worktree unlock <path>`.
4. When the Worktrees line says a desktop app manages the checkout, leave it in place for the app to remove, and go to Step 8.
5. Run `cd <primary>` first, because the shell's working directory is deleted along with the checkout, and later commands fail there. Then remove it with `git worktree remove <path>`, without `--force`. Removal keeps the branch.
6. Confirm with `git worktree list` that the path is gone. When removal fails, lock it again with the recorded reason, `git worktree lock --reason "<task>: <condition>" <path>`, and report the error.

### Step 7: List the worktrees (`list`)

This mode doesn't change any checkout. Run `git fetch origin <default>`, which updates only the remote-tracking ref. Then give one row per entry in `git worktree list --porcelain`:

- the path and the branch
- the lock reason, or "unlocked"
- dirty, as the line count of `git -C <path> status --porcelain`
- merged, when `git -C <path> merge-base --is-ancestor HEAD origin/<default>` exits 0
- the PR, from `gh pr view <branch> --json state,url`, or none when `gh` finds none
- `prunable`, when git marks the entry so

Flag the rows that need a decision. These are a lock whose PR merged (check the rest of its condition), an unlocked checkout with changes in it, and a prunable entry. Don't change any of them.

### Step 8: Report

- **Started**: the path and the branch, with the base SHA. Add the lock reason and any services started.
- **Released**: the four states from Step 5, each with how you know. Then what was torn down, what was left running, and whether the checkout was removed or kept, with the reason.
- **Listed**: the table and the flagged rows. `list` doesn't change anything, and its report skips Check and Undo.
- **Check**: a completion condition you proposed in place of the user's, and every state marked inferred. List anything shared or of unclear ownership you left running.
- **Undo**: after a start, `git worktree unlock <path>`, then `git worktree remove <path>`, then `git branch -D <branch>` while the branch has no commits of its own. After a release, `git worktree add <path> <branch>`, then `git worktree lock --reason "<task>: <condition>" <path>` with the recorded reason.

## Key Rules

1. **A task that writes code gets its own checkout.** Read-only work uses the current one.
2. **One lock per worktree.** Another task's lock is never unlocked, replaced, or worked under. This task gets a separate checkout.
3. **Release only on the recorded condition**, or when the user ends the work. An idle agent or a merged PR alone isn't enough.
4. **Never reset, clean, stash, or force-remove** a checkout to make it removable.
5. **Removal needs a clean checkout that merged**, by ancestry or by PR state, and it keeps the branch.
6. **Never stop the primary checkout or a shared service.** Tests go through the project's test command.
