# Slice — inboxsms-m2m-api — בריף

> **תאריך**: 2026-08-20
> **סוג מסמך**: בריף ביצועי לסלייס — לא תוכנית טרום-בריף
> **סטטוס**: טיוטה — תוקן אחרי אביגיל (USABLE-AFTER-FIX)
> **אימות אביגיל**: READY (דוח: `main/reports/InboxSMS/slice-inboxsms-m2m-api-avigail.md`, 2026-08-20, סבב 2)
> **Dispatch**: מותר לאליעזר רק אם `אימות אביגיל = READY`
> **Complexity**: 5/10 (verifier: light + phase אחרי commit 1)
> **תלויות (`depends_on`)**: []
> **Base**: `master` (InboxSMS) · `dev` (students-and-school-manager — רק commit אחרון)
> **Dev tip**: InboxSMS `8268a36` · students-and-school-manager — HEAD של dev

---

## §0 — Pre-flight

> סוכן חדש בלי context: אחרי סעיף זה יודע איך להריץ, באיזה repo, ומה לקרוא.

### שני repositories

| Repo | נתיב | תפקיד ב-slice |
|------|------|----------------|
| **InboxSMS** | `/home/user/Projects/InboxSMS` | עיקרי — multi-account API + UI merged |
| **students-and-school-manager** | `/home/user/Projects/students-and-school-manager` | commit אחרון בלבד — `backup/scripts/tiktak-login.cjs` |

**Worktree ראשי** — InboxSMS:

```bash
cd /home/user/Projects/InboxSMS
git worktree add .worktrees/inboxsms-m2m-api -b slice/inboxsms-m2m-api master
cd .worktrees/inboxsms-m2m-api
npm install
```

**Worktree משני** (רק ל-commit 4) — students-and-school-manager:

```bash
cd /home/user/Projects/students-and-school-manager
git worktree add .worktrees/tiktak-login-api -b slice/tiktak-login-api dev
```

### Deploy (Cloudflare Pages vs adapter)

- **Prod URL:** `https://sms-inbox.pages.dev` (Cloudflare Pages).
- **קוד היום:** `svelte.config.js` = `@sveltejs/adapter-vercel` — לא adapter-cloudflare.
- **לפני deploy:** לאשר pipeline בפועל (wrangler / CI). אם נדרש — commit ל-adapter או תיעוד בלבד.
- **אסור** להוסיף `API_ACCOUNTS`/סיסמות ל-`vite.config.ts` `define` — רק `$env/dynamic/private` ב-server.

> אין AGENTS.md ייעודי ב-InboxSMS. env רלוונטי — למטה.

### משתני סביבה (InboxSMS)

קיים היום (`.env.example`):

- `API_USERNAME`, `API_PASSWORD` — call2all **חשבון יחיד**
- `CLIENT_USERNAME`, `CLIENT_PASSWORD` — UI login
- `KV_REST_API_URL`, `KV_REST_API_TOKEN` — Upstash Redis (prod)
- `API_URL` — ברירת מחדל `https://www.call2all.co.il/ym/api/`

**חדש ב-slice:**

- `API_KEY` — secret למכונות (Bearer / X-API-Key)
- `API_ACCOUNTS` — JSON array של חשבונות call2all (ראה §3)

**דוגמת `API_ACCOUNTS` (prod — שני מספרים):**

```json
[
  {
    "id": "sms-reception",
    "label": "מערכת קבלת SMS",
    "phone": "0515131038",
    "username": "<call2all_user_1>",
    "password": "<call2all_pass_1>"
  },
  {
    "id": "tiktak-otp",
    "label": "OTP tik-tak",
    "phone": "0559661922",
    "username": "<call2all_user_2>",
    "password": "<call2all_pass_2>"
  }
]
```

**Backward compat:** אם `API_ACCOUNTS` ריק/חסר — fallback ל-`API_USERNAME`/`API_PASSWORD` כחשבון יחיד; `phone` = `API_USERNAME` (התנהגות נוכחית).

### איך להריץ (InboxSMS)

