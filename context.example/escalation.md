# Escalation — <project>

Agents stop and surface to the user — rather than proceeding — when:

- the work turns out to touch a T3 surface (see risk-tiers.md)
- an instruction conflicts with observed reality (spec says X, code does Y)
- a required credential, access, or data source is missing
- two sources of truth disagree and the resolution isn't recorded anywhere
- cost or time is running far past what the brief implied

## Channels

- Interactive session: say it plainly and stop.
- Unattended run: write the item into the run report; never resolve it silently.
- Paging (optional): <Slack channel / notification recipe, if configured>
