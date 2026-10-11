---
name: code-uncomment
version: 1.0.0
description: |
  Delete the comments and lint suppressions that code doesn't need, and flag the
  code they were covering for. Takes the current diff by default, or files or a
  checked-out PR. The comment-editor agent deletes in its own context, under the
  rules in comment-guide.md. The skill audits that diff, reverts anything that
  isn't a comment, fixes the trivial flags, and encodes a constraint comment as
  a test or a check where it can. It reports what to check and how to undo it.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Agent
  - Bash
---

# Uncomment

Delete the comments that code doesn't need. A comment that explains a surprise
in our own code is a sign the code should change, and agents copy comments they
see nearby. So the default is deletion. A comment is kept only when it's on the keep list in
`comment-guide.md`, and the code a comment was covering for gets a `MUST KILL`
flag. The `comment-editor` agent does the deleting in its own context, and this
skill checks its work.

## Arguments

- `/code-uncomment` (bare): the current branch, from its merge base with the default branch to the working tree. Uncommitted and untracked files count.
- `/code-uncomment <paths>`: those files, every comment in them.
- `/code-uncomment <PR number | url>`: that PR's diff, when its branch is checked out at its head. Otherwise report only, and say what to check out.
- Steers in plain words. `report` or "just tell me" edits nothing and reports the deletions it would make. `--review` or "ask first" reports, then waits for the go-ahead before deleting.

## Cases for another skill

- Prose that reads AI-generated → `/code-deslop`.
- Guards for states no caller can produce → `/code-simplify`.
- Code that needs restructuring beyond a flagged symbol → `/simplify`, or `/code-refactor` across many files.
- Tests a slice added past what its behavior needs → `/test-prune`.

## Instructions

Follow these steps in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm").

### Step 0: Resolve the scope

Turn the arguments into a file list and, for a diff, the base commit. For the bare form, the base is `git merge-base origin/<default> HEAD`, where `git symbolic-ref --short refs/remotes/origin/HEAD` gives the default branch. In a diff scope, only comments on lines the diff adds are in scope. Open with one line that gives the scope and the number of files.

### Step 1: Back up the scope

Skip this step in report mode. Copy every file in scope to the backup path in `~/.claude/AGENTS.md`. The copies are the Undo, and Step 3 compares against them.

### Step 2: Dispatch the comment editor

Dispatch the `comment-editor` agent (`subagent_type: "comment-editor"`). The rules are in `comment-guide.md`, which the agent loads, so don't restate them. The brief contains:

- the scope, as the file list, plus the base commit for a diff scope;
- the mode, edit or report;
- the armor rule, in these words or close to them. *Write the code the task needs, and no armor around it. Prefer a loud failure to a catch-and-default.*

In a tool without subagents, load `comment-guide.md` yourself and apply it inline. Step 3 then audits your own diff the same way.

### Step 3: Audit the edit

Compare each file in scope with its backup (`diff -u <backup> <file>`), and read the agent's report against it:

- **Every removed line is a comment or a suppression.** Revert any other change, such as an edited line of code or a reworded comment.
- **Every change is inside the scope.** In a diff scope, a comment a teammate wrote before the diff is out of scope.
- **Each Kept line cites a keep-list case that holds.** For a comment that only sounds weighty ("do not remove", "IMPORTANT"), check its claim yourself with `git log -S` and the call sites. A keep that fails the check gets deleted.
- **Each flag points to a real symbol in scope**, with a reason that matches the code.

When a check fails, restore the files from their backups and dispatch the agent once more, naming the failure in the brief. When the second run fails too, restore again and report the run as open.

### Step 4: Fix the flagged code

Skip this step in report mode. A flag is trivial when the fix keeps behavior the same. Deleting a dead path or an unused parameter qualifies, and so do calling the real API and renaming a symbol so it explains itself. Apply those. A fix that would change behavior is a decision that is mine, so it waits for the questions at the end.

A deleted suppression of a correctness or safety rule makes the linter fail until its flag is fixed. When the fix is trivial, apply it. Otherwise restore that suppression and report its flag as open.

### Step 5: Encode the constraint comments

For each comment under Constraints, pick the cheapest encoding in scope. A test that pins the behavior is applied directly. A rule that a lint check could enforce gets a private check in `context/<project>/checks/`. `~/.claude/AGENTS.md` explains why, under "Fix the class, not only the instance". When neither fits, the comment remains deleted, and the constraint goes in the report as open.

### Step 6: Verify

Skip this step in report mode. Run the touched files' tests and linters with the project's own runner. Find them in the repo's CLAUDE.md or AGENTS.md, `package.json`, `Gemfile`, or `Makefile`. When a failure comes from a fix in Step 4, revert that fix and report its flag as open.

### Step 7: Report

- **Deleted**: the count per file, and the lines a reader should look at.
- **Fixed**: the flags fixed in Step 4.
- **Open flags**: the `MUST KILL` lines left for later.
- **Encoded**: each constraint and its test or check, or "open".
- **Verification**: what ran, and the result.
- **Check**: the deleted comments that sounded weighty and the open flags. Also list each constraint deleted without an encoding.
- **Undo**: `cp <backup> <file>` for each file, from the Step 1 backup.

Then ask the questions that are mine, all together: each fix that would change behavior, with the options.

In report mode, list the deletions and flags the agent proposed, and leave out Verification, Check, and Undo.

## Key Rules

1. **Deletion is the default.** Keep a comment only when it's on the keep list, and keep it verbatim.
2. **The agent deletes and the skill audits.** Anything in the agent's diff that isn't a deleted comment or suppression gets reverted.
3. **Never touch a comment outside the scope.** In a diff scope, a teammate's earlier comment stays.
4. **Fix only what keeps behavior the same.** A behavior change is a question for the end.
5. **A constraint is encoded or reported open.** It never comes back as a comment.
6. **The rules live in `comment-guide.md`.** Don't restate them in the brief.
