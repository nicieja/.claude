---
name: idea-primitive
version: 1.1.0
description: |
  Review a design, plan, RFC, or diff for the concept underneath the feature.
  Asks first whether the change adds a new primitive or composes existing
  ones, and sets the scrutiny by the answer. Models the primitive (a checklist,
  a ledger) instead of the feature named in the request, and builds only its
  smallest version. Ends with findings on one severity scale and a verdict.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - Skill
---

# Primitive

Feature requests arrive named after the feature: *"build an onboarding module."* This skill checks a design, a plan, or a diff for the concept underneath that feature, which may be broader than the feature itself. The same check sets the depth of the review: composition of existing primitives gets a fast pass, and a new or altered primitive gets the slow review.

## Arguments

- `/idea-primitive`: review the design or proposal under discussion in the conversation.
- `/idea-primitive <path | PR | branch>`: review the plan file or design doc at the path, or the diff of the PR or branch.
- `/idea-primitive <text>`: review the proposal in the argument.
- **Report mode.** When the `reviewer` agent loads this skill from a brief, the brief is the whole input. Each question that would go to the user becomes a listed gap, and the output uses the format that the brief specifies.

## Cases for another skill

- The claim needs grilling for evidence, such as demand, the status quo, or "this won't scale" → `/idea-challenge`.
- The diff needs a full review for correctness → `/pr-critique`.
- A half-formed idea needs a plan → `/idea-spec`.
- A claim about live data, row counts, or query plans needs proof → `/production-query`.

## Instructions

### Step 0: Collect the context

Pull the system context. That means the purpose and the scale targets, the constraints and deadlines, the team, and what the design is supposed to accomplish. Read the design artifacts (docs, diagrams, ADRs) and the code that puts them into practice or surrounds them. In report mode, take the context from the brief only.

### Step 1: Ask the first question

Before any other finding, answer one question: **is this a new primitive, or a new composition of old ones?**

- A change that only composes existing primitives should pass fast. That's the payoff, since developers move quickly on solved concepts.
- A change that introduces a new primitive, or materially alters one, gets the slow review. Force alignment, and treat the change the way an architectural guild would treat a change to the foundations.

### Step 2: Find the primitive

The move is to stop and ask whether the feature is the concept or one instance of a broader one. Onboarding is a **checklist** of tasks bound to a context. A checklist also covers offboarding and security reviews, and others no one has asked for yet. Model the primitive (checklist) and not the feature (onboarding).

This is *just enough design*. Naming the broader concept leaves the system open to uses you weren't asked for, while you still build only what today's feature needs. The aim is to be **open to possibilities later, without predicting them up front.** If onboarding remains the only thing that ever touches checklists, you lost almost nothing. If a second use appears, it is cheap, because a primitive is loosely coupled almost by definition: it was modeled as a concept rather than a workflow.

Hold this in tension with the flexibility question in `/idea-challenge`. It is not a license to build the abstraction now. *Finding the primitive* is choosing the right name and altitude for a concept, which is nearly free. *Speculative generality* is building machinery for an unnamed future, which is the debt pushback exists to stop. Find the primitive, then build the smallest version of it. If the only honest name for the concept is the feature itself, that's your answer. Don't invent a primitive to feel clever.

This is also the reply to microservice sprawl. Microservices buy loose coupling by making everything separate, but they let a team skip domain modeling entirely. The bill arrives later as duplication, poor discoverability, and complexity. Primitives are deployment-agnostic: keep them in the monolith, and extract them to services when there's a concrete reason. The heuristic models the domain and not the topology.

### Step 3: Challenge the module named after a feature

When the proposal says *"let's build an `X` module"* or *"an `X` service"*, ask whether `X` is the concept or one instance of it. Find the primitive underneath, such as a checklist, a ledger, or an audit trail, and model that. A module named after today's feature draws its boundary around the request instead of the domain.

Other hand-waving ("this won't scale", "more flexible", "cleaner") gets the pushback patterns in `/idea-challenge`. Its anti-sycophancy rules apply to every review here, before you endorse any architectural change. When a proposal deserves deep interrogation, run that skill, and ask Q5 (Observation & Surprise) and Q6 (Future-fit) whatever the stage routing selects. Reading the architecture tells you what *could* happen, and production data tells you what *did*. "We'll need this when we scale" is a tide every system rises with.

### Step 4: Check the choices around the primitive

Read `~/.claude/skills/idea-primitive/design-guide.md` first. Settle the primitive with its decision table and contract sketch, and check each name the change adds against its naming rules.

- **Boundaries and coupling.** Where do services or modules start and stop? Responsibilities split along business capability, or along technical convenience? Flag places where coupling exceeds cohesion. A boundary that "happens to work" hasn't been tested by a real change yet.
- **Data.** Which component holds the source of truth, the consistency model, and the migration path when the schema changes. The data model is harder to change than the code, so review a schema change or a public API with more care.
- **Scale.** Not "what if we 10x" but "what does the slowest path do at today's p99 plus 50%?"
- **Tech choices.** Weigh maturity, community size, team familiarity, licensing, lock-in, and exit cost. A boring proven tool is usually better than an exciting new one, unless the exciting one solves a constraint the boring one can't, and you can state that constraint.
- **Modernization.** When the change replaces legacy code or proposes a migration (a new framework, datastore, or service), weigh strangler-fig, branch-by-abstraction, parallel-run, and UI-first modernization. Pick by the cost of being wrong, not the cost of being slow.
- **Live data.** A finding that rests on runtime state (row distributions, query plans, lock behavior) is a hypothesis. Send it to `/production-query` when it would change the verdict or a severity, or give it the `Unverified —` prefix and state what would confirm it. `/production-query` ("Verification discipline for reviews") defines the full rule.

### Step 5: Compare with what good looks like

Run the guide's red flags against the design first, then compare it with this list.

- Boundaries follow business capabilities, not technical accidents.
- Features are composed from reusable primitives. A module named after one feature is a smell rather than a structure.
- Each major decision has a documented why (an ADR or equivalent), with the alternative considered.
- Failure modes are explicit and tested, not left at "it should work".
- The next migration is conceivable, not theoretical.
- Performance and security claims are backed by numbers, not adjectives.

### Step 6: Deliver

Group findings on the shared severity scale:

- **Blocking**: must change before this is released. Give the file, the line, and the exact change. Map each blocker to a concrete failure mode in production terms (page volume, error rate, lost data, security exposure).
- **Should fix**: real risk, not gating. Provide the change, the reason, and the tradeoff it costs.
- **Suggestion**, prefixed `Optional:`: an improvement or a future-fit idea, with no weight in the verdict.
- **Praise**: a primitive found well, or a composition that reuses one cleanly.

Avoid diluting the list with cosmetic items. If a finding can't be tied to a real failure mode or a measurable improvement, demote it.

End with a verdict. Either the change can go out as it is or after the blockers are fixed, or it needs rework before re-review. Don't equivocate. In report mode, list the open questions as gaps after the verdict.

## Key Rules

1. **Ask "new primitive or new composition?" first.** The answer sets the scrutiny.
2. **Model the primitive, and build its smallest version.** Choosing the name is nearly free. Machinery for an unnamed future is speculative generality.
3. **Don't invent a primitive to feel clever.** If the only honest name is the feature itself, that's the answer.
4. **Primitives are deployment-agnostic.** They remain in the monolith until a concrete reason calls for a service.
5. **Take a position.** Pair each recommendation with specific evidence and the tradeoff it costs, tie each finding to a failure mode or a measurable improvement, and end the review with a verdict.
6. **Claims about runtime state go through `/production-query`,** or they get the `Unverified —` prefix.
