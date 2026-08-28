# Agent Definitions

This directory is the canonical source for BDS agent configuration.

- `agents.json` stores structured metadata per role and per CLI.
- `prompts/*.md` stores the long role instructions.

Generated outputs:

- `cli-configs/codex/agents/*.toml`
- `cli-configs/opencode/agents/*.md`
- `cli-configs/qoder/agents/*.md`
- `cli-configs/claude-code/agents/*.md`
- `agents/*.md` for legacy OpenCode compatibility

Regenerate outputs:

```bash
python3 scripts/generate-cli-configs.py
```

Then install them:

```bash
bash scripts/install-cli-configs.sh all
```
