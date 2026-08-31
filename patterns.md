# דפוסי כשל של Executor Agent

> ⚠️ **מ-31/08/2026 הקובץ מכסה גם כשלי-*מתכנן*** — בעידן הריצות האוטונומיות של אוגוסט
> הכשל הדומיננטי זז במעלה-הזרם (3/100 ‏blockers ‏בלבד היו של המבצע). ‏ראו הסעיף האחרון:
> **"טקסונומיית-מתכנן — זיקוק 2026-08-31"**.

> מבוסס על: case study יסוד (Slice 9 — drive-coding frontend refactor, מאי 2026)
> **+ זיקוק 2026-06-27 מ-118 דוחות כלב ב-10 projects** (ראה `distillations/2026-06-27-report.md`).
> hitrate כלב: 40/118 דוחות עם ממצא (34%), ממוצע 0.54 — נמוך, כי כלב הוא קו-הגנה אחרון
> אחרי אביגיל. יתעדכן בכל זיקוק / case study חדש.
>
> ⚠️ **ממצא-על מהזיקוק**: `unique` הוא הקטגוריה **הגדולה ביותר אצל כלב (31, ≈48% מהממצאים)** —
> רוב באגי-הריבור **לא נכנסים** ל-5 הקטגוריות של Slice 9. הסיבה: Slice 9 היה frontend-refactor,
> והשיטה התפשטה מאז ל-backend/CLI/infra (obsidian-web, opencode-config, mitm-proxy, bds עצמו).
> 5 הקטגוריות תקפות ל-UI-heavy slices; מחוץ לזה הטקסונומיה דקה מדי. לא מקדמים `unique` לקטגוריה
> (היא ה-fallback התקין) — אבל הסעיף "זיקוק 2026-06-27" למטה מסכם את התת-דפוסים שצצים בה.

המונחים:
- **Planner** = Opus 4.7/4.6 שכותב את ה-brief
- **Executor** = Sonnet 4.6 שמבצע את ה-brief
- **Investigator** = Opus בסבב חקירה אחרי הביצוע
- **Verifier** = סוכן (Sonnet כנראה מספיק) שמריץ את הקוד בדפדפן אחרי תיקונים

---

## קטגוריה 1: TDD ירוק ≠ התנהגות נכונה

**תדירות:** 4 מתוך 8 הבאגים הקריטיים ב-Slice 9.

**מנגנון:** Executor כותב טסטים על ה-unit שהוא בונה. הטסטים בודקים את ה-contract
של הפונקציה. ה-contract נכון מבחינה פנימית — אבל לא מתאר את מה שהמשתמש רואה.

**דוגמה מובהקת — B1 (Bubble grouping):**

ה-brief דרש: text_chunks מאותו kind+messageId יתאחדו ל-bubble אחד.

Sonnet כתב 11 טסטים, כולם ירוקים:
```typescript
test("text_chunks of same kind go to same bubble", () => {
  appendBubbleChunk("thought", "hello", "m1")
  appendBubbleChunk("thought", " world", "m1")
  expect(bubbles.length).toBe(1)
  expect(bubbles[0].segments.length).toBe(2)  // ← הבעיה כאן
})
```

הטסט בדק `segments.length === 2`. זה ה-contract הפנימי. אבל מבחינת המשתמש
זה אומר ששתי המילים מוצגות **כשני sub-segments נפרדים** — כלומר שתי מדבקות
עם padding ו-border, אחת מתחת לשנייה. ה-UI היה בלתי קריא.

מה שהיה צריך: `segments[0].text === "hello world"` (concat לאחרון, לא segment חדש).

**למה זה קשה לתפוס:**
- מבחינת ה-test runner הכל ירוק.
- מבחינת ה-developer שכותב את הטסט, הוא מאשר את ה-mental model שלו של "כל chunk = segment".
- רק כשרואים את ה-DOM בפועל מבינים שהמודל היה שגוי.

**דוגמאות נוספות מאותו slice:**
- ‏B10 — `voice-session` שמר `originalText`/`translatedText` ב-Map. `agent-session`
  בנה bubbles בלי המטא-דאטה. כל store עובר טסטים בנפרד, אף טסט לא בודק שהמידע
  חוצה ביניהם.
- ‏B15 — `player.jumpToBubble(messageId)` עבד מצוין בטסט. ב-call site הקריאה
  הייתה `player.addSegment(segId, kind, null)` — `messageId` hardcoded ל-null.
  הטסטים בידדו את הפונקציה מהשימוש בה.

