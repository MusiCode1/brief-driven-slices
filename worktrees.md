# Worktrees — ‏מנגנון לעבודה מקבילה

‏Slices ‏רצים ב-worktrees ייעודיים כדי לאפשר:
1. **‏עבודה מקבילה** — ‏שני executors ‏על שני slices בו-זמנית
2. **‏בידוד** — ‏שינוי ב-slice A ‏לא ‏שובר את slice B
3. **‏Cleanup קל** — ‏worktree ‏שלא רלוונטי = `git worktree remove`

## ‏מבנה מומלץ לפרויקט

```
<project>/
├── .bare/                  # bare git repo (‏אם משתמשים ב-bare)
├── .git                    # ‏קובץ עם `gitdir: ./.bare` (‏אם bare) ‏או ‏repo רגיל
├── .gitignore              # ‏מחריג .worktrees
├── .worktrees/             # ‏ספרייה לworktrees זמניים
│   ├── slice-X/
│   ├── slice-Y/
│   └── TRACKER.md          # (‏אופציונלי) ‏מי על מה רץ עכשיו
├── dev/                    # worktree של branch dev (‏long-lived)
└── main/                   # worktree של branch main (‏long-lived)
```

‏היתרון של מבנה bare + ‏שני worktrees ראשיים (`dev/`, `main/`): ‏אין branch switching, ‏git ‏לא ‏"מתבלבל" ‏כי ‏ה-bare repo בצד.

‏אלטרנטיבה: ‏worktree רגיל ‏עם `dev` ‏כ-main directory ‏וworktrees תחת `.worktrees/`. ‏עובד גם.

## ‏מוסכמת שמות — קידומת `slice/` ל-branch, dir בלי הקידומת

> **‏הכלל**: ‏שם ה-branch הוא `slice/<name>`; ‏שם תיקיית ה-worktree הוא `.worktrees/<name>`
> (**בלי** הקידומת `slice/`). ‏`<name>` ‏הוא השם הנקי (למשל `4-bubble-polish`).

| | ‏ערך | ‏דוגמה |
|---|------|--------|
| branch | `slice/<name>` | `slice/4-bubble-polish` |
| ‏worktree dir | `.worktrees/<name>` | `.worktrees/4-bubble-polish` |

**‏למה `slice/`**: namespace נייטיב של git — `git branch --list 'slice/*'`,
`git for-each-ref refs/heads/slice/` לניקוי-מסה, ‏והפרדה מ-`fix/`/`spike/` עתידיים.
**‏למה dir בלי הקידומת**: ‏slash בשם תיקייה יוצר תת-ספרייה מקוננת (`.worktrees/slice/foo`) — ‏מבולגן. ‏dir שטוח.

## ‏יצירת worktree לslice

```bash
cd <project-root>
git worktree add .worktrees/<name> -b slice/<name> <base-branch>
cd .worktrees/<name>
```

‏`<base-branch>` ‏הוא בד"כ `dev` ‏(או ‏ה-tip ‏המעודכן ביותר). ‏בשרשור — `slice/<dep-name>` ‏(branch של התלות).

‏אחרי יצירה:

```bash
<package-manager> install      # pnpm install / bun install / npm i
<package-manager> hooks:install # ‏אם פרויקט עם pre-commit hooks (‏voice-acp ‏עושה זה)
```

> [!warning] ‏gotcha: ‏worktree path
> ‏אם ‏ה-cwd ‏שלך ‏הוא ‏`dev/` ‏(לא הroot), ‏git ‏יצור ‏את ה-worktree ‏ב-`dev/.worktrees/<name>/` ‏ולא ב-`.worktrees/<name>/` ‏הראשי. **‏פתרון**: ‏absolute path: ‏`git worktree add /full/path/to/project/.worktrees/<name> -b slice/<name> dev`.

## ‏ports — ‏convention לעבודה מקבילה

‏הכלל הברזל:

| ‏Worktree | BE port | FE port |
|----------|---------|---------|
| ‏ראשון | 4000 (‏default) | OS-assigned |
| ‏שני | 4001 | OS-assigned |
| ‏שלישי | 4002 | OS-assigned |

‏ה-FE ‏תמיד OS-assigned, ‏אז ‏אין collision possible.
‏ה-BE ‏הוא הקריטי — ‏שני BEs ‏על ‏אותו port = EADDRINUSE.

### ‏איך executor בוחר port

‏בלי לשאול ‏את Tama:

```bash
# ‏בדוק אם 4000 ‏פנוי
ss -tln | grep -q ':4000 ' && PORT=4001 || PORT=4000

# ‏או פשוט נסה 4000 ‏ואם נכשל — ‏עבור ל-4001
```

‏הbrief ‏בד"כ ‏מציין: "BE port: 4000 ‏אם פנוי, ‏אחרת 4001+".

### ‏ה-FE ‏צריך לדעת ‏באיזה BE port ‏לחבר

