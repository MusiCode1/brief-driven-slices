# מחקר-עומק: GitHub Spec-Kit מול BDS — קריאה מהקוד

> **תאריך**: 2026-07-20
> **מקור**: clone של `github/spec-kit` @ `57cc518` (v0.13.0-dev, 2026-07-17)
> **שיטה**: קריאת ה-templates, ה-slash-commands, ה-Specify CLI, ה-workflow engine
> וה-test-suite בפועל — **לא** ה-README.
> **יחס למסמך הקודם**: `spec-kit.md` התבסס על ה-README. מסמך זה מאמת, מדייק ובמספר
> נקודות **מתקן** אותו. ההכרעה הסופית לא השתנתה ("ללמוד, לא לעבור") — אבל *הנימוקים*
> חדדו, ושניים מ-3 הפערים מקבלים מיסגור מדויק יותר.

---

## 0. TL;DR — מה השתנה אחרי קריאת הקוד

1. **Converge ≠ אימות-runtime.** זה התיקון הכי חשוב. Converge הוא **מבקר-שלמות סטטי**
   (static completeness auditor): קורא spec/plan/tasks + constitution, בוחן את הקוד **בלי
   להריץ אותו**, מסווג פערים (missing/partial/contradicts/unrequested), ו**מוסיף** משימות
   חדשות ל-`tasks.md` (append-only). הוא **לא מריץ קוד, לא git, לא diff**. לכן הוא **לא חופף
   לכלב** בכלל — הוא ממלא פער *אחר* של BDS (שלמות-הפרויקט-כולו), לא את הפער שכלב סוגר.
2. **ל-spec-kit יש gates אנושיים** — אבל ברמת ה**מסמך** (`review-spec`, `review-plan`
   ב-`workflow.yml`), לא ברמת merge/runtime. המסמך הקודם קרא לזה "agent-driven" וזה לא מדויק.
3. **/analyze חופף לאביגיל פחות ממה שחשבנו.** /analyze בודק עקביות *בין-מסמכים*; אביגיל
   בודקת עקביות *מסמך-מול-קוד-אמיתי*. משלימים, כמעט לא חופפים.
4. **הבשלות היא של ה-harness, לא של השיטה.** 129 קבצי-טסט / 3150 פונקציות-טסט — **כולם**
   על ה-CLI (bundler, catalog, integrations, hooks, path-safety). **אפס** טסטים שמודדים
   אם converge/analyze תופסים באגים אמיתיים בקוד-משתמש. זה בדיוק ההבחנה "טענה מול קוד".
5. **הבידוד של spec-kit חלש מהמתואר.** `create-new-feature.sh` יוצר `specs/NNN-slug/`
   ומחשב שם-branch — אבל **לא עושה checkout ולא worktree**. בידוד ברמת-תיקיית-ארטיפקטים
   בלבד. worktrees של BDS חזקים מהותית יותר.

---

## 1. מה spec-kit באמת עושה מכנית

### 1.1 הפקודות הן prompts, לא pipeline קשיח

כל "שלב" הוא קובץ `templates/commands/<name>.md` — **prompt לסוכן**, עם front-matter שמצביע
על סקריפט-הכנה (`check-prerequisites.sh --json`). הפקודות: `constitution, specify, clarify,
plan, tasks, analyze, implement, converge, checklist, taskstoissues`.

ה-workflow הרשמי (`workflows/speckit/workflow.yml`) מריץ **רק**:

```
specify → [gate: review-spec] → plan → [gate: review-plan] → tasks → implement
```

`clarify`, `analyze`, `converge`, `checklist` — **לא** ב-workflow הדיפולטי. הם פקודות
אופציונליות שהמשתמש מריץ ידנית. כלומר "6 השלבים" מה-README הם מסלול-על מומלץ, לא צינור אכיפה.

**מסקנה**: ה-gates ב-spec-kit קיימים ואנושיים (`options: [approve, reject]`,
`on_reject: abort`), אבל הם **gates על מסמכים** — "אשר את ה-spec", "אשר את ה-plan".
אין gate על "האם הקוד נכון" ואין מושג של merge. ה-`implement` פשוט כותב לקוד in-place.

