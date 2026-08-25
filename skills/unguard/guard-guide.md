# Guard guide

The reference `unguard` loads every run. It defines what armor is, the test that
licenses a cut, the boundaries that are never cut, the pattern taxonomy with worked
examples, and the searches that find candidates fast. Tune it over time — it is the
spec, and the author sharpens it as the patterns evolve.

## What armor is

Armor is **generated-but-not-authored defense**: a check, a rescue, a fallback, a retry
written for a state the code cannot reach. It is the defensive twin of slop. Cheap for an
agent to add — code with fallbacks passes more runs, so the training signal rewards it —
and expensive for a human to remove later, because deleting a guard *looks* like a
behavior change even when the guarded state is unreachable.

Two costs, and the second is the one that matters:

- **Reading cost.** Every branch is a claim that the state can happen. A reader who
  believes the claim goes looking for the caller that produces it. There isn't one. They
  lose the afternoon.
- **Truth cost.** A guard that returns a default converts a failure into a plausible wrong
  answer. The system stops crashing and starts lying. Stability bought this way is worth
  nothing — the app is up and the number on the screen is wrong.

Defense a human decided on is not armor, whatever it looks like. The target is the
guess, not the guard.

## The call-site test (primary instrument)

For each candidate, ask: **which caller can produce the state this defends?**

- **You can name one** → Keep. Done, no further argument.
- **You looked and there is none** → Cut. "Looked" means a search over the callers, quoted
  in the evidence column — not an impression.
- **You can't tell** → Keep. Uncertainty resolves toward the guard, always.

The test survives taste, which is why it is the instrument. Short code is not the goal;
honest code is. A run that keeps every guard and can say why each one is reachable has
done the job.

**The inverse failure: defended is not the same as over-defended.** Code at a system
boundary is *supposed* to look paranoid. Validation there is the design, not the debris.
Stripping it produces exactly the bug class this skill claims to prevent, and it produces
it in the one place where the input is hostile. When a file reads defensively and sits on
a boundary, that is a well-built file — say so and cut nothing.

**Type systems count as evidence.** In a language where the type cannot be null, a null
check is unreachable by construction and needs no call-site search. In a language where
everything can be nil, the type proves nothing and the search is the only evidence.

## The boundary map

A guard is right by default at every one of these, and none of them are candidates:

- **User input** — form params, query strings, request bodies, CLI arguments, uploaded
  files.
- **External responses** — third-party APIs, webhooks, callbacks, anything over a network
  you don't own.
- **Deserialization** — JSON, YAML, CSV, protobuf, cached blobs, session data, anything
  that was a string a moment ago.
- **Queues and jobs** — payloads enqueued by an older deploy, retried out of order, or
  written by another service.
- **Storage of unguaranteed shape** — schemaless columns, `jsonb`, legacy rows written
  before a constraint existed.
- **The public surface of a library** — callers you cannot enumerate, by definition. The
  call-site test can't be run, so the guard stays.
- **Concurrency and time** — a check that exists because a value can change between two
  reads is not defending a state, it's defending an interleaving.
- **Anything with a comment or a test naming the incident it came from.** Somebody paid
  for that guard.

Inside the boundary — service objects, models, private methods, code whose callers you can
list — the call-site test applies.

## The pattern taxonomy

### 1. Impossible-state guard

A check for a value the callers cannot pass.

```ruby
# before — every caller builds the invoice first
def sync(invoice)
  return unless invoice
  return if invoice.number.nil?
  push(invoice.number)
end

# after
def sync(invoice)
  push(invoice.number)
end
```

Note the second line's real damage: `return` on a nil number means the method *silently
does nothing*. The bug survives, without a trace.

### 2. Catch-and-default — the silent fallback

The highest-value cut in this guide.

```python
# before
def exchange_rate(currency):
    try:
        return api.rate(currency)
    except Exception:
        return 1.0          # <- invoices now total wrongly, forever, quietly

# after
def exchange_rate(currency):
    return api.rate(currency)
```

If the call really can fail and the failure needs handling, that is a **product
decision** — verdict *Ask*, with the options named: raise and alert, use the last known
rate and mark the invoice, or queue for retry. Never pick one silently, and never pick
`1.0`.

### 3. Broad rescue

```ruby
# before
begin
  report.generate
rescue => e
  Rails.logger.error(e)     # swallowed; the caller believes it worked
end

# after
report.generate
```

Log-and-continue is catch-and-default wearing a hat. Either the caller must know
(re-raise) or the failure is genuinely ignorable (say why, in one comment).

### 4. Unrequested retry or timeout

```typescript
// before — nobody asked for this, and 3 attempts on a non-idempotent POST is a bug
for (let i = 0; i < 3; i++) {
  try { return await post(order); } catch { await sleep(500); }
}
```

Retries change semantics: duplicate charges, duplicate emails, duplicate rows. Cut unless
the user specified them, or Ask.

### 5. Re-validation inside a boundary

The controller validated. The service validates again. The model validates a third time.
Keep the outermost one, cut the echoes — unless the inner one is a genuine invariant the
type doesn't carry.

### 6. Defensive copy

```ruby
items = raw_items.dup   # nothing mutates it
```

Cut when no callee mutates. Keep when one does, or when the object crosses a boundary you
don't control.

### 7. Existence-check spray

`obj&.a&.b&.c`, `obj?.a?.b?.c`, `hasattr(x, "y")`, `.try(:name)`, `.respond_to?`. Written
one `&.` at a time, never removed. Ask which link in the chain can actually be nil;
usually one can and three cannot, and the two extra hide a real bug in the one.

### 8. Shim for a format that never shipped

```typescript
// before — v1 payloads never existed outside this branch
const id = payload.id ?? payload.legacy_id ?? payload.data?.id;
```

Cut when the old shape was never written to production. Keep, with a removal note, when a
real migration window is open.

### 9. Kill-switch flag

A config flag added so the new path can be turned off. If the user didn't ask for it,
it's armor with an operations manual attached — and a second code path to maintain
forever. Cut, or Ask.

### 10. Over-broad defaults

```python
def notify(user, subject="", body="", cc=None):
```

A default that invents a value hides a missing argument. Required arguments should be
required; an empty email is not a graceful degradation.

## Search patterns

Fast candidate-finding, per language. Every hit is a candidate, never a verdict.

- **Ruby** — `rescue`, `rescue nil`, `&.`, `.try(`, `.presence ||`, `|| {}`, `|| []`,
  `return if .*\.nil\?`, `retry`, `Timeout::timeout`.
- **TypeScript / JS** — `?.`, `?? `, `catch (`, `catch {`, `|| {}`, `|| []`, `try {`,
  `setTimeout.*retry`, `as any`.
- **Python** — `except Exception`, `except:`, `getattr(`, `hasattr(`, `or {}`, `or []`,
  `if .* is None: return`, `contextlib.suppress`.
- **Go** — `if err != nil {\n\treturn nil`, `_ = `, `recover()`, `if x == nil { return }`.

Then filter by the boundary map before you rank anything: a hit inside a request handler
is usually a Keep, and the same hit in a service object usually isn't.

## The keep-list

Never cut, whatever the search says:

- Anything on the boundary map.
- A guard with a comment, a test, or a ticket naming the incident behind it.
- A check the type system doesn't make redundant, where the callers can't be enumerated.
- A guard in code you were not asked to touch. Scope is scope.
- Anything where the call-site test came back uncertain.
- Anything encoding a product decision about failure — that is an **Ask**, not a Cut,
  even when you're confident which option is right.
