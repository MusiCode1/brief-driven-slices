# המלצות — שינויים ל-brief template ול-pipeline

> מבוסס על 5 הקטגוריות ב-`patterns.md`. כל המלצה מסומנת באיזו קטגוריה היא מטפלת.

---

## 1. DoD חייב להיות ויזואלי, לא test-based

**מטפל ב:** קטגוריות 1, 3, 5

**הבעיה:** "כל הטסטים ירוקים" לא מעיד על כלום. ב-Slice 9 — 114 טסטים ירוקים,
19 באגים בפועל.

**הפתרון בתבנית ה-DoD:**

```markdown
## DoD

- [ ] `pnpm typecheck` + `pnpm lint` + `pnpm test` ירוקים
- [ ] **לכל phase שמשפיע על UI** — screenshot ב-`/tmp/<slice>/<phase>.png` +
      השוואה ל-mockup. הצמד screenshot לcommit message.
- [ ] **e2e flow ידני מלא** — את כל ה-feature: פתח דפדפן, הרץ את התרחיש
      הראשי מקצה לקצה. כל פעולה מהמפרט חייבת לעבוד. רשום אילו flows רצת.
- [ ] **Mobile + desktop** — וודא ששני ה-viewports עובדים. צלם את שניהם.
- [ ] **Mockup compliance audit** — phase ייעודי בסוף (ראה סעיף 4).
```

ה-`pnpm test` הוא תנאי **הכרחי, לא מספיק**. הוא מבטיח שהקוד מתקמפל ו-units
שעבדו לא נשברו. הוא לא מבטיח שהפיצ'ר עובד.

---

## 2. סעיף "Anti-patterns ידועים" בכל brief

**מטפל ב:** קטגוריות 1, 2, 4

**הבעיה:** Executor נופל בדפוסים חוזרים שכבר תועדו, כי ה-brief לא מתריע עליהם.

**הפתרון:** template section שמועתק לכל brief, ומותאם לתחום הספציפי. דוגמה:

```markdown
## Anti-patterns ידועים — אל תעשה

### Bubble grouping / streaming text
- ❌ לעולם לא `bubble.segments.push(newSegment)` כשמדובר ב-same-kind same-messageId.
  ✅ במקום: append ל-`text` של ה-segment האחרון שב-streaming.

### Cross-store data flow
- כל פעם ש-Store A מייצר metadata ו-Store B מציג — חובה לתעד את הגשר ב-brief.
- ❌ לעולם לא `someFunction(realArg1, null)` — `null` כפלייסהולדר ל-id ש"נמלא
  אחר כך" כמעט תמיד נשכח. אם הערך לא זמין — restructure.

### Library / framework conflicts
- ❌ `lucide.createIcons()` ב-Svelte → מערבב DOM, יוצר icons כפולים.
  ✅ השתמש ב-`lucide-svelte` npm package (inline SVG).
- (להוסיף עוד אחרי כל case study)

### Refactor vs rebuild
- אם ה-brief אומר "הסר X" — לרוב יש block קונקרטי למחיקה. **חפש אותו ומחק לחלוטין**.
  אל תוסיף flag מעליו.
```

הסעיף הזה גדל מ-case study ל-case study. כל פעם שמתגלה דפוס — מתעדכן ב-`patterns.md`
ומועתק/מותאם ל-brief הבא.

---

## 3. תיעוד מפורש של כל data bridge

**מטפל ב:** קטגוריה 2 (הגדולה ביותר).

**הפתרון:** בכל brief שיש בו יותר מ-store אחד או יותר מ-module אחד, להוסיף section:

```markdown
## Data Flow Bridges

לכל זוג (Producer, Consumer) — מנגנון מפורש:

| Producer | Consumer | Data | Mechanism | קובץ:שורה |
|----------|----------|------|-----------|-----------|
| ‏WS: audio_chunk | agent-session.bubbles | originalText, translatedText | `voice-session.handleAudio()` קורא ל-`agentSession.addTranslatedSegment(messageId, ...)` | voice-session.ts:67 |
| ‏WS: audio_chunk | player | messageId | `+page.svelte:51` — pass `meta.messageId` ל-`player.addSegment` (לא null) | +page.svelte:51 |
| ‏agent-orchestrator.create() | projects-registry | cwd | קריאה ל-`projectsRegistry.recordCwd(cwd)` אחרי spawn | orchestrator.ts:create |

חובה: לכל שורה בטבלה — integration test שעובר על שני הצדדים יחדיו.
```

