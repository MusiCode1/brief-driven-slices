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

## קטגוריה 8: `unrun-claim` — טענה עובדתית על הקוד שלא הורצה

**תדירות**: **3 מתוך 3 החוסמים** ב-slice-7 (‏obsidian-eq-checker), ותשעה מ-79 הממצאים
ב-slice-5. חדשה בזיקוק 2026-08-02 — ולפי היחס, **מועמדת ל-#1**.

**מנגנון**: ה-brief (או תיקון ל-brief) נושא טענה על הקוד — מה פונקציה מחזירה, כמה
פעמים מחרוזת מופיעה, מה אורך מערך — שנכתבה **מהזיכרון ולא מהרצה**. הטענה סבירה,
לפעמים אפילו נכונה-בעבר, והיא שגויה. אביגיל מוצאת אותה בסבב הבא בעלות של סבב מלא.

**דוגמאות מדודות**:

```
‏נכתב:  lastOut = {items, out}        ‏בפועל: return { items, out, autoOrigin }
‏נכתב:  DoD ‏סורק גם scripts/          ‏בפועל: ‏המחרוזת מופיעה שם 3 ‏פעמים — ‏השער אדום מיידית
‏נכתב:  rows[i] = out[i] + items[i]   ‏בפועל: out.length < items.length
```

**המנגנון שמאחורי המנגנון**: מיקור-חוץ של האימות מוריד את הזהירות במעלה הזרם. אותו
סוכן, אותו יום — קוד ספייק (**אין מאמת אחריו**) הורץ מיד ותפס 4 באגים בעצמו; ה-brief
(**יש מאמת**) נכתב מהזיכרון וייצר 3 חוסמים.

**הגנה**:
- **מרדכי**: לפני מסירה לאימות — לעבור על כל טענה עובדתית ולשאול "הרצתי את זה?".
  מה שלא הורץ — או שיורץ, או שמסומן ב-§0 כלא-מאומת עם הוראה מפורשת לאליעזר לבדוק.
- **אביגיל**: לסווג ממצא כ-`unrun-claim` כשהוא היה נתפס **בפקודה אחת** ע"י הכותב.
  היחס הזה הוא מדד "יעילות המאמת" — גבוה = הזהירות במעלה הזרם צנחה.
- **הצורה, לא המשמעת**: טענה נכתבת יחד עם הפקודה שהפיקה אותה, כך ש**אי אפשר לכתוב
  את השורה בלי להריץ אותה**. זה מה שהלינטר (`recommendations.md` פריט 34) הופך למכני.

> מקורות: `case-studies/RAW-2026-08-verification-cost.md` §22–§25 · obsidian-eq-checker slice-5, slice-7

---

## קטגוריה 9: `intermediate-state-unverified` — Verification נמדד ביעד, לא ברצף

**תדירות**: החוסם שתשעה סבבי אימות **לא** מצאו (obsidian-web R0). ביצוע אחד מצא אותו
ב-8 דקות.

**מנגנון**: ה-brief מתאר **רצף commits**, והאימות בודק את **מצב הסיום**. אביגיל מדדה
`tsc --build` ארבע פעמים בשלוש גרסאות TypeScript — ובכל פעם בנתה סקרץ' עם **כל
הקבצים במקום**. ‏Commit 1 יוצר `tsconfig.json` עם `include: ["fs/**/*.ts"]`; הקבצים
נוצרים ב-Commit 2. ה-Verification של Commit 1 (`typecheck` → exit 0) **לא יכול היה
לעבור**: `TS18003: No inputs were found`.

זו לא טעות נקודתית של מאמת אחד — זו **נקודה עיוורת מבנית** של אימות-brief.

**הגנה**:
- ‏אביגיל: כל Verification שמריץ כלי-בנייה גלובלי (`tsc --build`, `bun run test`,
  `npm run build`) נמדד **במצב שאותו commit משאיר**, לא במצב הסופי.
- ‏מרדכי: אחרי 3 סבבים ללא 🔴 חדש — ביצוע-זריק על worktree. זו המחלקה שאימות סטטי
  **אינו יכול** לתפוס (`recommendations.md` פריט 28).

> מקורות: `case-studies/2026-07-obsidian-web-r0-nine-rounds.md` §2, §10

---

## קטגוריה 10: `gate-cannot-fail` — שער שלא יכול להבחין בין הצלחה לכישלון

**תדירות**: 4+ ממצאים בשני התיקים, מהם אחד חוסם. שלושה תת-מצבים.

