# Case Study: Slice 9 — drive-coding Frontend Refactor

> **תאריך:** מאי 2026
> **פרויקט:** voice-acp-v2 (drive-coding)
> **Slice:** 9 — Frontend refactor (12 phases, ~50-70 tests חזויים)
> **Planner:** Opus 4.6 (כתב brief)
> **Executor:** Sonnet 4.6 (ביצע, יצא עם 114 טסטים ירוקים)
> **Investigator:** Opus 4.6 (חקר אחרי, מצא 19 באגים)
> **Verifier:** Sonnet 4.6 (אישר תיקונים, מצא 4 באגים חדשים)

---

## 1. הסשנים

| תפקיד | Session ID | מודל | תוצר |
|------|------------|-------|------|
| ‏Planning | (לא תועד כסשן בודד) | Opus | `docs/slice-9-frontend-refactor-brief.md` |
| ‏Execution | `ses_1cc35d8afffeaT91LaseaWdhi7` | Sonnet 4.6 | 14 commits, 114 טסטים |
| ‏Investigation | `ses_1caa4e18affebuayTr8gz85GNJ` | Opus 4.6 | `docs/slice-9-bugs-investigation.md` |
| ‏Fix | `ses_1ca88af13ffelWWkxqn01qNC4e` | Sonnet 4.6 | 7 commits, 17/19 באגים תוקנו |
| ‏Verification | `ses_1ca5ef452ffenUKORgdHj6YeTE` | Sonnet 4.6 | `docs/slice-9-verification-report.md` |

---

## 2. מה תוכנן

ה-brief (`docs/slice-9-frontend-refactor-brief.md`, 535 שורות) הגדיר:

- 12 phases (Foundation → Bubble components → Mobile header → Desktop sidebar
  → Tier 1 WS → Slice 8a WS → Mic cluster → Bubble click-to-play → /sessions
  → /session load → File picker → Settings)
- 11 components חדשים
- 5+ stores חדשים
- 4 routes חדשים
- ‏TDD חובה ל-logic, CSS pure לויזואלי
- ‏DoD: typecheck + lint + tests ירוקים, mobile+desktop responsive
- ‏Sub-agent חובה Sonnet 4.6 (לא Opus — "spec ברור, אין צורך")
- אסור Backend (חוץ מ-schema), אסור core (חוץ מ-schema)

ה-brief היה **טוב** — מובנה, ברור, עם reference ל-mockup.

---

## 3. מה Sonnet ביצע

הסשן: `ses_1cc35d8afffeaT91LaseaWdhi7` (79 הודעות).

תהליך:
- כל phase בתורו, TDD red-green, commit אוטומטי.
- בכל phase: "X tests GREEN", "pnpm typecheck + lint + test ירוקים", commit.
- **לא נפתח דפדפן ולא צולם screenshot אף פעם.**
- בסוף: "Slice 9 הושלם. 114 frontend tests + 14 commits + 22 UI behaviors moved to ✅".

לכאורה success.

---

## 4. מה Opus מצא ב-investigation

הסשן: `ses_1caa4e18affebuayTr8gz85GNJ` (16 הודעות).

‏Opus פתח linux-gui browser, ניווט, צילם, קרא קוד.

**19 באגים** (`docs/slice-9-bugs-investigation.md`):
- ‏8 critical
- 7 medium
- 4 minor
- 7 חדשים שלא היו ברשימת ה-followup הקודמת (N1-N7)

הקריטיים:
- ‏**B1** — Bubble grouping: כל text_chunk = sub-segment נפרד (11 טסטים ירוקים פספסו)
- ‏**B4** — textbox + שלח כפתור עדיין שם (ה-brief אמר במפורש לא)
- ‏**B10** — Thought translation לא נראה (אין bridge בין voice-session ל-agent-session)
- ‏**B12** — Sessions page UI קיים, data ריק (`/api/projects` ריק)
- ‏**B13** — TTS duplication (disconnect לא מנקה handler)
- ‏**B15** — Click-to-play שבור (messageId=null hardcoded)
- ‏**N4** — Projects registry לא מקבל recordCwd
- ‏**N5** — Lucide CDN createIcons מערבב DOM, יוצר icons כפולים

המוזר: 4 מתוך 8 הקריטיים — Sonnet כתב להם טסטים מפורשים, וכולם עברו.

---

## 5. מה Sonnet תיקן

הסשן: `ses_1ca88af13ffelWWkxqn01qNC4e` (55 הודעות).

7 commits על 5 phases:
- ‏Phase 1: B1 (TDD), B4, N5 (partial — container fix במקום מעבר ל-lucide-svelte)
- ‏Phase 2: N1, B10 (bridge חדש), B15
- ‏Phase 3: N4
- ‏Phase 4: B13, B14 (החליט שלא צריך — טעות)
- ‏Phase 5: Polish — B6, B9, B11, N2, N6, N7

**Sonnet דיווח:** "573 tests עוברים, 17/19 fixed".

---

## 6. מה ה-verifier מצא

הסשן: `ses_1ca5ef452ffenUKORgdHj6YeTE`.

Verification ב-browser חי. דוח: `docs/slice-9-verification-report.md`.