```bash
cd .worktrees/inboxsms-m2m-api
cp .env.example .env   # מלא creds אמיתיים מקומית — לא commit
npm run dev            # http://localhost:5173
npm run check          # svelte-check
npm test               # Playwright (דורש .env + creds)
npm run build
```

### Browser / deploy

- **Prod UI+API:** `https://sms-inbox.pages.dev` (Cloudflare Pages)
- **Legacy:** `inbox-sms.vercel.app` (Vercel adapter ב-`svelte.config.js`)
- אחרי merge: להגדיר `API_KEY` + `API_ACCOUNTS` ב-env של Pages/Vercel
- **אין** commit של secrets; Bitwarden item `inbox-sms` (`9f81918b…`)

### Reading list

**must-read:**

- `src/lib/server/api.ts` — Login + GetSmsIncomingLog, token cache key יחיד `api_token`
- `src/routes/+page.server.ts` — UI load/login/refresh
- `src/lib/server/apiKeyAuth.ts` — **קיים untracked** — לכלול ב-commit 0
- `/home/user/Projects/students-and-school-manager/backup/scripts/tiktak-login.cjs` — OTP flow שביר
- `/home/user/Projects/students-and-school-manager/llm-docs/HOWTO-מיפוי-וסקרייפינג-תיק-תק.md` §0 — OTP regex, מספרים

**reference:**

- `src/lib/components/Message.svelte` — `findCode()` generic
- `src/lib/types.ts` — `Message` shape
- call2all API: `https://www.call2all.co.il/ym/api/` — Login, GetSmsIncomingLog (POST JSON, limit 100)

### מקורות חיצוניים — עיגון + מסקנות מחייבות

- **call2all YM API** — POST לכל endpoint; Login מחזיר `token`; GetSmsIncomingLog עם `{ token, limit }` מחזיר `rows[]` עם `{ server_date, phone, dest, message }`. **מסקנה:** אין endpoint מרוכז multi-number — כל חשבון = Login נפרד + GetSmsIncomingLog נפרד; merge בצד InboxSMS.
- **HOWTO tik-tak §0** — OTP: `dest=0559661922`; regex `/מאת:\s*tiktak\s*\n\s*(\d{6})/i`; לא לקחת קוד מתאריך/שדות אחרים.

---

## §1 — מטרה

אחרי ה-slice: סוכן (או `tiktak-login.cjs`) יכול לקבל OTP של tik-tak **בלי לפתוח דפדפן** על SMS inbox — עם `curl`/fetch ו-`API_KEY`. במקביל, InboxSMS מציגה ומחזירה **את כל ההודעות האחרונות משני חשבונות call2all** (0515131038 + 0559661922), ממוינות לפי תאריך, עם API שמפרסם אילו מספרים מחוברים כרגע.

---

## §2 — Scope

| פיצ'ר | כן/לא | לאן |
|------|------|------|
| Multi-account call2all (2+ חשבונות) | ✅ | slice זה |
| Token cache **פר חשבון** ב-Redis | ✅ | slice זה |
| `GET /api/numbers` — רשימת מספרים זמינים | ✅ | slice זה |
| `GET /api/messages` — merged messages + filters | ✅ | slice זה |
| `GET /api/otp/latest` — OTP לסוכנים | ✅ | slice זה |
| `API_KEY` auth על `/api/*` | ✅ | slice זה |
| Backward compat `API_USERNAME`/`API_PASSWORD` יחיד | ✅ | slice זה |
| UI: הצגת הודעות merged מכל החשבונות | ✅ | slice זה |
| UI: בורר/סינון לפי מספר (כמו HOWTO מתאר) | ✅ | slice זה — כפתורים, לא `<select>` |
| עדכון `tiktak-login.cjs` — polling API | ✅ | commit 4, repo שני |
| גיבוי behavior tik-tak (L5/L6) | ❌ | slice נפרד אחרי login עובד |
| שינוי call2all API / limit >100 | ❌ | מחוץ לסקופ |
| commit secrets / PII | ❌ | אסור |

---

