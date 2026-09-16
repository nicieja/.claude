---
allowed-tools: Bash(gh pr list:*), Bash(gh pr view:*), Bash(date:*)
description: Prepare a standup status update from a seed
---

## Context

- Today's date: !`date +%Y-%m-%d`
- My PRs in the last 7 days: !`gh pr list --author "@me" --state all --search "created:>=$(date -v-7d +%Y-%m-%d)" --limit 50 --json number,title,state,createdAt,mergedAt,url`

## Your task

The user is preparing a standup update. Their seed (what they want the update to be about) is:

$ARGUMENTS

Use the seed to pick which PRs are relevant, and drop the rest. For each PR you plan to feature, read its description with `gh pr view <number>`. The impact language you need is usually in the body rather than the title. Don't parrot PR titles. Translate them into what changed for the user or the system.

**Shape:**

- Open with a thesis when the work has a unifying frame (e.g. "Merged four PRs that address the dominant failure modes…"). Skip the thesis when there isn't one, and don't manufacture cohesion.
- Group by *kind of change* or *impact theme*, not by directory or merge status. Give each group a short label ("Model upgrade." "Slimmer record expansions.") followed by a short paragraph explaining the problem, the change, and the impact.
- One-liner standups are fine. A multi-item release update is also fine. Length follows the work, not a target.
- Close with what's next when the seed mentions it, and a candid risk note when the seed mentions blockers, slips, or distractions. Skip both otherwise.

**Style:**

- Humanized and conversational, suitable to paste into a standup channel.
- Reference PR numbers (e.g. `#450`) only when they help the reader navigate to something still open or in review. Don't cite every PR by default.
- Start with the update itself, without a "Here's your update:" lead-in. It's a Slack message: paragraphs and the short group labels from above, nothing heavier.
