---
name: weekly
version: 1.0.0
description: |
  Draft the periodic review the project's charter defines — usage and metric
  movement, what shipped, what was learned, the top failure or blocker, and the
  change shipped in response. Every number comes from an executed command or
  query; anything uncomputable becomes an explicit gap. Produces a draft for the
  user to edit and post — never posts anywhere.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Weekly

Turn a week of activity into the review the charter promises, without laundering
guesses into numbers. The draft's authority comes from the fact that every figure
in it was computed in this run.

## Arguments

- `/weekly` — the last completed week for the current project.
- `/weekly <window>` — an explicit window ("this week", "June", "last 14 days").

## When this is the wrong skill

- A daily state-of-the-world → `/brief`
- A standup message → `/standup`
- A retro on one piece of work → `/retro`

## Instructions

### Step 1: Load the charter

Read `~/.claude/context/<project>/charter.md`. If it's missing or has no metric
definition, ask once whether to scaffold it from `context.example/charter.md`; a
review without a charter still runs, but its metric section is a single line naming
the gap.

### Step 2: Collect — computed or absent

- **Metric:** run the charter's "how to compute" if it is a command or query the
  session can execute. If it's a dashboard or not instrumented, emit
  `[needs manual number: <metric> — <where to get it>]`. Never estimate.
- **Shipped:** `gh pr list` for PRs merged in the window; translate titles into
  impact language (read bodies for the load-bearing ones).
- **Learning:** new entries in `context/<project>/insights.md` within the window.
- **Failures/blockers:** telemetry failures from `~/.claude/telemetry/fleet.jsonl`,
  error-tracker movers if a connector or CLI is available, and blocker notes in
  insights. Pick the **single** top blocker — the review names one, not a list.
- **Response:** the shipped change that answers the blocker, when one exists. When
  none does, say so plainly — that gap is the most useful sentence in the review.

### Step 3: Draft

Use the charter's `Periodic review` section order; default order otherwise: metric
→ shipped → learning → top blocker → change shipped in response → next week. When
the audience is Slack, follow `/summary`'s formatting rules (Slack mrkdwn, sentence
case, no template smell). End the draft with a horizontal rule and the line:
`Numbers above come from the commands run in this session; placeholders are yours
to fill. Edit and post yourself.`

## Key Rules

1. **The draft never types a number it didn't compute.** Placeholders over
   estimates, always.
2. **One top blocker.** Choosing is the analysis; a list is an evasion.
3. **Never posts.** No Slack writes, no tracker writes — the artifact is a draft.
4. **Honest gaps beat manufactured cohesion.** A missing response-to-blocker or an
   uninstrumented metric is stated, not papered over.
