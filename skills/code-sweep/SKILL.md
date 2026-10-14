---
name: code-sweep
version: 1.0.0
description: |
  Treat a mistake found in one PR or file as a class. Find every copy on the
  default branch and in open PRs, and fix each one where it lives. States the
  class and the look-alikes that are right, proves a detector on the known
  instance, traces where the copies came from, sends each open PR's author a
  follow-up, fixes the default branch in one PR, and installs the strongest
  guard that works against the next copy.
---

# Sweep

Agents copy the code they see nearby, so a mistake in one PR is rarely in only
one place. It came from a sibling file, a template, a brief or a comment, and
the next agent will copy it from there again. This skill finds every copy at
the first instance and fixes each one where it lives. It also removes the
source the copies came from.

## Arguments

- `/code-sweep <finding>`: a link or a `file:line` for the mistake. A sentence that describes it works too.
- `/code-sweep` (bare): the finding under discussion. When there is none, ask once what mistake to sweep for.
- Steers in plain words. `report` or "just find them" sweeps and reports, and fixes nothing.

## Cases for another skill

- A correction to how the agent works, not to code → `/self-improve`.
- A finding you aren't sure is real → `/test-prove` first.
- A fix that restructures many files → `/code-refactor`, with this skill's hit list as its input.

## Instructions

Follow these steps in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm").

### Step 1: State the class

Write three lines:

- **Wrong**: the code pattern of the mistake, general enough to match its copies.
- **Why**: the `file:line` evidence that it's wrong. Often that's the code that already does what the copy repeats.
- **Right**: the code pattern a fix leaves.

Then list the look-alikes, the same code where it's correct, and say why it's correct there. A filter that's redundant under one caller can be the only guard under another. When the evidence for **Why** doesn't hold, stop, because there's no class to sweep.

### Step 2: Prove a detector

Write the cheapest search that finds the class, such as a `git grep` pattern or a short script. Run it at the known instance, where it must hit. Run it on a correct look-alike, where it must miss, or the look-alike list must say how to sort that hit. Keep the detector in the scratch directory, because Step 6 may promote it.

### Step 3: Trace the source

Run `git log -S '<pattern>'` on the default branch to find the first commit. Then find how the copies spread. The usual sources are sibling files, templates, briefs and skills, and comments that invite the copy. Step 5 fixes the source along with the copies. Otherwise the next copy comes back from it.

### Step 4: Sweep

Search the default branch at `origin/<default>`. Then search every open PR by me or by an agent working for me, and every PR on a project's campaign list. In a PR, search only the lines it adds, from its merge base. Report a teammate's PR, and leave it alone.

Sort each hit as an instance or a correct look-alike. Read an unsure hit until it's one or the other.

### Step 5: Fix each copy where it lives

Fix the default branch in one PR with every instance and the source from Step 3. Its fixes keep behavior the same, and pushing and opening it follow the outward rules.

In each open PR, its author fixes its own lines. An agent's PR gets a follow-up through the channel it listens on, and my own branch gets a commit. Each follow-up says that the default branch's copies are fixed in their own PR, so the open PR doesn't widen.

A fix that changes behavior is my decision. Ask about it at the end, with the options.

### Step 6: Stop the next copy

Pick the strongest guard that works, in the order from "Fix the class, not only the instance" in `~/.claude/AGENTS.md`. Making the mistake impossible comes first, and a check whose error says the fix comes next. A test follows, and prose in the brief or skill the agents read comes last. Removing the source in Step 5 can be enough. A check must fail on the known instance and pass on the fix, and you run it on both.

### Step 7: Report

- **Class**: the three lines from Step 1, plus the look-alikes left alone.
- **Found**: each hit with its `file:line`, on the default branch first and then in each PR.
- **Fixed**: the default branch's PR, and each follow-up or commit.
- **Guard**: the guard, with its runs on the instance and on the fix.
- **Open**: hits not fixed and teammates' PRs, each with the reason.
- **Check**: the hits that were hard to sort, and each fix that could have changed behavior.
- **Undo**: for the PR, `gh pr close <n> --delete-branch`. For a guard, `git revert <sha>`.

Then ask my questions together.

## Key Rules

1. **Sweep at the first instance.** A mistake an agent can copy is a class the first time you see it.
2. **Prove the detector before you trust its silence.** It hits the known instance first.
3. **Correct look-alikes stay.** List them, and say why they're right.
4. **Fix each copy where it lives.** One PR for the default branch, and a follow-up or commit for each open PR.
5. **Fix the source of the copies.** It's usually a sibling, a template, a brief or a comment.
6. **The guard is the strongest that works, and it has run.**
