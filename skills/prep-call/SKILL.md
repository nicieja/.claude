---
name: prep-call
version: 1.0.0
description: |
  Prepare a one-page brief before a customer or partner call: where the
  relationship stands, what changed since last time, open commitments in both
  directions, and the 2-3 hypotheses this call should test. Reads the project's
  partner roster and insight log; read-only.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Prep-call

Walk into the call already knowing what you owe them, what they owe you, and what
you're trying to learn. The brief fits on one page; the hypotheses are the point.

## Arguments

- `/prep-call <partner>` — match against the roster (fuzzy is fine; ask once if
  ambiguous).
- `/prep-call` — bare: list the roster and ask which call to prep.

## When this is the wrong skill

- After the call → `/debrief-call`
- Product/roadmap strategy without a specific call → the `product-manager` agent

## Instructions

### Step 1: Load the relationship

Read `context/<project>/partners.md` (missing → ask once, offer to scaffold, stop:
there is nothing to prep from). Find the partner's row. Read their section of
`context/<project>/insights.md` for history, newest first.

### Step 2: Gather what changed

- Since the last debrief entry: shipped changes relevant to them (gh, changelog),
  and — if the charter or stack.md names a usage source the session can query —
  their recent usage. Skip-and-note what can't be reached.
- Open commitments: theirs and ours, from the insight log's commitment lines and
  the roster's next-step cell.

### Step 3: Compose the brief

One page, five sections: **Snapshot** (who, status, cadence, outcome definition
from the roster) · **Since last call** (what shipped for them, what their usage
shows) · **Commitments** (ours / theirs, each with its date) · **Hypotheses to
test** (2–3, phrased as questions the call can actually answer, tied to the
charter's drivers) · **Asks** (only what the roster's status justifies — e.g. an
outcome-definition conversation or pricing input when the next-step cell points
that way).

## Key Rules

1. **Read-only.** The debrief writes; the prep doesn't.
2. **Hypotheses are questions, not topics.** "Does X block their weekly usage?"
   beats "discuss X".
3. **Two to three hypotheses.** More means none get answered.
4. **Skip-and-note unreachable sources.** Never pad the brief with assumptions.
