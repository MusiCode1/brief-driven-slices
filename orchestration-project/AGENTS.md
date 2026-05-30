# ‏הנחיות לסוכנים — פרויקט האורקסטרציה

‏זוהי תיקיית הבית של **‏יתרו** (orchestrator). ‏כל session שנפתח מכאן עם `agent=yetro` ‏מריץ את ה-queue הלילי.

## ‏ל-יתרו

‏ה-projects.json בתיקייה הזו מגדיר אילו פרויקטים לעבד. ‏לכל פרויקט `active: true`:

1. ‏הרץ `python3 ~/projects/brief-driven-slices/main/scripts/cleanup_state.py <project>`
2. ‏קרא `~/.local/state/brief-driven-slices/<project>/state.json`
3. ‏פעל לפי הלולאה ב-`~/projects/brief-driven-slices/main/agents/yetro.md`

‏סיכומי ריצה נכתבים ל-`runs/<date>.summary.md` ‏בתיקייה זו.

## ‏ל-מרדכי (‏בבוקר)

‏קרא את `runs/<date>.summary.md` ‏לסיכום הלילה.
‏merges מתבצעים **‏בפרויקטים עצמם**, ‏לא מכאן.

## ‏כלים זמינים

- `tmux` — ‏לניהול sessions
- `python3` — ‏לפרסור state.json (stdlib json בלבד)
- `bash` — ‏לסקריפטים
- `git` — ‏לworktrees
- `flock` — ‏נגד שני יתרו

## ‏נתיב הסקריפטים

```
~/projects/brief-driven-slices/main/scripts/
```
