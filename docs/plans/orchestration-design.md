# ‏תוכנית: ‏מערכת אורקסטרציה ל-brief-driven-slices

> **‏תאריך**: 2026-05-29
> **‏סטטוס**: ‏טיוטה ‏מתוקנת (‏סבב 2) — ‏ממתין ל-Avigail ‏לאימות ‏חוזר
> **‏מטרה**: ‏הוספת שכבת אורקסטרציה ‏לסקיל `brief-driven-slices` ‏שמאפשרת ‏ביצוע ‏אוטומטי ‏של slices ‏מאומתים ‏ברצף, ‏ללא ‏מעורבות משתמשת, ‏עם הפרדת ‏תפקידים ‏ברורה ‏והגנה ‏על ‏פעולות merge.
>
> **‏שינויי ‏סבב 2** (‏אחרי ‏אימות ‏אביגיל ‏הראשון): ‏תיקון 2 ‏blockers (env vars + PATH ‏ב-tmux), ‏מעבר STATE ‏ל-YAML, ‏שרשור worktrees ‏כברירת ‏מחדל, ‏תלויות-חובה ‏ב-brief, 4 ‏מצבי ‏טיפול-כשל, ‏סקריפט discard-chain, ‏נעילה ‏נגד ‏שני ‏יתרו, ‏prompt ‏דרך stdin.
>
> **‏שינויי ‏סבב 3-4** (‏אחרי ‏אימות ‏אביגיל ‏השני ‏והשלישי): `yq` ‏ו-PyYAML ‏לא ‏זמינים → ‏מעבר ‏מ-YAML ‏ל-**JSON** (`state.json`), ‏סקריפטים ‏שמפרסרים state ‏נכתבים ‏ב-**python3 + json stdlib**. ‏מנגנון **`blocked.json`** ‏ל-BLOCKED ‏בלילה ‏(file-existence — `opencode run` ‏לא ‏מעביר exit code ‏של ‏הסוכן). ‏env scrub ‏ל-prefix ‏מלא. ‏כלל "merge commit ‏לא squash". ‏הגנת ‏מעגל + guard KeyError + ‏כתיבה ‏אטומית.

---

## §1 — ‏מטרה

‏היום, ‏ה-planner (build agent) ‏שמבצע תכניות נחסם ע"י sub-agents סינכרוניים, ‏ובמקרים ‏מסוימים ‏מבצע merge ‏ל-dev ‏ללא ‏אישור — ‏בעיה ‏שזוהתה ‏ב-voice-acp (5/7 ‏merges אחרונים ‏נעשו ‏ע"י build agent, ‏חלקם ‏בלי לשאול).

‏המטרה: **‏שכבת ‏אורקסטרציה** ‏שמאפשרת ‏לתת רשימת ‏briefs מאומתים ‏ולהריץ ‏אותם ‏ברצף ‏לאורך ‏לילה ‏שלם, ‏עם:

- ‏הפרדת ‏תפקידים ‏ברורה (‏מתכנן / ‏אורקסטרטור / ‏מבצע / ‏מאמתים)
- ‏איסור merge ‏על ‏כל הסוכנים ‏פרט ‏למתכנן
- ‏ביצוע ‏אסינכרוני ‏(executors ‏ב-tmux, ‏האורקסטרטור ‏לא ‏נחסם)
- ‏תמיכה ‏בריבוי ‏worktrees ‏וריבוי ‏פרויקטים
- ‏טיפול ‏בכשלים (stuck / crashed / failed)
- ‏ניקוי ‏עצמי ‏של ‏זבל ‏state

---

## §2 — ‏הצוות (5 ‏סוכנים)

| ‏שם | ‏תפקיד | ‏מצב OpenCode | ‏מודל | ‏רציונל |
|-----|-------|--------------|------|---------|
| **‏מרדכי** (Mordechai) | ‏מתכנן (planner) | `primary` | Opus | ‏תכנון אסטרטגי, ‏החלטות scope, ‏merge מאושר |
| **‏יתרו** (Yetro) | ‏אורקסטרטור (orchestrator) | `primary` | Sonnet | ‏לולאה מכנית: poll, dispatch, ‏עדכון STATE, ‏ניקוי |
| **‏אליעזר** (Eliezer) | ‏מבצע (executor) | `all` (primary+subagent) | Sonnet | ‏ביצוע brief, "ראש קטן", ‏נאמן לאדוניו |
| **‏אביגיל** (Avigail) | ‏מאמתת תוכניות (plan-verifier) | `subagent` | **Opus** | ‏reasoning ‏על מסמך מול codebase |
| **‏כלב** (Calev) | ‏מאמת ריצה (runtime-verifier) | `subagent` | Sonnet | ‏הפעלה בסביבה ‏אמיתית + ‏דיווח (mode: phase/light/heavy) |

### ‏רציונל ‏השמות

- **‏מרדכי** — ‏אסטרטג ‏מגילת אסתר. ‏תכנן רב-שלבי, ‏פעל דרך agents (‏אסתר), ‏הציל ‏עם שלם.
- **‏יתרו** — ‏המציא delegation (‏שמות יח): ‏ראה ‏שמשה ‏נחנק, ‏בנה ‏פירמידה ‏היררכית, ‏פתר scaling.
- **‏אליעזר** — ‏עבד אברהם (‏בראשית כד): ‏קיבל brief מפורט, ‏הטיל ‏unit test (‏מבחן רבקה), ‏חזר ‏ודיווח. ‏לא ‏הגדיל ‏ראש, ‏נאמן.
- **‏אביגיל** — ‏עצרה ‏את דוד ‏לפני ‏טעות ‏בלתי-הפיכה (1 ‏שמואל כה). ‏plan stage.
- **‏כלב** — ‏המרגל ‏שחזר ‏ואמר ‏את האמת ‏על ‏מה ‏שראה ‏בשטח. ‏runtime verification.

### ‏מצב ‏"both" ‏של אליעזר

‏אליעזר ‏צריך ‏לרוץ ‏בשני ‏אופנים:
- **‏subagent** — ‏כש-מרדכי ‏קורא ‏לו ‏ב-`Task` (Mode 1, ‏סינכרוני)
- **‏primary** — ‏כש-יתרו ‏מפעיל ‏`opencode run --agent eliezer` ‏ב-tmux (Mode 2, ‏אסינכרוני), ‏או ‏כשהמשתמשת ‏פותחת ‏סשן ‏ישיר (Mode 3)

‏ב-OpenCode ‏זה ‏מושג ‏עם `mode: all` ‏ב-frontmatter.

---

## §3 — ‏שלושת ‏אופני ‏ההפעלה

### Mode 1 — ‏Dispatch ‏ישיר ‏דרך ‏מרדכי (‏סינכרוני)

```
‏המשתמשת → ‏מרדכי: "‏בצע slice X"
‏מרדכי → Task(subagent_type="eliezer", ...)   [‏חוסם]
‏אליעזר ‏מבצע, ‏מפעיל ‏כלב (verifier), ‏מחזיר
‏מרדכי ‏מציג ‏למשתמשת → ‏המשתמשת ‏מאשרת → ‏מרדכי ‏עושה merge
```

- **‏מתי**: slice ‏בודד, ‏פיתוח ‏בזמן ‏אמת
- **State files**: ‏לא ‏בשימוש
- **Blocking**: ‏כן

### Mode 2 — ‏Orchestrated ‏דרך ‏יתרו (‏אסינכרוני, ‏לילי)

```
‏ערב:   ‏המשתמשת + ‏מרדכי ‏כותבים ‏briefs, ‏אביגיל ‏מאמתת, ‏מסמנים dispatch-ready ב-STATE
‏לילה:  ‏המשתמשת ‏פותחת ‏סשן ‏יתרו → "‏הרץ את ה-queue"
        ‏יתרו: ‏ניקוי → ‏מוצא slice ‏dispatch-ready → tmux dispatch ‏אליעזר → poll
              → ‏כלב verifier GO → ‏ארכוב brief → ‏slice ‏הבא
‏בוקר:  ‏המשתמשת ‏פותחת ‏סשן ‏מרדכי → ‏קורא summary → ‏עושה merges ‏מאושרים
```

