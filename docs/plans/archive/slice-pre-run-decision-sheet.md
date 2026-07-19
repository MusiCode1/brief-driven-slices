# Slice — pre-run-decision-sheet — ‏בריף

> **‏תאריך**: 2026-07-19
> **‏סוג מסמך**: ‏בריף ביצועי (‏slice דוקטרינה)
> **‏סטטוס**: ‏טיוטה
> **‏אימות אביגיל**: ‏לא מאומת (‏דוח: `reports/bds/pre-run-decision-sheet-avigail.md`)
> **Complexity**: 2/10 (verifier: light — ‏plan-verification בלבד)
> **‏תלויות (`depends_on`)**: []  (‏עורך §"‏ערב"/opening של mordechai.md — ‏לא נגע בו ב-slices הקודמים)
> **‏Base**: main
> **‏Dev tip**: ‏HEAD הנוכחי

---

## §0 — Pre-flight

slice ‏דוקטרינה. ‏עורך `agent-definitions/prompts/mordechai.md` + SKILL + regenerate. ‏מקור:
‏פריט 23 ב-`recommendations.md` (‏front-loaded decision sheet).

### Reading list
- `recommendations.md` §23 (‏המקור).
- `agent-definitions/prompts/mordechai.md` — §"‏ערב" (‏פתיחת ה-workflow, grep: `## ‏ערב`).

---

## §1 — ‏מטרה

‏לפני שמרדכי מתחיל ריצה (‏אוטונומית או לא), ‏הוא מציג **‏דף-החלטות אחד**: ‏כל שאלות ה-scope +
‏הרשאות-מראש ל-7 תרחישים שצצים תוך-כדי (‏עם defaults). ‏המשתמשת עונה **‏פעם אחת** → ‏מרדכי רץ
‏brief→אביגיל→יישום→כלב עד ה-merge gate **‏בלי הפרעה**. ‏אינטראקציה = ‏דף אחד לפני + ‏אישור-merge אחד אחרי.

---

## §2 — Scope

| ‏פריט | ‏כן/לא |
|------|------|
| ‏שלב "‏דף-החלטות" ב-§ערב של mordechai (‏לפני dispatch) | ✅ |
| ‏טבלת 7 התרחישים + defaults ‏בדוקטרינה | ✅ |
| ‏עדכון anti-pattern | ✅ |
| ‏אכיפה אוטומטית (‏כלי) | ❌ (‏דוקטרינה — ‏הרגל, ‏לא מנגנון) |

---

## §3 — ‏העיקרון

```
היום:  מרדכי → brief → אביגיל → dispatch → [עצירה כשצץ תרחיש] → שאלה → ...
חדש:   מרדכי → דף-החלטות (scope + 7 תרחישים/defaults) → אישור-פעם-אחת →
              brief → אביגיל → יישום → כלב  [בלי הפרעה]  → merge gate
```
7 ‏התרחישים (‏מ-track record): scope דו-משמעי · ‏תלות=WIP · ‏אביגיל NEEDS-REWORK ·
‏כלב NO-GO · ‏התנגשות-merge · **‏פעולה בלתי-הפיכה ל-mainline (=‏תמיד עצור)** · fix-loop depth.

---

## §4 — Commits ‏בסדר

### Commit 0 — ‏דוקטרינת §ערב (approach: manual)

**‏קבצים שמשתנים**: `agent-definitions/prompts/mordechai.md`
- ‏ב-§"‏ערב" (‏grep anchor: `## ‏ערב`): ‏הוסף **‏שלב 0 — ‏דף-החלטות** ‏לפני כתיבת briefs:
  ‏הצג scope-questions + ‏טבלת 7 התרחישים עם defaults; ‏קבל אישור-פעם-אחת.
- ‏הוסף את טבלת 7 התרחישים (‏מ-recommendations §23).
- anti-pattern: "❌ ‏להתחיל ריצה בלי דף-החלטות → ‏עצירות חוזרות באמצע".

**Verification**:
```bash
grep -q "דף-החלטות\|decision sheet" agent-definitions/prompts/mordechai.md && echo "✓"
python3 scripts/generate-cli-configs.py all
grep -l "דף-החלטות\|decision" agents/mordechai.md cli-configs/*/agents/mordechai.md
```

### Commit 1 — SKILL (approach: manual)

- `SKILL.md` — **‏חובה** (SKILL ‏מתאר את lifecycle ‏של Mode 1/2 ‏מפורשות — grep anchor:
  `### Mode 1`). ‏הוסף את שלב **‏דף-החלטות** ‏בתחילת הזרימה (‏לפני "‏מרדכי → Task(eliezer)"
  ‏ב-Mode 1, ‏ולפני "‏ערב: briefs מאומתים" ‏ב-Mode 2).

**Verification**:
```bash
grep -q "דף-החלטות\|decision sheet" SKILL.md && echo "✓ SKILL עודכן"
```

---

## §5 — DoD verifiable

> ‏כל ה-grep על **‏מקור-האמת** `agent-definitions/prompts/mordechai.md` (‏לא ה-generated).

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | ‏שלב דף-החלטות בדוקטרינה | `grep "דף-החלטות" agent-definitions/prompts/mordechai.md` |
| 2 | ‏טבלת 7 תרחישים | `grep -c "עצור\|default" agent-definitions/prompts/mordechai.md` ≥ 7 |
| 3 | ‏"‏בלתי-הפיך = ‏תמיד עצור" מפורש | `grep "בלתי-הפיך\|mainline" agent-definitions/prompts/mordechai.md` |
| 4 | **‏גבול micro-task מנוסח** (‏הסיכון המרכזי) | `grep "micro-task" agent-definitions/prompts/mordechai.md` — ‏טוקן ייחודי לפטור (‏לא "‏ריצה" הגנרי) |
| 5 | SKILL עודכן | `grep "דף-החלטות\|decision sheet" SKILL.md` — ‏לא-ריק |
| 6 | generated מסונכרן | ‏אחרי `generate-cli-configs.py all` — ‏אין diff לא-committed |
| 7 | anti-pattern **‏בסקציה** | `sed -n '/# Anti-patterns/,$p' agent-definitions/prompts/mordechai.md \| grep "דף-החלטות"` — ‏בתוך הסקציה בלבד |

---

## §6 — Risks
| ‏סיכון | ‏מיטיגציה |
|------|----------|
| ‏דף-החלטות הופך לבירוקרטיה על כל micro-task | ‏ניסוח: ‏חובה ל**‏ריצה** (‏מרובת-slices/אוטונומית); ‏למשימה טריוויאלית — ‏אופציונלי |
| ‏שכחת regenerate | DoD#6 |

## §7 — Escalation
- ‏אם §ערב ‏של mordechai ‏השתנה מהותית → ‏עדכן anchor.

## §8 — Complexity: 2/10 (‏דוקטרינה). Tier: light (‏plan-verify בלבד).

## §9 — ‏שאלות פתוחות
| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ‏חובה לכל ריצה ‏או רק אוטונומית? | ‏כל **‏ריצה** (‏מרובת-slices); ‏micro-task ‏פטור | ❌ |

## ‏סטיות מהתכנון
- ...
