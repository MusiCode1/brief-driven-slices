---
project: "drive-coding"
slice: "replay-quiet"
verifier: "avigail"
round: 3
date: "2026-08-23"
base: "b323c36d"
brief: "docs-for-llm/plans/slice-replay-quiet-by-reset.md @ 68b75fb"
verdict: "USABLE-AFTER-FIX"
findings:
  - id: 1
    severity: "blocker"
    category: "faithful-but-inadequate"
    summary: "תרחיש ה' (reconnect) מודד 0 על הבסיס, לא > 0 — החוט החדש מכווץ N סגמנטים ל-1 בכל snapshot, והמונה הישן חוסם"
    source_brief: "§evidence-3 ממצא 3 · §2 טבלת ה-לא · §4 Commit 1 תרחיש ה' · DoD 6 · §6 סיכון 4"
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:302 · sse-reader.ts:82 (foldSnapshot) · apply-patch-mutable.ts:137 · remote-session-view.ts:372"
    cost_estimate: "30-60min"
  - id: 2
    severity: "regression"
    category: "faithful-but-inadequate"
    summary: "יחידת-החתך (segmentCounts) אינה יציבה מול הכיווץ — מונה-גבוה-מיושן בולע סגמנטים חיים אחרי כל reset"
    source_brief: "§4/2ג #applyHistoryMark — הגנת \"לעולם לא להוריד מונה\""
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:302 · core/src/session/to-session-update.ts:85"
    cost_estimate: "15-30min"
  - id: 3
    severity: "confusion"
    category: "unrun-claim"
    summary: "grep register-then-snapshot מחזיר 8 מופעים, לא 4 — הבריף מצהיר \"אין אתר-קיבוע חמישי\""
    source_brief: "§4 Commit 3, סוף הסעיף על שכתוב הטסט"
    source_code: "patches-broadcaster.ts:6 · patches-broadcaster.test.ts:10,162 · session-host-http.integration.test.ts:263"
    cost_estimate: "5-10min"
  - id: 4
    severity: "confusion"
    category: "missing-dependency"
    summary: "פקודת-המשימה מפנה לבריף @ 8080a62 — בדיוק הגרסה שהבריף מכריז עליה כבטלה"
    source_brief: "missions/replay-quiet.md כותרת · מול slice-replay-quiet-by-reset.md §כותרת"
    source_code: "docs-repo: mission=2245eeb · brief=68b75fb"
    cost_estimate: "2min"
  - id: 5
    severity: "minor"
    category: "wrong-path"
    summary: "serializeFrame אינו מיוצא מ-core/session/testing אלא מ-core/session — Commit 1ד מציג את שניהם כמקור אחד"
    source_brief: "§4 Commit 1(ג)+(ד)"
    source_code: "packages/core/src/session/__testing__/wire-fixtures.ts:24-66 · packages/core/src/session/index.ts"
    cost_estimate: "5min"
  - id: 6
    severity: "minor"
    category: "missing-symbol"
    summary: "subscribe() מוצהר גם בממשק PatchesBroadcaster ולא רק במימוש — Commit 3 מונה רק את המימוש"
    source_brief: "§3 דיאגרמה · §4 Commit 3"
    source_code: "packages/backend/src/session-host/patches-broadcaster.ts:24 (+doc :21-22), :118"
    cost_estimate: "2min"
  - id: 7
    severity: "minor"
    category: "unique"
    summary: "\"9 מ-11\" מופיע פעמיים — טבלת ה-DoD מונה 12 שורות (0-11), מהן 10 פקודה ו-2 עיניים"
    source_brief: "§5 שורת-הסיכום · §8"
    source_code: "—"
    cost_estimate: "2min"
  - id: 8
    severity: "minor"
    category: "wrong-line-number"
    summary: "סחיפת שורות של 1-3 בעשרה עוגנים (כל הטקסט קיים ואומת) — להעדיף עיגון בתבנית"
    source_brief: "§3 · §4 Commit 1(ג) · §4 Commit 2(ג) · §4/2א"
    source_code: "speaker.svelte.ts 302/343/422 · remote-session-view.ts 211/298 · apply-patch-mutable.ts 28/33/51/98 · events.ts 155-157"
    cost_estimate: "5min"
