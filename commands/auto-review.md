---
allowed-tools: Bash(gh:*), Bash(git:*), Bash(which:*), Read, Agent, AskUserQuestion, Skill
description: Review the PRs assigned to you in the current repo — explain-pr each one in parallel and present a sorted readiness report
argument-hint: [PR-number-or-URL ...]
---

## Context

- Current repo: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "(not a gh repo)"`
- Argument: $ARGUMENTS

## Your task

You are the orchestrator for a batch PR review. The user is an assigned reviewer on multiple PRs and wants one consolidated view of which ones are ready to merge, which need their eyes, and which to push back on.

Do not read PR diffs yourself. Each PR gets its own subagent that runs `/explain-pr` end-to-end and returns a structured verdict. Your job is queue discovery, fan-out, and final synthesis.

---

### Step 0: Preflight

1. Verify `gh` is installed: `which gh`. If missing, tell the user and stop.
2. Verify we're inside a GitHub repo (`gh repo view` succeeded in the Context block). If not, tell the user and stop.

---

### Step 1: Resolve the PR set

- **If `$ARGUMENTS` is non-empty:** treat each whitespace-separated token as a PR number or URL. For each, run:
  ```bash
  gh pr view <ref> --json number,title,url,author,headRefName,baseRefName,state
  ```
  Skip closed/merged ones with a one-line note (*"Skipping #1234 — already merged."*).

- **If `$ARGUMENTS` is empty:** query the review queue:
  ```bash
  gh pr list \
    --search "is:open is:pr review-requested:@me -reviewed-by:@me" \
    --json number,title,url,author,headRefName,baseRefName \
    --limit 30
  ```
  This returns open PRs where the user is a requested reviewer AND has not yet submitted a review (the `-reviewed-by:@me` qualifier excludes already-reviewed ones).

- If the resulting set is empty, print *"No PRs waiting on your review in `<repo>`."* and stop. No subagent dispatch, no follow-up.

- If the set has more than ~8 PRs, ask via `AskUserQuestion` whether to proceed with all or cap to the top N (oldest first). The fan-out cost is real — each subagent itself dispatches `code-reviewer` + `code-simplifier`.

---

### Step 2: Print the queue

Before dispatching, print a one-line summary per PR so the user sees what's about to run:

```
Reviewing 4 PRs:
- #1234 Add ledger reconciliation job (@alice) → main
- #1235 Migrate users table to bigint id (@bob) → main
- #1236 …
```

---

### Step 3: Dispatch one subagent per PR (parallel)

Single assistant message, one `Agent` tool call per PR. Use `subagent_type: "general-purpose"` so the subagent has access to `Skill`, `Bash`, `Agent`, `Read`, etc. (Each `/explain-pr` invocation itself dispatches `code-reviewer` + `code-simplifier`, so the wrapping subagent must be allowed to dispatch nested agents.)

**Brief for each subagent** (literal, paraphrased only as needed):

> You are reviewing PR `<URL>` on behalf of the user. The user is the assigned reviewer and has not yet posted a review.
>
> 1. Invoke the `explain-pr` skill via the `Skill` tool with the PR URL as the argument. Let it run end-to-end — it will print its high-level explanation and dispatch its own reviewer/simplifier (and, by trait, specialist) subagents.
> 2. Once `/explain-pr` finishes, capture both of its user-facing sections: the high-level explanation (Step 5 of that skill — what/why, shape, architecture sketch, critical path, before-state) and the synthesized review (Step 7 — verdict, top concerns, simplifications, lower-priority notes). From the review, carry through its **Cutover / architecture risk** line and its **Lenses run** line — both feed your verdict below.
> 3. **Return a two-part message: the compact verdict block first, then a delimiter, then the full explain-pr output.** The verdict block, in this exact format:
>    ```
>    PR: #<num> <title>
>    URL: <url>
>    Author: <author>
>    Readiness: <0-10>
>    Cutover/architecture risk: <none | one line naming the risk>
>    Lenses run: <code-review, simplify, architecture, security, …; flag any trait-warranted lens that did NOT run>
>    Summary: <one sentence, max ~20 words, on the overall verdict>
>    Human-attention items:
>    - <bullet>
>    - <bullet>
>    ```
>    Readiness rubric: 0–3 = blocking issues, do not merge; 4–7 = needs author response or non-trivial changes; 8–9 = approve with comments; 10 = ship it. **Outside-the-diff breakage or an unsafe cutover is Blocking (0–3), no matter how clean the changed code is** — a diff can read flawlessly and still strand the readers that depend on it. Be honest — the user trusts your number to decide where to spend time.
>    Human-attention items are the 1–4 things the user must personally eyeball or comment on before approving. Examples: *"the migration in `db/migrate/...` is non-reversible"*, *"auth check in X looks wrong, worth a second pair of eyes"*, *"post a question about the cache invalidation in Y"*. Skip the section if there's nothing.
>    After the verdict block, print a line containing exactly `--- DETAILS ---`, then the full explain-pr output: the Step 5 high-level explanation followed by the Step 7 synthesized review, reproduced faithfully. You may condense mechanical noise (long file lists, repeated boilerplate), but never drop a finding, concern, or simplification.
> 4. Do not print anything outside verdict + delimiter + details. No framing, no preamble, no commentary.

No worktree needed — `/explain-pr` is read-only, so all subagents can share the same checkout safely.

---

### Step 4: Collect, sort, and present

When all subagents have returned, split each message on the `--- DETAILS ---` delimiter into its verdict block and its details. Sort by **descending readiness** (highest = closest to merge, first). On ties, preserve queue order.

Print one consolidated report — **the summary always comes first, the details after**; the summary's scannability is the point:

```
## Review queue summary

