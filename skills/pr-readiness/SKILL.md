---
name: pr-readiness
version: 1.0.0
description: |
  Quiz the human on the key decisions, tradeoffs, and pain points behind a
  PR, doc, or other artifact built with AI in this session, so they can stand
  behind every idea in it before review. 5-7 high-signal multiple-choice items,
  two-stage what-then-why on the highest-stakes calls, teach-then-re-verify on
  gaps, and an honest criticality-gated readiness verdict. Never minutiae,
  never overwhelming.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# PR readiness
The guiding principle is that **you must be able to defend every idea in your PRs and docs.** When AI did much of the work, the person releasing it can hold an artifact whose key calls they cannot defend. Self-report is not a gate, because feeling ready and being ready diverge hardest exactly when the AI did the reasoning. This skill checks the gap cheaply, with a short quiz on the decisions that matter. The quiz is asked before a reviewer asks the same questions, and it is asked by a colleague rather than an examiner. A wrong answer here is a feature. This is the one place where a wrong answer does not cost anything and shows the mechanism.

The quiz is never a trivia sweep. It has between five and seven questions, one per key decision. Each one is a question a skeptical reviewer would actually ask. Everything else about the machinery (how decisions are ranked, how questions are screened, and how answers are graded) is in the guide and is never shown to the user.

## Arguments

- `/pr-readiness`: quiz on the work done in this session, mined from the conversation and cross-checked against the actual diff or doc. If nothing is obviously in flight, ask once, *"What should I quiz you on?"*, and wait.
- `/pr-readiness <PR number | url | branch>`: quiz on that PR. Fetch with `gh pr view` / `gh pr diff`, then reconstruct the decision points from the artifact and commit messages (artifact-only mode).
- `/pr-readiness <file path>`: quiz on a doc or file. Its decisions are its claims, recommendations, structure, and deliberate omissions.
- Steers in plain words: `--short` / "just the big ones" gives the top 2 to 3 decisions only.

## Cases for another skill

- They want a *claim or proposal* grilled with evidence-forcing questions → `/idea-challenge`. Pushback interrogates an idea before it's built. Quiz verifies that the human can defend a finished artifact.
- Post-release reflection (waste, lessons, debt) → `/work-retrospective`.
- Harvesting session corrections into harness improvements → `/self-improve`.
- Reviewing *someone else's* PR → `/pr-review`. Quiz is for work the user is about to put their own name on.

## Instructions

Follow in order.

### Step 0: Resolve the source

Resolve per **Arguments**.

- **Bare:** session mode. Identify the artifact under construction, such as the branch diff or the doc being drafted. If the session's work is trivially mechanical (a lockfile bump, a rename, a one-liner with one sane way to build it), note it now. Step 3 may exit cheap.
- **PR reference:** artifact-only mode. `gh pr view <ref> --json title,body,commits` for rationale hints, `gh pr diff <ref>` for the substance. `gh` is read-only here, without posting or pushing.
- **File path:** doc mode. Read it.

In artifact-only mode there is no conversation to mine. You must **infer** each rationale. Mark it: WHY distractors must come from alternatives you derive (Step 4), and the verdict includes one honesty line (Step 7).

### Step 1: Load the guide

Read `~/.claude/skills/pr-readiness/quiz-guide.md` in full **before mining**. It contains the decision definition, the priority scoring, the stem families, the distractor and flaw rubrics, the grading ladder, and the verdict language. Load it every run, because it is the file tuned over time. Do not work from memory.

### Step 2: Mine the decisions

Two passes, then a cross-check.

**Conversation pass** (session mode): scan the session for choice points. Look for phrases like "we could A or B", "instead", and "actually, let's". Also look for an approach that was tried and then reverted, a correction from the user, an error and the fix chosen for it, a constraint discovered mid-flight, an explicitly accepted tradeoff, and a deferral with a reason.

**Artifact pass:** run `git diff <base>...HEAD` (or `gh pr diff`, or Read the doc) and reconcile:

- Drop mined decisions that are not present in the artifact. They are history and are not part of the artifact under review.
- **Add** decisions visible in the artifact but never discussed. These are prime candidates: the AI chose silently, so the human has had zero chances to rehearse the rationale.

**Artifact-only fallback** (argument passed): reconstruct decision points from the artifact alone. A decision point is every place where the artifact chooses among plausible alternatives, such as a boundary, a data structure, an error path, a sequencing, or a limit given a value. Use commit messages and the PR body as rationale hints.

For each candidate, record the decision, the rejected alternative(s), the rationale (stated or inferred), the anchor (file:line or doc section), and a criticality sketch.

### Step 3: Select and rank

Score each candidate with the guide's priority formula (irreversibility × scope of impact × novelty to author × opacity of rationale) and strike everything on the guide's negative list. Those never appear, regardless of score.

- Cap at **5 to 7 items, one per decision**. Never ask two questions on the same decision (the re-verify in Step 6 is the one exception, and it must come from a different angle). With `--short`, cap at 2 to 3.
- If more than seven candidates remain: sort by score, and break ties toward irreversibility first and then toward scope of impact. Each cut decision gets one line in the Step 7 verdict: *"not quizzed, deserves a skim: …"*.
- **The negative list and the depth screen strike every candidate**: say so in two lines, *"There is no decision here to defend. The work is mechanical and single-path"*, and stop. Do not deliver a quiz, ratings, or a verdict.

Mark the top one or two decisions by score as **two-stage** items.

### Step 4: Draft the items, then self-critique

Draft each item per the guide. First pick the stem family, biased toward failure and mechanism. The families are rejected alternative, conditional reversal, failure prediction, and relational purpose. Next write the stem, and then write three options where every distractor is an alternative that was in fact rejected, a real misconception, or a true-but-not-decisive fact. In artifact-only mode, distractors come from the plausible alternatives you derived, since no session-rejected ones exist.

Apply the guide's depth screen to every stem (*could someone who read the diff attentively but did not reason about it answer this?*) and discard what fails. Redraft it, and do not soften it.

For two-stage items, draft both stages: WHAT (the call or prediction) and WHY (three rationales, distractors plausible-but-wrong per the guide).

Then run the **mandatory self-critique pass**: check every item against the guide's flaw checklist before the user sees any item. The checklist covers cover-the-options, multiple defensible answers, throwaway distractors, longest-option-correct, grammar cues, and except/not stems. Check the first two hardest, because they are the known failure modes of machine-written items. Fix or redraft, and never deliver an unscreened item.

Finally, set each item's key position so the correct answer's slot varies across the quiz, and equalize option lengths.

### Step 5: Pre-quiz self-rating

One AskUserQuestion with the header `Ready?`:

> "Before we start: how well could you defend this work to a skeptical reviewer, today?"

Options: `5 — bulletproof` / `4 — solid` / `3 — big calls yes, edges no` / `2 or less — shaky`. Record the answer and move on without comment, reassurance, or foreshadowing. This rating is the confidence prior the verdict reads against. Do not ask **per-item confidence questions**.

### Step 6: Deliver the quiz

One AskUserQuestion per question, never batched. Header `Q <i>/<K>`. Each item offers the drafted options plus the built-in "Other". **Never add "(Recommended)" labels**, because a quiz with a giveaway does not measure anything, and the key's position varies item to item.

After **every** answer, respond in chat before the next tool call:

- **Correct:** one or two lines that confirm the answer and give the condition under which it would flip. Do not praise or keep a tally.
- **Wrong:** explain immediately with the guide's four-beat template. The beats are the actual call, the mechanism, the pointer into the diff or doc, and the feed-forward. Then queue a re-verify.
- **"Other" (free text):** authoritative. Grade it on the guide's ladder. An owned answer is accepted over the key even when it disagrees with the key. An answer better than the key gets full credit, said out loud. An answer at the surface level of the ladder (mechanics without purpose) gets exactly **one** probe deeper, asked as plain conversation and not as another item, then resolve. Never a second probe.

