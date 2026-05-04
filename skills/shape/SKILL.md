---
name: shape
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

# Shape

Turn a half-formed idea into a refined plan. The skill researches the codebase, reads any URLs in the seed, asks scope questions, scans the open web for prior art, runs the proposal through the CEO subagent for adversarial product review, then runs the implementation plan through technical specialists in pushback mode. The artifact is a plan file in the project's `plans/` directory. The skill never writes code — it ends with an explicit "implement now / defer" choice.

## Arguments
- `/shape <seed>` — shape the proposal in the seed (a sentence, a paragraph, a Slack pitch with URLs)
- `/shape` — with no args, ask once: "What's the idea you want to shape?"

## When this is the wrong skill
- They want to challenge a single claim, not plan work → use `/pushback` instead
- They want to diagnose a production issue → use `/investigate` instead
- The Linear ticket is already shaped and ready to execute → use `/triage` instead
- They want hours/days for a clear scope → use `/estimate` instead

## Instructions

Follow these steps in order. Do NOT skip steps unless the step explicitly says it can be skipped.

---

### Step 0: Preflight

1. **Capture the seed.** If invoked as `/shape <text>`, that's the seed. If bare, ask once: "What's the idea you want to shape?" Do not proceed without a seed.

2. **Find (or create) the plan directory.** First find the repo root:
   ```bash
   git rev-parse --show-toplevel 2>/dev/null
   ```
   On failure (not a git repo): plan dir = `~/.claude/plans/`. Tell the user explicitly: "Not in a git repo — falling back to `~/.claude/plans/`." Skip the rest of this step.

   On success, **discovery pass** — check paths like these:

   1. `<root>/docs/plans/`
   2. `<root>/plans/`
   3. `<root>/rfcs/`
   4. `<root>/designs/`
   5. `<root>/.agents/plans/` (and `<root>/apps/*/.agents/plans/` if monorepo)

   If none exist, create `<root>/plans/`.

   When you use a discovered directory, **read** any `README.md`, `AGENTS.md`, `CLAUDE.md`, or `TEMPLATE.md` inside it before writing the skeleton. These define the project's plan conventions — sections, ordering, frontmatter, naming, subdirectory routing (e.g. `active/` vs `completed/`). The project's conventions win over this skill's defaults.

   If a `TEMPLATE.md` exists, treat it as **binding** for sections, ordering, and any required frontmatter — it overrides the default skeleton in Step 1. The only rule from this skill that still applies regardless is "Out-of-scope is a single section near the end" (see Step 1). If the template has sections that don't get filled during shaping (e.g. "Surprises & Discoveries", "Idempotence and Recovery"), leave them as `_To be filled as work progresses._` placeholders rather than inventing content.

   If subdirectories exist (e.g. `active/` and `completed/`), pick the one for in-flight work (usually `active/`).

   Tell the user the chosen path. Distinguish discovered ("using existing `<path>`") from created ("creating `<path>`"). If a TEMPLATE.md was found, mention "following `<path>/TEMPLATE.md`" so they know the structure isn't being invented.

3. **Extract URLs** from the seed using a simple regex (`https?://[^\s)]+`). Queue them for Step 2's URL reading.

4. **Generate the slug.** Aim for **2–4 words, ≤32 chars**, lowercase, hyphen-separated. Strip qualifiers, hedges, and parentheticals. Bias toward the *core noun phrase that names the change*, not the surrounding context.

   Examples:
   - ✅ `eor-deposit-gap` — not `other-invoice-accounting-items-eor-deposit-gap`
   - ✅ `model-routing` — not `model-routing-via-openrouter`
   - ✅ `agreements` — not `structured-agreement-fields-and-signing-workflows`

   If `<plan-dir>/<slug>.md` already exists, append a 4-char hash to the slug. The plan title (the `# H1` in the file) must match the slug's intent — short, action-oriented, no parentheticals.

---

### Step 1: Create the empty plan file

Use Write to create the skeleton at `<plan-dir>/<slug>.md`.

**If Step 0.2 found a project `TEMPLATE.md`:** copy that template's structure verbatim. Title goes at the top. Sections that won't be filled by shaping (status logs, rollback notes, etc.) get `_To be filled as work progresses._` placeholders. **Out-of-scope still goes near the end as its own section** even if the template doesn't show one — that's the one structural rule this skill imposes regardless of template.

