---
name: triage
version: 1.0.0
description: |
  Fetch Linear issues with no PR attached, orchestrate parallel subagents
  through staged pipelines (explore → plan → implement → test → review),
  collect user feedback between stages, and push draft PRs when complete.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# /triage — Linear Issue Orchestrator

Fetch issues assigned to you in Linear that have no PR attached, dispatch specialized subagents to work on each in parallel, and push draft PRs when done.

## Arguments
- `/triage` — fetch and work on all eligible issues
- `/triage ENG-123` — work on a single specific issue
- `/triage ENG-123 ENG-456` — work on specific issues

## External tool

Uses the `linear` CLI (https://github.com/schpet/linear-cli). Do NOT use `./linear.toml` — rely on global config or env vars.

Key commands:
- `linear issue list --sort priority --no-pager` — user's unstarted issues
- `linear issue view <ID> --json --no-pager` — full issue details as JSON
- `linear issue view <ID> --no-pager` — issue details as text
- `linear issue start <ID>` — mark as started (also creates branch)
- `linear issue pr <ID> --draft --head <branch>` — create draft PR linked to issue

## Instructions

Follow these steps in order. Do NOT skip steps.

---

### Step 0: Preflight

1. Verify the `linear` CLI is installed:
   ```bash
   which linear
   ```
   If not found, tell the user to install it and stop.

2. If specific issue IDs were provided as arguments, skip to Step 2 with those issues.

3. Otherwise, fetch issues:
   ```bash
   linear issue list --sort priority --no-pager
   ```

4. If the command fails with a team error, run `linear team list` and use AskUserQuestion to ask the user which team. Retry with `--team <key>`.

---

### Step 1: Filter to Eligible Issues

1. From the issue list, get JSON details for each to check for existing PRs/branches:
   ```bash
   linear issue view <ID> --json --no-pager
   ```
   Parse the JSON. Skip issues that already have a branch name or PR URL in their metadata.

2. Filter down to issues with no PR attached.

3. For each eligible issue, **infer the issue type** from its title, description, and labels:
   - **Feature** — new functionality, "add", "implement", "build", "create"
   - **Bug** — "fix", "broken", "error", "crash", "regression"
   - **Refactor** — "refactor", "restructure", "clean up", "migrate"
   - **Performance** — "slow", "optimize", "latency", "performance"
   - **Chore** — "update", "bump", "docs", "config", small tasks

4. Present a table with suggested pipelines:
   ```
   | # | ID      | Title                    | Priority | Pipeline                                  |
   |---|---------|--------------------------|----------|-------------------------------------------|
   | 1 | ENG-123 | Add user export feature  | Urgent   | Understand → Design → Build → Verify      |
   | 2 | ENG-456 | Fix billing calculation  | High     | Understand → Build → Verify → Review      |
   | 3 | ENG-789 | Update API docs          | Medium   | Build → Review                            |
   ```

   Default pipeline per type (but use your judgment — add/skip/reorder phases as the issue demands):
   - **Feature**: Understand → Design → Build → Verify → Review
   - **Bug**: Understand → Diagnose → Build → Verify → Review
   - **Refactor**: Understand → Design → Build → Review
   - **Performance**: Understand → Design → Build → Verify
   - **Chore**: Build → Review

5. If zero eligible issues remain, say so and stop.

6. Use AskUserQuestion: "Ready to start working on N issues in parallel?" — **Start all** / **Pick issues** / **Done**

   If **Pick issues**: ask which issue numbers to include.

---

### Step 2: Dispatch Parallel Pipelines

For each selected issue:

1. **Create a task** (TaskCreate) to track its pipeline state. Include issue ID, title, and current stage.

2. **Dispatch the first pipeline stage** as a background agent (`run_in_background: true`).

**Dispatch all first-stage agents simultaneously** in a single message with multiple Agent tool calls. Each issue's agents run independently.

---

### Step 3: Pipeline Stages

**Do NOT hardcode subagent types.** For each stage, examine the available `subagent_type` options in the Agent tool and choose the best match for the work described. If new agent types have been added, prefer them when they fit. If no specialized agent fits, use `general-purpose`.

Always pass these into every agent prompt:
- The full issue description from Linear
- Results from ALL prior stages for this issue
- Any user feedback from the previous stage

The pipeline is a sequence of **work phases**, not a fixed list of agent types:

#### Phase: Understand
- **Goal:** Map which parts of the codebase are relevant to this issue
- **Work:** Find relevant files, models, services, schema, tests. Map domain relationships and key code paths. Report findings.
- **Agent selection:** Pick the agent best suited for codebase exploration and research.

#### Phase: Diagnose (bugs and customer-reported issues)
- **Goal:** Confirm the root cause with production data before building a fix
- **Work:** Generate a Rails console diagnostic script for the user to run in production. The script must be read-only (no mutations). **Before writing any script, read the actual model files and schema to verify every method name, attribute, and association path you plan to use.** Never assume a model has a given method — check first. Present the script, wait for the user to paste output, then analyze. Iterate if needed. Only proceed to Build once the root cause is confirmed by production data.
- **Agent selection:** This phase is handled by the orchestrator (you), not a subagent. You generate the script directly.
- **When to use:** For any bug or customer-reported issue. Skip for features, refactors, and chores where there's no production state to diagnose.
- **IMPORTANT — do NOT skip Diagnose for bugs.** Even when the root cause seems obvious from code review, production data often reveals that the actual behavior differs from what the code suggests. If the Linear issue includes identifiers (workspace, worker IDs, thread links, environment), use them to write targeted diagnostic scripts that verify the exact scenario described. The Understand phase tells you *what the code does*; Diagnose tells you *what actually happened*.
- **When Diagnose is impractical:** If the issue is purely a system prompt gap (no production state to query), or if no identifiers are provided in the ticket, fold diagnostic script generation into the Build phase instead — the Build agent must include a `diagnostic_script.rb` file alongside the fix that the user can run post-deploy to verify the fix works.

#### Phase: Design
- **Goal:** Create an implementation plan
- **Work:** Given the codebase understanding, design a step-by-step plan: files to create/modify, architectural decisions, testing strategy.
- **Agent selection:** Pick the agent best suited for software architecture and planning.

#### Phase: Build
- **Isolation:** `worktree` (REQUIRED — each issue gets its own isolated copy of the repo)
- **Goal:** Write the code
- **Work:** Implement the plan. Write clean code following existing codebase patterns. Do NOT commit — just write the files.
- **Agent selection:** Pick the agent best suited for writing production code. If the issue is primarily a refactor, prefer an agent specialized in simplification/refactoring if one exists.
- **Diagnostic scripts for bugs:** When building a fix for a bug or customer-reported issue, the Build agent MUST also produce a `tmp/diagnostic_<issue_id>.rb` file — a read-only Rails console script the user can run in production to verify the fix addresses the real issue. The script should target the specific workspace/worker/thread mentioned in the Linear issue. If Diagnose was skipped, this script is mandatory.

#### Phase: Verify
- **Goal:** Ensure the implementation works
- **Work:** Write and run tests for the changes. Ensure adequate coverage. Run the test suite and fix any failures.
- **Agent selection:** Pick the agent best suited for test automation and quality assurance.

#### Phase: Review
- **Goal:** Catch issues before PR
- **Work:** Review all changes for code quality, security, correctness, adherence to codebase patterns, and missing edge cases.
- **Agent selection:** Pick the agent best suited for code review. If the issue touches security-sensitive areas, also consider a security-focused agent.

---

### Step 4: Orchestration Loop

This is the core loop. Repeat until all issues are complete or the user says Done.

1. **When any background agent completes:**

   a. **Update the task** (TaskUpdate) for that issue with the new stage status.

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
      - **Continue** — advance to the next pipeline stage
      - **Feedback: [text]** — user provides specific input for the next stage
      - **Redo** — re-run the same stage with adjustments
      - **Skip this issue** — abandon this issue
      - **Done for now** — stop all work

2. **On Continue / Feedback:**
   Dispatch the next pipeline stage in the background. Pass all prior stage results and any feedback into the prompt. If it was the last stage, proceed to Step 5.

3. **On Redo:**
   Ask what to change, then re-dispatch the same stage with the adjustment.

4. **Auto-advance:** After the user has approved "Continue" for 3+ consecutive stages (across any issues), tell the user: "Auto-advancing remaining stages. Say 'pause' to review again." Then dispatch next stages without asking, but still show status updates after each completion. If the user says "pause", resume asking for feedback.

---

### Step 5: Finalize — Branch & Draft PR

When all pipeline stages complete for an issue:

1. **Start the issue in Linear** (marks it as "In Progress" and gets the branch name):
   ```bash
   linear issue start <ID>
   ```
   This outputs the branch name Linear expects. If it creates a new branch that conflicts with the worktree branch, use the Linear-provided branch name.

2. **Commit and push** the worktree changes:
   ```bash
   cd <worktree_path>
   git add -A
   git commit -m "<concise summary of changes>"
   git push -u origin HEAD
   ```

3. **Create a draft PR** linked to the Linear issue:
   ```bash
   linear issue pr <ID> --draft --head <branch_name>
   ```

   If `linear issue pr` fails, fall back to `gh`:
   ```bash
   gh pr create --draft \
     --title "<descriptive title — no issue ID prefix>" \
     --body "<PR body — see format below>" \
     --head <branch_name>
   ```

   **PR body format — the PR description must read like an investigation report.** Synthesize outputs from ALL pipeline phases (Understand, Diagnose, Build, Review) into a single standalone document. Someone reading the PR tomorrow should understand the problem, root cause, reasoning, and solution without any other context. **Do NOT include the Linear issue ID anywhere in the PR body** — no "**Issue:** ENG-123 —" prefixes, no "Resolves ENG-123" footers. The `linear issue pr` command handles the linking automatically.

   **IMPORTANT — shell escaping:** Use a single-quoted HEREDOC delimiter (`<<'EOF'`) so that backticks, dollar signs, and special characters pass through literally. Do NOT escape backticks with backslashes — inside `<<'EOF'`, backticks are plain text and render as inline code on GitHub. Never use double-quoted HEREDOC (`<<EOF`) or bare strings for PR bodies.

   ```bash
   gh pr create --draft --title "..." --body "$(cat <<'EOF'
   ## Context

   <Problem statement from the Linear issue: what was observed vs expected.
   Include workspace, environment, and reproduction steps if available from the ticket.>

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

   <Test commands (agent eval, unit tests)>
   <Manual verification steps>
   <Diagnostic script if applicable>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

4. **Update the task** as completed (TaskUpdate).

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

## Key Rules

1. **Choose agents dynamically.** Examine available `subagent_type` options for each phase and pick the best fit. Never assume a fixed mapping — new agent types may be added at any time.
2. **One subagent per issue at a time.** Pipeline phases are sequential within an issue. Never run Design and Build simultaneously for the same issue.
3. **Multiple issues in parallel.** Different issues can have agents running at the same time. Use `run_in_background: true` for all agent dispatches.
4. **Worktree isolation for Build.** The Build phase MUST use `isolation: "worktree"` so parallel issues don't conflict with each other.
5. **Always show status.** After every agent completion, show the status table for ALL issues — not just the one that completed.
6. **User feedback between phases.** Always ask unless auto-advance is active (3+ consecutive approvals).
7. **Draft PRs only.** Never create ready-for-review PRs. Always use `--draft`.
8. **Pass context forward.** Each phase receives all prior phase outputs. Don't make agents re-discover what earlier agents already found.
9. **Handle failures gracefully.** If an agent fails or produces bad results, show the error and ask: Retry / Skip / Done.
10. **Clean up on Done.** When the user stops early, list any worktrees with uncommitted changes and ask if they should be cleaned up.
11. **Handle team context gracefully.** If `linear issue list` fails with a team error, prompt for the team and retry.
