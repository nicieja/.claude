---
name: code-deslop
version: 3.0.0
description: |
  Strip AI-slop from prose, restoring information density and honesty, without
  changing meaning. Takes text, a prose file, or a PR description. Diagnoses,
  then converges through verify-and-repeat passes until it hits the predicted
  cut or proves the rest is essential, and applies the result. The report says
  what to check and how to undo it. Code comments belong to /code-uncomment.
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

Take text, a prose file, or a PR description and strip its **AI-slop**: prose that has the form of competent writing without the substance. You restore information density and honesty, and you **never change meaning**. Code comments and lint suppressions are `/code-uncomment`'s job.

Slop is *generated-but-not-authored* content: cheap to produce, expensive to read. The fix is to cut the uninformative words and keep the informative ones. A swap of fancy words for plain ones is not a fix. AI-assisted writing that a human shaped and is accountable for is not slop. The target is the abdication of judgment, not the tool.

Prose is diagnosed in two tiers. *Structural* tells are the real target. These are low information density, jargon in place of information, rhetorical postures that promise rigor they don't deliver, redundancy, and hedging that never decides. *Surface* tells (vocabulary, em-dash density, stock cadences) are Vale's job. Run Vale and apply its alerts, then spend your reading on structure.

The method uses the compression test and the convergence loop. The **compression test** is the measure. Try to cut a passage by half without losing meaning. Whatever you can cut was slop, and whatever survives is content. The **convergence loop** is the procedure. Declare a goal, cut, verify against the goal, and repeat until you hit the predicted cut or prove what's left is essential. The loop stops a timid pass from quitting a fraction of the way into a sloppy input.

## Arguments

- `/code-deslop <text>`: deslop the pasted text (prose).
- `/code-deslop <file path>`: read a prose file and deslop it. Diagnose first, then write the result back (Step 5). A code file goes to `/code-uncomment`.
- `/code-deslop <PR number | url | branch>`: fetch the PR with `gh`, then deslop its description. The comments in its diff go to `/code-uncomment`.
- `/code-deslop` (bare): deslop the text or file under discussion. If there's nothing obvious, ask once: "What should I deslop?"
- Steers in plain words. `--surface` / "just the tells" means Vale only: apply its alerts and stop. Skip the estimate and the loop. `--deep` / "go hard" means aggressive structural rework. `--review` / "ask first" stops after the Step 2 diagnosis and waits for the go-ahead.

If a path is under `~/Library/Mobile Documents/` (iCloud) and the Read fails with a permission error, tell the user that the iCloud path is blocked by macOS privacy controls. Ask them to paste the text or point at a non-iCloud copy (e.g. under `~/Documents/…`).

## Cases for another skill

- They want a *claim, proposal, or design* grilled, not the prose edited → `/idea-challenge`.
- They want code reviewed for **bugs or correctness** → `/pr-critique`. Deslop never reads for logic.
- They want code **restructured** or dead code removed → `/simplify` or `/code-refactor`.
- They want **code comments or lint suppressions** cut → `/code-uncomment`.

## Instructions

Follow in order. Acting and confirming follow `~/.claude/AGENTS.md` ("When to act and when to confirm"). This skill applies its edits and reports them. It never pushes, and it never edits a PR on GitHub.

### Step 0: Resolve the input

Resolve per **Arguments**: text, file, PR, or bare.

- **File.** Read it. A code file goes to `/code-uncomment`, so say so and stop.
- **PR.** `gh pr view <ref>` for the description. `gh` is read-only here.
- **Bare.** Use the obvious draft/file in the conversation. If none, ask once and wait.

### Step 1: Load the guide

Read `~/.claude/skills/code-deslop/slop-guide.md` in full **before diagnosing**. It contains the marker taxonomy and the worked before/after examples. Load it every run, because it is the file tuned over time. Don't work from memory.

### Step 2: Declare the goal and diagnose

Scan the input and build the diagnosis. **Do not edit yet.**

