# Brief guide

How to write a brief for an executor that doesn't remember this session: a
cloud agent, `codex exec`, a local subagent, or another model. The brief is the
whole handoff. `/work-delegate` and the `/prompt` command both write their
briefs by this guide.

There are two forms: a full brief for an executor that is new to the task, and
a follow-up for one that already worked on it.

A brief is instructions to an executor, never the plan itself. A restatement, a
summary, or a reordering of a plan's steps counts as the plan, so if the brief
could be mistaken for the plan, start over.

## The full brief

Use these headings, in this order. Leave a section out only when it would be
empty.

1. **Hold.** Only when the work waits on something, such as an unmerged PR or
   another issue. Start the brief with "Do not dispatch this yet." Then give
   what it waits on, and what to recheck on the base branch once it merges.
2. **Goal.** One paragraph on what will be true when the work is done, and for
   whom. For a missing capability, say what can't happen today, and why.
3. **Decisions so far.** The calls already made, each with its date and who
   made it, and the line "Do not stop on them." The executor treats them as
   settled.
4. **What to change.** Each change as the behavior or the design it needs, in
   words, one bullet each.
5. **Before you start.** The facts the executor would otherwise rediscover the
   slow way, as flat statements with file pointers. These include the files
   that matter, the files that look relevant but aren't, the approaches tried
   and rejected, the conventions the work assumes, and the gotchas. Tell the
   executor to recheck each fact on the base branch before relying on it.
6. **Setup.** The exact commands to fetch and branch from the base. When the
   base isn't the default branch, say the change is stacked, and that the PR
   targets the base and must not include the base's own commits.
7. **The plan.** When a plan file exists: "Read `<path>` before you start. It
   is the spec." When the executor's checkout won't have the file, paste its
   full text here instead, and cite the path. Never both.
8. **Steps.** A numbered list. Give the path of the repo's own skill to run at
   each step, such as `skills/<name>`.
9. **Verification.** The commands and checks that prove the work, and the
   success criteria.
10. **Rules.** Always include these, in these words or close to them:
    - *Write the code the task needs, and no armor around it. Validate at the
      system boundary and trust what you find inside. Do not add guards for
      states no caller can produce, and do not catch-and-default. Leave out
      retries, timeouts, and flags nobody asked for. Prefer a loud failure with
      a good message.*
    - *Obey every stop in the skills. At a stop, open a draft PR, and say in it
      what a person must decide.*
    - *In the PR, list each place where a skill was wrong, unclear, or missing
      a step.*

    Add the scope limits the work implies, such as what not to touch or
    refactor in passing.
11. **Deliverable.** Small commits with imperative subjects, and a PR against
    the base branch. The final report lists what was built, what was skipped
    and why, and each place the work departed from the plan.

## The follow-up

When the executor already worked on this task, as with its own PR or the issue
it holds, it already has everything a full brief would repeat. Send only what's
new, in a few lines. Say what to change and why, and add each decision made
since its last brief, with who made it. Leave out every section it already received.

A follow-up that needs more than a few short paragraphs means the task changed,
so write a full brief instead.

## Voice

- Address the executor as "you". Be imperative and specific, without hedging.
- **Describe behavior and design in words, without code.** The executor picks
  the names of the classes, methods, and files it creates. Its code then
  matches its own style and the repo's conventions. A name that already exists
  in the repo gets its path. A name or an interface a person decided goes under
  "Decisions so far", stated in words. Code samples help a person judge a design before the
  brief is written, and they stay out of the brief.
- Don't describe this session: no "we decided", no "the user said", no agent
  names. State outcomes as facts.
- Refer to the repo's own skills when a step needs one. A skill from
  `~/.claude` stays out of the brief, because the executor can't load it.
- Don't use the words `robust`, `production-ready`, `bulletproof`,
  `comprehensive`, or `handle all edge cases`. Say what must not break instead.
- Keep it as long as the work needs. Generic advice about testing or code
  quality doesn't belong in it.
- Use short, simple sentences, because the executor may be a different model,
  or a person.
