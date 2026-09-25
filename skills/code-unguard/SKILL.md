---
name: code-unguard
version: 2.0.0
description: |
  Cut over-defensive code, such as a guard for a state no caller can produce, a
  rescue that swallows, or a retry or flag nobody asked for. Takes a file, the
  current diff, or a PR. Maps the trust boundaries per value, then rules on every
  guard Cut / Convert / Ask / Keep. Uncertainty resolves to Convert (make the guard
  loud), never to leaving it alone. Keep is rare and must cite a real trigger.
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

Take a file, a diff, or a PR and cut its **armor**: defense written for states the code
cannot reach, and defense that hides the states it does reach. A nil check no call site
can trigger. A `return` on a bad argument that silently does nothing. A `rescue` that
logs and continues. A retry, a timeout, a kill-switch flag nobody asked for. The same
validation repeated three layers inside one trust boundary.

**The enemy is silence, not caution.** Most armor is not wrong to notice a state. It is
wrong about what to do next. `return if invoice.nil?` and `raise ArgumentError` defend
the same state. One hides the bug for a year and one reports it in the stack trace. So the
question is almost never "is this guard paranoid?" It is **"if this state ever happened,
would anyone find out?"**

That reframing is what makes this skill safe to be aggressive with. You are not asking
the code to be braver. You are asking it to stop lying.

## The call-site test and the loudness test

**1. The call-site test checks whether the state is reachable.** For each guard, state the
*production* call site that can produce the state it defends. Search the callers instead
of imagining one.

**2. The loudness test checks who finds out if the state happened.** A guard that raises,
or returns a typed failure the caller must handle, is loud. A guard is **silent** when it
returns nil or a default, when it logs and continues, or when it `return`s from a void
method. Silent guards are the target, whether or not the state is reachable.

Together the tests give four verdicts. Run both on every candidate, because the second
decides more cases than the first.

## Verdicts: Cut, Convert, Ask, Keep

- **Cut**: the call-site test did not find a caller, and the state is unreachable. Delete
  the guard. The evidence lists the callers you searched and the search you ran.
- **Convert**: the guard is **silent**, and the state may be reachable or you cannot
  prove that it is unreachable. Make it loud: `return` → `raise`; `rescue => e; log` →
  `rescue => e; log; raise`; optional argument with a nil default → required argument;
  `|| {}` → let it fail. Behavior on the reachable paths is unchanged; only the
  unreachable path changes, from quiet wrong to loud wrong.
- **Ask**: the guard encodes a **product decision**, such as retry or fail, degrade or
  alert, or drop or queue. State the options, and do not pick one.
- **Keep**: rare. The guard is already loud and it has a cited trigger (below).

**Uncertainty resolves to Convert.** Never to Keep. "I can't rule it out" is the exact
condition Convert exists for. You keep the check and delete the silence. A run that
ends with every candidate Keep has most likely used a void reason. Go back and
check it against the list.

## What licenses a Keep

A Keep needs **one cited, concrete trigger**, in this list:

- The guard is on the **first read of an untrusted value** at a boundary (see Step 2)
  and it is loud.
- A **named production call site** reaches the state. Cite `file:line`.
- A **real incident, ticket, or regression test that specifies what it prevents.** Not a
  test that merely exercises it.
- A **constraint that is not expressible in the type system** (a polymorphic column, a
  schemaless field, a `jsonb` blob) plus the code path that writes the odd structure.
- **Concurrency**, where the check actually closes the window: it is inside a
  transaction, holds a lock, or backs a unique constraint. A bare check-then-act closes
  nothing and is not a Keep.

## Void reasons: a Keep that rests on any of these is not a Keep

Each of these is disqualified. If a verdict rests on one, downgrade it to Convert
and say which reason you rejected.

1. **"A test exercises it."** Tests are not production callers. A test that exercises an
   unreachable state is a finding about the test. Report it as follow-up work.
2. **"An upstream bug could produce this."** True of every state in every program. This
   argument proves all armor, so it proves none.
3. **"This class is on a boundary."** Boundaries belong to *values* and never to files.
   See Step 2.
4. **"It's cheap / harmless to keep."** The cost is the reader who goes looking for the
   caller that doesn't exist.
5. **"Defense in depth."** Depth is for hostile input. Inside a boundary it is repetition.
6. **"A future refactor might reintroduce the state."** Not until it does.
7. **"Deploy skew might send the old format."** Void unless the deploy, the version
   window, and the date it closes are cited.
8. **"It's documented / it has a comment."** A comment is not evidence of reachability.
9. **"Crashing here would be worse."** That is an *Ask* and not a Keep. Usually the
   choice is between crashing and lying.

**Pre-existing code is out of scope, and you do not rule on it.** If a guard predates the
diff, don't rule on it. List it under *Out of scope* with one line, so it isn't smuggled
into the Keep column as if it had been examined.

## Arguments

- `/code-unguard` (bare): the current diff, `git diff HEAD`. If the tree is clean, the file
  under discussion. If neither, ask once: "What should I unguard?"
- `/code-unguard <file path>`: read the file and audit all of it.
- `/code-unguard <PR number | url | branch>`: fetch with `gh` and audit what the diff **adds**.
  Whether the branch is the current checkout decides edit or report.
