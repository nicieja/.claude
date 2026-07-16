---
name: learn
version: 2.0.0
description: |
  Turn the current session into durable harness improvements. Harvest
  corrections, failed paths, and repeated instructions; generalize each into a
  class-level lesson; route every lesson to the smallest durable home — global
  CLAUDE.md, an existing skill/command/agent, the project's context directory,
  or the project's own learning skill. Diagnose-first: proposes before writing.
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

# Learn

Extract what this session should change about future sessions, and install it. The
output is harness patches, not a summary: a future agent should need fewer
corrections because of what this run writes. Lessons that don't survive
generalization become nothing — an honest "no durable learning" is a valid result.

## Arguments

- `/learn` — harvest the current session.
- `/learn <hint>` — focus the harvest on one thread of the session.

## When this is the wrong skill

- Reflecting on a shipped piece of work (PR, issue) rather than this session → `/retro`
- Repairing accretion in the prompt library → `/self-heal`
- The repo has its own session-learning skill and the lesson is repo-owned → this
  skill detects that and routes to it (Step 3); invoking it directly is also fine.

## Instructions

Follow in order.

### Step 1: Harvest

Re-read the session for the moments that cost something:

- corrections the user made (especially repeated ones)
- paths tried and abandoned, and why
- instructions the user had to give that a file could have carried
- missing context that caused a wrong assumption
- tool/command incantations that took several attempts to get right

Each candidate keeps a pointer to its evidence (the message or output that shows it).

### Step 2: Generalize

For each candidate, strip the session's specifics — branch names, ticket IDs,
customer names, feature nouns — and restate the lesson at the class level: *when
<trigger>, do <behavior>, because <cost it avoids>*. If the lesson stops making
sense without its specific nouns, it is not general enough to install; keep it as
evidence only. Drop generic advice ("write tests", "read the code") and anything an
existing file already says.

### Step 3: Route each lesson to the smallest durable home

In order of preference:

1. **Global CLAUDE.md** — only for behavior that should change in every repo.
2. **An existing global skill, command, or agent** — when the lesson is a gap in a
   workflow this library already owns.
3. **`~/.claude/context/<project>/`** — project-specific facts and preferences:
   stack notes into `stack.md`, calls into `decisions.md`, metric learnings into
   `charter.md`.
4. **The project's own learning skill** — when the lesson belongs to the repo's
   harness (its docs, its skills, its routing) and the repo carries a skill for
   exactly this job: offer to invoke it via the Skill tool for those lessons.
   Never edit the project's files from here.
5. **A proposal** — repo-owned lesson, no project learning skill: write the
   suggested patch into the report for the user to hand to the repo's owners.
6. **Nothing** — useful history, no durable rule. Say so.

Never create a new skill from one session. A workflow gap earns a skill when it has
recurred; until then it is a note in `decisions.md`.

### Step 4: Propose, then wait

Present a table — lesson → home → one-line patch summary — and ask which to apply
(multi-select). The checkpoint is the point: nothing is written before it.

### Step 5: Apply

- Edits to existing tracked files follow the coverage-ledger discipline from
  `skills/self-heal/heal-guide.md`: every existing commitment survives.
- Every tracked write passes the publishability test: no employer, product,
  customer, or industry-domain vocabulary; neutral SaaS examples only.
  Project-specific content goes to `context/<project>/`, never to tracked files.
- Context files are created from their `context.example/` templates when missing.

### Step 6: Report

One line per lesson: installed where, or why not (skipped / proposal / evidence
only). If an edited file contained a rule that now looks obsolete, flag it as a
question — never silently drop it.

## Key Rules

1. **Harness-first.** A lesson that changes future behavior beats a note that
   describes past behavior. Notes are the fallback, not the default.
2. **One strong lesson beats five weak ones.** Prune before proposing.
3. **Diagnose-first.** No writes before the Step 4 checkpoint.
4. **Publishability governs every tracked write.** Project specifics live in
   `context/`, which is gitignored.
5. **Never edit another repo's files.** Repo-owned lessons route to the repo's own
   learning skill or become proposals.
6. **No new skills from a single session.** Recurrence earns skills.
