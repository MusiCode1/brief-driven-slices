# systemd/ — טיימר הזיקוק

קבצי systemd user unit לטיימר הזיקוק היומי.

---

## התקנה

```bash
# העתק את ה-units לתיקיית systemd user
mkdir -p ~/.config/systemd/user/
cp ~/projects/brief-driven-slices/main/systemd/bds-distill.service ~/.config/systemd/user/
cp ~/projects/brief-driven-slices/main/systemd/bds-distill.timer ~/.config/systemd/user/

# הפעל את הטיימר
systemctl --user daemon-reload
systemctl --user enable --now bds-distill.timer

# בדוק שהטיימר רץ
systemctl --user status bds-distill.timer
```

---

## שינוי הסף (BDS_DISTILL_THRESHOLD)

ברירת המחדל: 10 דוחות חדשים.

### אופציה 1 — EnvironmentFile (מומלץ)

```bash
mkdir -p ~/.config/bds
echo "BDS_DISTILL_THRESHOLD=5" > ~/.config/bds/distill.env
```

ואז ב-`bds-distill.service`, בטל הערה מהשורה:
```ini
EnvironmentFile=%h/.config/bds/distill.env
```

ואז: `systemctl --user daemon-reload && systemctl --user restart bds-distill.timer`

### אופציה 2 — env var ישיר

```bash
# הרצה ידנית עם סף נמוך (לבדיקה):
BDS_DISTILL_THRESHOLD=0 ~/projects/brief-driven-slices/main/scripts/distill-run.sh
```

---

## בדיקה ידנית

```bash
# הרץ את הwrapper עם סף=0 (תמיד יופעל)
BDS_DISTILL_THRESHOLD=0 ~/projects/brief-driven-slices/main/scripts/distill-run.sh

# בדוק שה-data.json נוצר
ls ~/projects/brief-driven-slices/main/distillations/

# בדוק שה-branch נוצר ול-main לא נגעו
git -C ~/projects/brief-driven-slices log main --oneline -3
```

---

## לוגים

```bash
journalctl --user -u bds-distill.service -f
```

---

## הסרה

```bash
systemctl --user disable --now bds-distill.timer
systemctl --user disable bds-distill.service
rm ~/.config/systemd/user/bds-distill.{timer,service}
systemctl --user daemon-reload
```
