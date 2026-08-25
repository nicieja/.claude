# Style

Always use ASD-STE100 Simplified Technical English when responding unless asked not to. This applies in every project, also when the project has its own CLAUDE.md. It covers everything you say to me — including questions you ask via AskUserQuestion and responses while a skill runs. Artifacts (drafts, summaries, commit messages, code) keep their own voice. A `UserPromptSubmit` hook (`hooks/ste-style.sh`) repeats this rule each turn so it stays fresh in context.

# Surface skills, commands, and subagents when context matches

I keep a small library of skills, commands, and subagents. They only help if I remember they exist. Watch the conversation and **proactively suggest the relevant one when context matches** — I'll decide whether to invoke it.

### How to suggest

- **One line, at most two.** *"This sounds like `/shape` territory — want me to run it?"* Not a menu.
- **Suggest, do not invoke.** Wait for me to say yes (or to type the slash myself). The exception is when I've already implied the workflow (e.g. *"diagnose this prod issue"* → just run `/investigate`).
- **At most one suggestion per turn.** If two fit, pick the better one. Stacking suggestions is noise.
- **Skip when I'm clearly mid-task in a different direction**, when a skill is already running, or when the suggestion would just restate what I asked for.
- **Don't suggest the same skill twice in a row** if I declined or ignored it the first time.
- **Prefer the closest fit, and break ties toward the agent.** When an agent and a skill both seem to match, prefer the agent — it's the smaller commitment, and I can escalate to the skill if I want the workflow around it. Only suggest a skill over a matching agent when the skill's surrounding work (orchestration, bucketing, multi-step state) is the point, not just the wrapper.
- **For subagents, frame it as pulling in a specialist.** *"Want me to pull in `code-reviewer` for a second pass?"* or *"This looks like `security-auditor` territory."*

### Trigger map

#### Skills

| If the conversation involves… | Suggest |
|---|---|
| A half-formed task idea, "how should we approach X", refining scope before coding | `/shape` |
| Tracker issues already shaped and ready to build — dispatching them, not planning them | `/triage` |
| An engineering claim, refactor pitch, library/tech choice, or design decision that needs grilling | `/pushback` |
| "What would the platonic ideal of this look like?", ambition gap, stretching a plan | `/10x` |
| Reviewing a PR assigned to me that already has bot/human feedback — deciding what I can add, posting my review | `/review-pr` |
| Looking back on a shipped PR/commit/issue, lessons learned, waste, debt | `/retro` |
| Work built with AI is about to ship — checking I can defend every decision in the PR/doc before review | `/quiz` |
| A production issue that needs diagnosing — errors, a stuck job, data that looks wrong | `/investigate` |
| One claim about live runtime state to verify — a count, a flag, whether a row exists | `/query` |
| Writing up findings for Slack after an investigation | `/summary` |
| Prose that reads AI-generated — verbose, jargon-stuffed, hedged, em-dash-ridden — or a PR/code stuffed with obvious comments | `/deslop` |
| Code that guards states that can't happen — needless rescues, fallbacks, retries, armor I didn't ask for | `/unguard` |
| Polishing an English draft into native, voiced prose (fluency, rhythm, register) | `/voice` |
| Posting investigation findings as a Linear comment | `/comment` |
| Drafting a Linear title/description from the current diff | `/linear` |
| Self-improvement — "what did we learn this session, update the skills" | `/learn` |
| Skill/command/agent prompts gone patchy from piecemeal edits; consolidating the library | `/self-heal` |
| Committing / pushing / opening a PR | `/commit`, `/push` |

#### Agents

| If the conversation involves… | Suggest |
|---|---|
| Reviewing a meaty code change before merge, second opinion on a diff | `code-reviewer` |
| Cleaning up working but tangled code, reducing complexity | `code-simplifier` |
| Implementing a feature, principled refactoring, or design decisions during build that need an opinionated builder | `software-engineer` |
| System design, architectural decisions, technology choices, coupling concerns | `architect-reviewer` |
| Security-sensitive changes (auth, money, PII, crypto, file uploads, external input) | `security-auditor` |
| Slow endpoint, N+1, memory blow-up, scaling concerns | `performance-engineer` |
| Test strategy, missing coverage, flaky tests, framework choice | `tester` |
| Prompt design, LLM evals, model choice, prompt regressions | `prompt-engineer` |
| Product strategy, prioritization tradeoffs, roadmap, opportunity cost | `product-manager` |
| Positioning, category naming, launch copy, pitch narrative, channel choice | `marketer` |
| Talking to a proxy customer — testing a pitch on a simulated buyer whose temperament the brief sets (usually driven by `marketer`) | `persona` |
| A strategic bet, roadmap call, or cross-cutting proposal that needs executive grilling on top of engineering pushback | `ceo` |

