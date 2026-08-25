# Walkthrough — brief-driven-slices

> ‏יומן-ביצוע כרונולוגי: ‏מה נבנה, ‏מתי, ‏ובאילו commits. ‏מתחזק ע"י אליעזר (executor).
> ‏"משעמם בכוונה": brief בוצע + ‏חריגות. ‏הרציונל וההחלטות → `docs/decisions/bds.md`.

---

## 2026-08-25 — שיגור לא-חוסם + סבב-הסגירה של ריצות 11–13

**הנחיית המשתמש:** *"שלא יריצו אף פעם סוכנים במצב חוסם, כדי שהשרשור הראשי
יישאר פנוי למשתמש לשאול שאלות."* הכלל נכנס כסעיף ב-`SKILL.md` והופץ לכל
נקודת-שיגור.

| קובץ | מה |
|------|------|
| `SKILL.md` | §שיגור לא-חוסם — הכלל, הנימוק, ומה מחליף את ההמתנה (ראיות-עץ) |
| `agent-definitions/prompts/{mordechai,eliezer,yetro}.md` | `run_in_background: true` בכל בלוק `Task({...})` + כלל מפורש בראש "הפעלת הצוות" |
| `autonomous-runs/prompts/kickoff-mordechai.md` | שורת-השיגור הופכה; אזהרה 1 **נמשכה** בגוף המסמך עם הראיה ששללה |
| `autonomous-runs/skills/autorun/SKILL.md` §6 | אזהרה 1 הופכה |
| `orchestration.md` · `SKILL.md` Mode 1 | `[חוסם]` → `[רקע]` + הבהרה ש"סינכרוני" = סדר, לא תור חסום |

**תיקון-drift שנחשף תוך כדי:** `generate-cli-configs.py` כותב גם ל-`agents/`,
ועריכות 23/08 (היפוך ה-plan-gate) נכתבו ישירות לשם ולא ל-`agent-definitions/prompts/`
⇒ **כל הרצה של הגנרטור החזירה אותן לאחור.** התגלה בהרצה חיה. `prompts/` סונכרן
מ-`agents/`, אומת round-trip (הגנרטור משחזר את `agents/` בית-בית), ואז הכלל החדש
הוחל על `prompts/` והופץ לכל ה-adapters. נרשם כפריט 14 ב-`BACKLOG.md` — חסר **שער**
שיתפוס drift כזה.

**‏`~/.claude/agents/` עודכן ידנית** (frontmatter של claude-code + הצבת `{{BDS_*}}`),
כי אין יעד `claude-code` בגנרטור — פריט 15 ב-BACKLOG.

**סבב-הסגירה של הניסוי:**

| קובץ | מה |
|------|------|
| `autonomous-runs/README.md` | סעיף-מצב מעודכן (נעצר בריצה 6) — 3 ריצות רצופות עם 0 צנרת; תנאי-היציאה **לא** התקיים כי 12 ו-13 נשאו כשל-מסירה אחד כל אחת; שורת `replay-quiet` היתומה הוחזרה לטבלה כ-`9*` |
| `RUN_REPORT_TEMPLATE.md` | `plan_rounds` + `brief_to_dispatch` כשדות-חובה + §שעון ה-plan-gate — תנאי-הסגירה השלישי של באג #1, שאף דוח לא מדד |
| `MISSION_TEMPLATE.md` §8ב | **פיקסצ'ר ≠ חוט** — תיקון-קבע 1 מריצה 13 |
| `kickoff-mordechai.md` | אזהרה 5: משתני-סביבה גנריים דולפים בעץ-התהליכים — תיקון-קבע 2 מריצה 13 |

**אימות:** 49/49 טסטים (`tests/test_path_substitution.py` 10, `tests/test_distill.py` 39),
`git diff agents/` ריק אחרי round-trip של הגנרטור.

---

## 2026-08-23 — ‏היפוך ה-plan-gate: ‏סבב אחד, ‏ההרצה זולה מהסבב (‏באג ‎#1)

‏בעקבות חקירת "‏כל משימה קטנה נמשכת שעות" (‏`docs/investigations/2026-08-23-slow-mechanism-diagnosis.md`):

| ‏קובץ | ‏מה |
|------|------|
| `MISSION_TEMPLATE.md` §4-5 | plan-gate = ‏סבב אביגיל אחד · ‏תיקון-במקום כשאילתות · ‏ביצוע-זריק · ‏בסיס קפוא |
| `agents/avigail.md` | ‏דוקטרינת ה-100% הוסרה · ‏אפס-ממצאים לגיטימי · ‏סבב חוזר = ‏דלתא |
| `agents/mordechai.md` | ‏"המאמת הוא קו ההגנה האחרון" · evidence ‏כחפצים ברי-הרצה · lint-brief ‏לפני שיגור |
| `agents/eliezer.md` · `agents/calev.md` | ‏שני ה-⬜ ‏מריצות 4–5 ‏נסגרו: ‏המבצע לא משגר מאמת · ‏מוטציה לא-מורצת = ‏אין GO |
| `briefs/BRIEF_TEMPLATE.md` | dispatch ‏בלי תנאי-READY · worktree ‏מ-hash · ‏חתימות-בלבד |
| `scripts/lint-brief.py` (‏חדש) | ‏אכיפה מכנית של איסור מספרי-שורות (‏אומת: ‏51 🔴 ‏על הבריף החי של replay-quiet) |
| `scripts/bds-init.sh` (‏חדש) + `~/.zshenv` | ‏חוב `bds init` ‏מריצות 4–8 — ‏השורש: `paths.env` ‏היה קיים ולא נטען |

‏רציונל מלא: `docs/decisions/bds.md` ‏רשומת 2026-08-23.

## 2026-08-18 — ‏בקלוג מאוחד עם סטטוס נגזר + ‏בריף `current-state-section`

‏חקירת ארכיון הדוחות (675 ‏דוחות, ‏מהם 380 ‏של אביגיל) ‏העלתה שתי מסקנות שהובילו לשינוי:

