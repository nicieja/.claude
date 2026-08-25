---
name: unguard
version: 2.0.0
description: |
  Cut over-defensive code — guards for states no caller can produce, rescues that
  swallow, retries and flags nobody asked for. Takes a file, the current diff, or a
  PR; maps the trust boundaries per value, then rules on every guard Cut / Convert /
  Ask / Keep. Uncertainty resolves to Convert — make the guard loud — never to
  leaving it alone. Keep is rare and must cite a real trigger. Loads guard-guide.md
  every run.
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

**The enemy is silence, not caution.** Most armor is not wrong to notice a state — it is
wrong about what to do next. `return if invoice.nil?` and `raise ArgumentError` defend
the same state; one hides the bug for a year and one names it in the stack trace. So the
question is almost never "is this guard paranoid?" It is **"if this state ever happened,
would anyone find out?"**

That reframing is what makes this skill safe to be aggressive with. You are not asking
the code to be braver. You are asking it to stop lying.

## The two tests

**1. The call-site test — is the state reachable?** For each guard, name the *production*
call site that can produce the state it defends. Search; don't imagine.

**2. The loudness test — if it happened, who finds out?** A guard that raises, or returns
a typed failure the caller must handle, is loud. A guard that returns nil, returns a
default, logs and continues, or `return`s from a void method is **silent** — and silent
is the target, whether or not the state is reachable.

The two tests give four verdicts. Run both on every candidate; the second decides more
cases than the first.

## The four verdicts

- **Cut** — the call-site test found nothing and the state is unreachable. Delete the
  guard. Evidence names the callers you searched and the search you ran.
- **Convert** — the state may be reachable, or you cannot prove it isn't, **and the guard
  is silent**. Make it loud: `return` → `raise`; `rescue => e; log` → `rescue => e; log;
  raise`; optional argument with a nil default → required argument; `|| {}` → let it fail.
  Behavior on the reachable paths is unchanged; only the unreachable path changes, from
  quiet wrong to loud wrong.
- **Ask** — the guard encodes a **product decision**: retry or fail, degrade or alert,
  drop or queue. Name the options; don't pick one.
- **Keep** — rare. The guard is already loud *and* it has a cited trigger (below).

**Uncertainty resolves to Convert.** Never to Keep. "I can't rule it out" is the exact
condition Convert exists for — you keep the check and delete the silence. A run that
ends with every candidate Keep has almost certainly used a void reason; go back and
check it against the list.

## What licenses a Keep

A Keep needs **one cited, concrete trigger**, in this list:

- The guard sits on the **first read of an untrusted value** at a boundary (see Step 2)
  and it fails loudly.
- A **named production call site** reaches the state. Cite `file:line`.
- A **real incident, ticket, or regression test that names what it prevents.** Not a test
  that merely exercises it.
- A **constraint the type system cannot carry** — a polymorphic column, a schemaless
  field, a `jsonb` blob — plus the code path that writes the odd shape.
- **Concurrency**, where the check actually closes the window: it is inside a
  transaction, holds a lock, or backs a unique constraint. A bare check-then-act closes
  nothing and is not a Keep.

## Void reasons — a Keep resting on any of these is not a Keep

These are the arguments that turned the first two runs of this skill into zero cuts.
Every one of them is disqualified. If a verdict rests on one, downgrade it to Convert
and say which reason you rejected.

1. **"A test reaches it."** Tests are not production callers. A test that exercises an
   unreachable state is a finding about the test — name it as follow-up work.
2. **"An upstream bug could produce this."** True of every state in every program. This
   argument proves all armor and therefore proves none.
3. **"This class sits on a boundary."** Boundaries belong to *values*, not files. See
   Step 2.
4. **"It's cheap / harmless to keep."** The cost is the reader who goes looking for the
   caller that doesn't exist.
5. **"Defense in depth."** Depth is for hostile input. Inside a boundary it is repetition.
6. **"A future refactor might reintroduce the state."** Not until it does.
7. **"Deploy skew might send the old shape"** — void unless you name the deploy, the
   version window, and when it closes.
8. **"It's documented / it has a comment."** A comment is not evidence of reachability.
9. **"Crashing here would be worse."** That is an *Ask*, not a Keep — and usually the
   choice is between crashing and lying.

**Pre-existing code is a scope question, not a verdict.** If a guard predates the diff,
don't rule on it — list it under *Out of scope* with one line, so it isn't smuggled into
the Keep column as if it had been examined.

## Arguments

- `/unguard` (bare) — the current diff: `git diff HEAD`. If the tree is clean, the file
  under discussion. If neither, ask once: "What should I unguard?"
- `/unguard <file path>` — read the file and audit all of it.
- `/unguard <PR number | url | branch>` — fetch with `gh`; audit what the diff **adds**.
  Whether the branch is the current checkout decides edit or report.
- Steers in plain words: `--report` / "just tell me" (rule and stop, write nothing),
  `--deep` / "the whole file" (on a diff target, audit the surrounding file too).

## When this is the wrong skill

