#!/usr/bin/env python3
"""List coding agents that are already running, so the orchestrator can hand work to one of them
instead of starting a new session.

  list_agents.py [--platform claude|codex|agy|copilot] [--json]

Sources (each is skipped silently when its tool is not installed or not answering):
  hc      Herdr app terminals (`hc ls --json`)
  herdr   herdr terminal-multiplexer panes (`herdr agent list`)
Claude Code sessions reachable over Remote Control are not listed here: a Claude orchestrator gets
them with its own ListAgents tool.

The caller's own terminal is left out ($HC_TERMINAL_ID / $HERDR_PANE_ID).
Each entry carries the commands to send it a task, wait for it, and read its answer.
"""
import json
import os
import shutil
import subprocess
import sys

KIND = {  # what each tool reports -> platform name used by roles.py
    "claude-code": "claude", "claude": "claude",
    "codex": "codex",
    "antigravity": "agy", "agy": "agy", "gemini": "agy",
    "copilot": "copilot",
}


def run_json(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else None
    except Exception:
        return None


def from_hc():
    if not shutil.which("hc"):
        return []
    d = run_json(["hc", "ls", "--json"])
    if not d:
        return []
    me = os.environ.get("HC_TERMINAL_ID")
    out = []
    for t in d.get("terminals", []):
        plat = KIND.get(t.get("agent") or "")
        if not plat or t.get("address") == me:
            continue
        a = t["address"]
        out.append({
            "platform": plat, "via": "hc", "id": a,
            "label": t.get("where") or t.get("name") or a,
            "status": t.get("status") or "unknown", "cwd": t.get("cwd"),
            "send": f"hc send {a} <contract>",
            "wait": f"hc wait {a}",
            "read": f"hc read {a} --lines 80",
        })
    return out


def from_herdr():
    if not shutil.which("herdr"):
        return []
    d = run_json(["herdr", "agent", "list"])
    if not d:
        return []
    me = os.environ.get("HERDR_PANE_ID")
    panes = run_json(["herdr", "pane", "list"]) or {}
    labels = {x.get("pane_id"): x.get("label") for x in (panes.get("result") or {}).get("panes", []) if x.get("label")}
    out = []
    for p in (d.get("result") or {}).get("agents", []):
        plat = KIND.get(p.get("agent") or "")
        pid = p.get("pane_id")
        if not plat or not pid or pid == me:
            continue
        out.append({
            "platform": plat, "via": "herdr", "id": pid,
            "label": labels.get(pid) or p.get("label") or p.get("terminal_title_stripped") or pid,
            "status": p.get("agent_status") or "unknown", "cwd": p.get("cwd"),
            "send": f"herdr agent prompt {pid} <contract>",
            "wait": f"herdr agent wait {pid} --until idle --until done --until blocked",
            "read": f"herdr agent read {pid}",
        })
    return out


def main(argv):
    want = None
    as_json = "--json" in argv
    if "--platform" in argv:
        i = argv.index("--platform")
        want = argv[i + 1] if i + 1 < len(argv) else None
    agents = from_hc() + from_herdr()
    if want:
        agents = [a for a in agents if a["platform"] == want]
    if as_json:
        print(json.dumps({"agents": agents}, indent=2))
        return
    if not agents:
        print("no running agents found" + (f" for {want}" if want else "") + " (start a new session)")
        return
    for a in agents:
        print(f"{a['platform']:<8} {a['via']:<6} {a['id']:<16} {a['status']:<8} {a['label']}  ({a.get('cwd') or '-'})")


if __name__ == "__main__":
    main(sys.argv[1:])
