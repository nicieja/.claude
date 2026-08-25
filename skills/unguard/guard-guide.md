# Guard guide

The reference `unguard` loads every run. It defines what armor is, the two tests, how a
boundary is scoped, the pattern taxonomy with its default verdicts, the worked cases that
tuned this file, and the searches that find candidates fast. Tune it over time — it is
the spec.

## What armor is

Armor is **generated-but-not-authored defense**: a check, a rescue, a fallback, a retry
written because it looked prudent, not because someone decided it. It is the defensive
twin of slop. Cheap for an agent to add — code with fallbacks passes more runs, so the
training signal rewards it — and expensive for a human to remove later, because deleting
a guard *looks* like a behavior change even when the state is unreachable.

Armor has two costs, and the second is the one that matters:

- **Reading cost.** Every branch is a claim that the state can happen. A reader believes
  the claim and goes looking for the caller that produces it. There isn't one.
- **Truth cost.** A guard that returns a default converts a failure into a plausible wrong
  answer. The system stops crashing and starts lying. Stability bought this way is worth
  nothing: the app is up and the number on the screen is wrong.

So the target is **silence**, not caution. These two defend the same state:

```ruby
return if invoice.nil?                    # silent: the method does nothing, forever
raise ArgumentError, "invoice required"   # loud: the bug has a stack trace
```

The first is armor. The second is a contract. Converting one into the other costs nothing
on any path that actually runs, and it is the most common right answer in this skill.

## The two tests

**The call-site test — is the state reachable?** Name the *production* call site that can
produce it. Search the callers; don't imagine one. A type that cannot hold the state is
proof on its own. A language where everything can be nil proves nothing, so the search is
the only evidence.

**The loudness test — if it happened, who finds out?**

| Silent | Loud |
|---|---|
| `return` / `return nil` on a bad argument | `raise` with the argument named |
| `rescue => e; log(e)` | `rescue => e; log(e); raise` |
| `rescue => e; nil` | a typed failure the caller must handle |
| `value \|\| default`, `value ?? default` | let it fail, or `fetch` |
| optional parameter with a nil default | required parameter |
| `.try(:x)`, `&.x` on a link that can't be nil | `.x` |

**Silent and unreachable → Cut. Silent and maybe reachable → Convert. Loud and cited →
Keep.** There is no fourth square where "leave the silent one alone" is correct.

## Boundaries belong to values

A boundary is a **value crossing into your control** — a request param, a webhook body, a
deserialized blob, an external API response, an argument to a public library method whose
callers you cannot enumerate. Values that qualify:

user input · external responses · deserialization (JSON, YAML, cached blobs, session
data) · queue and job payloads written by another deploy · schemaless or polymorphic
columns · the public surface of a library · a value read across a concurrency window

Three rules keep the boundary map from swallowing the audit — all three were broken in
the runs that produced zero cuts:

1. **One value, one guard, at the first read.** After that the value is validated and
   every later check on it is inside the boundary, and is a candidate.
2. **A boundary licenses a *loud* guard.** Untrusted input earns a refusal — a raise, a
   typed failure, a 400. It never earns a silent default. Armor at a boundary is still
   armor when it swallows.
3. **A service you own is a soft boundary.** One loud validation at entry. It does not
   turn every method behind that entry into boundary code, and "this class moved onto a
   boundary" is not a verdict for the checks inside it.

## The pattern taxonomy

Each pattern carries a default verdict. The default holds unless the guard is already
loud and carries a citation.

### 1. Impossible-state guard → Cut

```ruby
# before — every caller builds the invoice first
def sync(invoice)
  return unless invoice
  return if invoice.number.nil?    # non-null column; and it silently no-ops
  push(invoice.number)
end

# after
def sync(invoice)
  push(invoice.number)
end
```

### 2. Catch-and-default — the silent fallback → Convert, or Ask

```python
# before
try:
    return api.rate(currency)
except Exception:
    return 1.0          # invoices total wrongly, forever, quietly

# after
return api.rate(currency)
```

If the call genuinely needs handling, that is a **product decision** — Ask, with the
options named: raise and alert, use the last known rate and mark the invoice, queue for
retry. Never `1.0`.

### 3. Broad rescue → Convert

```ruby
begin
  report.generate
rescue => e
  Rails.logger.error(e)   # the caller believes it worked
end
```