| ‏ממצא | ‏מספר |
|------|------|
| `dropped-branch` — ‏"‏התוכנית לא מתחשבת בקיים" | **145 ‏מ-378 ‏החוסמים (38%)**, ‏הגדולה ביותר |
| ‏ממנה, ‏ניתן לגילוי מכני (`grep`) | ‏רק **22%** — ‏שאר ה-79% ‏סמנטיים |
| ‏הפניות שאינן קיימות (`missing-symbol`/`-dependency`/`wrong-path`) | **117 (31%)**, ‏וכמעט 100% ‏מכניות |
| ‏חוסמים בסבבים 2+ ‏שהקטגוריה שלהם כבר הופיעה באותה שרשרת | **121 ‏מול 14 ‏חדשות** |

**‏מה נוסף**:

| ‏קובץ | ‏מה |
|------|------|
| `BACKLOG.md` | ‏מקור-אמת יחיד לעבודה פתוחה. **‏אין עמודת סטטוס** — ‏כל שורה נושאת פקודה שמכריעה אותה |
| `scripts/backlog-status.sh` | ‏מריץ את פקודות הסגירה מתוך `BACKLOG.md` ‏וגוזר מצב. ‏הפקודות חיות במסמך בלבד |
| `docs/plans/slice-current-state-section.md` | ‏בריף (‏טיוטה): `§1.5` ‏בתבנית + ‏בדיקה 10 ‏לאביגיל + ‏כלל פריט 31 ‏למרדכי |
| `SKILL.md` · `recommendations.md` · ‏דוח הזיקוק | ‏מפנים ל-`BACKLOG.md` ‏ואינם משכפלים |

**‏עיצוב**: ‏סטטוס שנכתב ביד רוקב (‏פריט 39) — ‏לכן הוא **‏נגזר מהרצה**. ‏כלל כניסה:
‏פריט בלי פקודה שמכריעה אותו אינו נכנס לטבלה.

**‏אימות** (‏לא הצהרה):
- ‏הסקריפט תפס באג של עצמו — `|` ‏בתוך פקודה נחתך ע"י מפריד-העמודות של Markdown. ‏תוקן
  ‏בשני הצדדים (escape `\|` + ‏ניטרול בסקריפט) ‏ותועד ככלל בכותרת המסמך.
- **‏בדיקת-הבחנה**: ‏שתי שורות סינתטיות שאמורות להיסגר החזירו ✅, ‏מול 11 ⬜.
  ‏בלעדיה זה היה מד שתמיד מראה אותו דבר.
- ‏11 ‏פריטים פתוחים, ‏0 ‏שבורות. ‏הוותיק — `blocked/` ‏ב-`dispatch-executor.sh` — ‏מ-30/05.
- ‏מספרים מיושנים ב-`SKILL.md` ‏שנמצאו אגב ותוקנו: `plan-pitfalls` 10→**12**,
  ‏`recommendations` 38→**40**. `patterns` ‏היה נכון.
- ‏טסטים: `test_distill.py` 39/39 · `test_path_substitution.py` 10/10.

**‏חריגות**: ‏הבריף הוא **‏טיוטה שלא אומתה** — ‏לא הורצה אביגיל ולא בוצע. ‏העבודה נעשתה
‏ישירות ב-main session ‏ולא כ-slice: ‏תשתית מעקב, ‏לא שינוי בדוקטרינה עצמה.

---

## 2026-08-03 — 4 ‏קטגוריות חדשות לטקסונומיה (‏סגירת פריט 1 ‏בדוח הזיקוק)

‏דוח הזיקוק זיהה שהקטגוריות שנוספו לקטלוגים **‏אינן** ‏קיימות במקום שקובע מה נמדד.
‏שני מנגנונים נפרדים, ‏ושניהם נדרשו:

| ‏מנגנון | ‏קובץ | ‏שולט על |
|--------|------|---------|
| `CANONICAL_CATEGORIES` | `scripts/distill.py:50` | ‏דגל "‏מועמדת לטקסונומיה" ‏ב-`noncanonical` |
| ‏רשימת `category` ‏בפרומפט | `prompts/{avigail,calev}.md` | **‏מה שהמאמת באמת כותב בדוח** |

‏הפרומפט מורה במפורש "‏אם לא בטוח — `unique`", ‏ולכן שינוי ב-`distill.py` ‏לבדו לא היה
‏מייצר ולו ממצא אחד בקטגוריות החדשות. ‏זה גם ההסבר ל-`unique`=502 (60% ‏מממצאי אביגיל):
‏טקסונומיה שנקבעה ב-2026-06-27 ‏ולא הורחבה, ‏בזמן שהשיטה התפשטה ‏מ-frontend ‏ל-backend/CLI/infra.

**‏מה נוסף**: ‏אביגיל — `unrun-claim`, `intermediate-state-unverified`, `gate-cannot-fail`
(`plan-pitfalls.md` 8–10). ‏כלב — `stale-user-visible-string` (`patterns.md` ‏קטגוריה 7).
‏בכל פרומפט נוספה גם פסקת-הנחיה קצרה, ‏כי slug בלבד אינו אומר למאמת **‏מתי** ‏להשתמש בו.
‏`calev-heavy` ‏אינו מחזיק רשימת קטגוריות משלו — ‏אין מה לעדכן שם.

**‏אימות**:
- `generate-cli-configs.py` → 8 ‏קבצים (‏avigail+calev × ‏agents/ + codex + opencode + qoder).
  ‏הדיף מוגבל לשורות הקטגוריות ולפסקאות החדשות, ‏זהה ב-4 ‏ה-adapters, ‏אפס drift אחר.
- ‏הוכחה תפקודית (‏לא הצהרה): ‏דוח מזויף לכל אחת מ-4 ‏הקטגוריות → ‏`נספר=1`,
  ‏`מסומן-כלא-קנוני=False`. **‏ובדיקת-הבחנה**: ‏קטגוריה מומצאת → `True`.
  ‏בלי הבדיקה השנייה זה היה `gate-cannot-fail` ‏בעצמו.
- `tests/test_distill.py` 39/39 · `tests/test_path_substitution.py` 10/10.

**‏חריגות**: ‏בוצע ישירות ב-main session ‏ולא כ-slice — ‏לפי `SKILL.md` §"‏מתי **‏לא**
‏להשתמש בשיטה" (‏שינוי מתחת ל-50 ‏שורות). ‏השינוי בכתב-יד הוא 4 ‏מחרוזות + 2 ‏פסקאות;
‏השאר מיוצר.

---

