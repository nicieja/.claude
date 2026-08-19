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
- `marketer` — positioning, narrative, and copy that teaches the buyer how to buy
- `performance-engineer` — diagnoses bottlenecks and engineers optimizations
- `product-manager` — product strategy, prioritization, and roadmap decisions
- `prompt-engineer` — designs and evaluates prompts for production LLM systems
- `security-auditor` — vulnerability assessment and compliance review
- `software-engineer` — principal-level implementation with taste in naming and abstraction
- `tester` — test strategy, design, automation, and CI integration as one craft

## Skills (`skills/`)

User-invocable slash commands with multi-step workflows.

- `/10x` — paint the platonic ideal of an artifact and surface the gap
- `/comment` — post conversation findings as a Linear comment
- `/deslop` — strip AI slop from prose and comments without changing meaning
- `/investigate` — diagnose production issues via read-only console scripts, then dry-run fixes
- `/learn` — turn a session's corrections into durable harness improvements
- `/pushback` — anti-sycophantic challenge framework; six forcing questions
- `/query` — verify one claim about runtime state with one read-only script
- `/quiz` — short quiz on the crucial decisions behind a PR/doc so you can defend it in review
- `/retro` — extract learning from a shipped piece of work
- `/review-pr` — differential PR review: post only what bots and prior reviewers haven't said
- `/self-heal` — repair accretion debt across this library without regressing behavior
- `/shape` — turn a half-formed idea into a refined plan via research and adversarial review
- `/summary` — humanized Slack summary of an investigation
- `/triage` — dispatch tracker issues through parallel, tiered, repo-aware pipelines to draft PRs
- `/voice` — re-voice an English draft in the author's own literary voice

## Commands (`commands/`)

Thin slash-command wrappers.

- `/ack` — acknowledge external file changes
- `/commit` — create a focused git commit
- `/linear` — write a title and description for a Linear issue
- `/push` — open a pull request
- `/setup` — arm this session's recurring loops from the project's routine prompts
- `/simple` — restate the last message in Simplified Technical English
- `/standup` — humanized standup update from a seed

## The context layer (`context/`)

The tracked library is mechanism; configuration is private. `context/<project>/`
(gitignored) holds each project's charter, risk tiers, escalation contract, stack
notes, remembered skill resolutions, and decision log — see `context.example/`
for the shape of each file. Skills read the active project's context at runtime
and degrade gracefully when a file is missing.

Repos can also carry their own skills; this library defers to them — it detects
overlap, asks once, and remembers the answer per repo. Nothing project- or
employer-specific ever appears in tracked files.
