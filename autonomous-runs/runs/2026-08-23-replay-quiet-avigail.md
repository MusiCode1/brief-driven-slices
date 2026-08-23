---
project: "drive-coding"
slice: "replay-quiet-by-reset"
verifier: "avigail"
date: "2026-08-23"
round: 1
base: "integration/acp-playback @ c507fda0"
verdict: "NEEDS-REWORK"
findings:
  - id: 1
    severity: "blocker"
    category: "gate-cannot-fail"
    summary: "הרתמה תרוץ תחת environment node ותצא ירוקה-בשקר — הקובץ היחיד ב-FE שמריץ Speaker אמיתי מצהיר jsdom, והבריף לא מזכיר זאת"
    source_brief: "§4 Commit 1"
    source_code: "packages/frontend/vitest.config.ts:34 · packages/frontend/src/lib/view-models/speaker.test.svelte.ts:1"
    cost_estimate: "30-60min + עצירת-ריצה מיותרת"
  - id: 2
    severity: "blocker"
    category: "dropped-branch"
    summary: "isLoadingHistory מסמן שני מאגרים; historyEpoch מכסה רק אחד — narration של כלים היסטוריים תישאר"
    source_brief: "§4 Commit 2"
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:684-686"
    cost_estimate: "תיקון חלקי שעובר את הרתמה ונופל חי"
  - id: 3
    severity: "regression"
    category: "dropped-branch"
    summary: "op reset נפלט גם ב-SSE reconnect ולא רק ב-attach — סימון הכל כמעובד ישתיק תוכן שטרם נשמע בכל ניתוק באמצע תור"
    source_brief: "§4 Commit 2"
    source_code: "packages/frontend/src/lib/session/remote-session-view.ts:340-370"
    cost_estimate: "רגרסיה חיה בתרחיש הנהיגה; לא נתפסת ע'י תרחישי הרתמה א-ד"
  - id: 4
    severity: "blocker"
    category: "faithful-but-inadequate"
    summary: "טסט קיים מקבע את הסדר הנוכחי subscribe-לפני-state ויישבר ב-Commit 3; DoD 2 דורש אפס נופלים"
    source_brief: "§4 Commit 3 · §5 DoD 2"
    source_code: "packages/backend/src/session-host/http/events.test.ts:237-286 · events.ts:14,111-112"
    cost_estimate: "15-30min בלבול red-vs-intended"
  - id: 5
    severity: "confusion"
    category: "dropped-branch"
    summary: "makeSession במוק של speaker.test חסר historyEpoch — undefined !== 0 יפעיל את ענף-האפוק בכל הטסטים הקיימים"
    source_brief: "§4 Commit 2"
    source_code: "packages/frontend/src/lib/view-models/speaker.test.svelte.ts:71-81"
    cost_estimate: "10-20min"
  - id: 6
    severity: "confusion"
    category: "faithful-but-inadequate"
    summary: "התבנית שהבריף מפנה אליה דוחפת את כל פריימי ה-SSE ב-enqueue סינכרוני יחיד — בדיוק מה שאילוץ 2 אוסר"
    source_brief: "§4 Commit 1"
    source_code: "packages/frontend/src/lib/view-models/remote-session-view.integration.test.svelte.ts:57-70"
    cost_estimate: "20-40min"
  - id: 7
    severity: "confusion"
    category: "missing-symbol"
    summary: "markAllProcessed אינו קיים — הפסאודו-קוד קורא לו כאילו הוא קיים; יש שלושה עותקים inline של הלוגיקה"
    source_brief: "§4 Commit 2"
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:266-281,290-299,844-855"
    cost_estimate: "10min"
  - id: 8
    severity: "regression"
    category: "unrun-claim"
    summary: "markAllProcessed סופר segments.length בזמן flush-ה-effect ולא בזמן ה-reset — סגמנט חי שנחת בין השניים יסומן ולא ייאמר"
    source_brief: "§3 · §4 Commit 2"
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:176-216"
    cost_estimate: "תרחיש ב/ג ייפול או יעבור-בשקר"
  - id: 9
    severity: "confusion"
    category: "dropped-branch"
    summary: "return בתוך ה-untrack ידלג גם על handleStatusTransition ועל עדכון prevStatus/prevTurnState"
    source_brief: "§4 Commit 2"
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:209-216"
    cost_estimate: "15min"
  - id: 10
    severity: "confusion"
    category: "gate-cannot-fail"
    summary: "DoD 4 מורה על git stash לשינוי שכבר בקומיט — stash אינו נוגע בקומיטים"
    source_brief: "§5 DoD 4"
    source_code: "—"
    cost_estimate: "10min"
  - id: 11
    severity: "minor"
    category: "wrong-line-number"
    summary: "המלכודת על speakPending מיוחסת ל-283-287; המקום המתועד בפועל הוא 276-279"
    source_brief: "§4 Commit 2"
    source_code: "packages/frontend/src/lib/view-models/speaker.svelte.ts:276-279"
    cost_estimate: "5min"
  - id: 12
    severity: "minor"
    category: "unique"
    summary: "הפניה תלויה אל §9 שאלה 6 — ב-§9 יש ארבע שאלות בלבד; שריד מהגרסה הקודמת"
    source_brief: "§evidence-2 מסקנה 2"
    source_code: "—"
    cost_estimate: "2min"
  - id: 13
    severity: "minor"
    category: "unique"
    summary: "§8 טוען 7 מתוך 8 בדיקות-DoD הן פקודה; בפועל 6 — DoD 6 ו-8 הן עיניים"
    source_brief: "§8"
    source_code: "—"
    cost_estimate: "2min"
  - id: 14
    severity: "minor"
    category: "gate-cannot-fail"
    summary: "DoD 6 עלול להבהב — הסינון חל רק על שחזור-החוצץ; פאצ' שנפלט וטרם נוקז יימסר חי אחרי הסנאפשוט"
    source_brief: "§5 DoD 6"
    source_code: "packages/backend/src/session-host/patches-broadcaster.ts:96-112"
    cost_estimate: "10min"
  - id: 15
    severity: "minor"
    category: "unique"
    summary: "ל-Commit 3 אין אפקט על הבאג — ה-FE כבר זורק כל פאצ' משוחזר לפי version"
    source_brief: "§2 · §4 Commit 3"
    source_code: "packages/frontend/src/lib/session/remote-session-view.ts:290"
    cost_estimate: "0 — דיוק-ניסוח"
