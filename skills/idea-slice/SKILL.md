---
name: idea-slice
version: 1.0.0
description: |
  Slice an epic, a feature, or a plan into stories that each deliver value on
  their own. Starts from the outputs and the behavior change, narrows the segment
  and the role, maps the whole customer experience, and groups the slices into
  milestones with descriptive names. Every story states the behavior change, the
  system change, and the demo that proves it. Ends with a hand-off to
  /idea-challenge.
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

# Slice

Turn a big intention into a sequence of stories. The unit of delivery is the story. Bad stories produce features that can't be evaluated, can't be sliced, and can't be killed. The most common iteration failure is delivering pieces that only add value when they all come together at the end. That is Frankenstein iteration rather than real iteration, and this skill exists to prevent it.

## Arguments

- `/idea-slice <epic | plan path | ticket | URL>`: slice that work.
- `/idea-slice` (bare): slice the work under discussion. If there is none, ask once: "What should I slice?"
- Steers in plain words: "just the first milestone" (slice until the first milestone is clear, then stop).

## Cases for another skill

- A half-formed idea that needs research and a build plan → `/idea-spec`.
- A goal to make measurable, or a build, rank, launch, or kill call → `/idea-goal`.
- A proposal that needs grilling → `/idea-challenge`.
- Tracker issues already shaped and ready to build → `/work-triage`.

## Report mode

When the `reviewer` agent loads this skill from a brief, there is no user to ask. Slice from the material in the brief. Each question you would ask becomes a listed gap, and the output follows the format the brief defines.

## Instructions

Follow these steps in order. One question per AskUserQuestion call.

### Step 0: Capture the work

Read the epic, plan, or ticket. Read the code it touches only when a slice depends on what already exists. State the work in one sentence before slicing.

### Step 1: Start with the outputs

The value of a system is in its outputs, not its inputs. Define what comes out before you design what goes in. Then **identify the behavior change**: every story states what user behavior shifts when it is released. The behavior change is what makes the story measurable from a business perspective. If you can't state it, the story isn't ready.

### Step 2: Narrow the segment and the role

- **Pick a specific role, not "the user."** Generic roles produce generic stories. The role should be narrow enough that you can imagine one real person in it.
- **Narrow the segment ruthlessly.** Give 2% of users 100% of what they need before you give 100% of users 2% of what they need.
- **Play devil's advocate.** Challenge expressed needs and roles before believing them. Users misreport reasons, and internal proxies fabricate. Asking for something is free. Research can disprove a need in a day. A build can take weeks to disprove the same need.

### Step 3: Map the whole customer experience

The customer experience starts and ends outside the software. Map it end to end, not just the screen. A story map catches the steps you'd otherwise skip.

### Step 4: Slice

- **Slice by value, not technique.** Divide work by value first, then look for useful technical chunks. Never do the reverse. Each slice should be demonstrably valuable on its own.
- **State the system change.** Delineate scope explicitly so engineers and stakeholders share one picture of what's in.
- **Stay in your zone of control, and aim at your sphere of influence.** Deliverables belong in your zone of control. User needs and outcomes belong in your sphere of influence. Don't commit to outputs you can't deliver, or hide behind outcomes you can't measure.
- **Imagine the demo before you build.** Write down how you'll show the requirement was met. If you can't picture the demo, the story isn't ready.
- **Divide responsibility for definition.** Stakeholders express the need, and people who can design the software express the solution. Collapsing the two produces tech-led features users don't want, or stakeholder-led specs engineers can't build.

### Step 5: Simplify and separate the risks

- **Simplify outputs.** Investigate whether outputs can be reduced or postponed to de-risk the short-term plan.
- **Time-box major risks.** Manage risk-driven and deadline-driven stories separately so they don't turn into emergencies. Strike the balance between short-term wins and long-term sustainability.

### Step 6: Group into milestones

- **Use purpose alignment.** Split work by what the business needs from it:
  - *excel*: must outperform
  - *good enough*: be adequate, and go no further
  - *partner*: outsource where someone else can do it for you
  - *basics*: do the minimum without dropping the ball

  Don't pour excellence into a "good enough" item.
- **Give each milestone a descriptive name.** "Q3 release" is not a name. A name like "first power-user can complete the workflow without support" is one. Stakeholders give priority to what they can describe.
- **Limit each milestone to a few user segments.** A milestone that serves everyone serves no one. It produces generic stories and creeping scope.
- **Instead of "no," say "not now."** Negotiate the sequence of delivery instead of refusing the request.

### Step 7: Deliver

For each milestone, give its name and its segments. For each story in it:

- **Role**: the specific person.
- **Behavior change**: what they do differently after release.
- **System change**: what's in scope.
- **Demo**: how you'll show it works.
- **Purpose**: excel, good enough, partner, or basics.

List the stories that wait for a later milestone, with one line each on why. Then close with one line: *"Take this to `/idea-challenge` next."*

## Key Rules

1. **Every slice delivers value on its own.** A slice that adds value only after the others are released is Frankenstein iteration.
2. **Every story states its behavior change.** A story without one isn't ready.
3. **A specific role, never "the user."**
4. **Picture the demo before the build.** A story without a demo isn't ready.
5. **Milestones have descriptive names and few segments.**
6. **Say "not now" in place of "no."** Sequence the request instead of refusing it.
7. **Report mode never asks.** A question becomes a listed gap.
