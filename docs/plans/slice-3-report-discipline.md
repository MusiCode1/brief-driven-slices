# Slice 3 — Report discipline (משמעת-דוחות) — תוכנית

> **תאריך**: 2026-06-01
> **סטטוס**: plan-verified ✅ (אביגיל, סבב 2 — READY; reports/bds/slice-3-report-discipline-avigail-v2.md)
> **Complexity**: 3/10 (verifier: light — תיעוד/פרומפט בלבד, אין קוד להריץ)
> **תלויות (`depends_on`)**: [] — additive על main. בנוי מעל פורמט ה-MD-front-matter (slice-2, merged).
> **Base**: main tip `8fa471b` (או חדש יותר — ה-worktree נפתח מ-main בזמן dispatch)

---

## §0 — Pre-flight

> זה slice של **השיטה עצמה** (brief-driven-slices). "ריפו הפרויקט" = ריפו השיטה. אין BE/FE/browser/tunnel — זה עריכת agent.md + docs בלבד. אין קוד חדש להריץ.

### תלויות (חובה!)

slice זה **מבוסס על**:
- slice-2-distillation (status: **merged** ב-`18d2816`) — הוא שהקים את פורמט ה-MD-front-matter (`reports/<project>/<slice>-<verifier>.md`) ואת `docs/reports-format.md`. ה-slice הזה משנה את **חוזה ה-Task-result** של המאמתים, על גבי אותו פורמט-דוח.
- _אין תלות ב-branch לא-merged. additive בלבד._

> אביגיל: בדקי ש-`docs/reports-format.md` קיים (פורמט front-matter), ושהסעיפים שה-brief מצטט ב-agents/{avigail,calev,calev-heavy,mordechai,eliezer}.md אכן קיימים במספרי-השורות שצוינו.

### Worktree

```bash
cd /home/user/projects/brief-driven-slices
git worktree add /home/user/projects/brief-driven-slices/.worktrees/slice-3-report-discipline -b slice-3-report-discipline main
cd .worktrees/slice-3-report-discipline
```

> **מבנה bare**: ה-repo הוא bare+worktrees. base = `main` (אין dev). absolute path ל-worktree add.
> **אין `pnpm install`** — אין Node. אין מה לבנות. זה תיעוד.

### איך להריץ

