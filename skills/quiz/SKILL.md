---
name: quiz
version: 1.0.0
description: |
  Quiz the human on the crucial decisions, tradeoffs, and pain points behind a
  PR, doc, or other artifact built with AI in this session — so they can stand
  behind every idea in it before review. 5-7 high-signal multiple-choice items,
  two-stage what-then-why on the highest-stakes calls, teach-then-re-verify on
  gaps, and an honest criticality-gated readiness verdict. Never minutiae,
  never overwhelming. Loads quiz-guide.md every run.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Quiz

The guiding principle: **you must stand behind every idea in your PRs and docs.** When AI did much of the work, the person shipping it can hold an artifact whose crucial calls they cannot defend — and self-report is no gate, because feeling ready and being ready diverge hardest exactly when the AI did the reasoning. This skill checks the gap the cheap way: a short quiz on the decisions that matter, asked before a reviewer asks them, by a colleague rather than an examiner. A wrong answer here is a feature — it is the one place getting it wrong costs nothing and teaches the mechanism.

The quiz is never a trivia sweep. Five to seven questions, one per crucial decision, each one a question a skeptical reviewer would actually ask. Everything else about the machinery — how decisions are ranked, how questions are screened, how answers are graded — lives in the guide and stays invisible to the user.

## Arguments

- `/quiz` — quiz on the work done in this session, mined from the conversation and cross-checked against the actual diff or doc. If nothing is obviously in flight, ask once — *"What should I quiz you on?"* — and wait.
- `/quiz <PR number | url | branch>` — quiz on that PR: fetch with `gh pr view` / `gh pr diff`, reconstruct the decision points from the artifact and commit messages (artifact-only mode).
- `/quiz <file path>` — quiz on a doc or file; its decisions are its claims, recommendations, structure, and deliberate omissions.
- Steers in plain words: `--short` / "just the big ones" — top 2–3 decisions only.

## When this is the wrong skill

- They want a *claim or proposal* grilled with evidence-forcing questions → `/pushback`. Pushback interrogates an idea before it's built; quiz verifies the human owns a finished artifact.
- Post-ship reflection — waste, lessons, debt → `/retro`.
- Harvesting session corrections into harness improvements → `/learn`.
- Reviewing *someone else's* PR → `/review-pr`. Quiz is for work the user is about to put their own name on.

## Instructions

Follow in order.

### Step 0: Resolve the source

Resolve per **Arguments**.

- **Bare:** session mode. Identify the artifact under construction — the branch diff, the doc being drafted. If the session's work is trivially mechanical (a lockfile bump, a rename, a one-liner with one sane implementation), note it now; Step 3 may exit cheap.
- **PR reference:** artifact-only mode. `gh pr view <ref> --json title,body,commits` for rationale hints, `gh pr diff <ref>` for the substance. `gh` is read-only here — no posting, no pushing.
- **File path:** Read it; doc mode.

In artifact-only mode there is no conversation to mine — every rationale is **inferred**. Mark it: WHY distractors must come from alternatives you derive (Step 4), and the verdict carries one honesty line (Step 7).

### Step 1: Load the guide

Read `~/.claude/skills/quiz/quiz-guide.md` in full **before mining**. It holds the decision definition, the priority scoring, the stem families, the distractor and flaw rubrics, the grading ladder, and the verdict language. Load it every run — it's the thing tuned over time; don't work from memory.

### Step 2: Mine the decisions

Two passes, then a cross-check.

**Conversation pass** (session mode): scan the session for choice points — "we could A or B", "instead", "actually, let's", approaches tried and reverted, corrections from the user, errors hit and the fix chosen, constraints discovered mid-flight, tradeoffs explicitly accepted, deferrals with reasons.

**Artifact pass:** run `git diff <base>...HEAD` (or `gh pr diff`, or Read the doc) and reconcile:

- Drop mined decisions that didn't survive into the artifact — they're history, not the thing being shipped.
- **Add** decisions visible in the artifact but never discussed. These are prime candidates: the AI chose silently, so the human has had zero chances to rehearse the rationale.

**Artifact-only fallback** (argument passed): reconstruct decision points from the artifact alone — every place it chooses among plausible alternatives: a boundary, a data shape, an error path, a sequencing, a limit given a value — with commit messages and the PR body as rationale hints.

For each candidate record: the decision, the rejected alternative(s), the rationale (stated or inferred), the anchor (file:line or doc section), and a criticality sketch.

### Step 3: Select and rank

Score each candidate with the guide's priority formula — irreversibility × blast radius × novelty to author × opacity of rationale — and strike everything on the guide's negative list. Those never appear, regardless of score.

