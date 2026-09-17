---
name: pr-review
version: 1.2.0
description: |
  Differential PR review: baseline what any bot would say, absorb what human
  and AI reviewers already said, then dispatch code-reviewer with the context
  bots lack (ticket intent, file history, your ownership map, and whole-repo
  reach) to find only what has NOT been raised. Staged reveal
  (sentence → paragraph → tour → per-issue solution choice) ending in one GitHub review
  of inline comments in your voice, or in "nothing novel to add," which is
  success too.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

## Arguments

The skill may be invoked as `/pr-review <PR-number | branch | URL>` or bare `/pr-review`. Consume flag tokens before resolving the ref. `--unattended` switches to Unattended mode (section below), and `refresh-focus` (accept `--refresh-focus` too) forces focus-map regeneration in Step 7. Whatever token remains is the ref; if none remains, fall back to the current branch (`git branch --show-current`).

## Your task

You are reviewing a pull request on behalf of the user, typically one that AI reviewers (Cursor, Greptile, CodeRabbit, Copilot) and human colleagues have already commented on. Everything obvious has probably been said. Your job is exclusively the delta. Find what nobody has raised, powered by context the bots don't have (ticket intent, file history, the user's ownership map, and whole-repo reach). Orchestrate, and do not critique the code yourself. **"Nothing novel to add" is a success outcome.** Say it, recommend approve, and stop. Never manufacture findings to justify the run.

Follow the steps in order. Steps 3 to 8 form a parallel window: the baseline agent reviews in the background while you gather local context. The baseline and the Step 10 dispatch are inherently serial, because the mask (which includes baseline findings) rides in the Step 10 brief. Do not try to parallelize them.

---

### Step 0: Preflight

1. Resolve the argument to `{pr_number, head_branch, base_branch, pr_url, owner, repo}`:
   - **Numeric** (`1234`) → PR number. `gh pr view <num> --json baseRefName,headRefName,url`.
   - **URL** → extract the trailing number, then same as above.
   - **Branch name** → `gh pr list --head <branch> --state all --json number,baseRefName,headRefName,url`. If multiple, pick the most recent open one, and fall back to the most recent overall.
   - **Empty** → current branch (`git branch --show-current`), resolved as a branch arg.
   Get owner/repo once: `gh repo view --json owner,name -q '.owner.login + "/" + .name'`.
2. Verify `gh` is installed (`which gh`) and authenticated (`gh auth status`). Either failing: interactively, tell the user what to run (`gh auth login`) and stop; unattended, abort with a run report that states the failure.
3. Best-effort fetch so local diffs work: `git fetch origin <base_branch>` and `git fetch origin <head_branch>`. If the head fetch fails (fork PR), `git fetch origin pull/<pr_number>/head` and diff against `FETCH_HEAD`. Never `gh pr checkout`, because it mutates the working tree.
4. If no PR could be resolved but a branch exists → **analysis-only mode**: say once *"No PR found for `<branch>`. Reviewing the branch diff against `<base>` instead. There is nothing to post to."* Skip Steps 4 and 14, and the mask will be baseline-only.

---

### Step 1: Fetch PR metadata

```bash
gh pr view <num> --json title,body,author,baseRefName,headRefName,headRefOid,number,url,additions,deletions,changedFiles,labels,commits,state,isCrossRepository,reviewDecision
gh api user -q .login   # → viewer
```

Capture all fields. Note `headRefOid`, because it pins the eventual post. Set `viewer_is_author` when `author.login == viewer`. If `state` is not `OPEN`, carry a note: the Step 12 sentence must say it, and the Step 14 recommendation becomes **Don't post**.

If `body` is empty or under ~200 chars, mark it: the Step 12 paragraph must say *"PR description is thin. Context inferred from commits and Linear."* once, not repeatedly. Do not bail.

---

### Step 2: Shape the diff

```bash
git diff --stat -M <base>...<head>
```

Bucket every file:

