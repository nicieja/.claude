---
name: work-log
version: 1.0.0
description: |
  Keep a decision log for a long or unattended run, so the user can audit it
  afterwards instead of rereading the whole transcript. log.sh writes one TSV
  row per decision, with the reason and the evidence behind it.
  At the end of the run, the log is checked against what happened, and the
  reviewer agent reads it and the diff and writes the Attention section that
  closes the reply.
allowed-tools:
  - Read
  - Bash
  - Agent
---

# Work log

A run I'll review later needs a trail I can audit in minutes. The log records
each decision the run made, why, and the evidence, so I read the decisions
instead of the transcript. An independent reader then lists the rows I
should check first.

The stepping-away steer in `~/.claude/AGENTS.md` requires this log. So do
`/work-triage` unattended runs and `/work-delegate`.

## Arguments

- `/work-log <slug>`: start a log for this run, or continue the newest log with that slug.
- `/work-log catch me up` or `/work-log review`: read the newest log for this repo, then write the Attention section (Step 3).

## Instructions

### Step 1: Open the log

The log goes at `~/.cache/agent-logs/<repo>/<YYYYMMDD-HHMMSS>-<slug>.tsv`, outside the repo, so it never shows up in a diff. `<repo>` is the repo's directory name. When a log with the slug already exists for this repo, continue it.

The first row of each run has the phase `start`. Its decision states the finish condition, and its evidence identifies this run, such as the session or agent id. When the log already has rows from another run, the `start` row also gives the time range of those rows.

### Step 2: Log decisions as you go

Write each row with the helper:

```bash
~/.claude/skills/work-log/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

- **phase**: the stage or workstream, such as `build`, `verify`, or `retry`.
- **decision**: what you chose or did, in one plain line.
- **why**: the reason, in plain words.
- **evidence**: a pointer, never a paragraph. A commit or a PR works, and so do a `file:line` and an artifact path.
- **result**: the outcome, such as `tests green`, `reverted`, `open`, or `INCONCLUSIVE`.

Log decision points, not every action. Log a fork you chose, a unit finished with its check, a pivot or a revert with its trigger, a blocker, and a default you picked for a decision that is mine. In a loop, write one row per iteration.

The log is append-only. A wrong row gets a new row that corrects it, and the old row stays.

### Step 3: Close the run

1. **Audit the log against what happened.** Walk this run's rows against the transcript and the commits. Each row must match a real decision, and its evidence must resolve and show what the row claims. A fork or a pivot that changed the work but has no row is a gap, so add a row for it. A wrong row gets a correcting row.
2. **Dispatch the reviewer.** Send the `reviewer` agent (`subagent_type: "reviewer"`) a brief with the log path, the diff range of the run, and the run's report. Ask it to flag what deserves my attention, not to redo the work:
   - decisions with weak or missing evidence;
   - checks that were skipped, or claimed without proof;
   - choices that look risky in hindsight, such as a symptom papered over or scope that grew;
   - anything I'd miss on a quick read.

   In a tool without subagents, do this read yourself, and say so.
3. **End the reply with an Attention section.** Its first line is `reviewed by: reviewer agent` (or `self-review` without subagents). Then one line per flag, each pointing at a row or a commit. "No flags" is a valid result.

## Key Rules

1. **One row per decision, with its evidence.** A row without a pointer is a claim.
2. **Append-only.** A correction is a new row.
3. **The log stays out of the repo.** It lives in `~/.cache/agent-logs/`, and it's committed only when I ask for it.
4. **My calls go elsewhere.** A decision I made goes to `context/<project>/decisions.md`. This log records the run's own decisions.
5. **Every run that kept a log ends with an Attention section.**
