#!/usr/bin/env node
// dispatch-via-api — ‏שיגור סוכן דרך ה-API ‏של drive-coding, ‏בשני שלבים.
//
// ‏למה שני שלבים ולא אחד (‏הכרעת-משתמש 27/08):
//   ‏רשימת-המודלים וההגדרות **‏נודעת רק אחרי שהסשן עלה**. ‏מי ששולח `modelOverride`
//   ‏ביצירה מנחש — ‏ו**‏ניחוש שגוי נבלע בשקט**: ‏נמדד 27/08 ‏ש-`modelOverride:"composer-2.5"`
//   ‏לא נתפס, ‏והסשן רץ על `grok-4.6[effort=high,fast=true]` ‏בלי שאיש ידע.
//   ⇒ ‏פותחים · ‏**‏קוראים מה יש** · ‏מגדירים מהרשימה · ‏ואז שולחים.
//
//   open  --cli cursor --cwd <dir> [--env K=V] [--permission allow_once] [--json]
//         [--parent <agentId>]  → ‏מזריק DC_PARENT+DC_BASE ‏לסביבת הילד
//         → ‏מדפיס agentId · sessionId · ‏קישור · modes · configOptions (‏מודלים!)
//
//   notify --agent <id> (--text <s> | --text-file <f>)
//         → ‏דוחף prompt ‏לסשן חי של סוכן אחר. ‏זו דרך הילד לדווח להורה.
//
//   close --agent <id> [--force]
//         → ‏מוחק את הסוכן. ‏מסרב אם `turnState != idle` ‏אלא אם `--force`.
//
//   send  --agent <id> --prompt-file <f> [--set model=<‏ערך מהרשימה>]...
//         [--file <‏דוח>] [--marker <s>] [--timeout 1800] [--idle-timeout 300]
//         [--no-wait] [--keep]
//
// ‏קודי-יציאה של send: ‏0 ‏סיום · 2 ‏פג-זמן כולל · 3 ‏הזרם נסגר · 5 ‏שקט (‏תקוע) · 4 ‏שימוש
// 🔴 ‏סגירת-הסוכן האוטומטית היא **‏רק בקוד 0**. ‏בכל השאר הוא נשאר חי — ‏אחרת מוחקים
//   ‏את הראיה. ‏אבל "‏נשאר חי" ‏אינו "‏נשאר לנצח": ‏מי ששיגר **‏חייב** ‏להריץ `close`
//   ‏אחרי שאסף את הראיה. ‏נמדד 27/08: ‏שני סוכנים יתומים על :4050 ‏בסוף היום.
import { readFileSync } from "node:fs"
import { waitForTurnEnd } from "./lib/session-stream.mjs"

const [cmd, ...rest] = process.argv.slice(2)
const get = (k, d) => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : d }
const has = (k) => rest.includes(k)
const multi = (k) => rest.reduce((acc, v, i) => (rest[i - 1] === k ? [...acc, v] : acc), [])
const BASE = get("--base", "http://127.0.0.1:4050")
const PUBLIC = get("--public-url", BASE).replace(/\/$/, "")

const j = async (url, init) => {
  const r = await fetch(url, init); const t = await r.text()
  if (!r.ok) throw new Error(`HTTP ${r.status} ${url} :: ${t.slice(0, 200)}`)
  return t ? JSON.parse(t) : {}
}
const post = (u, b) => j(u, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) })
const die = (m) => { console.error(m); process.exit(4) }