---

# Plan Verification — replay-quiet (‏סבב r3)

> **Brief**: `docs-for-llm/plans/slice-replay-quiet-by-reset.md` @ `68b75fb`
> **Base tip**: `b323c36d` (`integration/acp-playback` == `integration/run-replay-quiet`, ‏שניהם על אותו hash — אומת)
> **Verdict**: 🟡 **USABLE-AFTER-FIX**
> **‏אומדן זמן אליעזר confusion אם לא תוקן**: **‏45-70 ‏דק'** (‏רובו על ממצא 1)

---

## ‏חלק א' — ‏שתי המחלוקות מ-r2. ‏שתיהן: **‏אתה צדקת.**

### ‏ר2 ‏ממצא #2 — "‏הערך 8 ‏אינו בר-מדידה" → **‏מופרך. ‏הבריף נכון.**

‏הרצתי probe עצמאי על הבסיס, ‏שמחקה את `#processBubbles` ‏מקצה-לקצה
(`splitStreamable` → `toSpeakable` → `splitIntoSentences`, ‏עם ‏`minChars:20, maxChars:200`):

```
8-segments enqueues: 8
1-segment  enqueues: 8
identical:           true
short synthetic ("seg0. seg1. …"): 1 enqueue
```

‏ו-probe שני, ‏על מסלול-החוט האמיתי (`stateToSessionUpdates` → `reduce`):

```
BEFORE messages: 1  segments: 8
AFTER  messages: 1  segments: 1
ids equal: m_0 m_0        text identical: true
```

‏**‏המסקנה שלך עומדת בכל שלושת החלקים:**
1. ‏הכיווץ 8→1 ‏אמיתי (`to-session-update.ts:85`, ‏אומת).
2. ‏הוא **‏אינו** ‏משנה את מספר ה-enqueues, ‏כי `speaker.svelte.ts:304-307` ‏משרשר
   ‏לפני ‏`splitIntoSentences` (`:332`). ‏הטקסט זהה בייט-לבייט ⇒ ‏אותם משפטים.
3. ‏האבחנה שלך על **‏למה ה-probe שלי הראה אחרת** ‏מדויקת: ‏`MIN_CHARS = 20`
   (`speaker.svelte.ts:57`, ‏אומת) ‏מקפל טקסט קצר-סינתטי ל-**1**. ‏שחזרתי את זה בדיוק.

⇒ ‏טסט-השפיות של הפיקסצ'ר (§4/Commit 1ב, ‏DoD 5) ‏מוצדק ‏**‏ומחייב**. ‏אשרתי.

> **‏הסתייגות אחת קטנה, 🟢:** ‏טסט-השפיות שבבריף מריץ ‏`splitIntoSentences(HISTORY_TEXT)`
> ‏**‏לבדו**, ‏בעוד המסלול האמיתי מריץ ‏`splitStreamable` → ‏`toSpeakable` → ‏`splitIntoSentences`.
> ‏לפרוזה רגילה זה זהה (‏אומת ב-probe), ‏אבל אם הפיקסצ'ר יכיל markdown (‏גדר-קוד, ‏קישור)
> ‏השניים יתפצלו, ‏והשומר יֵצא ירוק בזמן שהרתמה מודדת מספר אחר. ‏שקול שהשומר יריץ
> ‏את אותה שרשרת.

### ‏ר2 ‏ממצא #3 — "‏`https-serve` ‏נופל דטרמיניסטית" → **‏מופרך. ‏הבסיס בסדר.**

```
bunx vitest run tests/https-serve.test.ts   →   1 passed (1) · Tests 3 passed (3) · 2.88s
```

‏הרצה עצמאית משלי, ‏בבידוד — ‏ירוק. ‏החשד שלך (‏הרצות מקבילות) ‏מתיישב עם ההתנהגות.
**‏ניסוח DoD 2 סגור**: "‏אף טסט שעבר ב-baseline אינו נופל בסוף", ‏עם ‏DoD 0 ‏שרושם את
‏ה-baseline לפני כתיבת קוד — ‏זה מדיד, ‏חסין-מקביליות, ‏ואינו נשען על מספר קבוע. ‏אין ממצא.

