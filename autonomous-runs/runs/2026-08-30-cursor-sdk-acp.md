---
run: 25
date: 2026-08-30
project: cursor-sdk-acp
mission: /home/user/Projects/docs-repo/drive-coding/plans/missions/cursor-sdk-acp.md
slices: [skeleton-stdio, tools-permissions-mcp, config-resume, polish-ci]
interventions_product: 5
interventions_plumbing: 3
handoff_failures: 1
permanent_fixes: 2
plan_rounds: 1
brief_to_dispatch: ~00:05–00:15 per slice (estimated; not wall-clocked per slice)
verdict: הריצה החזיקה — 4/4 ממוזגים ל-main; נותר probe חי + רישום CLI_SPECS עם המשתמשת
---

# דוח-ריצה 25 — `cursor-sdk-acp`

> ⚠️ **הדוח הזה על ה*ריצה*, לא על הפרויקט.** מה שהקוד עושה שייך ל-`$BDS_REPORTS/cursor-sdk-acp/`
> ול-`cursor-sdk-acp/docs/decisions/`. כאן: האם המערכת שמייצרת אותו החזיקה.

## שעון ה-plan-gate  🔴

| מדד | ערך | הסף |
|---|---|---|
| סבבי אביגיל עד dispatch | **1** לכל סלייס (USABLE-AFTER-FIX → תיקון-במקום; לא לולאת READY) | **1** (+דלתא) |
| זמן-קיר בריף→dispatch | ~דקות בודדות לסלייס (לא נמדד בשעון מדויק לכל ארבעה) | **≤ שעתיים** |
| חריגת-תקרה | אין | אין |

## מה נמסר

ריפו חדש פרטי `MusiCode1/cursor-sdk-acp` · 4 סלייסים ממוזגים ל-`main` @ **`9f1dcc9`**  
(A `690095a` · B `ba3ac38` · C `ef012c0` · D `9f1dcc9`).  
שערי stdio בלי מפתח: `demo-stdio.mjs` ו-`stdio-gate-auth.mjs` — **exit 0** (אומת במתאם אחרי מסירת מרדכי).

## סשנים שנפתחו ונסגרו  🔴

| agentId | מי | מסלול | נסגר? | פקודה/ראיה |
|---|---|---|---|---|
| `2a3ce625-…` | מרדכי (ניסיון 1, **claude**) | MCP | ✅ force | נסגר אחרי הקפאת Claude |
| `2d594358-…` | מרדכי (cursor/Grok) | MCP | ✅ force | `session_close` אחרי מסירה |
| ילדים של מרדכי (אביגיל/אליעזר/כלב) | מרדכי סגר בשרשרת | MCP | ✅ (בסוף אין ילדים) | `GET /api/agents` אחרי close → `[]` תחת parent |

## התערבויות-משתמש — הספירה

| # | מה נשאל/נדרש | סוג | היה נמנע אילו… |
|---|---|---|---|
| 1 | סקופ = ACP מלא, כמה סלייסים, המתאם מתזמר | מוצר | — |
| 2 | ריפו נפרד + GitHub; רישום CLI_SPECS אחרי; מפתח אחרי | מוצר | — |
| 3 | הקפאת Claude / איסור שיגור `cli:claude` | **צנרת** | הכלל היה בזיכרון רך; המתאם עדיין שיגר Claude פעם |
| 4 | צופה heartbeat כל 5 דק' | מוצר/ניטור | — |
| 5 | העברת הצופה מ-systemd ל-tmux | מוצר (העדפת-נראות) | — |

**מוצר: 5 · צנרת: 3** (ר' גם כשלי-מסירה/תיקונים למטה על הצופה ו-Claude).

פירוט צנרת נוסף שלא בשאלת-משתמש ישירה:

| # | אירוע | סוג |
|---|---|---|
| P1 | שיגור מרדכי ראשון על Claude בניגוד לבקשות קודמות | צנרת |
| P2 | `sleep` כפול בצופה ⇒ טיק כל 10 דק' במקום 5 | צנרת |
| P3 | (מתועד) העדפת tmux אחרי systemd — לא כשל, הכרעה | — |

## כשלי-מסירה

| # | הכשל | "X" שנחשב ל-"Y" | עלות |
|---|---|---|---|
| 1 | המתאם דיווח "טיק הבא 12:35" אחרי טיק ב-12:30 | מרווח מוצהר 5 דק' = מרווח אמיתי (היה 10 בגלל sleep כפול) | בלבול משתמשת; תיקון סקריפט+restart |

## מה השערים תפסו — ומה חמק

| שער | תפס | פספס |
|---|---|---|
| אביגיל | USABLE-AFTER-FIX / תיקוני חתימה בכל סלייס | — |
| כלב (ריצה) | GO על A–D עם שערי stdio stub | probe חי מול api2 (מחוץ לסקופ בכוונה) |
| **המשתמש** | הקפאת Claude; בחירת tmux לצופה | — |

## תיקונים קבועים שנוצרו

| # | התיקון | נכנס ל- | commit / נתיב |
|---|---|---|---|
| 1 | הקפאת Claude עד הודעה חדשה | `dispatch.md` · basic-memory · `.cursor/rules/claude-quota-freeze.mdc` | קבצים מקומיים 30/08 |
| 2 | ניסוי צופה heartbeat (systemd→tmux, sleep כפול) | עובדת `צופה systemd ל-notify…` §ניסוי 2026-08-30 | basic-memory append |
| 3 | ערב: כשל `nohup`+buffer+wake עיוור (TikTak 309) | אותה עובדה §ניסוי 2026-08-30 ערב + learning `cursor-agent-heartbeats-fail-…` | basic-memory append |

## מה עדיין לא נבדק

1. **probe חי** עם `CURSOR_API_KEY` מול api2 / LocalExecutor + hooks  
2. **רישום** ב-drive-coding `CLI_SPECS` (D5) — שיחת-משתמשת, לא קומיט בריצה  
3. מדידת `brief_to_dispatch` מדויקת לכל סלייס (רק הערכה)

## הערכה

הריצה **החזיקה**: מרדכי על Grok תזמר 4 סלייסים ל-`main` בריפו חדש; שערי stdio ירוקים בלי מפתח.  
תנאי-יציאה של הניסוי (0 צנרת × 2 ריצות) **לא** — היו התערבויות צנרת (Claude + צופה).  
החסם הבא למוצר: מפתח API + החלטת רישום ב-drive-coding.
