---
name: hybrid-agent-orchestrator
description: Orchestration that routes work by task type between Claude, Codex CLI, Antigravity (agy), and local Herdr sessions. The agent that invokes the skill is the orchestrator; coding is always led by Claude. Prose (papers, reports, docs) is written by agy or Codex while Claude supplies facts; figures and pages (.svg, .html, plots) are designed by Codex; bulk reading and boilerplate go to agy/Codex to save the orchestrator's tokens. Includes a transport ladder (native same-provider messaging, herdr, one-shot CLI, shared-markdown mailbox). Accepts English and Korean requests.
license: MIT
metadata:
  category: developer-tooling
---

# Hybrid Agent Orchestrator

**The agent that invoked this skill is the orchestrator** (Claude, Codex or agy). It owns requirements, the plan, routing, integration, and final verification, and it does not spend its own tokens on work another agent is assigned below. **Coding is the one exception: Claude is always the main coder**, whoever orchestrates; a Codex or agy orchestrator hands coding components to Claude (`claude -p`, herdr, or the mailbox) and verifies the result.

In the rest of this file, "Claude" in the role columns means "the orchestrator" except for coding rows. English and Korean requests are equivalent; answer in the user's language.

**Bulk work** means high-volume, low-judgment work where the output is easy to check and the tokens spent mostly go to reading or typing, not thinking: summarizing long logs, PDFs or result files into a digest; sweeping a repo for every call site; generating many similar files, tests, or table rows; mechanical renames and migrations; reformatting data. It is what you delegate to save the orchestrator's context.

## 1. Route by task type first

| Task type | Lead (writes the artifact) | Claude's role | Support |
|---|---|---|---|
| Paper sections, reports, rebuttals, READMEs, emails, any prose | **agy `pro`** (long-form, grounded) or **Codex** (tight technical prose); pick one per document and keep it | Information provider: brief, fact pack, answers to `NEED:` requests, fact-check of the draft | agy `flash` for literature digests |
| Figures and pages: `.svg`, `.html`, slide/diagram layouts, matplotlib/plotly styling | **Codex** (main designer) | Supplies implementation details, experiment numbers with source paths, paper summaries, exact labels | agy `flash` fetches or summarizes source material Codex asks for |
| Coding of any size: architecture, multi-file changes, bugs, scripts, experiments code | **Claude** (always, even when Codex or agy orchestrates) | Owner | Codex for a second-opinion review; agy `flash` for tests and boilerplate |
| Token-heavy mechanical work: scaffolding, test generation, migrations, long-log or long-PDF summaries, repo sweeps | **agy `flash`** (deterministic bulk) or **Codex** | Writes the contract, verifies the digest and diff | — |

The user's explicit choice of agent overrides this table. If the lead agent is unavailable (quota, auth, repeated timeout), fall back in this order: prose agy → Codex → Claude (say so); design Codex → agy `pro` → Claude (say so); bulk agy `flash` → Codex → Claude.

### Writer mode (prose): Claude never drafts the text

Claude must not write the paragraphs itself, even "just a first pass". It instead:

1. Writes a **brief** (`brief.md` in the thread dir or the mailbox): audience, venue and page budget, the one claim each section must make, the outline if the user approved one, tone samples (point at existing sections rather than pasting them), terms to define, banned claims.
2. Writes a **fact pack**: every number, name and citation the writer may use, each with its source file and field (e.g. `0.672 — results/<run>.json: success_rate`). Numbers come from files read in this run, never from memory or chat. Caveats (pending fixes, non-significant results, cross-box pairs) travel with the number.
3. Tells the writer: "Use only facts in the pack. When you need anything else, emit a line `NEED: <question>` and stop, or continue with a `[NEED-n]` placeholder." Claude answers each `NEED:` from files, adds the answer to the fact pack, and returns it.
4. Reviews the draft for **facts only**: every number against the pack, every citation against the bib, every claim against the evidence. Claude returns a numbered correction list; the writer applies it. Claude does not rewrite style.
5. Pushing to Overleaf/git still follows the user's approval rule.

