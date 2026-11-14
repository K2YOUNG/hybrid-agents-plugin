#!/usr/bin/env python3
"""Shared-markdown mailbox: the last-resort transport between agents of different providers.

Use it when herdr and one-shot CLI calls (`claude -p`, `agy -p`, `codex exec`) are unavailable
or keep failing. One markdown file per thread; every agent can read and append with plain file
tools, so no provider-specific API is needed.

    mailbox.py post  --thread paper-intro --from claude --to codex --kind request --body-file req.md
    mailbox.py read  --thread paper-intro --to claude [--open]
    mailbox.py close --thread paper-intro --id 3 --by claude
    mailbox.py list

Message header format (one line, parseable by any agent):
    ## [3] claude -> codex · request · open · 2026-09-28T09:00:00Z
Kinds: request (asks for work), need (writer asks for information), answer, result, note.
The file lives in $AGENT_MAILBOX_DIR (default ~/.config/herdr-mgr/mailbox/).
"""
import argparse
import datetime as dt
import fcntl
import os
import re
import sys
from pathlib import Path

HDR = re.compile(r"^## \[(\d+)\] (\S+) -> (\S+) · (\w+) · (\w+) · (\S+)\s*$")
KINDS = ("request", "need", "answer", "result", "note")


def box_dir() -> Path:
    d = Path(os.environ.get("AGENT_MAILBOX_DIR", Path.home() / ".config/herdr-mgr/mailbox"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def thread_path(thread: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", thread):
        sys.exit(f"bad thread name: {thread!r}")
    return box_dir() / f"{thread}.md"


def parse(text: str):
    msgs, cur = [], None
    for line in text.splitlines():
        m = HDR.match(line)
        if m:
            cur = dict(id=int(m[1]), frm=m[2], to=m[3], kind=m[4], status=m[5], at=m[6], body=[])
            msgs.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    for m in msgs:
        m["body"] = "\n".join(m["body"]).strip()
    return msgs


def locked(path: Path, fn):
    path.touch(exist_ok=True)
    with open(path, "r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        out = fn(fh)
        fcntl.flock(fh, fcntl.LOCK_UN)
    return out


def cmd_post(a):
    body = Path(a.body_file).read_text() if a.body_file else (a.body or sys.stdin.read())
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def fn(fh):
        text = fh.read()
        nid = max([m["id"] for m in parse(text)] or [0]) + 1
        if not text:
            fh.write(f"# Mailbox thread: {a.thread}\n\n")
        fh.write(f"\n## [{nid}] {a.frm} -> {a.to} · {a.kind} · open · {now}\n")
        if a.reply_to:
            fh.write(f"re: [{a.reply_to}]\n")
        fh.write(body.rstrip() + "\n")
        return nid

    nid = locked(thread_path(a.thread), fn)
    print(f"posted [{nid}] to {thread_path(a.thread)}")


def cmd_read(a):
    p = thread_path(a.thread)
    msgs = parse(p.read_text()) if p.exists() else []
    for m in msgs:
        if a.to and m["to"] not in (a.to, "all"):
            continue
        if a.open and m["status"] != "open":
            continue
        print(f"## [{m['id']}] {m['frm']} -> {m['to']} · {m['kind']} · {m['status']} · {m['at']}\n{m['body']}\n")


def cmd_close(a):
    def fn(fh):
        text = fh.read()
        pat = re.compile(rf"^(## \[{a.id}\] \S+ -> \S+ · \w+ · )open( · \S+)$", re.M)
        new, n = pat.subn(rf"\1done\2", text)
        if n:
            fh.seek(0); fh.write(new); fh.truncate()
        return n

    n = locked(thread_path(a.thread), fn)
    print(f"closed [{a.id}]" if n else f"no open message [{a.id}]")


def cmd_list(_a):
    for p in sorted(box_dir().glob("*.md")):
        msgs = parse(p.read_text())
        print(f"{p.stem}: {len(msgs)} messages, {sum(m['status'] == 'open' for m in msgs)} open")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("post"); p.add_argument("--thread", required=True); p.add_argument("--from", dest="frm", required=True)
    p.add_argument("--to", required=True); p.add_argument("--kind", choices=KINDS, default="request")
    p.add_argument("--body"); p.add_argument("--body-file"); p.add_argument("--reply-to", type=int); p.set_defaults(fn=cmd_post)
    p = sp.add_parser("read"); p.add_argument("--thread", required=True); p.add_argument("--to"); p.add_argument("--open", action="store_true"); p.set_defaults(fn=cmd_read)
    p = sp.add_parser("close"); p.add_argument("--thread", required=True); p.add_argument("--id", type=int, required=True); p.add_argument("--by"); p.set_defaults(fn=cmd_close)
    p = sp.add_parser("list"); p.set_defaults(fn=cmd_list)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
