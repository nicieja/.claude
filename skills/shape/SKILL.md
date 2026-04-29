---
name: shape
version: 1.0.0
description: |
  Shape unshaped Linear issues by investigating the codebase, asking clarifying
  questions, and posting structured shaping comments back to the issue.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - AskUserQuestion
---

# /shape — Linear Issue Shaping

Pull unshaped issues from Linear, investigate the codebase for each, ask clarifying questions, and write a structured shaping comment back on the issue.

## User-invocable
When the user types `/shape`, run this skill.

## Arguments
- `/shape` — shape all unshaped issues assigned to you
- `/shape ENG-123` — shape a single specific issue

## External tool

Uses the `linear` CLI (https://github.com/schpet/linear-cli). Do NOT use `./linear.toml` — rely on global config or env vars.

Key commands:
- `linear issue list --sort priority` — user's unstarted issues
- `linear issue view <ID>` — full issue details
- `linear issue comment list <ID>` — list comments
- `linear issue comment add <ID> --body-file <path>` — post comment via temp file

## Instructions

Follow these steps in order. Do NOT skip steps.

---

### Step 0: Preflight

1. Verify the `linear` CLI is installed:
   ```bash
   which linear
   ```
   If not found, tell the user to install it and stop.

2. If a single issue ID was provided as an argument (e.g. `/shape ENG-123`), skip directly to Step 2 for that issue.

3. Otherwise, run:
   ```bash
   linear issue list --sort priority
   ```

4. If the command fails with a team error, run `linear team list` and use AskUserQuestion to ask the user which team to use. Then retry with `--team <key>`.

---

### Step 1: Filter to Unshaped Issues

1. For each issue from the list, run:
   ```bash
   linear issue comment list <ID>
   ```
   Check if any comment starts with `🛠️`. If it does, the issue is already shaped — skip it.

2. Filter down to unshaped issues only.

3. Present a table to the user:
   ```
   | # | ID      | Title                    | Priority |
   |---|---------|--------------------------|----------|
   | 1 | ENG-123 | Add user export feature  | Urgent   |
   | 2 | ENG-456 | Fix billing calculation  | High     |
   ```

4. If zero unshaped issues remain, say so and stop.

5. Use AskUserQuestion to ask: "Ready to shape N issues?" with options: **Start** / **Done for now**

---

### Step 2: Investigate Each Issue

Before starting each issue (except the first), use AskUserQuestion to ask: **Shape** / **Skip** / **Done for now**

For each issue to shape:

1. Get full issue details:
   ```bash
   linear issue view <ID>
   ```

2. Extract domain terms from the issue title and description — model names, feature areas, business concepts.

3. Do a **light** codebase exploration using Read, Glob, and Grep:
   - Models in `app/models/` matching domain terms
   - Services in `app/services/` matching domain terms
   - Schema in `db/schema.rb` for relevant tables
   - Controllers, jobs, concerns as needed

4. **Keep it light** — identify which files matter and what they do. Do not map every callback, scope, or association. This is shaping, not debugging.

---

### Step 3: Ask Clarifying Questions

- Ask **at most 2-3 questions** per issue, one per AskUserQuestion call (never batch).
- Focus on: scope, approach, business context, edge cases.
- **Skip this step entirely** if the issue description + code exploration make the path clear enough.

---

### Step 4: Draft & Post Shaping Comment

1. Compose the shaping comment in this exact format:

```
🛠️ Notes

## Summary
[1-2 sentences describing what needs to happen and why]

## Relevant Code
- `path/to/file.rb` — description of what it does and why it matters

## Implementation Notes
[approach, files to change, sequence of work]

## Considerations
- [edge cases, risks, dependencies, things to watch out for]
```

2. Show the full draft to the user. Use AskUserQuestion to ask: **Post** / **Edit** / **Skip**

3. If **Post**: write the comment body to a temp file and post it:
   ```bash
   TMPFILE=$(mktemp)
   # Write comment body to $TMPFILE
   linear issue comment add <ID> --body-file "$TMPFILE"
   rm -f "$TMPFILE"
   ```
   Always clean up the temp file after posting.

4. If **Edit**: accept the user's feedback, revise the draft, and ask again (Post / Edit / Skip).

5. If **Skip**: move on to the next issue without posting.

---

### Step 5: Next or Done

- After each issue, use AskUserQuestion before the next: **Shape** / **Skip** / **Done for now**
- When all issues are processed (or the user says Done), show a summary table:

```
| ID      | Title                   | Status  |
|---------|-------------------------|---------|
| ENG-123 | Add user export feature | Shaped  |
| ENG-456 | Fix billing calculation | Skipped |
```

---

## Key Rules

1. **Never post without user approval** — always show the full draft and get explicit confirmation before posting.
2. **One question at a time** — never batch multiple questions into a single AskUserQuestion call.
3. **Keep exploration light** — this is shaping, not debugging. Identify which files matter, not every detail.
4. **Use `--body-file` for comments** — never pass comment bodies inline to avoid shell escaping issues.
5. **Clean up temp files** — always `rm -f` the temp file after posting.
6. **Shaped marker is `🛠️ Notes` on the first line** — always check for this when filtering, and always include it when posting.
7. **Handle missing CLI and team context gracefully** — check for the CLI first, handle team errors with a prompt.