// ─── open ────────────────────────────────────────────────────────────────────
if (cmd === "open") {
  const cli = get("--cli"), cwd = get("--cwd")
  if (!cli || !cwd) die("open: --cli ‏ו---cwd ‏חובה")
  const env = Object.fromEntries(multi("--env").map((e) => { const i = e.indexOf("="); return [e.slice(0, i), e.slice(i + 1)] }))
  // ‏כתובת-החזרה: ‏בלי `DC_PARENT` ‏בסביבה, ‏הילד אינו יודע למי לדווח.
  if (get("--parent")) { env.DC_PARENT = get("--parent"); env.DC_BASE = BASE }
  const created = await post(`${BASE}/api/agents`, { cliKind: cli, cwd,
    ...(Object.keys(env).length ? { env } : {}),
    ...(get("--permission") ? { permissionPolicy: get("--permission") } : {}) })
  const agent = created.agentId

  // ⚠️ ‏טריגר ל-host ‏העצל. ‏בלעדיו /state ‏מחזיר 404 — ‏נמדד, ‏והפיל מבצע שלם.
  const c = new AbortController(); setTimeout(() => c.abort(), 15_000)
  try { const r = await fetch(`${BASE}/api/agents/${agent}/events`, { signal: c.signal }); await r.body?.cancel() } catch {}

  let st = null
  for (let i = 0; i < 20 && !st?.sessionId; i++) {
    try { st = await j(`${BASE}/api/agents/${agent}/state`) } catch {}
    if (!st?.sessionId) await new Promise((r) => setTimeout(r, 1500))
  }
  if (!st?.sessionId) { console.error("‏🔴 ‏הסשן לא עלה תוך 30ש'"); process.exit(3) }

  const url = `${PUBLIC}/chat/${cli}/${st.sessionId}?sessionTransport=http`
  if (has("--json")) { console.log(JSON.stringify({ agent, sessionId: st.sessionId, url, modes: st.modes, configOptions: st.configOptions }, null, 2)); process.exit(0) }
  console.log(`‏סוכן:    ${agent}\n‏סשן:     ${st.sessionId}\n‏קישור:   ${url}\n`)
  console.log(`modes: ${st.modes ? JSON.stringify(st.modes.availableModes?.map((m) => m.id) ?? st.modes) : "null"}`)
  for (const co of st.configOptions ?? []) {
    console.log(`\n## ${co.id} — ${co.name} · ‏נוכחי = ${co.currentValue}`)
    for (const o of co.options ?? []) console.log(`   ${o.value}`)
  }
  process.exit(0)
}

// ─── notify ──────────────────────────────────────────────────────────────────
// ‏הודעה מסוכן לסוכן: ‏דחיפת prompt ‏לסשן **‏חי** ‏של סוכן אחר. fire-and-forget.
// ‏נמדד 27/08 ‏על cursor: ‏ההודעה נקלטת **‏באמצע turn ‏רץ** (‏הסוכן ספר ל-60,
// ‏נעצר ב-57 ‏והשיב) — ‏בלי end_turn ‏ביניים. ‏זו דחיפה, ‏לא תור-לסוף.
// ⚠️ ‏פר-ספק: ‏claude ‏דוחף ל-turnQueue ‏מיָדית, ‏pi ‏ממתין לסוף-turn.
if (cmd === "notify") {
  const agent = get("--agent"), text = get("--text") ?? (get("--text-file") && readFileSync(get("--text-file"), "utf8"))
  if (!agent || !text) die("notify: --agent ‏ו-(--text | --text-file) ‏חובה")
  const st = await j(`${BASE}/api/agents/${agent}/state`)
  if (!st.sessionId) die(`notify: ‏לסוכן ${agent} ‏אין sessionId ‏חי`)
  const r = await post(`${BASE}/api/agents/${agent}/rpc`,
    { method: "session/prompt", params: { sessionId: st.sessionId, content: text } })
  console.log(`‏✅ ‏נמסר · version=${r.version} · ${agent}`)
  process.exit(0)
}

