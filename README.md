# .claude

My personal [Claude Code](https://claude.com/claude-code) configuration: agents, slash commands, and skills loaded from `~/.claude/`.

Open-sourced so others can crib from it. It's opinionated: most pieces reflect how I prefer to work, not best practices. Treat it as a reference and not as a drop-in.

Skills, commands, and two agents are the kinds of thing here. Skills are _how_ the work gets run, and commands just remove typing. An agent gives a skill a context of its own.

## Install

If you don't have a `~/.claude/` yet, clone it directly:

```bash
git clone git@github.com:nicieja/.claude.git ~/.claude
```

A clone brings the tracked half only. The rest, such as the Vale binary, its
plugin, its synced styles, and the machine's own config files, lives outside
git. So do the git hooks setting and the agent hooks, which are config on each
machine. `bin/setup` reports which of them a machine is missing, and prints the
fix for each. It runs nothing itself.

```bash
~/.claude/bin/setup
```

## Agents

There are three agents, and each exists because a skill needs a context smaller
than the conversation's.

`persona` plays one buyer for `/market-rehearse`. It has no tools and knows only
its brief. A buyer who could read the repo would hand your own value
proposition back to you as a discovery.

`reviewer` takes a brief from a skill and applies the skill that the brief
points to, such as `/idea-challenge` or `/pr-critique`. It can read code and run
tests, and it can't change a file. It never sees the reasoning that produced the
work, so its challenge or review is independent.

`comment-editor` deletes comments for `/code-uncomment`, and it's the one agent
that edits files. It may delete a comment or a lint suppression, and nothing
else. The skill then audits its diff and reverts anything that isn't a deleted
comment.

The expertise is in the skills, and the agents add only the isolation. Any
tool that reads skills can run them. A tool without subagents runs the same
skill inline, with a weaker check.

## Skills

A skill is a workflow I don't trust myself to improvise, usually because the
moment it runs is the moment I'm in a hurry. Each is multi-step, and each is
allowed to come back with nothing. A skill acts on what it finds, then reports
what changed, what to check, and the command that undoes it. It waits for me
only when the undo would cost real work, or before a post or a push outside my
own PRs and issues. Its comments under my account are signed as the agent's.
`AGENTS.md` has the rule, under "When to act and when to confirm".

Together they cover the arc of a piece of work: refining an idea and grilling it
while it's still cheap to change, then dispatching and diagnosing once it's
underway. Later they hunt what the bots and earlier reviewers missed before it
goes out and write it up for whoever needs it. At the end, the corrections turn
into changes to the harness itself, this library included.

A few rules matter more than any step. Numbers are not invented: a figure that
can't be computed appears as a named gap and never as an estimate presented as
a measurement. Where production is involved, everything is read-only. An agent
writes the script and a human runs it. The output comes back as a paste. And an
honest "nothing here" is a finished result, without a lesson, a finding, or a
cut left to make. It is said plainly instead of padded into something that looks
like work.

## Commands

Commands are the opposite, without a workflow, a checkpoint, or judgment. Each
runs a few shell commands and drops the output into the prompt, then asks for
one piece of writing I'd otherwise type from scratch. They save the paste.

The line between the two is judgment. Anything that has to stop and ask, or
has to decide what to keep and what to cut, belongs on the other side of it.

`/conversation` is different, because it changes how the session talks.
Running it once turns on short, chat-like replies, and running it again turns
them off. A hook in `bin/hooks/conversation_mode.py` repeats the rules on
every prompt while the mode is on, so they still apply after `/compact`. It
works in Claude Code only.

## Prose linting

Vale lints the prose in this repo and the prose Claude writes anywhere else. It
runs as a Claude Code plugin hook: after every Write or Edit to a Markdown or
text file, Vale checks it and returns any error-level alert to Claude in the
same turn. The rules are the `ai-tells` package, which flags the fingerprints
of machine-written prose (overused vocabulary, stock openings, contrastive
formulas, chatbot sign-offs), plus a small `deslop` style of my own
under `vale/styles/`. The config is `vale/.vale.ini`; Vale finds it because its
user-level directory is a symlink into this repo.

Every ai-tells rule comes at error level, the ini keeps it there, and the prose
in this repo passes the full rule set. The one exception is the commit-message
section, where the Co-Authored-By trailer that Claude Code requires is exempt
from two rules, because a git trailer is not prose.

Vale catches wording-level tells only. Whether a passage contains any
information is still `/code-deslop`'s job.

## Enforcement

A rule an agent can skip is a weaker rule than one that fails when it's broken.
`docs/enforcement.md` lists the rules here that have a mechanism, and what the
mechanism is:

- `bin/check` lints the library itself: references between skills, the trigger
  map, frontmatter, and words that belong to a private project.
- `.githooks/` runs `bin/check` and Vale on every commit, and Vale on the commit
  message, whichever agent or person commits.
- `bin/hooks/outward_guard.py` is a pre-tool hook. It denies a comment posted
  under my account without the signature line. It also denies a merge, a force
  push, or an approving review, which wait for me.

## The context layer

The tracked library is mechanism, and configuration is private.
`context/<project>/` (gitignored) contains each project's charter, risk tiers,
escalation contract, stack notes, remembered skill resolutions, and decision log.
See `context.example/` for the format of each file. Skills read the active
project's context, and keep working when a file is missing.

Repos can also have their own skills, and this library defers to them. It
detects overlap and asks once, then remembers the answer per repo. Nothing project- or
employer-specific ever appears in tracked files.

## Other agents

The global rules are in `AGENTS.md`, which most coding agents read. Claude Code
reads `CLAUDE.md`, so that file imports them with `@AGENTS.md` and adds the
Claude-only rules. Codex reads them through a symlink at `~/.codex/AGENTS.md`,
and `bin/setup` reports when it is missing. Cursor has no global rules file. Add
a User Rule in Cursor's settings that says "Read ~/.claude/AGENTS.md at the
start of every task."

`codex/` holds a default Codex config: `config.toml` (model, reasoning
effort, approvals reviewer) and `rules/default.rules` (approval prefix rules).
It also holds `hooks.json`, which runs the outward guard. `~/.codex/hooks.json`
is a symlink to it, and Codex runs it only after you trust it once with
`/hooks`. Cursor has no equivalent hook yet.
Codex does not load the agents, skills, or commands from this repo. Per-machine
project trust entries stay out. Codex adds them to the live file itself.
