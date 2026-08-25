---
name: unguard
version: 1.0.0
description: |
  Cut over-defensive code — guards for states no caller can produce, rescues that
  return a default, retries and flags nobody asked for — without weakening a single
  real boundary. Takes a file, the current diff, or a PR; maps the trust boundaries
  first, then ranks every guard Cut / Keep / Ask and waits for your call before it
  touches anything. The burden of proof is on the cut: name the caller, or the guard
  stays. Loads guard-guide.md every run.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# Unguard

Take a file, a diff, or a PR and cut its **armor**: the defense that was written for
states the code cannot reach. A nil check no call site can trigger. A `rescue` around
code that doesn't raise. A catch-and-default that turns a failure into a plausible
wrong answer. A retry, a timeout, a kill-switch flag nobody asked for. The same
validation repeated three layers inside one trust boundary.

This is the code twin of `/deslop`. Slop is generated-but-not-authored prose; armor
is generated-but-not-authored defense — cheap for an agent to add, expensive for a
human to read, and impossible to delete later because nobody can prove it's dead.
Deleting it is a behavior change on paper and no change at all in fact, which is
exactly why it needs evidence rather than taste.

The **silent fallback** is the first target. Extra lines cost reading time; a fallback
costs truth. It trades an error you would have seen for an answer you won't question.

One instrument runs the method: **the call-site test.** For each guard, name the caller
that can reach the state it defends. If you can name one, the guard stays. If you
cannot — after actually looking — it goes. No evidence, no cut. That test, and not a
preference for short code, is what makes this skill safe to run.

The inverse failure is real and it is worse than the disease: a skill that strips
validation off a system boundary has caused a bug, not removed one. Step 2 exists to
prevent it, and Key Rule 2 outranks every other rule here.

## Arguments

- `/unguard` (bare) — the current diff: `git diff HEAD`. If the tree is clean, the file
  under discussion. If neither, ask once: "What should I unguard?"
- `/unguard <file path>` — read the file and audit all of it.
- `/unguard <PR number | url | branch>` — fetch with `gh`; audit what the diff **adds**.
  Note whether the PR's branch is the current checkout: that decides whether Step 4 can
  edit files or only report.
- Steers in plain words: `--report` / "just tell me" (diagnose and stop, write nothing),
  `--deep` / "the whole file" (on a diff target, audit the surrounding file too, not only
  the added lines).

## When this is the wrong skill

- They want the code read for **bugs or correctness** → `code-reviewer` or `/code-review`.
  Unguard removes; it does not hunt.
- They want code **restructured**, or dead functions and branches removed → `code-simplifier`
  or `/simplify`.
- They want **comments or prose** cut → `/deslop`.
- A boundary is **missing** a guard — the opposite complaint → `code-reviewer`, or
  `security-auditor` when the boundary is a security one.
- The failure policy itself is the question ("should this retry or alert?") → that's a
  product decision; `/pushback` or a plain conversation, not this.

## Instructions

Follow in order.

### Step 0: Resolve the target

Resolve per **Arguments** — file, diff, PR, or bare.

- **File:** read it whole.
- **Diff:** `git diff HEAD` (add `--staged` if the user says staged). Audit added and
  changed lines; under `--deep`, the surrounding file too.
- **PR:** `gh pr view <ref>` and `gh pr diff <ref>`. Read-only: no push, no posted review,
  without an explicit ask.
- **Bare, nothing obvious:** ask once and wait.

State the target and its size in one line before you go on.

### Step 1: Load the guide

Read `~/.claude/skills/unguard/guard-guide.md` in full **before you judge anything**. It
holds the pattern taxonomy, the boundary map, the per-language search patterns, and the
keep-list. Load it every run — it's the part tuned over time; don't work from memory.

### Step 2: Map the boundaries first

Before a single verdict, list the **system boundaries** this code touches: HTTP params
and handlers, CLI input, external API responses, deserialization, queue and webhook
payloads, third-party callbacks, rows whose shape isn't guaranteed, the public surface of
a library. Use the guide's boundary map.