זה גם מאלץ את ה-planner לחשוב על הגשרים מראש, וגם נותן ל-executor רשימת
checks ספציפית.

---

## 4. Phase ייעודי: "Mockup Compliance Audit"

**מטפל ב:** קטגוריות 3, 5

**הפתרון:** במקום להניח שכל phase יישם את ה-mockup שלו — להוסיף phase אחרון
ייעודי:

```markdown
### Phase N+1 — Mockup Compliance Audit

(תמיד אחרון. אסור לדלג.)

**מטרה:** וודא שה-UI בפועל **זהה** ל-mockup, view-by-view.

**משימות:**
1. פתח דפדפן ב-mobile viewport (390×844). צלם כל route.
2. פתח דפדפן ב-desktop viewport (1280×800). צלם כל route.
3. ‏Open mockup files (final.html). עבור על כל view במקביל לscreenshot.
4. לכל divergence — תקן או תעד למה הוחלט אחרת.
5. flows ידניים: הקלטה→STT→ACP→TTS, click bubble→play, navigate sessions, וכו'.

**Tests:** ויזואלי בלבד. אין test runner.

**DoD:** screenshot per route per viewport + table:

| ‏Route | Mobile | Desktop | Divergences |
|-------|--------|---------|-------------|
| / | ✅ | ✅ | none |
| /agent/[id] | ⚠️ | ❌ | desktop header ישן |

**Commit:** `chore(frontend): Phase N+1 — mockup compliance audit`
```

ב-Slice 9, אם ה-phase הזה היה קיים, היו נתפסים מראש: B4, B11, N1, N2, N3, B6.

---

## 5. הוראות "הסר X" קונקרטיות

**מטפל ב:** קטגוריה 3

**הפתרון:** בכל brief, כל פעם שיש מחיקה — לתת file:line ספציפי, לא תיאור.

**במקום:**
> ‏Remove the textbox + send button from the agent page.

**לכתוב:**
> ‏DELETE block: `packages/frontend/src/routes/agent/[id]/+page.svelte`,
> lines 468–490 (the `<form class="text-form">` block).
> וודא שאין import-ים שנותרו ללא שימוש.

זה דורש מה-planner קצת יותר עבודה (לקרוא קוד קיים בזמן כתיבת ה-brief),
אבל מונע 100% של "Sonnet שכח למחוק".

---

## 6. Verifier Agent Design

**מטפל ב:** הקטגוריות שלא ניתן לחזות מראש (מטא-תופעה).

**עקרון יסוד:** investigation (קריאת קוד + צפייה) ≠ verification (הרצת flows אמיתיים).
שניהם נחוצים. ה-verifier הוא **שלב נפרד**, לא תוספת ל-investigator.

### מטרת ה-verifier

- **לא** לבדוק שהקוד "נראה נכון".
- **לא** להריץ את הטסטים.
- **כן** להפעיל את התוצר בסביבה אמיתית (דפדפן/CLI/API), לעבור על כל ה-flows
  המובטחים ב-brief/fixes, ולדווח על divergence/regressions.

### תוצרים נדרשים

1. ‏**Table של DoD items** — אחד-אחד, האם עובד? עדות (screenshot/log/curl).
2. **רשימת flows שעבדו מקצה לקצה**.
3. **רשימת flows שנשברו** + root cause hypothesis (לא חובה fix).
4. **בעיות חדשות שלא תועדו** — NBug1, NBug2, וכו'.
5. **Regressions** — דברים שעבדו לפני התיקון ולא עובדים אחרי.

### תפקיד המודל

