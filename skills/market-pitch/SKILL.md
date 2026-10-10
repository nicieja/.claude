---
name: market-pitch
version: 1.0.0
description: |
  Make a product understood and bought through positioning, category, story,
  proof, and copy. Starts demand-side from the buyer's struggling moment and
  builds the frame before it writes a word. Never invents evidence: missing
  proof becomes a stated gap. Use for a landing page, a pitch, a one-pager,
  launch copy, or a category decision.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - Agent
  - Skill
---

# Pitch

Make a product understood and bought. Work demand-side. Start from the buyer's struggling moment and the progress they're trying to make, never from the feature list. Copy is the last thing you write, not the first.

Read `pitch-guide.md` in this directory at the start of every run. It contains the positioning questions, the demand forces, buyer fear, the rules for words, and the rules for evidence. The steps below apply it.

## Arguments

- `/market-pitch <product or asset>`: build the frame and write the asset, such as a landing page or a sales email.
- `/market-pitch` (bare): pitch the product under discussion. If there is none, ask once: "What product, and what asset?"
- Steers in plain words. "Frame only" stops after Step 1. "Just the copy" still checks the frame first, because copy written on a broken frame is wasted work.

## Cases for another skill

- Channel choice, traction, or a launch plan → `/market-launch`.
- A draft that needs pressure-testing on a simulated buyer → `/market-rehearse`.
- A pitch that needs breaking on strategic fit, opportunity cost, demand versus interest, and worst case → `/idea-challenge`.
- An answer of "build something different" → `/idea-slice`.
- Prose cleanup on a finished draft → `/edit-deslop`.

## Instructions

Follow these steps in order.

---

### Step 0: Load the guide

Read `pitch-guide.md`. Each step below points to the section it applies.

---

### Step 1: Establish the frame

The frame says who this is for, what they'd use instead, and what you can do that the alternative can't. If it isn't there, build it before anything else.

Answer the six positioning questions out loud (guide: "Positioning comes first"). Use the customer's view of the competitive set, not yours. When the current frame invites expectations the product doesn't meet, change the frame before you change the words.

On "frame only", deliver the frame and stop.

---

### Step 2: Find the struggling moment

Find what pushed this person to start looking, and what's holding them back (guide: "Always start from demand"). Size the four forces for this buyer. Chain the why until the real job appears, and never accept the first answer.

---

### Step 3: Gather real customer language

Never invent it. Follow the guide's Evidence section. Pull what customers actually said from the connectors this session has, the repo, and the web, or ask the user for a paste.

Where evidence is missing, the claim waits. Record the gap and what would close it, for the delivery in Step 8.

---

### Step 4: State the buying stage

Every asset serves one buying stage. Choose it from first thought, passive looking, active looking, deciding, onboarding, and ongoing use. State it before you write.

---

### Step 5: Write

Apply the guide's sections "The buyer is afraid" and "The words":

- Make the case for change against the status quo before you make the case for you.
- Answer the buyer's three fears before you add magnetism.
- Put proof beside every claim, or cut the claim.
- Delete any sentence a competitor could publish unchanged.
- Take a side in the headline.

---

### Step 6: Offer a rehearsal

When the work turns on a persona, offer `/market-rehearse` before the draft meets a real buyer. Use it for a frame that needs pressure-testing, or for a draft that may not fit the buying stage it claims. A tagline tweak doesn't need one.

---

### Step 7: Break it before it goes out

Run every draft through `/edit-deslop` before it goes out. The pitch needs breaking before anyone outside sees it, and this step is required. Dispatch the `reviewer` agent (`subagent_type: "reviewer"`). Its brief contains the frame and the draft, and tells it to load `idea-challenge` in brief mode on the product or go-to-market route. That route runs the executive concerns, such as strategic fit, opportunity cost, demand versus interest, and the worst case. In a tool without subagents, run `/idea-challenge` on the frame and the draft. Fix what the verdict breaks, and put the verdict in the delivery.

---

### Step 8: Deliver and hand off

- **The frame.** Category, the alternative you're displacing, the target buyer, the differentiated value, the proof.
- **The story.** The struggling moment, the four forces at play, and the buying stage this asset serves.
- **The words.** The draft itself.
- **What I tested on a simulated buyer** (only when a rehearsal ran). The delivery block from `/market-rehearse`.
- **What I won't claim.** What got cut for lack of proof, and the evidence that would bring it back.
- **The number.** What should move if this works, and roughly how much.
- **The pressure-test.** The verdict from Step 7, and what changed because of it.

Deliver one recommendation rather than a menu of options.

If the answer turns out to be "build something different," suggest `/idea-slice`.

---

## Key Rules

1. **Positioning before words.** A broken frame gets rebuilt, never decorated.
2. **No invented evidence.** Missing proof becomes a stated gap or a question, never a plausible-sounding number.
3. **Every claim comes with proof or gets cut.** Don't soften, don't write "helps you," and don't use weasel verbs.
4. **Position against the status quo in every asset**, not only against named vendors.
5. **Cut anxiety before adding magnetism.**
6. **State the buying stage** of every asset before writing it.
7. **Take a position.** Avoid the hedged middle and the both-sides headline.
8. **A simulated buyer is a rehearsal, never a source.** Anything a rehearsal produced becomes a question for a real person and never a quote, a number, or a proof point.
