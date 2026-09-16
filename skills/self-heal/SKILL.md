---
name: self-heal
version: 1.1.0
description: |
  Sweep the prompt library (every skill, command, and agent, self-heal
  included) for accretion debt: the redundancy, bolt-on seams, duplicate
  rules, and tonal drift that build up when files are edited by stapling new
  instructions into convenient spots. Opens sweeps with a transcript usage
  audit that flags dead artifacts and asks which to remove. Ranks the worst,
  then, on your pick and diagnose-first, re-integrates a file from scratch so
  it reads like one author wrote it in one sitting, without regressing any
  baked-in rule. The prompt-library analog of code-simplifier.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
---

# Self-heal

Take the prompt library (every `skills/*/SKILL.md` and its companions, every `commands/*.md`, every `agents/*.md`) and repair its **accretion debt**: the patchwork that builds up when files are edited iteratively, each new instruction stapled wherever was handy. Every addition made local sense. Together the additions turn the file into a changelog. The same rule is restated in three places, parentheticals are bolted on, Key Rules are near-duplicates, cross-references exist only because content was added somewhere else, and sections drift in tone because different sittings wrote them. It still works. It's just harder to read, and the model has more to wade through to follow it.

You **re-integrate**: rewrite the file so it reads like one author wrote it in one sitting. The result is simpler, in one voice, with every instruction stated once in its right home. The contract is that you **never regress behavior**. Most of those bolt-ons were added for a reason, such as a guardrail after something went wrong, an edge case, or a hard-won correction. The win is to remove the patchwork and keep the lessons. Only wording and location are free to change. Every rule, boundary, and edge case the file encoded is preserved.

This is the prompt-library analog of `code-simplifier`, run as periodic maintenance. It inspects in parallel and ranks where debt has piled up. It heals only what you pick. It diagnoses first, you decide, and then it rewrites. It includes its own files in the sweep. The newest skill is often the most accreted.

## Arguments

- `/self-heal` (bare): sweep the whole library (every `skills/*/SKILL.md` and its companions, `commands/*.md`, `agents/*.md`) and rank by accretion debt. Report the ranking. You pick what to heal. **Includes self-heal's own files.**
- `/self-heal <name | path>`: focus one artifact. The target is a skill name (`deslop`), a command, an agent, or a path. Skip the ranking and go straight to diagnose → heal.
- `/self-heal skills | commands | agents`: sweep one type only.
- `/self-heal audit`: run the usage audit (Step 1) alone, then stop. It does not inspect or heal.
- Steers in plain words: `--report-only` / "just rank them" ranks without healing. "Be aggressive" / "be conservative" moves the threshold for what deserves a rewrite. "Skip the audit" goes straight from scope to inspection.

If a path is under `~/Library/Mobile Documents/` (iCloud) and the Read fails with a permission error, tell the user that macOS privacy controls block the iCloud path, and ask them to point at a non-iCloud copy.

## Cases for another skill

- Stripping AI-slop from arbitrary prose or code → `/deslop`. self-heal repairs *structural accretion in the prompt library*, not emptiness in any text.
- Restructuring working *code*, or reviewing a code diff → `code-simplifier` / `code-reviewer`. self-heal only touches prompt markdown. It never reads source for logic.
- It composes with `/deslop` (a heal may tighten sloppy prose inside a file as it goes), but self-heal is the one that sweeps the whole library. It also knows each artifact type's healthy-shape template and preserves a coverage ledger across a from-scratch rewrite.

## Instructions

Follow in order.

### Step 0: Resolve scope

Resolve per **Arguments**.

- **Bare** → the whole library. Enumerate with Glob: `~/.claude/skills/*/SKILL.md` and `~/.claude/skills/*/*.md` (companions), `~/.claude/commands/*.md`, `~/.claude/agents/*.md`.
- **Name or path** → resolve to the file(s) and jump to Step 4.
- **Type word** → that one directory.

Classify each file's **type** as skill, command, agent, or companion guide. Type sets the healthy-shape target in Step 6. Never heal one type toward another's template.

### Step 1: Usage audit

Identify dead weight before polishing it. This step runs on bare and type sweeps. Skip it on single-target runs or when the user says "skip the audit". `/self-heal audit` runs this step alone, then stops.

