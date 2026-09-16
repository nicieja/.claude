---
name: retro
version: 1.1.0
description: |
  Run a retrospective on a PR, commit, Linear issue, or freeform piece of
  work. Read the data and any cross-referenced material, apply the retro
  lenses (value stream, waste, technical debt, complexity, impediments, wins,
  improvements), and produce a copy-paste-ready retro doc with tasked-out
  improvements. Read-only: it never starts coding or writes a file.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - WebFetch
  - AskUserQuestion
---

# Retro

Take a piece of completed work and extract the learning. Read the PR/commit/Linear data and anything it cross-references, apply the retro lenses, and produce a copy-paste-ready document with tasked-out improvements. The artifact is the message. It is not written to a file.

## Arguments
- `/retro <PR URL>`: retro a GitHub pull request
- `/retro <commit SHA>`: retro one commit (7+ hex chars)
- `/retro <Linear ID>`: retro a Linear issue (e.g. `ENG-1234`) or `linear.app/...` URL
- `/retro <description>`: retro a freeform piece of work
- `/retro`: bare. Ask once "What work do you want to retro?"

## Cases for another skill
- Writing a humanized Slack update on an investigation → `/summary`
- Planning future work, not reflecting on past work → `/shape`
- Challenging one claim, not extracting learning → `/pushback`
- Diagnosing an active production issue → `/investigate`

## Instructions

Follow these steps in order. When a step is not relevant, skip it, but never silently drop work. Say so in the output.

---

### Step 0: Preflight

1. **Capture input.** If invoked as `/retro <text>`, that's the input. If bare, ask once: *"What work do you want to retro?"* Don't proceed without input.

2. **Detect input type** by format:
   - `https://github.com/.../pull/N` → **PR**
   - `[A-Z]{2,4}-\d+` or `https://linear.app/.../issue/...` → **Linear issue**
   - 7 to 40 hex chars → **commit**
   - else → **freeform description**

If the input contains both (e.g. a PR URL plus extra prose), treat the URL as the primary anchor and the prose as user-supplied framing.

---

### Step 1: Let the data in

Pull all relevant material before forming any opinion.

**For a PR:**
```bash
gh pr view <num> --json title,body,comments,reviews,commits,files,additions,deletions,author,state,mergedAt
gh api repos/<owner>/<repo>/pulls/<num>/comments
```
Read the body, top-level comments, review-thread comments, commit messages, and which files moved.

**For a commit:**
```bash
git show <sha>
git log <sha>~..<sha> --stat
```
Read the diff and the message.

**For a Linear issue:** fetch the issue (description, state, comments, linked PRs) through the Linear MCP tools (load them via ToolSearch if deferred). If Linear is unavailable in this session, say so once and work from the other sources.

**Cross-references: follow them.** The principle is plural: *all relevant pull requests, comments, Linear issues and discussions*.
- PR body mentions `XXX-NNNN` → fetch the Linear issue
- Linear issue lists linked PRs → fetch them via `gh pr view`
- A comment links to a Notion / Slack / blog URL → `WebFetch` if it looks essential

**For a freeform description:** there is nothing to fetch, so work from the description plus the user's answers in Step 2.

**Light codebase exploration is OK** to verify a claim (Read, Glob, Grep). Don't dive deep, because that's `/investigate`'s job.

Don't write the retro yet. Hold the facts in mind.

---

### Step 2: Initial questions

Ask **1 to 3 questions max via `AskUserQuestion`, one per call**. Skip any whose answer is obvious from the data.

- *"Was this typical work, or a painful piece?"* Typical drives general-workflow lessons, and painful drives rogue-dependency / false-assumption lessons. The value-stream principle requires both reads.
- *"What success criterion would you use in hindsight?"* The answer goes into the Numbers section. If the user can't state one, that's signal.
- *"Any prior signals to fold in, such as interruption counts you track, notes from previous retros, or related Slack threads?"* This invites existing data into the retro. Interruption-count data, where it exists, is a primary input to retrospectives, not just a future-facing recommendation.

---

### Step 3: Apply the lenses

Work through the lenses below and write 0..N **specific** findings for each. Cite the data (PR comment, file path, commit SHA, Linear comment author). Generic findings are useless. Skip any lens silently when nothing real is found.

