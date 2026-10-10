---
name: test-verify
version: 1.0.0
description: |
  Give a project a scripted way to prove its behavior: a private verify skill
  that launches the app, drives a feature the way a user would, and captures
  evidence, plus a feature map of what each feature does and how a user reaches
  it. Writes it to context/<project>/verify/ and proves it end to end once.
  `maintain` compares the map with the source, then runs every feature live.
  When the repo already has a verify skill, that one owns verification.
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

# Verify skill

"It compiles" and "the tests pass" don't prove a feature works. An agent that
can run the app and use the feature the way a user does can check its own work,
which makes it safe to leave alone. This skill
writes that ability for one project, as a private skill other skills read, and
updates it as the app changes.

The skill it writes is private by default, in `~/.claude/context/<project>/verify/`.
Only my local agents can see it there. Moving it into the repo, where cloud
agents and teammates can use it, happens only when I ask.

## Arguments

- `/test-verify` (bare): create the verify skill for the current repo, or report that one exists.
- `/test-verify maintain`: check an existing private verify skill against the app (see **Maintain**).
- `/test-verify promote`: copy the private skill into the repo's skills directory on a new branch. Only on my explicit ask.

## Cases for another skill

- Deciding what to test, or writing tests → `/test-design`.
- One question about a design, settled by a throwaway build → `/idea-prototype`.
- A claim about production data → `/production-query`.

## Instructions

Follow these steps in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm").

### Step 0: Check for an existing verify skill

Look in the repo's `skills/`, `.claude/skills/`, `.agents/skills/`, and `.cursor/skills/`, and in `~/.claude/context/<project>/verify/`. A skill counts as a verify skill when its instructions launch and drive the app, then capture evidence, whatever it's called. A skill named `verify-commitment` that checks a business commitment isn't one.

- **The repo has one.** It owns verification here. Say so and stop. Never edit it.
- **A private one exists.** Offer `/test-verify maintain` and stop.
- **Neither.** Continue.

### Step 1: Read the repo

Answer these from the code, and ask me only what the repo can't show:

- **Surface.** The part a user touches, such as a web UI or a CLI. Pick the main one, and list the others.
- **Run.** How the app starts locally, from the repo's own dev command, README, or Makefile, with its ports, environment, seed data, and auth.
- **Drive.** The way an agent uses it. Prefer an existing harness, such as Playwright specs or request specs. Otherwise write a plain recipe, such as the browser tools for a web UI or a shell for a CLI.
- **Observe.** What evidence a run can keep, such as screenshots, output, response bodies, logs, exit codes, files written, or rows changed.
- **Isolate.** Whether two runs can share the machine. When they can't, the skill says so, because driving someone's live instance corrupts it.

When the checkout doesn't run as it is, fix that or report it exactly before writing anything. A skill written against a broken base records wrong steps.

### Step 2: Write the skill

Write `~/.claude/context/<project>/verify/SKILL.md` for an agent that has never seen the app and reads it mid-task. Fill every section from Step 1, with no placeholders left:

- **Launch**: the exact command and the sign that the app is ready, plus how to stop it. A short-lived CLI has no server, so its launch is the build, and each drive runs on its own.
- **Doctor**: one read-only check that the instance is fit to drive, such as the process being up with the right build and valid auth. Run it first, and again after anything surprising.
- **Drive**: the recipe, with real selectors, commands, and routes from this repo. Prefer stable handles (labels, data attributes, route paths) over positions.
- **Evidence**: what to capture and where, under `~/.cache/agent-evidence/<project>/`. Capture the action and the state it produced, check side effects such as files or rows next to what's visible, and use the real path a user takes, never a test-only shortcut.
- **Cleanup**: how to stop what the run started. Stop only what this run started, and never delete the evidence.
- **Helpers**: each script that comes with the skill. Make it executable, and show its invocation in the skill.

### Step 3: Seed the feature map

Write `verify/features/README.md` as an index, plus one file for each of the three to five main features you found, from the routes, commands, menus, or docs. Each feature file has four sections, which are **Sub-features**, **How to get to it** (as a user), **Driving it**, and **Gotchas**. A proof that drives one entry point is incomplete when the map lists others.

### Step 4: Prove it once

Follow the new skill's own instructions end to end: launch, doctor, drive one mapped feature, capture its evidence, and clean up. Then confirm the evidence is still at its path after cleanup. Fix what failed, and clean up after every failed attempt too. A verify skill that never ran is a draft.

### Step 5: Report

- **Changed**: the files written under `~/.claude/context/<project>/verify/`.
- **Proof**: the feature driven and its evidence path, marked as measured.
- **Check**: the features in the map that weren't driven yet, and any step you had to guess at.
- **Undo**: `rm -r ~/.claude/context/<project>/verify`.

## Maintain

`/test-verify maintain` keeps the private skill true to the app. It edits only `~/.claude/context/<project>/verify/`, never the product code.

1. **Index.** Fix missing, extra, or dead entries in `features/README.md`.
2. **Source pass.** Dispatch one read-only `Explore` agent per feature file, in parallel. Each explains how the feature works from the source and cites the drift it finds. It also returns one recipe to verify the feature live.
3. **Reconcile.** Merge the recipes, and spot-check the cited drift. Look at recent changes for a user-facing feature the map lacks, and add it only with a source path behind it.
4. **Live pass.** Drive every feature at least once, following the skill's own Launch section. Run the doctor before the first drive and after any failed one. Keep the evidence through every cleanup, and stop whatever a drive started.
5. **Triage.**
   - A description that's wrong is map drift, and you fix it.
   - Behavior the harness can't drive is a harness gap, and you fix it.
   - App behavior that's broken is a product bug. Report it, and keep it out of the map.
6. **Outcome.** End with clean (nothing to fix), changed (the corrections made, each proven live), or blocked (what stopped the pass), plus Check and Undo for any change.

## Promote

`/test-verify promote` runs only when I ask for it. Copy the private skill into the repo's skills directory on a new branch, fix its paths, and open a draft PR only with my OK per `~/.claude/AGENTS.md`. From then on, the repo's copy owns verification, and Step 0 stops on it.

## Key Rules

1. **The repo's own verify skill wins.** Detect it by what it does, never edit it, and stop.
2. **Private until I say otherwise.** The skill is stored in `~/.claude/context/<project>/verify/`.
3. **A verify skill isn't done until it ran.** Step 4 proves it end to end.
4. **Cleanup keeps the evidence.** It removes what a run started, never the proof.
5. **Maintain edits only the verify skill.** A broken feature is a product bug to report.