## §3 — Architecture diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     env: API_ACCOUNTS[]                      │
│   [ {id, phone:0515131038, user, pass},                       │
│     {id, phone:0559661922, user, pass} ]                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  accounts.ts (חדש)    │
              │  parseAccounts()        │
              │  fallback → single env  │
              └────────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │ api.ts    │    │ tokenCache│    │ tokenCache│
   │ login()   │    │ key:      │    │ key:      │
   │ per acct  │    │ api_token:│    │ api_token:│
   └─────┬─────┘    │ sms-recep │    │ tiktak-otp│
         │          └─────┬─────┘    └─────┬─────┘
         │                │                │
         └────────────────┼────────────────┘
                          ▼
              ┌────────────────────────┐
              │  messages.ts (חדש)      │
              │  fetchAllMessages()     │
              │  Promise.all(accounts)  │
              │  → tag accountId/phone  │
              │  → merge sort desc      │
              │  filterMessages()       │
              │  extractTiktakOtp()     │
              └────────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  +page.server.ts   /api/messages     /api/otp/latest
  (UI merged)       /api/numbers      assertApiKey()
                           │
                           ▼
              ┌────────────────────────┐
              │ tiktak-login.cjs        │
              │ poll /api/otp/latest    │
              │ dest=0559661922         │
              └────────────────────────┘
```

**Message shape מורחב (server-only, לא לשבור UI בלי adapt):**

```ts
interface EnrichedMessage extends Message {
  accountId: string;      // e.g. "tiktak-otp"
  accountPhone: string;   // e.g. "0559661922"
}
```

---

## §4 — Commits בסדר

### Commit 0 — accounts config + token cache per account (approach: integration)

**קבצים חדשים:**

- `src/lib/server/accounts.ts`
- `src/lib/server/messages.ts` — skeleton: `fetchAllMessages`, `listAccountPhones`

**קבצים שמשתנים:**

- `src/lib/server/api.ts` — refactor: `apiClient` מקבל `{ username, password }` per call; `tokenCache` עם key `api_token:${accountId}`
- `src/lib/server/apiKeyAuth.ts` — **commit הקובץ הקיים** (untracked)
- `.env.example` — `API_KEY`, `API_ACCOUNTS` (JSON example commented)
- `package.json` — הוסף `"test": "playwright test"` (חסר היום; README מניח npm test)

**API skeleton:**

```ts
// accounts.ts
export interface Call2AllAccount {
  id: string;
  label: string;
  phone: string;
  username: string;
  password: string;
}
export function loadAccounts(): Call2AllAccount[];

// messages.ts
export async function fetchAllMessages(): Promise<EnrichedMessage[]>;
export function listAvailableNumbers(accounts: Call2AllAccount[]): { id: string; phone: string; label: string }[];
```

**Verification:**

```bash
npm run check
# manual: node -e "import('./src/lib/server/accounts.ts')" — או smoke script קטן
```

---

### Commit 1 — filter, merge, OTP extraction (approach: tdd)

**קבצים:**

- `src/lib/server/messages.ts` — `filterMessages`, `extractTiktakOtp`, `findLatestOtp`
- `src/lib/server/messages.test.cjs` — **CommonJS** + `node:test` (אין vitest/tsx בפרויקט — `.ts` לא ירוץ)

**חתימות:**

```ts
export function filterMessages(
  rows: EnrichedMessage[],
  opts: { dest?: string; sender?: string; accountId?: string; sinceSeconds?: number; limit?: number }
): EnrichedMessage[];

export function extractTiktakOtp(text: string): string | null;
// primary: /מאת:\s*tiktak\s*\n\s*(\d{6})/i
// fallback: /\b(\d{6})\b/ only if text matches /tiktak/i

