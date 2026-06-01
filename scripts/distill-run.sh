#!/usr/bin/env bash
# scripts/distill-run.sh — wrapper שהטיימר מפעיל
# מריץ את הזיקוק הכמותי, ואם יש מספיק דוחות חדשים — מפעיל מרדכי-אוטומטי.
# התוצר ממתין ב-branch ייעודי. merge תמיד אנושי.
set -euo pipefail

BDS="$HOME/projects/brief-driven-slices/main"
OPENCODE_BIN="$HOME/.opencode/bin/opencode"   # לא ב-PATH ב-timer (memory gotcha)

cd "$BDS"

# 1. טריגר כמותי: יש מספיק דוחות חדשים?
if ! python3 scripts/distill.py --check-only --threshold "${BDS_DISTILL_THRESHOLD:-10}"; then
  echo "distill: פחות מהסף — יציאה בשקט"
  exit 0
fi

# 2. הרץ את החלק הכמותי → data.json
DATE=$(date +%Y-%m-%d)
python3 scripts/distill.py --out "distillations/$DATE-data.json"

# 3. צור branch ייעודי (לא main!) דרך worktree
WT="$HOME/projects/brief-driven-slices/.worktrees/bds-distill-$DATE"
git worktree add "$WT" -b "bds-distill-$DATE" main 2>/dev/null || true

# 4. הפעל מרדכי-אוטומטי על ה-data, בתוך ה-worktree, עם פרומפט שאוסר merge
env -u OPENCODE_SESSION -u OPENCODE_AGENT "$OPENCODE_BIN" run \
    --agent mordechai --cwd "$WT" < scripts/distill-prompt.txt

# 5. אל תמזג. התוצר ממתין ל-branch.
echo "distill: תוצר ב-branch bds-distill-$DATE — ממתין למרג' אנושי"
