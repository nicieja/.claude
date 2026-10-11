#!/usr/bin/env python3
"""Hook that pings the user's phone through ntfy when an agent stops for them.

- Claude Code runs it on Notification, matched to idle_prompt and
  permission_prompt.
- Codex runs it on Stop, at the end of every turn. Codex has no idle event,
  and its `notify` command belongs to Computer Use.

Both send the event JSON on stdin.

The message is the cwd's folder name and the event, never conversation text:
ntfy.sh is public, and anyone who knows the topic can read it. The topic is
the only line of ~/.claude/ntfy-topic, which is gitignored, and bin/check
rejects it in tracked files.

Usage in a hook config: notify_phone.py --agent claude|codex
"""
import json
import sys
import urllib.request
from pathlib import Path

TOPIC = Path.home() / ".claude/ntfy-topic"
TITLES = {"claude": "Claude Code", "codex": "Codex"}


def body(agent, event):
    folder = Path(event["cwd"]).name
    if agent == "claude":
        return f"{folder}: {event['message']}"
    return f"{folder}: Codex finished a turn"


def main():
    agent = sys.argv[sys.argv.index("--agent") + 1]
    event = json.load(sys.stdin)
    topic = TOPIC.read_text(encoding="utf-8").strip()
    urllib.request.urlopen(urllib.request.Request(
        f"https://ntfy.sh/{topic}", data=body(agent, event).encode(),
        headers={"Title": TITLES[agent]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