- ‏Sonnet 4.6 כנראה **מספיק** ל-verifier. המשימה היא:
  - הפעלת CLI tools (curl, playwright, screenshots)
  - השוואה ויזואלית פשוטה
  - מילוי טבלה
  
  אין בה החלטות ארכיטקטוניות → אין צורך ב-Opus.

- אבל **חובה שיהיה סוכן נפרד מה-executor**. לא להריץ את ה-verification באותו
  סשן של הביצוע — ה-executor כבר "מאוהב" בקוד שלו ויראה אותו עובד גם כשלא.

### Prompt skeleton ל-verifier

```
אתה verifier. סוכן <executor> סיים <feature>. תפקידך להפעיל את הקוד
ולוודא שכל ה-DoD items עובדים.

מקורות:
- docs/<brief>.md — מה הובטח
- docs/<investigation>.md — אם היה (מה היה שבור לפני)
- git log — מה נעשה

שלבים:
1. קרא את ה-brief — צא עם טבלת DoD items.
2. הפעל את כל ה-flows הקריטיים בסביבה אמיתית.
   - frontend → linux-gui browser + pw-clean.sh
   - backend → curl + WS client
3. לכל item: סטטוס (✅/⚠️/❌/ⓘ) + evidence.
4. חפש regressions: דברים שעבדו לפני, לא עובדים עכשיו.
5. חפש בעיות שלא היו ברשימה — תפעיל גם flows צדדיים.
6. כתוב דוח ב-docs/<feature>-verification-report.md.

אסור: לערוך קוד. אסור: commit.
מותר: יצירת בדיקות זמניות, screenshots, dummy data.
```

### תזמון

```
Planner → Executor → Verifier-slice → (אם יש באגים) → Executor (fix) → Verifier → ...
```

**Verifier-slice חובה בסוף** — sub-agent נפרד, fresh context, לא executor עצמו.
ה-bias של "כותב הקוד מאמין שזה עובד" אמיתי, וזה תפקיד ה-verifier לעקוף אותו.

**Verifier-phase (בתוך הסליס) לא חובה** — opt-in מה-planner ספציפית לפי
היוריסטיקות בסעיף 8.

---

## 7. ‏שתי דרגות של verifier-slice — light ‏ו-heavy

‏Verifier-slice בסוף הסליס תמיד רץ — ‏אבל בדרגה שונה לפי score מורכבות.

| ‏Tier | ‏זמן | ‏סקופ |
|------|------|------|
| **`verifier-slice-light`** | ~15 דק' | ‏Read brief DoD → walk items עם evidence → 1-2 e2e happy paths → דוח קצר |
| **`verifier-slice-heavy`** | ~30-50 דק' | ‏הפרוטוקול המלא: 7 שלבים, edge cases, regressions, side flows, סיווג ל-patterns.md |

ה-light הוא **‏ביטוח קבוע** ‏(תופס DoD compliance, ‏fresh perspective).
ה-heavy הוא **‏topup ל-risk גבוה** ‏(תופס regressions ‏ו-flows לא רשומים).

‏הplanner קובע את הדרגה ב-brief לפי score (סעיף 8).

---

## 8. ‏Complexity Scoring — ‏מה tier להריץ

‏ה-planner ממלא checklist בכתיבת ה-brief. ‏הציון קובע tier אוטומטית.

### Checklist

```
Integration / Data flow:
[ ] Cross-store data flow ‏חדש (FE↔BE, store↔store, BE↔external)   +2
[ ] ‏Streaming / real-time (WS, SSE, audio chunks, partial text)     +2
[ ] ‏Protocol contract חדש (WS message, REST endpoint, schema)       +2

Code surface:
[ ] ‏Refactor של קוד קיים (לא greenfield)                            +1
[ ] >5 files touched ב->2 packages                                  +1
[ ] ‏State machine / async coordination (races, queues)              +2

External dependencies:
[ ] ‏ספרייה חיצונית חדשה (לא מוכרת מ-slices קודמים)                  +2
[ ] ‏הספרייה עושה DOM mutation / monkey-patching runtime             +1

Risk indicators:
[ ] 3 הslices האחרונים באזור הזה החזירו bugs                         +2
[ ] ‏Test coverage <70% על הקוד שמשתנה                                +1
[ ] ‏Deploy לפרודקשן מיד אחרי הסליס                                   +2

Mitigators:
[ ] ‏Pure logic, ‏אין IO                                              -2
[ ] ‏TDD מלא, ‏tests מקיפים על הbehavior החדש                         -1
[ ] ‏Greenfield, ‏אין call sites קיימים                               -1
```