- **Mechanical**: `*.lock`, `Gemfile.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `db/migrate/*`, `__snapshots__/*`, `*.snap`, `vendor/`, `third_party/`, vendored `node_modules/`, pure renames (the `-M` flag detects these), generated files (`*.pb.go`, `*.generated.*`, `*.gen.ts`), schema dumps (`db/schema.rb`, `schema.sql`).
- **Tests**: `*_spec.rb`, `*_test.go`, `*.test.ts`, `*.test.tsx`, `*.spec.ts`, `__tests__/`, `spec/`, `test/`, `tests/`.
- **Logic**: everything else.

Sum LoC per bucket. The split is signal: 4k LoC that is 3.5k mechanical is noise, and 4k that is 3k logic is the real thing. These gates decide here:

- **>10k LoC total**: interactively, ask via AskUserQuestion whether to proceed (slower, may need narrowing) or stop and recommend splitting; unattended, stop with a run report.
- **Small PR**: logic-bucket additions+deletions under ~150 → set `skip_baseline`, and the mask will be existing feedback only.

---

### Step 3: Dispatch the baseline reviewer (background)

The baseline approximates what any context-free bot would say. Its findings are subtracted later. They define "obvious", and they are not the review.

Skip when `skip_baseline` is set. In unattended mode, also skip when the PR already has bot feedback. Probe first:

```bash
gh api repos/<owner>/<repo>/pulls/<num>/reviews --jq '[.[] | select(.user.type=="Bot")] | length'
# if 0, also probe: gh api repos/<owner>/<repo>/issues/<num>/comments --jq '[.[] | select(.user.type=="Bot")] | length'
```

Otherwise dispatch now (`subagent_type: "general-purpose"`, `run_in_background: true`) with this brief and **nothing else** (literal, paraphrase only as needed):

> "Review PR `<pr_url>`. Use `gh pr view` and `gh pr diff` to read it. Return every issue you would raise as a reviewer, one line each: severity (Blocking / Should fix / Suggestion), `file:line`, one-sentence issue. Read-only: do not post anything to GitHub, and do not ask questions or write files. Your final message is the list itself, without a preamble."

**Do not enrich this brief.** Leave out the Linear context, the history, the focus map, and the critical path. Its emptiness is the mechanism. In analysis-only mode, replace the PR URL with *"the `<repo>` branch diff `<base>...<branch>`"*.

---

### Step 4: Harvest existing feedback

Skip in analysis-only mode. Three surfaces, then the patches.

```bash
gh api repos/<owner>/<repo>/issues/<num>/comments --paginate    # top-level conversation
gh api repos/<owner>/<repo>/pulls/<num>/reviews --paginate      # review summaries + states
```

Inline threads with resolution state are GraphQL-only (substitute real values for `<owner>`, `<repo>`, `<num>`, because `gh api graphql` does not expand `{owner}` placeholders):

```bash
gh api graphql --paginate -F owner=<owner> -F name=<repo> -F number=<num> -f query='
query($owner:String!, $name:String!, $number:Int!, $endCursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved isOutdated path line originalLine diffSide
          comments(first:1) { nodes { databaseId body createdAt author { login __typename } } }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[]'
```

Precision notes. Pass `number` with `-F` (typed int, since `-f` sends a string and the query fails). `--paginate` on GraphQL requires the `$endCursor` variable and the `pageInfo { hasNextPage endCursor }` block exactly as written. `comments(first:1)` is deliberate, because the first comment is the thread's top-level comment, and its `databaseId` is the only valid target for the Step 14 replies endpoint. Threads on deleted lines have `line: null` → use `originalLine` with side LEFT.

Fetch the patches now too and save them to the scratchpad (Step 11 validates anchors against them):

```bash
gh api repos/<owner>/<repo>/pulls/<num>/files --paginate > <scratchpad>/pr-files.json
```

(The files endpoint caps at 3000 files and omits `patch` for very large or binary files. Fall back to `gh pr diff <num>` and parse the same hunk headers.)

**Bot detection.** A source is a bot when any of these is true: REST `user.type == "Bot"`; login ends `[bot]`; GraphQL `author.__typename == "Bot"` (GraphQL logins lack the `[bot]` suffix, and both forms must be checked); case-insensitive match on `cursor`, `greptile`, `coderabbit`, `copilot`.

Normalize every discrete **finding** into a mask line. Not every comment is a finding: a bot walkthrough summary is not a finding, and one dense human comment can yield two. Write the gists yourself, and never paste comment bodies. Grammar:

```
KNOWN[<resolved|open|baseline>] <source> @ <file>:<line | (no anchor)> — <gist, ≤15 words>
```

Examples:

```
KNOWN[resolved] coderabbitai[bot] @ app/models/user.rb:42 — N+1 loading orgs inside the member loop
KNOWN[open]     alice             @ db/migrate/20260801_add_idx.rb:10 — index creation should be concurrent
KNOWN[open]     bob               @ (no anchor) — asks whether the backfill covers soft-deleted rows
```

Sources keep the REST-form login (`[bot]` suffix intact, because it also records provenance). Review summaries and issue comments get `(no anchor)`. On the side, build the **endorsement-target table**: open thread → first-comment `databaseId` + `path` + `line`. It stays in your working notes, and IDs never enter a brief.

---

### Step 5: Linear context (if a ticket is referenced)

1. Scan for the regex `[A-Z]+-\d+` across the PR title, the PR body, the head branch name, and each commit message in the `commits` array from Step 1. Deduplicate.
2. For each ticket ID: fetch the issue through the Linear MCP tools (load them via ToolSearch if deferred). If Linear is unavailable in this session, note it once and continue without ticket context.
3. From each ticket capture `description`, `state`, and the `comments` array. Filter out automation/bot comments (Linear's auto-posts for branch/PR creation). Newer comments supersede older ones; confirmed language ("the cause is", "fixed by") counts as ground truth, hedged language ("maybe", "might") does not.
4. If no ticket reference is found, skip silently, and do not pad the output with "no Linear ticket found".

---

### Step 6: Historical commit context and the critical path

Goal: "what was here before, and why", which is context no bot loads.

1. From Step 2's bucketing, pick the top 5 **logic** files by lines changed.
2. For each, look at the file's history on the base branch *before* this PR:
   ```bash
   git log --oneline -10 <base> -- <path>
   ```
   One-line summaries are enough. They give the recent narrative arc rather than the full history.
3. Read the PR's own commits (already in Step 1's `commits` array). When the description is thin, the commit messages often carry the author's narrative.
4. Synthesize one short paragraph: what existed in these top files before, what is being replaced or extended.
5. Close by picking the **critical path**, the 2-3 files chosen by largest logic change, sensitive-area touch (auth, money, migrations, public APIs, concurrency, data writes), or highest before-state churn. Give one sentence each on why. This feeds the Step 10 brief and the Step 12 tour.

---

### Step 7: Focus map, the user's areas

Resolve `<project>` = repo directory name (`basename $(git rev-parse --show-toplevel)`). Read `~/.claude/context/<project>/review-focus.md`.

- **Fresh** (its `Generated:` date is under ~30 days old) and no `refresh-focus` flag → use it as-is.
- **Missing, stale, or `refresh-focus`** → regenerate:

```bash
gh api user -q .login                                # GitHub login, for CODEOWNERS matching
git config user.email; git config user.name          # git-log author identities
for f in .github/CODEOWNERS CODEOWNERS docs/CODEOWNERS; do [ -f "$f" ] && grep -n "@<login>" "$f"; done
git log --since="12 months ago" --author="<email>" --name-only --format= | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -25
```

`--author` is a regex against `Name <email>`; run with the email first, and if it matches suspiciously few commits (<10), rerun with the name. Slashless survivors of the `sed` are repo-root files. List them as-is. Write the result to `~/.claude/context/<project>/review-focus.md` in the `context.example/review-focus.md` shape (create the directory if needed). Derivation is deterministic, with no interactive/unattended split. If `gh api user` fails or the git log is empty, write what you have or skip the focus map with one note. Never ask twice or loop.

**The map directs depth, never scope.** It buys depth (how this diff interacts with the code the user is responsible for, such as changed invariants, broken assumptions, or regressions to patterns they authored), and it never excludes findings elsewhere.

---

### Step 8: Collect the baseline, the join point

If the baseline agent has not returned yet, wait for it here (check its task output, and never fabricate its result). Merge its findings into the mask as `KNOWN[baseline] baseline @ <file>:<line> — <gist>` lines.

If it failed, timed out, or was skipped, proceed with the mask = existing feedback only, and note it once. Interactively, that is one line in the Step 12 paragraph (*"baseline unavailable: filtered against existing feedback only"*). Unattended, it is a run-report item.

---

### Step 9: Decide required consults + the blast-radius instruction

`code-reviewer` owns specialist dispatch. It triages and spawns `architect-reviewer`, `security-auditor`, and friends, then integrates their findings. Its triage depends on its *own* confidence, which can remain high on a re-architecture whose risk is outside the diff. Rather than dispatch specialists ourselves, we **remove the discretion** for the cases that matter by naming required consults in the Step 10 brief. This step is also the novelty engine: every bot on this PR is diff-scoped, so whole-repo findings are the class of feedback only this pipeline produces.

Decide by trait, not gut feel. The signals are the Step 2 buckets, the Step 1 title/branch/commits, and the Step 6 critical path:

- **`architect-reviewer`**: any of a migration in the diff (`db/migrate/*`, `db/schema.rb` churn); a removed model association; a polymorphic / enum / scope change; a column that is dropped, made nullable, or added to `ignored_columns`. **Also** when the title or branch matches `re-?architect | migrate | cutover | rename | re-?model`.
- **`security-auditor`**: auth/authz, crypto, secrets, PII, file upload, or new external-input handling on the critical path.
- **`performance-engineer`**: new queries (especially inside loops), caching changes, async/sync swaps, hot-path edits.
- **`quality-engineer`**: critical-path logic changed with thin or absent test coverage, or test-infrastructure / framework / CI edits.

**Lean by default.** Most PRs match no trait. Then the directive is empty and `code-reviewer` triages on its own exactly as before. A PR can match more than one trait, and each one is required.

**The blast-radius instruction** (when the `architect-reviewer` trait is present). `code-reviewer` writes `architect-reviewer`'s brief when it dispatches it, so this is **relayed through** `code-reviewer`. Tell it, in Step 10, to pass this verbatim (paraphrasable, keep the substance):

> "This PR changes or removes symbols that other code depends on. For every removed or semantically-changed symbol (a dropped column or association, a column relaxed to nullable or added to `ignored_columns`, a changed enum / scope / serializer, a deleted or renamed method), search the **whole repo** (not just the diff) for readers, and verify each was migrated in this PR or has a linked follow-up. **Findings outside the diff are in scope and are usually the most important on a re-architecture or cutover PR.** Also judge: is the target design right, and is the cutover sequenced safely? Are producers flipped ahead of their readers? Is a backfill deferred without keeping the old readers working in the meantime?"

---

### Step 10: Dispatch `code-reviewer` (one agent, context-rich)

Single dispatch (`subagent_type: "code-reviewer"`). No simplifier, because style polish is bot territory, and volume is the enemy. The brief contains, in order:

- PR metadata (title, URL, author, base/head, totals)
- The Linear snippet (Step 5) and the before-state paragraph (Step 6)
- The critical-path file list plus the mechanical/generated paths to ignore (Steps 2 and 6)
- **The focus instruction** (literal, paraphrasable):

  > "You are reviewing on behalf of `<viewer>`, who owns or actively works in: `<top focus-map areas>`. Give extra depth to how this diff interacts with that code (changed invariants, broken assumptions in files they own, regressions to patterns they authored). This guides where to go deep and does not limit scope: findings anywhere in the diff are fully in scope."

- **The mask, in two zones** (literal):

  > "Already raised on this PR, or obvious enough that a context-free read finds it. **Do not repeat any of these**; where you would have raised one, go deeper on its root cause or look elsewhere instead:
  > `<all KNOWN[resolved] + KNOWN[baseline] lines>`
  >
  > Open threads (unresolved points other reviewers have raised). Don't re-derive these at length. If your independent analysis **confirms or refutes** one, add a one-line note prefixed `ENDORSE:` or `REFUTE:` with the `file:line` and your one-sentence reason:
  > `<all KNOWN[open] lines>`"

- If Step 9 named required consults (literal, paraphrasable):

  > "This PR has traits that warrant specialist review: `<trait → specialist list>`. **Dispatch these specialists as part of your triage. Do not skip them on confidence grounds, because I'm requiring them.** When you dispatch `architect-reviewer`, give it this instruction verbatim: `<blast-radius instruction from Step 9>`. Integrate their findings into your report with attribution, as you normally would."

- The closing scope instruction (literal):

  > "The total diff is ~`<N>` LoC, but ~`<M>` LoC of that is mechanical/generated across these paths: `<list>`. Those don't need line-by-line review. Focus on the critical-path files above, plus their tests. **Do not refuse to review based on total LoC. The review area is already scoped for you.** Apply your usual Blocking / Should fix / Suggestion / Praise bucketing with `file:line` references. For each finding, give your recommended remedy **plus 1-2 alternatives at different cost/risk levels** (a narrow local patch, a root-cause fix, or defer-with-a-guard). For each, one line on what it changes, what it costs, and what it leaves unfixed. Say plainly when there is only one sane fix, and do not invent alternatives to fill a slot. Apply `/idea-challenge` framing: challenge rather than validate. Report only, and do not post anything to GitHub."

---

### Step 11: The differential filter

Classify every finding `code-reviewer` returned, in this order. Matching is semantic (same file and roughly the same lines, or the same symbol and the same substantive point), never string equality:

1. Matches a `KNOWN[resolved]` line → **drop** (already handled on the thread).
2. Matches a `KNOWN[baseline]` line → **drop** (obvious, since any bot would say it).
3. Matches a `KNOWN[open]` line, or arrived prefixed `ENDORSE:` → **endorsement candidate**, the +1 that tells the author which open comment actually matters.
4. Arrived prefixed `REFUTE:` → **refutation candidate**, the counter-reply that tells the author an open comment is wrong.
5. Otherwise → **novel**.

Sort novel by severity (Blocking > Should fix > Suggestion), and fold at most one Praise into the eventual review body. Cap the per-issue Q&A at **5 novel findings**. Endorsements and refutations always ride the one grouped question in Step 12(d). The remainder gets one named line each in chat and stays out of the posted review unless the user promotes one.

Validate every candidate's anchor now with `python3 ~/.claude/skills/pr-review/validate-anchors.py <scratchpad>/pr-files.json`, feeding it one `{"path": …, "line": N, "side": "RIGHT" | "LEFT"}` JSON object per line on stdin. It applies the hunk-range rule (a `RIGHT` anchor must fall inside a `+c,d` range for that file and a `LEFT` anchor inside `-a,b`, where context lines count). For each invalid anchor it prints the nearest changed line on that side. Fallback chain: that nearest changed line (re-point the comment text to match) → the review body. Record the differential counts: found F / dropped-as-known D / novel K / endorsements E / refutations R.

**K + E + R = 0 → the nothing-novel path.** The reveal still runs (sentence, paragraph), then concludes: *"Nothing to add beyond the existing review. Recommend approve (or don't post)."* Step 14 offers only **Post (approve) / Don't post**.

---

### Step 12: Staged reveal (interactive profile)

Never mention the machinery in the reveal or in anything posted. That means leaving out "baseline agent", "code-reviewer", and mask jargon. *"Not already raised on this thread"* is fine, and *"my baseline agent found"* is not.

**(a) One sentence.** What the PR does + the differential outcome (*"3 findings beyond what's already on the thread, 1 endorsement of an open comment"* / *"nothing novel to add"*). Then AskUserQuestion with header "Proceed?" and the options **Continue (Recommended)** / **Stop**.

**(b) One paragraph.** Why (Linear + description + commits, with the thin-description note if Step 1 marked it), the bucket split, and the differential summary with counts (F found, D already covered, K novel, E endorsements). Then AskUserQuestion with the options **Show the issues (Recommended)** / **Tour first** / **Stop**. On the nothing-novel path the options are **Wrap up (Recommended)** / **Tour first** / **Stop**.

**(c) The tour** (only on request) is the comprehension layer, compressed. It covers the bucket split, an architecture sketch (entry points and key modules, named by file path and grouped by directory), the 2-3 critical-path files with one sentence each on why, the before-state paragraph, and a suggested reading order. Then re-ask with **Show the issues (Recommended)** / **Stop**.

**(d) Per-issue solution choice**, novel findings only, severity order, max 5. The user is not rubber-stamping someone else's verdict. They decide as the engineer how the thing gets fixed. Their answer is the suggested fix that posts.

Each issue is one cycle with two parts in the same turn: **the write-up in chat, then the question**. This applies on every pass of the loop. After the user answers Issue N, Issue N+1 is printed in full before its question.

The write-up must be complete on its own. It gives the severity, the `file:line`, and where the comment will land (inline or review body). It explains the failure mechanism step by step. That means which pieces of code interact, the sequence that goes wrong, and what hides it on the happy path. It says why it matters and what is confirmed versus unverified. It lists each candidate remedy with what it changes, what it costs, and what it leaves unfixed. The user must be able to pick a remedy from the write-up alone, without asking for an explanation. The one-line issue name inside the question is a label, not the explanation.

Then AskUserQuestion with header `Issue <i>/<K>` and the question **"How would you solve this?"** with the issue named in one line. The options, in this order:

- **Option 1** is the reviewer's recommended remedy, labeled **(Recommended)**, with the fix in the label and its cost and risk in the description.
- **Options 2-3** are the alternatives, each with what it changes, what it costs, and what it leaves unfixed.
- **Option 4** is **"Drop: leave out of the review."**

The ceiling is four options, because AskUserQuestion takes no more, and "Other" is appended for free.

Use the option `preview` field when a remedy reads better as a code sketch than as a sentence. Previews render side by side.

If the reviewer returned only one remedy, derive one or two alternatives yourself at different cost/risk levels (a narrower local patch, a root-cause fix, or defer-with-a-guard). **Never pad**: two options beat three where one is filler. Drop is always present, so the tool's two-option floor is always met.

The built-in **"Other"** is the user's own words, and it is authoritative. A fix replaces the remedy. A disposition (*"make it a suggestion"*, *"ask the author instead"*, *"drop it"*) is honored directly. A question is answered in chat, then the same question is re-asked.

Record the chosen remedy against the finding. Step 13 posts it.

After the capped five, list the remainder with one line each. These lines are chat-only and are not posted. If endorsements/refutations exist, one grouped AskUserQuestion with **Include all (Recommended)** / **Pick which** / **Skip them**.

---

### Step 13: Assemble, voice, print the draft

Assemble three parts:

- **Review body** (short) contains the verdict recommendation, one line of differential transparency (*"N points already covered by existing reviews were left out"*), any unanchorable findings as `path:line — issue` prose, and at most one Praise line if deserved.
- **Inline comments**: every anchored finding the user kept, each with its `{path, line, side}`. The suggested fix in each comment is **the remedy the user chose**, not the reviewer's default; where they answered in free text, the comment gives their fix in their words. Never list the alternatives they passed over.
- **Endorsement/refutation replies**: one short reply per target thread (from the endorsement-target table). If `viewer_is_author`, reword replies as acknowledgements (*"Confirmed, will fix"*), not +1s.

Then the **slop pass** (literal). Read `~/.claude/skills/edit-deslop/slop-guide.md` in full, every run and not from memory, because it is tuned over time. Tighten every body just assembled (review body, inline comments, replies) against it. These are engineering comments rather than stories. Then pipe each body through `vale --no-exit --ext=.md` and fix its error-level alerts; these bodies post via `gh`, so the edit hook never sees them. Do NOT invoke the deslop skill. The meaning, the severity, and every `file:line` reference do not change.

Print the full draft. Start with the body, then each inline comment under its `path:line` anchor, then each reply under its target thread. **This printed text is exactly what posts.**

**Unattended mode stops here**, with a draft plus run report and never a post.

---

### Step 14: Post

AskUserQuestion offers **Post (comment)** / **Post (request changes)** / **Post (approve)** / **Don't post**, with the recommended event first and labeled **(Recommended)**. When `viewer_is_author`, offer only **Post (comment) / Don't post** (GitHub rejects self-approval and self-request-changes with a 422).

**"Don't post"** → stop cleanly. The draft stays in the conversation, without files, partial posts, or a follow-up menu.

On post:

1. Re-check `gh pr view <num> --json headRefOid`. If it drifted, re-fetch the `/files` patches, re-validate every anchor, and demote broken ones to the review body.
2. Build the payload as JSON in the session scratchpad directory (fall back to `/tmp`):

   ```json
   {
     "commit_id": "<validated headRefOid>",
     "event": "COMMENT | REQUEST_CHANGES | APPROVE",
     "body": "<review body>",
     "comments": [
       { "path": "app/models/user.rb", "line": 42, "side": "RIGHT", "body": "…" },
       { "path": "app/services/x.rb", "start_line": 10, "start_side": "RIGHT", "line": 14, "side": "RIGHT", "body": "…" }
     ]
   }
   ```

   ```bash
   gh api repos/<owner>/<repo>/pulls/<num>/reviews --method POST --input <scratchpad>/review-payload.json
   ```

   Always pass `event`, because omitting it creates a PENDING review nobody sees. Prefer single-line anchors. A multi-line anchor needs `start_line < line` within one hunk. An `APPROVE` on the nothing-novel path may omit `comments` and have a one-line body. The POST is **atomic**. A 422 means nothing was posted. Parse the error, demote the offending comment(s) to the body, and retry **once**. If it still fails, print the payload path and the error, then stop.
3. Post the replies, one call per endorsement/refutation, using the `databaseId` from the endorsement-target table (it must be the thread's top-level comment, because replies-to-replies are unsupported):

   ```bash
   gh api repos/<owner>/<repo>/pulls/<num>/comments/<databaseId>/replies --method POST -f body='…'
   ```

   Replies are not atomic with the review. If one fails, report which thread failed and continue with the rest.
4. Print the review URL. Stop without a follow-up menu.

---

## Unattended mode

`/pr-review --unattended <ref>` is the headless form. Differences from the interactive flow, all non-negotiable:

- **Never asks.** No AskUserQuestion anywhere. Anything that would have been a question becomes a skip or a run-report item.
- **>10k LoC** → stop with a run report instead of asking.
- **The baseline is skipped when the PR already has bot feedback** (Step 3 probe), because the bots themselves are the mask there.
- **Keeps all novel findings** at the reviewer's severity, each with its recommended remedy plus the alternatives, one line each. The user picks after the fact instead of in the flow.
- **Runs Steps 0 to 11, then Step 13's assembly and slop pass** (the draft must be paste-ready). Step 12's questions become printed sections: sentence, paragraph, and findings with their remedy sets.
- **Stops after the printed draft. Never posts a review or a reply, and there are no exceptions.**
- **Ends with a run report.** It has the differential counts (found / dropped-as-known / novel / endorsements / refutations), a one-line recommended event (comment / request changes / approve / don't post), and every gap (Linear unavailable, baseline skipped or failed, focus map missing, >10k stop).

---

## Key rules

1. **Don't read the whole diff top-to-bottom.** Bucket first, find the critical path, go deep only there.
2. **Don't critique the code yourself.** Orchestrate; code judgment comes from the dispatched reviewer, and so do the candidate remedies. The user picks among them, and you carry the pick through to the post.
3. **Never ask about an issue the user has not read.** Each per-issue question is preceded, in the same turn, by that issue's full write-up.
4. **Novelty rides in the briefs, never as an instruction.** Asymmetric context (ticket, history, focus map, whole-repo reach) plus the mask is the mechanism, and "find novel things" is not one.
5. **Dedupe against resolved only.** Open threads produce endorsements, not silence. An ignored critical finding endorsed by a human reviewer is high-value review.
6. **Nothing-novel is success.** Say it, recommend approve, stop. Never manufacture findings to justify the run.
7. **The focus map directs depth, never scope.** Go deep in the user's areas, and keep full scope everywhere.
8. **Hide the machinery.** Keep agent names, "baseline", and mask jargon out of the reveal and everything posted.
9. **Don't let `code-reviewer` bail on size.** The Step 10 brief keeps the explicit scoping language.
10. **Never post without the Step 14 ack, and unattended never posts at all.** The printed Step 13 draft is exactly what posts.
11. **The slop pass changes wording only.** The meaning, severity, and anchors are fixed.
12. **Writes are bounded** to `~/.claude/context/<project>/review-focus.md` and the scratchpad payload. Those are the only files this skill writes.
13. **Skip silently when a step doesn't apply.** No ticket → no Linear mention; no feedback → the mask is just the baseline; analysis-only → one note, then no posting talk.
