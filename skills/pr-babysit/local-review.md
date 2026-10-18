# Local review

`/pr-babysit` runs this loop in local mode, where no CI and no review bot on GitHub gives a verdict. Each round, a fresh `reviewer` agent reads the whole branch. The run fixes what it finds at Should fix or above, and the loop stops at the first round that finds nothing new at that level.

The cutoff is what makes the loop end. In a trial on a 340-line prototype, a loop that fixed Suggestions too didn't converge. Its rounds found 7, 3, then 5 findings, and the third round proposed undoing a fix from the first. Each round also reached into more files. With the cutoff, the Should fix findings went 2, 3, 2, 0, and the loop stopped after four rounds. Suggestions never ran out: every round raised three to five, and some were about the previous round's fixes.

## A round

Dispatch one `reviewer` agent, with the brief that `~/.claude/skills/pr-review/independent-review.md` sets and these parts:

- **The diff.** Point the reader at the whole branch, `git -C <checkout> diff <merge base>..HEAD`, every round. Don't narrow it to the commits the last round wrote. In the trial, a reader limited to the fix commits stopped a round sooner and missed a Should fix finding that a whole-branch reader caught.
- **The skill.** The reader applies `/pr-review` in report mode.
- **The sources.** Quote the commit messages in `git log <merge base>..HEAD`, and the PR body when there is one.
- **The output.** Ask for a JSON array. Each item has `id`, `file`, `line`, `severity` (Blocking, Should fix, or Suggestion), `verdict` (Fix, Cut, or Ask), `title`, `evidence`, and `fix`.

Send the same brief every round. Leave out the earlier rounds' findings and how they were ruled, because the reader is useful only while it hasn't seen them.

## Ruling on the findings

- **Blocking and Should fix** findings get the ruling that pr-babysit's Step 3 gives a review thread. The reviewer's `fix` is a proposal. In the trial, two readers of the same code proposed opposite fixes for one finding, so the fix has to be right for the code.
- **Suggestions** are never fixed by the loop. They go in the report's Suggestions part, and a repeat of one already listed is merged into it.
- **A finding that would undo an earlier round's fix** comes to me as a question, at any severity. Readers of the same code disagree, and the loop must not flip between them.
- **A finding already dismissed or asked** keeps its ruling, unless it brings evidence that the disproof didn't cover. It doesn't count as new.

Severity changes from one reader to the next near the cutoff. In the trial, four findings moved between Suggestion and Should fix. A Suggestion that comes back as Should fix is ruled as Should fix.

Fix commits follow pr-babysit's Step 4, and the tests run again before the next round.

## Stop rule

- **Done:** a round finds nothing new at Should fix or above, and the tests pass on the head. The run ends Ready, or Blocked on my answers while a question is still open.
- **Cap:** five rounds in a row on commits the loop wrote. A commit the loop didn't write, such as mine on the same branch, starts the count again, because the branch changed under the loop. At the cap, the run ends Blocked, and the report lists the open findings.

Only the current head counts. Each fix commit needs a new round and a new test run.
