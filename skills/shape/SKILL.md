---
name: shape
version: 1.1.0
description: |
  Take a half-formed task idea, research the codebase and the open web,
  challenge it with the CEO subagent, run the build plan through
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
  - Skill
  - AskUserQuestion
  - WebFetch
  - WebSearch
---

# Shape

Turn a half-formed idea into a refined plan. The skill researches the codebase and reads any URLs in the seed. It asks scope questions and scans the open web for prior art. It runs the proposal through the CEO subagent for adversarial product review, then runs the build plan through technical specialists in pushback mode. The artifact is a plan file in the project's `plans/` directory. The skill never writes code. It ends with an explicit "build now / defer" choice.

## Arguments
- `/shape <seed>`: shape the proposal in the seed (a sentence, a paragraph or a Slack pitch with URLs)
- `/shape`: with no args, ask once: "What's the idea you want to shape?"

## Cases for another skill
- They want to challenge one claim rather than plan work → use `/pushback` instead
- They want to diagnose a production issue → use `/investigate` instead
- The Linear ticket is already shaped and ready to execute → use `/triage` instead

## Instructions

Follow these steps in order. A step that plainly doesn't apply is skipped, with the skip noted in the plan (Key Rule 11).

---

### Step 0: Preflight

1. **Capture the seed.** If invoked as `/shape <text>`, that's the seed. If bare, ask once: "What's the idea you want to shape?" Do not proceed without a seed.

2. **Project-skill check.** Some repos have their own skill for this job. Check `~/.claude/context/<project>/resolutions.md` first (`<project>` = repo directory name): if it records a resolution for `shape`, follow it silently. Otherwise scan the project's skills (`<root>/skills/*/SKILL.md`, `<root>/.claude/skills/`, `<root>/.agents/skills/`, plus any project-scoped entries already in the available-skills listing) for one whose *output* covers turning an idea into a shaped plan or brief. No overlap → proceed. Overlap → ask via AskUserQuestion, one question:

   - **Use the project's skill (Recommended)**: invoke it via the Skill tool and end here. The project's workflow is the local law.
   - **Use this skill**: proceed as normal.
   - **Compose**: this skill's process with the project skill's output conventions (artifact home, format, naming).

   Append the choice to `resolutions.md` (create it if missing): `- shape → <choice> (<date>)`. Later runs follow it without asking. Unattended runs never ask. When there is no recorded resolution, skip this work and note the conflict in the run report. Leave the decision for an interactive session.

3. **Find (or create) the plan directory.** First find the repo root:
   ```bash
   git rev-parse --show-toplevel 2>/dev/null
   ```
   On failure (not a git repo): plan dir = `~/.claude/plans/`. Tell the user explicitly: "Not in a git repo, falling back to `~/.claude/plans/`." Skip the rest of this step.

   On success, run a **discovery pass** and check paths like these:

   1. `<root>/docs/plans/`
   2. `<root>/plans/`
   3. `<root>/rfcs/`
   4. `<root>/designs/`
   5. `<root>/.agents/plans/` (and `<root>/apps/*/.agents/plans/` if monorepo)

   If none exist, create `<root>/plans/`.

   When you use a discovered directory, **read** any `README.md`, `AGENTS.md`, `CLAUDE.md`, or `TEMPLATE.md` inside it before writing the skeleton. These define the project's plan conventions: sections, ordering, frontmatter, naming, subdirectory routing (e.g. `active/` vs `completed/`).

   **If a `TEMPLATE.md` exists, ask the user via AskUserQuestion which format to follow** before writing the skeleton:

   - **Repo template (Recommended)**: copy `<path>/TEMPLATE.md`'s structure verbatim. The new plan then matches the existing ones in the directory. This matters more when the repo has a populated `active/` folder and a routine of moving plans to `completed/`.
   - **Shape skill default**: use the seven-section skeleton (`Context`, `Research`, `Considerations`, `Implementation`, `Open questions`, `Out of scope`, `Verification`). Pick this when the repo template is heavy-process and gets in the way of a shaping artifact, or when the user just wants the skill's normal structure.

   Recommend the repo template by default (repos that bother to write a TEMPLATE.md usually want consistency), but let the user override in one click. Whichever they pick, one rule applies regardless: "Out-of-scope is one section near the end" (see Step 1).

   If the user picked the repo template and the template has sections that won't be filled during shaping (e.g. "Surprises & Discoveries", "Idempotence and Recovery"), leave them as `_To be filled as work progresses._` placeholders rather than inventing content.

   If subdirectories exist (e.g. `active/` and `completed/`), pick the one for in-flight work (usually `active/`).

   Tell the user the chosen path. Distinguish discovered ("using existing `<path>`") from created ("creating `<path>`"). If the user picked the repo template, mention "following `<path>/TEMPLATE.md`" so they know the structure isn't being invented.