‏ב-vite/Next/etc., ‏ה-proxy ל-`/api`, `/proxy`, `/ws` ‏צריך לעבור ‏ל-BE port ‏שבחר ה-executor. ‏הconvention: ‏env var ‏בשם `BE_PORT`:

```bash
# Worktree A — BE על 4000
PORT=4000 <run-be>
<run-fe>                 # ‏defaults ל-BE_PORT=4000

# Worktree B — BE על 4001
PORT=4001 <run-be>
BE_PORT=4001 <run-fe>    # ‏Vite proxy → 4001
```

‏הproxy config (‏vite.config.ts ‏או דומה):

```ts
const BE_PORT = process.env.BE_PORT || '4000'
export default defineConfig({
  server: {
    proxy: {
      '/api': `http://localhost:${BE_PORT}`,
      '/ws': { target: `ws://localhost:${BE_PORT}`, ws: true },
    }
  }
})
```

## ‏אסור להרוג processes ‏של Tama

‏אם Tama ‏הפעיל BE/FE/tunnel ‏לבדיקה — ‏אסור ל-executor להרוג אותם. ‏היא משתמשת בהם.

‏פתרון: ‏executor יבחר port אחר ‏(4001 ‏או 4002).

## Tunnels — ‏אם נדרש URL ‏ציבורי

‏ל-Mic ‏(HTTPS חובה) ‏או mobile testing:

```bash
ssh -i ~/.ssh/pico \
  -o StrictHostKeyChecking=accept-new \
  -o ServerAliveInterval=15 \
  -R <subdomain>:80:localhost:<fe-port> tuns.sh http
```

‏ה-URL: ‏`https://<your-username>-<subdomain>.tuns.sh`

‏Convention לעבודה מקבילה: ‏שם subdomain ‏שונה לכל slice (`drive-coding-slice-X` ‏ולא ‏סתם ‏`drive-coding`) — ‏אחרת ‏השני יחליף את הראשון.

> [!info] ‏ראה גם
> ‏סקיל `pico-tunnels` ל-tuns.sh ‏ופלגינים אחרים.

## ‏Pre-commit hooks

‏אם ‏פרויקט משתמש ‏ב-hooks (e.g. ‏i18n lint, ‏typecheck), ‏חובה להריץ ‏אחרי `install`:

```bash
<package-manager> hooks:install   # ‏מגדיר core.hooksPath
```

‏בלי זה — ‏hook ‏לא רץ, ‏ושינוי שגוי (e.g. ‏Hebrew string ‏שצריך i18n) ‏ייכנס ל-commit.

‏אם hook ‏חוסם:
- ‏רוב המקרים: ‏באמת שכחת ‏i18n / lint. ‏תקן.
- ‏אם זה false positive (‏prompt ל-LLM ‏שצריך עברית, ‏לדוגמה) — ‏whitelist ‏או ‏עדכן את ה-hook.
- ‏לא לעקוף עם ‏`--no-verify` ‏אלא אם Tama אישרה.

## Cleanup ‏בסוף slice

‏אחרי merge מוצלח ל-dev:

```bash
cd <project-root>
git worktree remove .worktrees/<name>
git branch -d slice/<name>  # -D ‏אם force
git worktree prune          # ‏ניקוי רישומים תלויים
```

‏אם ה-worktree ‏שינויים unstaged — `git worktree remove` ‏יתלונן. ‏החלט: `git stash` ‏או `git worktree remove --force`.

## Shared assets ‏(images, audio, fixtures)

‏אם הפרויקט ‏מכיל קבצים ‏גדולים שב-gitignore (e.g. ‏tests/fixtures ‏לאודיו), ‏worktree חדש לא יהיה להם גישה.

‏פתרון Linux: symlink ידני מ-source repo:

```bash
ln -s ../../<project>/tests/fixtures .worktrees/<name>/tests/fixtures
```

‏פתרון Windows: ‏מתועד בסקיל `git-worktree-shared-assets`.

## ‏Anti-patterns ‏ל-worktree usage

- ❌ ‏worktrees ‏ב-project root (‏רעש, ‏glob ‏מטונפים). ‏תמיד תחת `.worktrees/`.
- ❌ ‏branch ‏שם זהה לworktree directory ‏(אבל worktree על main branch ‏זה אקס, ‏עדיף שם נפרד).
- ❌ ‏שני executors ‏על אותו BE port (EADDRINUSE).
- ❌ ‏worktree ‏שיושב 11+ ‏ימים בלי שימוש — ‏stale, ‏עלול לסתור slice ‏שmerged ‏ב-base ‏בינתיים. ‏מחק ‏אם לא רלוונטי, ‏או ‏rebase.
- ❌ ‏commit ‏לdev ישירות מתוך worktree של slice — ‏עדיף merge formal ‏ע"י Tama.
- ❌ ‏push ‏לremote ‏מ-worktree של slice ‏(אם המשתמשת לא ביקשה).
