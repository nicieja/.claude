# Heal guide

The reference `self-heal` loads every run. It defines what accretion debt is, the symptoms to look for, the healthy shape each artifact type should converge to, the method for rewriting without regressing behavior, and worked before/after examples. Tune it over time — it's the spec.

## What accretion debt is

Prompt files are built iteratively. When something needs adjusting, the cheapest edit is to staple the new instruction into a convenient spot — an extra bullet, another Key Rule, a parenthetical. Each addition is locally sensible. Across many sessions the file stops reading like one authored prompt and becomes a **changelog**: the same point made in three places, seams where text was bolted on, near-duplicate rules, cross-references that exist only because content landed somewhere else, sections that drift in tone because different sittings wrote them.

This is **not slop.** Slop is empty — form without substance. An accreted file is usually the opposite: every line is load-bearing, the content was just badly *arranged* and never re-integrated. So the fix is not to cut emptiness (that's `/deslop`); it is to **re-integrate** — say everything the file already says, once, in its right place, in one voice — while losing none of it. The danger here is the inverse of slop's: not keeping fluff, but **dropping a hard-won rule** while tidying. Shed the seam, keep the lesson.

## Symptom taxonomy

The tells to detect and score:

- **Redundancy** — the same instruction stated in multiple places (intro *and* a step *and* a Key Rule). Cheap to add, expensive to maintain, and the copies drift out of sync.
- **Bolt-on seams** — text that reads as a later staple: trailing parentheticals, `Note:` / `Also:` / `Importantly:` / ALL-CAPS reemphasis, an extra bullet or Key Rule tacked onto the end.
- **Near-duplicate rules** — two Key Rules or two steps covering almost the same ground under different framing.
- **Length bloat** — a section or step list grown well past what its job needs; deep nesting that could be one tight paragraph.
- **Patching cross-references** — `as mentioned above`, `per Step 2`, `see guardrail #7`, `like Step 5`. A pointer that exists because content was added elsewhere instead of integrated where it's needed.
- **Tonal / voice seams** — one section terse and confident, the next dense and didactic: the fingerprint of different editing sessions never smoothed together.
- **Publishability leaks** — employer, product, customer, teammate, or industry-domain vocabulary in a tracked file. This library is public; examples must use neutral SaaS vocabulary. Tool names (Linear, Rails, Sentry) are fine; domain nouns that identify the employer's industry are not.

A file's **debt score** is a judgment across these — how much a fresh reader pays for the history. One stray parenthetical is noise; a file with redundancy *and* duplicate rules *and* tonal drift is a re-integration candidate.

## The three healthy shapes

Heal each file toward the shape its **type** has converged to across the library. Never impose one type's template on another.

**Skill (`skills/*/SKILL.md`)**
```
frontmatter: name, version, description: |, allowed-tools (dash list)
# Title + 1–3 sentence intro (what it does, when)
## Arguments                    — invocation forms + plain-word steers
## When this is the wrong skill  — trigger → alternative skill
## Instructions                 — "follow in order", ### Step 0…N
## Key Rules                    — numbered non-negotiables, one each
(optional) a companion .md loaded every run for the evolving spec
```

**Command (`commands/*.md`)**
```
frontmatter: description (required), allowed-tools?, argument-hint?
## Context     — ambient state, often embedded ! bash
## Your task   — the instruction; optional ### Step N
```
Lean and ephemeral; it speaks *to* Claude for one bounded run. No persona, no versioning, no Key Rules ceremony unless the task is genuinely complex.

**Agent (`agents/*.md`)**
```
frontmatter: name, description, tools, model
persona framing       — "## What you believe" / role & philosophy
operational sections  — how it thinks, what it checks, areas of focus
## How to deliver …   — the output shape it must produce
closing line          — its verdict / sign-off pattern
```
A system prompt written *as* the persona, dispatched as a subagent. Rich voice is correct here; don't strip it toward a skill's terse step list.

## The coverage ledger

The method that makes a from-scratch rewrite safe.

Before rewriting, list every **behavioral commitment** the original makes — anything that would change what the file *does* if it vanished:

- every rule and guardrail (each Key Rule counts),
- every instruction step and its ordering constraints,
- every scope / "wrong skill" boundary,
- every argument, flag, and steer,
- every named edge case and safety constraint,
- every entry in `allowed-tools` / `tools`, and the frontmatter fields.

That list is the contract. The rewrite preserves each item's **effect** — not its words, not its position. Rephrasing and relocating is the entire job; **dropping is not on the table.** After rewriting, walk the ledger item by item against the new draft. A commitment with no home in the rewrite is a regression — restore it. A commitment that looks genuinely obsolete or self-contradictory is **not yours to delete**: flag it to the user as a question, separate from the edit.

### A worked ledger (miniature)

Original, accreted — a fictional skill fragment:
```
Intro:      "...always work on a copy, never the original."
Step 3:     "Operate on a copy of the file."
Key Rule 2: "Never touch the user's original file."
Key Rule 5: "Work on a copy."
```
Ledger (the commitment, stated once): **never modify the original; operate on a copy.**
Healed: said once in the step where it bites, and once as a Key Rule pointer — not four times.
Ledger check: the commitment survives. ✅ Four mentions → two, zero behavior lost.

## Whole-file vs surgical

- **Whole-file re-integration** when debt is pervasive: seams throughout, rules repeated across sections, tone drifting. Rebuild the file from the ledger toward its type shape.
- **Surgical** when debt is localized to a section or two and the rest is clean: rewrite only those. But watch for a **new seam** — a freshly tightened section against an older, looser one can read worse than the original patchwork. If that happens, widen the rewrite.

## Estimating the heal

You may predict the consolidation up front — "this looks ~40% shorter, mostly the Instructions" — but treat it exactly as `/deslop` treats its cut estimate: a **prediction, not a target.** The moment you cut to hit a number you start dropping content, and here that means dropping a ledger commitment — the one thing the skill exists to prevent. Range over point; judgment wins every tie; report the actual change against the estimate as a finding, not a miss.

## Examples

Generic by design — illustrative, not pinned to any current library file, so this guide doesn't rot when those files are healed.

**1. Redundant rule folded once**
> ❌ Intro: "Default to no comments." · Step 4: "Add a comment only when it earns its place." · Key Rule 5: "Comments: default none." — same rule, three homes.
> ✅ One statement in Step 4, where the work happens, plus a one-line Key Rule pointer. Said once, where it bites.

**2. Bolt-on parenthetical dissolved**
> ❌ "Run the migration. (Note: importantly, always back up first — see Step 2.)"
> ✅ "Back up, then run the migration." The caveat moves into the sentence it governs; the back-reference disappears.

**3. Two near-duplicate rules merged**
> ❌ "3. Never edit the source file." / "7. Always write output to a new path, not the original."
> ✅ "3. Never overwrite the source — write output to a new path." One rule, both effects preserved.

**4. Patching cross-reference integrated**
> ❌ "Hide the machinery (like Step 5, the scaffolding doesn't appear in the output)."
> ✅ State the rule once, where it first applies; drop "like Step 5." If it genuinely governs two places, say it in the earlier one and let the later inherit — don't cross-stitch.

**5. Tonal seam evened out**
> ❌ A crisp, confident intro followed by a dense, didactic section bristling with nested sub-bullets — two authors on one page.
> ✅ One register throughout: the section keeps its detail but adopts the intro's voice. Same information, one speaker.
