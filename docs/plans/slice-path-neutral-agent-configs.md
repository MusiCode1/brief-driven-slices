# Slice B — path-neutral-agent-configs — ‏בריף

> **‏תאריך**: 2026-07-19
> **‏סוג מסמך**: ‏בריף ביצועי לסלייס
> **‏סטטוס**: ‏מאושר (‏מוכן ל-dispatch)
> **‏אימות אביגיל**: ✅ **READY** ‏(‏סבב 2 — ‏דוח: `reports/bds/path-neutral-agent-configs-avigail-r2.md`; ‏כל 6 findings ‏מ-r1 ‏נסגרו)
> **Dispatch**: ‏מותר לאליעזר רק אם `אימות אביגיל = READY`.
> **Complexity**: 6/10 (verifier: light + phase על Commit 1 — מנגנון ההחלפה)
> **‏תלויות (`depends_on`)**: []
> **‏Base**: main (‏זהו ריפו השיטה עצמו — "‏הפרויקט" = bds)
> **‏Dev tip**: `cb670b0`

---

## §0 — Pre-flight

> ‏זהו slice **‏על ריפו השיטה עצמו** (`brief-driven-slices`). ‏אין pnpm/browser/OneCLI.
> ‏הכלים: `python3`, `bash`, `git`, `grep`.

### ‏תלויות (‏חובה!)

‏אין. ‏בנוי ישירות על `main`. ‏לא נשען על slice אחר.

### ‏הקשר — ‏למה ה-slice הזה קיים

‏הגדרות הסוכנים מקשיחות נתיבים ספציפיים-למכונה. ‏על מכונה אחת העבודה ב-`~/Projects`
(P ‏גדולה) ‏אבל ההגדרות מצביעות על `~/projects` (p ‏קטנה) → ‏סוכנים כתבו 90 דוחות
‏לתיקיות שגויות/לא-מגובות (‏אירוע 2026-07-19). ‏השורש: **‏נתיבים מוקשחים במקור-האמת**.

### ‏מקור-האמת ‏(‏לתקן פה, ‏לא ב-generated)

- `agent-definitions/prompts/*.md` — ‏המקור. ‏generated נגזר מזה.
- `agent-definitions/agents.json` — ‏מטא (‏שמות, ‏מודלים, ‏tools).
- `scripts/generate-cli-configs.py` — ‏רינדור מקור → `cli-configs/*` + `agents/*`.
- `scripts/install-cli-configs.sh` — ‏symlink/copy ‏מ-`cli-configs/*` ‏ל-`~/.config/{opencode,codex,qoder}/agents`.

### ‏הבלאסט-רדיוס המדויק (grep ‏על `agent-definitions/prompts/`)

| ‏נתיב מוקשח | ‏מופעים | placeholder ‏מוצע |
|-----------|--------|------------------|
| `~/projects/brief-driven-slices/main/reports` | 4 | `{{BDS_REPORTS}}` |
| `~/projects/brief-driven-slices/main/scripts` | 3 | `{{BDS_SCRIPTS}}` |
| `~/projects/my-skills/lessons-learned/lessons-index` | 6 | `{{BDS_LESSONS}}` |
| `~/projects/orchestration/` | 1 | `{{BDS_ORCH}}` |

‏סה"כ 14 ‏מופעים ב-4 קבצי-מקור (`avigail.md`, `calev.md`, `calev-heavy.md`, `yetro.md`).

### Reading list

**must-read**:
- `scripts/generate-cli-configs.py`, `scripts/install-cli-configs.sh` (‏כל הקובץ)
- `agent-definitions/prompts/{avigail,calev,calev-heavy,yetro}.md` (‏השורות עם הנתיבים)

**reference**:
- `docs/methodology-evolution.md` §"reports sub-repo פרטי"
- `SKILL.md` §149 (‏"env ‏הוא קובץ git ‏רגיל — ‏עובד multi-machine")

---

## §1 — ‏מטרה