**הגנה:**
- ‏Integration test פר phase שעובר על stream של events אמיתי ומאשרר DOM/state סופי.
- אם זה UI — Playwright snapshot test.
- כלל אצבע: לכל unit test, יש לפחות 1 טסט שמפעיל אותו דרך ה-flow האמיתי.

---

## קטגוריה 2: צנרת בין-Stores / Modules נשכחת

**תדירות:** 5 מתוך 8 הקריטיים ב-Slice 9. **הקטגוריה הכי מסוכנת.**

**מנגנון:** Executor בונה רכיב A, בונה רכיב B, כותב טסטים לכל אחד עם mock —
ושוכח את הגשר ביניהם. בכל רכיב הכל עובד; שום מבחן לא רץ דרך השניים.

**דוגמאות מ-Slice 9:**

| באג | A מייצר | B צריך לצרוך | מה נשכח |
|-----|---------|--------------|---------|
| ‏B10 | voice-session: originalText, translatedText | agent-session bubbles | בכלל לא נכתב bridge |
| ‏B13 | session.disconnect() | voiceMessageHandler נשאר רשום | disconnect לא ניקה את ה-handler |
| ‏B15 | audio_chunk.messageId מה-WS | player.addSegment | hardcoded `null` ב-call site |
| ‏N4 | agent-orchestrator | projects-registry | שכחה לקרוא `recordCwd()` |
| ‏NBug2 | `audio_recording_saved` WS event | bubble.recordingId ב-DOM | שום handler לא עדכן את ה-bubble |

**למה זה קורה:**
- ‏Executor כותב את הרכיבים בסדר לינארי (phase-by-phase). שני הרכיבים נכתבים
  ב-phases שונים. כשהשני נכתב, הראשון כבר "נסגר" ופחות חי בקונטקסט.
- ‏Mocks ב-unit tests מסתירים את הצורך בגשר.
- ה-brief לרוב לא מפרט את הגשר במפורש — מצופה ש-"זה מובן מאליו".

**הגנה:**
- ב-brief: לכל data flow שחוצה גבול — **לתעד את הגשר במפורש**. "כש-A מייצר X
  ו-B צריך X — להגדיר את המנגנון: callback? subscription? shared store?".
- ‏Anti-pattern explicit: "לעולם לא להעביר `null` כפלייסהולדר לפרמטר שצריך להיות
  ערך אמיתי. אם הערך לא זמין עדיין — restructure."
- ‏Integration test שעובר על שני ה-stores ביחד.

---

## קטגוריה 3: Spec Drift — ה-brief אומר X, התוצאה Y

**תדירות:** 4 ב-Slice 9 (B4, N2, N3, B11).

**מנגנון:** ה-brief מצוין במפורש מה צריך — אבל Executor:
- נטה ל-refactor במקום rebuild: לא מוחק את הישן, רק מוסיף את החדש.
- מטפל ב-mockup הראשי ושוכח variants (mobile vs desktop).
- מפספס משפט קונקרטי בתוך פסקה כללית.

**דוגמאות:**

- ‏**B4** — ה-brief אמר "voice-only, no textbox". Sonnet שמר את `<textarea>` +
  כפתור "שלח" כי הם היו בקוד הקיים. ה-mockup ברור — אין textbox. כשמשתמש פתח
  את הדף, ראה textbox.
- ‏**N2** — ה-brief: "Lucide icons בכל מקום (לא emojis)". Sonnet טיפל ב-agent
  page, שכח את ה-dashboard (📚, ⚙, 🎙).
- ‏**N3** — ה-brief נתן 2 mockups: mobile + desktop. Sonnet ריענן את ה-mobile
  header, השאיר את ה-desktop header הישן בסגנון pre-refactor.
- ‏**B11** — ה-mockup הראה play icon קטן בפינת ה-bubble ב-idle. Sonnet הוסיף
  border ב-execution state, שכח את ה-idle indicator.

**למה זה קורה:**
- ה-brief הוא טקסט ארוך. הקונקרטי בתוך הכללי קל לפספס.
- ה-mockup הוא reference, לא DoD. אין enforcement של "התאמה ל-mockup".
- ‏Refactor פסיכולוגית קל מ-rebuild — Executor מוסיף, פחות מוחק.

**הגנה:**
- ב-brief: לכל "הסר X" — להוסיף שורה קונקרטית: `DELETE block at file.svelte:L-M`.
- ‏Mockup compliance audit phase כשלב מפורש בסוף ה-brief (Phase 13).
- ‏DoD: "open browser, walk through every mockup, find every divergence".

