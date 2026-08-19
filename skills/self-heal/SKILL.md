---
name: self-heal
version: 1.1.0
description: |
  Sweep the prompt library — every skill, command, and agent, self-heal
  included — for accretion debt: the redundancy, bolt-on seams, duplicate
  rules, and tonal drift that build up when files are edited by stapling new
  instructions into convenient spots. Opens sweeps with a transcript usage
  audit that flags dead artifacts and asks which to remove. Ranks the worst,
  then, on your pick and diagnose-first, re-integrates a file from scratch so
  it reads like one author wrote it in one sitting — without regressing a
  single baked-in rule. The prompt-library analog of code-simplifier. Loads
  heal-guide.md every run.
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

Take the prompt library — every `skills/*/SKILL.md` and its companions, every `commands/*.md`, every `agents/*.md` — and repair its **accretion debt**: the patchwork that builds up when files are edited iteratively, each new instruction stapled wherever was handy. Every addition made local sense; together they turn the file into a changelog — the same rule restated in three places, parentheticals bolted on, near-duplicate Key Rules, cross-references that exist only because content landed somewhere else, sections that drift in tone because different sittings wrote them. It still works. It's just harder to read, and the model has more to wade through to follow it.

You **re-integrate**: rewrite the file so it reads like one author wrote it in one sitting — simpler, in one voice, every instruction stated once in its right home. The contract is that you **never regress behavior**. Most of those bolt-ons were added for a reason: a guardrail after something went wrong, an edge case, a hard-won correction. The win is shedding the *seam*, not the *lesson*. Only wording and location are free to change; every rule, boundary, and edge case the file encoded survives.

This is the prompt-library analog of `code-simplifier`, run as periodic maintenance. It inspects in parallel, ranks where debt has piled up, and heals only what you pick — diagnose first, you decide, then it rewrites. It includes its own files in the sweep; the newest skill is often the most accreted.

## Arguments

- `/self-heal` (bare) — sweep the whole library (every `skills/*/SKILL.md` and its companions, `commands/*.md`, `agents/*.md`), rank by accretion debt, and report. You pick what to heal. **Includes self-heal's own files.**
- `/self-heal <name | path>` — focus one artifact: a skill name (`deslop`), a command, an agent, or a path. Skip the ranking; go straight to diagnose → heal.
- `/self-heal skills | commands | agents` — sweep one type only.
- `/self-heal audit` — run the usage audit (Step 1) alone, then stop. No inspection, no healing.
- Steers in plain words: `--report-only` / "just rank them" ranks without healing; "be aggressive" / "be conservative" moves the threshold for what's worth a rewrite; "skip the audit" goes straight from scope to inspection.

If a path is under `~/Library/Mobile Documents/` (iCloud) and the Read fails with a permission error, tell the user: the iCloud path is blocked by macOS privacy controls — ask them to point at a non-iCloud copy.

## When this is the wrong skill

- Stripping AI-slop from arbitrary prose or code → `/deslop`. self-heal repairs *structural accretion in the prompt library*, not emptiness in any text.
- Re-voicing prose into the author's literary voice → `/voice`.
- Restructuring working *code*, or reviewing a code diff → `code-simplifier` / `code-reviewer`. self-heal only touches prompt markdown; it never reads source for logic.
- It composes with `/deslop` — a heal may tighten sloppy prose inside a file as it goes — but self-heal is the one that sweeps the whole library, knows each artifact type's healthy shape, and preserves a coverage ledger across a from-scratch rewrite.

## Instructions

Follow in order.

### Step 0: Resolve scope

Resolve per **Arguments**.

- **Bare** → the whole library. Enumerate with Glob: `~/.claude/skills/*/SKILL.md` and `~/.claude/skills/*/*.md` (companions), `~/.claude/commands/*.md`, `~/.claude/agents/*.md`.
- **Name or path** → resolve to the file(s) and jump to Step 4.
- **Type word** → that one directory.

Classify each file's **type** — skill, command, agent, or companion guide. Type sets the healthy-shape target in Step 6; never heal one type toward another's template.

### Step 1: Usage audit

Identify dead weight before polishing it. Runs on bare and type sweeps; skip it on single-target runs or when the user says "skip the audit". `/self-heal audit` runs this step alone, then stops.

