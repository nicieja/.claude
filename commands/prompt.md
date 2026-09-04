---
description: Write a prompt for another model to execute a plan from this session
argument-hint: "[plan-file] [base-branch]"
allowed-tools: Read, Bash(git branch:*), Bash(git rev-parse:*), Bash(git status:*), Bash(git log:*), Bash(git symbolic-ref:*), Bash(test:*)
---

## Context

- Current branch: !`git branch --show-current`
- Default branch: !`git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed "s#^origin/##"`
- Working tree: !`git status --short`
- Arguments: `$ARGUMENTS`

## Your task

Write a prompt that a different model, in a fresh session with no memory of this one, can execute to implement a plan produced here. The prompt is the whole handoff: everything the executor needs must be in it, and nothing about how this session arrived at it.

**Resolve the arguments.** Each whitespace-separated token is either a file or a branch; check with `test -f` and `git rev-parse --verify`. A file is the plan. A branch is the base to stack on. Zero, one, or both may be present.

- No plan file → the plan is the one written in this session (a plan-mode plan, a `/shape` output, or the plan you last stated). If there is none, say so and stop.
- No base branch → the base is the current branch.
- A token that is neither → say which token, and stop.

**Pull the plan in verbatim.** Read the file if there is one. The prompt inlines the full plan text, never a summary or a pointer — the executor may run in a different checkout where an uncommitted plan file does not exist. Cite the path too when there is one, so the executor can diff against it.

**Add what only this session knows.** Scan the conversation for the things the plan file leaves implicit and the executor will otherwise rediscover the slow way: decisions already made and why, approaches tried and rejected, files that matter and files that look relevant but are not, project conventions the plan assumes, gotchas found while researching. Write them as flat statements of fact. Leave out anything the executor can learn faster by reading the repo.

**Write the prompt in this shape**, headings included, omitting a section only when it would be empty:

1. **Goal.** One paragraph: what will be true when the work is done, and for whom.
2. **Setup.** The exact commands: fetch, check out a new branch from the base, and — when the base is not the default branch — the note that this is a stacked change, so the PR targets the base branch and must not include the base's own commits in its diff.
3. **What you need to know.** The session knowledge from above.
4. **The plan.** The verbatim text, under its own heading.
5. **Constraints.** Scope boundaries the plan implies (what not to touch, what not to refactor in passing). Always include this rule, in these words or close to them: *Write the code the task needs, and no armor around it. Validate at the system boundary and trust what you find inside. No guards for states no caller can produce, no catch-and-default, no retries, timeouts, or flags nobody asked for. Prefer a loud failure with a good message. When the right failure behavior is a real decision, stop and ask instead of picking the safe-looking option.*
6. **Verification.** How to prove it works: the test commands, the manual checks, the success criteria from the plan.
7. **Deliverable.** Small commits with imperative subjects, a PR against the base branch, and a final report that lists what was built, what was skipped and why, and every place the executor departed from the plan.

**Rules for the prompt's voice:**

- Address the executor as "you". Imperative, specific, no hedging.
- Do not describe this session — no "we decided", "the user said", subagent names, or skill names. State the outcome as fact.
- Do not use the words *robust*, *production-ready*, *bulletproof*, *comprehensive*, or *handle all edge cases*. Say what must not break instead.
- Keep it as long as the plan needs and no longer. Do not pad with generic advice about testing or code quality.

**Output.** Print the prompt in one fenced Markdown block so it can be copied whole. Before it, one line: the resolved plan source and base branch. Nothing after it.
