# ‏אורקסטרציה — יתרו והלולאה הלילית

‏מסמך זה מסביר כיצד שכבת האורקסטרציה עובדת, ‏כולל state machine, ‏שרשור worktrees, ‏טיפול בכשלים, ‏ומנגנון BLOCKED.

‏למידע מלא על תכנון המערכת: `docs/plans/orchestration-design.md`

---

## §1 — ‏שלושת מצבי ‏ההפעלה

### Mode 1 — ‏סינכרוני (‏מרדכי → ‏אליעזר ישיר)

```
‏המשתמשת → ‏מרדכי: "‏בצע slice X"
‏מרדכי → Task(subagent_type="eliezer", ...)   [‏חוסם]
‏אליעזר מבצע, ‏מפעיל כלב (verifier), ‏מחזיר
‏מרדכי מציג למשתמשת → ‏המשתמשת מאשרת → ‏מרדכי עושה merge
```

‏אין שימוש ב-state.json. ‏מהיר, ‏אינטראקטיבי.

### Mode 2 — ‏לילי (‏יתרו מריץ queue)

```
‏ערב:   ‏המשתמשת + ‏מרדכי כותבים briefs, ‏אביגיל מאמתת, ‏מסמנים dispatch_ready=true ב-state.json
‏לילה:  ‏המשתמשת פותחת session יתרו → "‏הרץ את ה-queue"
         ‏יתרו: ‏ניקוי → ‏מוצא slice dispatch-ready → tmux dispatch אליעזר → poll
               → ‏כלב verifier GO → ‏ארכב brief → ‏slice הבא
‏בוקר:  ‏המשתמשת פותחת session מרדכי → ‏קורא summary → ‏עושה merges מאושרים
```

‏state.json מנוהל לאורך כל הלילה. ‏אסינכרוני.

### Mode 3 — ‏ישיר (‏המשתמשת → ‏אליעזר)

```
‏המשתמשת → session אליעזר ישיר: "‏בצע docs/plans/slice-X.md"
‏אליעזר מבצע ישירות
```

‏לגיטימי אבל לא המסלול הראשי. ‏אליעזר עדיין לא ממזג.

---

## §2 — ‏הצוות

| ‏שם | ‏תפקיד | ‏Mode | ‏מודל | merge? |
|-----|-------|-------|------|--------|
| **‏מרדכי** | planner | primary | Opus | ✅ ‏אחרי אישור |
| **‏יתרו** | orchestrator | primary | Sonnet | ❌ ‏לעולם לא |
| **‏אליעזר** | executor | all | Sonnet | ❌ ‏לעולם לא |
| **‏אביגיל** | plan-verifier | subagent | Opus | ❌ |
| **‏כלב** | runtime-verifier | subagent | Sonnet | ❌ |

---

## §3 — STATE Schema (JSON)

‏מיקום: `~/.local/state/brief-driven-slices/<project>/state.json`

‏פרסור: `python3 -c "import json"` ‏(stdlib, תמיד זמין). ‏אין yq, ‏אין PyYAML.

### ‏שדות slice

| ‏שדה | ‏סוג | ‏מי כותב | ‏משמעות |
|------|------|---------|---------|
| `id` | string | ‏מרדכי | ‏מזהה ייחודי |
| `name` | string | ‏מרדכי | ‏שם קריא |
| `status` | string | ‏ראה טבלה | ‏סטטוס נוכחי |
| `brief` | string | ‏מרדכי | ‏נתיב ל-brief (‏יחסי ל-repo_root) |
| `plan_verified` | boolean | ‏מרדכי | ‏אביגיל אישרה? |
| `depends_on` | array | ‏מרדכי | ‏IDs שה-slice תלוי בהם (‏חובה) |
| `dispatch_ready` | boolean | ‏מרדכי | ‏מוכן ליתרו? |
| `base` | string | ‏יתרו/מרדכי | branch ‏שממנו נגזר |
| `branch` | string\|null | ‏יתרו | branch ‏שנוצר |
| `worktree` | string\|null | ‏יתרו | ‏נתיב ל-worktree |
| `started` | string\|null | ‏יתרו | ‏timestamp ‏של dispatch |

