# .claude

My personal [Claude Code](https://claude.com/claude-code) configuration — agents, slash commands, and skills loaded from `~/.claude/`.

Open-sourced so others can crib from it. It's opinionated; most pieces here reflect how I prefer to work, not best practices for everyone. Treat it as a reference, not a drop-in.

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

## Agents (`agents/`)

Subagents Claude Code dispatches via the Agent tool.

- `architect-reviewer` — reviews system designs for scalability, coupling, and evolution risks
- `ceo` — founder-CEO archetype that grills proposals before execution
- `code-reviewer` — multi-domain code review that dispatches specialists in parallel
- `code-simplifier` — refactors functional code for readability
- `firefighter` — weekly support / production-fire rotation pair-partner
- `performance-engineer` — diagnoses bottlenecks and engineers optimizations
- `product-manager` — product strategy, prioritization, and roadmap decisions
- `prompt-engineer` — designs and evaluates prompts for production LLM systems
- `security-auditor` — vulnerability assessment and compliance review
- `tester` — test strategy, design, automation, and CI integration as one craft

## Skills (`skills/`)

User-invocable slash commands with multi-step workflows.

- `/shape` — turn a half-formed idea into a refined plan via codebase + web research, CEO challenge, and specialist pushback
- `/estimate` — honest estimate with codebase exploration and recursive break-down
- `/investigate` — diagnose production issues via console scripts (read-only diagnostic, then dry-run fix)
- `/pushback` — anti-sycophantic challenge framework; six forcing questions
- `/retro` — extract learning fro a piece of work
- `/summary` — write an investigation summary
- `/triage` — fetch unassigned tickets and orchestrate parallel pipelines through PR

## Commands (`commands/`)

Thin slash-command wrappers for git and Linear.

- `/ack` — acknowledge external file changes
- `/commit` — create a focused git commit
- `/learn` — document insights from the session into skills
- `/linear` — write a title and description for a Linear issue
- `/push` — open a pull request
