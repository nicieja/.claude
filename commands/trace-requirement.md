---
description: Trace each requirement in a plan, spec, brief, PR, or existing code to the person who made it, then question it
argument-hint: "[plan file | PR number | issue id | code path | behavior in words]"
---

## Context

- Arguments: `$ARGUMENTS`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Question a set of requirements, whether a plan proposes them or the code already enforces them. Building or maintaining a requirement that shouldn't exist is wasted effort, so two steps come first, in this order:

1. **Question every requirement.** Start with who made it. Each one needs the name of a real person, because only a person can say whether it still holds. A requirement whose author is a department, a document, or an agent has no owner yet.
2. **Delete what the questioning didn't justify.** A requirement with no named author, and nothing that depends on it, goes.

Simplifying what's left comes after both steps, and it isn't this command's job. The steps below carry out the two.

**Resolve the target.** A prose file is a plan, spec, or brief. A number or a PR URL is a PR, read with `gh pr view` and `gh pr diff`. An issue id is a tracker issue, read through the tracker's MCP tools when the session has them. A source file, a directory, a symbol, or a behavior in words, such as "refunds close after 30 days", points at requirements that already exist: find the code that enforces them and read it. With no argument, the target is the plan, spec, brief, or code under discussion in this session. When there's none, say so and stop.

**List the requirements.** A requirement is anything the target says the work must do or must avoid, or anything existing code enforces. A behavior counts, and so does a limit, a default, a validation, a field, a name, or a step. Keep each to one line, in the target's own words. A requirement in code also gets its `file:line`.

**Find each one's source**, from the strongest evidence you can reach:

- **A person decided it.** Give their name and the place it's written down, such as an issue comment or a PR review. Quote it and link it.
- **The code already does it.** Give the `file:line`. Find the commit that introduced the line with `git log -S` or `git log -L`, not `git blame`, which often shows a later reformat. Then follow that commit to its PR, and the PR to the issue or comment that asked for it. Whoever asked is the owner. The commit's author is the owner only when the trail ends at the commit. When a plan keeps this behavior, its requirement is "keep what main does", with the same owner.
- **Something outside forces it**, such as a vendor's API contract or a regulation. Link the document.
- **An agent wrote it**, in an earlier spec, a bot review, or an agent's PR, and no person confirmed it. Mark it **unconfirmed**, and link the text.
- **An agent made it up in a session**, as with a new name or class. Mark it **coined**, and say where it first appeared.

A requirement from a smart or senior person, me included, gets the same scrutiny as anyone else's. Their requirements are the ones least likely to be questioned.

**Question each one.** Rule on every requirement:

- **Keep**: it has a named owner, and it still holds.
- **Ask**: it's unconfirmed or coined, or its owner's reason no longer fits. Write the question for its owner, or for me when there's no owner.
- **Delete**: nothing depends on it, and no one owns it. For code that already runs, "nothing depends on it" needs evidence: search for its callers and the tests that pin it, and check usage data when the session has a query tool for it. Name in the row what removing it would touch. Delete more than feels comfortable. If you never have to add one back, you didn't delete enough.

**Write the report.** Print a table, `requirement · source · owner · verdict · question`, with a link or a `file:line` in the source column for every row. Then list the requirements to settle before anyone builds on them or keeps maintaining them: the Ask rows, with the unconfirmed and coined ones first. Mark each source as measured (you read it) or inferred.

Edit nothing and post nothing. The report is the output.