### ‏ערכי status

| status | ‏מי מסמן | ‏משמעות |
|--------|---------|---------|
| `planned` | ‏מרדכי | ‏רעיון, ‏אין brief |
| `brief-ready` | ‏מרדכי | brief ‏נכתב |
| `plan-verified` | ‏מרדכי | ‏אביגיל אישרה |
| `in-progress` | ‏יתרו | ‏אליעזר פעיל ב-tmux |
| `verified` | ‏יתרו | ‏כלב אישר (GO) |
| `merged` | ‏מרדכי | ‏מוזג ל-dev |
| `needs-revision` | ‏יתרו | ‏כלב סירב |
| `blocked` | ‏יתרו | ‏אליעזר כתב outcomes/<slice>.json עם status=blocked |
| `blocked-by:<id>` | ‏יתרו | ‏תלות שלו נכשלה |
| `timed-out` | ‏יתרו | ‏אין heartbeat > 2h |
| `crashed` | ‏יתרו | tmux ‏מת ללא sentinel |
| `failed:infra` | ‏יתרו | exit ≠ 0 (‏קריסת opencode) |
| `discarded` | ‏מרדכי | ‏נזרק ידנית |

---

## §4 — ‏שרשור Worktrees

‏לב המערכת: ‏slices תלויים יכולים לרוץ על branch של תלות, ‏גם לפני שהיא נמרגה ל-dev.

### ‏הכללים

```
‏כל depends_on ∈ {merged} → base = "dev"
‏יש תלות ∈ {verified} (לא merged) → base = branch של אותה תלות
```

### ‏דוגמה: A→B→C

```
‏לילה ראשון:
  dispatch A (base=dev, branch=slice/A, dir=.worktrees/A)
  → calev GO → status=verified (branch slice/A בחיים)
  → base של B נקבע = slice/A
  dispatch B (base=slice/A, branch=slice/B, dir=.worktrees/B)
  → B בנוי על קוד של A, גם אם A לא ב-dev עדיין

‏בוקר:
  ‏מרדכי ממזג: A → dev (git merge --no-ff slice/A) → git push
  ‏מרדכי ממזג: B → dev (git merge --no-ff slice/B) → git push
```

‏הכלל: ‏חייב merge commits (לא squash) ‏בשרשרת, ‏אחרת git מכפיל commits של A ‏כשממזג B.

---

## §5 — ‏מנגנון BLOCKED + COMPLETED (outcomes)

‏אליעזר כותב **תמיד** ‏ב-Mode 2 (‏מזהה לפי `$BDS_SLICE` מוגדר). ‏קובץ outcomes הוא ה-signal:

**‏בסיום מוצלח**:
```bash
cat > "$BDS_STATE_DIR/outcomes/$BDS_SLICE.json" << 'EOF'
{
  "slice": "<id>",
  "status": "completed",
  "commits": "<base>..HEAD",
  "calev_report": "<path or inline verdict>",
  "deviations": [],
  "notes": ""
}
EOF
```

**‏בחסימה** (BLOCKED):
```bash
cat > "$BDS_STATE_DIR/outcomes/$BDS_SLICE.json" << 'EOF'
{
  "slice": "<id>",
  "status": "blocked",
  "issue": "<one sentence>",
  "source": "<file:line | brief section>",
  "tried": "<what you tried>",
  "need": "<decision? new spec? skip?>"
}
EOF
```

‏יתרו בודק `outcomes/<slice>.json` ‏**‏לפני** ‏exit code:
- ‏לא קיים → crashed (‏אליעזר לא סיים לכתוב — קריסה שקטה)
- status==blocked → status=blocked, ‏לא מריץ כלב
- status==completed → ‏המשך לבדיקת exit code, ‏אז הרץ כלב

