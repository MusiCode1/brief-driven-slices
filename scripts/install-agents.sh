#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Backward-compatible wrapper: the old command installs the OpenCode adapter.
# The broader multi-CLI installer lives in install-cli-configs.sh.
bash "$ROOT/scripts/install-cli-configs.sh" opencode
