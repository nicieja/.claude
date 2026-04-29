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

# /investigate — Production Issue Investigation

Generate Rails console scripts to diagnose and fix production issues. You explore the codebase, generate read-only diagnostic scripts for the user to run, analyze the output, and iterate until the root cause is found and fixed.

## User-invocable
When the user types `/investigate`, run this skill.

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

### Step 2: Generate Diagnostic Script

Generate a Rails console script that gathers information to confirm or refute your hypothesis.

**First script priority: verify the reported symptoms.**
A bug report is a claim, not a fact. Before investigating *why* something is broken, confirm *that* it is broken and *how*. The first diagnostic script should query the actual records mentioned in the report and check whether the data matches what was described. If the reported symptoms don't match reality, the investigation changes direction entirely.

**Pre-check — verify every column name against `db/schema.rb` before writing any script:**
Before writing the script, re-read the model files AND the `db/schema.rb` table definition for every model you plan to query. For each column name you use in `find_by`, `where`, `pluck`, `order`, or `select`, confirm it exists in the schema. This is non-negotiable — a single wrong column name will crash the script in production. Pay attention to:
- Actual column names in the schema — never guess (e.g., `key` vs `slug`, `type` vs `kind`)
- Whether a field is a direct column vs. stored inside a JSONB store
- Whether state is managed by a state machine (with methods like `in_state?`, `current_state`) vs. a plain column accessor
- How models are associated — don't assume standard names like `.user` or `.name`; check the actual `belongs_to`/`has_many`/`has_one` declarations
- How records are looked up — identifiers in the issue (slugs, names, URLs) may not correspond to database columns. Read the schema to find the actual lookup column (e.g., the table may use `key` or `id` instead of `slug`)

**Script rules — diagnostic scripts are STRICTLY READ-ONLY:**
- NO `update`, `save`, `destroy`, `delete`, `create`, `touch`, or any mutation method
- NO assignment to model attributes
- Queries only: `find`, `find_by`, `where`, `pluck`, `count`, `exists?`, etc.
- Wrapped in `begin/rescue => e` with `puts e.full_message`
- For early exits, use `raise "descriptive message"` (caught by rescue) — never `next`, `break`, or `return`, which are syntax errors in a `begin/rescue` block in Rails console
- Uses `puts` with clear section labels (e.g., `puts "=== Account Details ==="`)
- Under 80 lines
- Each variable and query has a brief inline comment explaining why it's needed
- Independently runnable — no dependencies on previous scripts

**Output format:**

````
Here's a diagnostic script to run in Rails console:

```ruby
begin
  # [script content]
rescue => e
  puts "ERROR: #{e.full_message}"
end
```

Please run this in your Rails console and paste the output back here.
````

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