### ‏Score → tier mapping

```
0-3:  light    (verifier-slice-light בלבד, ‏ללא verifier-phase)
4-7:  light + verifier-phase ‏על 1-2 phases מסוכנים
8+:   heavy   (verifier-slice-heavy) + verifier-phase ‏על mostly phases
```

### ‏תיעוד ב-brief

‏ב-frontmatter / header של ה-brief, ‏הplanner מציין:

```yaml
verifier-slice: light | heavy
complexity-score: 5         # ‏אופציונלי — תיעוד
```

### ‏אימות (retrospective)

| ‏Slice | ‏Score משוער | ‏Tier מתאים | ‏מה קרה |
|-------|--------------|------------|---------|
| ‏migration-system | 1 | light | ‏אכן אפס bugs |
| ‏logging-infra | 9 | heavy | ‏אכן ~7 issues על 2 rounds |
| ‏Slice 9 (frontend) | 14 | heavy | 19 bugs (‏אבל verifier לא הופעל אז) |

‏הציון מכייל נכון על הסיפורים שכבר ראינו. ‏אם case study חדש סותר — ‏לעדכן משקלות.

---

## 9. ‏Per-Phase Testing Strategy

‏ה-planner מציין לכל phase ב-brief את אסטרטגיית הבדיקה. ‏ה-executor **‏כיבד את הבחירה**,
‏לא חולק עליה.

### ‏פורמט ב-phase header

```
‏Phase 3: Wire migrations to profile-manager
  Testing: tdd
```

### ‏ערכים אפשריים

| ‏ערך | ‏מתי | ‏מה Executor עושה |
|------|-----|--------------------|
| `tdd` | ‏Logic חדש, ‏protocol contract, ‏state machine | ‏Red test → green code → refactor |
| `integration` | ‏Wiring, ‏glue code שמחבר tested pieces, ‏refactor | ‏קוד קודם, ‏אז integration test בתוך אותו phase |
| `manual` | UI, CSS, ‏UX flows | ‏אין tests אוטומטיים — ‏בדיקה ידנית בדפדפן/curl |
| `none` | docs, config, pure rename | ‏שום בדיקה (typecheck + lint ‏עדיין כן) |

### ‏Defaults אם missing

‏אם הplanner שכח לציין, ה-executor ישתמש בברירות לפי תוכן ה-phase:

- ‏logic / protocol / schema → `tdd`
- ‏refactor → `integration`
- ‏ui / styling → `manual`
- ‏docs / config / rename → `none`

‏אבל **‏עדיף שה-planner יציין במפורש** — ‏מנע ויכוח באמצע.

### ‏אם executor לא מסכים עם הבחירה

‏זה case של "ראש קטן" — **‏STOP, ‏החזר STATUS: BLOCKED** ‏עם הסבר.
‏לא לסטות מהחלטת הplanner.

---

## 10. רשימת בקרה ל-planner (Opus)

לפני סגירת brief, וודא:

- [ ] ‏DoD ויזואלי + טסטים (לא רק טסטים)
- [ ] ‏Anti-patterns section עם הדפוסים הרלוונטיים מ-`patterns.md`
- [ ] טבלת Data Flow Bridges מלאה (אם יש מולטי-store)
- [ ] ‏Mockup Compliance Audit phase קיים (אם UI)
- [ ] כל "הסר X" — file:line קונקרטי
- [ ] **‏Complexity score ‏חושב + tier מסומן** (light/heavy)
- [ ] **‏Verifier-phase ‏מסומן לphases ספציפיים אם score 4+**
- [ ] **‏Testing strategy פר phase** (tdd/integration/manual/none)
- [ ] אזהרות על library incompatibilities ידועות (אם רלוונטי)
- [ ] **‏הופעל plan-verifier על ה-brief** (‏סעיף 11)
- [ ] **dev/main parity check** ‏(סעיף 12)

