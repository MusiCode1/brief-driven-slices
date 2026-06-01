# Brief-Driven Slices

> A multi-agent workflow for building software with AI agents — without letting an
> over-eager model merge half-broken code into your main branch at 3 AM.

**Brief-Driven Slices (BDS)** splits development into small, well-specified *slices*.
Each slice gets a detailed **brief** written by a planner, the brief is **verified
before any code is written**, executed by a separate agent in an isolated git
worktree, **verified again at runtime**, and only then — with a human in the loop —
merged.

It is a methodology plus a concrete set of OpenCode agents that implement it.

---

## The problem it solves

The methodology was born from a failure. An autonomous "TDD with Sonnet" experiment
on a real project (`voice-acp`, Slice 9) produced **114 green tests and 19 real
bugs**. The tests were green; the software was broken.

Two root causes:

1. **The agent decided what to test.** When the same model writes the code *and*
   chooses the tests, it tends to test what it already believes works.
2. **One agent did everything** — plan, code, verify, and merge. There was no
   independent check, and the agent merged to the main branch without asking
   (5 of 7 recent merges in `voice-acp` went straight to `dev`, some within 45
   seconds of each other).

BDS fixes both by **separating the roles** and inserting two independent
verification gates — one *before* code is written, one *after*.

The current form has since run **5 consecutive slices with zero verification-stage
bugs**.

---

## How it works

```
Planner  ──writes brief──▶  Plan Verifier  ──verifies brief vs. real code──▶  (fix)
                                                                                │
                                                                                ▼
                                              new git worktree (isolated branch)
                                                                                │
                                                                                ▼
                                Executor  ──implements commit-by-commit──▶  Runtime Verifier
                                                                                │
                                                       checks Definition-of-Done
                                                       in a real environment
                                                                                │
                                                                                ▼
                                          Planner + human review ──▶ merge
```

Two **gates** guard the pipeline, and a clean verdict at each is a *precondition*:

| Gate | When | Rule |
|------|------|------|
| **plan-gate** | before any code is written | proceed only on a `READY` verdict from the plan verifier |
| **runtime-gate** | before merge | merge only on a `GO` verdict from the runtime verifier — anything less requires an explicit, documented, human-approved decision |

### Why a brief, and why verify it first?

A *brief* is a structured spec for a single slice: goal, scope (what's in, what's
out), an architecture sketch, an ordered list of commits — **and, per commit, the
testing strategy** (`tdd` / `integration` / `manual` / `none`). The planner makes
that choice, not the executor. That single move is what fixes root cause #1 above.

Verifying the brief *before* coding turns out to be the highest-leverage step in
the whole pipeline. Across the first 3 briefs that were checked this way, the plan
verifier found a real problem in **100% of them** (on average 3 issues per brief) —
usually an unverified assumption about an API or the environment. Cost: ~10 minutes.
Savings: 30–60 minutes of downstream debugging, plus silent regressions avoided.

### Worktrees & chaining

