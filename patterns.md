# דפוסי כשל של Executor Agent

> מבוסס על: 1 case study (Slice 9 — drive-coding frontend refactor, מאי 2026).
> יתעדכן בכל case study חדש.

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

## קטגוריה X (placeholder)

> מקום לקטגוריה חדשה שתעלה מ-case study הבא.
