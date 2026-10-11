# Resolutions for <project>

Remembered answers to project-skill conflicts, written by the deference protocol.
One line per resolution, in the form `- <skill or skill.stage> → <choice> (<YYYY-MM-DD>)`.
Delete a line to be asked again.

| Choice | Meaning |
|---|---|
| `project:<name>` | The repo's skill runs instead of mine. A note in parentheses may follow the name. |
| `personal` | My skill runs. |
| `compose: project:<name>; <note>` | The repo's skill runs, and the note adds my part each time it runs, however it started. `bin/hooks/compose_notes.py` puts the note in the agent's context, so write it as an instruction an agent can follow without the rest of this file. |

A compose line looks like `- pr-babysit → compose: project:ci-loop; after each push, reply to each thread in a signed comment that cites the fixing commit. (2026-01-15)`.
