#!/usr/bin/env python3
"""Search what I typed in past Claude Code sessions.

Reads the top-level transcripts under ~/.claude/projects. Subagent transcripts
are skipped, because their user turns are briefs from a parent agent, not me.
Injected turns, compaction summaries, messages from other agents, and
<system-reminder> blocks are skipped too.

Usage: transcripts.py search <regex> [--days N] [--project TEXT] [--limit N]

The regex is case-insensitive. The last line counts matches and sessions,
which is how /self-improve tells a one-off correction from a recurring one.
Stdlib only. Writes nothing.
"""
import argparse
import datetime
import glob
import json
import os
import re

PROJECTS = os.path.expanduser("~/.claude/projects")
REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


def user_turns(path):
    """Yield (timestamp, text) for each turn I typed in one transcript."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict) or rec.get("type") != "user":
                continue
            if rec.get("isMeta") or rec.get("isCompactSummary"):
                continue
            origin = rec.get("origin")
            if isinstance(origin, dict) and origin.get("kind") != "human":
                continue
            msg = rec.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, str):
                texts = [content]
            elif isinstance(content, list):
                texts = [b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text"]
            else:
                continue
            text = REMINDER_RE.sub("", "\n".join(texts)).strip()
            if text:
                yield rec.get("timestamp", ""), text


def search(pattern, days, project, limit):
    regex = re.compile(pattern, re.I)
    since = ""
    if days:
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
        since = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
    hits = []
    for path in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        proj = os.path.basename(os.path.dirname(path))
        if project and project not in proj:
            continue
        session = os.path.basename(path)[: -len(".jsonl")]
        for ts, text in user_turns(path):
            if since and ts and ts < since:
                continue
            m = regex.search(text)
            if m:
                start = max(0, m.start() - 80)
                snippet = " ".join(text[start : m.end() + 120].split())
                hits.append((ts, session, proj, snippet))
    hits.sort()
    for ts, session, proj, snippet in hits[-limit:] if limit else hits:
        print(f"{ts[:10] or '-'}  {session[:8]}  {proj}\n    {snippet}")
    sessions = {h[1] for h in hits}
    print(f"\n{len(hits)} match(es) in {len(sessions)} session(s)")


def main():
    parser = argparse.ArgumentParser(description="Search my past Claude Code turns.")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search", help="print my turns that match a regex")
    s.add_argument("pattern")
    s.add_argument("--days", type=int, default=0, help="only the last N days")
    s.add_argument("--project", default="", help="only project dirs containing TEXT")
    s.add_argument("--limit", type=int, default=50, help="print the newest N matches (0 = all)")
    args = parser.parse_args()
    search(args.pattern, args.days, args.project, args.limit)


if __name__ == "__main__":
    main()