---

# Plan Verification — replay-quiet-by-reset

> **Brief**: `docs-for-llm/plans/slice-replay-quiet-by-reset.md`
> **Mission**: `docs-for-llm/plans/missions/replay-quiet.md`
> **Base tip**: `c507fda0` (`integration/acp-playback`) — אומת ב-worktree `.worktrees/integration-acp-playback`
> **Verdict**: ❌ **NEEDS-REWORK**
> **אומדן זמן אליעזר confusion אם לא יתוקן**: 90–150 דק', מתוכן ~40 דק' על עצירת-שווא בתנאי-העצירה #1

**למה NEEDS-REWORK ולא USABLE-AFTER-FIX**: שלושה ממצאים (2, 3, 8) מצביעים על אותה נקודה
אחת — **המנגנון של Commit 2 מסמן "הכל", בזמן flush-ה-effect, על מאגר אחד מתוך שניים**.
זו אינה השמטה שמתקנים בשורה; זו הכרעת-עיצוב שמרדכי צריכה לקבל מחדש (מה בדיוק מסומן,
לפי מה, ובאיזה רגע). שאר הממצאים אכן היו נסגרים בעריכה.

---

## 🔴 Blocker / Regression risk

| # | בעיה | מקור (brief / קוד) | עלות אם לא תוקן |
|---|---|---|---|
| 1 | **הרתמה תרוץ תחת `environment: "node"` ותצא ירוקה-בשקר.** ‏`packages/frontend/vitest.config.ts:34` קובע `environment: "node"` לכל ה-FE. סקירת **כל 34 קובצי ה-`*.test.svelte.ts`** מראה ש**בדיוק אחד** מצהיר `@vitest-environment jsdom` — `speaker.test.svelte.ts:1` — והוא היחיד שמריץ `Speaker` אמיתי (כלומר `$effect.root`). הקובץ החדש `agent-session.history-quiet.test.svelte.ts` יישב באותה תיקייה ו**יירש node**. זהו בדיוק תנאי-העצירה #1 של פקודת-המשימה, והבריף מזהה את הסיכון (§6 #1) אך **אינו נותן את המיטיגציה** — שהיא שורת-docblock אחת, בת-גילוי ב-grep יחיד. | brief §4/Commit 1 + §6 #1 / `packages/frontend/vitest.config.ts:34` · `speaker.test.svelte.ts:1` | הרתמה תצא 0 גם לפני וגם אחרי Commit 2 ⇒ עצירת-ריצה מיותרת לפי §7, 30–60 דק' |
| 2 | **`isLoadingHistory` מסמן שני מאגרים — `historyEpoch` מכסה אחד.** מלבד `#bubbleStates` (הודעה/מחשבה) יש `#processedNarrationCallIds` לבועות-כלי, ו-`#processToolBubbles` מסמן אותו **תחת אותו דגל בדיוק** (`speaker.svelte.ts:684-686`). ‏`narration` **אינו** חלק מ-`SessionState` (‏אפס מופעים ב-`packages/core/src/session/`), ולכן כל בועת-כלי שנבנית מ-reset מגיעה עם `narration: undefined` ו-`status:"completed"` (`apply-patch-mutable.ts:26-49`) ⇒ `#processToolBubbles` ידחוף job קריינות לכל כלי היסטורי. הפסאודו-קוד של Commit 2 קורא `#markAllProcessed(bubbles)` בלבד ומצדיק אותו רק דרך `processedSegments`. | brief §4/Commit 2 / `speaker.svelte.ts:684-686` · `packages/core/src/session/` · `apply-patch-mutable.ts:26-49` | הבאג נסגר חלקית; הרתמה (הודעות בלבד) תראה 0 והשדר החי עדיין ידבר |
| 3 | **`op:"reset"` אינו רק attach — הוא גם כל SSE-reconnect.** ‏`#handleReconnected` (`remote-session-view.ts:340-370`) פולט **בדיוק אותו** `op:"reset"` כשהסנאפשוט מתקדם (`snapshot.version > #lastVersion`), כלומר בכל ניתוק-וחיבור באמצע תור. הכלל `patches.some(p => p.op === "reset") ⇒ markAllProcessed` יסמן שם גם את **התוכן שפוספס ועוד לא נאמר**. היום אין אובדן: ה-reset בונה מחדש בועות עם **אותם ids** (`sessionMsgToBubble` → `msg.id`), ולכן מוני `processedSegments` שורדים והסגמנטים החדשים כן נאמרים. ⇒ זו **רגרסיה חדשה**, ובדיוק בתרחיש שהמשימה §1 קיימת בשבילו (נהיגה, סלולר). תרחישי הרתמה א-ד **אינם כוללים reconnect**. | brief §4/Commit 2 / `remote-session-view.ts:340-370` · `apply-patch-mutable.ts:25,128-131` | אובדן-שמע שקט בשטח, לא נתפס בשום שער |
| 4 | **Commit 3 שובר טסט קיים שמקבע את הסדר ההפוך.** ‏`events.test.ts:237-286` — ‏`describe("register-then-snapshot: subscribe before snapshot")` עם `expect(stateIdx).toBeGreaterThan(subscribeIdx)`. בנוסף החוזה מוצהר ב-doc-header `events.ts:14` ובהערות `:111-112`. הבריף מתאר את היפוך-הסדר ואינו מזכיר את הטסט ואת שני מקומות-התיעוד, בעוד DoD 2 דורש "**אפס נופלים**". | brief §4/Commit 3, §5 DoD 2 / `events.test.ts:237-286` · `events.ts:14,111-112` | 15–30 דק'; סיכון שאליעזר "יתקן" בחזרה לסדר הישן |