- **‏מתי**: ‏עומס slices, ‏ביצוע ‏לילי
- **State files**: ‏בשימוש ‏מלא
- **Blocking**: ‏יתרו ‏לא ‏נחסם (executors ‏ב-tmux)

### Mode 3 — ‏Dispatch ‏ישיר ‏דרך ‏המשתמשת (‏ללא ‏planner)

```
‏המשתמשת → ‏סשן ‏אליעזר ‏ישיר: "‏בצע docs/plans/slice-X.md"
‏אליעזר ‏מבצע ‏ישירות (‏לפי §0 ‏ב-EXECUTOR_DISPATCH)
```

- **‏מתי**: ‏המשתמשת ‏יודעת ‏בדיוק ‏מה ‏היא ‏רוצה
- ‏לגיטימי, ‏אבל ‏לא ‏המסלול ‏הראשי. ‏אליעזר ‏עדיין ‏לא ‏ממזג.

---

## §4 — ‏הפרדת ‏הרשאות merge (‏ההכרעה ‏המרכזית)

| ‏תפקיד | merge | push | worktree remove | ‏branch -d |
|-------|-------|------|------------------|-----------|
| **‏מרדכי** | ✅ ‏אחרי ‏אישור ‏משתמשת | ✅ ‏אחרי ‏אישור | ✅ ‏אחרי merge ‏או ‏זריקה | ✅ ‏אחרי merge ‏או ‏זריקה |
| **‏יתרו** | ❌ ‏לעולם ‏לא | ❌ | ❌ ‏(‏ראה ‏הערה ‏למטה) | ❌ |
| **‏אליעזר** | ❌ ‏לעולם ‏לא | ❌ | ❌ | ❌ |
| **‏אביגיל** | ❌ | ❌ | ❌ | ❌ |
| **‏כלב** | ❌ | ❌ | ❌ | ❌ |

‏ההיגיון: merge ‏הוא ‏נקודת ‏לא-תחזור. ‏רק ‏מי ‏שרואה ‏את ‏ה-roadmap ‏המלא ‏(מרדכי + ‏המשתמשת) ‏מחליט ‏מתי. ‏יתרו ‏אוטומטי ‏לא ‏רואה ‏את ‏התמונה ‏השלמה.

**‏מי ‏מוחק worktree (‏תיקון N2 ‏מאביגיל)**: ‏יתרו ‏רץ ‏בלילה, ‏מרדכי ‏ממזג ‏בבוקר ‏בסשן ‏נפרד — ‏אז ‏יתרו ‏אף ‏פעם ‏לא ‏במצב ‏"אחרי merge ‏של ‏מרדכי". ‏לכן: **‏יתרו ‏לא ‏מוחק worktrees ‏בכלל ‏בזמן ‏ריצה**. ‏מחיקת worktrees ‏שנמרגו ‏קורית ‏ב-`cleanup_state.py` ‏שיתרו ‏מריץ ‏**‏בתחילת ‏סשן** (‏מזהה slice ‏שמסומן `merged` ‏ב-state.json ‏שעדיין ‏יש ‏לו worktree → ‏מוחק), ‏או ‏ע"י ‏מרדכי ‏בבוקר ‏אחרי merge. ‏זה ‏מסיר ‏את ‏ההרשאה ‏המבלבלת ‏מהטבלה ‏המקורית.

**‏בעיה ‏שזוהתה**: ‏ה-build agent ‏הרגיל ‏(לא ‏אחד ‏מ-5 ‏האלה) ‏יכול ‏לבצע ‏slice ‏ב-Mode 3 ‏ולחשוב ‏שמותר ‏לו ‏merge. ‏לכן:

> **‏שינוי ‏נדרש ‏ב-`~/.config/opencode/SOUL.md`** ‏(תחת "גבולות"):
> ‏"אסור ‏לבצע `git merge` ‏או `git push` ‏על קוד שמישהו ‏אחר ‏כתב ‏(slice של executor) ‏ללא ‏אישור ‏מפורש ‏של ‏המשתמשת — ‏גם ‏אם verifier ‏סימן GO."

‏זה ‏מכסה ‏גם ‏את ‏ה-build agent ‏הרגיל ‏וגם ‏את ‏יתרו/אליעזר (‏שירשו ‏את SOUL.md).

---

## §5 — ‏מבנה ‏הקבצים

### ‏בתוך ‏הסקיל (`~/projects/my-skills/brief-driven-slices/`)

```
brief-driven-slices/
├── SKILL.md                      # ‏מעודכן — ‏מפת ‏הצוות ‏+ ‏modes
├── workflow.md                   # ‏קיים — ‏מעודכן ‏עם ‏orchestration
├── worktrees.md                  # ‏קיים
├── orchestration.md              # ‏NEW — ‏הסבר ‏על ‏יתרו, ‏ה-state machine, ‏ה-loop
├── patterns.md                   # ‏קיים
├── recommendations.md            # ‏קיים
├── agents/
│   ├── mordechai.md              # NEW — planner (primary, Opus)
│   ├── yetro.md                  # NEW — orchestrator (primary, Sonnet)
│   ├── eliezer.md                # NEW — executor (all, Sonnet) ← ‏מ-executor.md ‏הישן
│   ├── avigail.md                # NEW — plan-verifier (subagent, Opus) ← ‏מ-plan-verifier.md
│   └── calev.md                  # NEW — runtime-verifier (subagent, Sonnet) ← ‏איחוד 3 ‏הקודמים
├── briefs/
│   ├── BRIEF_TEMPLATE.md         # ‏קיים
│   ├── EXECUTOR_DISPATCH.md      # ‏קיים — ‏מעודכן ‏עם ‏שמות ‏חדשים
│   └── state.template.json       # NEW — ‏template ‏ל-state.json ‏פר-פרויקט
├── scripts/
│   ├── install-agents.sh         # NEW (bash) — ‏symlinks ‏ל-~/.config/opencode/agents/
│   ├── wait-for-slice.sh         # NEW (bash) — ‏blocking ‏מבוקר
│   ├── dispatch-executor.sh      # NEW (bash) — ‏tmux ‏עם env scrub + sentinel + heartbeat
│   ├── cleanup_state.py          # NEW (python3) — ‏ניקוי ‏זבל ‏(יתרו ‏קורא לו)
│   └── discard_chain.py          # NEW (python3) — ‏זריקת ‏שרשרת ‏בטוחה ‏(מרדכי ‏קורא לו)
├── orchestration-project/        # NEW — ‏template ‏לפרויקט ‏הבית ‏של ‏יתרו
│   ├── README.md
│   ├── projects.json.example
│   ├── AGENTS.md
│   └── policies/
│       └── example-project.json
├── docs/
│   └── plans/
│       ├── orchestration-design.md   # ‏המסמך ‏הזה
│       └── archive/
└── case-studies/                 # ‏קיים
```

### ‏State ‏פר-פרויקט (‏מחוץ ‏לריפו, ‏לא ‏tracked)

```
~/.local/state/brief-driven-slices/<project>/
├── state.json                    # ‏ה-state machine ‏(machine-readable, JSON)
├── yetro.lock                    # flock ‏נגד ‏שני ‏יתרו במקביל
├── dispatches/<slice>.prompt     # ‏ה-prompt ‏שנשלח ‏ל-executor
├── logs/<slice>.log              # ‏stdout/stderr ‏של ‏ה-executor
├── sentinels/<slice>.done        # ‏exit code ‏של opencode (0 ‏בד"כ; 124/125 ‏מ-wait)
├── blocked/<slice>.blocked.json  # ‏אם ‏אליעזר ‏עצר ‏ב-BLOCKED (‏יתרו ‏בודק ‏קיום)
├── heartbeats/<slice>.last       # ‏timestamp ‏מתעדכן ‏פר commit
├── crashes/<slice>-<ts>.log      # ‏log ‏של slices ‏שקרסו (‏שמור ל-debug)
└── archived/                     # sentinels/logs ‏של slices ‏שכבר merged (‏ניקוי)
```

