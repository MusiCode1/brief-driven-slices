#!/usr/bin/env bash
set -euo pipefail
SRC="$HOME/projects/brief-driven-slices/agents"
DST="$HOME/.config/opencode/agents"
mkdir -p "$DST"
for agent in mordechai yetro eliezer avigail calev; do
  ln -sfn "$SRC/$agent.md" "$DST/$agent.md"
  echo "linked: $agent"
done
# ‏שים ‏לב: ‏הסקריפטים ‏שמפרסרים state ‏הם python3 (cleanup_state.py, discard_chain.py),
# ‏השאר ‏bash (install/wait/dispatch). ‏ה-`.py` ‏רצים ‏עם python3 ‏ישירות.
# ‏ניקוי symlinks ‏ישנים ‏(executor, plan-verifier, verifier-*)
for old in executor plan-verifier verifier-phase verifier-slice-light verifier-slice-heavy; do
  [[ -L "$DST/$old.md" ]] && rm "$DST/$old.md" && echo "removed old: $old"
done
