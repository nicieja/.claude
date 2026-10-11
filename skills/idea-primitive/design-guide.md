# Design guide

The reference `/idea-primitive` loads at Step 4. Step 4 settles the primitive with the decision table and the contract sketch. Step 5 tests the design against the red flags, and the naming rules apply to each name the change adds.

## Decision table

Each row is a choice a new concept forces. Settle it with the test in the second column.

| Choice | Test |
|---|---|
| Unify or separate | Variants of one concept share an owner, a lifecycle, and their invariants. Separate concepts differ in at least one of these. Never merge resources into one namespace for symmetry. |
| Field or resource | A field has no identity or lifecycle of its own. Once something gets edited, listed, or permissioned by itself, it's a resource. |
| Enum or reference | Use an enum for a closed set the code branches on, and a reference to a table for a set that users or admins extend. |
| Status or presentation | Keep a status in the model only when it changes which actions are available. When a label changes only the display, it's presentation. |
| Columns or JSON | Columns hold what the code queries or joins on. JSON holds a payload the code stores and hands back without reading. |
| Typed or opaque external value | Type what the code reads. Store what it only passes along as received. |
| Derived state | One owner computes it. A second writer means two sources of truth. |

## Contract sketch

Before building, sketch the smallest contract.

- **The minimum write** takes stable references and the caller's intent, and derives the rest. When the write takes a value the system could compute, the caller's copy and the system's copy can disagree.
- **A useful read** has a current caller for each field. Leave out a field added for completeness until a caller needs it.
- **Growth by addition.** The next field, variant, or caller fits by adding, never by reusing a name, a unit, or an enum value for something new.
- **External effects.** A write sent to another system says how it retries and how a repeat is detected, such as an idempotency key. It also says how an ambiguous outcome gets resolved, like a timeout after the request left.

## Red flags

Read each design as its next contributor will. Assume an agent that sees only the files it opened and copies the nearest example, taking the shortest path that compiles. A design that works only for a careful reader fails that test.

- **Shallow module.** The interface is as complex as the code behind it. A pass-through method that only forwards a call is the small version.
- **Information leakage.** Callers have to know an internal rule, such as the order calls must happen in. Temporal decomposition, which splits code by when it runs instead of by what it knows, leaks the same way.
- **Split ownership.** More than one module writes the same state, so neither can enforce its invariants.
- **A second way to do a task**, with no plan to remove the old one. Strangler-fig and parallel-run (Step 4) are such plans. Without one, delete the old way in the same change, or the next contributor copies whichever way they find first.
- **Importable internals.** Code outside a module can import what the module hides. Make that fail the build where the language allows it.
- **Hand-synced lists.** Lists that must agree, such as an enum and its labels, get edited by hand in more than one place. Derive one from the other, or fail the build when they disagree.

## Naming

Check the existing vocabulary first: routes, modules, published API names, and migrations. Reuse a noun that already means the same idea.

- **One word per concept** across every layer, from the model and the route to the API object, the ID prefix, the event, and the docs.
- **A collision** is the same word used for an unrelated idea. A synonym doesn't fix it, because the next reader still has two words to tell apart. Rename one of them.
- **A qualifier needs a real peer.** `Catalog::Product` and `Inventory::Product` are both real, and each qualifier tells them apart. Without a peer, the qualifier is noise.
- **A resource noun is never also a namespace.** When `product` names a resource, its facets get names like `product_variant` instead of a `product/` namespace.
- **Units go in field names**, like `timeout_seconds` or `amount_cents`.
- **Project conventions** for ID prefixes, event tense, and route style come from the Naming line in `~/.claude/context/<project>/stack.md`.
