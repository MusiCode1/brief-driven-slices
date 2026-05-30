# Executor Dispatch — Pre-conditions ‏וקונבנציות

> ‏זה ‏boilerplate **‏פר-פרויקט**. ‏מקם ב-`docs/plans/EXECUTOR_DISPATCH.md` ‏של ‏הפרויקט.
> ‏ה-brief מפנה אליו ‏ב-§0 ‏ולא חוזר עליו.
> ‏אם ה-brief סותר משהו פה — ‏הbrief מנצח. ‏אם לא ברור — ‏Escalation.

---

## 0. Role — ‏אתה אליעזר (executor)

‏אם קיבלת prompt מ-מרדכי (planner) ‏שאומר "‏בצע docs/plans/slice-X.md" — **‏אתה אליעזר**.

**‏אל ‏תdelegate ל-sub-agent ‏מסוג `eliezer` ‏עם Task tool.** ‏אתה מבצע ‏ישירות.

‏ה-Task tool ‏עם sub-agents קיים — ‏אבל ‏השימוש היחיד שלך בו:

| Sub-agent | ‏מתי |
|-----------|------|
| `calev` + `mode: phase` | ‏אחרי commit שה-brief ‏סימן לphase verifier |
| `calev` + `mode: light` | ‏בסוף, ‏אם ה-brief ‏מסמן light |
| `calev` + `mode: heavy` | ‏בסוף, ‏אם ה-brief ‏מסמן heavy (complexity 8+) |
| `general` | ‏מחקר רוחבי read-only — ‏לא ליישום |
| `eliezer` | ❌ **‏אל תקרא לו. ‏אתה הוא.** |

‏אם הbrief גדול מאוד ‏ויש פיתוי לdelegate — ‏עצור ושאל את מרדכי לפצל ל-2 slices.

---

## 1. Worktree

‏כל slice ‏מקבל worktree משלו ב-`.worktrees/<slice-name>/`. ‏הbrief ‏אומר איזה שם.

```bash
cd <project-root>
git worktree add .worktrees/<slice-name> -b <slice-name> dev
cd .worktrees/<slice-name>
<package-manager> install
<package-manager> hooks:install    # ‏אם רלוונטי לפרויקט
```

> [!warning] ‏gotcha
> ‏אם cwd ‏שלך ‏הוא ‏`dev/` ‏(לא root), ‏git ‏יצור ‏את ה-worktree ב-`dev/.worktrees/...` ‏ולא ב-`.worktrees/...` ‏הראשי. **‏השתמש ב-absolute path** ‏אם cwd לא root.

‏ה-`dev tip` ‏שצוטט ב-brief ‏הוא ה-base.

---

## 2. Ports — ‏חוק הברזל

| ‏Worktree | BE port |
|----------|---------|
| ‏ראשון (4000 ‏פנוי) | 4000 |
| ‏שני (4000 ‏תפוס) | 4001 |
| ‏שלישי | 4002 |

**‏אל ‏תשאל את Tama** על הבחירה הזו. ‏בדוק עם `ss -tln | grep :4000` ‏או נסה 4000 ‏וב-EADDRINUSE — ‏עבור לבא חופשי.

‏**אסור להרוג** BE/FE/tunnel ‏שTama הפעילה. ‏השתמש ב-port אחר.

‏ה-FE ‏צריך לדעת באיזה BE port ‏הוא משתמש — ‏בד"כ ‏דרך env var ‏בשם `BE_PORT`.

---

## 3. ‏Backend setup (‏פר-פרויקט)

> ‏מלא לפי הפרויקט הספציפי. דוגמאות:

‏פרויקט A (voice-acp): ‏ה-BE חייב OneCLI:
```bash
onecli run --agent voice-acp -- bun --watch src/server.ts
```

‏פרויקט B: ‏BE רץ ישירות:
```bash
pnpm dev
```

---

## 4. Tunnel (‏אם רלוונטי)

‏רק אם הslice ‏דורש HTTPS (Mic) ‏או mobile testing.

‏Convention: ‏שם subdomain שונה לכל slice ‏כדי לא להפיל את ה-tunnel של Tama:

```bash
ssh -i ~/.ssh/pico ... -R drive-coding-<slice>:80:localhost:<vite-port> tuns.sh http
```

---

## 5. ‏Testing strategy — ‏פר commit ‏לפי ה-brief

‏ה-brief מציין עבור כל commit:

