# תוכנית טרום-בריף — הפרדה בין תוכניות לבריפים

> **תאריך**: 2026-06-08
> **סטטוס**: תוכנית טרום-בריף / רעיון מבני
> **חשוב**: זה **לא בריף**. אין להריץ את המסמך הזה מול אליעזר, אין לפתוח ממנו worktree, ואין לסמן אותו `plan_verified`.
> **מטרה**: ליישר את מבנה המסמכים של BDS כך שתוכניות מעורפלות יחיו בנפרד מבריפים ביצועיים ומאומתים.

---

## §1 — למה צריך את ההפרדה

כרגע הפרויקט משתמש ב-`docs/plans/` לשני סוגי מסמכים שונים:

- תוכניות טרום-בריף: רעיונות, מפרטים חלקיים, חקירות, כיווני פעולה, מסמכים שעדיין לא אומתו מול המציאות בשטח.
- בריפים ביצועיים: מסמכים מפורטים שמיועדים לאביגיל, אליעזר, כלב ויתרו; יש בהם commits, DoD, תלויות, base, strategy, ונתיבי dispatch.

הערבוב הזה יוצר בעיה מתודולוגית: עצם זה שמסמך נמצא ב-`docs/plans/` לא אומר אם הוא עדיין רעיון מעורפל או כבר חוזה ביצוע. אליעזר צריך לקבל רק בריף. מרדכי, לעומת זאת, צריך מקום לשמור תוכניות לא-מוכנות בלי שהן ייראו כמשהו dispatchable.

הדוגמה הברורה כרגע היא `docs/plans/spec-init-project-bootstrap.md`: הוא מצהיר בעצמו שזה לא בריף מלא, אלא מפרט לצירוף לסלייס הבא. לעומתו `docs/plans/slice-3-report-discipline.md` ו-`docs/plans/slice-4-brief-commit-lifecycle.md` הם בריפים ממשיים. שניהם נמצאים באותה תיקייה.

---

## §2 — הגדרות עבודה

### תוכנית

תוכנית היא חומר עבודה של מרדכי לפני כתיבת בריף.

תוכנית יכולה לכלול:

- בעיה או פער שזוהו.
- כיוון פתרון ראשוני.
- שאלות פתוחות.
- הנחות שעדיין צריך לאמת מול הקוד.
- רעיונות לחלוקה לסלייסים.
- רשימת קבצים/מסמכים שכדאי לקרוא בעת כתיבת הבריף.
- הצעת complexity ראשונית, בלי התחייבות.

תוכנית לא חייבת לכלול:

- commits מדויקים.
- DoD מלא.
- verification commands.
- line numbers מאומתים.
- base commit.
- worktree setup.
- החלטות סופיות.

תוכנית **לא** עוברת לאליעזר.

### בריף

בריף הוא חוזה ביצוע לסלייס יחיד.

בריף חייב לכלול:

- מטרה מנקודת מבט המשתמשת.
- scope ברור: מה כן ומה לא.
- `depends_on` מפורש, גם אם ריק.
- base branch או branch תלות.
- Pre-flight מספיק מפורט לסוכן חדש.
- reading list עם must-read/reference.
- commits בסדר ביצוע.
- testing strategy לכל commit.
- DoD verifiable.
- risks + mitigations.
- escalation triggers.
- complexity + verifier tier.

בריף הוא מה שאביגיל בודקת, מה שאליעזר מבצע, ומה שכלב מאמת מול DoD.

---

## §3 — מבנה יעד מוצע

מבנה יעד אפשרי:

```text
docs/
├── plans/
│   ├── active/
│   │   └── <topic>.md              # תוכניות טרום-בריף פעילות
│   └── archive/
│       └── <topic>.md              # תוכניות ישנות / תוכניות שהפכו לבריפים
├── briefs/
│   ├── active/
│   │   └── <slice>.md              # בריפים בתהליך כתיבה/אימות/ביצוע
│   └── archive/
│       └── <slice>.md              # בריפים שבוצעו / נזרקו / מוזגו
└── decisions/
```

חלופה מינימלית יותר:

```text
docs/
├── plans/
│   ├── <topic>.md
│   └── archive/
├── briefs/
│   ├── <slice>.md
│   └── archive/
└── decisions/
```

החלופה המינימלית כנראה מספיקה עכשיו. `active/` מוסיף סדר, אבל גם מוסיף עוד רמה לכל path. אם אין צורך ממשי, עדיף להתחיל פשוט.

---

## §4 — משמעות שינוי הנתיבים

אם מאמצים את ההפרדה, צריך לעדכן את כל המקומות שבהם `docs/plans/<slice>.md` משמש בפועל בתור בריף.

אזורים שצריך לעדכן:

- `workflow.md` — שלב כתיבת בריף, plan-gate, dispatch, runtime verification.
- `orchestration.md` — שדה `brief`, status machine, דוגמאות Mode 2.
- `briefs/state.template.json` — נתיבי בריפים ב-state.
- `agents/mordechai.md` והמקור ב-`agent-definitions/prompts/mordechai.md` — כתיבת בריפים, אביגיל, dispatch לאליעזר.
- `agents/eliezer.md` והמקור ב-`agent-definitions/prompts/eliezer.md` — קריאת בריף ועדכון סטטוס בסוף.
- `agents/yetro.md` והמקור ב-`agent-definitions/prompts/yetro.md` — dispatch prompt וארכוב.
- `agents/avigail.md`, `agents/calev.md`, `agents/calev-heavy.md` — ניסוח נתיבי בריף בדוחות וב-prompts.
- `cli-configs/` — תוצרים generated; לא לערוך ישירות, אלא להריץ generator אחרי שינוי המקור.
- `SKILL.md` — מפת הקבצים והנחיות השיטה.
- `README.md` — map of repo.

חשוב: `briefs/` בשורש כבר קיים ומשמש לתבניות (`BRIEF_TEMPLATE.md`, `EXECUTOR_DISPATCH.md`, `state.template.json`). אם יוצרים `docs/briefs/`, צריך להבהיר היטב את ההבדל:

- `briefs/` = templates/tooling.
- `docs/briefs/` = בריפים חיים/היסטוריים.

אם ההבחנה הזו מבלבלת מדי, אפשר לשקול שינוי עתידי של `briefs/` ל-`templates/briefs/`, אבל זה לא חייב להיות באותו סלייס.

---

## §5 — מחזור חיים מוצע

### תוכנית

1. מרדכי כותב תוכנית ב-`docs/plans/<topic>.md`.
2. התוכנית מסומנת בבירור כ-`תוכנית טרום-בריף`.
3. מרדכי או אביגיל-לייט יכולים להשתמש בה כדי לאתר פערי מציאות, אבל היא לא עוברת לאליעזר.
4. כשמגיע הזמן לבצע, מרדכי כותב בריף חדש ב-`docs/briefs/<slice>.md`.
5. התוכנית נשארת כ-reference או עוברת ל-`docs/plans/archive/`.

### בריף

1. מרדכי כותב בריף ב-`docs/briefs/<slice>.md` לפי `briefs/BRIEF_TEMPLATE.md`.
2. הבריף committed ל-base כטיוטה.
3. אביגיל בודקת את הבריף מול הקוד בפועל.
4. מרדכי מתקן עד verdict `READY`.
5. הבריף committed ל-base כמאושר.
6. רק אז נפתח worktree / מתבצע dispatch.
7. אליעזר מעדכן status וסטיות רק ב-worktree.
8. בסוף, אחרי GO ומיזוג מאושר, הבריף עובר ל-`docs/briefs/archive/`.

---

## §6 — כללים למניעת בלבול

כל תוכנית טרום-בריף צריכה לפתוח בבלוק מפורש:

```markdown
> **חשוב**: זה לא בריף. אין להריץ מול אליעזר, אין לפתוח ממנו worktree, ואין לסמן אותו plan_verified.
```

כל בריף צריך לפתוח בבלוק הפוך:

```markdown
> **סוג מסמך**: בריף ביצועי לסלייס.
> **Dispatch**: מותר רק אחרי אביגיל READY ו-commit ל-base.
```

בנוסף, אביגיל צריכה לסמן כ-blocker מצב שבו מרדכי מבקש ממנה לאמת מסמך שמסומן כטרום-בריף במקום כבריף.

אליעזר צריך לסמן BLOCKED אם קיבל מסמך שאומר במפורש “זה לא בריף”.

---

## §7 — מיגרציה ראשונית מוצעת

מיפוי ראשוני של הקבצים הקיימים:

| קובץ נוכחי | סוג בפועל | יעד מוצע |
|-----------|-----------|----------|
| `docs/plans/orchestration-design.md` | תוכנית/עיצוב רחב | `docs/plans/archive/orchestration-design.md` או להשאיר כתוכנית reference |
| `docs/plans/spec-init-project-bootstrap.md` | תוכנית טרום-בריף | `docs/plans/spec-init-project-bootstrap.md` או `docs/plans/active/spec-init-project-bootstrap.md` |
| `docs/plans/slice-bds-extraction-and-reporting.md` | בריף היסטורי | `docs/briefs/archive/slice-bds-extraction-and-reporting.md` |
| `docs/plans/slice-2-distillation.md` | בריף היסטורי שהושלם | `docs/briefs/archive/slice-2-distillation.md` |
| `docs/plans/slice-3-report-discipline.md` | בריף היסטורי / מאומת | `docs/briefs/archive/` או `docs/briefs/active/` לפי מצב merge בפועל |
| `docs/plans/slice-4-brief-commit-lifecycle.md` | בריף מאושר שטרם בוצע | `docs/briefs/active/slice-4-brief-commit-lifecycle.md`, אחרי התאמה לנתיבים החדשים |

