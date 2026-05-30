---
name: brief-driven-slices
description: |
  Brief-driven slice workflow — שיטת עבודה לפרויקטי קוד שמחלקת התקדמות
  ל-slices קטנים, כל אחד עם brief מפורט שכותב מרדכי (planner/Opus), מאומת
  לפני handoff ע"י אביגיל (plan-verifier), מבוצע ע"י אליעזר (executor) ב-worktree
  ייעודי, ומאומת בסוף ע"י כלב (runtime-verifier). יתרו מריץ queue לילי אוטומטי.
  מנגנון worktrees מאפשר שרשור slices תלויים ללא merge ל-dev עד הבוקר.

  השיטה התפתחה אחרי שניסיון של "TDD עם Sonnet אוטונומי" כשל ב-Slice 9
  של voice-acp (114 טסטים ירוקים, 19 באגים בפועל). הצורה הנוכחית הוכיחה
  את עצמה ב-5 slices רצופים ב-voice-acp (28-29/5/2026) — אפס באגים ב-verification.

  טען את הסקיל כשמתכננים סבב פיתוח חדש, כשכותבים brief ל-אליעזר,
  כשמדispatching ל-sub-agent מבצע, או כשמעדכנים template/recommendations.

  Triggers:
  - "אני רוצה לתכנן slice", "בוא נכתוב brief", "תכין תוכנית לסבב"
  - "נדispatch ל-executor", "תפעיל verifier", "הפעל plan-verifier"
  - "תכין worktree לפי הקונבנציה", "פתח worktree לסליס"
  - "תעדכן את ה-patterns אחרי הסליס", "case study חדש"
  - "Opus מתכנן Sonnet מבצע", "planner-executor", "Tama"
  - "מרדכי", "יתרו", "אליעזר", "אביגיל", "כלב"
  - "queue לילי", "orchestration", "שרשור worktrees"

  Anti-triggers (אל תטען):
  - שאלות one-off על git worktrees ללא slice
  - debug של בעיה ספציפית שלא חלק מ-slice
---

# Brief-Driven Slices

‏שיטת עבודה ל-slices ‏מודרכי-brief, ‏עם הפרדה ברורה בין תפקידי מרדכי/אביגיל/אליעזר/כלב/יתרו, ‏ומנגנון worktrees ‏לעבודה מקבילה ‏ולשרשור לילי.

## ‏הצוות (5 ‏סוכנים)

| ‏שם | ‏תפקיד | ‏Mode | ‏מודל | merge? |
|-----|-------|-------|------|--------|
| **‏מרדכי** | planner | primary | Opus 4.8 | ✅ ‏אחרי אישור |
| **‏יתרו** | orchestrator | primary | Sonnet 4.6 | ❌ ‏לעולם לא |
| **‏אליעזר** | executor | all | Sonnet 4.6 | ❌ ‏לעולם לא |
| **‏אביגיל** | plan-verifier | subagent | Opus 4.8 | ❌ |
| **‏כלב** | runtime-verifier (phase/light) | subagent | Sonnet 4.6 | ❌ |
| **‏כלב-heavy** | runtime-verifier (heavy, complexity 8+) | subagent | Opus 4.8 | ❌ |

> **‏עיקרון המודלים**: ‏Opus למקום שהאמת מגיעה מ**‏הסקה** (מרדכי תכנון, ‏אביגיל
> ‏על brief סטטי, ‏כלב-heavy על edge-cases/regressions/patterns). ‏Sonnet למקום
> ‏שהאמת מגיעה מ**‏הרצה** (אליעזר ביצוע, ‏יתרו מכני, ‏כלב phase/light — runtime).

‏להתקנת symlinks: `bash ~/projects/brief-driven-slices/main/scripts/install-agents.sh`

## ‏שלושת מצבי ‏ההפעלה

### Mode 1 — ‏סינכרוני (‏מרדכי → ‏אליעזר ישיר)

```
‏המשתמשת → ‏מרדכי: "‏בצע slice X"
‏מרדכי → Task(subagent_type="eliezer", ...)   [‏חוסם]
‏אליעזר מבצע, ‏מפעיל כלב, ‏מחזיר
‏מרדכי מציג → ‏המשתמשת מאשרת → ‏מרדכי עושה merge
```

### Mode 2 — ‏לילי (‏יתרו)

```
‏ערב:   ‏מרדכי + ‏אביגיל → briefs מאומתים → state.json
‏לילה:  ‏יתרו מריץ queue → tmux → אליעזר → כלב → ‏ארכב
‏בוקר:  ‏מרדכי קורא summary → ‏מחליט → merge
```

### Mode 3 — ‏ישיר (‏משתמשת → ‏אליעזר)

```
‏המשתמשת → session אליעזר: "‏בצע slice X"
```

## ‏הצינור (TL;DR)

