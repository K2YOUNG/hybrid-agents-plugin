# hybrid-agents

A Claude Code plugin with one skill, **Hybrid Agent Orchestrator**. The agent that invokes it acts as
the orchestrator and routes work by task type between Claude, Codex CLI, Antigravity (`agy`) and local
[Herdr](https://herdr.dev) sessions: prose to agy or Codex, figures and pages to Codex, coding to Claude,
token-heavy mechanical work to agy `flash`. English and Korean requests are both supported.

New here? Read the step-by-step guide: [English](GUIDE.md) · [한국어](GUIDE.ko.md)

Or let your coding agent do it. Paste this into Claude Code:

```
Follow https://github.com/K2YOUNG/hybrid-agents-plugin/blob/main/GUIDE.md to install and set up the hybrid-agents plugin for me. Run the commands yourself, and stop and tell me whenever I need to do something.
```

## Install

```
/plugin marketplace add K2YOUNG/hybrid-agents-plugin
/plugin install hybrid-agents@hybrid-agents
```

Then run `/hybrid-agents:hybrid-agent-orchestrator` (or just describe the task).

## First run: pick the main agent and the roles

The first time the skill runs it asks you:

1. **Main agent** (the orchestrator): whichever agent invoked the skill (default), or `claude`, `codex`, `agy`, `copilot`.
2. **Who leads each job**: `coding` (default Claude), `prose` (default agy), `design` = figures and pages (default Codex), `bulk` = token-heavy mechanical work (default agy), `review` = second-opinion review (default Codex).
3. **Existing agents**: `ask` (default) or `new`.

The answers are saved to `~/.config/hybrid-agents/config.json` (override with `$HYBRID_AGENTS_CONFIG`). Change them any time:

```
python3 skills/hybrid-agent-orchestrator/scripts/roles.py show
python3 skills/hybrid-agent-orchestrator/scripts/roles.py set coding=codex prose=claude
python3 skills/hybrid-agent-orchestrator/scripts/roles.py reset   # ask again next run
```

## Reusing agents that are already running

With `reuse = ask`, before handing work to another agent the skill lists the matching agents that are
already running (Herdr app `hc` terminals, herdr panes, and Claude Code sessions over Remote Control)
and lets you pick one, or start a new session. If none are running, or you say you want new sessions
for this request, it starts a new session without asking. To see what it would find:

```
python3 skills/hybrid-agent-orchestrator/scripts/list_agents.py
```

## Requirements

The skill delegates to other tools, so install what you want to use:

- **Codex CLI** (`codex`) for design and prose delegation
- **Antigravity CLI** (`agy`) for bulk work and long-context reads
- **GitHub Copilot CLI** (`copilot`), if you give it a role
- **Herdr** (`herdr`) for multi-session messaging (optional: without it the skill uses one-shot CLI calls and a shared-markdown mailbox)
- Python 3 and Bash for the bundled scripts

State lives in `~/.config/herdr-mgr/` (override with `$HERDR_MGR_HOME`); nothing is written inside the plugin.

## Layout

```
.claude-plugin/   marketplace.json, plugin.json
skills/hybrid-agent-orchestrator/
  SKILL.md        routing rules
  scripts/        roles.py, list_agents.py, agy-delegate.sh, codex_bridge.py, herdr_sync.py, mailbox.py, ...
  references/     upstream notes for agy, Codex and Herdr
```

## License

MIT, see `LICENSE`.
