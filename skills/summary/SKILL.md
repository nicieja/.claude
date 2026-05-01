---
name: summary
version: 1.1.0
description: |
  Write a humanized summary for an investigation but on the stuff that we found and the entire convo so that i can copy paste it into Slack for other people to understand the root cause and steps taken to mitigate.
allowed-tools: []
---

# /summary — Slack-Ready Investigation Summary

Write a quick, natural summary of what happened during the investigation so the user can drop it into Slack and people get it immediately.

## Arguments
- `/summary` — no args; pull everything from the conversation
- `/summary <extra context>` — weave in extra details (ticket links, user counts, timelines, etc.)

## Instructions

Look back through the entire conversation. Pull out what matters: what broke, why, what we did about it. Then write it up like a human would in Slack — not a report, not a template, just a clear explanation.

Do NOT use any tools. Everything you need is in the conversation.

---

### Writing style

This is the most important part. The summary should read like a real person typed it into Slack after fixing something. Think "engineer updating the team in #incidents", not "AI generating a structured report".

**Do this:**
- Write in flowing prose/paragraphs, not a rigid section-by-section template
- Use first person plural naturally ("we dug in", "turns out", "we found that", "fixed it by")
- Let the structure emerge from the story — if the investigation was simple, the summary should be short. If it was a journey, tell that story
- Be specific about the technical details — name the actual models, fields, values, code paths
- It's fine to be a little casual ("so basically", "the culprit was", "long story short")
- Contractions are good. Sentence fragments are fine when they land.
- If something was surprising or non-obvious, say so ("we initially thought X but it turned out to be Y")
- **Use normal sentence case.** Capitalize the first word of every sentence and proper nouns. Casual tone comes from word choice, contractions, and rhythm — never from dropping capitalization. All-lowercase output reads as twee/affected, not casual.

**Don't do this:**
- Don't use rigid headers like "*What happened:*", "*Root cause:*", "*Steps taken:*" — that's the AI-report smell
- Don't use bullet points for everything — mix prose and bullets naturally like a person would
- Don't start with a formulaic title like "*Investigation Summary —*" every time. Start with whatever feels right: the punchline, the context, or a quick "heads up, we just dealt with X"
- Don't pad with filler ("Upon investigation we determined that..." — just say what you found)
- Don't be overly formal or overly structured
- No emojis in every section. One or two max if they feel natural, zero is also fine.
- Don't use "Key Findings", "Action Items", "Impact Assessment" or any corporate-report language

**Slack formatting basics** (use Slack mrkdwn, not GitHub markdown):
- Bold: `*text*`
- Italic: `_text_`
- Code: backticks
- No `#` headers — bold lines work if you need a label
- Bullets: `-` when you need a list, but don't force everything into lists

---

### What to cover

Don't think of these as sections to fill in. Think of them as the questions someone reading Slack would want answered:

- What was going on? (the symptom / how it was noticed)
- What was actually wrong? (root cause — be specific)
- How bad was it? (scope — who/what was affected)
- What did we do? (the fix, and whether it's fully rolled out or still in progress)
- Anything left to do? (follow-ups, only if there are any)

Weave these into a natural narrative. Some summaries will be 5 lines. Some will be 15. Match the complexity of the incident.

---

### Edge cases

- If the investigation isn't done yet, say so up front. Share what's known and what the current thinking is.
- If no fix was applied yet, explain the root cause and what the plan is.
- If the user passes extra context in the args, fold it in naturally.

---

### Output

Wrap the final message in a code fence so it's easy to copy the raw Slack mrkdwn. Just put "Copy this into Slack:" above it.

## Key Rules

1. **Never use tools.** Everything comes from conversation context.
2. **Use Slack mrkdwn**, not GitHub markdown.
3. **Be specific.** Actual model names, field values, IDs, code paths. Vague summaries help no one.
4. **Write as the user.** This is their message to their team.
5. **No template smell.** Every summary should feel like it was written from scratch for this specific incident. If it looks like it was generated from a template, rewrite it.
