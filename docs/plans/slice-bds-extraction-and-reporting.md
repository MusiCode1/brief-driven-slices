# Slice — ‏הוצאת brief-driven-slices ‏לפרויקט ‏נפרד + ‏שכבת ‏דיווח ‏ויומנים

> **‏תאריך**: 2026-05-30
> **‏סטטוס**: ‏מדויק מול קוד — ‏אביגיל סבב 1 ✅ (5 ‏תוקנו) + ‏סבב 2 ✅ (Blocker discard_chain + edge-case תוקנו) — ‏מוכן ל-dispatch
> **Complexity**: 8/10 (verifier: heavy) — ‏מהלך מבני רב-רכיבי, ‏רובו manual/docs
> **‏תלות**: ‏הקוד שאליעזר בנה ב-branch `master` של `~/projects/my-skills` (commits `03b1a6d`→`1f9308c`)
> **Base**: branch `master` ב-my-skills (‏הקוד שאליעזר בנה — ‏ראה §0)

---

## §0 — Pre-flight

> ‏זהו slice מיוחד: ‏הוא בונה/מעביר את התשתית של השיטה עצמה. ‏אין worktree של
> ‏פרויקט-קוד רגיל, ‏אין BE/FE/tunnel. ‏רוב העבודה היא Bash (‏העברת קבצים, symlinks)
> ‏ועריכת Markdown (‏עדכון נתיבים, ‏הגדרות סוכנים).

### ‏תלויות (`depends_on`)

`depends_on: []` — ‏אין תלות ב-slice אחר במערכת ה-state. ‏ה-slice תלוי בקוד
‏שכבר קיים ב-branch `master` של my-skills (לא ב-slice אחר ב-queue), ‏ולכן
‏הרשימה ריקה. ‏זהו slice יחיד שלא רץ דרך יתרו אלא ידנית (Mode 3 — ‏מרדכי/אליעזר ישיר).

‏ה-slice תלוי בקוד הבא (commits `03b1a6d`→`1f9308c`, ‏אומת קיים ב-`master`):
- 5 ‏קבצי agents: `agents/{mordechai,yetro,eliezer,avigail,calev}.md`
- ‏סקריפטים: `scripts/{install-agents.sh,wait-for-slice.sh,dispatch-executor.sh,cleanup_state.py,discard_chain.py}`
- `briefs/{BRIEF_TEMPLATE.md,EXECUTOR_DISPATCH.md,state.template.json}`
- `orchestration-project/` template, `orchestration.md`, `SKILL.md`, ‏עדכון `README.md`

### ‏החלטה (default ‏מאושרת): ‏לא ממזגים `master` ‏ל-my-skills

‏ה-slice **‏מושך את הקוד מ-`master` ‏ישר למיקום החדש** (הפרויקט הנפרד), ‏בלי
merge ביניים. ‏הקוד כבר committed ב-`master`, ‏אז ההעברה היא checkout/copy
‏של עץ הקבצים, ‏לא merge.

### ‏מיקום יעד (default ‏מאושר)

‏פרויקט חדש: `~/projects/brief-driven-slices/` ‏עם git משלו.

### ‏איך לבדוק

‏אין tests אוטומטיים מסורתיים. ‏אימות הוא:
- **(א)** ‏הסקריפטים רצים: `python3 -c "import json"` ‏עובד (stdlib), `cleanup_state.py`/`discard_chain.py` ‏מתפרסים ‏בלי SyntaxError (`python3 -c "import ast; ast.parse(open('...').read())"`).
- **(ב)** ‏ה-symlinks מצביעים נכון: `readlink -f ~/.agents/skills/brief-driven-slices` ‏ו-`~/.config/opencode/agents/{mordechai,...}.md` ‏מצביעים ל-`~/projects/brief-driven-slices/`.
- **(ג)** ‏אין נתיב `my-skills/brief-driven-slices` שנשאר hardcoded בקבצים שעברו (פרט ל-`lessons-learned`, ‏שנשאר ב-my-skills — ‏ראה §3).
- **(ד)** ‏smoke של `opencode run --agent eliezer` ‏מהמיקום החדש (‏שאינו נופל ל-build) — ‏אופציונלי, ‏ראה DoD 14.

### Reading list

**must-read**:
- `docs/plans/orchestration-design.md` (‏המסמך שאליעזר בנה לפיו — 4 ‏סבבי אביגיל)
- ‏הקוד שאליעזר בנה ב-`~/projects/my-skills/brief-driven-slices/` (branch `master`)

**reference**:
- `briefs/BRIEF_TEMPLATE.md`, `briefs/EXECUTOR_DISPATCH.md`

---

## §1 — ‏מטרה

‏שני דברים הבשילו יחד:

**(1)** brief-driven-slices ‏גדל מ"סקיל בודד" ‏למתודולוגיה רב-רכיבית (צוות 5 ‏סוכנים,
‏אורקסטרציה, ‏סקריפטים, ‏תיעוד) ‏שמגיע לה פרויקט משלה עם git משלו — ‏במקום להיות
‏עוד תת-תיקייה ב-my-skills.

**(2)** ‏בזמן הפיתוח גילינו שהמאמתים (אביגיל/כלב) ‏וגם המבצע (אליעזר) ‏מתקשרים
‏ב-**‏הודעה** ‏ולא ב-**‏קובץ**, ‏אז פלט ערכי (דוחות אימות, ‏דיווחי סיום) ‏נעלם
‏כשהסשן נסגר. ‏המעבר להודעה→קובץ הופך את הפלט ל-(א) ‏נשמר ל-debug בבוקר,
‏(ב) ‏חומר-גלם מצטבר לזיקוק חוצה-פרויקטי (brief שני).

‏ה-slice הזה מוציא את השיטה לפרויקט נפרד, ‏הופך את כל פלטי הסוכנים לקבצים
‏נשמרים ‏ומתויגים, ‏ומפריד את התיעוד לשני יומנים (ביצוע של המבצע, ‏החלטות של
‏המתכנן). ‏הוא **‏לא** ‏בונה את שכבת העיבוד (זיקוק, ‏קטלוגים, ‏מדידה) — ‏זה ה-brief השני.

---

## §2 — Scope: ‏מה כן, ‏מה לא