### Designer mode (figures, pages): Codex leads

1. Claude sends Codex the data (CSV/JSON path, or a fact table), the message the figure must carry, the target (paper column width in pt, slide 1920x1080, light/dark), fonts and palette if the project has them, and where the output goes.
2. Codex owns layout, typography, color, and code. When it lacks information it asks (`NEED:`); Claude answers with sourced facts or dispatches agy `flash` to dig them out.
3. Claude checks the rendered output (open the PNG/PDF, or render the SVG/HTML to PNG and look): numbers match the data, labels are correct, nothing overflows or clips. Design critiques go back to Codex as a list; Claude does not redraw.

## 2. Plan and score before delegating

1. Restate the outcome and constraints.
2. Split into components; score each 1–5 on `expected_tokens`, `expected_time`, `difficulty`, `coupling`, `verification_cost`.
3. Apply the task-type table, then keep in Claude anything with high difficulty, coupling, ambiguity, or verification cost that is not prose or design.
4. Delegate only well-specified components; one big delegation beats many small ones (each round trip costs Claude context).

| Component | tokens | time | difficulty | coupling | verify | owner/model | acceptance check |
|---|---:|---:|---:|---:|---:|---|---|

Break-even: a delegation costs a contract + a digest + a verification. Skip it for tasks Claude can finish in a few short tool calls.

## 3. Communication: the transport ladder

Pick the first rung that works; drop a rung after two failures of the same kind.

**Same provider — use the provider's own channel.**
- Claude ↔ Claude: `ListAgents` + `SendMessage` (cross-session, including Remote Control sessions). Copy the incoming `from` as `to` when replying. Subagents: the Agent tool.
- Codex ↔ Codex: continue the same thread (`codex_bridge.py --SESSION_ID`, or `codex exec resume <id>`), or Codex's own subagents inside one session.
- agy ↔ agy: `agy --conversation <id>` / `agy -c` continuation, or one pane in herdr.

**Cross provider.**
1. **herdr** (optional; skip this rung if `herdr` is not installed) when both sides have a local pane: `herdr_sync.py status` → `send <label> "<contract>"` → `wait <label> 600` → `read <label> 80`. Observable and recoverable by the user. Local only; never SSH/remote herdr from this skill.
2. **One-shot CLI** when a single prompt and answer is enough:
   - agy: the wrapper `bash "${CLAUDE_SKILL_DIR}/scripts/agy-delegate.sh" --tier flash|pro --dir <repo> --timeout 600 --digest "<task>"` (or plain `agy -p "<task>" --output-format json`).
   - Codex: `python3 "${CLAUDE_SKILL_DIR}/scripts/codex_bridge.py" --cd <repo> --PROMPT "<task>" --sandbox read-only` (wraps `codex exec --json`; Codex has no `-p` for prompts — `-p` is a config profile).
   - Claude (from Codex/agy): `claude -p "<task>" --output-format json`.
3. **Shared-markdown mailbox** when both of the above are impossible or keep erroring:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/mailbox.py" post --thread <topic> --from claude --to codex --kind request --body-file req.md`
   The other agent reads with `mailbox.py read --thread <topic> --to codex --open` (or opens `~/.config/herdr-mgr/mailbox/<topic>.md` directly), appends `need`/`result` messages, and closes handled ids. Tell the other agent the file path once, over any channel (or the user relays it).

Every message, on every rung, is a **delegation contract**: objective; exact files/dirs; constraints; acceptance criteria; output format (ask for a `===DIGEST===` block: changed files, decisions, assumptions, open `NEED:`s); what to report back. Never rely on `@path` attachments across sessions: send the text or a path.

## 4. Operating agy (lessons from past sessions)

