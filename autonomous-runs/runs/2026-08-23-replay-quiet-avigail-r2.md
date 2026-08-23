---
project: "drive-coding"
slice: "replay-quiet-by-reset"
verifier: "avigail"
date: "2026-08-23"
round: 2
base_declared: "integration/acp-playback @ c507fda0"
base_actual: "integration/acp-playback @ b323c36d"
verdict: "NEEDS-REWORK"
findings:
  - id: 1
    severity: "blocker"
    category: "missing-dependency"
    summary: "הבסיס זז — integration/acp-playback הוא b323c36d ולא c507fda0; שלושה קומיטים החליפו את פרוטוקול-החוט ונגעו ב-24 קבצים, ביניהם כל הקבצים שהבריף מצטט"
    source_brief: "§0 Worktree · שורה 4 base"
    source_code: "git log c507fda0..integration/acp-playback"
    cost_estimate: "30-60min"
  - id: 2
    severity: "blocker"
    category: "gate-cannot-fail"
    summary: "הערך 8 אינו ניתן למדידה על הבסיס החדש — הסנאפשוט מכווץ את כל הסגמנטים של הודעה לאחד; נמדד בהרצה 8 נכנסים segCount 1 יוצא"
    source_brief: "§4 Commit 1 · §5 DoD 4 · §7"
    source_code: "packages/core/src/session/to-session-update.ts:85"
    cost_estimate: "עצירת-ריצה שקרית בתנאי-העצירה הראשי"
  - id: 3
    severity: "blocker"
    category: "unrun-claim"
    summary: "הבסיס אינו ירוק ו-2808 אינו המספר — נמדד 2834 passed, ‏247 קבצים, ואחד נופל דטרמיניסטית (https-serve)"
    source_brief: "§0 בדיקה 6 · §5 DoD 2"
    source_code: "packages/backend/tests/https-serve.test.ts:53"
    cost_estimate: "20-40min"
  - id: 4
    severity: "blocker"
    category: "dropped-branch"
    summary: "קיים מסלול שלישי שפולט op reset — _drive/reset ב-reduce; §7 מגדיר בדיוק את זה כתנאי-עצירה"
    source_brief: "§evidence-3 ממצא 3 · §3 הכרעה 3 · §7"
    source_code: "packages/core/src/session/reduce.ts:598 · packages/backend/src/session-host/session-host.ts:796,847"
    cost_estimate: "עצירה מיותרת 15-30min"
  - id: 5
    severity: "confusion"
    category: "faithful-but-inadequate"
    summary: "תבנית הרתמה ב-Commit 1 מתארת קוד שכבר לא שם — sseBody עובר דרך toWireText, ותשתית-הבדיקה החדשה core/session/testing אינה מוזכרת"
    source_brief: "§4 Commit 1 מקורות להעתקה"
    source_code: "packages/frontend/src/lib/view-models/remote-session-view.integration.test.svelte.ts:62 · packages/core/src/session/__testing__/wire-fixtures.ts"
    cost_estimate: "30-45min"
  - id: 6
    severity: "outdated"
    category: "faithful-but-inadequate"
    summary: "Commit 3 מותיר אתר-תיעוד שני סותר — הערות frame-count ב-session-host-http.integration.test שמתארות שחזור שיפסיק לקרות"
    source_brief: "§4 Commit 3 רשימת-קבצים"
    source_code: "packages/backend/src/session-host/http/session-host-http.integration.test.ts:303,351"
    cost_estimate: "15min + 600ms timeout מיותר בכל הרצה"
  - id: 7
    severity: "confusion"
    category: "wrong-line-number"
    summary: "עוגני events.ts זזו במיזוג ונוסף ביניהם קוד חדש — view = applyPatch שיושב בין קריאת הסנאפשוט ללולאה"
    source_brief: "§evidence-3 · §4 Commit 3"
    source_code: "packages/backend/src/session-host/http/events.ts:131,162,189"
    cost_estimate: "10-15min"
  - id: 8
    severity: "confusion"
    category: "missing-symbol"
    summary: "drainPatches אינו קיים — המתודה היא drainUpdates; השם השגוי אמור להיכתב לתוך הערת-קוד קבועה"
    source_brief: "§3 הכרעה 3 · §4 Commit 2ב"
    source_code: "packages/frontend/src/lib/session/remote-session-view.ts:259"
    cost_estimate: "5min"
  - id: 9
    severity: "minor"
    category: "wrong-line-number"
    summary: "תשעה עוגנים זזו במיזוג — כולם קיימים, רק המספר שונה"
    source_brief: "§3 · §4 Commit 2"
    source_code: "remote-session-view.ts:214,372,297 · apply-patch-mutable.ts:25,95 · speaker.svelte.ts:303 · speaker.test.svelte.ts:70,83"
    cost_estimate: "5min"
  - id: 10
    severity: "minor"
    category: "unrun-claim"
    summary: "אתרי emitPatches הם 16 ולא 20+"
    source_brief: "§evidence-3 · §4 Commit 3"
    source_code: "packages/backend/src/session-host/session-host.ts"
    cost_estimate: "2min"
  - id: 11
    severity: "minor"
    category: "unique"
    summary: "השכתוב אינו מקומט — הבריף האחרון בגיט הוא 8080a62, בדיוק הרוויזיה שפקודת-המשימה מצמידה"
    source_brief: "§0 אזהרת השכתוב-במקום"
    source_code: "git -C ~/Projects/docs-repo status --short"
    cost_estimate: "2min"
  - id: 12
    severity: "minor"
    category: "type-error"
    summary: "Patch אינו מיובא ב-agent-session — הקטע Extract<Patch> דורש import type חדש"
    source_brief: "§4 Commit 2ב"
    source_code: "packages/frontend/src/lib/view-models/agent-session.svelte.ts:27,103"
    cost_estimate: "3min"