### ‏פרויקט ‏הבית ‏של ‏יתרו ‏(נוצר ‏מ-template ‏בנפרד)

```
~/projects/orchestration/
├── README.md
├── projects.json                 # ‏רשימת ‏פרויקטים ‏פעילים
├── AGENTS.md                     # ‏הוראות ‏ל-יתרו
├── runs/<date>.summary.md        # ‏סיכום ‏ריצה ‏ללילה (‏מרדכי ‏קורא ‏בבוקר)
├── runs/<date>.log               # ‏לוג ‏מלא
└── policies/<project>.json        # ‏מדיניות ‏פר ‏פרויקט (JSON — ‏אין PyYAML)
```

---

## §6 — STATE schema (JSON)

‏מיקום: `~/.local/state/brief-driven-slices/<project>/state.json`

**‏החלטה (‏תיקון M4 + ‏סבב 3)**: ‏מבנה ‏JSON, ‏לא ‏Markdown table ‏ולא YAML. ‏הסיבה: ‏אימות ‏אביגיל ‏השני ‏גילה ‏ש-`yq` ‏וגם ‏PyYAML ‏**‏לא ‏זמינים** ‏בסביבה (`~/.config/opencode/AGENTS.md` ‏מציין yq ‏כ-NOT available; `python3 -c "import yaml"` ‏נכשל). ‏JSON ‏נפרס ‏ע"י `python3 -c "import json"` ‏(stdlib, ‏תמיד ‏זמין), ‏גם ‏ע"י ‏סקריפטים ‏וגם ‏ע"י ‏הסוכנים. ‏מנטרל ‏את ‏שלושת ‏באגי-הפרסור ‏(grep ‏שביר, substring collision, ‏פרסור ‏טבלה ‏ידני).

‏לקריאוּת-אדם: ‏מרדכי ‏יכול ‏לייצר view ‏ב-Markdown ‏מה-JSON ‏מתי ‏שצריך (‏הוא ‏LLM, ‏קורא JSON ‏בקלות; ‏העריכה ‏ממילא ‏שלו).

```json
{
  "project": "voice-acp",
  "repo_root": "/home/user/projects/voice-acp",
  "base_branch": "dev",
  "dev_tip": "e9a857f",
  "updated": "2026-05-29T22:34:04Z",
  "slices": [
    {
      "id": "17",
      "name": "Wake word",
      "status": "brief-ready",
      "brief": "docs/plans/slice-17-wake-word.md",
      "plan_verified": false,
      "depends_on": [],
      "dispatch_ready": false,
      "base": "dev",
      "branch": null,
      "worktree": null
    },
    {
      "id": "20",
      "name": "Local prod",
      "status": "brief-ready",
      "brief": "docs/plans/slice-20-local-prod-service.md",
      "plan_verified": true,
      "depends_on": [],
      "dispatch_ready": true,
      "base": "dev",
      "branch": null,
      "worktree": null
    },
    {
      "id": "15d",
      "name": "CF Pages",
      "status": "brief-ready",
      "brief": "docs/plans/slice-15d-cf-deployment.md",
      "plan_verified": true,
      "depends_on": ["15a", "15b", "15c"],
      "dispatch_ready": true,
      "base": "dev",
      "branch": null,
      "worktree": null
    },
    {
      "id": "B",
      "name": "Feature B (‏דוגמת ‏שרשור — ‏תלוי ב-A ‏שלא merged)",
      "status": "brief-ready",
      "plan_verified": true,
      "depends_on": ["A"],
      "dispatch_ready": true,
      "base": "slice-A",
      "branch": null,
      "worktree": null
    }
  ]
}
```

`depends_on` ‏חובה ‏בכל slice (‏רשימה, ‏יכולה ‏ריקה). ‏אביגיל ‏מאמתת ‏שהוא ‏ממולא ‏ועקבי ‏עם ‏ה-brief.
`base`: ‏אם ‏כל ‏התלויות merged → `"dev"`. ‏אם ‏יש ‏תלות verified ‏(לא merged) → ‏ה-branch ‏של ‏אותה ‏תלות (‏שרשור).

### ‏שדה `depends_on` — ‏תלויות-חובה (‏שינוי #1)

‏כל slice ‏חייב `depends_on` ‏מפורש (‏רשימה, ‏יכולה ‏להיות ‏ריקה). ‏אביגיל ‏(מאמתת ‏התוכניות) ‏מאמתת ‏ש:
- ‏ה-brief ‏מתעד ‏על ‏מה ‏הוא ‏בנוי (§0 ‏בתבנית ‏ה-brief)
- ‏זה ‏עקבי ‏עם `depends_on` ‏ב-state.json
- ‏אם ‏brief ‏לא ‏מצהיר ‏תלויות → ‏אביגיל ‏מחזירה ‏אותו ‏(🔴 blocker)

### ‏שדה `base` — ‏שרשור ‏כברירת ‏מחדל (‏שינוי #2)

‏זה ‏הלב ‏של ‏השרשור. ‏יתרו ‏קובע ‏את `base` ‏לפי ‏מצב ‏התלויות:

- ‏אם ‏כל ‏ה-`depends_on` ‏במצב `merged` → `base: dev` (‏הכל ‏כבר ‏ב-dev)
- ‏אם ‏יש ‏תלות ‏שלא ‏merged ‏(במצב `verified`) → `base: <branch של ‏התלות>` (‏שרשור!)
- ‏worktree ‏נוצר: `git worktree add .worktrees/<slice> -b <slice> <base>`