‏אחרי ה-slice: ‏מעביר את השיטה למכונה חדשה, ‏מגדיר **‏משתנה-סביבה אחד** (‏או קובץ config
‏אחד), ‏מריץ `install-cli-configs.sh` — ‏וכל הסוכנים כותבים למקומות הנכונים על **‏אותה מכונה**,
‏בלי לגעת בהגדרות. ‏מקור-האמת מכיל **‏אפס נתיבים אבסולוטיים**.

---

## §2 — Scope

| ‏פריט | ‏כן/לא | ‏לאן |
|------|------|------|
| placeholders ‏במקור-האמת ‏במקום נתיבים מוקשחים | ✅ | ‏slice זה |
| ‏החלפת placeholder ‏מ-env/config ‏ב-install-time | ✅ | ‏slice זה |
| ‏כשל-רועש אם משתנה לא-מוגדר | ✅ | ‏slice זה |
| ‏עדכון דוקטרינה (SKILL/reports-format/orchestration) ‏לעקרון הניטרלי | ✅ | ‏slice זה |
| ‏ברירות-מחדל של `distill.py`/`extract_sessions.py` ‏מ-env | ✅ | ‏slice זה |
| ‏מיזוג 3 התיקיות המפוזרות / ‏ניקוין | ❌ | ‏משימת-תחזוקה נפרדת (‏אחרי sync) |
| ‏שינוי מבנה ה-reports repo | ❌ | ‏מחוץ ל-scope |

---

## §3 — Architecture

```
מקור-האמת (ניטרלי)                    מכונה (קונקרטי)
┌───────────────────────────┐        ┌────────────────────────────┐
│ agent-definitions/         │        │ ~/.config/bds/paths.env    │ ← משתנה יחיד פר-מכונה
│   prompts/*.md             │        │   BDS_REPORTS=/abs/...      │
│   → {{BDS_REPORTS}} וכו'   │        │   BDS_SCRIPTS=/abs/...      │
└─────────────┬─────────────┘        │   BDS_LESSONS=/abs/...      │
              │                       │   BDS_ORCH=/abs/...         │
              ▼                       └─────────────┬──────────────┘
┌───────────────────────────┐                      │
│ generate-cli-configs.py    │  ← משאיר placeholders │
│ → cli-configs/* (ניטרלי,   │                      │
│   committed לריפו הציבורי) │                      │
└─────────────┬─────────────┘                      │
              ▼                                      ▼
┌────────────────────────────────────────────────────────────┐
│ install-cli-configs.sh                                       │
│  קורא paths.env → מחליף {{...}} → כותב עותק קונקרטי          │
│  לכל 3 ה-CLIs (dst שונה לכל אחד!):                           │
│    opencode → ${OPENCODE_AGENTS_DIR:-~/.config/opencode/agents}│
│    codex    → ${CODEX_AGENTS_DIR:-~/.codex/agents}           │
│    qoder    → ${QODER_AGENTS_DIR:-~/.qoder/agents}           │
│  ⚠️ opencode היום symlink (ln -sfn) — symlink לא נושא תוכן    │
│     מוחלף → חייב לעבור ל-copy. codex+qoder כבר cp (רק להוסיף  │
│     החלפה בזמן ה-copy). ההחלפה חלה על שלושתם.                 │
└────────────────────────────────────────────────────────────┘
```

**‏עקרון-על**: committed artifacts ‏(מקור + generated) ‏= ‏ניטרליים. ‏הקונקרטי חי **‏רק**
‏בתיקיות ה-agents של ה-CLIs (opencode=`~/.config/opencode`, codex=`~/.codex`,
qoder=`~/.qoder` — ‏שלא ב-git) ‏וב-`paths.env` ‏פר-מכונה.

---

## §4 — Commits ‏בסדר

### Commit 0 — placeholders ‏במקור-האמת (approach: manual)

**‏קבצים שמשתנים**: `agent-definitions/prompts/{avigail,calev,calev-heavy,yetro}.md`
- ‏החלף כל 14 המופעים בנתיב-מוקשח ל-placeholder המתאים (‏טבלת §0).
- `{{BDS_REPORTS}}/<project>/<slice>-calev.md` ‏וכו'.

