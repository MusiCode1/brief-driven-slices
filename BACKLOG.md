# BACKLOG — ‏מה עוד לא נחת

> **‏מקור האמת היחיד לעבודה פתוחה בשיטה.** ‏כל מקום אחר (‏`recommendations.md` ‏פריט 38,
> ‏חלק 6 ‏של דוח זיקוק, ‏הודעות commit) ‏מפנה לכאן ‏ואינו משכפל.
>
> **‏אין עמודת "‏סטטוס".** ‏סטטוס שנכתב ביד רוקב — ‏זה `recommendations.md` ‏פריט 39.
> ‏במקומו: ‏לכל שורה יש **‏פקודה שמכריעה אותה**, ‏ו-`scripts/backlog-status.sh` ‏מריץ את כולן.
> ‏המסמך מחזיק את ה**‏מה** ‏ואת ה**‏בדיקה**; ‏את ה**‏מצב** ‏מפיקה ההרצה.
>
> **‏pipe בתוך פקודה** — ‏לכתוב `\|` (‏escape תקני של Markdown). ‏בלעדיו התא נחתך
> ‏באמצע ‏והבדיקה מסומנת ⚠️ ‏שבורה.
>
> ```bash
> bash scripts/backlog-status.sh
> ```
>
> **‏להוספת שורה**: ‏פריט בלי פקודה שמכריעה אותו אינו נכנס. ‏אם אי אפשר לכתוב אותה —
> ‏הפריט לא מוגדר מספיק, ‏וזה הממצא הראשון עליו.

| # | ‏פריט | ‏מקור | check | expect |
|---|------|------|-------|--------|
| 1 | ‏כלל פריט 31 ‏בפרומפט של מרדכי — ‏"‏טענה עם הפקודה שהפיקה אותה" | `recommendations.md` §31 · `RAW` §25 | `grep -c "הפקודה שהפיקה" agent-definitions/prompts/mordechai.md` | `>0` |
| 2 | ‏בדיקה 10 ‏לאביגיל + `§1.5` ‏בתבנית | `docs/plans/slice-current-state-section.md` | `grep -c "§1.5" briefs/BRIEF_TEMPLATE.md` | `>0` |
| 3 | `scripts/lint-brief.js` — ‏שלב 1 (‏קיום סמלים/‏נתיבים) | `recommendations.md` §34 · `RAW` §16 | `test -f scripts/lint-brief.js` | `file` |
| 4 | ‏רטרו ל-lint-brief: ‏כמה מ-117 ‏החוסמים הוא תופס | `recommendations.md` §34 ("‏מספר, ‏לא הערכה") | `test -f distillations/lint-brief-retro.md` | `file` |
| 5 | ‏נרמול severity/category ‏ב-distill.py | `recommendations.md` §19 · ‏זיקוק 08-03 ‏חלק 6 | `grep -c "SEVERITY_MAP\\|normalize_severity" scripts/distill.py` | `>0` |
| 6 | ‏פילוח סבבים פר-brief ‏בתוך distill.py | ‏זיקוק 08-03 ‏חלק 6 ‏פריט 3 | `grep -c "rounds_per_brief" scripts/distill.py` | `>0` |
| 7 | `claude-code` ‏כיעד ב-generate-cli-configs.py | commit `3df40ec` ("‏דורש הכללה ב-generator") | `grep -c "claude-code" scripts/generate-cli-configs.py` | `>0` |
| 8 | `qoder` ‏ב-README ‏הראשי | ‏דוח כלב `qoder-path-neutral` (19/07) | `grep -c qoder README.md` | `>0` |
| 9 | `blocked/` ‏שנותר ב-dispatch-executor.sh | ‏דוח כלב `bds-extraction` NO-GO (30/05) | `grep -c ",blocked" scripts/dispatch-executor.sh` | `=0` |
| 10 | ‏בריף `slice-4-brief-commit-lifecycle` — READY ‏מ-03/06, ‏לא בוצע | `docs/plans/` | `test -f docs/plans/archive/slice-4-brief-commit-lifecycle.md` | `file` |
| 11 | ‏ערכי walkthrough ‏לקומיטים ‏3df40ec ‏ו-5cbace3 | `docs/walkthrough.md` | `grep -c "3df40ec" docs/walkthrough.md` | `>0` |
| 12 | **‏`install-cli-configs.sh` ‏אינו מתקין סקילים** — ‏רק agents. ‏`autorun`/`bug` ‏קושרו **ידנית** ‏לחמישה CLI (‏20/08), ‏ובמכונה חדשה לא יותקנו | ‏סשן 20/08 | `grep -ci "skill" scripts/install-cli-configs.sh` | `>0` |
| 13 | ‏**לא אומת שכל CLI באמת טוען סקילים** ‏בפורמט `SKILL.md` — ‏התיקיות מאוכלסות, ‏הטעינה לא נבדקה | ‏סשן 20/08 | `ls docs/skills-per-cli.md 2>/dev/null` | `file` |
| 14 | 🔴 **`generate-cli-configs.py` ‏כותב ל-`agents/` ‏ומוחק עריכות-יד שם.** ‏עריכות 23/08 (‏היפוך plan-gate) ‏נכתבו ישירות ל-`agents/` ‏ולא ל-`agent-definitions/prompts/` ⇒ ‏כל הרצה של ‏הגנרטור החזירה אותן לאחור. ‏סונכרן ‏25/08; ‏חסר **‏שער** ‏שיתפוס drift ‏כזה | ‏סשן 25/08 | `test -f scripts/check-agents-drift.sh` | `file` |
| 15 | ‏**‏`~/.claude/agents/` ‏מותקן ביד** — ‏אין יעד `claude-code` ‏בגנרטור (‏ר' פריט 7), ‏ולכן הסוכנים ש**‏בפועל מריצים את הריצות** ‏מתעדכנים בהעתקה ידנית ‏עם המרת-frontmatter ‏והצבת `{{BDS_*}}` | ‏סשן 25/08 | `grep -c install_claude scripts/install-cli-configs.sh` | `>0` |

## ‏מה שנסגר — ‏לתיעוד בלבד

‏שורה שנסגרה **‏נמחקת מהטבלה**. ‏ההיסטוריה נמצאת ב-`docs/walkthrough.md` ‏וב-git.
‏אל תשאיר שורות מסומנות ✅ — ‏זה בדיוק הרישום-ביד שהמסמך הזה נועד להימנע ממנו.

- [ ] **`eliezer.md`: אליעזר אינו כותב שדה `calev:` ב-walkthrough** — שדה שרק מאמת
      ממלא. מבצע שכותב אותו משמיע טענה שאין לו סמכות להשמיע. לדיווח על בדיקות
      שהריץ בעצמו: `בדיקות-עצמיות:` — שם שאי-אפשר לבלבל עם verdict.
      *מקור: ריצת `live-voice` 27/08 — הופעה שלישית של כשל-מסירה באותה ריצה.
      שתי הקודמות נסגרו בשער בר-כישלון בצד המקבל; זו טרם. שער מבני מונע את
      הצורה במקום לתפוס אותה בדיעבד.*
