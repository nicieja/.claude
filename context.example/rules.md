# Rules for <project>

The project's rules that agents keep breaking, and what enforces each one.
`/self-improve` adds a row when it fixes a mistake class. A rule whose enforcer
is "prose" and that gets broken again moves up a level, usually to a private
check in `checks/`. Moving a check into the repo itself is my decision. When the
rule is a call in `decisions.md`, the Rule cell contains its cite,
`(decisions: <heading>)`.

| Rule | Enforced by | Level | Evidence |
|---|---|---|---|
| <the rule, as one sentence> | <the cop, the type, `checks/<name>`, or the doc that states it> | <structure \| check \| test \| prose> | <the commit, PR, or session where the mistake happened> |
