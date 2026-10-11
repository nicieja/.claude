# Stack for <project>

- **Tracker:** <name + how sessions connect to it: MCP connector / CLI / API>
- **Code host & PR flow:** <gh, stacked PRs?, merge queue?, draft-first? A stacking tool
  is used only when it's installed>
- **CI:** <where checks run, and where the required ones are set, e.g. GitHub Actions
  with branch protection or rulesets>
- **Review bots:** <the bots that review PRs, and how each one signals it has finished:
  a review on the head commit, a status, a check run, or a reaction>
- **Commit conventions:** <path to .gitmessage or doc, or "none">
- **Error tracking:** <Sentry project(s) / …>
- **Production console:** <flavor (Rails/psql/none) and access mode, e.g., "human
  runs scripts and pastes output", or "read-only queries via <MCP server, e.g.
  Metabase MCP>. Mutations always human-run". Agents may execute read-only queries
  through a user-confirmed MCP, never mutations>
- **Schema locations:** <path or glob, e.g., db/schema.rb or apps/*/db/schema.rb>
- **Architecture reading order:** <docs an agent should read before exploring>
- **Test commands:** <how to run tests, lint, typecheck>
- **Local runtime:** <up, down, restart, status, and logs for one checkout; the dev host
  pattern, and any host an agent must never browse>
- **Worktrees:** <path and branch naming; the command when a worktree needs services;
  teardown; checkouts a desktop app manages>
- **Naming:** <ID prefixes and event and route style, or a link to the doc that sets them>
- **Project skills:** <where they live, if anywhere: skills/, .claude/skills/, …>
- **WIP cap:** <max concurrent build lanes for dispatched work; default 3>
