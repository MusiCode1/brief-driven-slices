#!/usr/bin/env bash
# wait-for-slice.sh <project> <slice> [timeout-min]
# ‏מחזיר exit code ‏של ‏ה-executor; 124 ‏על timeout.
set -euo pipefail
PROJECT="$1"; SLICE="$2"; TIMEOUT_MIN="${3:-120}"
STATE="$HOME/.local/state/brief-driven-slices/$PROJECT"
SENTINEL="$STATE/sentinels/$SLICE.done"
HEARTBEAT="$STATE/heartbeats/$SLICE.last"
TMUX_SESSION="bds-$PROJECT-$SLICE"

elapsed=0; poll=30
while [[ ! -f "$SENTINEL" ]]; do
  # ‏crash detection: tmux ‏מת ‏ללא sentinel
  if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "CRASHED: tmux session gone, no sentinel" >&2
    exit 125
  fi
  sleep $poll; elapsed=$((elapsed+poll))
  # heartbeat staleness
  if [[ -f "$HEARTBEAT" ]]; then
    age=$(( $(date +%s) - $(date -r "$HEARTBEAT" +%s) ))
    (( age > 1800 )) && echo "warn: heartbeat stale ${age}s" >&2
  fi
  # timeout
  if (( elapsed > TIMEOUT_MIN*60 )); then
    tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
    echo "TIMEOUT after ${TIMEOUT_MIN}min" >&2
    exit 124
  fi
done
cat "$SENTINEL"   # exit code ‏של ‏ה-executor
