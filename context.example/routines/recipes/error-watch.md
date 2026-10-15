# Recipe: a loop from error-tracker issues to fix PRs

A plan for `/work-create-loop`. The loop watches an error tracker for the exceptions that my recent PRs caused, or that come from code I own. It closes the noise by rule and logs each closure for my review. Each real bug gets a diagnosis and an issue with the fix, an executor builds it, and I get a notification to review the PR.

Start it with `/work-create-loop <name> ~/.claude/context.example/routines/recipes/error-watch.md`. The skill treats this file as the plan. Its Step 1 asks only the questions under "Questions for the project", and its Step 2 takes the measurements under "Measure before writing rules".

The recipe gives the design and the contracts, without code. The scripts are short and bound to one project's tracker, deploy records and repo layout, so `/work-create-loop` writes them for each project against the contracts below.

## The design every project keeps

- **The item** is one tracker issue, keyed by its short ID. Issues with one root cause share one fix issue.
- **The wake** runs these steps after the template's lock and reconcile:
  1. Triage each new item. It's closed by a rule, skipped because it's named elsewhere, or a question for me. Anything left goes to diagnosis.
  2. Diagnose with one read-only subagent per item, on a detached worktree at the default branch, with a small cap per wake. The subagent returns the root cause with file:line and the change that introduced it, then the fix in words and the input that reproduces it. Last come the paths the fix touches with their owners, and a confidence.
  3. Write the fix issue from the loop's own brief template, and link it back on the tracker issue.
  4. Dispatch to the executor in `delegation.md`, under a cap.
  5. Supervise the fix PR. A flaky CI failure gets one rerun per head, and a real failure gets a follow-up. The same failure after a follow-up means a takeover, and a decision the PR needs becomes a question for me. Once the PR is ready, run `/code-uncomment` on it in report mode, send the executor the cuts that pass the audit, and notify me after its push.
  6. After a merge, hold the item for two weeks without events before calling it fixed, because fixes come back weeks later.
  7. Report, notify me once per wake, commit, and wake on the watch or the timer.
- **States.** Each item takes the first that matches:
  1. closed by rule
  2. skipped
  3. regressed
  4. fixed
  5. merged
  6. waiting on me
  7. ready for review
  8. PR needs action
  9. running
  10. diagnosed
  11. new
- **The brief** makes the executor commit a test that raises the exception on the default branch, alone and first, before the fix. It fixes only the root cause, without refactors in passing.
- **Other loops' PRs** belong to them. Each loop routine starts with `<!-- schedule: loop -->` and declares its PRs in `routines/<loop>/scope` (one tracker filter per line) and `routines/<loop>/prs`. This loop's `other-loops` script fails on a loop without a `scope`, and the other loops' status scripts leave out what this loop lists in its `prs`.
- **A standing monitor.** Errors keep arriving, so the loop has no end. It's caught up when no item is `new`, and it wakes at least hourly to read the tracker when nothing else wakes it.

## Closing an issue without a fix

Start from these rules, and mark each threshold `(guess)` until the resolution log has counts.

| Rule | When it applies | Action in the tracker |
|---|---|---|
| **R1, deploy window** | Every event happened inside a deploy of the issue's app, from its start to a few minutes after its outcome. The exception and each one in its cause chain are on an exhaustive list of connection, timeout and shutdown errors. The last event is a day old or more | resolve |
| **R2, one-time** | A few events, the last one days old. Either the diagnosis cites the change on the default branch that stops the state from coming back, or every event is a connection error to a service the project runs, all within minutes | resolve |
| **R3, can't be fixed in code** | A not-found from outside the product (no referrer from its hosts, a scanner path, a bot), a probe, an expired form token, a client disconnect, or a correct refusal the screen never offered. Few users. A not-found with the product's own referrer, or with many users, is a broken link, which makes it a bug | archive until it escalates |
| **R4, needs a person** | A limit or an outage at a third party that users see | a question for me |

