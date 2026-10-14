# Decisions for <project>

The calls in force for this project, one entry per decision, grouped by topic. Each entry
states the rule as it stands now. Record the why when the call is made, not later.

`~/.claude/context/` is a git repo of its own, and git keeps the history. To change a
decision, edit its entry in place, and update the files that cite it in the same commit. The
commit message says what changed and why. Fix a wrong fact the same way. `bin/check --context`
fails a dated log line, and an entry that points at another entry instead of editing it.

`<who>` names the decider. For my own call, give my name, and quote my words when they settle
it. When an agent inferred the decision, write `<agent>'s reading of <what I said>`.

A call that binds one PR or issue goes on that issue or PR, where its executor reads it, and
into the ledger's Answered cell when a loop asked the question. Only the standing rule that
such a call implies becomes an entry here.

Other files cite an entry by its heading, as `(decisions: <heading>)`, in lowercase if you
like, because case doesn't matter to the check. Copy an entry's text only where its reader
can't open this file, such as a brief for a cloud agent, and put the cite beside the copy.

## <Topic>

### <The decision, in a few words>

<The decision as it stands, written so an agent can follow it.>

- Why: <the reason>
- Decided: <YYYY-MM-DD of the last change>, <who>[: "<the decider's words>"]
- Revisit when: <the trigger>
