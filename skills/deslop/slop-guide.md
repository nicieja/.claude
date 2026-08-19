# Slop guide

The reference `deslop` loads every run. It defines what slop is, the markers to look for, the rule for comments, and worked before/after examples. Tune it over time — it is the spec, and the author sharpens it as the tells evolve.

## What slop is

AI slop is **generated-but-not-authored** content: produced without a human applying judgment, review, or ownership. Its signature is the **form of competent work without the substance** — fluent, plausible, hollow. The economics are asymmetric: cheap to generate, expensive to read, verify, and maintain. The cost lands on the reader.

The fix is not cosmetic. Swapping fancy words for plain ones while the emptiness stays is still slop, just less ornate. Deslopping restores **information density** (meaning per unit of reading effort) and **honesty** (claims backed, postures dropped). Work a human shaped and stands behind is not slop, even when AI helped write it. The target is the abdication of judgment, not the tool.

## The compression test (primary instrument)

For any passage, try to cut it by **half** without losing meaning. Whatever drops was slop; what survives is the content. This is the test that matters because it survives paraphrase — you can't pass it by changing vocabulary. Apply it to the longest and densest passages first.

**The inverse failure: dense is not the same as sloppy.** Specific, load-bearing content that reads dense (real numbers, named mechanisms, exact constraints) is not slop, and compressing it into vague summary destroys information. Cut emptiness, not specificity. When a passage is hard to read because it's *packed*, that's an editing problem (break it up), not a slop problem (gut it).

**Estimating the cut.** From a fast first read, predict how much of the input is cuttable — a **range** (e.g. "~25–40%") plus **where it concentrates** (which sections, which kind of slop) — and state it at the top of the diagnosis. It is the **goal the convergence loop works toward** (SKILL.md Step 3), kept honest by two rules:

- **Prediction, not target.** The estimate predicts how much slop is there; it is not a quota to hit. The moment you chase a percentage you start removing words to make the number, and the cheapest words to remove are the specific, load-bearing ones — the inverse failure above. The loop verifies the prediction; it never flattens specificity to satisfy it.
- **Range over point** — a point estimate invites false precision and harder anchoring.

The estimate's job is to **expose a timid cut** — and the loop is what acts on the exposure. So a shortfall is not reported and shrugged off; it is **resolved**. After each pass, measure the actual reduction against the goal:

- if the cut falls short and slop still remains, the prediction was right and the pass was timid — **run another pass** (SKILL.md Step 3);
- if the cut falls short because what's left is genuinely load-bearing, the prediction was high — **revise it down and say why** ("estimated ~30%, cut 18% — the body was denser than the intro implied").

That second line is the only honest way to finish under the estimate. "Estimated ~30%, cut 6%" is never a finding on its own; it is a pass you still owe.

## Prose tells

### Structural — the real target (high confidence)

- **Low information density** — padding, throat-clearing, filler that announces instead of saying.
- **Jargon standing in for information** — technical-sounding nouns stacked until the sentence looks rigorous. Dense jargon is not dense information; the test is whether a reader extracts a checkable claim, not whether every noun is doing grammatical work.
- **Unbacked rhetorical posture** — a sentence that performs the *shape* of an argument it never makes ("the numbers don't add up," "fails at scale," "the math is clear") with no number, threshold, or mechanism behind it. A claim of rigor owes the rigor.
- **Redundancy** — the same point restated across sentences or sections. Cheap to write, expensive to read.
- **Hedging that never decides** — listing options and tradeoffs without committing. Slop enumerates to avoid owning a choice; authored prose decides and says why.

### Surface — cosmetic (low confidence, never proof)

- **Generic AI vocabulary** — *delve, tapestry, realm, testament, showcase, leverage, underscore,* and friends.
- **Em-dash overuse** — the "ChatGPT dash."
- **Monotone cadence** — the relentless "not X, but Y" antithesis, every sentence the same shape.

These are the most-memed tells and the **least reliable**: gameable in one pass, high false-positive rate (strong human writers use all of them), unmeasured, and decaying as a signal. Treat them as a light polish at the end. Never present them as evidence that something is AI-written, and never let fixing them stand in for fixing structure.

## Comment rubric

**Default: no comment.** A comment earns its place ONLY if it does one of:

