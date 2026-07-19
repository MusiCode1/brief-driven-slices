#!/usr/bin/env python3
"""Generate CLI-specific BDS agent files from the canonical definitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS = ROOT / "agent-definitions" / "agents.json"


def quote_toml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def multiline_toml(value: str) -> str:
    escaped = value.replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped.rstrip()}\n"""'


def render_toml_value(value: Any) -> str:
    if isinstance(value, str):
        return quote_toml(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return "[" + ", ".join(quote_toml(item) for item in value) + "]"
    raise TypeError(f"Unsupported TOML value: {value!r}")


def render_codex_agent(agent: dict[str, Any], prompt: str) -> str:
    codex = agent["codex"]
    lines = [
        f"name = {quote_toml(codex['name'])}",
        f"description = {quote_toml(agent['description'])}",
    ]

    for key in ("model", "model_reasoning_effort", "sandbox_mode", "nickname_candidates"):
        if key in codex:
            lines.append(f"{key} = {render_toml_value(codex[key])}")

    lines.extend(["", f"developer_instructions = {multiline_toml(prompt)}"])
    return "\n".join(lines) + "\n"


def render_yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    raise TypeError(f"Unsupported front matter value: {value!r}")


def render_mapping(name: str, mapping: dict[str, Any]) -> list[str]:
    lines = [f"{name}:"]
    for key, value in mapping.items():
        lines.append(f"  {key}: {render_yaml_scalar(value)}")
    return lines


def render_opencode_agent(agent: dict[str, Any], prompt: str) -> str:
    opencode = agent["opencode"]
    lines = [
        "---",
        f"name: {opencode['name']}",
        "description: >",
        f"  {agent['description']}",
        f"mode: {opencode['mode']}",
        f"model: {opencode['model']}",
    ]
    lines.extend(render_mapping("permission", opencode.get("permission", {})))
    lines.extend(render_mapping("tools", opencode.get("tools", {})))
    lines.extend(["---", "", prompt.rstrip(), ""])
    return "\n".join(lines)


def render_yaml_list(name: str, items: list[str]) -> list[str]:
    lines = [f"{name}:"]
    for item in items:
        lines.append(f"  - {item}")
    return lines


def render_qoder_agent(agent: dict[str, Any], prompt: str) -> str:
    qoder = agent["qoder"]
    lines = [
        "---",
        f"name: {qoder['name']}",
        "description: >",
        f"  {agent['description']}",
        f"model: {qoder['model']}",
        f"permissionMode: {qoder['permissionMode']}",
        f"effort: {qoder['effort']}",
    ]
    lines.extend(render_yaml_list("tools", qoder["tools"]))
    if qoder.get("disallowedTools"):
        lines.extend(render_yaml_list("disallowedTools", qoder["disallowedTools"]))
    if qoder.get("isolation"):
        lines.append(f"isolation: {qoder['isolation']}")
    lines.extend(["---", "", prompt.rstrip(), ""])
    return "\n".join(lines)


def load_definitions() -> dict[str, Any]:
    with DEFINITIONS.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def generate(target: str) -> list[Path]:
    definitions = load_definitions()
    changed: list[Path] = []

    for agent_id, agent in definitions["agents"].items():
        prompt_path = ROOT / "agent-definitions" / agent["prompt"]
        prompt = prompt_path.read_text(encoding="utf-8")

        if target in ("all", "codex"):
            content = render_codex_agent(agent, prompt)
            output = ROOT / "cli-configs" / "codex" / "agents" / f"{agent_id}.toml"
            if write_if_changed(output, content):
                changed.append(output)

        if target in ("all", "opencode"):
            content = render_opencode_agent(agent, prompt)
            for output in (
                ROOT / "cli-configs" / "opencode" / "agents" / f"{agent_id}.md",
                ROOT / "agents" / f"{agent_id}.md",
            ):
                if write_if_changed(output, content):
                    changed.append(output)

        if target in ("all", "qoder"):
            content = render_qoder_agent(agent, prompt)
            output = ROOT / "cli-configs" / "qoder" / "agents" / f"{agent_id}.md"
            if write_if_changed(output, content):
                changed.append(output)

    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", choices=("all", "codex", "opencode", "qoder"), default="all")
    args = parser.parse_args()

    changed = generate(args.target)
    for path in changed:
        print(f"generated: {path.relative_to(ROOT)}")
    if not changed:
        print("generated: no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
