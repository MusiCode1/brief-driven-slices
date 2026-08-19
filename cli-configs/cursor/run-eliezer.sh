#!/usr/bin/env bash
# מריץ את אליעזר על Cursor Composer במקום על סוכן-Task.
# שימוש:  run-eliezer.sh <worktree> <brief-path> ["הערות נוספות"]
set -euo pipefail
WT="${1:?worktree}"; BRIEF="${2:?brief}"; EXTRA="${3:-}"
ROLE="$(dirname "${BASH_SOURCE[0]}")/agents/eliezer.md"
[[ -f $ROLE ]] || { echo "חסר $ROLE — הרץ שוב את שלב ההצבה" >&2; exit 2; }

cd "$WT"
PROMPT="$(cat "$ROLE")

────────────────────────────────────────
# המשימה

Brief: $BRIEF
Worktree: $(pwd)   (אתה כבר כאן)

קרא את הבריף במלואו לפני שאתה כותב שורה. קרא גם את AGENTS.md בשורש —
שם כל ה-env של הפרויקט (פורטים, בילד, hooks, כללי-פריוויו).

🔴 קמט אחרי כל commit לפי סדר-הקומיטים בבריף. עבודה לא-מקומטת אבדה
בעבר כשתהליך נקטע.

$EXTRA"

exec cursor-agent -p --force --model composer-2.5 "$PROMPT"