### ‏שאלה 7 — "‏האם ריככתי יותר מדי?" → **‏לא. ‏§7 ‏של הבריף הוא על-קבוצה של §6 ‏במשימה.**

| ‏משימה §6 | ‏בריף §7 |
|---|---|
| 1 ‏רתמה ירוקה לפני Commit 2 | ✅ ‏קיים, ‏מסומן "‏החשוב ביותר" |
| 2 ‏`subscribe`/`host.state` לא-סינכרוניים | ✅ ‏עבר ל"‏נבדק מראש" **‏אחרי אימות בקוד** — ‏לגיטימי |
| 3 ‏effect לפני `historyEpoch` | ✅ ‏קיים מילה-במילה |
| 4 ‏מסלול-היסטוריה נוסף שאינו reset/session-update | ✅ ‏לא הוסר. ‏`_drive/reset` **‏הוא** ‏session/update ⇒ ‏מעולם לא ענה על התנאי |
| 5 ‏תרחיש ג' לא בר-ביטוי | ✅ ‏קיים, **‏והורחב** ‏ל"‏ג' ‏או ‏ה'" |

‏שני ה"‏ריכוכים" ‏שציינת:
- **‏`_drive/reset`** — ‏אומת בקוד: `reduce.ts:598` ‏מחזיר `messages: []` ‏תמיד
  (‏הפולטים ‏`session-host.ts:796`, ‏`:847` — ‏שני העוגנים מדויקים). ‏`historyMarkFromReset([])`
  ‏מחזיר mark ריק. ‏הוצאתו מרשימת-העצירה **‏נכונה**.
- **"‏ערך שאינו 8"** — ‏המשימה מעולם לא דרשה עצירה על זה; ‏היא דרשה עצירה על **‏ירוק**.
  ‏הבריף **‏מוסיף** ‏תנאי-עצירה, ‏ומגדר אותו בטסט-השפיות. ‏זה הידוק, ‏לא ריכוך.

⇒ ‏**‏אין כאן ריכוך-יתר.**

---

## ‏חלק ב' — ‏בעיות שנמצאו

### 🔴 Blocker / Regression risk

| # | ‏בעיה | ‏מקור (‏brief / ‏קוד) | ‏עלות |
|---|---|---|---|
| 1 | **‏תרחיש ה' ‏מודד `0` ‏על הבסיס, ‏לא `> 0`.** ‏הבריף מצהיר (‏§evidence-3 ‏ממצא 3, ‏"‏אומת מחדש מול `b323c36d`") ‏ש"‏היום ה-ids יציבים ‏ולכן המונים שורדים ‏והתוכן שהצטבר בפער **‏כן** ‏נאמר". ‏זה היה נכון **‏לפני** ‏מיזוג `acp-method-names` ‏— ‏וכבר לא. | brief §evidence-3/3 · §2 ‏"‏לא — ‏בכוונה" · §4 Commit 1 ‏תרחיש ה' · **DoD 6** · §6 ‏סיכון 4 / `speaker.svelte.ts:302` · `sse-reader.ts:82` · `apply-patch-mutable.ts:137` · `remote-session-view.ts:372` | **30-60 ‏דק'** |

**‏השרשרת, ‏כפי שנמדדה:**

1. ‏בתור חי מעל HTTP ‏הבועה צוברת ‏`k` ‏סגמנטים (`append-segment` ‏פר-chunk),
   ‏ו-`#bubbleStates[id].processedSegments = k`.
2. ‏SSE נופל. ‏`#handleReconnected` (`remote-session-view.ts:372`) ‏פולט `reset`
   ‏עם `snapshot.messages`.
3. ‏ה-snapshot החדש עובר ‏`foldSnapshot` (`sse-reader.ts:82`) — ‏`reduce` ‏על
   ‏`updates[]`. ‏**‏ה-updates הם הודעות-שלמות מכווצות** ⇒ ‏הודעה אחת = **‏סגמנט אחד**
   ‏עם כל הטקסט (‏כולל מה שהצטבר בפער). ‏ה-id **‏זהה** (`m_0`) — ‏אומת ב-probe.
4. ‏`applyPatchMutable` case `"reset"` (`:137`) ‏עושה `splice(0, len, ...)` ⇒
   ‏`bubble.segments.length === 1`.
