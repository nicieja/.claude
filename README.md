# .claude

My personal [Claude Code](https://claude.com/claude-code) configuration: agents, slash commands, and skills loaded from `~/.claude/`.

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
