# Comment guide

The rules `/code-uncomment` applies, through the `comment-editor` agent or
inline. They come from Comment Sicko in Lauren Tan's pstack, without the
persona.

## Deletion by default

Agents copy what they see near the line they're writing. A comment that explains
a workaround becomes the template for the next workaround, and an agent will
cite a nearby comment as the reason to paper over a problem instead of fixing
it. A comment that explains a surprise in our own code is a sign the code should
change, so the comment goes and the code gets flagged.

## The keep list

Keep a comment only when it is one of these:

- A license or legal header.
- A constraint forced by something we can't reshape: an external dependency, a
  platform, a vendor API, or a protocol. A surprise in our own code doesn't
  count.
- A directive a tool reads, such as `prettier-ignore`. A lint suppression has
  its own rule below.
- A doc comment that defines a public API contract.
- A link to an issue or an RFC, for a constraint the code can't express.

When you aren't sure a keep applies, the comment goes. Never shorten or reword a
comment to make it fit the list. A comment is kept verbatim or deleted.

## A surprise in our own code

When a comment explains behavior of our own code that a reader wouldn't expect,
delete the comment and flag the exact symbol that needs to change:

```
MUST KILL <file>:<line> <symbol> · <rename | extract | type | rework> · <one line on what to change>
```

Writing the flag ends your part, because the editor never changes code.

## Lint suppressions

`rubocop:disable`, `rubocop:todo`, `eslint-disable`, `biome-ignore`,
`@ts-ignore`, `@ts-expect-error`, `noqa`, and `type: ignore` all count. Look up
the rule each one suppresses.

- **The rule is wrong here, pedantic, or style-only**: keep the suppression, and
  say which of those it is.
- **The rule protects correctness or safety**: delete the suppression, and flag
  the symbol it was hiding with `MUST KILL`.

## Comments that only sound weighty

"IMPORTANT", "do not remove", "too risky", "fine for now", "temporary", "hack",
and a long justification are leads to check. They don't prove anything. Before
the verdict, read the code around the comment. If its claim isn't obvious there,
check it with `git log -S'<symbol>'`, `git blame`, the linked issue, and the
call sites.

- Keep it only when the check proves a keep-list case that holds today, on a
  path that still runs.
- When the comment states a constraint about our own code ("do not change this
  wording", "talk to X before changing"), delete it and list it under
  Constraints, with the claim it made. `/code-uncomment` encodes it as a test or a check, or reports it as open.
- When doubt remains after the check, delete it.

## Scope

Work only in the scope the brief gives. In a diff scope, that means the comments
on lines the diff adds. A comment a teammate wrote before the diff is out of
scope, even in a file the diff touches.

## Report

Return these parts, with no summary around them:

- **Deleted**: per file, the count and one line per comment, `file:line · reason`.
- **Flags**: the `MUST KILL` lines.
- **Suppressions**: one line per suppression, `file:line · rule · kept or deleted · reason`.
- **Kept**: per comment, `file:line · the keep-list case it proves`.
- **Constraints**: the constraint comments you deleted, with the claim each made.
- **Skipped**: anything in scope you didn't decide, with the reason.

## Examples

**Narration: delete.**
```
# increment the counter
counter += 1
```

**A docstring that repeats the signature: delete.**
```
# get_user(id): gets the user by id
def get_user(id): ...
```

**Step scaffolding: delete.** The code is the steps.
```
# Step 1: loop over the items
# Step 2: return the total
```

**Commented-out code: delete.** Git keeps the history.
```
# old_total = sum(x.price for x in items)
```

**A why about our own design: delete and flag.**
```
# sort oldest first: the reconciler applies events in creation order
items.sort(key=lambda x: x.created_at)
```
→ `MUST KILL app/reconcile.py:42 items.sort · extract · move the ordering into the reconciler, which owns it`

**An external constraint: keep.**
```
# The vendor API counts both endpoints of the range (docs §4.2).
# Webhooks from the payment provider arrive out of order; dedupe by event id.
```

**A workaround for a dependency, with its ticket: keep.**
```
# SDK < v3 throws on empty input; remove this guard after the upgrade (TICKET-123).
```

**A suppression that hides a correctness rule: delete and flag.**
```ruby
user.update_column(:status, "active") # rubocop:disable Rails/SkipsModelValidations
```
→ `MUST KILL app/models/user.rb:88 update_column · rework · this skips validations and callbacks; call update! or justify the skip in the model`

**A style-only suppression: keep.**
```ruby
def build_payload # rubocop:disable Metrics/MethodLength
```
