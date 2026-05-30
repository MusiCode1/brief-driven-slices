#!/usr/bin/env bash
# dispatch-executor.sh <project> <slice> <worktree> [agent]
# ‏ה-worktree ‏מועבר ‏כ-arg (‏יתרו ‏יודע ‏אותו ‏מ-state.json — ‏לא ‏מפרסר ‏עם grep ‏שביר)
set -euo pipefail
PROJECT="$1"; SLICE="$2"; WORKTREE="$3"; AGENT="${4:-eliezer}"
STATE="$HOME/.local/state/brief-driven-slices/$PROJECT"
mkdir -p "$STATE"/{dispatches,logs,sentinels,heartbeats,crashes,archived,blocked}

PROMPT="$STATE/dispatches/$SLICE.prompt"
LOG="$STATE/logs/$SLICE.log"
SENTINEL="$STATE/sentinels/$SLICE.done"

# ‏נתיב ‏מלא ל-opencode (‏תיקון B2 — PATH ‏לא ‏מובטח ‏ב-tmux non-interactive)
OPENCODE_BIN="$HOME/.opencode/bin/opencode"

# ‏env scrub ‏מלא ‏(תיקון B1 + N-new-1): ‏מנקה ‏את ‏**‏כל** ‏OPENCODE_* ‏ב-prefix,
# ‏לא whitelist ‏של ‏שמות ‏מפורשים (‏שדולף ‏על vars ‏עתידיים כמו OPENCODE_GEMINI_PROJECT_ID).
SCRUB=$(env | grep -o '^OPENCODE_[^=]*' | sed 's/^/-u /' | tr '\n' ' ')

# ‏ה-prompt ‏מועבר ‏דרך stdin (‏תיקון N6). BDS_* ‏ל-heartbeat + blocked.json (‏תיקון M2/#E).
# BDS_STATE_DIR ‏מוזרק ‏מפורשות ‏כדי ‏שאליעזר ‏לא ‏יבנה path ‏ידנית (‏מקור ‏לבאגים).
tmux new-session -d -s "bds-$PROJECT-$SLICE" \
  "cd '$WORKTREE' && \
   env $SCRUB BDS_PROJECT='$PROJECT' BDS_SLICE='$SLICE' BDS_STATE_DIR='$STATE' \
       '$OPENCODE_BIN' run --agent '$AGENT' < '$PROMPT' > '$LOG' 2>&1; \
   echo \"\$?\" > '$SENTINEL'"

echo "dispatched: bds-$PROJECT-$SLICE (tmux)"
