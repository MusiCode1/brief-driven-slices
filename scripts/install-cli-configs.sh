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

# resolve_paths — קוראת ${BDS_PATHS_ENV:-$HOME/.config/bds/paths.env} עבור כל משתנה
# שלא הוגדר ישירות ב-env (env גובר על הקובץ), ואז כשל-רועש (:?) על כל 4 המשתנים.
resolve_paths() {
  local paths_env="${BDS_PATHS_ENV:-$HOME/.config/bds/paths.env}"
  if [[ -f "$paths_env" ]]; then
    local var val
    for var in BDS_REPORTS BDS_SCRIPTS BDS_LESSONS BDS_ORCH; do
      if [[ -z "${!var:-}" ]]; then
        val="$(grep -E "^${var}=" "$paths_env" | tail -n1 | cut -d= -f2-)"
        [[ -n "$val" ]] && export "$var=$val"
      fi
    done
  fi

  : "${BDS_REPORTS:?BDS_REPORTS not set — ראה cli-configs/paths.env.example}" \
    "${BDS_SCRIPTS:?BDS_SCRIPTS not set — ראה cli-configs/paths.env.example}" \
    "${BDS_LESSONS:?BDS_LESSONS not set — ראה cli-configs/paths.env.example}" \
    "${BDS_ORCH:?BDS_ORCH not set — ראה cli-configs/paths.env.example}"
}

# substitute_into src dst — מחליף את 4 ה-placeholders ({{BDS_*}}) וכותב ל-dst.
# שכבת-הגנה: אם נשאר {{BDS_ ב-dst אחרי ההחלפה (placeholder לא-מוכר/לא-מוחלף) → exit 1.
substitute_into() {
  local src="$1" dst="$2"
  sed -e "s|{{BDS_REPORTS}}|$BDS_REPORTS|g" \
      -e "s|{{BDS_SCRIPTS}}|$BDS_SCRIPTS|g" \
      -e "s|{{BDS_LESSONS}}|$BDS_LESSONS|g" \
      -e "s|{{BDS_ORCH}}|$BDS_ORCH|g" \
      "$src" > "$dst"
  if grep -q "{{BDS_" "$dst"; then
    echo "error: placeholder לא-מוחלף ב-$dst" >&2
    exit 1
  fi
}

install_opencode() {
  local src="$ROOT/cli-configs/opencode/agents"
  local dst="${OPENCODE_AGENTS_DIR:-$HOME/.config/opencode/agents}"

  mkdir -p "$dst"
  for agent in mordechai yetro eliezer avigail calev calev-heavy; do
    substitute_into "$src/$agent.md" "$dst/$agent.md"
    echo "opencode installed: $agent"
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
    substitute_into "$file" "$dst/$(basename "$file")"
    echo "codex installed: $(basename "$file")"
  done

  mkdir -p "$ROOT/.codex"
  cp "$ROOT/cli-configs/codex/config.toml" "$project_config"
  echo "codex project config written: $project_config"
}

main() {
  generate_configs
  resolve_paths

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
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main
fi
