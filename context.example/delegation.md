# Delegation for <project>

The executors that can build work for me in this project, and how each one
gets its brief and returns its result. `/work-delegate` and the `/work-triage` Build stage read this
file. Without it, the only executor is a local subagent.

## Executors

| Executor | Dispatch | What it can read | Results come back as | Use it when |
|---|---|---|---|---|
| Local subagent | The Agent tool, in a worktree, in the background | This repo and `~/.claude` skills | Changes in its worktree | The work needs a `~/.claude` skill |
| `codex exec` | `git worktree add`, then `codex exec -C <worktree> "<brief>"` | This repo, its skills, `~/.claude/AGENTS.md`, and the `~/.claude` skills that `bin/setup --apply` links, though steps that use Claude-only tools don't run | Changes in its worktree | Work that doesn't need a `~/.claude` skill, run beside other work. Delete the row when Codex isn't installed |
| <cloud agent> | <the exact recipe, such as "create an issue in team X, assignee me, delegate Y"> | <this repo and its skills, or more> | <a PR attached to the issue, comments on the issue> | <when> |

## Brief rules for this project

Rules every brief here adds to `brief-guide.md`, such as "one PR per tool" or
the PR headings a project skill requires. Each rule cites the PR or the date it
came from. When a routine writes briefs from its own template, that template is
the only copy of the rules, and this section points to it. A lesson the routine
adds there then goes into the next brief.

## Holds

Where held work waits, and how it's marked, such as a "Hold" section at the top
of the issue and no delegate set.

## Pickup

- How to list delegated work, such as a tracker query.
- How a result shows up, such as the issue's status changes and the PR link.
- How to restart an executor that stopped, and the channel it reads, such as a
  reply in its session thread when it ignores top-level comments.
- How to tell whether a run is still going, when the tracker has no field for it.
- How long the executor keeps reacting to CI and reviews on its own.
- The branch names and the commit author on its work.
- Where to check a PR out locally, such as `../<repo>.<branch-slug>`.
- What the executor can't do on its own, such as a check that runs only locally.
