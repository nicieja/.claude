#!/usr/bin/env python3
"""Hook for /conversation, which switches a session to short, chat-like replies.

- UserPromptExpansion for /conversation turns the mode on or off for the session.
- UserPromptSubmit restates the rules on every prompt while the mode is on, so
  they still apply many turns later and after /compact.

The mode is on while ~/.cache/agent-modes/conversation/<session_id> exists.
The command itself is commands/conversation.md.

Usage in a hook config: conversation_mode.py
"""
import json
import sys
from pathlib import Path

STATE = Path.home() / ".cache/agent-modes/conversation"

RULES = """\
Conversation mode is on. The user wants a quick back-and-forth, one short message in and one short message out.
- Reply like a chat message, in one to three sentences. Stop when the answer is given.
- One point per message. When there's more, give the headline and offer the rest.
- No headings, lists, or tables. Don't recap their message or end with a summary.
- At most one question, at the end.
- Their messages will be short. A one-liner isn't a request for an essay.
- Tool work runs as usual. Report the result in a sentence or two. A report that AGENTS.md requires keeps Changed, Check, and Undo, at one line each.
- Use a code block only when they ask for code or a command to run.
- When they ask for something long, such as a plan, a file, or a draft, write it in full, then go back to short replies.
- Running /conversation again turns the mode off."""

OFF = "Conversation mode is off. Reply at normal length again."


def add_context(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def main():
    hook = json.load(sys.stdin)
    event = hook["hook_event_name"]
    flag = STATE / hook["session_id"]
    if event == "UserPromptExpansion":
        if flag.exists():
            flag.unlink()
            add_context(event, OFF)
        else:
            STATE.mkdir(parents=True, exist_ok=True)
            flag.touch()
            add_context(event, RULES)
    elif flag.exists() and not hook["prompt"].startswith("/conversation"):
        add_context(event, RULES)


if __name__ == "__main__":
    main()