## 2026-08-03 — זיקוק: איכותני (‏case-studies של אוגוסט) + כמותי (‏581 ‏דוחות)

**‏זיקוק איכותני** — שלושת המסמכים החדשים (`RAW-2026-08-verification-cost.md` §1–§25,
`2026-07-obsidian-web-r0-nine-rounds.md`, `2026-08-eq-checker-slice5-self-feeding-loop.md`)
זוקקו לדוקטרינה לפי `SKILL.md` §"אם case study חדש מוסיף תובנה":

| ‏קובץ | ‏מה נוסף |
|------|---------|
| `recommendations.md` | ‏פריטים **28–38** — ‏בלוק "‏שיפורים מסשן 2026-08-01/02 (‏עלות האימות)" |
| `plan-pitfalls.md` | ‏קטגוריות **8–10**: `unrun-claim`, `intermediate-state-unverified`, `gate-cannot-fail` |
| `patterns.md` | ‏מטא-תופעה 2 (‏המתקן מייצר את הממצא הבא) + ‏קטגוריה 7 `stale-user-visible-string` + traceability |
| `docs/methodology-evolution.md` | ‏ערך 2026-08-02 + ‏עקרונות 6–7 |
| `SKILL.md` | ‏מפת הקבצים — ‏ספירות מעודכנות + ‏שורת `plan-pitfalls.md` ‏שחסרה |

**‏זיקוק כמותי** — `distill.py --reports-dir main/reports` על 581 ‏דוחות (‏334 ‏אביגיל,
‏247 ‏כלב; ‏285 ‏חדשים מאז snapshot 2026-07-19). ‏תוצרים:
`distillations/2026-08-03-{data.json,report.md}`.

**‏באג שנמצא בהרצה** — `scripts/distill.py:99` ‏השתמש ב-`text.split("---", 2)`, ‏מפריד
לא-מעוגן לתחילת שורה. ‏כל `---` **‏בתוך מחרוזת** ‏ב-front-matter קטע את הבלוק, ‏ה-YAML
נשבר, ‏והדוח נשמט מכל זיקוק **‏בשקט**. ‏נפגע בפועל:
`obsidian-eq-checker/slice-5-page-split-calev-phase1.md` (`verdict: PARTIAL`, 1 blocker
+ 4 minor) — ‏החוסם שם הוא "‏שער הזהב אינו נופל על שתי מוטציות עצמאיות", ‏כלומר **‏המקור
של `recommendations.md` ‏פריט 33**, ‏שמעולם לא נספר.

**‏אימות**: regex ‏מעוגן `^---\n(.*?)\n---`; ‏טסט רגרסיה
`test_md_triple_dash_inside_front_matter_string` **‏הוכח כנופל על הקוד הישן**
(`git stash` ‏על `distill.py` → `AssertionError: unexpectedly None`).
`tests/test_distill.py` 39/39 + `tests/test_path_substitution.py` 10/10 ‏ירוקים.
‏אחרי התיקון: ‏245→**247** ‏דוחות כלב נקראים; ‏5 ‏אזהרות שנותרו הן דוחות בפורמט ישן בלי
front-matter כלל.

**‏תיקון נלווה בסאב-ריפו הפרטי** (`main/reports/`, ‏לא בקומיט הזה):
`pi-acp/pi-acp-bash-output-fix-calev.md` ‏היה חסר `---` ‏סוגר — ‏הפרת `docs/reports-format.md`.

**‏הממצא המרכזי של ההרצה** — ‏התפלגות סבבים פר-brief (‏נגזר מ-`report_ids`):
‏224 ‏בריפים · ‏חציון **1** · **‏81% ‏נסגרים בסבב אחד** · ‏אבל **19 ‏בריפים (8%) ‏צרכו
100 ‏דוחות = 30% ‏ממאמץ האימות**, ‏ושניים הגיעו ל-10 ‏סבבים.

**‏חריגות**: ‏זיקוק ידני ולא דרך ה-systemd timer (‏שמעולם לא הותקן — ‏ראה
`methodology-evolution.md` 2026-06-27). ‏נכתב ישירות על `main` ‏ולא ל-branch ייעודי,
‏בריצה מונחית-משתמש.

---

## 2026-07-19 — slice-qoder-path-neutral: Commit 1 — install_qoder מחווט ל-substitute_into

הוסף `install_qoder()` ל-`scripts/install-cli-configs.sh` — **כמו** `install_codex` (loop על
6 הסוכנים, dst=`${QODER_AGENTS_DIR:-$HOME/.qoder/agents}`) **אבל** קורא ל-`substitute_into`
(ולא `cp` גולמי, בניגוד ל-WIP המקורי בסטאש — זה בדיוק ה-fix ש-Commit 1 נדרש לתקן).
qoder נוסף ל-`case` הראשי (`all` + `qoder`) ול-usage string. `resolve_paths`/`substitute_into`
כבר קיימים (path-neutral, main) — install_qoder רק צורך אותם.

**אימות** (install מזויף עם 4 המשתנים + `QODER_AGENTS_DIR=/tmp/qo`):
`bash scripts/install-cli-configs.sh qoder` → 6 קבצים הותקנו; `grep -rl "{{BDS_" /tmp/qo` ריק
(placeholder הוחלף) ✅; `grep -rq "/tmp/fk-r" /tmp/qo` נמצא (נתיב מוזרק) ✅.
`tests/test_path_substitution.py` (9/9) + `tests/test_distill.py` (38/38) ירוקים (regression).

**חריגות**: אין. [verifier-phase לפי הבריף — calev הורץ אחרי הקומיט הזה, ראה entry הבא]

---

## 2026-07-19 — slice-qoder-path-neutral: Commit 0 — scaffolding + generator

שוחזר ה-scaffolding של qoder (מ-`git stash@{0}`, WIP קדם-path-neutral) — **בלי** קבצי
`cli-configs/qoder/*.md` המוקשחים מהסטאש (אלה יווצרו-מחדש ב-Commit 2 מה-prompts הנוכחיים):

