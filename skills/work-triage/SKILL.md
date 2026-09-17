---
name: work-triage
version: 1.2.0
description: |
  Fetch Linear issues with no PR attached, orchestrate parallel subagents
  through staged pipelines (explore → plan → build → test → review),
  collect user feedback between stages (or run unattended with tiers and
  recorded resolutions), and push draft PRs when complete.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - Skill
  - AskUserQuestion
---

# Triage

Fetch issues assigned to you in Linear that have no PR attached. Dispatch specialized subagents to work on each in parallel, and push draft PRs when done.

## Arguments
- `/work-triage`: fetch and work on all eligible issues
- `/work-triage ENG-123`: work on one specific issue
- `/work-triage ENG-123 ENG-456`: work on specific issues
- `/work-triage --unattended` (optionally with issue IDs): non-interactive run for schedules. See Unattended mode.

## Linear access

Use the Linear MCP tools. They're deferred, so load them via ToolSearch (search
"linear") before first use, and phrase calls by capability rather than assuming
exact tool names. If only authentication stubs are available, the server needs its
OAuth flow run once. In an interactive run, offer to run it. In an unattended run,
treat Linear as unavailable.

Operations this skill needs:
- list the user's issues, sorted by priority
- get an issue with its description, `updatedAt`, and comments
- update an issue to its started state, then read its branch name field
- PRs are created with `gh pr create --draft`. Linear links them automatically
  because the branch name includes the issue ID

## Instructions

Follow these steps in order. Do NOT skip steps.

---

### Step 0: Preflight

1. **Load project context.** Read `~/.claude/context/<project>/stack.md` and
   `risk-tiers.md` (`<project>` = repo directory name). Take the WIP cap (default 3
   when absent) and the tier surfaces. If either file is missing: interactively, ask
   once and offer to scaffold from `context.example/`; unattended, proceed with
   conservative defaults (every issue T2 minimum, WIP cap 3) and note it in the run
   report.

2. **Resolve stage deference.** Read `context/<project>/resolutions.md` for entries
   of the form `triage.<stage>`. Then scan the project's skills (`<root>/skills/`,
   `<root>/.claude/skills/`, `<root>/.agents/skills/`) for ones whose output covers a
   pipeline stage's job (verifying changes end-to-end, opening PRs, walking a PR to
   merge, reviewing a diff). For each overlapping stage without a recorded
   resolution: interactively, ask one AskUserQuestion per stage (use the project's
   skill (Recommended) / use the built-in stage / compose) and append the answer to
   `resolutions.md` as `- triage.<stage> → <choice> (<date>)`. Unattended, an
   unresolved overlapping stage means the affected issues are skipped with the
   conflict named in the run report. Never guess.

3. **Confirm Linear access.** Load the Linear MCP tools per the Linear access
   section. If only authentication stubs are available: interactively, offer to run
   the OAuth flow now; unattended, treat Linear as unavailable. When Linear is
   unavailable in an interactive run, stop and say so. In an unattended run, abort
   with a run report that still includes everything already discovered
   (missing-context defaults, unresolved stage overlaps).

