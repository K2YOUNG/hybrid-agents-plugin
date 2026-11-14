# Codex bridge reference

Source: https://github.com/GuDaStudio/collaborating-with-codex

The upstream Claude Code skill wraps `codex exec --json` and returns a compact JSON
object with `success`, `SESSION_ID`, `agent_messages`, and optional `all_messages`.
Its notable behaviors are resumable multi-turn sessions, explicit `read-only`,
`workspace-write`, and `danger-full-access` sandboxes, image forwarding, optional
model/profile selection, and non-zero failure reporting. These behaviors are
implemented locally in `scripts/codex_bridge.py`.

The hybrid skill keeps the same contract for Antigravity where its CLI supports it:
`scripts/agy-delegate.sh` provides continuation, sandboxing, model selection, digest
output, and structured usage/failure signals. Claude remains responsible for routing,
reviewing diffs, and running acceptance checks.
