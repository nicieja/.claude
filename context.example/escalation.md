# Escalation for <project>

Agents stop and surface to the user instead of proceeding when:

- the work turns out to touch a T3 surface (see risk-tiers.md)
- an instruction conflicts with observed reality (spec says X, code does Y)
- a required credential, access, or data source is missing
- two sources of truth disagree and the resolution isn't recorded anywhere
- cost or time is running far past what the brief implied

## Channels

- Interactive session: say it plainly and stop.
- Unattended run: write the item into the run report, and never resolve it silently.
- Paging (optional): <Slack channel / notification recipe, if configured>

## Outward actions

`~/.claude/AGENTS.md` sets the default list of what goes ahead without asking, under "When to act
and when to confirm". This section widens or narrows it for this project. Leave it out to keep the
default.

- Allowed without asking: <such as "create issues in team X, assigned to me and delegated to the
  cloud agent", or "signed comments on PRs from my delegated issues">
- Needs my OK here, though the default allows it: <such as "status changes in project Y">

### <routine name>

A routine in `routines/` gets its own subsection. Its scope is <such as one tracker project, with the PRs attached
to its issues>. Inside that scope, it may do these without asking:

- <such as "create and edit issues assigned to me">
- <such as "push to a PR's branch, never forced">

It never <what stays mine, such as merging, or closing an issue or a PR>.
