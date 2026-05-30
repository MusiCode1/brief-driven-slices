# ‏פרויקט הבית של יתרו

‏זוהי תיקיית ה-cwd שממנה יתרו (orchestrator) מפעיל את ה-queue הלילי.

## ‏מבנה

```
orchestration/
├── README.md                  # ‏המסמך הזה
├── projects.json              # ‏רשימת פרויקטים פעילים (ערוך לפי הצורך)
├── AGENTS.md                  # ‏הוראות ל-יתרו בפרויקט זה
├── runs/                      # ‏סיכומי לילה (מרדכי קורא בבוקר)
│   └── <date>.summary.md
└── policies/                  # ‏מדיניות פר פרויקט (JSON)
    └── <project>.json
```

## ‏התחלה מהירה

```bash
# 1. ‏צור state dir לכל פרויקט
mkdir -p ~/.local/state/brief-driven-slices/<project>
cp ~/projects/brief-driven-slices/main/briefs/state.template.json \
   ~/.local/state/brief-driven-slices/<project>/state.json
# ‏ערוך state.json: project, repo_root, base_branch, dev_tip, slices

# 2. ‏הוסף לprojec.json
# ‏ראה projects.json.example

# 3. ‏פתח session יתרו מתיקייה זו:
# opencode --agent yetro
```

## ‏הרצת הqueue

```
‏ערב:
1. ‏מרדכי כותב briefs + אביגיל מאמתת
2. ‏מרדכי מעדכן state.json: plan_verified=true, dispatch_ready=true
3. ‏פתח session יתרו מתיקייה זו

‏יתרו מריץ אוטומטית. ‏אל תפריע.

‏בוקר:
1. ‏פתח session מרדכי
2. ‏קרא runs/<date>.summary.md
3. ‏בצע merges מאושרים (git merge --no-ff)
```

## ‏כללים

- ‏יתרו **‏לא ממזג** — ‏רק מרדכי אחרי אישור משתמשת
- ‏יתרו **‏לא מוחק worktrees** בזמן ריצה
- ‏יתרו **‏לא מתקן כשלים** — ‏מתעד ועוצר
- ‏flock מונע שני יתרו על אותו פרויקט
