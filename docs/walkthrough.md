# Walkthrough — brief-driven-slices

> ‏יומן-ביצוע כרונולוגי: ‏מה נבנה, ‏מתי, ‏ובאילו commits. ‏מתחזק ע"י אליעזר (executor).
> ‏"משעמם בכוונה": brief בוצע + ‏חריגות. ‏הרציונל וההחלטות → `docs/decisions/bds.md`.

---

## 2026-06-01 — slice-2-distillation: Commit 5 — שני gates: plan-gate + runtime-gate

ניסוח כללי-שיטה שעד כה לא היו מנוסחים מפורשות:

| קובץ | מה |
|------|------|
| `agents/mordechai.md` | §"שני gates" חדש: plan-gate (READY בלבד) + runtime-gate (GO/דחייה-מתועדת) + 2 anti-patterns חדשים |
| `agents/eliezer.md` | §"הכרז במפורש": חידוד — ציין verdict כלב **GO/PARTIAL/NO-GO** מפורש (runtime-gate) |
| `agents/yetro.md` | הערה: status==plan-verified מניח READY (plan-gate — חוזה קיים, לא לוגיקה חדשה) |
| `workflow.md` | §"שני gates" חדש בין שלב 6 ל-7 |

**אימות manual**: grep "plan-gate|READY" + "runtime-gate|GO" + "USABLE-AFTER-FIX" mordechai.md ✅.
grep "gate|אימות-נקי" workflow.md ✅. Forward-ref "plan-gate למטה" שורה 59 — נסגר ✅.
**חריגות**: אין. Gates = ניסוח כללים קיימים, לא לוגיקה חדשה.

---

## 2026-06-01 — slice-2-distillation: Commit 4 — פורמט דוח MD-front-matter

עדכון פורמט דוחות-אימות מ-JSON ל-MD עם YAML front-matter (מקור-אמת יחיד):

| קובץ | מה |
|------|------|
| `agents/avigail.md` | §"כתיבת דוח JSON" → §"כתיבת דוח MD עם front-matter" + הוראת ציטוט (double-quote ל-`:'\|`) |
| `agents/calev.md` | אותו דבר + אחוד עם docs/<slice>-verification-report.md |
| `agents/calev-heavy.md` | שלב 7: הפניה לפורמט החדש ב-calev.md |
| `docs/reports-format.md` | שכתוב: front-matter schema + ⚠️ הוראת ציטוט + backward-compat + טבלת שדות |
| `reports/README.md` (sub-repo) | עדכון נתיב `.json` → `.md` + הערת dual-format |

