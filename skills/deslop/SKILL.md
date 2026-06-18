---
name: deslop
version: 1.0.0
description: |
  Strip AI-slop from prose and code comments — restoring information density and
  honesty — without changing meaning or code logic. Takes text, a file, or a PR;
  diagnoses first and waits for your call, then converges through verify-and-repeat
  passes until it hits the predicted cut or proves the rest is load-bearing. Default
  for comments: none, and each must earn its place. Loads slop-guide.md every run.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# Deslop

Take text, a file, or a PR and strip its **AI-slop**: prose that has the form of competent writing without the substance, and code comments that narrate what the code already says. You restore information density and honesty. You **never change meaning, and never change code logic** — only prose and comments.

Slop is *generated-but-not-authored* content: cheap to produce, expensive to read. The fix is not swapping fancy words for plain ones; it is cutting what carries no information and keeping what does. AI-assisted writing that a human shaped and stands behind is not slop — the target is the abdication of judgment, not the tool.

Two surfaces, handled differently:

- **Prose** — diagnosed in two tiers. *Structural* tells (the real target): low information density, jargon standing in for information, rhetorical postures that promise rigor they don't deliver, redundancy, hedging that never decides. *Surface* tells (cosmetic, low-confidence): generic AI vocabulary, em-dash overuse, the monotone "not X, but Y" cadence. Lead with structure; surface tells are gameable and unmeasured, never proof.
- **Code comments** — one rule: **the default is no comment, and a comment must earn its place.** It earns it only by explaining *why* (not *what*): a non-obvious decision, a gotcha, an invariant the code doesn't show, an external constraint, or a workaround. AI agents over-comment by narrating the obvious; that narration is the prime target.

Two instruments run the method. The **compression test** measures: try to cut a passage by half without losing meaning — what you can cut was slop, what survives is content. The **convergence loop** drives the work: declare a goal, cut, verify against it, repeat — until you hit the predicted cut or prove what's left is load-bearing. The loop is what stops a timid pass from quitting at 6% on a 30%-sloppy input.

## Arguments

- `/deslop <text>` — deslop the pasted text (prose).
- `/deslop <file path>` — read the file and deslop it. A prose file gets the prose treatment; a code file gets the comment treatment. **Diagnose first; write back only after the checkpoint** (Step 2).
- `/deslop <PR number | url | branch>` — fetch the PR with `gh`; deslop the description (prose) and rank the comments the diff **adds**. Read-only by default; never push or post without an explicit ask.
- `/deslop` (bare) — deslop the text or file under discussion. If there's nothing obvious, ask once: "What should I deslop?"
- Steers in plain words: `--surface` / "just the tells" (cosmetic vocabulary + em-dash pass only), `--deep` / "go hard" (aggressive structural rework).

If a path is under `~/Library/Mobile Documents/` (iCloud) and the Read fails with a permission error, tell the user: the iCloud path is blocked by macOS privacy controls — ask them to paste the text or point at a non-iCloud copy (e.g. under `~/Documents/…`).

## When this is the wrong skill

- They want the prose re-voiced into their own literary voice, or non-native fluency fixed → `/polish`.
- They want a *claim, proposal, or design* grilled, not the prose edited → `/pushback`.
- They want code reviewed for **bugs or correctness** → `code-reviewer`. Deslop never reads for logic.
- They want code **restructured** or dead code removed → `code-simplifier` / `/simplify`. Deslop prunes comments and prose; it does not refactor.
- Compose with `/polish`: **deslop first** (cut the empty, the over-dense, the noise comments), **then polish** (re-voice what remains).

## Instructions

Follow in order.

### Step 0: Resolve the input

Resolve per **Arguments** — text, file, PR, or bare.

- **File:** Read it. Decide prose vs code by extension and content.
- **PR:** `gh pr view <ref>` for the description and metadata, `gh pr diff <ref>` for the diff. Note whether the PR's branch is the current local checkout — that decides whether Step 5 can edit files or only report. `gh` is read-only here; no push, no posted review, without an explicit ask.
- **Bare:** use the obvious draft/file in the conversation; if none, ask once and wait.

### Step 1: Load the guide

Read `~/.claude/skills/deslop/slop-guide.md` in full **before diagnosing**. It holds the marker taxonomy, the comment rubric, and the worked before/after examples. Load it every run — it's the thing tuned over time; don't work from memory.

### Step 2: Declare the goal, diagnose — then stop

Scan the input and build the diagnosis. **Do not edit yet.**

