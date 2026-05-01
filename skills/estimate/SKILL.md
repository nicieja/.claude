---
name: estimate
version: 1.0.0
description: |
  Produce an honest engineering estimate in hours/days for a task by exploring
  the codebase, surfacing unknowns, and recursively breaking the work into
  smaller chunks when the estimate gets too big or too wide to be reliable.
  Bias toward ranges and named unknowns over single numbers.
allowed-tools:
  - Read
  - Glob
  - Grep
  - AskUserQuestion
---

# /estimate — Honest Engineering Estimate

Estimate a task in hours/days from pasted context (issue description, discussion, comments). Explore the affected code, surface unknowns, give a range, and recursively break the task into smaller chunks if the estimate is too coarse to be reliable.

## Arguments
- `/estimate <pasted context>` — task description, ticket dump, discussion thread, or comments
- `/estimate` — with no args, ask the user to paste context

## When this is the wrong skill
- Scope is fuzzy and you want it sharpened first → run `/pushback` to harden the scope, then come back
- They want to *implement* it → use a different skill
- They want a step-by-step plan, not a duration estimate → use plan mode

---

## Anti-sycophancy rules

Estimation rots when you wave the hand. These are non-negotiable:

- **No single number.** Always a range. A point estimate hides what you don't know.
- **No padding for safety.** If you'd inflate "just in case," that "case" is an unknown — surface it instead.
- **No silent assumptions.** If the estimate depends on "we'll skip tests" or "no migration needed," say so.
- **No estimating from the title alone.** The title is a label. The body, comments, and code are the work.
- **No estimate from text alone.** Code exploration is mandatory before any number leaves your mouth.

---

## Assume AI-enhanced collaboration

The user works with Claude Code in the loop. Estimates **must** reflect that, not solo-human duration. The split is:

- **AI compresses heavily:** scaffolding, boilerplate, drafting tests, generating new files that follow an existing pattern, search/exploration, syntax-level edits, regex/migrations across many files.
- **AI barely compresses:** architecture decisions (e.g. approach A vs B), human review of generated code, validation against real systems, debugging when the AI is wrong, stakeholder/design wait time, deploy and rollout.

Rules of thumb when sizing:
- A task that is 80% typing → roughly 0.3–0.5x solo duration.
- A task that is 50/50 typing and decision/review → roughly 0.5–0.7x solo duration.
- A task that is mostly judgment, integration, or waiting on others → 0.8–1.0x solo duration. AI doesn't help much.

State the assumed split when it materially shifts the number. If the task is decision-heavy, say so — don't pretend AI makes decisions cheap.

---

## Workflow

### Step 0: Restate the task