| קובץ | מה |
|------|------|
| `agent-definitions/agents.json` | הוסף מפתח `"qoder"` פר-סוכן (6 סוכנים) — `name`/`model`/`permissionMode`/`effort`/`tools`/`disallowedTools`(/`isolation` ל-eliezer), זהה למבנה שהיה ב-stash |
| `scripts/generate-cli-configs.py` | `render_yaml_list` + `render_qoder_agent()` (YAML frontmatter + tools/disallowedTools כרשימות); `qoder` נוסף ל-`generate()` (כותב ל-`cli-configs/qoder/agents/<agent>.md`) ול-`choices` של ה-CLI |

**אימות**: `python3 scripts/generate-cli-configs.py qoder` → 6 קבצים נוצרו.
`grep -l "{{BDS_" cli-configs/qoder/agents/*.md` → 4 (avigail/calev/calev-heavy/yetro) ✅.
`grep -c "~/projects\|/home/user" cli-configs/qoder/agents/*.md` → 0 בכל 6 ✅.
הרצה חוזרת → "no changes" (idempotent) ✅.
`python3 tests/test_path_substitution.py` (9/9) + `tests/test_distill.py` (38/38) ירוקים.

**חריגות**: אין. `cli-configs/qoder/` שנוצר בהרצת האימות **לא נכנס לקומיט הזה** (untracked) —
הקומיט של הקבצים המיוצרים בפועל הוא Commit 2, לפי §4 בבריף.

---

## 2026-07-19 — slice-path-neutral-agent-configs: Commit 0 — placeholders במקור-האמת

הוחלפו כל 14 הנתיבים-המוקשחים ב-`agent-definitions/prompts/{avigail,calev,calev-heavy,yetro}.md`
ב-4 placeholders, לפי טבלת §0 בבריף:

| נתיב מוקשח (הוסר) | placeholder | מופעים | קבצים |
|-------------------|-------------|--------|-------|
| `~/projects/brief-driven-slices/main/reports` | `{{BDS_REPORTS}}` | 4 | avigail.md (2), calev.md, calev-heavy.md |
| `~/projects/brief-driven-slices/main/scripts` | `{{BDS_SCRIPTS}}` | 3 | yetro.md |
| `~/projects/my-skills/lessons-learned/lessons-index` | `{{BDS_LESSONS}}` | 6 | avigail.md, calev.md, calev-heavy.md (2 כ״א) |
| `~/projects/orchestration/` | `{{BDS_ORCH}}/` | 1 | yetro.md |

**אימות**:
- `grep -rn "~/projects\|/home/user" agent-definitions/prompts/` → ריק ✅
- `grep -roh "{{BDS_[A-Z]*}}" agent-definitions/prompts/ | sort | uniq -c` → 4/3/6/1 (תואם לטבלה) ✅

**חריגות**: אין.

---

## 2026-07-19 — slice-path-neutral-agent-configs: Commit 1 — מנגנון החלפה + כשל-רועש

חוט אחד גנרי (`resolve_paths` + `substitute_into`) ב-`scripts/install-cli-configs.sh`,
מחוּוט לשני ה-installers ה-committed (`install_opencode`, `install_codex` — qoder לא
committed ב-base, מחוץ ל-scope לפי הבלוקר מ-df99501):

- `resolve_paths()` — טוענת `${BDS_PATHS_ENV:-$HOME/.config/bds/paths.env}` לכל משתנה
  שלא הוגדר ישירות ב-env (env גובר על הקובץ), ואז `:?` על כל 4 המשתנים → כשל-רועש.
- `substitute_into(src, dst)` — `sed` שמחליף את 4 ה-placeholders + שכבת-הגנה: אם נשאר
  `{{BDS_` ב-dst אחרי ההחלפה (placeholder לא-מוכר/לא-מוחלף) → `exit 1`.
- `install_opencode`: `ln -sfn` → `substitute_into` (symlink הוחלף ל-copy — symlink לא
  נושא תוכן-מוחלף).
