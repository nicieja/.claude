---
name: develop
version: 1.0.0
description: |
  Take a half-formed task idea, research the codebase and the open web,
  challenge it with the CEO subagent, run the implementation plan through
  technical specialists in pushback mode, and produce a refined plan in the
  project's plans/ directory. Never starts coding without explicit approval.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - WebFetch
  - WebSearch
---

# /develop — Upfront Task Planning Loop

Turn a half-formed idea into a refined plan. The skill researches the codebase, reads any URLs in the seed, asks scope questions, scans the open web for prior art, runs the proposal through the CEO subagent for adversarial product review, then runs the implementation plan through technical specialists in pushback mode. The artifact is a plan file in the project's `plans/` directory. The skill never writes code — it ends with an explicit "implement now / defer" choice.

## User-invocable
When the user types `/develop`, run this skill.

## Arguments
- `/develop <seed>` — develop the proposal in the seed (a sentence, a paragraph, a Slack pitch with URLs)
- `/develop` — with no args, ask once: "What's the idea you want to develop?"

## When this is the wrong skill
- They want to challenge a single claim, not plan work → use `/pushback` instead
- They want to diagnose a production issue → use `/investigate` instead
- The Linear ticket is already shaped and ready to execute → use `/triage` instead
- They want hours/days for a clear scope → use `/estimate` instead

## Instructions

Follow these steps in order. Do NOT skip steps unless the step explicitly says it can be skipped.

---

### Step 0: Preflight

1. **Capture the seed.** If invoked as `/develop <text>`, that's the seed. If bare, ask once: "What's the idea you want to develop?" Do not proceed without a seed.

2. **Find the plan directory.** Run:
   ```bash
   git rev-parse --show-toplevel 2>/dev/null
   ```
   - On success: plan dir = `<root>/plans/`. Run `mkdir -p <root>/plans` to ensure it exists.
   - On failure (not a git repo): plan dir = `~/.claude/plans/`. Tell the user explicitly: "Not in a git repo — falling back to `~/.claude/plans/`."

3. **Extract URLs** from the seed using a simple regex (`https?://[^\s)]+`). Queue them for Step 2's URL reading.

4. **Generate the slug.** Lowercase, hyphen-separated, ≤60 chars, derived from the seed's first meaningful noun phrase (e.g., "model-routing-via-openrouter"). If `<plan-dir>/<slug>.md` already exists, append a 4-char hash to the slug.

---

### Step 1: Create the empty plan file

Use Write to create the skeleton at `<plan-dir>/<slug>.md`:

```markdown
# <title pulled from the seed>

> Status: drafting — created <YYYY-MM-DD> by /develop.

## Context

_Pending — filled after Step 3._

## Research

_Pending — filled after Step 4._

## Considerations

_Pending — filled after Step 5._

## Implementation

_Pending — filled in Step 6._

## Open questions

_Pending — filled in Step 8._

## Verification

_Pending._
```

Tell the user the file path. From here on, **all section updates use Edit**, not Write — that preserves any manual edits the user makes mid-flow.

---

### Step 2: Codebase + URL research

This is groundwork — do not write any plan section yet.

**Codebase exploration.** Use Read, Glob, Grep to find the files, models, services, configs the seed touches. Light, not deep:
- Names of relevant files
- Existing patterns to extend or replace
- Where the change boundary likely sits

Mirror the lightness of shaping work. Do not map every callback, scope, or association — that's `/investigate`'s job.

**URL reading.** For each URL queued in Step 0, WebFetch it. Capture 2-3 sentences per URL: what it is, what's relevant. Don't paste full pages anywhere.

If the seed includes obvious technical terms with no codebase hits (e.g., "OpenRouter" when the repo has no LLM client yet), say so — that's signal about scope.

---

### Step 3: Initial questions → write Context

Ask **2-3 questions max** via AskUserQuestion. **One per call.** Skip questions whose answers are already in the seed or obvious from the code.

Focus on:
- **Scope boundaries** — what's in, what's out
- **Target user** — whose problem does this solve, by name or role
- **Constraints** — deadlines, platform requirements, hard nos
- **Success criteria** — what changes if this ships

