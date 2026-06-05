# Codex Adapter

Codex custom agents are standalone TOML files.

The TOML files under `cli-configs/codex/agents/` are generated. Edit
`agent-definitions/agents.json` or `agent-definitions/prompts/*.md`, then run
`python3 scripts/generate-cli-configs.py codex`.

Install:

```bash
bash scripts/install-cli-configs.sh codex
```

Installed files:

- `~/.codex/agents/mordechai.toml`
- `~/.codex/agents/yetro.toml`
- `~/.codex/agents/eliezer.toml`
- `~/.codex/agents/avigail.toml`
- `~/.codex/agents/calev.toml`
- `~/.codex/agents/calev-heavy.toml`

Codex only spawns subagents when explicitly asked. In normal BDS usage,
Mordechai is the main session that asks Codex to spawn Avigail, Eliezer, Calev,
or Yetro for bounded work.

Recommended project config snippet:

```toml
[agents]
max_threads = 6
max_depth = 1
job_max_runtime_seconds = 3600
```