export function findLatestOtp(
  rows: EnrichedMessage[],
  opts: { dest?: string; sinceSeconds?: number }
): { otp: string; message: EnrichedMessage } | null;
```

**Verification:**

```bash
node --test src/lib/server/messages.test.cjs
npm run check
```

**Verifier-phase:** כן — אחרי commit זה.

---

### Commit 2 — HTTP API routes (approach: integration)

**קבצים חדשים:**

- `src/routes/api/numbers/+server.ts`
- `src/routes/api/messages/+server.ts`
- `src/routes/api/otp/latest/+server.ts`

**התנהגות:**

| Route | Query params | Response |
|-------|--------------|----------|
| `GET /api/numbers` | — | `{ numbers: [{ id, phone, label }] }` |
| `GET /api/messages` | `dest?`, `sender?`, `account?`, `since?` (seconds), `limit?` (default 100) | `{ messages: EnrichedMessage[] }` |
| `GET /api/otp/latest` | `dest?` (default `0559661922`), `since?` (default 120) | 200 `{ otp, server_date, phone, dest, accountId, message }` · 404 אם אין |

**Auth:** `assertApiKey(request)` בתחילת כל handler.

**Errors:** 401 unauthorized · 503 אם `API_KEY` unset · לא ל-log OTP/body ב-prod.

**Verification:**

```bash
npm run dev &
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/api/numbers
# expect 401 without key

curl -s -H "Authorization: Bearer $API_KEY" \
  "http://localhost:5173/api/numbers"

curl -s -H "Authorization: Bearer $API_KEY" \
  "http://localhost:5173/api/messages?limit=5"

curl -s -H "Authorization: Bearer $API_KEY" \
  "http://localhost:5173/api/otp/latest?dest=0559661922&since=3600"
```

---

### Commit 3 — UI merged + phone filter (approach: manual)

**קבצים:**

- `src/routes/+page.server.ts` — `fetchAllMessages()` במקום single-account; pass `accounts`/`numbers` ל-client
- `src/routes/+page.svelte` — הצג `numbers`; default «הכל»
- `src/lib/components/MessageList.svelte` — כפתורי סינון לפי `accountPhone` / «הכל» (כפתורים, לא `<select>` — HOWTO)
- `src/lib/types.ts` — `EnrichedMessage` (optional export)
- `tests/login.spec.ts` — **תקן** `page.goto('/messages')` → `page.goto('/')` (route `/messages` לא קיים)

**לא לשבור:** login/logout/refresh form actions.

**Verification:**

```bash
npm run check
npm run build
npm test   # playwright — דורש .env + creds; script נוסף ב-C0
# manual: login → רואים הודעות משני מספרים (אם creds לשניהם) → סינון עובד
```

---

### Commit 4 — tiktak-login polling (approach: manual) — repo שני

**Repo:** `students-and-school-manager` · worktree `slice/tiktak-login-api`

**קובץ:**

- `backup/scripts/tiktak-login.cjs`

**שינויים:**

- הסר `fetchOtp()` עם Playwright tab ל-SMS UI
- הוסף `fetchOtpViaApi({ sinceMs })` — poll `GET ${SMS_API_URL}/api/otp/latest?dest=0559661922&since=...` כל 3s, עד 40 ניסיונות
- Env: `SMS_API_KEY` (חובה), `SMS_API_URL` (default `https://sms-inbox.pages.dev`); הסר חובה על `SMS_USER`/`SMS_PASS`
- שמור `TTIK_USER`, `TTIK_PASS`; record timestamp **לפני** submit password

**Verification:**

```bash
# אחרי deploy InboxSMS + API_KEY ב-prod:
TTIK_USER=… TTIK_PASS=… SMS_API_KEY=… \
  docker exec … node artifacts/tiktak-login.cjs
# expect: "login ok" + darchey URL
```

**הערה:** commit זה **תלוי** ב-deploy של commits 0–2 ל-prod (או local dev עם tunnel). אם prod לא מוכן — אפשר לבדוק מול `npm run dev` + tunnel.

---

## §5 — DoD verifiable

