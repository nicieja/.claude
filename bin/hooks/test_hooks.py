#!/usr/bin/env python3
"""Tests for the hooks in this directory: outward_guard.py, compose_notes.py, and
notify_phone.py.

Each failure prints as `path: problem. Fix: ...`, the format bin/check uses,
and the exit code is 1 when anything fails. bin/check runs this file.

Stdlib only. The compose cases build a throwaway repo, a worktree of it, and a
home directory with its resolutions.md, all under a temporary directory.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS))
# The pre-commit hook runs this file with GIT_DIR and GIT_INDEX_FILE set for
# this repo, and the throwaway repo's git commands must not inherit them.
for key in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[key]
import compose_notes  # noqa: E402
import notify_phone  # noqa: E402
import outward_guard  # noqa: E402

DENY = [
    "gh pr merge 12 --squash",
    "gh stack merge 12 --squash --yes",
    "gt merge --no-interactive",
    "gt --cwd /tmp/x merge",
    "gt submit -m",
    "gt ss --merge-when-ready",
    "gt s -f",
    "gt submit --comment 'done'",
    "gt submit --comment --publish",
    "git push --force origin main",
    "git push -fu origin x",
    "git push origin +main",
    "cd x && gt merge",
    "bash -c 'gh stack merge 3 --yes'",
    "gh api graphql -f query='mutation { enqueuePullRequest(input: {}) { clientMutationId } }'",
    "gh api -X POST repos/o/r/merges -f base=main -f head=x",
]
ALLOW = [
    "gt merge --dry-run --no-interactive",
    "gt submit --stack --publish",
    "gh stack view",
    "git push origin HEAD",
    "git push -u origin x",
    "gh pr view 12",
]

RESOLUTIONS = """\
# Resolutions for acme

- shape → project:plan (written by the repo's skill) (2026-01-01)
- refactor → personal (2026-01-01)
- pr-babysit → compose: project:ci-loop; reply to each thread you fixed. (2026-01-02)
- test-prove → compose: project verify runs the checks (2026-01-03)
- pr-open → project:pr
"""

failures = []


def fail(path, problem, fix):
    failures.append(f"{path}: {problem}. Fix: {fix}")


def denied(command):
    try:
        outward_guard.check_shell(command, "Claude", str(HOOKS))
    except outward_guard.Deny:
        return True
    return False


def check_guard():
    for command in DENY:
        if not denied(command):
            fail("bin/hooks/outward_guard.py", f"lets `{command}` through",
                 "make the guard deny it, or move the case to ALLOW in bin/hooks/test_hooks.py")
    for command in ALLOW:
        if denied(command):
            fail("bin/hooks/outward_guard.py", f"denies `{command}`",
                 "make the guard allow it, or move the case to DENY in bin/hooks/test_hooks.py")


def git(*args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   capture_output=True, check=True)


def run_hook(home, event):
    out = subprocess.run([sys.executable, str(HOOKS / "compose_notes.py")],
                         input=json.dumps(event), capture_output=True, text=True,
                         env={**os.environ, "HOME": str(home)}, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""


def expect(got, wanted, case):
    if got != wanted:
        fail("bin/hooks/compose_notes.py", f"{case}: got {got!r}, wanted {wanted!r}",
             "fix the hook, or the case in bin/hooks/test_hooks.py")


def check_compose():
    notes, malformed = compose_notes.parse(RESOLUTIONS)
    expect(notes, [("ci-loop", "pr-babysit", "reply to each thread you fixed.")], "parsed notes")
    expect([n for n, _ in malformed], [6, 7], "malformed line numbers")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp).resolve()
        repo, worktree, outside, home = tmp / "acme", tmp / "acme-wt", tmp / "outside", tmp / "home"
        git("init", "-q", str(repo))
        git("-C", str(repo), "commit", "-q", "--allow-empty", "-m", "start")
        git("-C", str(repo), "worktree", "add", "-q", str(worktree))
        outside.mkdir()
        (home / ".claude/context/acme").mkdir(parents=True)
        (home / ".claude/context/acme/resolutions.md").write_text(RESOLUTIONS)

        expect(compose_notes.project(str(repo)), "acme", "project of the main checkout")
        expect(compose_notes.project(str(worktree)), "acme", "project of a worktree")
        expect(compose_notes.project(str(outside)), None, "project outside a repo")

        start = run_hook(home, {"hook_event_name": "SessionStart", "cwd": str(worktree)})
        for text in ("`ci-loop` (resolution `pr-babysit`): reply to each thread you fixed.",
                     "line 6:", "line 7:"):
            if text not in start:
                fail("bin/hooks/compose_notes.py", f"SessionStart leaves out {text!r}",
                     "list every note and every malformed line in session_text")
        loaded = run_hook(home, {"hook_event_name": "PostToolUse", "cwd": str(repo),
                                 "tool_name": "Skill", "tool_input": {"skill": "ci-loop"}})
        if "reply to each thread you fixed." not in loaded:
            fail("bin/hooks/compose_notes.py", "PostToolUse on Skill(ci-loop) leaves out its note",
                 "match the note on tool_input['skill']")
        expect(run_hook(home, {"hook_event_name": "UserPromptExpansion", "cwd": str(repo),
                               "command_name": "deploy"}), "", "a skill with no note")
        expect(run_hook(home, {"hook_event_name": "SessionStart", "cwd": str(outside)}), "",
               "a cwd outside a repo")


def check_notify():
    cases = [
        ("claude", {"cwd": "/w/acme", "message": "Claude is waiting for your input"},
         "acme: Claude is waiting for your input"),
        ("codex", {"cwd": "/w/acme", "hook_event_name": "Stop",
                   "last_assistant_message": "the customer's card number is 4242"},
         "acme: Codex finished a turn"),
    ]
    for agent, event, wanted in cases:
        got = notify_phone.body(agent, event)
        if got != wanted:
            fail("bin/hooks/notify_phone.py", f"{agent} body: got {got!r}, wanted {wanted!r}",
                 "send only the cwd's folder and the event, never conversation text")


def main():
    check_guard()
    check_compose()
    check_notify()
    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
