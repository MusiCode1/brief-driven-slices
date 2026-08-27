// session-stream — ‏המתנה לסיום-turn ‏של סשן drive-coding, ‏דרך SSE.
//
// 🔴 ‏שתי עובדות שנמדדו 27/08 ‏ובלעדיהן הפרסור נכשל בשקט:
//
// 1. ‏**‏שתי צורות-פריים, ‏לא אחת:**
//      event: snapshot → {sessionId, version, epoch, updates:[ <update> ]}
//      event: update   → [ {jsonrpc, method:"session/update", params:{update:<update>}} ]
//    ‏פרסור שמכיר רק את הראשונה מחזיר [] ‏על השנייה, ‏והממתין לעולם לא יורה.
//
// 2. ‏**‏הרזולוציה העדינה ב-`_meta`:**
//      {sessionUpdate:"state_update", state:"running", _meta:{"_drive/turnState":"thinking"}}
//      {sessionUpdate:"state_update", state:"idle",   stopReason:"end_turn"}
//    ‏`state` ‏הקנוני מכיר שלוש דרגות ואנחנו חמש — ‏הגס בשדה, ‏העדין ב-`_meta`.
import { existsSync } from "node:fs"

/**
 * @returns {Promise<{code:0|2|3, why:string, stopReason?:string, frames:number, lastState:string}>}
 *   0 = ‏ה-turn ‏הסתיים / ‏סימן / ‏קובץ · 2 = ‏פג-זמן (‏לא כישלון) · 3 = ‏הזרם נסגר
 */
export async function waitForTurnEnd({ base, agent, marker, file, timeoutMs = 600_000 }) {
  const t0 = Date.now()
  let frames = 0, lastState = "?", sawBusy = false
  const out = (code, why, stopReason) => ({ code, why, stopReason, frames, lastState })
  if (file && existsSync(file)) return out(0, `‏הקובץ כבר קיים: ${file}`)

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort("timeout"), timeoutMs)
  let fileTimer
  if (file) fileTimer = setInterval(() => { if (existsSync(file)) ctrl.abort("file") }, 3000)
  const stop = () => { clearTimeout(timer); if (fileTimer) clearInterval(fileTimer) }

  let res
  try {
    res = await fetch(`${base}/api/agents/${agent}/events`, { signal: ctrl.signal })
  } catch { stop(); return out(3, "‏הזרם לא נפתח") }
  if (!res.ok) { stop(); return out(3, `‏הזרם נדחה: HTTP ${res.status}`) }

  const reader = res.body.getReader()
  const dec = new TextDecoder()
  let buf = ""
  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) { stop(); return out(3, "‏הזרם נסגר בלי סיום — ‏הסוכן מת או נותק") }
      buf += dec.decode(value, { stream: true })
      let i
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 1)
        if (!line.startsWith("data:")) continue
        frames++
        const raw = line.slice(5).trim()
        if (marker && raw.includes(marker)) { stop(); return out(0, `‏הסימן נצפה: "${marker}"`) }
        let d; try { d = JSON.parse(raw) } catch { continue }
        const items = Array.isArray(d) ? d : (d.updates ?? [])
        for (const x of items) {
          const u = x?.params?.update ?? x
          if (u?.sessionUpdate !== "state_update") continue
          lastState = u._meta?.["_drive/turnState"] ?? u.state ?? lastState
          if (u.state === "running") sawBusy = true
          else if (u.state === "idle" && sawBusy) {
            stop(); return out(0, "‏ה-turn ‏הסתיים", u.stopReason ?? "?")
          }
        }
      }
    }
  } catch (e) {
    stop()
    const why = ctrl.signal.reason
    if (why === "file") return out(0, `‏הקובץ נוצר: ${file}`)
    if (why === "timeout") return out(2, "‏פג הזמן — ‏קרא שוב")
    return out(3, `‏הזרם נקטע: ${String(e).slice(0, 80)}`)
  }
}