- Code read for **bugs or correctness** → `code-reviewer` or `/code-review`.
- Code **restructured**, dead functions removed → `code-simplifier` or `/simplify`.
- **Comments or prose** → `/deslop`.
- A **missing** guard on a boundary → `code-reviewer`, or `security-auditor` when the
  boundary is a security one.

## Instructions

### Step 0: Resolve the target

Per **Arguments**. For a diff: `git diff HEAD` (`--staged` if they say staged); audit
added and changed lines, plus the surrounding file under `--deep`. For a PR: `gh pr view`
and `gh pr diff`, read-only. State the target and its size in one line.

### Step 1: Load the guide

Read `~/.claude/skills/unguard/guard-guide.md` in full **before ruling on anything**. It
holds the pattern taxonomy, the boundary rules, the per-language searches, and the worked
Convert examples. Every run.

### Step 2: Map the boundaries — per value, not per file

A boundary is a **value crossing into your control**, not a class, a file, or a service.
For this target, list each untrusted value and where it enters: a request param, a webhook
body, a deserialized blob, an external API response, an argument to a public library
method.

Three rules that stop the boundary map from swallowing the audit:

- **One value, one guard.** The first read validates. Downstream reads of the same value
  are inside the boundary and are candidates like anything else.
- **A boundary licenses a loud guard, not a silent one.** Untrusted input earns a refusal
  — a raise, a typed failure, a 400. It never earns a silent default. Armor at a boundary
  is still armor when it swallows.
- **Another service you own is a soft boundary.** It earns one loud validation at entry.
  It does not turn every method behind that entry into boundary code.

### Step 3: Rule on every guard, then stop

Find candidates with the guide's searches, then rule on each. **Do not edit yet.**

Open with the shape of the target: how many guards are in scope, how many are silent, how
many sit on a first boundary read. Then one row each: `location · pattern · verdict ·
evidence`.

Evidence is symmetric. **A Cut cites the search; a Keep cites the trigger.** Prose is not
a citation. A Keep whose evidence column contains a scenario rather than a `file:line`, a
ticket, or a named test is a Convert.

Then, before presenting, two required self-checks:

- **The void-reason sweep.** Re-read each Keep against the void list. Downgrade what
  fails.
- **The weakest Keep.** Name the Keep you are least sure of and state exactly what
  evidence would flip it. If you cannot name one, you have not ruled — you have agreed.

Present the boundary map, the shape line, the table, the weakest Keep, and **stop for the
user's call.** They can flip a verdict, veto a cut, or answer the Asks. This checkpoint is
the skill.

### Step 4: Apply, then verify

Apply what was approved — **cuts and converts only**, no refactoring, no renaming, no
tidying the neighborhood.

Verify with what the project already configures: targeted tests, typechecker, linter.
Name what you ran.

**A test that fails after a change is information, not a verdict.**

- It failed because the state is *reachable in production* → the Cut was wrong. Restore
  the guard as a Convert and say so.
- It failed because **the test itself manufactures a state production cannot** → the test
  is the finding. Do not restore the guard to keep the test green. Report it as follow-up:
  the test needs to construct a real state, or the argument needs to be required.

Never delete a test to protect a change.

### Step 5: Report

Edits stay in the working tree. Never commit, never push, never post a review.

- **Cut** — count and one line each.
- **Converted** — the loudest half of the work: what was silent, what it says now.
- **Open Asks** — the product decisions still unanswered.
- **Kept** — with the cited trigger, one line each.
- **Out of scope** — pre-existing guards you did not rule on.
- **Verification** — what ran, what passed, what a failure taught you.
- **Residual risk** — one honest line.

**If the run produced zero cuts and zero converts, it owes an audit of itself.** Say which
named patterns were absent from the target and which were present but survived, name the
weakest Keep, and say what would flip it. "Nothing to cut" is a legitimate result — on a
target with more than a handful of guards it is also an unusual one, so it arrives with
its work shown, never as a victory lap.

## Key Rules

1. **Silence is the target.** Ask "if this happened, who finds out?" before "can this
   happen?" A loud guard is usually fine; a silent one usually isn't.
2. **Uncertainty resolves to Convert.** Never to Keep. Keep the check, delete the silence.
3. **Keep needs a citation.** A `file:line`, a ticket, a named regression test, a
   boundary read. A scenario is not evidence.
4. **The void reasons are void.** Tests-reach-it, a-bug-could, the-class-is-a-boundary,
   defense-in-depth, cheap-to-keep. Downgrade to Convert and name the rejection.
5. **Boundaries belong to values.** One value, one loud guard, at the first read.
6. **Never guess a failure policy.** Retry, degrade, alert, drop — that is the user's
   call. Verdict *Ask*.
7. **Cuts and converts only.** No refactoring while you're in there.
8. **Load `guard-guide.md` every run.**
9. **Never commit, never push, never post a review** without an explicit ask.
10. **A zero-change run shows its work.** Name the weakest Keep and what would flip it.
    A skill that only ever agrees with the code is not an instrument.