---

## 11. ‏Plan Verifier — ‏חובה לפני handoff

**‏מטפל ב:** ‏כל הקטגוריות. ‏זה ה-recommendation ‏עם ה-ROI הגבוה ביותר.

**‏הראיה:** ‏ב-`case-studies/2026-05-voice-acp-slices.md`, 100% (3/3) ‏מהbריפים שנבדקו ‏היו בעיה אמיתית, ‏בממוצע 3 ‏בעיות לbrief. ‏עלות ~10 ‏דק', ‏חיסכון 30-60 ‏דק' debug + ‏מנע ‏regression שקט אחד שהיה מגיע ל-production.

**‏הפתרון:** ‏אחרי שהbrief ‏מוכן ‏ולפני dispatched ל-executor — ‏הפעל [`agents/plan-verifier.md`](agents/plan-verifier.md):

```ts
Task({
  subagent_type: "plan-verifier",
  description: "Verify <slice> plan",
  prompt: `‏אתה plan-verifier. brief: docs/plans/<slice>.md.
Project root: <path>. Base tip: <hash>.
‏בצע את 7 ‏הבדיקות שמתועדות ב-`agents/plan-verifier.md`.`
})
```

**‏סוגי בעיות שתופס בפועל** (‏מ-case study):
- API/symbol לא קיים ב-dev (‏רק ב-main)
- Pseudo-code מחסיר branch ‏קיים → silent regression
- Pseudo-code עם type error צפוי
- Line numbers ‏factually wrong
- Naming inconsistency פנימי
- File paths שלא קיימים
- Risks/escalations ‏מיושנים

**‏Tama ‏מקבלת את הדוח ‏ומתקנת.** ~‏15-20 ‏דק' תיקון בממוצע. ‏ואז handoff.

---

## 12. dev/main Parity Check (‏על plan-verifier)

**‏מטפל ב:** ‏טעות חוזרת ‏שזוהתה ב-3/3 ‏briefs.

**‏הבעיה:** ‏Tama (planner) ‏מסתכלת על main worktree (‏או על תוצרי slices קודמים שעוד לא merged), ‏ומניחה ‏שsymbols קיימים. ‏אבל ה-base של slice ‏החדש ‏הוא dev tip, ‏ושם הם לא בהכרח קיימים.

‏דוגמאות מ-voice-acp:
- `deleteAgent` ‏ב-`adapters/agents-api.ts` — main מייצא, ‏dev לא
- ‏Line counts ‏ב-`sessions-ws.ts` — main 82 ‏שורות, ‏ה-brief טען 75 (`main` ‏ישן)

**‏הפתרון** ב-plan-verifier prompt:

```
‏לכל symbol/API ‏שhbrief מציין — ‏אמת מול dev tip ‏בפועל:

cd <project>/dev   # ‏או base worktree
git log -1 --oneline    # ‏לוודא tip
grep -rn "<symbol>" packages/
wc -l <path>
```

‏אם משהו לא קיים ‏ב-dev — 🔴 blocker.

---

## 13. JIT Briefs > Upfront Briefs

**‏מטפל ב:** ‏Brief stale ‏לפני dispatching.

**‏הראיה:** ‏מ-`~/.config/opencode/learnings.md` 2026-05-29: "‏אסטרטגיית 'גל-גל' — ‏לכתוב 2-3 briefs ‏לפני dispatch, ‏לא 9 briefs מראש — ‏עובדת טוב יותר. ‏כל גל לומד מהקודם (verifier findings, ‏סטיות מהbrief). ‏Brief ‏שנכתב ‏לפנים ‏שלא ‏נדispatched ‏עוד ‏הופך stale (codebase ‏זז)."

**‏הפתרון:**

