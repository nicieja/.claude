# Using skills

## Surface skills and commands when context matches

I keep a small library of skills and commands under `~/.claude/`. They only help if I remember they exist. Watch the conversation and **proactively suggest the relevant one when context matches** — I'll decide whether to invoke it.

### How to suggest

- **One line, at most two.** *"This sounds like `/shape` territory — want me to run it?"* Not a menu.
- **Suggest, do not invoke.** Wait for me to say yes (or to type the slash myself). The exception is when I've already implied the workflow (e.g. *"diagnose this prod issue"* → just run `/investigate`).
- **At most one suggestion per turn.** If two fit, pick the better one. Stacking suggestions is noise.
- **Skip when I'm clearly mid-task in a different direction**, when a skill is already running, or when the suggestion would just restate what I asked for.
- **Don't suggest the same skill twice in a row** if I declined or ignored it the first time.

### Trigger map

| If the conversation involves… | Suggest |
|---|---|
| A half-formed task idea, "how should we approach X", refining scope before coding | `/shape` |
| A claim, RFC, refactor pitch, or design decision that smells smart-but-unverified | `/pushback` or the `ceo` subagent |
| "What would the platonic ideal of this look like?", ambition gap, stretching a plan | `/10x` |
| Sizing work in hours/days, "how long will this take" | `/estimate` |
| Building the smallest thing that answers one question, throwaway exploration | `/prototype` |
| Looking back on a shipped PR/commit/issue, lessons learned, waste, debt | `/retro` |
| Writing up findings for Slack after an investigation | `/summary` |
| Posting investigation findings as a Linear comment | `/comment` |
| Drafting a Linear title/description from the current diff | `/linear` |
| Self-improvement — "what did we learn this session, update the skills" | `/learn` |
| Committing / pushing / opening a PR | `/commit`, `/push` |

### Anti-patterns

- Do not invent skills. Only suggest ones in the table above (or ones I've explicitly invoked this session).
- Do not pad responses with *"by the way, you have a `/foo` skill"* when the current task is already on rails.
- Do not turn every reply into a skill-discovery menu. Most turns should not include a suggestion at all.
