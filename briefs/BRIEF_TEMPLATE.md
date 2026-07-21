# Slice N — <name> — ‏בריף

> **‏תאריך**: YYYY-MM-DD
> **‏סוג מסמך**: ‏בריף ביצועי לסלייס — ‏לא תוכנית טרום-בריף
> **‏סטטוס**: ‏טיוטה / ‏מאושר / ‏בעבודה / ‏הושלם
> **‏אימות אביגיל**: ‏לא מאומת / READY (‏דוח: `reports/<project>/<slice>-avigail.md`)
> **Dispatch**: ‏מותר לאליעזר רק אם `אימות אביגיל = READY`; אחרת זה בריף לא-גמור.
> **Complexity**: X/10 (verifier: light/heavy)
> **‏תלויות (`depends_on`)**: [] ‏— ‏או [slice-K, slice-L] (‏חובה לציין, ‏גם אם ריק)
> **‏Base**: dev ‏— ‏או branch ‏של תלות אם לא ב-dev עדיין
> **‏Dev tip**: `<hash>`

---

## §0 — Pre-flight

> ‏סוכן חדש בלי context צריך לדעת אחרי הסעיף הזה איך להריץ הכל.
>
> **מקורות קבועים — אל תשכפל אותם כאן** (דוקטרינת env, ראה `EXECUTOR_DISPATCH.md`):
> - **env של הפרויקט** (ports, paths, OneCLI, tunnel, hooks) → ב-`AGENTS.md` של הפרויקט (ש-`CLAUDE.md` עושה לו `@import`).
> - **פרוטוקול executor גנרי** → בסוכן `eliezer`.
>
> §0 מציין רק את מה ש**ספציפי ל-slice הזה** מעבר ל-`AGENTS.md` — ומפנה אליו לשאר. ‏(אל "‏ראה AGENTS.md" סתמי — ציין מה רלוונטי.)

### ‏תלויות (‏חובה!)

‏slice זה **‏מבוסס על**:
- ‏slice K (status: merged / verified) — ‏מה הוא מוסיף שאנחנו צריכים
- _‏או: אין תלויות (‏בנוי ישירות על dev)_

> ‏אביגיל בודקת שסעיף זה עקבי עם `depends_on` ב-state.json. ‏חסר → 🔴 blocker.

### Worktree

```bash
cd <project-root>
git worktree add .worktrees/N-name -b slice/N-name dev   # branch: slice/<name> | dir: .worktrees/<name> (בלי קידומת)
cd .worktrees/N-name
pnpm install && pnpm hooks:install
```

‏(‏אם פרויקט עם bare repo — ‏השתמש בabsolute path: `git worktree add /full/path/.worktrees/...`)

### ‏איך להריץ

- BE: `<command>` (‏default port 4000, ‏אם תפוס — 4001+)
- FE: `<command>` (port: OS-assigned)
- ‏Tests: `<command>`
- ‏Tunnel (אופציונלי): `<ssh command>`

### Browser

‏איזה browser ‏לטסט? linux-gui? `pw-clean.sh`? ‏מכונה אמיתית?

### OneCLI agent (‏אם רלוונטי)

‏שם: `<agent-name>`
‏שימוש: `onecli run --agent <name> -- <cmd>` (‏מה הוא מזריק)

### Reading list

**must-read** ‏(לפני שמתחילים):
- ...

**reference** (‏בזמן עבודה):
- ...

### ‏מקורות חיצוניים (API / docs / ספרייה) — ‏עיגון + ‏מסקנות מחייבות-עיצוב

> ‏אם ה-slice נשען על API / ‏פורמט-פרומפט / ‏התנהגות של ספק או ספרייה חיצונית — ‏**‏קרא את ה-docs
> ‏הרשמי לעומק** (‏לא תקצירי-חיפוש) ‏ותעד כאן: ‏מה נקרא (URL) ‏ו-**‏מה המסקנה המחייבת-עיצוב**
> (‏פורמט מדויק, ‏מגבלות, failure modes ‏כמו rejection/leak).
>
> ⚠️ **‏למה זה שדה-חובה**: ‏אביגיל מאמתת brief↔**‏code** — ‏**‏לא** brief↔docs-חיצוני. ‏פער בין
> ‏ה-brief ‏ל-API ‏חיצוני הוא **‏נקודה עיוורת שיטתית** ‏שלה; ‏העיגון כאן הוא ההגנה היחידה
> ‏(‏case: gemini-tts-directing 2026-07-21 — ‏פורמט-פרומפט שגוי היה עובר את כל סבבי אביגיל).
>
> - _‏אין תלות חיצונית — ‏כתוב "‏אין" ‏ודלג._
> - ‏אחרת: `<URL>` — ‏מסקנה מחייבת: `<פורמט/‏מגבלה/failure-mode>`

---

## §1 — ‏מטרה

‏פסקה אחת. ‏מה תהיה החוויה אחרי שהsbb הושלם — ‏מנקודת מבט המשתמשת.

---

## §2 — Scope

| ‏פיצ'ר | ‏כן/לא | ‏לאן |
|------|------|------|
| ... | ✅ | ‏בsbb הזה |
| ... | ❌ | slice X |

