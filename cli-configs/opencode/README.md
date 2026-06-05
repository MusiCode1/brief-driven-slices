# OpenCode Adapter

OpenCode uses Markdown agent definitions with YAML front matter.

The generated adapter files are:

- `cli-configs/opencode/agents/mordechai.md`
- `cli-configs/opencode/agents/yetro.md`
- `cli-configs/opencode/agents/eliezer.md`
- `cli-configs/opencode/agents/avigail.md`
- `cli-configs/opencode/agents/calev.md`
- `cli-configs/opencode/agents/calev-heavy.md`

The canonical source is `agent-definitions/agents.json` plus
`agent-definitions/prompts/*.md`.

Install them with:

```bash
bash scripts/install-cli-configs.sh opencode
```

The installer symlinks these files into `~/.config/opencode/agents/`.
