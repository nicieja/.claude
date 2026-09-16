---
name: 10x
version: 1.1.0
description: |
  Generate the 10x version of a plan, spec, PR, ticket, UX flow,
  or architecture proposal. Reveals the gap between where the
  artifact sits today and where it could sit. Generative and never
  adversarial: it paints the picture and does not grill.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# 10x

Imagine the platonic ideal on one artifact. The output is two short pieces of prose and a list of differences. The prose covers where the artifact sits today and what 10x of it would look like, and the list covers the gap between them. The skill paints the picture and stops. What to do with the gap is the user's call.

This skill is *generative*. It does not grill or challenge, and it does not tell the user they're settling. The adversarial register belongs to `founder` and `/pushback`. The planning register belongs to `/shape`. `/10x` is for one move: vivid possibility-painting.

## Arguments

- `/10x <path>`: a file path (a `/shape` plan, spec, design doc, PR description saved locally)
- `/10x <ticket-id>`: a Linear ticket ID matching `[A-Z]+-\d+` (e.g., `ENG-1234`)
- `/10x <url>`: a Linear URL or GitHub PR URL
- `/10x <text>`: freeform description of what to stretch, in quotes or unquoted
- `/10x` with no args: ask once, "What should I stretch?" and wait

## Cases for another skill

- They want to *challenge* a claim or proposal → use `/pushback` or the `founder` subagent
- They want to *refine into a plan* → use `/shape`
- They're diagnosing a bug or production issue → use `/investigate`
- They want the full 1→11 ladder, not just the apex → not this skill (apex-only by design)
- They want the "practical adjacent step" to take after the absurd top. That is also not this skill. Surface the gap and stop. The user picks the move.

## Instructions

Follow these steps in order. Do not skip.

---

### Step 0: Parse the input

Determine the input type and resolve it:

- **Looks like a path** (starts with `/`, `./`, `~/`, or matches an existing file) → `Read` the file
- **Matches `[A-Z]+-\d+`** → Linear ticket → fetch it (description, state, comments) through the Linear MCP tools (load them via ToolSearch if deferred). If Linear is unavailable in this session, stop and say so: the ticket is the input.
- **URL**: for a Linear URL, extract the ticket ID and fetch it the same way. For a GitHub PR URL, use `gh pr view <num> --json title,body,baseRefName,headRefName`
- **Otherwise** → treat the argument as freeform text describing the artifact

If no argument was provided, ask once: "What should I stretch?" and wait. Do not proceed without input.

---

### Step 1: Understand the artifact

Read the input and write one tight paragraph capturing:

- **What it's trying to do**: the core intent in plain language
- **Who it's for**: the user, customer, developer, team, business
- **Current ambition**: what level of value or experience it's currently aiming at

Distill. Do not quote the artifact at length. If the input is sparse (a one-line ticket, a thin text prompt), say so and work with what you have. Do not invent detail to pad the understanding.

---

### Step 2: Pick the value axis

The 10x only makes sense along an axis. Different artifacts have different natural axes:

- **Product feature / UX flow** → end-user experience and value delivered
- **Roadmap bet** → strategic impact, market position, business outcome
- **Architecture / refactor / infra** → developer experience, operational simplicity, leverage
- **PR / code change** → what the code enables for users or the team
- **Process change** → friction removed, decision quality, team velocity

Pick the *dominant* axis, the one that determines whether the artifact ultimately succeeds. If two compete, pick the one a thoughtful stakeholder would say is the goal. State the axis explicitly in one sentence (*"The axis here is end-user onboarding experience"*) so the 10x version that follows is grounded rather than free-floating.

---

### Step 3: Generate the 10x version

Write the 10x version as one short narrative paragraph. The constraints to push past:

- Cost and budget
- Team size and skill mix
- Current tech stack
- Timeline
- Risk tolerance
- Politics, history, "we don't do that here"

It should be specific, sensory, named. Not *"improve the onboarding experience."*

Rules that always apply:

- **Concrete.** Specific moments, specific people, and specific outcomes instead of abstractions.
- **Vivid.** A reader should be able to picture it.
- **Single paragraph.** Write a scene rather than a feature list, a roadmap, or a bullet stack.
- **Single axis.** Don't 10x multiple dimensions at once, because that produces noise. Pick the one from Step 2 and go.
- **Unhedged.** Leave out `ambitious but…`, `of course we'd need…`, and `in an ideal world…`. The goal is to push past constraints, and hedging undoes it.

---

### Step 4: Surface the gap

Present the output in exactly this structure, with these section headings:

```
## Where it sits today

<the one-paragraph distillation from Step 1>

## 10x

<the vivid concrete narrative from Step 3>

## The gap

- <bullet, one sentence, on something specifically different>
- <bullet, one sentence, on something specifically different>
- <3 to 5 bullets total>
```

End there. Do not:

- Propose the "practical adjacent step" or "what you could deliver next quarter"
- Rate the current proposal on a stars scale ("this is a 4-star experience")
- Tell the user they're settling
- Suggest a roadmap or next actions
- Ask "want me to build this?" or "should I file a ticket?"

The gap is the artifact. What the user does with it is their decision, made outside this skill.

---

## Key rules

1. **One artifact along one axis with one 10x.** Don't 10x multiple dimensions at once. Pick the dominant axis and go.
2. **Concrete beats abstract.** A vivid scene with a named moment is better than a list of improvements every time.
3. **Generative and never adversarial.** Leave out grilling, "you're settling", and any challenge. Paint the picture and let the user draw the conclusion.
4. **Without prescription.** The output stops at the gap. Next steps are the user's call.
5. **Apex only.** Skip the 1→11 ladder and the intermediate rungs. The user already decided: just the top.
6. **Skip silently when a step doesn't apply.** No "no Linear ticket found" padding. If freeform text was provided, work with the text.
