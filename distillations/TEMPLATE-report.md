# Distillation Report — <YYYY-MM-DD>

> **תאריך**: <YYYY-MM-DD>
> **data.json**: `distillations/<YYYY-MM-DD>-data.json`
> **דוחות שנכללו**: <N> דוחות (avigail: <N_a>, calev: <N_c>)
> **מאז הזיקוק הקודם**: <K> דוחות חדשים

---

## חלק 1 — מבט-לאחור: הכללים מהדוח הקודם

> **מקור**: `delta` מה-data.json — השוואה לsnapshot הקודם.
> לכל כלל שנוסף בזיקוק הקודם: האם הוא עבד? האם הבעיה ירדה, לא השתנתה, החמירה?

| כלל | קטגוריה | מגמה | פרשנות |
|-----|---------|-------|---------|
| <כלל שנוסף בזיקוק הקודם> | <category> | ⬇️ ירד / ➡️ יציב / ⬆️ עלה / 🆕 חדש / 🚫 נעלם | <שורה אחת> |

> אם זה הזיקוק הראשון — כתוב: "אין זיקוק קודם. כל הקטגוריות בסטטוס 'new'."

---

## חלק 2 — התפלגות נוכחית

> **מקור**: `counts` + `hitrate` מה-data.json.

### אביגיל (plan-verifier)

| severity | count |
|----------|-------|
| blocker | <N> |
| regression | <N> |
| confusion | <N> |
| minor | <N> |

| category | count | reports תורמים |
|----------|-------|----------------|
| <category> | <N> | <project/slice, ...> |

**Hitrate**: <reports_with_findings>/<reports> דוחות עם ממצאים. ממוצע: <avg_findings> ממצאים/דוח.

### כלב (runtime-verifier)

| severity | count |
|----------|-------|
| blocker | <N> |
| ... | ... |

| category | count | reports תורמים |
|----------|-------|----------------|
| <category> | <N> | <project/slice, ...> |

**Hitrate**: <reports_with_findings>/<reports> דוחות עם ממצאים. ממוצע: <avg_findings> ממצאים/דוח.

---

## חלק 3 — חדשות: טקסונומיה מתפתחת

> **מקור**: `noncanonical` + `delta["trend"]=new` מה-data.json.
> קטגוריות שמופיעות בדוחות אבל **לא ב-CANONICAL_CATEGORIES** — מועמדות לזיקוק.

### קטגוריות לא-קנוניות (avigail)

| category | reports | פרשנות |
|----------|---------|---------|
| <category> | <project/slice> | <האם כדאי להוסיף לקנון?> |

### קטגוריות לא-קנוניות (calev)

| category | reports | פרשנות |
|----------|---------|---------|
| <category> | <project/slice> | <האם כדאי להוסיף לקנון?> |

> אם `noncanonical` ריק — "אין קטגוריות לא-קנוניות. הטקסונומיה יציבה."

#### שינוי-טקסונומיה (אם רלוונטי)

> אם זוהתה קטגוריה חדשה משמעותית שראוי להוסיף לקנון — תעד כאירוע:
>
> **<YYYY-MM-DD>**: הוספת קטגוריה `<new-cat>` ל-CANONICAL_CATEGORIES["avigail"|"calev"].
> מקור: <N> דוחות (<project/slice, ...>). פרשנות: <שורה אחת>.

---

## חלק 4 — עדכוני-קטלוג

> כל שינוי ב-`plan-pitfalls.md` ו/או `patterns.md` שנעשה בזיקוק זה — עם traceability.

### plan-pitfalls.md (אביגיל)

- **הוספה**: קטגוריה `<cat>` — `> מקורות: <project/slice-avigail, ...>` — <נימוק קצר>
- **עדכון דירוג**: `<cat>` עלה/ירד בחומרה — <נימוק>
- **ללא שינוי**: <cat-א>, <cat-ב> — מגמה יציבה

### patterns.md (כלב)

- **הוספה**: קטגוריה `<cat>` — `> מקורות: <project/slice-calev, ...>` — <נימוק קצר>
- **עדכון דירוג**: ...
- **ללא שינוי**: ...

> traceability דו-כיווני: כל שינוי בקטלוג מצביע לדוחות המקוריים שתמכו בו (via `trace` ב-data.json).
