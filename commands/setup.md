---
description: Arm this session's scheduled routines, and print the start command for each loop
allowed-tools: Read, Glob, Bash(ls:*)
---

## Context

- Project: the current repo's directory name. Routine prompts live in
  `~/.claude/context/<project>/routines/*.md`, and
  `~/.claude/context.example/routines/README.md` documents them.

## Your task

Arm the project's routines in **this session**:

1. Read every top-level routine file except `README.md`. Each may open with a
   schedule comment on its first line: `<!-- schedule: <5-field cron> -->`,
   `<!-- schedule: loop -->`, or `<!-- schedule: interactive-only -->`.
2. For each routine with a cron schedule, create a recurring session job
   (CronCreate) whose prompt is the file's body and whose cadence is the file's
   cron expression.
3. Don't create a job for a loop. Print its start command,
   `/loop follow ~/.claude/context/<project>/routines/<name>.md`, for me to run.
   When `routines/<name>/lock` exists, print its line too, so I can see whether
   another session runs the loop.
4. Skip files marked interactive-only or without a schedule line, and say why
   in one line each.
5. Report what was armed (cadence and routine name per job), the loop start
   commands, and the skipped files, plus the standing caveats: jobs are
   session-only, fire while this session is idle, and expire within 7 days, so
   re-run /setup when you reopen the window.

If the project has no routines directory, say so and stop. Never schedule a
routine the file marks interactive-only. That marker exists because the loop
isn't cleared for unattended writes yet.
