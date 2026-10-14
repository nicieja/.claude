# The context layer

The tracked library is mechanism. This directory documents the configuration. Real
configuration is stored in `~/.claude/context/<project>/`, which is gitignored, with one directory per
project, named after the repo's directory name. Skills load what they need from the
active project's context directory at runtime.

`~/.claude/context/` is a local git repo of its own, with no remote, and `bin/setup --apply`
creates it. Its files state the current setup, so they're edited in place, and git keeps
what they said before. Commit each write with
`git -C ~/.claude/context commit -m '<what, and why>' -- <paths>`, and undo one with
`git -C ~/.claude/context revert <sha>`. The repo's pre-commit hook runs
`bin/check --context`.

`/work-bootstrap` drafts the missing files for a repo from what the repo shows, and asks
once about the rest. To start by hand, copy a template here into `context/<project>/`
and fill it in. When a skill needs a
file that doesn't exist, it degrades gracefully. It asks once and offers to scaffold the
file from these templates, and it defaults to the conservative behavior (unknown risk =
high risk, unknown metric = ask).

Files:

- `charter.md`: what this project is aiming for, the primary metric and how it is
  computed, targets, and guardrails.
- `risk-tiers.md`: what work is safe to automate here and what always needs a human.
- `escalation.md`: when agents must stop and page the user, and how, plus the outward
  actions this project allows without asking.
- `delegation.md`: who can build work in this project (local subagents, `codex exec`, cloud
  agents), how to hand work over, and how results come back.
- `stack.md`: tracker, code host, error tracking, console access, schema locations,
  test commands, conventions. The file skills consult before touching the project.
- `resolutions.md`: remembered answers to project-skill conflicts. Written by skills.
  `bin/hooks/compose_notes.py` hands its compose notes to the repo's own skills.
- `decisions.md`: the non-obvious calls in force, one entry per decision under a topic, each
  with why it was made and who made it. Other files cite an entry by its heading.
- `routines/`: scheduled prompts and restartable `/loop` routines, with each loop's lock,
  ledger, and scripts. `routines/README.md` documents them, and `/setup` starts them.
- `rules.md`: the project's rules that agents keep breaking, each with what enforces it.
- `checks/`: private checks that enforce those rules for my agents, without changing the
  team's repo. `checks/README.md` has the contract.
- `verify/`: a private verify skill and its feature map, or only a feature map when the
  repo's own verify skill has none. Written by `/test-verify`.
- `private-terms`: words that tracked files in this library must never contain. `bin/check`
  and the commit-msg hook read it.

The library never tracks anything in `context/`. The local context repo versions it, and
project-specific content never leaves it.