---

## 🟡 Confusion / Regression-risk / Type

| # | בעיה | מקור | הצעה |
|---|---|---|---|
| 5 | ‏`makeSession()` ב-`speaker.test.svelte.ts:71-81` מחזיר `{status, turnState, isLoadingHistory, bubbles}` ב-cast ל-`AgentSession` — **בלי `historyEpoch`**. הקריאה ב-Speaker תחזיר `undefined`, ו-`undefined !== this.#seenHistoryEpoch(0)` ⇒ ענף-האפוק יילקח **בכל 7 טסטי ה-Speaker הקיימים** בריצה הראשונה. | `speaker.test.svelte.ts:71-81` | לציין במפורש ש-Commit 2 מעדכן גם את המוק |
| 6 | תבנית ה-BE המדומה שהבריף מפנה אליה, ‏`sseBody()` ב-`remote-session-view.integration.test.svelte.ts:57-70`, עושה `ctrl.enqueue(...)` **אחד** לכל הפריימים המצורפים במחרוזת אחת. זה בדיוק ה"לולאה סינכרונית" שאילוץ #2 של פקודת-המשימה אוסר. הבריף מפנה לתבנית כאילו היא מתאימה כמות-שהיא. | `remote-session-view.integration.test.svelte.ts:57-70` | להצהיר שהתבנית נדרשת התאמה: enqueue פר-פריים עם `await` ביניהם |
| 7 | ‏`#markAllProcessed` **אינו קיים**. הפסאודו-קוד קורא לו כאילו הוא קיים; הלוגיקה חיה היום בשלושה עותקים inline (`:266-281` ענף ה-history · `:290-299` ענף thought-off/disabled · `:844-855` ב-`#stopAndClear`). | `speaker.svelte.ts:266-281,290-299,844-855` | להצהיר "יוצרים מתודה חדשה, מאחדת את 3 העותקים" |
| 8 | **הרגע שבו נספרים הסגמנטים.** ה-`$effect` נשטף אסינכרונית ביחס ללולאת `#consumeViewPatches`; ‏`#markAllProcessed(bubbles)` יסמן `segments.length` **בזמן ה-flush**, לא בזמן ה-reset. אם `append-segment` חי נחת בין השניים — הוא ייבלע. הבריף מנמק רק ש"ה-effect יראה את שניהם", ולא ש"לא יראה יותר מדי". זה בדיוק כשל-ה-over-fix ש§6 #2 מזהיר מפניו. | brief §3 · §4/Commit 2 / `speaker.svelte.ts:176-216` · `agent-session.svelte.ts:600-640` | לתפוס את הספירה מתוך ה-`reset` עצמו (`patch.messages`), לא מ-`bubbles` בזמן flush |
| 9 | מיקום ה-`return` בפסאודו-קוד. אם הוא בתוך ה-callback של `untrack` (`speaker.svelte.ts:209-216`) הוא מדלג גם על `#handleStatusTransition` וגם על `#prevStatus`/`#prevTurnState` ⇒ הריצה הבאה תראה prev מיושן. | `speaker.svelte.ts:209-216` | לציין מפורשות מאיזו פונקציה חוזרים |
| 10 | DoD 4 מורה `git stash` על Commit 2 — ‏`stash` אינו נוגע בשינוי שכבר בקומיט. ה-DoD מתקיים ממילא מסדר ה-TDD (הרצה אחרי Commit 1). | brief §5 DoD 4 | לנסח כ"הרצה אחרי Commit 1, לפני Commit 2" |

