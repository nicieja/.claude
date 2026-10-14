#!/usr/bin/env python3
"""Takes a loop's lock for this session, or says which session holds it.

Usage: lock.py <lock file> <max age in minutes>

The lock file is one line, `<session id> <UTC time>`, and the session id comes
from CLAUDE_CODE_SESSION_ID. When the line names another session younger than
the max age, it prints `held by <session> since <time>` and exits 1. Otherwise
it writes this session's line with the current time and exits 0. When that line
replaced another session's, it prints `took over from <session>` first. Every
wake runs it first, so the time in the file is the time of the last wake.
Stdlib only.
"""
import datetime
import os
import sys
from pathlib import Path


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: lock.py <lock file> <max age in minutes>")
    path = Path(argv[0])
    max_age = datetime.timedelta(minutes=int(argv[1]))
    session = os.environ["CLAUDE_CODE_SESSION_ID"]
    now = datetime.datetime.now(datetime.UTC)
    if path.exists():
        holder, since = path.read_text().split()
        if holder != session:
            if now - datetime.datetime.fromisoformat(since) < max_age:
                print(f"held by {holder} since {since}")
                return 1
            print(f"took over from {holder}")
    path.write_text(f"{session} {now:%Y-%m-%dT%H:%M:%SZ}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
