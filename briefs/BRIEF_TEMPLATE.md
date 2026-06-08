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

> ‏סוכן חדש בלי context צריך לדעת אחרי הסעיף הזה איך להריץ הכל. ‏אל ‏תכתוב "‏ראה AGENTS.md" ‏בלי לציין מה ספציפית.

### ‏תלויות (‏חובה!)

‏slice זה **‏מבוסס על**:
- ‏slice K (status: merged / verified) — ‏מה הוא מוסיף שאנחנו צריכים
- _‏או: אין תלויות (‏בנוי ישירות על dev)_

> ‏אביגיל בודקת שסעיף זה עקבי עם `depends_on` ב-state.json. ‏חסר → 🔴 blocker.

### Worktree

```bash
cd <project-root>
git worktree add .worktrees/slice-N-name -b slice-N-name dev
cd .worktrees/slice-N-name
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
> DELETE block: `path/to/file.svelte` ‏שורות 468-490 (block ‏של `<form class="text-form">`)

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
