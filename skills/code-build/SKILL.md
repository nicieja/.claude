---
name: code-build
version: 1.0.0
description: |
  Build a slice of code from a plan, a spec, or a request, in the style of the
  codebase that receives it. Frames the smallest slice and reads the local
  conventions before writing. Treats an upstream plan as a starting point,
  with a fixed ladder for changes to it. Verifies with the project's own tools
  and ends with a handoff that someone else could release or revert.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - Skill
---

# Build

Build the slice so that it reads as if one careful engineer wrote both the feature and its neighbors, and not as if a new style was dropped into the middle of an existing codebase. Most production code is too clever and too layered, and it depends too much on accidental complexity. Push the slice in the opposite direction without imposing a taste on a codebase that already has its own.

## Arguments

- `/code-build <plan path>`: build the plan in that file.
- `/code-build <request>`: build what the request describes.
- `/code-build` (bare): build the plan or request under discussion. If there is none, ask once: "What should I build?"

## Cases for another skill

- The idea is half-formed and needs a plan first → `/idea-spec`.
- The code works and needs a cleanup pass → `/simplify`, or `/code-refactor` for a restructure across many files.
- The diff needs a review before merge → `/pr-critique`.
- Defensive code to cut → `/code-unguard`.
- The tests for the change need design → `/test-design`.

## Taste

Taste is only a tiebreaker (see Step 1), and it runs in this direction:

- **Less software.** Fewer dependencies, fewer abstractions, fewer files. Every line is a liability that pays back only when it does necessary work.
- **Names express intent.** The public API should read like the verb a caller would actually use, on the noun where the state is stored: `order.cancel()` and not `OrderCancellationService.execute(order)`. Reserve technical suffixes (`Manager`, `Handler`, `Service`, `Helper`) for nouns that do what the suffix promises.
- **A new layer or helper needs a concrete second caller.** Without one, skip it. Inline first and extract second: three similar lines are better than a premature abstraction. Extract when the inline code hides a verb that deserves a name, or when the duplication is real and has stabilized.
- **Grow the domain object, not a service layer.** When a domain object gets complicated, move its internals into cohesive supporting objects, and keep generic services out of it.
- **Fixed time, variable scope.** When the budget is tight, cut scope before you extend time. Decide which way before you start, not after.
- **Done means running in production, not merged.** A change isn't finished until it's verified end-to-end and small enough to roll back cleanly.

Guards follow the rule in CLAUDE.md ("Don't defend against what can't happen") and `/code-unguard`. Comments follow `/code-deslop` Key Rule 5. By default there is no comment. Write one only to explain a why, a gotcha, an invariant, an external constraint, or a workaround. Step 5 checks both rules.

## Instructions

### Step 0: Frame the slice

State the smallest version that delivers the outcome, the files you expect to touch, and the ones you've decided not to touch.

When the ask is ambiguous, pick the narrowest reading that still delivers the outcome, state the assumption in writing, and proceed reversibly. Escalate only when the ambiguity blocks correctness, security, or user trust.

### Step 1: Read before writing

Read enough of the surrounding code that the conventions in play are clear, and write them down. Those conventions include naming style and the domain's names for its concepts, method structure, where business logic is defined, how errors are handled, how tests are organized, and what the dependency footprint looks like.

**The codebase's conventions apply by default.** Match them even when you'd have written it differently from scratch. Use the name the codebase already has for a concept, and never add a second name for it. A consistent codebase in a style you mildly dislike is more valuable than one split between two tastes.

**Push back only on active harm.** Override the local pattern only when it causes bugs or blocks the change being made, when it leaks correctness or security, or when it has compounded into the thing you were brought in to fix. Aesthetic disagreement is not a qualifying reason, and different is not worse.

When you do push back, state the harm specifically. Give the file, the failure mode, and the concrete cost. Not "this pattern is dated" or "this would read better." Instead: "this class has accumulated fourteen methods that mutate state directly from three callers, so the bug we're debugging is hard to trace." Then propose the smallest change that removes the harm without rewriting things you weren't asked to rewrite.

### Step 2: Check the upstream plan

Skip this step when there is no plan. Plans, specs, design notes, and recommendations are a starting point. They are not a binding contract, but don't smuggle deviations either. Anything you change from the plan gets stated clearly in the handoff.

- **Cosmetic divergence: fix inline and flag it.** This covers names, file layout, and helper extraction. If a spec calls for `OrderCancellationService.execute(order)` and a verb on the noun reads better in this codebase, use the better name and flag the swap. Whoever wrote the plan was most likely not married to the exact API signature.
- **Structural divergence: raise it before building.** This covers new layers, extra abstractions, and changes to where logic is defined. Write up what the plan proposes, what you'd do instead, and the concrete cost of each, then ask before deviating. Don't drop a layer that was specifically requested.
- **Behavioral divergence: never deviate without explicit confirmation.** If building the plan as written would change what the system does, stop and ask.

### Step 3: Build the vertical slice

Build it end-to-end, in the style of the surrounding code, with intent-carrying names. Don't add a speculative abstraction or an unrequested guard.

### Step 4: Verify

Run the targeted tests, the type checker, the linter, and any security tooling already configured in the project. If nothing exercises the change, write a focused test that does.

### Step 5: Self-review

Read your own diff as a sharp reviewer would. Cut anything you wouldn't defend. Check each guard the diff adds against the armor rule, and each comment it adds against the comment rule above.

### Step 6: Hand off

Write a concise summary with these sections:

- **What changed**: the files touched and a high-level outline of the change.
- **Design rationale**: the local patterns you matched and any deliberate taste decisions. Also list each divergence from the upstream plan, with the swap stated.
- **What you ran**: tests, type checker, linter, security tooling, and their outcomes.
- **Residual risk**: what you didn't cover and why. List each open decision about failure behavior (retry, degrade, alert, drop) with its options, because that call belongs to the user.
- **Rollback**: how to undo the change cleanly.

## Key Rules

1. **The codebase's conventions apply by default.** Taste only breaks ties.
2. **Push back only on active harm,** with the file, the failure mode, and the concrete cost.
3. **Take the smallest plausible interpretation,** and state the assumption in writing.
4. **Follow the divergence ladder.** Fix and flag a cosmetic change. Ask before a structural change. Never make a behavioral change without confirmation.
5. **No speculative abstractions and no unrequested guards.**
6. **Exit criteria.** The slice is shippable. The change is small and respects the surrounding conventions, and intent-carrying names replace generic ones. Verification ran with evidence, and the handoff is concrete enough that someone else could release or revert it.
