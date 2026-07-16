# Risk tiers — <project>

Tier semantics are fixed; the surfaces are per-project. When work touches surfaces in
two tiers, the higher tier wins. Unknown or unlisted surface: treat as T2 minimum.

- **T0 — flows freely.** Docs, comments, internal tooling, test-only changes.
  Agents proceed and report.
- **T1 — machine-gated.** Reviewed by agents with evidence attached; the user samples.
- **T2 — user-gated.** The user reads the evidence bundle and skims the diff before
  merge. Default tier for anything not listed.
- **T3 — user-joined.** The user is in the loop while the work happens; never runs
  unattended; auto-advance is off.

## Surfaces

- T3: <irreversible or high-blast-radius surfaces: money movement, auth/permissions,
  data deletion, externally visible contracts…>
- T2: <core product logic, schema changes, public API…>
- T1: <routine feature work in well-tested areas…>
- T0: <docs, internal scripts…>
