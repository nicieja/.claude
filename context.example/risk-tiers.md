# Risk tiers for <project>

Tier semantics are fixed, and the surfaces are per-project. When work touches surfaces in
two tiers, the higher tier applies. Code in an area this file doesn't list takes the
Unlisted tier below, and T2 when this file is missing.

- **T0 (flows freely).** Docs, comments, internal tooling, test-only changes.
  Agents proceed and report.
- **T1 (machine-gated).** Reviewed by agents with evidence attached, and the user samples.
- **T2 (user-gated).** The user reads the evidence bundle and skims the diff before
  merge. Default tier for anything not listed.
- **T3 (user-joined).** The user is in the loop while the work happens. It never runs
  unattended, and auto-advance is off.

## Surfaces

These defaults are the surfaces that needed a person in practice. Keep them, and add this
project's paths under each one.

- T3: money movement (billing, payments, payouts, invoices, ledgers), auth and permissions
  (sessions, roles, policies, tokens), data deletion, and externally visible contracts
  (public API behavior, webhooks, published SDKs, tools other agents call).
- T2: schema changes and migrations, concurrency (locks, queues, background jobs, and
  transactions around them), and core domain logic.
- T1: routine feature work in areas with tests. The independent review in `/code-build`
  and `/pr-babysit` reads it before I do.
- T0: docs, comments, test-only changes, and internal scripts.
- Unlisted: T2. Lower it to T1 once the project has a verify harness that ran and the
  independent review has run here for a while.
