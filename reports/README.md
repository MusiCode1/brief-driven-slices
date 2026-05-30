# Reports — ‏דוחות אימות מתויגים

‏ריפוזיטורי זה (brief-driven-slices) ‏מצבר דוחות אימות מכל הפרויקטים.

## ‏מבנה

```
reports/
└── <project>/                      # e.g. voice-acp/, bds/
    └── <slice>-<verifier>.json     # e.g. 17-wake-word-avigail.json
```

## ‏מי כותב

| ‏מאמת | ‏קובץ | ‏מתי |
|------|------|------|
| **‏אביגיל** | `<slice>-avigail.json` | ‏אחרי verification של brief (‏לפני dispatch) |
| **‏כלב** | `<slice>-calev.json` | ‏אחרי verification של slice (‏אחרי ביצוע) |

## ‏מבנה JSON

```json
{
  "project": "voice-acp",
  "slice": "17",
  "verifier": "avigail | calev",
  "date": "2026-05-30T...",
  "verdict": "READY | USABLE-AFTER-FIX | NEEDS-REWORK | GO | NO-GO | PARTIAL",
  "findings": [
    {
      "id": 1,
      "severity": "blocker | regression | confusion | type-error | outdated | minor",
      "category": "<taxonomy below>",
      "summary": "תיאור קצר",
      "source_brief": "§4 Commit X",
      "source_code": "path/to/file.ts:line",
      "cost_estimate": "15-30min"
    }
  ]
}
```

## ‏טקסונומיה ראשונית

**‏אביגיל (plan)**:
`missing-symbol` | `dropped-branch` | `type-error` | `wrong-line-number` | `naming-inconsistency` | `wrong-path` | `outdated-risk` | `missing-dependency`

**‏כלב (runtime)**:
`bubble-grouping` | `cross-store-null` | `spec-drift` | `regression` | `mobile-desktop` | `reload-reconnect` | `library-compat` | `unique`

> ‏הטקסונומיה אינה קפואה — ‏ה-brief השני יזקק אותה מהדוחות שנצטברו.

## ‏מטרה

‏חומר-גלם מצטבר לזיקוק חוצה-פרויקטי (brief שני). ‏ה-severity הוא הציר העיקרי למדידה.
