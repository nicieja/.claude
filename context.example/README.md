# The context layer

The tracked library is mechanism. This directory documents the configuration. Real
configuration is stored in `~/.claude/context/<project>/`, which is gitignored, with one directory per
project, named after the repo's directory name. Skills load what they need from the
active project's context directory at runtime.

Copy any template here into `context/<project>/` and fill it in. When a skill needs a
file that doesn't exist, it degrades gracefully. It asks once and offers to scaffold the
file from these templates, and it defaults to the conservative behavior (unknown risk =
high risk, unknown metric = ask).

Files:

- `charter.md`: what this project is aiming for, the primary metric and how it is
  computed, targets, and guardrails.
- `risk-tiers.md`: what work is safe to automate here and what always needs a human.
- `escalation.md`: when agents must stop and page the user, and how.
- `stack.md`: tracker, code host, error tracking, console access, schema locations,
  test commands, conventions. The file skills consult before touching the project.
- `resolutions.md`: remembered answers to project-skill conflicts. Written by skills.
- `decisions.md`: a dated log of non-obvious calls and why they were made.
- `review-focus.md`: cached map of the code areas the user is responsible for and actively
  touches, used to focus a review. Written by `/review-pr`. Refreshes after ~30 days.
- `routines/`: prompt sources for scheduled runs (private by nature).

Nothing in `context/` is ever tracked. Project-specific content never leaves it.
