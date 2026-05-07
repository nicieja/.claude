---
allowed-tools: Bash(gh pr list:*), Bash(gh pr view:*), Bash(date:*)
description: Prepare a standup status update from a seed
---

## Context

- Today's date: !`date +%Y-%m-%d`
- My PRs in the last 7 days: !`gh pr list --author "@me" --state all --search "created:>=$(date -v-7d +%Y-%m-%d)" --limit 50 --json number,title,state,createdAt,mergedAt,url`

## Your task

The user is preparing a standup update. Their seed — what they want the update to be about — is:

$ARGUMENTS

Combine the seed with the PR data above to write a status update of **1–3 short cohesive paragraphs**. Use the seed to scope which PRs are relevant; drop the ones that don't fit the theme. Reference PR numbers inline (e.g. `#450`) and note merged vs. open where it matters. If you need more on a specific PR, run `gh pr view <number>`.

**Style:**

- Cohesive prose sentences, not bullet lists.
- Humanized and conversational — suitable to paste into a standup channel.
- Group merged work and in-flight work naturally; call out the theme tying things together if there is one.
- Concise. Three paragraphs is a ceiling, not a target — one tight paragraph is often better.
- No headers, no preamble like "Here's your update:". Just the update.