הערה: לפני הזזת בריפים היסטוריים צריך להיזהר עם דוחות קיימים שמפנים לנתיב המקורי. ייתכן שנרצה להשאיר קובץ redirect קצר או לבצע את המיגרציה בסלייס מתועד היטב.

---

## §8 — השפעה על slice-4 הקיים

`slice-4-brief-commit-lifecycle.md` כבר עוסק במחזור החיים של commit ה-brief. אם מאמצים את ההפרדה בין תוכניות לבריפים, לא כדאי לבצע אותו כפי שהוא בלי עדכון.

הסיבה: הוא ממשיך להניח שבריפים חיים ב-`docs/plans/<slice>.md`. אם נריץ אותו לפני שינוי ההפרדה, הוא יקבע עוד יותר את הנתיב הישן בשיטה.

אפשרויות:

1. להחליף את slice-4 בסלייס חדש שמטפל יחד במחזור חיים + הפרדת `plans`/`briefs`.
2. לעדכן את slice-4 כך שהנתיב החדש יהיה `docs/briefs/<slice>.md`.
3. לבצע slice קטן קודם: רק שינוי מבנה ונתיבים. אחריו לבצע slice-4 מעודכן על מחזור חיים.

האפשרות השלישית כנראה הכי נקייה: קודם מסדירים איפה בריפים חיים, אחר כך מסדירים מתי מקמטים אותם.

---

## §9 — שאלות פתוחות לפני כתיבת בריף

| # | שאלה | ברירת מחדל מוצעת | חוסם? |
|---|------|------------------|-------|
| 1 | האם להשתמש ב-`docs/briefs/` למרות שיש כבר `briefs/` לתבניות? | כן, עם הסבר ברור ב-README וב-SKILL | כן |
| 2 | האם ליצור `active/` או להשאיר מבנה שטוח עם `archive/` בלבד? | מבנה שטוח: `docs/briefs/<slice>.md` + `docs/briefs/archive/` | לא |
| 3 | האם להעביר בריפים היסטוריים מיד או רק בריפים חדשים? | להעביר בסלייס מסודר אחד, עם עדכון references | לא |
| 4 | האם `docs/plans/` צריך archive משלו? | כן, כדי לא לערבב רעיונות ישנים עם טרום-בריפים פעילים | לא |
| 5 | האם state status `planned` צריך להצביע למסמך plan? | לא בשלב ראשון; state מנהל רק slices עם brief | לא |

---

## §10 — הצעת סלייס עתידי

שם אפשרי: `slice-5-plan-brief-separation`.

מטרת הסלייס: להפריד במתודולוגיה בין תוכניות טרום-בריף לבין בריפים ביצועיים, כולל שינוי נתיבים, עדכון הסוכנים, עדכון templates, ועדכון state examples.

גבולות מוצעים:

- כן: יצירת `docs/briefs/` ו-`docs/briefs/archive/`.
- כן: עדכון כל ההפניות מ-`docs/plans/<slice>.md` ל-`docs/briefs/<slice>.md` בהקשר של בריפים.
- כן: הוספת הנחיות ברורות ל-`docs/plans/` כתוכניות טרום-בריף.
- כן: עדכון `README.md`, `workflow.md`, `orchestration.md`, `SKILL.md`, agent prompts, ו-state template.
- כן: עדכון `slice-4-brief-commit-lifecycle.md` או דחייתו עד אחרי הסלייס הזה.
- לא: שינוי לוגיקת יתרו מעבר לנתיבי dispatch/archive.
- לא: שינוי פורמט הדוחות.
- לא: שינוי names/roles של הסוכנים.

DoD אפשרי לבריף העתידי:

- אין יותר הפניות ל-`docs/plans/<slice>.md` כשמדובר בבריף dispatchable.
- יש הסבר ברור ש-`docs/plans/` הוא טרום-בריף בלבד.
- `briefs/` הקיים מוסבר כתיקיית templates, לא כתיקיית בריפים חיים.
- אביגיל/אליעזר/יתרו/כלב כולם משתמשים בנתיב החדש לבריפים.
- `state.template.json` משתמש ב-`docs/briefs/<slice>.md`.
- `README.md` ו-`SKILL.md` משקפים את מבנה הריפו החדש.
- מסמך זה נשאר כ-reference או עובר ל-`docs/plans/archive/` אחרי שהבריף נכתב.

---

## §11 — איך להשתמש במסמך הזה

המסמך הזה הוא חומר גלם למרדכי.

כדי להפוך אותו לבריף, צריך לבצע סבב כתיבה חדש:

1. לקרוא את המסמך הזה.
2. לבדוק בפועל את כל ההפניות הקיימות ל-`docs/plans/` ול-`briefs/`.
3. לבחור מבנה יעד סופי.
4. לכתוב בריף חדש לפי `briefs/BRIEF_TEMPLATE.md`.
5. להריץ אביגיל על הבריף החדש.

עד אז: המסמך הזה נשאר **תוכנית טרום-בריף**, לא מקור dispatch.