**‏למה לא exit code בלבד**: `opencode run` ‏תמיד מחזיר exit 0. ‏outcome-file הוא ה-signal.

---

## §6 — ‏ארבעה מצבי כשל (‏לבוקר)

| ‏מצב | ‏מתי | ‏פעולת מרדכי |
|------|------|--------------|
| **‏מזג-מה-שעבד** | A ‏עבר, B ‏ומעלה נכשלו | merge A, discard B+ |
| **‏תקן-במקום** | 90% ‏טוב, ‏תיקון קטן | ‏כנס ל-worktree, ‏תקן, ‏הרץ כלב שוב |
| **‏זרוק-הכל** | ‏כל השרשרת עקומה | `python3 scripts/discard_chain.py <project> A` |
| **‏מזג-הכל** | ‏הכל עבר | merge A→B→C ‏ל-dev ‏בסדר |

---

## §7 — ‏State Directory (‏פר פרויקט)

```
~/.local/state/brief-driven-slices/<project>/
├── state.json                    # ‏ה-state machine
├── yetro.lock                    # flock ‏נגד שני יתרו
├── dispatches/<slice>.prompt     # ‏ה-prompt שנשלח
├── logs/<slice>.log              # ‏stdout/stderr
├── sentinels/<slice>.done        # exit code
├── outcomes/<slice>.json         # ‏תמיד — completed | blocked (היעדר = קריסה שקטה)
├── heartbeats/<slice>.last       # ‏timestamp פר commit
├── crashes/<slice>-<ts>.log      # crash logs
└── archived/                     # ‏אחרי merge
```

---

## §8 — ‏הסקריפטים

| ‏סקריפט | ‏שפה | ‏מי קורא | ‏תפקיד |
|---------|------|---------|--------|
| `scripts/dispatch-executor.sh` | bash | ‏יתרו | tmux + env scrub + sentinel |
| `scripts/wait-for-slice.sh` | bash | ‏יתרו | ‏poll + crash/timeout detection |
| `scripts/install-agents.sh` | bash | ‏משתמשת | עותקים (path-substitution לפי `paths.env`) ל-~/.config/opencode/agents/ |
| `scripts/cleanup_state.py` | python3 | ‏יתרו | ‏ניקוי תחילת סשן |
| `scripts/discard_chain.py` | python3 | ‏מרדכי | ‏זריקת שרשרת בטוחה |

---

## §9 — ‏התקנה ראשונה

> **‏עקרון path-neutral**: `<bds>` ‏למטה = שורש ה-checkout ‏שלך ‏של brief-driven-slices
> (‏כל נתיב-מכונה קונקרטי — ‏כולל BDS_ORCH ‏שאתה בוחר כאן — ‏חי **‏רק** ‏ב-`paths.env`
> ‏פר-מכונה, ‏לא ‏במקור-האמת. ‏ראה `cli-configs/paths.env.example`).

```bash
# ‏צור state dir לפרויקט
mkdir -p ~/.local/state/brief-driven-slices/<project>
cp <bds>/briefs/state.template.json \
   ~/.local/state/brief-driven-slices/<project>/state.json
# ‏ערוך state.json לפי הפרויקט

# ‏צור פרויקט הבית של יתרו (מ-template) — ‏זה יהיה ‏ה-BDS_ORCH ‏שלך
cp -r <bds>/orchestration-project/ \
      <path-לבחירתך>/orchestration/
# ‏ערוך projects.json

# ‏הגדר paths.env פר-מכונה (BDS_REPORTS/BDS_SCRIPTS/BDS_LESSONS/BDS_ORCH)
cp <bds>/cli-configs/paths.env.example ~/.config/bds/paths.env
# ‏ערוך את 4 הנתיבים ‏ב-paths.env

# ‏התקן את הסוכנים (אחרי בדיקה!) — ‏מחליף {{BDS_*}} ‏לפי paths.env, ‏כשל-רועש ‏אם חסר
bash <bds>/scripts/install-agents.sh
```
