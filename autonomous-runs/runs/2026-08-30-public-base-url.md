---
run: 24
date: 2026-08-30
project: drive-coding
mission: docs-for-llm/plans/missions/public-base-url.md
slices: [public-base-url]
interventions_product: 1
interventions_plumbing: 2
handoff_failures: 1
permanent_fixes: 0
plan_rounds: 1
brief_to_dispatch: "0:22"
verdict: החזיקה אחרי חידוש — מוזג לענף-ההרצה בלבד
---

# דוח-ריצה 24 — `public-base-url`

> הדוח הזה על ה*ריצה*, לא על הפרויקט.
> אימות-תוכן: `$BDS_REPORTS/drive-coding/public-base-url-{avigail,calev}.md`

## שעון ה-plan-gate

| מדד | ערך | הסף |
|---|---|---|
| סבבי אביגיל עד dispatch | **1** (Cursor/Grok, READY, אפס ממצאים). סבב Claude קודם מת בלי דוח — לא נספר כסבב שני | 1 ✅ |
| זמן-קיר בריף→dispatch | **0:22** (`9c3bf84` 03:32 → `session_open` אביגיל 03:53) | ≤ שעתיים ✅ |
| חריגת-תקרה | מכסת Claude — כל השיגורים אחרי החידוש `cli=cursor` (Grok לאביגיל, Composer לאליעזר+כלב) | אין ✅ |

## מה נמסר

5 קומיטים על `f79bb438` → **`integration/run-public-base-url` @ `dae6f694`**.

- `54db5cd9` feat(core): publicBaseUrl ב-CONFIG_SPECS + normalizePublicBaseUrl
- `5f167bf2` feat(backend): PUBLIC_BASE_URL ב-loadConfig + דגל CLI
- `134cea6b` feat(backend): effectiveCorsOrigins — union אוטומטי ל-CORS
- `ce20f001` feat(backend): defaultPublicUrl מ-PUBLIC_BASE_URL; ילדים loopback
- `dae6f694` docs(deploy): PUBLIC_BASE_URL ב-systemd + AGENTS.md

**לא מוזג ל-`dev`.** (`merge-base --is-ancestor dae6f694 dev` → exit 1)

## סשנים שנפתחו ונסגרו

| agentId | מי | מסלול | נסגר? | ראיה |
|---|---|---|---|---|
| `d6064795-4a44-471f-a44c-1a1582b344c0` | אביגיל (cursor / Grok) | MCP :4001 | ✅ | `session_close` אחרי `turnState: idle` + `stat` על הדוח |
| `a740ba72-71e9-42ac-8d97-9a2e3d324953` | אליעזר (cursor / Composer) | MCP :4001 | ✅ | `session_close` אחרי `git log` 5 קומיטים @ `dae6f694` |
| `dafa3669-b5ae-4617-933a-364de29aba76` | כלב (cursor / Composer, light) | MCP :4001 | ✅ | `session_close` אחרי `stat` + פלט DoD 6 |

לא נסגרו (לא נפתחו בסבב הזה): `5174b41a`, `5c4d0ed3`, `49eb65bf`, `de726ced`.

## התערבויות-משתמש

| # | מה נשאל/נדרש | סוג | היה נמנע אילו… |
|---|---|---|---|
| 1 | חידוש אחרי סגירת-כוח של סשן Claude (מכסה) + הוראה מפורשת `cli: cursor` בלבד | **מוצר** | המכסה לא נגמרת; ה-fallback כבר כתוב ב-`dispatch.md` |
| 2 | סשן Claude-אביגיל נתקע על Write pending ונחסם — משתמש חידש | **צנרת** | גלאי-קיפאון על `turnState` / כתיבה תקועה (פער ישן, ריצה 14) |
| 3 | הסשן הקודם כתב/ניסה לכתוב דוח מחוץ ל-`$BDS_REPORTS/…/main/reports` | **צנרת** | הנתיב היחיד היה בגוף השיגור מההתחלה (תוקן בחידוש, לא בתבנית) |

**מוצר: 1 · צנרת: 2.**

## כשלי-מסירה

| # | הכשל | "X" שנחשב ל-"Y" | עלות |
|---|---|---|---|
| 1 | סשן Claude כתב ל-`brief-driven-slices/reports/` במקום `…/main/reports` | "BDS_REPORTS" = כל checkout של הריפו | סבב אביגיל שנזרק + חידוש |

נתפס ע"י המשתמש לפני החידוש, לא בייצור.

## מה השערים תפסו — ומה חמק

| שער | תפס | פספס |
|---|---|---|
| אביגיל | אפס ממצאים — עוגנים + faithful-but-inadequate על CONFIG_SPECS / parseCorsOrigins / פיצול DRIVE_CODING_BASE | — |
| כלב (סטטי) | DoD 1 (`CONFIG_SPECS` exit 0); DoD 7 עץ נקי | DoD 2–5 ⓘ declared — light, מכוון |
| כלב (ריצה חיה) | DoD 6 על 4360: `Access-Control-Allow-Origin: https://drive-coding-dev.example.com` בלי `CORS_ORIGINS` | — |
| **המשתמש** | מכסת Claude + נתיב-דוח שגוי בסשן הקודם | מיזוג ל-`dev` / restart systemd / Access — מחוץ ל-DoD |

## תיקונים קבועים שנוצרו

אין. הנתיב היחיד וה-`cli: cursor` כבר כתובים; הכשל הוא אי-ציות של הסשן הקודם, לא חור במסמך. לא הוספתי כלל חדש כדי לא לייצר drift.

## מה עדיין לא נבדק

- PWA installable מאחורי Cloudflare Access
- restart של הפריסה החיה (4000/4001) עם `PUBLIC_BASE_URL` אמיתי
- מיזוג ל-`dev`
- DoD 2–5 כהרצה חוזרת ע"י כלב (light סומך על אליעזר)

## הערכה

אחרי החידוש הצנרת החזיקה: סבב אביגיל אחד על Cursor/Grok, אליעזר 5 קומיטים נקיים, כלב GO עם מוטציית-שער מודבקת, מיזוג FF רק לענף-ההרצה, שלושת ה-id שנפתחו נסגרו. החסם הבא הוא עיניים + אישור מיזוג ל-`dev` — לא עוד תכנון.