---

## קטגוריה 4: אינטראקציות עם ספריות חיצוניות

**תדירות:** 1 ב-Slice 9 (N5 — Lucide CDN + Svelte DOM).

**מנגנון:** ה-brief בחר ספרייה/גישה ("Lucide via CDN"). Executor יישם בדיוק את זה.
הבעיה: הספרייה רצה outside ה-framework's virtual DOM (Lucide's `createIcons()`
מחליף `<i>` ב-`<svg>` ישירות ב-DOM), וה-framework לא יודע. בכל update — DOM tree
מתערבב.

**דוגמה:**

```svelte
<!-- Icon.svelte של Sonnet -->
<i data-lucide={name}></i>
<script>
  $effect(() => {
    lucide.createIcons()  // ← מחליף <i> ב-<svg> ב-DOM גלובלית
  })
</script>
```

תוצאה: בכל change של `name`, Lucide מוסיף `<svg>` חדש, ה-`<i>` הישן הוחלף ל-`<svg>`
פעם קודמת, Svelte מוסיף `<i>` חדש, נוצרים שני אייקונים על אותו כפתור.

**למה זה קשה לתפוס:**
- אין טסט שיתפוס את זה — DOM mixing מופיע רק עם שני Icons בו-זמנית עם re-render.
- ‏Executor יישם בדיוק את מה שה-brief אמר.

**הגנה:**
- ב-brief: לציין במפורש incompatibilities ידועות. "Lucide CDN's createIcons()
  is NOT compatible with Svelte's reactive DOM updates. Use `lucide-svelte` npm
  package instead (renders inline SVG)."
- כל פעם שה-brief בוחר ספרייה — לחפש "X integration with Y" לפני ה-finalize.

---

## קטגוריה 5: CSS / ויזואלי = שטח מת לחלוטין

**תדירות:** 3+ ב-Slice 9 (B6, B11, N3, וחלקית B3).

**מנגנון:** אין טסטים על CSS. אם Executor לא פותח דפדפן — אין הגנה.

**דוגמאות:**

- ‏B6 — `BottomSheet` grip = 40×4px. פונקציונלי, בלתי-נראה. אין טסט שיתפוס.
- ‏B11 — play indicator חסר. אין assertion על "icon element exists in DOM".
- ‏N3 — desktop view בעיצוב ישן. mobile נבדק, desktop לא.

**מאפיין:** Executor כותב CSS ועובר הלאה. בלי screenshot, בלי `playwright`.
דווח: "Phase 3 — ירוק". בפועל: לא ראה את התוצר אף פעם.

**הגנה:**
- ‏Mandatory: screenshot per phase שמשפיע על UI. השוואה ל-mockup.
- ‏Playwright snapshot tests על נתיבים קריטיים — לפחות 1 per route.
- ב-brief: "כל phase שמשנה UI חייב include screenshot evidence in commit message."

---

## מטא-תופעה: גם ה-investigator מפספס

ב-Slice 9, אחרי שה-investigator (Opus) מצא 19 באגים ו-Sonnet תיקן 17 מהם,
ה-verifier (סבב נפרד אחרי) מצא **4 באגים חדשים**:

- ‏NBug1 — N3 לא תוקן (Sonnet שכח, ה-investigator לא בדק)
- ‏NBug2 — Q5 recording playback עדיין שבור (Sonnet תיקן חלק מהצינור, לא הכל)
- ‏NBug3 — History reload — לא נבדק
- ‏NBug4 — Comma sentence splits — Sonnet אמר "לא צריך תיקון", ה-investigator קיבל

**משמעות:** investigation report (אפילו של Opus) ≠ verification. ה-investigator
קורא קוד וצופה. ה-verifier מפעיל ובודק. הם תופסים דברים שונים.

→ עיין ב-`recommendations.md` section "Verifier agent design".

---

## מטא-תופעה 2: המתקן מייצר את הממצא הבא

מקבילה ל"גם ה-investigator מפספס", ומדודה בשני תיקים בלתי-תלויים:

| ‏תיק | ‏סבבים | ‏מקדם המשוב (‏ממצאים שנולדו מהתיקון הקודם) |
|---|---|---|
| obsidian-web R0 | 9 | ‏בסבבים 5–8, **‏כל ה-🔴** ‏היו בטקסט שהמתכנן הוסיף כתיקון |
| eq-checker slice-5 | 6 | **44%** ‏בסבב 5, ‏והחוסם היחיד ביניהם |
| eq-checker slice-7 | 3 | **100%** — ‏שני החוסמים, ‏שניהם מתיקוני הסבב הקודם |

