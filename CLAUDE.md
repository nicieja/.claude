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
| An engineering claim, refactor pitch, library/tech choice, or design decision that needs grilling | `/pushback` |
| "What would the platonic ideal of this look like?", ambition gap, stretching a plan | `/10x` |
| Sizing work in hours/days, "how long will this take" | `/estimate` |
| Building the smallest thing that answers one question, throwaway exploration | `/prototype` |
| Looking back on a shipped PR/commit/issue, lessons learned, waste, debt | `/retro` |
| Writing up findings for Slack after an investigation | `/summary` |
| Posting investigation findings as a Linear comment | `/comment` |
| Drafting a Linear title/description from the current diff | `/linear` |
| Self-improvement — "what did we learn this session, update the skills" | `/learn` |
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
| A strategic bet, roadmap call, or cross-cutting proposal that needs executive grilling on top of engineering pushback | `ceo` |

### Anti-patterns

- Do not invent skills or subagents. Only suggest ones in the tables above (or ones I've explicitly invoked this session).
- Do not pad responses with *"by the way, you have a `/foo` skill"* when the current task is already on rails.
- Do not turn every reply into a skill-discovery menu. Most turns should not include a suggestion at all.