- Always use the wrapper with `--dir <repo>` so agy reads real files instead of pasted context; add `--digest` for any read/summarize task. A "looks like a raw dump" warning means re-run with `--digest`; do not ingest the dump.
- **Writes need a grant.** Exit 15 / `denied_actions` = agy's write was refused. Fix with a narrow `write_file(<dir>)` rule in `~/.gemini/antigravity-cli/settings.json` `permissions.allow`; use `--yolo` only for web search/terminal tools, and only on a dedicated branch. Check `git status` afterwards: a "done" with no diff is a failure.
- **Timeouts and quota are routine.** Pass `--timeout`; for long jobs in an interactive session use `agy-job start` and collect later (never in headless `claude -p`, which has no later turn). On a quota/auth signal, switch to the fallback agent instead of retrying. For measurable work set `--timeout` and `AGY_USAGE_LOG`, and summarize usage with `python3 "${CLAUDE_SKILL_DIR}/scripts/measure-session.py"`; react to the structured quota/auth/timeout/model/permission signals rather than scraping stderr.
- agy drafts contain confident factual errors (a delegated appendix shipped a wrong example and wrong constraints). Every agy-written number, example and citation is checked by Claude against files before it is used.
- When agy or Codex is itself the object of an experiment (a baseline), run it from an empty directory with tools disallowed, so project memory and the grader are not reachable.

## 5. Operating Codex

`python3 "${CLAUDE_SKILL_DIR}/scripts/codex_bridge.py" --cd <repo> --PROMPT "<task>" --sandbox read-only|workspace-write [--image fig.png] [--SESSION_ID <id>]` returns `success`, `SESSION_ID`, `agent_messages`. Save `SESSION_ID` for follow-ups (design iterations should stay in one session); add `--return-all-messages` only when the full event trace is needed. Use `workspace-write` only for approved edits; pass `--image` to show Codex the current render or a reference figure. Do not pass `--model`, `--profile`, or bypass flags unless the user asks. Claude reviews the filesystem diff and the rendered output.

## 6. Local Herdr transport

Reuse an existing pane by stable label; inspect before sending:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/herdr_sync.py" status
python3 "${CLAUDE_SKILL_DIR}/scripts/herdr_sync.py" read <agent> 40
python3 "${CLAUDE_SKILL_DIR}/scripts/herdr_sync.py" send <agent> "<delegation contract>"
python3 "${CLAUDE_SKILL_DIR}/scripts/herdr_sync.py" wait <agent> 600
```

`herdr_sync.py` also handles topology discovery, idempotent revival, permission pending/approve/deny/dismiss, dry-run/live modes, idle nudging and decision logs; state lives in `~/.config/herdr-mgr/` (or `$HERDR_MGR_HOME`). The companion scripts `herdr-act.sh` and `attach-herdr-agent.sh` provide safe action wrapping and attach behavior. Address panes by label, never by unstable pane IDs. Configure `remotes: []`. Read the policy before judging prompts, start in `dryrun`, auto-approve only the plain "Yes" in explicitly enabled live mode, escalate anything uncertain, never auto-deny.

## 7. Migrating a Claude skill for agy

Keep the Claude skill as the source of truth. Run the read-only planner first (`python3 "${CLAUDE_SKILL_DIR}/scripts/agy-migrate.py" --help`), review its plan, then apply. It preserves the upstream safeguards for absolute paths, trigger-compatible rules, project binding, non-destructive manifests, and unsupported hooks/tools. Test the migrated skill through agy (preferably in a herdr pane) and verify in Claude.

## 8. Verification is Claude's job, always

- Code: inspect the diff, run the tests or a real acceptance check. Never accept a success message as proof (agy has been seen patching its own environment to force a pass).
- Prose: fact-check against the fact pack and source files; return corrections, do not rewrite.
- Figures/pages: render and look; check every number and label against the data.
- Report outcomes faithfully to the user: who wrote what, what was verified, what was not.

Reference copies of the upstream approaches: `references/antigravity-upstream.md`, `references/herdr-upstream.md`, `references/codex-upstream.md`. Scripts: `agy-delegate.sh` (bash), `codex_bridge.py`, `herdr_sync.py`, `mailbox.py`, `agy-migrate.py`, `measure-session.py`.
