---
name: brief
version: 1.0.0
description: |
  Morning brief and decision inbox. Gather overnight state — PRs and CI, the
  issue queue, fleet telemetry, production errors, today's calendar — from
  whatever sources this project and session actually have, and compress it into
  what moved, what's blocked on the user, and a suggested plan. Zero questions;
  designed to run unattended.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

# Brief

Start the day from a written brief instead of a blank terminal. The skill reports
only what its sources actually returned — anything it can't reach is named as
skipped, never inferred.

## Arguments

- `/brief` — full brief for the current project.
- `/brief <focus>` — bias the brief toward one thread (a PR, an incident, a metric).

## When this is the wrong skill

- Drafting the weekly review → `/weekly`
- Investigating one production issue in depth → `/investigate`
- A standup message for the team → `/standup`

## Instructions

Follow in order. Every step that can't run (missing tool, missing file, no access)
is skipped and listed in the final section — no questions, no guesses.

### Step 1: Load context

Read `~/.claude/context/<project>/stack.md`, `charter.md`, and `escalation.md` if
present. Missing files reduce scope (no charter → no metric pulse) and are listed as
skipped.

### Step 2: Gather, read-only

- **PRs and CI:** `gh pr list --author "@me" --state open`, plus review-requested
  (`gh pr list --search "review-requested:@me"`), plus check states on open PRs.
- **Issue queue:** the tracker CLI named in stack.md (e.g. `linear issue list --sort
  priority --no-pager`); diff against what the user likely saw yesterday only if
  telemetry shows a prior run.
- **Fleet:** tail `~/.claude/telemetry/fleet.jsonl` for entries since the last brief
  — completed stages, failures, skips with reasons.
- **Production:** if an error-tracker connector tool is available in this session,
  pull the top new or regressed issues; else if stack.md names a CLI, use it; else
  skip.
- **Calendar:** if a calendar connector tool is available, list today's meetings;
  else skip.

### Step 3: Compose the brief

Five sections, in this order, each only as long as its content earns:

- **What moved** — merged/updated PRs, completed fleet stages, closed issues. One
  line each, impact language, not titles.
- **Blocked on you** — the decision inbox: every item waiting on the user (reviews
  requested, escalations from unattended runs, unresolved deference conflicts,
  stalled PRs), each with a one-line recommended action.
- **Fleet** — lanes active, queued, skipped; anything the telemetry flags as
  repeatedly failing.
- **Production pulse** — top movers from the error tracker; silence is reported as
  "nothing new", not omitted.
- **Suggested plan** — 2–4 bullets for the day, derived from the above and the
  charter's drivers when available.

Close with **Skipped sources** — every source that couldn't run and why, one line
each.

## Key Rules

1. **Report only what a command returned.** No inferred statuses, no invented
   numbers, no "probably fine".
2. **Zero questions.** This skill must be schedulable; gaps are named, not asked
   about.
3. **Read-only.** No writes anywhere — not to the tracker, not to git, not to
   context files.
4. **The decision inbox is the point.** If the user reads one section, it's Blocked
   on you — put the judgment there, one recommended action per item.
