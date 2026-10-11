#!/usr/bin/env python3
"""Pre-tool hook for posts made under the user's account.

It denies two kinds of call:

- A comment or message with no signature. Its body must end with the line
  "Posted by <Agent> on <Name>'s behalf", where <Agent> comes from --agent
  and <Name> is the first word of `git config --global user.name`.
- An action that always needs the user's OK: a merge, including a stacked
  merge through `gh stack` or Graphite's `gt`, an approving or
  change-requesting review, a force push, and Linear's merge_diff and
  submit_diff_review. They can run those themselves with `! <command>`.

Every other call passes with no output. The rules are in AGENTS.md ("When to
act and when to confirm"). Claude Code and Codex send the same PreToolUse JSON
on stdin and accept the same deny JSON on stdout.

Usage in a hook config: outward_guard.py --agent claude|codex
"""
import json
import os
import re
import shlex
import subprocess
import sys
from functools import cache

AGENTS = {"claude": "Claude", "codex": "Codex"}

# MCP tools that post text, matched on the part of the tool name after the last "__".
POSTING_TOOLS = {
    "save_comment", "save_diff_comment",                      # Linear
    "slack_send_message", "slack_schedule_message",           # Slack
    "send_message", "reply", "forward",                       # Gmail
    "add_internal_note",                                      # Intercom
    "create_incident_comment", "create_error_comment",        # Better Stack
}
NEEDS_OK_TOOLS = {"merge_diff", "submit_diff_review"}         # Linear
BODY_KEYS = ("body", "message", "text", "content", "note", "comment")

COMMENT_PATH = re.compile(r"/(comments|reviews|replies)(/|$|\?)")
GRAPHQL_POSTS = re.compile(r"\b(addComment|addPullRequestReview|addPullRequestReviewComment|"
                           r"addPullRequestReviewThreadReply|submitPullRequestReview|"
                           r"updateIssueComment|updatePullRequestReviewComment|addDiscussionComment)\b")
GRAPHQL_MERGES = re.compile(r"\b(mergePullRequest|enablePullRequestAutoMerge|mergeBranch|"
                            r"enqueuePullRequest)\b")
# Words that can start a shell command segment before the real command.
PREFIXES = {"do", "then", "else", "elif", "if", "while", "until", "{", "}", "!", "time",
            "command", "exec", "nohup", "env", "sudo"}
MERGE_PATH = re.compile(r"(/pulls/\d+/merge|/merges)(/|$|\?)")
CONTROL = {"&&", "||", ";", "|", "&", "\n", "(", ")"}


class Deny(Exception):
    pass


@cache
def signature(agent):
    name = subprocess.run(["git", "config", "--global", "user.name"],
                          capture_output=True, text=True).stdout.split()
    if not name:
        raise Deny("The signature names the user from `git config --global user.name`, "
                   "which is empty. Ask them to set it.")
    return f"Posted by {agent} on {name[0]}'s behalf"


def signed(body, agent):
    lines = [line.strip() for line in body.strip().splitlines() if line.strip()]
    if not lines:
        return False
    last = lines[-1].strip("*_ ").replace("’", "'").rstrip(".")
    return last == signature(agent)


def require_signature(body, agent, where):
    if not signed(body, agent):
        raise Deny(f"{where} has no signature. End the body with this line, on its own: "
                   f"{signature(agent)}")


def needs_ok(what):
    raise Deny(f"{what} needs the user's OK (AGENTS.md, \"Always my OK\"). Ask them. "
               "They can run it themselves with `! <command>`.")


def read_file(path, cwd):
    if path == "-":
        raise Deny("A body read from stdin can't be checked. Write it to a file and pass the file.")
    full = path if os.path.isabs(path) else os.path.join(cwd, os.path.expanduser(path))
    try:
        with open(os.path.expanduser(full), encoding="utf-8") as fh:
            return fh.read()
    except OSError as err:
        raise Deny(f"Couldn't read the body file {path}: {err}")


def options(args):
    """Split gh/git args into (flags, positionals). Flags map to a list of values."""
    flags, positionals = {}, []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--") and "=" in arg:
            key, value = arg.split("=", 1)
            flags.setdefault(key, []).append(value)
        elif arg.startswith("-") and arg != "-":
            nxt = args[i + 1] if i + 1 < len(args) else None
            if nxt is not None and not nxt.startswith("-"):
                flags.setdefault(arg, []).append(nxt)
                i += 1
            else:
                flags.setdefault(arg, []).append(None)
        else:
            positionals.append(arg)
        i += 1
    return flags, positionals


