#!/usr/bin/env python3
"""Hook that hands a skill the notes recorded for it in a project.

A note in ~/.claude/context/<project>/resolutions.md is the user's standing
instruction for one skill. A compose note is for one of the repo's skills, and
a personal note is for one of the user's own:

  - <skill or skill.stage> → compose: project:<name>; <note> (<YYYY-MM-DD>)
  - <skill or skill.stage> → personal; <note> (<YYYY-MM-DD>)

- SessionStart lists every note for the project, and the lines that don't
  parse. It runs again after /compact, so the notes outlive a long session and
  cover a skill that another skill runs from its file.
- UserPromptExpansion (a typed /<name>) and PostToolUse on the Skill tool add
  the note for the skill that just loaded.

<project> is the directory name of the repo's main checkout, so a worktree gets
the notes of its main checkout. Outside a repo, or without resolutions.md, the
hook prints nothing. The format is in context.example/resolutions.md.

Usage in a hook config: compose_notes.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CONTEXT = Path.home() / ".claude/context"
LINE = re.compile(r"- ([a-z0-9-]+(?:\.[a-z0-9-]+)?) → (.+) \((\d{4}-\d{2}-\d{2})\)")
COMPOSE = re.compile(r"compose: project:([a-z0-9-]+); (\S.*)")
PERSONAL = re.compile(r"personal; (\S.*)")
ASK = "Where the skill waits for the user to ask, the note is that ask."


def project(cwd):
    out = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute",
                          "--git-common-dir"], capture_output=True, text=True)
    return Path(out.stdout.strip()).parent.name if out.returncode == 0 else None


def parse(text):
    """Return (notes, malformed). A note is (skill it's for, resolution key, note)."""
    notes, malformed = [], []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.startswith("- "):
            continue
        m = LINE.fullmatch(line.strip())
        choice = m.group(2) if m else ""
        personal = PERSONAL.fullmatch(choice)
        if personal:
            notes.append((m.group(1).partition(".")[0], m.group(1), personal.group(1)))
            continue
        if choice.startswith(("project:", "personal")):
            continue
        compose = COMPOSE.fullmatch(choice)
        if compose:
            notes.append((compose.group(1), m.group(1), compose.group(2)))
        else:
            malformed.append((n, line))
    return notes, malformed


def session_text(path, notes, malformed):
    parts = []
    if notes:
        parts.append(f"Notes from {path}. Each one is the user's standing instruction "
                     "for one skill, the repo's or the user's own. Apply it whenever that skill runs, however "
                     "it starts: typed, loaded with the Skill tool, read from its file, or run "
                     f"as a step of another skill. {ASK}\n"
                     + "\n".join(f"- `{skill}` (resolution `{key}`): {note}"
                                 for skill, key, note in notes))
    if malformed:
        parts.append(f"These lines in {path} don't parse, so no hook applies them. Quote each "
                     "one to the user in your first reply, with the format from "
                     "~/.claude/context.example/resolutions.md.\n"
                     + "\n".join(f"- line {n}: `{line}`" for n, line in malformed))
    return "\n\n".join(parts)


def load_text(path, skill, notes):
    if not notes:
        return ""
    return (f"`{skill}` runs with a note from {path}, the user's standing instruction "
            f"for it. Apply it on this run. {ASK}\n"
            + "\n".join(f"- resolution `{key}`: {note}" for _, key, note in notes))


def main():
    hook = json.load(sys.stdin)
    event = hook["hook_event_name"]
    name = project(hook["cwd"])
    path = CONTEXT / str(name) / "resolutions.md"
    if name is None or not path.exists():
        return
    notes, malformed = parse(path.read_text(encoding="utf-8"))
    if event == "SessionStart":
        text = session_text(path, notes, malformed)
    else:
        skill = hook["command_name"] if event == "UserPromptExpansion" else hook["tool_input"]["skill"]
        text = load_text(path, skill, [note for note in notes if note[0] == skill])
    if text:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


if __name__ == "__main__":
    main()
