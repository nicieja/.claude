---
name: deslop
version: 1.0.0
description: |
  Strip AI-slop from prose and code comments, restoring information density and
  honesty, without changing meaning or code logic. Takes text, a file, or a PR.
  Diagnoses first and waits for your call, then converges through verify-and-repeat
  passes until it hits the predicted cut or proves the rest is essential. For
  comments the default is none, and each must justify its place.
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

Take text, a file, or a PR and strip its **AI-slop**: prose that has the form of competent writing without the substance, and code comments that narrate what the code already says. You restore information density and honesty. You **never change meaning, and never change code logic**. You edit only prose and comments.

Slop is *generated-but-not-authored* content: cheap to produce, expensive to read. The fix is to cut the uninformative words and keep the informative ones. A swap of fancy words for plain ones is not a fix. AI-assisted writing that a human shaped and is accountable for is not slop. The target is the abdication of judgment, not the tool.

Prose and code comments are handled differently:

- **Prose** is diagnosed in two tiers. *Structural* tells are the real target. These are low information density, jargon in place of information, rhetorical postures that promise rigor they don't deliver, redundancy, and hedging that never decides. *Surface* tells (vocabulary, em-dash density, stock cadences) are Vale's job. Run Vale and apply its alerts, then spend your reading on structure.
- **Code comments** have one rule: **the default is no comment, and a comment must justify its place.** It justifies its place only by explaining *why* (not *what*). That means a non-obvious decision, a gotcha, an invariant not visible in the code, an external constraint, or a workaround. AI agents over-comment by narrating the obvious. That narration is the prime target.

The method uses the compression test and the convergence loop. The **compression test** is the measure. Try to cut a passage by half without losing meaning. Whatever you can cut was slop, and whatever survives is content. The **convergence loop** is the procedure. Declare a goal, cut, verify against the goal, and repeat until you hit the predicted cut or prove what's left is essential. The loop stops a timid pass from quitting a fraction of the way into a sloppy input.

## Arguments

- `/deslop <text>`: deslop the pasted text (prose).
- `/deslop <file path>`: read the file and deslop it. A prose file gets the prose treatment, and a code file gets the comment treatment. **Diagnose first, and write back only after the checkpoint** (Step 2).
- `/deslop <PR number | url | branch>`: fetch the PR with `gh`, then deslop the description (prose) and rank the comments the diff **adds**. Read-only by default. Never push or post without an explicit ask.
- `/deslop` (bare): deslop the text or file under discussion. If there's nothing obvious, ask once: "What should I deslop?"
- Steers in plain words. `--surface` / "just the tells" means Vale only: run it and show the alerts, then apply them on the go-ahead and stop. Skip the estimate and the loop. `--deep` / "go hard" means aggressive structural rework.

If a path is under `~/Library/Mobile Documents/` (iCloud) and the Read fails with a permission error, tell the user that the iCloud path is blocked by macOS privacy controls. Ask them to paste the text or point at a non-iCloud copy (e.g. under `~/Documents/…`).

## Cases for another skill

- They want a *claim, proposal, or design* grilled, not the prose edited → `/pushback`.
- They want code reviewed for **bugs or correctness** → `code-reviewer`. Deslop never reads for logic.
- They want code **restructured** or dead code removed → `code-simplifier` / `/simplify`. Deslop prunes comments and prose without refactoring.

## Instructions

Follow in order.

### Step 0: Resolve the input

Resolve per **Arguments**: text, file, PR, or bare.

- **File.** Read it. Decide prose vs code from the file extension and the content.
- **PR.** `gh pr view <ref>` for the description and metadata, `gh pr diff <ref>` for the diff. Note whether the PR's branch is the current local checkout. That decides whether Step 5 can edit files or only report. `gh` is read-only here: do not push or post a review without an explicit ask.
- **Bare.** Use the obvious draft/file in the conversation. If none, ask once and wait.

### Step 1: Load the guide

Read `~/.claude/skills/deslop/slop-guide.md` in full **before diagnosing**. It contains the marker taxonomy, the comment rubric, and the worked before/after examples. Load it every run, because it is the file tuned over time. Don't work from memory.

