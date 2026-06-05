#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-all}"
PYTHON_BIN="${PYTHON:-}"
POWERSHELL_BIN=""

if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  elif command -v powershell.exe >/dev/null 2>&1 && command -v wslpath >/dev/null 2>&1; then
    POWERSHELL_BIN="powershell.exe"
  elif command -v pwsh.exe >/dev/null 2>&1 && command -v wslpath >/dev/null 2>&1; then
    POWERSHELL_BIN="pwsh.exe"
  fi
fi

generate_configs() {
  if [[ -n "$PYTHON_BIN" ]]; then
    "$PYTHON_BIN" "$ROOT/scripts/generate-cli-configs.py" "$TARGET"
    return
  fi

  if [[ -n "$POWERSHELL_BIN" ]]; then
    local win_root
    win_root="$(wslpath -w "$ROOT")"
    "$POWERSHELL_BIN" -NoProfile -ExecutionPolicy Bypass -Command \
      "Set-Location -LiteralPath '$win_root'; python scripts\\generate-cli-configs.py '$TARGET'"
    return
  fi

  echo "error: python3, python, or Windows PowerShell with python is required to generate CLI configs" >&2
  exit 1
}

install_opencode() {
  local src="$ROOT/cli-configs/opencode/agents"
  local dst="${OPENCODE_AGENTS_DIR:-$HOME/.config/opencode/agents}"

  mkdir -p "$dst"
  for agent in mordechai yetro eliezer avigail calev calev-heavy; do
    ln -sfn "$src/$agent.md" "$dst/$agent.md"
    echo "opencode linked: $agent"
  done

  for old in executor plan-verifier verifier-phase verifier-slice-light verifier-slice-heavy; do
    if [[ -L "$dst/$old.md" ]]; then
      rm "$dst/$old.md"
      echo "opencode removed old: $old"
    fi
  done
}

install_codex() {
  local src="$ROOT/cli-configs/codex/agents"
  local dst="${CODEX_AGENTS_DIR:-$HOME/.codex/agents}"
  local project_config="$ROOT/.codex/config.toml"

  mkdir -p "$dst"
  for file in "$src"/*.toml; do
    cp "$file" "$dst/$(basename "$file")"
    echo "codex copied: $(basename "$file")"
  done

  mkdir -p "$ROOT/.codex"
  cp "$ROOT/cli-configs/codex/config.toml" "$project_config"
  echo "codex project config written: $project_config"
}

generate_configs

case "$TARGET" in
  all)
    install_opencode
    install_codex
    ;;
  opencode)
    install_opencode
    ;;
  codex)
    install_codex
    ;;
  *)
    echo "usage: $0 [all|opencode|codex]" >&2
    exit 2
    ;;
esac
