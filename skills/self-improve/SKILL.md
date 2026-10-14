---
name: self-improve
version: 4.1.0
description: |
  Turn the current session, or the corrections that recur across past
  sessions, into durable harness improvements. Generalizes each correction into
  a class-level lesson, then fixes it at the strongest level that works: make
  the mistake impossible, add a check whose error says the fix, add a test, and
  only then write prose. Checks go in this library or, for a project, in its
  private context. Applies the lessons and commits them, with each lesson listed
  in the commit message.
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
- `/self-improve history [topic]`: look across past sessions and recent PRs for corrections that recur (see **History mode**).
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
- context the user pasted that a connected tool, such as an MCP server or `gh`, could have fetched

Each candidate keeps a pointer to its evidence (the message or output that shows it).

### History mode

`/self-improve history [topic]` harvests past work instead of this session:

1. Search my own turns with `~/.claude/bin/transcripts.py search '<regex>' --days 60`, for correction phrasing ("I said", "again", "don't", "stop", "why did you") and for the topic. Read each match in its session before counting it. Only Claude Code sessions are on disk, so Codex and Cursor corrections don't show up.
2. In the current repo, read `git log --grep='^Revert' --since='60 days ago'`, and the review comments on my recent PRs (`gh pr list --author @me --state all --limit 20`, then `gh api repos/<owner>/<repo>/pulls/<number>/comments`).
3. Group the findings into mistake classes. A class counts once it has happened twice, in two sessions or two PRs. The classes are the candidates for Step 2.

### Step 2: Generalize

For each candidate, strip the session's specifics (branch names, ticket IDs, PR
numbers, paths, customer names, feature nouns) and restate the lesson at the class level: *when
<trigger>, do <behavior>, because <cost it avoids>*. If the lesson stops making
sense without its specific nouns, it is not general enough to install; keep it as
evidence only. Drop generic advice ("write tests", "read the code") and anything an
existing file already says.

### Step 3: Pick the level, then the home

A rule an agent can skip is weaker than a check that fails. For each lesson, pick the strongest level that works, per `~/.claude/AGENTS.md` ("Fix the class, not only the instance"), and say why each level above it doesn't:

1. **Make it impossible.** In this library, that means one source of truth instead of hand-synced lists, or a hook. In a project, it means a type or a module boundary, which is a change to the project's code, so it becomes a proposal unless I say otherwise.
2. **A check whose error says the fix.** In this library, that's a rule in `bin/check`, a Vale rule in `vale/styles/deslop/`, or a pattern in `bin/hooks/outward_guard.py`. In a project, it's a private check in `context/<project>/checks/`, in the format of `context.example/checks/README.md`. Moving a private check into the repo is my call.
3. **A test.** In this library, that's an eval like `agents/persona.evals.md`. In a project, a test is a proposal.
4. **Prose.** Only for a decision that needs judgment, which a mechanism can't make. Its homes, in order of preference:
   1. **Global `~/.claude/AGENTS.md`**: only for behavior that should change in every repo. Claude Code loads it through `CLAUDE.md`, and a rule that only Claude Code can follow goes in `~/.claude/CLAUDE.md` itself.
   2. **An existing global skill, command, or agent**: when a workflow this library already covers is missing the lesson.
   3. **`~/.claude/context/<project>/`**: project-specific facts and preferences. Stack notes go into `stack.md`, and metric learnings into `charter.md`. A call goes into `decisions.md`, in the format of `context.example/decisions.md`: edit the entry for that call when one exists, and add one under its topic when none does.
   4. **The project's own learning skill**, for a lesson that belongs to the repo's harness (its docs, skills, and routing) when the repo has a skill for exactly this job. Offer to invoke it via the Skill tool for those lessons. Never edit the project's files from here.
   5. **A proposal**, for a repo-owned lesson without a project learning skill. Write the suggested patch into the report for the user to hand to the repo's owners.
   6. **Nothing**: useful history without a durable rule. Say so.

**A repeat moves up a level.** Search `AGENTS.md`, the skills, and the project's context for the lesson's rule before writing it. When the rule is already there as prose and the session broke it anyway, write the mechanism, not a second copy of the rule. First find out why the existing rule failed, and fix that cause too:

- **Routing.** The skill that contains the rule didn't load or didn't fire.
- **Conflict.** Another rule said otherwise.
- **Staleness.** The rule no longer matches the code or the workflow.
- **Skipped.** The agent read the rule and skipped it anyway, which is the case a mechanism fixes.

**Prove a check before keeping it.** Run it against the evidence where the mistake happened, such as the commit, the diff, or a file with the excerpt. It must report the mistake. A check that doesn't report its own evidence is wrong, so fix it or drop it.

Never create a new skill from one session. A workflow gap justifies a skill when it has
recurred. Until then it is an entry in `decisions.md`, with the recurrence as its Revisit when.

### Step 4: Prune and route

Print a table (lesson → level → home → one-line patch summary), then continue to Step 5 and
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
- A new check in this library gets a row in `docs/enforcement.md`. A private project check gets a row in `context/<project>/rules.md`.
- A tracked file that already has uncommitted changes is being edited now. Skip its
  lesson, apply the rest, and ask about it at the end of the run.
- A lesson that changes a workflow gets a minimal headless run (`claude -p` in a scratch repo) that sets up the situation without hinting at the answer. Report what the run did.
- Commit the tracked writes in `~/.claude` in one commit. Its message lists each lesson
  and its home. Writes to `context/<project>/` get their own commit in the context repo,
  `git -C ~/.claude/context commit -m '<lessons>' -- <paths>`, and its pre-commit hook
  must pass.

### Step 6: Report

Write one line per lesson with its level and where it's installed. A lesson that wasn't installed says why (skipped / proposal / evidence
only). A session that doesn't yield a lesson to install is a complete result. If an edited file contained a rule that now looks obsolete, flag it as a
question and never silently drop it.

End with **Check** and **Undo**. Check quotes each new or changed rule, because a bad
lesson changes every later session. It also quotes each line added under
`context/<project>/`. Undo is `git revert <sha>` for the library commit, and
`git -C ~/.claude/context revert <sha>` for the context commit.

## Key Rules

1. **Structure first.** A check that fails is stronger than a rule an agent can skip, and
   a rule is stronger than a note about the past. Prose is the fallback, and a note is the last resort.
2. **One strong lesson beats five weak ones.** Prune before proposing.
3. **Prune before writing, then apply and commit.** The commit message lists every lesson, and the report quotes every new rule.
4. **Publishability applies to every tracked write.** Project specifics live in
   `context/`, which is gitignored.
5. **Never edit another repo's files.** Repo-owned lessons route to the repo's own
   learning skill or become proposals.
6. **No new skills from one session.** Recurrence justifies skills, and `history` mode finds it.