**מנגנון א — עובר ירוק בלי קשר**: `npm install` כשער-רגרסיה עבר ירוק תמיד, כי npm
מטפס לשורש ה-workspace ומצליח בכל מקרה. אותו שער גם **ייצר בעצמו** `package-lock.json`
בשורש — בעוד כלל ההחרגה הגיע רק ב-commit הבא.

**מנגנון ב — כבר אדום/ירוק על הבסיס**:
> **שער שכבר אדום על הבסיס אינו שער. שער שכבר ירוק על הבסיס גם אינו שער** — הוא לא
> מודד את הסלייס.

**מנגנון ג — הפקודה מבנית לא יכולה למצוא**: `grep -rn "resolve-safe" src/` הוגדר
כ"אפס תוצאות = הצלחה". קובץ אחד מכיל 2 בתי NUL, GNU grep מסווג אותו כבינארי ומחזיר
**exit 1 בלי פלט** — כלומר "אפס תוצאות" בזמן שהייבוא עדיין שם. ובנפרד: `grep -c X`
מחזיר **exit 1 כשהספירה אפס** — המקרה **המצליח** נראה ככישלון תחת `set -e`.

**הגנה**:
- ‏אביגיל: **פקודת-אימות היא קוד.** להריץ כל פקודת-Verification על הקוד הנוכחי
  ולוודא שהיא **מבחינה** בין הצלחה לכישלון — לא רק שהיא "נראית נכונה".
  ‏`grep -a` כברירת-מחדל בריפו שיש בו בינארי.
- ‏מרדכי: להריץ כל שער DoD על קומיט הבסיס לפני שנגעו במשהו.
- **שער השוואתי**: כשמפתח נכנס לראשונה — לספור **ערכים שונים**. קריסה-לקבוע היא
  חתימה מדידה של קריאה בצורה שגויה (‏`--distinct`, סף 3).

**מנגנון ד — אימות-ציטוט אינו שער** (‏נוסף בזיקוק 2026-08-04): "‏הרג'קס צוטט
verbatim" · "‏אפס `wrong-line-number`" · "‏שם הפונקציה נכון" — כל אלה **‏ירוקים תמיד**
‏על brief שנכתב בעיון, ‏ואינם מודדים דבר על הסלייס. ‏ב-slice-4 הם היו ירוקים בעשרה
‏סבבים רצופים בזמן שהקוד המצוטט היה שגוי לצורך השינוי (‏קטגוריה 11).
‏**‏אימות נאמנות אינו אימות הלימה.**

> מקורות: `case-studies/2026-07-obsidian-web-r0-nine-rounds.md` §3, §5 ·
> `case-studies/RAW-2026-08-verification-cost.md` §6, §16

---

## קטגוריה 11: `faithful-but-inadequate` — התיאור נכון, והקוד המתואר עומד להישבר

**תדירות**: החוסם שעשרה סבבי אימות לא מצאו (eq-checker slice-4). חדשה בזיקוק 2026-08-04.

**מנגנון**: ה-brief מצטט קוד קיים **נכון**, האימות מוודא שהציטוט נאמן — והוא נאמן.
השאלה שלא נשאלת היא אם הקוד המצוטט **שורד את השינוי שהסלייס מכניס**.

**המקרה המדוד**: הסלייס מוסיף סוג-סימון רביעי `⚠` לצד `✓✗⊘`. אביגיל אימתה על פני
עשרה סבבים ש-`LEAD = /^\s*[✓✗⊘]\s+/` מצוטט **"נכון מילה במילה"**, ורשמה "אפס
`wrong-line-number`, שני סבבים ברציפות". הרג'קס אכן צוטט נכון. הוא גם היה בדיוק
הרג'קס שהיה צריך להוסיף לו `⚠`. כלב תפס בהרצה הראשונה:
`applyMarks` צובר `⚠ ⚠` במקום להחליף. ‏**NO-GO.**

**זו ההפך מקטגוריה 8** (`unrun-claim`): שם הטענה לא אומתה והייתה שגויה; כאן היא
אומתה, הייתה נכונה, **ולא רלוונטית**.

