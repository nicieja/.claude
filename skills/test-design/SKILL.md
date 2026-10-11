---
name: test-design
version: 1.0.0
description: |
  Decide what to test and why, then write tests that protect the behaviors users
  depend on. Takes a diff, a feature, a file, or a suite. Starts from capabilities,
  always/never statements, and the user-state paths, weights the work by risk, and
  proves each test with a red-then-green run before trusting it. Also rules Keep or
  Cut on tests that already exist, which is how /test-prune uses it.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Skill
---

# Test design

Choose what to test, write the tests, and prove that each one can fail. Testing is one job here: the choice of *what to test and why* and the automation that runs it come from the same pass. Splitting them produces strategy that ignores what's buildable and automation that protects the wrong things.

Load `test-guide.md` (next to this file) at the start of every run. It holds the heuristics that every step below applies.

## Arguments

- `/test-design` (bare): the current diff, `git diff HEAD`. If the tree is clean, the feature or file under discussion. If neither, ask once: "What should I design tests for?"
- `/test-design <file | feature | PR | branch>`: design tests for that target. For a PR or branch, the target is the behavior its diff adds.
- `/test-design suite [path]`: audit an existing suite and find its highest-leverage gap.
- Steers in plain words: `report` / "just tell me" (design and rule, and don't write a file).

## Cases for another skill

- Tests a slice added past what its behavior needs → `/test-prune`. That skill sends this one to the `reviewer` agent for its rulings.
- Guards for states no caller can produce → `/code-simplify`.
- A whole diff read for correctness → `/pr-critique`.
- A claim about live data or the current state of production → `/production-query`.

## Report mode

The `reviewer` agent loads this skill from a brief, and `/test-prune` is the main caller. In report mode:

- Edit no file. Rule and report only.
- Use the output format that the brief defines. For `/test-prune`, that is one row per test with a Keep or Cut ruling, and the run goes from Step 0 straight to Step 4.
- A question you would ask the user becomes a listed gap in the report.

## Instructions

Follow these steps in order. When the brief requests Keep or Cut rulings, run Step 0 and then Step 4 only. Any other report-mode run stops after Step 3.

### Step 0: Resolve the target

Per **Arguments**. Read the non-test part of the diff or the feature code first. The tests are judged against the behavior it adds.

### Step 1: Pull the testing context

- The domain, and what's at stake when this code is wrong.
- The current suite structure and size, and the conventions in the test code.
- The runner config and the framework choices. Conventions and framework choices reveal more than test counts.
- Recent defects, and the stage that missed each one.
- Pain points in CI.

### Step 2: Find the highest-leverage gap

Pick one of these and address it first:

- **Design**: the suite tests the wrong things.
- **Build**: the tests are slow, flaky, or unreadable.
- **Strategy**: there is no clear bar for "done".

Address one gap at a time. Map the effort to risk (consequence × likelihood), never to lines of code.

### Step 3: Design the tests

Apply `test-guide.md`, "Designing tests":

1. Draw the trust boundary first. For each neighbor of the change (an adjacent team's code, a third party, an upstream service), state how much you trust it. Then write checks inside the boundary. A check on a third party is a contract assertion.
2. List the capabilities the change gives users, and what it prevents them from doing.
3. Write the always/never statements.
4. Walk the user-state paths, and keep the ones that a caller of this change can produce. An input that crosses a system boundary (user input, an external response, a queue payload) can always be produced, so the delinquent, greedy, and stressful paths apply to it.
5. Pick the key examples and their counter-examples.
6. State what each test proves, in user-visible terms, before any code.

When a feature has dozens of edge cases, stop and raise the model problem before writing more tests.

### Step 4: Rule on existing tests (when asked)

When the target already has tests, or the brief requests Keep or Cut rulings, apply "Judging a test that already exists" in `test-guide.md` to each test. Rule Keep or Cut. Each Keep states the behavior it protects in one line. Each Cut gives the kept test that already covers the same behavior, or the reason the behavior doesn't need a test. A Keep/Cut brief ends here and returns its rows.

### Step 5: Write the tests

One topic per test, assertions first, with technical and business checks in separate tests. Follow "Building the automation" in the guide and the conventions of the surrounding suite.

### Step 6: Verify each test before trusting it

A test you haven't seen fail is a test you don't trust. Green-on-first-run is the failure mode this step exists to prevent. It usually means that the test asserts something that's already true, that the assertion never runs, or that the test is wired to the wrong code path.

**For a regression test (a bug just got reported):**

1. Run the test against the **un-fixed code** (revert the fix, stash it, or check out the pre-fix commit). The test must FAIL, and the failure message must match the symptom from the bug report. If it passes, the test is testing something other than the bug. Rewrite it before continuing.
2. Apply the fix. Run the test. It must PASS.
3. If you couldn't get step 1 to fail, do not merge the test. A regression test that's green against the broken code protects nothing.

**For a test of new behavior (TDD or after-the-fact):**

1. Write the assertion first. Run it against code that does NOT yet contain the behavior. Confirm it fails for the right reason, and not because of a missing import, a typo, or a fixture that doesn't exist. The failure message should describe the missing behavior, not the missing infrastructure.
2. Write the code for the behavior. Run the test. It must PASS.
3. A test that's green before the code exists is testing the framework, not the code.

**For a test of existing behavior (backfilling coverage):**

1. Run the test as written. If green, you've confirmed the behavior, but you haven't confirmed the test catches a regression.
2. Mutate the production code under test (flip a boolean, comment out a branch, or change `==` to `!=`). Run the test. It must FAIL on the mutation.
3. Restore the production code. The test must PASS.
4. If the mutation didn't break the test, the test isn't testing the line you think it is. Strengthen the assertion or pick a different mutation that the test should catch.

**Skip this loop only when** the test is intrinsically a tautology (e.g., a snapshot test that locks the current output by design). Document the skip in a comment. Tautology tests have a place, but never lump a regression test in with them.

### Step 7: Deliver

For each finding or automation effort:

- **What's at risk**: the real failure mode, not a generic concern.
- **Probability**: any signal from prod, history, or analogous systems.
- **What "addressed" looks like**: a concrete bar (e.g., "p95 of order-flow has unit + integration coverage and a smoke test in CI").
- **Cost to fix**: engineering hours and infra cost, plus the ongoing maintenance footprint.

For each delivered test, state the behavior it protects, the runtime impact (before and after), the flake risk and what prevents it, and the changes elsewhere that would force a change here. For a regression test, also give the red-then-green proof: the failure message against the un-fixed code (or the mutation) and the pass against the fix. A regression test delivered without that proof is only a claim.

Group findings on the shared review scale. Blocking is for release-stoppers and Should fix is for real risk. Suggestion is for improvements, with `Nit:`, `Optional:`, or `FYI:`. Praise is for a test or a suite decision that is done well. Don't dilute the list.

End with a verdict on the suite or the release: trustworthy, recovering, or rotting. Or green, yellow with named risks, or red with named blockers. Then state the next move.

## Key Rules

1. **A test you haven't seen fail is not trusted.** Every regression test comes with its red-then-green proof.
2. **Protect behavior users depend on.** Don't deliver tests that test the framework or the language.
3. **Risk drives investment.** Effort follows consequence × likelihood, never lines of code.
4. **A flake is a failure.** Quarantine or fix it, and never rerun-and-merge.
5. **Coverage is one signal among several.** Decide what a test is for before choosing its format.
6. **A test for a state no caller can produce is armor.** `~/.claude/AGENTS.md` and `/code-simplify` define the rule, and it applies to tests too.
7. **Report mode never edits.** It rules and reports, and a question becomes a listed gap.
