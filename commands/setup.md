---
description: Arm this session's recurring loops from the project's routine prompts
allowed-tools: Read, Glob, Bash(ls:*)
---

## Context

- Project: the current repo's directory name. Routine prompts live in
  `~/.claude/context/<project>/routines/*.md`.

## Your task

Arm the project's recurring loops in **this session**:

1. Read every routine file. Each may open with a schedule comment on its first
   line — `<!-- schedule: <5-field cron> -->` or `<!-- schedule: interactive-only -->`.
2. For each routine with a cron schedule, create a recurring session job
   (CronCreate) whose prompt is the file's body and whose cadence is the file's
   cron expression. Skip files marked interactive-only or carrying no schedule
   line, and say why in one line each.
3. Report what was armed — cadence and routine name per job — plus the standing
   caveats: jobs are session-only, fire while this session is idle, and expire
   within 7 days, so re-run /setup when you reopen the window.

If the project has no routines directory, say so and stop. Never schedule a
routine the file marks interactive-only — that marker exists because the loop
isn't cleared for unattended writes yet.