In 1–2 sentences, restate the task. Include:
- The user-visible change (or system change if it's pure infra)
- The surfaces touched (UI, API, jobs, schema, etc.)
- What "done" looks like

If you can't restate it clearly, the context is too thin. Ask the user **one** focused question to fill the gap before exploring code.

### Step 1: Explore the code (MANDATORY)

Use Read, Glob, Grep to ground the estimate. Map:

- **Affected files / packs / modules** — which models, services, components, jobs change
- **Existing patterns to follow** — does similar code already exist? An existing pattern usually halves the work
- **Integration points** — callers, callees, public APIs, database tables, queues
- **Test surface** — what test files exist, what coverage looks like, whether you'll need new fixtures
- **Hidden complexity** — state machines, feature flags, multi-tenancy, async jobs, callbacks, polymorphism

Don't read the whole repo. Aim for **enough exploration to spot the obvious traps**, not a complete map. If exploration reveals the task touches surfaces the description didn't mention, flag it.

### Step 2: First-pass estimate

Produce an initial range in hours or days for the whole task.

**Sizing anchors (AI-enhanced — already adjusted for Claude Code in the loop):**
- **< 1h** — typo, copy change, single-file constant tweak
- **1–2h** — small change in an existing pattern, no migration, no new test setup
- **2–4h** — feature touching 2–3 files with tests, simple migration
- **0.5–1d** — multi-file feature, new pattern, new tests, careful integration
- **1–2d** — cross-cutting change, schema + service + UI, edge cases
- **> 2d** — too big to estimate as one unit. **Break it down (Step 3).**

If the task is mostly decision/review/integration (AI doesn't help), shift one anchor up.

**Range rules:**
- Lower bound = optimistic case (everything as you expect, no surprises).
- Upper bound = the named unknowns realized. If you can't justify the upper bound by pointing to specific unknowns, the upper bound is wrong.
- If `upper / lower > 3`, the range is too wide — break it down.

### Step 3: Break-down loop

Trigger break-down when **any** of these is true:
- Upper bound > 3 days
- `upper / lower > 3` (range too wide to be useful)
- More than ~3 unknowns that each meaningfully shift the estimate
- The task spans multiple independent surfaces (e.g., "API + UI + migration + new job")

**How to break down:**

1. Split the task into **independently-shippable chunks**. Each chunk should:
   - Have a clear "done" state
   - Touch a coherent surface (one pack, one feature area)
   - Be estimable in < 3 days as a single unit
2. For each chunk, re-run Step 1 (explore) and Step 2 (estimate).
3. **Recurse**: if a chunk's estimate triggers break-down again, split it further.
4. **Cap at 3 levels of nesting.** If you're still triggering break-down at level 3, the task isn't ready to estimate — say so explicitly. The output is "this needs scoping work, not estimation," not a fake number.
5. Sum the chunk ranges for a total. Note any **cross-cutting unknowns** that affect the total beyond the per-chunk sum (shared migration risk, integration testing across chunks, sequencing penalties).

**Don't over-decompose.** Chunks below ~2h aren't worth splitting — bundle them. The break-down is for taming bigness, not for theatrics.

### Step 4: Surface unknowns

For every estimate (whole task or per chunk), name unknowns explicitly. Examples that matter:

- **Scope unknowns** — "is this behind a flag?", "does it need backfill?", "is X out of scope?"
- **Code unknowns** — "the existing serializer mixes two concerns; untangling could go either way"
- **Test unknowns** — "no integration tests exist for this flow yet — first-time setup adds time"
- **Stakeholder unknowns** — "design hasn't signed off on the empty state"
- **Data unknowns** — "we don't know how many records hit this path in prod"
- **Dependency unknowns** — "blocked on the X migration that another team owns"

If an unknown is **load-bearing** (would shift the estimate by > 50%), use AskUserQuestion to ask the user about it before finalizing. One question at a time. If they answer, fold it in. If they say "not sure," surface it as an unknown and widen the upper bound.

---

## Output formats

**All estimates are formatted as tables.** Tables make the structure scannable and force concision per cell. Use prose only when a value can't be summarized in one cell.

### Format A — Single estimate (no break-down)

Lead with a header table, then an unknowns table. Optional risks table only if there are real risks.

```
| Field          | Value                                              |
|----------------|----------------------------------------------------|
| Task           | [1–2 sentence restatement]                         |
| Estimate       | [range, e.g. "2–4h" or "0.5–1d"]                   |
| Confidence     | [High / Medium / Low]                              |
| Why this size  | [one-line justification]                           |
| Touch points   | [files / packs, comma-separated]                   |
| AI-enhanced?   | [Yes — typing-heavy / Partial / No — judgment-heavy] |

| Unknown | Impact |
|---------|--------|
| ...     | shifts estimate by [amount/direction] |

| Risk | Why it matters |
|------|----------------|
| ...  | ... |
```

### Format B — Break-down

Lead with a header table, then a per-chunk table, then unknowns/sequencing/risks tables.

```
| Field          | Value                                  |
|----------------|----------------------------------------|
| Task           | [1–2 sentence restatement]             |
| Total estimate | [summed range]                         |
| Confidence     | [High / Medium / Low]                  |
| AI-enhanced?   | [Yes / Partial / No, with one-line why] |

| # | Chunk | Range | Done when | Touch points | Key unknowns |
|---|-------|-------|-----------|--------------|--------------|
| 1 | ...   | 2–4h  | ...       | ...          | ...          |
| 2 | ...   | ...   | ...       | ...          | ...          |

| Cross-cutting unknown | Impact on total |
|-----------------------|-----------------|
| ...                   | ...             |

| Sequencing | What blocks what |
|------------|------------------|
| ...        | ...              |

| Risk | Why it matters |
|------|----------------|
| ...  | ...            |
```

If a chunk row gets too dense for one line per cell, use line breaks within the cell (`<br>`) — but keep cells under ~3 lines. If you need more, the chunk is probably its own break-down.

### Format C — Not ready to estimate

When break-down hits the 3-level cap or scope is too unbounded:

```
| Field   | Value                       |
|---------|-----------------------------|
| Task    | [restatement]               |
| Verdict | Not ready to estimate.      |

| Why not ready | Detail |
|---------------|--------|
| ...           | ...    |

| What would unblock | Detail |
|--------------------|--------|
| ...                | ...    |
```

---

## Key rules

1. **Always explore the code before estimating.** No estimate from text alone.
2. **Always give a range.** No point estimates.
3. **Always assume AI-enhanced collaboration** unless the user says otherwise. Adjust the estimate down for typing-heavy work; do not for decision/review-heavy work.
4. **Always format as a table.** Tables are the default; prose only fills cells that can't be condensed.
5. **Break down when the estimate is too big or too wide** (upper > 2d, or upper/lower > 3, or >3 load-bearing unknowns, or spans multiple surfaces).
6. **Recurse the break-down up to 3 levels.** Beyond that, output Format C — the task isn't ready to estimate.
7. **Surface unknowns explicitly.** Don't pad the estimate to absorb them.
8. **Ask via AskUserQuestion when an unknown is load-bearing** (would shift estimate > 50%). One at a time.
9. **No code edits.** This is an analysis skill. Produce the estimate; don't write the code, don't propose patches.
10. **Independently shippable chunks.** When breaking down, each chunk should be a real PR you could merge alone.
11. **Don't over-decompose.** Chunks below ~1h get bundled, not split further.