**Verification**:
```bash
grep -rn "~/projects\|/home/user" agent-definitions/prompts/   # → ריק
grep -roh "{{BDS_[A-Z]*}}" agent-definitions/prompts/ | sort | uniq -c   # → 4 placeholders
```

### Commit 1 — ‏מנגנון החלפה + ‏כשל-רועש (approach: tdd) [verifier-phase ‏פה — ‏הכי מסוכן]

> ⚠️ **‏קריטי (finding אביגיל #1)**: ההחלפה + ‏כשל-רועש חלים על **‏שלושת** ה-installers —
> `install_opencode`, `install_codex`, `install_qoder` — ‏לא רק opencode. ‏אחרת codex/qoder
> ‏יתקינו placeholder ‏מילולי. ‏חוט אחד משותף שכל שלושתם קוראים לו.

**‏קבצים חדשים**:
- `cli-configs/paths.env.example` — ‏תבנית עם 4 המשתנים + ‏הסבר.
- `tests/test_path_substitution.py` — ‏**stdlib `unittest`** (‏קונבנציית הריפו — ‏`tests/test_distill.py`; pytest ‏לא מותקן). ‏טסטים: (א) ‏החלפה תקינה של 4 ה-placeholders, (ב) ‏משתנה חסר → ‏כשל-רועש (exit≠0), (ג) placeholder ‏לא-מוכר → ‏מתריע.

**‏קבצים שמשתנים**: `scripts/install-cli-configs.sh`
- ‏פונקציה `resolve_paths()` — ‏קוראת `${BDS_PATHS_ENV:-$HOME/.config/bds/paths.env}` (‏או env ‏ישיר), ‏ו-`:?`‎ ‏על כל 4 המשתנים → ‏**כשל-רועש** ‏אם חסר.
- ‏פונקציה `substitute_into(src, dst)` — ‏sed ‏שמחליף 4 ה-placeholders ‏וכותב ל-dst.
- **‏חיווט לשלושת ה-installers**:
  - `install_opencode`: ‏**`ln -sfn` → `substitute_into`** (symlink ‏לא נושא תוכן מוחלף → ‏חובה copy מוחלף).
  - `install_codex`: ‏ה-`cp` ‏הקיים → `substitute_into`.
  - `install_qoder`: ‏ה-`cp` ‏הקיים → `substitute_into`.
- **‏שכבת-הגנה**: ‏אחרי כל התקנה, ‏אם נשאר `{{BDS_` ‏ב-dst → `exit 1`.

**API skeleton** (bash):
```bash
resolve_paths() { : "${BDS_REPORTS:?BDS_REPORTS not set — ראה cli-configs/paths.env.example}" \
                    "${BDS_SCRIPTS:?}" "${BDS_LESSONS:?}" "${BDS_ORCH:?}"; }
substitute_into() {  # $1=src $2=dst
  sed -e "s|{{BDS_REPORTS}}|$BDS_REPORTS|g" -e "s|{{BDS_SCRIPTS}}|$BDS_SCRIPTS|g" \
      -e "s|{{BDS_LESSONS}}|$BDS_LESSONS|g" -e "s|{{BDS_ORCH}}|$BDS_ORCH|g" "$1" > "$2"
  grep -q "{{BDS_" "$2" && { echo "error: placeholder לא-מוחלף ב-$2" >&2; exit 1; }
}
```

**Verification** (‏unittest + ‏שלושת ה-CLIs):
```bash
python3 tests/test_path_substitution.py            # unittest, לא pytest
# install מזויף לשלושת ה-CLIs (dst נפרד לכל אחד):
env BDS_REPORTS=/tmp/fk-r BDS_SCRIPTS=/tmp/fk-s BDS_LESSONS=/tmp/fk-l BDS_ORCH=/tmp/fk-o \
    OPENCODE_AGENTS_DIR=/tmp/oc CODEX_AGENTS_DIR=/tmp/cx QODER_AGENTS_DIR=/tmp/qo \
    bash scripts/install-cli-configs.sh all
for d in /tmp/oc /tmp/cx /tmp/qo; do
  grep -rl "{{BDS_" "$d" && echo "FAIL: placeholder נשאר ב-$d" || echo "OK: $d מוחלף"
done
grep -rq "/tmp/fk-r" /tmp/oc && echo "OK: נתיב מוזרק מופיע"
# כשל-רועש: בלי BDS_REPORTS → exit≠0
env -u BDS_REPORTS bash scripts/install-cli-configs.sh opencode; echo "exit=$? (מצופה ≠0)"
```

### Commit 2 — ‏דוקטרינה + ‏סקריפטים (approach: manual)

> **‏scope-note (finding אביגיל #3)**: `docs/plans/` ‏(בריפים היסטוריים, ‏כולל זה) ‏ו-docs
> ‏היסטוריים (`walkthrough.md`, `methodology-evolution.md`) ‏מכילים ~60 ‏אזכורי-נתיב שהם
> ‏**‏פרוזה היסטורית מחוץ ל-scope** (§2). ‏אין לגעת בהם, ‏וה-grep ‏של ה-DoD ‏**‏מוגבל לקבצים
> ‏שבאמת נערכים** — ‏אחרת לעולם לא יחזיר ריק.

**‏קבצים שמשתנים** (‏רשימה סגורה — ‏רק אלה):
- `SKILL.md`, `docs/reports-format.md`, `orchestration.md`, `orchestration-project/AGENTS.md` —
  ‏החלף נתיבים-מוקשחים בתיאור **‏העיקרון הניטרלי** + ‏הפניה ל-`paths.env.example`.
- `scripts/distill.py`, `scripts/extract_sessions.py` — ‏ברירת-מחדל ל-`--reports-dir` ‏מ-`$BDS_REPORTS`
  (‏אם מוגדר), ‏אחרת ‏ההתנהגות הקיימת.
- ‏(‏`mordechai.md`/`eliezer.md` ‏— ‏**‏לא נוגעים**: ‏אביגיל אימתה שהם נקיים מנתיב-מוחלט, ‏משתמשים ב-relative בלבד.)

**Verification** (grep ‏מוגבל לקבצים הנערכים בלבד):
```bash
# אין נתיב-מוקשח בקבצים שנערכו (לא סורקים docs/plans + docs היסטוריים — מחוץ ל-scope)
grep -n "~/projects\|/home/user" \
  SKILL.md docs/reports-format.md orchestration.md orchestration-project/AGENTS.md \
  scripts/distill.py scripts/extract_sessions.py   # → ריק
python3 scripts/generate-cli-configs.py all   # regenerate — cli-configs נשארים ניטרליים
grep -rl "{{BDS_" cli-configs/ agents/ | wc -l   # → כל קבצי הסוכנים (placeholders נשמרו ב-committed)
```

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | ‏אפס נתיב-מוקשח במקור | `grep -rn "~/projects\|/home/user" agent-definitions/prompts/` → ‏ריק |
| 2 | ‏4 placeholders בלבד | `grep -roh "{{BDS_[A-Z]*}}" agent-definitions/` → BDS_REPORTS/SCRIPTS/LESSONS/ORCH |
| 3 | ‏החלפה עובדת ב-**3 ה-CLIs** | `install ... all` ‏עם env מזויף → ‏אין `{{` ‏באף אחד מ-`/tmp/oc,cx,qo`, ‏הנתיב המוזרק מופיע |
| 4 | ‏כשל-רועש | ‏install ‏בלי `BDS_REPORTS` → `exit≠0` ‏עם הודעה ברורה |
| 5 | ‏committed ‏נשאר ניטרלי | ‏אחרי regenerate: `cli-configs/*` + `agents/*` ‏מכילים `{{BDS_*}}`, ‏לא נתיב מכונה |
| 6 | ‏טסטים ירוקים | `python3 tests/test_path_substitution.py` (unittest, ‏לא pytest) |
| 7 | ‏regression: ‏install ‏אמיתי | ‏עם `paths.env` ‏אמיתי → ‏הסוכנים ב-**שלושת** ה-dst (opencode/codex/qoder) ‏מצביעים על נתיבי המכונה |

---

## §6 — Risks + mitigations

| ‏סיכון | ‏מקור | ‏מיטיגציה |
|------|------|----------|
| opencode symlink ‏לא נושא תוכן-מוחלף | ‏install ‏קיים משתמש ב-`ln -sfn` | ‏לעבור ל-copy, ‏או symlink ‏לתיקיית-build ‏מוחלפת (§9 Q1) |
| placeholder ‏נשאר בלי החלפה → ‏סוכן כותב ל-`{{BDS_REPORTS}}/...` ‏מילולי | ‏החלפה חלקית | ‏כשל-רועש ‏ב-install (DoD#4) — ‏חוסם דריסה שקטה |
| ‏חוסר-עקביות P/p ‏חוזר ‏אם המשתמש מגדיר env ‏שגוי | ‏טעות-אדם | `paths.env.example` ‏מפורש + ‏install ‏מוודא שהתיקיות קיימות (`test -d`) |
| ‏דוגמאות בדוקטרינה נתפסות ‏ע"י ‏ה-grep ‏של DoD#1 | ‏nested docs | ‏להחריג `.example` ‏ו-‏בלוקי-דוגמה ‏מפורשים |

---

## §7 — Escalation triggers

- ‏אם opencode ‏לא עובד עם copy **‏ולא** ‏עם symlink-to-build → ‏עצור, ‏זו החלטת-ארכיטקטורה.
- ‏אם מתגלה נתיב-מוקשח ‏שלא ב-4 ה-stems (‏sub-path ‏נסתר) → ‏עדכן §0 ‏ושאל.
- ‏אם ה-generated committed **‏חייבים** ‏להיות קונקרטיים ‏(‏לא placeholders) ‏מסיבה שלא צפינו → ‏עצור.

---

## §8 — Complexity score + verifier tier

| ‏פרמטר | ‏ניקוד |
|------|------|
| Refactor של קוד קיים (install/generate) | +1 |
| >5 files ‏ב->2 packages (‏prompts + scripts + docs) | +1 |
| ‏State machine / async | 0 |
| ‏חדש: ‏שכבת-החלפה + ‏כשל-רועש | +2 |
| TDD מלא (‏Commit 1) | -1 |
| ‏Deploy ‏מיידי | 0 |
| ‏נגיעה בצינור-install ‏שמשפיע על כל הסוכנים | +2 |
| Pure-ish (‏אין IO ‏מורכב) | -1 |

**Score**: 6/10

**Tier**: 4-7 → `verifier-slice-light` + `verifier-phase` ‏על **Commit 1** (‏מנגנון ההחלפה — ‏הכי מסוכן).

---

## §9 — ‏שאלות פתוחות

| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | opencode: copy ‏או symlink-לתיקיית-build? | **‏נפתר → copy.** ‏ההחלפה חלה על **‏שלושת** ה-installers (opencode עובר מ-symlink ל-copy; codex/qoder כבר cp). | ✅ ‏(‏הוכרע) |
| 2 | env ‏ישיר ‏או קובץ `paths.env`? | **‏שניהם** — env ‏גובר, ‏אחרת קובץ | ❌ |
| 3 | `{{BDS_ORCH}}`/`{{BDS_LESSONS}}` — ‏חובה, ‏או אופציונליים ‏עם ברירת-מחדל? | ‏חובה (‏כשל-רועש ‏על כולם) | ❌ |
| 4 | ‏להוסיף `BDS_DOCS` ‏(docs-repo) ‏עכשיו, ‏או ‏להשאיר ל-slice ‏של docs-relocation? | ‏להשאיר — ‏מחוץ ל-scope | ❌ |

---

## ‏סטיות מהתכנון (‏מתעדכן ע"י executor)

- ...
