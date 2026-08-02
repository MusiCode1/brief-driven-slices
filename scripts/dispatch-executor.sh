#!/usr/bin/env bash
# dispatch-executor.sh <project> <slice> <worktree> [agent]
# ‏ה-worktree ‏מועבר ‏כ-arg (‏יתרו ‏יודע ‏אותו ‏מ-state.json — ‏לא ‏מפרסר ‏עם grep ‏שביר)
set -euo pipefail
PROJECT="$1"; SLICE="$2"; WORKTREE="$3"; AGENT="${4:-eliezer}"
STATE="$HOME/.local/state/brief-driven-slices/$PROJECT"
mkdir -p "$STATE"/{dispatches,logs,sentinels,heartbeats,crashes,archived,blocked,outcomes}

PROMPT="$STATE/dispatches/$SLICE.prompt"
LOG="$STATE/logs/$SLICE.log"
SENTINEL="$STATE/sentinels/$SLICE.done"

# ‏executor CLI runtime — ‏ניתן ‏לבחירה ‏דרך BDS_EXECUTOR_CLI (default: opencode).
# claude ‏נוסף 2026-07-22 (opencode ‏קרס ‏על ‏drive-coding עם "Unexpected server error"
# ‏— ‏בעיית ‏config/auth ‏של ‏opencode; claude ‏רץ ‏נקי). ‏שני ‏המסלולים ‏מזינים prompt ‏מ-stdin.
EXECUTOR_CLI="${BDS_EXECUTOR_CLI:-opencode}"

# ‏env scrub ‏מלא ‏(תיקון B1 + N-new-1): ‏מנקה ‏את ‏**‏כל** ‏OPENCODE_* ‏ב-prefix,
# ‏לא whitelist ‏של ‏שמות ‏מפורשים (‏שדולף ‏על vars ‏עתידיים כמו OPENCODE_GEMINI_PROJECT_ID).
# ‏הערה (יתרו 2026-07-22): grep ‏מחזיר exit 1 ‏כשאין ‏אף OPENCODE_* ‏ב-env —
# ‏עם pipefail ‏זה ‏מפיל ‏את ‏כל ‏ה-script ‏לפני ‏ה-dispatch. ‏|| true ‏לא ‏משנה ‏התנהגות
# (‏עדיין ‏מנקה ‏את ‏כל ‏מה ‏שכן ‏נמצא), ‏רק ‏מונע crash ‏כש-SCRUB ‏אמור ‏לצאת ‏ריק.
SCRUB=$( (env | grep -o '^OPENCODE_[^=]*' || true) | sed 's/^/-u /' | tr '\n' ' ')

# ‏פקודת ‏ה-executor ‏לפי ‏ה-CLI (‏נתיב ‏מלא — PATH ‏לא ‏מובטח ‏ב-tmux non-interactive)
if [ "$EXECUTOR_CLI" = "claude" ]; then
  EXEC_CMD="'$HOME/.local/bin/claude' --agent '$AGENT' --dangerously-skip-permissions -p"
else
  EXEC_CMD="'$HOME/.opencode/bin/opencode' run --agent '$AGENT'"
fi

# ‏ה-prompt ‏מועבר ‏דרך stdin (‏תיקון N6). BDS_* ‏ל-heartbeat + outcomes/<slice>.json.
# BDS_STATE_DIR ‏מוזרק ‏מפורשות ‏כדי ‏שאליעזר ‏לא ‏יבנה path ‏ידנית (‏מקור ‏לבאגים).
tmux new-session -d -s "bds-$PROJECT-$SLICE" \
  "cd '$WORKTREE' && \
   env $SCRUB BDS_PROJECT='$PROJECT' BDS_SLICE='$SLICE' BDS_STATE_DIR='$STATE' \
       $EXEC_CMD < '$PROMPT' > '$LOG' 2>&1; \
   echo \"\$?\" > '$SENTINEL'"

echo "dispatched: bds-$PROJECT-$SLICE (tmux, cli=$EXECUTOR_CLI)"
