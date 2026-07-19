# השוואה: BDS מול GitHub Spec-Kit

> **תאריך**: 2026-07-20
> **מקור**: https://github.com/github/spec-kit
> **שאלה**: ללמוד מהם, או לעבור אליהם?
> **הכרעה בקצרה**: **ללמוד, לא לעבור.** לאמץ 3 רעיונות (Constitution / Converge / commands-UX);
> לשמר את שלושת ה-crown-jewels של BDS (אימות-runtime, זיקוק, merge-gate אנושי).

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
| אימות | `/clarify` (בהירות) + `/analyze` (עקביות מסמכים) | **אביגיל** (plan) + **כלב** (runtime — מריץ קוד) |
| סוכנים | 30+ גנריים | 5 תפקידים ייעודיים (מודל/prompt פר-תפקיד) |
| בידוד | לא מודגש | worktrees + שרשור slices |
| gate אנושי | agent-driven | **merge אנושי-בלבד** + live-preview ל-web |
| לולאת-שיפור | — | **זיקוק** (patterns/pitfalls מ-reports) |
| אורקסטרציה | אינטראקטיבי | יתרו (queue לילי) |
| בשלות/גיבוי | רשמי GitHub, CLI מלוטש, docs, presets | bespoke, single-user, 307 דוחות אמפיריים |

---

## 3. מה ללמוד מהם (רעיונות שווי-אימוץ)

1. **Constitution phase** — עקרונות-על מוגדרים **פעם אחת פר-פרויקט**. ב-BDS הדוקטרינה
   מפוזרת בין mordechai/SKILL/AGENTS. `<project>/constitution.md` היה מרכז את "החוקה".
2. **Converge phase** — **הפער הגדול ביותר שלנו.** BDS מאמת slice-slice, אבל אין בדיקה
   "האם הפרויקט **השלם** תואם את הכוונה, ומה נותר?". spec-kit הופך את זה לשלב מפורש.
3. **UX של slash-commands** — discoverable, שקוף. הפעלת-הסוכנים שלנו פחות נגישה למשתמש חדש.
4. **breadth של סוכנים (30+)** — spec-kit agent-agnostic; BDS תומך ב-3 CLIs. פורטביליות.
5. **CLI רשמי + presets/bundles** — onboarding ותחזוקה טובים מ-`generate/install` שלנו.

---

## 4. איפה BDS חזק יותר (למה לא לעבור)

1. **אימות דו-שכבתי עם סוכן שמריץ קוד.** `/analyze` בודק *עקביות-מסמכים*; **כלב מריץ את
   הקוד בסביבה אמיתית** ותופס באגי-runtime. הוכחה חיה: כלב תפס 11 blockers ב-155 ריצות;
   באג ה-symlink של ה-install נתפס **רק** בהרצה אמיתית, לא בבדיקת-מסמכים.
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

- **24. Constitution פר-פרויקט** — לרכז עקרונות-על ל-`<project>/constitution.md`.
- **25. Converge check** — שלב "האם הפרויקט השלם תואם את הכוונה + מה נותר" (הפער הגדול).
- **26. commands-UX** — עטיפת הפעלות-הסוכן ב-commands discoverable.

> נדחה במפורש: מעבר ל-spec-kit. הרציונל: אובדן אימות-runtime + זיקוק + merge-gate.