‏ככה slice ‏תלוי ‏נבנה ‏על ‏הקוד ‏של ‏התלות ‏שלו, ‏גם ‏אם ‏היא ‏עוד ‏לא ‏ב-dev. ‏זה ‏פותר ‏את N1 ‏מאביגיל ‏(הבסיס ‏לא ‏חסר ‏יותר). dev ‏לא ‏נוגעים ‏בו ‏כל ‏הלילה (‏שינוי #3).

### ‏ערכי status

| status | ‏משמעות | ‏מי מסמן |
|--------|---------|---------|
| `planned` | ‏רעיון, ‏אין brief | ‏מרדכי |
| `brief-ready` | ‏brief נכתב | ‏מרדכי |
| `plan-verified` | ‏אביגיל ‏אישרה (`plan_verified=true`) | ‏מרדכי ‏(אחרי ‏אביגיל) |
| `in-progress` | ‏יתרו dispatched ‏אליעזר | ‏יתרו |
| `verified` | ‏כלב ‏אישר ‏(GO) | ‏יתרו |
| `merged` | ‏מרדכי ‏מיזג ‏ל-dev | ‏מרדכי |
| `needs-revision` | ‏אביגיל ‏או ‏כלב ‏סירבו | ‏יתרו/מרדכי |
| `blocked` | ‏אליעזר ‏עצר (BLOCKED) | ‏יתרו |
| `blocked-by:<id>` | ‏תלות ‏שלו ‏נכשלה ‏בשרשרת | ‏יתרו |
| `timed-out` | ‏אין heartbeat > 2h | ‏יתרו |
| `crashed` | tmux ‏מת ‏ללא sentinel | ‏יתרו |
| `failed:<cat>` | ‏exit code ≠ 0 | ‏יתרו |
| `discarded` | ‏מרדכי ‏זרק ‏ידנית (`discard_chain.py`) | ‏מרדכי |

### ‏מי מעדכן

- **‏מרדכי** (‏ידני): `planned` → `brief-ready` → `plan-verified` (+ `dispatch_ready=true`), ‏וגם → `merged` / `discarded`
- **‏יתרו** (‏אוטומטי): `plan-verified` → `in-progress` → `verified` / `needs-revision` / `blocked` / `blocked-by` / `timed-out` / `crashed` / `failed`
- ‏סנכרון ‏עם git: ‏בכל ‏טעינה ‏יתרו ‏בודק `git rev-parse <base_branch>` ‏מול `dev_tip`. ‏drift → ‏עוצר ‏ושואל ‏מרדכי.

### ‏נעילה ‏נגד ‏שני ‏יתרו ‏(תיקון N7 ‏מאביגיל)

‏בתחילת ‏הלולאה, ‏יתרו ‏לוקח flock ‏על `~/.local/state/brief-driven-slices/<project>/yetro.lock`. ‏אם ‏נעול ‏כבר → ‏עוצר ‏עם ‏הודעה ‏"יתרו ‏אחר ‏כבר ‏רץ ‏על ‏הפרויקט ‏הזה". ‏משחרר ‏בסוף ‏הסשן ‏(או ‏אם ‏התהליך ‏מת — flock ‏משתחרר ‏אוטומטית).

---

## §7 — ‏לולאת ‏יתרו (‏ה-orchestrator loop)

```
‏יתרו ‏מתחיל (‏המשתמשת ‏פתחה ‏סשן ‏עם agent=yetro, ‏cwd=~/projects/orchestration/)
   │
   ▼ ‏[‏נעילה]
   flock על yetro.lock פר-פרויקט. ‏אם נעול → ‏עצור (‏יתרו אחר רץ)
   │
   ▼ ‏[‏ניקוי ‏תחילי]
   ‏קרא projects.json → ‏לכל ‏פרויקט ‏פעיל: ‏הרץ cleanup_state.py
   │     (‏מנקה logs/heartbeats ‏ישנים, orphan tmux, worktrees ‏שמסומנים merged)
   │
   ▼ ‏[‏לכל ‏פרויקט ‏ב-queue, ‏סדרתית]
   ‏קרא state.json
   ‏בדוק git rev-parse <base_branch> == dev_tip ? ‏אם ‏לא → ‏עצור ‏ושאל ‏מרדכי
   │
   ▼ ‏[‏מצא ‏slice ‏הבא]
   ‏slice ‏ש: status==plan-verified, dispatch_ready==true,
            ‏וכל ‏depends_on ‏שלו status ∈ {merged, verified}
            (verified = ‏שרשור: ה-base ‏יהיה ‏ה-branch ‏של ‏התלות, ‏לא dev)
            (‏אם ‏תלות ‏במצב failed/blocked → ‏סמן ‏את ‏ה-slice blocked-by:<id>, ‏דלג)
   ‏אם ‏אין → ‏לוג "queue empty for <project>", ‏עבור ‏לפרויקט ‏הבא
   │
   ▼ ‏[‏קבע base — ‏שרשור]
   ‏אם ‏כל depends_on במצב merged → base = dev
   ‏אם ‏יש ‏תלות verified (‏לא merged) → base = branch ‏של ‏אותה ‏תלות
   ‏עדכן state.json: base = <base>
   │
   ▼ ‏[‏dispatch]
   git worktree add .worktrees/<slice> -b <slice> <base>
   ‏כתוב dispatch prompt → dispatches/<slice>.prompt
   ‏סמן state.json: status=in-progress, branch=<slice>, worktree=<path>, started=<ts>
   ‏הרץ: dispatch-executor.sh <project> <slice> <worktree>   [tmux + env scrub + sentinel]
   │
   ▼ ‏[‏המתנה]
   ‏הרץ: wait-for-slice.sh <project> <slice> 120
   │
   ▼ ‏[‏טיפול ‏בתוצאה — ‏סדר ‏בדיקה ‏חשוב]
   ‏(1) ‏קיים blocked/<slice>.blocked.json?  ← ‏הבדיקה ‏הראשונה, ‏לא ‏exit code
   │       ‏כן → ‏קרא ‏אותו → status=blocked → ‏עצור ‏ענף (‏לא ‏מריץ ‏כלב!)
   ‏(2) ‏exit 124 (timeout) → status=timed-out → ‏עצור ‏ענף
   ‏(3) ‏exit 125 (crash)   → status=crashed → ‏שמור crash log → ‏עצור ‏ענף
   ‏(4) ‏exit ≠0 ‏אחר        → ‏קריסת-תשתית ‏של opencode → status=failed:infra → ‏עצור ‏ענף
   ‏(5) ‏exit 0 ‏ואין blocked.json → ‏הרץ ‏כלב:
   │       ‏כלב GO → status=verified → ‏ארכב brief (‏ב-branch) → ‏slice ‏הבא
   │       ‏כלב NO → status=needs-revision → ‏עצור ‏ענף (worktree ‏נשאר ‏לתיקון)
   │     ‏("עצור ‏ענף" = ‏סמן ‏כל ‏מה ‏שתלוי ‏ב-slice ‏הזה ‏כ-blocked-by, ‏אבל ‏המשך
   │      ‏לשרשראות/slices ‏אחרים ‏שלא ‏תלויים. dev ‏לא ‏נגעו ‏בו → ‏הכל ‏ניתן ‏לזריקה ‏בבוקר)
   │
   │  ‏הערה ‏(תיקון #9/#10): `opencode run` ‏כמעט ‏תמיד ‏מחזיר exit 0 — ‏גם ‏אם ‏אליעזר
   │  ‏נכשל ‏לוגית (typecheck ‏נשבר). ‏לכן ‏סיווג ‏כשל ‏לוגי ‏קורה ‏דרך **‏כלב** (NO-GO),
   │  ‏לא ‏דרך exit code. exit≠0 ‏שמור ‏רק ‏לקריסות-תשתית ‏של opencode ‏עצמו.
   │
   ▼ ‏[‏סוף]
   ‏כתוב runs/<date>.summary.md: ‏מה ‏עבר, ‏מה ‏blocked (+ ‏סיבה ‏מ-blocked.json), ‏מה ‏נכשל, ‏מה ‏ממתין ‏ל-merge
   ‏שחרר flock
```

### ‏הערה ‏על ‏מקביליות

‏כרגע ‏יתרו **‏סדרתי** — slice ‏אחד ‏בכל ‏פעם. ‏מקביליות (‏כמה executors ‏ב-tmux ‏בו-זמנית) ‏אפשרית ‏טכנית ‏(sentinels ‏נפרדים), ‏אבל **‏נדחית ‏בכוונה**:
- ‏בלילה ‏אין ‏לחץ ‏זמן → ‏מקביליות ‏רק ‏מסכנת (‏שני executors ‏על ‏אותו ‏BE port, ‏conflicts ‏ב-shared files)
- ‏סדרתי = ‏פשוט ‏יותר ‏ל-debug ‏בבוקר
- ‏אם ‏בעתיד ‏יידרש: ‏ה-infra (tmux + sentinels) ‏כבר ‏תומך, ‏רק ‏צריך ‏לולאה ‏שמחזיקה N ‏active

---

## §8 — ‏Scripts

### `dispatch-executor.sh`

```bash
#!/usr/bin/env bash
# dispatch-executor.sh <project> <slice> <worktree> [agent]
# ‏ה-worktree ‏מועבר ‏כ-arg (‏יתרו ‏יודע ‏אותו ‏מ-state.json — ‏לא ‏מפרסר ‏עם grep ‏שביר)
set -euo pipefail
PROJECT="$1"; SLICE="$2"; WORKTREE="$3"; AGENT="${4:-eliezer}"
STATE="$HOME/.local/state/brief-driven-slices/$PROJECT"
mkdir -p "$STATE"/{dispatches,logs,sentinels,heartbeats,crashes,archived,blocked}

PROMPT="$STATE/dispatches/$SLICE.prompt"
LOG="$STATE/logs/$SLICE.log"
SENTINEL="$STATE/sentinels/$SLICE.done"

# ‏נתיב ‏מלא ל-opencode (‏תיקון B2 — PATH ‏לא ‏מובטח ‏ב-tmux non-interactive)
OPENCODE_BIN="$HOME/.opencode/bin/opencode"

# ‏env scrub ‏מלא ‏(תיקון B1 + N-new-1): ‏מנקה ‏את ‏**‏כל** ‏OPENCODE_* ‏ב-prefix,
# ‏לא whitelist ‏של ‏שמות ‏מפורשים (‏שדולף ‏על vars ‏עתידיים כמו OPENCODE_GEMINI_PROJECT_ID).
SCRUB=$(env | grep -o '^OPENCODE_[^=]*' | sed 's/^/-u /' | tr '\n' ' ')

# ‏ה-prompt ‏מועבר ‏דרך stdin (‏תיקון N6). BDS_* ‏ל-heartbeat + blocked.json (‏תיקון M2/#E).
# BDS_STATE_DIR ‏מוזרק ‏מפורשות ‏כדי ‏שאליעזר ‏לא ‏יבנה path ‏ידנית (‏מקור ‏לבאגים).
tmux new-session -d -s "bds-$PROJECT-$SLICE" \
  "cd '$WORKTREE' && \
   env $SCRUB BDS_PROJECT='$PROJECT' BDS_SLICE='$SLICE' BDS_STATE_DIR='$STATE' \
       '$OPENCODE_BIN' run --agent '$AGENT' < '$PROMPT' > '$LOG' 2>&1; \
   echo \"\$?\" > '$SENTINEL'"

echo "dispatched: bds-$PROJECT-$SLICE (tmux)"
```

> [!warning] ‏תיקון #E — ‏הרשאת ‏כתיבה ‏חוץ-workspace
> ‏אליעזר ‏כותב `blocked.json` ‏ו-heartbeat ‏ל-`$BDS_STATE_DIR` (‏מחוץ ‏ל-worktree). ‏ב-OpenCode ‏כלי ‏הכתיבה ‏לרוב ‏מוגבל ‏ל-cwd. ‏לכן: ‏(א) eliezer.md ‏צריך `permission: { external_directory: allow }`, ‏(ב) ‏אליעזר ‏כותב ‏עם `$BDS_STATE_DIR/blocked/$BDS_SLICE.blocked.json` ‏(לא ‏בונה ‏path ‏ידנית). ‏לאמת ‏ב-Commit 1.

> [!warning] ‏תלוי ‏באימות ‏אמפירי (‏שאלות §13)
> ‏לפני ‏הרצה ‏אמיתית: ‏לוודא ‏ש-(א) `opencode run --agent X < file` ‏קורא ‏stdin ‏(אביגיל ‏אימתה ‏`run.ts:342` — ‏כן), ‏(ב) ‏שרשימת ‏ה-`OPENCODE_*` ‏לניקוי ‏מלאה, ‏(ג) ‏שהנתיב `$HOME/.opencode/bin/opencode` ‏נכון.

### `wait-for-slice.sh`

```bash
#!/usr/bin/env bash
# wait-for-slice.sh <project> <slice> [timeout-min]
# ‏מחזיר exit code ‏של ‏ה-executor; 124 ‏על timeout.
set -euo pipefail
PROJECT="$1"; SLICE="$2"; TIMEOUT_MIN="${3:-120}"
STATE="$HOME/.local/state/brief-driven-slices/$PROJECT"
SENTINEL="$STATE/sentinels/$SLICE.done"
HEARTBEAT="$STATE/heartbeats/$SLICE.last"
TMUX_SESSION="bds-$PROJECT-$SLICE"

elapsed=0; poll=30
while [[ ! -f "$SENTINEL" ]]; do
  # ‏crash detection: tmux ‏מת ‏ללא sentinel
  if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "CRASHED: tmux session gone, no sentinel" >&2
    exit 125
  fi
  sleep $poll; elapsed=$((elapsed+poll))
  # heartbeat staleness
  if [[ -f "$HEARTBEAT" ]]; then
    age=$(( $(date +%s) - $(date -r "$HEARTBEAT" +%s) ))
    (( age > 1800 )) && echo "warn: heartbeat stale ${age}s" >&2
  fi
  # timeout
  if (( elapsed > TIMEOUT_MIN*60 )); then
    tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
    echo "TIMEOUT after ${TIMEOUT_MIN}min" >&2
    exit 124
  fi
done
cat "$SENTINEL"   # exit code ‏של ‏ה-executor
```

### `cleanup_state.py` (python3 — ‏תיקון N3 ‏ובעיית yq)

```python
#!/usr/bin/env python3
# cleanup_state.py <project>
# ‏יתרו ‏קורא ‏לזה ‏בתחילת ‏כל ‏סשן. ‏python3 stdlib ‏בלבד (‏אין yq/PyYAML).
import json, os, sys, time, subprocess
from pathlib import Path

# ‏הקשחה ‏(תיקון #3): ‏עטיפת subprocess ‏מפני FileNotFoundError (tmux/git ‏לא ‏ב-PATH)
def run(cmd, **kw):
    try: return subprocess.run(cmd, **kw)
    except FileNotFoundError: return None

project = sys.argv[1]
state_dir = Path.home() / ".local/state/brief-driven-slices" / project
state = json.loads((state_dir / "state.json").read_text())
slices = {s["id"]: s for s in state["slices"]}

now = time.time()
def older_than(p, days):
    return p.is_file() and (now - p.stat().st_mtime) > days * 86400

# 1. logs/archived > 30 ‏יום → ‏מחק
for sub in ("logs", "archived"):
    for f in (state_dir / sub).glob("*"):
        if older_than(f, 30): f.unlink()

# 2. heartbeats ‏לא-פעילים > 7 ‏ימים → ‏מחק
for f in (state_dir / "heartbeats").glob("*"):
    if older_than(f, 7): f.unlink()

# 3. orphan tmux: bds-<project>-<id> ‏ש-id ‏שלו ‏לא in-progress → kill
#    (‏עיגון ‏מדויק ‏לפי id ‏מלא — ‏לא substring. ‏פותר N3.)
res = run(["tmux", "ls"], capture_output=True, text=True)
out = res.stdout if res else ""
for line in out.splitlines():
    name = line.split(":")[0]
    prefix = f"bds-{project}-"
    if not name.startswith(prefix): continue
    sid = name[len(prefix):]                    # ‏id ‏מדויק
    s = slices.get(sid)
    if s is None or s["status"] != "in-progress":
        run(["tmux", "kill-session", "-t", name])

# 4. worktrees ‏של slices ‏שמסומנים merged ‏ב-state ‏אבל ‏עוד ‏קיימים → ‏מחק (‏תיקון N2)
for s in state["slices"]:
    if s["status"] == "merged" and s.get("worktree"):
        wt = Path(s["worktree"])
        if wt.exists():
            run(["git", "-C", state["repo_root"],
                 "worktree", "remove", "--force", str(wt)])
            if s.get("branch"):
                run(["git", "-C", state["repo_root"],
                     "branch", "-D", s["branch"]])
```

### `install-agents.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
SRC="$HOME/projects/my-skills/brief-driven-slices/agents"
DST="$HOME/.config/opencode/agents"
mkdir -p "$DST"
for agent in mordechai yetro eliezer avigail calev; do
  ln -sfn "$SRC/$agent.md" "$DST/$agent.md"
  echo "linked: $agent"
done
# ‏שים ‏לב: ‏הסקריפטים ‏שמפרסרים state ‏הם python3 (cleanup_state.py, discard_chain.py),
# ‏השאר ‏bash (install/wait/dispatch). ‏ה-`.py` ‏רצים ‏עם python3 ‏ישירות.
# ‏ניקוי symlinks ‏ישנים ‏(executor, plan-verifier, verifier-*)
for old in executor plan-verifier verifier-phase verifier-slice-light verifier-slice-heavy; do
  [[ -L "$DST/$old.md" ]] && rm "$DST/$old.md" && echo "removed old: $old"
done
```

### `discard_chain.py` (python3 — ‏זריקת ‏שרשרת ‏בטוחה)

```python
#!/usr/bin/env python3
# discard_chain.py <project> <from-slice>
# ‏זורק slice ‏ואת ‏כל ‏מה ‏ש**‏תלוי ‏בו** ‏(dependents, ‏כלפי ‏מעלה). ‏מרדכי ‏מריץ ‏ידנית.
# ‏בטיחות: ‏מסרב ‏לזרוק slice ‏שכבר merged. ‏הגנת ‏מעגל ‏ב-visited set.
import json, sys, subprocess
from pathlib import Path

# ‏הקשחה ‏(תיקון #D): ‏עטיפת subprocess ‏מפני FileNotFoundError (tmux/git ‏לא ‏ב-PATH)
def run(cmd, **kw):
    try: return subprocess.run(cmd, **kw)
    except FileNotFoundError: return None

project, frm = sys.argv[1], sys.argv[2]
state_dir = Path.home() / ".local/state/brief-driven-slices" / project
state_path = state_dir / "state.json"
state = json.loads(state_path.read_text())
by_id = {s["id"]: s for s in state["slices"]}

if frm not in by_id:                    # ‏תיקון #7 — guard ‏ל-slice ‏לא-קיים
    sys.exit(f"unknown slice: {frm}")

# 1. compute dependents (‏מי ‏תלוי ב-frm, ‏טרנזיטיבית) — BFS ‏עם visited (‏הגנת ‏מעגל)
chain, queue, visited = set(), [frm], set()
while queue:
    cur = queue.pop(0)
    if cur in visited: continue        # ‏הגנת ‏מעגל
    visited.add(cur); chain.add(cur)
    for s in state["slices"]:
        if cur in s.get("depends_on", []) and s["id"] not in visited:
            queue.append(s["id"])
# frm ‏עצמו ‏כלול; ‏מה ‏שמתחתיו (dependencies) ‏לא — ‏רק dependents.

# 2. ‏בטיחות: ‏אף ‏אחד ‏לא merged
for sid in chain:
    if by_id[sid]["status"] == "merged":
        sys.exit(f"REFUSE: slice {sid} already merged — chain not safely discardable")

# 3. ‏לכל slice: ‏עצור tmux, ‏מחק worktree+branch, ‏סמן discarded, ‏נקה ‏קבצים
repo = state["repo_root"]
for sid in chain:
    s = by_id[sid]
    run(["tmux", "kill-session", "-t", f"bds-{project}-{sid}"], stderr=subprocess.DEVNULL)
    if s.get("worktree"):
        run(["git", "-C", repo, "worktree", "remove", "--force", s["worktree"]],
            stderr=subprocess.DEVNULL)
    if s.get("branch"):
        run(["git", "-C", repo, "branch", "-D", s["branch"]], stderr=subprocess.DEVNULL)
    s["status"] = "discarded"           # ‏שומר ‏רשומה, ‏לא ‏מוחק
    for sub in ("dispatches", "logs", "sentinels", "heartbeats", "blocked"):
        for f in (state_dir / sub).glob(f"{sid}.*"):
            f.unlink()
    print(f"discarded: {sid}")

# ‏כתיבה ‏אטומית ‏(תיקון #8): temp + rename ‏כדי ‏שלא ‏יישאר state.json ‏חצי-כתוב
tmp = state_path.with_suffix(".json.tmp")
tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
tmp.replace(state_path)
```

‏אותו ‏דפוס temp+rename ‏לכל ‏כתיבת state.json (‏גם ‏ב-cleanup_state.py ‏וגם ‏ביתרו ‏עצמו).

‏מה ‏שהצליח ‏**‏לפני** ‏ה-slice ‏שנכשל ‏(A ‏בשרשרת A→B→C ‏שבה B ‏נכשל) ‏**‏לא ‏נזרק** — ‏הוא ‏ה-dependency ‏של B, ‏לא ‏dependent ‏שלו, ‏אז ‏לא ‏ב-closure. ‏A ‏נשאר ‏ל-merge.

### ‏Heartbeat ‏מצד ‏אליעזר

‏אליעזר ‏(ב-eliezer.md) ‏כותב ‏heartbeat ‏אחרי ‏כל commit. ‏ה-`BDS_PROJECT`/`BDS_SLICE` ‏מוזרקים ‏ל-env ‏שלו ‏ע"י `dispatch-executor.sh` (‏תיקון M2):

```bash
date +%s > "$BDS_STATE_DIR/heartbeats/$BDS_SLICE.last"
```

‏זה ‏מתועד ‏ב-eliezer.md ‏כצעד ‏ב-workflow ‏פר-commit. ‏ב-Mode 1 ‏(Task ‏סינכרוני, ‏ללא tmux) ‏ה-env ‏לא ‏מוגדר → ‏אליעזר ‏מדלג ‏על ‏heartbeat ‏וגם ‏על blocked.json ‏(בודק ‏`[[ -n "${BDS_SLICE:-}" ]]`; ‏ב-Mode 1 ‏הוא ‏מחזיר BLOCKED ‏ל-Task ‏רגיל).

---

## §9 — ‏טיפול ‏בכשלים

### ‏זיהוי ‏ע"י ‏יתרו ‏בלילה

| ‏מצב | ‏זיהוי | ‏פעולת ‏יתרו |
|------|--------|-------------|
| **blocked** | ‏קיים `blocked/<slice>.blocked.json` | ‏קרא ‏סיבה, status=blocked, ‏לא ‏מריץ ‏כלב, ‏עצור ‏ענף |
| **stuck** | heartbeat > 30min (warn), > 2h (act) | kill tmux, status=timed-out, ‏עצור ‏ענף |
| **crashed** | `tmux has-session` fail + ‏אין sentinel | ‏שמור crash log, status=crashed, ‏עצור ‏ענף |
| **failed:infra** | sentinel ‏עם exit ≠ 0 (‏רק ‏קריסת-תשתית ‏של opencode) | status=failed:infra, ‏עצור ‏ענף |
| **rejected** | sentinel exit 0, ‏אין blocked.json, + ‏כלב NO-GO | status=needs-revision, ‏עצור ‏ענף (worktree ‏נשאר) |

‏**הערה (‏תיקון #C)**: ‏כשל ‏לוגי (typecheck/lint ‏נשבר) ‏**‏לא ‏מסווג ‏דרך exit code** — `opencode run` ‏מחזיר 0 ‏גם ‏אז. ‏הוא ‏נתפס ‏ע"י ‏כלב ‏(NO-GO → needs-revision). exit≠0 ‏שמור ‏אך ‏ורק ‏לקריסות-תשתית ‏של opencode ‏עצמו (`failed:infra`).

"‏עצור ‏ענף" = ‏סמן ‏כל ‏מה ‏שתלוי ‏בו ‏כ-`blocked-by:<id>`, ‏אבל ‏המשך ‏לשרשראות ‏אחרים. ‏יתרו **‏לא ‏מנסה ‏לתקן, ‏לא ‏מ-dispatched ‏שוב, ‏לא ‏מוחק worktrees**. ‏הכל ‏מתועד ‏ב-summary.

**‏עיקרון**: ‏יתרו ‏יציב > ‏אגרסיבי. ‏הוא ‏לא ‏מקבל ‏החלטות ‏תיקון — ‏זה ‏מרדכי.

### ‏ארבעה ‏מצבי ‏הכרעה ‏ע"י ‏מרדכי ‏בבוקר (‏שינוי #4)

‏כשמרדכי ‏פותח ‏סשן ‏בבוקר ‏וקורא ‏את ‏ה-summary, ‏לכל ‏ענף ‏שנכשל ‏יש ‏ארבע ‏אפשרויות:

| ‏מצב | ‏מתי | ‏פעולה |
|------|------|--------|
| **‏מזג-מה-שעבד** | A ‏עבר, B ‏ומעלה ‏נכשלו | ‏מזג A ‏ל-dev, ‏הרץ `discard_chain.py <project> B` ‏(זורק B→C→D), ‏תקן ‏brief ‏של B ‏ללילה ‏הבא |
| **‏תקן-במקום** | slice ‏90% ‏טוב, ‏צריך ‏תיקון ‏קטן | ‏היכנס ‏ל-worktree ‏הקיים, ‏תקן ‏ידנית ‏או ‏עם ‏מבצע ‏בסבב ‏fix, ‏הרץ ‏שוב ‏את ‏כלב, ‏אם ‏עובר → ‏מזג. ‏ה-worktree ‏נשאר ‏חי. |
| **‏זרוק-הכל** | ‏כל ‏השרשרת ‏עקומה | `discard_chain.py <project> A` ‏(זורק ‏את ‏כל ‏השרשרת). dev ‏לא ‏נגעו ‏בו → ‏אין ‏מה ‏לתקן. ‏מתחילים ‏מחדש. |
| **‏מזג-הכל** | ‏הכל ‏עבר | ‏מזג ‏את ‏השרשרת ‏בסדר A→B→C ‏ל-dev, ‏אחד-אחד, ‏עם ‏בדיקה. |

‏המפתח: ‏**‏dev ‏לא ‏נוגעים ‏בו ‏כל ‏הלילה**, ‏אז ‏כל ‏זריקה ‏בטוחה ‏(אין ‏מה ‏"לבטל" ‏ב-dev). ‏ומה ‏שהצליח ‏לפני ‏הכשל ‏נשמר ‏(לא ‏ב-closure ‏של ‏הזריקה).

### §9.1 — ‏מנגנון BLOCKED (‏אליעזר ‏נתקע ‏בכוונה ‏בלילה)

‏אליעזר ‏מקבל ‏הוראה ‏מפורשת ‏"ראש ‏קטן" — ‏אם ‏הוא ‏נתקע ‏בבעיה ‏שדורשת ‏יותר ‏ממיומנות ‏מכנית, ‏הוא ‏**‏עוצר ‏ולא ‏מנסה ‏לתקן**. ‏ב-Mode 1 ‏(סינכרוני) ‏הוא ‏מחזיר STATUS: BLOCKED ‏ב-Task, ‏ומרדכי ‏מטפל ‏מיד.

‏אבל ‏ב-Mode 2 ‏(לילי, ‏ב-tmux) ‏אין ‏עם ‏מי ‏לדבר.

> [!warning] ‏למה ‏**‏לא** exit code (‏תיקון #9 ‏מאביגיל)
> ‏בתכנון ‏מוקדם ‏חשבנו ‏שאליעזר ‏"יוצא ‏עם exit 3". ‏זה ‏**‏בלתי-אפשרי**: `opencode run` ‏תמיד ‏מחזיר exit 0 ‏(אומת ‏בקוד `run.ts` — ‏אין `process.exit` ‏עם ‏קוד ‏מהסוכן ‏פרט ‏לקריסות-תשתית). ‏אליעזר ‏הוא ‏LLM ‏בתוך ‏session — ‏אין ‏לו ‏שליטה ‏על ‏exit code ‏של ‏ה-CLI. ‏גם `exit 3` ‏ב-bash tool ‏רץ ‏ב-subshell, ‏לא ‏בתהליך ‏opencode.

**‏הפתרון — ‏file-existence, ‏לא exit code**: ‏אליעזר, ‏כשהוא ‏מחליט ‏BLOCKED ‏ב-Mode 2 (‏מזהה ‏לפי `$BDS_SLICE` ‏מוגדר), ‏פשוט ‏**‏כותב ‏קובץ**:

`$STATE/blocked/$BDS_SLICE.blocked.json`:
```json
{
  "slice": "17",
  "issue": "‏ספריית ‏ה-wake-word ‏לא ‏תומכת ‏בעברית",
  "source": "docs/plans/slice-17-wake-word.md §4 Commit 2",
  "tried": "‏ניסיתי locale=he → unsupported error",
  "need": "‏החלטה: ‏ספרייה ‏אחרת? ‏או ‏לדלג ‏על ‏עברית ‏בסליס?"
}
```

‏וזהו — ‏הוא ‏מסיים ‏את ‏הסשן ‏רגיל. ‏**‏יתרו ‏בודק ‏קיום ‏הקובץ ‏הזה ‏כ-signal ‏הראשון** (‏לפני ‏שמריץ ‏כלב). ‏אם ‏קיים → status=blocked, ‏לא ‏מריץ ‏כלב, ‏קורא ‏את ‏ה-json ‏ל-summary. ‏בבוקר ‏מרדכי ‏רואה ‏בדיוק ‏למה ‏אליעזר ‏נתקע.

‏זה ‏אותו ‏פורמט ‏ISSUE/SOURCE/TRIED/NEED ‏שכבר ‏מוגדר ‏ב-eliezer.md — ‏רק ‏שבמקום ‏להחזיר ‏ל-Task, ‏הוא ‏נכתב ‏לקובץ. ‏קיום-הקובץ ‏הוא ‏הסימן, ‏לא ‏קוד-יציאה.

**‏שתי ‏רשתות ‏ביטחון** ‏לאליעזר ‏שלא ‏מתקדם:
- ‏**BLOCKED ‏מכוון** (‏הוא ‏יודע ‏שהוא ‏תקוע) → ‏כתיבת `blocked.json` (‏יתרו ‏בודק ‏קיום)
- ‏**stuck ‏לא-מכוון** (‏לולאה ‏בלי ‏לעצור) → heartbeat ‏מתיישן → ‏אחרי 2h ‏יתרו ‏הורג (timed-out)

---

## §10 — ‏ארכוב brief

‏כש-slice ‏עובר ‏כלב (verified):

‏יתרו ‏מבצע ‏ב-worktree ‏של ‏ה-slice:

```bash
cd <worktree>
git mv docs/plans/<slice>.md docs/plans/archive/<slice>.md
git commit -m "(docs): archive brief <slice> — verified"
```

‏ככה ‏ה-archive ‏נכנס ‏ל-merge ‏עם ‏ה-slice. ‏אין commit ‏ייעודי ‏נפרד ‏ל-dev — ‏הכל ‏ב-branch ‏של ‏ה-slice.

### §10.1 — merge commits, ‏לא ‏squash (‏לשרשור)

‏בשרשור (B ‏מבוסס ‏על branch ‏של A), ‏כשמרדכי ‏ממזג ‏בבוקר ‏הוא ‏חייב ‏**merge commits** (`git merge --no-ff`), ‏**‏לא ‏squash**. ‏הסיבה: ‏אם A ‏עובר squash ‏ל-commit ‏יחיד ‏ב-dev, ‏ה-ancestry ‏נשבר — B ‏עדיין ‏נושא ‏את ‏ה-commits ‏המקוריים ‏של A, ‏וה-merge ‏של B ‏יביא ‏אותם ‏שוב → ‏כפילויות/conflicts. ‏עם merge commit, git ‏מזהה ‏ancestry ‏משותף ‏ולא ‏מכפיל. ‏(‏אם ‏מרדכי ‏בכל ‏זאת ‏רוצה squash — ‏צריך ‏rebase ‏של B ‏על dev ‏לפני merge.)

---

## §11 — ‏שינויים ‏בקבצים ‏קיימים

| ‏קובץ | ‏שינוי |
|------|--------|
| `~/.config/opencode/SOUL.md` | ‏הוסף ‏איסור merge/push ‏על ‏קוד ‏של ‏executor ‏ללא ‏אישור ‏משתמשת (‏מכסה ‏build agent ‏רגיל + ‏יתרו + ‏אליעזר) |
| `agents/executor.md` → `agents/eliezer.md` | ‏שנה ‏שם, `mode: all`, ‏heartbeat ‏פר-commit (‏אם `$BDS_SLICE`), ‏BLOCKED→‏כתיבת `blocked.json` ב-Mode 2 (‏לא exit 3 — ‏בלתי-אפשרי) |
| `agents/plan-verifier.md` → `agents/avigail.md` | ‏שנה ‏שם, ‏מודל Opus, ‏אימות `depends_on` ‏חובה |
| `agents/verifier-*.md` (3) → `agents/calev.md` | ‏איחוד ‏ל-mode ‏פרמטר (phase/light/heavy) |
| `briefs/EXECUTOR_DISPATCH.md` | ‏עדכן ‏שמות ‏(מרדכי/יתרו/אליעזר/כלב) + ‏מנגנון BLOCKED |
| `briefs/BRIEF_TEMPLATE.md` | §0: ‏סעיף ‏תלויות ‏חובה |
| `SKILL.md` | ‏מפת ‏הצוות, ‏modes, ‏הפניה ‏ל-orchestration.md |
| `workflow.md` | ‏הפניה ‏ל-Mode 2 |
| ‏README ‏של ‏my-skills | ‏עדכון ‏תיאור |

---

## §12 — DoD (‏מה ‏צריך ‏להתקיים ‏בסוף)

| # | ‏בדיקה |
|---|--------|
| 1 | 5 ‏קבצי ‏agents ‏קיימים ‏עם frontmatter ‏תקין. ‏אליעזר = `mode: all` (‏לא subagent — ‏תיקון N4) |
| 2 | `install-agents.sh` ‏יוצר ‏symlinks ‏נכונים ‏ומסיר ‏ישנים |
| 3 | `wait-for-slice.sh` ‏מחזיר exit code ‏נכון ‏ב-תרחישים (success=0/timeout=124/crash=125). ‏BLOCKED ‏מזוהה ‏ע"י ‏יתרו ‏דרך ‏קיום blocked.json, ‏לא ‏ע"י ‏הסקריפט |
| 4 | `dispatch-executor.sh` ‏פותח tmux ‏עם **env scrub ‏מלא (prefix)** + sentinel + ‏prompt ‏דרך stdin |
| 5 | `cleanup_state.py` (python3) ‏מנקה ‏ללא ‏מחיקת state ‏פעיל (‏עיגון id ‏מדויק) |
| 6 | `discard_chain.py` (python3) ‏זורק dependents, ‏מסרב merged, ‏הגנת ‏מעגל |
| 7 | `state.template.json` ‏תקין, ‏עם `depends_on` ‏חובה ‏ו-`base` ‏לשרשור |
| 8 | ‏פרויקט ‏הבית ‏(template) ‏מתועד |
| 9 | SOUL.md ‏מעודכן ‏עם ‏איסור merge (‏מכסה ‏build agent + ‏יתרו + ‏אליעזר) |
| 10 | SKILL.md ‏משקף ‏את ‏הצוות ‏החדש |
| 11 | ‏הסקילים ‏הישנים (executor/plan-verifier/verifier-*) ‏מטופלים |
| 12 | **‏בדיקה ‏אמפירית**: `opencode run --agent eliezer` ‏ב-tmux ‏עם env scrub ‏רץ ‏(לא "Session not found", ‏לא ‏נופל ‏ל-build) |
| 13 | ‏שרשור: slice ‏עם ‏תלות `verified` ‏נגזר ‏מ-branch ‏של ‏התלות, ‏לא ‏מ-dev |
| 14 | ‏BLOCKED ‏ב-Mode 2: ‏אליעזר ‏כותב `blocked.json`; ‏יתרו ‏בודק ‏**‏קיום ‏הקובץ** (‏לא exit 3) ‏ולא ‏מריץ ‏כלב |
| 15 | `python3 -c "import json"` ‏עובד (‏stdlib), ‏אין ‏תלות ‏ב-yq/PyYAML |
| 16 | ‏יתרו ‏בודק blocked.json **‏לפני** ‏exit code ‏בטיפול-תוצאה (‏סדר ‏נכון) |

---

## §13 — ‏שאלות ‏פתוחות (‏עודכן ‏סבב 2)

| # | ‏שאלה | ‏סטטוס |
|---|------|--------|
| 1 | `opencode run --agent X < file` ‏קורא stdin? | ✅ ‏אומת (`run.ts:342`) |
| 2 | `mode: all` ‏לאליעזר ‏חוקי? | ✅ ‏אומת (`config/agent.ts:45`) |
| 3 | ‏אליעזר ‏ב-tmux ‏יודע `$PROJECT`/`$SLICE`? | ✅ `BDS_PROJECT`/`BDS_SLICE` ‏מוזרקים |
| 4 | ‏יתרו ‏יכול `tmux` ‏מ-OpenCode? | ✅ bash ‏מותר |
| 5 | ‏פרסור state ‏שביר? | ✅ ‏נפתר — JSON + python3 stdlib |
| 6 | env scrub ‏prefix ‏מלא ‏עובד ‏ב-tmux? | ⚠️ ‏לאמת ‏אמפירית ‏ב-Commit 0 |
| 7 | ‏הנתיב `$HOME/.opencode/bin/opencode` ‏נכון? | ✅ ‏אומת |
| 8 | yq/PyYAML ‏זמינים? | ✅ ‏לא — ‏לכן JSON+json stdlib (‏אומת `import yaml` ‏נכשל) |
| 9 | `opencode run` ‏מעביר exit code ‏של ‏הסוכן? | ✅ **‏לא** (‏אומת `run.ts`) — ‏לכן BLOCKED ‏דרך ‏קיום `blocked.json`, ‏לא exit 3. ‏סיווג ‏כשל ‏לוגי ‏דרך ‏כלב. |

---

## §14 — ‏סדר ‏ביצוע ‏מוצע (commits)

1. **Commit 0** — `scripts/` (install.sh, wait.sh, dispatch.sh ‏ב-bash; cleanup_state.py, discard_chain.py ‏ב-python3) + **‏בדיקה ‏אמפירית** ‏של ‏שאלה 6 (env scrub ‏prefix ‏ב-tmux ‏עם `opencode run`). ‏זה ‏ה-commit ‏הקריטי — ‏אם ‏ה-env scrub ‏לא ‏עובד, ‏כל ‏השאר ‏חסר ‏טעם.
2. **Commit 1** — 5 ‏קבצי agents (mordechai, yetro, eliezer, avigail, calev) ‏עם ‏smoke-test ‏ש-`opencode run --agent eliezer` ‏רץ ‏כ-eliezer ‏ולא ‏נופל ‏ל-build (‏תיקון N4)
3. **Commit 2** — `state.template.json` + orchestration.md (‏כולל ‏שרשור, 4 ‏מצבי ‏כשל, BLOCKED)
4. **Commit 3** — orchestration-project/ template (‏בית ‏יתרו)
5. **Commit 4** — SOUL.md ‏שינוי (‏איסור merge) + SKILL.md ‏עדכון + ‏טיפול ‏בסקילים ‏ישנים
6. **Commit 5** — ‏עדכון README + ‏walkthrough ‏של ‏הסקיל

---

## §15 — ‏שיפורים ‏עתידיים (‏מתועד, ‏לא ‏נבנה ‏עכשיו)

‏רעיונות ‏שעלו ‏בתכנון ‏ונדחו ‏בכוונה ‏לגרסה ‏הבאה:

### 15.1 ‏סוכן ‏פותר-תקלות

‏סוכן ‏על ‏מודל ‏חכם ‏יותר ‏שמנסה ‏לתקן ‏כשלים ‏אוטומטית ‏בלילה.
**‏למה ‏נדחה**: ‏שובר ‏את ‏העיקרון ‏ש"בלילה ‏אף ‏אחד ‏לא ‏מקבל ‏החלטות ‏מורכבות ‏לבד". ‏סוכן ‏שמתקן ‏אוטומטית ‏עלול ‏לחפור ‏בור ‏עמוק ‏יותר ‏בלי ‏פיקוח. ‏יתרו ‏נשאר ‏טיפש-ובטוח ‏בכוונה.

### 15.2 ‏"להעיר ‏את ‏מרדכי" ‏באמצע ‏הלילה

‏הרצת ‏סשן Opus ‏אד-הוק ‏על ‏כשל ‏בודד.
**‏למה ‏נדחה**: ‏יותר ‏בטוח ‏מ-15.1 ‏(ממוקד, ‏חד-פעמי), ‏אבל ‏דורש ‏הגדרה ‏של ‏"מתי ‏שווה ‏להעיר" ‏בלי ‏שזה ‏יקרה ‏על ‏כל ‏טעות ‏קטנה. ‏לגרסה ‏הבאה.

### 15.3 ‏מקביליות ‏אמיתית ‏ביתרו

‏כרגע ‏סדרתי. ‏ה-infra (tmux + sentinels ‏נפרדים) ‏כבר ‏תומך. **‏למה ‏נדחה**: ‏בלילה ‏אין ‏לחץ ‏זמן, ‏מקביליות ‏רק ‏מסכנת (port conflicts, ‏shared file races). ‏אם ‏יידרש — ‏לולאה ‏שמחזיקה N ‏active.