**Otherwise, use this default skeleton:**

```markdown
# <short, action-oriented title>

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

## Out of scope

_Pending — filled with anything that came up during shaping but is not in this plan._

## Verification

_Pending._
```

Out-of-scope is **second-to-last, before Verification**, and is the *only* place out-of-scope content lives — Context does not restate it, Implementation does not have its own out-of-scope subsection.

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
- **Target user** — whose problem does this solve, by role
- **Constraints** — deadlines, platform requirements, hard nos
- **Success criteria** — what changes if this ships

**Two rules govern how Context is written, regardless of seed:**

> **Roles, not names.** Refer to people by role: "the customer's accountant", "Finance", "the team", "the on-call engineer", "we". **Never name individuals** — engineers, customers, accountants, employees, contractors, internal teammates. Repos can be public; team members rotate; specific names rot and create awkwardness when the spec outlives the people in it. Substitute role-based references even when the seed uses names verbatim.
>
> **Abstract the trigger, don't transcribe it.** Context narrates *what class of problem* and *what user-visible behavior* — not the specific incident that prompted it. **Do not** include charge IDs, invoice numbers, customer names, exact amounts, or exact dates in Context. Those identifiers belong in Verification, where they help reproduce or sanity-check a fix; in Context, they read like an incident transcript and date the spec.

Example transformation:

> ❌ "Jane Doe (their accountant) noticed only because reconciliation flagged the gap. The workaround is the manual script John Smith ran for Acme Corp on Mar 16 2026 (charge `ch_abc123`, $85,926)."
>
> ✅ "The gap was caught downstream by reconciliation, after the customer-facing payment had already succeeded. The affected invoice was patched manually; this plan is the forward fix so it doesn't recur."