4. **Extract URLs** from the seed using a simple regex (`https?://[^\s)]+`). Queue them for Step 2's URL reading.

5. **Generate the slug.** Aim for **2 to 4 words, ≤32 chars**, lowercase, hyphen-separated. Strip qualifiers, hedges, and parentheticals. Bias toward the *core noun phrase that identifies the change* rather than the surrounding context.

   Examples:
   - ✅ `webhook-retry-gap` instead of `payment-provider-webhook-retry-gap-handling`
   - ✅ `model-routing` instead of `model-routing-via-openrouter`
   - ✅ `agreements` instead of `structured-agreement-fields-and-signing-workflows`

   If `<plan-dir>/<slug>.md` already exists, append a 4-char hash to the slug. The plan title (the `# H1` in the file) must match the slug's intent: short and action-oriented, without parentheticals.

---

### Step 1: Create the empty plan file

Use Write to create the skeleton at `<plan-dir>/<slug>.md`.

**If the user picked the repo template in Step 0.3:** copy that template's structure verbatim. Title goes at the top. Sections that won't be filled by shaping (status logs, rollback notes, etc.) get `_To be filled as work progresses._` placeholders. **Out-of-scope still goes near the end as its own section** even if the template doesn't show one. That's the one structural rule this skill imposes regardless of template.

