---
name: prototype
version: 1.0.0
description: |
  Build the smallest working version of an idea to answer one specific
  question — fast. The code is throwaway; the learnings it surfaces are
  the artifact. Use when /shape's questions can't be answered in the
  abstract and you need to see something running before judging it.
  Surfaces learnings in conversation, never writes a doc.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - WebFetch
---

# Prototype

Build the smallest possible working version of an idea to surface answers that abstract discussion can't. The code is throwaway — its job is to make the idea tangible enough to judge. Learnings come back in the conversation, not a file. After this skill runs, you'll usually loop back to `/shape` with sharper inputs, or run `/prototype` again with a sharper question.

## Arguments
- `/prototype <seed>` — prototype the idea in the seed (a sentence, a paragraph, a Slack pitch)
- `/prototype` — bare; ask once *"What do you want to prototype?"*

## When this is the wrong skill
- The proposal already has clear answers and you want a refined plan → `/shape`
- You're diagnosing an active production issue → `/investigate`
- You want to extract learning from work that already shipped → `/retro`
- You want hours/days for a known scope → `/estimate`

## Instructions

Follow these steps in order. Skip steps that genuinely don't apply, but never silently drop work — say so in the output.

---

### Step 0: Preflight

1. **Capture the seed.** If invoked as `/prototype <text>`, that's the seed. If bare, ask once: *"What do you want to prototype?"* Don't proceed without a seed.

2. **Decide where it lives.** Two cases:
   - **In-app feature** — a new feature inside an existing codebase. Lives where the feature would naturally live in the app's tree. Throwaway property comes from being *easy to rip out*: one entry point, ideally one feature flag or route, minimal touching of existing code.
   - **Standalone idea** — net-new, no existing app to extend. Lives in `<repo-root>/prototypes/<slug>/` (fall back to `~/.claude/prototypes/<slug>/` if not in a git repo, and tell the user). Slug is lowercase, hyphen-separated, ≤60 chars, derived from the seed's first meaningful noun phrase.

   If the case isn't obvious from the seed, ask once: *"Is this a new feature inside this codebase, or a standalone idea?"*

---

### Step 1: The one question

Ask via AskUserQuestion: *"What's the one question this prototype is built to answer?"*

This is the **stop condition**. When the prototype can answer it, you stop building. Without it, prototypes balloon into half-implementations.

Good questions are specific:
- *"Does the LLM produce coherent retro output from a real PR?"*
- *"Is OpenRouter's latency acceptable for our chat flow?"*
- *"Does this layout work on mobile when the title is long?"*

Push back once on too-broad questions before proceeding:
- *"Does the feature work?"* — too vague
- *"Can we build X?"* — that's a planning question, not a prototype question

---

### Step 2: Light codebase scan

For **in-app prototypes**, use Read / Glob / Grep to find existing types, utilities, and conventions worth reusing. Just enough to wire the prototype in cleanly — not deep. That's `/investigate`'s job.

For **standalone prototypes**, skip this step.

---

### Step 3: Build the smallest thing

Hard rules:

- **Hardcoded data** — no real DB, auth, or external services unless that's literally what's being tested
- **No tests, no error handling** beyond what's required to make it run
- **Single command to run it**
- **Inline data, no abstractions** — extract nothing
- **Comments only where a real version would diverge significantly** (e.g., `# real version paginates`, `# real version needs auth`)
- **In-app:** one entry point, ideally a feature flag or route; minimize touching existing files
- **Standalone:** lives in the prototype dir from Step 0

Build until the one question can be answered. Stop there.

---

### Step 4: Run it

Show the user how to run it:
- **Script** — exec it directly and show output
- **UI** — start the dev server, give the URL/path
- **LLM call** — run once with a real-ish input and show output
- **Service** — provide curl or a one-liner

If running it surfaces something the prototype itself doesn't yet show (latency numbers, model output quality, layout glitches), capture that in Step 5.

---

### Step 5: Surface learnings (in conversation)

Once the prototype runs, summarize in the conversation — no file:

- **The question** — exactly as asked in Step 1
- **The answer** — what running the prototype told us
- **What surprised** — anything that ran differently than expected
- **What changed about the proposal** — concrete revisions to the original idea
- **Open questions** — what the prototype didn't answer that still matters
- **Abstraction call** — does the shape that emerged suggest the right design, or did it expose that the model is wrong?

Be specific. *"The LLM output was inconsistent on PRs with >20 comments"* beats *"it kind of worked"*.

---

### Step 6: Hand off

End with: *"This code is throwaway — the value is in the answers above. Next: `/shape <updated proposal>` with what we learned, or `/prototype` again with a sharper question."*

---

## Key Rules

1. **Code is throwaway.** No commits, no tests, no polish. Don't suggest merging or productionizing the prototype as-is.
2. **Stop when the one question is answered.** Don't over-build. If the question can't be answered yet, sharpen it — don't expand scope.
3. **In-app prototypes minimize touching existing code.** One entry point, ideally one feature flag or route. The throwaway property comes from being easy to rip out.
4. **Standalone prototypes live in `<repo-root>/prototypes/<slug>/`.** Fall back to `~/.claude/prototypes/<slug>/` only when not in a git repo, and tell the user.
5. **Learnings live in conversation, not a file.** The artifact is the message.
6. **One question per AskUserQuestion call.** Never batch.
7. **Never modify existing tests.** A prototype isn't a refactor.
8. **Don't lecture.** This is a build-and-learn loop, not an essay on prototyping.
