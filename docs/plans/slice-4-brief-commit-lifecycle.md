# Slice 4 — brief-commit-lifecycle — ‏תוכנית

> **‏תאריך**: 2026-06-03
> **‏סטטוס**: ‏טיוטה
> **Complexity**: 2/10 (verifier: light)
> **‏תלויות (`depends_on`)**: [] ‏— ‏בנוי ישירות על main
> **‏Base**: main
> **‏Dev tip**: `a8c521a`

---

## §0 — Pre-flight

> ‏זהו slice **‏של השיטה עצמה** (brief-driven-slices). ‏לכן "‏הפרויקט" = ‏ריפו השיטה,
> ‏ו-decisions ‏נכתב ל-`main/docs/decisions/bds.md` (‏לא ל-project נפרד).
> ‏ה-base כאן הוא `main` (‏לא `dev` — ‏לפרויקט הזה אין branch dev; ‏ראה `git branch -a`).

### ‏תלויות (‏חובה!)

‏slice זה **‏אין לו תלויות** — ‏בנוי ישירות על `main` ‏בtip `a8c521a`.
‏הוא נוגע רק בקבצי תיעוד/מתודולוגיה, ‏לא בקוד.

### Worktree

```bash
cd /home/user/projects/brief-driven-slices
git worktree add .worktrees/slice-4-brief-commit-lifecycle -b slice-4-brief-commit-lifecycle main
cd .worktrees/slice-4-brief-commit-lifecycle
```

‏(‏פרויקט bare — ‏ה-worktree נוצר תחת ה-root `.worktrees/`, ‏לא תחת `main/`.
‏אם cwd ‏שלך הוא `main/` ‏ולא ה-root — ‏השתמש ב-absolute path.)

‏אין `pnpm install` / `hooks:install` — ‏אין package manager ‏פעיל לקבצי docs.
‏הבדיקות בפרויקט הן Python (`python3 -m pytest tests/`), ‏אבל **‏ה-slice הזה לא נוגע בקוד Python** ‏ולכן לא מריץ אותן (‏ראה §5 DoD).

### ‏איך להריץ

- ‏אין שרת. ‏זה slice docs-only.
- ‏אימות = ‏קריאה + grep (‏ראה §5).
- ‏tests קיימים (לא-קשורים): `cd <worktree> && python3 -m pytest tests/ -q` — ‏אמורים להישאר ירוקים (‏לא נגענו ב-`scripts/distill.py`).

### Browser

‏לא רלוונטי — ‏אין UI.

### OneCLI agent

‏לא רלוונטי.

### Reading list

