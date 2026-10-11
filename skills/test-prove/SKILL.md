---
name: test-prove
version: 1.0.0
description: |
  Prove that a diff works by running it, not by reading it. Takes the current
  diff by default, or a PR, a branch, a SHA, or a claim in words such as "prove
  the retry can't charge twice". Finds the project's verify harness, states the
  one fact that makes the change safe, and looks for the breakage a search won't
  show. Then it runs the cheapest checks that prove that fact against the real
  code, and reproduces a bug on the old code before trusting its fix. Each fact
  climbs a proof ladder from stated to reproduced in the running app, and the
  report says where it stopped. Never edits the working tree: scripts and
  evidence go to a scratch directory, and anything that writes files runs in a
  scratch worktree.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Skill
  - AskUserQuestion
---

# Prove

Reading a diff tells you what its author meant. Running it tells you what the
code does. This skill takes a change and proves it works by running it, one fact
at a time, against the real code, with output a reader can check.

Most changes that look risky are safe for one reason. The work is to find that
reason and prove it on the code that will run.

The skill never edits your working tree. Scripts and evidence go to
`~/.cache/agent-evidence/<project>/<slug>/`, where `<project>` is the repo's
directory name and `<slug>` names the target, such as `pr-412` or
`retry-double-charge`. Anything that writes files, such as a migration, a schema
dump, or a build, runs in a detached scratch worktree under the evidence directory, which the run removes at the end. `/code-worktree` is for a task's own checkout, not for these. The repro on
the old code runs in a worktree at the base.

## Arguments

- `/test-prove` (bare): the diff against the base. That's the uncommitted
  changes plus the branch's commits since its merge-base with the default
  branch. When both are empty, ask once: "What should I prove?"
- `/test-prove <PR number | url | branch | sha>`: that change, read with `gh` or
  `git` and run in a scratch worktree at its head.
- `/test-prove "<claim>"`: a claim in words, such as "prove the retry can't
  charge twice" or "prove the orders API still returns prices in cents". The
  claim becomes the fact in Step 2. The code under test is the bare diff when
  there is one, and the current checkout otherwise.

## Cases for another skill

- Building the verify harness for a project → `/test-verify`.
- Deciding which tests stay in the suite, and writing them → `/test-design`.
- A claim about production data → `/production-query`.
- Design or correctness review of the diff → `/pr-critique`.

## Instructions

Follow these steps in order. Your checkout is read-only to this run.

### Step 0: Find the verify harness

The harness is how this run launches the app and drives it. Look in this order,
and use the first that applies:

1. **A recorded resolution.** Read `~/.claude/context/<project>/resolutions.md`.
   A `test-prove` line there decides, and you follow it without asking.
2. **The repo's own verify skill.** Look in the repo's `skills/`,
   `.claude/skills/`, `.agents/skills/`, and `.cursor/skills/`, and judge each
   skill by what it does, the way `/test-verify` Step 0 does. One that launches
   and drives the app is the harness. Read it and follow it, and never edit it.
   When it also proves changes the way this skill does, the two overlap. Ask
   once, per the project-skill rule in `~/.claude/AGENTS.md`, whether to use the
   project's skill (the default), this one, or this skill's ladder over the
   project's harness and output conventions. Record the answer in
   `resolutions.md` as `- test-prove → <choice> (<date>)`, in the format of `~/.claude/context.example/resolutions.md`. An unattended run without
   a recorded answer skips the proof and reports the conflict. Under the
   stepping-away steer in `~/.claude/AGENTS.md`, it uses the project's skill and
   logs the choice.
3. **The private harness.** `~/.claude/context/<project>/verify/SKILL.md`,
   written by `/test-verify`. Its feature map in `verify/features/` tells you how
   a user reaches each feature.
4. **The stack notes.** The **Test commands** and **Local runtime** lines in
   `~/.claude/context/<project>/stack.md`. Local runtime gives the up, down,
   restart, status, and logs commands for one checkout, the dev host pattern,
   and any host never to browse.

Whichever harness applies, read the feature map in
`~/.claude/context/<project>/verify/features/` when it exists. It lists every way a
user reaches the changed feature, and a proof through one entry point is
incomplete when the map lists others.

When none of these exist, use the repo's own dev command and test runner, from
its README, Makefile, or package scripts. When a check needed a harness to drive
the app, the report lists it under **Unproven** and names `/test-verify` as the
fix. When `stack.md` is
missing, offer once to scaffold it from `context.example/stack.md`.

