---
name: comment
version: 1.1.0
description: |
  Post a markdown comment on a Linear issue via the Linear MCP tools. Pulls
  material from the current conversation (typically findings from an
  /investigate run) and formats it as engineering-grade markdown.
allowed-tools: []
---

# Post Linear Comment

Post a markdown comment on a Linear issue, drawing the body from the conversation context.

## Arguments
- `/comment <issue-id-or-url>` — required; the Linear identifier (e.g. `ENG-2217`) or full Linear URL
- `/comment <issue-id-or-url> <extra context>` — fold extra context into the comment alongside what's already in the conversation

## Linear access

Use the Linear MCP tools — they're deferred, so load them via ToolSearch (search
"linear") before first use, and phrase calls by capability (create a comment on an
issue) rather than assuming exact tool names. If only authentication stubs are
available, the server needs its OAuth flow run once — offer to run it. If no Linear
MCP tools are available in this session, stop and say so — do not try to post via
curl or any other side channel.

## Instructions

### Step 1: Parse the issue identifier

Accept either form:
- Bare identifier: `ENG-2217`, `ABC-42`
- Full URL: `https://linear.app/<org>/issue/ENG-2217/<slug>`

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

**Sensitive data:** real user names from production data should be substituted or omitted unless they're load-bearing for the finding. Account names from the original ticket are fine to repeat.

### Step 3: Post the comment

Create the comment through the Linear MCP tools, passing the composed markdown as
the tool's string argument — one call, the whole body.

The tool result includes the comment (and its URL when the server returns one).
Surface that back to the user as the final reply, on its own line — that's the
artifact they want to confirm the post landed.

If the tool call fails, do not retry blindly. Show the user the error and ask how
to proceed (an expired authentication is the likely cause — offer the OAuth flow).

## Key rules

1. **Pass the body as one markdown string through the MCP tool.** Never assemble it through shell interpolation — that's how markdown gets mangled.
2. **Confirm the issue ID** by extracting it explicitly before calling the tool. Don't pass a full URL as the identifier.
3. **Match the conversation.** The comment should reflect what was actually said to the user, not a fresh summary written from a template.
4. **One comment per invocation.** Don't post follow-ups or split into multiple comments unless the user asks.
5. **Surface the comment URL** (or the tool's returned confirmation) as the final reply so the user can verify.
