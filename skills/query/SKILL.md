---
name: query
version: 1.2.0
description: |
  Generate a single read-only diagnostic script (Rails console, SQL,
  EXPLAIN) to verify or refute a specific claim about runtime state.
  Execute it directly through a confirmed query MCP (Metabase, a
  Postgres/BigQuery connector) when the session has one; otherwise hand
  it to the user for execution. Parse the output and return a verdict
  (Confirmed / Refuted / Inconclusive) with the evidence cited.
---

# Query

Verify a single claim about runtime state. The artifact is a verdict — `Confirmed`, `Refuted`, or `Inconclusive` — with the cited evidence from the query output. The execution channel comes from the project's `stack.md` when present: a confirmed query MCP the skill drives itself, or a console script the user runs by hand and pastes back. The default, absent any confirmed MCP, is the hand-run Rails console.

This skill is **one-shot**. It does not iterate, does not chain follow-ups, does not generate fix scripts. Multi-round diagnostic chains belong in `/investigate`; data mutations belong in `/investigate` Step 4. `/query` produces exactly one script and one verdict.

## Arguments

- `/query <claim>` — the specific claim to verify. Examples:
  - `/query "rows in status 'pending' older than 7 days exist"`
  - `/query "the new query plan does a sequential scan on accounts"`
  - `/query "no Account record has a NULL email"`
- `/query` — with no args, ask once: "What claim do you want to verify?"

## When this is the wrong skill

- Multi-round diagnostic chains (hypothesis → query → refine → query → ...) → use `/investigate`
- Generating a fix or any mutation → never use `/query`; that's `/investigate` Step 4
- Free-form exploration ("what does the data look like?") → that's exploration, not a claim. Refine to a claim first.

## Instructions

Follow these steps in order. Do not skip any.

---

### Step 0: Parse the claim

Identify three things:

- **Assertion** — what's being claimed (count, existence, status distribution, query plan, lock behavior, NULL pattern, association presence)
- **Subject** — the model(s), table(s), or query at stake
- **Smallest evidence** — the smallest output that would confirm OR refute the assertion

If the claim is too vague to pin down all three, ask the caller for one round of clarification, then proceed. Do not write a script for an under-specified claim.

---

### Step 0.5: Resolve the execution channel

Decide who runs the script: you (through a query MCP) or the user (copy-paste into a console).

1. **Read `~/.claude/context/<project>/stack.md`** (`<project>` = repo directory name). If its **Production console** line names a query MCP, use that MCP silently. If it says the human runs scripts (or explicitly rules out an MCP), use handoff mode. Either way, skip the rest of this step.
2. **If stack.md doesn't settle it**, check the current session for MCP tools that can execute remote read-only queries — Metabase, Postgres, BigQuery, Snowflake, and similar connectors. Scan the deferred-tools listing and search with ToolSearch (keywords like "metabase sql query database execute").
3. **If candidates exist, ask once** via AskUserQuestion: one option per candidate MCP, plus "hand scripts to me to run". When the user picks an MCP, offer to record the choice in stack.md's **Production console** line so later runs don't re-ask (update only that line; if stack.md is missing, offer to scaffold it from `context.example/stack.md` per the existing convention).
4. **No candidates, or the user declines** → handoff mode, exactly the classic behavior.
5. **Unattended run with nothing recorded** → never guess. Return `Inconclusive — no execution channel confirmed` and end the skill.

A confirmed MCP channel is for **read-only diagnostics only**. It changes who executes the query, not what the query is allowed to do.

---

### Step 1: Schema check (mandatory for column-level claims)

Before writing any query that names columns, verify them in the schema. A wrong column name is the most common cause of a crashed script.

- Read the owning app's schema for every table you'll touch (`db/schema.rb`, the location named in `~/.claude/context/<project>/stack.md`, or discovered via `**/db/schema.rb`). Read the actual `create_table` block — do not guess column names from model code alone.
- In MCP mode, the queryable schema may differ from the app schema — a Metabase or warehouse connector may expose different table names or a subset of columns. When stack.md says so, or when the MCP offers schema/table-listing tools, verify against that source instead.
- Confirm column types and NULL constraints relevant to the assertion.
- Confirm how subject records are looked up. Identifiers in the claim (slugs, names, URLs) may not be database columns directly.
- For state machines, confirm whether state is a column accessor or an AASM-style helper (`in_state?`, `current_state`).

Skip this step only when the claim is purely about query plans (`EXPLAIN`) over verbatim SQL the caller has provided.

---

### Step 2: Generate ONE read-only script

Generate a single script that produces the smallest evidence from Step 0, in the dialect of the channel from Step 0.5: SQL for a Metabase-style query MCP, ActiveRecord/Ruby for a hand-run Rails console, or whatever flavor stack.md names. The read-only rules below apply verbatim in every dialect.

**Strictly read-only:**

