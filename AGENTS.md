# AGENTS.md — brief-driven-slices

This repository is the source of truth for the Brief-Driven Slices methodology.

## Project Rules

- Load and follow the user's `dev-conventions` skill before development work.
- Keep CLI-specific agent definitions under `cli-configs/<cli>/`.
- Keep reusable methodology documentation in the root docs and agent files.
- Do not merge branches without explicit user approval.
- Do not remove existing CLI compatibility unless the user explicitly asks.

## Agent Compatibility

The canonical role descriptions are still the OpenCode-style Markdown files in
`agents/`. CLI adapters live in:

- `cli-configs/opencode/` — OpenCode installer metadata. Uses `agents/*.md`.
- `cli-configs/codex/` — Codex custom-agent TOML files.
- `cli-configs/qoder/` — Qoder Markdown agents.
- `cli-configs/claude-code/` — Claude Code Markdown agents (`~/.claude/agents/`).

Install adapters with:

```bash
bash scripts/install-cli-configs.sh all
```

The legacy command still works:

```bash
bash scripts/install-agents.sh
```

## BDS Roles

- Mordechai: planner and merge decision maker.
- Yetro: queue orchestrator.
- Eliezer: executor.
- Avigail: plan verifier.
- Calev: runtime verifier.
- Calev-heavy: heavy runtime verifier.

Dispatch (how roles are spawned): `docs/dispatch.md` — MCP first, HTTP API as backup.

In Codex, Mordechai is normally the parent/main session. The other roles are
custom subagents.