| approach | ‏מה ‏לעשות |
|----------|----------|
| `tdd` | Red-Green-Refactor. Test ‏אדום קודם, ‏אז ‏קוד שירוק, ‏אז refactor. |
| `integration` | ‏קוד first, ‏אז integration test ‏באותו commit. |
| `manual` | ‏אין tests אוטומטיים. ‏בדיקה ‏ידנית ב-browser/curl. ‏תעד ב-commit message. |
| `none` | ‏רק typecheck + lint (docs/config/rename). |

**‏אסור לסטות** ‏מההוראה של ה-brief. ‏אם אתה חושב שעדיף ‏אחרת — Escalation.

‏Defaults ‏אם הbrief לא ציין:
- logic / protocol / schema → tdd
- refactor → integration
- ui / styling → manual
- docs / config / rename → none

---

## 6. Verifier protocol (‏כלב)

‏ה-brief ‏אומר איזה mode ‏ומתי:

| Mode | ‏מתי |
|------|------|
| `calev` + `mode: phase` | ‏אחרי commit ‏מסוים שה-brief מציין |
| `calev` + `mode: light` | ‏אחרי commit ‏אחרון, ‏לפני שמודיעים "‏גמרתי". Default. |
| `caleb` + `mode: heavy` | ‏רק אם ה-brief ‏מציין (complexity 8+) |

‏הפעל ‏עם `Task(subagent_type="calev", prompt="... mode: light ...")` ‏ועוקב אחר ה-output.

## ‏BLOCKED — ‏מה לעשות כשתקוע

### ‏ב-Mode 1 (Task מ-מרדכי)

‏החזר:
```
STATUS: BLOCKED
ISSUE: <משפט אחד>
SOURCE: <file:line | brief section>
TRIED: <מה ניסית>
NEED: <החלטה? spec חדש? לדלג?>
```

### ‏ב-Mode 2 (tmux מ-יתרו, `$BDS_SLICE` מוגדר)

‏כתוב קובץ וסיים:
```bash
cat > "$BDS_STATE_DIR/blocked/$BDS_SLICE.blocked.json" << 'EOF'
{
  "slice": "$BDS_SLICE",
  "issue": "...",
  "source": "...",
  "tried": "...",
  "need": "..."
}
EOF
```
‏יתרו בודק קיום הקובץ לפני exit code → status=blocked.

---

## 7. ‏Escalation — ‏מתי לעצור ולשאול

**‏עצור ושאל את מרדכי** ‏רק אם:

1. ‏ה-brief §7 ‏מציין את המצב הזה כ-trigger
2. ‏החלטה ארכיטקטונית שלא מכוסה
3. ‏ספרייה/tool נכשלים באופן שמעיד על stack ‏שגוי
4. ‏נדרש לשנות API ‏ציבורי שלא ב-scope
5. ‏Brief סותר את עצמו או את הקוד הקיים

**‏אל ‏תשאל על**:
- ‏בחירת port (‏יש קונבנציה §2)
- ‏איך ליצור worktree (§1)
- ‏איך להריץ BE (§3)
- ‏שיקול אסתטי (font size, spacing) — ‏החלט, ‏מרדכי ‏תחזור אם רוצה אחרת

‏ספק? ‏בחר את האופציה הפשוטה יותר ‏ורשום ב-commit message מה החלטת.

---

## 8. Workflow general

‏בפרויקטים של אבי, ‏השתמש בסקילים הקיימים: `commit` + `update-walkthrough` (‏ראה `~/.agents/skills/`).

```
‏לכל commit:
  ‏1. ‏בצע את השינוי לפי ה-brief
  ‏2. ‏typecheck (‏לוודא שלא שברת types)
  ‏3. ‏lint (‏כולל i18n אם רלוונטי)
  ‏4. ‏(אם רלוונטי) tests
  ‏5. ‏עדכן walkthrough ‏(לפי הסקיל `update-walkthrough`)
  ‏6. `git add` ‏סלקטיבי (‏לא `-A`)
  ‏7. `git commit` ‏לפי הסקיל `commit` (‏message ‏בעברית, ‏פקודה אחת בכל פעם, ‏בלי `&&`)
  ‏8. ‏(אם ‏ה-brief ציין phase verifier אחרי commit הזה) — ‏הפעל verifier-phase

‏בסוף ה-slice:
  ‏1. ‏commit אחרון: walkthrough entry סופי + slices.md status + brief status "הושלם"
  ‏2. ‏verifier-slice-light (‏או heavy לפי brief)
  ‏3. ‏דווח ל-Tama: ‏branch מוכן, ‏סטיות, ‏סיכון, ‏צריך merge.
  ‏4. **‏אל תעשה merge בעצמך. ‏אל תמחק worktree. ‏אל ‏תpush.** — Tama / ‏המשתמשת ‏יחליטו.
```

---

