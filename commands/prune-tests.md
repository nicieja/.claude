---
description: Cut the tests a slice added that don't protect a behavior
argument-hint: "[branch | PR | range | sha] [paths] [report]"
allowed-tools: Read, Grep, Glob, Edit, Agent, Bash(git fetch:*), Bash(git diff:*), Bash(git log:*), Bash(git rev-parse:*), Bash(git merge-base:*), Bash(git show:*), Bash(git status:*), Bash(git branch:*), Bash(git symbolic-ref:*), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(test:*)
---

## Context

- Current branch: !`git branch --show-current`
- Default branch: !`git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed "s#^origin/##"`
- Working tree: !`git status --short`
- Arguments: `$ARGUMENTS`

## Your task

Find the tests that a slice of work added, and cut the ones that don't protect a behavior. `quality-engineer` rules on each test. Agents write more tests than a change needs, and this command removes the surplus. It never adds a test or rewrites one.

A test stays when it protects a behavior that a user or a caller depends on, and no other kept test already protects that behavior. Cheap tests of real behavior stay too, because "essential" is too strict a word for this bar.

**Resolve the slice.** Turn the arguments into one `base..tip` range and an optional path filter. A number or a PR URL is a PR, and a token with `..` is a range. A token after `--`, or one that exists on disk, is a path. Anything else is a branch or a sha.

| Argument | Range |
|---|---|
| none | `git merge-base origin/<default> HEAD` to the working tree. Uncommitted changes count, and so do untracked test files. |
| `<branch>` | `git fetch origin <branch>`. The tip is `origin/<branch>` when it exists, else the local branch. The base is its merge base with `origin/<default>`. |
| `<PR number \| url>` | `gh pr view --json headRefName,baseRefName`, then the same as a branch, with the PR's base in place of the default branch. |
| `<a>..<b>` or `<a>...<b>` | Exactly that range. |
| `<sha>` | `<sha>^..<sha>`. |
| paths | Limit any form above to those paths. |
| plain words ("the last 3 commits", "only the request specs") | Map them to one of the forms above, and state the mapping. |

Open with one line that gives the resolved range, the path filter, and the number of new tests across how many files.

**Decide edit or report.** Cut only when the checked-out files match the tip of the slice. That is the bare form, or a target that is the current branch with `HEAD` at the tip. For any other target, rule and report only, and say what to check out ("local is 2 commits behind origin. Pull, then re-run to apply."). `report`, `--report`, or "just tell me" also means report only.

**Find the new tests.** In scope are the test files the range adds, plus the test cases (`it`, `test`, `specify`, `scenario`, `def test_`, `func Test`, `@Test`, and the like) that the range adds to files that already existed. A test declared before the range is out of scope, even when the range changes its body, and it goes under *Out of scope* in the report. If the slice doesn't add a test, say so and stop.

**Dispatch `quality-engineer`.** The verdicts come from the agent's own heuristics. Do not restate them in the brief. The brief contains:

- The range, and the list of new tests as `file:line · name`.
- The non-test part of the diff. The agent judges each test against the behavior the slice adds.
- The bar above. Rule **Keep** or **Cut** on every listed test.
- Evidence on both sides. Each Keep states the behavior it protects, in one line. For a Cut, the evidence is the kept test that already covers the same behavior, or the reason the behavior doesn't need a test. Typical reasons: it checks the framework or a library instead of this code. It restates what the type system or the schema guarantees. It pins internals instead of behavior. It builds a state that no production caller can produce.
- Cuts only. For near-duplicates, keep the clearest one and cut the rest. Rewrites the agent would suggest, and coverage it finds missing, come back as one line each.
- Do not edit files. Return one row per test, `file:line · test · Keep|Cut · reason`, then the weakest Keep and the evidence that would flip it.
- The armor rule, in these words or close to them. *Write the code the task needs, and no armor around it. Validate at the system boundary and trust what you find inside. Prefer a loud failure to a catch-and-default. A test for a state no caller can produce is armor too, and it is a Cut.*

**Apply the cuts.** Delete each Cut. Then remove what the slice added that only the cut tests used: `let` blocks, fixtures, factories, helpers, and imports. Remove a `describe` or `context` block that the cuts leave empty, and delete a new test file that the cuts leave empty. Do not touch pre-existing tests or production code.

**Verify.** Run the touched test files with the project's own runner. Find it in the repo's CLAUDE.md, `package.json`, `Gemfile`, or `Makefile`. When a failure comes from the cleanup, a kept test still uses something you removed, and you put it back. Report a failure that the cuts can't explain, and do not fix it.

**Report.** Leave the edits in the working tree, and do not commit.

- **Cut**: how many, and one line per test as `file:test · reason`.
- **Kept**: how many, and one line per test as `file:test · behavior`.
- **Follow-ups**: the rewrites and coverage gaps the agent flagged. None of them were applied.
- **Out of scope**: the pre-existing tests that the range changed.
- **Verification**: what ran, and the result.

In report mode, the Cut list holds proposed cuts, and there is no Verification section.

A run that cuts nothing says so plainly, and names the weakest Keep and what would flip it. On tests an agent wrote, that result is unusual, so it shows its work.
