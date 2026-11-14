#!/usr/bin/env python3
"""Role setup for the hybrid-agent-orchestrator skill.

Who is the main agent (orchestrator), which agent leads each kind of job, and whether to
reuse already-running agents. The user sets this once at the first run; it is saved and
reused until they change it.

  roles.py show                 effective config as JSON, plus "configured" (false = ask the user first)
  roles.py init [--main A] [--coding A] [--prose A] [--design A] [--bulk A] [--review A] [--reuse ask|new]
                                write the config (unspecified keys keep their defaults)
  roles.py set key=value ...    change some keys (main, coding, prose, design, bulk, review, reuse)
  roles.py reset                delete the config; the next run asks again
  roles.py path                 where the config lives

Agents: claude, codex, agy, copilot. `main` also accepts "invoker" (whichever agent invoked the skill).
reuse: "ask" = list running agents and let the user pick one or a new session; "new" = always start new sessions.
Config file: $HYBRID_AGENTS_CONFIG, else ~/.config/hybrid-agents/config.json
"""
import json
import os
import sys

AGENTS = ("claude", "codex", "agy", "copilot")
JOBS = ("coding", "prose", "design", "bulk", "review")
DEFAULTS = {
    "main": "invoker",
    "coding": "claude",
    "prose": "agy",
    "design": "codex",
    "bulk": "agy",
    "review": "codex",
    "reuse": "ask",
}


def path():
    return os.environ.get("HYBRID_AGENTS_CONFIG") or os.path.expanduser("~/.config/hybrid-agents/config.json")


def load():
    cfg = dict(DEFAULTS)
    p = path()
    configured = os.path.exists(p)
    if configured:
        try:
            with open(p) as f:
                cfg.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
        except Exception as e:  # a broken file must not stop the skill
            print(f"warning: could not read {p}: {e}; using defaults", file=sys.stderr)
            configured = False
    return cfg, configured


def check(key, value):
    if key not in DEFAULTS:
        raise SystemExit(f"unknown key {key!r}; keys: {', '.join(DEFAULTS)}")
    if key == "main" and value not in AGENTS + ("invoker",):
        raise SystemExit(f"main must be one of {', '.join(AGENTS + ('invoker',))}")
    if key in JOBS and value not in AGENTS:
        raise SystemExit(f"{key} must be one of {', '.join(AGENTS)}")
    if key == "reuse" and value not in ("ask", "new"):
        raise SystemExit("reuse must be ask or new")


def save(cfg):
    p = path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump({k: cfg[k] for k in DEFAULTS}, f, indent=2)
        f.write("\n")
    return p


def main(argv):
    cmd = argv[0] if argv else "show"
    if cmd == "show":
        cfg, configured = load()
        print(json.dumps({**cfg, "configured": configured, "path": path()}, indent=2))
    elif cmd == "init":
        cfg = dict(DEFAULTS)
        it = iter(argv[1:])
        for flag in it:
            if not flag.startswith("--"):
                raise SystemExit(f"unexpected argument {flag!r}")
            key = flag[2:]
            value = next(it, None)
            if value is None:
                raise SystemExit(f"{flag} needs a value")
            check(key, value)
            cfg[key] = value
        print(f"saved {save(cfg)}")
        print(json.dumps(cfg, indent=2))
    elif cmd == "set":
        cfg, _ = load()
        for pair in argv[1:]:
            if "=" not in pair:
                raise SystemExit(f"expected key=value, got {pair!r}")
            key, value = pair.split("=", 1)
            check(key, value)
            cfg[key] = value
        print(f"saved {save(cfg)}")
        print(json.dumps(cfg, indent=2))
    elif cmd == "reset":
        p = path()
        if os.path.exists(p):
            os.remove(p)
            print(f"removed {p}; the next run asks the user again")
        else:
            print("no config to remove")
    elif cmd == "path":
        print(path())
    else:
        print(__doc__)
        raise SystemExit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
