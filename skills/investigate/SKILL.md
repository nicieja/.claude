---
name: investigate
version: 1.2.0
description: |
  Investigate production issues by exploring the codebase and generating
  read-only diagnostic queries — executed directly through a confirmed
  query MCP (Metabase, a Postgres connector) when the session has one,
  or as console scripts the user runs by hand (Rails console by default;
  the project's stack.md can override). Iterative workflow: explore code,
  run a read-only diagnostic, analyze output, generate fix script with
  dry-run safety. Fix scripts are always human-run.
---

# Production Issue Investigation

Diagnose and fix production issues through read-only diagnostics and human-run fix scripts (Rails console by default — see the project-context step below). You explore the codebase, generate read-only diagnostic queries — executed through a confirmed query MCP when one exists, handed to the user to run otherwise — analyze the output, and iterate until the root cause is found and fixed.

## Arguments
- `/investigate <description>` — issue description, ticket URL, or bug report
- `/investigate` — with no args, ask the user to describe the issue

## Instructions

Follow these steps in order. Do NOT skip steps. Do NOT generate any script before completing Step 1.

---

### Step 0: Parse the Issue

Extract from the user's input:
- **Identifiers**: names, IDs, URLs, slugs, email addresses, account names — anything that uniquely identifies the affected record(s)
- **Symptoms**: what's happening vs what should be happening (expected vs actual behavior)
- **Domain terms**: model names, status values, feature areas, job names, queue names

Present a brief summary back to the user:

```
**Issue summary**
- Record(s): [identifiers]
- Expected: [what should happen]
- Actual: [what is happening]
- Domain: [relevant models/features]
```

If critical information is missing (e.g., no identifier to look up), ask for it before proceeding.

---

### Step 0.5: Load project context

Read `~/.claude/context/<project>/stack.md` if it exists (`<project>` = repo directory
name). Take from it: the console flavor and access mode — including a query MCP for
direct read-only execution, if one is recorded — the schema location(s), and the
architecture reading order. If the file is missing, ask once whether to scaffold
it from `context.example/stack.md`, then proceed with defaults: Rails console, human
runs scripts and pastes output, schema discovered by glob.

Channel detection and confirmation live in `/query` (its Step 0.5), not here — when no
channel is recorded, the first `/query` invocation detects candidate MCPs, asks the
user once, and records the answer in stack.md. Every later invocation in this
investigation reuses it silently.

In a monorepo, identify the owning app before exploring: follow the architecture
reading order from stack.md, or look for a services index / architecture doc at the
repo root. Scope every subsequent path in this skill to that app.

---

### Step 1: Explore the Codebase

This step is MANDATORY before generating any script. Use Read, Glob, and Grep to build a domain model understanding.

**1a. Find relevant models**
- Search the owning app's models directory (e.g. `app/models/**/*.rb`, or `<app>/app/models/**/*.rb` in a monorepo) for models matching domain terms
- Read each relevant model file completely

**1b. Map the domain**
For each relevant model, note:
- Associations (`belongs_to`, `has_many`, `has_one`, polymorphic)
- State machines (`aasm`, `enum`, custom state columns)
- Validations and callbacks (especially `before_save`, `after_commit`)
- Scopes that might be useful for querying
- Any STI or polymorphic patterns

**1c. Check the schema (MANDATORY)**
- Read the owning app's schema for every table you plan to query — `db/schema.rb`, or the location stack.md names; discover with a glob like `**/db/schema.rb` when unsure. Read the actual `create_table` block — do not guess column names from model code alone.
- Note column types, defaults, null constraints, and indexes
- Identifiers from the issue (slugs, URLs, names) often don't map to column names. Confirm how records are actually looked up before writing any query.

**1d. Find related code**
- Search for services (`app/services/`), concerns (`app/models/concerns/`), jobs (`app/jobs/`), workers, and controllers that touch these models
- Focus on code paths that relate to the reported symptoms

**1e. Summarize understanding**
Before generating any script, present your domain understanding:
- Which models and tables are involved
- How they relate to each other
- What state transitions or workflows are relevant
- Your hypothesis for what might be wrong

These are **hypotheses, not conclusions**. Code reading tells you what *could* happen; only production data tells you what *did* happen. Do not state root causes at this stage — state what you suspect and what the diagnostic script needs to verify.

---

### Step 2: Generate Diagnostic Script via `/query`

Pick the claim to verify in this round and invoke `/query` with it as the argument. `/query` handles schema verification, script generation, execution — direct through the confirmed query MCP, or handed to the user to run — and verdict parsing. Its single artifact is one of `Confirmed`, `Refuted`, or `Inconclusive` with cited evidence.

**First script priority: verify the reported symptoms.**
A bug report is a claim, not a fact. Before investigating *why* something is broken, confirm *that* it is broken and *how*. The first invocation of `/query` should target the reported symptoms against the actual records mentioned in the report. If the reported symptoms don't match reality, the investigation changes direction entirely.

**On each iteration, pick one claim** — the narrowest assertion that, if confirmed or refuted, moves the investigation forward. Examples:

- `/query "account 'acme' has status 'suspended' and updated_at < 2026-01-01"`
- `/query "Subscription has rows where account_id is NULL"`
- `/query "the index `index_payments_on_account_id_and_status` is being used by the new query"`

Subsequent iterations refine the hypothesis based on Step 3 analysis. Do not invoke `/query` with the same claim twice — refine first.

**What `/query` returns:**

- **`Confirmed`** — the hypothesis under test is now a fact. Carry it into Step 3 and decide the next hypothesis.
- **`Refuted`** — the hypothesis was wrong. Carry that into Step 3 and re-orient.
- **`Inconclusive — <reason>`** — Step 3 decides whether to invoke `/query` again with a refined claim, expand to multi-claim exploration outside `/query`'s one-shot remit, or escalate.

`/query` enforces the script-craft rules (read-only, schema-checked, copy-paste-ready) so this step stays focused on hypothesis selection. The full script-writing rules live in `/Users/kamil/.claude/skills/query/SKILL.md`.

---

### Step 3: Analyze and Iterate

When query output returns (executed via the MCP, or pasted back by the user):

1. Parse the output carefully, noting any unexpected values or nil fields
2. Cross-reference with your codebase understanding from Step 1
3. Determine if you have enough information to identify the root cause

**If more information is needed:**
- Explain what the output revealed and what's still unclear
- Generate another diagnostic script (following Step 2 rules)
- Each iteration should narrow the investigation — never re-query the same data

**If root cause is identified:**
- State the root cause clearly
- Explain the causal chain: what happened, why it happened, and what state is now wrong
- Proceed to Step 4

---

### Step 4: Generate Fix Script

Only generate a fix AFTER at least one diagnostic script has been run and the root cause is confirmed.

Fix scripts are **always human-run**. The query MCP is never used to apply a fix — not even in dry-run form. A mutation goes through the user's own console session, with the safety structure below.

**Script structure:**

````
Here's the fix script. Run it first with `dry_run = true` (the default) to verify, then change to `false` to apply.

```ruby
dry_run = true

begin
  ActiveRecord::Base.transaction do
    # === Safety Checks ===
    # Verify the record is in the expected bad state before modifying.
    # If any check fails, abort with a clear message.

    record = Model.find(id)
    unless record.status == "bad_state"
      puts "ABORT: Record is not in expected state (status=#{record.status}). No changes made."
      raise ActiveRecord::Rollback
    end

    # === Before State ===
    puts "=== Before ==="
    puts "status: #{record.status}"
    # [other relevant attributes]

    # === Apply Fix ===
    record.update!(status: "correct_state")

    # === After State ===
    record.reload
    puts "=== After ==="
    puts "status: #{record.status}"
    # [other relevant attributes]

    if dry_run
      puts "\n[DRY RUN] Rolling back. Set dry_run = false to apply."
      raise ActiveRecord::Rollback
    else
      puts "\n[APPLIED] Changes committed."
    end
  end
rescue ActiveRecord::Rollback
  # Expected in dry-run mode, swallow silently
rescue => e
  puts "ERROR: #{e.full_message}"
end
```
````

**Fix script rules:**
- `dry_run = true` at the very top — user must explicitly change to `false`. Use a local variable, NOT a constant, so it can be reassigned in the same console session
- Wrapped in `ActiveRecord::Base.transaction`
- Safety checks BEFORE any mutation: verify the record is in the expected broken state
- Before/after comparison with `puts` for every changed attribute
- `raise ActiveRecord::Rollback` when `dry_run` is true
- If fixing multiple records, process them in a loop with per-record safety checks and output
- Under 100 lines
- Independently runnable
- For non-Rails consoles (per stack.md), preserve the same safety structure: an explicit dry-run flag defaulting to on, a transaction or equivalent rollback path, safety checks before any mutation, and before/after output.

---

## Key Rules

1. **Never treat the bug report as ground truth.** A report describes what someone observed — it may be incomplete, misattributed, or wrong. The first diagnostic script must verify the reported symptoms against actual data. Do not hypothesize root causes until you've confirmed the problem exists as described.
2. **Never generate a fix without diagnosis.** At least one diagnostic script must be run and its output analyzed before proposing any mutation.
3. **Never apply code fixes during an investigation.** This skill produces read-only diagnostics and fix *scripts* for the user to run. Do not edit application code, modify serializers, change prompts, or make any code changes yourself. If the investigation reveals a code-level fix is needed, describe it — do not apply it.
4. **Always explore the codebase first.** Step 1 is mandatory. Never guess at model names, column names, or associations.
5. **Each script is independently runnable.** No shared state between scripts. A user should be able to copy-paste any single script and have it work.
6. **Scripts must be copy-paste ready.** No placeholders like `<FILL_IN>`. Use the actual identifiers from the issue. No setup instructions beyond "paste this in Rails console."
7. **Diagnostic scripts are read-only. No exceptions.** If you need to test a write, that's a fix script with dry_run.
8. **Fix scripts are always human-run.** A confirmed query MCP grants read-only diagnostic access, nothing more. Never execute a mutation through it, no matter what it's capable of.
9. **When in doubt, gather more data.** Another diagnostic script is always safer than a premature fix.
