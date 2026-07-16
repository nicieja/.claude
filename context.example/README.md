# The context layer

The tracked library is mechanism; this directory documents the configuration. Real
configuration lives in `~/.claude/context/<project>/` — gitignored, one directory per
project, named after the repo's directory name. Skills load what they need from the
active project's context directory at runtime.

Copy any template here into `context/<project>/` and fill it in. When a skill needs a
file that doesn't exist, it degrades gracefully: it asks once, offers to scaffold the
file from these templates, and defaults to the conservative behavior (unknown risk =
high risk, unknown metric = ask, no roster = ask).

Files:

- `charter.md` — what this project is optimizing, the primary metric and how it is
  computed, targets, guardrails, and the shape of the periodic review.
- `risk-tiers.md` — what work is safe to automate here and what always needs a human.
- `escalation.md` — when agents must stop and page the user, and how.
- `stack.md` — tracker, code host, error tracking, console access, schema locations,
  test commands, conventions. The file skills consult before touching the project.
- `partners.md` — the customer/partner roster for prep and debrief workflows.
- `resolutions.md` — remembered answers to project-skill conflicts. Written by skills.
- `decisions.md` — a dated log of non-obvious calls and why they were made.
- `routines/` — prompt sources for scheduled runs (private by nature).

Nothing in `context/` is ever tracked. Nothing project-specific ever leaves it.