**הגנה**:
- ‏אביגיל: לכל **סמל קיים** שה-brief מצטט (רג'קס, enum, טבלת-קבועים, union type) —
  שתי שאלות ולא אחת: (‏א) האם הוא מצוטט נכון? (‏ב) **האם הוא שורד את השינוי?**
  ‏(ב) הוא היחיד שיכול להחזיר 🔴 על קוד שהתיאור שלו מושלם.
- **הסימן המחשיד**: סלייס שמוסיף איבר לקבוצה סגורה (סימון, סטטוס, סוג-אירוע).
  לכל צרכן של הקבוצה — האם הוא מונה את האיברים במפורש?
- ‏מרדכי: רשימת-צרכנים בבריף אינה תיעוד, היא **שאילתה**. אם `grep` על הסמל מחזיר
  ‏4 אתרים וה-brief מונה 2 — זה 🔴, גם אם ה-2 מתוארים נכון.

> מקורות: `case-studies/2026-08-eq-checker-slice4-ten-rounds.md` §2 ·
> obsidian-eq-checker slice-4 (r1–r10 + commit2-calev NO-GO)

---

## קטגוריה 12: `convention-violation` — הבריף מנחה לעבור על כלל של הפרויקט

**תדירות**: חוסם אחד ב-drive-coding `cli-bin-resolution-unify` (2026-08-16), ש**שרד שלושה
סבבי אביגיל, אימות-phase של כלב ואימות-סיום של כלב** — כולם READY/GO. נתפס ע"י המשתמשת
אחרי שהקוד כבר נכתב, אומת, נבנה והוגש ב-preview.

**המנגנון**: הבריף היה **נכון מול הקוד** בכל טענה — ולכן עבר כל שער. הוא היה **שגוי מול
`AGENTS.md`**. מרדכי הנחה במפורש:

> *"המטמון הוא `Map` ברמת-המודול, ב-`packages/core/src/cli-resolve.ts` עצמו"*

בעוד `AGENTS.md` של הפרויקט קובע:

```
packages/core/ — pure logic, no IO
Functional core / imperative shell — pure in core, IO in backend
```

**מה שהפך את ההפרה לסבירה בעיני מרדכי**: הוא ציטט כתקדים את `cli-config-file.ts`,
שבאמת ממטמן ברמת-המודול — אבל יושב ב-`packages/provider`, כלומר ב**קליפה**, שם זה מותר.
**תקדים מהקליפה הוחל על הליבה.** בנוסף, קובץ-היעד מכריז בכותרתו *"Pure + synchronous"*
בזמן שהוא קורא `fs.existsSync` — כלומר הקובץ עצמו כבר מודל את הדבר הלא-נכון.

**למה אף שער לא תפס:**

| שער | מה בודק | למה פספס |
|---|---|---|
| אביגיל | brief ↔ **קוד** | הבריף היה מדויק מול הקוד |
| כלב | התנהגות בזמן-ריצה | הקוד עבד מצוין |
| typecheck / lint | טיפוסים וסגנון | מצב מודולרי הוא TS תקין לחלוטין |

**אף שער לא בודק brief ↔ מוסכמות.** זו לא תקלה בשער מסוים — זה **ממד שלם שאינו נבדק**.

**חתימה מזהה**: הפרת-מוסכמה כמעט תמיד מגיעה עם **הנמקה** בבריף, ולעיתים עם ציטוט-תקדים.
ככל שההנמקה משכנעת יותר, כך גדל הסיכוי שהיא מכסה על חצייה של גבול ארכיטקטוני.
**תקדים שנלקח משכבה אחרת הוא הדגל האדום המרכזי.**

**הגנה**:
- ‏**אביגיל: לקרוא את `AGENTS.md` של הפרויקט לפני קריאת הבריף, ולבדוק את הבריף מולו** —
  לא רק מול הקוד. במיוחד: גבולות-שכבה (`core` מול shell), טוהר, מצב, טיפול-שגיאות, תלויות.
- ‏אביגיל: כשבריף מצטט **תקדים** — לוודא שהוא חי ב**אותה שכבה**. נתיב-הקובץ של התקדים מול
  נתיב-היעד; חבילות שונות = 🔴 עד שיוכח אחרת.
- ‏אביגיל: **מצב חדש ב-`core/` הוא 🔴 כברירת-מחדל.** מטמון הוא state; אם אינו מועבר
  כפרמטר — זו הפרה, גם אם הוא עובד.
- ‏מרדכי: לפני נעילת הכרעה שנוגעת במיקום או במצב — **לצטט את השורה מ-`AGENTS.md` שמתירה
  אותה**. אין שורה כזו → זו לא הכרעה אלא חריגה, וצריך לומר זאת במפורש.
- **סימן-אזהרה עצמי**: פונקציה שקיימת **רק** כדי לאפס מצב (`invalidateXCache()`) היא
  תסמין ולא פיצ'ר — היא מעידה שהמצב יושב במקום הלא-נכון.

> מקור: drive-coding `slice-cli-bin-resolution-unify` — בריף r1–r4 ודוחות
> `cli-bin-resolution-unify-avigail{,-r2,-r3}.md` · `-calev.md` · `-calev-slice.md`, כולם ירוקים.

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
