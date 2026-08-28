# Claude Code — agent definitions

מקור-האמת להגדרות הסוכנים בפורמט **Claude Code** (frontmatter `model:` + `tools:`).
מותקנות ב-`~/.claude/agents/`, שאינה תיקייה מנוהלת ב-git.

התוכן זהה במהות ל-`agents/` (פורמט opencode) — **רק ה-frontmatter שונה**.
הקבצים כאן **נגזרים**: `python3 scripts/generate-cli-configs.py claude-code`
(דרך `oc2cc.convert` על פלט OpenCode). שינוי מהותי בהנחיות נכנס ל-
`agent-definitions/prompts/`, לא לכאן.

## התקנה על מכונה חדשה

```bash
bash scripts/install-cli-configs.sh claude-code
```

המתקין ממיר placeholders (`{{BDS_*}}`) לנתיבים של המכונה דרך `substitute_into`.
אל תעתיקו גולמית — העתקה משאירה placeholders או נתיב של מכונה אחרת.

## ⚠️ למה הקבצים האלה כאן

2026-07-26: התגלה שארבע ההגדרות (`avigail`, `calev`, `calev-heavy`, `yetro`) הפנו
ל-`~/projects/` ב-**אות קטנה** — 11 מופעים. `~/Projects` ו-`~/projects` הן שתי ספריות
שונות במכונה רגישת-רישיות, וזה פיזר **91 דוחות אימות** לנתיב שגוי, גרם לשתי ריצות
`calev-heavy` מקבילות שלא ידעו זו על זו, ולסוכנת שקראה דוח מסבב שגוי.

התיקון בוצע ב-`~/.claude/agents/`, שאינו מגובה — ולכן היה נעלם במעבר בין מכונות.
העותקים כאן קיימים כדי שזה לא יקרה שוב.

**הערה**: `~/Projects/my-skills/lessons-learned/lessons-index` שמוזכר בהגדרות
**אינו קיים** בשום נתיב. יכולת מתה, לא קשורה לרישיות. פתוח.
