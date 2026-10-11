---
name: code-build
version: 1.3.0
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
  - Agent
---

# Build

Build the slice so that it reads as if one careful engineer wrote both the feature and its neighbors, and not as if a new style was dropped into the middle of an existing codebase. Most production code is too clever and too layered, and it depends too much on accidental complexity. Push the slice in the opposite direction without imposing a taste on a codebase that already has its own.

## Arguments

- `/code-build <plan path>`: build the plan in that file.
- `/code-build <request>`: build what the request describes.
- `/code-build` (bare): build the plan or request under discussion. If there is none, ask once: "What should I build?"
- Steers in plain words: `--review` / "ask first" stops after Step 2 and waits for the go-ahead before building.

## Cases for another skill

- The idea is half-formed and needs a plan first → `/idea-spec`.
- The change needs a cleanup pass → `/code-simplify`, or `/code-refactor` for a restructure across many files.
- The diff needs a review before merge → `/pr-critique`.
- Defensive code, or an addition with no caller, to cut → `/code-simplify`.
- The tests for the change need design → `/test-design`.

## Taste

Taste is only a tiebreaker (see Step 1), and it runs in this direction:

- **Less software.** Fewer dependencies, fewer abstractions, fewer files. Every line is a liability that pays back only when it does necessary work.
- **Names express intent.** The public API should read like the verb a caller would actually use, on the noun where the state is stored: `order.cancel()` and not `OrderCancellationService.execute(order)`. Reserve technical suffixes (`Manager`, `Handler`, `Service`, `Helper`) for nouns that do what the suffix promises.
- **A new layer or helper needs a concrete second caller.** Without one, skip it. Inline first and extract second: three similar lines are better than a premature abstraction. Extract when the inline code hides a verb that deserves a name, or when the duplication is real and has stabilized.
- **Grow the domain object, not a service layer.** When a domain object gets complicated, move its internals into cohesive supporting objects, and keep generic services out of it.
- **A write is safe to repeat when something repeats it.** When something can run a write twice, ask what the second run does and what a run that crashed halfway leaves behind. Retried jobs and redelivered webhooks can, and so can a client that sends an idempotency key. When nothing repeats the write, don't add a key or a lock. A port keeps exactly the repeat protection its old path had.
- **Fixed time, variable scope.** When the budget is tight, cut scope before you extend time. Decide which way before you start, not after.
- **Done means running in production, not merged.** A change isn't finished until it's verified end-to-end and small enough to roll back cleanly.

Guards follow the rule in `~/.claude/AGENTS.md` ("Don't defend against what can't happen") and `/code-simplify`. Comments follow the keep list in `~/.claude/skills/code-uncomment/comment-guide.md`. By default there is no comment, and a surprise in our own code gets a clearer name or shape instead of a comment. Step 5 checks both rules.

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

An open question in the plan that running something would answer goes to `/idea-prototype` first, before the ladder below. Build from what the prototype showed.

- **Cosmetic divergence: fix inline and flag it.** This covers names, file layout, and helper extraction. If a spec calls for `OrderCancellationService.execute(order)` and a verb on the noun reads better in this codebase, use the better name and flag the swap. Whoever wrote the plan was most likely not married to the exact API signature.
- **Structural divergence: build the plan, and record the alternative.** This covers new layers, extra abstractions, and changes to where logic is defined. Build what the plan says. In the handoff, write what you'd do instead and the concrete cost of each, so the plan's author can decide. Don't drop a layer that was specifically requested.
- **Behavioral divergence: the call belongs to the user.** If building the plan as written would change what the system does in a way the request didn't ask for, leave that part unbuilt. Build the rest, then ask about it at the end, per "Decisions that are mine" in `~/.claude/AGENTS.md`.

### Step 3: Build the vertical slice

Build it end-to-end, in the style of the surrounding code, with intent-carrying names. Don't add a speculative abstraction or an unrequested guard.

**A bug fix starts with a repro.** Reproduce the bug on the layer where it shows, as `/test-prove` Step 5 describes, and commit the failing repro before the fix. When a test isn't practical, use the closest executable check, such as a script or a request against the running app, and say why. Test one hypothesis at a time, and revert the code written for a hypothesis the evidence refuted. Each line of the fix needs evidence behind it, so code that only might help stays out. Never weaken an assertion or edit a test to match the code. When two fixes that rest on the same assumption have both failed, stop fixing. Write the assumption down as one sentence, and test it before trying a third fix.

### Step 4: Verify

Run the targeted tests, the type checker, the linter, and any security tooling already configured in the project. If nothing exercises the change, write a focused test that does.

Then run the project's private checks: each executable in `~/.claude/context/<project>/checks/`, with the changed files as arguments. A failure says the fix, so apply it.

For a change a user would notice, passing tests don't prove the feature works, so prove it on the running app. Drive it with the repo's own verify skill, or with `~/.claude/context/<project>/verify/SKILL.md` when the repo has none, and treat an inconclusive drive as a fail. Whichever harness drives it, read the feature map in `~/.claude/context/<project>/verify/features/` when it exists. A proof through one entry point is incomplete when the map lists others.

### Step 5: Review

Read your own diff as a sharp reviewer would. Cut anything you wouldn't defend. Check each guard the diff adds against the armor rule, and each comment it adds against the keep list above. Check each name it adds against the naming rules in `~/.claude/skills/idea-primitive/design-guide.md`.

Then follow `~/.claude/skills/pr-critique/independent-review.md` on the slice's diff, with the plan or the request as its source. The lenses are `/pr-critique` and `/trace-requirement`. `/code-simplify` isn't one of them, because it runs after the build as its own stage.

### Step 6: Hand off

Write a concise summary with these sections:

- **What changed**: the files touched and a high-level outline of the change.
- **Design rationale**: the local patterns you matched and any deliberate taste decisions. Also list each divergence from the upstream plan, with the swap stated.
- **What you ran**: tests, type checker, linter, security tooling, and their outcomes.
- **Reviewed**: the independent review's part, as `~/.claude/skills/pr-critique/independent-review.md` sets it.
- **Residual risk**: what you didn't cover and why. List each open decision about failure behavior (retry, degrade, alert, drop) with its options, because that call belongs to the user.
- **Needs you**: the review's Ask findings and the open decisions, asked together.
- **Undo**: the exact command that undoes the change, such as `git restore <files>` or `git revert <sha>`.

To publish the branch as a PR, `/pr-open` comes next.

## Key Rules

1. **The codebase's conventions apply by default.** Taste only breaks ties.
2. **Push back only on active harm,** with the file, the failure mode, and the concrete cost.
3. **Take the smallest plausible interpretation,** and state the assumption in writing.
4. **Follow the divergence ladder.** Fix and flag a cosmetic change. Build a structural disagreement as planned, and record the alternative. Never make a behavioral change without confirmation, and ask about it at the end.
5. **No speculative abstractions and no unrequested guards.**
6. **Exit criteria.** The slice is shippable. The change is small and respects the surrounding conventions, and intent-carrying names replace generic ones. Verification ran with evidence, and the handoff is concrete enough that someone else could release or revert it.