After answers, Edit the `## Context` section to capture:
- The problem in one paragraph (what's broken / missing today)
- The proposed direction (one sentence)
- Scope (in / out, as bullets)
- Constraints (as bullets)
- Links to the URLs you read in Step 2 with a one-line summary each

Keep it scannable. A reader should grok the work in 60 seconds.

---

### Step 4: External research → write Research

WebSearch for how others solve the same problem. Pick queries from the seed's domain language. Examples:
- "OpenRouter model routing rate limiting"
- "Stripe webhook idempotency design"
- "ActiveJob retry exponential backoff Sidekiq"

Read 2-3 results via WebFetch. **Drop weak sources** — marketing pages, a Hacker News thread with no signal, blog spam. Don't pad.

Edit `## Research` with:
- Each useful source as a bullet: `- [title](url) — 1-2 lines on what's worth borrowing`
- A short paragraph: "What we'd borrow / what we wouldn't."

**Skip this step entirely** when the work is obviously internal-only (a config tweak, a known-pattern refactor, a one-file change). Note the skip in the section: `_External research skipped — internal scope._`

---

### Step 5: CEO adversarial → write Considerations

Dispatch the `ceo` subagent via the Agent tool with `subagent_type: "ceo"`. The CEO runs in its own context window — that's the unbiased-review property the skill depends on.

The brief must include:
- The seed prompt verbatim
- The Context section just written
- The Research section's "what we'd borrow / what we wouldn't" paragraph
- An explicit ask:
  > "Challenge this end-to-end. Apply your usual interrogation. Don't rubber-stamp. Return your verdict (Solid / Weak / What to bring back) and the specific concerns I should reflect back to the user."

When the CEO returns:

**If the verdict surfaces real concerns:**
1. Brainstorm 2-3 ways to address them (as concrete options, not "we could think about…").
2. Present via AskUserQuestion. Each option is a directional choice ("Narrow the wedge to X first", "Keep scope but add Y guardrail", etc.). The user can pick "Other" to write their own.
3. Edit `## Considerations` to capture:
   - What the CEO challenged (one bullet per concern)
   - The user's response (the option picked or the freehand reply)
   - What changed in the proposal as a result (one line per change)

The point is for someone reading the plan a month later to see the **thought process** — not just the conclusion.

**If the CEO greenlights with no real concerns:**
Write that explicitly in `## Considerations`:
> CEO review: approved with no major concerns. Notes: <one line on anything the CEO did flag, even minor>.

---

### Step 6: Implementation plan → write Implementation

Edit `## Implementation` with:
- **Files to create / modify** — bulleted list with one line per file on what changes
- **Sequence** — what ships first, what comes after, what depends on what
- **Hard tradeoffs** — for each, name the tradeoff and the chosen side ("Use Solid Queue over Sidekiq because we're already on Rails 8 and want one fewer infra dep")
- **Effort sense** — only if asked. Otherwise skip; that's `/estimate`'s job.

Keep it scannable: bullets and short paragraphs, not prose walls. A reader should know what to build in 2 minutes.

---

### Step 7: Technical specialists, adversarial mode

**Auto-pick reviewers by domain** based on the Implementation section. Mapping:

| Trigger in the plan | Specialist |
|---|---|
| Touches auth, crypto, secrets, input validation, dependency surfaces | `security-auditor` |
| Introduces new abstractions, cross-service boundaries, schema migrations, public APIs | `architect-reviewer` |
| Hot paths, new queries (especially in loops), cache changes, async/sync swaps | `performance-engineer` |
| Adds critical paths that need testing, changes test strategy | `qa-expert` |
| Changes test infrastructure or CI | `test-automator` |
| Touches LLM prompts, model selection, evals | `prompt-engineer` |

A change can match more than one — pick all that fit. A change that matches none probably doesn't need review at this gate; say so.

**Show the user the auto-picked panel** before dispatch and ask via AskUserQuestion:
- **Run as picked** (Recommended)
- **Add or remove**
- **Skip review**

If "Add or remove": let the user write a freehand response listing which to drop and which to add.

**Dispatch in parallel** — single message, multiple Agent tool calls. Each brief includes:
- The Context (one paragraph version)
- The Research summary
- The full Implementation section
- An explicit instruction:
  > "Apply the `/pushback` skill — challenge this plan, don't validate it. Return blocking issues, should-fix items, and a one-line verdict. Use the smart-routing rules in `/pushback` to choose the questions that matter for this stage (designing / pre-implementation)."

Wait for **all** specialists to return before writing.

---

### Step 8: Integrate, present, wait

1. **Integrate findings.** Read each specialist's report. Don't bury feedback at the bottom — fold concrete changes into the Implementation section they affect. Use Edit to revise.

2. **Open questions.** Edit `## Open questions` with anything that's not blocking but needs a call from the user. One question per entry, with a sentence of context.

3. **Final clarifications.** If a specialist's feedback opened a real new tradeoff, ask 1-2 final questions via AskUserQuestion (one per call) before locking the plan.

4. **Verification section.** Edit `## Verification` with how to test the work end-to-end once it's built — what command, what to look for, what would prove it broken.

5. **Final ask.** Show the plan path and use AskUserQuestion:
   - **Implement now** — confirm the path; the user is expected to invoke implementation separately (e.g., `/triage` for ticket-driven work, or just "implement this plan"). The skill exits cleanly.
   - **Edit plan** — user wants to revise. Loop back to Step 6 (re-plan) or Step 7 (re-review).
   - **Defer** — leave the plan in the repo. The skill exits.

**Never start coding from this skill.** The artifact is the plan. Implementation is a separate invocation.

---

## Key Rules

1. **Plans live in `<repo-root>/plans/`.** Fall back to `~/.claude/plans/` only when not in a git repo, and tell the user.
2. **One question per AskUserQuestion call.** Never batch.
3. **Edit, don't rewrite.** After Step 1's skeleton, all section updates use Edit so user mid-flow tweaks survive.
4. **CEO must run as a subagent** (`subagent_type: "ceo"`) — the separate context is the unbiased-review property this skill depends on.
5. **Specialists in Step 7 must be briefed with explicit pushback framing** — not "review this," but "challenge this." A specialist who rubber-stamps got the wrong brief.
6. **Skip steps when obviously not applicable**, but note the skip in the plan (`_External research skipped — internal scope._`). Don't silently drop work.
7. **No code is written by this skill.** The artifact is the plan file. Implementation is a separate invocation.
8. **External research is best-effort.** If WebSearch and WebFetch return nothing useful, say so in the Research section. Don't pad with weak sources.
9. **The plan should read as a thought process, not a conclusion.** Considerations captures what was challenged and how it changed the proposal. That's what makes the plan reviewable later.