**המנגנון**: כל תיקון-פרוזה הוא קוד שנכתב בלי מהדר. ה-brief הפך לתוכנית, והמאמת
שימש כמהדר במחזור של עשרים דקות. **שני שערים שנוספו כתיקון היו חסרי-ערך לחלוטין**,
ואחד מהם ייצר בעצמו את הקובץ שכלל-ההחרגה עוד לא כיסה.

**המנגנון שמתחת**: מיקור-חוץ של האימות מוריד את הזהירות במעלה הזרם — risk compensation.
אותו סוכן, אותו יום: קוד שאין אחריו מאמת הורץ מיד ותפס 4 באגים עצמית; טקסט שיש
אחריו מאמת נכתב מהזיכרון וייצר 3 חוסמים. **מאמת אינו חינם — הוא גם מייצר חלק מהממצאים.**

**משמעות**: מסבב 3–4 ואילך, שאלת האימות משתנה מ"האם ה-brief נכון" ל"**האם התיקונים
של הסבב הקודם נכונים**". וקיצור ה-brief מקטין את **הנפח** של הלולאה, לא את **קיומה**
(‏379 שורות מול 1,161 → ‏2 חוסמים במקום 7, אבל היחס עלה מ-44% ל-100%).

→ ‏`recommendations.md` פריטים 27, 28, 30, 31.

---

## קטגוריה 6: `reload-reconnect` — מצב לא שורד reload/reconnect (מועמדת)

**תדירות:** 3 ב-זיקוק 2026-06-27. **טרם קטגוריה מלאה** — מסומנת כמועמדת.

**מנגנון:** ה-slice עובד ב-happy-path, אבל אחרי refresh של הדף / ניתוק-וחיבור מחדש של
WS, ה-state לא משוחזר נכון: turn תקוע, connection לא מתאושש, session לא נטען מחדש.
כלב תופס את זה רק כי שלב 4 ב-heavy ("edge cases — reload/reconnect") הוא חובה.

**הגנה:** ב-brief — לכל slice עם WS/session-state, DoD item מפורש "reload mid-flow → state נשמר".
זה כבר ב-`agents/calev.md` §"נקודות שכבר נפלנו עליהן" — להעלות גם ל-brief.

> מקורות (3): drive-coding/chat-render-polish, opencode-config/slice-D-memfs-claude-spike, voice-acp/slice-fix-turnstate-stuck

---

## קטגוריה 7: `stale-user-visible-string` — נכונות של מחרוזת בממשק (מועמדת)

**תדירות**: מקרה אחד מדוד, אבל **חוצה את כל שכבות האימות בבת אחת** — ולכן מועמדת.
זיקוק 2026-08-02.

**מנגנון**: השערים בודקים **קיום** של מחרוזות, לא **נכונות** שלהן. ‏`Object.keys().length`
סופר מפתחות ולא מאמת ערכים; שער-זהב מקפיא **פלט של פונקציות**, ומחרוזת קשיחה אינה
פלט של פונקציה; ה-E2E בודק שהדף נטען בלי שגיאות, ומחרוזת גרסה שגויה אינה שגיאה.

**המקרה**: `עוזר משוואות v26 / מנוע v20 · 2026-08-01` — שניים משלושה שדות שגויים,
כולל **תאריך בנייה של יום קודם**. מה שלא תפס: ‏255 בדיקות מנוע · ‏54 לוגיקה ·
‏3,677 ערכי זהב · ‏116 שרשראות פאזר · ‏6 סבבי אביגיל · ‏3 סבבי כלב. **אף אחד.**
המשתמש תפס את זה בעין, בשנייה.

השדה היחיד באותו קובץ שכן נבדק על **נכונות** הוא תווית כפתור — ורק מפני שכלב תפס
פעם ששינוי-שם-מפתח היה מפיל אותה בשקט, ואז נוספה בדיקת E2E מפורשת. כלומר: הדבר
היחיד שנבדק על נכונות הוא זה שכבר נשבר פעם.

> **תאריך בנייה שקרי גרוע מהיעדר תאריך — הוא נראה כמו מידע.**
> **מטא-דאטה שמתוחזקת ביד תרקב, והשערים לא ירגישו.**

