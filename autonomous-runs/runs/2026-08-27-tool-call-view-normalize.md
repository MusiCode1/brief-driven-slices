---
run: 21
date: 2026-08-27
project: drive-coding
mission: docs-for-llm/plans/missions/ui-polish-bubbles.md (המשך אחרי S1/S2)
slices: [tool-call-view-normalize]
interventions_product: 1
interventions_plumbing: 3
handoff_failures: 2
permanent_fixes: 0
plan_rounds: 2
brief_to_dispatch: "0:05"
verdict: החזיקה
---

# דוח-ריצה 21 — `tool-call-view-normalize`

> הדוח הזה על ה*ריצה*, לא על הפרויקט. אימות-תוכן: `reports/drive-coding/tool-call-view-normalize-{avigail,calev}.md`.

## שעון ה-plan-gate

| מדד | ערך | הסף |
|---|---|---|
| סבבי אביגיל עד dispatch | **2** (סבב 1 USABLE-AFTER-FIX + דלתא READY) | 1 + דלתא על ממצאים 🟡 ✅ |
| זמן-קיר בריף→dispatch אליעזר | דקות אחרי READY | ≤ שעתיים ✅ |
| חריגת-תקרה | אין | אין ✅ |

## מה נמסר

3 קומיטים (`a939ec17` · `472e93d7` · `e0e47d94`) + merge `931ac783` → **`edge`**. FE בלבד. **לא מוזג ל-`dev`.**

## סשנים שנפתחו ונסגרו

| agentId | מי | מסלול | נסגר? | ראיה |
|---|---|---|---|---|
| `1a173ac1-…` | אביגיל (HTTP, לא המאמת) | api :4022 | ✅ | `DELETE` 204 |
| `48a13cd0-…` | אליעזר | tmux/acpx | ✅ | `sessions close` + `tmux kill` |
| `21dc7b4f-…` | אליעזר | api :4022 | ✅ | `DELETE` 204 אחרי DONE |
| `d4c722eb-…` | כלב | api :4022 | ✅ | `close --agent` 204 |

## התערבויות-משתמש

| # | מה נשאל/נדרש | סוג | היה נמנע אילו… |
|---|---|---|---|
| 1 | "למה ACPX?" | **צנרת** | השיגור הראשון היה `dispatch-via-api.mjs`, לא `dispatch-agent` |
| 2 | לסגור סוכנים בסיום הריצה | **צנרת** | חובת-הסוגר רצה אחרי כל turn, לא רק אחרי תזכורת |
| 3 | `busy` ברשימה משקר — להציץ ב-`/state` | **צנרת** | המעקב היה `GET /state.turnState` (+ הודעות), לא `AgentPublic.busy` |
| 4 | שער-עיניים + "מאשר" | **מוצר** | — לגיטימי |

**מוצר: 1 · צנרת: 3.**

## כשלי-מסירה

| # | הכשל | "X" שנחשב ל-"Y" | עלות |
|---|---|---|---|
| 1 | שיגור אביגיל/אליעזר דרך acpx | **פרוטוקול BDS ישן** נחשב ל-**מסלול drive-coding** | אליעזר נעצר באמצע C3; הושלם ב-API |
| 2 | `GET /api/agents` `busy:false` בזמן `turnState: calling-tool` | **דגל הרשימה** נחשב ל-**מצב התור** | איחור בזיהוי סיום כלב; נתפס ב-`/state` |

## מה השערים תפסו — ומה חמק

| שער | תפס | פספס |
|---|---|---|
| אביגיל | 3 ממצאי TDD/תיעוד (command non-string, path vs fields, trim) | — |
| כלב | מוטציה 3/37 אדומים; DoD 1–9 | #10 עיניים (במכוון) |
| **המשתמש** | מסלול השיגור + סגירת סוכנים + `busy` | — |

## תיקונים קבועים

אין commit חדש לתבנית בריצה הזו: `dispatch-via-api.mjs` + חובת-הסוגר + שני השלבים **כבר כתובים** ב-`kickoff-mordechai.md` מ-27/08. הכשל הוא אי-ציות, לא חור במסמך.

לקח למעקב: **`busy` אינו אות-תור.** האות הוא `GET /state` → `turnState`.

## מה עדיין לא נבדק

- Slice B (Speaker / קריינות מ-description)
- `bugs/50` / `_meta`
- מיזוג `edge` → `dev`

## הערכה

הסלייס הגיע ל-`edge` אחרי GO + עיניים. הצנרת דלפה שלוש פעמים לאותו שורש: מסלול-שיגור/מעקב של drive-coding קיים ולא נבחר עד שהמשתמש תיקן.