- Cap at **5–7 items, one per decision** — never two questions on the same decision (Step 6's re-verify is the sole exception, and it must come from a different angle). With `--short`, cap at 2–3.
- More than seven survivors: sort by score, break ties toward irreversibility, then blast radius. Each cut decision gets one line in the Step 7 verdict — *"not quizzed, worth a skim: …"*.
- **Nothing survives** the negative list and the depth screen: say so in two lines — *"Nothing here needs defending — the work is mechanical, single-path"* — and stop. No quiz, no ratings, no verdict theater.

Mark the top one or two decisions by score as **two-stage** items.

### Step 4: Draft the items, then self-critique

Draft each item per the guide: pick the stem family (rejected alternative, conditional reversal, failure prediction, relational purpose — biased toward failure and mechanism), write the stem, then three options where every distractor is a genuinely rejected alternative, a real misconception, or a true-but-not-decisive fact. In artifact-only mode, distractors come from the plausible alternatives you derived, since no session-rejected ones exist.

Apply the guide's depth screen to every stem — *could someone who read the diff attentively but did no reasoning answer this?* — and discard what fails; redraft, don't soften.

For two-stage items, draft both stages: WHAT (the call or prediction) and WHY (three rationales, distractors plausible-but-wrong per the guide).

Then the **mandatory self-critique pass**: run every item through the guide's flaw checklist before anything reaches the user — cover-the-options, multiple defensible answers, throwaway distractors, longest-option-correct, grammar cues, except/not stems. The first two are the known failure modes of machine-written items; check them hardest. Fix or redraft; never deliver an unscreened item.

Finally, set each item's key position so the correct answer's slot varies across the quiz, and equalize option lengths.

### Step 5: Pre-quiz self-rating

One AskUserQuestion — header `Ready?`:

> "Before we start: how well could you defend this work to a skeptical reviewer, today?"

Options: `5 — bulletproof` / `4 — solid` / `3 — big calls yes, edges no` / `2 or less — shaky`. Record the answer and move on without comment — no reassurance, no foreshadowing. This rating is the confidence prior the verdict reads against; there are **no per-item confidence questions**.

### Step 6: Deliver the quiz

One AskUserQuestion per question — never batch. Header `Q <i>/<K>`. Three options plus the built-in "Other". **No "(Recommended)" labels, ever** — a quiz with a giveaway measures nothing — and the key's position varies item to item.

After **every** answer, respond in chat before the next tool call:

- **Correct:** one or two lines — confirm, plus the condition under which the answer would flip. No praise, no tally.
- **Wrong:** teach immediately with the guide's four-beat template — the actual call, the mechanism, the pointer into the diff or doc, the feed-forward. Then queue a re-verify.
- **"Other" (free text):** authoritative. Grade it on the guide's ladder. Owned beats the key even when it disagrees with it; an answer better than the key gets full credit said out loud. A surface answer (mechanics without purpose) gets exactly **one** probe deeper — asked as plain conversation, not another item — then resolve. Never a second probe.

**Two-stage flow** (top items): stage one asks WHAT. Correct → follow with the WHY stage, header `Why?`. A wrong WHY is the item-level confident-and-wrong signal — teach it and queue a re-verify. Wrong WHAT → teach immediately and **skip the WHY**; the teach just gave it away.

**Re-verify:** each taught gap queues one differently-angled question on the same decision — different stem family, per the guide — appended after the last planned item with header `Recheck 1` (max `Recheck 2`; further gaps become verdict notes). Passing upgrades the gap to recovered; failing keeps it a gap.

**Escape hatch** — if the user wants out ("just give me the verdict", "skip it"):

- **First time:** "The questions are the value — defending it to me is cheaper than fumbling it in review. One more: the one you'd most regret being asked there." Deliver only the highest-criticality remaining item (or two).
- **Second time:** respect it. Wrap with what you have; the verdict states plainly it is partial — *"only N of K decisions checked — no readiness claim on the rest."*
- **Full skip** only when the user already demonstrated ownership unprompted — they authored the key rationale in-session themselves. Even then, print the verdict-shaped summary of what would have been asked.

### Step 7: Post-rating and verdict

Re-ask the Step 5 question verbatim — header `Ready now?`, same options. Then print the verdict in a fenced markdown block:

1. **The delta**, first and plainly: pre-rating → post-rating. Self-generated evidence beats anything the skill could assert.
2. **The confidence read**, derived per the guide: high pre-rating crossed with a high-criticality gap = confident-and-wrong, flagged first — that is the dangerous cell. Low pre-rating crossed with a clean run = underclaim, named as such.
3. **The verdict, gated on criticality — never a percentage:** *Ready to defend* / *Ready, with notes* / *Not yet*. An unrecovered gap on a one-way-door or high-blast decision blocks *Ready* even at six of seven correct. Every gap and note carries its feed-forward: what to re-read (with the pointer) and what to raise with a reviewer.
4. **Uncovered decisions** — Step 3 overflow and escape-hatch skips, one line each.
5. **The honest claim**, verbatim shape: *"N gaps found on the hardest-to-reverse decisions"* — never "you understand this PR." Plus the standing caveat: this checked whether you can defend the decisions, not whether the code works — tests and review still do their jobs. Artifact-only mode adds its reconstruction line.

## Key Rules

1. **Load `quiz-guide.md` every run.** The rubrics live there, not in memory.
2. **5–7 items, one per decision.** A re-verify after a taught gap is the only exception, always from a different angle.
3. **Nothing from the negative list, nothing below the depth screen.** An item an attentive non-reasoner could answer gets discarded, not softened.
4. **Self-critique every item before delivery.** Multiple defensible answers and throwaway distractors are the known machine failure modes; screen for them explicitly.
5. **One AskUserQuestion per question, no "(Recommended)" labels, key position varies.** A quiz with giveaways measures nothing.
6. **"Other" is authoritative.** Grade it on the guide's ladder; a better-than-key answer wins and is said out loud.
7. **Feedback is immediate, aimed at the work, and ends in a next action.** Point into the diff or doc; never praise or shame the person. A failed question is a feature.
8. **One probe per surface answer, then resolve.** A second probe is interrogation.
9. **The verdict gates on criticality, never a percentage.** Claim only "N gaps on the hardest-to-reverse decisions" — never "you understand this."
10. **Colleague, not examiner.** No running tally, no red pen, and none of the guide's machinery vocabulary shown to the user.
11. **Read-only.** No file written, nothing posted; the verdict block in conversation is the artifact.
