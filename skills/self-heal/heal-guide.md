# Heal guide

The reference `self-heal` loads every run. It defines what accretion debt is and the symptoms to look for. It gives the healthy-shape template that each artifact type converges to, the method for rewriting without regressing behavior, and worked before/after examples. Tune it over time, because it's the spec.

## What accretion debt is

Prompt files are built iteratively. When something needs adjusting, the cheapest edit is to staple the new instruction into a convenient spot (an extra bullet, another Key Rule, a parenthetical). Each addition is locally sensible. Across many sessions the file stops reading like one authored prompt and becomes a **changelog**. The same point is made in three places, text is bolted on with visible seams, rules are near-duplicates, cross-references exist only because content was added somewhere else, and sections drift in tone because different sittings wrote them.

This is **not slop.** Slop is empty, form without substance. An accreted file is usually the opposite: every line has a purpose, and the content was just badly *arranged* and never re-integrated. So the fix is different from cutting emptiness (that's `/deslop`). The fix is to **re-integrate**, which means to say everything the file already says, once, in its right place, in one voice, while losing none of it. The danger here is the inverse of slop's: instead of keeping fluff, you might **drop a hard-won rule** while tidying. Remove the patchwork and keep the lesson.

## Symptom taxonomy

The tells to detect and score:

- **Redundancy**: the same instruction stated in multiple places (intro and a step and a Key Rule). Cheap to add, expensive to maintain, and the copies drift out of sync.
- **Bolt-on seams**: text that reads as a later staple, such as trailing parentheticals, `Note:` / `Also:` / `Importantly:` / ALL-CAPS reemphasis, or an extra bullet or Key Rule tacked onto the end.
- **Near-duplicate rules**: two Key Rules or two steps covering almost the same ground under different framing.
- **Length bloat**: a section or step list grown well past what its job needs, or deep nesting that could be one tight paragraph.
- **Patching cross-references**: `as mentioned above`, `per Step 2`, `see guardrail #7`, `like Step 5`. A pointer that exists because content was added elsewhere instead of integrated where it's needed.
- **Tonal / voice seams**: one section terse and confident, the next dense and didactic. This is the fingerprint of different editing sessions never smoothed together.
- **Publishability leaks**: employer, product, customer, teammate, or industry-domain vocabulary in a tracked file. This library is public, so examples must use neutral SaaS vocabulary. Tool names (Linear, Rails, Sentry) are fine, but domain nouns that identify the employer's industry are not.

A file's **debt score** is a judgment across these: how much a fresh reader pays for the history. One stray parenthetical is noise. A file with redundancy and duplicate rules and tonal drift is a re-integration candidate.

## Healthy-shape templates

Heal each file toward the template its **type** has converged to across the library. Never impose one type's template on another.

**Skill (`skills/*/SKILL.md`)**
```
frontmatter: name, version, description: |, allowed-tools (dash list)
# Title + 1–3 sentence intro (what it does, when)
## Arguments                    — invocation forms + plain-word steers
## Cases for another skill  — trigger → alternative skill
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
Lean and ephemeral, it speaks *to* Claude for one bounded run. It skips persona and versioning, and skips Key Rules ceremony unless the task is complex.

**Agent (`agents/*.md`)**
```
frontmatter: name, description, tools, model
persona framing       — "## What you believe" / role & philosophy
operational sections  — how it thinks, what it checks, areas of focus
## How to deliver …   — the output shape it must produce
closing line          — its verdict / sign-off pattern
```
A system prompt written *as* the persona, dispatched as a subagent. Rich voice is correct here, so don't strip it toward a skill's terse step list.

## The coverage ledger

The method that makes a from-scratch rewrite safe.

Before rewriting, list every **behavioral commitment** the original makes, meaning anything that would change what the file *does* if it vanished:

- every rule and guardrail (each Key Rule counts),
- every instruction step and its ordering constraints,
- every scope / "wrong skill" boundary,
- every argument, flag, and steer,
- every edge case and safety constraint the file states,
- every entry in `allowed-tools` / `tools`, and the frontmatter fields.

That list is the contract. The rewrite preserves each item's **effect**, and it is free to change the words and the position. Rephrasing and relocating is the entire job, and **dropping is not on the table.** After rewriting, walk the ledger item by item against the new draft. A commitment with no home in the rewrite is a regression, so restore it. A commitment that looks obsolete or self-contradictory is **not yours to delete**: flag it to the user as a question, separate from the edit.

### A worked ledger (miniature)

Original, accreted, from a fictional skill fragment:
```
Intro:      "...always work on a copy, never the original."
Step 3:     "Operate on a copy of the file."
Key Rule 2: "Never touch the user's original file."
Key Rule 5: "Work on a copy."
```
Ledger (the commitment, stated once): **never modify the original, and operate on a copy.**
Healed: said once in the step where it applies and once as a Key Rule pointer, not four times.
Ledger check: the commitment is preserved. ✅ Four mentions → two, zero behavior lost.

## Whole-file vs surgical

- **Whole-file re-integration** when debt is pervasive, with seams throughout, rules repeated across sections, and tone drifting. Rebuild the file from the ledger toward its type's template.
- **Surgical** when debt is localized to a section or two and the rest is clean: rewrite only those. But watch for **new seams**: a freshly tightened section against an older, looser one can read worse than the original patchwork. If that happens, widen the rewrite.

## Estimating the heal

You may predict the consolidation up front. An example is "this looks ~40% shorter, mostly the Instructions". Treat it exactly as `/deslop` treats its cut estimate: a **prediction and never a target.** The moment you cut to hit a number, you start dropping content. Here that means dropping a ledger commitment, which is the one thing the skill exists to prevent. Prefer a range over a point estimate. Judgment decides every tie. Report the actual change against the estimate as a finding and never as a miss.

## Examples

These are generic by design. They are illustrative and not pinned to any current library file, so this guide doesn't rot when those files are healed.

<!-- vale off -->
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
> ✅ State the rule once, where it first applies; drop "like Step 5." If it governs two places, say it in the earlier one and let the later inherit — don't cross-stitch.

**5. Tonal seam evened out**
> ❌ A crisp, confident intro followed by a dense, didactic section bristling with nested sub-bullets — two authors on one page.
> ✅ One register throughout: the section keeps its detail but adopts the intro's voice. Same information, one speaker.
<!-- vale on -->
