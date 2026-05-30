# Case Study: voice-acp Slices 2, 3, 8, 11, 14 — ‏הצורה החדשה עובדת

> **‏תאריך**: ‏מאי 2026, 28-29
> **‏פרויקט**: voice-acp (drive-coding)
> **Slices**: 2 (Speaker TTS), 3 (Mic + VoiceMode), 8 (Session Picker), 11 (Audio Prompt), 14 (Generic Injector), testing-coverage
> **‏Planner**: Tama (Opus 4.6/4.7)
> **‏Executors**: Sonnet 4.6 + Opus 4.7 (‏מעורב)
> **‏Verifiers**: plan-verifier (3 ‏שרצו), slice-verifier-light (4), phase-verifier (1)

‏המקרה שמתקיים בניגוד ל-`case-studies/2026-05-slice-9-frontend-refactor.md`.

---

## 1. ‏מה שונה הפעם

‏ב-Slice 9 (‏מקרה השבירה): TDD ‏אוניברסלי, ‏אין plan verifier, ‏slice verifier ‏רק אחרי 14 commits. ‏תוצאה: 19 + 7 + 4 = **30 ‏באגים**, 12 ‏שעות עבודה + ‏תיקונים.

‏ב-voice-acp slices ‏החדשים:

- ‏Per-commit testing strategy (tdd/integration/manual/none) ‏שhplanner ‏קובע
- ‏Plan verifier ‏לפני handoff (‏מצא 100% ‏מהbריפים)
- ‏Slice verifier-light חובה בסוף
- Worktree ‏ייעודי ‏לכל slice ‏(parallel-safe)
- EXECUTOR_DISPATCH.md ‏כ-boilerplate משותף

‏תוצאה: **‏0 ‏באגים אמיתיים ב-verification** ‏על ‏פני 5 slices.

---

## 2. ‏הסשנים

| ‏תפקיד | Slice | Session ID | ‏מודל |
|--------|-------|------------|------|
| Planner (Tama) | ‏כל | `ses_18c005b36ffeT2R3Z1H5n412Sz` | Opus 4.7 |
| ‏שיחה ראשונית | ‏כל | `ses_190d11126ffeuEe3lN17v5QCYw` | Opus 4.7 |
| Plan verifier | 14 | `ses_18c1b891fffe4QKBjmvEKmcr16` | Sonnet 4.6 |
| Plan verifier | 8 | `ses_18c30bcc0ffe27yDVQ0oJOQciT` | Sonnet 4.6 |
| Plan verifier | 6 | `ses_18d5a48b0ffeNmFTO1NPF5WyRB` | Sonnet 4.6 |
| Executor | 3 | `ses_18d6125a9ffe1h0xhrFPKzzJeX` | Sonnet 4.6 |
| Executor | 8 (sub-agent) | `ses_18c26d1ecffemND5Dy6OC8lxMN` | Sonnet 4.6 |
| Executor | 8 (orchestrator) | `ses_18c295df5ffeTmIdzFrnDsdKSE` | Opus 4.7 |
| Executor | 11 | `ses_18d60cae9ffezQ0O8UYCBvEfrb` | Sonnet 4.6 |
| Executor | 14 | `ses_18c1b5cadffecOQ3m9YkYFLQUv` | Opus 4.7 |
| Executor | testing-cov | `ses_18f434f1cffehHeVxxlbayywaB` | Opus 4.7 |
| Phase verifier | 3 commit 2 | `ses_18d5b7978ffeEmC4CGVoNhKAr0` | Sonnet 4.6 |
| Slice-light | 3 | `ses_18d56e8b8ffe4eUxKY01r2yPqg` | Sonnet 4.6 |
| Slice-light | 8 | `ses_18c1f54f5ffevSaLXnSWJF87Yd` | Sonnet 4.6 |
| Slice-light | 11 | `ses_18d59860fffe6lyichhSng1gUa` | Sonnet 4.6 |
| Slice-light | 14 | `ses_18c0e9503ffeuw2MIjdnfDofsD` | Sonnet 4.6 |

---

## 3. ‏מה Plan Verifier ‏תפס

‏9 ‏בעיות ב-3 ‏briefs (avg 3/brief, 100% hit rate):

### slice-14 plan verification

| ‏חומרה | ‏סוג | ‏פירוט |
|--------|------|--------|
| 🔴 | API mismatch / regression risk | Commit 2 pseudo מחסיר את הענף `typeof config.plugin === "string"` ‏מ-`plugin-config.ts:28-30`. ‏executor יעתיק verbatim → silent regression ל-users עם `plugin: "single-string"` |
| 🟡 | wasted work | Commit 0 ‏(verification של PluginModule type) ‏מיותר — ‏ה-API מתועד ב-`dist/index.d.ts` |
| 🟡 | TS error חסר | Commit 2 pseudo: `config.$schema ?? "..."` ‏ללא `as string` ‏מתחת ל-`noUncheckedIndexedAccess` |