1. Run `python3 ~/.claude/skills/self-heal/usage-audit.py` with Bash. It scans every transcript under `~/.claude/projects/` (subagent transcripts included) for the three invocation signals — Skill tool calls, typed slash commands, and agent dispatches — and prints, per inventory item: sessions, calls, last-used date, a `DEAD` marker at zero use, and the window start date.
2. For each zero-use item, Grep the library for references from *other* files. An item that live files read or dispatch — an agent that loads a skill's SKILL.md as its spec, a skill whose dispatch prompts invoke it — is **indirect use: keep or consolidate**, never dead.
3. Present the verdicts — dead / dormant / alive — with two caveats stated plainly: the window is bounded by transcript retention (~30 days by default), and cadence-based skills (`/retro` after a shipped piece of work, self-heal itself as periodic maintenance) can legitimately sit quiet longer than the window.
4. **Ask which to remove** via AskUserQuestion — multiSelect, one question per type (skills / commands / agents), in rounds when a type has more than 4 candidates. Selecting nothing removes nothing; that is a valid outcome.
5. For each pick: `git rm` its files (a skill's directory, a command's file, an agent's file), then Grep the surviving library for dangling references to it and surgically clean those pointer lines. Never commit — the user commits.
6. Drop removed items from the sweep scope and continue.

### Step 2: Load the guide

Read `~/.claude/skills/self-heal/heal-guide.md` in full **before inspecting**. It holds the accretion taxonomy, the three healthy-shape templates, the coverage-ledger method, and the worked examples. Load it every run — it's the spec, tuned over time; don't work from memory.

### Step 3: Inspect in parallel

Fan out read-only `Explore` subagents across the resolved set, batched so none is overloaded (one per type, or chunks of ~6–8 files). Hand each inspector the relevant healthy-shape template from the guide so its read is grounded. Each returns, per file:

- a **debt score** (0–5),
- the symptoms found, each with a line cite (redundancy, bolt-on seam, duplicate rule, length bloat, patching cross-reference, tonal seam),
- a one-line gap from its type's healthy shape.

Merge the reports on the main thread and rank by debt. (A single-file target needs no fan-out — inspect it directly.)

### Step 4: Diagnose & rank — then stop

- **Whole-library / type sweep:** present a ranked table — `artifact · type · debt · headline symptoms · one-line heal proposal` — worst first, and recommend the few worth healing now.
- **Single target:** present the itemized diagnosis — each symptom as a short quote + line cite — and the heal plan, stating whether it will be **whole-file** (pervasive debt) or **surgical** (localized), and why.

**Stop for the user.** They pick targets, veto a symptom, or correct a call. The diagnosis is a proposal, not a fait accompli — this checkpoint is the point of the skill.

### Step 5: Build the coverage ledger

For each file the user picked, before rewriting a word, inventory every **behavioral commitment** in the original — anything that would change what the file *does* if it vanished:

- every rule and guardrail (each Key Rule included), every instruction step and ordering constraint, every scope / "wrong skill" boundary, every argument, flag, and steer, every named edge case and safety constraint, every entry in `allowed-tools` / `tools`, and the frontmatter fields.

This ledger is the contract for the rewrite. It preserves each item's **effect**, not its wording or location — rephrasing and relocating is the whole job; dropping is not.

### Step 6: Heal

Rewrite the file toward its type's healthy-shape template (skill / command / agent — from the guide).

- **Unit:** whole-file re-integration when debt is pervasive (seams throughout, rules repeated across sections, tone drifting); surgical when it's localized to a section or two and the rest is clean — but if rewriting one section leaves a visible seam against the untouched ones, widen the rewrite.
- **Moves:** fold each repeated instruction into one statement in its right home; dissolve bolt-on parentheticals into the prose; merge near-duplicate rules; inline the content a cross-reference points at; even out tonal seams; cut bloat.
- **Goal:** simpler and natural — it should read like one sitting. Shorter is the usual result, **never a target**; don't drop content to shrink a file (the Goodhart trap `/deslop` warns about).
- **Never regress:** every ledger item survives. A rule that looks obsolete or self-contradictory is **flagged for the user as a question — never silently dropped.**

### Step 7: Verify against the ledger

Before writing, re-read the rewrite against the ledger and the guide:

- **Every commitment preserved?** Walk the ledger item by item — this is the regression check.
- **Right shape?** It matches its type's template.
- **Frontmatter intact?** `name`, `version` (preserve unless the user asks to bump), `allowed-tools` / `tools`, and companion paths all correct.
- **One voice?** No new seam; genuinely simpler.

Fix silently. Anything that genuinely can't be preserved goes to the user as a question — it does not vanish.

### Step 8: Write & report

Per file, after the checkpoint:

- **Git-clean guard:** run `git status --porcelain <path>`. If the file has uncommitted changes, stop and ask before overwriting — git is the undo, and that only works from a clean base.
- **Write in place.**
- **Report:** the symptoms resolved, the before→after line count, and an explicit **ledger-coverage line** ("all N commitments preserved"). Raise any flagged-obsolete rules as open questions, separate from the applied edit.
- **Close** with one honest line: structural change should be large, substantive change near zero. If a file is beyond healing by re-integration — genuinely confused about its own purpose, not just messy — say so. self-heal untangles seams; it can't supply a design that was never decided.

## Key Rules

1. **Diagnose & rank before you touch a word.** Present findings; the user picks. The checkpoint is the skill.
2. **Never regress behavior.** The coverage ledger is the contract: every rule, step, boundary, flag, and edge case survives — only wording and location change.
3. **Heal toward the artifact's own type shape.** Skill, command, and agent are three different shapes; never flatten one into another.
4. **Flag, don't drop.** A rule that looks obsolete becomes a question for the user, never a silent deletion.
5. **Simpler and natural is the goal; shorter is never a target.** Don't shrink a file by cutting content.
6. **Write in place only after the checkpoint, and only when git is clean on that file.** Git is the undo.
7. **Include self-heal's own files in the sweep.** The newest skill is often the most accreted.
8. **Load `heal-guide.md` every run.** The taxonomy, templates, and examples live there, not in memory.
9. **The audit proposes; the user removes.** And zero direct invocations is not dead — text references from live files count as usage.