**הגנה**:
- ‏כלב: בסקירה הוויזואלית — לקרוא כל מחרוזת-מטא-דאטה שנראית למשתמש (גרסה, תאריך,
  שם מנוע, שם סביבה) ולהשוות למציאות. זו בדיקת-עיניים, לא בדיקת-שער.
- ‏ב-DoD: `□ מטא-דאטה שנראית למשתמש נבדקה מול המציאות? □ אם היא ביד — אפשר לגזור אותה?`
- **הפתרון האמיתי הוא הזרקה בזמן בנייה** (`esbuild --define`) — להוציא את השדה
  מידיים אנושיות, לא להוסיף עליו שער. תיקון ידני מחזיר את אותה שיחה בעוד סלייס.

**‏אותו מנגנון על ה-brief עצמו** (זיקוק 2026-08-04): ‏ב-slice-4, ‏חמישה ממצאים
‏בחמישה סבבים נפרדים היו על **‏עקבת-האימות של הבריף** — ‏"‏העקבה נעצרת ב-r6 ‏בעוד
‏r7–r9 ‏באו אחריה". ‏כל סבב הוסיף שורה, ‏הסבב הבא מצא אותה לא-עקבית, ‏וזה היה ממצא.
‏הפעם **‏המאמת הוא השער שמרגיש** — ‏והוא מדווח על ריקבון שהאימות עצמו ייצר.
‏התרופה זהה: ‏להיגזר (‏משמות הדוחות, ‏מ-`git`, ‏מספירה), ‏לא להיכתב.
‏→ `recommendations.md` ‏פריט 39.

> מקורות: `case-studies/RAW-2026-08-verification-cost.md` §19 · obsidian-eq-checker slice-5 ·
> `case-studies/2026-08-eq-checker-slice4-ten-rounds.md` §4 (‏הווריאנט של הבריף)

---

## זיקוק 2026-06-27 — התפלגות ממצאי כלב (118 דוחות)

| category | count | ממופה לקטגוריה | הערה |
|----------|-------|----------------|------|
| `unique` | 31 | — (fallback) | רוב הממצאים. טקסונומיה דקה מחוץ ל-UI. ראה ממצא-העל בראש הקובץ. |
| `spec-drift` | 13 | קטגוריה 3 | "הסר X" שלא קרה / variant שנשכח |
| `regression` | 7 | מטא-תופעה | feature ישן שנשבר — בדיוק מה ש-heavy שלב 5 נועד לתפוס |
| `reload-reconnect` | 3 | קטגוריה 6 (חדש) | ראה למעלה |
| `cross-store-null` | 3 | קטגוריה 2 | null שחוצה stores |
| `library-compat` | 2 | קטגוריה 4 | ספרייה מול framework |

**verdicts:** GO 101, PARTIAL 11, NO-GO 5, GO-WITH-NOTE 1 — כלב תפס 16 slices שלא היו מוכנים
ל-merge (חוב-שקט שנמנע).

---

## Traceability — מקורות

> כל קטגוריה מצביעה על הדוחות (reports/) שתרמו לה.
> מבנה: `> מקורות: project/slice-verifier, ...`
> מעודכן בכל זיקוק (ראה `distillations/`). `trace` מלא ב-`distillations/2026-06-27-data.json`.

**קטגוריה 1 — TDD ירוק ≠ התנהגות נכונה**:
> מקורות: drive-coding/slice-9 (case study יסוד). נפח runtime נמוך כי אביגיל תופסת dropped-branch מוקדם.

**קטגוריה 2 — צנרת בין-Stores / Modules נשכחת** (`cross-store-null`):
> מקורות: drive-coding/slice-chat-virtualization, obsidian-web/server-bootstrap-perf, voice-acp/slice-redesign-6-modals

**קטגוריה 3 — Spec Drift** (`spec-drift`, 13):
> מקורות: bds/bds-extraction-and-reporting, drive-coding/slice-chat-virtualization, obsidian-web/server-bootstrap-perf, voice-acp/slice-redesign-3-settings, voice-acp/slice-redesign-6-modals, voice-acp/slice-ws-reconnect-infra

**קטגוריה 4 — אינטראקציות עם ספריות חיצוניות** (`library-compat`):
> מקורות: drive-coding/slice-chat-virtualization, obsidian-web/server-bootstrap-perf

**קטגוריה 5 — CSS / ויזואלי = שטח מת**:
> מקורות: drive-coding/slice-9 (case study יסוד). נתפס כיום ב-heavy שלב 2 (סקירה ויזואלית mobile+desktop).

