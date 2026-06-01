# Workflow — ‏הפרוטוקול end-to-end

‏מתאר את כל הצינור משלב התכנון ועד merge ‏ל-dev.

## ‏שלב 1: ‏החלטה — ‏האם זה slice ‏בכלל?

‏לפני שכותבים brief, ‏שאל את עצמך:

- ‏האם יש DoD ‏ברור שאפשר לאמת בסוף?
- ‏האם ההיקף בין 100-500 ‏שורות שינוי?
- ‏האם זה דורש יותר מ-1-2 ‏commits?

‏אם **‏כן** ‏לכל ה-3 — ‏זה slice. ‏המשך.
‏אם **‏לא** ‏ל-1+ — ‏עבוד ישירות, ‏בלי brief.

‏אם ה-feature ‏גדול מ-500 ‏שורות / ‏5+ commits — ‏פצל ל-2 slices ‏וכתוב brief לכל אחד.

## ‏שלב 2: ‏Planning — ‏Tama כותב brief

‏ב-`docs/plans/<slice-name>.md`. ‏הבסיס הוא [`briefs/BRIEF_TEMPLATE.md`](briefs/BRIEF_TEMPLATE.md), ‏שמבוסס על `docs/plans/README.md` ‏שהתפתח ב-voice-acp.

‏סעיפים חובה ב-brief:

| § | ‏סעיף | ‏למה |
|---|------|------|
| 0 | Pre-flight | ‏worktree, ports, ‏איך להריץ, ‏reading list ‏עם priority |
| 1 | ‏מטרה | ‏פסקה אחת מנקודת מבט המשתמשת |
| 2 | Scope (‏מה כן, ‏מה לא) | ‏הגנה מ-scope creep |
| 3 | Architecture diagram | ASCII, ‏מסמן ‏מה חדש איפה |
| 4 | Commits בסדר | ‏לכל אחד: ‏שם, ‏approach (tdd/integration/manual/none), ‏קבצים, API skeleton, verification commands |
| 5 | DoD verifiable | ‏טבלת checkboxes ‏עם פקודה לכל אחד |
| 6 | Risks + mitigations | ‏מ-`learnings.md` ‏ומ-walkthroughs קודמים |
| 7 | Escalation triggers | ‏מתי לעצור ולשאול את Tama |
| 8 | Complexity score + tier | ‏לפי `recommendations.md` §8 — ‏קובע light/heavy |
| 9 | ‏שאלות פתוחות | ‏עם default ‏ו"‏חוסם?" |

‏זמן ממוצע לכתיבת brief: ~‏30-45 ‏דק' ‏ל-slice ‏בינוני.

> [!warning] JIT, ‏לא upfront
> ‏אל תכתוב 9 ‏briefs ‏מראש. ‏כתוב 2-3, ‏dispatch, ‏ראה ‏מה הvellrier ‏מצא, ‏עדכן את ההמלצות, ‏ואז כתוב את הבאים.

## ‏שלב 3: ‏Plan verification — ‏לפני handoff

**‏זה חובה. ‏לדלג עליו זה לעלות בממוצע 30-60 ‏דק' ‏debug ‏באג'נטים בסיסיים.**

‏מ-3 plan verifiers שרצו ב-voice-acp:
- ‏מצאו ‏9 ‏בעיות ב-3 briefs (avg 3/brief)
- 100% ‏מהbריפים היו בעיה ‏פוטנציאלית
- ‏עלות ‏~‏10 ‏דק' פר verifier round

‏איך מפעילים:

```ts
Task({
  subagent_type: "general",   // ‏או "plan-verifier" ‏אם הוגדר ‏ב-OpenCode
  description: "Verify <slice> plan",
  prompt: `‏אתה plan-verifier. ‏קרא את ה-brief ‏ב-docs/plans/<slice>.md ‏ובדוק:

1. **‏כל symbol/API ‏ש-brief טוען שקיים — ‏אמת ב-dev tip ‏בפועל** (grep, ‏file:line).
2. ‏Pseudo-code — ‏וודא שלא מחסיר branches קיימים ‏(typeof === "string", etc.)
3. ‏Line numbers — ‏אמת שהם נכונים ב-version הנוכחי.
4. ‏Type errors צפויים (‏noUncheckedIndexedAccess, ‏וכו') — ‏סמן.
5. ‏Naming inconsistency פנימי ‏ב-brief.
6. ‏File paths שהbrief טוען שקיימים — ‏אמת.
7. ‏Risks/escalations מיושנים — ‏סמן.

‏החזר דוח: ‏רשימת ‏בעיות מסווגות (🔴 blocker / 🟡 confusion / 🟢 minor), 
‏עם file:line ‏ספציפי, ‏ו-verdict: ✅ READY / 🟡 USABLE-AFTER-FIX / ❌ NEEDS-REWORK.`
})
```

‏אם הוגדר ‏סוכן ‏`plan-verifier` ‏מותאם — ‏עדיף ‏(קובץ ‏[`agents/plan-verifier.md`](agents/plan-verifier.md)).

‏Tama ‏מתקן לפי הדוח (~‏15-20 ‏דק' ‏בממוצע), ‏ועובר ל-handoff.

## ‏שלב 4: ‏Worktree setup

‏פירוט מלא ב-[`worktrees.md`](worktrees.md). ‏TL;DR:

```bash
cd <project-root>
git worktree add .worktrees/<slice-name> -b <slice-name> <base-branch>
cd .worktrees/<slice-name>
<package-manager> install
<package-manager> hooks:install   # ‏אם פרויקט עם pre-commit hooks
```

## ‏שלב 5: Execution — ‏executor ‏מבצע

### ‏אופציה A: ‏Executor ‏כ-sub-agent (‏Opus orchestrator)

‏Tama ‏מ-dispatched:

```ts
Task({
  subagent_type: "executor",
  description: "Execute <slice>",
  prompt: `‏בצע docs/plans/<slice>.md.
Pre-conditions ‏ב-docs/plans/EXECUTOR_DISPATCH.md (‏פר-פרויקט).
Base: <dev tip hash>
<port convention, tunnel notes, OneCLI agent ‏אם רלוונטי>
Verifier: light (‏או heavy ‏לפי brief)`
})
```

‏Tama ‏ממתינה לדוח, ‏אז dispatched verifier.

### ‏אופציה B: Executor ‏הוא ה-build agent (‏המשתמשת dispatched ‏ישירות)

‏המשתמשת פותחת סשן חדש ‏ושולחת: "‏בצע docs/plans/<slice>.md".

> [!warning] ‏Sonnet ‏לפעמים מבלבל ‏ב-delegate
> ‏אם build agent ‏הוא Sonnet ‏והוא מקבל "‏בצע X" — ‏הוא לפעמים חושב שהוא ה-planner ‏ומ-delegated ל-executor sub-agent. ‏ה-EXECUTOR_DISPATCH §0 ‏אומר במפורש: **"‏אתה ה-executor, ‏אל ‏תdelegate"**.

### ‏Testing strategy פר commit (‏המפתח להצלחה)

‏ה-brief ‏מציין לכל commit אחד מ-4:

| approach | ‏מתי | ‏מה executor עושה |
|----------|------|--------------------|
| `tdd` | Logic, schema, state machine | Red-Green-Refactor |
| `integration` | Wiring, refactor | ‏קוד קודם, ‏אז integration test ‏באותו commit |
| `manual` | UI, CSS, UX | ‏בדיקה ידנית ב-browser/curl, ‏תיעוד ב-commit msg |
| `none` | docs, config, rename | ‏רק typecheck + lint |

**‏executor חייב לכבד את הבחירה.** ‏סטיה = Escalation.

### ‏Phase verifier (אופציונלי)

‏אחרי commits high-risk שה-brief סימן — ‏executor ‏מ-dispatched verifier-phase:

```ts
Task({
  subagent_type: "verifier-phase",
  prompt: `Phase X ‏הושלם. Brief: docs/plans/<slice>.md. Commit: <hash>.
‏סביבה: BE על port X, ‏browser linux-gui ‏או pw-clean.sh.
‏בדוק רק את Phase X (‏לא ‏phases ‏הבאים).`
})
```

‏שווה רק לcommits ‏עם:
- Cross-store data flow חדש
- State machine ‏עם אפשרות ל-infinite loop
- Wiring שכמה sub-agents יעבדו עליו

‏אם plan verifier ‏איכותי, ‏phase verifier ‏בד"כ ‏רק אישור פורמלי.

## ‏שלב 6: Slice verifier (‏סוף slice)

**‏חובה. ‏גם אם executor אמר ‏"הכל ירוק".**

‏ה-brief ‏מציין tier:

```ts
Task({
  subagent_type: "verifier-slice-light",  // ‏או heavy
  description: "Verify <slice>",
  prompt: `‏Slice <slice> ‏הושלם.
Brief: docs/plans/<slice>.md
Base commit: <hash>
Commits: git log <base>..HEAD
‏סביבה: <ports, browser, fixtures>

‏עבור על כל ה-DoD items, ‏רוץ happy path אחד-שניים, ‏כתוב report ‏ב-docs/<slice>-verification-report.md.`
})
```

‏Light: ~‏15-25 ‏דק', happy path, DoD walk.
‏Heavy: ~‏30-50 ‏דק', edge cases, regressions, ‏side flows.

‏פירוט הקריטריונים ב-[`recommendations.md`](recommendations.md) §7-8.

## חוזה ה-Task-result — אינדקס בלבד

המאמת (אביגיל/כלב) כותב דוח מלא → מחזיר אינדקס → הצרכן פותח את הדוח.

```
מאמת              Task-result (אינדקס)        דוח מלא
┌──────────┐ ──── verdict+report+כותרות ───► מרדכי/אליעזר
│ אביגיל / │                                    │
│  כלב     │ ──── front-matter+גוף MD ──────► reports/<project>/<slice>-*.md
└──────────┘                                    │
                                    חייבים לפתוח לכל החלטה על finding
```

> **כלל**: ניתוח ב-Task-result = תקלה. ה-result הוא אינדקס, הבשר בדוח.
> פירוט: `docs/reports-format.md` §"חוזה ה-Task-result (משמעת-דוחות)".

## שני gates — אימות-נקי כתנאי

> **plan-gate**: לפני dispatch (§שלב 2 → §שלב 4)
> **runtime-gate**: לפני merge (§שלב 6 → §שלב 7)

### plan-gate — dispatch רק על READY

| מצב אביגיל | פעולה |
|-----------|-------|
| ✅ READY | status=plan-verified → dispatch |
| 🟡 USABLE-AFTER-FIX | **תיקון + אביגיל שוב** (לא dispatch עד READY) |
| ❌ NEEDS-REWORK | rewrite + אביגיל שוב |

> plan-verified = מרדכי קיבל READY מאביגיל. לא פחות.

### runtime-gate — merge רק על GO

| מצב כלב | פעולה |
|---------|-------|
| ✅ GO | אפשר למזג (אחרי אישור משתמשת) |
| ⚠️ PARTIAL | (א) סבב fix + כלב שוב עד GO, **או** (ב) דחייה מפורשת (תיעוד+אישור) |
| ❌ NO-GO | חובה: סבב fix + כלב שוב, **או** דחייה מפורשת |

> merge על PARTIAL/NO-GO ללא תיעוד ואישור = חוב שקט. **אסור**.
>
> **פירוט מלא**: `agents/mordechai.md` §"שני gates".

---

## ‏שלב 7: ‏Merge ל-dev (‏רק אחרי אישור המשתמשת)

> [!warning] ‏Tama ‏לא ‏עושה merge על דעת עצמה
> ‏Slice ‏שעבר verifier-slice ‏עם GO ‏הוא **‏מוכן ל-merge**, ‏אבל ‏ההחלטה ‏היא של המשתמשת:
>
> - ‏האם להמתין ל-slices ‏נוספים שירוצו במקביל?
> - ‏האם יש שאלות פתוחות שדורשות החלטה לפני merge?
> - ‏האם הסטיות שה-executor תיעד מקובלות?
>
> **‏Tama מציגה את הסיכום ‏ושואלת.** ‏המשתמשת מאשרת → merge.

‏זרימה אחרי אישור:

```bash
cd <project-root>/dev   # ‏או main worktree
git merge --no-ff <slice-name>
# ‏אם יש conflict ב-walkthrough.md / slices.md — ‏פתור ידנית
<package-manager> test
# ‏אם passes — ‏commit ה-merge (‏לפי הסקיל `commit`)
```

‏אם 2+ slices ‏רצו במקביל ‏עם BE_PORT שונה — ‏merge ‏את ה-second ‏בנפרד, ‏פתור conflicts בקבצים משותפים (‏ה-`additive design` ‏ב-`docs/conventions/parallel-safe-code.md`).

### ‏Cleanup worktree (‏רק אחרי שה-merge ‏מאומת)

‏אחרי שה-merge עבר בהצלחה ‏וtests עוברים על dev:

```bash
git worktree remove .worktrees/<slice-name>
git branch -d <slice-name>
```

> [!info] ‏מתי **‏לא** ‏למחוק worktree
>
> - ‏אם המשתמשת רוצה לבדוק ידנית עוד — ‏השאר עד שאישרה
> - ‏אם יש WIP ‏לא-committed (`git status` ‏לא נקי) — ‏שאל לפני `--force`
> - ‏אם זה worktree של slice ‏שטרם הושלם — ‏ברור שלא
> - ‏אם branch לא נמרג ל-dev עוד — ‏אזהרה: ‏אם מוחקים branch ‏לפני merge, ‏הקוד אובד

## ‏וריאציה: Batch dispatch — ‏מספר slices ‏ברצף

‏לפעמים יש 2-3 slices ‏שתלויים זה בזה: ‏slice A יוצר foundation, slice B ‏בונה מעליו, ‏slice C ‏מנקה. ‏אין טעם לפצל ל-3 ‏dispatches נפרדים, ‏Tama ‏מעבירה את כולם ב-batch ‏ל-executor אחד.

### ‏מאפיינים של batch

- ‏**‏אותו worktree** ‏ל-batch כולו (`.worktrees/<batch-name>/`)
- ‏**‏אותו branch** (‏slice ‏הראשון יוצר, ‏השני ‏ממשיך עליו)
- ‏**Verifier-slice ‏חובה לכל slice** ‏בנפרד (‏לא רק לאחרון!)
- ‏**Merge ‏אחד בסוף** (‏אם המשתמשת מאשרת) — ‏לא בין slices
- ‏**Plan verifier על כל אחד** ‏לפני dispatching

### ‏מתי batch ‏נכון

✅ ‏Slices ‏רצופים שhPLAN ‏שלהם תלוי בקודמים (‏A → B → C)
✅ ‏מאמץ קטן יחסית ‏(כל slice 100-200 ‏שורות; ‏batch ‏כולל לא יותר מ-3-4 slices)
✅ ‏Slices ‏מאותו תחום ‏(אותו module, ‏אותו feature area)

❌ ‏Slices ‏עצמאיים — ‏עדיף parallel dispatch ‏ב-worktrees נפרדים (‏ראה [`worktrees.md`](worktrees.md))
❌ ‏Slices ‏גדולים מאוד — ‏סשן executor ‏יתארך מדי, ‏אבד פוקוס
❌ ‏Slices ‏בתחומים שונים — ‏קשה לhmerge, ‏קשה לתאם conflict

### ‏Dispatch לbatch

```ts
Task({
  subagent_type: "executor",
  description: "Execute batch: slices A → B → C",
  prompt: `‏בצע את ה-slices האלה בסדר:
1. docs/plans/slice-A.md
2. docs/plans/slice-B.md  (‏על גבי slice A)
3. docs/plans/slice-C.md  (‏על גבי slice B)

Worktree: .worktrees/<batch-name>/
Base: <dev tip hash>
‏סביבה: <ports, browser, OneCLI agent>

‏לכל slice:
- ‏בצע commits ‏לפי ה-brief שלו
- ‏הפעל verifier-slice (tier ‏מהbrief) ‏בסופו
- ‏אם verifier ‏אישר ✅ — ‏המשך ל-slice ‏הבא
- ‏אם verifier ‏סירב ❌ — ‏STOP, ‏דווח לTama עם הreport

‏אחרי כל ה-slices — ‏דווח: "Batch done. <N> slices. Reports: ...".
‏Tama תחליט על merge.`
})
```

### ‏מה Executor עושה בין slices ‏ב-batch

1. ‏Verifier-slice ‏לסוף slice N → ‏אם GO:
2. ‏עדכן walkthrough ‏עם entry סופי לslice N (‏לפי `update-walkthrough` skill)
3. Final commit לslice N (‏סטטוסים, ‏summary)
4. ‏אם יש slice N+1 ב-batch — ‏המשך אליו ‏(‏אותו worktree, ‏אותו branch)
5. ‏אם זה ה-slice ‏האחרון — ‏STOP ‏ודווח לTama

‏לא לעשות `git worktree remove` ‏בין slices. ‏לא למחוק branch. ‏רק להמשיך לעבוד.

### ‏Escalation ‏באמצע batch

‏אם slice באמצע נכשל ‏(verifier ❌, ‏או executor נתקע):
- ‏STOP ‏את ה-batch מיד
- ‏אל תנסה את slice הבא
- ‏דווח לTama: ‏איזה slice נכשל, ‏איזה report, ‏האם slices קודמים עברו בהצלחה
- Tama תחליט: ‏לתקן ולהמשיך, ‏לפצל את ה-batch, ‏לבטל את כולו, ‏או לעשות merge חלקי

### ‏Merge ‏אחרי batch

‏בד"כ ‏merge אחד ל-dev (‏כל ה-batch), ‏אבל המשתמשת יכולה להחליט גם:
- ‏merge slices A+B, ‏ולהשאיר C בbranch ‏לבדיקה נוספת
- merge ‏אחד אחד עם cherry-pick (‏אם יש סיבה)

‏הdefault: ‏one merge for the batch.

---

## ‏שלב 8: ‏עדכון learnings + ‏case study (‏אם רלוונטי)

‏אם התגלה משהו חדש — ‏gotcha, ‏failure mode, ‏או pattern:

1. ‏הוסף שורה ל-`~/.config/opencode/learnings.md` ‏(global) ‏או ל-project's `docs/learnings.md`.
2. ‏אם זו קטגוריית כשל חדשה — ‏עדכן `patterns.md`.
3. ‏אם זה שינוי לתבנית — ‏עדכן `recommendations.md`.
4. ‏אם זה case study שלם — ‏צור קובץ ב-`case-studies/`.

## ‏Anti-patterns ל-Tama עצמה

- ❌ ‏לכתוב brief בלי plan-verifier ‏(100% chance ‏של ‏באג בbrief)
- ❌ ‏לכתוב brief מ-500+ ‏שורות (‏Sonnet ‏מאבד פוקוס; ‏עדיף 200-300)
- ❌ ‏לדלג על verifier-slice ‏כי "‏היה plan verifier וphase verifiers"
- ❌ ‏לעשות merge ‏לפני שbreafier ‏עבר
- ❌ ‏לכתוב 9 ‏briefs ‏מראש לפני dispatching — JIT > upfront
- ❌ ‏לbiasing את verifier-prompt ‏עם "‏בדוק שX עובד" (‏הסתרת באג אפשרי). ‏פשוט "‏אמת DoD ‏מול brief".