1. Run `python3 ~/.claude/skills/self-heal/usage-audit.py` with Bash. It scans every transcript under `~/.claude/projects/` (subagent transcripts included) for the three invocation signals (Skill tool calls, typed slash commands, and agent dispatches) and prints, per inventory item: sessions, calls, last-used date, a `DEAD` marker at zero use, and the window start date.
2. For each zero-use item, Grep the library for references from *other* files. An item that live files read or dispatch (an agent that loads a skill's SKILL.md as its spec, a skill whose dispatch prompts invoke it) is **indirect use: keep or consolidate**, never dead.
3. Present the verdicts (dead / dormant / alive) with two caveats stated plainly. The window is bounded by transcript retention (~30 days by default). Cadence-based skills (`/retro` after a completed piece of work, self-heal itself as periodic maintenance) can legitimately sit quiet longer than the window.
4. **Ask which to remove** via AskUserQuestion. Use multiSelect, one question per type (skills / commands / agents), in rounds when a type has more than 4 candidates. Selecting nothing is a valid outcome, and then nothing is removed.
5. For each pick: `git rm` its files (a skill's directory, a command's file, an agent's file), then Grep the surviving library for dangling references to it and surgically clean those pointer lines. Never commit. The user commits.
6. Drop removed items from the sweep scope and continue.

### Step 2: Load the guide

Read `~/.claude/skills/self-heal/heal-guide.md` in full **before inspecting**. It contains the accretion taxonomy, the healthy-shape templates for the three types, the coverage-ledger method, and the worked examples. Load it every run. It is the spec, tuned over time. Do not work from memory.

### Step 3: Inspect in parallel

Dispatch read-only `Explore` subagents across the resolved set, batched so none is overloaded (one per type, or chunks of about 6 to 8 files). Hand each inspector the relevant healthy-shape template from the guide so its read is grounded. Each returns, per file:

- a **debt score** (0 to 5),
- the symptoms found, each with a line cite (redundancy, bolt-on seam, duplicate rule, length bloat, patching cross-reference, tonal seam),
- a one-line gap from its type's healthy-shape template.

Merge the reports on the main thread and rank by debt. (A single-file target does not need a fan-out. Inspect it directly.)

### Step 4: Diagnose & rank, then stop

- **Whole-library / type sweep:** present a ranked table (`artifact · type · debt · headline symptoms · one-line heal proposal`) with the worst first, and recommend the few that deserve healing now.
- **Single target:** present the itemized diagnosis (each symptom as a short quote plus line cite) and the heal plan. State whether the plan is **whole-file** (pervasive debt) or **surgical** (localized), and why.

**Stop for the user.** They pick targets and can veto a symptom or correct a call. The diagnosis is a proposal that the user can change. This checkpoint is the core of the skill.

### Step 5: Build the coverage ledger

For each file the user picked, before rewriting a word, inventory every **behavioral commitment** in the original. A commitment is anything that would change what the file *does* if it vanished:

- every rule and guardrail (each Key Rule included), every instruction step and ordering constraint, every scope / "wrong skill" boundary, every argument, flag, and steer, every edge case and safety constraint the file states, every entry in `allowed-tools` / `tools`, and the frontmatter fields.

This ledger is the contract for the rewrite. It preserves each item's **effect**, and it does not need to preserve wording or location. Rephrasing and relocating is the whole job, and dropping is not part of it.

### Step 6: Heal

Rewrite the file toward its type's healthy-shape template (skill / command / agent, from the guide).

- **Unit.** Whole-file re-integration when debt is pervasive (seams throughout, rules repeated across sections, tone drifting). Surgical when debt is localized to a section or two and the rest is clean. But if rewriting one section leaves a visible mismatch against the untouched ones, widen the rewrite.
- **Moves.** Fold each repeated instruction into one statement in its right home. Dissolve bolt-on parentheticals into the prose. Merge near-duplicate rules. Inline the content a cross-reference points at. Even out tonal seams and cut bloat.
- **Goal.** The result should be simpler and natural, so it reads like one sitting. Shorter is the usual result and **never a target**. Do not drop content to shrink a file (the Goodhart trap `/deslop` warns about).
- **Never regress.** Preserve each ledger item. A rule that looks obsolete or self-contradictory is **flagged for the user as a question and never silently dropped.**

### Step 7: Verify against the ledger

Before writing, re-read the rewrite against the ledger and the guide:

- **Every commitment preserved?** Walk the ledger item by item. This is the regression check.
- **Right structure?** It matches its type's template.
- **Frontmatter intact?** `name`, `version` (preserve unless the user asks to bump), `allowed-tools` / `tools`, and companion paths all correct.
- **One voice?** The rewrite reads as one voice, without new seams, and it is simpler in fact.

Fix silently. Anything that can't be preserved goes to the user as a question instead of vanishing.

### Step 8: Write & report

Per file, after the checkpoint:

- **Git-clean guard:** run `git status --porcelain <path>`. If the file has uncommitted changes, stop and ask before overwriting. Git is the undo, and that only works from a clean base.
- **Write in place.**
- **Report.** List the symptoms resolved and the before→after line count, plus an explicit **ledger-coverage line** ("all N commitments preserved"). Raise any flagged-obsolete rules as open questions, separate from the applied edit.
- **Close** with one honest line: structural change should be large, substantive change near zero. If a file is beyond healing by re-integration (confused about its own purpose, not just messy), say so. self-heal untangles seams. It can't supply a design that was never decided.

## Key Rules

1. **Diagnose & rank before you touch a word.** Present findings, and the user picks. The checkpoint is the skill.
2. **Never regress behavior.** The coverage ledger is the contract: every rule, step, boundary, flag, and edge case is preserved, and only wording and location change.
3. **Heal toward the artifact's own type template.** Skill, command, and agent are three different templates. Never flatten one into another.
4. **Flag, don't drop.** A rule that looks obsolete becomes a question for the user, never a silent deletion.
5. **Simpler and natural is the goal, and shorter is never a target.** Don't shrink a file by cutting content.
6. **Write in place only after the checkpoint, and only when git is clean on that file.** Git is the undo.
7. **Include self-heal's own files in the sweep.** The newest skill is often the most accreted.
8. **Load `heal-guide.md` every run.** The taxonomy, templates, and examples are defined there and not in memory.
9. **The audit proposes and the user removes.** Zero direct invocations is not dead, because text references from live files count as usage.
