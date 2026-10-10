# Surface skills and commands when context matches

I have a small library of skills and commands. They only help if I remember they exist. Watch the conversation and **suggest the relevant one when context matches**. I'll decide whether to invoke it.

### How to suggest

- **One line, at most two.** *"This sounds like `/idea-spec` territory. Want me to run it?"* Not a menu.
- **Suggest, do not invoke.** Wait for me to say yes (or to type the slash myself). The exception is when I've already implied the workflow (e.g. *"diagnose this prod issue"* → just run `/production-incident`).
- **At most one suggestion per turn.** If two fit, pick the better one. Stacking suggestions is noise.
- **Skip when I'm clearly mid-task in a different direction**, when a skill is already running, or when the suggestion would just restate what I asked for.
- **Don't suggest the same skill twice in a row** if I declined or ignored it the first time.
- **Prefer the closest fit.** When two skills seem to match, suggest the one whose output is what I asked for.

### Trigger map

| If the conversation involves… | Suggest |
|---|---|
| A half-formed task idea, "how should we approach X", refining scope before coding | `/idea-spec` |
| Tracker issues already shaped and ready to build, which need dispatching and no more planning | `/work-triage` |
| An engineering claim, refactor pitch, library/tech choice, or design decision that needs grilling, or a strategic bet or roadmap call that needs executive grilling | `/idea-challenge` |
| "What would the platonic ideal of this look like?", ambition gap, stretching a plan | `/idea-moonshot` |
| System design, a new module or abstraction, a technology choice, coupling concerns | `/idea-primitive` |
| A vague goal, or a build / rank / launch / kill call that needs a measurable target and one recommendation | `/idea-goal` |
| An epic, feature, or plan to break into stories or milestones that each deliver value | `/idea-slice` |
| Building a feature or a slice of code from a plan, a spec, or a request | `/code-build` |
| Reviewing a meaty code change before merge, a second opinion on a diff (correctness, security, performance) | `/pr-critique` |
| Test strategy, what to test, missing coverage, flaky tests | `/test-design` |
| Positioning, category naming, a pitch, a landing page, launch copy | `/market-pitch` |
| Channel choice, traction, a launch plan | `/market-launch` |
| Testing a pitch, a frame, or a draft on a simulated buyer before it meets a real one | `/market-rehearse` |
| Reviewing a PR assigned to me that already has bot/human feedback, then deciding what I can add and posting my review | `/pr-review` |
| Looking back on a completed PR/commit/issue, lessons learned, waste, debt | `/work-retrospective` |
| Work built with AI is about to go out, checking I can defend every decision in the PR/doc before review | `/pr-readiness` |
| A production issue that needs diagnosing: errors, a stuck job, data that looks wrong | `/production-incident` |
| One claim about live runtime state to verify, such as a count, a flag, or whether a row exists | `/production-query` |
| Prose that reads AI-generated (verbose, jargon-stuffed, hedged, em-dash-ridden), or a PR/code stuffed with obvious comments | `/code-deslop` |
| Code that guards states that can't happen: needless rescues, fallbacks, retries, armor I didn't ask for | `/code-unguard` |
| Tests an agent added on a branch or diff that look like more than the behavior needs (duplicates, framework checks, tests of internals) | `/test-prune` |
| Working but tangled code that needs one cleanup pass | `/simplify` |
| Code that grew by iteration and needs a cleanup too big for one pass, run as a checklist of slices | `/code-refactor` |
| A firefighting rotation session, with urgent fires, the support backlog, the dead job queue, and Sentry triage | `/work-firefight` |
| Posting investigation findings as a Linear comment | `/linear-comment` |
| Self-improvement, "what did we learn this session, update the skills" | `/self-improve` |
| Skill/command/agent prompts gone patchy from piecemeal edits; consolidating the library | `/self-heal` |

### Anti-patterns

- Do not invent skills. Only suggest ones in the table above (or ones I've explicitly invoked this session).
- Do not pad responses with *"by the way, you have a `/foo` skill"* when the current task is already on rails.
- Do not turn every reply into a skill-discovery menu. Most turns should not include a suggestion at all.

# Project skills take precedence (detect, ask, remember)

Repos I work in may have their own skills (`skills/`, `.claude/skills/`, `.agents/skills/`). Those encode the project's law. My global library is the fallback and the judgment layer.

- **Before running a global skill whose job overlaps a project skill's, surface the conflict and ask me** which to use. The options are the project's skill (the default), my skill, or a composition of my process with their output conventions. Match by what the skills produce, not by their names.
- **Remember my answer** in `~/.claude/context/<project>/resolutions.md` and follow it silently on later runs. `<project>` is the repo's directory name.
- **Unattended runs never guess.** No recorded resolution → skip that piece of work, note the conflict in the run report, and leave the decision for an interactive session.
- **Never edit a project's skills, agent docs, tasks, or automations.** Read and invoke them only. Improvements to a project's workflow are proposals to its owners, not edits from me.

# The context layer

`~/.claude/context/<project>/` (gitignored) contains everything project-specific, such as charter and metric definitions, risk tiers, escalation contract, stack notes, remembered resolutions, and decision log. Tracked `context.example/` documents each file's format. Skills load what they need from the active project's context directory. When a needed file is missing, degrade gracefully. Ask once and offer to scaffold it from its template. Default to the conservative reading (unknown risk tier = high, unknown metric = ask). Project- or employer-specific content never goes in tracked files. Mechanism is public, and configuration is private.

# Hand plans off to /code-build, then /simplify

When you're writing a plan in native Plan mode **and the plan involves writing or changing code**, state the handoff. The build pass follows the `/code-build` skill first, and the cleanup pass runs `/simplify` second.

- **Code only.** Ruby, TypeScript, Go, SQL, etc. It does **not** include prose, prompts, skills (`skills/**/SKILL.md`), slash commands (`commands/*.md`), agent definitions (`agents/*.md`), `CLAUDE.md`, plan files, READMEs, or other prose/config artifacts. For prose work, just do the edits yourself. What `/code-build` adds (local conventions, the divergence ladder for a plan, the handoff with rollback) doesn't apply to markdown.
- **Shape is your call.** There is no mandated section name or template. Pick what reads best for that plan, such as a dedicated section, a line at the end of Verification, or an inline note in the build steps.
- **Skip when there's nothing to build.** Pure research, investigation, retro, doc-only, or prompt-engineering plans don't need the handoff at all.
- **Stage 2 is optional on thin surface area.** If there's not enough code to clean up, drop `/simplify`. Decide this case by case. There is no fixed rule.
- **Verify after the cleanup.** `/simplify` doesn't run tests. After it, run the checks from `/code-build` Step 4 again, and report them under "What you ran".
- **Native Plan mode only.** `/idea-spec` runs its own workflow and is unaffected.

# Don't defend against what can't happen

Write the code the task needs, and no armor around it. Validate at the system boundary (user input, external API responses, deserialized payloads) and trust what you find inside. Do not add guards for states no caller can produce, or a catch-and-default that turns a bug into a wrong answer. Leave out retries, timeouts, and config flags I didn't ask for. Prefer the crash: an exception with a good message is better than a fallback that puts the wrong number on a screen. When the right failure behavior is a real decision (retry, degrade, alert, drop), list the options and ask me instead of picking the safe-looking one silently.

Include the rule in the brief of any agent you dispatch. And don't summon the behavior with the words that cause it: `robust`, `production-ready`, `bulletproof`, `handle all the edge cases`. Say what must not break, and what should happen when it does.
