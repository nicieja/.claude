---
name: idea-prototype
version: 1.0.0
description: |
  Settle one design or behavior question by building something throwaway and
  watching it run. Scopes the decision first, builds
  two or three variants in a scratch directory or worktree behind one switcher,
  observes them where a user would see them, and reports the evidence with a
  recommendation. The prototype is never merged, and the chosen direction goes
  to /code-build.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Prototype

Some questions look like the user's call but are facts you can observe. Whether a
layout reads well at real density is one of them. Build the smallest thing that
shows the answer, look at it, and decide from the evidence. You own the
decision, not the code. The prototype is an instrument, and you throw it away.

This is the one skill where code quality doesn't matter. Speed and the evidence
do. Propose a variant the user didn't ask for when it might win.

## Arguments

- `/idea-prototype <question>`: the question to settle, such as "which of these two layouts for the settings page" or "is the batch export fast enough on 60k rows".
- `/idea-prototype` (bare): the open question under discussion. When there is none, ask once what decision the prototype should make.

## Cases for another skill

- A question about the data in production → `/production-query`.
- A product or preference call that no experiment can settle, such as what to charge or whether to build it → ask the user, or `/idea-goal`.
- Building the chosen direction for real → `/code-build`.
- A design to grill rather than to try → `/idea-challenge`.

## Instructions

Follow these steps in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm").

### Step 1: Scope the decision

Write the decision in one sentence, and what you'll observe to make it. No decision means no prototype, so hand the work to `/code-build` instead. When the question turns out to be a preference, say so and give it back to the user with the options.

### Step 2: References for an open design

For a visual or interaction question with no direction yet, look at the prior art in the codebase and outside it, and pick two or three distinct directions. Skip this step when the direction is set and only a detail is open.

### Step 3: Build throwaway

- **A script, a query, or a page** goes in `~/.cache/agent-prototypes/<repo>/<slug>/`, outside the repo.
- **Code that needs the running app** goes in a scratch worktree on a branch named `prototype/<slug>`, which is never pushed: `git worktree add ~/.cache/agent-prototypes/<repo>/<slug> -b prototype/<slug>`.

Use the lightest stack that shows the answer: plain HTML and a CDN library for a layout, a short script for timing or output. Skip tests and abstractions, and use the production framework only when the question is about it.

### Step 4: Put the variants behind one switcher

For two or three variants, make them switchable in one place, such as buttons, a keypress, or a command-line flag, and label each one. A second flavor of the first idea doesn't count as a variant.

### Step 5: Observe

Look at each variant where a user would meet it. A visual question gets a screenshot of each variant, through the browser tools or the project's verify skill (`context/<project>/verify/SKILL.md`, when the repo has none of its own). A behavioral or timing question gets the real output, or a timing with the run count and the spread. The observation is the test.

### Step 6: Decide and report

- **Decision**: the variant you recommend. Give the evidence that decided it, marked as measured.
- **Variants**: one line each, with its tradeoff.
- **Evidence**: the screenshots, outputs, or timings, with their paths.
- **Scratch path**: where the prototype is, and a plain statement that it's throwaway.
- **Next**: the chosen direction, handed to `/code-build` for the real build.
- **Check**: what the prototype didn't cover, such as real data volume or an edge case it skipped.
- **Undo**: `rm -rf ~/.cache/agent-prototypes/<repo>/<slug>`, or `git worktree remove ~/.cache/agent-prototypes/<repo>/<slug> && git branch -D prototype/<slug>`.

When the evidence doesn't separate the variants, say so, and give the user the choice with the evidence attached.

## Native Plan mode

Plan mode doesn't allow writes. The plan records the prototype as its first step instead, with the decision it settles and the variants to compare.

## Key Rules

1. **One decision per prototype.** Without a decision to make, build nothing.
2. **The prototype is never merged or pushed.** The real build follows `/code-build`.
3. **The observation is the test.** A claim about a variant needs a screenshot, an output, or a timing behind it.
4. **A preference goes back to the user,** with the evidence attached.