---

## 🟢 Minor

| # | בעיה | מקור |
|---|---|---|
| 11 | המלכודת על `speakPending` מיוחסת ל-`speaker.svelte.ts:283-287`; המקום המתועד בפועל הוא `:276-279` (ושוב `:296-298`, `:851-854`). ה-anchor קיים — רק המספר זז. | brief §4/Commit 2 |
| 12 | ‏§evidence-2 מסקנה 2 מפנה ל"§9 שאלה 6"; ב-§9 יש **ארבע** שאלות. שריד מהגרסה הקודמת של הבריף. | brief §evidence-2 |
| 13 | ‏§8 טוען "7 מ-8 הן פקודה"; DoD 6 (DevTools) ו-8 (קונסול) הן עיניים ⇒ 6 מ-8. | brief §8 |
| 14 | DoD 6 ("אפס פאצ'י-שחזור") עלול להבהב: הסינון של Commit 3 חל רק על **שחזור-החוצץ**. פאצ' שנפלט אך טרם נוקז ל-`buffer` ברגע ה-subscribe (`drain()` אסינכרוני) יימסר **חי** אחרי הסנאפשוט, עם `version <= snapshot.version`. ה-FE יזרוק אותו, אבל ה-EventStream כן יראה `patch`. | `patches-broadcaster.ts:96-112` |
| 15 | ‏Commit 3 אינו משפיע על הבאג הנצפה: ה-FE כבר זורק כל פאצ' משוחזר ב-`remote-session-view.ts:290` (`if (patch.version <= this.#lastVersion) return`). ערכו האמיתי = רוחב-פס + הכנה ל-`sse-resume`. כדאי לומר זאת מפורשות כדי שלא ייקרא כאילו הוא חלק מהתיקון. | `remote-session-view.ts:290` |