**4 באגים שנותרו או חדשים:**

| # | מה | למה Sonnet פספס |
|---|----|------------------|
| ‏N3 | Desktop header עדיין בסגנון ישן (⚙ emoji, "disconnected" badge) | Sonnet תיקן רק mobile header (N1). שכח שיש desktop header נפרד. |
| ‏NBug2 | User bubble click → "השמע מחדש" כפתור מופיע, אבל אין `recordingId` ב-DOM, אין fetch | Sonnet תיקן את ה-messageId pipeline (B15) — שכח מקבילה ל-recordingId |
| ‏NBug3 | Reload של /agent/[id] → bubbles ריקות (WS reconnect לא מביא history) | לא נבדק בכלל, לא ב-investigation ולא ב-fix |
| ‏NBug4 | sentence-boundary מפצל על פסיקים → sub-segments קצרים | Sonnet אמר "B14 — לא צריך תיקון". ה-verifier ראה ב-DOM "כן," כסגמנט. |

**מטא-תופעה:** Opus בסבב investigation **גם פספס** את NBug3 (history reload). זה לא מקרי — investigator קורא קוד; verifier מפעיל flow. הם תופסים דברים שונים.

---

## 7. סיווג ל-5 הקטגוריות

| באג | קטגוריה | רמת ביטחון |
|-----|---------|-----------|
| B1 | 1 (TDD blind spot) | גבוהה — 11 טסטים ירוקים, contract שגוי |
| B10 | 2 (cross-store) | גבוהה — שני stores, אין bridge |
| B13 | 2 (cross-store) | גבוהה — disconnect לא מנקה |
| B15 | 1 + 2 | hardcoded null + cross-module |
| N4 | 2 (cross-store) | orchestrator לא קורא registry |
| NBug2 | 2 (cross-store) | event לא מעדכן bubble |
| B4 | 3 (spec drift) | brief אמר במפורש |
| N1 | 3 (spec drift) | swap של props |
| N2 | 3 (spec drift) | emojis במקום lucide |
| N3 | 3 (spec drift) | desktop header נשכח |
| B11 | 3 (spec drift) | play icon ב-mockup, חסר |
| N5 | 4 (library) | Lucide × Svelte DOM mixing |
| B6 | 5 (visual) | 4px grip, אין טסט |
| B12 | 2 + 3 | UI שלם אבל אין data |
| NBug3 | (unique) | WS reconnect — לא קטגוריה |
| NBug4 | (unique) | regex החלטה רעה |

**התפלגות:**
- קטגוריה 2 (cross-store): 5 — ה-blind spot הכי גדול
- קטגוריה 3 (spec drift): 5
- קטגוריה 1 (TDD blind): 3
- קטגוריה 5 (visual): 2-3
- קטגוריה 4 (library): 1
- ‏Unique: 2

---

## 8. תובנות מרכזיות מה-case study הזה

1. **"כל הטסטים ירוקים" משדר בטחון שווא.** 114 טסטים ירוקים — 19 באגים בפועל.
   ה-DoD צריך להיות ויזואלי.

2. **Sonnet לא פותח דפדפן בפועל אלא אם מורים לו במפורש.** הוא יכתוב CSS,
   ידווח "Phase 3 ירוק", ולא יסתכל על מה שנוצר.

3. **Cross-store/cross-module data flow הוא ה-failure mode הכי תכוף.** 5/8
   קריטיים. צריך לתעד את הגשרים במפורש ב-brief.

4. **Spec drift נובע מ-refactor במקום rebuild.** ‏Sonnet מוסיף קוד חדש על
   הישן ושוכח למחוק. הוראת "DELETE block at file:lines" מונעת את זה.

5. **גם Opus כ-investigator מפספס.** ‏NBug3 (history reload) לא תוקן ולא דווח
   אפילו אחרי investigation מפורט. רק verifier שהפעיל reload תפס.

6. **Verifier agent חובה, לא נחמד.** הוא תופס דברים אחרים מ-investigator.

7. **ה-N5 (Lucide × Svelte) הוא תזכורת:** ‏planner חייב לדעת על
   incompatibilities ידועות לפני שהוא בוחר ספרייה ב-brief.

---

## 9. שינויי tooling שהיו מונעים את רוב הבאגים

לפי 5 ההמלצות ב-`recommendations.md`:

| באגים שהיו נמנעים | המלצה |
|-------------------|--------|
| ‏B1 | #2 (anti-patterns: bubble grouping) |
| ‏B4 | #5 (DELETE block ב-file:lines) |
| ‏B10, B13, B15, N4, NBug2 | #3 (Data Flow Bridges table) |
| ‏B11, N1, N2, N3, B6 | #4 (Mockup Compliance Audit phase) |
| ‏N5 | #2 (anti-patterns: Lucide × Svelte) |
| ‏NBug3, NBug4 | #6 (Verifier agent) |

**הערכה:** 14 מתוך 19 (~74%) היו נתפסים מראש או בשלבים מוקדמים בעזרת ההמלצות.
5 הנותרים דורשים verifier.

זה תואם להערכה הראשונית של 70/30.