### Step 2: Declare the goal and diagnose, then stop

Scan the input and build the diagnosis. **Do not edit yet.**

**Declare the goal: a cut estimate.** From a fast read, predict how much is cuttable, as a **range plus where it concentrates**. For prose: "this reads ~25 to 40% cuttable, mostly the intro and the three hedging paragraphs". For comments: "~6 of 9 added comments look cuttable." This is the goal the loop in Step 3 converges toward. It is a prediction the loop verifies against, **never a quota you flatten specificity to hit** (see the guide's "Estimating the cut" and Key Rules 10 and 11). Skip the formal estimate on trivially short inputs, because a sentence or two doesn't need a percentage.

**Run Vale.** It is responsible for surface tells (vocabulary, em-dash density, stock cadences, sign-offs), so you don't hunt those by hand. For a file: `vale --no-exit <path>`. For pasted text or a PR description, pass it on stdin as Markdown: `vale --no-exit --ext=.md <<'EOF' … EOF`. For PR comments with the branch checked out: `vale --no-exit $(gh pr diff <ref> --name-only)`, keeping only alerts on lines the diff adds. A clean Vale run is not a clean text, and forty alerts are not a cut estimate. The estimate above came from your read, and the compression test runs either way. Alerts from `deslop.Posture` and the `ai-tells` hedging and attribution rules point at structural tells. They go to the Structural bucket as leads, and the fix is backing or dropping the claim rather than rewording it.

Then build the itemized diagnosis, and **state the passages you're targeting** so each pass has concrete aim:

- **Prose:** find the structural tells. Vale's alerts form the bucket for surface tells. Run the compression test on the longest and densest passages. That test, not vocabulary, is the headline.
- **Comments (code file or PR diff):** rank each comment **Keep / Cut / Borderline** against the justify-its-place rubric. Bias to Cut, because the default is no comment.

**Reconcile** the estimate against the itemized findings before presenting. If the listed cuts total much less than the predicted range, either the prediction was inflated or the scan missed slop. Resolve it now, before editing. That delta is the first turn of the loop, done on paper.

Present the diagnosis, goal first and then the specifics, and **stop for the user's input**:

- A few prose findings as **before/after** pairs drawn from their actual text (quote → tightened → one-line why).
- Surface, from Vale: one line per distinct check, such as `OverusedVocabulary ×4: delve, leverage, tapestry, testament`. Skip the pairs, because the fix is mechanical.
- For comments, a compact table: `comment · verdict · one-line reason`.

Let the user interject, correct a verdict, adjust the goal, or veto a change. This checkpoint is the point of the skill, and the diagnosis is a proposal that is still open to change. It is also the **only** gate: once you have the go-ahead, Step 3 runs to convergence on its own.

### Step 3: Converge (pass, verify, repeat)

With the goal declared and the go-ahead given, work the input in passes until it converges. **Do not stop at the first pass.**

**Pass N (apply).** Cut the slop the diagnosis identified:

- **Prose:** structural fixes first, surface polish last and light. Preserve every fact and claim. Where a plain rewrite would require knowing whether a jargon claim is *true*, **flag it for the author and do not fabricate a confident paraphrase.**
- **Comments:** delete the Cut ones and reword Borderline into a real *why* (or delete them). Keep the comments that matter. **Never change code logic.** Change only comments.

Pass 1 hits the passages identified in Step 2. Later passes hit whatever verification reveals.

**Verify N (measure against the goal).** Tally the cut so far, then re-run the compression test on what now remains. One of three things is true:

- **Converged.** The cut has reached the goal range and meaning is intact. Exit the loop.
- **Short, and slop remains.** The gap comes from a timid or incomplete pass rather than from a dense input. State the passages that still contain slop and run **Pass N+1** aimed at them. This case is the reason the loop exists. A 6% cut on a 30%-sloppy input does not get to stop here.
- **Short, but the remainder is essential content.** The prediction was high, and what's left is specific and real (the inverse failure in the guide). **Revise the goal down and record why** ("the body was denser than the intro implied"), then exit. This is the *justify* exit, the only honest way to finish below the prediction.

**Cap at ~3 passes.** If it still hasn't converged, stop and say so plainly: what's left, and why it resisted. Don't spin or pad the count. The answer can be "this is as tight as it gets," never a faked number.

**Every pass obeys the guardrails.** Meaning and code logic remain untouched (Rule 3), and **don't-over-compress wins every tie** (Rule 7): the loop may never flatten specificity to chase the goal. Its only two exits are *converged* and *justified*. "I tried, the gap is just a finding" is not an exit.

### Step 4: Self-check

Once the loop has converged, reread the result against the **original** (the whole input, not just the last pass's diff):

- **Meaning intact?** Check that no fact changed, that no claim was invented, and that no real distinction was lost across the passes while "tightening."
- **Logic untouched?** For code, you changed only comments.
- **Not over-compressed?** Dense-but-real content (specific and essential) is not slop. Make sure no pass flattened it into vagueness.
- **Was all narration cut, and every real *why* kept?** The comment ledger is accurate.
- **Did the loop exit cleanly?** It ended on *converged* or *justified*, and a timid stop presented as a finding does not count.
- **Vale clean?** Re-run it on the result. Any alert left is one you can defend, such as a term the author uses on purpose or a dash the sentence depends on. State each one in Step 5's close.

Fix anything that fails, silently.

### Step 5: Output

- **Text input:** print the deslopped prose in a fenced code block with a short lead-in ("Deslopped:").
- **File input:** write the result back to the file (the Step 2 checkpoint was the gate), then confirm the path. Print instead if the user preferred.
- **PR, branch checked out:** apply the edits to the working tree (remove cut comments, and tighten the description if it is stored in a file). Do not commit or push. Summarize what changed.
- **PR, not checked out:** print a ranked report (the comment table plus suggested removals) that the user can apply. Offer to post it as PR review comments only if they ask.

Report **how the loop converged**, not a bare gap. Prose gets the percent reduced over N passes against the goal, and comments get N of M cut. State which exit it took: *met the goal* ("converged at ~28% over 2 passes; goal was 25 to 40%") or *justified the shortfall* ("revised the goal to ~8% after pass 2 because the body was essential", followed by the reason). A shortfall is reportable only once it's been justified in the loop, and it is never a substitute for the pass you didn't run.

Close with **one honest line** separating *cosmetic* from *substantive* changes. If a passage is empty (form with no substance to recover), say so plainly. Deslop can tighten prose but cannot supply judgment that was never there.

## Key Rules

1. **Diagnose before you touch a word.** Present findings and let the user correct them. The checkpoint is the skill.
2. **The compression test is the measure.** Lead with structure and treat surface tells as cosmetic.
3. **Never change meaning or code logic.** Preserve every fact and claim. Flag unverifiable jargon instead of faking a plain version.
4. **Jargon density is not information density.** Specific-sounding nouns are not the same as transferred understanding.
5. **Comments default to none, and each must justify its place.** Keep only *why* / gotcha / invariant / external-constraint / workaround. Cut narration of the obvious. AI over-commenting is the prime target.
6. **Be honest about cosmetic vs substantive.** Never sell a vocabulary swap as a substance fix.
7. **Don't over-compress.** Real machinery (specific and essential) remains, even when it reads dense.
8. **Surface tells are Vale's job.** Its alerts are input. Treat them as neither proof of authorship nor the headline. Fix them last and light.
9. **Load `slop-guide.md` every run.** The taxonomy and examples are in that file, not in memory.
10. **The cut estimate is a prediction the loop verifies, never a target you flatten to hit.** Range over point, location over total. An *unexplained* shortfall means another pass. You may finish below the prediction only by proving the remainder is essential and revising the estimate down with that reason. Judgment wins every tie: treat the skill's own number with the suspicion it aims at em-dash counts.
11. **Converge, and don't report-and-shrug.** Loop pass→verify until the goal is met or the remainder is proven essential. Cap at ~3 passes, then stop and say so. The only exits are *met* and *justified*. A timid pass that quits short and calls the gap "a finding" is the failure this skill exists to prevent.