---

## Spot-check שעבר (לא מצא בעיה)

- ✅ `BUFFER_SIZE = 64` ב-`patches-broadcaster.ts:17` — מדויק. `subscribe()` היום **בלי פרמטר** (`:19-24`, `:116`).
- ✅ `broadcaster.subscribe()` ב-`events.ts:113`; ההערה `register-then-snapshot` ב-`:111-112` — שני המספרים מדויקים.
- ✅ **תנאי-עצירה #2 אינו נדלק**: `host.state` הוא getter סינכרוני (`session-host.ts:176`, `:644` — `return currentState`), ‏`subscribe()` סינכרוני לחלוטין. בין `:113` ל-`:137` אין `await` (רק `doSetInterval`) ⇒ ההיפוך בר-ביצוע בלי לפתוח פער.
- ✅ **האינווריאנטה של Commit 3 מחזיקה בכל האתרים.** נבדקו כל 20+ אתרי `emitPatches` ב-`session-host.ts`. החריג-לכאורה ב-`:712` אכן מקדם `currentState.version` ב-`:719` באותו בלוק סינכרוני; ומעבר לכך, ההוספה ל-`buffer` מתרחשת ב-`drain()` **האסינכרוני** (`patches-broadcaster.ts:96-111`), כלומר תמיד אחרי שהבלוק הסינכרוני נסגר. ⇒ החוצץ ⊆ הסנאפשוט.
- ✅ `#consumeViewPatches` ב-`agent-session.svelte.ts:600`; `applyPatchMutable` ב-`:623`; אין `await` בין `:623` לסוף האיטרציה ⇒ ה-`historyEpoch++` אכן באותו בלוק סינכרוני.
- ✅ `#consumeViewPatches` נקרא **רק** משלושה מסלולי remote (`:225`, `:1506`, `:1587`); המסלול המקומי משתמש בקורא-ריק (`:684`) ⇒ Commit 2 אינו נוגע ב-WS, בהתאם ל-scope.
- ✅ `isLoadingHistory` קיים (`agent-session.svelte.ts:259`) ומזין `LoadingModal` ב-`+page.svelte:291` **ובדיוק** ב-`AppShell.svelte:415`. שני המספרים מדויקים.
- ✅ `apply-patch-mutable.ts:89` = `b.segments.push(patch.segment)` — מדויק, ו-`append-segment` הוא אכן append-only. (‏`reset` ב-`:128-131` מחליף את המערך כולו, אבל ids הבועות יציבים דרך `msg.id`.)
- ✅ `SpeakerDebugInfo` קיים ב-`playback-registry.ts:51` עם 4 שדות: `inFlight`/`queued`/`lookahead`/`recent`. שלושת השדות שהבריף מוסיף אינם קיימים (grep: אפס `historyEpoch`/`bubbleStates`/`recentSources`). `Speaker.debugInfo()` ב-`speaker.svelte.ts:538`.
- ✅ הציטוט שמצדיק את Commit 0 מדויק מילה במילה — `audio-playlist.svelte.ts:195-197` ("אינו משנה סדר-השמעה… אפשר להכניס אותו לפני שמכריעים איך לתקן").
- ✅ שני קובצי-המקור של הרתמה קיימים: `remote-session-view.integration.test.svelte.ts` (‏תחת `view-models/`, לא `session/`) ו-`speaker.test.svelte.ts` עם `makeMockSink()` שסופר `prepareSegment` (`:84-97`).
- ✅ **DoD 2 = 2808 מדויק.** הרצה מלאה על הבסיס: `Test Files 242 passed | 3 skipped (245)` · `Tests 2808 passed | 21 skipped (2829)`, 146s. הבסיס ירוק לחלוטין.
- ✅ `BACKLOG.md` פריט 13 ("הסרת `__dc`") קיים — המתח ש-§4/Commit 0 מצהיר עליו אמיתי ומתועד נכון.
- ✅ `proxy-auth.ts:27` — `env["ELEVENLABS_API_KEY"]` ו-`if (!key) return null`. הנימוק ב-§evidence-2 מדויק.
- ✅ **מוסכמות `AGENTS.md`**: אין מצב חדש ב-`core/` · אין IO ב-`core/` · אין adapters ב-`core/` · השינוי כולו ב-`view-models/` וב-`backend/session-host/` · `historyEpoch` הוא `$state` ב-VM (שכבה נכונה). אין חריגת-שכבה.
- ✅ **עקביות עם פקודת-המשימה**: `base`/`depends_on: []` תואמים · תרחיש ב' (`> 0`) אכן ב-DoD (§5 שורה 5) · נתיב-הדוחות היחיד מוצהר ב-§0 בדיקה 5 · §5.1 ו-§9 אינם טוענים מעבר לנמדד.

---

## Verdict

❌ **NEEDS-REWORK** — Commit 2 (הליבה) דורש הכרעה מחודשת, לא עריכה:

1. **מה מסומן** — שני מאגרים, לא אחד (ממצא 2).
2. **מתי נמדד** — ברגע ה-`reset`, לא ברגע flush-ה-effect (ממצא 8).
3. **על אילו resets** — `attach` בלבד, או גם `reconnect`? כרגע הכלל תופס את שניהם ויוצר רגרסיה (ממצא 3).

בנוסף, שני שערים לא יעבדו כפי שנכתב: הרתמה (ממצא 1 — שורה אחת, אך בלעדיה הריצה נעצרת
בתנאי-עצירה #1) ו-DoD 2 מול הטסט המקבע ב-BE (ממצא 4).

**ההערכה החיובית**: הבסיס נמדד ירוק (2808), ‏11 מתוך 13 טענות-הקוד של הבריף אומתו
**מדויקות עד מספר-השורה**, ותנאי-העצירה #2 (סינכרוניות) נבדק ואינו נדלק. הבריף מדויק
בתיאור הקוד הקיים; מה שחסר הוא השאלה השנייה — **האם הקוד המצוטט שורד את השינוי**.
