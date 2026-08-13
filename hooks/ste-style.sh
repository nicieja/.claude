#!/bin/sh
# Injected on every UserPromptSubmit so the STE style rule stays the freshest
# instruction in context, in every project — see CLAUDE.md "Style".
cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"Style: respond in ASD-STE100 Simplified Technical English unless asked not to — in every project, including questions you ask via AskUserQuestion and everything you say while running a skill. Artifacts (drafts, summaries, commit messages, code) keep their own voice."}}
EOF
