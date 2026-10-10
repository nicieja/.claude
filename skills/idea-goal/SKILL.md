---
name: idea-goal
version: 1.0.0
description: |
  Turn a vague goal into a measurable one, and a product question (build,
  rank, launch, or kill) into one recommendation backed by evidence. Translates
  the goal to money, specifies it as Scale, Meter, Benchmark, Constraint, and
  Target, probes the riskiest assumption with a small slice of the budget, and
  writes a short decision memo. Ends with a hand-off to /idea-challenge.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - Skill
---

# Goal

Turn raw demand into a measurable goal, and a product question into a decision. The output is one recommendation with its evidence, never a list of considerations. Conviction comes from the specificity in the memo (the specific user, the measured benchmark, and the demoable slice that `/idea-slice` defines) rather than from forced confidence.

## Arguments

- `/idea-goal <goal | proposal | question>`: shape that goal or decision.
- `/idea-goal` (bare): use the proposal under discussion. If there is none, ask once: "What decision or goal should I shape?"

## Cases for another skill

- Slicing the work into stories and milestones → `/idea-slice`.
- Grilling the proposal before anyone commits → `/idea-challenge`.
- A build plan with research and file-level steps → `/idea-spec`.
- A claim about the current state of production data → `/production-query`.

## Report mode

When the `reviewer` agent loads this skill from a brief, there is no user to ask. Work from the material in the brief. Each question you would ask becomes a listed gap. A missing number is reported as a gap and is never estimated. A shaky answer in Step 1 doesn't end the report: list it as a gap, continue, and mark the recommendation as conditional on that gap. The output follows the format the brief defines.

## Instructions

Follow these steps in order. One question per AskUserQuestion call.

### Step 0: Frame the question

Pull the product context:

- the target users and the current metrics
- the goal behind the request
- recent wins and losses
- the competitive moves that matter here

Then look at the evidence: user feedback, analytics, and competitive moves. Separate signal from noise. A theme that shows up in both what users say and what the data shows is real, and a theme with one source is suspect.

Then state which call this is: build, rank, launch, or kill. Steps 1 to 4 apply to every call. Step 5 applies to rank calls, and Step 6 to build and launch calls.

### Step 1: The one-breath test

Answer these in one breath:

- who this is for
- what problem it solves better than the alternative, with the specific competitor or status-quo behavior it displaces
- why now

If any answer is shaky, the strategy is shaky. Say which one and stop there until it's fixed (in report mode, see **Report mode**).

### Step 2: Translate the goal to money

A goal that can't be translated to money (saved, made, or protected) isn't sharp enough. The translation conversation alone kills doomed projects before they start. If no path to dollars survives serious examination, recommend that the work not be funded.

### Step 3: Specify the goal

Specify each goal with five elements:

- **Scale**: what we'll measure
- **Meter**: how we'll measure it
- **Benchmark**: the current value
- **Constraint**: the minimum acceptable value, or the break-even point for the investment
- **Target**: the desired value

A benchmark you can't measure today is a gap to close first. Never fill it with a guess presented as a measurement.

### Step 4: Probe the riskiest assumption

If the math says there's enough budget to try, spend a small slice of it first to test the riskiest assumptions. If they fail, kill the project before the rest is gone. Cheap assumption probes are the highest-leverage prioritization tool you have.

Watch for "we already started it". Sunk cost is not priority. Judge the work with fresh eyes, as if nothing had been spent.

### Step 5: Rank the work (rank calls only)

Don't deliver a list. Deliver a sequence with a reason for each item.

- Rank by expected value (impact × probability) ÷ effort, and don't fudge the inputs. Probability is a forecast rather than a wish, and impact is measurable rather than aspirational.
- When the field is narrow, use a "do this first because X is bleeding" argument instead of a scoring sheet.
- The lowest-energy items often dominate when you're honest about effort. Don't pad estimates to make a vanity item win.
- "We already started it" is not a reason for a higher place. Sunk cost is not priority. Look at the list with fresh eyes every quarter.

### Step 6: Define success before release (build and launch calls)

- Define success before launch. State which metric moves and by how much, and in what window. Without that, "the launch went well" is unfalsifiable.
- Pick a North Star and 2 to 3 supporting metrics. More than that and you're hedging.
- Instrument before launch, not after. A feature released without measurement is a feature you can't iterate on.
- Run the launch as a hypothesis test. Set the threshold at which you double down and the one at which you roll back.
- Agree in advance when the data gets reviewed and who decides what to do next.

### Step 7: Write the decision memo

Deliver a position rather than a deck:

- **What we're doing**: one sentence. For a rank call, the ordered sequence from Step 5, with one reason per item.
- **Why now**: the demand or the deadline that makes this urgent.
- **What we're not doing**: the explicit tradeoff.
- **How we'll know**: the metric and the bar, from Step 3.
- **Worst case**: what happens if this is wrong. Add how fast we find out and how reversible it is.

Give one recommendation. A menu of options hands the decision back without the analysis.

Close with one line: *"Take this to `/idea-challenge` next."*

## Key Rules

1. **A goal translates to money.** When serious examination doesn't find a path to money, recommend against funding the work.
2. **Specify all five elements.** Close a missing benchmark as a gap, and never fill it with a guess.
3. **Probe the riskiest assumption before spending the rest.**
4. **Sunk cost is not priority.**
5. **One recommendation per memo.** For a rank call, the recommendation is the sequence. The memo states what we're not doing as clearly as what we are.
6. **Instrument before release.** A build or a launch without measurement is a release you can't iterate on.
7. **Report mode never asks.** A question becomes a listed gap.