1. ‏זהה 2-3 ‏ה-slices ‏הבאים בעדיפות.
2. ‏כתוב brief ‏לראשון. ‏הפעל plan-verifier. ‏Dispatch executor.
3. ‏בזמן שexecutor רץ — ‏כתוב brief לשני.
4. ‏אחרי verifier-slice הראשון — ‏עדכן את ה-recommendations / patterns ‏אם משהו ‏עלה.
5. ‏אז ‏כתוב brief לשלישי, ‏עם הלקחים החדשים.

**‏לא:** ‏לכתוב 9 ‏briefs ‏מראש "‏לחסוך זמן". ‏בפועל זה ‏מאבד זמן כי:
- Brief מס' 9 ‏נכתב לפי מצב code ‏שכבר השתנה
- ‏לקחים מ-slice 1-3 ‏לא מועברים ‏ל-briefs 4-9
- ‏שינויי scope מ-stakeholder ‏לא משתקפים

---

## 14. Gotchas טכניים שחוזרים

**‏מטפל ב:** ‏זמן מבוזבז ב-executors ‏על gotchas צפויים.

**‏זוהו ב-voice-acp slices 11, 14, testing-coverage:**

### 14.1 core dist missing אחרי worktree (monorepo)

‏Typecheck נכשל ‏עם TS6305 ב-incremental cache. ‏Sonnet (slice 11) ‏בילה **12 ‏הודעות** ‏באותה שגיאה. ‏Opus פתר ב-1.

**‏פתרון:** ‏ב-EXECUTOR_DISPATCH §0 ‏ובbriefs לפרויקטי monorepo:

```bash
# ‏אחרי worktree + install:
pnpm build --force      # ‏או tsc --build --force ‏ל-core/types package
```

### 14.2 Worktree path mistake

‏Opus (‏slices 14, testing-coverage) ‏יצר ‏worktree ב-`dev/.worktrees/` ‏במקום ב-`.worktrees/` ‏הראשי **‏פעמיים**. ‏זיהה ‏ותיקן עצמאית, ‏אבל זמן מבוזבז.

**‏פתרון:** ‏ב-EXECUTOR_DISPATCH §1:

> ‏אם ‏cwd ‏שלך ‏הוא `dev/` (‏לא root), ‏השתמש ב-absolute path: `git worktree add /full/path/.worktrees/<slice> -b <slice> dev`

### 14.3 ‏CLI assumption שגויה (claude אינו ACP-compliant)

‏slice 8 brief ‏ביקש לטסט עם claude. ‏ה-WS ‏נסגר עם code 1005 ‏מיד.

**‏פתרון:** plan-verifier ‏בבדיקה 7 ‏(risks/escalations מיושנים) ‏צריך לאמת ש-CLI שצוין ב-brief ‏אכן ACP-compliant ‏עם הפרויקט. ‏אם לא — 🟡 ‏המלץ ל-Tama להחליף.

### 14.4 SDKs ‏שצריכים apiKey ‏ב-constructor ‏עם OneCLI

‏SDKs ‏כמו `@ai-sdk/elevenlabs`, `@ai-sdk/google` ‏צריכים `apiKey` ‏ב-constructor. ‏פתרון: ‏העבר string placeholder, OneCLI ‏מחליף ב-proxy. ‏מתועד ב-`~/.config/opencode/learnings.md` 2026-05-16.

---

## 15. ‏אל תbiasing את verifier-prompts

**‏מטפל ב:** ‏False negatives של verifier.

**‏הבעיה:** ‏executor (‏שכותב את הprompt ל-verifier) ‏עלול לא בכוונה למסגר את המשימה בצורה שמסתירה את הבאגים שלו. ‏דוגמה: "‏בדוק ש-bubble grouping עובד" — ‏אם Sonnet בנה bubble grouping שגוי לחלוטין, ‏הוא יבדוק על הקוד הקיים ‏ויאשר.

**‏הפתרון:** ‏verifier prompts ‏צריכים להיות נטרליים:

❌ ‏"‏בדוק ש-X ‏עובד"
✅ ‏"‏אמת את כל DoD items של slice <name> ‏מול brief: ‏docs/plans/<name>.md"
✅ ‏"‏קרא את ה-brief לבד. ‏אל תסמוך על המסגור של הprompt הזה — ‏הוא הגיע מ-executor."