// ─── close ───────────────────────────────────────────────────────────────────
// ‏חובת-הסוגר: ‏כל סוכן שנפתח כאן נסגר כאן. ‏ר' `agents/mordechai.md §‏סגירת-סשן`.
if (cmd === "close") {
  const agent = get("--agent")
  if (!agent) die("close: --agent ‏חובה")
  let cwd = null
  try {
    const { agents = [] } = await j(`${BASE}/api/agents`)
    const a = agents.find((x) => x.id === agent)
    if (!a) { console.log(`‏אינו ברשימה — ‏כבר סגור: ${agent}`); process.exit(0) }
    cwd = a.cwd
  } catch (e) { console.error(`‏⚠️ ‏לא הצלחתי לקרוא את הרשימה: ${e.message}`) }

  // 🔴 ‏האות הוא `turnState` ‏מ-/state, **‏לא** `busy` ‏מהרשימה.
  // ‏נמדד 27/08: `busy` ‏הוא debounce-‏שקט של 1.5ש' (`turn-tracker.ts`) — ‏סוכן
  // ‏שחושב או מריץ כלי שקט יותר משנייה וחצי מדווח `busy:false` ‏באמצע turn.
  let turnState = null
  try { turnState = (await j(`${BASE}/api/agents/${agent}/state`)).turnState } catch {}
  if (turnState && turnState !== "idle" && !has("--force")) {
    console.error(`‏🔴 ‏turnState=${turnState} — ‏ה-turn **‏פתוח**. ‏לא נסגר. ‏המתן לסיום, ‏או --force.`)
    process.exit(3)
  }
  if (turnState === null) console.error(`‏⚠️ ‏אין /state (‏host ‏לא עלה?) — ‏סוגר בלי בדיקת-turn.`)
  const r = await fetch(`${BASE}/api/agents/${agent}`, { method: "DELETE" })
  console.log(`${r.ok ? "‏✅" : "‏🔴"} DELETE ${r.status} · ${agent}${cwd ? ` · ${cwd}` : ""}`)
  process.exit(r.ok ? 0 : 3)
}

// ─── send ────────────────────────────────────────────────────────────────────
if (cmd === "send") {
  const agent = get("--agent"), pf = get("--prompt-file")
  if (!agent || !pf) die("send: --agent ‏ו---prompt-file ‏חובה")
  const st0 = await j(`${BASE}/api/agents/${agent}/state`)
  const sid = st0.sessionId
  if (!sid) die("send: ‏אין sessionId ‏— ‏הרץ open ‏קודם")

  // ‏הגדרות **‏לפני** ‏הפרומפט, ‏ועם אימות שנתפסו
  for (const kv of multi("--set")) {
    const i = kv.indexOf("="); const id = kv.slice(0, i), value = kv.slice(i + 1)
    await post(`${BASE}/api/agents/${agent}/rpc`,
      { method: "session/set_config_option", params: { configId: id, value }, waitMs: 15_000 })
    const st = await j(`${BASE}/api/agents/${agent}/state`)
    const now = (st.configOptions ?? []).find((c) => c.id === id)?.currentValue
    console.log(`${now === value ? "‏✅" : "‏⚠️"} ${id} = ${now}${now === value ? "" : `  (‏ביקשתי ${value} — ‏**‏לא נתפס**)`}`)
  }

  await post(`${BASE}/api/agents/${agent}/rpc`,
    { method: "session/prompt", params: { sessionId: sid, content: readFileSync(pf, "utf8") } })
  console.log("‏המשימה נמסרה (202)")
  if (has("--no-wait")) process.exit(0)

  const r = await waitForTurnEnd({ base: BASE, agent, file: get("--file"), marker: get("--marker"),
    timeoutMs: Number(get("--timeout", "1800")) * 1000,
    idleTimeoutMs: Number(get("--idle-timeout", "0")) * 1000 })
  const icon = r.code === 0 ? "‏✅" : r.code === 2 ? "‏⏳" : "‏🔴"
  console.log(`${icon} ${r.why}${r.stopReason ? ` · stopReason=${r.stopReason}` : ""} · ‏פריימים=${r.frames} · ‏מצב=${r.lastState}`)
  if (r.code === 0 && !has("--keep")) {
    await fetch(`${BASE}/api/agents/${agent}`, { method: "DELETE" }); console.log("‏הסוכן נסגר.")
  } else if (r.code !== 0) console.log(
    `‏הסוכן **‏נשאר חי** ‏לבדיקה — ‏אחרי שאספת את הראיה, ‏סגור:\n`
    + `  scripts/dispatch-via-api.mjs close --base ${BASE} --agent ${agent}`)
  process.exit(r.code)
}

die("‏שימוש: dispatch-via-api.mjs open|send|notify|close …")
