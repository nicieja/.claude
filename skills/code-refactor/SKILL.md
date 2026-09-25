---
name: code-refactor
version: 1.0.0
description: |
  Refactor code that grew by iteration, as a checklist of slices in a plan
  file in the repo. Surveys the scope, says whether a refactor is useful, and
  writes the plan, then stops for your edits. After the go-ahead it pins
  today's behavior in a baseline, proves that the check can fail, and commits
  one slice at a time. Bugs it finds wait in a list for you. A later run
  continues from the plan.
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

# Refactor

Take code whose layout still shows how it was built, with requirements that changed and experiments that became the product, and refactor it to the same behavior in less code, with each concept in one module. The work runs from a plan file in the repo. The plan is a checklist of slices, each one commit, with the rules and the checks at the top and a log at the end. The file is the memory of the run. It is still there after a context compaction or in a new session, and the user can edit it between slices.

The method has two halves with a checkpoint between them. The first half reads and plans, and the code does not change. The second half pins the current behavior in a baseline, then changes the code one slice at a time and compares each result with the baseline. A survey can end with the verdict that a refactor is not useful here, and that is a finished result.

## Arguments

- `/code-refactor <scope>`: plan and run a refactor of the scope. A scope is a path or a list of files, a feature or module by name, a branch, or a PR by number or URL. For a PR, the scope is the files it changes, and the slices commit to its branch. Ask before a checkout.
- `/code-refactor <plan path>`: continue the plan at its first open slice.
- `/code-refactor` (bare): if the plans directory has a refactor plan with open slices, offer to continue it. If it has none, ask once: "What code should I refactor?"
- Steers in plain words. "Plan only" stops after the checkpoint in Step 4. "One slice" runs the next open slice and stops.

## Cases for another skill

- One pass over a diff or a file, with no plan → `code-simplifier`.
- Only the defensive code → `/code-unguard`.
- A pitch for a refactor that needs grilling before any work → `/idea-challenge`.
- Work that changes behavior, such as a new requirement → `/idea-spec`. A refactor that must also change behavior is two pieces of work, and this skill runs the refactor alone.

## Instructions

Follow these steps in order. Steps 0 to 4 plan, and the code is unchanged until the checkpoint in Step 4. Steps 5 to 9 run the plan.

---

### Step 0: Preflight

1. **Resolve the scope.** State it and its size in one line. Stop outside a git repo, because each slice is a commit and each check is a diff.
2. **Look for a plan to continue.** A plan path in the arguments means a continuation. So does a refactor plan with open slices for this scope in the plans directory. Read the plan and the harness, and go to Step 6 at the first open slice.
3. **Project-skill check.** Check `~/.claude/context/<project>/resolutions.md` first (`<project>` is the repo directory name). If it records a resolution for `refactor`, follow it silently. Otherwise scan the project's skills (`<root>/skills/`, `<root>/.claude/skills/` and `<root>/.agents/skills/`) for one whose output covers a planned refactor. If one does, ask once with AskUserQuestion:
   - **Use the project's skill (Recommended)**: invoke it with the Skill tool and end here.
   - **Use this skill**: continue as normal.
   - **Compose**: this skill's process with the project skill's conventions, such as where plans go and how they look.

   Append the choice to `resolutions.md` (create it if missing) as `- refactor → <choice> (<date>)`. Unattended runs never ask. Without a recorded resolution, they skip the work and note the conflict in the report.
4. **Load the guide.** Read `~/.claude/skills/code-refactor/refactor-guide.md` in full before the survey, on every run. It has the catalog of refactor targets and the slice order, plus the harness recipe and the plan template.
5. **Find the plans directory.** Check `docs/plans/`, `plans/`, `rfcs/`, `designs/` and `.agents/plans/` under the repo root. Read any README, AGENTS, CLAUDE or TEMPLATE file inside, and follow its conventions. When the repo sorts plans by status, such as `active/` and `completed/`, use the folder for work in progress. When none of these directories exists, ask once whether to create `docs/plans/` or to keep the plan untracked in the harness directory.
6. **Check the tree.** If the scope has uncommitted changes, ask before you go on, because the baseline must be of committed code.