> ‏זו לא טבלת TODO. ‏זו הגנה מ-scope creep.

---

## §3 — Architecture diagram

```
┌─────────────┐
│ Component A │ ← ‏חדש
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Component B │ ← ‏קיים, ‏משתנה
└─────────────┘
```

(ASCII. ‏~30 שורות. ‏חוסך 5K tokens של חיפוש.)

---

## §4 — Commits ‏בסדר

### Commit 0 — <‏שם> (approach: tdd | integration | manual | none)

**‏קבצים חדשים**:
- `path/to/file.ts`

**‏קבצים שמשתנים**:
- `path/to/other.ts` — ‏מוסיף method X, ‏לא משנה Y

**API skeleton** (‏אם מוסיף class/function ציבורי):

```ts
class NewThing {
  constructor(opts: { a: string; b: number })
  doStuff(): Promise<Result<X, Error>>
}
```

(‏לא רק שמות — ‏החתימה המדויקת. ‏executor אסור לשנות.)

**DELETE block** (‏אם רלוונטי):
> DELETE: `path/to/file.svelte` — block של `<form class="text-form">` (grep anchor: `class="text-form"`)
>
> ⚠️ **עגן ב-anchor, לא במספר-שורה.** מספרי-שורות מתיישנים ברגע שה-base זז — זו טעות
> ה-`wrong-line-number` (#1 ב-`plan-pitfalls.md`). תן symbol/pattern ש-grep ימצא, לא `שורות 468-490`.

**Verification**:

```bash
pnpm typecheck
pnpm test --filter @x/y
# ‏manual: ‏פתח https://X, ‏וודא Y
```

### Commit 1 — ...

(‏אותו פורמט)

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | typecheck + build + tests | `pnpm typecheck && pnpm build && pnpm test` |
| 2 | lint:i18n | `pnpm lint:i18n` |
| 3 | <Feature X> ‏עובד | ‏פתח <URL>, ‏לחץ Y, ‏וודא Z ‏ב-DOM |
| 4 | mobile + desktop | ‏screenshot של ‏שני viewports |
| 5 | regression: <feature ‏ישן> | ‏עוד עובד? ‏פקודה |

‏לא "‏הכל עובד" — ‏טבלת checkboxes ‏עם פקודה לכל אחד.

---

## §6 — Risks + mitigations

| ‏סיכון | ‏מקור | ‏מיטיגציה |
|------|------|----------|
| Hardcoded Hebrew strings | learnings.md ‏[‏תאריך] | ‏pre-commit hook חוסם, ‏וודא `pnpm hooks:install` |
| Svelte 5 reactivity על array | learnings.md ‏[‏תאריך] | `{#each ... as ... (id)}` + ‏הקרא `.length` |
| ... | ... | ... |

> ‏3 ‏שתמיד נשכחים (‏לבדוק תמיד):
> 1. Hardcoded strings → i18n
> 2. ‏Reactivity gotchas של ה-framework
> 3. ‏OneCLI placeholder pattern (‏אם רלוונטי)

---

## §7 — Escalation triggers

> ‏אם X — ‏עצור ושאל את Tama:

- ‏החלטה ארכיטקטונית שלא מכוסה ב-D1-D50
- ‏ספרייה חיצונית נכשלת באופן שמעיד על stack שגוי
- BE proxy לא מועבר ל-upstream שדרוש
- ‏פתחת ‏3+ ‏גישות לאותה בעיה, ‏אף אחת לא עבדה
- ‏Brief סותר את עצמו
- ‏אתה רוצה לסטות מ-Testing strategy שה-brief קבע

---

## §8 — Complexity score + verifier tier

| ‏פרמטר | ‏ניקוד |
|------|------|
| Cross-store data flow ‏חדש | +2 |
| ‏Streaming/real-time (WS, SSE, audio) | +2 |
| ‏Protocol contract חדש | +2 |
| Refactor של קוד קיים | +1 |
| >5 files ‏ב->2 packages | +1 |
| State machine / async coordination | +2 |
| ‏ספרייה חיצונית חדשה | +2 |
| ‏ספרייה DOM-mutating | +1 |
| 3 ‏slices אחרונים באזור החזירו bugs | +2 |
| Test coverage <70% ‏באזור | +1 |
| Deploy ‏לפרודקשן מיד | +2 |
| Pure logic, ‏אין IO | -2 |
| TDD מלא, tests מקיפים | -1 |
| Greenfield, ‏אין call sites קיימים | -1 |

**Score**: __ / 10

**Tier**:
- 0-3 → `verifier-slice-light` ‏בלבד
- 4-7 → `verifier-slice-light` + `verifier-phase` ‏על 1-2 phases מסוכנים
- 8+ → `verifier-slice-heavy` + verifier-phase על mostly phases

**‏Verifier-phase ‏אחרי commit/phase**: __ (‏ציין מספרים)

---

## §9 — ‏שאלות פתוחות

| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ... | ... | ❌ |
| 2 | ... | ... | ✅ ‏(‏ממתין להחלטה) |

---

## ‏סטיות מהתכנון (‏מתעדכן ע"י executor ‏תוך כדי)

> ‏ה-executor מתעד פה כל סטייה ‏מה-brief ‏ולמה.

- ...
