#!/usr/bin/env python3
"""Validate review-comment anchors against a PR's file patches.

usage: validate-anchors.py PR-FILES.json < ANCHORS.jsonl

PR-FILES.json: the raw output of
  gh api repos/<owner>/<repo>/pulls/<num>/files --paginate
(one JSON array per page, concatenated; a JSON-lines file of
{"filename", "patch"} objects is accepted too).

ANCHORS.jsonl on stdin: one {"path": ..., "line": N, "side": "RIGHT"|"LEFT"}
object per line.

Prints one line per anchor: VALID; INVALID with the nearest changed line on the
same side; or NONE when the file has no patch (binary or oversized).
"""
import json
import re
import sys

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def json_stream(text):
    decoder = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        obj, i = decoder.raw_decode(text, i)
        yield from (obj if isinstance(obj, list) else [obj])


def ranges(patch):
    sides = {"LEFT": [], "RIGHT": []}
    for header in patch.splitlines():
        m = HUNK.match(header)
        if not m:
            continue
        a, b, c, d = (int(x) if x is not None else 1 for x in m.groups())
        sides["LEFT"].append(range(a, a + b))
        sides["RIGHT"].append(range(c, c + d))
    return sides


def changed_lines(patch, side):
    out, old, new = [], 0, 0
    for raw in patch.splitlines():
        m = HUNK.match(raw)
        if m:
            old, new = int(m.group(1)), int(m.group(3))
            continue
        if raw.startswith("+"):
            if side == "RIGHT":
                out.append(new)
            new += 1
        elif raw.startswith("-"):
            if side == "LEFT":
                out.append(old)
            old += 1
        elif raw.startswith("\\"):
            continue
        else:
            old += 1
            new += 1
    return out


with open(sys.argv[1]) as f:
    patches = {row["filename"]: row.get("patch") or "" for row in json_stream(f.read())}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    anchor = json.loads(line)
    path, n, side = anchor["path"], int(anchor["line"]), anchor.get("side", "RIGHT")
    patch = patches.get(path, "")
    if not patch:
        print(f"NONE    {path}:{n} {side}  (no patch for file)")
    elif any(n in r for r in ranges(patch)[side]):
        print(f"VALID   {path}:{n} {side}")
    else:
        near = min(changed_lines(patch, side), key=lambda x: abs(x - n), default=None)
        print(f"INVALID {path}:{n} {side}  nearest changed line on this side: {near}")
