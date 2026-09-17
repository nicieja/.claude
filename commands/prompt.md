---
description: Write a prompt for another model to execute a plan from this session
argument-hint: "[plan-file] [base-branch]"
allowed-tools: Read, Bash(git branch:*), Bash(git rev-parse:*), Bash(git status:*), Bash(git log:*), Bash(git cat-file:*), Bash(git symbolic-ref:*), Bash(test:*)
---

## Context

- Current branch: !`git branch --show-current`
- Default branch: !`git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed "s#^origin/##"`
- Working tree: !`git status --short`
- Arguments: `$ARGUMENTS`

## Your task

Write a prompt that a different model, in a fresh session with no memory of this one, can execute to complete a plan produced here. The prompt is the whole handoff: everything the executor needs must be in it, and nothing about how this session arrived at it.

The output is instructions to an executor, not the plan. The plan already exists. Your job is to tell someone how to execute it. If what you produce could be mistaken for the plan itself, you have written the wrong document. A restatement, a summary, or a reordering of its steps all count as the plan itself. Start over.

**Resolve the arguments.** Each whitespace-separated token is either a file or a branch. Check with `test -f` and `git rev-parse --verify`. A file is the plan, and a branch is the base to stack on. Zero, one, or both may be present.

- No plan file → the plan is the one written in this session (a plan-mode plan, a `/idea-spec` output, or the plan you last stated). If there is none, say so and stop.
- No base branch → the base is the current branch.
- A token that is neither → say which token, and stop.

**Decide how the executor gets the plan.** Read the plan so you know what is in it, then pick one:

- The plan file is committed on the base branch (`git cat-file -e <base>:<path>` succeeds, and `git status --short <path>` is empty so the committed copy is the one you read) → the prompt points at the path and tells the executor to read it first. Do not copy the plan into the prompt.
- The plan file exists but is not on the base branch, or has local edits → the executor's checkout will not have what you read. Inline the full text under its own heading, and cite the path so the executor can write it there.
- No file, the plan lives only in this session → inline the full text under its own heading.

**Add what only this session knows.** Scan the conversation for the things the plan file leaves implicit and the executor would otherwise rediscover the slow way. These include decisions already made and why, the approaches that were tried and rejected, which files matter and which look relevant but are not, project conventions the plan assumes, and gotchas found while researching. Write them as flat statements of fact. Leave out anything the executor can learn faster by reading the repo.

**Write the prompt with this structure**, headings included, omitting a section only when it would be empty:

1. **Goal.** One paragraph on what will be true when the work is done, and for whom.
2. **Setup.** The exact commands to fetch and to check out a new branch from the base. When the base is not the default branch, add the note that this is a stacked change. The PR then targets the base branch and must not include the base's own commits in its diff.
3. **What you need to know.** The session knowledge from above.
4. **The plan.** Either "Read `<path>` before you start; it is the spec" or, when the file is not committed, the verbatim text under this heading. Never both a pointer and a copy.
5. **Constraints.** Scope boundaries the plan implies (what not to touch, what not to refactor in passing). Always include this rule, in these words or close to them. *Write the code the task needs, and no armor around it. Validate at the system boundary and trust what you find inside. Do not add guards for states no caller can produce, and do not catch-and-default. Leave out retries, timeouts, and flags nobody asked for. Prefer a loud failure with a good message. When the right failure behavior is a real decision, stop and ask instead of picking the safe-looking option.*
6. **Verification.** How to prove it works: the test commands and manual checks to run, and the success criteria from the plan.
7. **Deliverable.** Small commits with imperative subjects, a PR against the base branch, and a final report that lists what was built, what was skipped and why, and every place the executor departed from the plan.

**Rules for the prompt's voice:**

- Address the executor as "you". Be imperative and specific, without hedging.
- Do not describe this session (no "we decided", "the user said", subagent names, or skill names). State the outcome as fact.
- Do not use the words `robust`, `production-ready`, `bulletproof`, `comprehensive`, or `handle all edge cases`. Say what must not break instead.
- Keep it as long as the plan needs and no longer. Do not pad with generic advice about testing or code quality.
- Do not restate the plan's steps in your own words anywhere in the prompt. The plan is the spec, and the prompt is the briefing around it.

**Output.** Print the prompt in one fenced Markdown block so it can be copied whole. Before it, one line: the resolved plan source and base branch. Nothing after it.
