# Reports — ‏פורמט דוחות אימות

‏ריפוזיטורי זה (brief-driven-slices) ‏מצבר דוחות אימות מכל הפרויקטים.

---

## ‏מבנה תיקייה

```
reports/
└── <project>/                           # e.g. voice-acp/, bds/
    └── <slice>-<verifier>.md            # פורמט חדש: YAML front-matter + גוף MD
    └── <slice>-<verifier>.json          # פורמט ישן (backward-compat, לא ממירים)
```

---

## ‏פורמט חדש — `.md` עם YAML front-matter (מומלץ)

**מבנה**: YAML front-matter בראש הקובץ (בין שני `---`) + גוף Markdown מלא אחריו.

```markdown
---
project: "voice-acp"
slice: "slice-17"
verifier: "avigail"
date: "2026-05-30"
verdict: "USABLE-AFTER-FIX"
findings:
  - id: 1
    severity: "blocker"
    category: "missing-symbol"
    summary: "loadSession is missing in acp-client.ts"
    source_brief: "§4 Commit 0"
    source_code: "packages/frontend/src/acp-client.ts:22"
    cost_estimate: "15-30min"
  - id: 2
    severity: "minor"
    category: "wrong-line-number"
    summary: "Brief says line 75 but file has 50 lines"
    source_brief: "§3"
    source_code: "packages/backend/src/server.ts:75"
    cost_estimate: "5min"
---

# Plan Verification — slice-17

> **Brief**: docs/plans/slice-17.md
> **Base tip**: abc1234
> **Verdict**: 🟡 USABLE-AFTER-FIX

... (גוף הדוח המפורט — טבלאות, spot-check, evidence) ...
```

### ‏שדות front-matter

| שדה | חובה | ערכים |
|-----|------|-------|
| `project` | ✅ | basename של Project root |
| `slice` | ✅ | שם ה-slice (e.g. "slice-17") |
| `verifier` | ✅ | `"avigail"` \| `"calev"` |
| `date` | ✅ | ISO 8601 string: `"2026-05-30"` |
| `verdict` | ✅ | avigail: `READY` \| `USABLE-AFTER-FIX` \| `NEEDS-REWORK`; calev: `GO` \| `NO-GO` \| `PARTIAL` |
| `findings` | ✅ | רשימת Finding (ראה למטה) — יכולה ריקה `[]` |
| `mode` | כלב בלבד | `"phase"` \| `"light"` \| `"heavy"` |
| `dod_items` | כלב בלבד | רשימת strings |
| `spot_check` | כלב בלבד | string |

### ‏מבנה finding

```yaml
findings:
  - id: 1
    severity: "blocker"          # ראה ערכים קנוניים למטה
    category: "missing-symbol"   # ראה ערכים קנוניים למטה
    summary: "תיאור קצר"
    source_brief: "§4 Commit 0"  # איפה ב-brief זה מוזכר
    source_code: "path/file.ts:22"
    cost_estimate: "15-30min"
```

---

## ⚠️ הוראת ציטוט — חובה

כל `summary`, `spot_check`, ושדה-string ב-front-matter שמכיל:
- `:` (נקודתיים)
- `'` (גרש)
- `|` (pipe)
- `#` (hash)
- `[`, `]`, `{`, `}` (סוגריים)

— **חייב להיות עטוף ב-double-quote** (כפול `"`), אחרת yaml.safe_load ישבר בשקט.

**דוגמאות**:
```yaml
# ✅ מצוטט נכון:
summary: "loadSession is missing in acp-client"
summary: "passes string|boolean: fails edge case"
summary: "brief says line 75 — file has 50 lines"

# ❌ יישבר:
summary: passes: fails
summary: boolean | string issue
```

> **למה**: `distill.py` (שכבת הזיקוק) קורא את ה-front-matter דרך `yaml.safe_load`.
> front-matter שבור → `parse_report_file` מחזיר `None` (דלג+warn) — הדוח לא ייספר בזיקוק.

---

## ‏פורמט ישן — `.json` (backward-compat)

```json
{
  "project": "voice-acp",
  "slice": "17",
  "verifier": "avigail",
  "date": "2026-05-30T...",
  "verdict": "USABLE-AFTER-FIX",
  "findings": [
    {
      "id": 1,
      "severity": "blocker",
      "category": "missing-symbol",
      "summary": "תיאור קצר",
      "source_brief": "§4 Commit X",
      "source_code": "path/to/file.ts:line",
      "cost_estimate": "15-30min"
    }
  ]
}
```

> **לא ממירים** — 9+ דוחות `.json` קיימים נשארים כפי שהם. `distill.py` תומך בשניהם.

---

## ‏טקסונומיה ראשונית

**‏אביגיל (plan)**:
`missing-symbol` | `dropped-branch` | `type-error` | `wrong-line-number` | `naming-inconsistency` | `wrong-path` | `outdated-risk` | `missing-dependency`

**‏כלב (runtime)**:
`bubble-grouping` | `cross-store-null` | `spec-drift` | `regression` | `mobile-desktop` | `reload-reconnect` | `library-compat` | `unique`

> ‏הטקסונומיה אינה קפואה — ‏`distill.py` מסמן `noncanonical` מועמדים לזיקוק, מרדכי מחליט.

---

## ‏מי כותב

| ‏מאמת | ‏קובץ | ‏מתי |
|------|------|------|
| **‏אביגיל** | `<slice>-avigail.md` | ‏אחרי verification של brief (‏לפני dispatch) |
| **‏כלב** | `<slice>-calev.md` | ‏אחרי verification של slice (‏אחרי ביצוע) |

---

## ‏מטרה

‏חומר-גלם מצטבר לזיקוק חוצה-פרויקטי (`distill.py` + מרדכי). ‏ה-severity הוא הציר העיקרי למדידה.
