# Slice B — web-live-preview-gate — ‏בריף

> **‏תאריך**: 2026-07-19
> **‏סוג מסמך**: ‏בריף ביצועי (‏slice דוקטרינה)
> **‏סטטוס**: ‏טיוטה
> **‏אימות אביגיל**: ‏לא מאומת (‏דוח: `reports/bds/web-live-preview-gate-avigail.md`)
> **Complexity**: 2/10 (verifier: light — ‏plan-verification בלבד)
> **‏תלויות (`depends_on`)**: [merge-archive-cleanup]  (‏שניהם עורכים `mordechai.md` — ‏סקציות שונות; ‏שרשור למניעת התנגשות)
> **‏Base**: `slice/merge-archive-cleanup` (‏שרשור — ‏slice A ‏לא-מוזג עדיין)
> **‏Dev tip**: `fe1a0a3` (+ ‏commits של slice A)

---

## §0 — Pre-flight

slice ‏דוקטרינה על ריפו השיטה. ‏עריכת `agent-definitions/prompts/mordechai.md` §runtime-gate + SKILL + regenerate. ‏אין runtime.

### ‏תלויות
**‏slice A (merge-archive-cleanup)** — ‏חובה שיושם/יבוצע **‏לפני** ה-slice הזה (‏base = branch של A).
‏שני ה-slices עורכים את `mordechai.md`, ‏וב**‏פרט את סקציית ה-Anti-patterns המשותפת** (‏שניהם
‏מוסיפים anti-pattern) — ‏אז section-separation ‏**‏לא** ‏מספיק; ‏מה שמונע התנגשות הוא ה**‏שרשור**
‏(finding אביגיל B#1/#2): ‏B ‏מבוסס על branch של A, ‏אז git ‏רואה את שינויי-A כבר בבסיס.
‏**‏משמעות אופרטיבית**: ‏לא לבצע את B ‏עד ש-A ‏קיים כ-branch.

### Reading list
- `agent-definitions/prompts/mordechai.md` — §"runtime-gate — לפני merge" (grep: `## runtime-gate`) + ‏טבלת GO/PARTIAL/NO-GO.

---

## §1 — ‏מטרה

‏בפרויקטי **web**, ‏לפני merge — ‏אחרי שכלב מחזיר GO (‏אימות-מכונה) — ‏מרדכי מעלה **preview חי** (dev server / deployed URL) ‏ומציג למשתמשת ל**‏אישור-עיניים**. ‏המשתמשת רואה שהכל עובד לפני נקודת אי-החזרה. ‏שתי שכבות: ‏אימות-מכונה (‏כלב) → ‏אימות-אדם-חי (‏משתמשת).

---

## §2 — Scope

| ‏פריט | ‏כן/לא |
|------|------|
| gate ‏חדש "live-preview" ל-web, ‏אחרי כלב-GO ‏ולפני merge | ✅ |
| ‏חל **‏רק** ‏על פרויקטי web (‏יש UI ‏לראות) | ✅ |
| ‏בניית כלי-preview אוטומטי | ❌ (‏מרדכי משתמש ב-dev server הקיים של הפרויקט) |
| ‏החלפת calev-heavy "visual review" | ❌ (‏משלים — ‏עיני-אדם ≠ ‏שיפוט-סוכן) |

---

## §3 — ‏העיקרון (‏gate מורחב)

```
runtime-gate (קיים):  כלב GO → אפשר merge (אחרי אישור משתמשת)
                              ▼  חדש ל-web:
live-preview gate:    מרדכי מריץ dev server / preview URL
                      → מציג למשתמשת → אישור-עיניים מפורש
                      → רק אז merge
```
‏זה הופך את "merge רק באישור מפורש" (‏הכלל הקדוש) ל**‏מושכל** ‏— ‏האישור מבוסס על מה שהמשתמשת ‏**‏ראתה רץ**, ‏לא רק על verdict של סוכן.

---

## §4 — Commits ‏בסדר

### Commit 0 — ‏דוקטרינת runtime-gate (approach: manual)

**‏קבצים שמשתנים**: `agent-definitions/prompts/mordechai.md`
- ‏ב-§"runtime-gate" (grep anchor: `## runtime-gate — לפני merge`): ‏אחרי טבלת GO/PARTIAL/NO-GO, ‏הוסף **‏שלב live-preview ל-web**: "‏אם הפרויקט web ‏ו-verdict=GO → ‏העלה preview חי, ‏הצג למשתמשת, ‏קבל אישור-עיניים מפורש **‏לפני** merge".
- ‏עדכן את שורת ה-GO (grep: `אפשר למזג (אחרי אישור משתמשת)`): ‏ל-web, ‏האישור דורש preview חי, ‏לא רק verdict.
- ‏הוסף anti-pattern: "❌ ‏למזג web-slice ‏בלי preview חי שהמשתמשת ראתה — ‏גם אם כלב GO".

**Verification**:
```bash
grep -q "preview" agent-definitions/prompts/mordechai.md && echo "live-preview gate קיים"
python3 scripts/generate-cli-configs.py all
grep -rl "preview" cli-configs/*/agents/mordechai.md agents/mordechai.md
```

### Commit 1 — SKILL.md (approach: manual)

**‏קבצים שמשתנים**: `SKILL.md` — ‏אם מתאר runtime-gate/merge, ‏הוסף את ה-live-preview gate ל-web. ‏אחרת דלג (‏§סטיות).

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | live-preview gate בדוקטרינה | `grep "preview.*web\|web.*preview" agent-definitions/prompts/mordechai.md` |
| 2 | ‏מותנה ב-web בלבד | ‏הניסוח מגביל ל-web (‏לא כל slice) |
| 3 | ‏אחרי כלב-GO, ‏לפני merge | ‏הסדר בטקסט: GO → preview → merge |
| 4 | anti-pattern נוסף | `grep "preview" agent-definitions/prompts/mordechai.md` ‏ב-anti-patterns |
| 5 | generated מסונכרן | ‏אחרי regenerate — ‏אין diff לא-committed |

---

## §6 — Risks
| ‏סיכון | ‏מיטיגציה |
|------|----------|
| ‏התנגשות עם slice A ‏על mordechai.md (‏כולל Anti-patterns משותף) | **‏שרשור** — base=branch A (‏section-separation לבד לא מספיק, ‏כי שניהם עורכים Anti-patterns) |
| ‏"web" ‏אין trigger מכני (‏אין project-type marker בדוקטרינה) | ‏**‏שיפוט מוגדר**: "web" = ‏פרויקט עם FE/UI ‏שאפשר לפתוח בדפדפן (‏dev server / URL). ‏אם ספק — ‏מרדכי מחיל את ה-gate (‏fail-safe: ‏עדיף preview מיותר מאשר merge-עיוור). ‏marker מכני = ‏slice עתידי, ‏מחוץ ל-scope. |

## §7 — Escalation
- ‏אם SKILL.md ‏לא מתאר runtime-gate → ‏דלג Commit 1.

## §8 — Complexity: 2/10 (‏דוקטרינה). Tier: light (‏plan-verify בלבד).

## §9 — ‏שאלות פתוחות
| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | preview = dev server מקומי ‏או deployed URL? | ‏מה שהפרויקט מספק (‏dev server מקומי ‏בד"כ) | ❌ |
| 2 | ‏גם ל-non-web (CLI/lib) ‏צריך gate-אדם? | ‏לא — ‏רק web (‏יש מה לראות). CLI ‏נשען על כלב. | ❌ |

## ‏סטיות מהתכנון
- ...