‏מתועד ב-`agents/verifier-phase.md`, `agents/verifier-slice-light.md` ‏ב-section "‏כלל יסוד: ‏אל תסמוך על ה-prompt".

---

## שיפורים מסשן 2026-07-19 (זיקוק מלא + אירוע פיזור-דוחות)

> 7 פריטים שצפו בסשן שבו אותרו: פיצול 91 דוחות ל-3 מיקומים לא-מסונכרנים, תזה שגויה
> ממדגם קטן, ואובדן-גלם עם קריסת-process. מקור: `distillations/2026-07-19-full-report.md`.

### 16. progress/todo-file לסוכנים

**מטפל ב:** נראות + עמידות מול קריסת-process.

**הבעיה:** סשני אביגיל/כלב ארוכים ואטומים — אין לדעת מה הם עושים תוך כדי. וכשה-process
קורס, הגלם מתפוגג (ה-CLI store מסתובב/נמחק). בסשן הזה אביגיל נקטעה כשה-process יצא.

**הפתרון:** כל מאמת מתחזק **to-do file קבוע** (markdown checklist) בנתיב peekable. הכללה
של מנגנון ה-`log_path` הקיים של כלב → always-on לכל המאמתים, לא רק בריצות-יתרו.

### 17. path-neutrality בהגדרות הסוכנים

**מטפל ב:** מעבר בין מכונות.

**הבעיה:** ההגדרות מקשיחות `~/projects` (p קטנה). על מכונה עם `~/Projects` (P גדולה) →
הסוכנים כתבו 90 דוחות לתיקיות שגויות/לא-מגובות.

**הפתרון:** env יחיד פר-מכונה + placeholders (`{{BDS_REPORTS}}`...) במקור-האמת + החלפה
ב-install-time לשלושת ה-CLIs. **מאומת READY** — `docs/plans/slice-path-neutral-agent-configs.md`.

### 18. כיול-mode של כלב

**מטפל ב:** עלות verifier.

**הבעיה:** `calev-heavy` = median 16.5 דק' Opus; לפי הזיקוק רוב ה-heavy מחזיר GO/0-findings.
gate מורכבות-8 נדיב מדי.

**הפתרון:** heavy רק ל**סיכון-סוג** (security/concurrency/data-integrity), לא רק ניקוד;
`mode` מפורש-חובה בכל dispatch; default=רגיל. ⚠️ **לכייל, לא לקצץ** — כלב תופס 11 blockers
ב-155 ריצות (12% non-GO). ה-payoff אמיתי, רק לא מכויל לתיק.

### 19. distill.py: פילוח verdict×mode + נרמול severity

**מטפל ב:** דיוק הזיקוק.

**הבעיה:** אי-אפשר לענות "האם ה-blockers נתפסו ב-heavy או ברגיל" — אין פילוח. וה-severity
מגיע כ-`HIGH`/`MED` לצד `blocker`/`minor` → ספירה כפולה ורעש.

**הפתרון:** הוסף ל-`distill.py` פילוח verdict×mode לכלב; נרמל severity/category (lower-case
+ פיצול מחרוזות מרובות-קטגוריה).

### 20. ארכוב-בריפים + cleanup כריטואל-merge נאכף (slice A)

**מטפל ב:** הצטברות בריפים ו-worktrees.

**הבעיה:** `docs/plans/` מלא בבריפים-שיושמו שלא אורכבו; worktrees מצטברים. הארכוב לא קשור
לטקס ה-merge → נשכח.

**הפתרון:** **merge = פעולה אטומית** שכוללת `archive (brief → docs/plans/archive/)` +
worktree cleanup, ע"י הסוכן הממזג, **מיד אחרי אישור-ה-merge**. לא צעד נפרד שנשכח.

### 21. live-preview gate ל-web לפני merge (slice B)

**מטפל ב:** merge מושכל בפרויקטי web.

