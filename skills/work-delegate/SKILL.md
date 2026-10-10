---
name: work-delegate
version: 1.0.0
description: |
  Hand a task to another executor, and pick up what comes back. Reads the
  project's delegation.md to choose between a local subagent, codex exec, and
  the project's cloud agents, writes a self-contained brief per brief-guide.md,
  and dispatches it. `check` lists the delegated work, reviews each new PR in a
  local worktree, and posts one signed comment with the findings.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - Skill
  - AskUserQuestion
---

# Delegate

Some work doesn't need my session. A cloud agent or a local subagent can build
it from a good brief while I do something else, and I review what comes back.
Which executors a project has, and how to reach them, is configuration, so it
lives in `context/<project>/delegation.md`. This skill reads it and never
assumes a tracker or a vendor.

I own every delegate's work. Pickup reviews the PR as carefully as my own work,
and a delegate's report never replaces that review.

## Arguments

- `/work-delegate <task | issue id | plan file>`: write the brief and dispatch it.
- `/work-delegate check`: pick up the delegated work that came back (see **Pickup**).
- Steers in plain words. `dry run` or `--review` stops after the brief and the choice of executor, before dispatch.

## Cases for another skill

- A queue of tracker issues to build in parallel → `/work-triage`, which hands its Build stage here when a cloud executor fits.
- Building it myself, now → `/code-build`.
- A prompt to paste into another tool by hand → the `/prompt` command.

## Instructions

Follow these steps in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm").

### Step 0: Read the project's delegation setup

Read `~/.claude/context/<project>/delegation.md` and `escalation.md` (`<project>` is the repo's directory name). When `delegation.md` is missing, the only executor is a local subagent. Offer once to scaffold the file from `~/.claude/context.example/delegation.md`.

### Step 1: Check for a hold

When the task depends on work that hasn't merged, such as another PR or issue, don't dispatch it. Write the brief with its Hold section, and leave it where `delegation.md` keeps held work. Report the hold and stop.

### Step 2: Pick the executor

- **The work needs skills that exist only in `~/.claude`.** Run it as a local Claude subagent in a worktree. Cloud agents and `codex exec` can't load those skills.
- **The repo's own skills or plain instructions cover it.** Use the cloud executor when `delegation.md` lists one, else `codex exec` when listed, else a local subagent.

Say which executor you picked and why, in one line.

### Step 3: Write the brief

Write it per `~/.claude/skills/work-delegate/brief-guide.md`. Add the project-specific rules from `delegation.md`. For a tracker-based executor, the brief is the issue description.

### Step 4: Dispatch

Follow the dispatch recipe in `delegation.md` for the executor:

- **A cloud executor through a tracker.** Create or update the issue as the recipe says. Creating an issue is outward, so it goes ahead only when `escalation.md` allows it. Otherwise show the brief and ask.
- **`codex exec`.** Create a worktree with `git worktree add <path> -b <branch>`, then run `codex exec -C <path> "<brief>"` in the background.
- **A local subagent.** Use the Agent tool with `isolation: "worktree"` and `run_in_background: true`, and the brief as its prompt.

When a `/work-log` is open for this run, log the dispatch.

### Step 5: Report

- **Dispatched**: the executor and where its work is, such as an issue URL or a worktree path.
- **Coming back**: how the result returns per `delegation.md`. `/work-delegate check` collects it.
- **Check**: anything the brief had to guess at, such as a fact you couldn't verify on the base branch.
- **Undo**: clear an issue's delegate or cancel the issue, which is outward. For a local executor, run `git worktree remove <path>` and `git branch -D <branch>`.

## Pickup

`/work-delegate check` collects what the executors sent back.

1. **List the delegated work** the way `delegation.md` says, such as the issues assigned to me and delegated to the cloud agent. For local executors, list the worktrees this skill created.
2. **For each PR without a review from me since its last push:**
   - Check it out in a worktree, named as `delegation.md` says.
   - Run `/pr-critique` through the `reviewer` agent, and `/test-prune` and `/code-unguard` in report mode. Run the private checks in `~/.claude/context/<project>/checks/`, and the project's verify skill when it has one (the repo's own, or `~/.claude/context/<project>/verify/SKILL.md`).
   - Post one comment on the PR with the findings. A PR from my delegated issue is my own thread. The comment goes ahead without asking, signed per `~/.claude/AGENTS.md`.
   - Collect what the executor asked me to decide, such as its "Decisions for you" comments.
   - Hand the PR to the project's babysit skill when it has one, per the project-skill rules in `~/.claude/AGENTS.md`.
3. **Report** one row per item, with the issue and its PR, the findings count, the decisions waiting for me, and the next step. Then ask the decisions together.

## Key Rules

1. **The executor comes from `delegation.md`.** This skill works with any tracker or vendor that file describes.
2. **Work that needs `~/.claude` skills runs locally.** No other executor can load them.
3. **Held work is never dispatched.**
4. **Every brief follows `brief-guide.md`,** with the armor rule and the stop rule.
5. **I own the delegate's work.** Pickup reviews every PR before anything else happens to it.