- Steers in plain words: `--report` / "just tell me" (rule and stop, and do not write
  anything), `--deep` / "the whole file" (on a diff target, audit the surrounding file
  too).

## Cases for another skill

- Code read for **bugs or correctness** → `code-reviewer` or `/code-review`.
- Code **restructured**, dead functions removed → `code-simplifier` or `/simplify`.
- A **restructure across many files**, run as a checklist of slices → `/code-refactor`.
- **Comments or prose** → `/edit-deslop`.
- A **missing** guard on a boundary → `code-reviewer`, or `security-auditor` when the
  boundary is a security one.

## Instructions

### Step 0: Resolve the target

Per **Arguments**. For a diff: `git diff HEAD` (`--staged` if they say staged); audit
added and changed lines, plus the surrounding file under `--deep`. For a PR: `gh pr view`
and `gh pr diff`, read-only. State the target and its size in one line.

### Step 1: Load the guide

Read `~/.claude/skills/code-unguard/guard-guide.md` in full **before ruling on anything**, and
read it every run. It contains the pattern taxonomy, the boundary rules, the per-language
searches, and the worked Convert examples.

### Step 2: Map the boundaries per value (not per file)

A boundary is a **value crossing into your control**. A class, a file, or a service is
never a boundary by itself. For this target, list each untrusted value and where it
enters. Entry points include a request param, a webhook body, a deserialized blob, an
external API response, and an argument to a public library method.

These rules stop the boundary map from swallowing the audit:

- **Each value gets one guard.** The first read validates. Downstream reads of the same
  value are inside the boundary and are candidates like anything else.
- **A boundary licenses only a loud guard.** Untrusted input gets a refusal (a raise, a
  typed failure, a 400). It never gets a silent default. Armor at a boundary is still
  armor when it swallows.
- **Another service you own is a soft boundary.** It gets one loud validation at entry.
  It does not turn every method behind that entry into boundary code.

### Step 3: Rule on every guard, then stop

Find candidates with the guide's searches, then rule on each. **Do not edit yet.**

Open with a summary of the target. Say how many guards are in scope, how many are silent,
and how many are on a first boundary read. Then one row each: `location · pattern ·
verdict · evidence`.

Evidence is symmetric. **A Cut cites the search, and a Keep cites the trigger.** Prose is
not a citation. A Keep whose evidence column contains a scenario rather than a
`file:line`, a ticket, or a named test is a Convert.

Then, before presenting, two required self-checks:

- **The void-reason sweep.** Re-read each Keep against the void list. Downgrade what
  fails.
- **The weakest Keep.** State the Keep you are least sure of and say exactly what
  evidence would flip it. If you cannot point to one, you have not ruled. You have agreed.

Present the boundary map, the summary line, the table, and the weakest Keep, and **stop
for the user's call.** The user can flip a verdict or veto a cut, and can answer the Asks.
This checkpoint is the skill.

### Step 4: Apply the approved changes and verify

Apply what was approved, **cuts and converts only**, without refactoring, renaming, or
tidying the neighborhood.

Verify with what the project already configures, such as targeted tests, the typechecker,
and the linter. Say what you ran.

**A test that fails after a change is information to weigh, and it does not decide the
verdict.**

- It failed because the state is *reachable in production* → the Cut was wrong. Restore
  the guard as a Convert and say so.
- It failed because **the test itself manufactures a state production cannot** → the test
  is the finding. Do not restore the guard to make the test pass. Report it as follow-up:
  the test needs to construct a real state, or the argument needs to be required.

Never delete a test to protect a change.

### Step 5: Report

Edits remain in the working tree. Do not commit, push, or post a review.

- **Cut**: count and one line each.
- **Converted**: the loudest half of the work, what was silent and what it says now.
- **Open Asks**: the product decisions still unanswered.
- **Kept**: with the cited trigger, one line each.
- **Out of scope**: pre-existing guards you did not rule on.
- **Verification**: what ran and what passed, plus what a failure showed you.
- **Residual risk**: one honest line.

**If the run did not produce any cuts or converts, it owes an audit of itself.** Say which
named patterns were absent from the target and which were present but were kept, state
the weakest Keep, and say what would flip it. "Nothing to cut" is a legitimate result. On
a target with more than a few guards it is also an unusual one, so it arrives with its
work shown, never as a victory lap.

## Key Rules

1. **Silence is the target.** Ask "if this happened, who finds out?" before "can this
   happen?" A loud guard is usually fine, and a silent one usually isn't.
2. **Uncertainty resolves to Convert.** Never to Keep. Keep the check, delete the silence.
3. **Keep needs a citation.** A `file:line`, a ticket, a named regression test, a
   boundary read. A scenario is not evidence.
4. **The void reasons are void.** Tests-exercise-it, a-bug-could, the-class-is-a-boundary,
   defense-in-depth, cheap-to-keep. Downgrade to Convert and state the rejection.
5. **Boundaries belong to values.** Each value gets one loud guard, at the first read.
6. **Never guess a failure policy.** Retry, degrade, alert, or drop is the user's call.
   Verdict *Ask*.
7. **Cuts and converts only.** No refactoring while you're in there.
8. **Load `guard-guide.md` every run.**
9. **Never commit, push, or post a review** without an explicit ask.
10. **A zero-change run shows its work.** State the weakest Keep and what would flip it.
    A skill that only ever agrees with the code is not an instrument.