**אימות manual**: grep "front-matter" docs/reports-format.md ✅.
grep "double-quote|לצטט" agents/avigail.md ✅. grep "reports/.*\.md" agents/*.md ✅.
round-trip distill.py על fixtures.md: 3/3 avigail ✅.
**חריגות**: reports/README.md עודכן ישירות ב-main/reports/ (sub-repo פרטי, לא ב-git השיטה).

---

## 2026-06-01 — slice-2-distillation: Commit 3 — systemd timer + distill-run.sh + distill-prompt.txt

נוספו קבצי ה-wrapper + systemd לטיימר הזיקוק היומי:

| קובץ | מה |
|------|------|
| `scripts/distill-run.sh` | wrapper: טריגר כמותי → distill.py → worktree branch → מרדכי-אוטומטי |
| `scripts/distill-prompt.txt` | פרומפט למרדכי-אוטומטי (כולל "אסור לעשות merge") |
| `systemd/bds-distill.service` | Type=oneshot, ExecStart=$HOME/scripts/distill-run.sh |
| `systemd/bds-distill.timer` | OnCalendar=daily, Persistent=true |
| `systemd/README.md` | הוראות התקנה, שינוי סף, בדיקה ידנית, לוגים |

**אימות manual**: `bash -n scripts/distill-run.sh` ✅.
grep "אסור לעשות merge" scripts/distill-prompt.txt ✅. grep OnCalendar systemd/bds-distill.timer ✅.
systemd-analyze verify — לא זמין בסביבה (קובץ נקרא ידנית, syntax תקין).
**חריגות**: systemd-analyze לא זמין בcontainer — קריאה ידנית של ה-unit (תקין).

---

## 2026-06-01 — slice-2-distillation: Commit 2 — יומן גלובלי אבולוציית השיטה

נוסף `docs/methodology-evolution.md` — יומן גלובלי נדיר של התפתחות השיטה.
5 אירועים: יצירת הצוות (5 סוכנים + רציונל השמות + מה לא עבד), המעבר לפרויקט עצמאי,
פיצול calev→calev-heavy, שכבת הזיקוק (Commit הנוכחי, כולל פורמט+gates). + 5 עקרונות.

**אימות manual**: `test -f docs/methodology-evolution.md` ✅. grep "merge|זיקוק|calev-heavy" ✅.
**חריגות**: אין.

---

## 2026-06-01 — slice-2-distillation: Commit 1 — פורמט דוח-זיקוק + קטלוגים + traceability

נוספו קטלוגים ותבניות לשכבת הזיקוק:

| קובץ | מה |
|------|------|
| `distillations/README.md` | הסבר שכבת הזיקוק, מבנה, טריגר, חלוקה כמותי/איכותני |
| `distillations/.gitkeep` | שמירת תיקייה ב-git |
| `distillations/TEMPLATE-report.md` | תבנית 4-חלקים לדוח זיקוק (מבט-לאחור, התפלגות, חדשות, עדכוני-קטלוג) |
| `plan-pitfalls.md` | קטלוג טעויות-תכנון (אביגיל) — 2 קטגוריות + traceability מקורות |
| `patterns.md` (עדכון) | שורה 2: "+ זיקוק אוטומטי מ-reports/"; סעיף Traceability בסוף |

**אימות manual**: `test -f plan-pitfalls.md && test -f distillations/TEMPLATE-report.md` ✅.
grep "הנחה לא-מאומתת" plan-pitfalls.md ✅. grep "מקורות" patterns.md ✅.
**חריגות**: אין.

---

## 2026-06-01 — slice-2-distillation: Commit 0 — distill.py מנוע כמותי + tests

בוצע TDD (red→green). הוקמה תשתית הזיקוק הכמותי: `scripts/distill.py`,
`tests/test_distill.py` (37 טסטים), `tests/fixtures/sample-reports/` (4 fixtures md + 1 json).

| קובץ | מה |
|------|------|
| `scripts/distill.py` | מנוע כמותי: parse_report_file (dual-format .md/.json), load_reports (סלחני), count_by_severity_category, compute_hitrate, traceability_index, flag_noncanonical, compute_delta, count_new_reports_since, build_data, main (CLI) |
| `tests/test_distill.py` | 37 unittest: כל פונקציה, כולל: dual-format, date normalization, summary-עם-נקודתיים, סלחנות (None ב-broken yaml/json/no-fm), threshold trigger |
| `tests/fixtures/sample-reports/projA/*.md` | 2 fixtures md בפורמט חדש (YAML front-matter) |
| `tests/fixtures/sample-reports/projA/slice-3-calev.json` | 1 fixture json פורמט ישן (backward-compat) |
| `tests/fixtures/sample-reports/projB/*.md` | 2 fixtures md (avigail + calev עם mode/dod_items) |

**אימות**: `python3 tests/test_distill.py` → 37/37 ✅.
`distill.py --check-only --threshold 999` → exit 1 ✅; `--threshold 0` → exit 0 ✅.
`git check-ignore tests/fixtures/sample-reports/...` → ריק ✅ (לא נתפס ע"י gitignore).
**חריגות**: אין.

---

## 2026-05-29 — ‏בניית מערכת האורקסטרציה (commits 03b1a6d→1f9308c, ‏ב-my-skills)

‏אליעזר בנה את התשתית הראשונית של מערכת ה-5 ‏סוכנים, ‏לפי `orchestration-design.md`
‏(שעבר 4 ‏סבבי אביגיל). 6 ‏commits:

| Commit | ‏מה | ‏קבצים |
|--------|------|--------|
| `03b1a6d` | Commit 0 — scripts | dispatch-executor.sh, wait-for-slice.sh, install-agents.sh, cleanup_state.py, discard_chain.py |
| `265f429` | Commit 1 — 5 ‏סוכנים | agents/{mordechai,yetro,eliezer,avigail,calev}.md |
| `2f38d53` | Commit 2 — state + orchestration | state.template.json, orchestration.md |
| `755bdc2` | Commit 3 — בית יתרו | orchestration-project/ template |
| `f6bf30f` | Commit 4 — SKILL + briefs | SKILL.md, BRIEF_TEMPLATE, EXECUTOR_DISPATCH, ‏מחיקת סוכנים ישנים |
| `1f9308c` | Commit 5 — README + walkthrough | README, docs/walkthrough |

‏אימות: GO, 16/16 DoD (דוח ב-`/tmp/orchestration-verification-report.md`).

**‏מאפיינים מרכזיים שנבנו**: env scrub מלא (prefix OPENCODE_*), ‏prompt דרך stdin,
‏BLOCKED דרך קיום-קובץ (לא exit code), ‏JSON state + python3 stdlib, ‏שרשור worktrees,
‏flock נגד שני יתרו, ‏discard_chain (dependents בלבד), ‏4 ‏מצבי טיפול-כשל.

---

## 2026-05-30 — slice bds-extraction: ‏הוצאה לפרויקט נפרד + ‏שכבת דיווח

‏העברת brief-driven-slices מ-`~/projects/my-skills/` ‏לפרויקט עצמאי
‏`~/projects/brief-driven-slices/` ‏עם git משלו, + ‏שכבת דיווח-בקבצים + ‏2 ‏יומנים.
‏Mode 3 ‏(ידני, ‏לא דרך יתרו). brief עבר 2 ‏סבבי אביגיל (5+1 ‏ממצאים, ‏כולם תוקנו).

| Commit | ‏מה |
|--------|------|
| `32ea702` | Commit A — ‏העברה: ‏git init חדש, ‏עדכון 12 ‏נתיבי my-skills, symlinks (skill + 5 agents) למיקום חדש |
| `50fbce4` | Commit B — outcomes: ‏אליעזר כותב `outcomes/<slice>.json` ‏תמיד (אופציה A); ‏יתרו בודק אותו ראשון; discard_chain.py blocked→outcomes |
| `07f43dd` | Commit C — דוחות מתויגים: avigail write:true + JSON ל-`reports/<project>/`; calev JSON בנוסף ל-MD; ‏טקסונומיה severity/category |
| `ea7aa38` | Commit D — ‏הפרדת יומנים: walkthrough=ביצוע (אליעזר), decisions/<project>.md=רציונל (מרדכי) |
| `c6513b8` | Commit E — ‏תיעוד 2 ‏סטיות (SOUL.md, ‏סוכנים ישנים) ב-decisions/bds.md |

**‏חריגות/הערות**:
- ‏מחיקת התיקייה הישנה ב-my-skills (`git rm`) — ‏הצעד האחרון, ‏commit נפרד ב-my-skills, ‏רק אחרי grep נקי.
- ‏calev tier: heavy (complexity 8) — ‏smoke של opencode run + ‏בדיקת symlinks + grep נקי.
- ‏מה שלא נכנס (brief שני, ‏עתידי): ‏קטלוגים תמציתיים, ‏זיקוק תקופתי, ‏טקסונומיה מתפתחת, ‏יומן גלובלי.
