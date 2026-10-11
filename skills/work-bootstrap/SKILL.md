---
name: work-bootstrap
version: 1.0.0
description: |
  Set a project up so agents can work in it with little hand-holding. Drafts
  the missing files of ~/.claude/context/<project>/ from the repo itself: stack
  notes, risk tiers seeded with the surfaces that usually need a person,
  escalation, delegation, resolutions for overlapping repo skills, and private
  terms. Asks one round of questions about what the repo can't show, then runs
  /test-verify so agents can prove their own work. Never overwrites a file that
  exists.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Skill
  - Agent
  - AskUserQuestion
---

# Bootstrap a project

An agent in a new project starts blind. It has to ask how to run the tests and the app, and it can't tell which code is risky. Each gap becomes a question for me, and the conservative defaults in `~/.claude/AGENTS.md` make every change wait for my review. This skill drafts the context layer from what the repo already shows. The first unattended run then starts where a project usually gets only after weeks of corrections.

## Arguments

- `/work-bootstrap` (bare): the current repo.
- `/work-bootstrap --check`: list the context files that exist and the ones that are missing, with what each missing one would say. It doesn't write a file.

## Cases for another skill

- A verify skill or a feature map → `/test-verify`, which this skill runs as its last step.
- A rule agents keep breaking → `/self-improve`, which adds rows to `rules.md` and writes checks.
- Recurring loops → `/setup`, which arms the routines in `context/<project>/routines/`.

## Instructions

Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm"). The files this skill writes are private and new, so it writes them, then reports. It never overwrites a file that exists.

### Step 0: Find the project and what it has

`<project>` is the directory name of the main checkout, the first entry in `git worktree list`. List `~/.claude/context/<project>/`. A file that exists stays as it is, and the report lists the fields it lacks. Only a missing file gets drafted.

### Step 1: Read the repo

Answer each field from the repo, and keep the evidence for each answer, such as the file or the command it came from. A field the repo can't answer becomes a question for Step 2, never a guess.

| File | Field | Where to look |
|---|---|---|
| `stack.md` | Code host and PR flow | `git remote -v`, `gh repo view`, the stacking tools that are installed and configured, and a merge queue in the rulesets |
| | CI | `.github/workflows/`, and the required checks in the default branch's protection and rulesets |
| | Review bots | the authors of reviews and checks on the last ten merged PRs |
| | Commit conventions | `.gitmessage`, a commitlint config, and the style of the last 50 commit subjects |
| | Test commands and local runtime | `package.json` scripts, `Makefile`, `justfile`, `mise.toml`, `bin/`, `Procfile`, `docker-compose.yml`, and the README |
| | Schema locations | the schema and migration files |
| | Architecture reading order | `README`, `AGENTS.md`, `CLAUDE.md`, and `docs/` |
| | Worktrees | `git worktree list`, and any worktree script in the repo |
| | Tracker and error tracking | issue keys in branch names and PR titles, config and environment variable names, and the MCP servers this session has |
| | Project skills | `skills/`, `.claude/skills/`, `.agents/skills/`, and `.cursor/skills/` |
| `risk-tiers.md` | Surfaces | the paths that match the default entries under Surfaces in `~/.claude/context.example/risk-tiers.md` |
| `delegation.md` | Executors | `codex` on the path, PRs from cloud agents in recent history, and the repo's agent config |
| `resolutions.md` | Overlaps | each project skill whose output overlaps one of mine, judged by what it produces |
| `private-terms` | Terms | the repo's name, its owner on the code host, and the product names in the README |

Run the read-only commands in parallel. In a large repo, hand the survey to one `Explore` agent per area.

### Step 2: Ask once

Put every open question into one AskUserQuestion round of at most four questions. Each question offers the drafted answer as the recommended option. Ask about these whenever the repo doesn't settle them:

- **The tier of unlisted surfaces.** At T2, I read every diff. At T1, the independent review in `/code-build` and `/pr-babysit` reads it, and I sample. Recommend T2 when the project has few tests or its app can't run locally, and T1 otherwise.
- **The production console.** None, read-only queries through an MCP server, or a person who runs scripts. Mutations are always run by a person.
- **Outward widenings.** Which tracker or PR actions here should go ahead without asking, beyond the defaults in AGENTS.md.
- **Overlaps.** The project's skill is the default. When it forbids an action that AGENTS.md lets go ahead, such as replying on my own PR, offer a compose note that allows it.

Skip a question the repo already answered, and leave overlaps that don't fit in the round to the deference protocol, which asks about each the first time it comes up.

### Step 3: Write the missing files

Write each missing file in the format of its template in `~/.claude/context.example/`. Fill the fields from Steps 1 and 2, and put each field's source after it in parentheses: the file or command, or "asked". A field nothing answered says `unknown` and names what would answer it. Never leave a placeholder.

- `risk-tiers.md` keeps the template's tier semantics. Under each tier's default entries, it gives this repo's paths, and its Unlisted line takes the answer from Step 2.
- `escalation.md` takes the template's triggers, plus the widenings from Step 2.
- `delegation.md` lists only the executors Step 1 found.
- `resolutions.md` gets one line per answered overlap.
- `rules.md` starts with the template's header and an empty table, and `checks/` starts empty.
- `private-terms` gets one term per line.

Then run `~/.claude/bin/check`. A tracked file that contains a new private term is a leak in this library, and it goes in the report.

### Step 4: Give agents a way to prove their work

Run `/test-verify`. It writes a private verify skill and feature map when the repo has neither. When the repo's verify skill has no feature map, it writes the map alone. It stops when the repo already has both. When the app can't run locally, the report says so, because that gap comes before any unattended run.

### Step 5: Report

- **Changed**: each file written. Give a count of the fields the repo answered and of the ones I answered. The rest are `unknown`.
- **Existing**: each file that was already there, and the fields it lacks.
- **Proof**: the feature `/test-verify` drove and its evidence path, or why it couldn't drive one.
- **Ready for**: the furthest step the project now supports, and what the next one needs.
  - Supervised runs need test commands.
  - Runs under the stepping-away steer also need `risk-tiers.md` and a verify harness that ran.
  - Unattended `/work-triage` also needs `delegation.md`, `escalation.md`, and a resolution for each overlapping project skill.
- **Check**: the fields marked `unknown` and the risk entries matched by keyword alone. Also list any private term common enough to cause false alarms in `bin/check`.
- **Undo**: `rm` of each file this run wrote, plus the Undo from `/test-verify`'s report.

## Key Rules

1. **Read the repo before asking.** A question is only for what the repo can't show.
2. **Never overwrite a context file.** Draft only the missing ones.
3. **Each field cites its source.** A field nothing answered says `unknown`, never a placeholder.
4. **The risk tiers start from the template's defaults.** The tier of unlisted work is my call.
5. **End with a way to prove work.** `/test-verify` runs before the report.
