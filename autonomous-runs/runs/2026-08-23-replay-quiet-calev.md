---
project: drive-coding
slice: replay-quiet
verifier: calev
date: 2026-08-23
branch: slice/replay-quiet
base: b323c36d
verdict: GO
---

# runtime-gate — replay-quiet (calev)

> **Brief:** `docs-for-llm/plans/slice-replay-quiet-by-reset.md` (read §1, §4, §5, §5.1, §evidence-2, §evidence-5)
> **Worktree:** `/home/user/Projects/drive-coding/dev/.worktrees/replay-quiet` · clean tree · 4 commits on `slice/replay-quiet`
> **Preview build:** `FE_ENV=preview FE_PREVIEW_LABEL=replay-quiet` → title **`Preview · replay-quiet · Drive Coding`** ✅
> **Live env:** BE `PORT=4241` via `bun packages/backend/src/bin/drive-coding.ts --env-file /home/user/Projects/drive-coding/.env` · Gemini TTS (`ttsProvider=google`) · HTTP transport (`?sessionTransport=http`)

## Verdict: **GO**

השערים הסטטיים כבר נסגרו (מרדכי). runtime-gate סגר את מה שנשאר: attach חי מעל HTTP, הגנה מפני over-fix, DoD 10–11, וניתוח חשד הרתמה.

---

## DoD table

| # | בדיקה | תוצאה | איך נמדד |
|---|--------|--------|----------|
| 0–3 | baseline / typecheck / tests / i18n | ✅ (spot-check) | `bun run typecheck` → 0 · `lint:i18n` נקי · לא הורצה סוויטה מלאה (כבר 246+2854 pass אצל מרדכי) |
| 4 | הרתמה אדומה לפני Commit 2 | ✅ (pre-verified) | מרדכי: revert Commit 2 → `AssertionError: expected 8 to be +0` |
| 5–9 | harness / history-mark / speaker mock / events rewrite | ✅ (pre-verified) | מרדכי: `agent-session.history-quiet` 6/6 · full suite green |
| **10** | אפס שחזור SSE (`version <= snapshot.version`) | ✅ | `node /tmp/replay-quiet-dod10.mjs` על agent `2209dc80…`: `snapshotVersion=248`, `frameCount=2`, **`replayViolations=[]`** |
| **11** | `__dc.playback().speaker` — 3 שדות | ✅ | אחרי attach חי: `bubbleStates`, `historyEpoch`, `recentSources` קיימים (`historyEpoch=1`) |
| **Live-1** | attach HTTP לסוכן חי — **0** enqueues מהיסטוריה | ✅ | Playwright take-over על opencode agent עם `version=183`, assistant **40 segs** → `recentLen=0`, `recentSourcesLen=0`, `queued=0` |
| **Live-2** | תוכן חדש **אחרי** attach — חייב להישמע (enqueue) | ✅ | אחרי attach: RPC `session/prompt` → תוך ~6s: `recent:1`, `inFlight:1` (לא over-fix) |
| **Harness-γ** | חשד לולאת `>= X` → `toBe(X)` | ⚠️ ממצא איכות-טסט | ר' §ניתוח הרתמה — לא חוסם GO |

### §5.1 — לא נבדק / לא נרשם (כמתחייב)

- "רגע כן רגע לא" · מרוץ POST↔SSE · איכות שמע · reconnect gap (§evidence-5, באג קיים) · WS · load-session · hono backpressure · `reserveTimeoutMs`

---

## 🔴 הבדיקה המרכזית — attach חי (§evidence-2)

**Setup:** סוכן opencode חי `2209dc80-8511-4a58-ad9f-afe3d007b2e7`, snapshot עם 3 הודעות (assistant 40 segments, version 183). פריוויו build + `sessionTransport=http`. Take-over דו-שלבי (Plug ×2) מהפאנל.

**מיד אחרי attach** (`__dc.playback().speaker`):