### slice-8 plan verification

| ‏חומרה | ‏סוג | ‏פירוט |
|--------|------|--------|
| 🔴 | API ‏לא קיים | `deleteAgent` ‏ב-`adapters/agents-api.ts` — main מייצא, ‏**dev לא**. brief מניח שקיים. ‏executor יתקע ב-Commit 0 |
| 🟡 | naming inconsistency | `listSessionsViaTempAgent` ‏ב-§2 ‏vs `listSessionsForCwd` ‏ב-§4 — ‏זהה |
| 🟡 | pseudo skeleton | Commit 1 skeleton ‏הוא pseudo (`// ‏אותו setup כמו attach`), ‏executor יעתיק ~35 ‏שורות ‏ולא ידע מה לשמור |
| 🟡 | line count שגוי | "75 ‏שורות" ‏ב-`sessions-ws.ts` ‏בפועל 82 |

### slice-6 plan verification

| ‏חומרה | ‏סוג | ‏פירוט |
|--------|------|--------|
| 🔴 | false claim | brief ‏טוען ש"stub ל-cues סומן ב-context.ts" — ‏בפועל יש stubs ל-mic/voice-mode/car-mode, ‏אין ל-cues |
| 🟡 | outdated risk | Risk #8 + Escalation #1 מבוססים על "vitest config FE ‏אולי לא יטפל ב-`.test.ts`" — ‏ה-glob כבר כולל |
| 🟡 | confused structure | ‏שני "Commit 2" + ‏רפלקציה עצמית בתוך brief |

### ‏סיכום

| ‏קטגוריה | ‏מס' |
|---------|-----|
| API/symbol לא קיים | 1 |
| False claim על stub/code state | 1 |
| Pseudo code מחסיר branch קיים | 1 |
| Pseudo code עם type error | 1 |
| Naming inconsistency | 1 |
| Line count factually wrong | 1 |
| Outdated risk/escalation | 1 |
| Wasted research commit | 1 |
| Confused structure | 1 |

‏ROI: ~‏10 ‏דק' פר verifier, ‏חיסכון 30-60 ‏דק' debug + ‏מנע ‏regression שקט אחד.

---

## 4. ‏מה Slice Verifier ‏Light תפס

**‏0 ‏באגים אמיתיים בקוד** ‏באף אחד מ-4 ‏ה-slices.

‏מה כן הוא תפס:

| Slice | ‏מה | ‏סווג |
|-------|-----|------|
| 8 | brief ‏טעה: claude אינו ACP-compliant. ‏המשתמשת התערבה ‏וhverifier ‏עבר ל-opencode | Brief assumption ‏שגויה |
| 3 (phase 2) | Speaker/thinking order swap | Deviation מבוררת |
| 14 | MD5 hash check אישר byte-identical | ‏ראיה ל-behavior parity |
| 11 | `output.system.push()` ‏ולא `unshift()` (‏קריטי לcache) — ‏אומת | Spot check ‏שעבר |

**False positives**: ‏אפס. ‏slice-8 ‏סימן smoke ⚠️ ‏אבל מיד הסביר שזה pre-existing infra (חסר playwright ב-worktree, ‏לא regression). ‏ניתוח נכון.

**False negatives**: ‏אין עדות. ‏כל ה-APPROVED slices ‏זכו לפיתוח המשך ללא ‏regression מדווחת.

### ‏זמן

- slice 11 (static): ~‏10-12 ‏דק' — ‏לפי היעד
- slice 3 (static): ~‏10-12 ‏דק' — ‏לפי היעד
- slice 14 (‏עם BE+FE+smoke): ~‏20-25 ‏דק' — ‏מעט מעל היעד
- **slice 8: ~‏30-40 ‏דק'** — ‏חרג כי brief טעה ב-CLI choice (claude vs opencode)

---

## 5. ‏הבדל Opus vs Sonnet ‏כ-executor

‏לא רק עלות (Opus עולה פי 10 ‏לפי `~/.config/opencode/learnings.md` 2026-05-16).
‏הבדל באיכות התנהגותית:

### Opus ‏(slices 14, testing-cov)

- ‏פותח BE + FE + tunnel ‏ומריץ smoke ‏אמיתי
- ‏בודק BE logs לתפוס plugin failures
- **‏משנה גישה כשנתקע** — testing-coverage commit 2 (cache-replay): ‏זיהה ש-LLM ‏non-deterministic ‏שובר את ה-plan, ‏ושכתב את ה-smoke לגישה אחרת (browser fetch ‏עם NONCE). ‏תיעד למה.