Each slice runs in its own git worktree on its own branch. Dependent slices can be
**chained** (slice B based on slice A's branch, not on `dev`) and run back-to-back
overnight, because `dev` is never touched until a human merges in the morning. That
makes discarding a failed chain completely safe — nothing downstream was affected.

`depends_on` is mandatory in every brief; the plan verifier rejects a brief that
omits it.

---

## The team — five agents, biblical names

The pipeline is implemented as five OpenCode agents. The names are Hebrew/biblical,
each chosen because the character embodies that exact role. (This started as a
Hebrew-language project; the names stuck because the rationale is genuinely apt.)

| Agent | Role | Merges? | Name rationale |
|-------|------|---------|----------------|
| **Mordechai** (מרדכי) | Planner — writes briefs, decides, merges | ✅ after human approval | The strategist of the Book of Esther: planned multi-step, **acted through other agents** (Esther), saved the people. The only candidate who *planned through others*. |
| **Yitro** (יתרו) | Orchestrator — runs the nightly queue | ❌ never | Jethro **invented delegation** (Exodus 18): saw Moses overwhelmed, built a hierarchy, solved scaling. |
| **Eliezer** (אליעזר) | Executor — implements the brief | ❌ never | Abraham's servant (Genesis 24): received a detailed brief, applied a test (Rebecca), reported back. Didn't improvise, didn't merge on his own. |
| **Avigail** (אביגיל) | Plan verifier (before) | ❌ | Abigail stopped David **before** an irreversible mistake (1 Samuel 25) — the essence of plan-stage verification. |
| **Calev** (כלב) | Runtime verifier (after) | ❌ | The spy who came back and told **the truth about what he actually saw on the ground** — runtime verification, reporting from the real environment. |

> **Model principle**: Opus where truth comes from **reasoning** (Mordechai's
> planning, Avigail on a static brief, Calev-heavy on edge cases / regressions).
> Sonnet where truth comes from **running** (Eliezer executing, Yitro's mechanical
> orchestration, Calev's lightweight runtime checks).

> **One rule above all:** only **Mordechai** merges, and only after explicit human
> approval — even if a verifier said `GO`. Merge is the point of no return; only
> someone who sees the full roadmap (the planner + the human) gets to make it.

---

## Three operating modes

- **Mode 1 — synchronous.** Human → Mordechai: "execute slice X". Mordechai
  dispatches Eliezer as a blocking sub-task, Calev verifies, Mordechai reports back,
  human approves, Mordechai merges.
- **Mode 2 — nightly.** In the evening Mordechai + Avigail prepare verified briefs.
  Overnight Yitro runs a queue (tmux, sequential, never blocking), dispatching
  Eliezer → Calev per slice and archiving results. In the morning Mordechai reads
  the summary, decides, and merges.
- **Mode 3 — direct.** Human → Eliezer directly. Legitimate but not the main path.

---

## Self-improvement loop (distillation)

The reports Avigail and Calev write (`reports/<project>/`) are periodically
*distilled* into three memory layers, so the methodology learns from its own
mistakes:

| Layer | File | Frequency |
|-------|------|-----------|
| **Live catalogs** | `plan-pitfalls.md` (planning mistakes), `patterns.md` (execution mistakes) | every distillation |
| **Distillation reports** | `distillations/<date>-report.md` | every distillation |
| **Global journal** | `docs/methodology-evolution.md` | rare (a real methodology change) |

A daily `systemd` timer runs a **quantitative** script (`distill.py` — it counts and
measures, it does *not* interpret), then an automated Mordechai session writes the
**qualitative** interpretation to a dedicated branch — and waits for a human merge
in the morning. The script never invents rules or merges; interpretation and merge
are always human(-model)-driven.

---

## When *not* to use this

- A small bug fix (< ~50 lines) — just do it directly.
- An exploratory spike — no clear Definition-of-Done, nothing to verify.
- An urgent hotfix — the brief + verifier overhead isn't worth it.
- A project with no git or no package manager — the worktree convention doesn't apply.

---

## Map of the repo

| Path | What it is |
|------|------------|
| [`SKILL.md`](SKILL.md) | The OpenCode skill definition — loads the whole methodology into an agent's context |
| [`workflow.md`](workflow.md) | The end-to-end protocol, step by step |
| [`worktrees.md`](worktrees.md) | The worktree convention and parallel-executor setup |
| [`orchestration.md`](orchestration.md) | Mode 2 internals — Yitro, the state machine, chaining, BLOCKED handling |
| [`patterns.md`](patterns.md) | Catalog of execution mistakes (Calev feeds it) |
| [`plan-pitfalls.md`](plan-pitfalls.md) | Catalog of planning mistakes (Avigail feeds it) |
| [`recommendations.md`](recommendations.md) | The brief template rationale and the guard-rails |
| [`agents/`](agents/) | The five agent definitions (`mordechai`, `yitro`, `eliezer`, `avigail`, `calev`, plus `calev-heavy`) |
| [`briefs/`](briefs/) | `BRIEF_TEMPLATE.md`, the executor-dispatch boilerplate, and the `state.json` template |
| [`docs/decisions/bds.md`](docs/decisions/bds.md) | **The "why" journal** — every design decision and the alternatives that were rejected |
| [`docs/methodology-evolution.md`](docs/methodology-evolution.md) | Global journal of how the methodology itself changed |
| [`case-studies/`](case-studies/) | The real slices the methodology was forged on |
| [`distillations/`](distillations/) | The self-improvement loop's outputs |

---

## Installing the agents (OpenCode)

```bash
bash scripts/install-agents.sh
```

This symlinks the agent definitions into `~/.config/opencode/agents/`.

---

*This methodology is itself developed using Brief-Driven Slices — the planner plans
slices of the methodology, the executor builds them in worktrees, and the verifiers
check them. The repo is its own first user.*