**קטגוריה 6 — reload-reconnect**:
> מקורות: drive-coding/chat-render-polish, opencode-config/slice-D-memfs-claude-spike, voice-acp/slice-fix-turnstate-stuck

**קטגוריה 7 — stale-user-visible-string** (מועמדת, זיקוק 2026-08-02):
> מקורות: obsidian-eq-checker/slice-5-page-split (‏case study, ‏לא דוח פורמלי — ‏נתפס ע"י המשתמש אחרי כל השערים)

**מטא-תופעה 2 — המתקן מייצר את הממצא הבא** (מטא, חוצה-קטגוריות):
> מקורות: obsidian-web/monorepo-foundation-avigail-round5..round8, obsidian-eq-checker/slice-5-page-split-avigail-r5, obsidian-eq-checker/slice-7-practice-loop-avigail-r1
> (‏סבבי slice-7 r2–r3 מתועדים ב-`RAW-2026-08-verification-cost.md` §21, §23 בלבד — ‏דוח פורמלי לא הוגש)

**רגרסיות** (`regression`, 7 — מטא, חוצה-קטגוריות):
> מקורות: drive-coding/slice-release-cli-hardening, drive-coding/slice-ws-error-survival, learn-games-project/slice-3.6a-kit-settings-config-cleanup, voice-acp/slice-22-tts-ordering, voice-acp/slice-redesign-3-settings, voice-acp/slice-ws-reconnect-infra

---

## טקסונומיית-מתכנן — זיקוק 2026-08-31

> **מקור**: 34 דוחות-ריצה אוטונומית (19–31/08) + **172 דוחות-אימות** של drive-coding מהחלון
> (‏100 ממצאי-blocker) + יומן-ההחלטות (HR-01..HR-05). ‏פירוט מלא וספירות ברות-שחזור:
> `distillations/2026-08-31-report.md`.
>
> **הממצא המרכזי**: ‏מתוך 100 ‏ממצאי-blocker באוגוסט — ‏**96 מצביעים על הבריף** (‏92 ממצאי-אביגיל
> ‏+ 4 חוסמי-כלב שגופם טענת-בריף מופרכת), ‏**3 בלבד במימוש** (‏מבצע), ‏1 ‏פגם-עיצוב. ‏(‏4 ממצאי-מאמת-שגויים
> ‏+ 2 של המתזמר תועדו בדוחות-הריצה, ‏מחוץ למאה.) ‏חמש הקטגוריות ההיסטוריות של הקובץ
> ‏הזה מתארות את המיעוט. ‏הגוש הגדול (63/100) ‏הוא **הצהרה או שער של המתכנן שנראו כמדודים
> ‏ולא נמדדו** — "‏מדוד-למחצה". ‏ההיגד המכונן, ‏HR-05: *"‏את מסלול ה-cwd מדדתי חי — ‏ולכן א'
> ‏עבר בסבב אחד; ‏את מחזור-חיי ה-epoch לא מדדתי, ‏והנחתי."*

### מ1: שער שנכתב ולא הורץ

**תדירות**: ‏הגדול ביותר — ‏37 `gate-cannot-fail` + ‏רוב 12 ה-`unrun-claim` (‏~44 מ-100).

**מנגנון**: ‏המתכנן כותב שורת-DoD/שער/מוטציה מהזיכרון. ‏היא נראית מדויקת — ‏פקודה, ‏נתיב,
‏מספר — ‏אבל לא הורצה ולו פעם אחת, ‏ולכן אינה אדומה-על-הבסיס, ‏או אינה ניתנת להרצה כלל,
‏או ירוקה גם מול מימוש שבור.

**דוגמה מובהקת**: ‏`ttl-ownership` — ‏תשעה חוסמים בארבעה סבבי-אביגיל, ‏כולם שערים שהמתכנן
כתב: ‏`grep` על תיקייה שאינה קיימת · ‏חלון-זמן שנגזר ממודל שגוי של ה-sweep · ‏בדיקת-BOOT
ש"`listening`" ‏שלה נרשם גם על `EADDRINUSE`. ‏סיכום דוח-הריצה: *"‏כל תשעת החוסמים הם אותו
דבר: **קוד שנכתב מהזיכרון ולא הורץ**."* (`autonomous-runs/runs/2026-08-19-ttl-ownership.md`)

**הגנה** (‏MISSION_TEMPLATE/plan-gate): ‏שורת-שער נמסרת רק עם **פלט ההרצה שלה על הבסיס
מודבק** — ‏אדום-על-הבסיס לשער-תוכן, ‏ירוק-על-הבסיס לשער-רגרסיה (‏ואז מוטציה מורצת שמאדימה
אותו). ‏"‏אימתתי אנליטית" = ‏לא-מורץ. ‏זה §8ה קיים — ‏ההעלאה: ‏plan-gate **מסרב** לשורת-DoD
בלי בלוק-פלט, ‏מכנית, ‏כמו שער-השיגור של אליעזר.

### מ2: קריאת-קוד שהוצגה כמדידה

**תדירות**: ‏~10 (‏החמור ביותר ליחידה — ‏פעמיים עצר סלייс שלם).

**מנגנון**: ‏טענה על *התנהגות-מערכת* ("‏ה-epoch זז ב-F5", "‏החוט נושא `tool_call`",
"‏הצירוף לא ישבור אידמפוטנטיות") ‏מנוסחת כעובדה ונשענת על קריאת-קוד או על סבירות.
‏קריאת-קוד רואה את השורה; ‏היא אינה רואה את מסלול-הריצה, ‏את השומר שמונע אותו, ‏או את
‏השכבה שמפילה את הנתון בדרך.

**דוגמה מובהקת**: ‏HR-05 (‏`explicit-disconnect`) — ‏שני סבבי NEEDS-REWORK על אותו כשל:
‏D2 ‏נבנה על "‏ב-F5 ה-epoch זז", ‏והקוד אומר במפורש *"never bump the epoch on an ordinary
second connection"*; ‏וה-epoch ‏כלל אינו מגיע ל-JS (‏פרסר ה-SSE משליך שורות `id:`).
(`explicit-disconnect-avigail{,-delta}.md` · `autonomous-decisions-log.md` HR-05)

**הגנה**: ‏פורמט-חובה ל-§11: ‏כל שורה מסומנת **‏✅ נמדד-חי / 📖 נקרא-בקוד / 🔮 תחזית**,
‏ו-✅ ‏מחייב פקודה+פלט. ‏plan-gate: ‏שורת-§11 שתנאי-עצירה או Commit ‏נשען עליה חייבת ✅;
‏📖/🔮 במקום כזה = ‏ממצא. ‏(‏זה כלל `60-system-claims` הגלובלי, ‏מובא לשער אכיף.)

### מ3: נמדד — בסביבה אחרת

**תדירות**: ‏~8.

**מנגנון**: ‏המדידה בוצעה באמת — ‏אבל בעץ החם של המתכנן (‏אחרי `bun install` לא-מתועד),
‏על מכונה/TZ אחרים, ‏על פיקסצ'ר באוצר-מילים שהחוט אינו נושא, ‏או בשער שאינו מכסה את
היעד (‏"typecheck 0" ‏שלא נגע ב-FE). ‏התוצאה נכונה-אצלי ושבורה-אצל-המבצע.

**דוגמה מובהקת**: ‏ריצה 17 — ‏`bunx svelte-kit sync` ‏הופץ לשלוש פקודות-משימה ולתבנית;
‏"‏היא עבדה אצלי **רק מפני שהרצתי `bun install` לפניה** — ‏צעד שלא תיעדתי", ‏ובעץ טרי היא
מורידה חבילת npm ‏זרה. (`runs/2026-08-26-fe-defaults.md`) ‏וכן `frame-ingest`: ‏שער שהוזן
בפיקסצ'ר v1 — ‏"‏אוצר-מילים שחוט ה-HTTP לעולם אינו נושא; ‏השער יהיה ירוק בעוד הייצור שבור".

**הגנה**: ‏✅ ב-§11 מחייב גם **סביבה**: ‏עץ (‏טרי/חם), ‏מכונה, ‏והאם זהו מסלול-הייצור או
‏פיקסצ'ר (‏ואם פיקסצ'ר — ‏באיזה אוצר-מילים). ‏בדיקת-טרום: ‏פקודות ‏§0 ‏מורצות פעם אחת
ב-worktree ‏טרי לפני dispatch (‏§8ו ‏קיים — ‏להפוך לחובה).