**Two-stage flow** (top items): stage one asks WHAT. Correct → follow with the WHY stage, header `Why?`. A wrong WHY is the item-level confident-and-wrong signal. Explain it and queue a re-verify. Wrong WHAT → explain immediately and **skip the WHY**, because the explanation just gave the answer away.

**Re-verify:** each explained gap queues one differently-angled question on the same decision. Use a different stem family, per the guide. Append it after the last planned item with the header `Recheck 1` (max `Recheck 2`). Further gaps become verdict notes. A pass upgrades the gap to recovered, and a fail leaves it a gap.

**Escape hatch**, if the user wants out ("just give me the verdict", "skip it"):

- **First time:** "The questions are the value. Defending it to me is cheaper than fumbling it in review. One more, the one you'd most regret being asked there." Deliver only the highest-criticality remaining item (or two).
- **Second time:** respect it. Wrap with what you have, and the verdict states plainly that it is partial: *"only N of K decisions checked, with no readiness claim on the rest."*
- **Full skip** only when the user already demonstrated ownership unprompted, that is, they authored the key rationale in-session themselves. Even then, print a summary, in the verdict format, of what would have been asked.

### Step 7: Post-rating and verdict

Re-ask the Step 5 question verbatim, with the header `Ready now?` and the same options. Then print the verdict in a fenced markdown block:

1. **The delta**, first and plainly: pre-rating → post-rating. Self-generated evidence is stronger than anything the skill could assert.
2. **The confidence read**, derived per the guide. A high pre-rating crossed with a high-criticality gap is confident-and-wrong. Flag it first, because that is the dangerous cell. A low pre-rating crossed with a clean run is underclaim, and say so.
3. **The verdict, decided by criticality and never by a percentage.** The verdict is *Ready to defend*, *Ready, with notes*, or *Not yet*, and criticality decides which. An unrecovered gap on a one-way-door or high-impact decision blocks *Ready* even at six of seven correct. Give each gap and note its feed-forward: what to re-read (with the pointer) and what to raise with a reviewer.
4. **Uncovered decisions**, the Step 3 overflow and escape-hatch skips, one line each.
5. **The honest claim**, in this exact wording: *"N gaps found on the hardest-to-reverse decisions"*, and never "you understand this PR." Add the standing caveat: tests and review still do their jobs, because this checked only whether you can defend the decisions and did not check whether the code works. Artifact-only mode adds its reconstruction line.

## Key Rules

1. **Load `quiz-guide.md` every run.** The rubrics are defined there, and memory is not a substitute.
2. **5 to 7 items, one per decision.** A re-verify after an explained gap is the only exception, always from a different angle.
3. **Nothing from the negative list, nothing below the depth screen.** An item an attentive non-reasoner could answer gets discarded, not softened.
4. **Self-critique every item before delivery.** Multiple defensible answers and throwaway distractors are the known machine failure modes. Screen for them explicitly.
5. **One AskUserQuestion per question, no "(Recommended)" labels, key position varies.** A quiz with giveaways does not measure anything.
6. **"Other" is authoritative.** Grade it on the guide's ladder. A better-than-key answer gets full credit, and you say so out loud.
7. **Feedback is immediate, aimed at the work, and ends in a next action.** Point into the diff or doc, and never praise or shame the person. A failed question is a feature.
8. **One probe per surface answer, then resolve.** A second probe is interrogation.
9. **Criticality decides the verdict, never a percentage.** Claim only "N gaps on the hardest-to-reverse decisions", and never "you understand this."
10. **Act as a colleague rather than an examiner.** Do not show the user a running tally, a red pen, or the guide's machinery vocabulary.
11. **Read-only.** Do not write a file or post anything. The verdict block in conversation is the artifact.
