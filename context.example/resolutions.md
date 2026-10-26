# Resolutions for <project>

Remembered answers to project-skill conflicts, written by the deference protocol.
One line per resolution, in the form `- <skill or skill.stage> → <choice> (<YYYY-MM-DD>)`.
Delete a line to be asked again.

| Choice | Meaning |
|---|---|
| `project:<name>` | The repo's skill runs instead of mine. A note in parentheses may follow the name. |
| `personal` | My skill runs. |
| `personal; <note>` | My skill runs, and the note changes how it works in this project each time it runs, however it started. `bin/hooks/compose_notes.py` puts the note in the agent's context, as it does a compose note. |
| `compose: project:<name>; <note>` | The repo's skill runs, and the note adds my part each time it runs, however it started. `bin/hooks/compose_notes.py` puts the note in the agent's context, so write it as an instruction an agent can follow without the rest of this file. |

A compose line looks like `- pr-babysit → compose: project:ci-loop; after each push, reply to each thread in a signed comment that cites the fixing commit. (2026-01-15)`, and a personal note like `- idea-spec → personal; write the plan in native Plan mode, not a plans/ file. (2026-01-15)`.
