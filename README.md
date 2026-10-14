# .claude

My Claude Code setup.

Working with coding agents, I spent most of my time watching them, reading
every turn and correcting course. When I stepped away, the work drifted. More
agents wouldn't have fixed that. I can't hand an agent a task and leave until I
trust the result, and that trust has to come from the environment the agent
works in. A better prompt won't supply it. Each part of this repo builds a piece
of that environment.

## Install

```bash
git clone git@github.com:nicieja/.claude.git ~/.claude
~/.claude/bin/setup
```

A clone brings only the tracked half. `bin/setup` reports which machine-local
pieces are missing, such as the prose linter, the agent hooks, the git hooks,
and phone notifications, and prints the fix for each. It runs nothing itself,
except that `bin/setup --apply` fills in the Codex config and makes the Codex
links. [docs/setup.md](docs/setup.md) covers each piece, and how Codex and
Cursor read the same rules.

## Skills

Each skill writes down one of my playbooks, such as how I review a diff or
debug an incident. Verification shows that a feature works, and the skills
cover what it can't: whether the code is any good. That judgment used to work
only while I watched. The skills run when the conversation matches them, so
nobody has to remember to call one.

Most heavy users of agents keep a library like this by now, and little in mine
is unusual. A repo's own skills encode that project's law and take precedence
over mine. When one of mine overlaps with one of theirs, the agent asks once
which to use and remembers the answer for that repo.

## The context layer

The library is mechanism, and configuration is private. Everything specific to
one project is stored in a gitignored directory per repo. That covers the
project's goal and its metric, the risk tiers that say which work is safe to
automate, the escalation contract that says when an agent stops to ask, and the
stack. A decisions file states the non-obvious calls in force, and a local git
repo keeps what they said before, so a changed call is an edit and not a new
entry. Skills read the active
project's context before they act.

A missing file isn't an error. The agent asks once and offers to draft the file
from what the repo shows. Until then it reads every gap conservatively: an
unknown risk is a high risk, and an unknown metric means ask. A check fails any
commit that would put a project's or an employer's name in a tracked file.

## Verification

An agent's claim counts only after something has checked it. That holds for
the work, and for the rules the agent works under.

### Proving the work

An agent proves a change by running it, because reading a diff proves little.
Each project gets a harness with two parts. A script launches the app, drives
it the way a user would, and collects evidence the same way in every session.
A feature map records what each feature does and how a user reaches it, so an
agent handed a vague bug report doesn't have to guess which screen it's about.

Every claim in a report says how the agent knows it: measured, inferred, or a
guess. When running something would settle a question about behavior, output,
or timing, the agent runs it before it asks me.

### Enforcing the rules

A rule written in prose works only when an agent reads it and follows it. A
rule with a mechanism fails when someone breaks it, whichever agent or person
did. So each correction I give goes to the strongest level that can enforce
it:

1. Make the mistake impossible, with one source of truth, a type, a module
   boundary, or a hook.
2. A check whose error message says the fix, such as a lint rule, CI, or a
   commit hook.
3. A test.
4. Prose in a skill or a rules file, last.

The codebase is stronger than all four, because agents copy what they see. One
workaround, one guard against a state that can't happen, or one comment that
excuses a hack becomes the pattern the next agent extends. So the skills that
delete needless armor and comments are enforcement too. My own review is the
weakest layer, since I can't read every line. A correction I give in review
points to a gap in a stronger layer, and when the same correction comes back,
`/self-improve` moves its rule up a level.

Prose gets the same treatment. A linter checks every Markdown file an agent
writes, in the turn it writes it, and flags the fingerprints of machine-written
text, from stock vocabulary to chatbot sign-offs. Commit hooks run it again,
with the library's own checks, whoever commits. The linter checks wording only.
Whether a passage contains any information is still `/code-deslop`'s job.

Hooks also guard what's hard to take back. A merge, a force push, or an
approving review waits for me. A comment posted under my name without the line
that says an agent wrote it is blocked before it goes out.

In a team repo, I can't rework the architecture or add CI for my agents alone.
Private checks fill that gap. They live in the project's context and run for my agents only, and moving
one into the team's repo is a proposal to its owners.

## Running without me

Everything above exists so I can leave.

An agent acts on what it finds, then reports what changed and what I should
check. Each report ends with the exact command that undoes it. It asks first
only when the undo costs real work, such as a history rewrite, or before an
outward action the project hasn't cleared. Merges, deploys, and production changes
always wait for me. Calls that are mine, like a failure policy or a behavior
change I didn't ask for, get batched into one set of questions at the end, so
the rest of the work doesn't stall behind them.

When I say I'm stepping away, the agent sets a finish condition, a check that
passes or fails, and gets more room. It commits, pushes its own branch, opens
draft PRs, picks a reversible default for each of my decisions, and logs every
one with its reason.

Routines are the longest unattended runs. A scheduled routine is a prompt on a timer. A loop
works through a campaign one wake at a time, such as a stack of PRs to bring to
ready-to-merge, and a restart picks it up where the last wake stopped:

- Each wake rebuilds its view from the sources I'd check myself: the tracker,
  the code host, and the error tracker. There's no separate memory, and a
  ledger records only what those sources don't.
- A lock keeps two sessions from running the same loop.
- Before an outward action, the loop writes the action's key to the ledger, so
  a restart after a crash never sends the same thing twice.
- A question for me pauses only the items that depend on it, and the loop keeps
  working on the rest.
- When nothing is left but my questions, the loop stops, and my phone gets a
  push.

## Codex

The global rules are written once, in the file most coding agents read. Claude
Code imports it and adds a few rules of its own, and Codex reads it as its
global instructions. The hooks that block an unsigned post or a merge without
my OK run in Codex too, along with the compose notes and the phone ping, so the
same limits apply whichever agent is working. Commit hooks run on every commit,
from either agent.

Codex loads the same skills, which the setup script links in one by one. Some
use tools Codex doesn't have, such as scheduling a wake-up. When Codex reaches
a step that needs one, it stops and says the step needs Claude Code, instead of
working around it. `/work-delegate` hands work to Codex first. It writes a
self-contained brief, runs `codex exec` in its own worktree, and later reviews
the PR that comes back. When Codex stopped partway, the Claude session that
picks up the results finishes the task from that step.
