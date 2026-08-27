#!/usr/bin/env bash
# await-dispatch — ‏מחזיק את ההמתנה לסוכן ששוגר, ‏ומכריע סיום לפי **‏ארטיפקט**.
#
# ‏נולד מפער 1+2 ‏ב-autonomous-runs/OPEN-GAPS.md (‏ריצה 19):
#   ‏פער 1 — ‏תור של מרדכי הסתיים בעוד ילד ה-tmux ‏רץ, ‏ואיש לא החזיק את ההמתנה.
#   ‏פער 2 — ‏`acpx` ‏יצא 0 ‏אחרי ניתוק-תעבורה באמצע העבודה; ‏הסנטינל שיקר.
#
# ⇒ ‏הסנטינל הוא אות-**‏חיוּת** ‏בלבד. ‏הסיום נקבע ע"י `git log`/`git status`.
#
# ‏שימוש:
#   await-dispatch <name> --repo <path> --branch <ref> --base <ref> \
#                  --expect-commits <n> [--timeout <sec>]
#
# ‏קודי-יציאה — ‏**‏מובחנים בכוונה**:
#   0  ‏הושלם ואומת   — ‏סנטינל ירה, ‏מספר הקומיטים תואם, ‏העץ נקי
#   2  ‏עדיין רץ       — ‏פג ה-timeout ‏של הקריאה הזו. ‏**‏לא כישלון** — ‏קרא שוב
#   3  ‏סנטינל ירה אך העבודה **‏חלקית** — ‏זה בדיוק הכשל של ריצה 19
#   4  ‏שגיאת-שימוש
set -uo pipefail

NAME="${1:?usage: await-dispatch <name> --repo P --branch B --base R --expect-commits N}"; shift
REPO="" BRANCH="" BASE="" EXPECT="" TIMEOUT=570 WORKTREE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --base) BASE="$2"; shift 2 ;;
    --expect-commits) EXPECT="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --worktree) WORKTREE="$2"; shift 2 ;;
    *) echo "await-dispatch: unknown arg $1" >&2; exit 4 ;;
  esac
done
[ -n "$REPO" ] && [ -n "$BRANCH" ] && [ -n "$BASE" ] && [ -n "$EXPECT" ] || {
  echo "await-dispatch: --repo/--branch/--base/--expect-commits ‏חובה" >&2; exit 4; }

# ‏🔴 ‏העץ שנבדק הוא זה שהמבצע עובד בו. ‏בלי --worktree ‏הבדיקה ריקה כשהוא ב-worktree
# ‏(‏נתפס ע"י grok ‏בריצה 20 — ‏הפגם היה בגרסה הראשונה של הסקריפט).
TREE="${WORKTREE:-$REPO}"
DIR="${AGENT_DISPATCH_DIR:-/tmp/agent-dispatch}"
DONE="$DIR/$NAME.done"
LOG="$DIR/$NAME.log"
START=$(date +%s)

artifact_report() {
  local n dirty
  n="$(git -C "$REPO" rev-list --count "$BASE..$BRANCH" 2>/dev/null || echo ERR)"
  dirty="$(git -C "$TREE" status --short 2>/dev/null | head -20)"
  echo "commits: $n (‏מצופה $EXPECT) · ‏עץ שנבדק: $TREE"
  git -C "$REPO" log --oneline "$BASE..$BRANCH" 2>/dev/null | head -10
  if [ -n "$dirty" ]; then echo "tree: ‏מלוכלך"; echo "$dirty"; else echo "tree: ‏נקי"; fi
  [ "$n" = "$EXPECT" ] && [ -z "$dirty" ]
}

while :; do
  if [ -f "$DONE" ]; then
    rc="$(cat "$DONE" 2>/dev/null || echo '?')"
    echo "‏סנטינל ירה · acpx exit=$rc  ← ‏אות-חיוּת בלבד"
    tail -c 400 "$LOG" 2>/dev/null | grep -iE "error|retriable" | tail -2 && echo "⚠️ ‏שגיאה בזנב הלוג"
    echo "── ‏הכרעת-סיום לפי ארטיפקט ──"
    if artifact_report; then echo "‏✅ ‏הושלם ואומת"; exit 0
    else echo "‏🔴 ‏חלקי — ‏אל תשגר מאמת. ‏ר' OPEN-GAPS ‏פער 2"; exit 3; fi
  fi
  if [ $(( $(date +%s) - START )) -ge "$TIMEOUT" ]; then
    echo "‏⏳ ‏עדיין רץ אחרי ${TIMEOUT}s — ‏קרא שוב (‏זה אינו כישלון)"
    artifact_report >/dev/null; echo "‏מצב-ביניים: $(git -C "$REPO" rev-list --count "$BASE..$BRANCH" 2>/dev/null) ‏קומיטים"
    exit 2
  fi
  sleep 15
done
