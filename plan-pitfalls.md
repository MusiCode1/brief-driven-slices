# קטלוג טעויות-תכנון (אביגיל — plan-verifier)

> מבוסס על: 12 דוחות ב-7 projects (נכון ל-2026-06-01). יתעדכן בכל זיקוק.
> מקביל ל-`patterns.md` (טעויות-ביצוע של אליעזר).
>
> traceability דו-כיווני: כל קטגוריה מצביעה על הדוחות שיצרו אותה (`> מקורות:`).
> דוח-זיקוק מצביע על הכללים שעדכן (חלק 4 ב-`distillations/TEMPLATE-report.md`).

---

## קטגוריה 1: הנחה לא-מאומתת על כלי/API/סביבה

**תדירות**: גבוהה (הקטגוריה הנפוצה ביותר בדוחות אביגיל — 3 מתוך 3 ב-bds).

**מנגנון**: ה-brief מניח ש-X קיים/זמין/עובד, בלי לאמת. כשאליעזר מגיע לשלב הזה — הוא מתקע.

**דוגמאות מהדוחות**:
- `yq` — ה-brief הניח שהוא מותקן. אינו. (bds-extraction, avigail סבב 1)
- `PyYAML` — ה-brief הניח שאינו זמין. הוא כן זמין (6.0.2). (slice-2, avigail סבב 1)
- exit-code `opencode run` — ה-brief הניח ש-exit 0=הצלחה. תמיד 0, גם בכשל.
- pytest — ה-brief יצר dependency על pytest שאינו מותקן.

**הגנה**:
- לכל tool/lib/API שה-brief מניח: **אמת ב-env ממשי** לפני ה-finalize.
- מרדכי: `env -i /usr/bin/python3 -c "import <lib>"` לפני שכותבים `import <lib>`.
- תעד את האימות ב-§6 Risk ("אומת: `env -i ... → <version>`").

> מקורות: reports/bds/bds-extraction-avigail-v1.json, reports/bds/slice-2-distillation-avigail-v1.json, reports/bds/slice-2-distillation-avigail-v2.json

---

## קטגוריה 2: file path לא-ממשי (wrong-path / gitignore-trap)

**תדירות**: בינונית (2 מתוך 3 ב-bds, אחד מהם regression שמרדכי עצמו הכניס).

**מנגנון**: ה-brief מציין נתיב לקובץ חדש/קיים שהוא שגוי — ספריה לא קיימת, קובץ בשם אחר,
או (המקרה המסוכן) ספרייה בשם ש-.gitignore תופס.

**דוגמאות מהדוחות**:
- `tests/fixtures/reports/` — gitignore תופס `reports/` בכל עומק. ה-fixtures לא יתועדו. (slice-2, avigail סבב 2 — regression שמרדכי הכניס בתיקון אחר)
- קובץ שה-brief אמר "יש ב-dev" ואינו שם.

**הגנה**:
- לכל נתיב חדש ב-brief: `git check-ignore -v <path>` לפני שמגדירים אותו.
- בספריות tests/fixtures — **לעולם לא** להשתמש בשם שקיים ב-.gitignore (`reports/`, `.codenomad/` וכו').

> מקורות: reports/bds/slice-2-distillation-avigail-v2.json

---

## קטגוריה 3: line number לא-מדויק / naming inconsistency (placeholder)

> מקום לקטגוריה שתעלה מזיקוקים עתידיים.

---

## קטגוריה X (placeholder)

> מקום לקטגוריה חדשה מהזיקוק הבא.
