# קטלוג טעויות-תכנון (אביגיל — plan-verifier)

> מבוסס על: **106 דוחות אביגיל ב-9 projects** (זיקוק 2026-06-27, ראה `distillations/2026-06-27-report.md`).
> hitrate: 87/106 דוחות עם ממצא (82%), ממוצע 2.74 ממצאים/דוח. 290 ממצאים סה"כ.
> מקביל ל-`patterns.md` (טעויות-ביצוע של אליעזר, מ-כלב).
>
> traceability דו-כיווני: כל קטגוריה מצביעה על הדוחות שיצרו אותה (`> מקורות:`).
> דוח-זיקוק מצביע על הכללים שעדכן (חלק 4 ב-`distillations/<date>-report.md`).
>
> **הקטגוריות מסודרות לפי תדירות בפועל** (לא לפי סדר היסטורי).

---

## קטגוריה 1: `wrong-line-number` — מספר-שורה לא-מדויק

**תדירות**: **הגבוהה ביותר — 63 ממצאים** (≈22% מכלל הממצאים).

**מנגנון**: ה-brief מצטט "‏§4 Commit 1 ‏שורה 129 ‏עושה X", אבל ה-base זז מאז שמרדכי כתב
את ה-brief (slice קודם נמרג, מרדכי הסתכל על main ולא על dev tip). רוב המקרים
**cosmetic** — הקוד עדיין נכון, רק המספר לא — אבל זה רעש שאליעזר חייב לפענח, ובמקרה
הגרוע מפנה אותו לשורה הלא-נכונה.

**הלקח המבני (לא רק finding)**: מספרי-שורות מוחלטים בבריף הם **חוב מובנה**. הם נכונים
ברגע הכתיבה ומתיישנים מיד. הפתרון אינו "לאמת טוב יותר את המספר" אלא **לא לעגן ב-מספר
מלכתחילה** — לעגן ב-symbol + grep pattern שמחזיק גם אחרי שהקובץ זז.

**הגנה**:
- ‏מרדכי (בכתיבת brief): במקום `שורות 468-490` → `block של <form class="text-form"> (grep: 'class="text-form"')`.
- ‏אביגיל (בדיקה): אמת ש-ה-**anchor** (symbol/pattern) קיים, לא שמספר-השורה מדויק.
  אם ה-brief בכל זאת נתן מספר — סמן 🟢 minor בלבד (cosmetic), לא בזבז זמן.
- ‏ראה כלל מעודכן ב-`agents/avigail.md` בדיקה 4 וב-`briefs/BRIEF_TEMPLATE.md` §4 (DELETE block).

> מקורות (43 דוחות): bds/slice-2-distillation, bds/slice-3-report-discipline, drive-coding/cache-headers-version, drive-coding/slice-P1a-provider-abstraction, drive-coding/slice-P1b-acp-adapter, drive-coding/slice-active-agents-backend, drive-coding/slice-active-processes-layout, ...

---

## קטגוריה 2: `outdated-risk` — סיכון/escalation מיושן

