# Design guide

The reference `/idea-primitive` loads at Step 4 of a review and at the start of the design mode. The decision table and the contract sketch settle the primitive. The red flags test the design, and the naming rules apply to each name the change adds.

## Decision table

Each row is a choice a new concept forces. Settle it with the test in the second column.

| Choice | Test |
|---|---|
| Unify or separate | Variants of one concept share an owner, a lifecycle, and their invariants. Separate concepts differ in at least one of these. Never merge resources into one namespace for symmetry. |
| Field or resource | A field has no identity or lifecycle of its own. Once something gets edited, listed, or permissioned by itself, it's a resource. |
| Workflow or new model | Approval, progress, and pending changes go to the modules that already define them. A new model needs state and invariants that no existing model has. |
| Enum or reference | Use an enum for a closed set the code branches on, and a reference to a table for a set that users or admins extend. |
| Status or presentation | Keep a status in the model only when it changes which actions are available. When a label changes only the display, it's presentation. |
| Optional fields or variants | When a field is valid only alongside another, model the variants as distinct types, such as a tagged union or a sealed type. A flag the code could derive from another field gets derived: `shipped` comes from `shipped_at`, and the two can't disagree. Each match over the variants is exhaustive, and a new variant then fails the build at every missing case. |
| Columns or JSON | Columns hold what the code queries or joins on. JSON holds a payload the code stores and hands back without reading. |
| Typed or opaque external value | Type what the code reads. Store what it only passes along as received. |
| Derived state | One owner computes it. A second writer means two sources of truth. |
| Shared writes | Concurrent writers each get their own key, row, file, or branch, and the results merge where they're read. A lock, or one writer for everyone, is for a value every writer must agree on, such as an account balance. |

## Contract sketch

Before building, sketch the smallest contract.

- **Variants.** Test the design against each variant it must support today, plus one extreme variant. When it needs a flag or a special case to fit a variant, a concept is missing. Build only today's variants.
- **The minimum write** takes stable references and the caller's intent, and derives the rest. When the write takes a value the system could compute, the caller's copy and the system's copy can disagree.
- **A useful read** has a current caller for each field. Leave out a field added for completeness until a caller needs it.
- **One ordinary call.** Write the call a caller makes today, as a request or a method call. When that call needs explaining, the names or the defaults are wrong.
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
- **A value no one can trace.** A new reader can't answer "where does this value come from?" and "what can change it?" within 30 seconds. Cut a layer, or shrink the state that can change the value. A pass-through wrapper is a common cause, and a value copied by hand into a second place is another.

## Naming

Check the existing vocabulary first: routes, modules, published API names, and migrations. Reuse a noun that already means the same idea.

- **One word per concept** across every layer. The casing, plurals, and tense on each layer follow the project's conventions, and this table shows one common style:

  | Layer | Example |
  |---|---|
  | Model | `Catalog::Product` |
  | Route | `/v1/catalog/products` |
  | API object | `catalog.product` |
  | ID prefix | `prod_` |
  | Event | `catalog.product.created` |
  | Docs and errors | "catalog product" |

- **A collision** is the same word used for an unrelated idea. A synonym doesn't fix it, because the next reader still has two words to tell apart. Rename one of them.
- **A qualifier needs a real peer.** `Catalog::Product` and `Inventory::Product` are both real, and each qualifier tells them apart. Without a peer, the qualifier is noise.
- **A resource noun is never also a namespace.** When `product` names a resource, its facets get names like `product_variant` instead of a `product/` namespace.
- **A child resource nests under its parent** when it's created and changed along with the parent, as order lines do at `/orders/{id}/lines`. When it moves through its own states while the parent doesn't change, it gets a top-level collection with a parent filter, as shipments do at `/shipments?order_id=`. An ID of its own, or being editable by itself, doesn't make a child independent.
- **One route per resource.** A nested alias next to the top-level collection is a second route.
- **Units go in field names**, like `timeout_seconds` or `amount_cents`.
- **The set of allowed values gets a different name from the chosen value**, like `allowed_currencies` and `currency`.
- **A permission covers what a user is granted**, such as `orders:write`, and not every model or action behind it. Once released, it remains until a migration maps the users who have it.
- **Released names are contracts.** Renaming a route, an event, an ID prefix, or a stored enum value changes a contract that callers depend on. That call is mine, per "Decisions that are mine" in `~/.claude/AGENTS.md`.
- **Project conventions** for ID prefixes, event tense, and route style come from the Naming line in `~/.claude/context/<project>/stack.md`.

Finish with one pass over each layer the change touches:

- the model
- write and read parameters
- the route and the API object
- IDs
- permissions
- events
- docs and error messages

The noun keeps one meaning, each layer uses its own separators, and helper names reuse the noun.