### #1234 Add ledger reconciliation job
<URL>
Readiness: 9/10 — Lean approve, non-blocking notes.
Cutover/architecture risk: none.
Lenses run: code-review, simplify.
Human-attention items:
- Confirm the idempotency key strategy in `app/jobs/ledger_reconcile.rb:42` matches what we agreed on Slack.

### #1235 …
…
```

Always print the **Cutover/architecture risk** and **Lenses run** lines for each PR — they make design/cutover risk and review coverage visible at a glance, and they stop a clean-execution PR with a broken cutover from reading as "basically fine."

After the summary, print a `## Details` section so the user can investigate each verdict themselves — one `### #<num> <title>` subsection per PR, **in the same sorted order as the summary**, each containing that PR's full explain-pr explanation and review exactly as the subagent returned it:

```
## Details

### #1234 Add ledger reconciliation job
<the full explain-pr explanation + synthesized review for this PR>

### #1235 …
…
```

If a PR's verdict parsed but its details are missing, keep it in the summary and put a one-line note in its details slot (*"No detailed review returned."*).

**Output rules:**

1. Sort by readiness descending, in both sections. Highest-ready first.
2. **Hide the machinery.** Never write *"the explain-pr subagent said..."*, *"agent 3 returned..."*, or any phrasing that exposes the dispatch graph. The reader sees one voice — in the details section too (the explain-pr output is already single-voice; pass it through, don't reframe it).
3. No follow-up menu, no *"want me to post comments?"*. Stop after the report (summary + details).
4. If any subagent failed or returned a malformed block, list that PR at the bottom under a `### Failed to review` section with the URL and a one-line reason.

---

## Key rules

1. **Don't review PRs yourself.** Each PR's judgment comes from its subagent. Your job is fan-out and synthesis.
2. **Hide the machinery in Step 4.** No subagent names, no per-PR transcript framing. One voice across the report.
3. **Stop after Step 4.** The report (summary + details) is the final output — no comment posting, no approve/request-changes prompts, no deeper menus.