### מ4: תחזית בלשון עובדה

**תדירות**: ‏~5.

**מנגנון**: ‏"‏יהיו צרכנים", ‏"‏השער יהיה אדום", ‏"‏המוטציה תיתפס" — ‏עתיד מנוסח כהווה.
‏המבצע והמאמת קוראים עובדה, ‏בונים עליה, ‏והתנאי לא מתקיים.

**דוגמה מובהקת**: ‏`live-ears` — ‏הבריף הצהיר ב-DoD 7 ‏שיש ל-`ear`/`mouth` ‏צרכנים; ‏כלב
מדד **אפס** צרכני-ייצור, ‏והשער "‏מאדים רק מול assertions ‏שנכתבו באותו קומיט".
‏דוח-ריצה 18: ‏"‏מתוך 5 ‏הופעות דפוס-השער, ‏**4 היו תחזיות של המתכנן**." (`live-ears-calev.md`)

**הגנה**: ‏lint-בריף טקסטואלי (‏פריט 34): ‏"‏יהיו/‏אמור/‏צפוי" ‏בשורת-DoD ‏או ‏§11 ⇒ ‏אזהרה;
‏plan-gate ‏מסווג אותן 🔮 ‏ודורש או מדידה או שער שנכשל כשהתחזית לא מתממשת.