- **Order.** Write the row in `routines/<name>/resolution-log.md`, then the action's key in the ledger. Then act in the tracker with the rule and its evidence as the visible reason, assign the issue to me so its return is found, and add it to the wake's notification.
- **Review.** I write `ok` or `wrong: <why>` in the log. A `wrong` reopens the issue and adds a counted exception to its rule. A rule with two `wrong` rows stops closing until I approve it again in `decisions.md`.
- **Never** archive forever, delete or merge tracker issues, or close one that an open PR or another issue names. An issue the loop closed that comes back goes to diagnosis, and the rule that closed it is barred for that issue.

## Questions for the project

Step 1 asks these, with the drafted answer as the recommended option:

- **The tracker,** and how the loop reads and writes it (a connector, a CLI or an API token). A shell-readable tracker lets `status` watch it, and otherwise the timer brings new issues.
- **Whose errors.** My PRs from the last N days, my owned paths, or both. Which environments.
- **The first sweep.** How far back the first wake reads. The backlog then drains under the cap.
- **The fix tracker and executor,** the label or filter for the loop's issues, and the brief template.
- **The notification channel.**
- **The outward actions.** Always asked, never inferred. Draft them from the steps above, and keep merges and production writes mine.

## Measure before writing rules

Step 2 measures these on the project's own history and live data. Each result changes the design.

- **How an issue ties to a change.** When the tracker's release is the deploy's commit, a match on my merge commits says nothing about the cause, because each deploy contains everyone's commits. Count the matches, and count how many trace to my code. The changed files of each PR, matched against stack frames, usually work better. Read one event to learn the frame's filename format: relative to the app, or to a package's library directory.
- **Ownership.** Compare one of the tracker's auto-assignments with the history of the repo's `CODEOWNERS`. A tracker's imported copy goes stale, and the repo is the source.
- **Shared files.** A file in many stacks, such as a base model or a framework class, matches PRs that didn't cause the error. The diagnosis must say whether the PR is on the failing path.
- **Search precision.** Search the tracker and the code host for one short ID and count the false matches. Both usually match loosely. The loop accepts whole-word matches only.
- **Query forms.** Run every query through the same interface the loop uses, because a connector may rewrite a query into a form the tracker refuses.
- **Deploy records.** Where they live, how often each service deploys, and whether a record gets a later status when the next deploy replaces it. At dozens of deploys a day, a wide window covers half the day. A grace of a few minutes after the outcome is enough.
- **The history of past fixes.** Over the last 10 to 20 fixed issues, count who finished each one, how often the executor's root cause was wrong, how often the error came back after the merge, how often the base branch moved, and how many were noise. The counts set the cap, the brief's rules and the closing thresholds.
- **Volume** per week, which sets the cap and the wake interval.

## The scripts, by contract

Write each in the project's routine directory, in the style of the project's other scripts. A script exits non-zero with a message that says the fix. Prove each one against a known issue or record before the first wake.

- **`other-loops`** prints `<loop> scope <filter>` and `<loop> pr <entry>` for every other loop routine, and exits 1 for a loop without a `scope`.
- **`queries`** prints one tracker search per line, as `<label> <project> <query>`. It reads owned paths from the repo's `CODEOWNERS` on the default branch, and the changed files of my PRs minus the claimed ones. Every file counts, past any cap on the code host's file list. It leaves out tests and docs, and maps package files to every app that builds with the package. It also prints the searches for my issues that came back.
- **`deploy-window`** takes an app and event times, and prints for each time the deploy it's inside, or `outside`. It ends a deploy at its outcome, not at a later "replaced" status. It refuses an unknown app, a time without an offset, and a deploy that stopped without an outcome.
- **`prs-naming`** prints the open PRs that name a short ID as a whole word.
- **`status`** prints one line per fix PR, per the contract in `~/.claude/skills/work-create-loop/watch.py`.

## Files the loop adds

- `routines/<name>.md`, `ledger.md` (plus `Items` and `Sweeps`), `resolution-log.md`, `brief.md`, `scope`, `prs`, and the scripts.
- The loop's subsection in `escalation.md`, with closing tracker issues by rule listed as an outward action.
- Entries in `decisions.md` for whose errors, the run mode, closing noise by rule, and other loops' PRs.
- A pointer in `delegation.md` to the loop's brief template.
