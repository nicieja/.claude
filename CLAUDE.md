@AGENTS.md

# Hand plans off to /code-build, then /code-simplify

When you're writing a plan in native Plan mode **and the plan involves writing or changing code**, state the handoff. The build pass follows the `/code-build` skill first, and the cleanup pass runs `/code-simplify` second.

- **Code only.** Ruby, TypeScript, Go, SQL, etc. It does **not** include prose, prompts, skills (`skills/**/SKILL.md`), slash commands (`commands/*.md`), agent definitions (`agents/*.md`), `AGENTS.md`, `CLAUDE.md`, plan files, READMEs, or other prose/config artifacts. For prose work, just do the edits yourself. What `/code-build` adds (local conventions, the divergence ladder for a plan, the handoff with rollback) doesn't apply to markdown.
- **Shape is your call.** There is no mandated section name or template. Pick what reads best for that plan, such as a dedicated section, a line at the end of Verification, or an inline note in the build steps.
- **Skip when there's nothing to build.** Pure research, investigation, retro, doc-only, or prompt-engineering plans don't need the handoff at all.
- **Stage 2 is optional on thin surface area.** If there's not enough code to clean up, drop `/code-simplify`. Decide this case by case. There is no fixed rule.
- **Verify after the cleanup.** `/code-simplify` runs only the targeted tests for its own cuts. After it, run the checks from `/code-build` Step 4 again, and report them under "What you ran".
- **Native Plan mode only.** `/idea-spec` runs its own workflow and is unaffected.