**Declare the goal: a cut estimate.** From a fast read, predict how much is cuttable, as a **range plus where it concentrates**. For prose: "this reads ~25 to 40% cuttable, mostly the intro and the three hedging paragraphs". This is the goal the loop in Step 3 converges toward. It is a prediction the loop verifies against, **never a quota you flatten specificity to hit** (see the guide's "Estimating the cut" and Key Rules 10 and 11). Skip the formal estimate on trivially short inputs, because a sentence or two doesn't need a percentage.

**Run Vale.** It is responsible for surface tells (vocabulary, em-dash density, stock cadences, sign-offs), so you don't hunt those by hand. For a file: `vale --no-exit <path>`. For pasted text or a PR description, pass it on stdin as Markdown: `vale --no-exit --ext=.md <<'EOF' … EOF`. A clean Vale run is not a clean text, and forty alerts are not a cut estimate. The estimate above came from your read, and the compression test runs either way. Alerts from `deslop.Posture` and the `ai-tells` hedging and attribution rules point at structural tells. They go to the Structural bucket as leads, and the fix is backing or dropping the claim rather than rewording it.

Then build the itemized diagnosis, and **state the passages you're targeting** so each pass has concrete aim:

Find the structural tells. Vale's alerts form the bucket for surface tells. Run the compression test on the longest and densest passages. That test, not vocabulary, is the headline.

**Reconcile** the estimate against the itemized findings before presenting. If the listed cuts total much less than the predicted range, either the prediction was inflated or the scan missed slop. Resolve it now, before editing. That delta is the first turn of the loop, done on paper.

Print the diagnosis, goal first and then the specifics:

- A few prose findings as **before/after** pairs drawn from their actual text (quote → tightened → one-line why).
- Surface, from Vale: one line per distinct check, such as `OverusedVocabulary ×4: delve, leverage, tapestry, testament`. Skip the pairs, because the fix is mechanical.

Then continue to Step 3 without waiting. The user can interrupt to correct a verdict or to veto a change. With the `--review` steer, stop here and wait for the go-ahead instead.

### Step 3: Converge (pass, verify, repeat)

With the goal declared, work the input in passes until it converges. For file input, make the backup before Pass 1, because the passes edit the file: if it has uncommitted changes or isn't tracked, copy it to the backup path in `~/.claude/AGENTS.md`. **Do not stop at the first pass.**

**Pass N (apply).** Cut the slop the diagnosis identified. Structural fixes come first, and surface polish last and light. Preserve every fact and claim. Where a plain rewrite would require knowing whether a jargon claim is *true*, **flag it for the author and do not fabricate a confident paraphrase.**

Pass 1 hits the passages identified in Step 2. Later passes hit whatever verification reveals.

**Verify N (measure against the goal).** Tally the cut so far, then re-run the compression test on what now remains. One of three things is true:

- **Converged.** The cut has reached the goal range and meaning is intact. Exit the loop.
- **Short, and slop remains.** The gap comes from a timid or incomplete pass rather than from a dense input. State the passages that still contain slop and run **Pass N+1** aimed at them. This case is the reason the loop exists. A 6% cut on a 30%-sloppy input does not get to stop here.
- **Short, but the remainder is essential content.** The prediction was high, and what's left is specific and real (the inverse failure in the guide). **Revise the goal down and record why** ("the body was denser than the intro implied"), then exit. This is the *justify* exit, the only honest way to finish below the prediction.

**Cap at ~3 passes.** If it still hasn't converged, stop and say so plainly: what's left, and why it resisted. Don't spin or pad the count. The answer can be "this is as tight as it gets," never a faked number.

**Every pass obeys the guardrails.** Meaning remains untouched (Rule 3), and **don't-over-compress wins every tie** (Rule 7): the loop may never flatten specificity to chase the goal. Its only two exits are *converged* and *justified*. "I tried, the gap is just a finding" is not an exit.

### Step 4: Self-check

Once the loop has converged, reread the result against the **original** (the whole input, not just the last pass's diff):

- **Meaning intact?** Check that no fact changed, that no claim was invented, and that no real distinction was lost across the passes while "tightening."
- **Not over-compressed?** Dense-but-real content (specific and essential) is not slop. Make sure no pass flattened it into vagueness.
- **Did the loop exit cleanly?** It ended on *converged* or *justified*, and a timid stop presented as a finding does not count.
- **Vale clean?** Re-run it on the result. Any alert left is one you can defend, such as a term the author uses on purpose or a dash the sentence depends on. State each one in Step 5's close.

Fix anything that fails, silently.

### Step 5: Output

- **Text input:** print the deslopped prose in a fenced code block with a short lead-in ("Deslopped:").
- **File input:** the passes already wrote the result to the file, so confirm the path. The backup from Step 3 is the Undo source. Print instead if the user asked for that, and leave the file unchanged.
- **PR input:** print the deslopped description in a fenced code block. Updating the PR itself (`gh pr edit`) is a post, so it follows the outward rule in `~/.claude/AGENTS.md`.

Report **how the loop converged**, not a bare gap. Give the percent reduced over N passes against the goal. State which exit it took: *met the goal* ("converged at ~28% over 2 passes; goal was 25 to 40%") or *justified the shortfall* ("revised the goal to ~8% after pass 2 because the body was essential", followed by the reason). A shortfall is reportable only once it's been justified in the loop, and it is never a substitute for the pass you didn't run.

Close with **one honest line** separating *cosmetic* from *substantive* changes. If a passage is empty (form with no substance to recover), say so plainly. Deslop can tighten prose but cannot supply judgment that was never there.

The convergence report above is the Changed part. End with **Check** and **Undo**. Check lists each passage where the meaning could have shifted, and each jargon claim flagged for the author. Undo is the command that restores the original, such as `git restore <file>` or `cp <backup> <file>`. Printed text and a PR description don't need an Undo.

## Key Rules

1. **Diagnose before the first pass, then apply.** Print the diagnosis and continue. The report says what to check and how to undo it.
2. **The compression test is the measure.** Lead with structure and treat surface tells as cosmetic.
3. **Never change meaning.** Preserve every fact and claim. Flag unverifiable jargon instead of faking a plain version.
4. **Jargon density is not information density.** Specific-sounding nouns are not the same as transferred understanding.
5. **Prose only.** Code comments and lint suppressions go to `/code-uncomment`.
6. **Be honest about cosmetic vs substantive.** Never sell a vocabulary swap as a substance fix.
7. **Don't over-compress.** Real machinery (specific and essential) remains, even when it reads dense.
8. **Surface tells are Vale's job.** Its alerts are input. Treat them as neither proof of authorship nor the headline. Fix them last and light.
9. **Load `slop-guide.md` every run.** The taxonomy and examples are in that file, not in memory.
10. **The cut estimate is a prediction the loop verifies, never a target you flatten to hit.** Range over point, location over total. An *unexplained* shortfall means another pass. You may finish below the prediction only by proving the remainder is essential and revising the estimate down with that reason. Judgment wins every tie: treat the skill's own number with the suspicion it aims at em-dash counts.
11. **Converge, and don't report-and-shrug.** Loop pass→verify until the goal is met or the remainder is proven essential. Cap at ~3 passes, then stop and say so. The only exits are *met* and *justified*. A timid pass that quits short and calls the gap "a finding" is the failure this skill exists to prevent.
