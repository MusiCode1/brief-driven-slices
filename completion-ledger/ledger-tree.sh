#!/usr/bin/env bash
# ‏הולך על עץ-הפנקסים דרך שורות ה-🔗 ‏ומדפיס את **‏כל** ‏המשימות במבט אחד.
#
# ‏מריץ שלוש בדיקות שאי-אפשר לעשות מתוך פנקס בודד (`FIELD-CONTRACT` §10):
#   1. ‏מבחן-החוקיות — ‏היעד בנוי על אותה תבנית
#   2. ‏מעגלים
#   3. ‏אב כפול — ‏אותו פנקס מופנה משניים ⇒ ‏ספירה כפולה
set -uo pipefail
export DC="${DC:-$HOME/Projects/drive-coding/edge}"
ROOT_DOC="${1:?שימוש: ledger-tree.sh <נתיב-פנקס>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

declare -A VISITED=()            # ‏נתיב-מוחלט → ‏מי הפנה אליו
T_OPEN=0; T_CLOSED=0; T_LEDGERS=0; UNMIGRATED=0

legal() {                        # ‏§10 — ‏מבחן-החוקיות
  head -20 "$1" | grep -q '^type: completion-ledger' &&
  head -20 "$1" | grep -q '^method: .*FIELD-CONTRACT'
}

walk() {
  local doc="$1" depth="$2" parent="$3"
  local abs; abs="$(cd "$(dirname "$doc")" && pwd)/$(basename "$doc")"
  local pad=""; (( depth )) && pad="$(printf '%*s' $((depth*2)) '')└─ "

  if [[ -n ${VISITED[$abs]-} ]]; then
    printf '%s🛑 %s — ‏כבר הופנה מ-%s ⇒ ‏מעגל או אב כפול\n' "$pad" "$(basename "$doc")" "${VISITED[$abs]}"
    return
  fi
  VISITED[$abs]="${parent:-שורש}"

  if [[ ! -f $doc ]]; then printf '%s🛑 ‏חסר: %s\n' "$pad" "$doc"; return; fi
  if (( depth )) && ! legal "$doc"; then
    printf '%s🛑 %s — ‏**‏נכשל במבחן-החוקיות** (§10): ‏אינו נושא `type: completion-ledger` + `method:`\n' "$pad" "$(basename "$doc")"
    printf '%s   ⇒ ‏אינו הפניה אלא קישור. ‏העבודה שבו **‏אינה נספרת בשום מקום**.\n' "$pad"
    return
  fi

  local out o c r rc
  out="$("$HERE/ledger-status.sh" "$doc" 2>/dev/null | tail -2 | head -1)"; rc=$?
  if (( rc == 3 )); then      # ‏פנקס לא-מוסב — ‏לא נמדד, ‏ולכן **‏אינו נכנס לסכום**
    printf '%s%-46s 🛑 ‏לא-מוסב ל-§11 — ‏**‏לא נמדד** (‏אינו נספר בעץ)\n' "$pad" "$(basename "${doc%-DEFINITION-OF-DONE.md}" .md)"
    UNMIGRATED=$((UNMIGRATED+1)); return
  fi
  o=$(grep -oP '(?<=‏פתוחים: )[0-9]+' <<<"$out"); c=$(grep -oP '(?<=‏סגורים: )[0-9]+' <<<"$out")
  r=$(grep -oP '(?<=‏הפניות: )[0-9]+' <<<"$out")
  o=${o:-0}; c=${c:-0}; r=${r:-0}
  (( T_OPEN += o )); (( T_CLOSED += c )); (( T_LEDGERS++ ))
  printf '%s%-46s %3d ‏פתוחות · %3d ✅%s\n' "$pad" "$(basename "${doc%-DEFINITION-OF-DONE.md}" .md)" "$o" "$c" \
    "$( (( r )) && printf ' · %d 🔗' "$r" )"

  # ‏ירידה לכל 🔗 — ‏הנתיב יחסי לתיקיית הפנקס המפנה
  local base; base="$(dirname "$doc")"
  while IFS= read -r child; do
    [[ -n $child ]] || continue
    walk "$base/$child" $((depth+1)) "$(basename "$doc")"
  done < <(grep -oP '^\s*🔗\s+`\K[^`]+' "$doc" 2>/dev/null)
}

walk "$ROOT_DOC" 0 ""
echo "─────────────────────────────────────────────"
printf '‏סך-הכול בעץ: ‏%d ‏פנקסים · ‏%d ‏פתוחות · ‏%d ✅\n' "$T_LEDGERS" "$T_OPEN" "$T_CLOSED"
(( UNMIGRATED )) && echo "🛑 ‏$UNMIGRATED ‏פנקסים **‏לא נמדדו** (‏לא-מוסבים ל-§11) ‏ואינם בסכום. ‏הסכום הזה **‏חלקי**." >&2
echo "‏🔑 ‏זהו המספר ה**‏נגזר**. ‏הכותרת של כל פנקס נשארת התיבות שלו בלבד (§10)."
exit 0
