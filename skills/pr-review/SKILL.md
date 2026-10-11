---
name: pr-review
version: 1.0.0
description: |
  Review a diff, a branch, or a PR for what compilers and tests miss: a design
  that doesn't belong, subtle correctness bugs, security holes, performance
  traps, and decisions that are expensive to undo. The bar is a codebase
  healthier than before, not perfect code. Findings come with file:line and
  the fix, on one severity scale, and the review ends with a merge
  recommendation. Runs interactively or in report mode from a brief.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Skill
---

# Review

Review code changes, meaning diffs, branches, pull requests, and sometimes whole files when something feels off. Catch the issues that compile-time checks and tests don't, such as security holes, subtle correctness bugs, performance traps, and decisions that will be expensive to undo.

Load `review-guide.md` (next to this file) every run. It is the standard the checks apply. It sets the bar and the order of the checks, and it covers comment tone, pushback, and the emergency test.

## Arguments

- `/pr-review` (bare): the current branch against the default branch, from `git merge-base origin/<default> HEAD` to the working tree. Uncommitted changes count.
- `/pr-review <PR number | url>`: fetch it with `gh pr view` and `gh pr diff`.
- `/pr-review <branch>`: `git fetch origin <branch>`, then the diff against its merge base with the default branch.
- A path after any form limits the review to that path.
- `/pr-review <file path>` with no diff on that file: review the whole file, for when something feels off.
- **Report mode.** When the `reviewer` agent loads this skill from a brief, the brief defines the scope, the context, and the output format, and its format overrides the one in Step 6. Focus lines in the brief, such as extra depth on security or on performance, steer where to go deep, and findings anywhere in the diff remain in scope. A question that would go to the author becomes a listed gap.

## Cases for another skill

- Only the defensive code, or additions with no caller → `/code-simplify`.
- Only comments or lint suppressions → `/code-uncomment`, and prose alone → `/code-deslop`.
- Working code that needs restructuring → `/simplify`, or `/code-refactor` across many files.
- A design that needs grilling before code exists → `/idea-challenge`, or `/idea-primitive` for the concept underneath.
- The tests a change added past what its behavior needs → `/test-prune`.

## Instructions

### Step 0: Resolve the target

Per **Arguments**. Read the PR description or the commit messages, and record the totals (files changed, lines added and removed).

### Step 1: Take a broad view first

Read the description and skim the change as a whole before anything else. Does this change even make sense? Does it belong here, or should it be somewhere else, or not exist at all? If the direction is wrong, say so now, and don't review line by line on top of a wrong premise.

Judge the description itself while you're there. It's permanent history, and "Fix bug", "Phase 1", or "Add convenience functions" doesn't tell future readers *what* changed or *why*. Flag a thin description as a finding.

If the change is too large to review well, ask the author to split it before you continue. The guide covers how.

### Step 2: Read the diff and its context

Start with the largest or most-changed file, since that's usually the heart of the change and gives the smaller pieces context. Read the surrounding code too, and don't skim past human-written code. Cover every line you've been asked to cover, and read past the diff where the change reaches into a larger method or file.

### Step 3: Run the checks

Apply the checks in the guide, in its order. Design comes first, because a wrong-shape change wastes everything below it. Use the language reflexes from the guide for the language under review.

### Step 4: Verify the claims

Verify claims against the code, and don't trust commit messages alone. A claim about live data, migration runtime behavior, or a query plan that changes a finding's severity goes to `/production-query` before you state it. Skip this for small changes, UI-only diffs, and claims the schema alone answers. A `Refuted` claim becomes a dropped finding, listed in the review so the next reader sees what was checked. An `Inconclusive` verdict, or a claim the user can't verify, gets the `Unverified —` prefix and the query, plan, or count that would settle it. `/production-query` ("Verification discipline for reviews") defines the full rule.

When you run interactively, `/test-prove` settles a claim about runtime behavior that would change a finding's severity. Whether a retry can charge twice is that kind of claim. In report mode, which runs in the read-only `reviewer` agent, the finding gets the `Unverified —` prefix and states the `/test-prove` check that would settle it.

### Step 5: Flag the limits of a code read

- **What users see.** For UI, animation, perceived performance, accessibility behavior, or layout under real data, say that a human needs to review screenshots or a running build before approval. A code read doesn't cover UX.
- **What you can't judge.** Privacy (PII handling, retention, consent flows), accessibility, internationalization, legal and compliance, and a language you have no strong reflexes for. Flag the area, state what specifically concerns you, and tell the human reviewer to get domain expertise on it before merge.

### Step 6: Deliver

Group findings by severity, each with `file:line`, the issue, and the concrete fix:

- **Blocking.** Security, data loss, correctness bugs, unauthorized access, and design problems that need rework. Must fix before merge.
- **Should fix.** Performance traps, missing test coverage on critical paths, and design issues that will compound. Strong recommendation.
- **Suggestion.** The author's call. Prefix with `Nit:` for minor polish, `Optional:` for ideas you'd like the author to consider, and `FYI:` for context the author may want for future work.
- **Praise.** When something is well done, point it out. Reviewers who only flag problems calibrate authors to defensiveness.

The `Unverified —` prefix is orthogonal to severity. A Blocking finding can be Unverified and still Blocking *if confirmed*. After the findings, add one line per claim that `/production-query` refuted: what was checked, and why the finding was dropped.

End with one recommendation: approve, approve with non-blocking comments, request changes, or request major rework. The guide sets the bar for each.

## Key Rules

1. **The bar is a healthier codebase, not perfect code.** Approve when the change improves the codebase, even with comments still attached.
2. **Design first.** Don't review line by line on top of a wrong premise.
3. **Be concrete.** Give the file and line, the issue, the fix, and why. "Consider extracting" is a soft sell. Say "extract X to Y because Z" or don't say it.
4. **Don't pile on.** Thirty findings on a fifty-line change is review theatre. Pick what matters.
5. **Never state an unverified claim as if it were verified.** Live-data claims go through `/production-query` or get the `Unverified —` prefix.
6. **Don't accept "I'll clean it up later" for added complexity.** Either it's fixed in this change, or the author files a tracked ticket.
7. **Report only.** This skill doesn't edit code, dispatch other reviewers, or post to GitHub.
