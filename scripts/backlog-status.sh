#!/usr/bin/env bash
# ‏מריץ את פקודת-הסגירה של כל שורה ב-BACKLOG.md ‏ומדפיס מצב נגזר.
# ‏המקור היחיד לפקודות הוא BACKLOG.md — ‏הסקריפט אינו מחזיק עותק שלהן.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
DOC="${1:-BACKLOG.md}"
[[ -f $DOC ]] || { echo "‏אין $DOC" >&2; exit 2; }

SEP=$'\x01'   # ‏מציין זמני ל-\| ‏שאינו מפריד-עמודות
open=0; closed=0; bad=0; rows=()

while IFS= read -r line; do
  [[ $line == \|* ]] || continue
  esc="${line//\\|/$SEP}"                    # ‏נטרל pipes ‏עם escape
  IFS='|' read -r _ num item _src check expect _ <<<"$esc"
  num="${num//[[:space:]]/}"
  [[ $num =~ ^[0-9]+$ ]] || continue
  item="$(echo "${item//$SEP/|}" | sed 's/^ *//; s/ *$//')"
  check="$(echo "${check//$SEP/|}" | sed 's/^ *`//; s/` *$//')"
  expect="$(echo "$expect" | sed 's/^ *`//; s/` *$//')"

  state=bad
  if [[ $expect == file ]]; then
    eval "$check" >/dev/null 2>&1 && state=closed || state=open
  else
    out="$(eval "$check" 2>/dev/null | tr -d '[:space:]')"
    if [[ $out =~ ^[0-9]+$ ]]; then
      case "$expect" in
        ">0") (( out > 0 )) && state=closed || state=open ;;
        "=0") (( out == 0 )) && state=closed || state=open ;;
        "="*) (( out == ${expect#=} )) && state=closed || state=open ;;
      esac
    fi
  fi

  case $state in
    closed) ((closed++)); rows+=("✅ $num  $item") ;;
    open)   ((open++));   rows+=("⬜ $num  $item") ;;
    *)      ((bad++));    rows+=("⚠️  $num  $item   ← ‏הבדיקה לא הכריעה: $check") ;;
  esac
done < "$DOC"

printf '%s\n' "${rows[@]}"
echo "──────────────────────────────────────────────"
printf '‏פתוחים: %d · ‏סגורים: %d · ‏שבורות: %d\n' "$open" "$closed" "$bad"
(( bad > 0 )) && echo "⚠️  ‏שורה שאי אפשר להכריע אינה פריט — ‏תקן את הפקודה ב-$DOC." >&2
exit 0