**Otherwise (no TEMPLATE.md, or the user picked this skill's default), use this default skeleton:**

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

Out-of-scope is **second-to-last, before Verification**, and is the *only* place where out-of-scope content is written. Context does not restate it, and `Implementation` does not have its own out-of-scope subsection.

Tell the user the file path. From here on, **all section updates use Edit** rather than Write. That preserves any manual edits the user makes mid-flow.

---

### Step 2: Codebase + URL research

This is groundwork. Do not write any plan section yet.

**Codebase exploration.** Use Read, Glob, Grep to find the files, models, services, configs the seed touches. Light, not deep:
- Names of relevant files
- Existing patterns to extend or replace
- Where the change boundary likely sits

Mirror the lightness of shaping work. Do not map every callback, scope, or association. That's `/investigate`'s job.

**URL reading.** For each URL queued in Step 0, WebFetch it. Capture 2-3 sentences per URL: what it is, what's relevant. Don't paste full pages anywhere.

If the seed includes obvious technical terms with no codebase hits (e.g., "OpenRouter" when the repo has no LLM client yet), say so. That's signal about scope.

---

### Step 3: Initial questions → write Context

Ask **2-3 questions max** via AskUserQuestion. **One per call.** Skip questions whose answers are already in the seed or obvious from the code.

Focus on:
- **Scope boundaries**: what's in, what's out
- **Target user**: whose problem does this solve, by role
- **Constraints**: deadlines, platform requirements, hard nos
- **Success criteria**: what changes once this is released

**These rules apply to how Context is written, regardless of seed:**

> **Use roles instead of names.** Refer to people by role: "the customer's accountant", "Finance", "the team", "the on-call engineer", "we". **Never name individuals**, whether engineers, customers, accountants, employees, contractors, or internal teammates. Repos can be public, and team members rotate. Specific names rot and create awkwardness when the spec is still in use after the people in it have left. Substitute role-based references even when the seed uses names verbatim.
>
> **Abstract the trigger, don't transcribe it.** Context narrates *what class of problem* and *what user-visible behavior*, and leaves out the specific incident that prompted it. **Do not** include charge IDs, invoice numbers, customer names, exact amounts, or exact dates in Context. Those identifiers belong in Verification, where they help reproduce or sanity-check a fix; in Context, they read like an incident transcript and date the spec.

Example transformation:

> ❌ "Jane Doe (their accountant) noticed only because reconciliation flagged the gap. The workaround is the manual script John Smith ran for Acme Corp on Mar 16 2026 (charge `ch_abc123`, $85,926)."
>
> ✅ "The gap was caught downstream by reconciliation, after the customer-facing payment had already succeeded. The affected invoice was patched manually. This plan is the forward fix so it doesn't recur."

After answers, Edit the `## Context` section to capture:
- The problem in one paragraph (what's broken / missing today, anonymized and abstract per the rules above)
- The proposed direction (one sentence)
- Scope (**in only**, since out-of-scope content is written in its own section near the end of the file)
- Constraints (as bullets)
- Links to the URLs you read in Step 2 with a one-line summary each

Keep it scannable. A reader should grok the work in 60 seconds.

---

### Step 4: External research → write Research

WebSearch for how others solve the same problem. Pick queries from the seed's domain language. Examples:
- "OpenRouter model routing rate limiting"
- "Stripe webhook idempotency"
- "ActiveJob retry exponential backoff Sidekiq"

Read 2-3 results via WebFetch. **Drop weak sources** (marketing pages, a Hacker News thread with no signal, blog spam). Don't pad.

Edit `## Research` with:
- Each useful source as a bullet: `- [title](url) — 1-2 lines on what's worth borrowing`
- A short paragraph: "What we'd borrow / what we wouldn't."

**Skip this step entirely** when the work is obviously internal-only (a config tweak, a known-pattern refactor, a one-file change). Do not note the skip, just remove the section.

---

### Step 5: CEO adversarial → write Considerations

Dispatch the `ceo` subagent via the Agent tool with `subagent_type: "ceo"`. The CEO runs in its own context window. That's the unbiased-review property the skill depends on.

The brief must include:
- The seed prompt verbatim
- The Context section just written
- The Research section's "what we'd borrow / what we wouldn't" paragraph
- An explicit ask:
  > "Challenge this end-to-end. Apply your usual interrogation. Don't rubber-stamp. Return your verdict (Solid / Weak / What to bring back) and the specific concerns I should reflect back to the user."

When the CEO returns:

**If the verdict reports real concerns:**
1. Brainstorm 2-3 ways to address them (as concrete options, not "we could think about…").
2. Present via AskUserQuestion. Each option is a directional choice ("Narrow the wedge to X first", "Keep scope but add Y guardrail", etc.). The user can pick "Other" to write their own.
3. Edit `## Considerations` to capture each surviving concern as **integrated prose owned by one voice**. Each paragraph says what the concern is and why it's real. It then says how the proposal answers it. These rules apply to the writing:

   > **Hide the machinery**, because the reader doesn't care which subagent raised which concern. **Never** use headings, labels, or framings like "CEO challenge", "User response", "What changed", "Architect-reviewer", "Tester verdict", "Specialist pushback", **and do not name subagents at all.** The Considerations section should read as if one engineer wrote it after thinking hard about the proposal.
   >
   > **Synthesize, don't transcribe.** Each concern that was kept in the plan becomes one short paragraph in prose, without `**Why:**` / `**How to apply:**` style scaffolding, transcript-style call-and-response, or "the user said" framing.
   >
   > **Drop concerns the team chose not to act on.** A list of rejected concerns is noise. Only immortalize a concern if either (a) it changed the plan, or (b) the *reasoning for setting it aside* is non-obvious and useful to a later reviewer.

Someone reading the plan a month later should see the **thought process**, written as the writer's own reasoning rather than as a transcript of the shaping session.

**If the CEO greenlights with no real concerns:** move on.
---

### Step 5.5: Verify riskiest assumptions against production data

Some surviving concerns from Step 5 (and sometimes claims already written into Context from Step 3) rest on the current state of production data rather than on what the code or schema suggests. Examples are schema reality, row distributions, query plans, lock behavior, and whether the bad combination of states already exists in the wild. Code reading tells you what *could* happen, while production data tells you what *did*. Ratify those claims before they are written into `Implementation`.

For each surviving claim of this kind, invoke `/query` with the narrowest assertion that, if confirmed or refuted, moves the plan forward. Examples:

- `/query "no Account record has a NULL primary_subscription_id"`
- `/query "the existing index_accounts_on_user_id is used by the proposed query plan"`
- `/query "rows where status='active' AND archived_at IS NOT NULL exist"`

`/query` writes the script, the user runs it, and returns one of `Confirmed`, `Refuted`, or `Inconclusive` with cited evidence. Use the verdicts to:

- **`Confirmed`**: the assumption is true. Carry it into Step 6.
- **`Refuted`**: the design rested on a wrong premise. Loop back to Step 5 (re-brainstorm with the new information) or Step 3 (revise Context). Do not write `Implementation` on a refuted assumption.
- **`Inconclusive`**: record it in Step 8's `## Open questions` with the specific query, count, or plan that would resolve it. `Implementation` can proceed, and the gap is stated so the next reader sees it.

**When to skip.** Skip when no surviving claim concerns current data state, as with pure config tweaks, prose, UX-only work, or claims about future demand / user behavior / cross-system bets (those belong to `/pushback` and the CEO interrogation). When the skip applies, say so in the plan once: `_Production-data verification skipped — no claims rest on current data state._`

**Hide the machinery.** Like Step 5, the verification itself doesn't show up in the plan file as scaffolding. Confirmed findings fold into Considerations or `Implementation` as if the writer just knew them. Refuted claims become dropped (or reshaped) plan items rather than "we asked `/query` and it said no" call-outs. Write in one voice without a transcript, the same rule as Step 5 and Step 8.1.

---

### Step 6: Build plan → write `Implementation`

Edit `## Implementation` with:
- **Files to create / modify**: bulleted list with one line per file on what changes
- **Sequence**: what is built first and what comes after, and what depends on what
- **Hard tradeoffs**: for each, state the tradeoff and the chosen side ("Use Solid Queue over Sidekiq because we're already on Rails 8 and want one fewer infra dep")
- **Effort sense**: only if asked. Otherwise skip.

Be detailed but not overly verbose.

**Do not** add an "Out of scope" subsection inside `Implementation`. All out-of-scope content belongs in the canonical `## Out of scope` section near the end of the file (see Step 1), which is the one section for it in the whole file.

---

### Step 7: Technical specialists, adversarial mode

**Auto-pick reviewers by domain** based on the `Implementation` section. Mapping:

| Trigger in the plan | Specialist |
|---|---|
| Touches auth, crypto, secrets, input validation, dependency surfaces | `security-auditor` |
| Introduces new abstractions, cross-service boundaries, schema migrations, public APIs | `architect-reviewer` |
| Hot paths, new queries (especially in loops), cache changes, async/sync swaps | `performance-engineer` |
| Adds critical paths that need testing, changes test strategy, test infrastructure, or CI | `tester` |
| Touches LLM prompts, model selection, evals | `prompt-engineer` |

A change can match more than one specialist, in which case pick all that fit. A change that matches none probably doesn't need review at this gate, and you should say so.

**Show the user the auto-picked panel** before dispatch and ask via AskUserQuestion:
- **Run as picked** (Recommended)
- **Add or remove**
- **Skip review**

If "Add or remove": let the user write a freehand response listing which to drop and which to add.

**Dispatch in parallel**, in one message with multiple Agent tool calls. Each brief includes:
- The Context (one paragraph version)
- The Research summary
- The full `Implementation` section
- An explicit instruction:
  > "Apply the `/pushback` skill: challenge this plan, don't validate it. Return blocking issues, should-fix items, and a one-line verdict. Use the smart-routing rules in `/pushback` to choose the questions that matter for this stage (designing / pre-build)."

Wait for **all** specialists to return before writing.

---

### Step 8: Integrate, present, wait

1. **Integrate findings.** Read each specialist's report. Don't bury feedback at the bottom. Fold concrete changes into the `Implementation` section they affect. Use Edit to revise.

   **The integration is silent.** Specialist names, "verdict" labels, and "blocking / should-fix" bucketing are scaffolding. They belong in the specialist's report and never in the plan file. When a finding causes a change, the plan reflects the change as if the writer thought of it. When a finding adds a new tradeoff to Considerations, write it as one paragraph of integrated reasoning, never as "Architect-reviewer flagged X". Same rule as Step 5: hide the machinery.

2. **Open questions.** Edit `## Open questions` with anything that's not blocking but needs a call from the user. One question per entry, with a sentence of context.

3. **Out of scope.** Edit `## Out of scope` with anything that came up during shaping but is not in this plan. Examples are explicit non-goals, related work that should be a separate plan, and things deliberately deferred. Write one bullet per item with one short reason each. This is the **only** out-of-scope section in the file (without duplication in Context or a subsection inside `Implementation`).

4. **Final clarifications.** If a specialist's feedback opened a real new tradeoff, ask 1-2 final questions via AskUserQuestion (one per call) before locking the plan.

5. **Verification section.** Edit `## Verification` with how to test the work end-to-end once it's built (what command, what to look for, what would prove it broken). **This is where specific identifiers from the seed (charge IDs, invoice numbers, exact amounts, dates) are allowed and useful**, because they help reproduce or sanity-check the fix in production.

6. **Self-audit.** Re-read the plan end-to-end as if you'd never seen it before. The plan has been built section by section under different lenses (CEO, specialists, user clarifications). That makes drift between sections the default rather than the exception. Catch it before the user does.

   Run these checks against the file you just wrote, and **edit in place** to fix any gaps you find. Do not put "audit notes" in the plan. The integration is silent, same as Step 5 and 8.1. The reader sees a coherent plan, and the caught inconsistencies are fixed in place rather than listed.

   - **Coverage.** For every in-scope item in Context, find the corresponding entry in `Implementation`. If a scope item has no build step, either add the step or move the item to Out of scope. Coverage gaps are the most common drift, because Context grew during clarifications and `Implementation` didn't.
   - **Considerations are addressed as well as listed.** For every concern in Considerations, the plan must show how it's answered. The answer can be a specific change in `Implementation` or a constraint in Context. It can also be an explicit "we accept this risk because…" clause inside the Considerations paragraph itself. A Consideration that's only described and never resolved is a tradeoff the writer didn't actually make.
   - **Verification matches the success criteria.** Whatever Context implies about what "released" looks like must be testable from Verification. If Context says "the customer's accountant sees one line item per deposit," Verification needs a step that proves exactly that rather than a generic "check the invoice renders."
   - **Sections do not contradict each other.** Out of scope must not list something Context says is in scope. `Implementation` must not depend on something Out of scope rules out. Open questions must not duplicate something Considerations already settled.
   - **No orphan bullets.** Every bullet in `Implementation` should connect to a scope item or a Consideration, or otherwise to a constraint. Bullets that exist for their own sake are over-engineering that survived integration.

   Tell the user: *"Self-audit found N gaps, addressed them in the plan."* or *"Self-audit clean."* Use one short line without a list. The user can read the diff if they want details.

7. **Final ask.** Show the plan path and use AskUserQuestion:
   - **Build now**: confirm the path. The user is expected to start the build separately (e.g., `/triage` for ticket-driven work, or just `implement this plan`). The skill exits cleanly.
   - **Edit plan**: user wants to revise. Loop back to Step 6 (re-plan) or Step 7 (re-review).
   - **Defer**: leave the plan in the repo. The skill exits.

**Never start coding from this skill.** The artifact is the plan. The build is a separate invocation.

---

## Key Rules

1. **The spec is the artifact, the process isn't.** Nothing in the plan file should reveal how it was produced. That rules out subagent names ("CEO", "architect-reviewer", "tester"), procedural subheadings ("CEO challenge", "User response", "Specialist pushback", "Verdict"), and "the user said" framing. A reader six months from now should see one coherent voice rather than a transcript of the shaping session.
2. **Use roles instead of names.** Refer to people by role ("the customer's accountant", "Finance", "the team", "we"). Never name individuals (engineers, customers, teammates), even when the seed uses names verbatim. Repos can be public and team members rotate. Specific names rot.
3. **Abstract narrative, specific verification.** Context narrates the *class of problem* in role-based, identifier-free prose. Specific charge IDs, invoice numbers, exact amounts, and exact dates only appear in `## Verification`, where they help reproduce or sanity-check.
4. **Plan directory: discover first, default last.** Step 0.3 checks `docs/plans/`, `plans/`, `rfcs/`, `designs/`, `.agents/plans/`. When a `TEMPLATE.md` is detected, the user picks (repo template vs. skill default). The skill recommends the repo template but doesn't override silently. Fall back to `~/.claude/plans/` only when not in a git repo, and tell the user.
5. **Out-of-scope is written in exactly one section, near the end** (before Verification). Context contains in-scope only, and `Implementation` has no out-of-scope subsection.
6. **Slugs are tight.** 2 to 4 words, ≤32 chars, the core noun phrase. The plan title matches the slug's intent.
7. **One question per AskUserQuestion call.** Never batch.
8. **Edit, don't rewrite.** After Step 1's skeleton, all section updates use Edit so user mid-flow tweaks survive.
9. **CEO must run as a subagent** (`subagent_type: "ceo"`). The separate context is the unbiased-review property this skill depends on.
10. **Specialists in Step 7 must be briefed with explicit pushback framing.** The brief says "challenge this" rather than "review this." A specialist who rubber-stamps got the wrong brief.
11. **Skip steps when obviously not applicable**, but note the skip in the plan (`_External research skipped — internal scope._`). Don't silently drop work.
12. **This skill never writes code.** The artifact is the plan file. The build is a separate invocation.
13. **External research is best-effort.** If WebSearch and WebFetch return nothing useful, say so in the Research section. Don't pad with weak sources.
14. **The plan should read as a thought process rather than a conclusion.** Considerations captures what was challenged and how it changed the proposal, synthesized in one voice rather than transcribed as a back-and-forth. That's what makes the plan reviewable later.
15. **Self-audit before final ask.** A plan built section by section under different lenses drifts. The audit (Step 8.6) re-reads the whole plan and catches coverage gaps between Context and `Implementation`, unanswered Considerations, Verification that doesn't match the success criteria, and contradictions between sections. Edit in place and never expose the audit as scaffolding in the plan file.
16. **Verify the riskiest design bets against production data.** Step 5.5 invokes `/query` for any surviving claim about the current state of data, such as schema reality, row distributions, query plans, lock behavior, or status combinations. Refuted claims rewrite the plan, and inconclusive ones are recorded in Open questions. `/query` is for the current state of production rather than for its future state. Demand and behavior belong to `/pushback` and the CEO.
17. **The publishability test extends "roles instead of names" to domains.** This library is public: plans may contain project specifics (they're gitignored), but nothing written back into skills, commands, or agents may mention an employer, product, customer, internal service, or industry domain. Examples in prompt files use neutral SaaS vocabulary (orders, accounts, subscriptions, webhooks).
