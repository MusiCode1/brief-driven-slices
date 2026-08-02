# השוואה: BDS מול GitHub Spec-Kit

> **תאריך**: 2026-07-20
> **מקור**: https://github.com/github/spec-kit
> **שאלה**: ללמוד מהם, או לעבור אליהם?
> **הכרעה בקצרה**: **ללמוד, לא לעבור.** לאמץ 3 רעיונות (Constitution / Converge / commands-UX);
> לשמר את שלושת ה-crown-jewels של BDS (אימות-runtime, זיקוק, merge-gate אנושי).

> ⚠️ **עודכן אחרי מחקר-עומק מהקוד** (`spec-kit @ 57cc518`) — ראה
> [`spec-kit-deep-dive.md`](./spec-kit-deep-dive.md). ההכרעה לא השתנתה, אבל 3 תיקונים
> מהותיים מהמסמך הזה (שנכתב מה-README בלבד):
> 1. **Converge הוא מבקר-שלמות *סטטי*, לא אימות-runtime** — קורא קוד בלי להריצו, מוסיף
>    tasks (append-only). **לא חופף לכלב**; ממלא פער *אחר* (שלמות-הפרויקט-כולו).
> 2. **ל-spec-kit *יש* gates אנושיים** — אבל ברמת-מסמך (`review-spec`/`review-plan`), לא merge/runtime.
> 3. **/analyze משלים ולא מחליף את אביגיל** — /analyze = עקביות בין-מסמכים; אביגיל = עובדתיות מול-קוד.

---

## 1. מה זה Spec-Kit

Toolkit רשמי של GitHub ל-**Spec-Driven Development**: מפרט מפורט **מקדים ומנחה** ייצור-קוד
ע"י סוכני-AI, במקום "קוד קודם, תיעוד אחר-כך".

### הזרימה (6 שלבים)
1. **Constitution** — עקרונות-על ותקנון-פיתוח לפרויקט.
2. **Specify** — דרישות ו-user-stories (ה"מה" וה"למה").
3. **Plan** — אסטרטגיית-מימוש טכנית + stack.
4. **Tasks** — רשימת-משימות מהתוכנית.
5. **Implement** — ביצוע כל המשימות.
6. **Converge** — הערכת ה-codebase מול הארטיפקטים; זיהוי עבודה שנותרה.

### כלים
- **Slash-commands**: `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`,
  + `/speckit.clarify` (תחומים תת-מוגדרים), `/speckit.analyze` (בדיקת-עקביות בין ארטיפקטים).
- **Specify CLI** (Python, `uv tool install`) — init, setup, ניהול commands/extensions. תיקיות `.specify/`.
- **30+ סוכני-AI** נתמכים (Copilot, Claude, ועוד) — slash או skills-mode.
- **Extensions / Presets / Bundles** — התאמה דומיינית, תבניות, חבילות מבוססות-תפקיד.

---

## 2. מיפוי מול BDS

| ציר | Spec-Kit | BDS |
|-----|----------|-----|
| יחידת-עבודה | Spec → Plan → Tasks | Brief (slice) |
| ממשק | slash-commands | הפעלת-סוכנים (Task/Agent) |
| אימות | `/clarify` (בהירות) + `/analyze` (עקביות בין-מסמכים) + `/converge` (שלמות סטטית) | **אביגיל** (עובדתיות מול-קוד) + **כלב** (runtime — מריץ קוד) |
| סוכנים | 30+ גנריים | 5 תפקידים ייעודיים (מודל/prompt פר-תפקיד) |
| בידוד | תיקיית-ארטיפקטים בלבד (`specs/NNN/`; ללא checkout/worktree) | worktrees + שרשור slices |
| gate אנושי | **doc-level** (`review-spec`/`review-plan`); אין merge-gate/runtime-gate | **merge אנושי-בלבד** + live-preview ל-web |
| לולאת-שיפור | — | **זיקוק** (patterns/pitfalls מ-reports) |
| אורקסטרציה | אינטראקטיבי | יתרו (queue לילי) |
| בשלות/גיבוי | **harness** בשל (3150 טסטים — כולם על ה-CLI/plumbing; **efficacy השיטה לא-נמדדת**) | bespoke, single-user, **307 דוחות efficacy** אמפיריים |

---

## 3. מה ללמוד מהם (רעיונות שווי-אימוץ)

1. **Constitution phase** — עקרונות-על מוגדרים **פעם אחת פר-פרויקט**. ב-BDS הדוקטרינה
   מפוזרת בין mordechai/SKILL/AGENTS. `<project>/constitution.md` היה מרכז את "החוקה".