### Step 1: Read the change

Resolve the target per **Arguments**, and state it in one line with its size in
files and lines.

- **Bare**: `git diff $(git merge-base HEAD origin/<default>)` covers the
  branch's commits and the uncommitted changes together. Add the untracked files
  that `git status --short` lists.
- **A PR**: `gh pr view` and `gh pr diff`. The base is the PR's base branch.
- **A branch or SHA**: its diff from its merge-base with the default branch, or
  from its parent for a SHA.

Read every changed file in full, not only the hunks. Then read the behavior the
diff doesn't spell out:

- Defaults, callbacks, hooks, and framework conventions that run without
  appearing in the diff.
- What the changed code calls, and what those calls return now.
- Behavior the diff removes. A deleted line can be the only one that enforced a
  rule.
- What the commit messages, the PR description, or the linked issue say the
  change does. Each of those claims is a candidate fact for Step 2.

### Step 2: State the safety fact

Write the one fact that makes the change safe, as a sentence a check could prove
false:

- "The cache key now includes the account, so reads never cross accounts."
- "A second attempt of the retry sends the first attempt's idempotency key,
  and the provider answers it with the first charge."

Spend most of the run here. Most risky-looking changes are safe for one reason,
and proving that one reason rules out most of the risks at once. Ten risks
checked one by one cost more than one fact proven on the real code, and prove
less.

- When the change depends on more than one fact, list each one. Each climbs the
  ladder in Step 6 on its own.
- When the target is a claim in words, restate it as a fact a check could prove
  false.
- When you can't find a fact that makes the change safe, that's the first
  finding. Say so, and go on to Step 3 for the risks.

### Step 3: Look where grep stops

A search for the changed name finds the callers. Listing them isn't the job.
The job is to find the breakage a search won't show. Look at:

- **The library's source** at the version the lockfile pins, plus any local
  patches or vendored copies. Read the function the change depends on, not its
  documentation.
- **Serialized formats**, such as JSON a client parses, a queue payload, a cache
  entry, or a file on disk. Records the old code wrote are still there when the
  new code reads them.
- **Other readers of the same data**, flags, and config: another service, a
  report, a job, or a setting that reads what the change writes.
- **Jobs that retry.** What happens when the job runs twice, or crashed halfway
  and starts again?
- **Timing and teardown**, such as a job enqueued before its transaction
  commits, a cache entry still read after the request ends, or a process stopped
  mid-write.

A risk needs a caller that can produce it. A state no caller can produce isn't a
risk, per "Don't defend against what can't happen" in `~/.claude/AGENTS.md`, and
listing it makes the real ones harder to find. Record each risk with how it breaks and its
`file:line`, then decide whether the fact from Step 2 already rules it out.

### Step 4: Choose the checks

Pick checks by what changed. Each one proves a fact from Step 2, or rules a risk
from Step 3 in or out.

| What changed | Check |
|---|---|
| Logic | The smallest targeted test. |
| An API | One real request against the running app, with the response body saved. |
| UI | Drive the page through the verify harness, plus one narrow viewport when the layout changed. |
| A job | Run it once, then read its logs and the records it wrote. |
| A migration | Run it in the scratch worktree against a throwaway database, then check the schema it produced. |
| Config | Boot the app with it. |

Size the run to the change. A focused change gets one smoke check, and a change
that crosses services gets the whole path, from the first request to the last
record written.

Where the checks run:

- A test file this run writes goes in a scratch worktree, never in your tree,
  with a copy in the evidence directory.
- For the bare target, create the scratch worktree at `HEAD` with
  `git worktree add --detach <path> HEAD`, then apply the uncommitted changes there with
  `git diff HEAD --binary | git -C <worktree> apply`. Copy in each untracked
  file the change adds.
- Run the app from the scratch worktree with the Local runtime commands for
  that checkout. Only the task's own runtime ever gets a restart. Never restart
  the primary checkout's app or a shared service, such as a database server or
  a queue that other checkouts use.
- Restart a long-running process after a code change, before you trust what it
  returns. A running process may still have the old code loaded.
- A database with data the user cares about is off limits. Migrations and
  writes go to a throwaway database that this run creates and drops.
- When the harness says two instances can't share the machine and another one
  is up, skip that check and list it as unproven, with the command that would
  run it.
- Never browse a host the Local runtime line rules out, and never point a check
  at production.

Write scratch scripts plainly. A script that crashes with a clear message is
better evidence than one that catches the error and prints "ok".

