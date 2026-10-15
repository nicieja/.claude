#!/usr/bin/env python3
"""Prints one line each time an item in a loop's status changes.

Usage: watch.py <status script> [seconds]

It runs the status script every `seconds` (default 120). A loop arms it with
Monitor, so each line it prints wakes the loop. Stdlib only.

The status script's output is the contract between a loop and this watch:
- Every stdout line is one item, with no blank, header or summary line. The
  first word is the item's key, and each key appears once.
- The script exits non-zero when it can't read its source. Exit 0 with no
  output means there are no items.
- A line that starts with `~ ` is an item still settling, such as CI pending or
  mergeability unknown. Its key is the first word after the `~ `.
- Any change in a settled line wakes the loop. So a line leaves out fields that
  move with time or with the loop's own actions, such as an age, or a marker
  that the loop already replied.

The first poll only records the starting state. After it, the watch prints
`<line> (new)` for a new key, `<key> gone` for a key that left, and a settled
line that differs from its key's last settled line. A settling line prints only
when its key is new, so an item that settles back to the line it had wakes no
one. A failed status run goes to stderr, and the
next poll compares with the last good one.
"""
import subprocess
import sys
import time

SETTLING = "~ "


def key(line):
    return line.removeprefix(SETTLING).split()[0]


def poll(status):
    out = subprocess.run([status], capture_output=True, text=True, check=True).stdout
    return {key(line): line for line in out.splitlines()}


def changes(before, after):
    for item, line in after.items():
        if item not in before:
            yield f"{line} (new)"
        elif not line.startswith(SETTLING) and line != before[item]:
            yield line
    for item in before.keys() - after.keys():
        yield f"{item} gone"


def remember(before, after):
    return {item: before[item] if line.startswith(SETTLING) and item in before else line
            for item, line in after.items()}


def main(argv):
    if len(argv) not in (1, 2):
        sys.exit("usage: watch.py <status script> [seconds]")
    status = argv[0]
    interval = int(argv[1]) if len(argv) == 2 else 120
    before = None
    while True:
        try:
            after = poll(status)
        except subprocess.CalledProcessError as error:
            print(f"{status} failed with exit {error.returncode}: {error.stderr.strip()}",
                  file=sys.stderr, flush=True)
        else:
            if before is None:
                before = after
            else:
                for line in changes(before, after):
                    print(line, flush=True)
                before = remember(before, after)
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
