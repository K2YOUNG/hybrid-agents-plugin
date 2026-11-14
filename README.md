# hybrid-agents

A Claude Code plugin with one skill, **Hybrid Agent Orchestrator**. The agent that invokes it acts as
the orchestrator and routes work by task type between Claude, Codex CLI, Antigravity (`agy`) and local
[Herdr](https://herdr.dev) sessions: prose to agy or Codex, figures and pages to Codex, coding to Claude,
token-heavy mechanical work to agy `flash`. English and Korean requests are both supported.

## Install

```
/plugin marketplace add K2YOUNG/hybrid-agents-plugin
/plugin install hybrid-agents@hybrid-agents
```

Then run `/hybrid-agents:hybrid-agent-orchestrator` (or just describe the task).

## Requirements

The skill delegates to other tools, so install what you want to use:

- **Codex CLI** (`codex`) for design and prose delegation
- **Antigravity CLI** (`agy`) for bulk work and long-context reads
- **Herdr** (`herdr`) for multi-session messaging (optional: without it the skill uses one-shot CLI calls and a shared-markdown mailbox)
- Python 3 and Bash for the bundled scripts

State lives in `~/.config/herdr-mgr/` (override with `$HERDR_MGR_HOME`); nothing is written inside the plugin.

## Layout

```
.claude-plugin/   marketplace.json, plugin.json
skills/hybrid-agent-orchestrator/
  SKILL.md        routing rules
  scripts/        agy-delegate.sh, codex_bridge.py, herdr_sync.py, mailbox.py, ...
  references/     upstream notes for agy, Codex and Herdr
```

## License

MIT, see `LICENSE`.
