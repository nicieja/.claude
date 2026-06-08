---
name: explain-pr
version: 1.0.0
description: |
  Explain a large PR by reading it, its Linear ticket, and historical commits,
  then dispatch code-reviewer + code-simplifier and synthesize feedback into a
  single-voice review.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

## Arguments

The skill may be invoked as `/explain-pr <PR-number | branch | URL>` or bare `/explain-pr`. Treat the argument (if any) the same way Step 0 below describes. If empty, fall back to the current branch (`git branch --show-current`).

## Your task

You are explaining a pull request — typically 3-5k LoC — to a reviewer who needs to understand it before they can review it well. Reading the whole diff top-to-bottom is the wrong move. Instead: read the description and ticket first, get the diff's shape, identify the critical path (2-3 highest-risk files), then dispatch the subagents on a scoped surface.

Follow the steps below in order. Do not critique the code yourself — that's what the subagents are for. Your job is orchestration, context-gathering, and a single-voice synthesis at the end.

---

### Step 0: Preflight

1. Resolve the argument to `{pr_number, head_branch, base_branch, pr_url}`:
   - **Numeric** (`1234`) → PR number. `gh pr view <num> --json baseRefName,headRefName,url`.
   - **URL** (`https://github.com/.../pull/1234`) → extract trailing number, then same as above.
   - **Branch name** → `gh pr list --head <branch> --state all --json number,baseRefName,headRefName,url`. If multiple, pick the most recent open one; fall back to the most recent overall.
   - **Empty** → use the current branch (`git branch --show-current`); resolve as a branch arg.
2. Verify `gh` is installed: `which gh`. If missing, tell the user and stop.
3. Best-effort fetch refs so diffs work locally: `git fetch origin <base_branch>` and `git fetch origin <head_branch>`. Ignore failures (the user may be reviewing a fork).
4. If no PR could be resolved but a branch exists, tell the user: *"No PR found for `<branch>` — explaining branch diff against `<base>` instead."* Set `pr_url=null` and skip PR-only fields in later steps.

---

### Step 1: Fetch PR metadata

```bash
gh pr view <num> --json title,body,author,baseRefName,headRefName,number,url,additions,deletions,changedFiles,labels,commits,state
```

Capture all fields. Note `additions + deletions` as the LoC total.

If `body` is empty or under ~200 chars, mark it: the eventual explanation in Step 5 must say *"PR description is thin — context inferred from commits and Linear."* once, not repeatedly. Do not bail.

---

### Step 2: Shape the diff

```bash
git diff --stat -M <base>...<head>
```

Bucket every file:

- **Mechanical** — `*.lock`, `Gemfile.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `db/migrate/*`, `__snapshots__/*`, `*.snap`, `vendor/`, `third_party/`, vendored `node_modules/`, pure renames (the `-M` flag surfaces these in `--stat`), generated files (`*.pb.go`, `*.generated.*`, `*.gen.ts`), schema dumps (`db/schema.rb`, `schema.sql`).
- **Tests** — `*_spec.rb`, `*_test.go`, `*.test.ts`, `*.test.tsx`, `*.spec.ts`, `__tests__/`, `spec/`, `test/`, `tests/`.
- **Logic** — everything else.

Sum LoC per bucket. The split itself is signal: a 4k LoC PR that's 3.5k mechanical is mostly generated noise; a 4k LoC PR that's 3k logic is the real problem.

If total > 10k LoC, ask via `AskUserQuestion` whether to proceed (slower, may need narrowing) or stop and recommend the author split the PR.

---

### Step 3: Linear context (if a ticket is referenced)

1. Scan for the regex `[A-Z]+-\d+` across: PR title, PR body, head branch name, and each commit message in the `commits` array from Step 1. Deduplicate.
2. For each ticket ID:
   ```bash
   linear issue view <ID> --json --no-pager
   ```
3. From each JSON capture `description`, `state`, and the `comments` array. Filter out automation/bot comments (Linear's auto-posts for branch/PR creation). Newer comments supersede older ones; confirmed language ("the cause is", "fixed by") counts as ground truth, hedged language ("maybe", "might") does not.
4. If no ticket reference is found, skip silently — do not pad the explanation with "no Linear ticket found".

---

### Step 4: Historical commit context

Goal: understand "what was here before, and why." This is what makes a large diff legible.

1. From Step 2's bucketing, pick the top 5 **logic** files by lines changed.
2. For each, look at the file's history on the base branch *before* this PR:
   ```bash
   git log --oneline -10 <base> -- <path>
   ```
   One-line summaries are enough — you're after the recent narrative arc, not the full history.
3. Also read the PR's own commits (already in the `commits` array from Step 1). When the description is thin, the commit messages often carry the author's narrative.
4. Synthesize one short paragraph: what existed in these top files before, what's being replaced or extended.

---

### Step 5: High-level explanation (print to the user)

Print a structured explanation in the conversation, in this order:

1. **What this PR does** — one paragraph. Title, author, `<head_branch>` → `<base_branch>`, PR URL if present.
2. **Why** — synthesized from Linear (Step 3) + PR description + commit messages. If the description was thin, say so here (once).
3. **Shape** — the bucket split: *"Mechanical X LoC across n files / Tests Y LoC / Logic Z LoC."* This calibrates how much real review surface exists.
4. **Architecture sketch** — entry points and key modules touched, named by file path. Group by directory or module.
5. **Critical path** — the 2-3 files the reviewer should read most carefully. Pick by: largest logic change, touches sensitive areas (auth, money, migrations, public APIs, concurrency, data writes), or has the most before-state churn from Step 4. For each, give one sentence on *why it made the list*.
6. **Before-state context** — the one-paragraph synthesis from Step 4.

This is what the user came for. Print it before dispatching subagents — it sets up scope for what comes next.

---

### Step 5.5: Decide which specialists `code-reviewer` must consult

`code-reviewer` already owns specialist dispatch — it triages each PR and spawns `architect-reviewer`, `security-auditor`, and friends as needed, then integrates their findings. The only gap is that its triage is gated on its *own* confidence, which can stay quietly high on a re-architecture whose risk lives outside the diff. So we don't dispatch specialists ourselves and fight that machinery — we **remove the discretion** for the cases that matter, by naming the required consults in `code-reviewer`'s brief.

Decide which specialists this PR warrants — deterministically, by trait, not by gut feel. You already have the signals: the diff buckets (Step 2), the title/branch/commits (Step 1), and the sensitive-area read from the Step 5 critical path. The list you produce here becomes a **mandatory-consult directive** in the Step 6 brief.

**Trait → specialist:**

- **`architect-reviewer`** — any of: a migration in the diff (`db/migrate/*`, `db/schema.rb` churn); a removed model association; a column dropped, relaxed to nullable, or added to `ignored_columns`; a polymorphic / enum / scope change; **or** the title or branch matches `re-?architect | migrate | cutover | rename | re-?model`.
- **`security-auditor`** — auth/authz, crypto, secrets, PII, file upload, or new external-input handling on the critical path.
- **`performance-engineer`** — new queries (especially inside loops), caching changes, async/sync swaps, hot-path edits.
- **`tester`** — critical-path logic changed with thin or absent test coverage, or test-infrastructure / framework / CI edits.

**Lean by default.** Most PRs match no trait, so the directive is empty and `code-reviewer` triages on its own exactly as before. Name a required consult only when a trait is genuinely present — don't manufacture a reason to fan out. A PR can match more than one trait; require each.

**The blast-radius instruction (when the `architect-reviewer` trait is present).** `code-reviewer` writes `architect-reviewer`'s brief when it dispatches it, so this instruction has to be **relayed through** `code-reviewer`. Tell it, in Step 6, to pass this to `architect-reviewer` verbatim (paraphrasable, but keep the substance):

> "This PR changes or removes symbols that other code depends on. For every removed or semantically-changed symbol — a dropped column or association, a column relaxed to nullable or added to `ignored_columns`, a changed enum / scope / serializer, a deleted or renamed method — search the **whole repo** (not just the diff) for readers, and verify each was migrated in this PR or has a linked follow-up. **Findings outside the diff are in scope and are usually the most important on a re-architecture or cutover PR.** Also judge: is the target design right, and is the cutover sequenced safely — are producers flipped ahead of their readers? is a backfill deferred without keeping the old readers working in the meantime?"

This instruction is the point of the whole step. Diff-scoped reviewers cannot find a reader that the diff strands; only an explicit whole-repo search can.

---

### Step 6: Dispatch `code-reviewer` and `code-simplifier` in parallel

Single assistant message, two `Agent` tool calls. Wait for **both** to return before writing Step 7. Specialists are `code-reviewer`'s job, not yours — Step 5.5's output rides into `code-reviewer`'s brief as a required-consult directive (below), so you never dispatch `architect-reviewer` and friends directly.

**Brief for `code-reviewer`** (`subagent_type: "code-reviewer"`):

Include:
- PR metadata (title, URL, author, base/head, totals)
- Linear context snippet from Step 3 (if any) — description + key comments, abstracted
- The "before state" paragraph from Step 4
- The high-level explanation from Step 5 verbatim
- The **critical-path file list** plus the mechanical/generated paths to ignore

End the brief with this instruction (literal, paraphrased only as needed):

> "The total diff is ~`<N>` LoC, but ~`<M>` LoC of that is mechanical/generated across these paths: `<list>`. Those don't need line-by-line review. Focus on the critical-path files I've identified above, plus their tests. **Do not refuse to review based on total LoC — I've already scoped the surface for you.** Apply your usual Blocking / Should fix / Suggestion bucketing with `file:line` references. Apply `/pushback` framing — challenge, don't validate."

If Step 5.5 identified any required consults, add this to `code-reviewer`'s brief (literal, paraphrasable):

> "This PR has traits that warrant specialist review: `<trait → specialist list>`. **Dispatch these specialists as part of your triage — do not skip them on confidence grounds; I'm requiring them.** When you dispatch `architect-reviewer`, give it this instruction verbatim: `<blast-radius instruction from Step 5.5>`. Integrate their findings into your report with attribution, as you normally would."

This leans on `code-reviewer`'s existing specialist router instead of competing with it — we override only the one discretionary step (the confidence gate) for traits we've judged non-negotiable, and let `code-reviewer` own the dispatch and integration.

This explicit scoping matters: `code-reviewer`'s contract says it will ask the author to split oversized PRs. Without this brief it will bail on a 3-5k LoC change.

**Brief for `code-simplifier`** (`subagent_type: "code-simplifier"`):

Include:
- The same PR + Linear + before-state context, compressed
- A focused list of 3-5 logic files (a subset of the critical path) most likely to yield simplifications — pick by: longest new functions, deepest nesting, highest churn-per-LoC ratio in the diff
- Instruction:

> "Suggest concrete simplifications scoped to these files. Behavior must be preserved. Return specific before/after snippets with `file:line` references and one sentence of rationale per suggestion. Don't propose whole-file rewrites or speculative refactors."

---

### Step 7: Synthesize and present (single voice)

Read all subagent reports. Synthesize into one narrative. **Never write "code-reviewer says", "code-simplifier suggests", "the simplifier flagged", "Agent 1", or any other phrasing that exposes which subagent produced what.** Hide the machinery. The reader sees one reviewer's voice.

Structure:

1. **Verdict** — one short line. Examples: *"Lean toward approve with non-blocking notes."* / *"Request changes — three blocking items below."* Pulled from the reviewer's verdict, restated.
2. **Cutover / architecture risk** — one line, present whenever the architecture lens ran (or its trait was present in Step 5.5). State the risk plainly, or *"none"*. **If outside-the-diff breakage or an unsafe cutover was found, the Verdict cannot be "approve"** — it becomes "request changes," and those findings lead Top concerns.
3. **Top concerns** — 3-5 bullets, ordered by severity, each with a `file:line` citation and one sentence on issue + suggested fix. Blocking items first.
4. **Simplification opportunities** — short subsection with the highest-value suggestions, each as a before/after sketch with `file:line`. Skip the whole subsection if nothing survived synthesis.
5. **Lower-priority notes** — collapsed bullet list of nits, optionals, and FYIs. Skip if empty.
6. **Lenses run** — one line naming which lenses ran (e.g. *"code-review, simplify, architecture"*), read from `code-reviewer`'s report (it attributes each specialist it consulted) plus the simplifier. If a Step 5.5 trait was present but `code-reviewer` didn't consult the matching specialist, **say so explicitly** — never let the reader assume a lens covered something it didn't.

**Severity rule:** outside-the-diff breakage and unsafe cutover sequencing are **Blocking** regardless of how clean the changed code itself is. A diff can be flawless line-by-line and still strand the readers that depend on it.

Print. Stop. No follow-up menu, no "want me to post this as a comment?" — by design.

---

## Key rules

1. **Don't read the whole diff top-to-bottom.** The point of this skill is to avoid that. Bucket first, identify the critical path, then go deep only there.
2. **Don't critique the code yourself.** Your job is orchestration and synthesis. Code judgment comes from the subagents.
3. **Hide the machinery in Step 7.** No subagent names, no "the reviewer said" framing. One voice.
4. **Don't let `code-reviewer` bail on size.** The Step 6 brief must include the explicit scoping language — without it, the subagent will request the author split the PR.
5. **Skip silently when a step doesn't apply.** No Linear ticket → don't mention Linear. No PR found → fall back to branch diff and say so once.
6. **Stop after Step 7.** No comment posting, no Linear update, no deeper menus.