- `install_codex`: ה-`cp` הקיים על agents/*.toml → `substitute_into` (config.toml
  הפרויקטלי, שאין בו placeholders, נשאר `cp` רגיל).
- `main()` + guard `BASH_SOURCE[0]==$0` — כדי לאפשר `source` של הסקריפט מ-unittest בלי
  להריץ install אמיתי.
- נוצר `cli-configs/paths.env.example` (תבנית + הסבר ל-4 המשתנים).
- **חריגה מתועדת**: `cli-configs/{opencode,codex}/agents/*` ו-`agents/*.md` (avigail,
  calev, calev-heavy, yetro) הורצו מחדש דרך `generate-cli-configs.py` — הם היו stale
  מ-Commit 0 (עדיין הכילו את הנתיבים-המוקשחים הישנים, כי Commit 0 נגע רק ב-source
  prompts ולא ב-generated). ההרצה נחוצה כדי ש-DoD#5/#7 יהיו אמיתיים לפני ש-Commit 2
  "מאשר" idempotently. אין שינוי-תוכן מעבר להחלפת placeholder (idempotent
  write_if_changed).

**טסטים**: `tests/test_path_substitution.py` (stdlib unittest, TDD — נכתב RED לפני
המימוש, אומת ל-RED עם 4 כשלונות אמיתיים לפני המימוש) — 7 טסטים: substitute_into (4
placeholders + placeholder לא-מוכר → exit≠0), resolve_paths (כל המשתנים מוגדרים / כל
משתנה חסר בנפרד → exit≠0), install_opencode/install_codex (משתמשים ב-substitute_into
בפועל, נבדק על תיקיות /tmp מזויפות).

**אימות** (unittest + 2 ה-CLIs, `/tmp/oc` + `/tmp/cx`):
- `python3 tests/test_path_substitution.py` → 7/7 ירוק ✅
- `install-cli-configs.sh all` עם env מזויף → `/tmp/oc`, `/tmp/cx` ללא `{{BDS_`, נתיב
  `/tmp/fk-r` מופיע בשניהם ✅
- `env -u BDS_REPORTS install-cli-configs.sh opencode` → `exit=1` עם הודעה ברורה ✅
- `grep -rn "~/projects\|/home/user" agent-definitions/prompts/` → ריק (עדיין) ✅

**חריגות**: regenerate של cli-configs/agents (ראה לעיל) — לא היה ברשימת "קבצים
שמשתנים" המקורית של Commit 1 בבריף, אבל נחוץ למימוש נכון של DoD#5/#7 (ראו §5 בבריף).

### תיקון אחרי calev (verifier-phase, verdict GO, 2 findings minor)

כלב מצא 2 בעיות-קצה ב-`substitute_into`: (1) ערך BDS_* המכיל `&` מתפרש ע"י sed
כ-backreference ("כל ההתאמה") ומחדיר בחזרה `{{BDS_...}}` לתוך התוכן, מה שמפעיל
את שכבת-ההגנה בטעות (הודעה לא-מדויקת); (2) ערך המכיל `|` (ה-delimiter שנבחר ל-sed)
שובר את הפקודה בשגיאת syntax גולמית. שתי הבעיות "minor" (נתיבי-מכונה אמיתיים כמעט
לעולם לא מכילים תווים אלה) אבל תוקנו באותו phase לפי הפרוטוקול (1-2 findings → תיקון).

**תיקון**: נוספה `_sed_escape()` — בורחת `\`, `&`, `|` בערך לפני הזרקתו ל-`sed`
replacement. 2 טסטים חדשים (RED מאומת לפני התיקון, GREEN אחרי) ב-
`tests/test_path_substitution.py`: `test_replacement_value_containing_ampersand`,
`test_replacement_value_containing_pipe`. סה"כ 9/9 טסטים ירוקים.

---

## 2026-07-19 — slice-path-neutral-agent-configs: Commit 2 — דוקטרינה + סקריפטים

עדכון "רשימה סגורה" (per §4 בבריף — לא נגעו ב-docs/plans או docs היסטוריים, מחוץ ל-scope):

- **`SKILL.md`**: (1) פקודות ההתקנה (שורות ~50) — הוחלפו נתיבים-מוקשחים ב-נתיב יחסי
  משורש-הריפו + הפניה ל-`cli-configs/paths.env.example`. (2) §"הסוכנים" (שורות ~154) —
  תוקן תיאור מיושן ("OpenCode מקבל symlinks") ל-**עותקים** אחרי path-substitution
  (עקבי עם Commit 1: symlink הוחלף ל-copy כי symlink לא נושא תוכן-מוחלף) + תיאור מפורש
  של עקרון ה-path-neutral (4 ה-placeholders, כשל-רועש).
- **`orchestration.md`**: (1) טבלת §8 — תוקן אותו תיאור-symlinks מיושן.
  (2) §9 "התקנה ראשונה" — כל 3 הנתיבים-המוקשחים (`~/projects/brief-driven-slices/main/...`,
  `~/projects/orchestration/`) הוחלפו בקונבנציית `<bds>` (כבר קיימת ב-`docs/reports-format.md`)
  + צעד מפורש ליצירת `paths.env` פר-מכונה.
- **`orchestration-project/AGENTS.md`**: 2 הנתיבים-המוקשחים (`~/projects/brief-driven-slices/main/...`)
  הוחלפו ב-`<bds>` + הערה שהנתיב הקונקרטי חי ב-`paths.env`, לא במקור-האמת של ה-template.
  (זהו template שמשתמש מעתיק פר-מכונה — ה-`{{BDS_*}}` placeholders לא רלוונטיים כאן כי
  substitute_into לא מחווט אליו; `<bds>` הוא convention תיעודי בלבד.)
- **`docs/reports-format.md`**: לא נמצאו נתיבים-מוקשחים (כבר משתמש ב-`<bds>/main/reports/`
  יחסי) — נוספה הערה מקשרת בין הקונבנציה היחסית כאן ל-`{{BDS_REPORTS}}` (אותה תיקייה,
  שני אזכורים — יחסי ב-checkout מול placeholder בפרומפט של הסוכנים).
- **`scripts/distill.py`**: `--reports-dir` ברירת-מחדל → `os.environ.get("BDS_REPORTS", "reports/")`
  (env גובר, אחרת ההתנהגות הקיימת). נוסף `import os`.
- **`scripts/extract_sessions.py`**: `--reports-dir` ברירת-מחדל →
  `os.environ.get("BDS_REPORTS", "main/reports")` (`os` כבר מיובא).
- **לא נגעו**: `mordechai.md`/`eliezer.md` (אביגיל אימתה נקיים — relative בלבד), `docs/plans/`,
  `walkthrough.md`/`methodology-evolution.md` היסטוריים (מחוץ ל-scope לפי finding אביגיל #3).

**אימות**:
- `grep -n "~/projects\|/home/user" SKILL.md docs/reports-format.md orchestration.md orchestration-project/AGENTS.md scripts/distill.py scripts/extract_sessions.py` → ריק ✅
- `python3 scripts/generate-cli-configs.py all` → `generated: no changes` (idempotent, cli-configs נשארו ניטרליים) ✅
- `grep -rl "{{BDS_" cli-configs/ agents/ | wc -l` → 13 (12 קבצי-סוכנים + `paths.env.example` שמזכיר את השמות בהערת-תיעוד) ✅
- `python3 tests/test_distill.py` → 38/38 ירוק (regression, לא נשבר ע"י שינוי ברירת-המחדל) ✅
- `python3 tests/test_path_substitution.py` → 9/9 ירוק ✅

**חריגות**: אין.

---

## 2026-06-08 15:04 — סימון בריפים מול תוכניות טרום-בריף

נוספה הגנה מתודולוגית שמבהירה לסוכנים האם מסמך הוא בריף dispatchable או תוכנית טרום-בריף.

#### מה בוצע?

**1. תוכנית טרום-בריף**

- נוסף `docs/plans/pre-brief-plan-briefs-vs-plans-separation.md` כתוכנית מפורטת להפרדה עתידית בין `plans` לבין `briefs`.
- המסמך מסומן במפורש כלא-בריף: אין להריץ מול אליעזר, אין לפתוח ממנו worktree, ואין לסמן אותו `plan_verified`.

**2. תבנית בריף ואליעזר**

- `briefs/BRIEF_TEMPLATE.md` עכשיו מציין `סוג מסמך: בריף ביצועי לסלייס` ו-`אימות אביגיל: לא מאומת / READY`.
- אליעזר עודכן לעצור כ-BLOCKED אם המסמך שקיבל אינו בריף ביצועי או אם אימות אביגיל אינו READY.
- קבצי ה-adapter של אליעזר סונכרנו ל-OpenCode ול-Codex.

**אימות**: `python3 tests/test_distill.py` עבר בהצלחה — 38/38.
**חריגות**: אין. קבצי `orchestration-project/projects.json` ו-`orchestration-project/runs/2026-06-03.summary.md` קיימים כ-untracked ולא נכללו בשינוי.

---

## 2026-06-05 — תאימות Codex + שכבת CLI adapters

נוספה שכבת תאימות ל-CLI מרובים בלי לשבור את OpenCode:

| קובץ | מה |
|------|----|
| `AGENTS.md` | הנחיות פרויקט כלליות לסוכני קוד + מיפוי roles |
| `agent-definitions/agents.json` | מקור אמת למטא-דאטה של הסוכנים לפי CLI |
| `agent-definitions/prompts/*.md` | מקור אמת לגופי הפרומפטים הארוכים |
| `scripts/generate-cli-configs.py` | גנרטור stdlib-only ל-Codex/OpenCode |
| `cli-configs/` | תוצרי adapters לפי CLI |
| `cli-configs/codex/agents/*.toml` | custom agents generated ל-Codex עבור mordechai/yetro/eliezer/avigail/calev/calev-heavy |
| `cli-configs/opencode/agents/*.md` | agents generated ל-OpenCode |
| `cli-configs/codex/config.toml` | defaults ל-subagents של Codex |
| `scripts/install-cli-configs.sh` | generation + התקנה ל-OpenCode/Codex/all |
| `scripts/install-agents.sh` | wrapper תאימות אחורה ל-OpenCode |
| `README.md`, `SKILL.md`, `docs/decisions/bds.md` | תיעוד מקור האמת, generated outputs, והרציונל |

**אימות**: JSON נטען ✅; TOML נטען עם `tomllib` ✅; `bash -n` לשני סקריפטי ההתקנה ✅; התקנת ניסיון לתיקיות זמניות ✅; generator idempotent ✅.
**חריגות**: `.localappdata/` ו-`.specstory/` קיימות כ-untracked מלפני השינוי ולא נגעו בהן.

---

## 2026-06-01 — slice-3-report-discipline: Commit 3 — תיעוד חוזה + סגירה

תיעוד החוזה בקבצי ה-reference + עדכון brief לסטטוס "הושלם":

| קובץ | מה |
|------|------|
| `docs/reports-format.md` | §חדש "חוזה ה-Task-result (משמעת-דוחות)": שני פורמטים (avigail/calev), כלל הברזל, הפניות |
| `workflow.md` | §חדש "חוזה ה-Task-result — אינדקס בלבד": diagram + כלל + הפניה ל-reports-format |
| `docs/decisions/bds.md` | entry חדש: הבעיה שנסגרה (slice-2), ההחלטה, הרציונל לקביעות, יישום |
| `docs/plans/slice-3-report-discipline.md` | סטטוס → הושלם |

**slice-3-report-discipline סוכם**: 4 commits, 9 קבצים עודכנו, חוזה מנוסח, עקבי, צרכנים מצפים.
**אימות manual**: grep ✅ × 12 DoD items (לפני calev light).
**חריגות**: אין סטיות מהbrief.

---

## 2026-06-01 — slice-3-report-discipline: Commit 2 — הצרכנים מצפים לחוזה (mordechai + eliezer)

עדכון `agents/mordechai.md` ו-`agents/eliezer.md` לחוזה החדש:
- mordechai §"הפעל אביגיל": הערה "מה אביגיל מחזירה = תמצית-אינדקס, פתח את הדוח לתיקון".
- mordechai §runtime-gate: "לפני merge — פתח את דוח כלב המלא".
- mordechai anti-pattern: "להחליט על finding מכותרת בלבד = אינדקס לא תחליף".
- eliezer §"מה לעשות עם calev": "פתח reports/.../calev.md לפני תיקון, לא מהכותרת".
- eliezer §"Feedback loop": הוסף path לדוח כלב בדיווח למרדכי.

**אימות manual**: grep ✅ × 4 (פתח+אינדקס, runtime-gate, תמצית+פתח, אינדקס).
**חריגות**: אין.

---

## 2026-06-01 — slice-3-report-discipline: Commit 1 — חוזה result אצל calev + calev-heavy

הרחבת חוזה ה-Task-result ל-`agents/calev.md` ו-`agents/calev-heavy.md`:
- §"מה אתה לא עושה": anti-pattern "לא לכתוב ניתוח ב-Task-result".
- §"פורמט דוח" בכל 3 modes (phase/light/heavy): משפט "הדוח מפורט — הערוץ היחיד לניתוח".
- §חדש "מה אתה מחזיר ב-Task-result": אינדקס קבוע (verdict+report+mode+DoD+findings+כותרות בלבד).
- Anti-pattern בסוף: "result = אינדקס, דוח = בשר".
- calev-heavy: הפניה מפורשת לחוזה.

**עקביות avigail/calev**: שניהם ≥1 "כותרות בלבד" ✅. מבנה זהה, הבדלים לגיטימיים: verdicts, DoD, mode.
**אימות manual**: grep ✅ × 4.
**חריגות**: אין.

---

## 2026-06-01 — slice-3-report-discipline: Commit 0 — חוזה result + חובת-דוח אצל avigail

הוספת חוזה ה-Task-result ל-`agents/avigail.md`:
- משפט חובה בראש §"פורמט הדוח": "הדוח חייב להיות מפורט ומלא — הערוץ היחיד לניתוח."
- §חדש "מה אתה מחזיר ב-Task-result": אינדקס קבוע (verdict+report+findings+כותרות בלבד).
- Anti-pattern חדש: "result-שמן = תקלה".

**אימות manual**: grep ✅ × 4 (חייב-מפורט, אינדקס-קבוע, כותרות-בלבד, תקלה).
**חריגות**: אין.

---

## 2026-06-01 — slice-2-distillation: תיקון post-calev — date.date normalization

כלב מצא bug minor: `parse_report_file` ניר datetime.datetime אבל לא datetime.date.
YAML מפרסר "2026-05-01" (date-only) כ-date object — לא datetime.

תיקון: `from datetime import date as date_type, datetime` + elif לnormalization.
טסט חדש (38 ✅): `test_md_date_as_date_object_normalized`.

**חריגות**: אין.

---

## 2026-06-01 — slice-2-distillation: Commit 6 — e2e + תיעוד סגירה

commit סגירה — manual e2e + תיעוד 4+5 ב-decisions + עדכון SKILL.md/workflow.md + סטטוס brief.

| בדיקה | תוצאה |
|-------|-------|
| distill.py על fixtures (.md + .json) | ✅ 3 avigail + 2 calev, שני פורמטים נטענו |
| distill.py על reports אמיתי (18 דוחות) | ✅ לא קרס, noncanonical מסומן, ספירה הגיונית |
| distill-run.sh threshold=0 כמותי (ללא opencode) | ✅ data.json נוצר, main לא נגע |
| 3 קטלוגים/יומן קיימים | ✅ plan-pitfalls.md, methodology-evolution.md, TEMPLATE-report.md |
| פורמט חדש מתועד | ✅ grep front-matter reports-format.md |

| קובץ | מה |
|------|------|
| `SKILL.md` | שכבת הזיקוק + שני gates (סעיפים חדשים) + רשומות agent |
| `docs/decisions/bds.md` | entry חדש: זיקוק + פורמט MD-front-matter + שני gates (רציונל) |
| `docs/plans/slice-2-distillation.md` | סטטוס → הושלם |

**חריגות**:
- systemd-analyze לא זמין בcontainer — קריאה ידנית (תקין, תועד)
- distill-run.sh step 4 (opencode) — לא הורץ (יקר, לא נדרש ב-e2e)
- reports/README.md עודכן ב-sub-repo ישירות (לא tracked ב-git השיטה)

---

## 2026-06-01 — slice-2-distillation: Commit 5 — שני gates: plan-gate + runtime-gate

ניסוח כללי-שיטה שעד כה לא היו מנוסחים מפורשות:

| קובץ | מה |
|------|------|
| `agents/mordechai.md` | §"שני gates" חדש: plan-gate (READY בלבד) + runtime-gate (GO/דחייה-מתועדת) + 2 anti-patterns חדשים |
| `agents/eliezer.md` | §"הכרז במפורש": חידוד — ציין verdict כלב **GO/PARTIAL/NO-GO** מפורש (runtime-gate) |
| `agents/yetro.md` | הערה: status==plan-verified מניח READY (plan-gate — חוזה קיים, לא לוגיקה חדשה) |
| `workflow.md` | §"שני gates" חדש בין שלב 6 ל-7 |

**אימות manual**: grep "plan-gate|READY" + "runtime-gate|GO" + "USABLE-AFTER-FIX" mordechai.md ✅.
grep "gate|אימות-נקי" workflow.md ✅. Forward-ref "plan-gate למטה" שורה 59 — נסגר ✅.
**חריגות**: אין. Gates = ניסוח כללים קיימים, לא לוגיקה חדשה.

---

## 2026-06-01 — slice-2-distillation: Commit 4 — פורמט דוח MD-front-matter

עדכון פורמט דוחות-אימות מ-JSON ל-MD עם YAML front-matter (מקור-אמת יחיד):

| קובץ | מה |
|------|------|
| `agents/avigail.md` | §"כתיבת דוח JSON" → §"כתיבת דוח MD עם front-matter" + הוראת ציטוט (double-quote ל-`:'\|`) |
| `agents/calev.md` | אותו דבר + אחוד עם docs/<slice>-verification-report.md |
| `agents/calev-heavy.md` | שלב 7: הפניה לפורמט החדש ב-calev.md |
| `docs/reports-format.md` | שכתוב: front-matter schema + ⚠️ הוראת ציטוט + backward-compat + טבלת שדות |
| `reports/README.md` (sub-repo) | עדכון נתיב `.json` → `.md` + הערת dual-format |

**אימות manual**: grep "front-matter" docs/reports-format.md ✅.
grep "double-quote|לצטט" agents/avigail.md ✅. grep "reports/.*\.md" agents/*.md ✅.
round-trip distill.py על fixtures.md: 3/3 avigail ✅.
**חריגות**: reports/README.md עודכן ישירות ב-main/reports/ (sub-repo פרטי, לא ב-git השיטה).

---

## 2026-06-01 — slice-2-distillation: Commit 3 — systemd timer + distill-run.sh + distill-prompt.txt

נוספו קבצי ה-wrapper + systemd לטיימר הזיקוק היומי:

| קובץ | מה |
|------|------|
| `scripts/distill-run.sh` | wrapper: טריגר כמותי → distill.py → worktree branch → מרדכי-אוטומטי |
| `scripts/distill-prompt.txt` | פרומפט למרדכי-אוטומטי (כולל "אסור לעשות merge") |
| `systemd/bds-distill.service` | Type=oneshot, ExecStart=$HOME/scripts/distill-run.sh |
| `systemd/bds-distill.timer` | OnCalendar=daily, Persistent=true |
| `systemd/README.md` | הוראות התקנה, שינוי סף, בדיקה ידנית, לוגים |

**אימות manual**: `bash -n scripts/distill-run.sh` ✅.
grep "אסור לעשות merge" scripts/distill-prompt.txt ✅. grep OnCalendar systemd/bds-distill.timer ✅.
systemd-analyze verify — לא זמין בסביבה (קובץ נקרא ידנית, syntax תקין).
**חריגות**: systemd-analyze לא זמין בcontainer — קריאה ידנית של ה-unit (תקין).

---

## 2026-06-01 — slice-2-distillation: Commit 2 — יומן גלובלי אבולוציית השיטה

נוסף `docs/methodology-evolution.md` — יומן גלובלי נדיר של התפתחות השיטה.
5 אירועים: יצירת הצוות (5 סוכנים + רציונל השמות + מה לא עבד), המעבר לפרויקט עצמאי,
פיצול calev→calev-heavy, שכבת הזיקוק (Commit הנוכחי, כולל פורמט+gates). + 5 עקרונות.

**אימות manual**: `test -f docs/methodology-evolution.md` ✅. grep "merge|זיקוק|calev-heavy" ✅.
**חריגות**: אין.

---

## 2026-06-01 — slice-2-distillation: Commit 1 — פורמט דוח-זיקוק + קטלוגים + traceability

נוספו קטלוגים ותבניות לשכבת הזיקוק:

| קובץ | מה |
|------|------|
| `distillations/README.md` | הסבר שכבת הזיקוק, מבנה, טריגר, חלוקה כמותי/איכותני |
| `distillations/.gitkeep` | שמירת תיקייה ב-git |
| `distillations/TEMPLATE-report.md` | תבנית 4-חלקים לדוח זיקוק (מבט-לאחור, התפלגות, חדשות, עדכוני-קטלוג) |
| `plan-pitfalls.md` | קטלוג טעויות-תכנון (אביגיל) — 2 קטגוריות + traceability מקורות |
| `patterns.md` (עדכון) | שורה 2: "+ זיקוק אוטומטי מ-reports/"; סעיף Traceability בסוף |

**אימות manual**: `test -f plan-pitfalls.md && test -f distillations/TEMPLATE-report.md` ✅.
grep "הנחה לא-מאומתת" plan-pitfalls.md ✅. grep "מקורות" patterns.md ✅.
**חריגות**: אין.

---

## 2026-06-01 — slice-2-distillation: Commit 0 — distill.py מנוע כמותי + tests

בוצע TDD (red→green). הוקמה תשתית הזיקוק הכמותי: `scripts/distill.py`,
`tests/test_distill.py` (37 טסטים), `tests/fixtures/sample-reports/` (4 fixtures md + 1 json).

| קובץ | מה |
|------|------|
| `scripts/distill.py` | מנוע כמותי: parse_report_file (dual-format .md/.json), load_reports (סלחני), count_by_severity_category, compute_hitrate, traceability_index, flag_noncanonical, compute_delta, count_new_reports_since, build_data, main (CLI) |
| `tests/test_distill.py` | 37 unittest: כל פונקציה, כולל: dual-format, date normalization, summary-עם-נקודתיים, סלחנות (None ב-broken yaml/json/no-fm), threshold trigger |
| `tests/fixtures/sample-reports/projA/*.md` | 2 fixtures md בפורמט חדש (YAML front-matter) |
| `tests/fixtures/sample-reports/projA/slice-3-calev.json` | 1 fixture json פורמט ישן (backward-compat) |
| `tests/fixtures/sample-reports/projB/*.md` | 2 fixtures md (avigail + calev עם mode/dod_items) |

**אימות**: `python3 tests/test_distill.py` → 37/37 ✅.
`distill.py --check-only --threshold 999` → exit 1 ✅; `--threshold 0` → exit 0 ✅.
`git check-ignore tests/fixtures/sample-reports/...` → ריק ✅ (לא נתפס ע"י gitignore).
**חריגות**: אין.

---

## 2026-05-29 — ‏בניית מערכת האורקסטרציה (commits 03b1a6d→1f9308c, ‏ב-my-skills)

‏אליעזר בנה את התשתית הראשונית של מערכת ה-5 ‏סוכנים, ‏לפי `orchestration-design.md`
‏(שעבר 4 ‏סבבי אביגיל). 6 ‏commits:

| Commit | ‏מה | ‏קבצים |
|--------|------|--------|
| `03b1a6d` | Commit 0 — scripts | dispatch-executor.sh, wait-for-slice.sh, install-agents.sh, cleanup_state.py, discard_chain.py |
| `265f429` | Commit 1 — 5 ‏סוכנים | agents/{mordechai,yetro,eliezer,avigail,calev}.md |
| `2f38d53` | Commit 2 — state + orchestration | state.template.json, orchestration.md |
| `755bdc2` | Commit 3 — בית יתרו | orchestration-project/ template |
| `f6bf30f` | Commit 4 — SKILL + briefs | SKILL.md, BRIEF_TEMPLATE, EXECUTOR_DISPATCH, ‏מחיקת סוכנים ישנים |
| `1f9308c` | Commit 5 — README + walkthrough | README, docs/walkthrough |

‏אימות: GO, 16/16 DoD (דוח ב-`/tmp/orchestration-verification-report.md`).

**‏מאפיינים מרכזיים שנבנו**: env scrub מלא (prefix OPENCODE_*), ‏prompt דרך stdin,
‏BLOCKED דרך קיום-קובץ (לא exit code), ‏JSON state + python3 stdlib, ‏שרשור worktrees,
‏flock נגד שני יתרו, ‏discard_chain (dependents בלבד), ‏4 ‏מצבי טיפול-כשל.

---

## 2026-05-30 — slice bds-extraction: ‏הוצאה לפרויקט נפרד + ‏שכבת דיווח

‏העברת brief-driven-slices מ-`~/projects/my-skills/` ‏לפרויקט עצמאי
‏`~/projects/brief-driven-slices/` ‏עם git משלו, + ‏שכבת דיווח-בקבצים + ‏2 ‏יומנים.
‏Mode 3 ‏(ידני, ‏לא דרך יתרו). brief עבר 2 ‏סבבי אביגיל (5+1 ‏ממצאים, ‏כולם תוקנו).

| Commit | ‏מה |
|--------|------|
| `32ea702` | Commit A — ‏העברה: ‏git init חדש, ‏עדכון 12 ‏נתיבי my-skills, symlinks (skill + 5 agents) למיקום חדש |
| `50fbce4` | Commit B — outcomes: ‏אליעזר כותב `outcomes/<slice>.json` ‏תמיד (אופציה A); ‏יתרו בודק אותו ראשון; discard_chain.py blocked→outcomes |
| `07f43dd` | Commit C — דוחות מתויגים: avigail write:true + JSON ל-`reports/<project>/`; calev JSON בנוסף ל-MD; ‏טקסונומיה severity/category |
| `ea7aa38` | Commit D — ‏הפרדת יומנים: walkthrough=ביצוע (אליעזר), decisions/<project>.md=רציונל (מרדכי) |
| `c6513b8` | Commit E — ‏תיעוד 2 ‏סטיות (SOUL.md, ‏סוכנים ישנים) ב-decisions/bds.md |

**‏חריגות/הערות**:
- ‏מחיקת התיקייה הישנה ב-my-skills (`git rm`) — ‏הצעד האחרון, ‏commit נפרד ב-my-skills, ‏רק אחרי grep נקי.
- ‏calev tier: heavy (complexity 8) — ‏smoke של opencode run + ‏בדיקת symlinks + grep נקי.
- ‏מה שלא נכנס (brief שני, ‏עתידי): ‏קטלוגים תמציתיים, ‏זיקוק תקופתי, ‏טקסונומיה מתפתחת, ‏יומן גלובלי.
