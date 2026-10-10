---
name: market-rehearse
version: 1.0.0
description: |
  Rehearse a pitch, a frame, or a draft on simulated buyers before it meets a
  real one. Pre-registers the hypothesis and its fail condition, builds the
  brief from real customer material, and runs 2 or 3 isolated persona agents
  with different temperaments. It can kill an idea cheaply and can never
  confirm one. Each persona line becomes a question for a real person, never
  evidence.
allowed-tools:
  - Read
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - Agent
  - SendMessage
  - Skill
---

# Rehearse

Put a buyer in the room. Dispatch the `persona` agent, hand it a brief, ask about its world, then show it the asset and find where the pitch falls over. It's a rehearsal room and not a research method, worse than a real customer in every way except that you can run it now, twice, before anyone sees the draft.

The `persona` agent (`~/.claude/agents/persona.md`) has no tools and knows only its brief. That isolation is deliberate: a buyer who has read your material hands your own value proposition back as a discovery. This skill writes the brief and runs the conversation. The agent plays the buyer.

## Arguments

- `/market-rehearse <asset or hypothesis>`: rehearse that asset, or the asset that tests that hypothesis.
- `/market-rehearse` (bare): rehearse the frame or draft under discussion. If there is none, ask once: "What should the buyer see, and what do you expect to learn?"

## Cases for another skill

- No frame or draft yet → `/market-pitch`.
- A real customer is reachable → talk to them, because a rehearsal is worse in every way except speed.
- A tagline tweak → no rehearsal. Edit the line.

## Instructions

Follow these steps in order.

---

### Step 0: Decide whether a rehearsal fits

Use it when the work turns on a persona:

- pressure-testing the frame
- working out which anxieties the copy has to answer
- checking whether a draft fits the buying stage it claims
- comparing how two segments meet the same asset

A tagline tweak doesn't need one.

---

### Step 1: Pre-register the hypothesis and the fail condition

Write one falsifiable sentence, and what would count as a fail, *before* writing the brief. This is what stops the goalposts moving after an answer you didn't want. Show both to the user.

---

### Step 2: Ground the brief

Read the Evidence section of `../market-pitch/pitch-guide.md` first. Real customer language, where it exists, goes *into* the persona instead of being replaced by it.

- **Grounded** means you pulled the real material first and built the brief out of it. Every trait traces back to a ticket, a quote, a call, or a review. Load the relevant connector tools via ToolSearch (support inbox, CRM, tracker, chat, docs), or ask the user for a paste.
- **Assumed** means nothing real was available, and every trait is labeled an assumption, in the brief and in the output.

Never run Assumed when Grounded is one connector call away, and never describe the two as though they were the same thing.

---

### Step 3: Write the brief

**The brief is a whitelist.** The persona can't look anything up and has no context but the brief. So the brief contains their situation and nothing else:

- their role and what they're accountable for
- the size and kind of their company
- what their week actually looks like
- the workaround in use today and what it costs them
- budget authority and who else has to say yes
- what happens to *them* if they pick wrong
- how they meet change (eager, wary, indifferent)
- in the grounded case, the words they really used

The persona takes its temperament from you, so choose it on purpose and record the choice. A persona left unprimed is not neutral, just vague.

These never go in a brief, in any wording:

- your hypothesis
- your value proposition
- your category frame
- your read of the competitive set
- your draft copy
- your analysis
- the buyer's own shopping status (whether this person would go looking is what the rehearsal measures, so writing it in answers the question)

Any trait phrased as a conclusion rather than a circumstance is also out. *Closes the books by hand every month* is a circumstance. *Frustrated by manual work* is the finding the rehearsal exists to produce. Write it in and you're guaranteed to get it back. Temperament obeys the same line: *eager to try new tools* or *burned by the last rollout* is a circumstance, and *excited about this product* is a conclusion and never goes in. They learn about the product when you show them the asset, and only what the asset says. A real buyer meets it the same way.

---

### Step 4: Audit the brief against the hypothesis

Whatever the brief and the hypothesis share is where the answer gets planted. A brief that can only produce one answer is a broken brief. Rewrite it before any dispatch.

---

### Step 5: Run the panel

**Run two or three over the same asset**, not one, and vary the temperament across them. An all-skeptic panel can only kill and an all-enthusiast panel is a pep rally, and neither one tells you anything. One persona is an anecdote.

Spawn with the Agent tool, `subagent_type: "persona"`, and **never `"fork"`**, which hands it your whole context and turns the exercise into you talking to yourself. The dispatch prompt is the brief plus your first line as the seller, without your notes or your hypothesis. Continue the same persona with `SendMessage` so its context remains intact. Where that isn't available, re-dispatch with the brief plus the dialogue turns only, never your own notes.

**In a tool without subagents**, tell the user to open a new chat that has not seen this conversation. The first message in that chat is `~/.claude/agents/persona.md` followed by the brief. After that, the user relays each seller line you write and pastes each reply back here.

---

### Step 6: Ask without leading

A rigged rehearsal produces a transcript that reads exactly like customer research. The rules in Steps 1, 4, 6, and 7 (pre-register the hypothesis, audit the brief, ask open questions, re-brief only for mechanical failure) are what prevent that.

- Ask about their world first. Ask what they did and in what order, then ask what happened next.
- Show the asset only after that. They know exactly what it says and nothing more.
- **Open questions before closed ones, and never one that contains its own answer.** Don't ask whether a benefit would appeal to them.
- Push past the first answer. The persona leads with the acceptable reason and gives the real one only to a seller who keeps asking why.

---

### Step 7: Re-brief only for mechanical failure

**Re-brief only for mechanical failure.** That means it broke character or coached you, it invented product facts, or the brief leaked. **Never re-brief because the answer was unwelcome**, and log every re-brief and its reason.

---

### Step 8: Read the panel

The signal is where the personas diverge (a segment split) or converge (a probably-real objection). Personas built from different sources and temperaments objecting in the same words is the cheapest tell that a brief was leaking.

Score the result against the fail condition from Step 1, as written. **A hypothesis that passes a rehearsal is still unconfirmed.** This kills an idea cheaply, and it can never confirm one.

---

### Step 9: Deliver

**What I tested on a simulated buyer:**

- Which personas ran, each one grounded or assumed, with its temperament.
- The hypothesis and its pre-registered fail condition, and whether the fail condition was met.
- What broke. List each objection and where the asset lost them, plus the divergences between personas.
- Any re-brief and why.
- What a real person still has to confirm, written as questions for a real buyer.

When the rehearsal ran for `/market-pitch`, this block goes into that skill's delivery.

---

## Key Rules

1. **A simulated buyer is a rehearsal, never a source.** Anything it says becomes a question for a real person and never a quote, a number, or a proof point.
2. **Never lead a persona.** Keep your hypothesis out of the brief, don't ask a question that contains its own answer, and don't re-run one because you didn't like what it said.
3. **Pre-register first.** The hypothesis and the fail condition exist before the brief does.
4. **Grounded before Assumed.** Never run Assumed when Grounded is one connector call away, and label every assumed trait.
5. **The brief is a whitelist.** Circumstances only, never conclusions, and nothing of yours.
6. **`persona` only, never `fork`.** Continue with `SendMessage`, or re-dispatch with the brief plus the dialogue turns only.
7. **Two or three personas, varied temperament.** One persona is an anecdote.
8. **A pass never confirms.** A rehearsal can kill an idea cheaply, and a real buyer still has to confirm it.
9. **No invented evidence.** The Evidence section of `../market-pitch/pitch-guide.md` applies to everything this skill reports.
