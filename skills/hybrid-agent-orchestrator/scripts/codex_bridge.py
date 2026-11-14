#!/usr/bin/env python3
"""Small JSON bridge from Claude Code to the Codex CLI.

The bridge intentionally emits one JSON result and keeps Codex's event stream out of
Claude's context unless --return-all-messages is requested.  SESSION_ID enables
multi-turn continuation.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Codex Bridge")
    p.add_argument("--PROMPT", required=True)
    p.add_argument("--cd", required=True)
    p.add_argument("--sandbox", choices=("read-only", "workspace-write", "danger-full-access"), default="read-only")
    p.add_argument("--SESSION_ID", default="")
    p.add_argument("--return-all-messages", action="store_true")
    p.add_argument("--image", action="append", default=[])
    p.add_argument("--model", default="")
    p.add_argument("--profile", default="")
    p.add_argument("--yolo", action="store_true")
    p.add_argument("--skip-git-repo-check", action="store_true")
    args = p.parse_args()

    if not os.path.isdir(args.cd):
        return emit(False, error=f"workspace does not exist: {args.cd}")
    if shutil.which("codex") is None:
        return emit(False, error="codex CLI not found on PATH")

    cmd = ["codex", "exec", "--sandbox", args.sandbox, "--cd", args.cd, "--json"]
    if args.image:
        cmd += ["--image", ",".join(str(Path(x)) for x in args.image)]
    if args.model:
        cmd += ["--model", args.model]
    if args.profile:
        cmd += ["--profile", args.profile]
    if args.yolo:
        cmd += ["--yolo"]
    if args.skip_git_repo_check:
        cmd += ["--skip-git-repo-check"]
    if args.SESSION_ID:
        cmd += ["resume", args.SESSION_ID]
    cmd += ["--", args.PROMPT]

    events = []
    messages = []
    thread_id = None
    errors = []
    try:
        proc = subprocess.Popen(cmd, cwd=args.cd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        assert proc.stdout is not None
        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                errors.append(line)
                continue
            events.append(event)
            thread_id = event.get("thread_id", thread_id)
            item = event.get("item") or {}
            if item.get("type") == "agent_message":
                messages.append(item.get("text", ""))
            if event.get("type", "").startswith("error") or event.get("type", "").endswith("failed"):
                errors.append(event.get("message") or (event.get("error") or {}).get("message", "Codex reported failure"))
        rc = proc.wait()
    except OSError as exc:
        return emit(False, error=str(exc))

    if rc != 0:
        errors.append(f"codex exited with status {rc}")
    if not thread_id:
        errors.insert(0, "Codex did not return a SESSION_ID")
    if not messages:
        errors.insert(0, "Codex did not return agent_messages")
    result = {"success": not errors, "SESSION_ID": thread_id,
              "agent_messages": "".join(messages)}
    if errors:
        result = {"success": False, "error": "\n\n".join(str(e) for e in errors)}
    if args.return_all_messages:
        result["all_messages"] = events
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 2


def emit(success: bool, **payload: object) -> int:
    print(json.dumps({"success": success, **payload}, ensure_ascii=False, indent=2))
    return 0 if success else 2


if __name__ == "__main__":
    raise SystemExit(main())