### 1.2 Constitution — מכניקה

- קובץ `.specify/memory/constitution.md`, ממולא מ-`templates/constitution-template.md`.
- מבנה: N עקרונות (I–V בדוגמה), כל אחד עם משפטי MUST/SHOULD + rationale, ואז
  Security/Cross-Platform, Development Workflow & Quality Gates, Governance עם SemVer +
  "Sync Impact Report" (HTML-comment בראש הקובץ).
- פקודת `/constitution` ממלאת את התבנית, **מפיצה** שינויים ל-plan/spec/tasks-templates
  ולקבצי-הפקודות, ומנהלת גירסה.
- **האכיפה היא prompt-based, לא code-based.** אין linter. החוקה נאכפת בכך שהיא **נטענת
  להקשר** של הפקודות הבאות ומשמשת checklist:
  - `plan-template.md:39` — `## Constitution Check` עם `*GATE: Must pass before Phase 0
    research. Re-check after Phase 1 design.*`
  - `analyze.md:60` — התנגשות עם MUST היא אוטומטית CRITICAL.
  - `converge.md:85-88` — הפרת MUST היא finding בחומרה הגבוהה ביותר.

הדוגמה בריפו עצמו (`.specify/memory/constitution.md`) מצוינת: 5 עקרונות שנגזרו מדפוסי-הקוד
הקיימים ("registry-driven architecture", "Test-Backed Change NON-NEGOTIABLE", וכו').

### 1.3 Converge — מכניקה מדויקת (הפער הכי נחקר)

מקור: `templates/commands/converge.md`. ציטוטים מפתח:

- **מטרה** (שורות 59-66): "Close the gap between what a feature's specification, plan, and
  tasks call for and what the codebase currently implements... **append each piece of
  remaining work as a new, traceable task**".
- **לא runtime** (שורות 68-69): "This is **not** a diff tool and does **not** track changes...
  no git, no branch comparison, no history."
- **append-only** (שורות 73-83): הכתיבה היחידה היא הוספת `## Phase N: Convergence` ל-tasks.md.
  אסור לגעת ב-spec/plan, אסור לשכתב משימות, **אסור לגעת בקוד** ("completing the appended
  tasks is the job of `implement`").
- **סיווג פערים** (שורות 145-160): `missing` / `partial` / `contradicts` / `unrequested`,
  כל אחד עם severity CRITICAL/HIGH/MEDIUM/LOW.
- **הערכת-קוד סטטית** (שורות 133-147): בונה "code-scope map" מ-file-paths ב-plan/tasks +
  keyword-search, וקורא את הקוד. **קריאה, לא הרצה.**

**מה זה באמת**: מבקר-שלמות. עונה על "האם *כל* מה שה-spec ביקש אכן נבנה?" — **לא** על "האם
מה שנבנה עובד". סוגר לולאה של *כיסוי* חזרה ל-`implement`, בלי אף פעם להריץ את הקוד.

**המשמעות ל-BDS**: הפער שהוא ממלא **אמיתי** ו-BDS **חסר** אותו: BDS מאמת slice-slice
(אביגיל plan, כלב runtime לכל slice), אבל אין ל-BDS שלב "עצור, בחן את הפרויקט **השלם** מול
הכוונה המקורית — מה חסר, מה סותר, מה נכנס בלי שביקשו?". אפשר למזג 9 slices ירוקים ועדיין
לסטות מהכוונה הכוללת, או להשאיר תפרים בין slices שאף slice לא היה אחראי עליהם. זה בדיוק
הפער שConverge מכוון אליו — אבל בגישה סטטית.

### 1.4 /analyze — מכניקה, וחפיפה אמיתית לאביגיל

מקור: `templates/commands/analyze.md`. read-only, cross-artifact. passes (שורות 115-152):
duplication, ambiguity (vague adjectives / placeholders), underspecification, constitution
alignment, coverage gaps (requirement בלי task, task בלי requirement), inconsistency
(terminology drift, requirements סותרים, סדר-משימות).

**החפיפה לאביגיל — מדויקת**:

| | /analyze | אביגיל |
|--|----------|--------|
| ציר-בדיקה | עקביות **בין-מסמכים** (spec↔plan↔tasks↔constitution) | עובדתיות **מסמך-מול-קוד** |
| קורא קוד אמיתי? | **לא** | **כן** |
| תופס: "brief טוען שהפונקציה `foo()` קיימת, אבל אין כזו" | ❌ מבנית לא יכול | ✅ הליבה שלה |
| תופס: "spec אומר Next.js, plan אומר Vue" | ✅ | לרוב לא (בודקת קוד, לא סתירות פנימיות) |

הנקודה היחידה שנוגעים: /analyze מסמן "tasks referencing files not defined in spec/plan" —
אבל גם זה doc-vs-doc, לא doc-vs-code. **אביגיל תופסת מחלקת-באגים ש-/analyze לא יכול מבנית**:
brief עקבי-לחלוטין-פנימית אבל שגוי-עובדתית לגבי הקוד. זו בדיוק מחלקת ה-41%-briefs-דורשים-תיקון.

### 1.5 clarify / implement / checklist

- **clarify**: עד 5 שאלות רב-ברירה ממוקדות להסרת עמימות מה-spec, מקודד תשובות בחזרה ל-spec.md.
  ל-BDS אין אנלוג ישיר (מרדכי עושה זאת implicitly בכתיבת-brief; אין לולאת-clarify אינטראקטיבית).
- **implement**: מריץ tasks.md phase-by-phase. יש checklist-gate לפני התחלה (PASS/FAIL, שואל
  את המשתמש אם להמשיך). שלב 9 "Completion validation": "Validate that tests pass" — אבל זה
  **אותו סוכן שכתב את הקוד בודק את הטסטים של עצמו**, רק אם המשימות כללו טסטים, בלי סוכן-אימות
  עצמאי בסביבה נקייה. **אין runtime-gate נפרד.**
- **checklist**: מייצר checklists שגייטים את implement. מנגנון מעניין (ראה §4).

### 1.6 בידוד ואורקסטרציה

`create-new-feature.sh` יוצר `specs/NNN-slug/` + מחשב `BRANCH_NAME` + שומר `feature.json`.
**הוא לא עושה `git checkout -b` ולא worktree** (בגירסה זו אפילו יצירת-branch מנותקת, כנראה
כדי לתמוך ב-non-git). הבידוד הוא ברמת-תיקיית-ארטיפקטים בלבד. worktrees של BDS — הפיכות,
מקביליות, שרשור — חזקים מהותית יותר.

מנגנון נלווה חשוב: **hooks**. לכל פקודה יש `before_<cmd>` / `after_<cmd>` דרך
`.specify/extensions.yml`. זו הרחבה אלגנטית — עקרונית אפשר לתלות אימות-runtime כ-hook על
`after_implement` / `after_converge`. spec-kit עצמו **לא** משלח hook כזה.

---

## 2. הבשלות — harness בשל, efficacy לא-נמדדת

| מימד | ממצא |
|------|------|
| test-suite | 129 קבצים, 3150 פונקציות-טסט |
| מה הם מכסים | `bundler`, `catalog`, `integrations` (parity), `branch_numbering`, `check_prerequisites`, `extensions`, `hooks`, `bundler_security_paths`, `authentication` — **ה-plumbing** |
| מה הם **לא** מכסים | אף טסט שמריץ פרויקט-SDD מיוצר end-to-end, או שמודד אם converge/analyze תופסים באג אמיתי |
| קצב | v0.13.0, CHANGELOG פעיל מאוד, releases תכופים |

**ההבחנה "טענה מול קוד"**: spec-kit הוא **harness מצוין ליצירת-ארטיפקטים ואורקסטרציה** —
מיוצר, מלוטש, נבדק היטב *ככלי*. אבל היעילות של ה**שיטה** (האם התהליך תופס באגים) לא נמדדת
באף טסט. הדבר היחיד שבאמת "מריץ קוד" הוא סוכן-ה-implement שבודק את עצמו. מנגד, 307 דוחות-האימות
של BDS הם דווקא ראיית-**efficacy** (סוג-בשלות רלוונטי יותר לשאלה "האם זה תופס באגים"), גם אם
בקנה-מידה קטן ו-single-user.

---

## 3. שלושת הפערים — הערכה מחודשת

### 3.1 Constitution — ✅ לאמץ (אושר, ערך גבוה, אפס התנגשות)

- זול, קונקרטי, ערך גבוה. מרכז דוקטרינה שהיום מפוזרת בין mordechai/SKILL/AGENTS.
- **אפס התנגשות** עם מודל BDS — למעשה **מחזק** את אביגיל וכלב: שניהם יכולים לקרוא
  `<project>/constitution.md` כאילוץ-על (בדיוק כמו ש-/analyze ו-/converge עושים). הפרת
  עיקרון-MUST הופכת ל**מחלקת-blocker ממדרגה ראשונה** ב-plan-gate (אביגיל) וב-runtime-gate (כלב).
- מנגנון ה-Sync Impact Report + SemVer שווה חיקוי — חוקה עם היסטוריית-גירסאות.

### 3.2 Converge — 🟡 לאמץ את הרעיון, אבל למסגר מחדש (זה השינוי מהמסמך הקודם)

- **תיקון**: זה לא "הדבר הכי קרוב ל-runtime". זה **מבקר-שלמות סטטי**. הוא לא חופף לכלב.
- הפער שהוא ממלא **אמיתי** ל-BDS (שלמות-פרויקט-כולו מול אימות slice-slice).
- **אבל אסור לאמץ אותו כמו-שהוא**: ב-spec-kit הוא מוסיף-משימות-אוטומטית ולולאה בחזרה
  ל-implement באופן אוטונומי — זה **מפר** את merge-gate ואת סמכות-המתכנן של BDS.
- **גירסת-BDS**: read-only, בבעלות **מרדכי**, שמפיק **briefs חדשים** (לא מוסיף tasks
  אוטומטית), gated על-ידי מרדכי + משתמשת. ורצוי לזווג עם מעבר-**runtime של כלב** — כלומר
  BDS-Converge = שלמות-סטטית (סגנון spec-kit) **+** E2E-runtime (הסופר-כוח של BDS), שזה
  **חזק ממש מ-converge של spec-kit**. ראה skeleton ב-§5.

### 3.3 commands-UX — 🟡 לאמץ בררנית (הערך הכי נמוך מהשלושה)

- ה-slash-commands (discoverable, מתועדים) — UX טוב יותר מ-"הפעל סוכן דרך Task". אבל למקרה
  single-user quality-critical זה nice-to-have.
- **מה שכן שווה יותר מהקישוט**: (א) מנגנון ה-**hooks** (`before_`/`after_` פר-פקודה) — כך
  BDS יכול להפוך את כלב/אביגיל ל-pluggable; (ב) מנגנון ה-**checklist** שגייט את הביצוע.

---

## 4. מה spec-kit עושה טוב יותר מ-BDS (מוכח בקוד)

1. **Constitution כאזרח-ממדרגה-ראשונה** — governance ממורכז, מגורסן, נאכף-בהקשר על כל שלב.
   ל-BDS אין מקבילה.
2. **Converge כשלב-שלמות מפורש** — BDS מאמת slice-slice ואין לו "בחן את השלם". פער אמיתי.
3. **harness בשל ורחב** — CLI מלוטש, 30+ סוכנים, presets/extensions/bundler, מנגנון hooks,
   `/analyze` cross-artifact, `/clarify` אינטראקטיבי. BDS bespoke ומצומצם.
4. **/clarify** — לולאת הסרת-עמימות אינטראקטיבית לפני plan. ל-BDS אין.

## 5. מה BDS עושה טוב יותר (אושר ברמת-הקוד, לא רק README)

1. **אימות-runtime על-ידי סוכן עצמאי (כלב).** בשום מקום ב-spec-kit אין סוכן-אימות שמריץ את
   הקוד בסביבה נקייה. ה-"validation" של implement הוא הסוכן-שכתב-בודק-את-עצמו. זה crown-jewel
   שאושר: הקוד לא מכחיש אותו — הוא פשוט לא קיים אצלם.
2. **לולאת-הזיקוק.** אין ל-spec-kit feedback-loop שמשפר את השיטה מדוחות-אימות. (יש להם
   CHANGELOG אנושי, אבל לא זיקוק-אוטומטי מ-runtime findings.)
3. **merge-gate אנושי + worktree isolation.** ל-spec-kit אין מושג merge בכלל, ובידודו
   ברמת-תיקייה בלבד. BDS הפיך ובטוח יותר ל-quality-critical.
4. **אביגיל = עובדתיות-מול-קוד.** /analyze בודק עקביות-מסמכים; אביגיל תופסת briefs ששגויים
   עובדתית לגבי הקוד — מחלקה ש-/analyze לא יכול מבנית.

---

## 6. Skeleton: Converge כ-slice ב-BDS

> **שם עבודה**: `project-converge` — מבקר-שלמות-ודריפט של הפרויקט-השלם, בבעלות מרדכי,
> read-only, מפיק briefs (לא מוסיף tasks), gated אנושית. גירסה חזקה מ-spec-kit: מוסיף
> מעבר-runtime של כלב לצד השלמות-הסטטית.

```markdown
# Brief: project-converge — מבקר-שלמות-פרויקט

## מטרה
לסגור את הפער בין הכוונה-הכוללת של הפרויקט (specs/roadmap + constitution) לבין מה
שממומש בפועל ב-dev — אחרי סדרת slices. מפיק briefs-להשלמה, לא ממזג, לא נוגע בקוד.

## Owner: מרדכי (read-only). לא אליעזר, לא יתרו.

## קלט
- מקור-כוונה: docs/specs/*.md + roadmap + <project>/constitution.md (אילוץ-על)
- מצב-קוד: dev tip (אחרי merge של הגל האחרון)
- דוחות: reports/<project>/*-calev.md (מה כבר אומת ב-runtime)

## שני מסלולים (רצים יחד, זה מה שעושה אותנו חזקים מ-spec-kit)

### מסלול A — שלמות סטטית (בהשראת converge של spec-kit)
לכל requirement / success-criterion / עיקרון-constitution:
  בחן את הקוד ב-dev, סווג פער: missing / partial / contradicts / unrequested.
  severity: CRITICAL (הפרת MUST / P1 חסום) / HIGH / MEDIUM / LOW.
  APPEND-ONLY בתודעה: לא נוגעים בקוד, לא מוסיפים tasks — מייצרים רשימת-findings.

### מסלול B — שלמות-runtime (הסופר-כוח של BDS; אין ל-spec-kit)
הפעל כלב (calev-heavy) על dev המאוחד ב-E2E:
  - flows חוצי-slices (מה שאף slice בודד לא בדק — התפרים)
  - regressions בין slices שמוזגו
  - DoD ברמת-הפרויקט, לא ברמת-slice

## פלט (מרדכי כותב)
1. reports/<project>/converge-<date>.md — findings (A) + verdict כלב (B)
2. אם יש findings אקשן: מרדכי כותב briefs-להשלמה חדשים ל-docs/plans/ ומריץ אביגיל
   עליהם (הזרימה הרגילה) — לא מוסיף tasks אוטומטית.
3. אם converged נקי + כלב GO: "✅ הפרויקט תואם את הכוונה" → מרדכי מציג למשתמשת.

## Gate
המשתמשת מאשרת: (א) אילו findings הופכים ל-briefs, (ב) האם דוחים ידועים (עם תיעוד
ב-docs/decisions/<project>.md, כמו runtime-gate). מרדכי לא ממזג כלום מכאן — זה שלב-ראייה.

## Testing strategy: none (זה שלב-אבחון read-only; הבדיקות הן ב-briefs שהוא מייצר)
## Complexity: 6 → calev (light) למסלול B; אם הפרויקט גדול → 8+ → calev-heavy
## depends_on: [סדרת ה-slices שכבר מוזגה ל-dev]
```

**למה זה חזק מ-converge של spec-kit**: spec-kit עוצר ב-A (סטטי) ומזרים אוטומטית. BDS
מוסיף B (runtime E2E דרך כלב) ושומר את המתכנן+המשתמשת בלולאה. A תופס "לא נבנה"; B תופס
"נבנה אבל לא עובד / שבר משהו אחר". יחד — כיסוי-שלמות שלם.

---

## 7. האם spec-kit שולל את BDS? — לא. משלימים.

- **מרכז-הכובד של spec-kit**: authoring של ארטיפקטים + אורקסטרציה של סוכן שיממש אותם,
  עם לולאת-שלמות. זה עושה מצוין.
- **מרכז-הכובד של BDS**: אימות (runtime + plan) + שיפור-עצמי (זיקוק). זה עושה מצוין.
- אין ב-spec-kit אימות-runtime עצמאי ולא לולאת-שיפור-עצמי — אלה נשארים crown-jewels
  ייחודיים של BDS, **מאושר ברמת-הקוד**.
- אין ב-BDS constitution, converge, ו-harness בשל — אלה פערים אמיתיים שכדאי לסגור.

**המסקנה הסופית לא השתנתה: ללמוד, לא לעבור.** מה שהשתנה: המיסגור המדויק של Converge
(שלמות-סטטית, לא runtime), ההבנה ש-spec-kit *כן* עם gates אנושיים (ברמת-מסמך), וההבחנה
החדה ש-/analyze משלים ולא מחליף את אביגיל.

---

## 8. Backlog מעודכן

- **24. Constitution פר-פרויקט** — `<project>/constitution.md`; אביגיל+כלב קוראים כאילוץ-על;
  Sync Impact Report + SemVer. **עדיפות: גבוהה** (זול, ערך גבוה, אפס התנגשות).
- **25. project-converge slice** — מסלול A (שלמות סטטית) + מסלול B (כלב E2E), בבעלות מרדכי,
  מפיק briefs, gated. **עדיפות: גבוהה** (פער אמיתי; skeleton ב-§6). **מוסגר מחדש**: לא runtime,
  מבקר-שלמות; הזיווג עם כלב הוא התוספת שלנו.
- **26a. hooks pattern** — `before_`/`after_` פר-שלב כדי להפוך אביגיל/כלב ל-pluggable.
  **עדיפות: בינונית** (יותר ערך מ-slash-UX עצמו).
- **26b. checklist-gate** — checklists שגייטים ביצוע. **עדיפות: בינונית.**
- **26c. commands-UX (slash)** — קישוט discoverable. **עדיפות: נמוכה.**
- **27. /clarify-loop — שלב-חובה לפני חתימת-brief** (חדש מהמחקר; **הועלה בעדיפות**).
  לולאת הסרת-עמימות אינטראקטיבית: מרדכי סורק את ה-brief/spec, מזהה עמימויות **שמשנות
  ארכיטקטורה/מודל-נתונים/אבטחה/פירוק-משימות**, ושואל את המשתמשת **עד 5 שאלות רב-ברירה**
  (לא פתוחות), אחת-אחת, וכותב את התשובות **בחזרה ל-brief**. **עדיפות: בינונית-גבוהה.**
  **הרציונל**: 41% מה-briefs דורשים תיקון — חלק ניכר הוא הנחות-לא-מבוררות של מרדכי על
  פרטים קטנים. היום מרדכי עושה clarify *implicitly* — וזה בדיוק המקום שבו פרטים נופלים.
  הפיכתו לשלב **מפורש עם כללים** תופסת את הבאג מראש (במקום שאביגיל תתפוס אחר-כך או שאליעזר
  ייתקע). זול למימוש, תוקף ישירות את מספר-הכאב הגדול ביותר.
  כללי-מפתח לחיקוי מ-`clarify.md`: (א) רק שאלות high-impact; (ב) רב-ברירה עם אופציות
  מוכנות; (ג) מקסימום 5; (ד) התשובות מקודדות בחזרה למסמך כדי שלא ילכו לאיבוד; (ה) עצירה
  כשאין עוד עמימות מהותית.

> נדחה במפורש: מעבר ל-spec-kit. הרציונל (מאושר ברמת-הקוד): אובדן אימות-runtime עצמאי (כלב),
> זיקוק, ו-merge-gate+worktree. אף אחד מהשלושה לא קיים ב-spec-kit.
