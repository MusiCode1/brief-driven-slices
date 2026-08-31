---
run: 28
date: 2026-08-31
project: drive-coding
mission: docs-for-llm/plans/missions/acp-wire-http.md
slices: [acp-wire-http]
interventions_product: 0
interventions_plumbing: 1
handoff_failures: 0
permanent_fixes: 0
plan_rounds: 1
brief_to_dispatch: "~0:16"
verdict: החזיקה — מוזג לענפי-ההרצה בלבד (שני ריפואים)
---

# דוח-ריצה 28 — `acp-wire-http`

> הדוח הזה על ה*ריצה*, לא על הפרויקט.
> אימות-תוכן: `$BDS_REPORTS/drive-coding/acp-wire-http-{avigail,calev,run}.md`

## שעון ה-plan-gate

| מדד | ערך | הסף |
|---|---|---|
| סבבי אביגיל עד dispatch | **1** (USABLE-AFTER-FIX → תיקון-במקום) | 1 ✅ |
| זמן-קיר בריף→dispatch | **~16 דק׳** (בריף ~11:31 → אליעזר 11:47) | ≤ שעתיים ✅ |
| חריגת-תקרה | הקפאת Claude — כל השיגורים `cli=cursor` (Grok / Composer 2.5) | אין ✅ |

## מה נמסר

שלב 2: Streamable HTTP ב־`@drive-coding/acp-wire` + `listenHttp`/שער HTTP ב־`cursor-sdk-acp`.  
מוזג ל־**`integration/run-acp-wire`** בשני הריפואים (מעל tip שלב 1):

- drive-coding @ **`d74592c5`** — לא ב־`edge`/`dev`/`main`
- cursor-sdk-acp @ **`8ea3c6d`** (C2=`1e202fb`, C3=`8ea3c6d`) — לא ב־`main`

כלב **GO 5/5** (`acp-wire-http-calev.md`). אין UI / אין עיניים.

## סשנים שנפתחו ונסגרו

| agentId | מי | מסלול | נסגר? | ראיה |
|---|---|---|---|---|
| `41054ff8-bd03-41c6-9b18-e793f0a87ecb` | מרדכי (cursor / grok-4.6) | MCP · פתחתי אני | ✅ | `session_close force` → `{ok:true}` אחרי `notify_parent` |
| `c18452d7-48c4-41fc-8960-8528e57b9bda` | אביגיל | MCP (ילד מרדכי) | ✅ | דוח מרדכי |
| `e5644960-4af5-4d57-8012-cc7dff94e76a` | אליעזר | MCP | ✅ | דוח מרדכי |
| (כלב) | כלב | לא נפתח משרשור מרדכי; דוח קיים | ✅ | `acp-wire-http-calev.md` + אימות-מחדש בדוח מרדכי |

צופה tmux `autorun-watch-awh`: `DONE` + `kill-session` אחרי מסירה.

## התערבויות-משתמש

| # | מה | סוג |
|---|---|---|
| 1 | צופה ראשון מת / לא `notify` — שחזור לתבנית proven + `dispatch-via-api notify` | **צנרת** (חזר על לקח 30–31/08) |

**מוצר: 0 · צנרת: 1**

(ממצא אביגיל על `LISTEN=http:` שתולה stdio — תוקן-במקום בבריף; נספר כצנרת-מוצר בתוך הסלייס, לא התערבות משתמש.)

## כשלי-מסירה

אין על תוכן הסלייס.  
צופה ad-hoc נפל אחרי `WATCH_START`; הוחלף בעותק של תבנית הצופה המוכחת.

## מה השערים תפסו

| שער | תפס |
|---|---|
| אביגיל | 1 ממצא (LISTEN תולה stdio) → תיקון-במקום |
| כלב | GO 5/5 כולל מוטציית HTTP → exit≠0 ≤10s |
| **המשתמש** | ממתין — מיזוג החוצה ל־`edge`/`dev`/`main` |

## תיקונים קבועים שנוצרו

אין קומיט לשיטה. עובדת צופה/`notify` כבר ב־basic-memory.

## מה עדיין לא נבדק / מחוץ לסקופ

- שלב 3 (BE כלקוח ACP)
- מיזוג ל־`edge`/`dev`/`main`

## הערכה

הריצה **החזיקה**: plan-gate סבב אחד, runtime GO, מיזוג לענפי-ההרצה בלבד.  
החסם הבא: אישור משתמשת למיזוג החוצה / שלב 3.
