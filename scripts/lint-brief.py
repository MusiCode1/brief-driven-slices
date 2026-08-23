#!/usr/bin/env python3
"""lint-brief — אכיפה מכנית של כללי-הבריף שהנחיה טקסטואלית לא אכפה.

הרקע: `wrong-line-number` היא קטגוריית-הממצאים הגדולה ביותר (79→162 בין
שני זיקוקים), למרות שהכלל "עוגן בתבנית, לא בשורה" תועד בשלושה מקומות.
זיקוק 2026-08-03: "הכלל הוא הנחיה טקסטואלית שאיש לא אוכף" — פריט 34.

שימוש:  scripts/lint-brief.py <brief.md>
יציאה:  0 נקי · 1 יש ממצאי 🔴 (מספרי-שורות)

מה נבדק:
  🔴 הפניות `file.ext:NN` — עוגן שמתיישן ברגע שה-base זז. לעגן בסמל/תבנית.
  🟡 ספירות-יד ("בדיוק N מופעים", "N טסטים") — נדיפות באותה מידה.
  🟡 אורך המסמך — בריף >300 שורות "הפך לתוכנית" (case-study slice-5:
     תוכנית שנכתבת בלי מהדר צוברת באגים בקצב של קוד).
"""

import re
import sys
from pathlib import Path

LINE_REF = re.compile(r"`?[\w./-]+\.(ts|js|svelte|py|sh|rs|go|css|html|json)`?:\d+")
HAND_COUNT = re.compile(
    r"(בדיוק\s+\d+\s+(מופעים|אתרים|קריאות|שדות|קבצים))|(\d{3,}\s+(טסטים|passed))"
)
MAX_LINES = 300


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    red, yellow = [], []
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:  # פקודות להרצה רשאיות לציין שורות (sed -n וכו')
            continue
        for m in LINE_REF.finditer(line):
            red.append((i, m.group(0)))
        for m in HAND_COUNT.finditer(line):
            yellow.append((i, m.group(0)))

    for i, frag in red:
        print(f"🔴 {path.name}:{i}  הפניית מספר-שורה: {frag}  → עגן בסמל/תבנית ברת-grep")
    for i, frag in yellow:
        print(f"🟡 {path.name}:{i}  ספירת-יד נדיפה: {frag!r}  → גזור בפקודה, אל תקבע במסמך")
    if len(lines) > MAX_LINES:
        print(f"🟡 {path.name}: {len(lines)} שורות (> {MAX_LINES}) — הבריף הופך לתוכנית; "
              f"העבר ידע לחפצים ברי-הרצה (טסט אדום, probe, סקריפט-שער)")

    print(f"\nסיכום: 🔴 {len(red)} · 🟡 {len(yellow) + (1 if len(lines) > MAX_LINES else 0)}")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
