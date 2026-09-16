# .claude

My personal [Claude Code](https://claude.com/claude-code) configuration: agents, slash commands, and skills loaded from `~/.claude/`.

Open-sourced so others can crib from it. It's opinionated; most pieces here reflect how I prefer to work, not best practices for everyone. Treat it as a reference and not as a drop-in.

Agents, skills, and commands are the kinds of thing here. Agents are *who* you ask. Skills are *how* the work gets run. Commands just remove typing.

## Install

If you don't already have a `~/.claude/`, you can clone directly:

```bash
git clone git@github.com:nicieja/.claude.git ~/.claude
```

## Agents

An agent is a named professional with an opinion, pulled in for one question,
then gone. The purpose is disagreement rather than extra hands: each takes a
position and defends it with evidence, because an assistant that agrees with you
is useless on the decision you're about to get wrong.

Some build a slice with taste in naming and abstraction, then clean it
without changing behavior. Others review from one named angle, because a change
can be wrong in ways that don't overlap; the generalist takes correctness and
dispatches the specialists in parallel. Some are configured without write tools,
on the theory that finding a gap and closing it are different jobs. The rest aren't
engineering, split on purpose: one makes a proposal its strongest version, one
works out how it gets sold, one breaks it. An agent that both strengthens and
breaks does neither.

## Skills

A skill is a workflow I don't trust myself to improvise, usually because the
moment it runs is the moment I'm in a hurry. Each is multi-step and stops at a
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

The line between the two is that checkpoint. Anything that has to stop and ask
belongs on the other side of it.

## Prose linting

Vale lints the prose in this repo and the prose Claude writes anywhere else. It
runs as a Claude Code plugin hook: after every Write or Edit to a Markdown or
text file, Vale checks that file and any error-level alert comes back to Claude
in the same turn. The rules are the `ai-tells` package, which flags the
fingerprints of machine-written prose (overused vocabulary, stock openings,
contrastive formulas, chatbot sign-offs), plus a small `deslop` style of my own
under `vale/styles/`. The config is `vale/.vale.ini`; Vale finds it because its
user-level directory is a symlink into this repo.

Every ai-tells rule comes at error level and the ini keeps it there. The hook
relays all of them, and the prose in this repo passes the full rule set. The one exception is the commit-message section of the ini. There, the
Co-Authored-By trailer that Claude Code requires is exempt from two rules,
because a git trailer is not prose.

Vale catches wording-level tells only. Whether a passage contains any
information is still `/deslop`'s job.

```bash
brew install vale
claude plugin marketplace add vale-cli/agent-tools
claude plugin install vale@agent-tools
rm -r ~/Library/Application\ Support/vale && ln -s ~/.claude/vale ~/Library/Application\ Support/vale
(cd ~/.claude/vale && vale sync)
```

## The context layer

The tracked library is mechanism, and configuration is private.
`context/<project>/` (gitignored) contains each project's charter, risk tiers,
escalation contract, stack notes, remembered skill resolutions, and decision log.
See `context.example/` for the format of each file. Skills read the active project's context at runtime
and degrade gracefully when a file is missing.

Repos can also have their own skills, and this library defers to them. It
detects overlap and asks once, then remembers the answer per repo. Nothing project- or
employer-specific ever appears in tracked files.

## Other agents

`codex/` holds a default Codex config: `config.toml` (model, reasoning
effort, approvals reviewer) and `rules/default.rules` (approval prefix rules).
Codex does not load the agents, skills, or commands from this repo. Per-machine
project trust entries stay out. Codex adds them to the live file itself.