---

### Step 1: Survey

1. **Read all of it.** Read every file in scope and its tests in full, and tell the user the line count. Do not skim, and do not hand the reading to a subagent. The slices depend on details that a summary drops.
2. **Read the history.** Run `git log --stat -- <scope>`, and read the finished plans that touched the scope. They show which requirements changed and which code still serves the old ones.
3. **Run the suite and the linter.** A red suite on a clean tree is a precondition. Find its cause now, such as a generated file that is out of date, because slice 0 fixes it.
4. **Map what pins the behavior.** The tests pin part of it. List the outputs outside the tests too, such as generated files and script output, or pages and API payloads. Mark the code with few tests, such as the UI, because its slices need a manual check.
5. **Hunt with the catalog.** Go through the marks in the guide, and confirm each one in the code with a file and a line. Write down the behavior bugs that you see on the way. They become findings for later, and the refactor leaves them unfixed.

---

### Step 2: Verdict

Tell the user whether a refactor is useful here. Give three to five concrete marks that the history left, each with a file. If the answer is no, give the reason and stop. That is a finished result, and it does not need a plan.

---

### Step 3: Write the plan

Write the plan from the template in the guide, as `<plans dir>/<area>-refactor.md`. The area is two or three words for the scope.

- **Context** tells how the code got to its current state and lists the marks from the survey. The goal is the same behavior in less code, with each concept in one module.
- **Rules for every slice** are the rules of the template, plus the rules of this project, such as a key order that an output depends on.
- **The checks** fit the recipe in the guide to this code. State the inputs of the probe, the slices that need a manual check, and the step that needs the network.
- **Slices** start with slice 0, the baseline. The planned slices follow in the order of the guide. Each one is one idea that a reviewer can read as one commit, and the tree is green after it. A second-look slice comes after them, and a docs slice is last. A slice that must change an output states the exact change. A slice that touches code with few tests states its manual check.
- **Findings for later** start with the bugs from the survey, each with what shows it.
- **Log** starts empty.

---

### Step 4: Checkpoint

Present the plan in one message. Give the path and a table of the slices, with the number, the title and the change of each. Then list the planned output changes and the preconditions, and the findings for later so far. Tell the user that they can edit or reorder the plan file before they answer.

Then ask with AskUserQuestion:

- **The commit policy.** The options:
  - **I commit each slice on a new branch** (Recommended on the default branch).
  - **I commit each slice on this branch.**
  - **You commit.** Each slice then stops with its changes staged, and the user commits.
- **Preconditions**, only when the survey found one: may slice 0 fix it as its first commit?

On "plan only", stop here. Otherwise, after the answers, read the plan file again for the user's edits, and commit it alone as the first commit.

---

### Step 5: Slice 0, the baseline

1. Fix each precondition in a commit of its own.
2. Write the harness from the recipe in the guide, in a git-ignored directory inside the repo. Confirm the ignore with `git check-ignore`. When no ignored directory fits, add one line to `.git/info/exclude`, which git does not track, and tell the user.
3. Run every generator on the unchanged code. A diff at this point is drift from before the refactor, and it gets a slice of its own.
4. Save the baseline outputs, and run the check. It must pass.
5. Mutation-test the check as the guide describes. It must fail on the change and pass after the revert.
6. Record the timings, tick the box, write the log line with the hash of the commit that the baseline comes from, and commit.

---

### Step 6: Run the slices

Take the open slices in file order, one after another. The run pauses between slices only under the "You commit" policy, where each slice waits for the user's commit. For each slice:

