# Setup

A clone brings the tracked half only. The rest, such as the Vale binary, its
plugin, its synced styles, and the machine's own config files, lives outside
git. So do the git hooks setting and the agent hooks, which are config on each
machine. `bin/setup` reports which of them a machine is missing, and prints the
fix for each. It runs nothing itself, except that `bin/setup --apply` makes the
Codex links under "Other agents", and makes `context/` a local git repo with its
own pre-commit hook. That run exits 0 once those are made, whatever else is
left, so a bootstrap script can call it.

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

`.githooks/` runs `bin/check` and Vale on every commit, and Vale on the commit
message, whichever agent or person commits. `docs/enforcement.md` lists every
rule that has a mechanism.

## Phone notifications

`bin/hooks/notify_phone.py` sends a push to your phone through
[ntfy](https://ntfy.sh) when an agent stops for you. Claude Code sends one when
a session waits on a permission prompt, or has sat idle at its prompt for about
a minute. Codex sends one at the end of every turn, from a `Stop` hook in
`codex/hooks.json`, because Codex has no idle event.

The topic is the only line of `ntfy-topic` in the repo root, which git
ignores. Use one topic on every machine, and subscribe to it once in the ntfy
app. ntfy.sh is a public server where anyone who knows the topic can read it.
The push contains only the folder name and the event, never conversation text,
and `bin/check` fails a commit that contains the topic.

## Other agents

The global rules are in `AGENTS.md`, which most coding agents read. Claude Code
reads `CLAUDE.md`, so that file imports them with `@AGENTS.md` and adds the
Claude-only rules. Codex reads them through a symlink at `~/.codex/AGENTS.md`.
Cursor has no global rules file. Add a User Rule in Cursor's settings that says
"Read ~/.claude/AGENTS.md at the start of every task."

`codex/` holds a default Codex config: `config.toml.example` (model, reasoning
effort, approvals reviewer), and `rules/default.rules` (approval prefix rules).
It also holds `hooks.json`, which runs the outward guard, the compose notes at
session start, and the phone notification at the end of each turn. Codex runs
the hooks only after you trust them with `/hooks`, and again after each change
to the file. Cursor has no equivalent hook yet.

`bin/setup --apply` makes every Codex link. It copies `config.toml.example` to
`config.toml` when that file is missing, then links `AGENTS.md`, `config.toml`,
`rules/default.rules`, and `hooks.json` into `~/.codex`. Each skill gets its own
link in `~/.codex/skills`, because that directory also holds Codex's own
`.system` skills, and a link to a skill that no longer exists is removed. It
never links `~/.codex` itself, which holds auth and session state. Anything
already at a link's path first moves into a time-stamped `~/.codex/backup-*`
folder.

Codex does not load the agents or commands from this repo. A skill that uses
Claude-only tools, such as scheduling a wake-up, loads in Codex, and Codex stops
at the step that needs the tool. Per-machine project trust entries stay out of
`config.toml`. Codex adds them to the live file itself.
