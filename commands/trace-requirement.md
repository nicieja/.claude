---
description: Trace each requirement in a plan, spec, brief, or PR to the person who made it, then question it
argument-hint: "[plan file | PR number | issue id]"
---

## Context

- Arguments: `$ARGUMENTS`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Apply the first two steps of Musk's algorithm to a set of requirements: question every requirement, then delete what doesn't survive. "You need to know the name of the real person who made that requirement." A requirement whose author is a department, a document, or an agent has no owner yet.

**Resolve the target.** A file path is a plan, spec, or brief. A number or a PR URL is a PR, read with `gh pr view` and `gh pr diff`. An issue id is a tracker issue, read through the tracker's MCP tools when the session has them. With no argument, the target is the plan, spec, or brief under discussion in this session. When there's none, say so and stop.

**List the requirements.** A requirement is anything the target says the work must do or must avoid. A behavior counts, and so does a field, a name, or a step. Keep each to one line, in the target's own words.

**Find each one's source**, from the strongest evidence you can reach:

- **A person decided it.** Give their name and the place it's written down, such as an issue comment or a PR review. Quote it and link it.
- **The code on the base branch already does it.** Give the `file:line`. Then the requirement is "keep what main does", and its owner is whoever wrote that code (`git blame`).
- **Something outside forces it**, such as a vendor's API contract or a regulation. Link the document.
- **An agent wrote it**, in an earlier spec, a bot review, or an agent's PR, and no person confirmed it. Mark it **unconfirmed**, and link the text.
- **An agent made it up in a session**, as with a new name or class. Mark it **coined**, and say where it first appeared.

A requirement from a smart or senior person, me included, gets the same scrutiny as anyone else's. Their requirements are the ones least likely to be questioned.

**Question each one.** Rule on every requirement:

- **Keep**: it has a named owner, and it still holds.
- **Ask**: it's unconfirmed or coined, or its owner's reason no longer fits. Write the question for its owner, or for me when there's no owner.
- **Delete**: nothing depends on it, and no one owns it. Delete more than feels comfortable. If you never have to add one back, you didn't delete enough.

**Write the report.** Print a table, `requirement · source · owner · verdict · question`, with a link or a `file:line` in the source column for every row. Then list the requirements to settle before anyone builds on them: the Ask rows, with the unconfirmed and coined ones first. Mark each source as measured (you read it) or inferred.

Edit nothing and post nothing. The report is the output.