Log-and-continue is catch-and-default wearing a hat. Re-raise, or say in one comment why
this failure is genuinely ignorable.

### 4. Silent early return → Convert

The single most common piece of armor, and the easiest win. `return if x.blank?` in a
method whose whole job is to do something. Convert to a raise or a typed failure; the
caller learns nothing today.

### 5. Unrequested retry or timeout → Cut, or Ask

Retries change semantics: duplicate charges, duplicate emails, duplicate rows. Cut unless
the user specified them. If the call really is flaky, Ask.

### 6. Re-validation inside a boundary → Cut

The controller validated, the service validates again, the model a third time. Keep the
outermost. Cut the echoes unless an inner one carries an invariant the type doesn't.

### 7. Existence-check spray → Cut or Convert

`obj&.a&.b&.c`, `obj?.a?.b?.c`, `hasattr(x, "y")`, `.try(:name)`, `.respond_to?`. Written
one link at a time, never removed. Usually one link can be nil and three cannot, and the
three hide a real bug in the one. `.try` is worse than `&.`: it swallows a missing method
as well as a nil, so it hides type errors too.

### 8. Shim for a shape that never shipped → Cut

```typescript
const id = payload.id ?? payload.legacy_id ?? payload.data?.id;
```

Cut when the old shape was never written to production. Keep, with a removal date, when a
real migration window is open.

### 9. Kill-switch flag → Cut, or Ask

A config flag so the new path can be turned off. If nobody asked for it, it is armor with
an operations manual attached, and a second code path to maintain forever.

### 10. Over-broad defaults → Convert

```python
def notify(user, subject="", body="", cc=None):
```

A default that invents a value hides a missing argument. Required things should be
required; an empty email is not graceful degradation.

## Worked cases

Both are real verdicts from the first two runs of this skill, and both were wrong.

### Case A — "six tests reach it"

The run proved a parameter guard unreachable in production: one production caller, and
the constructor raises when the value is blank. Then it kept the guard, because **six
tests omitted the argument**.

Wrong. Tests are not production callers. The correct ruling is **Convert** — make the
parameter required — with the six tests named as follow-up work. A test that manufactures
a state production cannot produce is a finding about the test. Keeping armor to protect a
test's convenience is how the armor becomes permanent.

### Case B — "exactly what a bug produces"

The run kept an ownership check with: *the state it defends is exactly what an agent bug
produces.* Every state in every program is what some bug produces; the argument proves
all armor and therefore proves none.

The real question was the loudness test, and the guard passed it — it returned a typed
failure the caller must handle. So the ruling was right and the reasoning was void. Record
the citation, not the story: the polymorphic association with no type restriction, plus
the unique index the mis-aimed write would burn.

The same run kept a check-then-act (*"the turn can close while the model composes"*) under
the concurrency heading. A bare check-then-act closes no window — it narrows it and hides
the remainder. That is a **finding**: either take the lock, lean on the constraint, or
admit the race is unhandled.

## Searches

Every hit is a candidate, never a verdict. Lead with the silence patterns — they are the
highest-value cuts.

- **Ruby** — `rescue nil`, `rescue => e` (then look for a missing `raise`), `return if`,
  `return unless`, `&.`, `.try(`, `.presence ||`, `|| {}`, `|| []`, `retry`,
  `Timeout::timeout`.
- **TypeScript / JS** — `catch (`, `catch {`, `?? `, `?.`, `|| {}`, `|| []`,
  `return;` inside a guard, `as any`.
- **Python** — `except Exception`, `except:`, `contextlib.suppress`, `getattr(`,
  `hasattr(`, `or {}`, `or []`, `if .* is None:\n *return`.
- **Go** — `if err != nil {\n\treturn nil`, `_ = `, `recover()`, `if x == nil { return }`.

Then scope by the boundary rules: the same hit is usually a loud-guard Keep at a first
boundary read, and a Convert or a Cut two layers in.

## The citation list

A Keep needs one of these, cited — not described:

- The first read of an untrusted value, failing loudly.
- A named production call site: `file:line`.
- A real incident, ticket, or a regression test that names what it prevents.
- A constraint the type system cannot carry — polymorphic column, `jsonb`, schemaless
  field — plus the path that writes the odd shape.
- Concurrency where the check actually closes the window: inside a transaction, under a
  lock, or backed by a unique constraint.

Anything else, including every argument on the void list in `SKILL.md`, is a **Convert**.
