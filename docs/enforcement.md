# What enforces what

A rule in prose works only when an agent reads it and follows it. These rules
also have a mechanism that fails when someone breaks them, whichever agent or
person did it. Rules without a mechanism stay in `AGENTS.md` and the skills,
and aren't listed here.

When a correction recurs, `/self-improve` moves its rule up a level: from prose
to a test or a check, and then to a structure that makes the mistake
impossible. Add a row here when a rule gets its mechanism.

| Rule | Stated in | Enforced by |
|---|---|---|
| Prose has no AI tells: em dashes, stock vocabulary, tricolons, and the rest of the `ai-tells` rules | README, "Prose linting" | Vale, through the Claude Code edit hook and `.githooks/pre-commit` |
| A commit message has no AI tells | README, "Prose linting" | `.githooks/commit-msg`, with Vale's commit-message rules |
| Every backticked `/<skill>` reference names a skill, a command, or a known built-in | This file | `bin/check` |
| The trigger map and the skills directory agree, in both directions | `AGENTS.md`, "Trigger map" | `bin/check` |
| A skill's frontmatter `name` matches its directory, and an agent's matches its file | README | `bin/check` |
| A `~/.claude/skills/<skill>/<file>` path that a file cites exists | This file | `bin/check` |
| Tracked files don't contain project- or employer-specific words | `AGENTS.md`, "The context layer" | `bin/check` and `.githooks/commit-msg`, with the words from each `context/<project>/private-terms` |
| Tracked files and commit messages don't contain the ntfy topic | README, "Phone notifications" | `bin/check` and `.githooks/commit-msg`, with the topic from `ntfy-topic` |
| Tracked files outside `docs/references/` don't credit where an idea came from | `AGENTS.md`, "The context layer" | `bin/check` |
| A command in the trigger map has no `allowed-tools` line, because the model can't load such a command through the Skill tool | This file | `bin/check` |
| A skill that acts, then reports (its Instructions open with "Acting and confirming follow"), has Check and Undo parts in its report | `AGENTS.md`, "When to act and when to confirm" | `bin/check` |
| A comment or message posted under my account ends with the signature line | `AGENTS.md`, "When to act and when to confirm" | `bin/hooks/outward_guard.py`, a pre-tool hook in Claude Code and Codex |
| Merges, stacked merges included, approving or change-requesting reviews, and force pushes wait for my OK | `AGENTS.md`, "When to act and when to confirm" | `bin/hooks/outward_guard.py` |
| Each hook does what its docstring says, on the cases in its test table | This file | `bin/hooks/test_hooks.py`, which `bin/check` runs |
| A compose note in `context/<project>/resolutions.md` applies whenever its project skill runs | `AGENTS.md`, "Project skills take precedence" | `bin/hooks/compose_notes.py`, which adds the notes at session start, after `/compact`, and when the skill loads |
| In conversation mode, every reply is short | `commands/conversation.md` | `bin/hooks/conversation_mode.py`, which repeats the rules on every prompt while the mode is on |

## The mechanisms

- **`bin/check`** reads the tracked files, plus new files that git doesn't ignore. Run it by hand, or let the
  pre-commit hook run it.
- **`.githooks/`** runs on every commit in this repo once `core.hooksPath`
  points at it. `bin/setup` reports when it doesn't. `git commit --no-verify`
  skips it.
- **The outward guard** is configured per tool. Claude Code loads it from
  `settings.json`, whose `hooks` block is in `settings.json.example`. Codex loads
  it from `~/.codex/hooks.json`, a symlink to `codex/hooks.json`, after you trust
  it with `/hooks`, and again after each change to the file. Cursor has no hook yet, so the prose rule is its only
  guard.
- **The compose-notes hook** runs in Claude Code on SessionStart,
  UserPromptExpansion, and PostToolUse for the Skill tool, from the same
  `hooks` block. Codex runs it on SessionStart only, from `codex/hooks.json`.
  Cursor has no hook. There, the AGENTS.md rule is the only guide. A line it can't
  parse goes into the context at session start, for the agent to quote to me.
- **The conversation-mode hook** runs in Claude Code only, from the same
  `hooks` block. `/conversation` turns the mode on or off for one session, and
  the mode is on while `~/.cache/agent-modes/conversation/<session_id>` exists.