After answers, Edit the `## Context` section to capture:
- The problem in one paragraph (what's broken / missing today, anonymized and abstract per the rules above)
- The proposed direction (one sentence)
- Scope (**in only** — out-of-scope lives in its own section near the end of the file)
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

**Skip this step entirely** when the work is obviously internal-only (a config tweak, a known-pattern refactor, a one-file change). Do not note the skip, just remove the section.

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
3. Edit `## Considerations` to capture each surviving concern as **integrated prose owned by one voice** — what the concern is, why it's real, and how the proposal answers it. Three rules govern the writing:

   > **Hide the machinery.** The reader doesn't care which subagent raised which concern. **Never** use headings, labels, or framings like "CEO challenge", "User response", "What changed", "Architect-reviewer", "Tester verdict", "Specialist pushback". **Never name subagents at all.** The Considerations section should read as if one engineer wrote it after thinking hard about the proposal.
   >
   > **Synthesize, don't transcribe.** Each concern that survived into the plan becomes one short paragraph in prose. No `**Why:**` / `**How to apply:**` style scaffolding, no transcript-style call-and-response, no "the user said".
   >
   > **Drop concerns the team chose not to act on.** A list of rejected concerns is noise. Only immortalize a concern if either (a) it changed the plan, or (b) the *reasoning for setting it aside* is non-obvious and worth preserving for a later reviewer.

The point is for someone reading the plan a month later to see the **thought process** — but as the writer's reasoning, not as a transcript of the shaping session.

**If the CEO greenlights with no real concerns:** move on.
---

### Step 6: Implementation plan → write Implementation

Edit `## Implementation` with:
- **Files to create / modify** — bulleted list with one line per file on what changes
- **Sequence** — what ships first, what comes after, what depends on what
- **Hard tradeoffs** — for each, name the tradeoff and the chosen side ("Use Solid Queue over Sidekiq because we're already on Rails 8 and want one fewer infra dep")
- **Effort sense** — only if asked. Otherwise skip; that's `/estimate`'s job.

Be detailed but not overly verbose.

**Do not** add an "Out of scope" subsection inside Implementation. All out-of-scope content belongs in the canonical `## Out of scope` section near the end of the file (see Step 1). One section, one place.

---

### Step 7: Technical specialists, adversarial mode

**Auto-pick reviewers by domain** based on the Implementation section. Mapping:

| Trigger in the plan | Specialist |
|---|---|
| Touches auth, crypto, secrets, input validation, dependency surfaces | `security-auditor` |
| Introduces new abstractions, cross-service boundaries, schema migrations, public APIs | `architect-reviewer` |
| Hot paths, new queries (especially in loops), cache changes, async/sync swaps | `performance-engineer` |
| Adds critical paths that need testing, changes test strategy, test infrastructure, or CI | `tester` |
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

   **The integration is silent.** Specialist names, "verdict" labels, and "blocking / should-fix" bucketing are scaffolding — they belong in the specialist's report, not in the plan file. When a finding causes a change, the plan reflects the change as if the writer thought of it; when a finding causes a new tradeoff to surface in Considerations, write it as one paragraph of integrated reasoning, never as "Architect-reviewer flagged X". Same rule as Step 5: hide the machinery.

2. **Open questions.** Edit `## Open questions` with anything that's not blocking but needs a call from the user. One question per entry, with a sentence of context.

3. **Out of scope.** Edit `## Out of scope` with anything that came up during shaping but is not in this plan — explicit non-goals, related work that should be a separate plan, things deliberately deferred. One bullet per item, one short reason each. This is the **only** out-of-scope section in the file (no duplication in Context, no subsection inside Implementation).

4. **Final clarifications.** If a specialist's feedback opened a real new tradeoff, ask 1-2 final questions via AskUserQuestion (one per call) before locking the plan.

5. **Verification section.** Edit `## Verification` with how to test the work end-to-end once it's built — what command, what to look for, what would prove it broken. **This is where specific identifiers from the seed (charge IDs, invoice numbers, exact amounts, dates) are allowed and useful** — they help reproduce or sanity-check the fix in production.

6. **Final ask.** Show the plan path and use AskUserQuestion:
   - **Implement now** — confirm the path; the user is expected to invoke implementation separately (e.g., `/triage` for ticket-driven work, or just "implement this plan"). The skill exits cleanly.
   - **Edit plan** — user wants to revise. Loop back to Step 6 (re-plan) or Step 7 (re-review).
   - **Defer** — leave the plan in the repo. The skill exits.

**Never start coding from this skill.** The artifact is the plan. Implementation is a separate invocation.

---

## Key Rules

1. **The spec is the artifact, the process isn't.** Nothing in the plan file should reveal how it was produced — no subagent names ("CEO", "architect-reviewer", "tester"), no procedural subheadings ("CEO challenge", "User response", "Specialist pushback", "Verdict"), no "the user said" framing. A reader six months from now should see one coherent voice, not a transcript of the shaping session.
2. **Roles, not names.** Refer to people by role ("the customer's accountant", "Finance", "the team", "we"). Never name individuals — engineers, customers, teammates — even when the seed uses names verbatim. Repos can be public; team members rotate; specific names rot.
3. **Abstract narrative; specific verification.** Context narrates the *class of problem* in role-based, identifier-free prose. Specific charge IDs, invoice numbers, exact amounts, and exact dates only appear in `## Verification`, where they help reproduce or sanity-check.
4. **Plan directory: discover first, default last.** Step 0.2 checks `docs/plans/`, `plans/`, `rfcs/`, `designs/`, `.agents/plans/`. Project conventions (README, AGENTS, TEMPLATE) win over this skill's defaults. Fall back to `~/.claude/plans/` only when not in a git repo, and tell the user.
5. **Out-of-scope lives in exactly one section, near the end** (before Verification). Context contains in-scope only; Implementation has no out-of-scope subsection.
6. **Slugs are tight.** 2–4 words, ≤32 chars, the core noun phrase. The plan title matches the slug's intent.
7. **One question per AskUserQuestion call.** Never batch.
8. **Edit, don't rewrite.** After Step 1's skeleton, all section updates use Edit so user mid-flow tweaks survive.
9. **CEO must run as a subagent** (`subagent_type: "ceo"`) — the separate context is the unbiased-review property this skill depends on.
10. **Specialists in Step 7 must be briefed with explicit pushback framing** — not "review this," but "challenge this." A specialist who rubber-stamps got the wrong brief.
11. **Skip steps when obviously not applicable**, but note the skip in the plan (`_External research skipped — internal scope._`). Don't silently drop work.
12. **No code is written by this skill.** The artifact is the plan file. Implementation is a separate invocation.
13. **External research is best-effort.** If WebSearch and WebFetch return nothing useful, say so in the Research section. Don't pad with weak sources.
14. **The plan should read as a thought process, not a conclusion.** Considerations captures what was challenged and how it changed the proposal — synthesized in one voice, not transcribed as a back-and-forth. That's what makes the plan reviewable later.
