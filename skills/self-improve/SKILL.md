---
name: self-improve
version: 3.0.0
description: |
  Turn the current session into durable harness improvements. Harvest
  corrections, failed paths, and repeated instructions; generalize each into a
  class-level lesson; route every lesson to the smallest durable home: global
  AGENTS.md, an existing skill/command/agent, the project's context directory,
  or the project's own learning skill. Applies the lessons and commits them,
  with each lesson listed in the commit message.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - Skill
---

# Self-improve
Extract what this session should change about future sessions, and install it. The
output is harness patches, not a summary: a future agent should need fewer
corrections because of what this run writes. Lessons that don't survive
generalization become nothing. An honest "no durable learning" is a valid result.

## Arguments

- `/self-improve`: harvest the current session.
- `/self-improve <hint>`: focus the harvest on one thread of the session.
- Steers in plain words: `--review` / "ask first" stops after the Step 4 table and waits for your pick.

## Cases for another skill

- Reflecting on a finished piece of work (PR, issue) rather than this session → `/work-retrospective`
- Repairing accretion in the prompt library → `/self-heal`
- The repo has its own session-learning skill and the lesson is repo-owned → this
  skill detects that and routes to it (Step 3). Invoking it directly is also fine.

## Instructions

Follow in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm").

### Step 1: Harvest

Re-read the session for the moments that cost something:

- corrections the user made (especially repeated ones)
- paths tried and abandoned, and why
- instructions the user had to give that a file could have contained
- missing context that caused a wrong assumption
- tool/command incantations that took several attempts to get right

Each candidate keeps a pointer to its evidence (the message or output that shows it).

### Step 2: Generalize

For each candidate, strip the session's specifics (branch names, ticket IDs,
customer names, feature nouns) and restate the lesson at the class level: *when
<trigger>, do <behavior>, because <cost it avoids>*. If the lesson stops making
sense without its specific nouns, it is not general enough to install; keep it as
evidence only. Drop generic advice ("write tests", "read the code") and anything an
existing file already says.

### Step 3: Route each lesson to the smallest durable home

In order of preference:

1. **Global `~/.claude/AGENTS.md`**: only for behavior that should change in every repo. Claude Code loads it through `CLAUDE.md`, and a rule that only Claude Code can follow goes in `~/.claude/CLAUDE.md` itself.
2. **An existing global skill, command, or agent**: when the lesson is a gap in a
   workflow this library already covers.
3. **`~/.claude/context/<project>/`**: project-specific facts and preferences.
   Stack notes go into `stack.md`, calls into `decisions.md`, and metric learnings into
   `charter.md`.
4. **The project's own learning skill**, for a lesson that belongs to the repo's
   harness (its docs, skills, and routing) when the repo has a skill for
   exactly this job. Offer to invoke it via the Skill tool for those lessons.
   Never edit the project's files from here.
5. **A proposal**, for a repo-owned lesson without a project learning skill. Write the
   suggested patch into the report for the user to hand to the repo's owners.
6. **Nothing**: useful history without a durable rule. Say so.

Never create a new skill from one session. A workflow gap justifies a skill when it has
recurred. Until then it is a note in `decisions.md`.

### Step 4: Prune and route

Print a table (lesson → home → one-line patch summary), then continue to Step 5 and
apply every lesson that has a home. The user can interrupt to drop a lesson. With
`--review`, ask which to apply (multi-select) and wait for the answer before any write.

Route 4 stays an offer, because the project's learning skill edits the project's repo.
Route 5 stays a written proposal.

### Step 5: Apply

- Edits to existing tracked files follow the coverage-ledger discipline from
  `skills/self-heal/heal-guide.md`: every existing commitment is kept.
- Each tracked write must pass the publishability test: no employer, product,
  customer, or industry-domain vocabulary, and neutral SaaS examples only.
  Project-specific content goes to `context/<project>/`, never to tracked files.
- Context files are created from their `context.example/` templates when missing.
- A tracked file that already has uncommitted changes is being edited now. Skip its
  lesson, apply the rest, and ask about it at the end of the run.
- Commit the tracked writes in `~/.claude` in one commit. Its message lists each lesson
  and its home. Writes to `context/<project>/` are gitignored, so they stay out of the
  commit.

### Step 6: Report

Write one line per lesson: installed where, or why not (skipped / proposal / evidence
only). If an edited file contained a rule that now looks obsolete, flag it as a
question and never silently drop it.

End with **Check** and **Undo**. Check quotes each new or changed rule, because a bad
lesson changes every later session. It also quotes each line added under
`context/<project>/`. Undo is `git revert <sha>` for the commit, and deleting the
quoted lines for the context files.

## Key Rules

1. **Harness-first.** A lesson that changes future behavior is better than a note that
   describes past behavior. Notes are only the fallback.
2. **One strong lesson beats five weak ones.** Prune before proposing.
3. **Prune before writing, then apply and commit.** The commit message lists every lesson, and the report quotes every new rule.
4. **Publishability applies to every tracked write.** Project specifics live in
   `context/`, which is gitignored.
5. **Never edit another repo's files.** Repo-owned lessons route to the repo's own
   learning skill or become proposals.
6. **No new skills from one session.** Recurrence justifies skills.
