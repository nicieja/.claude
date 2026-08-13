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

## A week in the loop

The sections below are a catalog; this is how they compose. The example assumes the
fullest version of the job: you own a product end to end — its metric, its
customers, its roadmap, its code — and you'd rather run a fleet of agents than
write every line yourself. The design splits into three planes: work flows through
pipelines, trust is earned per risk tier, and what you learn routes back into the
harness. Everything project-specific in this story — the metric definition, the
risk tiers, the partner roster, where the schema lives — comes from
`context/<project>/`, which is gitignored; the tracked skills are pure mechanism.
On the first run in a fresh project, skills notice what's missing, offer to
scaffold it from `context.example/`, and default to the conservative reading until
you fill things in.

**Monday starts with `/brief`, not a blank terminal.** It reads whatever sources
the session actually has — your open PRs and their checks, the tracker queue, the
fleet's telemetry, the error tracker, today's calendar — and compresses them into
what moved, what's blocked on you, and a suggested plan. The section that matters
is *Blocked on you*: every item waiting on a decision, each with a recommended
action. Anything it couldn't reach is listed as skipped, never inferred.

**You dispatch, not implement.** Two tracker issues look shaped enough to build,
so `/triage` sends each through its pipeline — understand, design, build, verify,
review — in its own git worktree, in parallel. How much rope each issue gets is
not a mood: `risk-tiers.md` assigns every issue a tier, and tiers govern autonomy.
A docs fix (T0) flows to a draft PR on its own. The billing-webhook change (T3)
never auto-advances — every stage gate waits for you, and mid-run discoveries only
raise tiers, never lower them. Builders end with an evidence bundle — what
changed, why this shape, what ran, residual risk, rollback — so review starts from
evidence instead of reading every line.

**The repo's own workflow outranks yours.** When a project carries its own skills
— its own shaping doc, its own verify or PR flow — your skills detect the overlap
and ask once: use the project's, use mine, or compose. The answer lands in
`resolutions.md`, and later runs follow it silently. Unattended runs never guess:
an unresolved conflict means that work is skipped and reported, not decided by a
bot in someone else's repo.

**Wednesday is a customer call.** `/prep-call <partner>` builds a one-page brief
from the roster and the insight log: where the relationship stands, commitments in
both directions, and the two or three hypotheses this call should test. Afterwards
`/debrief-call` files what was actually learned — load-bearing claims as verbatim
quotes, commitments with an owner and a date, commercial signals — into
`insights.md` and updates the roster row. The insight log is the memory the
customer loop runs on.

**Something breaks Thursday.** `/investigate` explores the code, then generates
read-only console scripts for you to run in production — agents never touch
production directly — and iterates on the pasted output until the root cause is
confirmed. Fixes arrive as dry-run-first scripts; console flavor and schema
locations come from `stack.md`.

**Friday, `/weekly` drafts the review your charter defines** — metric movement,
what shipped, what was learned, the one top blocker, and the change shipped in
response. Its rule is the whole point: the draft never types a number it didn't
compute in that run; anything uncomputable appears as an explicit
`[needs manual number: …]` gap, never an estimate. You fill the gaps, edit, and
post it yourself — it never posts anywhere.

**The loop compounds.** `/learn` turns the week's corrections into harness patches
routed to the smallest durable home; `/retro` extracts lessons from the shipped
work; `/self-heal` keeps these prompt files themselves from accreting into
changelogs. Automation stays pull-based: schedule `/brief` and `/weekly` only once
the loop has demonstrably recurred — an automation you stop using is a failed
automation.

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
- `software-engineer` — principal-level implementation with taste in naming and abstraction
- `tester` — test strategy, design, automation, and CI integration as one craft

## Skills (`skills/`)

User-invocable slash commands with multi-step workflows.

- `/10x` — paint the platonic ideal of an artifact and surface the gap
- `/brief` — morning brief and decision inbox from live sources; schedulable
- `/comment` — post conversation findings as a Linear comment
- `/debrief-call` — file a partner call into the insight log with verbatim quotes
- `/deslop` — strip AI slop from prose and comments without changing meaning
- `/estimate` — honest estimate with codebase exploration and recursive break-down
- `/investigate` — diagnose production issues via read-only console scripts, then dry-run fixes
- `/learn` — turn a session's corrections into durable harness improvements
- `/voice` — re-voice an English draft in the author's own literary voice
- `/prep-call` — one-page brief before a customer or partner call
- `/prototype` — smallest working build to answer one question, throwaway by design
- `/pushback` — anti-sycophantic challenge framework; six forcing questions
- `/query` — verify one claim about runtime state with one read-only script
- `/quiz` — short quiz on the crucial decisions behind a PR/doc so you can defend it in review
- `/retro` — extract learning from a shipped piece of work
- `/review-pr` — differential PR review: post only what bots and prior reviewers haven't said
- `/self-heal` — repair accretion debt across this library without regressing behavior
- `/shape` — turn a half-formed idea into a refined plan via research and adversarial review
- `/summary` — humanized Slack summary of an investigation
- `/triage` — dispatch tracker issues through parallel, tiered, repo-aware pipelines to draft PRs
- `/weekly` — draft the charter-defined weekly review; computed numbers only

## Commands (`commands/`)

Thin slash-command wrappers.

- `/ack` — acknowledge external file changes
- `/commit` — create a focused git commit
- `/linear` — write a title and description for a Linear issue
- `/push` — open a pull request
- `/setup` — arm this session's recurring loops from the project's routine prompts
- `/standup` — humanized standup update from a seed

## The context layer (`context/`)

The tracked library is mechanism; configuration is private. `context/<project>/`
(gitignored) holds each project's charter, risk tiers, escalation contract, stack
notes, partner roster, remembered skill resolutions, and decision log — see
`context.example/` for the shape of each file. Skills read the active project's
context at runtime and degrade gracefully when a file is missing.

Repos can also carry their own skills; this library defers to them — it detects
overlap, asks once, and remembers the answer per repo. Nothing project- or
employer-specific ever appears in tracked files.