### Step 5: Reproduce the bug on the old code first

When the change fixes a bug, reproduce the bug before you trust the fix. Write
the repro as:

- **Actor**: who acts, such as a signed-in customer or the nightly retry job.
- **State**: what exists before the action, such as an order with one failed
  charge.
- **Action**: what the actor does, such as a request or a job run.
- **Expected and observed**: what should happen, and what the old code does.

Run it in a worktree at the base and capture the failure. Then run the same
steps, unchanged, on the new code. Create the state through the app's APIs or
its fixtures, never with raw inserts. A raw insert can build a state the app
can't produce, and then the run proves a fix for a bug users never hit.

When the old code doesn't reproduce the bug, the fix is unproven. Either the
repro misses the trigger, or the bug is somewhere else. Say which you think it
is. A pass on the new code means little until the same steps fail on the old
code.

### Step 6: Climb the proof ladder

Each fact the change's safety depends on climbs as far as is cheap, and the
report says where each one stopped.

1. **Stated.** Written down, with no evidence yet. That's a guess.
2. **Cited.** A `file:line` in the repo, or the library's source at its pinned
   version, shows the fact. That's inferred.
3. **Walked.** The failure is traced step by step, with a citation at each step,
   and shown not to arrive. That's inferred.
4. **Ran.** A script or test calls the real code, through the library the app
   uses, and exits non-zero when it's wrong. That's measured.
5. **Reproduced.** The behavior is observed in the running app, through the
   harness. That's measured.

Rules for the ladder:

- A check proves something only when it can fail. Before you trust a pass on
  rung 4 or 5, see the same check fail against code that breaks the fact. Use
  the base for a bug, or the scratch worktree with the fact broken on purpose.
- A missing job, log line, or error doesn't prove anything. Its absence can
  mean the code never ran.
- An inconclusive result counts as a fail, and so does a check on the wrong
  layer, such as a unit test with the database mocked when the fact concerns
  the database.
- Static analysis alone never makes a fact "verified". Rungs 1 to 3 are reading,
  and only rungs 4 and 5 are running.
- Reuse evidence from an earlier run only when the diff and the environment are
  both unchanged. Record the diff hash, the lockfile hash, and the runtime
  versions next to each result, so a later run can tell.
- A writeup that sounds right doesn't prove anything by itself. The proof is the output
  pasted under it.

### Step 7: Clean up and report

Stop the processes this run started, drop its throwaway databases, and remove
its scratch worktrees with `git worktree remove`. Keep the evidence directory. Each
script in it records the SHA it ran against, so a rerun can rebuild its
worktree.

Then report:

- **Change**: the target with its size, and what it does in one or two
  sentences.
- **Safety fact**: each fact, the rung where it stopped, and its proof pasted under it,
  meaning the command and the lines of output that show the result. A fact
  without proof is marked **Unproven**.
- **Checks run**: each command, the worktree and SHA it ran against, and its
  output or the path to it.
- **Risks**: each with how it breaks, its `file:line`, how likely it is, and
  what it costs when it happens.
- **Ruled out**: the risks the checks put to rest, and why.
- **Unproven**: for each fact or risk below rung 4, the cheapest check that
  would prove or refute it.
- **Scratch**: the evidence directory path.

Mark every claim measured, inferred, or guess, per "Say how you know" in
`~/.claude/AGENTS.md`. A test from this run that belongs in the suite goes to
`/test-design` to decide and to `/code-build` to write. This skill never adds it
to the repo.

Save the report as `report.md` in the evidence directory too, where a PR
description from `/pr-open` can quote it.

## Key Rules

1. **Never edit the working tree.** Scripts and evidence go to the evidence
   directory, and anything that writes files runs in a scratch worktree.
2. **Prove the reason, not the list.** Find the one fact that makes the change
   safe, and prove it on the real code.
3. **Reproduce on the old code first.** A fix whose bug never failed on the base
   is unproven.
4. **A check has to be able to fail.** A missing error, an inconclusive result,
   or a check on the wrong layer counts as a fail.
5. **Reading is never "verified".** Only rungs 4 and 5 run the code.
6. **Only the task's own runtime gets a restart.** Never the primary checkout's
   app, a shared service, a database with data the user cares about, or
   production.
7. **The repo's own verify skill comes first.** Read it and follow it, and
   never edit it.
8. **Every claim says how you know.** Mark it measured, inferred, or guess, with
   the proof pasted in.