def short_flag(args, letter):
    """Whether a short flag is present, alone or in a cluster such as -fu."""
    return any(re.fullmatch(rf"-[A-Za-z]*{letter}[A-Za-z]*", arg) for arg in args)


def flag(flags, *names):
    for name in names:
        if name in flags:
            return flags[name]
    return None


def inline_body(value):
    if "$(" in value or re.search(r"\$\{?[A-Za-z_0-9@*#?]", value):
        raise Deny("A post's body can't come from a command substitution or a shell variable, "
                   "because the guard can't read it. Write the body to a file and pass it with "
                   "--body-file, -F body=@file, or --input.")
    return value


def body_from_flags(flags, cwd):
    inline = flag(flags, "-b", "--body")
    if inline and inline[0] is not None:
        return inline_body(inline[0])
    path = flag(flags, "-F", "--body-file")
    if path and path[0] is not None:
        return read_file(path[0], cwd)
    return None


def check_gh(args, agent, cwd):
    args = skip_global_options(args, ("-R", "--repo", "--hostname"))
    if len(args) < 2:
        return
    group, verb = args[0], args[1]
    if group == "pr" and verb == "merge":
        needs_ok("Merging a PR")
    if group == "stack" and verb == "merge":
        needs_ok("Merging a stack")
    if group == "pr" and verb == "review":
        flags, _ = options(args[2:])
        if flag(flags, "-a", "--approve") or flag(flags, "-r", "--request-changes"):
            needs_ok("An approving or change-requesting review")
        body = body_from_flags(flags, cwd)
        if body is None:
            raise Deny("`gh pr review` needs a body passed with --body or --body-file.")
        require_signature(body, agent, "The review")
    if group in ("pr", "issue") and verb == "close":
        flags, _ = options(args[2:])
        comment = flag(flags, "-c", "--comment")
        if comment and comment[0] is not None:
            require_signature(inline_body(comment[0]), agent, f"The comment on `gh {group} close`")
    if group in ("pr", "issue") and verb == "comment":
        flags, _ = options(args[2:])
        body = body_from_flags(flags, cwd)
        if body is None:
            raise Deny(f"`gh {group} comment` needs a body passed with --body or --body-file.")
        require_signature(body, agent, "The comment")
    if group == "api":
        check_gh_api(args[1:], agent, cwd)


def check_gh_api(args, agent, cwd):
    flags, positionals = options(args)
    if not positionals:
        return
    path = positionals[0]
    fields = {}
    for name in ("-f", "-F", "--field", "--raw-field"):
        for value in flags.get(name) or []:
            if value and "=" in value:
                key, val = value.split("=", 1)
                if name in ("-F", "--field") and val.startswith("@"):
                    val = read_file(val[1:], cwd)
                elif key == "body":
                    val = inline_body(val)
                fields[key] = val
    payload = {}
    input_file = flag(flags, "--input")
    if input_file and input_file[0] is not None:
        try:
            payload = json.loads(read_file(input_file[0], cwd))
        except json.JSONDecodeError as err:
            raise Deny(f"The --input file isn't valid JSON: {err}")
    method = (flag(flags, "-X", "--method") or [None])[0]
    method = (method or ("POST" if fields or payload else "GET")).upper()
    if path == "graphql":
        check_graphql(fields, payload, agent)
        return
    if method == "GET":
        return
    if MERGE_PATH.search(path):
        needs_ok("Merging a PR")
    event = str(fields.get("event") or payload.get("event") or "").upper()
    if event in ("APPROVE", "REQUEST_CHANGES"):
        needs_ok("An approving or change-requesting review")
    if COMMENT_PATH.search(path):
        body = fields.get("body", payload.get("body"))
        if body is None:
            raise Deny(f"A {method} to {path} needs a body field.")
        require_signature(body, agent, "The post")


def skip_global_options(args, takes_value):
    while args and args[0].startswith("-"):
        args = args[2:] if args[0] in takes_value else args[1:]
    return args


def check_graphql(fields, payload, agent):
    query = str(fields.get("query") or payload.get("query") or "")
    if "mutation" not in query:
        return
    everything = query + "\n" + "\n".join(map(str, fields.values())) + "\n" + json.dumps(payload)
    if GRAPHQL_MERGES.search(query):
        needs_ok("Merging a PR")
    if re.search(r"\b(APPROVE|REQUEST_CHANGES)\b", everything):
        needs_ok("An approving or change-requesting review")
    if GRAPHQL_POSTS.search(query):
        text = everything.replace("\u2019", "'").replace("\\'", "'")
        if signature(agent) not in text:
            raise Deny("The GraphQL post has no signature. End its body with this line, on its "
                       f"own: {signature(agent)}")