### Sonnet ‏(slices 3, 11)

- ‏מסתפק ב-"typecheck + lint + test ‏ירוקים"
- ‏לא פותח דפדפן
- **‏נדבק ב-pattern ‏הראשון** — slice 11 ‏בילה 12 ‏הודעות באותה שגיאה על core dist
- ‏מבקש מהמשתמשת לבדוק ידנית (slice 11 #77: "‏נשאר לך לבדוק ידנית")

### ‏התצורה שעבדה הכי טוב

**Opus orchestrator + Sonnet executor sub-agent** (slice 8): Opus dispatched, Sonnet ‏ביצע 5 commits ב-59 ‏הודעות נקיות. ‏אף sub-agent delegation שגוי לא קרה.

---

## 6. ‏Gotchas ‏חדשים שזוהו

‏עדכון ל-`recommendations.md` ‏ול-EXECUTOR_DISPATCH:

### 6.1 core dist missing אחרי worktree

‏Typecheck נכשל ‏עם TS6305 ב-incremental cache. ‏Sonnet (slice 11) ‏בילה 12 ‏הודעות; Opus פתר ב-1 ‏עם `pnpm build --force`.

### 6.2 Worktree path mistake

‏Opus יצר ב-`dev/.worktrees/` ‏במקום ב-`.worktrees/` ‏הראשי ‏פעמיים (slices 14, testing-coverage). ‏זיהה ‏ותיקן עצמאית, ‏אבל זמן מבוזבז. ‏פתרון: absolute path.

### 6.3 claude אינו ACP-compliant

‏ה-WS ‏נסגר עם code 1005 ‏מיד אחרי initialize. ‏slice-8 brief ‏ביקש לטסט עם claude. ‏ה-verifier ‏היה צריך לעבור ל-opencode עצמאית.

---

## 7. ‏מה עדיין לא נסגר

‏גם בצורה החדשה, ‏הסיכונים האלה נשארים:

1. **Executor ‏עדיין לא פותח דפדפן ב-default** — Sonnet ספציפית. ‏יש להוסיף ל-prompt של executor.
2. **Cross-store data flow risk** — ‏הקטגוריה הכי מסוכנת ב-Slice 9 (5/8 ‏מהקריטיים). ‏tests-per-commit ‏לא חוצים. ‏צריך integration test ‏מפורש בbrief.
3. **dev/main parity לא נבדק אוטומטית** — 3/3 ‏briefs ‏הניחו symbols ‏מ-main. ‏הוסף ל-plan-verifier: `grep symbols ב-dev`.
4. **Brief assumption ‏שגוי = ‏executor שגוי** — claude/opencode זוהה ‏רק כי המשתמשת התערבה. ‏לא תפס אוטומטית.
5. **Architectural drift** — ‏אין מנגנון אוטומטי. ‏רק brief מפורש ‏+ verifier על DoD.

---

## 8. ‏השוואה כמותית

| ‏מדד | Slice 9 (‏ישנה) | 5 slices ‏חדשים | ‏Delta |
|------|-----------------|-------------------|--------|
| ‏באגים ב-verification | 30 | 0 ‏אמיתיים | −30 |
| ‏זמן עד approved | ~‏12 ‏שעות + סבבי תיקון | ~‏1-2 ‏שעות + verifier | −85% |
| ‏"סיימתי" false positive | ‏מובהק (114 ‏טסטים ירוקים) | ‏אפס | — |
| Plan verifier hit rate | ‏לא היה | 100% (3/3) | +∞ |
| Sub-agent delegation שגוי | ‏היה | ‏אפס מקרים נצפו | — |

---

## 9. ‏הלקח המטא

‏מה שעבד הוא לא verifier ‏יחיד — ‏זה **‏שכבות verification ‏עם תפקידים שונים**:

1. **plan verifier** — ‏לתפוס בעיות במסמך לפני handoff (ROI ‏הכי גבוה)
2. **phase verifier** — ‏לתפוס בעיות ב-commit ‏ספציפי מסוכן (ROI ‏שולי אם plan verifier ‏איכותי)
3. **slice verifier light** — ‏לסגור DoD ‏בסוף (‏ביטוח חובה)

‏ולא פחות חשוב: **‏הזזת האחריות מ-"Sonnet ‏יחליט נכון" ‏ל-"planner ‏יחשוב מראש מה הסיכון בכל שלב"**.

‏ב-Slice 9, ‏Sonnet בחר לבד מה לטסט (TDD universal → ‏טסטים שלא תופסים).
‏בvoice-acp ‏החדש, Tama קובעת ‏פר-commit ‏את ה-approach.
