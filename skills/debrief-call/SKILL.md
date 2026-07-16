---
name: debrief-call
version: 1.0.0
description: |
  File what a customer or partner call actually taught: facts, product signals
  with verbatim quotes, success and pricing signals, commitments in both
  directions, and the next step. Appends a structured entry to the project's
  insight log and updates the roster row. The only skill that writes the
  customer-learning files.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Debrief-call

Capture the call while it's fresh, in a shape future runs can mine: one dated entry
per call, quotes preserved verbatim, commitments explicit. The insight log is the
memory the customer loop runs on.

## Arguments

- `/debrief-call <partner>` — source the transcript automatically when a meeting
  connector (recording/notes tool) is available in the session; otherwise ask for
  pasted notes or a transcript path.
- `/debrief-call <partner> <path-or-notes>` — explicit source.

## When this is the wrong skill

- Before the call → `/prep-call`
- A Slack-ready investigation summary → `/summary`

## Instructions

### Step 1: Resolve partner and source

Match the partner against `context/<project>/partners.md` (ask once if ambiguous).
Resolve the transcript: connector search by participant and date when available,
else the provided path or pasted notes. No source → stop; there is nothing to file.

### Step 2: Extract

From the transcript, pull: **facts** (plan, environment, scale — things that don't
expire), **product signals** (feature asks, friction, failures — each load-bearing
claim as a verbatim quote with the speaker's role), **success signals** (what they
called valuable, in their words), **commercial signals** (willingness-to-pay,
outcome-definition reactions, pricing comments), **commitments** (ours and theirs,
each with an owner and a date), **next step**. Ask at most two clarifying questions,
and only when a commitment or quote is genuinely ambiguous.

### Step 3: Write

- Append to `context/<project>/insights.md` under `## <Partner>` (create the file
  or heading if missing), one dated entry:

  `### <YYYY-MM-DD> — <call type>` followed by the six extraction sections, each a
  short list, quotes kept verbatim.

- Update the partner's row in `partners.md`: last-call date implied by the entry,
  refreshed status and next step.

### Step 4: Surface follow-ups

List anything that should become tracker issues or roadmap items — as suggestions
with a one-line rationale each. Offer `/linear` (or the project's equivalent) for
any the user picks; never create issues from this skill.

## Key Rules

1. **Quotes are verbatim or absent.** Paraphrase is where invented signal sneaks
   in; a claim worth acting on is worth quoting exactly.
2. **Commitments carry an owner and a date.** "We'll look into it" is not a
   commitment entry.
3. **Writes only to `context/<project>/`.** Roster and insight log, nothing else —
   no tracker writes, no repo writes.
4. **Two clarifying questions maximum.** The transcript is the source of truth;
   the user's memory fills gaps, it doesn't replace the record.
