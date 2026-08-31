#!/usr/bin/env python3
"""render-run-ledger — הפנקס נגזר מדוחות-הריצה, לא נכתב ביד.

סוגר את פערים 0+4 ב-autonomous-runs/OPEN-GAPS.md: הפנקס הידני צבר שורה
כפולה (ריצה 23, ספירות סותרות), ריצה חסרה (18), ושלוש כפילויות-מספור.
מקור-האמת היחיד הוא ה-frontmatter של runs/<date>-<name>.md — אותו עיקרון
שכבר הופעל על BACKLOG.md של drive-coding (סטטוס נגזר, לא נכתב).

שימוש:
    render-run-ledger.py [--runs-dir DIR] [--check]

  ברירת-מחדל: מדפיס את טבלת-הפנקס הנגזרת (markdown) ל-stdout, אזהרות ל-stderr.
  --check: קוד-יציאה 1 אם יש דוח בלי frontmatter, כפל-מספר, או שדה-חובה חסר.

שדות frontmatter (חובה אלא אם צוין):
  run (מספר, או null עם counted: false) · date · project ·
  interventions_product · interventions_plumbing · handoff_failures ·
  permanent_fixes (רשות) · verdict (רשות) · slices (רשות) ·
  new_territory (רשות — עמודת "שטח חדש?": אפס-על-שטח-מוכר הוא אינדיקציה חלשה)
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED = ["date", "project", "interventions_product", "interventions_plumbing", "handoff_failures"]
DEFAULT_DIR = Path(__file__).resolve().parent.parent / "autonomous-runs" / "runs"


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm: dict = {}
    for line in text[3:end].splitlines():
        line = line.split("  #", 1)[0].rstrip()  # הערת-שוליים בשורת ערך
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip().strip('"')
        if v.startswith("[") and v.endswith("]"):
            fm[k] = [s.strip() for s in v[1:-1].split(",") if s.strip()]
        elif v in ("true", "false"):
            fm[k] = v == "true"
        elif v == "null":
            fm[k] = None
        else:
            fm[k] = v
    return fm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", type=Path, default=DEFAULT_DIR)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows, warnings = [], []
    for f in sorted(args.runs_dir.glob("*.md")):
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None:
            warnings.append(f"⚠️  {f.name}: אין frontmatter — הריצה אינה נספרת (זה פער 0!)")
            continue
        if "verifier" in fm or ("run" not in fm and "round" in fm):
            continue  # דוח-משנה של מאמת (אביגיל/כלב), לא דוח-ריצה
        if "run" not in fm:
            warnings.append(f"⚠️  {f.name}: frontmatter בלי run: — הוסף run: <n> או run: null + counted: false")
            continue
        missing = [k for k in REQUIRED if k not in fm]
        if missing:
            warnings.append(f"⚠️  {f.name}: שדות-חובה חסרים: {', '.join(missing)}")
        fm["_file"] = f.name
        rows.append(fm)

    # כפל-מספרים — בדיוק מה שקרה לריצות 2/6/7/23 בפנקס הידני
    by_num: dict[str, list[str]] = {}
    for r in rows:
        if r.get("run") is not None:
            by_num.setdefault(str(r["run"]), []).append(r["_file"])
    def natkey(v) -> tuple:
        # ‏מספור קנוני הוא מספר, ‏אבל ההיסטוריה מכילה גם 9b/23b/23c — ‏סידור טבעי
        m = re.match(r"^(\d+)([a-z]*)$", str(v))
        return (int(m.group(1)), m.group(2)) if m else (10**6, str(v))

    for num, files in sorted(by_num.items(), key=lambda kv: natkey(kv[0])):
        if len(files) > 1:
            warnings.append(f"🔴 ריצה {num} מופיעה ב-{len(files)} דוחות: {', '.join(files)}")

    rows.sort(key=lambda r: (str(r.get("date", "")), natkey(r["run"]) if r.get("run") is not None else (10**6, "")))

    def cell(r, k, dash="—"):
        v = r.get(k, dash)
        return dash if v is None or v == "" else v

    print("| # | תאריך | ריצה | התערבויות: מוצר / צנרת | כשלי-מסירה | תיקונים קבועים | שטח חדש? |")
    print("|---|---|---|---|---|---|---|")
    streak = 0
    streak_alive = True
    for r in reversed(rows):  # הרצף נספר מהסוף אחורה
        if r.get("counted") is False:
            continue
        if streak_alive and str(cell(r, "interventions_plumbing")) == "0" and str(cell(r, "handoff_failures")) == "0":
            streak += 1
        else:
            streak_alive = False
    for r in rows:
        num = "—" if r.get("run") is None else r["run"]
        name = r["_file"].removesuffix(".md")
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
        desc = f"`{name}` ({cell(r, 'project')})"
        if r.get("counted") is False:
            desc += " — ⏹ אינה נספרת"
        v = r.get("verdict")
        if v:
            desc += f" · {v}"
        terr = {True: "🆕", False: "מוכר"}.get(r.get("new_territory"), "—")
        print(f"| {num} | {cell(r, 'date')} | {desc} | {cell(r, 'interventions_product')} / "
              f"{cell(r, 'interventions_plumbing')} | {cell(r, 'handoff_failures')} | "
              f"{cell(r, 'permanent_fixes')} | {terr} |")

    print()
    print(f"> נגזר מ-{len(rows)} דוחות ב-`runs/` ע\"י `scripts/render-run-ledger.py` — אין לערוך ביד.")
    print(f"> **רצף תנאי-היציאה** (0 צנרת + 0 כשלי-מסירה, מהסוף): **{streak}** / 2 נדרשות.")

    for w in warnings:
        print(w, file=sys.stderr)
    if args.check and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