- explains **why**, not what — a decision or tradeoff the code can't show;
- warns of a **gotcha / footgun** — a non-obvious edge or ordering constraint;
- documents an **invariant or precondition** not visible in the code;
- cites an **external constraint** — a spec clause, bug id, or API quirk;
- explains a **workaround** — with the reason, ideally a ticket.

Everything else is cut. The clearest tell of AI over-commenting is narration: a comment that restates the line below it. Code says *what*; comments exist for *why*.

---

## Prose examples

Fresh and generic by design — illustrative, not drawn from any real document.

**1. Padding / throat-clearing** (low information density)
> ❌ "It's important to note that, in today's fast-paced world, caching is a technique that can be leveraged to significantly improve the overall performance of an application by reducing the need to repeatedly fetch the same data."
> ✅ "Caching improves performance by avoiding repeated fetches of the same data."

34 words to 11, nothing lost. The compression test in one move.

**2. Jargon posing as information**
> ❌ "The naive implementation is non-performant at scale: the abstraction layer instantiates a discrete handle per transaction, the orchestrator serializes all inbound events through a singular execution context, and sustained load precipitates a cascade of redundant state propagations."
> ✅ "The simple version is slow under load: it opens a new connection per transaction, handles events one at a time, and repeats the same state updates over and over."

The jargon sounds rigorous but mostly raises the reader's cost. The plain version transfers the actual argument. Note: "non-performant at scale" promises numbers — if you can't verify the claim from the text, flag it for the author; don't fake a confident paraphrase.

**3. Unbacked rhetorical posture**
> ❌ "The numbers simply don't add up — this approach is a non-starter."
> ✅ (with data) "This needs ~200 writes/sec; the database sustains ~60, so it can't keep up."
> ✅ (without data) "I doubt this keeps up under load, but I haven't measured it."

A sentence that performs the shape of a calculation owes the calculation. Supply it or drop the certainty.

**4. Redundancy**
> ❌ "A queue decouples the services. By putting a queue between them, they no longer call each other directly, which means they're decoupled and can scale on their own."
> ✅ "A queue between the services decouples them, so each scales independently."

The second and third clauses restate the first.

**5. Hedging without a decision** (abdication of judgment)
> ❌ "There are several possible approaches. We could use Redis, or Postgres, or a dedicated queue. Each has tradeoffs, and the best choice depends on various factors."
> ✅ "Use Redis: we already run it and the job volume is well under one instance's capacity. Postgres would add a polling loop; a dedicated queue is more infra than this needs."

Slop enumerates to avoid committing. Authored prose chooses and says why.

**6. Generic AI vocabulary + inflation** (surface — cosmetic)
> ❌ "This release isn't just an update — it's a testament to our commitment, a rich tapestry of features that delve into what users truly need."
> ✅ "This release adds the three features users asked for most: X, Y, and Z."

Delete the style-words, but note: if the sentence still names nothing, vocabulary wasn't the problem. Naming X/Y/Z is the fix that matters.

**7. Em-dash overuse + monotone cadence** (surface — cosmetic)
> ❌ "The tool is fast — really fast — and reliable, scalable, clean — everything you'd want — not a toy, but a tool."
> ✅ "The tool is fast, reliable, and scalable. It's built for real work."

The most-memed tells and the least reliable. Light polish only; never evidence of authorship.

---

## Comment examples

**C1. Obvious narration → cut**
```
# increment the counter
counter += 1
```
→ delete the comment.

**C2. Docstring paraphrasing the signature → cut**
```
# get_user(id): gets the user by id
def get_user(id): ...
```
→ delete; the signature already says it.

**C3. Step scaffolding → cut**
```
# Step 1: loop over the items
# Step 2: return the total
```
→ delete; the code is the steps.

**C4. Commented-out code → cut**
```
# old_total = sum(x.price for x in items)
```
→ delete; git remembers.

**C5. "What" → reword to "why" (borderline)**
```
# sort the list
items.sort(key=lambda x: x.created_at)
```
→ ✅ `# oldest-first: the reconciler applies events in creation order` — but only if that *why* is real; otherwise cut.

**C6. Crucial "why" → keep**
```
# Webhooks can arrive out of order; dedupe by event id before applying.
# Inclusive range — the vendor API counts both endpoints (docs §4.2).
```
→ keep; the code can't say this itself.

**C7. Workaround / gotcha → keep**
```
# WORKAROUND: SDK <v3 throws on empty input; guard until upgrade (TICKET-123).
```
→ keep; it explains a non-obvious guard and points to its end.
