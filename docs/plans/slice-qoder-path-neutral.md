# Slice — qoder-path-neutral — ‏בריף

> **‏תאריך**: 2026-07-19
> **‏סוג מסמך**: ‏בריף ביצועי (‏קוד: generator + installer)
> **‏סטטוס**: ‏טיוטה
> **‏אימות אביגיל**: ‏לא מאומת (‏דוח: `reports/bds/qoder-path-neutral-avigail.md`)
> **Complexity**: 4/10 (verifier: light)
> **‏תלויות (`depends_on`)**: []  (path-neutral **‏כבר merged ל-main** — `substitute_into` קיים)
> **‏Base**: main (`1f3dff8`+)
> **‏Dev tip**: ‏HEAD הנוכחי

---

## §0 — Pre-flight

‏slice על ריפו השיטה. ‏משחזר תמיכת **qoder** ‏כ-CLI adapter שלישי — ‏**‏path-neutral מהיום הראשון**
‏(‏מחווט ל-`substitute_into` ‏שכבר קיים מ-slice path-neutral). ‏הכלים: python3/bash/git.

### ‏רקע

‏תמיכת qoder נכתבה כ-WIP לא-committed (‏שמור ב-`git stash@{0}`) **‏לפני** ‏ש-path-neutral מוזג —
‏קבצי `cli-configs/qoder/*.md` ‏שנוצרו אז נגזרו מ-prompts ‏עם נתיבים מוקשחים — ‏אז ‏commit
‏שלהם כמו-שהם ‏מסתכן ב-**regression** ‏של path-neutral. ‏**‏בכל מקרה** ‏אנחנו לא נשענים עליהם:
‏לשחזר את ה-**scaffolding** ‏בלבד (generator + installer + agents.json keys), ‏ו**‏לייצר מחדש**
‏את ה-cli-configs/qoder ‏מה-prompts הנוכחיים (‏avigail/calev/calev-heavy/yetro ‏מכילים `{{BDS_*}}`;
‏mordechai/eliezer ‏נקיים) → qoder ‏ניטרלי by-construction, ‏ללא תלות במצב קבצי-ה-stash.

### ‏מקור-ה-scaffolding (`git stash@{0}`)

- `scripts/generate-cli-configs.py` — `render_qoder_agent()` + qoder ל-targets/generate loop + `choices`.
- `agent-definitions/agents.json` — ‏מפתח `"qoder"` ‏פר-סוכן.
- `scripts/install-cli-configs.sh` — `install_qoder()` (cp-based) + qoder ל-`case`.
- READMEs — ‏תיעוד adapter.

### Reading list
- `scripts/generate-cli-configs.py` (render_codex/render_opencode כתבנית ל-qoder), `scripts/install-cli-configs.sh` (install_codex + substitute_into — כתבנית).
- `git stash show -p stash@{0}` — ה-scaffolding.

---

## §1 — ‏מטרה

‏qoder חוזר כ-CLI adapter נתמך (`install-cli-configs.sh qoder`), **‏path-neutral** — ‏קבציו
‏committed ‏עם placeholders, ‏וה-install ‏מזריק נתיב-מכונה דרך `substitute_into` (‏בדיוק כמו opencode/codex).

---

## §2 — Scope

| ‏פריט | ‏כן/לא |
|------|------|
| render_qoder_agent + qoder target ב-generator | ✅ |
| agents.json qoder keys | ✅ |
| install_qoder **‏מחווט ל-`substitute_into`** (‏לא cp גולמי) | ✅ |
| cli-configs/qoder ‏מיוצר-מחדש path-neutral | ✅ |
| ‏שימוש בקבצי qoder המוקשחים מה-stash | ❌ (‏regression — ‏מיוצר מחדש) |

---

## §4 — Commits ‏בסדר

### Commit 0 — scaffolding + generator (approach: manual)

**‏קבצים שמשתנים**:
- `agent-definitions/agents.json` — ‏הוסף מפתח `"qoder"` ‏פר-סוכן (‏מה-stash).
- `scripts/generate-cli-configs.py` — ‏הוסף `render_qoder_agent()` + qoder ל-`generate()` ‏ול-`choices` (`all`/`qoder`).

