---
name: work-firefight
version: 1.0.0
description: |
  Pair with the human on a weekly firefighting rotation. Gathers urgent fires,
  the support backlog, the dead job queue, and error-tracker issues into one
  prioritized view, then works them in strict priority order through
  /production-incident. Delegates what a specialist would fix faster, owns
  the follow-up on every delegation, and ends with a rotation handoff summary.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - Agent
  - Skill
---

# Firefight

Pair with the engineer on this week's firefighting rotation, a human who has production console access. The rotation triages and resolves support issues, production fires, the Sidekiq dead queue, and Sentry errors, so the rest of the team can focus on roadmap work. There is zero expectation of roadmap progress during the rotation. Some issues need delegation to specialists. That's fine, but the rotation engineer owns follow-up on every delegated item.

## Roles

- **This skill** explores the codebase and generates scripts, then analyzes the output and iterates toward resolution.
- **The human** runs scripts in the production console and pastes the output back. The human also makes the final decision on applying fixes.
- **Reach into production** is exactly what `/production-query` grants: read-only diagnostics through a query MCP the user has confirmed for this project, recorded in the project's `stack.md`. There is no other access to production.
- **Every production mutation goes through the human.** A read-only diagnostic may run through the confirmed query MCP. A fix script never does. The human runs it in their own console.

## Arguments

- `/work-firefight`: start or resume a rotation session.
- `/work-firefight <issue>`: add one issue to the session. The issue is a Linear ID or URL, or a pasted report. Steps 0 to 3 still run, and the issue takes its place in the priority order.

## Cases for another skill

- One production issue to diagnose, outside a rotation → `/production-incident`.
- One claim about live state to verify → `/production-query`.
- An issue that needs scoping before work begins → `/idea-spec`.
- Investigation findings to post on a Linear issue → `/linear-comment`.

## Instructions

### Step 0: Ask about fires

Always ask first: "Any active fires or urgent escalations?" These come from the engineering escalation channel, pasted in by the rotation engineer. An active fire is P0, and it goes ahead of everything below, the delegation check included.

### Step 1: Check earlier delegations

Ask about the status of any items delegated in earlier sessions. Flag anything past its follow-up date. For each overdue item, offer to ping the assignee or take the issue back, or to extend the deadline.

### Step 2: Gather the other sources

The priority order is strict. Never skip to a lower priority while a higher one remains unaddressed.

| Priority | Source | Description |
|----------|--------|-------------|
| P0 | Urgent fires | Engineering escalation channel, Slack pings, active incidents |
| P1 | Support backlog | General support issues from Linear |
| P2 | Quality initiatives | Other quality work identified by the team |
| P3 | Sidekiq dead queue | Failed background jobs needing investigation |
| P4 | Sentry issues | Error tracking items to triage and resolve |
| P5 | Remaining quality | Lower-priority improvements and cleanup |

Linear is reached through the Linear MCP tools (load them via ToolSearch). If none are available in the session, say so and work from what the human pastes.

- **Urgent fires (P0).** Asked in Step 0.
- **Linear support backlog (P1).** List support-labeled issues through the Linear MCP tools, sorted by priority. Adapt the label filter if the team uses a different convention.
- **Sidekiq dead queue (P3).** Generate a read-only console script to enumerate dead jobs. The human runs it and pastes the output back.

  ```ruby
  # Diagnostic: enumerate Sidekiq dead queue (read-only)
  dead = Sidekiq::DeadSet.new
  dead.group_by(&:klass).transform_values(&:count).sort_by { |_, v| -v }.first(20)
  ```

- **Sentry (P4).** Attempt `sentry-cli issues list --project <project>`, or ask the human to paste the top issues from the Sentry dashboard.
- **Quality work (P2, P5).** Take these from the team's list, if the human has one.

### Step 3: Present one prioritized view

After gathering all sources, present one merged, prioritized table. Confirm the order with the human before diving into any issue.

### Step 4: Handle or delegate

**Handle directly** when the issue:

- is resolvable within about 30 minutes
- doesn't require deep specialist knowledge of a specific domain
- is within the rotation engineer's ability to diagnose and fix

**Delegate** when the issue:

- requires domain expertise that only a specific team or person has
- would take a specialist a fifth of the rotation engineer's time
- involves systems the rotation engineer shouldn't be modifying

Delegating doesn't mean forgetting. For each delegation:

1. Assign it in Linear by updating the issue's assignee through the Linear MCP tools.
2. Add a context comment through the Linear MCP tools, with the body passed as the tool's string argument.
3. Set a follow-up date.
4. Track it for the session summary.

Keep a running list of delegations with the issue ID, the assignee, the delegated date, the follow-up date, and the current status.

### Step 5: Investigate and fix

Run `/production-incident` for each issue that is handled directly. It covers the whole loop, from parsing the issue and exploring the codebase through read-only diagnostics and the root cause to a fix script with `dry_run = true`. It also runs the check before the human applies a fix. Wait for each output, pasted by the human or returned by the query MCP, before analyzing or proceeding. Work one issue at a time, because the human needs to be in the loop for each.

Other tools for the rotation:

- A code change or a fix script that needs review before it's applied → dispatch the `reviewer` agent (`subagent_type: "reviewer"`) with a brief that loads `pr-critique` and contains the script text or the diff. A fix script exists only in chat, so it goes into the brief in full.
- A quality issue that is a refactor → `/simplify`, or `/code-refactor` across many files.
- A decision that needs more pushback than the pre-apply check gives → `/idea-challenge`.

### Step 6: Close each issue

After resolving each issue:

1. **Slack summary.** Offer a humanized, copy-pasteable Slack summary covering the root cause, the steps taken, the resolution, and any follow-up needed.
2. **Close in Linear.** Update the issue to its done state through the Linear MCP tools.

### Step 7: Write the session summary

After all the work is done, produce a full session summary for the rotation handoff:

- issues resolved, with a brief root cause and fix for each
- issues delegated, with the assignee and the follow-up date
- open items carrying over
- any patterns or systemic issues noticed

## Key Rules

1. **Reads through `/production-query`, writes through the human.** A read-only diagnostic may execute through the confirmed query MCP. The human runs every fix script and pastes the output back.
2. **Priority order is sacred.** Never skip to a lower priority while a higher one remains.
3. **Investigate before fixing.** At least one diagnostic runs first, through `/production-query` or by the human.
4. **Diagnostic scripts are read-only, and fix scripts use `dry_run = true`,** without exception.
5. **Wait for the output,** pasted by the human or returned by the query MCP, before analyzing or proceeding.
6. **Delegation is not abandonment.** Own the follow-up on every delegated item.
7. **One issue at a time.** Process issues in sequence, because the human needs to be in the loop for each.
8. **Always offer a Slack summary** after resolving a fire.
9. **Write the session summary for the rotation handoff** at the end of every session.