1. **Read the plan again.** Read the rules and this slice, and the last lines of the log. After a compaction or in a new session, the file is the only state that counts, and the user's edits to it win over your memory of it.
2. **Make the change.** A test changes only when the code it tests moves or gets a new name, and a moved test keeps its notes. After a move, search for unused imports and for names without a definition. Read the lint config to learn what the linter checks, because a config without `no-undef` misses an undefined name.
3. **Update the harness with the API.** When a probe or a script in the harness calls an API that the slice changes, update it in the same slice. Its outputs must still match the baseline.
4. **Run the whole check**, one step after another, and let it stop at the first failure. To make it pass, fix the code and leave the baseline as it is.
5. **Apply planned output changes to the baseline.** When the slice declares an output change, apply exactly that change to the baseline, and require equality with the new output. Then save the new output as the baseline, and write the change in the log.
6. **Handle surprises.**
   - When a slice grows past one idea, split it. Add a sub-slice, such as 2b, right after it in the plan.
   - Write a bug in the findings for later with what shows it, and leave the bug as it is.
   - When a tool changes data as a side effect, such as a refresh that rewrites a value, restore the file and write the change in the findings. The side effect is never part of a slice commit.
   - A question that only the user can answer stops the run. Ask it, and continue after the answer.
7. **Close the slice.** Tick its box (`### - [x]`). Add the log line with the date, what the slice found or deferred, and any measurement. The line leaves out the hash, because a commit cannot contain its own hash, and `git log -- <plan>` finds it. Commit the code and the plan together, as the policy says.

On "one slice", stop after the first closed slice.

---

### Step 7: Second look

After the planned slices, dispatch the `code-simplifier` agent for one pass over the code in scope. It runs in its own context and reads the result without the history of the run, and that is the reason for this step. Its brief contains these parts.

- The file list, and the plan path to read first.
- The rules of the plan, and this rule word for word: "Don't defend against what can't happen. Validate at the boundary and trust what you find inside. Do not propose guards, fallbacks, retries or try/catch for states no caller can produce. Prefer a crash with a clear message, and report existing defensive code of that kind as a finding."
- The idioms of the codebase, such as its comment density and its naming.
- The findings for later, which it must not report again.
- The instruction to report only and to edit no file.
- The report format. Each finding gives the file and line and the change, and why the change is simpler and what it risks. The most valuable finding comes first, with about 15 at most. Behavior bugs go in a separate list.

Its findings become new slices before the docs slice, each marked "From slice N", or findings for later. Run the new slices with Step 6. Keep your own judgment. A finding that changes behavior goes to the findings for later, even when the agent calls it a cleanup.

---

### Step 8: Docs slice (last)

Update the docs that point to moved or renamed code. If the repo keeps finished plans in a folder of their own, move the finished plans for this scope there, this plan included. Close the slice as in Step 6. The harness directory is still in the repo and ignored, and the user can delete it.

---

### Step 9: Report

Report in one message:

- the commits, and whether they are pushed;
- the changes by area, and the test count before and after;
- each measured gain in the form that matters to its reader, such as the gzipped size of a bundle next to the raw size;
- the checks of each slice and the mutation test, and each manual check with its limits;
- the findings for later, one line each, for the user to decide.

---

## Key Rules

1. **The baseline decides.** Behavior does not change, and a diff against the baseline of slice 0 decides it. A planned output change is checked as exactly that change.
2. **The plan file is the state.** Read it before each slice, and tick and log after it. The user's edits to it win.
3. **The code waits for the checkpoint.** The code is unchanged until the user answers in Step 4, and the plan is the first commit.
4. **Each slice is one commit on a green tree.** The check runs whole and serially, and it stops at the first failure.
5. **Trust a check after it fails once.** Slice 0 mutation-tests the harness.
6. **Bugs wait for the user.** A bug that the refactor finds goes to the findings for later, unfixed. Each finding says what shows it, such as a failing test or a reproduction, and a bug found by reading says so.
7. **Tests move with their code.** A test changes only when the code it tests moves or gets a new name.
8. **Do not write defensive code.** Validate at the boundaries and trust the data inside. Keep the crashes that exist, and put this rule in every agent brief.
9. **Push only on request.** Commit as the chosen policy says, and push only when the user asks.
10. **Git ignores the harness.** It is in an ignored directory inside the repo, and it is never committed.
11. **Load `refactor-guide.md` every run.** The catalog and the recipe come from that file and never from memory.