**הבעיה:** runtime-gate = כלב GO. אבל כלב הוא **סוכן** שמריץ טסטים — המשתמש לא ראה את
התוצאה בעיניו. calev-heavy עושה "visual review" אבל זה שיפוט שלו, לא העיניים של המשתמש.

**הפתרון:** לפרויקטי web — אחרי כלב GO ולפני merge — מרדכי מעלה **preview חי** (dev server/URL)
ומציג למשתמש לאישור-עיניים. שתי שכבות: אימות-מכונה (כלב) → אימות-אדם-חי (משתמש). זה מה
שהופך את "merge רק באישור מפורש" ל**מושכל**.

### 22. יישור דוקטרינת docs ל-docs-repo

**מטפל ב:** דוקטרינה מול מציאות + פרטיות.

**הבעיה:** הדוקטרינה אומרת "decisions/walkthrough בריפו הפרויקט, ליד הקוד". בפועל כבר קיים
`docs-repo` נפרד (private) עם decisions/plans/reports פר-פרויקט — כי תוכן אישי דלף למסמכים
ועדיף שלא יתפרסם. הדוקטרינה מפגרת אחרי מה שכבר נעשה.

**הפתרון:** לעדכן `mordechai`/`eliezer`/`SKILL`: decisions+walkthrough → docs-repo פרטי,
לא ריפו-הפרויקט הציבורי. reports כבר ב-repo פרטי ייעודי (`brief-driven-slices-reports`).

### 23. Front-loaded decision sheet — כל השאלות + התרחישים לפני הריצה

**מטפל ב:** מקסום אוטונומיה — צמצום הפרעות מ-N-פר-ריצה ל-**1 לפני + 1 במיזוג**.

**הבעיה:** גם בריצה "אוטונומית", החלטות צצות באמצע (בסשן 2026-07-19: ambiguity של scope
A/B, וה-qoder blocker) ומאלצות עצירה. כל עצירה = הפרעה + המתנה, ושוברת את הרצף.

**הפתרון:** לפני שמרדכי מתחיל ריצה (‏אוטונומית **או לא**), הוא מציג **דף-החלטות אחד**:

1. **שאלות scope** — כל ההבהרות על *מה* לבנות.
2. **הרשאות-מראש לתרחישים** — נקודות-ההחלטה החוזרות שצצות תוך-כדי, כל אחת עם default.
   מ-track record, ~7 התרחישים:

| תרחיש | default מוצע | חלופה |
|-------|-------------|-------|
| scope דו-משמעי | הפרשנות השמרנית + תיעוד | לשאול |
| תלות מתגלה כ-WIP לא-committed | לצמצם scope, לדחות ל-slice נפרד | לעצור / לקמיט |
| אביגיל USABLE-AFTER-FIX | fix+re-verify עד READY (אוטומטי) | — |
| אביגיל NEEDS-REWORK | rewrite פעם אחת; עדיין NEEDS → עצור | — |
| כלב PARTIAL/NO-GO | fix-loop עד GO (N סבבים) → עצור | דחייה מתועדת+מאושרת |
| התנגשות-merge בשרשרת | לפתור אם טריוויאלי; אחרת עצור | — |
| פעולה בלתי-הפיכה ל-mainline (commit לא-סקור, מחיקת data) | **לעולם לא אוטונומי — תמיד עצור** | — |

3. המשתמש עונה **פעם אחת** (או מקבל defaults) → מרדכי רץ brief→אביגיל→יישום→כלב עד
   ה-merge gate **בלי הפרעה**.

**התוצאה:** אינטראקציה אנושית = דף-החלטות אחד *לפני* + אישור-merge אחד *אחרי*. זה ה-batching
האולטימטיבי של נקודות-האדם.

**הוכחת-הרעיון (הריצה החיה, 2026-07-19):** ה-qoder blocker היה בדיוק תרחיש #2. ‏לו נשאל
מראש "אם תלות מתגלה כ-WIP — לצמצם או לעצור?", הריצה לא הייתה נעצרת כלל. ה-default (‏לצמצם)
הוא בדיוק מה שמרדכי עשה בפועל — אז front-loading היה חוסך את העצירה.
