#!/usr/bin/env bash
# bds-init — הכנסת פרויקט לשיטה (החוב שנספר בריצות 4–8, חמש פעמים).
#
# הרקע (דוח-ריצה 4): "הפרויקט לא הוכנס לשיטה, רק הורץ בה" — שלוש
# התערבויות-צנרת מאותו שורש: אין plans/missions, אין roadmap, ו-BDS_REPORTS
# לא בסביבה. החצי הסביבתי נסגר ב-~/.zshenv (source ל-paths.env); זה החצי
# הפר-פרויקטי.
#
# שימוש: scripts/bds-init.sh <project-root>
set -euo pipefail

PROJ="${1:?שימוש: bds-init.sh <project-root>}"
[ -d "$PROJ" ] || { echo "לא תיקייה: $PROJ" >&2; exit 1; }
NAME="$(basename "$PROJ")"

mkdir -p "$PROJ/docs-for-llm/plans/missions"
mkdir -p "$PROJ/docs-for-llm/bugs/archive"

[ -f "$PROJ/docs-for-llm/roadmap.md" ] || cat > "$PROJ/docs-for-llm/roadmap.md" <<EOF
# Roadmap — $NAME

> פריטים עתידיים (💭). באגים → bugs/ · עבודה פתוחה מנוהלת → BACKLOG.
EOF

# תבנית-באג — מועתקת מריפו-השיטה אם קיימת שם
TPL="$(dirname "$0")/../docs/bugs/_TEMPLATE.md"
[ -f "$PROJ/docs-for-llm/bugs/_TEMPLATE.md" ] || { [ -f "$TPL" ] && cp "$TPL" "$PROJ/docs-for-llm/bugs/_TEMPLATE.md"; }

# אימות סביבה
if [ -z "${BDS_REPORTS:-}" ]; then
  echo "⚠️  BDS_REPORTS אינו בסביבה. ודא ש-~/.zshenv עושה source ל-~/.config/bds/paths.env" >&2
else
  mkdir -p "$BDS_REPORTS/$NAME"
  echo "✓ מאגר-דוחות: $BDS_REPORTS/$NAME"
fi

echo "✓ $NAME הוכנס לשיטה: docs-for-llm/{plans/missions,bugs,roadmap.md}"
