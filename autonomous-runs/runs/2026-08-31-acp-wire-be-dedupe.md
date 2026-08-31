---
run: 29
date: 2026-08-31
project: drive-coding
mission: docs-for-llm/plans/missions/acp-wire-be-dedupe.md
slices: [acp-wire-be-dedupe]
interventions_product: 0
interventions_plumbing: 1
handoff_failures: 0
permanent_fixes: 1
plan_rounds: 1
brief_to_dispatch: "~0:15"
verdict: החזיקה — מוזג ל-integration/run-acp-wire-be בלבד
---

# דוח-ריצה 29 — `acp-wire-be-dedupe`

> הדוח הזה על ה*ריצה*, לא על הפרויקט.
> אימות-תוכן: `$BDS_REPORTS/drive-coding/acp-wire-be-dedupe-{avigail,calev}.md`

## שעון ה-plan-gate

| מדד | ערך | הסף |
|---|---|---|
| סבבי אביגיל עד dispatch | **1** (USABLE-AFTER-FIX → תיקון-במקום) | 1 ✅ |
| זמן-קיר בריף→dispatch | **~15 דק׳** | ≤ שעתיים ✅ |
| חריגת-תקרה | הקפאת Claude — `cli=cursor` (Grok / Composer 2.5) | אין ✅ |

## מה נמסר

סידור BE / ביטול כפילות wire: `InProcessAcpTransport` → `acp-wire` `from-line-wire`;  
`provider` re-export של `AcpTransport`; SessionHost צורך מהחבילה.  
מוזג ל־**`integration/run-acp-wire-be` @ `d79e150f`** (לא `edge`/`dev`/`main`).

קומיטים: `b8aaa61e` (C0) · `e412b3fe` (C1) · `fad262fb` (C2) · merge `d79e150f`.

כלב **GO 8/8**.

## סשנים שנפתחו ונסגרו

| agentId | מי | מסלול | נסגר? | ראיה |
|---|---|---|---|---|
| `1c99d00c-a1da-4e3f-8892-6727ee745a62` | מרדכי (cursor / grok-4.6) | MCP · פתחתי אני | ✅ | `session_close` → `{ok:true}` |
| `530fd2a0-…` | אביגיל | MCP (ילד) | ✅ | דוח מרדכי / נעלמה מהרשימה |
| `18d49463-…` | אליעזר | MCP · Composer 2.5 | ✅ | דוח מרדכי |
| `5fadea78-…` | כלב | MCP · Composer 2.5 | ✅ | דוח מרדכי |

צופה `autorun-watch-awbd` (systemd-run): `DONE` + stop אחרי מסירה.

## התערבויות-משתמש

| # | מה | סוג |
|---|---|---|
| 1 | טיק חי ≠ עובד — חובת בדיקת הודעות/git/דוחות; תיעוד ב־fact + autorun SKILL + Action בצופה | **צנרת** (+ תיקון קבוע) |

**מוצר: 0 · צנרת: 1**

## כשלי-מסירה

אין על תוכן הסלייס.

## מה השערים תפסו

| שער | תפס |
|---|---|
| אביגיל | 2 ממצאים (דריסת `index.ts`; נוסח `onClose`) → תיקון-במקום |
| כלב | GO 8/8 כולל מוטציה |
| **המשתמש** | ממתין — מיזוג ל־`edge` |

## תיקונים קבועים שנוצרו

| # | התיקון | נכנס ל- |
|---|---|---|
| 1 | חי ≠ עובד בטיק; Action מפורט | basic-memory עובדת צופה · `autorun/SKILL.md` · סקריפט צופה |

## מה עדיין לא נבדק / מחוץ לסקופ

- connect unix/HTTP לגשר (`AGENT_ACP_WIRE`)
- מיזוג ל־`edge`/`dev`

## הערכה

הריצה **החזיקה**: plan-gate סבב אחד, runtime GO, מיזוג לענף-הרצה בלבד.  
החסם הבא: אישור משתמשת ל־`edge` / סלייס connect.
