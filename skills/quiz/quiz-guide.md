# Quiz guide

The reference `quiz` loads every run. It defines what counts as a quizzable decision, how to rank candidates, the question shapes that carry signal, the distractor and flaw rubrics that keep multiple-choice honest, the grading of free-text answers, and the verdict language. Tune it over time — it's the spec.

The spec is distilled from assessment science: item-writing doctrine (NBME), depth taxonomies (Webb's DOK, SOLO), viva/probing practice, the testing effect, and the illusion of explanatory depth. The jargon stays in this file; the user only ever sees a colleague asking good questions.

## What counts as a decision

A decision is a choice among live alternatives — something that could defensibly have gone another way. Tradeoffs accepted, pain points worked around, assumptions baked in, and deliberate omissions all qualify. An implementation with one sane path does not.

Conversation tells: "we could A or B", "instead", "actually, let's", an approach tried and reverted, a correction from the user, an error hit and the fix chosen, a constraint discovered mid-flight, a TODO deferred with reasons.

Artifact tells: a boundary drawn (what's in this module vs. its caller), a data shape, an error path (retry vs. fail vs. queue), a sequencing, a dependency taken, a limit or timeout given a value. For a doc: its claims, its recommendations, its structure, and what it deliberately leaves out.

The richest candidates are decisions **visible in the artifact but never discussed** — the AI chose silently, so the human has had zero chances to rehearse the rationale.

## Priority scoring

Score each candidate 1–3 on four factors; priority is the product.

| Factor | 1 | 2 | 3 |
|---|---|---|---|
| **Irreversibility** | config value, easy revert | new internal API others will call | schema migration, published API, data backfill |
| **Blast radius** | one private function | one subsystem or every reader of a doc section | every caller; the doc's central claim |
| **Novelty to author** | a pattern they've shipped before | familiar area, new technique | first contact with this subsystem or approach |
| **Opacity of rationale** | argued at length in-session | mentioned once in passing | chosen silently, never discussed |

Ties break toward irreversibility: a one-way door beats a loud blast.

**The negative list** — never quizzed, regardless of score:

- **Naming and formatting** — tests taste, not ownership.
- **Ctrl-F-discoverable facts** ("which file holds X") — tests reading, not reasoning.
- **Library and framework trivia** — tests memory of docs, not this artifact.
- **Team-contested calls** — a question with no agreed key measures allegiance, not understanding.
- **Anything answerable without reading the artifact** — generic knowledge is not this PR.

## The depth screen

Target strategic reasoning — justification, prediction, tradeoff — never recall. The one-question filter, applied to every stem:

> Could someone who read the diff attentively but did no reasoning answer this?

If yes, discard the item and redraft; don't soften it.

- ❌ "Which module holds the retry logic?" — attentive reading suffices.
- ✅ "Why does the retry live in the client and not the queue worker?" — demands the mechanism.

## Stem families

Four shapes, in preference order. Bias the mix toward failure-prediction and mechanism — debugging is where comprehension of AI-built work collapses hardest.

| Family | Template | Example |
|---|---|---|
| **Rejected alternative** | "We considered X and shipped Y — what breaks if we'd shipped X?" | "We considered a DB unique index and shipped an app-level check — under what load does the app-level check fail?" |
| **Conditional reversal** | "Under what conditions is this the wrong call?" | "The cache TTL is 5 minutes — name the traffic pattern where that's the wrong number." |
| **Failure prediction** | "This pages at 3am — what's the symptom, and where do you look first?" | "The webhook handler starts timing out — which log do you grep first, and for what?" |
| **Relational purpose** | "What does this buy us that we didn't have?" | "What does the outbox table buy us that a direct publish doesn't?" |

Doc-mode adaptations: failure prediction becomes "a skeptical reader's strongest objection"; where-do-you-look becomes "which section carries the load if this claim is challenged."

## Distractor rubric

Three options per question — more adds reading time, not signal. Every distractor must be one of:

- **A genuinely rejected alternative** — the road not taken, stated as if it were the key.
- **A real misconception** — wrong in the way someone who skimmed would actually be wrong.
- **A true-but-not-decisive fact** — accurate, relevant, and not the reason.

Never a throwaway an amused reader would eliminate on sight. Options stay roughly equal in length and grammatically parallel with the stem — the longest or most hedged option must not flag the key.

- ✅ Distractor: the rejected alternative's own best argument, paraphrased fairly.
- ❌ Distractor: "because it looked nicer" — nobody picks it, so the item is a coin flip between two.

## Item-flaw checklist

Run on every drafted item before delivery. An unscreened item never reaches the user.

- **Cover-the-options test** — can a competent author answer the stem with the options hidden? If not, the stem is incomplete and the options are doing its work.
- **Multiple defensible answers** — the most common machine-written flaw. If two options can be argued, merge or redraft.
- **Throwaway distractors** — the second most common. Every option must be pickable by someone real.
- **Longest-option-correct** — equalize lengths.
- **Grammar and number cues** — every option must complete the stem cleanly.
- **Except/not stems** — rewrite positively; negation tests parsing, not understanding.

## Two-stage construction

Reserved for the top one or two decisions by priority. Stage one asks WHAT — the call made or the prediction. Stage two asks WHY — three rationales, where the distractors are plausible-but-wrong: the rejected alternative's rationale paraphrased, a real-sounding misconception, a true-but-not-decisive benefit.

Flow rules:

- WHY is asked only after a correct WHAT. A wrong WHAT is already a gap — teach, skip the WHY (the teach just contaminated it), schedule a re-verify.
- WHAT right, WHY wrong is the item-level **confident-and-wrong** signal: they know what was done without knowing why. Weight it accordingly in the verdict.

## Grading free-text answers

The built-in "Other" is authoritative — grade whatever the user types on this ladder:

| Level | Looks like | Call |
|---|---|---|
| **Missed** | wrong, or one disconnected fact | gap — teach |
| **Surface** | mechanics recited, no purpose or tradeoff ("it retries three times with backoff") | one probe deeper, then resolve |
| **Owned** | purpose + tradeoff + condition connected ("it absorbs transient 503s so checkout doesn't fail, at the cost of holding the connection longer") | correct, even if it disagrees with the key |
| **Beyond the key** | generalizes or improves on the shipped rationale | full credit, said out loud; a verdict strength |

The probe: exactly one follow-up within the same decision, asked as plain conversation, not another item — "what does that buy us?" or "when would that stop being enough?". A deep answer gets **more specific** under the probe; a surface one gets vaguer or replays the AI's phrasing. One probe, then resolve — a second reads as interrogation and oversamples one decision.

If an "Other" answer genuinely beats the shipped rationale, say so plainly and suggest updating the PR description or doc — the artifact should carry the better argument.

## Feedback

Immediate, at the point of the miss, before the next question. A wrong answer corrected now beats a question never asked — that is the point of quizzing before review instead of during it.

Template, four beats: **the actual call → the mechanism (2–3 sentences) → the pointer (file:line or doc section) → the feed-forward** ("re-read the pool sizing before you ship" / "ask your reviewer whether X was considered").

Feedback addresses the work, never the person. Banned in both directions: "great job!", "you should know this", "incorrect.", any running score. Correct answers get one line — confirm, plus the condition under which the answer would flip.

## Teach, then re-verify

After teaching a gap, queue one re-verify on the same decision: a **different stem family**, delivered near the end of the quiz. Same-angle repeats test short-term memory of the teach; a new angle tests whether the mechanism landed.

Cap re-verifies at two, spent on the highest-criticality gaps; further gaps become feed-forward notes in the verdict. A passed re-verify upgrades the gap to **recovered**; a failed one keeps it a gap and sharpens the feed-forward.

## Confidence read

Derived, never asked per-item. The pre-quiz self-rating is the prior; cross it with results:

- Pre-rating 4–5 + a gap on a high-criticality item = **confident-and-wrong** — the dangerous cell. Flag it first and prominently in the verdict.
- Pre-rating ≤3 + a clean run = **underclaim** — say so; unwarranted doubt has a cost too.
- Hedged "Other" answers ("I think…?") that grade as owned also count toward underclaim.

## Verdict language

Three verdicts, gated on criticality — never on a percentage:

- **Ready to defend** — no gaps on high-criticality decisions. Notes allowed.
- **Ready, with notes** — low-criticality gaps only, each with its feed-forward line.
- **Not yet** — at least one unrecovered gap on a one-way-door or high-blast decision. Even at 6/7 correct. Name exactly what to re-read (pointer) and what to raise with a reviewer.

The honest validity claim, verbatim shape: *"N gaps found on the hardest-to-reverse decisions"* — never "you understand this PR." A handful of questions cannot certify understanding; it can only fail to find gaps where gaps matter most.

One standing caveat, in every verdict: this checks whether you can *defend* the decisions, not whether the code *works* — tests and review still do their jobs.

Artifact-only mode adds one line: rationale was reconstructed from the artifact, not the discussion — the quiz tested defensibility, not fidelity to a conversation that isn't here.

## Tone

A colleague asking the questions a skeptical reviewer will ask — not an examiner grading. Exam theater causes the exact rubber-stamping this skill exists to prevent. No running tally, no ✓/✗, no red pen, and none of this guide's vocabulary (priority scores, depth screens, grading ladders) ever shown to the user.

Banned phrasings: "Incorrect.", "Let's see if you know…", "As expected, you missed…", "Don't worry, this one's easy."