| מדד | לפני תיקון (§evidence-2) | נמדד עכשיו |
|-----|--------------------------|------------|
| פריטים שנכנסו לתור TTS (`recent` / `recentSources`) | **8 / 8** | **0 / 0** |
| `queued` / `inFlight` | — | 0 / 0 |
| `historyEpoch` | — | **1** |
| `bubbleStates` | — | `{ m_1: 1, m_2: 1 }` (חתך היסטוריה הוחל) |

**מסקנה:** המסלול הפגוע (HTTP attach לסוכן חי) **תוקן** — היסטוריה לא נכנסת לתור.

---

## 🔴 הגנה מפני over-fix

אחרי attach, `session/prompt` חדש ("Brand new live sentence…"):

- t+0..4s: `recent=0`
- t+6s: **`recent=1`, `inFlight=1`, `recentSources=1`**

⇒ תוכן **חדש** עדיין עובר ל-Speaker — אין שקט מוחלט.

*(UI TypeArea + Ctrl+Enter ב-automation לא שלח בזמן ב-run הראשון; RPC אימת את אותה שכבה.)*

---

## DoD 10 — EventStream

```
snapshotVersion: 248
frameCount: 2
replayViolations: []
```

אפס פריימים עם `version <= snapshot.version` אחרי הסנאפשוט. (חיבור SSE נשאר פתוח — נמדד 5s window.)

---

## DoD 11 — debug surface

עם `FE_ENV=preview`:

```json
"speaker": {
  "bubbleStates": { "m_1": 1, "m_2": 1 },
  "historyEpoch": 1,
  "recentSources": []
}
```

שלושת השדות החדשים **נוכחים** ב-bundle preview.

---

## ניתוח הרתמה — חשד לולאת `>= X` (§5 item 5)

**קובץ:** `packages/frontend/src/lib/view-models/agent-session.history-quiet.test.svelte.ts`

| תרחיש | דפוס | סיכון |
|--------|------|--------|
| **א** | `flushEffects` → `toBe(0)` מיידי | ✅ אין — לא משתמש בלולאת break |
| **ב** | break על `> 0`, assert `toBeGreaterThan(0)` | ✅ אין — לא assert שוויון מדויק |
| **ג** | break על `>= 4`, assert **`toBe(4)`** | ⚠️ **כן** — אם enqueues נוספים מגיעים **אחרי** ה-break, הלולאה כבר יצאה ב-4 והאסרשן עבר; קוד שבור שממשיך ל-8 עלול **לעבור בשקר** |
| **ה** | break על `>= 1`, assert **`toBe(1)`** | ⚠️ **אותו מנגנון** (פחות חמור — baseline=1) |

**אימות:** תרחיש **ג** הורץ 3× ברצף — עבר בכל פעם (65–70ms). זה **לא** מפריך את הסיכון התיאורטי; רק delay אחרי break + `expect(enqueueCount()).toBe(4)` שנייה הייתה מחזקת.

**הערכה:** ממצא **איכות-טסט** (minor), לא רגרסיה prod. השער האדום האמיתי הוא **א** (8 לפני / 0 אחרי) — סגור.

---

## בעיות סביבה (לא חוסמות GO)

1. **Enter לשליחה:** `TypeArea` שולח Enter רק אם `settings.enterToSend` (ברירת מחדל true; localStorage merge ב-automation היה בעייתי). **Ctrl+Enter** / RPC עוקפים.
2. **DoD 10 בדפדפן:** `fetch(/events)` + abort 8s נכשל; מדידה ב-Node עם deadline 5s עבדה.
3. **ריבוי agents:** כמה spawn מניסיונות automation — לא השפיע על attach למטרה.

---

## מה **לא** נבדק מחדש

Static full suite · DoD 4 red harness · WS · load-session · reconnect gap · audio quality — לפי הוראת מרדכי / §5.1.

---

## Evidence artifacts

| קובץ | תוכן |
|------|------|
| `/tmp/replay-quiet-attach-out.json` | attach + DoD11 + follow-up UI attempt |
| `/tmp/replay-quiet-dod10.mjs` output | SSE replay count |
| Preview title | `Preview · replay-quiet · Drive Coding • Sessions` |

**BE PID שנסגר:** `3613770` (PORT 4241).