---

# Plan Verification — replay-quiet-by-reset (r2)

> **Brief**: `docs-for-llm/plans/slice-replay-quiet-by-reset.md` (‏שכתוב מלא #2, **לא מקומט**)
> **Mission**: `docs-for-llm/plans/missions/replay-quiet.md`
> **Base שהוצהר**: `integration/acp-playback` @ `c507fda0`
> **Base בפועל**: `integration/acp-playback` @ **`b323c36d`** ‏— ‏`git log -1` ב-worktree שנמסר לאימות
> **Verdict**: ❌ **NEEDS-REWORK**
> **אומדן זמן אליעזר confusion אם לא יתוקן**: 90–150 דק', מתוכן ~45 דק' על שתי עצירות-שווא (‏ממצא 2 ו-4)

**זהו verdict מסוג אחר מ-r1.** ב-r1 הבעיה הייתה בעיצוב Commit 2. **העיצוב החדש נכון** —
כל שלוש ההכרעות אומתו ומחזיקות, כולל טענת "‏ה-batch הראשון" שהיא הכי קשה לאימות
(‏ר' §Spot-check). מה ששבר את הסבב הזה הוא שהקרקע זזה מתחת לבריף: **הבסיס התקדם
בשלושה קומיטים שהחליפו את פרוטוקול-החוט**, ואיתו נשמט הערך `8` שעליו הריצה כולה
נשענת כתנאי-עצירה.

---

## 🔴 Blocker / Regression risk

| # | בעיה | מקור (brief / קוד) | עלות אם לא תוקן |
|---|---|---|---|
| 1 | **הבסיס זז.** הבריף מצהיר `c507fda0`; ‏`integration/acp-playback` הוא היום **`b323c36d`** — שלושה קומיטים קדימה (`37e6c1c0` reduce v2 · `ff684d30` "`Patch` יורד מהחוט" · `b323c36d` merge `acp-method-names`). ‏§0 יוצר את ה-worktree **משם-הענף** (`git worktree add … integration/acp-playback`) ⇒ אליעזר יקבל את `b323c36d`, לא את מה שהבריף מתאר. ה-diff הוא **24 קבצים, ‏1691 הוספות**, וביניהם **כל** קובץ שהבריף מצטט: `events.ts` · `events.test.ts` · `remote-session-view.ts` · `apply-patch-mutable.ts` · `sse-reader.ts` · `remote-session-view.integration.test.svelte.ts`. הפרוטוקול עצמו הוחלף: `event: patch`+`Patch` → `event: update`+**batch JSON-RPC של `session/update`**, וגוף ה-snapshot מ-`SessionState` גולמי ל-`{sessionId, version, epoch, updates[]}`. | brief שורה 4 + §0 / `git log c507fda0..integration/acp-playback` | 30–60 דק' של "‏למה הקובץ לא נראה כמו בבריף" |
| 2 | **הערך `8` אינו בר-מדידה על הבסיס החדש — הגייט המרכזי של הריצה ייכשל-בשקר.** ‏`stateToSessionUpdates` ממפה כל הודעה דרך `messageToUpdate`, ושם: `const text = m.segments.map((s) => s.text).join("")` (`to-session-update.ts:85`) ⇒ **כל הסגמנטים של הודעה מתכווצים לבלוק-טקסט אחד**. הרצתי probe על הבסיס: ‏8 סגמנטים פנימה → `stateToSessionUpdates` → `reduce` → **`segCount: 1`**, `texts: ["seg0. seg1. … seg7. "]`, ‏`msgId: "m_0"` נשמר. כלומר ה-snapshot שה-FE מקפל מחזיק **סגמנט אחד להודעה היסטורית**, וכמות ה-enqueues שהרתמה תמדוד נקבעת מעכשיו ע"י `splitIntoSentences` על טקסט מאוחד — לא ע"י מספר הסגמנטים. המדידה החיה `8/8` ב-§evidence-2 נלקחה על **החוט הישן**. הבריף מעלה את `8` לדרגת אינווריאנטה קשיחה בשלושה מקומות (§4/Commit 1 "‏לאמת בהרצה שהתרחיש א' באמת מודד **8**" · §5 DoD 4 "‏באדום היא מודדת **8**, לא 0" · §7 "‏או מודדת ערך שאינו 8" = **תנאי-עצירה #1, "‏החשוב ביותר"**), ופקודת-המשימה §3/#1 ו-§6/#1 חוזרות עליה. ⇒ הרתמה תמדוד מספר אחר, ואליעזר **חייב** לעצור לפי ההוראה. | brief §4/Commit 1 · §5 DoD 4 · §7 · §evidence-2 / `packages/core/src/session/to-session-update.ts:85` (‏probe מוצא: `segCount: 1`) | עצירת-ריצה על ראיה תקינה; זה ההפך מהמטרה של האילוץ |
| 3 | **הבסיס אינו ירוק, והמספר ב-DoD 2 שגוי.** ‏§0 בדיקה 6 מצהיר "‏✅ נמדד … `242 passed, 3 skipped` · `2808 passed, 21 skipped`", ו-DoD 2 מקבע `2808` + "‏**אפס נופלים**". הרצתי `bun run test` על `b323c36d` עכשיו: **`Test Files 1 failed \| 243 passed \| 3 skipped (247)`** · **`Tests 2834 passed \| 24 skipped (2858)`**, ‏259s. הנופל הוא `packages/backend/tests/https-serve.test.ts` — *"Server on https://127.0.0.1:39231 did not start in time"* — **ושחזרתי אותו בבידוד** (‏`bunx vitest run tests/https-serve.test.ts` → `1 failed`, פורט אחר, אותו כשל). ⇒ DoD 2 כפי שנוסח אינו בר-סיפוק על המכונה הזו, ואליעזר יבזבז זמן על כשל שאינו שלו. | brief §0 בדיקה 6 · §5 DoD 2 / `packages/backend/tests/https-serve.test.ts:53` | 20–40 דק' דיבוג של כשל pre-existing |
| 4 | **קיים מסלול שלישי שפולט `op:"reset"` — וזהו תנאי-עצירה מפורש בבריף.** ‏§evidence-3 ממצא 3 קובע "`op:"reset"` נפלט **בשני** מקומות", §3 הכרעה 3 בונה על כך, ו-§7 מגדיר "‏מתגלה מסלול **שלישי** שפולט `op:"reset"`" כ**עצירה-ושאלה**. ‏`grep -rn 'op: "reset"' packages/{frontend,core}/src` מחזיר **ארבעה** אתרים, מהם שלישי אמיתי: `packages/core/src/session/reduce.ts:598` — ה-handler של `_drive/reset`, שפולט `{op:"reset", messages:[]}`. הוא מגיע ל-`#consumeViewPatches` דרך `#applyIncoming → #emit(produced)`, והוא נפלט מה-BE בשני אתרים (`session-host.ts:796`, `:847`) בהחלפת-סשן. **פונקציונלית זה שפיר** — `messages: []` ⇒ `historyMarkFromReset([])` מחזיר mark ריק, ובכל מקרה `attachWindow` כבר `false` בשלב הזה. אבל אליעזר לא יודע את זה: ה-grep הראשון שלו יפגע בו, וההוראה מחייבת אותו לעצור. שים לב שפקודת-המשימה §6/#4 מנוסחת **צר יותר** ("‏מסלול שמזרים היסטוריה ואינו `reset` ואינו `session/update`") ולא הייתה נדלקת — הבריף החמיר על עצמו. | brief §evidence-3 ממצא 3 · §3 הכרעה 3 · §7 / `packages/core/src/session/reduce.ts:598` · `session-host.ts:796,847` | עצירה מיותרת 15–30 דק' |

---

## 🟡 Confusion / Outdated

| # | בעיה | מקור | הצעה |
|---|---|---|---|
| 5 | **תבנית הרתמה שהבריף מפנה אליה תוארה נכון ל-r1 ולא נכון להיום.** ‏`sseBody` הוא כעת ב-`:59-71` (לא `:57-70`), וגופו כבר **אינו** `frames.map(f => …).join("")` אלא `toWireText(frames)` — פונקציה חדשה ב-`@drive-coding/core/session/testing` (`packages/core/src/session/__testing__/wire-fixtures.ts`) שמתרגמת "‏תיאור-כוונה" (`event: snapshot` עם `SessionState` גולמי · `event: patch` עם `Patch`) לצורת-החוט האמיתית דרך `snapshotFrame`/`updateFrame`. זו **בשורה טובה** — הרתמה יכולה להמשיך לתאר כוונה — אבל אליעזר צריך לדעת שהיא קיימת, ושאילוץ "enqueue פר-פריים" מתורגם ל-`toWireFrames(frames).map(serializeFrame)` ואז enqueue לכל אחד, ולא לפיצול המחרוזת שהבריף מתאר. ‏**בנוסף**: §4/Commit 1 מונה מ-`speaker.test.svelte.ts` רק את `makeMockSink()`; רתמה שמריצה Speaker אמיתי צריכה גם את חמשת ה-`vi.mock` שלו (`tts-resolve` · `capabilities.svelte` · `translate` · `narrate` · `cache-key`) ואת stub-ה-`localStorage` (`:16-65`). | brief §4/Commit 1 / `remote-session-view.integration.test.svelte.ts:27,59-71` · `wire-fixtures.ts` · `speaker.test.svelte.ts:16-96` | 30–45 דק' |
| 6 | **Commit 3 משאיר אתר-תיעוד שני סותר — בדיוק הכשל ש-§4/Commit 3 מזהיר מפניו לגבי `events.ts:14`.** ‏`session-host-http.integration.test.ts` מתעד את מספרי-הפריימים כתלויים בשחזור: ‏`:303` — *"3 frames each: snapshot@v1 … → replayed 'set' patch (v1, buffered before this subscriber connected) → live 'clear' patch (v2)"*; ‏`:351` — *"4 frames: snapshot@v2 … → 2 replayed patches … → the live idle+lastTurnError patch (v3)"*. אחרי Commit 3 השחזור נעלם. **בדקתי — הטענות עצמן שורדות**: ‏`readSseFrames` אינו זורק כשמגיעים פחות פריימים (`:164` לולאה עם deadline), ו-`computeFinalClientState` מגיע לאותה מסקנה. ⇒ לא כשל, אבל **שני טסטים ישרפו את מלוא ה-300ms** של ה-timeout בכל הרצה, ושתי ההערות הופכות שקריות. רשימת-הקבצים של Commit 3 מונה רק `patches-broadcaster.ts`/`events.ts`/`events.test.ts`. | brief §4/Commit 3 / `session-host-http.integration.test.ts:200-205,303,351` | להוסיף את הקובץ לרשימה |
| 7 | **עוגני `events.ts` זזו, ונוסף ביניהם קוד חדש שיש להתחשב בו.** ‏`register-then-snapshot` `:111-112`→**`:129-130`** · `broadcaster.subscribe()` `:113`→**`:131`** · `const snapshot = host.state` `:137`→**`:162`**. ‏**אימתי מחדש שהטענה המהותית עומדת**: בין `:131` ל-`:162` אין `await` (רק `doSetInterval`) ⇒ ההיפוך של Commit 3 עדיין בר-ביצוע בלי לפתוח פער, ותנאי-עצירה #2 של המשימה אינו נדלק. אבל המיזוג הכניס `let view: SessionState = snapshot` (`:163`) ו-`view = applyPatch(view, patch)` + `updateFrame(view, patch)` בלולאה (`:189-190`) — קוד שיושב **בדיוק** בין שני הקטעים שהבריף מבקש להחליף, ואינו מוזכר בו. | brief §evidence-3 · §4/Commit 3 / `events.ts:129-131,162-163,189-190` | 10–15 דק' |
| 8 | **`#drainPatches` אינו קיים.** המתודה היא `#drainUpdates` (`remote-session-view.ts:259`); השם הישן שרד רק בהערת-קוד מיושנת ב-`:210`. הבריף מעתיק אותו פעמיים — ב-§3 הכרעה 3 וב**הערת-הקוד ש-§4/2ב מורה לאליעזר להדביק**. ⇒ שם-סמל שגוי ייכתב לקובץ קבוע. | brief §3 הכרעה 3 · §4 Commit 2ב / `remote-session-view.ts:259` | 5 דק' |

---

## 🟢 Minor

| # | בעיה | מקור |
|---|---|---|
| 9 | תשעה עוגנים זזו במיזוג (‏כולם **קיימים**, רק המספר): reset ב-`#doConnect` `:212`→**`:214`** · reset ב-`#handleReconnected` `:359`→**`:372`** · שומר-הגרסה `:290`→**`:297`** (‏ושם הוא `batch.version <= this.#lastVersion`, לא `patch.version`) · בלוק ה-hydration `:207-222`→**`:209-221`** · `sessionMsgToBubble` `:25-62`→**`:25-59`** · `segments.push` `:89`→**`:95`** · דילוג-המונה ב-`#processBubbles` `:302`→**`:303`** · `makeSession` `:71-81`→**`:70-81`** · `makeMockSink` `:84-97`→**`:83-96`** | brief §3 · §4 Commit 2 |
| 10 | אתרי `emitPatches` הם **16** קריאות (‏18 מופעי-grep, מהם 2 הגדרות), לא "‏20+". החריג ב-`:712`/`:719` — **אומת מדויק**. | brief §evidence-3 · §4 Commit 3 |
| 11 | **השכתוב אינו מקומט.** ‏`git -C ~/Projects/docs-repo status --short` → `M drive-coding/plans/slice-replay-quiet-by-reset.md`; ‏`git log -1` על הקובץ מחזיר **`8080a62`** — בדיוק הרוויזיה שפקודת-המשימה מצמידה ("‏בריף: … @ `8080a62`"). מי שיפתור את הבריף לפי ה-ref יקבל את הגרסה **הבטלה**. זו בדיוק מחלקת-הכשל ש-§0 מזהיר מפניה בעצמו. | brief §0 · mission §כותרת |
| 12 | ‏`Patch` אינו מיובא ב-`agent-session.svelte.ts` — יש שם שני ייבואים מ-`@drive-coding/core/session` (`:27` type-only, `:103` ערכי), שניהם בלי `Patch`. הקטע `Extract<Patch, { op: "reset" }>` דורש `import type` חדש. ‏`SessionMessage` ל-`history-mark.ts` **כן** מיוצא (`session/index.ts` → `export * from "./types"`). | brief §4 Commit 2ב |

---

## Spot-check שעבר — **רק טענות חדשות מ-r1**

### הטענה הקשה ביותר: "‏ה-batch הראשון" ✅ **מחזיקה**

נבדקה לגופה, לא הונחה:

- ‏`#emit` הוא `this.#patchesCtrl?.enqueue(patches)` יחיד (`remote-session-view.ts:317-319`) — **אין buffering ואין coalescing**. כל קריאה = chunk נפרד ב-`ReadableStream<Patch[]>`, וכל `read()` מחזיר אחד. ⇒ הפרדת-batch נשמרת גם אם הצרכן טרם התחיל לקרוא (ה-stream מתור).
- ה-batch הראשון הוא **בדיוק `[resetPatch]`** — איבר אחד. ⇒ התרחיש "‏reset **וגם** append-segment חי באותו batch ראשון" **אינו יכול לקרות**. (‏גם אילו קרה, ה-mark מ-`patch.messages` היה חסין — אבל אין צורך בהגנה.)
- ‏**מרוץ-הרשמה אינו קיים**: ‏`#doConnect` פולט את ה-reset ‏(`:219`) לפני `void this.#drainUpdates(updates)` ‏(`:222`), ושלושת האתרים שפולטים (`:219`, `:314`, `:384`) ממופים לשלושה מקורות בלבד.
- ‏**reconnect לא יכול להיות ראשון**: ‏`onReconnected` מחווט בקונסטרוקטור (`:114`), אבל נקרא **רק** מ-`#runLoop` (`sse-reader.ts:443`), ו-`#runLoop` מושק ב-`:298` **אחרי** ש-`connect()` כבר החזיר snapshot (`:277`). ⇒ אין חלון שבו `#handleReconnected` מקדים את ה-hydration.
- ⚠️ **הסייג שהבריף עצמו מציין נכון**: ‏`#doConnect` פולט reset רק `if (snapshot.messages.length > 0)` (`:213`). כשהסנאפשוט ריק אין reset, ו-`attachWindow` נסגר על ה-batch החי הראשון בלי mark — התנהגות נכונה. שים לב ש-`#consumeViewPatches` עושה `if (patches.length === 0) continue` **לפני** הבלוק (`:622`), כך ש-batch ריק לעולם לא סוגר את החלון.
- ‏`#consumeViewPatches` נקרא פעם אחת לכל view **טרי** בשלושת האתרים (`:225` DI · `:1506` `attachRemote` · `:1587` `attachRemoteToLiveAgent`) — כל אחד קודם לו `createRemoteView` חדש. ⇒ `attachWindow` כמשתנה-מקומי-ללולאה תקין.

### מיפוי ה-ids ב-`historyMarkFromReset` ✅ **מדויק**

- ‏`SessionMessage` הוא discriminated union לפי **`role`**, וארבעת הערכים הם בדיוק `user` · `thought` · `assistant` · `tool` (`packages/core/src/session/types.ts:114-130`). ‏אין ערך חמישי.
- ‏`user`/`thought`/`assistant` — ‏**‏`thought` אכן נושא `segments`** (וריאנט אחד לשלושתם). ‏`tool` נושא `toolCall` ו-`messageId: null` בלבד.
- ‏`toolCall.toolCallId` קיים ומגיע ל-bubble כמות-שהוא (`apply-patch-mutable.ts:32`); ‏`id: msg.id` לכל הבועות (`:27`, `:52`).
- ‏דילוג `user` מוצדק — `#processBubbles` מסנן `kind !== "message" && kind !== "thought"` (`speaker.svelte.ts:285`), ו-`user` ממופה ל-`kind: "user"`.

### "‏אין `return` מוקדם" ✅ **נכון, וזה הענף שיילקח**

- ‏`if (state.processedSegments >= segArr.length) continue` — `speaker.svelte.ts:**303**`.
- ‏**אין ענף מוקדם יותר שיוצר job**: לפניו רק `if (bubble.kind !== "message" && kind !== "thought") continue` (`:285`) ו-`if (bubble.kind === "thought" && !speakThoughts)` (`:295`) — שגם הוא מסמן-ומדלג. ה-job הראשון נדחף רק ב-`:344`.
- ‏אותו דבר בצד הכלים: ‏`if (this.#processedNarrationCallIds.has(tc.toolCallId)) continue` ב-`:693` **קודם** לכל דחיפת-job (`:715`). ⇒ הזרעת ה-Set ב-`#applyHistoryMark` אכן משתיקה קריינות היסטורית.

### שאר החדשות

- ‏**`#seenHistoryEpoch` ב-Commit 0 — לא יוצר commit שבור.** השדה **נקרא** ע"י `debugInfo()`, ולכן `noUnusedPrivateClassMembers` של biome אינו נדלק; שדה `= 0` שאיש אינו כותב אליו הוא TS תקין.
- ‏**`recentSources` — המזהה זמין באתר.** ‏`#enqueue(kind, messageId, text, bubbleId)` (`:421-427`), ובאתר ה-push של `#recentTexts` (`:450-451`) גם `bubbleId` וגם `bid` ב-scope. ⇒ "‏נדחף באותו אתר בדיוק" בר-ביצוע.
- ‏**DoD 4 בר-ביצוע כפי שנוסח** — "‏הרצה אחרי Commit 1 ולפני Commit 2, והפלט נשמר" מתקיים מסדר ה-TDD; ממצא 10 של r1 (`git stash`) נסגר.
- ‏**תרחיש ה' (reconnect) בר-ביטוי — אינו 🔴.** קיים תקדים עובד: ‏`remote-session-view.test.ts:944-1050` מפעיל את `#handleReconnected` דרך `sseBody(..., {keepOpen:false})` + `_sleep: noSleep`, כולל שתי הווריאציות (`version >` ו-`version <=`). ‏`sseBody` בקובץ האינטגרציה מתעד את הדפוס במפורש (`:50-56`).
- ‏**Commit 3 · שכתוב `events.test.ts:237-286`** — הטווח **מדויק לשורה** על הבסיס הנוכחי (‏`describe` ב-`:237`, `expect(stateIdx).toBeGreaterThan(subscribeIdx)` ב-`:285`). ארבע נקודות-החוזה מכסות את מה שהטסט הישן הגן עליו: הישן בדק **סדר-קריאות בלבד** דרך getter מכשיר, והחדש מקבע סדר-הפוך + סינכרוניות + הערך שמועבר. נקודה 4 (‏"‏פאצ' שנוחת אחרי ה-subscribe נמסר") היא **תוספת** ולא תחליף — אבל היא בדיוק האינווריאנטה שהסדר הישן הגן עליה בעקיפין. ⇒ מספק.
- ‏**אין אתר-קיבוע שלישי לסדר הישן** מעבר ל-`events.ts:14` ו-`:129-130` (‏שהבריף מכנה `:111-112`) ול-`events.test.ts:12` (‏שורת doc-header נוספת, קלה). ‏`grep "register-then-snapshot"` = ‏4 מופעים בלבד.
- ‏`environment: "node"` ב-`packages/frontend/vitest.config.ts:**34**` ✅ · ‏**34** קובצי `*.test.svelte.ts` · ‏**בדיוק אחד** מצהיר jsdom (`speaker.test.svelte.ts`) ✅ · ‏7 טסטים בקובץ ✅.
- ‏`BUFFER_SIZE = 64` (`patches-broadcaster.ts:17`) ✅ · `subscribe()` בלי פרמטר (`:118`) ✅ · replay ב-`:135` ✅ · `drain()` אסינכרוני (`:97`) והוספה ל-`buffer` דרך `dispatch` (`:68`) ✅ · החריג `:712`→`:719` ב-`session-host.ts` ✅.
- ‏עוגני ה-Speaker **כולם ללא שינוי**: `:117` `#bubbleStates` · `:121` `#recentTexts` · `:136` `#processedNarrationCallIds` · `:176-207` הקריאות הנעקבות · `:209-216` ה-`untrack` על ארבע הקריאות · `:266-281` · `:276-279` מלכודת `speakPending` · `:290-299` · `:450-451` · `:538` `debugInfo()` · `:684-686` · `:844-855`.
- ‏`SpeakerDebugInfo` עם 4 שדות ב-`playback-registry.ts` ✅ · `LoadingModal` ב-`+page.svelte:291` **וב-`AppShell.svelte:415`** ✅ · `BACKLOG.md` פריט 13 (`הסרת __dc`) ✅.
- ‏**מוסכמות `AGENTS.md`** — נבדק מחדש על העיצוב החדש: ‏`history-mark.ts` יושב ב-`packages/frontend/src/lib/view-models/` והוא **פונקציה טהורה בלי IO ובלי מצב** ⇒ אין מצב חדש ב-`core/`, אין adapters ב-`core/`, אין globals של דפדפן ב-`core/`. ‏`historyEpoch` הוא `$state` על ה-VM — השכבה הנכונה. ‏`#historyMark` הוא שדה-מופע לא-ריאקטיבי על ה-VM, לא מטמון ברמת-מודול. **אין חריגת-שכבה.**

---

## Verdict

❌ **NEEDS-REWORK.**

**העיצוב עבר.** שלוש ההכרעות של Commit 2 — שני מאגרים · חתך מ-`patch.messages` ברגע
ה-reset · רק ה-reset של ה-batch הראשון — אומתו כולן מול הקוד, כולל הטענה הקשה
("‏תמיד ה-batch הראשון") שנבדקה עד `#emit`/`enqueue`/`#runLoop` ומחזיקה. חמישה מששת
ה-🔴 של r1 נסגרו נכון.

**מה שמחייב שכתוב אינו העיצוב אלא הבסיס:**

1. ‏**הבריף מתאר codebase שאינו הבסיס.** ‏`c507fda0` מול `b323c36d` — ‏24 קבצים, פרוטוקול-חוט
   מוחלף. §0 מייצר את ה-worktree משם-הענף, כך שאליעזר יקבל את החדש בכל מקרה.
2. ‏**האינווריאנטה המרכזית של הריצה — "‏הרתמה מודדת 8" — הופרכה.** לא בטענה: ‏`to-session-update.ts:85`
   מכווץ סגמנטים, וה-probe שהרצתי החזיר `segCount: 1` מול 8 שנכנסו. ⇒ הגייט שהמשימה
   מגדירה כ"‏החשוב ביותר" ייתן עצירה על ראיה **תקינה**. צריך להחליף את המספר בתנאי
   שנגזר מהחוט החדש (למשל "‏> 0 לפני, ‏= 0 אחרי"), או לנמק מחדש מהו הערך הצפוי.
3. ‏**הבסיס אינו ירוק.** ‏2834/2858 עם קובץ אחד נופל דטרמיניסטית — מול "‏2808, אפס נופלים".
4. ‏**תנאי-עצירה #3 של הבריף כבר דלוק** (`reduce.ts:598`).

לכל ארבעתם יש תיקון קצר, אבל אף אחד מהם אינו עריכת-שורה: הם דורשים למדוד מחדש
מול `b323c36d` ולנסח מחדש את שער-הראיה. **זה סבב r2 בתקרת "‏3 סבבים בלי 🔴 חדש"
של פקודת-המשימה — ‏ארבעת ה-🔴 כאן חדשים, ורובם נובעים ממיזוג שקרה אחרי r1.**