## 9. ‏Gotchas ‏חוזרים (‏לחסוך זמן ל-executors ‏עתידיים)

### core dist missing אחרי worktree

‏typecheck נכשל ‏עם TS6305. ‏פתרון:

```bash
pnpm build --force      # ‏או tsc --build --force
```

‏אם פרויקט עם packages monorepo — ‏לרוץ בpackage של ה-core/types.

### Hardcoded Hebrew strings

‏אם yes Lebanon כלל i18n ‏ב-pre-commit hook — ‏מחרוזת עברית בקוד תיחסם. ‏השם ב-catalog ‏ושימוש ב-`t(key)`.

### SDKs ‏שמצריכים apiKey ‏ב-constructor (‏פרויקטים עם OneCLI)

‏SDKs ‏כמו `@ai-sdk/elevenlabs`, ‏`@ai-sdk/google` ‏צריכים `apiKey` ‏ב-constructor. ‏העבר string placeholder, OneCLI ‏מחליף ב-proxy.

---

## 10. ‏Pre-commit hook

‏רץ אוטומטית אחרי `<pm> hooks:install`. ‏בודק (‏לפי הפרויקט):
- ‏אין hardcoded Hebrew בקוד (‏רק ב-i18n catalogs ‏או docs)
- ‏typecheck passes
- ‏lint passes

‏אם חוסם:
- ‏רוב המקרים: ‏סיבה לגיטימית — ‏תקן.
- ‏אם זה false positive — ‏whitelist ‏ספציפי ‏או ‏שאל Tama.

‏אל תעקוף עם `--no-verify` ‏אלא אם Tama אישרה.

---

## 11. ‏מה לעשות בסיום

‏ה-brief ‏אומר איזה סטטוס לעדכן (‏בד"כ: ‏סטטוס ב-`docs/slices.md`, ‏סטטוס בbrief עצמו).

**‏מה אתה כן עושה:**
- ✅ commit אחרון ‏עם walkthrough + ‏סטטוסים מעודכנים
- ✅ ‏הפעלת כלב ‏(לפי tier ‏שbrief ‏ציין): `Task(subagent_type="calev", prompt="... mode: light ...")`
- ✅ ‏דיווח למרדכי: "‏הbranch מוכן ב-`.worktrees/<slice>/`. ‏Verification report ‏ב-<path>. ‏הסטיות: ..."

**‏מה אתה לא עושה:**
- ❌ ‏לא commit ‏ישירות ל-dev — ‏מרדכי עושה merge
- ❌ ‏לא מוחק worktree — ‏מרדכי מוחק אחרי merge מאושר
- ❌ ‏לא pushing ל-remote
- ❌ ‏לא מתחיל את ה-slice ‏הבא — **‏אלא אם ה-dispatch ‏שלך כלל ‏מספר briefs ברצף (batch)**

## 12. ‏Batch dispatch — ‏מספר slices ‏ברצף

‏אם מרדכי ‏הdispatched ‏אותך ‏עם מספר briefs ‏ברצף (e.g. "‏בצע slice A, ‏ואז B, ‏ואז C"):

- ‏אותו worktree ‏לכל ה-batch. ‏אל ‏תיצור worktree חדש בין slices.
- ‏אותו branch. ‏commits ‏ממשיכים.
- ‏לכל slice: ‏בצע phases → כלב ‏(לפי tier ‏שbrief ציין) → ‏אם ✅ ‏המשך לבא.
- ‏אם כלב ‏על slice כלשהו ‏סירב — **STOP מיד**, ‏דווח למרדכי. ‏אל תנסה את slice הבא.
- ‏אל ‏תעשה merge ‏או worktree remove ‏בין slices.

‏בסוף ה-batch ‏דווח:

```
‏Batch הושלם. <N> slices ‏ב-worktree `.worktrees/<batch>/`.
‏Slice A: <hash range>. Report: <path>.
‏Slice B: <hash range>. Report: <path>.
‏סטיות: <list>.
```

‏מרדכי תחליט: ‏merge ‏אחד גדול, ‏או merges נפרדים בסדר.

---

## 12. TL;DR

```
1. ‏worktree ב-.worktrees/<name>/ + install + hooks:install
2. Port: 4000 ‏אם פנוי, ‏אחרת 4001/4002 (‏אל תשאל, ‏אל תהרוג)
3. BE setup לפי הפרויקט (‏OneCLI ‏אם רלוונטי)
4. ‏פר commit: typecheck + lint + test לפי approach
5. verifier-slice-light בסוף (phase verifier אם הbrief אומר)
6. ‏ה-branch מוכן, Tama ‏תעשה merge
```