| ‏רכיב | ‏כן/לא | ‏הערה |
|------|------|------|
| ‏הוצאה לפרויקט נפרד `~/projects/brief-driven-slices/` (git init) | ✅ | §4 Commit A |
| ‏עדכון נתיבי `my-skills/brief-driven-slices` ‏בקבצים פנימיים | ✅ | §4 Commit A |
| ‏עדכון symlinks (skill + 5 agents) ‏למיקום חדש | ✅ | §4 Commit A |
| ‏קובץ-דיווח-תמיד של אליעזר (`outcomes/<slice>.json`, ‏מחליף blocked-בלבד) | ✅ | §4 Commit B |
| ‏אביגיל וכלב כותבים דוחות מתויגים ל-`reports/` ‏בריפו השיטה | ✅ | §4 Commit C |
| ‏הפרדת שני יומנים (ביצוע/החלטות) ‏רוחבית | ✅ | §4 Commit D |
| ‏שתי הסטיות של אליעזר (SOUL.md, ‏סוכנים ישנים) — ‏תיעוד | ✅ | §4 Commit E |
| **‏קטלוגים תמציתיים** (plan-pitfalls + patterns) | ❌ | brief ‏שני |
| **‏דוחות זיקוק תקופתיים** + ‏מדידה לאורך זמן | ❌ | brief ‏שני |
| **‏טקסונומיה מתפתחת** + ‏היסטוריית-גרסאות | ❌ | brief ‏שני |
| **‏יומן גלובלי נדיר של השיטה** | ❌ | brief ‏שני (‏או מאוחר יותר) |
| **‏מי מריץ זיקוק / ‏טריגר** | ❌ | brief ‏שני |
| ‏סוכן-פותר-תקלות / ‏הערת-מרדכי-בלילה / ‏מקביליות | ❌ | §15 ‏ב-orchestration-design (‏עתידי) |

> **‏עיקרון החלוקה ראשון/שני**: ‏ה-slice הזה (ראשון) ‏מסיים את שכבת "‏הסוכנים
> ‏כותבים קבצים מתויגים במקום הודעות" + ‏ההעברה המבנית. ‏ה-brief השני בונה
> ‏מעליה את ה-**‏עיבוד** (זיקוק, ‏קטלוגים, ‏מדידה). ‏ה-tags שאנחנו כותבים עכשיו
> ‏(severity + category) ‏הם התשתית שהזיקוק יצרוך.

---

## §3 — Architecture (‏מבנה יעד)

```
~/projects/brief-driven-slices/         ← ‏פרויקט חדש, git משלו
├── .git/
├── SKILL.md
├── workflow.md, worktrees.md, orchestration.md
├── patterns.md, recommendations.md
├── agents/         (mordechai, yetro, eliezer, avigail, calev)
├── scripts/        (install-agents.sh, wait-for-slice.sh, dispatch-executor.sh,
│                    cleanup_state.py, discard_chain.py)
├── briefs/         (BRIEF_TEMPLATE, EXECUTOR_DISPATCH, state.template.json)
├── orchestration-project/
├── reports/        ← NEW: ‏דוחות אימות מתויגים, מצטברים חוצה-פרויקטי (Commit C)
│   └── <project>/  (e.g. voice-acp/, bds/)
│       └── <slice>-<verifier>.json
├── docs/
│   ├── plans/ + plans/archive/
│   ├── decisions/  ← NEW: ‏יומן-החלטות של מרדכי, פר-פרויקט (Commit D)
│   └── case-studies/
└── ...

~/.agents/skills/brief-driven-slices  → symlink ל~/projects/brief-driven-slices/  (מעודכן)
~/.config/opencode/agents/{mordechai,yetro,eliezer,avigail,calev}.md
                                       → symlinks ל~/projects/brief-driven-slices/agents/  (מעודכן)

~/.local/state/brief-driven-slices/<project>/   ← state פר-פרויקט (חיצוני, לא tracked)
├── state.json
├── outcomes/       ← NEW: קבצי-דיווח של אליעזר — Mode 2 בלבד (Commit B)
│   └── <slice>.json   (status: completed | blocked + גוף)
├── dispatches/, logs/, sentinels/, heartbeats/, crashes/, archived/, blocked/
└── yetro.lock
```

### ‏שתי משפחות פלט — ‏הבחנה קריטית (‏לא לבלבל)

| ‏פלט | ‏מי כותב | ‏מתי | ‏איפה | ‏מדוע שם |
|------|---------|------|-------|---------|
| **outcomes** (`<slice>.json`) | ‏אליעזר | Mode 2 ‏בלבד | `$BDS_STATE_DIR/outcomes/` (‏state חיצוני) | ‏רלוונטי לריצה בודדת; ‏יתרו צורך ב-cwd שלו; ‏רעש בריפו השיטה |
| **reports** (`<slice>-<verifier>.json`) | ‏אביגיל + ‏כלב | ‏תמיד (Mode 1 + Mode 2) | `~/projects/brief-driven-slices/reports/<project>/` (‏ריפו השיטה) | ‏חומר-גלם מצטבר לזיקוק חוצה-פרויקטי |

> **‏למה reports בריפו השיטה ולא ב-state החיצוני**: ‏ה-state החיצוני הוא פר-פרויקט
> ‏וחד-פעמי (יתרו מנקה אותו). ‏ה-reports הם חומר-הגלם שה-brief השני יזקק
> ‏**‏חוצה כל הפרויקטים**, ‏אז מקומם בריפו השיטה (מצטבר, tracked, ‏גלובלי).
> ‏זה גם פותר את בעיית Mode 1: ‏הנתיב לריפו השיטה קבוע ולא תלוי ב-env שמזריק
> dispatch-executor.sh (‏ראה §4 Commit C, ‏בעיית "Mode 1 ‏אין BDS_STATE_DIR").

### ‏נתיבי my-skills hardcoded שצריכים שינוי (‏רשימה מאומתת מול grep)

‏ה-slice **‏חייב** ‏לעדכן את כל ההופעות הבאות מ-`~/projects/my-skills/brief-driven-slices/`
‏ל-`~/projects/brief-driven-slices/`:

| ‏קובץ:שורה | ‏ההקשר |
|-----------|--------|
| `scripts/install-agents.sh:3` | `SRC="$HOME/projects/my-skills/brief-driven-slices/agents"` |
| `agents/yetro.md:51` | `python3 ~/projects/my-skills/.../cleanup_state.py` |
| `agents/yetro.md:75` | `bash ~/projects/my-skills/.../dispatch-executor.sh` |
| `agents/yetro.md:79` | `bash ~/projects/my-skills/.../wait-for-slice.sh` |
| `orchestration-project/AGENTS.md:9` | `python3 ~/projects/my-skills/.../cleanup_state.py` |
| `orchestration-project/AGENTS.md:11` | ‏הפניה ל-`~/projects/my-skills/.../agents/yetro.md` |
| `orchestration-project/AGENTS.md:31` | `~/projects/my-skills/.../scripts/` |
| `orchestration-project/README.md:23` | `cp ~/projects/my-skills/.../state.template.json` |
| `orchestration.md:196` | `cp ~/projects/my-skills/.../state.template.json` |
| `orchestration.md:201` | `cp -r ~/projects/my-skills/.../orchestration-project/` |
| `orchestration.md:206` | `bash ~/projects/my-skills/.../install-agents.sh` |
| `SKILL.md:45` | `bash ~/projects/my-skills/.../scripts/install-agents.sh` |

> **‏לא לשנות** (‏נשארים ב-my-skills, ‏זה תקין):
> - `agents/avigail.md:189-190` ו-`agents/calev.md:270-271` — `~/projects/my-skills/lessons-learned/lessons-index`. ‏ה-`lessons-learned` ‏הוא סקיל נפרד שנשאר ב-my-skills.

---

## §4 — Commits

> **‏סדר**: A (‏העברה) ‏חייב להיות ראשון — ‏כל השאר עורכים קבצים במיקום החדש.
> ‏B/C/D/E ‏עורכים את הסוכנים והסקריפטים אחרי שהם כבר ב-`~/projects/brief-driven-slices/`.

### Commit A — ‏הוצאה לפרויקט נפרד + ‏עדכון נתיבים (Testing: `manual`)

**‏מה לעשות**:

1. ‏צור `~/projects/brief-driven-slices/` ‏עם `git init` (branch ראשי `master` ‏או `main` — ‏עקבי לפרויקט).
2. ‏העבר את כל תוכן `~/projects/my-skills/brief-driven-slices/` ‏מ-branch `master` ‏למיקום החדש. ‏שיטה מומלצת:
   ```bash
   cp -a ~/projects/my-skills/brief-driven-slices/. ~/projects/brief-driven-slices/
   # ‏ואז: cd ~/projects/brief-driven-slices && git init && git add -A && git commit
   ```
   ‏(לא להעתיק `.git` ‏של my-skills — ‏פרויקט חדש מתחיל היסטוריה נקייה.)
3. ‏עדכן את **‏כל 12 הנתיבים** ‏ב-§3 (‏טבלת "‏נתיבי my-skills hardcoded") ‏מ-`my-skills/brief-driven-slices` ‏ל-`brief-driven-slices`.
4. ‏עדכן symlink הסקיל:
   ```bash
   rm ~/.agents/skills/brief-driven-slices
   ln -sfn ~/projects/brief-driven-slices ~/.agents/skills/brief-driven-slices
   ```
5. ‏הרץ `bash ~/projects/brief-driven-slices/scripts/install-agents.sh` (‏עם ה-`SRC` ‏המעודכן) ‏כדי לקשר מחדש את 5 הסוכנים מהמיקום החדש.
6. ‏וודא ש-`sync-skills/sync.sh` ‏של my-skills כבר לא ייצור symlink ל-brief-driven-slices: ‏מאחר ש-`brief-driven-slices/` ‏לא תהיה יותר תת-תיקייה ב-my-skills (היא הועברה), ‏הסריקה לא תמצא אותה. ‏**‏אם נשארה תיקייה ריקה/שאריות ב-my-skills** — ‏הסר אותה (`git rm -r brief-driven-slices` ‏ב-my-skills, ‏commit נפרד ב-my-skills).

**‏אימות (manual)**:
- `readlink -f ~/.agents/skills/brief-driven-slices` → `~/projects/brief-driven-slices`
- `readlink -f ~/.config/opencode/agents/mordechai.md` → `~/projects/brief-driven-slices/agents/mordechai.md`
- `grep -rn "my-skills/brief-driven-slices" ~/projects/brief-driven-slices/ --include="*.md" --include="*.sh"` → ‏רק התיעוד ההיסטורי ב-`docs/plans/` ‏(orchestration-design, ‏ה-brief הזה) ‏מותר; ‏קוד/הוראות פעילות — ‏אפס.

> [!warning] ‏בעיית self-reference ב-brief הזה
> ‏ה-brief הזה (`docs/plans/slice-bds-extraction-and-reporting.md`) ‏ו-`orchestration-design.md`
> ‏מכילים בעצמם נתיבי `my-skills/brief-driven-slices` ‏כתיעוד היסטורי. ‏**‏אל תשנה אותם** —
> ‏הם רשומה של מצב לפני ההעברה. ‏ה-grep באימות מתעלם מ-`docs/plans/`.

### Commit B — ‏קובץ-דיווח-תמיד של אליעזר (Testing: `none` — ‏עריכת הגדרת סוכן + סקריפט)

**‏הרקע**: ‏היום ב-Mode 2 ‏אליעזר כותב `blocked.json` ‏**‏רק** ‏כשהוא חסום. ‏אם
‏הסשן קרס לפני שכתב — ‏אין דרך להבחין בין "‏הכל טוב" ‏ל"‏קריסה". ‏הפתרון:
‏קובץ-דיווח שאליעזר כותב **‏תמיד** ‏בסיום (Mode 2), ‏עם שדה `status`.

