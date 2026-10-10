---
name: market-launch
version: 1.0.0
description: |
  Choose the channel and plan the launch. Starts from the number that has to
  move, ranks every channel against it (the unfamiliar ones too), and plans the
  launch around the smallest group that makes the product work. Market
  benchmarks need a source, and a missing bright spot is reported as a
  positioning or product signal.
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

# Launch

Poor distribution kills more products than bad product does. Most companies never get one channel working. This skill finds the one channel to run first, then plans a launch that a small group of buyers can actually feel.

It assumes a frame exists. A frame states the category and the alternative being displaced, plus the target buyer and the differentiated value. Without one, build it first with `/market-pitch` (frame only).

## Arguments

- `/market-launch <product>`: rank the channels and plan the launch.
- `/market-launch` (bare): plan for the product under discussion. If there is none, ask once: "What product are we launching?"
- Steers in plain words. "Channels only" stops after Step 3. "Launch only" skips the full ranking when the channel is already chosen, but first states the number and the channels the chosen one was ranked against. A chosen channel is where channel bias hides.

## Cases for another skill

- No frame yet, or the copy itself → `/market-pitch`.
- A launch message that needs testing on a simulated buyer → `/market-rehearse`.
- A launch bet that needs grilling on opportunity cost and worst case → `/idea-challenge`.
- An answer of "build something different" → `/idea-slice`.

## Instructions

Follow these steps in order.

---

### Step 0: Check the frame and load the evidence rules

Confirm the frame. If it is missing, stop and run `/market-pitch` with "frame only" first.

Read the Evidence section of `../market-pitch/pitch-guide.md`. Every number in this skill obeys it. A conversion rate, a channel average, a competitor's numbers, or a "typical launch does X" figure is a claim like any other. Cite where it came from, or mark it as your own guess.

---

### Step 1: State the number

State the number that has to move before you propose anything. If a tactic can't move it even when it works perfectly, drop it now.

Work backwards from the traction goal to the milestones that must happen, then check each activity against that path. Anything off it is a hobby.

---

### Step 2: Rank every channel

- **One channel is usually optimal.** Find it before you spread. Running six half-channels is the most common way to get zero.
- **Fight your channel bias.** Rank every channel, including the ones unfamiliar to you, because the underpriced attention is in those. Then run cheap tests rather than arguing.
- **Channels decay.** The tactic that converted last year converts worse now. Keep the next candidate on deck.

For the top candidates, give the cheap test, what it costs, and the result that would promote or kill each one.

---

### Step 3: Hunt bright spots

Hunt bright spots (the pocket of users who love this) and expand from them. When there is no bright spot anywhere, that is a positioning or product signal rather than a copy problem, and no amount of copy will fix it. Report it in those words, and point to `/market-pitch` for the frame or `/idea-slice` for the product.

On "channels only", deliver and stop here.

---

### Step 4: Plan the launch

- **Launch the simplest version with a value proposition that explains itself.** Feature-complete launches hide the one thing buyers would have understood.
- **Aim at the smallest group that makes the thing actually work,** not at the market size. Density in one tiny pocket beats thin coverage everywhere, and "but the market is bigger than that" is the objection to ignore at this stage.
- **Do whatever it takes**, including things that neither scale nor pay. Throw the party, hand-recruit the first hundred, seed the empty room yourself. The right to scale comes afterwards.
- **Replace missing product with manual work** and say so internally. Release the thing while a human does the part the code can't yet.
- **Come for the tool, stay for the network.** Single-player value comes first, and the multiplayer reason to stay comes second.
- **Competitors copy products easily and networks with difficulty.** Put the moat where copying is hard.
- **Split your attention between product and traction.** Hiding in the product feels productive and is the more comfortable failure.

---

### Step 5: Deliver

- **The number.** What has to move, and the milestones on the path back from the goal.
- **The channel.** The ranking, the chosen channel, and the cheap tests for the runners-up.
- **The bright spot.** Where it is, or the statement that there is none and what that signals.
- **The launch.** The smallest group, the simplest version, and the manual work that replaces missing product.
- **What I won't claim.** Benchmarks and figures without a source, and the evidence that would bring them back.

Deliver one recommendation rather than a menu of options.

---

## Key Rules

1. **State the number before any tactic.** A tactic that can't move it gets dropped.
2. **One channel before many.** Find the one that works before you spread.
3. **Rank every channel**, the unfamiliar ones included, and settle disagreements with cheap tests.
4. **No invented evidence.** Market benchmarks need a source or a "my guess" label, per the Evidence section of `pitch-guide.md`.
5. **No bright spot means a positioning or product problem.** Copy will not fix it.
6. **Launch small and dense.** Aim at the smallest group that makes the thing work, not at the market size.
7. **Take a position.** One recommendation, not a menu.
8. **Split your attention between product and traction.** Hiding in the product feels productive and is the more comfortable failure.
