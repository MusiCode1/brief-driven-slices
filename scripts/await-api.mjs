#!/usr/bin/env node
// await-api — ‏סנטינל לסוכן ששוגר דרך ה-API ‏של drive-coding.
//
// ‏נולד מפער 1 ‏ב-OPEN-GAPS ‏בגלגולו החדש: ‏שיגור דרך ה-API ‏מחזיר 202 ‏ואין קובץ .done.
// ‏מנוי ל-GET /api/agents/:id/events ‏ומכריע סיום לפי **‏מה שנצפה בזרם**.
//
// ‏שימוש:
//   await-api.mjs --base http://127.0.0.1:4050 --agent <id> \
//                 [--marker "<‏מחרוזת>"] [--file <‏נתיב>] [--timeout 600]
//
// ‏קודי-יציאה:
//   0  ‏ה-turn ‏הסתיים (idle) ‏— ‏או שהסימן/‏הקובץ הופיעו
//   2  ‏פג הזמן (‏**‏אינו כישלון** — ‏קרא שוב)
//   3  ‏הזרם נסגר בלי סיום — ‏הסוכן מת או נותק
//   4  ‏שגיאת-שימוש
import { existsSync } from "node:fs"

const a = process.argv.slice(2)
const get = (k, d) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : d }
const BASE = get("--base"), AGENT = get("--agent")
const MARKER = get("--marker"), FILE = get("--file")
const TIMEOUT = Number(get("--timeout", "600")) * 1000
if (!BASE || !AGENT) { console.error("await-api: --base ‏ו---agent ‏חובה"); process.exit(4) }

const t0 = Date.now()
let sawBusy = false, frames = 0, lastState = "?"

const done = (code, why) => {
  console.log(`${why} · ‏פריימים=${frames} · ‏מצב-אחרון=${lastState} · ${Math.round((Date.now()-t0)/1000)}s`)
  process.exit(code)
}
if (FILE && existsSync(FILE)) done(0, `‏✅ ‏הקובץ כבר קיים: ${FILE}`)

const ctrl = new AbortController()
setTimeout(() => { ctrl.abort(); done(2, "‏⏳ ‏פג הזמן — ‏קרא שוב") }, TIMEOUT)

// ‏בדיקת-קובץ ‏רצה במקביל: ‏דוח שנכתב הוא אות-סיום חזק יותר מ-idle
if (FILE) setInterval(() => { if (existsSync(FILE)) done(0, `‏✅ ‏הקובץ נוצר: ${FILE}`) }, 3000).unref?.()

// ‏🔴 ‏סיום-התור **‏כן** ‏מגיע בזרם — ‏אומת בניסוי 27/08:
//   {"sessionUpdate":"state_update","state":"idle","stopReason":"end_turn"}
//   {"sessionUpdate":"state_update","state":"running","_meta":{"_drive/turnState":"waiting"}}
// ‏ההנחה הקודמת ("turnState ‏אינו זורם") ‏נבעה מגריפ על שם-שדה שגוי:
// ‏הרזולוציה העדינה יושבת ב-`_meta["_drive/turnState"]`, ‏לא ב-"turnState".
// ⇒ ‏אין צורך לסקור את /state. ‏דחיפה, ‏לא polling — ‏**‏ועם הסיבה**.

const res = await fetch(`${BASE}/api/agents/${AGENT}/events`, { signal: ctrl.signal })
if (!res.ok) done(3, `‏🔴 ‏הזרם נדחה: HTTP ${res.status}`)

const reader = res.body.getReader()
const dec = new TextDecoder()
let buf = ""
while (true) {
  const { value, done: fin } = await reader.read()
  if (fin) done(3, "‏🔴 ‏הזרם נסגר בלי סיום — ‏הסוכן מת או נותק")
  buf += dec.decode(value, { stream: true })
  let i
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i); buf = buf.slice(i + 1)
    if (!line.startsWith("data:")) continue
    frames++
    const raw = line.slice(5).trim()
    if (MARKER && raw.includes(MARKER)) done(0, `‏✅ ‏הסימן נצפה: "${MARKER}"`)
    let d; try { d = JSON.parse(raw) } catch { continue }
    // 🔴 ‏שתי צורות-פריים, ‏ולא אחת (‏נמדד 27/08):
    //   event: snapshot → {sessionId, version, epoch, updates:[ <update> ]}
    //   event: update   → [ {jsonrpc,method:"session/update",params:{update:<update>}} ]
    // ‏פרסור שמכיר רק את הראשונה מחזיר [] ‏על השנייה — ‏ואז הסנטינל לעולם לא יורה.
    const items = Array.isArray(d) ? d : (d.updates ?? [])
    const ups = items.map((x) => x?.params?.update ?? x).filter(Boolean)
    // ‏snapshot ‏פותח ב-state:"idle" ‏של ה-turn ‏**‏הקודם** ⇒ ‏סופרים רק אחרי שנצפתה פעילות
    for (const u of ups) {
      if (u.sessionUpdate !== "state_update") continue
      const fine = u._meta?.["_drive/turnState"]
      lastState = fine ?? u.state ?? lastState
      if (u.state === "running") sawBusy = true
      else if (u.state === "idle" && sawBusy) {
        done(0, `‏✅ ‏ה-turn ‏הסתיים · stopReason=${u.stopReason ?? "?"}`)
      }
    }
  }
}