- NO `update`, `save`, `destroy`, `delete`, `create`, `touch`, or any mutation method
- NO assignment to model attributes
- NO `BEGIN; ... ROLLBACK` tricks to test writes
- NO DDL (`ALTER`, `CREATE`, `DROP`)
- NO `system` / shell-out calls

Queries only: `find`, `find_by`, `where`, `pluck`, `count`, `exists?`, `EXPLAIN`, `SELECT`.

**Common Rails / Ruby gotchas (Rails-console mode):**

- **Rails 8 strict pluck/order/select** — raw SQL fragments in `pluck`, `order`, or `select` raise `ActiveRecord::UnknownAttributeReference`. Wrap in `Arel.sql(...)`:
  ```ruby
  state_expr = Arel.sql("locations.address->>'state'")
  scope.pluck(:id, state_expr)
  ```
  In `where`, parameterized SQL strings (`scope.where("col = ?", v)`) are still fine — the rule is specifically about pluck/order/select arguments.
- **Ruby string interpolation can't contain escaped double-quotes** — `"#{Foo.where(\"col = ?\", x).count}"` is a parse error; Ruby treats the inner `\"` as terminating the outer string. Hoist:
  ```ruby
  q = Foo.where("col = ?", x)
  puts "count: #{q.count}"
  ```

**Style:**

- Single-purpose — query exactly what's needed for the verdict, nothing else
- Under 30 lines
- `puts` with clear section labels (`puts "=== Counts ==="`)
- Wrapped in `begin/rescue => e` with `puts e.full_message`
- For early exits, use `raise "descriptive message"` — never `next`, `break`, or `return`, which are syntax errors inside `begin/rescue` in Rails console
- Copy-paste ready — no `<FILL_IN>` placeholders, no setup instructions beyond "paste this"

For raw SQL (psql / `EXPLAIN`), the same read-only rules apply; wrap multi-statement scripts in `BEGIN READ ONLY; ... COMMIT;` if you want belt-and-braces safety.

---

### Step 3: Execute or hand off

**MCP mode** (channel confirmed in Step 0.5):

Execute the query yourself through the confirmed MCP tool and treat its result as the output. Show the user the query you ran alongside the verdict — the query is part of the evidence.

- On an execution error (bad column, dialect mismatch, timeout), fix the query once and retry.
- If it still fails, fall back to the human handoff below (interactive session) or return `Inconclusive — MCP execution failed: <error>` (unattended).
- Never "fix" an error by weakening the read-only rules — a query that only works with a mutation or DDL is not this skill's query.

**Handoff mode:**

Present the script in a fenced code block, then ask for the output:

````
Run this in your Rails console and paste the output:

```ruby
begin
  # [script content]
rescue => e
  puts "ERROR: #{e.full_message}"
end
```
````

Wait for the output. Do not proceed without it. If the user signals verification isn't available — no console access, prod is locked down, "skip this one" — return `Inconclusive` immediately with the reason and end the skill.

---

### Step 4: Analyze and return a verdict

Parse the output. Return exactly one verdict:

- **`Confirmed`** — the output supports the claim. Cite the specific number, row, or plan element.
- **`Refuted`** — the output contradicts the claim. Cite what would have been expected and what was found instead.
- **`Inconclusive — <reason>`** — the output is ambiguous, errored, or doesn't address the claim cleanly. Name what would resolve it (a more targeted query, a different table, missing context).

Output format:

```
**Verdict:** Confirmed | Refuted | Inconclusive — <reason>

**Evidence:** <one or two sentences citing the specific output that supports the verdict>

[For Inconclusive only: one-line suggestion for the next narrowest query]
```

For `Inconclusive`, suggest a next-narrowest query but **do not auto-iterate**. Return control to the caller — they decide whether to invoke `/query` again with a refined claim, escalate to `/investigate`, or accept the inconclusive verdict.

---

## Key Rules

1. **One claim per invocation.** Two claims = two invocations, or use `/investigate` for a chain.
2. **Read-only, always.** Mutations belong in `/investigate` Step 4. No exceptions.
3. **Schema check before script.** Step 1 is mandatory whenever column names appear, with the single carve-out for `EXPLAIN` over verbatim SQL.
4. **Verdict is a single label.** `Confirmed`, `Refuted`, or `Inconclusive`. No hedged "probably" — if it's inconclusive, say so and name what's missing.
5. **Don't auto-iterate.** One script, one output, one verdict. The caller drives any follow-up.
6. **No code edits, no fix scripts.** This skill produces a diagnostic and a verdict. Anything that touches data lives elsewhere.
7. **Direct execution is read-only execution.** A query MCP is never used for mutations, no matter what it's capable of; anything that writes goes through a human-run fix script in `/investigate` Step 4.
8. **The user confirms the channel.** Never start querying production through a connector the user hasn't confirmed for this project — either in this session or recorded in stack.md.
