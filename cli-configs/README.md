# CLI Config Adapters

This directory contains generated per-CLI configuration adapters for Brief-Driven Slices.

The methodology stays shared; only the CLI-specific packaging changes. Do not
edit generated agent files here directly; edit `agent-definitions/agents.json`
or `agent-definitions/prompts/*.md`, then regenerate.

| CLI | Source | Installed to |
|-----|--------|--------------|
| OpenCode | `cli-configs/opencode/agents/*.md` | `~/.config/opencode/agents/` |
| Codex | `cli-configs/codex/agents/*.toml` | `~/.codex/agents/` |
| Qoder | `cli-configs/qoder/agents/*.md` | `~/.qoder/agents/` |
| Claude Code | `cli-configs/claude-code/agents/*.md` | `~/.claude/agents/` |

Install all supported adapters:

```bash
bash scripts/install-cli-configs.sh all
```

Install one adapter:

```bash
bash scripts/install-cli-configs.sh opencode
bash scripts/install-cli-configs.sh codex
bash scripts/install-cli-configs.sh qoder
bash scripts/install-cli-configs.sh claude-code
```

The installer copies Codex TOML files and symlinks OpenCode Markdown files.
Codex agent files are copied rather than symlinked because Codex config is
usually treated as local user configuration and should continue working even if
the repository moves.

Regenerate without installing:

```bash
python3 scripts/generate-cli-configs.py all
```
