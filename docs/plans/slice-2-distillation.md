# Slice 2 — Distillation layer (זיקוק) — תוכנית

> **תאריך**: 2026-05-30
> **סטטוס**: טיוטה (טרם אומת ע"י אביגיל)
> **Complexity**: 7/10 (verifier: light + verifier-phase על Commit 0 ו-Commit 4)
> **תלויות (`depends_on`)**: [] — additive על main. בנוי מעל התשתית של slice-bds-extraction-and-reporting (שכבר merged): הדוחות המתויגים ב-`reports/<project>/<slice>-<verifier>.json`.
> **Base**: main tip `df93edb`

---

## §0 — Pre-flight

> זה slice של **השיטה עצמה** (brief-driven-slices). "ריפו הפרויקט" = ריפו השיטה (אותו מקום). אין BE/FE/tunnel/browser — זה כלי CLI (python3 + bash + systemd) + תיעוד. ה-boilerplate הכללי ב-`briefs/EXECUTOR_DISPATCH.md`. מה שספציפי ל-slice הזה למטה.

### תלויות (חובה!)

slice זה **מבוסס על**:
- slice-bds-extraction-and-reporting (status: **merged**, tip `df93edb`) — הוא זה שהקים את `reports/<project>/<slice>-<verifier>.json` (דוחות מתויגים severity+category) ואת ה-README של reports עם הטקסונומיה. **כל הזיקוק קורא מהמבנה הזה.**
- _אין תלות ב-branch לא-merged. additive בלבד._

> אביגיל: בדקי ש-`reports/README.md` קיים ושמבנה ה-JSON (severity/category/findings) תואם את מה שה-distill.py מצפה לקרוא. depends_on ריק כי הכל merged.

### Worktree

```bash
cd /home/user/projects/brief-driven-slices
git worktree add /home/user/projects/brief-driven-slices/.worktrees/slice-2-distillation -b slice-2-distillation main
cd .worktrees/slice-2-distillation
```

> **שים לב — מבנה bare**: ה-repo הוא bare+worktrees. ה-base הוא `main` (לא `dev` — אין dev ב-bds, ראה worktrees.md). השתמש ב-absolute path ל-worktree add.
> **אין `pnpm install`** — אין Node בפרויקט הזה. python3 stdlib בלבד + bash.

### איך להריץ

- **אין BE/FE.** הכלי הוא CLI.
- **הסקריפט**: `python3 scripts/distill.py --help` (מ-root ה-worktree).
- **Tests**: `python3 -m pytest tests/` — **אבל**: אין pytest מותקן בסביבה (אומת: ראה §6 risk). השתמש ב-`python3 tests/test_distill.py` עם unittest (stdlib) — ראה Commit 0.
- **systemd**: `systemctl --user` (timer setup, Commit 3). אל תפעיל בפועל ב-CI — רק הקבצים נכתבים ונבדקים syntactically.

### Browser / OneCLI agent

לא רלוונטי. אין UI, אין proxy.

### Reading list

**must-read** (לפני שמתחילים):
- `reports/README.md` — מבנה הדוחות והטקסונומיה (2 זרמים: avigail plan / calev runtime). **זה הקלט של distill.py.**
- `reports/bds/bds-extraction-calev.json` — דוגמת דוח אמיתי יחיד (השדות בפועל: project, slice, verifier, date, verdict, findings[], לפעמים mode/summary/dod_items). **שים לב: השדות לא אחידים לגמרי בין avigail ל-calev — distill.py חייב להיות סלחני.**
- `agents/avigail.md` (שורות 184-216) + `agents/calev.md` (שורות 275-308) — פורמט ה-JSON שכל מאמת כותב, וערכי severity/category הקנוניים.
- `patterns.md` — קטלוג טעויות-הביצוע הקיים (5 קטגוריות). זה הקטלוג שכלב מזין; הזיקוק מעדכן אותו.
- `worktrees.md` — מבנה bare+worktrees (רלוונטי לנספח A — init-project).

**reference** (בזמן עבודה):
- `scripts/discard_chain.py` — דוגמה לסגנון python stdlib בפרויקט (json, pathlib, sys, subprocess-wrapped). חקה את הסגנון.
- `agents/mordechai.md` (שורות 150-192) — איך decisions/walkthrough/reports נבדלים. הזיקוק קורא reports, לא decisions.

---

## §1 — מטרה

אחרי ה-slice הזה, יש למתודולוגיה **לולאת שיפור עצמית מודדת**. הדוחות המתויגים שאביגיל וכלב צוברים (severity + category) מזוקקים תקופתית לשלוש שכבות זיכרון: קטלוגים תמציתיים חיים (`plan-pitfalls.md` ל-תכנון, `patterns.md` ל-ביצוע) שמרדכי פותח לפני כל brief, דוחות-זיקוק כרונולוגיים שמודדים מגמות מול הקודם ("האם הכללים שהוספנו עבדו?"), ויומן-גלובלי נדיר של אבולוציית השיטה. הזיקוק רץ אוטומטית בלילה (טיימר → סקריפט כמותי → סשן מרדכי לפרשנות), מייצר תוצר ב-branch ייעודי, **וממתין למיזוג אנושי בבוקר** — בדיוק כמו slice רגיל.

---

## §2 — Scope

| פיצ'ר | כן/לא | לאן |
|------|------|------|
| `distill.py` — סקריפט כמותי דטרמיניסטי (ספירה, hitrate, דלתא, traceability) | ✅ | ה-slice הזה |
| פורמט דוח-זיקוק (`distillations/<date>-report.md`) + קובץ-data ביניים (`<date>-data.json`) | ✅ | ה-slice הזה |
| 2 קטלוגים: `plan-pitfalls.md` (חדש, avigail) + מבנה-עדכון ל-`patterns.md` (קיים, calev) | ✅ | ה-slice הזה |
| traceability דו-כיווני (קטלוג→דוחות, דוח-זיקוק→כללים) | ✅ | ה-slice הזה |
| מנגנון טקסונומיה-מתפתחת (זיהוי קטגוריות חדשות/`unique`, תיעוד שינוי כאירוע) | ✅ | ה-slice הזה |
| יומן-גלובלי נדיר של השיטה (`docs/methodology-evolution.md`) | ✅ | ה-slice הזה |
| מנגנון הרצה תקופתית: systemd user timer + הפעלת מרדכי-אוטומטי ל-branch ייעודי | ✅ | ה-slice הזה |
| **הרצת הזיקוק האמיתי הראשון** על חומר-גלם מצטבר | ❌ | אחרי שיצטברו ≥N דוחות אמיתיים (לא עכשיו — יש report אחד) |
| מיזוג branch הזיקוק ל-main | ❌ | תמיד אנושי (מרדכי, אחרי סקירה) — לא בקוד |
| `init-project.sh` (bootstrap פרויקט חדש) | ❌ | **slice נפרד — ראה נספח A** |

> זו הגנה מ-scope creep. במיוחד: **הסקריפט לא מפרש, לא מנסח כללים, לא ממציא טקסונומיה.** הוא סופר ומודד. הפרשנות היא עבודת מרדכי (המודל). זו החלוקה המרכזית של ה-slice.

---

## §3 — Architecture diagram

```
                  reports/<project>/<slice>-<verifier>.json   ← קיים (slice-1)
                  (severity + category, 2 זרמים: avigail/calev)
                          │
                          ▼ קורא הכל
        ┌─────────────────────────────────────────────┐
        │  scripts/distill.py   ← חדש (pure-ish, TDD)  │
        │  - count: severity × category, per-verifier  │
        │  - hitrate: briefs-with-findings / total     │
        │  - delta: מול ה-snapshot הקודם               │
        │  - traceability: category → [reports]        │
        │  - flag: categories לא-קנוניים (taxonomy)    │
        └────────────────┬────────────────────────────┘
                          │ כותב (כמותי בלבד)
                          ▼
        distillations/<date>-data.json   ← חדש (חצי-כמותי, קלט למרדכי)
                          │
                          ▼ קורא + מפרש (פרשנות מודל)
        ┌─────────────────────────────────────────────┐
        │  מרדכי-אוטומטי (opencode run --agent ...)     │
        │  כותב ל-branch bds-distill-<date>, לא ל-main  │
        └────────────────┬────────────────────────────┘
                          │ מייצר (איכותני)
          ┌───────────────┼───────────────┬──────────────────┐
          ▼               ▼               ▼                  ▼
  distillations/    plan-pitfalls.md  patterns.md     methodology-
  <date>-report.md  (חדש, avigail)   (קיים, calev)   evolution.md
  (snapshot,        ← קטלוג חי        ← קטלוג חי       (יומן גלובלי
   מבט-לאחור)        + traceability    + traceability   נדיר)
                          ▲
        ┌─────────────────┴───────────────────────────┐
        │  systemd --user timer (יומי)                 │ ← חדש (Commit 3)
        │  → distill.py; אם <N דוחות חדשים: יציאה-בשקט  │
        │  → אחרת: opencode run --agent mordechai      │
        │  → תוצר ב-branch, ממתין למרג' אנושי           │
        └─────────────────────────────────────────────┘
```

---

## §4 — Commits בסדר

### Commit 0 — `distill.py`: מנוע כמותי + tests (approach: tdd)

> זה הליבה הניתנת-לבדיקה. כל הספירה/מדידה/דלתא/traceability — pure על קלט קבצים, פלט JSON. **כל הלוגיקה הבדיקה של ה-slice כאן.** שאר ה-commits הם IO-wiring (פורמטים, systemd) שנבדקים manual/none.

**קבצים חדשים**:
- `scripts/distill.py`
- `tests/test_distill.py` — unittest (stdlib). **אין pytest בסביבה** (§6) — חובה `import unittest`, לא pytest.
- `tests/fixtures/reports/<project>/*.json` — קבצי דוח סינתטיים (≥2 projects, ≥2 verifiers, severity/category מגוונים) — חומר-גלם לבדיקה. **fixtures, לא הדוחות האמיתיים.**

**API skeleton** (החתימה המדויקת — executor אסור לשנות):

```python
from pathlib import Path
from typing import TypedDict

class Finding(TypedDict, total=False):
    id: int
    severity: str          # blocker|regression|confusion|type-error|outdated|minor
    category: str
    summary: str
    source_brief: str
    source_code: str
    cost_estimate: str

class Report(TypedDict, total=False):
    project: str
    slice: str
    verifier: str          # "avigail" | "calev"
    date: str
    verdict: str
    findings: list[Finding]

# ─── ספרה דטרמיניסטית: כל הפונקציות pure (קלט→פלט, אין side-effect) ───

def load_reports(reports_dir: Path) -> list[Report]:
    """קורא את כל reports/<project>/*.json. סלחני: קובץ לא-תקין → דלג + warn ל-stderr,
    לא קריסה. מתעלם מ-README.md/.gitkeep. מחזיר רשימה שטוחה."""

def count_by_severity_category(reports: list[Report], verifier: str) -> dict:
    """מסנן ל-verifier נתון, סופר findings.
    מחזיר: {"by_severity": {sev: n}, "by_category": {cat: n}, "total_findings": n,
            "total_reports": n}"""

def compute_hitrate(reports: list[Report], verifier: str) -> dict:
    """מחזיר: {"reports": n, "reports_with_findings": k, "avg_findings": float,
            "verdicts": {verdict: n}}. avg_findings מעוגל ל-2."""

def traceability_index(reports: list[Report], verifier: str) -> dict[str, list[str]]:
    """category → רשימת מזהי-דוח שתרמו אליה. מזהה-דוח = "<project>/<slice>".
    ממוין. כך קטלוג יכול להצביע חזרה למקור."""

CANONICAL_CATEGORIES = {
    "avigail": {"missing-symbol","dropped-branch","type-error","wrong-line-number",
                "naming-inconsistency","wrong-path","outdated-risk","missing-dependency"},
    "calev":   {"bubble-grouping","cross-store-null","spec-drift","regression",
                "mobile-desktop","reload-reconnect","library-compat"},
}

def flag_noncanonical(reports: list[Report], verifier: str) -> dict[str, list[str]]:
    """מחזיר categories שמופיעים בדוחות אבל לא ב-CANONICAL_CATEGORIES[verifier]
    (כולל "unique"). → {category: [report-ids]}. אלה מועמדים לזיקוק-טקסונומיה.
    'unique' תמיד מועמד (לא קנוני בכוונה)."""

def compute_delta(current: dict, previous_data: dict | None) -> dict:
    """משווה התפלגות נוכחית מול ה-data.json הקודם.
    previous_data=None (אין קודם) → כל הקטגוריות "new".
    מחזיר: {"by_category": {cat: {"now": n, "prev": m, "trend": "up|down|same|new|gone"}}}.
    trend לפי now מול prev: now>prev=up, <prev=down, ==same, prev חסר=new, now=0&prev>0=gone."""

def count_new_reports_since(reports_dir: Path, last_data: Path | None) -> int:
    """כמה דוחות חדשים מאז ה-snapshot האחרון (לפי last_data["report_ids"]).
    last_data=None → כל הדוחות חדשים. משמש את הטריגר הכמותי (§Commit 3)."""

def build_data(reports_dir: Path, prev_data_path: Path | None) -> dict:
    """מאחד הכל ל-data.json אחד. מבנה:
    {"date": ISO, "report_ids": [...],
     "avigail": {"counts":..., "hitrate":..., "trace":..., "noncanonical":..., "delta":...},
     "calev":   {...same...}}.
    זה הפלט היחיד ל-stdout/קובץ. כל המספרים, אפס פרשנות."""

def main() -> int:
    """CLI: argparse.
    --reports-dir (default: reports/), --out (default: distillations/<date>-data.json),
    --prev (default: ה-data.json האחרון ב-distillations/ אם קיים),
    --threshold N (default 10), --check-only (רק החזר exit: 0 אם ≥threshold דוחות חדשים,
       1 אם פחות — לטיימר), --quiet.
    כותב את ה-data.json. מדפיס סיכום קצר ל-stdout."""
```

**Tests (TDD — אדום קודם)**. unittest, על fixtures סינתטיים:

*count_by_severity_category:*
- 3 findings (2 blocker avigail, 1 minor calev) → סינון ל-avigail מחזיר by_severity={blocker:2}, total_findings=2.
- דוח בלי findings (verdict=READY, findings=[]) → נספר ב-total_reports אבל 0 findings.
- category זהה בשני דוחות → by_category מסכם נכון.

*compute_hitrate:*
- 3 דוחות avigail, 2 עם findings → reports=3, reports_with_findings=2, avg_findings מעוגל.
- verdicts נספרים: {READY:1, USABLE-AFTER-FIX:2}.

*traceability_index:*
- 2 דוחות עם category="missing-symbol" מ-projects שונים → {"missing-symbol": ["projA/s1","projB/s2"]} ממוין.

*flag_noncanonical:*
- finding עם category="weird-new-thing" (לא קנוני) → מסומן. category="unique" → תמיד מסומן. category="missing-symbol" (קנוני avigail) → לא מסומן.
- **edge**: category קנוני של calev שמופיע בדוח avigail → מסומן (כי לא קנוני *ל-avigail*).

*compute_delta:*
- prev=None → כל trend="new".
- prev מכיל {missing-symbol: 5}, now {missing-symbol: 3} → trend="down", now=3, prev=5.
- now חדש (לא ב-prev) → "new". now=0 ו-prev=2 → "gone".

*count_new_reports_since:*
- last_data=None → מחזיר את כל מספר הדוחות.
- last_data עם 3 report_ids, יש 5 דוחות (2 חדשים) → מחזיר 2.

*load_reports (סלחנות — קריטי):*
- קובץ JSON לא-תקין → מדולג (לא קריסה), warn ל-stderr.
- README.md / .gitkeep בתיקייה → מדולגים (רק *.json שהם דוחות).
- דוח בלי שדה findings → נטען עם findings=[] (לא KeyError).
- **שונות שדות avigail/calev**: דוח calev עם mode/summary/dod_items (שדות נוספים) → נטען בלי בעיה (TypedDict total=False).

**Verification**:
```bash
python3 tests/test_distill.py          # כל ה-unittest ירוקים
python3 scripts/distill.py --reports-dir tests/fixtures/reports --out /tmp/d.json
python3 -c "import ast; ast.parse(open('scripts/distill.py').read())"  # syntax
```

**verifier-phase אחרי commit זה**: כן — זו הליבה. ה-verifier יריץ את ה-tests + יריץ את הסקריפט על ה-fixtures ויאמת שה-data.json נכון מספרית.

---

### Commit 1 — פורמט דוח-זיקוק + קטלוגים + traceability (approach: manual)

> **למה manual ולא integration**: אלה **תבניות Markdown** (templates) שמרדכי ממלא, לא קוד. אין מה לבדוק אוטומטית מעבר לקיום-מבנה. ה-content האמיתי נכתב ע"י מרדכי בזמן זיקוק. כאן רק מקימים את השלד + הכללים-איך-למלא.

**קבצים חדשים**:
- `distillations/README.md` — מסביר את שכבת הזיקוק: data.json (כמותי, סקריפט) → report.md (איכותני, מרדכי). מבנה תיקייה. הטריגר.
- `distillations/.gitkeep`
- `distillations/TEMPLATE-report.md` — תבנית דוח-זיקוק. 4 חלקים (מהדיון המקורי):
  1. **מבט-לאחור**: הכללים מהדוח הקודם, סטטוס יישום כל אחד (ירד/לא-השתנה/החמיר/אין-נתונים) — מבוסס על `delta` מה-data.json.
  2. **התפלגות נוכחית**: severity × category פר-verifier (טבלה מה-data.json).
  3. **חדשות**: קטגוריות `new`/`noncanonical` — מועמדות לזיקוק-טקסונומיה.
  4. **עדכוני-קטלוג**: מה נכנס/יצא/השתנה-בדירוג ב-plan-pitfalls/patterns.
- `plan-pitfalls.md` — קטלוג טעויות-**תכנון** (avigail), חדש. מבנה מקביל ל-`patterns.md`:
  - כותרת + "מבוסס על: N דוחות. יתעדכן בכל זיקוק."
  - קטגוריה ראשונה מהדיון המקורי (כבר ידועה): **"הנחה לא-מאומתת על כלי/API/סביבה"** (yq/PyYAML/exit-code) — המלכה. עם **traceability**: "מבוסס על: reports/bds/bds-extraction-*, voice-acp/17-*" (רשימת מקורות).
  - placeholder לקטגוריות עתידיות.

**קבצים שמשתנים**:
- `patterns.md` — **הוסף בלבד** (אל תשנה את 5 הקטגוריות הקיימות): סעיף **"## Traceability — מקורות"** בסוף, שמסביר שכל קטגוריה תצביע על reports שתרמו לה (מבנה: `> מקורות: project/slice-verifier, ...`). + עדכן את שורה 2 ("מבוסס על: 1 case study") → להוסיף "+ זיקוק אוטומטי מ-reports/ (ראה distillations/)".

> **traceability דו-כיווני** (ההכרעה מהדיון): כל **כלל בקטלוג** מצביע על הדוחות שיצרו אותו (`> מקורות: ...`). כל **דוח-זיקוק** מצביע על הכללים שעדכן (חלק 4 בתבנית). אפשר לחזור מכלל למקור ולהפך.

**Verification** (manual):
```bash
# קיום + מבנה
test -f plan-pitfalls.md && test -f distillations/TEMPLATE-report.md
grep -q "הנחה לא-מאומתת" plan-pitfalls.md      # הקטגוריה המלכה קיימת
grep -q "מקורות" patterns.md                    # traceability נוסף
grep -q "Traceability\|מקורות" plan-pitfalls.md  # traceability דו-כיווני
```

---

### Commit 2 — יומן-גלובלי של אבולוציית השיטה (approach: manual)

> זה ה-walkthrough של **השיטה עצמה** (שכבה 3: נרטיב מלא, לא שוכח). נדיר — מתעדכן רק כשמשפרים את brief-driven-slices כמתודולוגיה, לא כשמשתמשים בה (ההכרעה מהדיון, ses_18bf3938 #181).

**קבצים חדשים**:
- `docs/methodology-evolution.md` — יומן גלובלי. מבנה כרונולוגי. **תוכן ראשוני** (האירועים שכבר קרו — מקור: `docs/decisions/bds.md` + `docs/walkthrough.md`):
  - היווצרות הצוות (5 סוכנים תנ"כיים), הרציונל ל-merge-בלעדי-למרדכי.
  - המעבר מ-exit-code ל-file-existence ל-BLOCKED.
  - JSON-לא-YAML (אין PyYAML).
  - פיצול calev→calev-heavy (Opus למקום שהאמת מהסקה).
  - **השיפור הנוכחי**: שכבת הזיקוק (ה-slice הזה).
- הבחנה מפורשת בראש הקובץ: זה **לא קטלוג** (מזוקק, שוכח) ו**לא decisions פר-פרויקט** (לוקאלי). זה הנרטיב הגלובלי של איך השיטה התפתחה.

**Verification** (manual):
```bash
test -f docs/methodology-evolution.md
grep -q "merge\|זיקוק\|calev-heavy" docs/methodology-evolution.md
```

---

### Commit 3 — מנגנון הרצה תקופתית: systemd timer + מרדכי-אוטומטי (approach: manual)  ⚠️ verifier-phase

> **למה manual ולא integration**: systemd units הם config; אי-אפשר לבדוק טיימר אמיתי ב-CI בלי לתזמן ריצה. אימות: syntax (`systemd-analyze verify`), ו-`bash -n` על ה-wrapper. ה-flow המלא נבדק ב-verifier-phase (כלב מריץ את ה-wrapper ידנית, מאמת שהוא קורא ל-distill.py ולא-ממזג).

**קבצים חדשים**:
- `scripts/distill-run.sh` — ה-wrapper שהטיימר מפעיל. הלוגיקה (העתק את הסגנון מ-`dispatch-executor.sh`):
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  BDS="$HOME/projects/brief-driven-slices/main"
  OPENCODE_BIN="$HOME/.opencode/bin/opencode"   # לא ב-PATH ב-timer (memory gotcha)
  cd "$BDS"
  # 1. טריגר כמותי: יש מספיק דוחות חדשים?
  if ! python3 scripts/distill.py --check-only --threshold "${BDS_DISTILL_THRESHOLD:-10}"; then
    echo "distill: פחות מהסף — יציאה בשקט"; exit 0
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
  ```
  > **גבולות אמת** (אומתו ב-slice קודם, decisions/bds.md): `opencode run` תמיד exit 0 גם בשגיאה; OPENCODE_BIN תחת `$HOME/.opencode` לא ב-PATH; `env -u OPENCODE_*` (memory 2026-05-16) למניעת זליגת context.
- `scripts/distill-prompt.txt` — הפרומפט למרדכי-אוטומטי. **חייב לכלול**:
  - "אתה מרדכי במצב **זיקוק-אוטומטי**. קרא את `distillations/<date>-data.json` (הכמותי שכבר חושב)."
  - "כתוב `distillations/<date>-report.md` לפי TEMPLATE-report.md (4 חלקים). עדכן `plan-pitfalls.md`/`patterns.md` עם traceability. אם יש קטגוריה חדשה משמעותית — תעד שינוי-טקסונומיה כאירוע."
  - "**אתה על branch `bds-distill-<date>`. אסור לעשות merge, push, או worktree remove. סיים, commit ל-branch, ועצור.** התוצר ממתין למרג' אנושי בבוקר (SOUL.md)."
- `systemd/bds-distill.service` (user unit) — `Type=oneshot`, `ExecStart=%h/projects/brief-driven-slices/main/scripts/distill-run.sh`.
- `systemd/bds-distill.timer` — `OnCalendar=daily`, `Persistent=true`. prefix `bds-distill-` (כמו scheduler skill).
- `systemd/README.md` — איך להתקין: `systemctl --user enable --now bds-distill.timer`, ואיך משנים threshold (`BDS_DISTILL_THRESHOLD` env / EnvironmentFile).

> **המנגנון המשולב (ההכרעה — סגור)**: טיימר יומי → distill.py כמותי. אם <N דוחות חדשים → יציאה בשקט (זול). אחרת → מרדכי-אוטומטי כותב את הזיקוק האיכותני ל-**branch ייעודי**, **לא ל-main**. בבוקר מרדכי-האנושי סוקר וממזג ידנית. ה-merge תמיד אנושי — הטיימר הוא כמו אליעזר בלילה: מייצר תוצר, ממתין לאישור.

> **הגנת חגורה-וכתפיים נגד merge אוטומטי**: (1) הפרומפט אוסר merge מפורשות; (2) מרדכי-אוטומטי רץ ב-worktree של branch נפרד — merge ל-main דורש פעולה מפורשת שהפרומפט אוסר; (3) SOUL.md אוסר merge בלי אישור (חל על כל מצב מרדכי).

**Verification**:
```bash
bash -n scripts/distill-run.sh                      # syntax
systemd-analyze verify systemd/bds-distill.service  # אם זמין; אחרת קריאה אנושית
grep -q "אסור לעשות merge" scripts/distill-prompt.txt
grep -q "OnCalendar" systemd/bds-distill.timer
```

**verifier-phase אחרי commit זה**: כן — כלב מריץ את `distill-run.sh` ידנית עם threshold=0 (כדי לכפות הרצה), מאמת: (א) distill.py נקרא ו-data.json נכתב, (ב) branch נוצר ולא main נגעו, (ג) הפרומפט אוסר merge. **לא** מריץ את opencode עצמו (יקר) — רק מאמת שה-wrapper מגיע לנקודה הנכונה.

---

### Commit 4 — manual e2e + תיעוד (approach: manual)  ⚠️ verifier-phase

**קבצים שמשתנים**:
- `SKILL.md` / `workflow.md` — הוסף את שכבת הזיקוק לתיאור השיטה (3 שכבות זיכרון, מי מריץ, הטריגר).
- `docs/walkthrough.md` — ערך חדש (skill `update-walkthrough`): מה נבנה ב-slice הזה.
- `docs/decisions/bds.md` — ערך חדש (מרדכי): הרציונל של המנגנון המשולב (טיימר→כמותי→מרדכי-אוטומטי→branch→מרג'-אנושי), והחלוקה כמותי/איכותני.
- ה-brief הזה (סטטוס → הושלם).

**Manual e2e** (תעד ב-commit msg):
1. הרץ `distill.py` על ה-fixtures → ודא data.json נכון.
2. הרץ `distill.py` על ה-reports האמיתי (`reports/`, report אחד) → ודא שלא קורס על דגימה דלה, שמסומן noncanonical/new נכון.
3. הרץ `distill-run.sh` עם threshold=0 → ודא branch נוצר, main לא נגע (דמה את opencode — אל תפעיל מודל אמיתי).
4. ודא ש-3 הקטלוגים/יומן קיימים ובמבנה תקין.

**verifier-phase אחרי commit זה**: כן — verifier-slice-light הסופי (§5).

---

## §5 — DoD verifiable

| # | בדיקה | איך |
|---|------|------|
| 1 | distill.py tests ירוקים | `python3 tests/test_distill.py` — כל ה-unittest עוברים |
| 2 | syntax נקי | `python3 -c "import ast; ast.parse(open('scripts/distill.py').read())"` + `bash -n scripts/distill-run.sh` |
| 3 | **ספירה נכונה** | הרץ על fixtures, ודא `by_severity`/`by_category` תואמים את מה שב-fixtures (ספירה ידנית) |
| 4 | **דלתא** | הרץ פעמיים (snapshot→snapshot), ודא trend (up/down/new/gone) מחושב נכון מול ה-prev |
| 5 | **traceability** | category בקטלוג → `> מקורות:` קיים; data.json `trace` ממפה category→reports |
| 6 | **טריגר כמותי** | `distill.py --check-only --threshold 999` → exit 1 (פחות מהסף); `--threshold 0` → exit 0 |
| 7 | **לא-ממזג** | `distill-run.sh` (threshold=0, opencode מדומה) → branch `bds-distill-*` נוצר, `git log main` לא השתנה |
| 8 | סלחנות | JSON פגום ב-reports/ → distill.py לא קורס, warn ל-stderr, ממשיך |
| 9 | קטלוגים + יומן קיימים | `test -f plan-pitfalls.md && test -f docs/methodology-evolution.md && test -f distillations/TEMPLATE-report.md` |
| 10 | על reports אמיתי | `distill.py --reports-dir reports` (report אחד) → לא קורס, מסמן noncanonical |
| 11 | systemd syntax | `grep OnCalendar systemd/bds-distill.timer` + prompt אוסר merge |

---

## §6 — Risks + mitigations

| סיכון | מקור | מיטיגציה |
|------|------|----------|
| **אין pytest בסביבה** | AGENTS.md global ("NOT available: ... pytest" — אומת) | unittest (stdlib) בלבד. `python3 tests/test_distill.py`, לא `pytest`. ⚠️ אם אליעזר יכתוב pytest — יתקע. |
| **אין PyYAML/yq** | decisions/bds.md (אומת אמפירית) | json stdlib בלבד. הדוחות JSON ממילא. |
| שדות לא-אחידים avigail/calev בדוחות | calev מוסיף mode/summary/dod_items; avigail לא | TypedDict `total=False` + `.get()` בכל גישה. load_reports סלחני. Test מכסה. |
| **דגימה דלה** (report אחד) שוברת חישוב | reports/ מכיל רק bds-extraction-calev | distill.py חייב לעבוד על n=1 (avg, delta מול None). Test + DoD 10. **זו הסיבה שההרצה-האמיתית מחוץ ל-scope.** |
| `opencode run` exit 0 גם בכשל | memory 2026-05-28, decisions/bds.md | ה-wrapper לא סומך על exit code של opencode. הסיגנל הוא קיום ה-branch + ה-report. |
| OPENCODE_BIN לא ב-PATH בטיימר | memory + decisions/bds.md | נתיב מלא `$HOME/.opencode/bin/opencode` ב-wrapper. |
| **מרדכי-אוטומטי ממזג בטעות** | merge הוא בלעדי-אנושי (SOUL.md) | 3 הגנות (Commit 3): פרומפט אוסר + worktree-branch-נפרד + SOUL.md. DoD 7 מאמת ש-main לא נגע. |
| זליגת OPENCODE_* context לסשן מרדכי-אוטומטי | memory 2026-05-16 (sub-agent run) | `env -u OPENCODE_SESSION -u OPENCODE_AGENT` ב-wrapper. |
| טקסונומיה משתנה שוברת מדידה | הדיון (ses_18bf3938 #175) | flag_noncanonical מסמן מועמדים; שינוי מתועד כאירוע בדוח-זיקוק (חלק 3/4). distill.py לא מחליט לבד — רק מסמן. |

> 3 שתמיד נשכחים:
> 1. Hardcoded strings → i18n: לא רלוונטי (CLI/תיעוד, לא UI). הטקסט בקטלוגים עברית-מכוון.
> 2. Reactivity: לא רלוונטי (אין framework).
> 3. OneCLI placeholder: לא רלוונטי (אין proxy).
> **במקום זה, ה-3 הרלוונטיים כאן**: pytest-לא-קיים, opencode-exit-0, merge-אוטומטי.

---

## §7 — Escalation triggers

> אם X — עצור ושאל את Tama:

- פיתוי לתת ל-distill.py **לפרש** (לנסח כללים, לכתוב נרטיב, להחליט פיצול-קטגוריה) — לא. זו עבודת מרדכי. הסקריפט סופר בלבד.
- פיתוי לגרום למרדכי-אוטומטי **למזג** — אסור מוחלט. אם נראה שצריך merge אוטומטי — Escalate.
- pytest נדרש (משהו ש-unittest לא מכסה) — Escalate לפני התקנה.
- distill.py קורס על n=1 או על reports אמיתי — זה DoD, לא Escalation. אבל אם החישוב **לא מוגדר** ל-n=1 (למשל avg של 0 דוחות) — Escalate על ההגדרה.
- מבנה ה-systemd לא עובד בסביבה (no `systemd --user`) — Escalate; אולי cron/scheduler skill חלופי.
- Brief סותר את עצמו / קוד בפועל שונה מ-file:line שצוטט.

---

## §8 — Complexity score + verifier tier

| פרמטר | ניקוד |
|------|------|
| State machine / async coordination (delta מול snapshot, טריגר כמותי) | +2 |
| >5 files ב->2 "packages" (scripts/, distillations/, systemd/, docs/, catalogs) | +1 |
| מנגנון הרצה תקופתית (systemd + opencode orchestration) | +2 |
| Pure logic core (distill.py) — TDD מלא | -1 |
| Cross-store data flow חדש? לא (קורא reports קיימים, אין store חדש) | 0 |
| ספרייה חיצונית חדשה? לא (stdlib בלבד) | 0 |
| Refactor של קוד קיים? מעט (patterns.md additive בלבד) | +1 |
| Greenfield (distill.py, אין call sites) | -1 |
| רגישות: מרדכי-אוטומטי + merge guard | +2 |

**Score**: 6 / 10

**Tier**: light + verifier-phase על Commit 0 (הליבה הכמותית) ו-Commit 3 (ה-wrapper + merge-guard) ו-Commit 4 (e2e סופי).

**Verifier-phase אחרי commit/phase**: 0, 3, 4.

---

## §9 — שאלות פתוחות

| # | שאלה | ברירת מחדל | חוסם? |
|---|------|----------|------|
| 1 | סף הטריגר N | **10** (ניתן-לשינוי ב-`BDS_DISTILL_THRESHOLD`) | ❌ |
| 2 | תדירות הטיימר | **יומי** (`OnCalendar=daily`); הטריגר האמיתי כמותי, לא זמני | ❌ |
| 3 | מי "מרדכי-אוטומטי" — סוכן mordechai עם פרומפט-מגביל, או דמות נפרדת? | **סגור: mordechai עם פרומפט שאוסר merge + worktree-branch-נפרד** (גישה א + הגנות) | ❌ |
| 4 | distill.py — כמותי בלבד, מרדכי מפרש? | **סגור: כן.** סקריפט סופר, מודל מפרש | ❌ |
| 5 | ההרצה האמיתית הראשונה — ב-slice הזה? | **לא** — כשיצטברו ≥N דוחות אמיתיים. כאן בונים את הכלי ובודקים על fixtures | ❌ |
| 6 | יומן-גלובלי — קובץ אחד או פר-נושא? | קובץ אחד (`methodology-evolution.md`), נדיר ממילא | ❌ |

---

## נספח A — פער נפרד שעלה תוך כדי: bootstrap של פרויקט חדש (`init-project`)

> **זה לא חלק מ-scope ה-slice הזה.** זה פער נפרד שזוהה בזמן ה-bootstrap הידני של bds, ותועד כדי שלא ייפול. **slice עתידי נפרד** — לא להחליט/לבצע כאן. מקור מלא נשמר ב-`docs/specs/init-project-bootstrap.md` (קבוע, tracked).

**הפער**: השיטה (`worktrees.md`) מתעדת את מבנה bare+worktrees ואיך ליצור worktree של slice — אבל **אין bootstrap** להקמת המבנה כשמתחילים פרויקט חדש. מי שמקים פרויקט חדש מבצע ~6 צעדים ידניים לא-טריוויאליים (בוצע פעם אחת ידנית ב-bootstrap של bds, מתועד כסטייה ב-decisions/bds.md).

**הדרישה המוצעת**: `scripts/init-project.sh <name>` — מקים פרויקט במבנה bare+worktrees בפקודה אחת. אופציות: `--main-only` (default), `--dev-main` (גם dev/ וגם main/, כמו voice-acp), `--existing <url>` (clone של repo קיים).

**3 מלכודות מאומתות שה-slice הזה יחויב לטפל בהן** (מהניסיון הידני):
1. **`gh repo create --source=.` נכשל מ-worktree** — ה-`.git` הוא pointer, לא directory. פתרון: `gh repo create` בלי `--source`, אז `git remote add` + `git push` ידני. (מתועד ב-memory global, 2026-05-30-gotcha-gh-repo-create-source-fails-in-worktree.)
2. **`core.worktree` שריד** בהמרת repo רגיל קיים ל-bare → warning. צריך `git config --unset core.worktree`. (ל-init מאפס לא קורה.)
3. **nested repos ב-gitignore** — אם הפרויקט מכיל reports/ או תת-repo, `.gitignore` של main צריך להחריגו.

**הערות חשובות (שלא ייפלו)**:
- המבנה **נשאר המלצה, לא חובה** — ה-bootstrap צריך לתמוך גם ב-worktree רגיל, לא רק bare.
- אם לא בונים סקריפט מלא — המינימום לסגירת הפער הוא **checklist ב-worktrees.md** ("הקמת פרויקט חדש", צעדים 1-7).

**הצעת complexity/verifier (ל-slice העתידי)**: ~4-5, calev **light**. מקור-אמת לצעדים: `decisions/bds.md` (סעיף "מבנה bare") + `walkthrough.md`. **מתאים במיוחד להיות ה-slice הראשון שרץ בלולאה המלאה** (worktree→אליעזר→calev→merge) — פואטי: slice על worktrees שרץ ב-worktree.

---

## סטיות מהתכנון (מתעדכן ע"י executor תוך כדי)

> ה-executor מתעד פה כל סטייה מה-brief ולמה.

- ...