**תדירות**: **44 ממצאים** (#2).

**מנגנון**: §6 Risks / §7 Escalation של ה-brief מסתמך על learnings ישנים או על מצב-קוד
שכבר זז. הגוטשה כבר תוקנה ב-slice קודם, או ה-base tip השתנה וה-risk כבר לא חל. מבזבז
את זמן אליעזר על מיטיגציה מיותרת.

**הגנה**:
- ‏מרדכי: בזמן ה-finalize, רענן את §6 מול ה-**dev tip האמיתי** (לא main, לא slice קודם לא-merged).
  לכל risk: "האם הגוטשה עוד רלוונטית? האם ה-mitigation עוד עובד?"
- ‏אביגיל (בדיקה 7): פתח כל risk ב-§6/§7 ואמת שהוא עדיין חי. אם לא — 🟢 outdated.

> מקורות (32 דוחות): bds/slice-2-distillation, drive-coding/cache-headers-version, drive-coding/slice-P1a-provider-abstraction, drive-coding/slice-active-agents-backend, drive-coding/slice-agent-busy-indicator, drive-coding/slice-bunx-single-command, ...

---

## קטגוריה 3: `naming-inconsistency` — שם לא-עקבי בתוך ה-brief

**תדירות**: **32 ממצאים** (#3).

**מנגנון**: ה-brief קורא לאותו symbol בשני שמות (`listSessionsViaTempAgent` ב-§2,
`listSessionsForCwd` ב-§4). אליעזר בוחר אקראית — ואם בחר את השם שלא קיים בקוד, נתקע.

**הגנה**:
- ‏מרדכי: בחר שם **אחד** ל-symbol והשתמש בו בכל ה-brief. אם זה symbol קיים — העתק את שמו המדויק מהקוד (grep).
- ‏אביגיל (בדיקה 5): סרוק את ה-brief ל-symbols שמופיעים בשני שמות. 🟡 confusion.

> מקורות (28 דוחות): bds/slice-2-distillation, bds/slice-3-report-discipline, brief-driven-slices/slice-4-brief-commit-lifecycle, dev/slice-23-agent-options-panel, drive-coding/slice-P1b-acp-adapter, drive-coding/slice-latex-math, ...

---

## קטגוריה 4: `dropped-branch` — הפסאודו-קוד מחסיר ענף קיים

**תדירות**: **31 ממצאים** (#4). **הקטגוריה היקרה ביותר** — silent regression פוטנציאלי.

**מנגנון**: ה-brief מציג pseudo-code שאמור להחליף קוד קיים, אבל מחסיר ענף/קצה שהקוד
המקורי טיפל בו: `typeof === "string"` branch, null check, error handling, סדר-precedence,
policy שכבר מתועד בקוד, side-effect של layout שלא ב-§6 Risks. אליעזר מעתיק verbatim —
ושובר workflow קיים בלי שאף טסט יתפוס.

**דוגמאות מהדוחות**:
- ‏הוספת `style` ל-`ALLOWED_ATTR` סותרת policy מפורש בקוד שאוסר `style` כ-CSS-injection vector.
- ‏4 extensions ל-marked בלי לציין סדר block-before-inline → `$$` נאכל כשני `$`.
- ‏textarea auto-grow מותח את כפתור-השליחה ל-6 שורות — side-effect של flex שלא ב-Risks.

**הגנה**:
- ‏מרדכי: לכל pseudo-code שמחליף קוד — **קרא את הקוד המקורי** וודא שכל ענף מיוצג.
- ‏אביגיל (בדיקה 2): השווה pseudo-code לקוד הקיים. ענף חסר → 🔴 regression risk.

> מקורות (19 דוחות): bds/slice-2-distillation, dev/slice-23-agent-options-panel, drive-coding/slice-P1b-acp-adapter, drive-coding/slice-active-agents-backend, drive-coding/slice-agent-busy-indicator, drive-coding/slice-enter-toggle, drive-coding/slice-input-autogrow, ...

---

## קטגוריה 5: `wrong-path` — נתיב-קובץ לא-ממשי (כולל gitignore-trap)

**תדירות**: **25 ממצאים** (#5).

**מנגנון**: ה-brief מציין נתיב שגוי — ספריה לא קיימת, קובץ בשם אחר, או (המסוכן)
ספרייה בשם ש-`.gitignore` תופס בכל עומק (`reports/`, `.codenomad/`) → הקבצים החדשים
לא יתועדו ב-git בשקט.

**הגנה**:
- ‏לכל נתיב חדש ב-brief: `git check-ignore -v <path>` לפני שמגדירים אותו.
- ‏בספריות tests/fixtures — לעולם לא שם שקיים ב-.gitignore.
- ‏אביגיל (בדיקה 6): אמת שכל ספריית-אב קיימת, ושאין התנגשות-שם או gitignore-trap.

> מקורות (21 דוחות): bds/slice-2-distillation, bds/slice-3-report-discipline, drive-coding/slice-P1a-provider-abstraction, drive-coding/slice-P1b-acp-adapter, drive-coding/slice-active-agents-backend, drive-coding/slice-remove-idle-reaper, drive-coding/slice-session-prefs-per-cwd, ...

---

## קטגוריה 6: `missing-symbol` / `type-error` — symbol שלא קיים / שגיאת-טיפוס צפויה

**תדירות**: **20 + 20 ממצאים** (#6, מאוחדים — שניהם נתפסים ב-grep/typecheck-mental).

**מנגנון (missing-symbol)**: ה-brief מניח class/function/method שקיים — אבל הוא ב-`main`
ולא ב-`dev` (ה-base של ה-slice), בקובץ אחר, או נמחק. אליעזר נתקע ב-Commit 0.
זוהי בדיוק **טעות ה-dev/main parity** (recommendations.md §12).

**מנגנון (type-error)**: pseudo-code שלא מטפל ב-`noUncheckedIndexedAccess` (צריך `?`/cast),
`verbatimModuleSyntax` (`import type` מפורש) → אליעזר נתקע ב-typecheck.

**הגנה**:
- ‏אביגיל (בדיקות 1+3): לכל symbol — `grep -n "<symbol>"` ב-**dev tip בפועל** (לא main).
  חסר → 🔴 blocker. לכל array-access/import ב-pseudo-code — בדוק תאימות strict-TS → 🟡.

> מקורות missing-symbol (12): drive-coding/cache-headers-version, drive-coding/slice-P1a-provider-abstraction, drive-coding/slice-latex-math, drive-coding/slice-session-prefs-per-cwd, learn-games-project/slice-4-find-letter-kit-adoption, ...
> מקורות type-error (14): dev/slice-23-agent-options-panel, drive-coding/slice-P1a-provider-abstraction, drive-coding/slice-P1b-acp-adapter, drive-coding/slice-agent-busy-indicator, drive-coding/slice-bundle-single-artifact, ...

---

## קטגוריה 7: `missing-dependency` — הנחה לא-מאומתת על כלי/lib/env

**תדירות**: **15 ממצאים** (#7). הקטגוריה ההיסטורית הראשונה (זיקוק 2026-06-01).

**מנגנון**: ה-brief מניח ש-X קיים/זמין/עובד בלי לאמת. כשאליעזר מגיע — נתקע.

**דוגמאות**: `yq` (לא מותקן), `PyYAML` (כן זמין, 6.0.2 — ה-brief הניח שלא), exit-code של
`opencode run` (תמיד 0, גם בכשל), pytest (לא מותקן).

**הגנה**:
- ‏מרדכי: `env -i /usr/bin/python3 -c "import <lib>"` לפני שכותבים `import <lib>`. תעד ב-§6.
- ‏אביגיל (בדיקה 1): לכל tool/lib/API שה-brief מניח — אמת ב-env ממשי.

> מקורות (12 דוחות): bds/slice-2-distillation, dev/slice-23-agent-options-panel, drive-coding/slice-P1b-acp-adapter, drive-coding/slice-active-agents-widget, drive-coding/slice-session-prefs-per-cwd, learn-games-project/slice-4-find-letter-kit-adoption, ...

---

## זנב ארוך: קטגוריות-singleton (מועמדות-קנון עתידיות)

הזיקוק זיהה ~13 קטגוריות לא-קנוניות, רובן ממצא בודד: `algorithm-gap`,
`logic-inconsistency`, `spec-gap`, `type-mismatch`, `stale-state`, `typecheck-risk`,
`style-inconsistency`, `error-isolation`, `wrong-symbol`, ובנוסף `cross-verification` (8)
ו-`unique` (17).

**הכרעה (2026-06-27)**: לא מקדמים אף אחת לקנון עדיין — נפח לא מצדיק. **חריג לבחינה**:
`cross-verification` (8) — אביגיל מאמתת ממצא של אביגיל קודמת בסבב חוזר; אם יחצה 12+ בזיקוק
הבא, ראוי לקטגוריה. `unique` הגבוה (17) תקין לצד plan-verifier — בריפים מגוונים מטבעם.

> מקורות cross-verification (8): ראה `trace` ב-`distillations/2026-06-27-data.json`.
