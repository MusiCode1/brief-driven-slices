#!/usr/bin/env node
// dispatch-via-api — ‏שיגור סוכן דרך ה-API ‏של drive-coding, ‏מקצה-לקצה.
//
// ‏המקבילה של `dispatch-agent`, ‏בלי tmux ‏ובלי acpx. ‏מה שהיא נותנת ו-tmux ‏לא:
// ‏הסוכן **‏מופיע ברשימה**, ‏יש לו **‏URL**, ‏ואפשר **‏לצפות בו רץ מכל מכשיר**.
//
//   dispatch-via-api.mjs --base http://127.0.0.1:4050 \
//     --cli cursor --model composer-2.5 --cwd <dir> --prompt-file <file> \
//     [--env K=V]... [--permission allow_once] [--public-url https://…] \
//     [--file <‏דוח-שמסמן-סיום>] [--timeout 1800] [--no-wait] [--keep]
//
// ‏מחזור-החיים: create → ‏טריגר-host → prompt → ‏המתנה → **‏סגירה**.
// 🔴 ‏סגירה **‏רק בהצלחה**. ‏בכישלון/‏פג-זמן הסוכן **‏נשאר חי** ‏— ‏אחרת מוחקים את
// ‏הראיה בדיוק כשצריך אותה. `--keep` ‏משאיר תמיד.
import { readFileSync } from "node:fs"
import { waitForTurnEnd } from "./lib/session-stream.mjs"

const a = process.argv.slice(2)
const get = (k, d) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : d }
const has = (k) => a.includes(k)
const envs = a.reduce((acc, v, i) => (a[i - 1] === "--env" ? [...acc, v] : acc), [])

const BASE = get("--base", "http://127.0.0.1:4050")
const CLI = get("--cli"), CWD = get("--cwd"), PF = get("--prompt-file")
if (!CLI || !CWD || !PF) { console.error("dispatch-via-api: --cli ‏--cwd ‏--prompt-file ‏חובה"); process.exit(4) }
const PUBLIC = (get("--public-url", BASE)).replace(/\/$/, "")
const TIMEOUT = Number(get("--timeout", "1800")) * 1000

const j = async (url, init) => {
  const r = await fetch(url, init)
  const t = await r.text()
  if (!r.ok) throw new Error(`HTTP ${r.status} ${url} :: ${t.slice(0, 200)}`)
  return t ? JSON.parse(t) : {}
}
const post = (u, b) => j(u, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) })

// 1 · ‏יצירה
const env = Object.fromEntries(envs.map((e) => { const i = e.indexOf("="); return [e.slice(0, i), e.slice(i + 1)] }))
const body = { cliKind: CLI, cwd: CWD, ...(get("--model") ? { modelOverride: get("--model") } : {}),
  ...(Object.keys(env).length ? { env } : {}),
  ...(get("--permission") ? { permissionPolicy: get("--permission") } : {}) }
const created = await post(`${BASE}/api/agents`, body)
const agent = created.agentId
console.log(`‏סוכן: ${agent}  (${CLI}${get("--model") ? "/" + get("--model") : ""})`)

// 2 · ‏טריגר ל-host ‏העצל. ⚠️ ‏בלעדיו /state ‏מחזיר 404 ‏— ‏נמדד, ‏והפיל מבצע שלם.
const ctrl = new AbortController()
setTimeout(() => ctrl.abort(), 15_000)
try { const r = await fetch(`${BASE}/api/agents/${agent}/events`, { signal: ctrl.signal }); await r.body?.cancel() } catch {}

let sid = null
for (let i = 0; i < 20 && !sid; i++) {
  try { sid = (await j(`${BASE}/api/agents/${agent}/state`)).sessionId } catch {}
  if (!sid) await new Promise((r) => setTimeout(r, 1500))
}
if (!sid) { console.error("‏🔴 ‏הסשן לא עלה — ‏אין sessionId ‏אחרי 30ש'"); process.exit(3) }

const url = `${PUBLIC}/chat/${CLI}/${sid}?sessionTransport=http`
console.log(`‏קישור: ${url}`)

// 3 · ‏המשימה
await post(`${BASE}/api/agents/${agent}/rpc`,
  { method: "session/prompt", params: { sessionId: sid, content: readFileSync(PF, "utf8") } })
console.log("‏המשימה נמסרה (202)")
if (has("--no-wait")) process.exit(0)

// 4 · ‏המתנה
const r = await waitForTurnEnd({ base: BASE, agent, file: get("--file"), marker: get("--marker"), timeoutMs: TIMEOUT })
console.log(`${r.code === 0 ? "‏✅" : r.code === 2 ? "‏⏳" : "‏🔴"} ${r.why}` +
  `${r.stopReason ? ` · stopReason=${r.stopReason}` : ""} · ‏פריימים=${r.frames} · ‏מצב=${r.lastState}`)

// 5 · ‏סגירה — ‏רק בהצלחה
if (r.code === 0 && !has("--keep")) {
  await fetch(`${BASE}/api/agents/${agent}`, { method: "DELETE" })
  console.log("‏הסוכן נסגר.")
} else if (r.code !== 0) {
  console.log(`‏הסוכן **‏נשאר חי** ‏לבדיקה: ${url}`)
}
process.exit(r.code)
