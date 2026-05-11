---
name: investigate
version: 1.0.0
description: |
  Investigate production issues by exploring the codebase and generating
  Rails console scripts for diagnosis and fixes. Iterative workflow:
  explore code, generate read-only diagnostic script, analyze output,
  generate fix script with dry-run safety.
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Production Issue Investigation

Generate Rails console scripts to diagnose and fix production issues. You explore the codebase, generate read-only diagnostic scripts for the user to run, analyze the output, and iterate until the root cause is found and fixed.

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

### Step 1: Explore the Codebase

This step is MANDATORY before generating any script. Use Read, Glob, and Grep to build a domain model understanding.

**1a. Find relevant models**
- Search `app/models/**/*.rb` for models matching domain terms
- Read each relevant model file completely

**1b. Map the domain**
For each relevant model, note:
- Associations (`belongs_to`, `has_many`, `has_one`, polymorphic)
- State machines (`aasm`, `enum`, custom state columns)
- Validations and callbacks (especially `before_save`, `after_commit`)
- Scopes that might be useful for querying
- Any STI or polymorphic patterns

**1c. Check the schema (MANDATORY)**
- Read `db/schema.rb` for every table you plan to query. Read the actual `create_table` block — do not guess column names from model code alone.
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

Pick the claim to verify in this round and invoke `/query` with it as the argument. `/query` handles schema verification, script generation, the user handoff, and verdict parsing — its single artifact is one of `Confirmed`, `Refuted`, or `Inconclusive` with cited evidence.

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

When the user pastes back console output:

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

---

## Key Rules

1. **Never treat the bug report as ground truth.** A report describes what someone observed — it may be incomplete, misattributed, or wrong. The first diagnostic script must verify the reported symptoms against actual data. Do not hypothesize root causes until you've confirmed the problem exists as described.
2. **Never generate a fix without diagnosis.** At least one diagnostic script must be run and its output analyzed before proposing any mutation.
3. **Never apply code fixes during an investigation.** This skill produces diagnostic and fix *scripts* for the user to run. Do not edit application code, modify serializers, change prompts, or make any code changes yourself. If the investigation reveals a code-level fix is needed, describe it — do not apply it.
4. **Always explore the codebase first.** Step 1 is mandatory. Never guess at model names, column names, or associations.
5. **Each script is independently runnable.** No shared state between scripts. A user should be able to copy-paste any single script and have it work.
6. **Scripts must be copy-paste ready.** No placeholders like `<FILL_IN>`. Use the actual identifiers from the issue. No setup instructions beyond "paste this in Rails console."
7. **Diagnostic scripts are read-only. No exceptions.** If you need to test a write, that's a fix script with dry_run.
8. **When in doubt, gather more data.** Another diagnostic script is always safer than a premature fix.