**must-read** ‏(לפני שמתחילים):
- `workflow.md` §שלב 2 (‏שורות 18-40), §שלב 3 (42-74), §שלב 4 (76-86) — ‏גבול ה-planning↔worktree
- `agents/mordechai.md` §ערב (44-63) — ‏סדר הצעדים של מרדכי
- `briefs/EXECUTOR_DISPATCH.md` §1 Worktree (29-44), §8 Workflow general (177-197), §11 (238-251)
- `briefs/BRIEF_TEMPLATE.md` ‏שורות 1-9 (‏front-matter status), ‏214-218 (‏סטיות ע"י executor)

**reference** (‏בזמן עבודה):
- ‏ה-handoff ב-`system/handoff.md` (memfs project scope) — ‏ה-gotcha של זליגת-עריכה ל-main בslice-3

---

## §1 — ‏מטרה

‏היום ה-workflow ‏לא אומר במפורש **‏מתי לקמט את ה-brief**. ‏זו פרצה: ב-bare+worktrees,
‏ה-worktree הוא branch נפרד שמתפצל מה-base — ‏אם ה-brief לא committed ל-base **‏לפני**
`git worktree add`, ‏האקזקיוטר (אליעזר) ‏פשוט **‏לא יראה את התוכנית** בworktree שלו.

‏אחרי ה-slice הזה, ‏מי שקורא את `workflow.md` ‏ו-`agents/mordechai.md` ‏ידע בדיוק
‏את מחזור-החיים של ה-commit של ה-brief: ‏מי מקמט, ‏מתי, ‏ובאיזה branch — ‏כולל
‏ההגנה מהזליגה ל-main שקרתה בslice-3 (‏אליעזר ערך brief ב-`main/` ‏במקום בworktree).

---

## §2 — Scope

| ‏פיצ'ר | ‏כן/לא | ‏לאן |
|------|------|------|
| ‏תיעוד "‏מרדכי מקמט brief לפני worktree" ב-`workflow.md` | ✅ | ‏slice הזה |
| ‏תיעוד מחזור-הסטטוס (טיוטה→מאושר→בעבודה→הושלם) ‏ומי מקמט כל מעבר | ✅ | ‏slice הזה |
| ‏הוספת הצעד ל-`agents/mordechai.md` §ערב | ✅ | ‏slice הזה |
| ‏אזהרת "‏executor עורך brief רק בworktree, ‏לא ב-main" ב-EXECUTOR_DISPATCH | ✅ | ‏slice הזה |
| ‏חידוד ב-`BRIEF_TEMPLATE.md` ‏שה-status מתעדכן ‏ומי מקמט | ✅ | ‏slice הזה |
| ‏תיקון ה-staleness ב-workflow §שלב 3 (Tama→מרדכי, general→avigail, plan-verifier.md לא קיים) | ❌ | slice נפרד ‏(scope creep — ‏אזכור בלבד ב-§9) |
| ‏שינוי קוד Python / distill / state.template | ❌ | ‏לא רלוונטי |
| ‏יצירת מנגנון אכיפה אוטומטי (pre-commit שבודק brief committed) | ❌ | ‏over-engineering ל-docs slice |

> ‏זו לא טבלת TODO. ‏זו הגנה מ-scope creep. ‏ה-slice הזה הוא **‏docs בלבד**.

---

## §3 — Architecture diagram

‏אין ארכיטקטורת קוד — ‏זה slice תיעוד. ‏הדיאגרמה היא של **‏מחזור-החיים** שאנחנו מתעדים:

```
                    branch = base (main / dev)          worktree (slice branch)
                    ┌──────────────────────────┐        ┌──────────────────────────┐
‏מרדכי כותב brief    │ docs/plans/slice.md       │        │                          │
status: ‏טיוטה   ───►│  commit #1 (מרדכי)        │        │                          │
                    │                           │        │                          │
‏אביגיל READY        │                           │        │                          │
status: ‏מאושר  ───►│  commit #2 (מרדכי)        │        │                          │
                    │                           │        │                          │
                    │   ── git worktree add ──────────►  │ ‏(ה-brief כבר כאן —       │
                    │      (‏רק עכשיו!)          │        │  ‏כי committed ל-base)    │
                    │                           │        │                          │
‏אליעזר מתחיל        │                           │        │ status: ‏בעבודה           │
                    │                           │        │  commit (‏בworktree)      │
                    │                           │        │                          │
‏אליעזר מסיים        │                           │        │ status: ‏הושלם            │
                    │                           │        │  final commit (‏בworktree)│
                    └──────────────────────────┘        └──────────────────────────┘
                              ▲                                      │
                              └────────── merge (‏מרדכי, ‏אחרי אישור) ◄┘

‏הכלל הקריטי:  commit #1/#2 ‏חייבים לקרות **‏לפני** ‏ה-worktree add,
              ‏אחרת ה-brief לא קיים ב-branch של ה-worktree.
‏הכלל השני:   ‏אליעזר עורך status ‏**‏רק בworktree** — ‏לא ב-main/dev ישירות
              (‏הזליגה שקרתה בslice-3).
```

---

## §4 — Commits ‏בסדר

### Commit 0 — workflow.md: ‏מחזור-החיים של commit ה-brief (approach: none)

**‏קבצים שמשתנים**:
- `workflow.md` — ‏מוסיף תת-סעיף ב-§שלב 2 ‏וב-§שלב 4. ‏לא משנה §שלב 3.

**‏מה להוסיף ב-§שלב 2 (‏אחרי ה-warning של JIT, ‏שורה ~40, ‏לפני §שלב 3):**

```markdown
### ‏Commit ה-brief — ‏מתי ולאיזה branch

‏ה-brief הוא **‏ארטיפקט מ-committed**, ‏לא קובץ זמני. ‏הוא חי ב-base branch
(`main` ‏או `dev` ‏לפי הפרויקט) ‏ונכנס ל-worktree ‏רק בזכות ה-commit הזה.

| ‏מעבר סטטוס | ‏מי מקמט | ‏לאיזה branch | ‏מתי |
|-----------|---------|-------------|------|
| → ‏טיוטה | ‏מרדכי | base (main/dev) | ‏מיד אחרי כתיבה ראשונה |
| ‏טיוטה → ‏מאושר | ‏מרדכי | base (main/dev) | ‏אחרי שאביגיל החזירה READY |
| ‏מאושר → ‏בעבודה | ‏אליעזר | **‏worktree** | ‏כשמתחיל לבצע |
| ‏בעבודה → ‏הושלם | ‏אליעזר | **‏worktree** | ‏ב-commit האחרון של ה-slice |

> [!warning] ‏ה-brief חייב להיות committed ל-base **‏לפני** ‏ה-worktree add
> ‏ב-bare+worktrees, ‏worktree ‏הוא branch ‏נפרד. ‏אם ה-brief לא committed ל-base
> ‏לפני `git worktree add`, ‏אליעזר **‏לא יראה את התוכנית** בworktree. ‏לכן commit
> ה-"מאושר" (‏או לפחות commit ה-"טיוטה") ‏קודם ל-§שלב 4.

> [!warning] ‏אליעזר עורך את ה-brief **‏רק בworktree שלו**
> ‏אחרי שה-worktree נוצר, ‏עדכוני-status (בעבודה/הושלם) ‏ו-§"סטיות" ‏נכתבים
> ‏ב-branch של ה-slice — ‏**‏לא** ‏ב-`main`/`dev` ‏ישירות. ‏עריכה ישירה ב-base
> ‏גורמת לסטטוס "‏הושלם" ‏לזלוג ל-base לפני merge מאושר (‏קרה ב-slice-3).
```

**‏מה להוסיף ב-§שלב 4 (‏בתחילתו, ‏אחרי השורה "‏פירוט מלא ב-worktrees.md"):**

```markdown
> [!info] ‏Precondition: ‏ה-brief committed ל-base
> ‏לפני `git worktree add` — ‏וודא שה-brief (‏לפחות status "‏מאושר") ‏committed
> ל-base branch. ‏אחרת ה-worktree לא יכיל את התוכנית. ‏ראה §שלב 2 → "‏Commit ה-brief".
```

**Verification**:

```bash
grep -n "Commit ה-brief — ‏מתי ולאיזה branch" workflow.md   # ‏סעיף קיים
grep -n "committed ל-base" workflow.md | grep -c "worktree"  # ‏≥1 (‏האזהרות)
grep -c "מאושר" workflow.md                                  # ‏≥1 (‏הטבלה — ‏בלי ** ‏שמכיל RLM)
```

> ‏הערה: ‏הטקסט המוסף מכיל RLM (U+200F) ‏בתוך `**‏לפני**`. ‏אל תכלול `**...**`
> ‏ב-grep patterns — ‏השתמש ב-substring פשוט (`committed ל-base`) ‏שאינו תלוי ב-RLM.

---

### Commit 1 — agents/mordechai.md + EXECUTOR_DISPATCH + BRIEF_TEMPLATE (approach: none)

**‏קבצים שמשתנים**:
- `agents/mordechai.md` — ‏§ערב: ‏מוסיף צעד commit מפורש.
- `briefs/EXECUTOR_DISPATCH.md` — ‏§11: ‏מוסיף "‏עורך brief רק בworktree".
- `briefs/BRIEF_TEMPLATE.md` — ‏front-matter: ‏חידוד מי מקמט status.

**‏ב-`agents/mordechai.md` §ערב — ‏מוסיף צעד 1.5 (‏בין "‏כתוב briefs" ל-"‏הפעל אביגיל"):**

‏הטקסט הקיים (‏שורה 47):
```markdown
1. **‏כתוב briefs** ל-docs/plans/<slice>.md ‏לפי BRIEF_TEMPLATE.md
```
‏הופך ל:
```markdown
1. **‏כתוב briefs** ל-docs/plans/<slice>.md ‏לפי BRIEF_TEMPLATE.md, ‏**‏וקמט** (status: ‏טיוטה) ל-base branch.

   > ‏ה-brief חייב להיות committed ל-base **‏לפני** ‏ה-worktree add — ‏אחרת אליעזר לא יראה אותו.
```

‏ובצעד "‏עדכן state.json" ‏(שורה 62) ‏מוסיפים אחריו ‏(צעד 4.5):
```markdown
4.5 **‏קמט את ה-brief המעודכן** (status: ‏מאושר) ל-base branch — ‏לפני worktree/dispatch.
```

**‏ב-`briefs/EXECUTOR_DISPATCH.md` §11 "‏מה אתה לא עושה" (‏שורות ~247-251):**

‏מוסיפים bullet:
```markdown
- ❌ ‏לא עורך את ה-brief ב-`main`/`dev` ‏ישירות — ‏עדכוני-status ‏ו-§"סטיות" ‏רק בworktree שלך. ‏עריכה ב-base ‏מזליגה "‏הושלם" ‏לפני merge.
```

**‏ב-`briefs/BRIEF_TEMPLATE.md` ‏front-matter (‏שורה 4):**

‏הטקסט הקיים:
```markdown
> **‏סטטוס**: ‏טיוטה / ‏מאושר / ‏בעבודה / ‏הושלם
```
‏הופך ל:
```markdown
> **‏סטטוס**: ‏טיוטה / ‏מאושר / ‏בעבודה / ‏הושלם
> ‏  (‏מרדכי מקמט: ‏טיוטה→מאושר ל-base. ‏אליעזר מקמט: ‏בעבודה→הושלם ‏בworktree. ‏ראה workflow.md §שלב 2.)
```

**Verification**:

```bash
# ‏patterns ‏נקיים — ‏בלי ** ‏ובלי גבול-RLM:
grep -n "וקמט" agents/mordechai.md
grep -n "קמט את ה-brief המעודכן" agents/mordechai.md
grep -n "לא עורך את ה-brief ב-" briefs/EXECUTOR_DISPATCH.md
grep -n "מרדכי מקמט" briefs/BRIEF_TEMPLATE.md
```

---

### Commit 2 — decisions entry + walkthrough (approach: none)

**‏קבצים שמשתנים**:
- `docs/decisions/bds.md` — ‏entry חדש (‏מרדכי כותב רציונל).
- `docs/walkthrough.md` — ‏entry ביצוע (‏אליעזר, ‏לפי skill `update-walkthrough`).

**‏ב-`docs/decisions/bds.md` — ‏entry חדש בראש (‏אחרי הכותרת):**

```markdown
## 2026-06-03 — slice-4-brief-commit-lifecycle: ‏מחזור-חיים של commit ה-brief

### ‏רציונל
‏ה-workflow לא תיעד מתי מקמטים את ה-brief. ‏ב-bare+worktrees זה לא קוסמטי:
‏worktree ‏הוא branch ‏נפרד, ‏ואם ה-brief לא committed ל-base לפני `git worktree add`,
‏אליעזר לא רואה את התוכנית. ‏תיעדנו טבלת מעברי-סטטוס (‏מי מקמט, ‏לאיזה branch, ‏מתי)
‏+ ‏שתי אזהרות: (1) commit לפני worktree, (2) אליעזר עורך רק בworktree.

### ‏ממצאי אביגיל
<‏תמצית — ‏ימולא אחרי הרצת אביגיל>

### ‏שינויי-כיוון
<‏אם היו — ‏ימולא>

### ‏רעיונות שנדחו
- **‏אכיפה אוטומטית** (pre-commit ‏שבודק brief committed): ‏over-engineering ל-docs.
  ‏ההגנה היא תיעוד + ‏משמעת, ‏לא hook.
```

**Verification**:

```bash
grep -n "slice-4-brief-commit-lifecycle" docs/decisions/bds.md
grep -n "slice-4" docs/walkthrough.md
```

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
> **‏כלל-זהב ל-grep ב-DoD הזה**: ‏אל תכלול `**...**` (markdown bold) ‏ב-pattern —
> ‏הטקסט המוסף מכיל RLM (U+200F) ‏בין `**` ‏למילה, ‏ו-grep ‏פשוט לא יתפוס.
> ‏השתמש ב-substring "‏נקי" (‏בלי `*`, ‏בלי גבול-RLM). ‏כל ה-patterns למטה ‏כבר ‏נקיים.

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | ‏workflow §שלב 2 ‏מכיל סעיף "‏Commit ה-brief" ‏עם טבלת 4 מעברים | `grep -n "Commit ה-brief — ‏מתי ולאיזה branch" workflow.md` |
| 2 | ‏workflow ‏מכיל אזהרת "‏committed ל-base לפני worktree" | `grep -n "committed ל-base" workflow.md \| grep worktree` |
| 3 | ‏workflow ‏מכיל אזהרת "‏אליעזר עורך רק בworktree" | `grep -n "רק בworktree שלו" workflow.md` |
| 4 | ‏workflow §שלב 4 ‏מכיל precondition info-block | `grep -n "Precondition: ‏ה-brief committed" workflow.md` |
| 5 | `agents/mordechai.md` §ערב צעד 1 ‏כולל "‏וקמט" | `grep -n "וקמט" agents/mordechai.md` |
| 6 | `agents/mordechai.md` ‏כולל צעד "‏קמט brief מעודכן (מאושר)" | `grep -n "קמט את ה-brief המעודכן" agents/mordechai.md` |
| 7 | `EXECUTOR_DISPATCH.md` §11 ‏כולל "‏לא עורך brief ב-main/dev" | `grep -n "לא עורך את ה-brief ב-" briefs/EXECUTOR_DISPATCH.md` |
| 8 | `BRIEF_TEMPLATE.md` front-matter ‏מבהיר מי מקמט status | `grep -n "מרדכי מקמט" briefs/BRIEF_TEMPLATE.md` |
| 9 | decisions entry קיים | `grep -n "slice-4-brief-commit-lifecycle" docs/decisions/bds.md` |
| 10 | ‏טסטים קיימים לא נשברו (‏רגרסיה) | `python3 -m pytest tests/ -q` → ‏ירוק |
| 11 | ‏אין קישורים שבורים שהוספנו | ‏קריאה ידנית — ‏כל הפניה ל-§ ‏מצביעה על סעיף קיים |

---

## §6 — Risks + mitigations

| ‏סיכון | ‏מקור | ‏מיטיגציה |
|------|------|----------|
| ‏עריכה משנה line numbers שמסמכים אחרים מצטטים | ‏ניסיון פנימי | ‏ה-slice לא מוחק תוכן, ‏רק מוסיף; ‏מסמכים מצטטים §-כותרות לא שורות. ‏אם הוספה מזיזה — ‏בדוק grep references |
| ‏RTL/עברית בקוד-בלוקים של grep ‏ב-DoD לא תואם בפועל | ‏עברית + RLM (U+200F) ‏ב-grep patterns | **‏טופל**: ‏כל ה-patterns ב-§5 ‏נוקו מ-`**...**` (‏RLM מסתתר אחרי `**`). ‏כלל-זהב מתועד בראש §5: ‏substring נקי, ‏בלי markdown-bold. ‏fallback: ‏אם בכל-זאת 0 — ‏substring קצר יותר |
| ‏סטייה מ-"docs only" — ‏פיתוי לתקן staleness ב-§שלב 3 | scope creep | ‏§2 ‏אוסר במפורש. ‏staleness ‏מתועד ב-§9 כ-slice עתידי |
| ‏זליגת-עריכה ל-main (‏האירוני — ‏על slice שמתעד בדיוק את זה) | handoff slice-3 | ‏אליעזר עובד **‏רק** ‏ב-`.worktrees/slice-4-.../`, ‏לא ב-`main/` |

> ‏3 ‏שתמיד נשכחים: (1) Hardcoded strings — ‏לא רלוונטי (docs). (2) Reactivity — ‏לא רלוונטי. (3) OneCLI — ‏לא רלוונטי.

---

## §7 — Escalation triggers

> ‏אם X — ‏עצור ושאל את מרדכי:

- ‏מצאת שהוספת תוכן **‏סותר** ‏סעיף קיים (‏לא רק מוסיף) — ‏עצור, ‏זה מעיד על אי-הבנה.
- ‏ה-grep ב-DoD ‏מחזיר 0 ‏גם אחרי שניסית substring קצר — ‏יתכן שלא הוספת נכון.
- ‏גילית ש-`docs/decisions/bds.md` ‏או `docs/walkthrough.md` ‏לא קיימים — ‏צור (‏אל תניח מבנה).
- ‏ה-staleness ב-§שלב 3 (Tama/general/plan-verifier.md) ‏נראה לך שחייב תיקון עכשיו — ‏לא בסקופ, ‏שאל.
- ‏Brief סותר את עצמו או את הקוד הקיים.

---

## §8 — Complexity score + verifier tier

| ‏פרמטר | ‏ניקוד |
|------|------|
| Pure docs, ‏אין IO, ‏אין קוד | -2 |
| Greenfield (‏סעיפים חדשים, ‏אין call sites) | -1 |
| >5 files ‏ב->2 packages | 0 (‏4 ‏קבצים, ‏package אחד) |
| Refactor של קוד קיים | 0 (‏אין) |
| ‏base value | +5 (‏נקודת מוצא) |

**Score**: 2 / 10

**Tier**: 0-3 → `verifier-slice-light` ‏בלבד (‏calev, mode: light).

**‏Verifier-phase ‏אחרי commit/phase**: ‏אין — ‏slice docs קצר, ‏light בסוף מספיק.

---

## §9 — ‏שאלות פתוחות

| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ‏האם לתקן באותו slice את ה-staleness ב-workflow §שלב 3 (Tama→מרדכי, `subagent_type:"general"`→avigail, ‏הפניה ל-`agents/plan-verifier.md` ‏שלא קיים — ‏השם הנכון `avigail.md`)? | ‏לא — ‏slice נפרד. ‏מתעד פה כדי לא לשכוח. | ❌ |
| 2 | ‏האם ה-base אמור להיקרא "‏base" ‏גנרי או "main" ‏ספציפי בתיעוד? | ‏גנרי "base (main/dev)" — ‏כי השיטה משרתת גם פרויקטים עם dev. | ❌ |
| 3 | ‏האם להוסיף את הצעד גם ל-`SKILL.md` (‏הצינור TL;DR)? | ‏לא בסקופ — ‏ה-SKILL מתאר זרימה, ‏לא מחזור-commit. ‏אזכור עתידי. | ❌ |

---

## ‏סטיות מהתכנון (‏מתעדכן ע"י executor ‏תוך כדי)

> ‏ה-executor מתעד פה כל סטייה ‏מה-brief ‏ולמה.

- ...