def check_git(args):
    args = skip_global_options(args, ("-C", "-c", "--git-dir", "--work-tree"))
    if not args or args[0] != "push":
        return
    flags, positionals = options(args[1:])
    if short_flag(args[1:], "f") or \
            flag(flags, "--force", "--force-with-lease", "--force-if-includes") or \
            any(p.startswith("+") for p in positionals):
        needs_ok("A force push")


def check_gt(args, agent):
    args = skip_global_options(args, ("--cwd",))
    if not args:
        return
    verb, rest = args[0], args[1:]
    if verb == "merge" and "--dry-run" not in rest:
        needs_ok("Merging a stack")
    if verb not in ("submit", "s", "ss"):
        return
    flags, _ = options(rest)
    if short_flag(rest, "m") or flag(flags, "--merge-when-ready"):
        needs_ok("Marking PRs to merge when ready")
    if short_flag(rest, "f") or flag(flags, "--force"):
        needs_ok("A force push")
    comment = flag(flags, "--comment")
    if comment:
        require_signature(inline_body(comment[0] or ""), agent, "The comment on `gt submit`")


def segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    current = []
    for token in lexer:
        if token in CONTROL or set(token) <= set(";&|()\n"):
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
GATED = re.compile(r"(^|[;&|(]\s*)(gh\s+(pr|issue|api|stack)\b|git\s+push\b|gt\b)", re.M)


def strip_heredocs(command):
    """Drop heredoc bodies, so text fed to another program isn't read as commands."""
    lines, out, delimiter = command.split("\n"), [], None
    for line in lines:
        if delimiter is not None:
            if line.strip() == delimiter:
                delimiter = None
            continue
        out.append(line)
        m = HEREDOC.search(line)
        if m:
            delimiter = m.group(2)
    return "\n".join(out)


def check_shell(command, agent, cwd):
    if isinstance(command, list):
        command = shlex.join(command)
    if not re.search(r"\b(gh|git|gt)\b", command):
        return
    command = strip_heredocs(command)
    try:
        parts = list(segments(command))
    except ValueError as err:
        if GATED.search(command):
            raise Deny(f"Couldn't parse the command to check it: {err}")
        return
    for tokens in parts:
        check_command(tokens, agent, cwd)


def check_command(tokens, agent, cwd):
    while tokens and (tokens[0] in PREFIXES
                      or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[0])):
        tokens = tokens[1:]
    if not tokens:
        return
    program = os.path.basename(tokens[0])
    if program in ("bash", "sh", "zsh") and "-c" in tokens[:-1]:
        check_shell(tokens[tokens.index("-c") + 1], agent, cwd)
    elif program == "xargs":
        rest = tokens[1:]
        while rest and rest[0].startswith("-"):
            rest = rest[2:] if rest[0] in ("-I", "-n", "-P", "-L", "-d", "-E", "-s") else rest[1:]
        check_command(rest, agent, cwd)
    elif program == "gh":
        check_gh(tokens[1:], agent, cwd)
    elif program == "git":
        check_git(tokens[1:])
    elif program == "gt":
        check_gt(tokens[1:], agent)


def check_mcp(tool, tool_input, agent):
    short = tool.rsplit("__", 1)[-1]
    if short in NEEDS_OK_TOOLS:
        needs_ok(f"`{short}`")
    if short not in POSTING_TOOLS:
        return
    for key in BODY_KEYS:
        if isinstance(tool_input.get(key), str):
            require_signature(tool_input[key], agent, f"`{short}`'s {key}")
            return
    raise Deny(f"Couldn't find the text field of `{short}` (keys: {sorted(tool_input)}). "
               "Add its key to BODY_KEYS in bin/hooks/outward_guard.py.")


def main():
    agent = AGENTS[sys.argv[sys.argv.index("--agent") + 1]]
    event = json.load(sys.stdin)
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()
    try:
        if tool == "Bash":
            check_shell(tool_input.get("command", ""), agent, cwd)
        elif tool.startswith("mcp__"):
            check_mcp(tool, tool_input, agent)
    except Deny as deny:
        json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                          "permissionDecision": "deny",
                                          "permissionDecisionReason": str(deny)}}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
