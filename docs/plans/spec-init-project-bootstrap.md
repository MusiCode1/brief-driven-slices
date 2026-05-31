# ‏מפרט לצירוף לסלייס הבא — bootstrap של פרויקט חדש (מבנה bare+worktrees)

> ‏מיועד לסוכן שמכין את ה-slice הבא של brief-driven-slices.
> ‏זה **‏לא** ‏brief מלא — ‏זה תיאור פער + ‏דרישות, ‏לשילוב ב-brief קיים.

## ‏הפער

‏השיטה (`worktrees.md`) ‏**‏מתעדת** ‏את מבנה ה-bare+worktrees (`.bare/` + `main/` +
‏`.worktrees/` + `.gitignore`) ‏כמבנה מומלץ, ‏ו**‏מתעדת** ‏איך יוצרים worktree של
‏slice בודד (`git worktree add`). ‏אבל **‏אין שום מקום בשיטה שמתאר/מאוטמט את
‏ה-bootstrap הראשוני** — ‏הקמת המבנה כשמתחילים פרויקט חדש מאפס.

‏כרגע מי שמקים פרויקט חדש חייב לבצע ידנית ~6 ‏צעדים לא-טריוויאליים (הומר
‏repo רגיל → bare, ‏יצירת worktree ראשי, ‏gitignore). ‏זה נעשה בפועל פעם אחת
‏(ב-bootstrap של brief-driven-slices עצמו) ‏ידנית ע"י מרדכי — ‏מתועד כסטייה
‏ב-`docs/decisions/bds.md`. ‏אין כלי, ‏אין checklist. ‏זה הפער.

> ‏הערה: ‏המבנה עצמו נשאר **‏המלצה, ‏לא חובה** (worktrees.md אומר "מומלץ" +
‏"אלטרנטיבה: worktree רגיל עובד גם"). ‏ה-bootstrap צריך לתמוך גם באופציה
‏הרגילה, ‏לא רק bare.

## ‏הדרישה: ‏סקריפט `scripts/init-project.sh`

‏סקריפט bash שמקים פרויקט חדש במבנה bare+worktrees בפקודה אחת.

### ‏שימוש מוצע
```bash
init-project.sh <project-name> [--main-only | --dev-main] [--existing <git-url>]
```

### ‏מה הוא עושה (‏מבנה bare, ‏main בלבד — ‏ברירת מחדל מומלצת)

‏לפרויקט **‏חדש מאפס**:
```
<project>/
├── .bare/          ← git init --bare (או git clone --bare אם --existing)
├── .git            ← קובץ: "gitdir: ./.bare"
├── .gitignore      ← מחריג .worktrees (+ .codenomad/.playwright-cli אם רלוונטי)
├── .worktrees/     ← ריק (לסליסים)
└── main/           ← git worktree add main main
```

‏הצעדים (מבוססים על מה שנעשה ידנית ב-bds — ‏אומתו עובדים):
1. ‏`mkdir <project> && cd <project>`
2. ‏`git init --bare .bare` ‏(או `git clone --bare <url> .bare` ‏ל-`--existing`)
3. ‏`echo "gitdir: ./.bare" > .git`
4. ‏ליצור branch `main` ‏אם חדש (commit ריק ראשוני, ‏או מ-clone)
5. ‏`git --git-dir=.bare worktree add main main`
6. ‏ליצור `main/.gitignore` ‏עם `.worktrees` ‏(+ commit אותו)
7. ‏`mkdir .worktrees`

### ‏אופציות
- ‏`--main-only` (ברירת מחדל) — ‏רק `main/`. ‏מתאים לפרויקט-תשתית / ‏סקיל.
- ‏`--dev-main` — ‏גם `dev/` ‏וגם `main/` (כמו voice-acp: ‏dev=פיתוח, main=יציב).
- ‏`--existing <url>` — ‏clone של repo קיים למבנה bare (במקום init מאפס).

## ‏מלכודות מאומתות (‏מהניסיון הידני — ‏חובה לטפל בהן)

1. **‏`gh repo create --source=.` ‏נכשל מ-worktree** — ‏ה-`.git` ‏הוא pointer, ‏לא
   ‏directory. ‏אם הסקריפט גם דוחף ל-GitHub: ‏`gh repo create` ‏בלי `--source`,
   ‏אז `git remote add` + `git push` ‏ידני. ‏(מתועד ב-memory global.)
2. **‏core.worktree שריד** — ‏בהמרת repo קיים ל-bare, ‏ה-config עלול לשמור
   ‏`core.worktree` ‏→ ‏warning "core.bare and core.worktree do not make sense".
   ‏צריך `git config --unset core.worktree`. ‏(ל-init מאפס לא קורה.)
3. **‏nested repos ב-gitignore** — ‏אם הפרויקט מכיל reports/ ‏או תת-repo אחר,
   ‏ה-`.gitignore` ‏של main צריך להחריג אותו (אביגיל אישרה: ‏nested-in-worktree
   ‏בטוח כשהחיצוני מתעלם).

## ‏בנוסף — ‏checklist ב-worktrees.md

‏גם אם לא בונים סקריפט מלא, ‏worktrees.md צריך סעיף **‏"הקמת פרויקט חדש"** ‏עם
‏הצעדים 1-7 ‏למעלה כ-checklist ידני. ‏זה המינימום לסגירת הפער.

## ‏מקור-אמת לצעדים

‏הצעדים המדויקים שעבדו ב-bds bootstrap מתועדים ב-`docs/decisions/bds.md`
‏(סעיף "מבנה bare") ‏וב-`docs/walkthrough.md`. ‏הסוכן שכותב את ה-brief יכול
‏להעתיק משם את הרצף המאומת.

## ‏הצעת complexity / verifier

- ‏סקריפט bash + ‏תיעוד → ‏complexity ~4-5 (לא 8). ‏calev tier: **‏light**.
- ‏אימות: ‏הרצת הסקריפט בתיקייה זמנית (`/tmp/test-init`), ‏בדיקה ש-`git worktree
  ‏list` ‏תקין, ‏ש-symlinks/gitignore נכונים, ‏ש-commit עובר.
- ‏זה slice מתאים להיות **‏הראשון שרץ בלולאה המלאה** (worktree → ‏אליעזר →
  ‏calev → merge) ‏על brief-driven-slices — ‏פואטי (slice על worktrees, ‏רץ ב-worktree).