Write the list down in the diagnosis. A guard **on** a boundary is a Keep by default and
needs no further argument. Everything inside the boundary is a candidate, and nothing
else is.

This step is not optional and it is not a formality. Judging guards before mapping
boundaries is how this skill breaks a system.

### Step 3: Diagnose — rank every guard, then stop

Find the candidates (the guide's search patterns make this fast), then rank them. **Do
not edit yet.**

**Declare the goal: a count and its location.** "~7 of 11 guards look cuttable, mostly in
the service layer, none in the controller." This is the prediction Step 4 verifies
against — never a quota. Skip it when there are only two or three guards in scope.

**Rank each candidate** in one table: `location · pattern · verdict · evidence`.

- **Cut** — no caller can produce the state. The evidence column names what you checked:
  the call sites and the search that found them ("3 callers, all pass a built object —
  `grep -rn 'InvoiceSync.new'`"). An unchecked guess is not evidence.
- **Keep** — a boundary, a documented contract, a type that admits the state, or a real
  caller reaches it. One clause of reason is enough.
- **Ask** — the guard encodes a **product decision** you don't get to make: retry or
  fail, degrade or alert, drop or queue. Name the options and put them to the user.

**Reconcile** the count against the table before presenting. If the named cuts fall well
short of the prediction, either the prediction was inflated or the scan missed guards —
resolve that now, on paper, not after editing.

Present the boundary map, then the goal, then the table, and **stop for the user's
call.** They can correct a verdict, veto a cut, or answer the Asks. This checkpoint is
the skill.

### Step 4: Cut, then verify

With the go-ahead, remove what was approved — **cuts only**. No renaming, no extracting,
no tidying the neighbourhood. Where a Cut leaves a now-pointless local variable or an
empty block, remove that too; anything larger is `/simplify`'s job.

Then verify with what the project already configures: the targeted tests, the
typechecker, the linter. Name what you ran.

**A test that fails because it asserted the guard is evidence, not an obstacle.** Something
reaches that state, or someone decided it must be handled. Restore the guard, move it to
Keep, and say so in the report. Never delete the test to make the cut survive.

If verification surfaces more candidates, run another pass. Cap at ~3, then stop and say
what's left.

### Step 5: Report

- **File or diff target:** the edits are in the working tree. Never commit, never push.
- **PR, branch checked out:** same. Summarize what changed.
- **PR, not checked out, or `--report`:** print the ranked table plus the suggested
  removals. Offer to post them as review comments only if asked.

Report:

- **Cut** — count against the prediction, one line each.
- **Kept** — with the reason, boundary keeps first. This half of the report matters as
  much as the other; a run that cut nothing but proved the armor was load-bearing is a
  finished result.
- **Open Asks** — the product decisions still unanswered.
- **Verification** — what ran, what passed, what a failure taught you.
- **Residual risk** — in one honest line. If a cut changes behavior on a path you could
  not fully rule out, say which path and why you judged it unreachable.

## Key Rules

1. **The burden of proof is on the cut.** Name the caller, or the guard stays. An
   unchecked assumption is not evidence.
2. **Boundaries keep their armor.** User input, external responses, deserialized
   payloads, public library surfaces. Stripping a real validation for tidiness is the one
   failure this skill must never have — this rule outranks all the others.
3. **Silent fallbacks first.** A catch-and-default is the highest-value cut: it hides
   bugs, and it is the pattern agents add most.
4. **A failing test is evidence.** Restore the guard and reclassify. Never edit the test
   to protect the cut.
5. **Cuts only.** No refactoring, no renaming, no unrelated cleanup while you're in there.
6. **Never guess a failure policy.** Retry, degrade, alert, drop — that's the user's
   call. Verdict *Ask*, not a quiet decision.
7. **Load `guard-guide.md` every run.** The taxonomy and keep-list live there, not in
   memory.
8. **Never commit, never push, never post a review** without an explicit ask.
9. **"Nothing to cut" is a finished result.** Say it plainly. Padding a thin run with
   marginal cuts is how this skill would start causing the bugs it was written to prevent.
