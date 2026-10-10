# Private checks for <project>

Checks that enforce this project's rules for my agents, without changing the
team's repo. Each file in `context/<project>/checks/` is one check.

- **The contract.** A check is an executable. It gets the changed files as
  arguments. It exits 0 when they pass, and non-zero with one line per problem
  when they don't. Each line gives the file, the line, and the fix, in words an
  agent can act on.
- **Who runs them.** `/code-build` Step 4, the `/work-triage` Verify stage, and
  `/work-delegate` pickup run every check on the files a change touched.
- **How one is born.** `/self-improve` writes a check when a mistake class
  recurs, proves it reports the mistake on the commit where it happened, and
  adds a row to `rules.md`.
- **Moving one into the repo.** A private check binds only my local agents,
  because cloud agents and teammates never see it. When I decide the team should
  have it, it becomes a lint rule or a CI check in the repo, through a PR.

A check can be a short script around a tool the project already has. For a
Ruby project, that's `bundle exec rubocop --require <cop file> --only <Cop>`
on the changed files.
