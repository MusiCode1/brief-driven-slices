# Slice A — merge-archive-cleanup — ‏בריף

> **‏תאריך**: 2026-07-19
> **‏סוג מסמך**: ‏בריף ביצועי (‏slice דוקטרינה — ‏עריכת הגדרות-סוכן, ‏אין קוד-runtime)
> **‏סטטוס**: ‏טיוטה
> **‏אימות אביגיל**: ‏לא מאומת (‏דוח: `reports/bds/merge-archive-cleanup-avigail.md`)
> **Complexity**: 2/10 (verifier: light — ‏אין runtime; ‏plan-verification בלבד)
> **‏תלויות (`depends_on`)**: []  (‏נוגע ב-mordechai.md — ‏path-neutrality לא נוגע בו, ‏אין התנגשות)
> **‏Base**: main
> **‏Dev tip**: `fe1a0a3`

---

## §0 — Pre-flight

slice ‏על ריפו השיטה. ‏עריכת דוקטרינה בלבד: `agent-definitions/prompts/mordechai.md` (‏מקור-האמת) + regenerate. ‏אין pnpm/runtime.

### ‏תלויות
‏אין. ‏path-neutrality (‏branch מקביל) ‏עורך avigail/calev/yetro prompts + scripts — ‏**‏לא** ‏את mordechai.md. ‏אין חפיפת-קבצים.

### Reading list
- `agent-definitions/prompts/mordechai.md` — §"‏בוקר (‏אחרי לילה)" (grep: `## ‏בוקר`) + §cleanup (grep: `נקה worktrees`).
- `scripts/generate-cli-configs.py` — ‏להבין regenerate.

---

## §1 — ‏מטרה

‏אחרי merge מאושר, ה-brief שיושם **‏מתארכב אוטומטית** ‏וה-worktree **‏מתנקה** — ‏כ**‏ריטואל אטומי אחד**, ‏לא צעדים נפרדים שנשכחים. ‏`docs/plans/` ‏מכיל רק briefs חיים (‏לא-מוזגו); ‏מיושמים ‏ב-`docs/plans/archive/`.

---

## §2 — Scope

| ‏פריט | ‏כן/לא | ‏לאן |
|------|------|------|
| ‏ארכוב brief כחלק-חובה מטקס ה-merge | ✅ | ‏slice זה |
| ‏cleanup worktree ‏באותו ריטואל אטומי | ✅ | ‏slice זה (‏קיים — ‏להדק לאטומי) |
| ‏יצירת `docs/plans/archive/` | ✅ | ‏slice זה |
| ‏ארכוב **‏רטרואקטיבי** של briefs ישנים קיימים | ❌ | ‏קורה מעצמו ‏כשכל slice ימוזג; ‏לא batch ידני |
| ‏מי מארכב: **‏הסוכן הממזג (מרדכי)**, ‏אחרי אישור-merge | ✅ | ‏עיקרון |

> ‏הבהרה (‏החלטת משתמשת): ‏הארכוב הוא **‏ריטואל של הסוכן אחרי merge מאושר** — ‏לא ניקוי ידני חד-פעמי.

---

## §3 — ‏העיקרון

```
merge ritual (מרדכי, אחרי אישור-משתמשת):
  git merge --no-ff <branch>
  git push
  ─── חדש: אטומי, לא צעד-נפרד-נשכח ───
  git mv docs/plans/<slice>.md docs/plans/archive/<slice>.md   # ארכוב ה-brief
  git commit -m "archive: <slice> brief (merged)"
  git worktree remove --force .worktrees/<name>                # cleanup
  git branch -D slice/<name> ; git worktree prune
```
‏merge, push, archive, cleanup = **‏פעולה אחת מושגית**. ‏אין "‏אמזג עכשיו ‏ואארכב אחר כך".

---

## §4 — Commits ‏בסדר

### Commit 0 — ‏תיקיית archive + ‏דוקטרינת-מרדכי (approach: manual)

**‏קבצים חדשים**: `docs/plans/archive/.gitkeep`

**‏קבצים שמשתנים**: `agent-definitions/prompts/mordechai.md`
- ‏ב-§"‏בוקר" (grep anchor: `**‏עבור על slices שעברו**`): ‏אחרי צעד ה-merge+push, ‏הוסף צעד **‏ארכוב ה-brief** (`git mv docs/plans/<slice>.md docs/plans/archive/`).
- ‏ב-§cleanup (grep anchor: `נקה worktrees שנמרגו`): ‏הדק לניסוח **‏ריטואל אטומי** — merge→push→archive→cleanup ‏כיחידה, ‏עם אזהרה מפורשת ש"‏אחר-כך" = ‏נשכח (‏הראיה: `docs/plans/` ‏שהצטבר).
- ‏עדכן anti-pattern: ‏הוסף "❌ ‏למזג בלי לארכב את ה-brief ‏באותו ריטואל".

**Verification**:
```bash
grep -q "archive" agent-definitions/prompts/mordechai.md && echo "archive step קיים"
python3 scripts/generate-cli-configs.py all   # regenerate
grep -rl "archive" cli-configs/*/agents/mordechai.md agents/mordechai.md   # → מופיע בכל ה-generated
ls docs/plans/archive/.gitkeep
```

### Commit 1 — SKILL.md (‏אם מתאר את טקס ה-merge) (approach: manual)

**‏קבצים שמשתנים**: `SKILL.md` — ‏אם יש §merge ritual / ‏lifecycle, ‏הוסף את שלב הארכוב. ‏אם אין — ‏דלג (‏תעד ב-§סטיות).

**Verification**: `grep -n "archive\|ארכוב\|merge" SKILL.md`

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | ‏שלב-ארכוב בדוקטרינת מרדכי | `grep "archive.*docs/plans/archive\|git mv docs/plans" agent-definitions/prompts/mordechai.md` |
| 2 | ‏ריטואל אטומי מנוסח | ‏§cleanup ‏מזכיר merge→push→archive→cleanup ‏כיחידה |
| 3 | ‏תיקיית archive קיימת | `ls docs/plans/archive/.gitkeep` |
| 4 | ‏generated מסונכרן | ‏אחרי `generate-cli-configs.py all` — ‏אין diff לא-committed ב-cli-configs/agents |
| 5 | anti-pattern נוסף | `grep "לארכב\|archive" agent-definitions/prompts/mordechai.md` ‏ב-anti-patterns |

---

## §6 — Risks

| ‏סיכון | ‏מיטיגציה |
|------|----------|
| ‏שכחת regenerate → generated לא מסונכרן עם המקור | DoD#4 ‏חוסם |
| ‏ניסוח "‏רטרואקטיבי" ‏מבלבל — ‏מישהו יחשוב שצריך batch ידני | §2 ‏מפורש: ‏קורה פר-merge, ‏לא batch |

---

## §7 — Escalation
- ‏אם SKILL.md ‏לא מתאר merge ritual ‏בכלל → ‏דלג על Commit 1, ‏תעד.

## §8 — Complexity: 2/10 (‏דוקטרינה, ‏אין runtime, ‏אין state). Tier: light (‏plan-verify בלבד; ‏אין calev — ‏אין מה להריץ).

## §9 — ‏שאלות פתוחות
| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ‏גם yetro מארכב (‏בלילה) ‏או רק מרדכי (‏ב-merge)? | ‏רק מרדכי — ‏yetro ‏לא ממזג, ‏אז ‏לא מארכב | ❌ |

## ‏סטיות מהתכנון
- ...
