# .claude

My personal [Claude Code](https://claude.com/claude-code) configuration — agents, slash commands, and skills loaded from `~/.claude/`.

Open-sourced so others can crib from it. It's opinionated; most pieces here reflect how I prefer to work, not best practices for everyone. Treat it as a reference, not a drop-in.

Three kinds of thing live here. Agents are *who* you ask. Skills are *how* the work gets run. Commands just remove typing.

## Install

If you don't already have a `~/.claude/`, you can clone directly:

```bash
git clone git@github.com:nicieja/.claude.git ~/.claude
```

If you do, **don't overwrite it**. Clone elsewhere and copy or symlink individual pieces:

```bash
git clone git@github.com:nicieja/.claude.git ~/code/nicieja-claude
ln -s ~/code/nicieja-claude/skills/pushback ~/.claude/skills/pushback
```

## Agents

An agent is a named professional with an opinion, pulled in for one question,
then gone. The point isn't extra hands. It's disagreement: each takes a position
and defends it with evidence, because an assistant that agrees with you is worth
nothing on the decision you're about to get wrong.

Some implement a slice with taste in naming and abstraction, then clean it
without changing behavior. Others review from one named angle, because a change
can be wrong in ways that don't overlap; the generalist takes correctness and
dispatches the specialists in parallel. Some hold no write tools, on the theory
that finding a gap and closing it are different jobs. The rest aren't
engineering, split on purpose: one makes a proposal its strongest version, one
works out how it gets sold, one breaks it. An agent that both strengthens and
breaks does neither.

## Skills

A skill is a workflow I don't trust myself to improvise, usually because the
moment it runs is the moment I'm in a hurry. Each is multi-step, each stops at a
checkpoint instead of running to the end, and each is allowed to come back with
nothing.

Together they cover the arc of a piece of work: shaping an idea and grilling it
while it's still cheap to change, dispatching and diagnosing once it's underway,
hunting what the bots and earlier reviewers missed before it ships, writing it
up for whoever needs it, and turning the corrections into changes to the harness
itself — this library included.

Three rules matter more than any single step. No invented numbers: a figure that
can't be computed appears as a named gap, never an estimate dressed as a
measurement. Where production is involved it stays read-only: an agent writes
the script, a human runs it, the output comes back as a paste. And an honest
"nothing here" is a finished result — no lesson, no finding, no cut left to
make, said plainly instead of padded into something that looks like work.

## Commands

Commands are the opposite: no workflow, no checkpoint, no judgment. Each runs a
few shell commands, drops the output into the prompt, and asks for one piece of
writing I'd otherwise type from scratch. What they save is the paste.

The line between the two is that checkpoint. Anything that has to stop and ask
belongs on the other side of it.

## The context layer

The tracked library is mechanism; configuration is private. `context/<project>/`
(gitignored) holds each project's charter, risk tiers, escalation contract, stack
notes, remembered skill resolutions, and decision log — see `context.example/`
for the shape of each file. Skills read the active project's context at runtime
and degrade gracefully when a file is missing.

Repos can also carry their own skills; this library defers to them — it detects
overlap, asks once, and remembers the answer per repo. Nothing project- or
employer-specific ever appears in tracked files.

## Other agents

`codex/` holds a default Codex config: `config.toml` (model, reasoning
effort, approvals reviewer) and `rules/default.rules` (approval prefix rules).
Codex does not load the agents, skills, or commands from this repo. Per-machine
project trust entries stay out; Codex adds them to the live file itself.