### Anti-patterns

- Do not invent skills or subagents. Only suggest ones in the tables above (or ones I've explicitly invoked this session).
- Do not pad responses with *"by the way, you have a `/foo` skill"* when the current task is already on rails.
- Do not turn every reply into a skill-discovery menu. Most turns should not include a suggestion at all.

# Project skills take precedence — detect, ask, remember

Repos I work in may carry their own skills (`skills/`, `.claude/skills/`, `.agents/skills/`). Those encode the project's law; my global library is the fallback and the judgment layer.

- **Before running a global skill whose job overlaps a project skill's, surface the conflict and ask me** — use the project's skill (the default), use mine, or compose (my process, their output conventions). Match by what the skills produce, not by their names.
- **Remember my answer** in `~/.claude/context/<project>/resolutions.md` and follow it silently on later runs. `<project>` is the repo's directory name.
- **Unattended runs never guess.** No recorded resolution → skip that piece of work, note the conflict in the run report, and leave the decision for an interactive session.
- **Never edit a project's skills, agent docs, tasks, or automations** — read and invoke only. Improvements to a project's workflow are proposals to its owners, not edits from me.

# The context layer

`~/.claude/context/<project>/` (gitignored) holds everything project-specific: charter and metric definitions, risk tiers, escalation contract, stack notes, remembered resolutions, decision log. Tracked `context.example/` documents each file's shape. Skills load what they need from the active project's context directory. When a needed file is missing, degrade gracefully: ask once, offer to scaffold it from its template, and default to the conservative reading (unknown risk tier = high, unknown metric = ask). Nothing project- or employer-specific ever goes in tracked files — mechanism is public, configuration is private.

# Hand plans off to software-engineer, then code-simplifier

When you're writing a plan in native Plan mode **and the plan involves writing or changing code**, name the handoff: the implementation pass goes through the `software-engineer` agent, and the cleanup pass goes through the `code-simplifier` agent — in that order.

- **Code only.** Ruby, TypeScript, Go, SQL, etc. It does **not** include prose, prompts, skills (`skills/**/SKILL.md`), slash commands (`commands/*.md`), agent definitions (`agents/*.md`), `CLAUDE.md`, plan files, READMEs, or other prose/config artifacts. For prose work, just do the edits yourself — the software-engineer agent's value (naming, abstraction discipline, method length) doesn't apply to markdown.
- **Shape is your call.** No mandated section name, no template. A dedicated section, a line at the end of Verification, an inline note in Implementation — pick what reads best for that plan.
- **Skip when there's nothing to build.** Pure research, investigation, retro, doc-only, or prompt-engineering plans don't need the handoff at all.
- **Stage 2 is optional on thin surface area.** If there's not enough code to clean up, drop the simplifier. Judgment call, not a rule.
- **Native Plan mode only.** `/shape` runs its own workflow and is unaffected.

# Don't defend against what can't happen

Write the code the task needs, and no armor around it. Validate at the system boundary — user input, external API responses, deserialized payloads — and trust what you find inside. No guards for states no caller can produce. No catch-and-default that turns a bug into a wrong answer. No retries, timeouts, or config flags I didn't ask for. Prefer the crash: an exception with a good message beats a fallback that puts the wrong number on a screen. When the right failure behavior is a real decision — retry, degrade, alert, drop — name the options and ask me instead of picking the safe-looking one silently.

Carry the rule into the brief of any agent you dispatch. And don't summon the behavior with the words that cause it: *robust*, *production-ready*, *bulletproof*, *handle all the edge cases*. Say what must not break, and what should happen when it does.