5. ‏`#processBubbles`: ‏`state.processedSegments (k) >= segArr.length (1)` → ‏**`continue`**
   (`speaker.svelte.ts:302`). ‏התוכן שהצטבר בפער **‏לא נאמר — ‏היום, ‏על הבסיס, ‏לפני הסלייס.**

**‏מה זה שובר:**
- ‏תרחיש ה' ‏יימדד `0` ‏גם **‏לפני** ‏Commit 2 ‏וגם **‏אחריו**. ‏DoD 6 ("‏5 ‏תרחישים עוברים —
  ‏**‏כולל ה'**") ‏אינו בר-סיפוק. ‏אליעזר יראה אנטי-רגרסיה אדומה ‏ויחפש רגרסיה שהוא לא יצר.
- ‏הנימוק ב-§2 ‏להוצאת reset-של-reconnect מהסימון ("‏שם התוכן שהצטבר בפער **‏טרם נשמע**.
  ‏סימונו = ‏רגרסיה") ‏מתאר תוכן ש**‏ממילא אינו נשמע היום**. ‏ההכרעה עצמה עדיין
  ‏הנכונה (‏שמרנית, ‏ותקפה ל-WS ‏ולעתיד) — ‏אבל ‏**‏הראיה שמתחתיה בטלה**.

> ‏זו בדיוק החתימה של `faithful-but-inadequate`: ‏הבריף מצטט את ההתנהגות **‏נכון**
> ‏(‏ids יציבים · ‏`sessionMsgToBubble → msg.id` · ‏`append-segment` ‏append-only —
> ‏שלושתם אומתו ונכונים), ‏ואיש לא שאל אם ההתנהגות **‏שורדת את שינוי-החוט**
> ‏שנחת בבסיס באמצע הריצה. ‏`to-session-update.ts:85` ‏מוזכר בבריף **‏פעמיים**,
> ‏שתיהן בהקשר "‏למה 8 ‏נשאר 8" — ‏ואף פעם בהקשר "‏מה זה עושה למונה".

**‏מה אני ‏*‏לא*‏ ‏אומרת:** ‏שהתיקון שגוי. ‏Commit 2 ‏עובד למסלול הראשי
(‏attach ראשון: ‏`#bubbleStates` ‏ריק → ‏mark קובע 1 → ‏append-segment חי נותן 2 > 1 → ‏נאמר ✅).
‏ההכרעה מה למרוח ‏ומתי — ‏עומדת. ‏מה שצריך תיקון הוא ‏**‏הציפייה של תרחיש ה' ‏והראיה שמצדיקה אותה**.

---

### 🟡 Confusion / Type error / Outdated

| # | ‏בעיה | ‏מקור | ‏הצעה |
|---|---|---|---|
| 2 | **‏יחידת-החתך אינה יציבה מול הכיווץ.** ‏`segmentCounts` ‏סופר סגמנטים; ‏החוט מכווץ אותם. ‏אחרי **‏כל** ‏reset שבא אחרי streaming חי (‏reconnect · ‏attach שני · ‏החלפת-view), ‏המונה נשאר `k` ‏בעוד המערך ‏`1` — ‏ולכן ‏`k-1` ‏הסגמנטים החיים הבאים **‏נבלעים בשקט** ‏עד שהמערך יעבור את `k`. ‏ההגנה "‏לעולם לא להוריד מונה" ‏ב-`#applyHistoryMark` ‏מנציחה את זה (‏היא נחוצה לתרחיש ד' — ‏ולכן זה מתח אמיתי, ‏לא באג בהגנה). | brief §4/2ג / `speaker.svelte.ts:302` · `to-session-update.ts:85` | ‏לתחום במפורש: ‏הסלייס נשען על מודל-הספירה **‏רק ל-attach הראשון**. ‏לרשום את חוסר-היציבות כבאג נפרד ב-`bugs/` (‏מועמד: ‏חתך לפי **‏אורך-טקסט מצטבר** ‏במקום אינדקס-סגמנט) |
| 3 | ‏`grep "register-then-snapshot"` ‏= ‏**8** ‏מופעים (‏בלי `dist/`), ‏לא 4. ‏הבריף קובע "‏4 ‏מופעים בלבד; **‏אין אתר-קיבוע חמישי**". ‏הארבעה שלא נמנו: ‏`patches-broadcaster.ts:6` · ‏`patches-broadcaster.test.ts:10` ‏ו-`:162` (‏כותרת `describe`) · ‏`session-host-http.integration.test.ts:263`. **‏אף אחד אינו נשבר** (‏בלי `since` ‏ההתנהגות נשמרת), ‏אבל שלושה הופכים לתיעוד-שקר, ‏והאחרון יושב בדיוק בקובץ ש-Commit 3 ‏כן נוגע בו. ‏פקודה אחת הייתה תופסת. | brief §4 Commit 3 / ‏4 ‏הנתיבים | ‏לתקן את הספירה ‏ולהוסיף את ‏`:263` ‏לרשימת-ההערות-לעדכון (‏לצד `:303`/`:351`) |
| 4 | **‏פקודת-המשימה מפנה לבריף הבטל.** ‏`missions/replay-quiet.md` (`2245eeb`) ‏אומרת "‏בריף: … @ `8080a62`" — ‏וזו בדיוק הגרסה שהבריף עצמו מכריז עליה כ**‏בטלה** ‏בכותרתו (‏"‏(ב) `8080a62`, ‏שבה Commit 2 ‏סימן 'הכל' ‏בזמן flush-ה-effect"). ‏הבריף החי הוא `68b75fb`. ‏זה בדיוק מנגנון-הכשל ש-§כותרת נכתבה כדי למנוע. | mission ‏כותרת / brief ‏כותרת · docs-repo log | ‏לעדכן את המשימה ל-`68b75fb`, ‏או להסיר את ה-pin |

---

### 🟢 Minor

| # | ‏בעיה | ‏מקור |
|---|---|---|
| 5 | ‏`serializeFrame` **‏אינו** ‏מיוצא מ-`@drive-coding/core/session/testing` — ‏`wire-fixtures.ts` ‏מייצא רק `IntentFrame` · ‏`toWireFrames` · ‏`toWireText`. ‏הוא מגיע מ-`@drive-coding/core/session` (‏re-export של `wire-frames.ts` ‏דרך ‏`session/index.ts`). ‏Commit 1(ד) ‏מורה `toWireFrames(frames).map(serializeFrame)` ‏בלי לומר שאלה **‏שני** ‏specifiers | brief §4 Commit 1(ג)+(ד) / `wire-fixtures.ts:24-66` |
| 6 | ‏`subscribe()` ‏מוצהר **‏פעמיים**: ‏בממשק ‏`PatchesBroadcaster` (`patches-broadcaster.ts:24`, ‏עם doc ב-`:21-22`) ‏ובמימוש (`:118`). ‏Commit 3 ‏מונה רק `:118` ‏ו-`:135` | brief §3 + §4 Commit 3 |
| 7 | ‏"**‏9 ‏מ-11**" ‏מופיע פעמיים (‏§5 ‏שורת-סיכום, ‏§8 ‏נימוק ה-`light`). ‏טבלת ה-DoD מונה **‏12** ‏שורות (0–11): ‏**10** ‏פקודה, ‏**2** ‏עיניים. ‏שריד מגרסה קודמת | brief §5 · §8 |
| 8 | ‏סחיפת-שורות של 1–3 ‏בעשרה עוגנים. **‏כל הטקסט קיים ואומת** — ‏זה קוסמטי, ‏אבל שיטתי: ‏`speaker.svelte.ts` ‏`:303`→**302**, ‏`:344`(‏ה-enqueue)→**343**, ‏`:421`→**422** · ‏`remote-session-view.ts` ‏`:213`→**211**, ‏`:297`→**298** · ‏`apply-patch-mutable.ts` ‏`:27`→**28**, ‏`:32`→**33**, ‏`:52`→**51**, ‏`:95`→**98** · ‏`events.ts` ‏`:153-155`→**155-157** · ‏`…integration.test.svelte.ts` ‏`:59-71/:62`→**57-70/61** · ‏`speaker.test.svelte.ts:1`→**2**. ‏המלצה: ‏לעגן בתבנית | ‏פזור ב-§3/§4 |

---

## Spot-check ‏שעבר (‏לא מצא בעיה)

**‏עוגנים מדויקים לחלוטין (‏שורה + ‏תוכן):**

- ✅ `speaker.svelte.ts` — ‏`:57` `MIN_CHARS = 20` · ‏`:117` `#bubbleStates` · ‏`:121` `#recentTexts`
  · ‏`:136` `#processedNarrationCallIds` · ‏`:176` `$effect.root` · ‏`:209-216` ה-`untrack` ‏על
  ‏ארבע הקריאות **‏בסדר המדויק שהבריף מצטט** · ‏`:266-281` ‏ענף `isLoadingHistory` · ‏`:276-279`
  ‏מלכודת ה-`speakPending` · ‏`:285` ‏סינון-kind · ‏`:290-299` ‏ענף thought-off · ‏`:304-307` ‏השרשור
  · ‏`:332` `splitIntoSentences` · ‏`:450-451` ‏טבעת ‏`#recentTexts` ‏עם תקרת 8 · ‏`:538` `debugInfo()`
  · ‏`:684-686` ‏ענף isLoadingHistory ‏בכלים · ‏`:693` ‏שומר `#processedNarrationCallIds`
  · ‏`:715` ‏דחיפת-job · ‏`:844-855` ‏העותק השלישי. ‏גם ‏`MAX_CHARS = 200` ‏אומת (‏תואם לטסט-השפיות).
- ✅ `#enqueue(kind, messageId, text, bubbleId?)` — ‏`bubbleId` **‏אכן** ‏זמין ב-scope של ‏`:450`.
- ✅ `SpeakerDebugInfo` ‏מחזיק **‏בדיוק 4** ‏שדות (`playback-registry.ts:51-`).
- ✅ `remote-session-view.ts` — ‏`:114` ‏חיווט `onReconnected` ‏בקונסטרוקטור · ‏`:214` ‏ה-`op:"reset"`
  ‏של ה-hydration · ‏`:219` ‏**`#emit([resetPatch])` — ‏מערך בן איבר אחד** (‏מקיים את כלל
  "‏ה-batch הראשון") · ‏`:259` `#drainUpdates` · ‏`:317-319` `#emit` ‏= ‏`enqueue` ‏יחיד בלי coalescing
  · ‏`:372` ‏ה-reset של ‏reconnect · **‏`:210` ‏— ‏ההערה המיושנת ‏`#drainPatches` ‏אכן שם, ‏בדיוק כפי שהבריף מזהיר.**
- ✅ `agent-session.svelte.ts` — ‏`:27` ‏ייבוא type-only ‏ו-`:103` ‏ייבוא-ערך, ‏**‏שניהם בלי `Patch`**
  ⇒ ‏אזהרת "‏דורש ייבוא חדש" ‏נכונה · ‏`:225`/`:1506`/`:1587` ‏שלושת אתרי `#consumeViewPatches`
  · ‏`:259` `isLoadingHistory` · ‏`:600` ‏החתימה · ‏`:621` `if (patches.length === 0) continue`
  · ‏`:623` `applyPatchMutable` · ‏`:684` ‏הקורא-הריק המקומי. ‏**‏כל טענות ה-additive/parallel-safe מחזיקות.**
- ✅ `events.ts` — ‏`:14` ‏התיעוד · ‏`:129-130` ‏ההערה · ‏`:131` `subscribe()` · ‏`:162` `host.state`
  · ‏`:163` `let view = snapshot` · ‏`:189-190` `applyPatch`+`updateFrame`.
  **‏אומת: ‏בין ‏`:131` ‏ל-`:162` ‏אין `await`** (‏רק ‏`doSetInterval` ‏סינכרוני) ⇒ ‏ההיפוך בר-ביצוע,
  ‏ו-`let view = snapshot` ‏אינו נפגע. ‏גם ‏`currentEpoch` ‏מחושב **‏לפני** ‏ה-`stream()` ⇒ ‏אינו מושפע.
- ✅ `events.test.ts:12` ‏doc-header · ‏`:237` ‏ה-`describe` · ‏`:285` ‏האסרשן
  `expect(stateIdx).toBeGreaterThan(subscribeIdx)` — ‏**‏שלושתם מדויקים לשורה.**
- ✅ `patches-broadcaster.ts:17` `BUFFER_SIZE = 64` · ‏`:68` `buffer.push` ‏בתוך `dispatch`
  · ‏`:97` `async function drain()` · ‏`:118` `subscribe(): ReadableStream<Patch>` ‏**‏בלי פרמטר**
  · ‏`:135` ‏לולאת ה-replay. ‏האינווריאנטה "‏ההוספה ל-buffer אסינכרונית" — ‏מחזיקה.
- ✅ `session-host.ts` — ‏`:176` ‏ו-`:644` `get state()` ‏**‏סינכרוניים** · ‏`:712` `emitPatches([`
  ‏עם ‏`:719` ‏שמקדם את ה-version **‏באותו בלוק סינכרוני** · ‏`:796`/`:847` ‏שני ה-resets.
- ✅ **‏`emitPatches` — ‏18 ‏מופעים, ‏מהם 2 ‏הגדרות (`:137`, `:370`) ⇒ ‏בדיוק ‏16 ‏אתרי-קריאה.**
  ‏המספר בבריף **‏נכון**.
- ✅ `reduce.ts:598` — ‏`op: "reset"` ‏עם `messages: []` **‏בדיוק על השורה**, ‏עם הערת-קוד שמפנה
  ‏ל-`session-host.ts` 796/847. ‏מסלול ‏`_drive/reset` ‏שפיר כפי שנטען.
- ✅ `types.ts:114-131` — ‏`SessionMessage` ‏union לפי `role`, ‏**‏בדיוק 4** ‏ערכים,
  ‏`thought` ‏אכן נושא `segments`, ‏`tool` ‏נושא `toolCall`. ‏**‏`narration` ‏אינו ב-`SessionToolCall`** —
  ‏אומת, ‏ולכן החצי-השני של התיקון (`toolCallIds`) ‏מוצדק.
- ✅ `apply-patch-mutable.ts` — ‏`sessionMsgToBubble` ‏נותן ‏`id: msg.id` ‏לשני הענפים,
  ‏`toolCall.toolCallId` ‏לכלים, ‏ו-`append-segment` ‏עושה ‏`b.segments.push()` ‏בלבד (‏append-only ✓).
- ✅ `sse-reader.ts:277` ‏(‏`connect()` ‏מחזיר snapshot) ‏ו-`:298` ‏(`#runLoop` ‏מושק אחריו)
  ‏ו-`:443` ‏(`onReconnected` ‏נקרא רק מ-`#runLoop`) — ‏**‏שלושתם מדויקים** ⇒ ‏"‏reconnect לא יכול
  ‏להיות ה-batch הראשון" ‏מוכח.
- ✅ `vitest.config.ts:34` = `environment: "node"` · ‏**‏34** ‏קובצי `*.test.svelte.ts` · ‏מהם
  ‏**‏בדיוק אחד** ‏מצהיר jsdom (`speaker.test.svelte.ts`). ‏שלושת המספרים נכונים.
- ✅ `speaker.test.svelte.ts` — ‏**‏חמשת ה-`vi.mock` ‏מדויקים ושלמים**: ‏`$lib/adapters/voice/tts-resolve`
  (‏:20) · ‏`./capabilities.svelte` (‏:31) · ‏`../adapters/voice/translate` (‏:41) ·
  ‏`../adapters/voice/narrate` (‏:42) · ‏`@drive-coding/core/voice/cache-key` (‏:45),
  ‏ו-stub ה-`localStorage` ‏ב-`:49-65`. ‏הטווח ‏`:16-65` ‏מכסה את כולם. ‏`makeSession()` ‏אכן
  ‏cast **‏בלי** ‏`historyEpoch`. ‏`makeMockSink()` ‏ב-`:83-96`. ‏**‏`it(` = ‏בדיוק 7** ⇒ ‏DoD 8 ‏נכון.
- ✅ `remote-session-view.test.ts:944` — ‏`describe("RemoteSessionView — reconnect mid-turn")`
  ‏קיים, ‏ומשתמש ב-`keepOpen:false` + `_sleep: noSleep`. ‏תקדים תקף לתרחיש ה'.
- ✅ `session-host-http.integration.test.ts` — ‏`:164` ‏לולאת-ה-deadline (‏אינה זורקת),
  ‏`:303` ‏ו-`:351` ‏שתי ההערות. **‏קראתי את גופי שני הטסטים**: ‏שניהם קובעים על
  ‏`computeFinalClientState(frames)` ‏בלבד, ‏לא על ‏`frames.length` ‏ולא על `frames[i]` ⇒
  ‏**‏הטענה "‏הטסטים עצמם שורדים" ‏נכונה**, ‏והעלות היא 300ms deadline לכל אחד.
- ✅ `c507fda0..b323c36d` = ‏**‏3 ‏קומיטים, ‏24 ‏קבצים, ‏1691 ‏הוספות** — ‏מדויק לספרה.
- ✅ ‏בדיקת-הטרום 1: ‏אפס `historyEpoch` ‏בריפו · ‏אין `history-mark.ts` · ‏אין `bubbleStates`
  ‏ב-`debug/` · ‏`subscribe()` ‏בלי פרמטר ⇒ ‏**‏העבודה טרם בוצעה**, ‏כפי שנטען.
- ✅ ‏`integration/run-replay-quiet` ‏קיים ומצביע ל-`b323c36d`, ‏זהה ל-`integration/acp-playback`.
  ‏פקודת ה-worktree ‏ב-§0 ‏תקינה. ‏העץ נקי.
- ✅ ‏מוסכמות ‏`AGENTS.md`: ‏`history-mark.ts` ‏נכנס ל-`packages/frontend/src/lib/view-models/`
  ‏כפונקציה טהורה ‏(‏לא ל-`core/`, ‏שם היה נדרש `Result`) — ‏עקבי. ‏אין `any`, ‏אין CommonJS,
  ‏אין מצב-מודול חדש, ‏אין מחרוזות-עברית בקוד. ‏ה-`$state` ‏החדש הוא שדה-מופע ב-VM, ‏לא ברמת-מודול.

---

## ‏Verdict — 🟡 USABLE-AFTER-FIX

‏הבריף הזה ‏**‏מדויק בצורה יוצאת-דופן** ‏ברמת העוגנים: ‏מתוך ‏כ-70 ‏טענות-קוד שבדקתי,
‏אחת בלבד שגויה מהותית, ‏ומספרי-השורות שנסחפו נעים ב-1–3 (‏כל הטקסט קיים).
‏שלוש ההכרעות של §3, ‏שרשרת "‏ה-batch הראשון", ‏סינכרוניות ה-BE, ‏16 ‏אתרי ה-`emitPatches`,
‏חמשת ה-`vi.mock`, ‏שבעת טסטי ה-Speaker, ‏ושרידות שני טסטי-האינטגרציה — ‏**‏כולם אומתו ומחזיקים**.

‏מה שחוסם הוא ממצא אחד, ‏והוא ‏**‏בדיוק ה-blind-spot שהזזת-הבסיס פתחה**: ‏הבריף שאל על כל
‏סמל "‏האם הוא מצוטט נכון?" ‏וענה נכון — ‏אבל לא שאל על ‏`to-session-update.ts:85`
"‏**‏האם המונה שורד את הכיווץ?**". ‏התשובה היא לא, ‏ולכן תרחיש ה' ‏אינו בר-סיפוק כפי שנוסח.

**‏מה מספיק כדי להפוך ל-READY (‏~20 ‏דק' ‏של מרדכי):**
1. ‏למדוד את תרחיש ה' ‏על הבסיס, ‏ואז ‏**‏או** ‏לנסח אותו כ"‏אין שינוי מול baseline"
   ‏**‏או** ‏להוציאו מ-DoD 6 ‏ולרשום את הכיווץ-מול-המונה כבאג נפרד ב-`bugs/`.
2. ‏למשוך את ‏§evidence-3 ‏ממצא 3 ‏**‏בגוף המסמך** (‏לא רק להפסיק להסתמך עליו) — ‏עם ה-probe ‏ששלל.
3. ‏ממצאים 3–4 (‏ספירת ה-grep, ‏ה-pin במשימה) — ‏שורה כל אחד.
4. ‏5–8 ‏רשות.

‏ממצא 2 ‏אינו חוסם dispatch, ‏אבל **‏חייב להיאמר במפורש בבריף** ‏כתיחום, ‏אחרת הוא ייפול על כלב.
