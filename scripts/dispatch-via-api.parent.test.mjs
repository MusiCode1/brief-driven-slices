import assert from "node:assert/strict"
import { execFile } from "node:child_process"
import { once } from "node:events"
import { createServer } from "node:http"
import { test } from "node:test"
import { fileURLToPath } from "node:url"
import { promisify } from "node:util"

const run = promisify(execFile)
const script = process.env.DISPATCH_VIA_API_TEST_SCRIPT
  ?? fileURLToPath(new URL("./dispatch-via-api.mjs", import.meta.url))
const agent = "fixture-agent"
const cwd = "/tmp/fixture-cwd"
const state = {
  sessionId: "fixture-session",
  modes: { availableModes: [{ id: "ask", name: "Ask" }] },
  configOptions: [{ id: "model", currentValue: "fixture-model" }],
}
const publicBase = "https://dispatch.example.test"

async function openAgent(t, args) {
  const requests = []
  const posts = []
  const server = createServer(async (req, res) => {
    requests.push(`${req.method} ${req.url}`)
    if (req.method === "POST" && req.url === "/api/agents") {
      try {
        req.setEncoding("utf8")
        let body = ""
        for await (const chunk of req) body += chunk
        posts.push({ contentType: req.headers["content-type"], body: JSON.parse(body) })
      } catch {
        res.writeHead(400).end()
        return
      }
      res.writeHead(201, { "Content-Type": "application/json" })
        .end(JSON.stringify({ agentId: agent }))
    } else if (req.method === "GET" && req.url === `/api/agents/${agent}/events`) {
      res.writeHead(200, { "Content-Type": "text/event-stream" }).end("data: {}\n\n")
    } else if (req.method === "GET" && req.url === `/api/agents/${agent}/state`) {
      res.writeHead(200, { "Content-Type": "application/json" }).end(JSON.stringify(state))
    } else {
      res.writeHead(404).end()
    }
  })
  t.after(async () => {
    if (!server.listening) return
    await new Promise((resolve, reject) => {
      server.close((error) => error ? reject(error) : resolve())
      server.closeAllConnections()
    })
  })
  const listening = once(server, "listening")
  server.listen(0, "127.0.0.1")
  await listening

  const base = `http://127.0.0.1:${server.address().port}`
  const { stdout } = await run(process.execPath, [
    script, "open", "--base", base, "--public-url", `${publicBase}/`,
    "--cli", "fixture", "--cwd", cwd, "--permission", "allow_once", "--json", ...args,
  ], { timeout: 10_000, killSignal: "SIGKILL" })

  assert.deepEqual(requests, [
    "POST /api/agents",
    `GET /api/agents/${agent}/events`,
    `GET /api/agents/${agent}/state`,
  ])
  assert.equal(posts.length, 1, "fixture received one valid JSON POST")
  assert.equal(posts[0].contentType, "application/json")
  assert.deepEqual(JSON.parse(stdout), {
    agent,
    ...state,
    url: `${publicBase}/chat/fixture/${state.sessionId}?sessionTransport=http`,
  })
  return { base, body: posts[0].body }
}

test("open --parent registers the parent and overrides legacy environment values", async (t) => {
  const parent = "fixture-parent"
  const { base, body } = await openAgent(t, [
    "--env", "DC_PARENT=legacy-parent",
    "--env", "DC_BASE=https://legacy.example.test",
    "--env", "CUSTOM=value",
    "--parent", parent,
  ])

  const { parentAgentId, ...input } = body
  assert.deepEqual(input, {
    cliKind: "fixture",
    cwd,
    permissionPolicy: "allow_once",
    env: { DC_PARENT: parent, DC_BASE: base, CUSTOM: "value" },
  })
  assert.equal(parentAgentId, parent, "POST body parentAgentId")
})

test("open with legacy DC_PARENT env keeps the parent field absent", async (t) => {
  const { body } = await openAgent(t, [
    "--env", "DC_PARENT=legacy-parent", "--env", "DC_BASE=https://legacy.example.test",
  ])

  assert.deepEqual(body, {
    cliKind: "fixture",
    cwd,
    permissionPolicy: "allow_once",
    env: { DC_PARENT: "legacy-parent", DC_BASE: "https://legacy.example.test" },
  })
})