- **אין BE/FE/tests.** זה עריכת תיעוד/פרומפט.
- האימות הוא **grep + קריאה אנושית**: שהחוזה מנוסח, עקבי בין 3 המאמתים, ושהצרכנים (מרדכי/אליעזר) מצפים לו.
- **אין `distill.py` להריץ** — אבל ודא שלא שברת את reports-format.md (הפורמט שה-distill קורא לא משתנה כאן; רק חוזה ה-result משתנה, וה-result לא נקרא ע"י distill).

### Browser / OneCLI agent

לא רלוונטי.

### Reading list

**must-read** (לפני שמתחילים):
- `docs/reports-format.md` — פורמט ה-MD-front-matter הקיים. **לא משתנה ב-slice הזה** (הדוח עצמו זהה). מה שמשתנה: מה המאמת מחזיר ב-Task-result.
- `agents/avigail.md` (§"פורמט הדוח" סביב שו' 143-183, §"כתיבת דוח" סביב שו' 185+) — הדוח שאביגיל כותבת + מה שהיא מחזירה.
- `agents/calev.md` (§"פורמט דוח" של כל mode: phase ~78-95, light ~128-159, §"כתיבת דוח" ~276+) — דוחות כלב.
- `agents/mordechai.md` (§"הפעל אביגיל" ~48, §"בוקר" ~62, §"הפעלת אביגיל" prompt template) — מי שצורך את ה-result של אביגיל.
- `agents/eliezer.md` (§"חובה: Verifier (כלב)" ~194, §"מה לעשות עם דוח ה-calev" ~214, §"Feedback loop" ~347) — מי שצורך את ה-result של כלב.

**reference** (בזמן עבודה):
- `agents/calev-heavy.md` — מצביע ל-calev.md לפורמט; צריך עדכון עקבי.
- `workflow.md` — הפרוטוקול הכללי (להוסיף את החוזה).

---

## §1 — מטרה

אחרי ה-slice הזה, **הדוח המלא הוא הערוץ היחיד** שבו מאמת (אביגיל/כלב) מעביר ניתוח. ה-Task-result שלו הוא **תמיד** רק תמצית-אינדקס קבועה (verdict + path + כותרות-findings), אף פעם לא ניתוח. כך לא ייתכן שפרט ניתוחי "ייאמר ב-result אך לא יישמר בדוח" — הבעיה שתיקנו ב-slice-2 ברמת-הפורמט, נסגרת כאן ברמת-ההרגל. מרדכי ואליעזר מצפים לתמצית הזו ויודעים ש**חובה לפתוח את הדוח** לכל פעולה על finding — אין קיצור-דרך שמפתה לדלג.

---

## §2 — Scope

| פיצ'ר | כן/לא | לאן |
|------|------|------|
| חוזה Task-result קבוע למאמתים: תמצית-אינדקס בלבד (verdict + path + ספירות + כותרות-findings) | ✅ | ה-slice הזה |
| חובת דוח-מפורט מנוסחת חד: "כל ניתוח הולך לדוח; ניתוח ב-result = תקלה" | ✅ | ה-slice הזה |
| עדכון 3 המאמתים (avigail, calev, calev-heavy) לחוזה החדש | ✅ | ה-slice הזה |
| עדכון 2 הצרכנים (mordechai, eliezer): "צפה לתמצית, פתח את הדוח תמיד" | ✅ | ה-slice הזה |
| תיעוד החוזה ב-workflow.md + reports-format.md | ✅ | ה-slice הזה |
| **שינוי מבנה ה-front-matter / הדוח עצמו** | ❌ | לא משתנה — slice-2 כבר הגדיר אותו |
| **אכיפה אוטומטית** (בדיקה ש-result קצר מ-N שורות) | ❌ | אין מנגנון שרץ על Task-result; האכיפה היא ניסוח-חד + הרגל. slice עתידי אם יידרש |
| שינוי distill.py | ❌ | ה-result לא נקרא ע"י distill — אין נגיעה |

> הגנה מ-scope creep: זה slice של **ניסוח חוזה**, לא קוד. הדוח והפורמט שלו לא משתנים — רק מה שעובר ב-Task-result.

---

## §3 — Architecture diagram

```
                    לפני (slice-2):                  אחרי (slice-3):
  ┌──────────────┐                          ┌──────────────┐
  │   מאמת        │ ─── MD מלא ב-result ──┐  │   מאמת        │ ─── תמצית בלבד ──┐
  │ (אביגיל/כלב) │ ─── front-matter ──┐  │  │ (אביגיל/כלב) │ ─── דוח מלא ──┐  │
  └──────────────┘                    ▼  ▼  └──────────────┘  (front-matter ▼  ▼
         שני ערוצים → סיכון דליפה         │         + גוף MD)    │  result = אינדקס
         (פרט ב-result שלא בדוח)          │    ערוץ יחיד לבשר ───┘  (verdict+path+
                                          │    הדוח. result מצביע    כותרות)
                                          ▼                          ▼
                              reports/<project>/<slice>-<verifier>.md
                                  (זהה ב-slice-2 ו-3 — לא משתנה)
                                          │
                    ┌─────────────────────┴──────────────────┐
                    ▼                                          ▼
            מרדכי/אליעזר קוראים result                 distill.py קורא front-matter
            → חייבים לפתוח את הדוח                     (לא נוגע ב-result — אין שינוי)
            (קבוע — אין קיצור דרך)
```

---

## §4 — Commits בסדר

> **גישה כללית**: כל ה-commits הם `manual` (עריכת agent.md/docs, אין קוד). האימות: grep שהחוזה מנוסח + קריאה אנושית שהוא עקבי. הסדר: קודם מנסחים את החוזה במאמתים (0-1), אז מעדכנים צרכנים (2), אז מתעדים (3).

### Commit 0 — חוזה ה-result + חובת דוח-מפורט: avigail (approach: manual)

> מתחילים מאביגיל כי היא המאמת הראשון בזרימה. מגדירים כאן את **תבנית-החוזה** שתחזור גם אצל כלב.

**קבצים שמשתנים**:
- `agents/avigail.md`:
  - **§"פורמט הדוח"** (סביב שו' 143-183) — הוסף בראשו משפט-חובה: "**הדוח חייב להיות מפורט ומלא** — הוא הערוץ היחיד שבו אתה מעביר ניתוח. כל טבלה, spot-check, evidence, ורציונל-verdict — בדוח, לא ב-Task-result."
  - **§"כתיבת דוח MD עם front-matter"** (סביב שו' 185+) — אחרי הוראת-הכתיבה, הוסף **§ חדש "מה אתה מחזיר ב-Task-result"**:
    ```
    ה-Task-result שלך הוא אינדקס קבוע — לא ניתוח. פורמט מדויק:

    verdict: <READY|USABLE-AFTER-FIX|NEEDS-REWORK>
    report: reports/<project>/<slice>-avigail.md
    findings: <N>
    findings (כותרות בלבד — ה-summary של כל finding, שורה לכל אחד):
      - 🔴 <summary של finding בחומרה blocker/regression>
      - 🟡 <summary של finding בחומרה confusion/type-error/outdated>
      - 🟢 <summary של finding minor>

    זהו. שום הסבר, שום source_code/cost, שום "למה", שום המלצת-תיקון.
    כל אלה כבר בדוח. מי שרוצה עומק — פותח את reports/.../<slice>-avigail.md.
    ```
  - **Anti-patterns** (סוף הקובץ) — הוסף: "❌ לכתוב ניתוח/הסבר/המלצה ב-Task-result — זו תקלה. ה-result הוא אינדקס (verdict+path+כותרות), הבשר בדוח. אם הדוח רזה וה-result שמן — הפכת את היוצרות."

**Verification** (manual):
```bash
grep -q "הדוח חייב להיות מפורט" agents/avigail.md
grep -q "מה אתה מחזיר ב-Task-result\|אינדקס קבוע" agents/avigail.md
grep -q "כותרות בלבד" agents/avigail.md
grep -q "תקלה" agents/avigail.md   # ה-anti-pattern
```

### Commit 1 — אותו חוזה: calev + calev-heavy (approach: manual)

> מעתיקים את **אותה תבנית-חוזה** מ-Commit 0, מותאמת ל-verdicts של כלב (GO/PARTIAL/NO-GO) ול-DoD. חובה: ניסוח עקבי עם avigail (אחרת מרדכי/אליעזר יבלבלו בין שני פורמטים).

**קבצים שמשתנים**:
- `agents/calev.md`:
  - **§"מה אתה לא עושה (בכל mode)"** (סביב שו' 57+) — הוסף: "❌ **לא לכתוב ניתוח ב-Task-result**. ה-result הוא תמצית-אינדקס; כל ממצא/evidence/רציונל בדוח."
  - בכל אחד מ-3 פורמטי-הדוח (phase ~78, light ~126, heavy ~205) — הוסף משפט "**הדוח מפורט — הערוץ היחיד לניתוח**".
  - **§"כתיבת דוח MD מתויג"** (סביב שו' 276+) — הוסף **§ "מה אתה מחזיר ב-Task-result"** עם הפורמט (מותאם לכלב):
    ```
    verdict: <GO|PARTIAL|NO-GO>
    report: reports/<project>/<slice>-calev.md
    mode: <phase|light|heavy>
    DoD: <X/Y>           ← light/heavy בלבד
    findings: <N>
    findings (כותרות בלבד):
      - 🔴 <summary>
      - 🟡 <summary>

    זהו. אפס ניתוח ב-result — הכל בדוח.
    ```
  - **Anti-patterns** (סוף) — הוסף: "❌ לכתוב ניתוח/evidence ב-Task-result — תקלה. result = אינדקס, דוח = בשר."
- `agents/calev-heavy.md`:
  - מצביע ל-calev.md לפורמט הדוח (כבר היום). הוסף הפניה מפורשת: "**חוזה ה-Task-result זהה ל-calev.md §'מה אתה מחזיר ב-Task-result'** — אינדקס בלבד, אפס ניתוח."

**Verification** (manual):
```bash
grep -q "מה אתה מחזיר ב-Task-result\|תמצית-אינדקס" agents/calev.md
grep -q "GO|PARTIAL|NO-GO\|<GO|PARTIAL|NO-GO>" agents/calev.md
grep -q "כותרות בלבד" agents/calev.md
grep -q "Task-result\|אינדקס" agents/calev-heavy.md
# עקביות: שני המאמתים משתמשים באותה תבנית
grep -c "כותרות בלבד" agents/avigail.md agents/calev.md   # שניהם ≥1
```

### Commit 2 — הצרכנים מצפים לחוזה: mordechai + eliezer (approach: manual)

> מרדכי ואליעזר מקבלים את ה-result ופועלים עליו. הם חייבים לדעת: ה-result הוא אינדקס, **חובה לפתוח את הדוח** לכל החלטה על finding. בלי זה הם "יופתעו" מ-result דליל.

**קבצים שמשתנים**:
- `agents/mordechai.md`:
  - **§"הפעל אביגיל"** (סביב שו' 48-60) — הוסף הערה: "**מה אביגיל מחזירה**: תמצית-אינדקס (verdict + path + כותרות-findings), **לא** את הניתוח המלא. כדי לתקן finding — **פתח את `reports/<project>/<slice>-avigail.md`**. אל תסיק מהכותרת לבד."
  - **§"בוקר"** (סביב שו' 62) / **§ runtime-gate** — הוסף ל-runtime-gate: "כלב מחזיר תמצית (verdict + DoD + כותרות). לפני merge — **פתח את דוח כלב המלא** (`reports/.../calev.md`), אל תסתמך על שורת-התמצית להחלטת-merge."
  - **Anti-patterns** — הוסף: "❌ להחליט על finding מתוך כותרת ה-result בלבד — פתח את הדוח. ה-result הוא אינדקס, לא תחליף."
- `agents/eliezer.md`:
  - **§"מה לעשות עם דוח ה-calev"** (סביב שו' 214) — הוסף: "כלב מחזיר תמצית-אינדקס (verdict + כותרות). הספירה (0 / 1-2 / 3+) נגזרת מ-`findings: <N>` ב-result. **כדי להבין finding ולתקן — פתח את `reports/.../calev.md`**, אל תתקן מהכותרת."
  - **§"Feedback loop"** (סביב שו' 347) — חידוד: "הדיווח שלך למרדכי כבר כולל verdict כלב מפורש (מ-runtime-gate slice-2); הוסף את ה-path לדוח כלב כדי שמרדכי יפתח אותו."

**Verification** (manual):
```bash
grep -q "פתח את\|אינדקס, לא תחליף\|אל תסיק מהכותרת" agents/mordechai.md
grep -q "תמצית\|פתח את.*calev" agents/eliezer.md
grep -q "אינדקס" agents/mordechai.md
```

### Commit 3 — תיעוד החוזה + סגירה (approach: manual)

**קבצים שמשתנים**:
- `docs/reports-format.md` — הוסף **§ חדש "חוזה ה-Task-result (משמעת-דוחות)"**: הסבר שהדוח הוא הערוץ היחיד, ה-result הוא אינדקס (verdict+path+כותרות), והפורמט המדויק לכל מאמת. קישור ל-agents.
- `workflow.md` — הוסף את החוזה לתיאור הזרימה (המאמת כותב דוח מלא → מחזיר אינדקס → הצרכן פותח את הדוח).
- `docs/walkthrough.md` — ערך חדש (skill `update-walkthrough`): מה השתנה ב-slice הזה.
- `docs/decisions/bds.md` — ערך חדש (מרדכי): הרציונל — למה הדוח הוא ערוץ-יחיד וה-result אינדקס-קבוע (סגירת פער-הדליפה מ-slice-2 ברמת-ההרגל; הקביעות מונעת שמרדכי ידלג על קריאת הדוח).
- ה-brief הזה (סטטוס → הושלם).

**Verification** (manual):
```bash
grep -q "חוזה ה-Task-result\|משמעת-דוחות" docs/reports-format.md
grep -q "אינדקס\|ערוץ יחיד" workflow.md
test -f docs/walkthrough.md && grep -q "report-discipline\|חוזה.*result" docs/walkthrough.md
grep -q "ערוץ-יחיד\|אינדקס-קבוע\|משמעת-דוחות" docs/decisions/bds.md
```

---

## §5 — DoD verifiable

| # | בדיקה | איך |
|---|------|------|
| 1 | חוזה ה-result מנוסח אצל avigail | `grep "מה אתה מחזיר ב-Task-result" agents/avigail.md` + פורמט (verdict/report/findings/כותרות) |
| 2 | חובת דוח-מפורט אצל avigail | `grep "הדוח חייב להיות מפורט" agents/avigail.md` |
| 3 | חוזה ה-result מנוסח אצל calev (3 modes) | `grep "מה אתה מחזיר" agents/calev.md` + verdicts GO/PARTIAL/NO-GO + DoD |
| 4 | calev-heavy מצביע לחוזה | `grep "Task-result" agents/calev-heavy.md` |
| 5 | **עקביות בין avigail ל-calev** | שתי התבניות זהות במבנה (verdict+report+findings+כותרות); ההבדלים הלגיטימיים: (א) ערכי ה-verdict (READY/USABLE/NEEDS-REWORK מול GO/PARTIAL/NO-GO), (ב) שורת `DoD: X/Y` — calev בלבד, (ג) שורת `mode` — calev בלבד. קריאה אנושית. |
| 6 | mordechai מצפה לתמצית + פותח דוח | `grep "פתח את.*avigail\|אל תסיק מהכותרת" agents/mordechai.md` |
| 7 | mordechai: runtime-gate פותח דוח כלב | `grep "פתח את דוח כלב\|פתח את.*calev" agents/mordechai.md` |
| 8 | eliezer מצפה לתמצית + פותח דוח | `grep "פתח את.*calev" agents/eliezer.md` |
| 9 | anti-patterns אצל שני המאמתים | `grep "תקלה" agents/avigail.md agents/calev.md` (result-שמן = תקלה) |
| 10 | תיעוד ב-reports-format + workflow | `grep "חוזה ה-Task-result" docs/reports-format.md` + `grep "אינדקס" workflow.md` |
| 11 | decisions מתעד רציונל | `grep "ערוץ-יחיד\|משמעת-דוחות" docs/decisions/bds.md` |
| 12 | **לא נשבר**: reports-format front-matter | `grep "front-matter" docs/reports-format.md` עדיין קיים (הפורמט לא השתנה) |

---

## §6 — Risks + mitigations

| סיכון | מקור | מיטיגציה |
|------|------|----------|
| **אי-עקביות בין avigail ל-calev** בפורמט ה-result | שני קבצים נפרדים, ניסוח ידני | Commit 0 מגדיר תבנית, Commit 1 מעתיק אותה. DoD 5 בודק עקביות. אביגיל תתפוס drift. |
| **המאמת ימשיך לכתוב ניתוח ב-result מהרגל** | מודל עלול לסכם בעל-פה למרות ההוראה | ניסוח **חד** + anti-pattern מפורש ("result-שמן = תקלה"). אין אכיפה אוטומטית (מחוץ ל-scope) — מסתמכים על הניסוח. |
| **מרדכי/אליעזר ידלגו על קריאת הדוח** | אם פעם אחת ה-result מספיק → הרגל-דילוג | הקביעות: ה-result **תמיד** רק אינדקס → אין מצב שהוא מספיק → חובה תמיד לפתוח. מנוסח כ-anti-pattern אצל הצרכנים. |
| **שבירת reports-format** (הפורמט שה-distill קורא) | עריכה בטעות של מבנה הדוח במקום חוזה-ה-result | ה-slice לא נוגע ב-front-matter schema. DoD 12 מוודא ש-front-matter עדיין מתועד. |
| forward-refs בין הקבצים נשברים | calev-heavy מצביע ל-calev; mordechai מצביע ל-reports/ | grep ב-Verification. אביגיל בודקת file:line. |

> 3 שתמיד נשכחים:
> 1. Hardcoded strings → i18n: לא רלוונטי (תיעוד עברית-מכוון).
> 2. Reactivity: לא רלוונטי (אין framework).
> 3. OneCLI placeholder: לא רלוונטי.
> **הרלוונטיים כאן**: עקביות-בין-מאמתים, הרגל-המאמת, הרגל-הצרכן.

---

## §7 — Escalation triggers

> אם X — עצור ושאל את Tama:

- פיתוי לבנות **אכיפה אוטומטית** (בדיקה ש-result קצר) — מחוץ ל-scope, Escalate אם נראה הכרחי.
- פיתוי לשנות את **מבנה הדוח / front-matter** — אסור, זה slice-2. אם נראה שצריך — Escalate.
- אי-בהירות איך לנסח את החוזה כך שיהיה עקבי בין avigail ל-calev (verdicts שונים) — Escalate על הניסוח.
- Brief סותר את עצמו / סעיף ב-agent.md שצוטט לא קיים במספר-השורה.

---

## §8 — Complexity score + verifier tier

| פרמטר | ניקוד |
|------|------|
| Pure docs/prompt, אין IO, אין קוד | -2 |
| >5 files (avigail, calev, calev-heavy, mordechai, eliezer, reports-format, workflow, decisions, walkthrough) | +1 |
| רגישות: נוגע בחוזה שכל המאמתים+הצרכנים תלויים בו | +2 |
| Greenfield? לא — עורך קבצים קיימים | 0 |
| State machine / async? לא | 0 |
| ספרייה חיצונית? לא | 0 |
| עקביות-בין-קבצים קריטית (drift risk) | +1 |
| אין runtime לאמת (האמת מ-קריאה, לא הרצה) | -1 |

**Score**: 3 / 10

> נמוך כי אין קוד. הרגישות (חוזה משותף) מאוזנת ע"י היעדר-runtime. הסיכון העיקרי הוא **עקביות-ניסוח**, וזה בדיוק מה שאביגיל (plan-verifier) תופסת — לכן light מספיק, אבל אביגיל קריטית כאן.

**Tier**: light. אין verifier-phase (אין phases מסוכנים — הכל manual-docs).

**Verifier-phase אחרי commit/phase**: אין. כלב light בסוף בלבד — יקרא את 5 הקבצים, יוודא שהחוזה מנוסח, עקבי, ושהצרכנים מצפים לו. (כלב לא "מריץ" — אין מה להריץ; הוא קורא ומאמת ניסוח, וזה גבולי ל-light. ראה §9 שאלה 2.)

---

## §9 — שאלות פתוחות

| # | שאלה | ברירת מחדל | חוסם? |
|---|------|----------|------|
| 1 | תמצית ה-result — קשיחה (verdict+path בלבד) או תמצית+כותרות-findings? | **סגור: תמצית+כותרות.** הכותרות הן ה-summary שכבר בדוח → אפס דליפה, רק שיקוף. מרדכי רואה מה יש בלי לפתוח, אבל חייב לפתוח לפרטים | ❌ |
| 2 | כלב light על slice בלי-קוד — מה הוא בודק? | **קורא 5 קבצים + מאמת ניסוח/עקביות (grep + קריאה).** זה גבולי ל-runtime-verify (אין runtime), אבל ה-DoD ניתנים ל-grep. אם כלב מרגיש שאין מה לאמת — זה תקין, יסמן GO על בסיס ה-grep | ❌ |
| 3 | אכיפה אוטומטית (result קצר מ-N) | **מחוץ ל-scope.** אין hook על Task-result. ניסוח-חד + הרגל. slice עתידי אם יידרש | ❌ |
| 4 | האם לשנות את מבנה הדוח עצמו? | **לא.** הדוח (front-matter + גוף) זהה ל-slice-2. רק חוזה ה-result משתנה | ❌ |
| 5 | קביעות — האם להשאיר "פתח תמיד" בלי יוצא מן הכלל? | **כן, קבוע.** המשתמשת ביקשה מפורשות: אם מרדכי יחשוב שהוא יכול לדלג — ההרגל יישבר. אין יוצאי-דופן | ❌ |

---

## סטיות מהתכנון (מתעדכן ע"י executor תוך כדי)

> ה-executor מתעד פה כל סטייה מה-brief ולמה.

- ...