> [!important] ‏סדר ביצוע פנימי ב-Commit B (‏קריטי — ‏מונע נתיב-החלטה שבור ביתרו)
> ‏ה-sub-steps **‏חייבים** ‏בסדר הזה, ‏אחרת נוצר חלון שבו אליעזר-ישן (‏שלא כותב
> outcomes) ‏רץ מול יתרו-חדש (‏שמצפה ל-outcomes ‏ומסמן "‏קריסה" ‏על היעדרו):
> 1. ‏עדכן `dispatch-executor.sh` (mkdir של outcomes/) — ‏תשתית.
> 2. ‏עדכן `eliezer.md` — ‏שאליעזר **‏יתחיל לכתוב** ‏outcomes תמיד.
> 3. **‏רק אז** ‏עדכן `yetro.md` — ‏שיתרו **‏יתחיל לצפות** ‏ל-outcomes.
> ‏מאחר שזה slice יחיד שמבוצע בבת-אחת (‏לא רץ דרך יתרו, ‏לא נמרג חלקית), ‏אין
> ‏באמת ריצה חיה באמצע — ‏אבל הסדר חשוב כדי שה-DoD יאמת את שלושתם כיחידה.
> ‏**‏אין צורך ב-flag/תקופת-מעבר** ‏כי אין executor ישן בריצה: ‏ברגע שה-slice
> ‏ממוזג, ‏גם eliezer וגם yetro מעודכנים יחד. ‏אביגיל העלתה את הסיכון הזה
> ‏(Risk 5) — ‏ה-mitigation הוא הסדר הזה + ‏ההבהרה ש-yetro ‏אף פעם לא רץ מול
> ‏eliezer מ-version אחרת (‏שניהם symlink לאותו repo, ‏מתעדכנים אטומית ב-merge).

**‏מה לעשות**:

1. **`scripts/dispatch-executor.sh`** — ‏הוסף `outcomes` ‏ל-mkdir (‏השורה הקיימת היא **‏שורה 7**, ‏שמכילה כרגע `{dispatches,logs,sentinels,heartbeats,crashes,archived,blocked}`):
   ```bash
   mkdir -p "$STATE"/{dispatches,logs,sentinels,heartbeats,crashes,archived,blocked,outcomes}
   ```
   > **‏לא לגעת ב-`OPENCODE_BIN` (‏שורה 14)**: ‏הוא `$HOME/.opencode/bin/opencode` — ‏נתיב מערכת, ‏**‏לא** ‏תחת my-skills, ‏לא משתנה בהעברה. (‏אביגיל וידאה — ‏זו לא טעות.)

2. **`agents/eliezer.md`** — ‏עדכן את לוגיקת ה-Mode 2:
   - **‏בסיום מוצלח** (Mode 2, ‏כש-`$BDS_SLICE` ‏מוגדר): ‏כתוב `$BDS_STATE_DIR/outcomes/$BDS_SLICE.json`:
     ```json
     {
       "slice": "<id>",
       "status": "completed",
       "commits": "<base>..HEAD",
       "calev_report": "<path or inline verdict>",
       "deviations": ["..."],
       "notes": "<הערות שנצברו במהלך הריצה>"
     }
     ```
   - **‏בחסימה** (Mode 2): ‏כתוב `outcomes/$BDS_SLICE.json` ‏עם `"status": "blocked"` ‏וגוף שכולל `issue/source/tried/need` (‏אותם שדות כמו ה-blocked.json הקיים). **‏שמור גם על `blocked/$BDS_SLICE.blocked.json`** ‏לתאימות-אחורה עם הסדר הקיים של יתרו, ‏או — ‏מועדף — ‏אחד את שניהם (‏ראה החלטה למטה).
   - ‏עדכן את הקטעים הרלוונטיים: `eliezer.md:59-71` (Mode 2 BLOCKED), `eliezer.md:259-268` (‏פורמט BLOCKED ב-Mode 2), ‏וקטע "‏בסוף הסליס" (`eliezer.md:270-282`) ‏שיכלול כתיבת outcome ב-Mode 2.

