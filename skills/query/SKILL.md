---
name: query
version: 1.0.0
description: |
  Generate a single read-only diagnostic script (Rails console, SQL,
  EXPLAIN) to verify or refute a specific claim about runtime state.
  Hand it to the user for execution, parse the output, and return a
  verdict (Confirmed / Refuted / Inconclusive) with the evidence cited.
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Query

Verify a single claim about runtime state. The artifact is a verdict — `Confirmed`, `Refuted`, or `Inconclusive` — with the cited evidence from output the user pastes back.

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

### Step 1: Schema check (mandatory for column-level claims)

Before writing any query that names columns, verify them in the schema. A wrong column name is the most common cause of a crashed script.

- Read `db/schema.rb` for every table you'll touch. Read the actual `create_table` block — do not guess column names from model code alone.
- Confirm column types and NULL constraints relevant to the assertion.
- Confirm how subject records are looked up. Identifiers in the claim (slugs, names, URLs) may not be database columns directly.
- For state machines, confirm whether state is a column accessor or an AASM-style helper (`in_state?`, `current_state`).

Skip this step only when the claim is purely about query plans (`EXPLAIN`) over verbatim SQL the caller has provided.

---

### Step 2: Generate ONE read-only script

Generate a single script that produces the smallest evidence from Step 0.

**Strictly read-only:**

- NO `update`, `save`, `destroy`, `delete`, `create`, `touch`, or any mutation method
- NO assignment to model attributes
- NO `BEGIN; ... ROLLBACK` tricks to test writes
- NO DDL (`ALTER`, `CREATE`, `DROP`)
- NO `system` / shell-out calls

Queries only: `find`, `find_by`, `where`, `pluck`, `count`, `exists?`, `EXPLAIN`, `SELECT`.

**Common Rails / Ruby gotchas:**

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

### Step 3: Hand off and wait

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
