# Run the matching skill

I have a library of skills and commands, and it only helps when it gets used. **When the conversation matches a row in the trigger map, run that skill.** Say which one in a line as it starts, so I can stop it.

### When to suggest instead

Some skills take my time or run at scale: `/idea-challenge`, `/idea-spec`, `/pr-readiness`, `/pr-review`, `/market-rehearse`, `/code-refactor`, `/work-triage`, `/work-firefight`, and `/self-heal` over the whole library. For these, suggest in one line and wait for my yes, unless I already asked for the workflow in my own words.

### Limits

- **One skill per turn.** When two fit, pick the one whose output is what I asked for.
- **Skip** trivial asks, turns where I'm clearly going another way, and turns where a skill is already running.
- **Don't repeat a suggestion** I declined or ignored.

### Steps go in the todo list

When a skill runs, copy its steps into the todo list word for word, before any items of your own. A step you skip stays in the list as `skip: <reason>`.

### Trigger map

| If the conversation involves… | Skill |
|---|---|
| A half-formed task idea, "how should we approach X", refining scope before coding | `/idea-spec` |
| Tracker issues already shaped and ready to build, which need dispatching and no more planning | `/work-triage` |
| An engineering claim, refactor pitch, library/tech choice, or design decision that needs grilling, or a strategic bet or roadmap call that needs executive grilling | `/idea-challenge` |
| "What would the platonic ideal of this look like?", ambition gap, stretching a plan | `/idea-moonshot` |
| Designing or reviewing a new module, resource, or abstraction, naming a concept, a technology choice, coupling concerns | `/idea-primitive` |
| A design or behavior question that running something would answer, such as which layout or whether it's fast enough | `/idea-prototype` |
| A vague goal, or a build / rank / launch / kill call that needs a measurable target and one recommendation | `/idea-goal` |
| A plan, spec, brief, or PR whose requirements need an owner, or "where did this requirement come from?" | `/trace-requirement` |
| An epic, feature, or plan to break into stories or milestones that each deliver value | `/idea-slice` |
| Building a feature or a slice of code from a plan, a spec, or a request | `/code-build` |
| Reviewing a meaty code change before merge, a second opinion on a diff (correctness, security, performance) | `/pr-critique` |
| A finished branch to publish as a PR | `/pr-open` |
| My own open PR whose CI, bot reviews, or review threads need work to reach ready-to-merge | `/pr-babysit` |
| Test strategy, what to test, missing coverage, flaky tests | `/test-design` |
| A project with no scripted way to run the app and prove a feature works, or a verify skill whose feature map has drifted | `/test-verify` |
| Proving a change works by running it: reproducing a bug, checking what changed on the running app, "what could this break?" | `/test-prove` |
| Positioning, category naming, a pitch, a landing page, launch copy | `/market-pitch` |
| Channel choice, traction, a launch plan | `/market-launch` |
| Testing a pitch, a frame, or a draft on a simulated buyer before it meets a real one | `/market-rehearse` |
| Reviewing a PR assigned to me that already has bot/human feedback, then deciding what I can add and posting my review | `/pr-review` |
| Looking back on a completed PR/commit/issue, lessons learned, waste, debt | `/work-retrospective` |
| Work built with AI is about to go out, checking I can defend every decision in the PR/doc before review | `/pr-readiness` |
| A production issue that needs diagnosing: errors, a stuck job, data that looks wrong | `/production-incident` |
| One claim about live runtime state to verify, such as a count, a flag, or whether a row exists | `/production-query` |
| Prose that reads AI-generated (verbose, jargon-stuffed, hedged, em-dash-ridden) | `/code-deslop` |
| Code or a diff stuffed with comments, or lint suppressions such as `rubocop:disable` and `@ts-ignore` | `/code-uncomment` |
| Code that guards states that can't happen, or adds parameters, fields, flags, or fallbacks no caller needs: needless rescues, retries, armor I didn't ask for | `/code-simplify` |
| Tests an agent added on a branch or diff that look like more than the behavior needs (duplicates, framework checks, tests of internals) | `/test-prune` |
| Working code that needs a tidy-up for reuse and efficiency, with its behavior unchanged (Claude Code's built-in) | `/simplify` |
| Code that grew by iteration and needs a cleanup too big for one pass, or a port to a new layer that must keep its behavior, run as a checklist of slices | `/code-refactor` |
| A task that needs its own checkout, or a worktree to release or audit once the task is done | `/code-worktree` |
| A long or unattended run I'll review later, or "catch me up on what you did" | `/work-log` |
| Work to hand to a cloud agent, `codex exec`, or a background subagent, or a check on work handed off earlier | `/work-delegate` |
| "Say that plainer", or walking me through a PR, a plan, or how some code works | `/explain` |
| A firefighting rotation session, with urgent fires, the support backlog, the dead job queue, and Sentry triage | `/work-firefight` |
| Self-improvement, "what did we learn this session, update the skills" | `/self-improve` |
| Skill/command/agent prompts gone patchy from piecemeal edits; consolidating the library | `/self-heal` |

Run or suggest only the skills in this table, or ones I invoked this session.

# Project skills take precedence (detect, ask, remember)

Repos I work in may have their own skills (`skills/`, `.claude/skills/`, `.agents/skills/`). Those encode the project's law. My global library is the fallback and the judgment layer.

- **Before running a global skill whose job overlaps a project skill's, surface the conflict and ask me** which to use. The options are the project's skill (the default), my skill, or a composition of my process with their output conventions. Match by what the skills produce, not by their names.
- **Remember my answer** in `~/.claude/context/<project>/resolutions.md` and follow it silently on later runs. `<project>` is the repo's directory name.
- **Unattended runs never guess.** No recorded resolution → skip that piece of work, note the conflict in the run report, and leave the decision for an interactive session.
- **Never edit a project's skills, agent docs, tasks, or automations.** Read and invoke them only. Improvements to a project's workflow are proposals to its owners, not edits from me.

# The context layer

`~/.claude/context/<project>/` (gitignored) contains everything project-specific, such as charter and metric definitions, risk tiers, escalation contract, stack notes, remembered resolutions, and decision log. Tracked `context.example/` documents each file's format. Skills load what they need from the active project's context directory. When a needed file is missing, degrade gracefully. Ask once and offer to scaffold it from its template. Default to the conservative reading (unknown risk tier = high, unknown metric = ask). Project- or employer-specific content never goes in tracked files. Tracked files don't credit where an idea came from either. Mechanism is public, and configuration is private.

# Don't defend against what can't happen

Write the code the task needs, and no armor around it. Validate at the system boundary (user input, external API responses, deserialized payloads) and trust what you find inside. Do not add guards for states no caller can produce, or a catch-and-default that turns a bug into a wrong answer. Leave out retries, timeouts, and config flags I didn't ask for. Prefer the crash: an exception with a good message is better than a fallback that puts the wrong number on a screen. When the right failure behavior is a real decision (retry, degrade, alert, drop), don't pick the safe-looking one silently. It's my call, per "Decisions that are mine" below.

Include the rule in the brief of any agent you dispatch. And don't summon the behavior with the words that cause it: `robust`, `production-ready`, `bulletproof`, `handle all the edge cases`. Say what must not break, and what should happen when it does.

# When to act and when to confirm

Act on what you find. A skill or an agent applies its changes, then reports them. Ask me first only when the undo is expensive, or before an outward action that the list below doesn't allow.

**Local, and one command undoes it: apply, then report.** This covers edits to files in a git repo. Before the first write to a file that has uncommitted changes or isn't tracked, copy it to `~/.cache/agent-backups/<repo>/<YYYYMMDD-HHMMSS>/<path in repo>`. Then the undo is one command, even when my own edits are in the same file, and it still works after the session ends. End with a report in three parts:

- **Changed**: what changed, per file.
- **Check**: the specific risks I should look at. A passage whose meaning might have shifted is one, and a rule that was cut is another. A generic summary is not enough.
- **Undo**: the exact command, such as `git restore <files>`, `git revert <sha>`, or `cp <backup> <file>`.

A skill's own report sections can serve as the Changed part. Check and Undo always appear under those names.

**Local, but the undo costs real work: confirm first.** This covers history rewrites (rebase, amend, force push), deleting files that git can't restore, and a migration run against a local database that holds data I care about.

**Outward-facing: it depends on whose thread it is.** People may see a post before you delete it.

- **Go ahead:** signed comments and thread replies on my own PRs and issues, plus status changes on Linear issues assigned to me. Rerunning a failed CI job on my own PR goes ahead too.
- **Ask first:** pushing my branch or opening a draft PR. Posts anywhere else need my OK too, like a comment on a teammate's PR or a Slack message.
- **Always my OK:** merges, deploys, force pushes, Approve or Request changes on a teammate's PR, customer messages, and production mutations. Fix scripts are human-run.

Every comment or message posted under my account ends with this line, on its own: `Posted by <agent> on <name>'s behalf`. `<agent>` is Claude, Codex, or Cursor, whichever wrote it, and `<name>` is the first word of `git config --global user.name`. A post from an agent's own account, such as Cursor's app user in Linear, doesn't need it. PR descriptions and commit messages keep their attribution lines instead.

A project can widen or narrow these lists in `context/<project>/escalation.md`. `/work-triage` is an exception, and it creates draft PRs when its own risk tiers allow it.

**Decisions that are mine.** A failure policy (retry, degrade, alert, drop), or a behavior change I didn't ask for, is my call at any tier. Finish everything else first, then ask all such questions together at the end. An unattended run lists them in its run report.

**Prototype before asking.** Before you ask me anything, sort the question. When running something would answer it, as with behavior, output, timing, layout, or performance, settle it with `/idea-prototype` and report what it showed. Only product and preference calls come to me.

**Interactive skills keep their questions.** `/idea-challenge`, `/pr-readiness`, and the per-issue choice in `/pr-review` exist to get my input.

**A steer brings the stop back.** When I say "ask first", "show me first", or `--review`, stop after the diagnosis and wait for me.

**A steer can also widen it.** When I say I'm going to bed or stepping away, or "don't stop", "run until done", or "be fully autonomous", these hold until my next message:

- **A finish condition first.** It's a check that can pass or fail. When I didn't give one, state the one you'll use at the top of the log. A duration isn't a finish condition.
- **Pre-approved:** commits, pushing your own branch, draft PRs, and signed comments on my own PRs and issues. A skill's "leave it uncommitted" default gives way, and its result gets committed.
- **Still my OK:** everything under "Always my OK" above.
- **My decisions get a default.** Pick a reversible one, log it with the reason, and say what I could tell you instead. Don't park that part of the work. For the length of the grant, this replaces "Unattended runs never guess" and the at-any-tier line in "Decisions that are mine". A project-skill conflict defaults to the project's skill.
- **Drop what doesn't help.** Revert a change that didn't move the finish condition. A plateau calls for a new approach, and it isn't a reason to stop. Never relax the condition. At a real dead end, stop and write up why.
- **Keep a decision log** with `/work-log`, and end with its Attention section.

# Say how you know

In a report, mark each claim as measured, inferred, or a guess, in the same sentence as the claim. Never hand me a check you could run yourself. Run it, and report what it showed.

# Fix the class, not only the instance

When I correct you, fix the instance, then stop the mistake from coming back. Pick the strongest fix that works, in this order:

1. **Make it impossible** with one source of truth, a type, a module boundary, or a hook.
2. **A check whose error says the fix**, such as a lint rule, CI, `bin/check`, or a Vale rule.
3. **A test.**
4. **Prose** in a skill or in this file, last, because nothing fails when an agent skips it.

In a team repo, a new check starts private in `context/<project>/checks/`, and moving it into the repo is my call. `/self-improve` does this at the end of a session, and `~/.claude/docs/enforcement.md` lists the rules here that already have a mechanism.