```
‏מרדכי (Opus, planner)
  ↓ ‏כותב brief ב-docs/plans/<slice>.md
  ↓
‏אביגיל (plan-verifier, Opus, sub-agent)
  ↓ ‏בודק את ה-brief מול הקוד בפועל. ‏כולל depends_on חובה.
  ↓ ‏מרדכי מתקן
  ↓
‏worktree חדש (`.worktrees/<slice>/`) — ‏base: dev ‏או branch תלות
  ↓
‏אליעזר (executor, Sonnet, all-mode)
  ↓ ‏מבצע phase-by-phase לפי testing strategy פר commit
  ↓ ‏heartbeat אחרי כל commit (ב-Mode 2)
  ↓ ‏(אופציונלי) כלב (mode: phase) ‏אחרי commit מסוכן
  ↓
‏כלב (runtime-verifier, Sonnet, mode: light) ‏או כלב-heavy (Opus, complexity 8+)
  ↓ ‏בודק DoD ‏מול הקוד בסביבה אמיתית. ‏כותב report.
  ↓
‏מרדכי ‏מוודא, ‏עושה merge ‏ל-dev, ‏מוחק worktree.
```

## ‏מפת הקבצים

| ‏קובץ | ‏מתי לקרוא |
|------|------------|
| [`orchestration.md`](orchestration.md) | ‏Mode 2 — ‏יתרו, state machine, ‏שרשור, BLOCKED |
| [`workflow.md`](workflow.md) | ‏לפני התחלת slice ‏חדש — ‏הפרוטוקול המלא |
| [`worktrees.md`](worktrees.md) | ‏כשמכינים worktree, ‏או שני executors במקביל |
| [`patterns.md`](patterns.md) | 5 ‏קטגוריות הכשל שזוהו ב-Slice 9 — ‏רקע לwhy |
| [`recommendations.md`](recommendations.md) | 10 ‏סעיפים ל-template ‏וההגנות |
| [`briefs/BRIEF_TEMPLATE.md`](briefs/BRIEF_TEMPLATE.md) | ‏Skeleton ‏ל-brief ‏חדש |
| [`briefs/EXECUTOR_DISPATCH.md`](briefs/EXECUTOR_DISPATCH.md) | Boilerplate ‏ל-dispatch ‏ל-אליעזר (‏פר-פרויקט) |
| [`briefs/state.template.json`](briefs/state.template.json) | ‏Template ‏ל-state.json ‏פר-פרויקט |
| [`orchestration-project/`](orchestration-project/) | ‏Template ‏לפרויקט הבית של יתרו |

## ‏הסוכנים (sub-agents ‏ב-OpenCode)

‏מקושרים ‏סמלית ל-`~/.config/opencode/agents/` ‏דרך `install-agents.sh`. ‏ב-`agents/`:

| ‏סוכן | ‏מתי |
|------|------|
| [`agents/mordechai.md`](agents/mordechai.md) | ‏session ‏תכנון — ‏כותב briefs, ‏ממזג, ‏מחליט |
| [`agents/yetro.md`](agents/yetro.md) | ‏session ‏לילי — ‏מריץ queue אוטומטית |
| [`agents/eliezer.md`](agents/eliezer.md) | **‏מבצע** (all mode — Task ‏או primary) |
| [`agents/avigail.md`](agents/avigail.md) | **‏חובה לפני handoff** — ‏בודקת brief + depends_on |
| [`agents/calev.md`](agents/calev.md) | **‏חובה בסוף** — mode: phase/light (Sonnet) |
| [`agents/calev-heavy.md`](agents/calev-heavy.md) | heavy tier (complexity 8+, Opus) |

## ‏שלוש תובנות ‏ליבה

‏מ-`case-studies/2026-05-voice-acp-slices.md`:

1. **‏אביגיל הוא חובה, ‏לא nice-to-have.** ‏ב-100% ‏מ-3 ‏ה-briefs שנבדקו ‏נמצאה לפחות בעיה אמיתית, ‏בממוצע 3 ‏לbrief. ‏עלות 10 ‏דק', ‏חיסכון 30-60 ‏דק' ‏debug ‏+ ‏מנע regression שקט.

2. **‏הזזת האחריות מ-Sonnet ל-מרדכי.** ‏בעבר Sonnet בחר לבד מה לטסט. ‏היום ‏מרדכי ‏קובע פר-commit: `tdd` / `integration` / `manual` / `none`. ‏אליעזר מכבד את הבחירה.

3. **JIT briefs > upfront briefs.** ‏לכתוב 2-3 ‏briefs ‏לפני dispatch, ‏לא 9 ‏מראש. ‏כל גל לומד מהקודם.

## ‏מתי **‏לא** ‏להשתמש בשיטה

- ‏Fix של bug קטן (פחות מ-50 ‏שורות שינוי) — ‏עבודה ישירה ‏ב-main session
- ‏Exploratory spike — ‏אין DoD ‏ברור, ‏אין מה לאמת
- ‏Hotfix דחוף — ‏overhead של brief + verifier ‏לא משתלם
- ‏פרויקט בלי git ‏או בלי package manager — ‏worktree convention לא רלוונטי

## ‏אם case study חדש מוסיף תובנה

‏עדכן את `patterns.md` ‏אם זו קטגוריית כשל חדשה, ‏את `recommendations.md` ‏אם זה שינוי לתבנית, ‏וצור קובץ ב-`case-studies/` ‏עם הראיות.
