---
description: Explain something plainly, from restating the last reply to walking through code, a PR, a plan, or a commit
argument-hint: "[question | PR number | plan file | path] [step by step]"
allowed-tools: Read, Grep, Glob, Agent, Bash(git log:*), Bash(git show:*), Bash(git diff:*), Bash(gh pr view:*), Bash(gh pr diff:*)
---

## Context

- Arguments: `$ARGUMENTS`

## Your task

Explain it so I understand it, not so it sounds complete. This is read-only, so don't edit or post anything.

**Pick the mode from the arguments.**

- **None:** restate your last message plainer and shorter. Keep its meaning and its hedges, and add nothing new.
- **A question about code**, like "how does checkout calculate tax": explain how it works.
- **A PR, plan, file, or commit:** walk me through it.
- **`step by step`** anywhere in the arguments: number the steps and give each its own paragraph.

**How code works.** Read the code yourself for a simple question. A question that spans several subsystems gets 2 to 4 read-only Explore agents in parallel, each starting from a different entry point. Ask each one for the components it found, the flow, the files it read, the boundaries, anything surprising, and what it couldn't trace. Merge their reports, and settle a contradiction by reading the code yourself. Never infer behavior from a name. The write-up has an overview, the key concepts, how it works, where things live, and the gotchas when there are some. How it works is the longest part, and it's prose.

**Walking through a change or a plan.**

1. Pick the few things I need to take away, from why I'm asking and what I already know. Read both from the conversation, and don't quiz me.
2. Open with a plain definition and the thing's common name, then tie it to this case.
3. Explain the mechanism, the reasons it's built this way, and the edge cases.
4. Give the smallest complete answer first, then offer to go deeper on a named thread.

**Diagrams.** When several parts move, draw a series of small diagrams in code blocks, each adding one part to the last. One big diagram at the end works as a reference, but it doesn't explain anything.

**Keep the language plain.**

- Short sentences, and one name for each thing. Define a term the first time it appears, or use an everyday word instead.
- Use the concrete class, function, or table, not "the service".
- Keep the hedges from the evidence, like "probably" or "the logs suggest". They're findings, not filler.
- Stop when the explanation ends, and list the threads I could follow next. Skip any recap of what you just said.
