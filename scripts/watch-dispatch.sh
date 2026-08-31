#!/usr/bin/env bash
# watch-dispatch — ‏הצופה הקנוני. ‏מחזיק את ההמתנה לשיגור עד הכרעה, ‏ומעיר את
# ‏המשגר בערוץ שהוא באמת מקשיב לו.
#
# ‏נולד מפער 9 ‏ב-autonomous-runs/OPEN-GAPS.md: ‏שלוש ריצות רצופות (27–29) ‏שילמו
# ‏התערבות-צנרת על צופה שנכתב JIT — ‏אחד שלח tg ‏במקום notify, ‏אחד נפל אחרי
# WATCH_START, ‏אחד תיקתק "‏חי" ‏בלי לבדוק עבודה. ‏הלקחים מגולמים כאן, ‏פעם אחת:
#
#   1. ‏הכרעה לפי **‏ארטיפקט** — ‏await-dispatch.sh ‏הוא השופט (‏קומיטים + ‏עץ),
#      ‏לא קוד-יציאה של תהליך ולא "‏הטרנסקריפט זז".
#   2. ‏הערת-המשגר היא **‏אך ורק** `dispatch-via-api notify` — ‏לוג/טלגרם אינם
#      ‏מעירים סוכן (‏ריצה 27).
#   3. ‏גלאי-קיפאון: ‏אם שום ארטיפקט לא זז STALL ‏שניות — ‏מעירים עם אזהרה
#      (‏פעם אחת), ‏לא ממשיכים לתקתק בשקט (‏ריצה 14: ‏כלב מת 15 ‏דק' ‏בלי שאיש שם לב).
#   4. ‏הצופה עצמו הוא bash ‏חסר-מודל ⇒ ‏אין לו זרם-ספק שיכול להישמט (‏פער 6).
#
# ‏שימוש (‏אותם ארגומנטים של await-dispatch + ‏שלושה משלו):
#   watch-dispatch <name> --repo P --branch B --base R --expect-commits N \
#       [--worktree W] [--notify-agent <agentId>] [--notify-base <url>] \
#       [--stall <sec>=900] [--interval <sec>=60]
#
# ‏קודי-יציאה: ‏כשל ההכרעה הסופית של await-dispatch — 0 ‏הושלם ואומת · 3 ‏חלקי.
#   (2 ‏אינו קוד-יציאה של הצופה — ‏הוא בדיוק מה שהצופה בולע ולולא.)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NAME="${1:?usage: watch-dispatch <name> --repo P --branch B --base R --expect-commits N [...]}"; shift
NOTIFY="" NBASE="http://127.0.0.1:4050" STALL=900 INTERVAL=60
PASS=()   # ‏מועבר ל-await-dispatch ‏כמות-שהוא
REPO="" BRANCH="" BASE_REF=""
while [ $# -gt 0 ]; do
  case "$1" in
    --notify-agent) NOTIFY="$2"; shift 2 ;;
    --notify-base)  NBASE="$2";  shift 2 ;;
    --stall)        STALL="$2";  shift 2 ;;
    --interval)     INTERVAL="$2"; shift 2 ;;
    --repo)   REPO="$2";     PASS+=("$1" "$2"); shift 2 ;;
    --branch) BRANCH="$2";   PASS+=("$1" "$2"); shift 2 ;;
    --base)   BASE_REF="$2"; PASS+=("$1" "$2"); shift 2 ;;
    *) PASS+=("$1"); [ $# -gt 1 ] && { PASS+=("$2"); shift; }; shift ;;
  esac
done

notify() {  # ‏הערוץ היחיד שמעיר סוכן. ‏בלי --notify-agent — ‏הדפסה בלבד (‏ריצה ידנית).
  local msg="$1"
  echo "── notify ──"; echo "$msg"
  [ -n "$NOTIFY" ] || return 0
  node "$HERE/dispatch-via-api.mjs" notify --base "$NBASE" --agent "$NOTIFY" \
    --text "$msg" \
    || echo "⚠️ watch-dispatch: notify ‏נכשל — ‏המשגר לא הוער. ‏בדוק ש-$NBASE ‏חי ושה-agent ‏קיים." >&2
}

# ‏חתימת-התקדמות: tip ‏של הענף + ‏מצב-העץ + ‏גודל לוג-השיגור. ‏אם היא לא זזה — ‏קיפאון.
progress_sig() {
  local tip dirty logsz
  tip="$(git -C "$REPO" rev-parse "$BRANCH" 2>/dev/null || echo none)"
  dirty="$(git -C "${TREE:-$REPO}" status --short 2>/dev/null | md5sum | cut -d' ' -f1)"
  logsz="$(stat -c %s "${AGENT_DISPATCH_DIR:-/tmp/agent-dispatch}/$NAME.log" 2>/dev/null || echo 0)"
  echo "$tip:$dirty:$logsz"
}

LAST_SIG="$(progress_sig)"; LAST_MOVE=$(date +%s); STALL_SENT=0
echo "WATCH_START $NAME · interval=${INTERVAL}s · stall=${STALL}s · notify=${NOTIFY:-stdout}"

while :; do
  OUT="$("$HERE/await-dispatch.sh" "$NAME" "${PASS[@]}" --timeout "$INTERVAL" 2>&1)"; RC=$?
  case $RC in
    0|3)
      VERDICT="✅ ‏הושלם ואומת"; [ $RC -eq 3 ] && VERDICT="🔴 ‏חלקי — ‏אל תשגר מאמת"
      notify "watch-dispatch [$NAME] ‏הכרעה: $VERDICT (exit=$RC)
$OUT"
      exit $RC ;;
    2)  # ‏עדיין רץ — ‏זה המצב הרגיל. ‏בדוק קיפאון לפני הסיבוב הבא.
      SIG="$(progress_sig)"
      if [ "$SIG" != "$LAST_SIG" ]; then
        LAST_SIG="$SIG"; LAST_MOVE=$(date +%s); STALL_SENT=0
      elif [ $(( $(date +%s) - LAST_MOVE )) -ge "$STALL" ] && [ "$STALL_SENT" -eq 0 ]; then
        STALL_SENT=1   # ‏מעירים פעם אחת; ‏ממשיכים לצפות — ‏ההכרעה נשארת אצל המשגר.
        notify "watch-dispatch [$NAME] ⚠️ ‏חשד-קיפאון: ‏שום ארטיפקט לא זז ${STALL}s (‏ענף/עץ/לוג). ‏הסוכן אולי מת או תקוע — ‏בדוק אותו. ‏הצופה ממשיך."
      fi ;;
    *)
      notify "watch-dispatch [$NAME] 🔴 await-dispatch ‏נפל (exit=$RC) — ‏הצופה עוצר. ‏פלט:
$OUT"
      exit $RC ;;
  esac
done
