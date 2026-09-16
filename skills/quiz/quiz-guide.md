# Quiz guide

The reference `quiz` loads every run. It defines what counts as a quizzable decision, how to rank candidates, the question formats that produce signal, the distractor and flaw rubrics that keep multiple-choice honest, the grading of free-text answers, and the verdict language. Tune it over time, because it's the spec.

The spec is distilled from assessment science: item-writing doctrine (NBME), depth taxonomies (Webb's DOK, SOLO), viva/probing practice, the testing effect, and the illusion of explanatory depth. The jargon remains in this file. The user only ever sees a colleague asking good questions.

## What counts as a decision

A decision is a choice among live alternatives that could defensibly have gone another way. Tradeoffs accepted, pain points worked around, assumptions built in, and deliberate omissions all qualify. A change with one sane path does not.

Conversation tells: "we could A or B", "instead", "actually, let's", an approach tried and reverted, a correction from the user, an error hit and the fix chosen, a constraint discovered mid-flight, a TODO deferred with reasons.

Artifact tells: a boundary drawn (what's in this module vs. its caller), a data structure, an error path (retry vs. fail vs. queue), a sequencing, a dependency taken, a limit or timeout given a value. For a doc, the tells are its claims and recommendations, its structure, and what it deliberately leaves out.

The richest candidates are decisions **visible in the artifact but never discussed**. The AI chose silently, so the human has had zero chances to rehearse the rationale.

## Priority scoring

Score each candidate 1 to 3 on four factors. Priority is the product.

| Factor | 1 | 2 | 3 |
|---|---|---|---|
| **Irreversibility** | config value, easy revert | new internal API others will call | schema migration, published API, data backfill |
| **Scope of impact** | one private function | one subsystem or every reader of a doc section | every caller; the doc's central claim |
| **Novelty to author** | a pattern they've released before | familiar area, new technique | first contact with this subsystem or approach |
| **Opacity of rationale** | argued at length in-session | mentioned once in passing | chosen silently, never discussed |

Ties break toward irreversibility: a one-way door ranks above a wide impact.

Items on **the negative list** are never quizzed, regardless of score:

- **Naming and formatting**: tests taste, not ownership.
- **Ctrl-F-discoverable facts** ("which file holds X"): tests reading, not reasoning.
- **Trivia about a library or framework**: tests memory of the docs, not this artifact.
- **Team-contested calls**: a question with no agreed key measures allegiance, not understanding.
- **Anything answerable without reading the artifact**: generic knowledge is not this PR.

## The depth screen

Target strategic reasoning (justification, prediction, tradeoff), never recall. Apply this one-question filter to every stem:

> Could someone who read the diff attentively but did not reason about it answer this?

If yes, discard the item and redraft. Don't soften it.

- ❌ "Which module holds the retry logic?" Attentive reading suffices.
- ✅ "Why does the retry live in the client and not the queue worker?" This demands the mechanism.

## Stem families

The families below are in preference order. Bias the mix toward failure-prediction and mechanism, because debugging is where comprehension of AI-built work collapses hardest.

| Family | Template | Example |
|---|---|---|
| **Rejected alternative** | "We considered X and built Y. What breaks if we'd built X?" | "We considered a DB unique index and built an app-level check. Under what load does the app-level check fail?" |
| **Conditional reversal** | "Under what conditions is this the wrong call?" | "The cache TTL is 5 minutes. State the traffic pattern where that's the wrong number." |
| **Failure prediction** | "This pages at 3am. What's the symptom, and where do you look first?" | "The webhook handler starts timing out. Which log do you grep first, and for what?" |
| **Relational purpose** | "What does this give us that we didn't have?" | "What does the outbox table give us that a direct publish doesn't?" |

Doc-mode adaptations: failure prediction becomes "a skeptical reader's strongest objection", and where-do-you-look becomes "which section supports this claim if it is challenged."

## Distractor rubric

Use three options per question, because more adds reading time, not signal. Every distractor must be one of:

- **An alternative that was in fact rejected**, the road not taken, stated as if it were the key.
- **A real misconception** that is wrong in the way someone who skimmed would actually be wrong.
- **A true-but-not-decisive fact** that is accurate, relevant, and not the reason.

Never a throwaway an amused reader would eliminate on sight. Options remain roughly equal in length and grammatically parallel with the stem. The longest or most hedged option must not flag the key.

- ✅ Distractor: the rejected alternative's own best argument, paraphrased fairly.
- ❌ Distractor: "because it looked nicer". Nobody picks it, so the item is a coin flip between two.

## Item-flaw checklist

Run on every drafted item before delivery. Never deliver an unscreened item.

- **Cover-the-options test**: can a competent author answer the stem with the options hidden? If not, the stem is incomplete and the options are doing its work.
- **Multiple defensible answers**: the most common machine-written flaw. If two options can be argued, merge or redraft.
- **Throwaway distractors**: the second most common. Every option must be pickable by someone real.
- **Longest-option-correct**: equalize lengths.
- **Grammar and number cues**: every option must complete the stem cleanly.
- **Except/not stems**: rewrite positively. Negation tests parsing, not understanding.

## Two-stage construction

Reserved for the top one or two decisions by priority. Stage one asks WHAT (the call made or the prediction). Stage two asks WHY, with three rationales where the distractors are plausible-but-wrong. The distractors are the rejected alternative's rationale paraphrased, a real-sounding misconception, and a true-but-not-decisive benefit.

Flow rules:

- WHY is asked only after a correct WHAT. A wrong WHAT is already a gap: teach, skip the WHY (the explanation has just contaminated it), and schedule a re-verify.
- WHAT right, WHY wrong is the item-level **confident-and-wrong** signal: they know what was done without knowing why. Give it matching weight in the verdict.

## Grading free-text answers

The built-in "Other" is authoritative. Grade whatever the user types on this ladder:

| Level | Looks like | Call |
|---|---|---|
| **Missed** | wrong, or one disconnected fact | gap, then teach |
| **Surface** | mechanics recited, no purpose or tradeoff ("it retries three times with backoff") | one probe deeper, then resolve |
| **Owned** | purpose + tradeoff + condition connected ("it absorbs transient 503s so checkout doesn't fail, at the cost of holding the connection longer") | correct, even if it disagrees with the key |
| **Beyond the key** | generalizes or improves on the rationale in the artifact | full credit, said out loud, and a verdict strength |

The probe is exactly one follow-up within the same decision, asked as plain conversation rather than as another item, such as "what does that give us?" or "when would that stop being enough?". A deep answer gets **more specific** under the probe, while an answer graded Surface gets vaguer or replays the AI's phrasing. Ask one probe, then resolve, because a second reads as interrogation and oversamples one decision.

If an "Other" answer is better than the rationale in the artifact, say so plainly and suggest updating the PR description or doc, because the artifact should contain the better argument.

## Feedback

Immediate, at the point of the miss, before the next question. A wrong answer corrected now is better than a question never asked. That is the point of quizzing before review instead of during it.

Use a four-beat template: **the actual call → the mechanism (2 to 3 sentences) → the pointer (file:line or doc section) → the feed-forward** ("re-read the pool sizing before you merge" / "ask your reviewer whether X was considered").

Feedback addresses the work, never the person. Banned in both directions: "great job!", "you should know this", "incorrect.", any running score. Correct answers get one line: confirm, plus the condition under which the answer would flip.

## Re-verify after teaching

After you explain a gap, queue one re-verify on the same decision. Use a **different stem family**, delivered near the end of the quiz. Same-angle repeats test short-term memory of the teach. A new angle tests whether the mechanism was understood.

Cap re-verifies at two, spent on the highest-criticality gaps. Further gaps become feed-forward notes in the verdict. A passed re-verify upgrades the gap to **recovered**, and a failed one keeps it a gap and sharpens the feed-forward.

## Confidence read

Derived, never asked per-item. The pre-quiz self-rating is the prior. Cross it with results:

- Pre-rating 4 to 5 + a gap on a high-criticality item = **confident-and-wrong**, the dangerous cell. Flag it first and prominently in the verdict.
- Pre-rating ≤3 + a clean run = **underclaim**. Say so, because unwarranted doubt has a cost too.
- Hedged "Other" answers ("I think…?") that grade as owned also count toward underclaim.

## Verdict language

The verdict depends on criticality, never on a percentage:

- **Ready to defend**: no gaps on high-criticality decisions. Notes allowed.
- **Ready, with notes**: low-criticality gaps only, each with its feed-forward line.
- **Not yet**: at least one unrecovered gap on a one-way-door or high-impact decision, even at 6/7 correct. State exactly what to re-read (pointer) and what to raise with a reviewer.

The honest validity claim, in this exact form: *"N gaps found on the hardest-to-reverse decisions"*, never "you understand this PR." A few questions cannot certify understanding. They can only fail to find gaps where gaps matter most.

One standing caveat, in every verdict: this checks whether you can *defend* the decisions, not whether the code *works*. Tests and review still do their jobs.

Artifact-only mode adds one line: rationale was reconstructed from the artifact rather than the discussion. The quiz tested defensibility rather than fidelity to a conversation that isn't here.

## Tone

A colleague asking the questions a skeptical reviewer will ask, and never an examiner grading. Exam theater causes the exact rubber-stamping this skill exists to prevent. Never show the user a running tally, ✓/✗ marks, a red pen, or this guide's vocabulary (priority scores, depth screens, grading ladders).

Banned phrasings: "Incorrect.", "Let's see if you know…", "As expected, you missed…", "Don't worry, this one's easy."