3. **‏החלטה — blocked.json מול outcomes (‏פתוחה לאביגיל, §9 Q1)**:
   - **‏אופציה A (‏מומלצת)**: outcomes/<slice>.json ‏הוא המקור היחיד. ‏יתרו בודק קיום `outcomes/<slice>.json` ‏כ-signal ראשון; ‏אם קיים וקורא `status`: `blocked`→‏עצור ענף, `completed`→‏הרץ כלב. ‏**‏מבטל את `blocked/` ‏לגמרי**.
   - **‏אופציה B (‏שמרנית)**: ‏משאיר את `blocked.json` ‏לחסימה, ‏מוסיף outcomes ‏רק ל-completed. ‏יתרו בודק blocked.json קודם (‏סדר קיים), ‏אז outcomes.
   - ‏ה-default ב-brief: **‏אופציה A** — ‏היעדר outcomes = ‏קריסה (‏לא "‏הכל טוב"). ‏זה מחדד את זיהוי-הקריסה, ‏וזו בדיוק המטרה (#1.9 ‏בדיון). ‏אביגיל תאמת שאין נתיב שבו יתרו מתבלבל.

4. **`agents/yetro.md`** — ‏עדכן את "‏טיפול בתוצאה" (`yetro.md:82-90`) ‏ואת §9 ‏ב-orchestration-design (‏שורות 344-358):
   - **‏הקשר**: ‏יתרו רץ **‏רק ב-Mode 2** (tmux). ‏בלילה אליעזר **‏תמיד** ‏כותב outcomes (‏זו ההוראה החדשה ב-eliezer.md). ‏לכן "‏היעדר outcomes" ‏בלילה = ‏באמת קריסה (‏אליעזר לא הגיע לכתוב). ‏אין כאן בעיית Mode 1 — ‏יתרו לא נוגע ב-Mode 1.
   - ‏סדר הבדיקה החדש (‏מחליף את `yetro.md:82-90`, ‏סעיף "‏טיפול בתוצאה"):
     ```
     (1) קיים $STATE/outcomes/<slice>.json?
         לא קיים → status=crashed (אליעזר לא סיים לכתוב — קריסה שקטה). עצור ענף.
         קיים → קרא status:
            status=="blocked"   → status=blocked. עצור ענף. לא מריץ כלב.
            status=="completed" → המשך לבדיקת exit code (2)-(4), אז הרץ כלב.
     (2) exit 124 → timed-out → עצור ענף
     (3) exit 125 → crashed   → שמור crash log → עצור ענף
     (4) exit ≠0  → failed:infra → עצור ענף
     (5) exit 0 + status==completed → הרץ כלב (GO→verified→ארכב; NO→needs-revision)
     ```
   - **‏הבהרה ל-edge case** (‏אביגיל סבב 2): ‏שלבים (2)-(4) ‏עדיין רלוונטיים גם אחרי `completed`, ‏כי הם guard ל-**‏קריסה אחרי כתיבת outcomes ולפני סיום נקי**: ‏אם אליעזר כתב `completed` ‏ואז ה-tmux נהרג (timeout/crash), ‏ה-sentinel יחזיר 124/125 ‏ויתרו יסמן timed-out/crashed — **‏לא** verified. ‏זו ההתנהגות הרצויה (‏אליעזר לא באמת סיים נקי). ‏אין נתיב שבו completed שגוי הופך ל-verified.
   - ‏עדכן גם `agents/yetro.md:176-186` (‏קריאת blocked.json) ‏לקריאת `outcomes/<slice>.json`.
   - ‏עדכן את `yetro.md:83-84` ‏(הערת "‏הבדיקה הראשונה!") ‏ואת anti-pattern `yetro.md:226` ("‏לבדוק exit code לפני blocked.json") ‏→ "‏לפני outcomes".
   - ‏עדכן `orchestration-design.md` §9 ‏(שורות 344-358) ‏ו-§7 ‏(שורות 344-362) ‏לשקף את הסדר החדש (outcomes ‏מחליף blocked.json ‏כ-signal ראשון).

5. **`briefs/EXECUTOR_DISPATCH.md:138-152`** — ‏הקטע הקיים "BLOCKED ב-Mode 2" ‏כותב `blocked/$BDS_SLICE.blocked.json`. ‏החלף את גוף ה-bash ל-outcomes (status=blocked):
   ```bash
   # היה: cat > "$BDS_STATE_DIR/blocked/$BDS_SLICE.blocked.json"
   # יהיה:
   cat > "$BDS_STATE_DIR/outcomes/$BDS_SLICE.json" << 'EOF'
   {
     "slice": "$BDS_SLICE",
     "status": "blocked",
     "issue": "...",
     "source": "...",
     "tried": "...",
     "need": "..."
   }
   EOF
   ```
   ‏ועדכן את משפט-הסיום (`:152`) ‏מ-"‏יתרו בודק קיום הקובץ ‏לפני exit code" ‏ל-"‏יתרו בודק `outcomes/<slice>.json` ‏לפני exit code; ‏`status=blocked` → ‏עצור ענף".
   ‏**‏אותו שינוי** ‏גם ב-`agents/eliezer.md:61-70` ‏וב-`eliezer.md:259-268` (‏שני המקומות שמראים את כתיבת blocked.json).

6. **`scripts/discard_chain.py:49`** — ‏**‏קוד פעיל** (‏לא תיעוד). ‏השורה מנקה את תיקיות ה-state כש-slice נזרק. ‏אופציה A ‏מבטלת את `blocked/`, ‏לכן החלף `"blocked"` ‏ב-`"outcomes"` ‏ברשימה:
   ```python
   # היה:  for sub in ("dispatches", "logs", "sentinels", "heartbeats", "blocked"):
   for sub in ("dispatches", "logs", "sentinels", "heartbeats", "outcomes"):
   ```
   > ‏אחרת קובץ outcomes של slice שנזרק יישאר זבל ב-state dir. ‏(אביגיל תפסה — Blocker סבב 2.)
   > ‏`cleanup_state.py` ‏**‏לא** ‏נוגע ב-`blocked/`/`outcomes/` (‏מנקה logs/archived/heartbeats בלבד) — ‏אין מה לשנות שם.

**‏אימות (none)**: `python3 -c "import ast; ast.parse(...)"` ‏על dispatch-executor.sh? ‏לא — ‏זה bash. ‏במקום: `bash -n scripts/dispatch-executor.sh` (‏syntax check). ‏לוגיקת eliezer/yetro היא Markdown — ‏אימות הוא קריאה אנושית (‏אביגיל/מרדכי).

### Commit C — ‏אביגיל וכלב כותבים דוחות מתויגים לארכיב (Testing: `none`)

**‏המבנה**: `~/projects/brief-driven-slices/reports/<project>/<slice>-<verifier>.json`
- `<verifier>` ∈ `{avigail, calev}`
- ‏שטוח-יחסית: ‏תיקיית `<project>` ‏אחת, ‏הקובץ נושא שדות פנימיים `project` + `verifier`.
- ‏דוגמה: `reports/voice-acp/17-wake-word-avigail.json`, `reports/voice-acp/17-wake-word-calev.json`.

**‏מבנה הדוח המתויג (JSON, ‏ראש + ‏גוף findings)**:
```json
{
  "project": "voice-acp",
  "slice": "17",
  "verifier": "avigail",
  "date": "2026-05-30T...",
  "verdict": "USABLE-AFTER-FIX",
  "findings": [
    {
      "id": 1,
      "severity": "blocker",          // blocker | regression | confusion | type-error | outdated | minor
      "category": "missing-symbol",    // טקסונומיה ראשונית — ראה רשימה למטה
      "summary": "deleteAgent לא קיים ב-dev",
      "source_brief": "§4 Commit 0",
      "source_code": "packages/.../agents-api.ts:23",
      "cost_estimate": "15-30min"
    }
  ]
}
```

**‏טקסונומיה ראשונית** (‏לא קפואה — ‏ה-brief השני יפתח אותה):
- ‏אביגיל (plan): `missing-symbol`, `dropped-branch`, `type-error`, `wrong-line-number`, `naming-inconsistency`, `wrong-path`, `outdated-risk`, `missing-dependency`.
- ‏כלב (runtime): `bubble-grouping`, `cross-store-null`, `spec-drift`, `regression`, `mobile-desktop`, `reload-reconnect`, `library-compat`, `unique`.

> ‏ה-`category` ‏הוא **‏מנבא** — ‏אם הסוכן לא בטוח, `unique`. ‏ה-brief השני יזקק.
> ‏ה-`severity` ‏הוא הציר העיקרי למדידה (‏כמה blockers נתפסו לפני ביצוע).

**‏מה לעשות**:

1. **`agents/avigail.md`**:
   - ‏שנה frontmatter `write: false` (‏שורה 29) → `write: true`. ‏(אביגיל היום read-only; ‏צריכה לכתוב את הדוח. ‏זה לא סותר את "‏אסור לערוך קוד/brief" — ‏היא כותבת **‏רק** ‏ל-`reports/`, ‏לא לקוד.)
   - ‏עדכן את Anti-pattern `avigail.md:43` ("‏אסור לערוך קוד או brief") → ‏הבהר: ‏מותר לכתוב ל-`reports/` ‏בלבד.
   - ‏הוסף שלב בפורמט הדוח (`avigail.md:142-182`): ‏אחרי הדוח ה-Markdown, ‏כתוב גם JSON מתויג ל-`~/projects/brief-driven-slices/reports/<project>/<slice>-avigail.json`.
   - ‏הוסף הוראה איך לגזור `<project>` ‏מה-prompt: ‏ה-prompt כולל "Project root: <path>" → `<project>` = ‏basename. ‏אם ה-prompt לא כולל project → ‏השתמש ב-`unknown` ‏ו-warn.

2. **`agents/calev.md`**:
   - frontmatter כבר `write: true` (**‏שורה 33**, ‏לא 27 — ‏שורה 27 היא `webfetch: allow`) — ‏אין שינוי ב-frontmatter.
   - ‏היום כלב כותב `docs/<slice>-verification-report.md` ‏בריפו הפרויקט (`calev.md` ‏פורמטים, ‏ו-`eliezer.md:319`). ‏**‏הוסף** ‏כתיבת JSON מתויג ל-`reports/<project>/<slice>-calev.json` ‏(בנוסף ל-Markdown, ‏או במקומו — ‏ראה החלטה).
   - **‏החלטה (§9 Q2)**: ‏המלצה — ‏השאר את ה-Markdown report בריפו הפרויקט (אנושי, ‏נוח לקריאה בבוקר) **‏וגם** ‏כתוב JSON מתויג לריפו השיטה (מצטבר לזיקוק). ‏הכפילות מקובלת — ‏שני קוראים שונים (אדם בבוקר מול זיקוק חוצה-פרויקטי).
   - ‏גזירת `<project>`: ‏מה-prompt (סביבה/brief path) ‏או מה-cwd.

3. ‏צור `reports/.gitkeep` ‏ו-`reports/README.md` ‏קצר שמסביר את המבנה והטקסונומיה.

> [!warning] ‏בעיית Mode 1 — ‏אין BDS_STATE_DIR לאביגיל/כלב
> ‏ב-Mode 1 (Task ‏מ-מרדכי) ‏אין dispatch-executor.sh ‏שמזריק env. ‏לכן הדוחות
> ‏**‏חייבים** ‏ללכת לנתיב קבוע (`~/projects/brief-driven-slices/reports/`), ‏לא
> ‏ל-`$BDS_STATE_DIR`. ‏הסוכנים בונים את הנתיב מ-`$HOME` ‏ישירות. ‏זה דורש
> `permission: external_directory: allow` — ‏אומת קיים אצל שניהם
> (`avigail.md:24`, `calev.md:28`).

**‏אימות (none)**: ‏קריאה אנושית של הגדרות הסוכנים + ‏וידוא ש-`reports/` ‏קיימת.

### Commit D — ‏הפרדת שני יומנים (Testing: `none`)

**‏ההבחנה**:
- **‏יומן-ביצוע** (`docs/walkthrough.md` ‏בריפו הפרויקט) — ‏של אליעזר, ‏כרונולוגי, "‏משעמם": "brief בוצע. ‏אם היו חריגות — ‏הנה הן." ‏מבצע שכותב יומן ארוך = ‏מגדיל ראש.
- **‏יומן-החלטות** (`docs/decisions/` ‏בריפו השיטה, ‏פר-פרויקט) — ‏של מרדכי, ‏נושאי, ‏רציונל: "‏למה בחרנו ככה, ‏מה אביגיל מצאה, ‏שינויי-כיוון."

**‏מה לעשות**:

1. **`~/projects/my-skills/update-walkthrough/SKILL.md`** (‏זה המקור; ‏ה-symlink הוא `~/.agents/skills/update-walkthrough/SKILL.md` → ‏ערוך את המקור) — ‏נשאר ב-my-skills (‏החלטה D):
   - ‏הוסף סעיף שמבהיר את ההפרדה: ‏walkthrough = ‏ביצוע (‏מה קרה, ‏כרונולוגי). ‏יומן-החלטות = ‏קובץ נפרד (‏לא תיוג בתוך walkthrough — ‏פרסור שביר).
   - ‏הבהר שה-walkthrough הוא תחום המבצע; ‏החלטות-תכנון הולכות לקובץ נפרד שמרדכי מתחזק.

2. **`agents/eliezer.md`** (‏יומן-ביצוע):
   - ‏עדכן `eliezer.md:175`, `eliezer.md:272`, ‏וקטע DoD: ‏ה-walkthrough של אליעזר הוא **‏רק ביצוע** — ‏מה בוצע, ‏חריגות, ‏בדיקות. ‏לא רציונל ארכיטקטוני (‏זה של מרדכי).

3. **`agents/mordechai.md`** (‏יומן-החלטות):
   - ‏הוסף סעיף "‏יומן-החלטות": ‏לכל brief חתום-לביצוע, ‏מרדכי כותב entry ל-`docs/decisions/<project>.md` (‏בריפו השיטה) ‏עם: ‏הרציונל, ‏מה אביגיל מצאה, ‏שינויי-כיוון, ‏רעיונות-שנדחו.
   - ‏הבהר את ההבחנה מ-`walkthrough` (‏ביצוע) ‏ומ-`reports` (‏ממצאי אימות גולמיים).

4. ‏צור `docs/decisions/.gitkeep` ‏ו-`docs/decisions/README.md` ‏קצר.

> ‏**‏הבחנה לאביגיל לאמת**: ‏שלושה סוגי זיכרון נפרדים, ‏לא לבלבל:
> - `walkthrough.md` (‏ריפו פרויקט) — ‏ביצוע, ‏אליעזר.
> - `decisions/<project>.md` (‏ריפו שיטה) — ‏רציונל, ‏מרדכי.
> - `reports/<project>/*.json` (‏ריפו שיטה) — ‏ממצאי אימות גולמיים, ‏אביגיל/כלב.

**‏אימות (none)**: ‏קריאה אנושית.

### Commit E — ‏תיעוד שתי הסטיות (Testing: `none`)

**‏שתי הסטיות שאליעזר עשה בבנייה (כבר בוצעו — ‏זה Commit תיעוד, ‏לא פעולה)**:

1. **SOUL.md** — ‏האיסור על merge/push על קוד של executor **‏כבר נכנס** ‏ל-`~/.config/opencode/SOUL.md:29` (‏אומת). ‏הקובץ לא tracked ב-git (‏שינוי ישיר). **‏פעולה**: ‏רק לתעד ביומן-ההחלטות שזה בוצע ‏ושזה שינוי-ישיר מכוון (‏לא ב-repo). ‏**‏אין מה לשנות ב-SOUL.md** — ‏הוא כבר נכון.

2. **‏סוכנים ישנים** (`executor`, `plan-verifier`, `verifier-phase`, `verifier-slice-light`, `verifier-slice-heavy`) — ‏נמחקו לגמרי, ‏בלי גיבוי. ‏אומת: ‏אינם ב-`~/.config/opencode/agents/` (‏רק החדשים + just-a-man + yolo). ‏היו untracked ממילא. **‏פעולה**: ‏תעד ביומן-ההחלטות כהחלטה מודעת בלי גיבוי. ‏`install-agents.sh:13-14` ‏כבר מנקה symlinks ישנים — ‏אין מה להוסיף.

**‏מה לעשות**: ‏entry ביומן-ההחלטות (`docs/decisions/bds.md`) ‏שמתעד את שתי ההחלטות. ‏זהו.

**‏אימות (none)**:
- `grep -n "executor" ~/.config/opencode/SOUL.md` → ‏האיסור קיים.
- `ls ~/.config/opencode/agents/` → ‏אין executor/plan-verifier/verifier-*.

---

## §5 — DoD (Definition of Done)

| # | ‏בדיקה | ‏איך לאמת |
|---|--------|---------|
| 1 | `~/projects/brief-driven-slices/` ‏קיים עם git משלו, ‏כל התוכן הועבר | `ls`, `git -C ... log -1` |
| 2 | symlink הסקיל מצביע למיקום החדש | `readlink -f ~/.agents/skills/brief-driven-slices` |
| 3 | 5 ‏symlinks של סוכנים מצביעים למיקום החדש | `readlink -f ~/.config/opencode/agents/mordechai.md` ‏וכו' |
| 4 | ‏אין נתיב `my-skills/brief-driven-slices` ‏hardcoded בקוד/הוראות פעילות (‏פרט ל-docs/plans היסטורי ו-lessons-learned) | `grep -rn` |
| 5 | `install-agents.sh:3` `SRC=` ‏מצביע למיקום החדש | ‏קריאה |
| 6 | `dispatch-executor.sh` ‏יוצר `outcomes/` (mkdir כולל אותו) | `grep outcomes scripts/dispatch-executor.sh` |
| 7 | `eliezer.md` ‏כותב outcome **‏תמיד** ‏ב-Mode 2 (completed + blocked) | ‏קריאה |
| 8 | `yetro.md` + orchestration-design §9: ‏בודק `outcomes/<slice>.json` ‏כ-signal ראשון; ‏היעדרו = ‏קריסה. ‏anti-pattern `yetro.md:226` ‏עודכן ל-"outcomes לפני exit" | ‏קריאה |
| 8b | ‏סדר deployment ב-Commit B: dispatch-executor → eliezer → yetro (‏אליעזר כותב לפני שיתרו מצפה). ‏שלושתם באותו commit/merge | ‏קריאה |
| 8c | ‏אופציה A — ‏**‏קבצים פעילים** ‏הוסבו מ-blocked ל-outcomes: eliezer.md (61-70, 259-268), yetro.md (83, 176-186, **226** anti-pattern), EXECUTOR_DISPATCH (138-152), **`discard_chain.py:49`** (`"blocked"`→`"outcomes"`), orchestration-design §7/§9 (344-358) | ‏קריאה + ‏`grep -n outcomes scripts/discard_chain.py` |
| 8d | ‏אזכורי `blocked.json` ‏שנשארו = ‏**‏רק תיעוד היסטורי** (`docs/plans/` ‏ישן). ‏אין קוד/הוראה פעילה שמסתמכת על `blocked/` | `grep -rn "blocked.json" --include="*.md" --include="*.py"` ‏→ ‏רק docs/plans |
| 9 | `avigail.md` frontmatter `write: true`; ‏כותב JSON מתויג ל-`reports/<project>/<slice>-avigail.json` | ‏קריאה |
| 10 | `calev.md` ‏כותב JSON מתויג ל-`reports/<project>/<slice>-calev.json` (‏בנוסף ל-MD) | ‏קריאה |
| 11 | ‏מבנה הדוח כולל `severity` + `category` ‏פר finding | ‏קריאה |
| 12 | `reports/` + `docs/decisions/` ‏קיימות עם README/‏.gitkeep | `ls` |
| 13 | ‏הפרדת היומנים מתועדת: update-walkthrough (‏ביצוע), mordechai.md (‏החלטות) | ‏קריאה |
| 14 | ‏שתי הסטיות מתועדות ב-`docs/decisions/bds.md`; SOUL.md ‏אומת קיים; ‏סוכנים ישנים אומתו לא-קיימים | `grep`, `ls` |
| 15 | ‏הסקריפטים מתפרסים: `python3 -c "import ast; ast.parse(...)"` ‏ל-.py, `bash -n` ‏ל-.sh | ‏הרצה |
| 16 | (‏אופציונלי) smoke: `opencode run --agent eliezer` ‏מהמיקום החדש לא נופל ל-build | ‏הרצה |

---

## §6 — Risks

| # | ‏סיכון | ‏חומרה | ‏מיטיגציה |
|---|-------|--------|----------|
| 1 | **‏שכחת נתיב hardcoded** — ‏נתיב my-skills שנשאר → ‏סקריפט/הפניה שבורה אחרי שתימחק התיקייה הישנה | 🔴 ‏גבוה | ‏grep מקיף ב-DoD 4. ‏טבלת 12 הנתיבים ב-§3. ‏אל תמחק את התיקייה הישנה ב-my-skills עד אחרי אימות grep נקי |
| 2 | **‏מחיקת התיקייה הישנה מוקדם מדי** — ‏אם מוחקים `my-skills/brief-driven-slices` ‏לפני שכל הנתיבים עודכנו | 🔴 ‏גבוה | ‏Commit A: ‏מחיקה היא **‏הצעד האחרון**, ‏commit נפרד ב-my-skills, ‏רק אחרי DoD 4 ✅ |
| 3 | **self-reference** — ‏ה-brief הזה ו-orchestration-design מכילים נתיבי my-skills כתיעוד → ‏grep תופס אותם כ"‏לא עודכן" | 🟡 ‏בינוני | ‏ה-grep מחריג `docs/plans/`. ‏מתועד ב-Commit A warning |
| 4 | **‏אביגיל write:true ‏מסוכן** — ‏אם אביגיל תתחיל לכתוב לקוד/brief במקום רק ל-reports | 🟡 ‏בינוני | ‏הבהרה מפורשת ב-anti-patterns: ‏כתיבה **‏רק** ‏ל-`reports/`. ‏לאמת ב-Commit C |
| 5 | **‏יתרו מתבלבל ב-outcomes** — ‏שינוי הסדר (outcomes לפני exit code) ‏עלול ליצור נתיב שבו completed מסומן crashed או להפך | 🔴 ‏גבוה | ‏אופציה A מפורטת; ‏אביגיל תאמת את כל ענפי ההחלטה ב-yetro.md מול orchestration-design §9 |
| 6 | **‏גזירת `<project>` ‏בסוכנים שגויה** — Mode 1 ‏לא תמיד נותן project root מפורש | 🟡 ‏בינוני | ‏fallback ל-`unknown` + warn; ‏מרדכי תמיד מעביר "Project root" ‏ב-Task prompt (‏mordechai.md:144 ‏כבר עושה) |
| 7 | **‏היסטוריית git אבודה** — ‏פרויקט חדש מתחיל מ-commit אחד, ‏היסטוריית הפיתוח של הסוכנים ב-my-skills | 🟢 ‏נמוך | ‏מקובל — ‏ההיסטוריה נשמרת ב-my-skills git. ‏אפשר לתעד ב-decisions שזו נקודת-פיצול מכוונת |

---

## §7 — Escalation (‏מתי אליעזר עוצר ושואל את מרדכי)

‏עצור ו-BLOCKED אם:

1. **‏העברת הקבצים יוצרת קונפליקט** — ‏אם `~/projects/brief-driven-slices/` ‏כבר קיים עם תוכן לא-ריק (‏לא לדרוס). ‏שאל.
2. **grep מוצא נתיב my-skills שלא ברשימת 12** — ‏אם יש הופעה לא-צפויה (‏למשל בקובץ שלא נסקר), ‏אל תנחש — ‏דווח לאיזה קובץ ‏ומה ההקשר.
3. **‏החלטת blocked.json מול outcomes** (§4 Commit B Q1) — ‏אם אופציה A יוצרת רגרסיה בלוגיקת יתרו שלא צפינו, ‏עצור עם הפירוט.
4. **frontmatter של אביגיל/כלב** — ‏אם שינוי `write:true` ‏שובר משהו ב-OpenCode (‏schema validation), ‏דווח.
5. **‏מחיקת התיקייה הישנה** — ‏אם יש ספק האם בטוח למחוק `my-skills/brief-driven-slices` (‏תלות חיצונית שלא ידועה), ‏**‏אל תמחק** — ‏השאר ל-מרדכי להחליט ידנית.

**‏אל תשאל על**: ‏שם branch (master/main), ‏פורמט README של reports/decisions, ‏סדר הצעדים בתוך commit.

---

## §8 — Complexity score

| ‏ציר | ‏ניקוד | ‏נימוק |
|------|--------|--------|
| ‏מספר קבצים נוגעים | 3 | ~12 ‏קבצים (5 agents, 3 scripts, SKILL, 2 docs-new, update-walkthrough, EXECUTOR_DISPATCH) |
| ‏סיכון רגרסיה | 2 | ‏שינוי הסדר ב-yetro (outcomes) ‏ושינוי symlinks — ‏עלול לשבור dispatch אם שגוי |
| ‏עומק לוגי | 1 | ‏רוב העבודה manual/docs; ‏מעט לוגיקה (רק ענפי ההחלטה ב-yetro) |
| ‏תלות בקוד קיים | 1 | ‏מבוסס על master הקיים, ‏לא בונה מאפס |
| ‏אימות אמפירי | 1 | ‏smoke אופציונלי; ‏רוב האימות הוא grep + ‏קריאה |
| **‏סה"כ** | **8/10** | **calev tier: heavy** (‏בעיקר בגלל סיכון הרגרסיה של symlinks + ‏סדר yetro) |

> ‏ההצדקה ל-heavy למרות שרוב העבודה docs: ‏אם symlink או נתיב hardcoded שגוי,
> ‏**‏כל מערכת האורקסטרציה מפסיקה לעבוד** ‏באופן שקט. calev heavy יריץ smoke
> ‏אמיתי של dispatch + ‏יבדוק שכל ה-symlinks resolve.

---

## §9 — ‏שאלות פתוחות

| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | blocked.json מול outcomes — ‏מאחדים (A) ‏או משאירים שניהם (B)? | **A** (‏outcomes יחיד, ‏היעדר=קריסה). ‏אביגיל אימתה (Risk 5): ‏ה-mitigation הוא סדר ה-deployment ב-Commit B (‏dispatch→eliezer→yetro, ‏באותו merge) — ‏אין executor ישן בריצה | ❌ ‏(‏סגור) |
| 2 | calev — JSON מתויג **‏במקום** ‏או **‏בנוסף** ‏ל-MD report? | **‏בנוסף** (‏MD לאדם, ‏JSON לזיקוק) | ❌ |
| 3 | ‏שם ה-branch הראשי בפרויקט החדש | `master` (‏עקבי ל-my-skills) | ❌ |
| 4 | ‏מבנה reports: `reports/<project>/<slice>-<verifier>.json` ‏או שטוח לגמרי? | ‏תת-תיקייה פר project | ❌ |
| 5 | ‏יומן-החלטות: ‏קובץ אחד פר-פרויקט (`decisions/<project>.md`) ‏או נושאי? | ‏פר-פרויקט | ❌ |
| 6 | ‏מתי למחוק `my-skills/brief-driven-slices` ‏הישנה? | ‏Commit נפרד ב-my-skills, ‏אחרי DoD 4 ✅; ‏אם ספק — ‏מרדכי ידנית | ❌ |

---

## §10 — calev tier

`calev: heavy` — ‏ראה §8. ‏ה-heavy יכלול: smoke של `opencode run --agent eliezer`
‏מהמיקום החדש, ‏וידוא שכל ה-symlinks resolve (`readlink -f`), ‏grep נקי לנתיבי
my-skills, ‏ובדיקה שהסקריפטים מתפרסים.