| # | בדיקה | איך |
|---|------|-----|
| 1 | typecheck + build | `npm run check && npm run build` (InboxSMS) |
| 2 | unit tests OTP/filter | `node --test src/lib/server/messages.test.cjs` |
| 3 | `/api/numbers` מחזיר 2 מספרים | curl עם API_KEY; `numbers.length >= 2` (prod/staging creds) |
| 4 | `/api/messages` merged | curl; הודעות עם `accountId`/`accountPhone` שונים; sorted desc |
| 5 | `/api/otp/latest` | curl; 200 עם otp תקין **או** 404 אם אין הודעה בחלון (לא 500) |
| 6 | API בלי key → 401 | curl בלי header |
| 7 | UI: סינון לפי מספר | manual — login, לחץ מספר, רשימה מצטמצמת |
| 8 | Backward compat | `.env` בלי `API_ACCOUNTS` — עדיין עובד עם `API_USERNAME`/`API_PASSWORD` יחיד |
| 9 | tiktak-login | `node tiktak-login.cjs` → `login ok` (smoke, דורש CDP + creds) |
| 10 | אין secrets ב-git | `git diff` — לא `.env`, לא API_KEY |

---

## §6 — Risks + mitigations

| סיכון | מקור | מitigation |
|------|------|------------|
| Token cache collision | `api_token` key יחיד היום | key per `accountId`: `api_token:${id}` |
| OTP ישן נלקח | SMS קודם עדיין ב-log | `since` מ-anchor לפני submit; default 120s |
| חשבון אחד נכשל → 500 על הכל | Promise.all strict | `fetchAllMessages`: allSettled; include `errors[]` per account; UI/API still return partial |
| `API_ACCOUNTS` JSON שגוי | typo ב-env | validate at startup; log account ids; fail fast on parse error |
| Playwright tests נשברים | UI שינוי | הרץ `npm test`; עדכן selectors אם צריך |
| Pages vs Vercel env drift | שני hosts | document both; smoke על sms-inbox.pages.dev |

**3 שתמיד נשכחים:**

1. לא commit creds
2. OTP regex tik-tak — לא generic date digits
3. כפתורי סינון UI — לא `<select>` (HOWTO)

---

## §7 — Escalation triggers

> אם X — עצור ושאל את המשתמש:

- call2all מחזיר פורמט שונה מ-`rows[]` documented
- רק חשבון אחד זמין ב-Bitwarden (לא 2)
- `API_ACCOUNTS` לא נתמך ב-Cloudflare Pages env size
- tiktak-login עובד מול dev אבל לא prod
- Brief סותר HOWTO על regex OTP

---

## §8 — Complexity score + verifier tier

| פרמטר | ניקוד |
|------|------|
| Cross-store / multi-account fetch | +2 |
| Protocol contract חדש (`/api/*`) | +2 |
| Refactor קוד קיים (`api.ts`) | +1 |
| >5 files | +1 |
| Deploy לפרודקשן (Pages; adapter mismatch) | +1 |
| Pure logic tests (OTP) | -1 |
| Greenfield API routes | -1 |

**Score**: 5 / 10

**Tier**: `verifier-slice-light` + `verifier-phase` אחרי commit 1 (OTP logic) ו-commit 2 (API smoke)

**Verifier-phase אחרי commit/phase**: 1, 2

---

## §9 — שאלות פתוחות

| # | שאלה | ברירת מחדל | חוסם? |
|---|------|----------|------|
| 1 | האם `0515131038` ו-`0559661922` creds שניהם ב-Bitwarden item אחד? | כן — שדות נפרדים באותו item; executor ממלא `API_ACCOUNTS` locally | ❌ |
| 2 | Deploy ראשון ל-Pages או Vercel? | Pages (`sms-inbox.pages.dev`) — HOWTO מפנה לשם | ❌ |
| 3 | האם commit 4 (tiktak-login) באותו PR כ-InboxSMS? | **לא** — שני repos, שני PRs; InboxSMS קודם, deploy, אז SSM | ❌ |
| 4 | Limit 100 per account — מספיק? | כן — כמו UI היום; merge עד 200 max | ❌ |

---

## סטיות מהתכנון (מתעדכן ע"י executor)

### אחרי אביגיל (2026-08-20)

- C1: `messages.test.cjs` במקום `.ts` (אין TS test runner)
- C0: `"test": "playwright test"` ב-package.json
- C3: תיקון `tests/login.spec.ts` `/messages` → `/`
- §0: הערת deploy Pages vs adapter-vercel; איסור API_ACCOUNTS ב-vite define

---

- (ריק — executor)
