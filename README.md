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
git. `bin/setup` reports which of them a machine is missing, and prints the fix
for each. It runs nothing itself.

```bash
~/.claude/bin/setup
```

## Agents

There are two agents, and each exists because a skill needs a context smaller
than the conversation's.

`persona` plays one buyer for `/market-rehearse`. It has no tools and knows only
its brief. A buyer who could read the repo would hand your own value
proposition back to you as a discovery.

`reviewer` takes a brief from a skill and applies the skill that the brief
points to, such as `/idea-challenge` or `/pr-critique`. It can read code and run
tests, and it can't change a file. It never sees the reasoning that produced the
work, so its challenge or review is independent.

The expertise is in the skills, and the agents add only the isolation. Any
tool that reads skills can run them. A tool without subagents runs the same
skill inline, with a weaker check.

## Skills

A skill is a workflow I don't trust myself to improvise, usually because the
moment it runs is the moment I'm in a hurry. Each is multi-step, most stop at a
checkpoint instead of running to the end, and each is allowed to come back with
nothing.

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

`codex/` holds a default Codex config: `config.toml` (model, reasoning
effort, approvals reviewer) and `rules/default.rules` (approval prefix rules).
Codex does not load the agents, skills, or commands from this repo. Per-machine
project trust entries stay out. Codex adds them to the live file itself.
