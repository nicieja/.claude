---
name: work-create-loop
version: 1.0.0
description: |
  Create a restartable loop routine for a campaign of many items that runs over
  days, one wake at a time. Frames the campaign with me, counts where past
  items of the same kind stalled, and turns the counts into the loop's rules.
  Writes the routine with its ledger and status script into
  ~/.claude/context/<project>/, in the format of
  context.example/routines/README.md, plus the loop's escalation subsection.
  The routine runs the shared lock.py and watch.py. A fresh subagent then
  proves the loop restarts cold in its read-only mode. Never starts the loop.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Create a loop

Some work takes days and more items than one session holds, such as a stack of PRs from a cloud agent or a goal list to close. A loop works through it one wake at a time, and a restart picks up where the last wake stopped. The first loop took about four days by hand. Most of that went into the design: what past items of the same kind got stuck on, and which actions the loop may take without me. This skill does that design with me, then writes the files and proves the loop restarts cold.

## Arguments

- `/work-create-loop <name>`: create the loop `<name>` for the current repo's project.
- `/work-create-loop <name> <plan path>`: start from a plan that `/idea-spec` or I wrote. The questions cover only what it leaves open.
- `--review` or "show me first" stops after the design in Step 3, before any file is written.

## Cases for another skill

- A prompt on a timer, with no items to track → a routine with a cron schedule line, which `/setup` arms.
- A few of my own PRs to bring to ready-to-merge → `/pr-babysit`.
- Tracker issues to dispatch once → `/work-triage`.
- An existing loop to restart → `/setup`, which prints its start command.
- An existing routine gone patchy → `/self-heal context <project>`.
- A campaign whose goal is still open → `/idea-spec` first, then this skill with its plan.

## Instructions

Follow these steps in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm"). The files this skill writes are private and new, so it writes them, then reports. An existing routine stays as it is, and a loop starts only when I start it.

### Step 0: Find the project

`<project>` is the directory name of the main checkout, the first entry in `git worktree list`. Read the routine format in `~/.claude/context.example/routines/README.md`, and the status-line contract in the docstring of `~/.claude/skills/work-create-loop/watch.py`. Then read `decisions.md`, `delegation.md`, `escalation.md`, `rules.md` and `stack.md` in `~/.claude/context/<project>/`.

When `~/.claude/context/<project>/` or its `escalation.md` is missing, offer `/work-bootstrap` once and stop. When `routines/<name>.md` exists, stop, and name `/self-heal context <project>` for a routine that needs work.

### Step 1: Frame the campaign

Fill in what the conversation or the plan already answers. Ask the rest in AskUserQuestion rounds of at most four questions, each with the drafted answer as the recommended option. In a tool without AskUserQuestion, ask the same questions as plain text.

- **The item.** What one item is, such as a PR, an issue, or a row of a goal list.
- **The sources.** The shell-pollable source that the routine's `status` script reads, such as the code host. Items with no shell state yet, such as an issue nobody has started, come from a source each wake reads another way, through MCP or a subagent.
- **The executor.** Who works each item. It's this session or its subagents, or an executor listed in `delegation.md`. When it's another agent and `delegation.md` is missing, offer `/work-bootstrap` once and stop.
- **The done condition.** A check over the whole campaign that passes or fails.
- **The brief.** When another agent works the items, whether the loop shares the brief template `delegation.md` points to or gets its own. `delegation.md` points to one template, the only copy of the brief rules.
- **The outward actions.** Always asked, never inferred. Draft the list from what the steps will need, and mark what stays mine. Merges always do.

### Step 2: Measure the history

Send a read-only subagent to pull the last 10 to 20 finished items of this kind from the Step 1 sources and return one table. Each row says who finished the item (the executor alone, or a takeover) and each reason it stalled, such as a CI rerun, a base that moved, a late review, or a decision that waited on me. Under the table come the items that ended unfinished, with the reason, and each recurring kind of finding with its count. Without subagents, do the read yourself, and say so.

The counts become the routine's step rules and the brief's first rules. A rule without a count ends with the marker `(guess)`. With no history, say so, and start the cap at 2.

### Step 3: Design the wake

Show the design in chat. It covers only the choices this loop makes, because the template fixes the rest:

- the states, a fixed list with one state per item, and the first-match rule for each
- the fields of the status line
- the ledger's own sections, beyond the template's two
- the escalation subsection, with the outward actions from Step 1
- the cap and the wake interval

`--review` stops here.

### Step 4: Write the files

First run `git -C ~/.claude/context status --porcelain` on `escalation.md`, `decisions.md` and `delegation.md`. A running loop may have uncommitted edits there. When one is dirty, stop before writing anything, and report the file and its change.

Then write, under `~/.claude/context/<project>/`:

- `routines/<name>.md`, in the template's sections, starting with the loop schedule line.
- `routines/<name>/ledger.md`, in the template's ledger format, plus the sections from Step 3.
- `routines/<name>/status`, per the contract in `watch.py`, and `chmod +x` it. It follows the armor rule in AGENTS.md.
- `routines/<name>/brief.md`, only when Step 1 gave the loop its own brief, per `~/.claude/skills/work-delegate/brief-guide.md`. Point `delegation.md` to it.
- The loop's subsection in `escalation.md`, in the format of `~/.claude/context.example/escalation.md`.
- An entry in `decisions.md` for each Step 1 answer that binds the loop, in that file's format. A proposal I didn't answer, such as the cap, stays in the routine.

### Step 5: Prove a cold restart

Run `status`, and check two of its lines against their source by hand. Then send a fresh subagent only this brief: "Follow `~/.claude/context/<project>/routines/<name>.md` in its `reconcile only` mode, and return the status table." Compare its table with your two checks. A difference is a bug in the routine or in `status`. Fix it, and run this step again. Without subagents, run reconcile only yourself, and say the restart wasn't cold.

### Step 6: Commit

```bash
git -C ~/.claude/context add -- <paths>
git -C ~/.claude/context commit -m '<what, and why>' -- <paths>
```

The context repo's pre-commit hook runs `bin/check --context`, and a failure says the fix.

### Step 7: Report

- **Changed**: each file written or edited.
- **Proof**: the subagent's status table, and the two lines checked by hand.
- **Start**: `/loop follow ~/.claude/context/<project>/routines/<name>.md`, and its `reconcile only` form. The loop needs Claude Code, because it wakes through `Monitor` and `ScheduleWakeup`.
- **Check**: the outward actions in the escalation subsection, word for word. Then the done condition, the cap, and each rule marked `(guess)`.
- **Undo**: `git -C ~/.claude/context revert <sha>`.

Then ask my open calls together, such as a failure policy the history didn't settle.

## Key Rules

1. **The template is the format, and `watch.py` holds the status-line contract.** Read both on every run, and don't restate them.
2. **Never overwrite a routine, and never start a loop.**
3. **Rules come from counted history.** A rule without a count is marked `(guess)`.
4. **I grant every outward permission.** Step 1 asks for the list, and the report quotes it.
5. **Everything this skill writes is private,** under `~/.claude/context/<project>/`.
