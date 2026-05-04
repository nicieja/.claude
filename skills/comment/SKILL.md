---
name: comment
version: 1.0.0
description: |
  Post a markdown comment on a Linear issue using the linear CLI. Pulls material
  from the current conversation (typically findings from an /investigate run),
  formats it as engineering-grade markdown, and posts via `linear issue comment add`.
allowed-tools:
  - Bash
  - Write
---

# Post Linear Comment

Post a markdown comment on a Linear issue, drawing the body from the conversation context.

## Arguments
- `/comment <issue-id-or-url>` — required; the Linear identifier (e.g. `ENG-2217`) or full Linear URL
- `/comment <issue-id-or-url> <extra context>` — fold extra context into the comment alongside what's already in the conversation

## Prerequisites

The `linear` command must be available on PATH. If `linear --version` fails, stop and tell the user to install it (https://github.com/schpet/linear-cli) — do not try to post via curl.

## Instructions

### Step 1: Parse the issue identifier

Accept either form:
- Bare identifier: `ENG-2217`, `ABC-42`
- Full URL: `https://linear.app/<workspace>/issue/ENG-2217/<slug>`

Extract the `[A-Z]+-\d+` identifier. If the input has no recognizable identifier, ask the user for one — do not guess.

### Step 2: Compose the comment body

Source material is the **current conversation** plus any extra context the user passed in args. Typical use is right after an `/investigate` run — the comment should capture the findings the way they were just stated to the user, lightly tightened for a written ticket.

Write GitHub-flavored markdown (Linear renders it). Headings, lists, code spans, and links are all fine.

**Style:**
- Engineering-grade, specific. Name actual file paths, line numbers, model fields, IDs, query shapes — whatever's load-bearing.
- Headed sections are fine when they help structure ("## Root cause", "## Fix recommendation"). Don't force them onto a short comment that doesn't need them.
- Use normal sentence case. Never all-lowercase casual.
- No emojis unless the user asks.
- Don't pad with filler ("Upon investigation we determined that…" — just say what you found).
- If a fix recommendation has alternatives, name them and the tradeoff briefly. Avoid presenting one option as if it were the only option.
- Don't restate the issue body — the reader is on the ticket and can see it. Lead with what the conversation actually added: confirmation, root cause, evidence, recommendation.

**Sensitive data:** real worker/user names from production data should be substituted or omitted unless they're load-bearing for the finding. Workspace names from the original ticket are fine to repeat.

### Step 3: Write to a temp file

Always use `--body-file`, never `--body`. Inline `--body` mangles newlines and special characters in markdown. Write the composed markdown to a tempfile under `${TMPDIR:-/tmp}`, named after the issue (e.g. `/tmp/eng-2217-comment.md`) so it's easy to find if the post fails and you need to retry.

### Step 4: Post the comment

Run:

```bash
linear issue comment add <ID> --body-file <path>
```

The CLI prints a comment URL on success. Surface that URL back to the user as the final reply, on its own line — that's the artifact they want to confirm the post landed.

If the CLI exits non-zero, do not retry blindly. Show the user the error and ask how to proceed (likely an auth issue: `linear auth status` is the first check).

## Key rules

1. **Always use `--body-file`.** Never inline markdown via `--body` — escaping breaks formatting.
2. **Confirm the issue ID** by extracting it explicitly. Don't pass a full URL to the CLI.
3. **Match the conversation.** The comment should reflect what was actually said to the user, not a fresh summary written from a template.
4. **One comment per invocation.** Don't post follow-ups or split into multiple comments unless the user asks.
5. **Surface the comment URL** as the final reply so the user can verify.