### מ5: נמדד — האובייקט הלא-נכון

**תדירות**: ‏~5 (‏כולל שני ממצאי-המאמת-השגויים — ‏אותה מכניקה בצד השני).

**מנגנון**: ‏המדידה רצה, ‏המספר אמיתי — ‏אבל על מנגנון שכן, ‏קורפוס חלקי או שדה מיושן:
‏שומרי-גרסה כשהכפילות בסריאליזציה; ‏`grep` ‏שאינו פותח `.zst` (‏181 ‏מ-613 ‏קבצים);
‏`num_tables` ‏של `wrangler d1 list` ‏שהוא מטא-נתון מת; ‏probe ‏שמצביע על קובץ שהקוד לא נחת בו.

**דוגמה מובהקת**: ‏ריצה 16 (‏`msg-coalesce`) — ‏§11ג ‏בדק שומרי-**גרסה** והסיק "‏אין סיכון";
‏הכפילות מגיעה מ**סריאליזציה מצטברת בפולט**. ‏"‏בדקתי את המנגנון הלא-נכון והכרזתי על
ניצחון." (`runs/2026-08-26-msg-coalesce.md`)

**הגנה**: ‏מדידת-קורפוס מצהירה **כמה נפתחו מתוך כמה קיימים**; ‏טענת-שלילה ("‏אין X")
מחייבת בקרה-חיובית (‏להראות שהמדידה כן מוצאת X ‏מוזרק). ‏וכלל replay-quiet ‏למאמתים:
‏🔴 ‏מבוסס-מדידה מצטט את **הקלט המדויק** — ‏כדי שיהיה בר-הפרכה בשורה אחת.

### מה מבדיל הצהרה שהחזיקה — הדיסקרימיננטה

‏הצהרה החזיקה כשהתקיימו **כל** החמישה, ‏ונפלה כשחסר אחד:
‏(1) ‏הורצה, ‏לא נקראה · ‏(2) ‏בסביבת-המבצע · ‏(3) ‏על האובייקט שהטענה עליו ·
‏(4) ‏בכיוון הכישלון (‏אדום-על-הבסיס/מוטציה) · ‏(5) ‏עם קלט+פלט+היקף מצוטטים.

‏אימות חיצוני: ‏blockers ‏פר-יום ירדו מ-35 (‏27/08) ‏ל-**0·0·1** ‏ב-29–31/08 — ‏מה שהשתנה
הוא פרה-בריפים עם מדידות-חיות לפני הבריף ושערים מוכחי-אדום-על-הבסיס, ‏לא מודל ולא מבצע.
‏וריצה 7, ‏הנקייה הראשונה: ‏"‏**העובדות נאספו לפני הבריף, ‏לא במהלכו**."

> מקורות: drive-coding/ttl-ownership-avigail-r1..r4 · explicit-disconnect-avigail{,-delta} ·
> frame-ingest-unify-avigail{,-r2} · msg-diagrams-avigail · meta-passthrough-avigail ·
> msg-coalesce-avigail · fe-defaults-avigail · live-ears-{avigail,avigail-delta,calev} ·
> live-secretary-avigail{,-delta} · live-contract-gemini-{avigail,calev} · live-transcript-box-avigail ·
> live-unprompted-guard-avigail-delta · wire-rec-compress-avigail · ws-transport-dedupe-calev ·
> playlist-invariants-avigail{,-r2} · slice-control-roles-avigail-r3 ·
> autonomous-runs/runs/2026-08-{19..31}-*.md · docs-repo/drive-coding/plans/autonomous-decisions-log.md
