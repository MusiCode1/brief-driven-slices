# Cross-platform agent tooling — מה נבדק ומה נבחר

המתודולוגיה תומכת בשתי פלטפורמות: **OpenCode** (המקורית) ו-**Claude Code**. מסמך זה
מתעד את הכלים החיצוניים שנבחנו להמרה בין הפלטפורמות, ומדוע בחרנו מחולל-עצמי.

## ההכרעה: מחולל זעיר משלנו (`scripts/oc2cc.py`)

מקור-האמת הוא `agents/<name>.md` בפורמט **OpenCode**. קבצי Claude Code **נוצרים** ממנו
על-ידי `oc2cc.py`. הגוף (הוראות ה-Markdown) זהה בייט-לבייט; רק ה-frontmatter מומר.

**מדוע לא ספרייה חיצונית:** ההמרה היא ~3 טרנספורמציות (ראו טבלה למטה) — קוד שאנו
שולטים בו לחלוטין, ללא תלות, ללא coupling ל-API חיצוני לא-יציב.

### טבלת ההמרה (OpenCode → Claude Code)
| frontmatter | OpenCode | Claude Code |
|-------------|----------|-------------|
| `model` | `anthropic/claude-opus-4-8` | `opus` (תחילית `anthropic/` מוסרת, alias ממופה) |
| `tools` | מפה של בוליאנים (`read: true`) | מחרוזת (`Read, Glob, ...`) |
| `mode`, `permission:` | קיימים | מושמטים (CC מנהל הרשאות ב-settings.json / `--permission-mode`) |
| `name`, `description`, **גוף** | — | מועתקים כפי שהם |

### הבדל ארכיטקטוני: אין "primary agent" ב-Claude Code
ב-OpenCode מפעילים session **בתור** agent (`opencode run --agent X`). ב-CC כל ה-custom
agents הם sub-agents (דרך כלי Task) ואין דגל שמאתחל את ה-main loop כ-agent בעל-שם.
לכן מרדכי/יתרו ב-headless רצים עם `claude -p --append-system-prompt "$(oc2cc.py … --body-only)"`,
ומרדכי האינטראקטיבי נשען על ה-Skill הנטען ב-session רגיל. ראו `scripts/dispatch-executor.sh`
ו-`scripts/distill-run.sh` (בורר `BDS_RUNNER=opencode|claude`).

## כלים חיצוניים שנבחנו (לעיון עתידי)

- **[wshobson/agents](https://github.com/wshobson/agents)** — marketplace רב-הארנס
  (Claude Code / OpenCode / Codex / Cursor / Gemini / Copilot) עם מקור-אמת יחיד בפורמט
  Claude Code ומחולל Python (`tools/generate.py`, `tools/adapters/*.py`).
  **לא אומץ:** לא ארוז כ-package (אין pip/npm), `generate.py` קושח `PLUGINS_DIR`,
  ה-API הפנימי אינו חוזה יציב, ו-over-engineering ל-6 agents.
  *רלוונטי אם בעתיד נרצה גם Codex/Cursor/Gemini:* הפורמט הקנוני שלהם הוא Claude Code,
  כך שהפיכת מקור-האמת שלנו ל-CC תפתח את הדלת ל-adapters שלהם.
- **[converting-claude-subagents](https://claude-plugins.dev/skills/@edheltzel/dotfiles/converting-claude-subagents)**
  — skill שממיר Claude Code → OpenCode (חד-כיווני; הכיוון ההפוך לצורך שלנו).
- **[RichardHightower gist](https://gist.github.com/RichardHightower/827c4b655f894a1dd2d14b15be6a33c0)**
  — מדריך ידני להמרה CC↔OpenCode עם טבלת מיפוי.