**Verification**:
```bash
python3 scripts/generate-cli-configs.py qoder
grep -l "{{BDS_" cli-configs/qoder/agents/calev.md   # → placeholders (לא ~/projects!)
grep -c "~/projects\|/home/user" cli-configs/qoder/agents/*.md   # → 0
```

### Commit 1 — install_qoder ‏מחווט ל-substitute_into (approach: manual) [verifier-phase]

**‏קבצים שמשתנים**: `scripts/install-cli-configs.sh`
- ‏הוסף `install_qoder()` — ‏כמו install_codex ‏אבל dst=`${QODER_AGENTS_DIR:-$HOME/.qoder/agents}`,
  ‏ו-**‏במקום `cp` גולמי → `substitute_into "$src/$agent.md" "$dst/$agent.md"`**.
- ‏הוסף qoder ל-`case` (all + qoder) ול-usage.
- `resolve_paths` ‏כבר קיים — install_qoder ‏חייב לקרוא לו (‏או להסתמך שהוא נקרא ב-all).

**Verification**:
```bash
env BDS_REPORTS=/tmp/fk-r BDS_SCRIPTS=/tmp/fk-s BDS_LESSONS=/tmp/fk-l BDS_ORCH=/tmp/fk-o \
    QODER_AGENTS_DIR=/tmp/qo bash scripts/install-cli-configs.sh qoder
grep -rl "{{BDS_" /tmp/qo && echo "FAIL: placeholder נשאר" || echo "OK: qoder מוחלף"
grep -rq "/tmp/fk-r" /tmp/qo && echo "OK: נתיב מוזרק מופיע"
```

### Commit 2 — regenerate + docs (approach: manual)

- `python3 scripts/generate-cli-configs.py all` → cli-configs/qoder committed (placeholders).
- READMEs: ‏הוסף qoder ל-adapter list (‏מה-stash).

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | cli-configs/qoder ‏ניטרלי (‏כל 6) | `grep -c "~/projects\|/home/user" cli-configs/qoder/agents/*.md` → 0 |
| 2 | placeholders ‏ב-4 ה-prompts שיש להם | `grep -l "{{BDS_" cli-configs/qoder/agents/*.md` → **4** (avigail/calev/calev-heavy/yetro). mordechai/eliezer ‏נקיים מ-hardcoded **וגם** ‏בלי placeholder (‏relative/runtime בלבד — ‏אין מה להזריק). |
| 3 | install qoder ‏מחליף | ‏install מזויף → ‏אין `{{`, ‏נתיב מוזרק מופיע |
| 4 | generator idempotent | `generate-cli-configs.py all` פעמיים → "no changes" בשני |
| 5 | 3 CLIs עובדים יחד | `install ... all` ‏עם 3 ה-*_AGENTS_DIR → ‏שלושתם מוחלפים |
| 6 | regression | `python3 tests/test_path_substitution.py` + `test_distill.py` ירוקים |

---

## §6 — Risks
| ‏סיכון | ‏מיטיגציה |
|------|----------|
| ‏שימוש בטעות בקבצי qoder המוקשחים מה-stash | Commit 0 ‏מייצר מחדש; DoD#1 ‏חוסם (grep=0) |
| install_qoder ‏עם cp גולמי (‏שוכח substitute_into) | DoD#3 ‏חוסם |
| agents.json qoder keys ‏לא תואמים ל-render | ‏אימות: generate qoder ‏רץ בלי שגיאה |

## §7 — Escalation
- ‏אם ה-scaffolding מה-stash ‏לא תואם את מבנה agents.json הנוכחי (‏שהשתנה ב-merge) → ‏עצור.

## §8 — Complexity: 4/10 (‏generator+installer, ‏אין state/streaming). Tier: light + phase על Commit 1.

## §9 — ‏שאלות פתוחות
| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ‏לזרוק את `stash@{0}` ‏אחרי? | ‏כן — ‏אחרי DoD ‏ירוק (‏ה-scaffolding נשחזר, ‏הקבצים המוקשחים מיותרים) | ❌ |

## ‏סטיות מהתכנון
- ...