**Declare the goal: a cut estimate.** From a fast read, predict how much is cuttable — as a **range plus where it concentrates**: prose → "this reads ~25–40% cuttable, mostly the intro and the three hedging paragraphs"; comments → "~6 of 9 added comments look cuttable." This is the goal the loop in Step 3 converges toward — a prediction it verifies against, **never a quota you flatten specificity to hit** (see the guide's "Estimating the cut" and Key Rules 10–11). Skip the formal estimate on trivially short inputs — a sentence or two needs no percentage.

Then build the itemized diagnosis, and **name the passages you're targeting** so each pass has concrete aim:

- **Prose:** find the tells, bucketed Structural (priority) and Surface (cosmetic). Run the compression test on the longest and densest passages; that, not vocabulary, is the headline.
- **Comments (code file or PR diff):** rank each comment **Keep / Cut / Borderline** against the earn-its-place rubric. Bias to Cut; the default is no comment.

**Reconcile** the estimate against the itemized findings before presenting: if the named cuts fall well short of the predicted range, either the prediction was inflated or the scan missed slop — resolve it now, not after editing. That delta is the first turn of the loop, done on paper.

Present the diagnosis — goal first, then the specifics — and **stop for the user's input**:

- A few prose findings as **before/after** pairs drawn from their actual text (quote → tightened → one-line why).
- For comments, a compact table: `comment · verdict · one-line reason`.

Let the user interject, correct a verdict, adjust the goal, or veto a change. This checkpoint is the point of the skill — the diagnosis is a proposal, not a fait accompli. It is also the **only** gate: once you have the go-ahead, Step 3 runs to convergence on its own.

### Step 3: Converge — pass, verify, repeat

With the goal declared and the go-ahead given, work the input in passes until it converges. **Do not stop at the first pass.**

**Pass N — apply.** Cut the slop the diagnosis named:

- **Prose:** structural fixes first, surface polish last and light. Preserve every fact and claim. Where a plain rewrite would require knowing whether a jargon claim is *true*, **flag it for the author — do not fabricate a confident paraphrase.**
- **Comments:** delete the Cut ones, reword Borderline into a real *why* (or delete), keep the crucial. **Never change code logic** — only comments.

Pass 1 hits the passages named in Step 2; later passes hit whatever verification surfaces.

**Verify N — measure against the goal.** Tally the cut so far, then re-run the compression test on what now remains. One of three things is true:

- **Converged** — the cut has reached the goal range and meaning is intact. Exit the loop.
- **Short, and slop remains** — the gap is a timid or incomplete pass, not a dense input. Name the passages still carrying slop and run **Pass N+1** aimed at them. This is the case the loop exists for: a 6% cut on a 30%-sloppy input does not get to stop here.
- **Short, but the remainder is load-bearing** — the prediction was high; what's left is specific and real (the inverse failure in the guide). **Revise the goal down, record why** ("the body was denser than the intro implied"), and exit. This is the *justify* exit — the only honest way to finish below the prediction.

**Cap at ~3 passes.** If it still hasn't converged, stop and say so plainly — what's left, and why it resisted — rather than spin or pad the count. (Same honesty as `/estimate` capping its break-down: the answer can be "this is as tight as it gets," never a faked number.)

**Every pass obeys the guardrails.** Meaning and code logic stay untouched (Rule 3), and **don't-over-compress wins every tie** (Rule 7): the loop may never flatten specificity to chase the goal. Its only two exits are *converged* and *justified* — never "I tried, the gap is just a finding."

### Step 4: Self-check

Once the loop has converged, reread the result against the **original** — the whole input, not just the last pass's diff:

- **Meaning intact?** No fact changed, no claim invented, no real distinction lost across the passes while "tightening."
- **Logic untouched?** For code, you changed only comments.
- **Not over-compressed?** Dense-but-real content (specific, load-bearing) is not slop; no pass flattened it into vagueness.
- **No narration kept, no real *why* cut?** The comment ledger is honest.
- **Did the loop exit honestly?** It ended on *converged* or *justified* — not a timid stop dressed up as a finding.

Fix anything that fails, silently.

### Step 5: Output

- **Text input:** print the deslopped prose in a fenced code block with a short lead-in ("Deslopped:").
- **File input:** write the result back to the file (the Step 2 checkpoint was the gate), then confirm the path; or print if the user preferred.
- **PR, branch checked out:** apply the edits to the working tree (remove cut comments; tighten the description if it lives in a file). Do not commit or push. Summarize what changed.
- **PR, not checked out:** print a ranked report — the comment table plus suggested removals — that the user can apply. Offer to post it as PR review comments only if they ask.

Report **how the loop converged**, not a bare gap — prose: percent reduced over N passes against the goal; comments: N of M cut. State which exit it took: *met the goal* ("converged at ~28% over 2 passes; goal was 25–40%") or *justified the shortfall* ("revised the goal to ~8% after pass 2 — the body was load-bearing, here's why"). A shortfall is reportable only once it's been justified in the loop; it is never a substitute for the pass you didn't run.

Close with **one honest line** separating *cosmetic* from *substantive* changes. If a passage is genuinely empty — form with no substance to recover — say so plainly; deslop can tighten prose but cannot supply judgment that was never there.

## Key Rules

1. **Diagnose before you touch a word.** Present findings and let the user correct them. The checkpoint is the skill.
2. **The compression test is the measure.** Lead with structure; treat surface tells as cosmetic.
3. **Never change meaning or code logic.** Preserve every fact and claim. Flag unverifiable jargon; don't fake a plain version.
4. **Jargon density is not information density.** Specific-sounding nouns are not the same as transferred understanding.
5. **Comments: default none; each earns its place.** Keep only *why* / gotcha / invariant / external-constraint / workaround. Cut narration of the obvious. AI over-commenting is the prime target.
6. **Be honest about cosmetic vs substantive.** Never sell a vocabulary swap as a substance fix.
7. **Don't over-compress.** Real machinery — specific and load-bearing — stays, even when it reads dense.
8. **Surface tells are weak.** Em dashes, AI vocabulary, and the "not X, but Y" cadence are gameable, false-positive-prone, and unmeasured. Light polish, never proof, never the headline.
9. **Load `slop-guide.md` every run.** The taxonomy and examples live there, not in memory.
10. **The cut estimate is a prediction the loop verifies, never a target you flatten to hit.** Range over point, location over total. An *unexplained* shortfall means another pass; you may finish below the prediction only by proving the remainder is load-bearing and revising it down with that reason. Judgment wins every tie — treat the skill's own number with the suspicion it aims at em-dash counts.
11. **Converge; don't report-and-shrug.** Loop pass→verify until the goal is met or the remainder is proven load-bearing — cap at ~3 passes, then stop honestly. Two exits only: *met* or *justified*. A timid pass that quits short and calls the gap "a finding" is the failure this skill was rebuilt to prevent.
