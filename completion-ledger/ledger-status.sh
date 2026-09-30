#!/usr/bin/env bash
# ‏מריץ את שורת ה-⟂ ‏של כל תיבה בפנקס ‏ומדפיס מצב נגזר.
# ‏המקור היחיד לפקודות הוא הפנקס — ‏הסקריפט אינו מחזיק עותק שלהן.
#
# ‏🛑 ‏שני מצבים בלבד: ‏סגור / ‏פתוח (`FIELD-CONTRACT` §11).
#    ‏⚠️ ‏ו-🟡 ‏הן **‏הערות על שורה פתוחה**, ‏לא מצב שלישי.
set -uo pipefail
export DC="${DC:-$HOME/Projects/drive-coding/edge}"
DOC="${1:-DEFINITION-OF-DONE.md}"
[[ -f $DOC ]] || { echo "‏אין $DOC" >&2; exit 2; }

open=0; closed=0; broken=0; suspect=0; refs=0; probes=0; raw=0
RLM=$'\u200f'; LRM=$'\u200e'      # ‏סימני-כיווניות נפוצים בפנקס עברי
rows=(); seen=(); dups=()
id=""; title=""

flush() {                       # ‏תיבה בלי ⟂ ‏היא תיבה שאי-אפשר להכריע
  [[ -n $id ]] || return
  ((open++)); ((broken++))
  rows+=("⬜ $id  $title   ← ⚠️ ‏אין שורת ⟂ — ‏אי-אפשר להכריע")
  id=""
}

# ─── סמני-אימות: תיבה שנבדקה ידנית ונמצאה פתוחה באמת מפסיקה להיות 🟡 ───
#     בלעדיהם `G4` (‏פרוב-חשוד = 0) אינו יכול להוריק לעולם: ההיוריסטיקה
#     יורה על **קיום דוח-כלב**, ואין שדה שאומר "בדקתי, והוא באמת פתוח".
#     הסמן הוא **ראיה מתוארכת**, לא שדה-סטטוס — ולכן אינו רוקב.
VERIFIED="$(grep -oP 'פרוב אומת[^—]*— *\K[A-Za-z]+[0-9]+' "$DOC" 2>/dev/null | tr '\n' ' ')"

fence=0
while IFS= read -r line; do
  # ─── גדר-קוד: המקרא בראש הפנקס מכיל שורת-תיבה לדוגמה, ואסור לספור אותה ───
  [[ $line =~ ^[[:space:]]*\`\`\` ]] && { fence=$((1-fence)); continue; }
  (( fence )) && continue
  line="${line//$RLM/}"; line="${line//$LRM/}"      # ‏בלי זה `**‏A1**` ‏אינו מתאים
  [[ $line =~ ^-\ \[[\ x]\] ]] && ((raw++))
  # ─── שורת-תיבה ────────────────────────────────────────────────────────────
  if [[ $line =~ ^-\ \[[\ x]\]\ \*\*([A-Za-z]+[0-9]+[a-z]?)\*\*\ ·\ (.*)$ ]]; then
    flush
    id="${BASH_REMATCH[1]}"; title="${BASH_REMATCH[2]}"
    [[ " ${seen[*]-} " == *" $id "* ]] && dups+=("$id")
    seen+=("$id")
    continue
  fi
  # ─── הפניה: אינה תיבה, אינה נספרת (§10) ──────────────────────────────────
  if [[ $line =~ ^[[:space:]]*🔗[[:space:]]+\`([^\`]+)\` ]]; then
    ((refs++)); rows+=("🔗 $id  $title   ← ‏הפניה: ${BASH_REMATCH[1]} (‏אינה נספרת)")
    id=""; continue
  fi
  # ─── שורת-פרוב ────────────────────────────────────────────────────────────
  [[ $line =~ ^[[:space:]]*⟂[[:space:]]+\`(.*)\`[[:space:]]*→[[:space:]]*\`(.*)\` ]] || continue
  check="${BASH_REMATCH[1]}"; expect="${BASH_REMATCH[2]}"; ((probes++))
  [[ -n $id ]] || continue

  note=""; state=open
  out="$(eval "$check" 2>/dev/null | tr -d '[:space:]')"
  if [[ $out =~ ^[0-9]+$ ]]; then
    case "$expect" in
      ">0")  (( out > 0 ))  && state=closed ;;
      "=0")  (( out == 0 )) && state=closed ;;
      "="*)  (( out == ${expect#=} )) && state=closed ;;
      *)     note="⚠️ ‏`expect` ‏אינו \`>0\`/\`=0\`/\`=N\`: $expect"; ((broken++)) ;;
    esac
  else
    # ‏פלט שאינו מספר חשוף — ‏הסיבה השכיחה: ‏`rg -n` ‏במקום `rg -c`
    note="⚠️ ‏הפלט אינו מספר: $check"; ((broken++))
  fi

  # ‏פרוב-חשוד: ‏"‏פתוח" ‏אך קיים דוח-כלב לאותו slug
  if [[ $state == open && -z $note && " $VERIFIED " != *" $id "* ]]; then
    slug="$(grep -oP '(?<=\x60)[a-z0-9][a-z0-9-]+(?=\x60)' <<<"$title" | head -1)"
    if [[ -n ${slug:-} ]] && ls "${BDS_REPORTS:-$HOME/Projects/brief-driven-slices/main/reports}/${BDS_PROJECT:-drive-coding}/${slug}"*-calev*.md >/dev/null 2>&1; then
      note="🟡 ‏יש דוח-כלב (\`$slug\`) ‏והפרוב מחזיר פתוח — ‏בדוק שהוא מצביע נכון"; ((suspect++))
    fi
  fi

  if [[ $state == closed ]]; then ((closed++)); rows+=("✅ $id  $title")
  else ((open++)); rows+=("⬜ $id  $title${note:+   ← $note}"); fi
  id=""
done < "$DOC"
flush

# ─── 🛑 אפס-שקט: פנקס עם תיבות ובלי אף ⟂ הוא פנקס שלא הוסב, לא פנקס ריק ───
if (( raw > 0 && probes == 0 )); then
  echo "🛑 ‏פנקס לא-מוסב ל-\`FIELD-CONTRACT\` §11: ‏$raw ‏שורות-תיבה, ‏**‏0 ‏שורות ⟂**." >&2
  echo "   ‏המספרים שבו כתובים-ביד ואינם נגזרים. ‏\"‏לא נמדד\" ‏אינו \"‏0\"." >&2
  exit 3
fi

printf '%s\n' "${rows[@]}"
echo "──────────────────────────────────────────────"
printf '‏פתוחים: %d · ‏סגורים: %d · ‏הפניות: %d\n' "$open" "$closed" "$refs"
printf '‏הערות על שורות פתוחות — ‏פרוב שבור: %d · ‏פרוב חשוד: %d\n' "$broken" "$suspect"
(( ${#dups[@]} )) && printf '🛑 ‏מזהים כפולים: %s\n' "${dups[*]}" >&2
(( broken > 0 )) && echo "⚠️  ‏שורה שאי אפשר להכריע אינה פריט — ‏תקן את ה-⟂ ‏ב-$DOC." >&2
exit 0