2. **Converge phase** — **פער אמיתי שלנו.** BDS מאמת slice-slice, אבל אין בדיקה
   "האם הפרויקט **השלם** תואם את הכוונה, ומה נותר?". spec-kit הופך את זה לשלב מפורש.
   ⚠️ **דיוק מהקוד**: זה **מבקר-שלמות סטטי** (קורא קוד בלי להריצו, מוסיף tasks append-only) —
   **לא** אימות-runtime ו**לא** חופף לכלב. גירסת-BDS צריכה לזווג אותו עם מעבר-runtime של כלב
   (ראה skeleton ב-`spec-kit-deep-dive.md §6`).
3. **UX של slash-commands** — discoverable, שקוף. הפעלת-הסוכנים שלנו פחות נגישה למשתמש חדש.
4. **breadth של סוכנים (30+)** — spec-kit agent-agnostic; BDS תומך ב-3 CLIs. פורטביליות.
5. **CLI רשמי + presets/bundles** — onboarding ותחזוקה טובים מ-`generate/install` שלנו.

---

## 4. איפה BDS חזק יותר (למה לא לעבור)

1. **אימות דו-שכבתי עם סוכן שמריץ קוד.** `/analyze` בודק *עקביות בין-מסמכים* ו-`/converge`
   בודק *שלמות סטטית* — **שניהם לא מריצים קוד**. ב-spec-kit הדבר היחיד ש"מריץ" הוא סוכן-ה-implement
   שבודק את *עצמו* (implement.md שלב 9). **כלב הוא סוכן-אימות עצמאי שמריץ את הקוד בסביבה נקייה**
   ותופס באגי-runtime — מנגנון שפשוט לא קיים ב-spec-kit. הוכחה חיה: כלב תפס 11 blockers ב-155
   ריצות; באג ה-symlink של ה-install נתפס **רק** בהרצה אמיתית, לא בבדיקת-מסמכים.
   ועוד: **אביגיל** תופסת briefs ששגויים *עובדתית מול הקוד* — מחלקה ש-/analyze לא יכול מבנית.
2. **לולאת-הזיקוק.** BDS מזקק את דוחות-האימות שלו כדי לשפר את **השיטה עצמה** — כלל ה-anchor
   הוריד את `wrong-line-number` מ-63→0. ל-spec-kit אין feedback-loop כזה. זה ה-crown-jewel.
3. **merge קדוש + worktree isolation.** spec-kit נוטה "לרוץ עד הסוף"; BDS עוצר ב-gate אנושי,
   ומריץ על worktrees הפיכים. ל-quality-critical — בטוח יותר.
4. **הוכחה אמפירית.** 307 דוחות מראים שה-gates תופסים באגים אמיתיים (41% briefs דורשים תיקון,
   38 blockers שנתפסו לפני dispatch).

---

## 5. ההבחנה התמציתית

> **spec-kit מצוין ב"להגדיר כוונה ולהוציא קוד". BDS מצוין ב"לאמת שהקוד באמת עובד — ולשפר
> את עצמו". BDS יותר paranoid, וזה מתאים למקרה-השימוש שלנו (quality-critical, self-improving).**

עבירה ל-spec-kit הייתה מאבדת את שלושת ה-jewels. אבל **הזרימה שלו נקייה יותר** בהגדרת-כוונה
(Constitution) ובסגירת-לולאה (Converge) — ומשם באים 3 פריטי ה-backlog (24-26).

---

## 6. פעולות-המשך (backlog)

> ה-backlog המפורט והמעודכן ב-[`spec-kit-deep-dive.md §8`](./spec-kit-deep-dive.md).

- **24. Constitution פר-פרויקט** — `<project>/constitution.md`; אביגיל+כלב קוראים כאילוץ-על.
  **עדיפות: גבוהה.**
- **25. project-converge slice** — מסלול A (שלמות סטטית, סגנון spec-kit) + מסלול B (כלב E2E —
  התוספת שלנו), בבעלות מרדכי, מפיק briefs, gated. skeleton ב-deep-dive §6. **עדיפות: גבוהה.**
- **26. commands-UX / hooks / checklist** — הכי חשוב מהשלושה: מנגנון **hooks** (`before_`/`after_`)
  שהופך אביגיל/כלב ל-pluggable; אחריו checklist-gate; ה-slash-UX עצמו הכי פחות דחוף.
- **27. /clarify-loop — שלב-חובה לפני חתימת-brief** (חדש; **הועלה בעדיפות → בינונית-גבוהה**).
  מרדכי שואל את המשתמשת עד 5 שאלות רב-ברירה high-impact להסרת עמימות, וכותב תשובות בחזרה
  ל-brief. **הרציונל**: תוקף ישירות את ה-41%-briefs-דורשים-תיקון (הנחות-לא-מבוררות). פירוט
  ב-`spec-kit-deep-dive.md §8`.

> נדחה במפורש: מעבר ל-spec-kit. הרציונל (מאושר ברמת-הקוד): אובדן אימות-runtime עצמאי (כלב),
> זיקוק, ו-merge-gate+worktree — אף אחד מהשלושה לא קיים ב-spec-kit.
