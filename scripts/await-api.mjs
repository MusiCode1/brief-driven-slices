#!/usr/bin/env node
// await-api — ‏CLI ‏דק מעל lib/session-stream.mjs. ‏ר' שם את שתי מלכודות-הפרסור.
//   0 = ‏סיום · 2 = ‏פג-זמן (‏קרא שוב) · 3 = ‏הזרם נסגר · 4 = ‏שימוש
import { waitForTurnEnd } from "./lib/session-stream.mjs"
const a = process.argv.slice(2)
const get = (k, d) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : d }
const base = get("--base"), agent = get("--agent")
if (!base || !agent) { console.error("await-api: --base ‏ו---agent ‏חובה"); process.exit(4) }
const r = await waitForTurnEnd({ base, agent, marker: get("--marker"), file: get("--file"),
  timeoutMs: Number(get("--timeout", "600")) * 1000 })
console.log(`${r.code === 0 ? "‏✅" : r.code === 2 ? "‏⏳" : "‏🔴"} ${r.why}` +
  `${r.stopReason ? ` · stopReason=${r.stopReason}` : ""} · ‏פריימים=${r.frames} · ‏מצב=${r.lastState}`)
process.exit(r.code)
