#!/usr/bin/env python3
# discard_chain.py <project> <from-slice>
# ‏זורק slice ‏ואת ‏כל ‏מה ‏ש**‏תלוי ‏בו** ‏(dependents, ‏כלפי ‏מעלה). ‏מרדכי ‏מריץ ‏ידנית.
# ‏בטיחות: ‏מסרב ‏לזרוק slice ‏שכבר merged. ‏הגנת ‏מעגל ‏ב-visited set.
import json, sys, subprocess
from pathlib import Path

# ‏הקשחה ‏(תיקון #D): ‏עטיפת subprocess ‏מפני FileNotFoundError (tmux/git ‏לא ‏ב-PATH)
def run(cmd, **kw):
    try: return subprocess.run(cmd, **kw)
    except FileNotFoundError: return None

project, frm = sys.argv[1], sys.argv[2]
state_dir = Path.home() / ".local/state/brief-driven-slices" / project
state_path = state_dir / "state.json"
state = json.loads(state_path.read_text())
by_id = {s["id"]: s for s in state["slices"]}

if frm not in by_id:                    # ‏תיקון #7 — guard ‏ל-slice ‏לא-קיים
    sys.exit(f"unknown slice: {frm}")

# 1. compute dependents (‏מי ‏תלוי ב-frm, ‏טרנזיטיבית) — BFS ‏עם visited (‏הגנת ‏מעגל)
chain, queue, visited = set(), [frm], set()
while queue:
    cur = queue.pop(0)
    if cur in visited: continue        # ‏הגנת ‏מעגל
    visited.add(cur); chain.add(cur)
    for s in state["slices"]:
        if cur in s.get("depends_on", []) and s["id"] not in visited:
            queue.append(s["id"])
# frm ‏עצמו ‏כלול; ‏מה ‏שמתחתיו (dependencies) ‏לא — ‏רק dependents.

# 2. ‏בטיחות: ‏אף ‏אחד ‏לא merged
for sid in chain:
    if by_id[sid]["status"] == "merged":
        sys.exit(f"REFUSE: slice {sid} already merged — chain not safely discardable")

# 3. ‏לכל slice: ‏עצור tmux, ‏מחק worktree+branch, ‏סמן discarded, ‏נקה ‏קבצים
repo = state["repo_root"]
for sid in chain:
    s = by_id[sid]
    run(["tmux", "kill-session", "-t", f"bds-{project}-{sid}"], stderr=subprocess.DEVNULL)
    if s.get("worktree"):
        run(["git", "-C", repo, "worktree", "remove", "--force", s["worktree"]],
            stderr=subprocess.DEVNULL)
    if s.get("branch"):
        run(["git", "-C", repo, "branch", "-D", s["branch"]], stderr=subprocess.DEVNULL)
    s["status"] = "discarded"           # ‏שומר ‏רשומה, ‏לא ‏מוחק
    for sub in ("dispatches", "logs", "sentinels", "heartbeats", "blocked"):
        for f in (state_dir / sub).glob(f"{sid}.*"):
            f.unlink()
    print(f"discarded: {sid}")

# ‏כתיבה ‏אטומית ‏(תיקון #8): temp + rename ‏כדי ‏שלא ‏יישאר state.json ‏חצי-כתוב
tmp = state_path.with_suffix(".json.tmp")
tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
tmp.replace(state_path)