| Lens | What it covers |
|---|---|
| **What went well** | Specific moves, decisions, people. Not "good teamwork", but "the early review request on the migration caught the FK ordering before it was merged." If wins are real, prompt the user at the end to actually mark them (a thanks message, a Slack shout-out). The principle is about acknowledging progress, not listing it. |
| **Value stream** | Where time was spent. For typical work: workflow shape, prioritization, batching. For painful work: rogue dependencies and false assumptions, plus hidden coupling. |
| **Waste exposed** | Unused features, abandoned branches, dead code, debates that didn't resolve, premature abstractions, work that did not change behavior. |
| **Technical debt revealed** | Deviations from good engineering practice this work exposed, such as test gaps, missing observability, copy-paste, untyped boundaries, missing migration guards. |
| **Complexity to address** | For each "this was complex" complaint, drill to the *root cause*. If the answer is "the model is wrong," say so, and don't accept the complaint as stated. |
| **Impediments to challenge** | Things being worked around long enough that they feel like part of the furniture. Name them before they harden. |

---

### Step 4: Numbers

For each improvement that's measurable, capture:

- **Scale**: what we measure
- **Meter**: how we measure it
- **Baseline**: current value (or *"unknown, first action is to measure"*)
- **Target**: desired value
- **Check**: when we look again

Skip the section entirely when improvements are qualitative ("write more focused PRs"). Don't fabricate numbers, because vague metrics are worse than no metrics.

---

### Step 5: Bake improvements in + task them out

Each improvement is written as a task:

- **Title**: imperative, scoped (e.g. *"Add CI check for migration safety on schema changes"*)
- **Why**: one sentence on the gain
- **Effort**: rough estimate (h / d / w)
- **When**: set *Now* if it's a tweak to agentic config (a new skill, hook, agent definition, settings change) or any other low-cost change the user could make today; *Queued* otherwise.

Source principle: *"Improvements that can be made to agentic work should be proposed immediately."* For *Now* items, end the retro with a one-line nudge to act on them right after this conversation. `/retro` itself remains read-only, but it should hand the user a clear next move.

Aim for about three sharp improvements, which beat ten weak ones. *"We should think about..."* is not an improvement. Either it states an action or it's not on the list.

---

### Step 6: Ongoing practices (optional)

When the data shows symptoms of longer-horizon problems, state the practice that would help, but only when the data triggers it. Cap at one or two.

- Repeated "I dropped this for X" / "got pulled off" → recommend an **interruption-count exercise** next sprint. (The *count your interruptions* principle applies here. It can't be measured from one PR, only recommended.)
- Recurring tech-debt themes → suggest a **quarterly technical-debt retro**.
- Same impediment showing up across multiple retros (if the user mentions it) → escalate.

Don't lecture. If nothing real triggers, skip the section.

---

### Step 7: Output

Wrap the final retro in a fenced code block as **GitHub-flavored markdown** (renders cleanly in Linear, GitHub, and Notion). Structure:

````
```markdown
# Retro: <title>

## What we did
<one short paragraph>

## What went well
- ...

## Value stream
- ...

## Waste exposed
- ...

## Technical debt revealed
- ...

## Complexity to address
- ...

## Impediments to challenge
- ...

## Numbers
- **Scale**: ...
- **Meter**: ...
- **Baseline**: ...
- **Target**: ...
- **Check**: ...

## Improvements to bake in
- **<title>** — <why>. Effort: <est>. When: <Now | Queued>.

## Ongoing practices
- ...
```
````

**Skip empty sections silently.** Don't render `## Technical debt revealed` followed by *"none"*. A clean retro of clean work might only have **What we did**, **What went well**, **Improvements**, and one closing line saying nothing else came up. That's a fine retro.

After the code fence, add (in this order, skipping any that don't apply):

1. **If real wins came up**, add one short line nudging the user to actually mark them (a thanks-message, a Slack shout-out, anything tangible). The principle is *celebrate*, not *list*.
2. **If any improvement is tagged `When: Now`**, one line that states the immediate next move (e.g. *"The CI-check improvement is a `Now` item. Say the word and we can shape it."*).
3. *"Copy this into wherever the team reviews retros."*

---

## Key Rules

1. **Read-only.** Do not edit files, commit, write to Linear, or comment on PRs. The artifact is the message.
2. **Cite the data.** Each finding traceable to a PR comment, file path, commit SHA, or Linear comment. *"Review thread on `app/models/order.rb`"* beats *"the code review process"*.
3. **One question per `AskUserQuestion` call.** Never batch.
4. **Skip empty sections silently.** No headers with *"none"* under them.
5. **Improvements are tasked out** with title, why, and effort. *"We should consider..."* is not an improvement.
6. **Interruption-counting is a recommendation, never a deliverable.** It's a multi-day team practice, and the skill can't measure it from one PR.
7. **Don't lecture.** This is a retro of one piece of work. An essay on engineering culture is out of scope.
8. **No file written.** GitHub markdown inside a code fence, in conversation. Output once, then stop.
