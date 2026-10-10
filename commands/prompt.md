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

**Write the prompt per `~/.claude/skills/work-delegate/brief-guide.md`**: its sections in its order, and its voice rules. Put the session knowledge from above under "Before you start". Put the plan, as decided above, under "The plan".

**Output.** Print the prompt in one fenced Markdown block so it can be copied whole. Before it, one line: the resolved plan source and base branch. Nothing after it.