4. If specific issue IDs were provided as arguments, take them as the eligible set and continue with Step 1. Skip only the list fetch (Step 1.1 fetches each provided ID's details directly) and the no-PR eligibility filter (an explicitly named issue is worked regardless). Type inference, prior-analysis synthesis, and tier assignment run for every issue, argument-provided or not. An issue is never dispatched without a tier.

5. Otherwise, list the user's issues, sorted by priority, through the Linear MCP
   tools.

---

### Step 1: Filter to Eligible Issues

1. From the issue list (or the IDs provided as arguments), get details for each through the Linear MCP tools (description, `updatedAt`, and comments). Skip issues that already have a branch name or PR URL in their metadata. Retain the full payload for eligible issues, because you'll use the description, `updatedAt`, and `comments` array in step 1.4.

2. Filter down to issues with no PR attached.

3. For each eligible issue, **infer the issue type** from its title, description, and labels:
   - **Feature**: new functionality, `add`, `implement`, `build`, `create`
   - **Bug**: `fix`, `broken`, `error`, `crash`, `regression`
   - **Refactor**: `refactor`, `restructure`, `clean up`, `migrate`
   - **Performance**: `slow`, `optimize`, `latency`, `performance`
   - **Chore**: `update`, `bump`, `docs`, `config`, small tasks

4. **Read comments and description for prior analysis.** Comments often contain ground truth that supersedes the description. For each eligible issue, scan the `comments` array (newest first) and the description together, then decide:

   - **Confirmed root cause in comments?** A teammate has named specific files, lines, or methods and stated the cause without hedging ("the bug is in X because Y", "root cause is Z at file:line"). → Diagnose can be skipped or compressed.
   - **Specific files/lines named?** → Understand can be narrowed to those paths instead of broad codebase exploration.
   - **Solution proposed?** → Design becomes validation of the proposal, not invention from scratch.
   - **Scope-narrowing notes?** ("no prod fix needed", "no broken state", "transcript-only", "system prompt change only") → Do NOT silently trim the pipeline. Surface to the user via AskUserQuestion (see step 1.7 below) before dispatching.
   - **Description edited after the latest comment?** If `issue.updatedAt` is newer than the newest non-bot `comments[].createdAt`, treat the description as already incorporating the thread, and read it as fresh ground truth.

   **Trust rules:**
   - Treat newer comments as superseding older comments and possibly the description.
   - Filter out bot/automation comments (Linear's auto-posts for branch/PR creation).
   - **Confirmed language** ("the cause is", "fixed by", "needs to") vs **hedged language** ("maybe", "I think", "could be", "might"): only confirmed-language findings count as ground truth. Hedged findings are hypotheses. They may narrow Understand, but they do NOT justify skipping Diagnose.
   - If two comments contradict each other and you can't tell which supersedes, do NOT skip stages. Raise the conflict with the user.

   Produce a short **prior-analysis synthesis** for each eligible issue with two lists:
   - **Pre-established (confirmed):** what comments have already nailed down (specific files and the root cause, or a proposed fix).
   - **Still to verify:** what remains uncertain, hedged, or unaddressed.

   Use this synthesis to set the pipeline (next step) and to brief every subagent (Step 3).

5. Present a table with suggested pipelines. When the prior-analysis synthesis (step 1.4) justifies a compressed pipeline, mark skipped/compressed phases inline with a brief reason in parentheses:
   ```
   | # | ID      | Title                    | Priority | Tier | Pipeline                                                       |
   |---|---------|--------------------------|----------|------|----------------------------------------------------------------|
   | 1 | ENG-123 | Add user export feature  | Urgent   | T1   | Understand → Design → Build → Verify                           |
   | 2 | ENG-456 | Fix billing calculation  | High     | T3   | Understand → Build → Verify → Review (Diagnose skipped: root cause confirmed in comments) |
   | 3 | ENG-789 | Update API docs          | Medium   | T0   | Build → Review                                                 |
   ```

   Assign each issue a **tier** from `context/<project>/risk-tiers.md` by matching
   the issue's likely surfaces to the tier lists. Unlisted or unknown surfaces
   are T2 minimum, and when the surfaces are in more than one tier the highest
   tier applies. Tier consequences:
   T3 issues are excluded from unattended runs and from auto-advance. Every stage
   gate waits for the user, and the status table marks them `requires you in the loop`. If
   work-in-flight reveals a T3 surface the ticket didn't (a deny-listed path shows
   up in the diff), raise the tier mid-run and drop that issue out of auto-advance;
   tiers only ever go up.

   The parenthetical reason is mandatory whenever the pipeline deviates from the type default. If multiple phases are affected (e.g., Understand narrowed AND Diagnose skipped), list the most consequential change.

   Default pipeline per type is listed below. Use your judgment, though: phases can be added, skipped, or reordered as the issue demands, and compressions justified by step 1.4 apply.
   - **Feature**: `Understand → Design → Build → Verify → Review`
   - **Bug**: `Understand → Diagnose → Build → Verify → Review`
   - **Refactor**: `Understand → Design → Build → Review`
   - **Performance**: `Understand → Design → Build → Verify`
   - **Chore**: `Build → Review`

6. If zero eligible issues remain, say so and stop.

7. Use AskUserQuestion: "Ready to start working on N issues in parallel?" with the options **Start all** / **Pick issues** / **Done**

   If **Pick issues**: ask which issue numbers to include.

   **Before dispatching**, if any issue's prior-analysis synthesis found scope-narrowing notes ("no prod fix needed", "transcript-only", "system prompt change only", or similar), confirm scope explicitly with the user for that issue. Do NOT auto-trim the pipeline based on these notes.

---

### Step 2: Dispatch Parallel Pipelines

For each selected issue:

1. **Record its pipeline state** (issue ID, title, current stage) in your working notes. The Step 4 status table is the user-facing view of that record.

2. **Dispatch the first pipeline stage** as a background agent (`run_in_background: true`).

**Dispatch all first-stage agents simultaneously** in one message with multiple Agent tool calls. Each issue's agents run independently. Dispatch at most the WIP cap (Step 0.1) of issues into active pipelines at once. Queue the rest and start the next queued issue whenever one finishes or is skipped.

---

### Step 3: Pipeline Stages

**Do NOT hardcode subagent types.** For each stage, examine the available `subagent_type` options in the Agent tool and choose the best match for the work described. If new agent types have been added, prefer them when they fit. If no specialized agent fits, use `general-purpose`.

Always pass these into every agent prompt:
- The full issue description from Linear
- All Linear comments on the issue (excluding bot/automation comments), newest first
- The prior-analysis synthesis from step 1.4, that is, what is **pre-established (confirmed)** vs **still to verify**
- Results from ALL prior stages for this issue
- Any user feedback from the previous stage

Subagents must treat the synthesis as authoritative for what's pre-established: don't re-derive root causes that comments have already confirmed, don't re-explore files when comments name specific paths. But they verify everything in the "still to verify" list.

The pipeline is a sequence of **work phases**, and the agent types are not fixed:

#### Phase: Understand
- **Goal:** map which parts of the codebase are relevant to this issue
- **Work:** find relevant files, models, services, schema, tests. Map domain relationships and key code paths. Report findings.
- **Agent selection:** pick the agent best suited for codebase exploration and research.

#### Phase: Diagnose (bugs and customer-reported issues)
- **Goal:** confirm the root cause with production data before building a fix
- **Work:** generate a read-only diagnostic script for the project's production console (flavor and access mode per `stack.md`, Rails console by default) for the user to run in production. The script must be read-only (no mutations). **Before writing any script, read the actual model files and schema to verify every method name, attribute, and association path you plan to use.** Never assume a model has the method without checking first. Present the script, wait for the user to paste output, then analyze. Iterate if needed. Only proceed to Build once the root cause is confirmed by production data.
- **Agent selection:** this phase is handled by the orchestrator (you), not a subagent. You generate the script directly.
- **When to use:** every bug or customer-reported issue. The Understand phase tells you *what the code does*; Diagnose tells you *what actually happened*, and the two differ more often than code review suggests. A root cause that looks obvious from the code still gets checked against production data. Use the identifiers in the ticket (record IDs, account slugs, thread links, environment) to target the exact scenario described. Skip for features, refactors, and chores with no production state to diagnose.
- **Diagnose moves into Build in two cases:** the ticket lacks identifiers or lacks any production state to query (a pure system-prompt gap, say), or the prior-analysis synthesis (step 1.4) marks the root cause as pre-established in confirmed, non-hedged language with no broken production state to repair. In both, the Build agent produces `tmp/diagnostic_<issue_id>.rb`, a read-only console script the user runs after deploy to re-validate the cause against production data. The cause is then verified by the run rather than assumed. Hedged, contradictory, or hypothetical comments do not qualify, and Diagnose runs in those cases.

#### Phase: Design
- **Goal:** create a build plan
- **Work:** given the codebase understanding, design a step-by-step plan that covers files to create/modify and architectural decisions as well as the testing strategy.
- **Agent selection:** pick the agent best suited for software architecture and planning.

#### Phase: Build
- **Isolation:** `worktree` (each issue gets its own isolated copy of the repo)
- **Goal:** write the code
- **Work:** write the code described in the plan. Write clean code following existing codebase patterns. Do NOT commit, just write the files.
- **Agent selection:** pick the agent best suited for writing production code. If the issue is primarily a refactor, prefer an agent specialized in simplification/refactoring if one exists.
- **Diagnostic scripts for bugs:** for a bug or customer-reported issue, the Build agent also produces `tmp/diagnostic_<issue_id>.rb`. This is a read-only Rails console script that targets the records and identifiers listed in the Linear issue. The user runs it in production to verify that the fix addresses the real issue. When Diagnose moved into Build, this script is the diagnosis.
- **Evidence bundle:** the Build agent's completion report must end with five short sections: `What changed`, `Why this shape`, `What you ran`, `Residual risk`, and `Rollback`. Verify and Review receive it, and the PR body's How-to-test section contains its verified commands.

#### Phase: Verify
- **Goal:** ensure the code works
- **Work:** write and run tests for the changes. Ensure adequate coverage. Run the test suite and fix any failures.
- **Agent selection:** pick the agent best suited for test automation and quality assurance.
- **Stage deference:** when Step 0.2 recorded a project skill for this stage, instruct the stage agent to run that skill (via the Skill tool) inside the worktree instead of improvising a test plan. Its output is passed to the pipeline exactly like the built-in stage's would be.

#### Phase: Review
- **Goal:** catch issues before PR
- **Work:** review all changes for code quality, security, correctness, adherence to codebase patterns, and missing edge cases.
- **Agent selection:** pick the agent best suited for code review. If the issue touches security-sensitive areas, also consider a security-focused agent.
- **Output requirement:** the Review must group findings by severity (`Blocking` / `Should fix` / `Suggestion`) and end with a verdict (`approve` / `approve with non-blocking comments` / `request changes` / `rework`). The auto-fix loop in Step 4.5 keys off these labels. Instruct the agent to use them explicitly.
- **Deterministic pre-checks (fail closed):** before the review agent runs, the orchestrator checks: (a) diff size within the project's norm (default: flag above ~500 changed lines or 20 files), (b) no deny-listed T3 surface touched (else raise the tier per Step 1.5 and pause auto-advance for the issue), (c) tests changed alongside behavior, or the Build report justifies why not. Failures become mandatory Review findings. The review agent may tighten these outcomes but never loosen them. Stage deference applies here too when recorded.

---

### Step 4: Orchestration Loop

This is the core loop. Repeat until all issues are complete or the user says Done.

1. **When any background agent completes:**

   a. **Update that issue's recorded stage** with the new status.

   b. **Show status table for ALL issues:**
      ```
      | ID      | Title                   | Stage      | Status     |
      |---------|-------------------------|------------|------------|
      | ENG-123 | Add user export feature | Implement  | Complete   |
      | ENG-456 | Fix billing calculation | Explore    | Running    |
      | ENG-789 | Update API docs         | —          | Queued     |
      ```

   c. **Show a concise summary** of what the completed agent found/did.

   d. **Ask for feedback** via AskUserQuestion:
      - **Continue**: advance to the next pipeline stage
      - **Feedback: [text]**, where the user provides specific input for the next stage
      - **Redo**: re-run the same stage with adjustments
      - **Skip this issue**: abandon this issue
      - **Done for now**: stop all work

2. **On Continue / Feedback:**
   dispatch the next pipeline stage in the background. Pass all prior stage results and any feedback into the prompt. If it was the last stage, proceed to Step 5.

3. **On Redo:**
   ask what to change, then re-dispatch the same stage with the adjustment.

4. **Auto-advance:** after the user has approved "Continue" for 3+ consecutive stages (across any issues), tell the user: "Auto-advancing remaining stages. Say 'pause' to review again." Then dispatch next stages without asking, but still show status updates after each completion. If the user says "pause", resume asking for feedback.

5. **Auto-fix loop on Review blockers.** When the Review phase returns with **blocking findings** (severity `Blocking`, or a verdict of `request changes` / `rework`), close the loop without asking the user, the same way a developer would re-run the test suite after a fix. Specifically:

   a. **Cap: 2 auto-fix iterations per issue**, total across the pipeline. Track the count in the issue's record. After the cap, surface to the user with: *"Auto-fix attempted N times for ENG-XXX. Remaining blockers: [list]."* and ask Continue / Redo / Skip / Done.

   b. **Construct a feedback message** from the Review's blocking findings: verbatim quotes of each blocker, with file:line references. Don't paraphrase, because the Build agent needs the specifics.

   c. **Re-dispatch Build** in the worktree (background) with the original issue context and all prior stage results, plus the Review's blocking findings as the feedback payload and an explicit instruction to address each blocker. Keep `isolation: "worktree"` on the same worktree path so the iteration builds on the existing state, not a fresh tree.

   d. **Re-dispatch Verify** when Build completes (background). Pass the blockers and the new Build output so Verify knows what to re-test.

   e. **Re-dispatch Review** when Verify completes (background). Pass the blockers and the new diff so Review can confirm they were addressed (or surface that they weren't).

   f. **Exit the auto-fix loop** when Review returns clean. Clean means the `Blocking` list is empty and the verdict is `approve` or `approve with non-blocking comments`. Then ask the user normally per the standard loop in 1.d.

   g. **Pause respects the user.** If the user has explicitly said "pause" (turning off auto-advance), do NOT auto-fix either. Ask normally, even on blockers. The auto-fix loop is part of forward motion, and pause means stop all forward motion.

   h. **Show the auto-fix in the status table.** Add a column or annotation when an iteration is in flight so the user sees it: e.g., `Build (auto-fix 1/2)`, `Review (auto-fix 1/2)`. Don't silently spin.

6. **Telemetry.** After every stage completion, skip, or finalization, append one
   JSON line to `~/.claude/telemetry/fleet.jsonl` (create the directory if needed):
   `{"ts":"<iso8601>","project":"<repo dir>","skill":"triage","issue":"<ID>","stage":"<stage>","tier":"<T0-T3>","outcome":"<complete|failed|skipped>","attempt":<n>}`.
   Logging is best-effort. A write failure never blocks the pipeline.

---

### Step 5: Finalize (Branch & Draft PR)

When all pipeline stages complete for an issue:

1. **Start the issue in Linear** (marks it as "In Progress" and yields the branch name): update the issue to its started state through the Linear MCP tools, then read the issue's branch name field and create that branch in the worktree (`git checkout -b <branch>`). If it conflicts with the worktree's existing branch, the Linear-provided branch name takes precedence.

2. **Commit and push** the worktree changes:
   ```bash
   cd <worktree_path>
   git add -A
   git commit -m "<concise summary of changes>"
   git push -u origin HEAD
   ```

3. **Create a draft PR** linked to the Linear issue:
   ```bash
   gh pr create --draft \
     --title "<descriptive title — no issue ID prefix>" \
     --body "<PR body — see format below>" \
     --head <branch_name>
   ```

   **PR body format.** The PR description must read like an investigation report. Synthesize outputs from ALL pipeline phases (Understand, Diagnose, Build, Review) into one standalone document. Someone reading the PR tomorrow should understand the problem, root cause, reasoning, and solution without any other context. **Do NOT include the Linear issue ID anywhere in the PR body.** That rules out `**Issue:** ENG-123 —` prefixes and "Resolves ENG-123" footers. Linear links the PR automatically via the issue-ID-bearing branch name.

   **IMPORTANT (shell escaping):** use a single-quoted HEREDOC delimiter (`<<'EOF'`) so that backticks and dollar signs pass through literally, as do other special characters. Do NOT escape backticks with backslashes. Inside `<<'EOF'`, backticks are plain text and render as inline code on GitHub. Never use double-quoted HEREDOC (`<<EOF`) or bare strings for PR bodies.

   ```bash
   gh pr create --draft --title "..." --body "$(cat <<'EOF'
   ## Context

   <Problem statement from the Linear issue: what was observed vs expected.
   Include the affected records, environment, and reproduction steps if available from the ticket.>

   ## Investigation

   <Root cause from the Understand phase: what was found in the code.
   Key files examined, data model relationships, the specific gap or bug identified.
   If Diagnose ran: what production data confirmed.>

   ## Approach

   <What was changed and why this approach was chosen.
   For each file modified, explain the reasoning — not just what was done but why.
   If alternatives were considered, briefly note why they were rejected.>

   ## Files changed

   <Bulleted list of modified files with one-line descriptions>

   ## How to test

   <Test commands (project test suite, targeted specs)>
   <Manual verification steps>
   <Diagnostic script if applicable>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

4. **Mark the issue's record completed.**

5. Show confirmation:
   ```
   ENG-123: Draft PR created → <PR URL>
   ```

---

### Step 6: Summary

When all issues are processed or the user says Done, show a final table:

```
| ID      | Title                   | Result     | PR                          |
|---------|-------------------------|------------|-----------------------------|
| ENG-123 | Add user export feature | PR created | github.com/org/repo/pull/42 |
| ENG-456 | Fix billing calculation | Skipped    | —                           |
| ENG-789 | Update API docs         | PR created | github.com/org/repo/pull/43 |
```

---

## Unattended mode

`/work-triage --unattended` is the scheduled/headless form. Differences from the
interactive flow, all non-negotiable:

- **Never asks.** No AskUserQuestion anywhere. Anything that would have been a
  question becomes either a skip or a run-report item.
- **Skips instead of guessing.** An issue is skipped (with the reason recorded)
  when it: is tier T3; carries scope-narrowing notes or contradictory comments
  (step 1.4); needs a stage whose project-skill overlap has no recorded resolution;
  or requires production diagnostics that only a human can run.
- **Auto-advance from the start**, auto-fix loop unchanged (cap 2).
- **Ends with a run report:** issues dispatched with stages completed and PR links,
  issues skipped with reasons, telemetry summary, and any conflicts left for an
  interactive session.

## Key Rules

1. **Choose agents at run time.** Examine available `subagent_type` options for each phase and pick the best fit. Never assume a fixed mapping, because new agent types may be added at any time.
2. **One subagent per issue at a time.** Pipeline phases are sequential within an issue. Never run Design and Build simultaneously for the same issue.
3. **Multiple issues in parallel.** Different issues can have agents running in parallel. Use `run_in_background: true` for all agent dispatches.
4. **Worktree isolation for Build.** The Build phase uses `isolation: "worktree"` so parallel issues don't conflict with each other.
5. **Always show status.** After every agent completion, show the status table for ALL issues rather than just the one that completed.
6. **User feedback between phases.** Always ask unless auto-advance is active (3+ consecutive approvals).
7. **Draft PRs only.** Never create ready-for-review PRs. Always use `--draft`.
8. **Pass context forward.** Each phase receives all prior phase outputs. Don't make agents re-discover what earlier agents already found.
9. **Comments are evidence rather than authority.** Linear comments often pre-establish root causes, files, and fixes. Read them before suggesting a pipeline (step 1.4). But only confirmed-language findings justify skipping or compressing phases. Hedged claims, contradictory comments, and outdated descriptions are hypotheses to verify, not facts to skip past.
10. **Handle failures gracefully.** If an agent fails or produces bad results, show the error and ask, offering **Retry** / **Skip** / **Done**.
11. **Auto-fix Review blockers, capped at 2 iterations.** Forward motion shouldn't pause for the user to copy-paste a Review's blockers back into Build's prompt. That's a loop the orchestrator can close. After 2 attempts without convergence, hand the decision to the user and never spin indefinitely. Pause overrides auto-fix.
12. **Clean up on Done.** When the user stops early, list any worktrees with uncommitted changes and ask if they should be cleaned up.
13. **Handle tracker errors gracefully.** If a Linear MCP call fails or needs disambiguation (team, project, filter), surface it and ask rather than guessing; unattended, skip the affected issues and record the reason in the run report.
14. **Project skills run the stages assigned to them.** A recorded `triage.<stage>`
    resolution routes that stage through the project's skill. In unattended mode an
    unresolved overlap skips the issue rather than guessing.
15. **Tiers govern autonomy.** T3 is excluded from unattended runs and from auto-advance.
    Surfaces that are discovered mid-run only raise the tier, never lower it.
16. **Telemetry is best-effort.** Never block or fail a pipeline over a logging
    error.
17. **Unattended never asks.** Skip and report instead, because a skipped issue is
    recoverable and a wrong guess in someone's repo is not.
