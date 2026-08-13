#!/usr/bin/env python3
"""Audit skill/command/agent usage across Claude Code transcripts.

Inventory is derived live from ~/.claude/skills, ~/.claude/commands, and
~/.claude/agents. Invocation evidence comes from every transcript under
~/.claude/projects, including both subagent layouts.

Skills and commands are invoked two ways -- the Skill tool (input.skill) and
typed slash commands (<command-name> blocks in user messages). Both signal
streams merge into one record per name. Agents come only from Task/Agent
tool_use input.subagent_type.

Stdlib only. Prints plain text to stdout; writes nothing.
"""
import collections
import glob
import json
import os
import re

HOME = os.path.expanduser("~/.claude")

def inventory():
    skills = sorted(os.path.basename(p.rstrip(os.sep))
                    for p in glob.glob(os.path.join(HOME, "skills", "*", "")))
    commands = sorted(os.path.splitext(os.path.basename(p))[0]
                      for p in glob.glob(os.path.join(HOME, "commands", "*.md")))
    agents = sorted(os.path.splitext(os.path.basename(p))[0]
                    for p in glob.glob(os.path.join(HOME, "agents", "*.md")))
    return skills, commands, agents

def transcript_files():
    projects = os.path.join(HOME, "projects")
    return (glob.glob(os.path.join(projects, "*", "*.jsonl"))
            + glob.glob(os.path.join(projects, "*", "*", "subagents", "*.jsonl"))
            + glob.glob(os.path.join(projects, "*", "subagents", "*.jsonl")))

def session_of(path):
    """Top-level files are their own session; subagent files belong to the
    parent session directory."""
    parts = path.split(os.sep)
    if "subagents" in parts:
        return parts[parts.index("subagents") - 1]
    return os.path.basename(path)[:-len(".jsonl")]

CMD_RE = re.compile(r"<command-name>/?([\w:-]+)</command-name>")

def new_record():
    return {"sessions": set(), "calls": 0, "last": ""}

def main():
    skills, commands, agents = inventory()

    # Two evidence pools: invocations (Skill tool + slash commands, shared by
    # skills and commands) and agents (subagent_type only). Origin of each
    # invoked name is kept so uninventoried leftovers land in the right section.
    invoked = collections.defaultdict(new_record)
    agent_use = collections.defaultdict(new_record)
    via_skill_tool = set()
    via_slash = set()

    def note(pool, name, sess, ts):
        rec = pool[name]
        rec["sessions"].add(sess)
        rec["calls"] += 1
        if ts and ts > rec["last"]:
            rec["last"] = ts

    files = transcript_files()
    scanned = 0
    earliest = ""
    for path in files:
        sess = session_of(path)
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(rec, dict):
                    continue
                ts = rec.get("timestamp", "")
                if ts and (not earliest or ts < earliest):
                    earliest = ts
                msg = rec.get("message") or {}
                content = msg.get("content") if isinstance(msg, dict) else None
                is_user = rec.get("type") == "user"

                if isinstance(content, str):
                    if is_user:
                        for m in CMD_RE.finditer(content):
                            note(invoked, m.group(1), sess, ts)
                            via_slash.add(m.group(1))
                    continue
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text" and is_user:
                        for m in CMD_RE.finditer(block.get("text", "")):
                            note(invoked, m.group(1), sess, ts)
                            via_slash.add(m.group(1))
                    if block.get("type") != "tool_use":
                        continue
                    inp = block.get("input") or {}
                    if not isinstance(inp, dict):
                        continue
                    tool = block.get("name", "")
                    if tool == "Skill" and inp.get("skill"):
                        name = str(inp["skill"])
                        note(invoked, name, sess, ts)
                        via_skill_tool.add(name)
                    elif tool in ("Task", "Agent") and inp.get("subagent_type"):
                        note(agent_use, str(inp["subagent_type"]), sess, ts)
        scanned += 1

    print(f"window start: {earliest[:10] or '-'}")
    print(f"files scanned: {scanned}")
    print(f"distinct sessions: {len({session_of(p) for p in files})}")

    known = set(skills) | set(commands)
    leftovers = set(invoked) - known
    extras = {
        "SKILLS": sorted(leftovers & via_skill_tool),
        "COMMANDS": sorted(leftovers - via_skill_tool),
        "AGENTS": sorted(set(agent_use) - set(agents)),
    }

    def line(name, rec):
        last = rec["last"][:10] if rec["last"] else "-"
        dead = " DEAD" if rec["calls"] == 0 else ""
        return (f"{name:24s} sessions={len(rec['sessions']):3d} "
                f"calls={rec['calls']:4d} last={last}{dead}")

    for title, names, pool in (("SKILLS", skills, invoked),
                               ("COMMANDS", commands, invoked),
                               ("AGENTS", agents, agent_use)):
        print(f"\n=== {title} ({len(names)} in inventory) ===")
        rows = sorted(names, key=lambda n: (-len(pool[n]["sessions"])
                                            if n in pool else 0, n))
        for name in rows:
            print(line(name, pool.get(name) or new_record()))
        if extras[title]:
            print("  (also seen, not in inventory):")
            for name in extras[title]:
                print("  " + line(name, pool[name]))

if __name__ == "__main__":
    main()
