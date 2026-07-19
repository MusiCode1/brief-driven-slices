#!/usr/bin/env python3
"""extract_sessions.py — חילוץ סשני-מאמת (אביגיל/כלב) לפורמט-מחקר קומפקטי.

מדוע: הטרנסקריפט הגולמי של ה-CLI (jsonl) ענק, מקונן, ובעל חיי-מדף קצרים
(מסתובב/נמחק). כדי לחקור "מה המאמתים *באמת* עושים" — צריך ארטיפקט יציב,
מסונן-רעש, ששמור ליד הדוחות ב-reports/. הסקריפט:

  1. סורק את ~/.claude/projects/*/*.jsonl
  2. מזהה סשנים שבהם ה-agent הראשי הוא מאמת (agentSetting / חתימת-prompt)
  3. מחלץ פר-סשן: מטא, היסטוגרמת-כלים, רצף-צעדים (שם-כלי + תקציר-arg +
     גודל-פלט — *ללא* גוף הפלט הענק), ונרטיב-הסוכן (טקסט/מסקנה)
  4. שומר JSON קומפקטי ל-<reports>/_sessions/<project>/<slice>-<agent>.session.json

השימוש:
  python3 scripts/extract_sessions.py --reports-dir main/reports          # שמירה
  python3 scripts/extract_sessions.py --reports-dir main/reports --dry-run # תצוגה בלבד
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

VERIFIERS = {"avigail", "calev", "calev-heavy"}
# חתימות ב-prompt הראשון כשה-agentSetting חסר
PROMPT_SIGS = ("mode: phase", "mode: light", "mode: heavy",
               "בדקי את ה-brief", "בדוק את ה-brief", "plan-verifier")

# איזה שדה-קלט מסכם הכי טוב כל כלי
ARG_KEY = {
    "Bash": "command", "Read": "file_path", "Write": "file_path",
    "Edit": "file_path", "Grep": "pattern", "Glob": "pattern",
    "Task": "description", "WebFetch": "url", "TodoWrite": "todos",
}


def _first_user_text(rows: list[dict]) -> str | None:
    for d in rows:
        if d.get("type") != "user":
            continue
        c = d.get("message", {}).get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text":
                    return b["text"]
    return None


def _primary_agent(rows: list[dict]) -> str | None:
    for d in rows:
        a = d.get("agentSetting")
        if isinstance(a, str):
            return a
    return None


def _parse_meta(prompt: str) -> dict:
    meta = {"mode": None, "project": None, "slice": None}
    for key, field in (("mode", "mode"), ("Project", "project"),
                       ("Slice", "slice"), ("project", "project"), ("slice", "slice")):
        m = re.search(rf"^{key}:\s*(.+)$", prompt, re.MULTILINE)
        if m and not meta[field]:
            meta[field] = m.group(1).strip()
    # נפילה-לאחור: חלץ project/slice מנתיבים בתוך ה-prompt (Brief:/Worktree:)
    if not meta["project"]:
        m = re.search(r"/Projects/([^/]+)/", prompt)
        if m:
            meta["project"] = m.group(1)
    if not meta["slice"]:
        m = re.search(r"/plans/([^/\s]+?)\.md", prompt)
        if m:
            meta["slice"] = m.group(1)
    for f in ("project", "slice", "mode"):
        if meta[f]:
            meta[f] = _slug(meta[f])
    return meta


def _slug(val: str) -> str:
    """שורה-ראשונה, תווים בטוחים לשם-קובץ, עד 60 תווים."""
    val = str(val).splitlines()[0] if str(val).splitlines() else ""
    val = re.sub(r"[^\w.\-]+", "-", val.strip()).strip("-")
    return val[:60] or ""


def _iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _summarize_arg(tool: str, inp: dict) -> str:
    key = ARG_KEY.get(tool)
    val = inp.get(key) if key else None
    if val is None:
        val = inp.get("command") or inp.get("file_path") or inp.get("pattern") or ""
    return re.sub(r"\s+", " ", str(val)).strip()[:200]


def build_agent_map(projects_dir: str) -> dict[str, str]:
    """סרוק סשני-אב ובנה מיפוי agentId -> subagent_type.

    הכלי `Agent` משגר subagents ברקע; ה-result מחזיר 'agentId: a…'.
    הטרנסקריפט של כל subagent נשמר ב-<parent>/subagents/agent-<agentId>.jsonl.
    כדי לדעת אם קובץ-subagent הוא אביגיל/כלב — צריך את הסוג מסשן-האב.
    """
    id2type: dict[str, str] = {}
    for pf in glob.glob(os.path.join(projects_dir, "*", "*.jsonl")):
        try:
            rows = [json.loads(l) for l in open(pf, encoding="utf-8") if l.strip()]
        except (json.JSONDecodeError, OSError):
            continue
        pending: dict[str, str] = {}  # tool_use_id -> subagent_type
        for d in rows:
            m = d.get("message", {})
            c = m.get("content") if isinstance(m, dict) else None
            if not isinstance(c, list):
                continue
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use" and b.get("name") == "Agent":
                    pending[b.get("id")] = b.get("input", {}).get("subagent_type")
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
                    txt = json.dumps(b.get("content"), ensure_ascii=False)
                    mm = re.search(r"agentId: (a[0-9a-f]+)", txt)
                    if mm:
                        id2type[mm.group(1)] = pending[b["tool_use_id"]]
    return id2type


def extract_session(jf: str, agent_hint: str | None = None) -> dict | None:
    rows = []
    for line in open(jf, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    prompt = _first_user_text(rows) or ""
    primary = _primary_agent(rows)
    agent = agent_hint or primary
    is_verif = agent in VERIFIERS or any(s in prompt for s in PROMPT_SIGS)
    if not is_verif:
        return None

    if agent not in VERIFIERS:
        agent = "avigail" if "brief" in prompt else "calev"
    meta = _parse_meta(prompt)

    # מפה tool_use_id -> גודל-פלט (מההודעה-user שאחריה)
    result_bytes: dict[str, int] = {}
    for d in rows:
        tur = d.get("toolUseResult")
        if isinstance(tur, dict):
            tid = tur.get("tool_use_id") or tur.get("toolUseID")
            if tid:
                result_bytes[tid] = len(json.dumps(tur, ensure_ascii=False))
        m = d.get("message", {})
        c = m.get("content") if isinstance(m, dict) else None
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    tid = b.get("tool_use_id")
                    body = b.get("content")
                    if tid:
                        result_bytes[tid] = len(json.dumps(body, ensure_ascii=False))

    steps = []
    narration = []
    hist = Counter()
    model = None
    ts_first = ts_last = None
    for d in rows:
        ts = _iso(d.get("timestamp"))
        if ts:
            ts_first = ts_first or ts
            ts_last = ts
        m = d.get("message", {})
        if not isinstance(m, dict):
            continue
        model = model or m.get("model")
        c = m.get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                tool = b.get("name", "?")
                hist[tool] += 1
                steps.append({
                    "i": len(steps) + 1,
                    "tool": tool,
                    "arg": _summarize_arg(tool, b.get("input", {})),
                    "out_bytes": result_bytes.get(b.get("id"), 0),
                })
            elif b.get("type") == "text" and b.get("text", "").strip():
                narration.append(b["text"].strip())

    dur = None
    if ts_first and ts_last:
        dur = round((ts_last - ts_first).total_seconds(), 1)

    return {
        "source_file": jf.replace(os.path.expanduser("~"), "~"),
        "agent": agent,
        "mode": meta["mode"],
        "project": meta["project"],
        "slice": meta["slice"],
        "model": model,
        "started": ts_first.isoformat() if ts_first else None,
        "ended": ts_last.isoformat() if ts_last else None,
        "duration_sec": dur,
        "num_tool_calls": sum(hist.values()),
        "tool_histogram": dict(hist),
        "total_out_bytes": sum(s["out_bytes"] for s in steps),
        "steps": steps,
        "narration": narration,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="חילוץ סשני-מאמת לפורמט-מחקר")
    ap.add_argument("--projects-dir",
                    default=os.path.expanduser("~/.claude/projects"),
                    help="ספריית סשני ה-CLI (ברירת מחדל: ~/.claude/projects)")
    ap.add_argument("--reports-dir", default="main/reports",
                    help="ריפו הדוחות — היעד ל-_sessions/")
    ap.add_argument("--dry-run", action="store_true",
                    help="הצג בלבד, אל תכתוב")
    args = ap.parse_args()

    out_root = Path(args.reports_dir) / "_sessions"
    print("בונה מיפוי agentId→סוג מסשני-האב…")
    id2type = build_agent_map(args.projects_dir)

    # מקורות: (א) קבצי subagent ברקע  (ב) סשנים שבהם מאמת הוא ה-agent הראשי
    targets: list[tuple[str, str | None]] = []
    for sf in glob.glob(os.path.join(args.projects_dir, "*", "*", "subagents", "agent-*.jsonl")):
        aid = os.path.basename(sf).replace("agent-", "").replace(".jsonl", "")
        targets.append((sf, id2type.get(aid)))
    for jf in glob.glob(os.path.join(args.projects_dir, "*", "*.jsonl")):
        targets.append((jf, None))

    sessions = []
    seen = set()
    for jf, hint in sorted(targets):
        if jf in seen:
            continue
        seen.add(jf)
        try:
            s = extract_session(jf, agent_hint=hint)
        except Exception as e:  # noqa: BLE001
            print(f"  ! שגיאה ב-{jf}: {e}")
            continue
        if s:
            sessions.append(s)

    print(f"נמצאו {len(sessions)} סשני-מאמת ניתנים-לשחזור")
    print(f"{'agent':12s} {'mode':6s} {'calls':>5s} {'sec':>6s} {'MB-out':>7s}  slice")
    for s in sessions:
        proj = s["project"] or "?"
        slc = s["slice"] or "?"
        print(f"{s['agent']:12s} {str(s['mode']):6s} {s['num_tool_calls']:5d} "
              f"{str(s['duration_sec']):>6s} {s['total_out_bytes']/1e6:7.2f}  {proj}/{slc}")

    if args.dry_run:
        print("\n(dry-run — לא נכתב)")
        return

    for s in sessions:
        proj = (s["project"] or "unknown").replace("/", "_")
        slc = (s["slice"] or "unknown").replace("/", "_")
        # מזהה-קצר מהקובץ כדי למנוע התנגשות (r1/r2, אותו slice)
        sid = re.search(r"agent-(a[0-9a-f]+)", s["source_file"])
        sid = sid.group(1)[:8] if sid else Path(s["source_file"]).stem[:8]
        d = out_root / proj
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{slc}-{s['agent']}-{sid}.session.json"
        path.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  → נכתבו {len(sessions)} קבצים תחת {out_root}/")


if __name__ == "__main__":
    main()
