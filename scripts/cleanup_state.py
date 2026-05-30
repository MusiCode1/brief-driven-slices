#!/usr/bin/env python3
# cleanup_state.py <project>
# ‏יתרו ‏קורא ‏לזה ‏בתחילת ‏כל ‏סשן. ‏python3 stdlib ‏בלבד (‏אין yq/PyYAML).
import json, os, sys, time, subprocess
from pathlib import Path

# ‏הקשחה ‏(תיקון #3): ‏עטיפת subprocess ‏מפני FileNotFoundError (tmux/git ‏לא ‏ב-PATH)
def run(cmd, **kw):
    try: return subprocess.run(cmd, **kw)
    except FileNotFoundError: return None

project = sys.argv[1]
state_dir = Path.home() / ".local/state/brief-driven-slices" / project
state = json.loads((state_dir / "state.json").read_text())
slices = {s["id"]: s for s in state["slices"]}

now = time.time()
def older_than(p, days):
    return p.is_file() and (now - p.stat().st_mtime) > days * 86400

# 1. logs/archived > 30 ‏יום → ‏מחק
for sub in ("logs", "archived"):
    for f in (state_dir / sub).glob("*"):
        if older_than(f, 30): f.unlink()

# 2. heartbeats ‏לא-פעילים > 7 ‏ימים → ‏מחק
for f in (state_dir / "heartbeats").glob("*"):
    if older_than(f, 7): f.unlink()

# 3. orphan tmux: bds-<project>-<id> ‏ש-id ‏שלו ‏לא in-progress → kill
#    (‏עיגון ‏מדויק ‏לפי id ‏מלא — ‏לא substring. ‏פותר N3.)
res = run(["tmux", "ls"], capture_output=True, text=True)
out = res.stdout if res else ""
for line in out.splitlines():
    name = line.split(":")[0]
    prefix = f"bds-{project}-"
    if not name.startswith(prefix): continue
    sid = name[len(prefix):]                    # ‏id ‏מדויק
    s = slices.get(sid)
    if s is None or s["status"] != "in-progress":
        run(["tmux", "kill-session", "-t", name])

# 4. worktrees ‏של slices ‏שמסומנים merged ‏ב-state ‏אבל ‏עוד ‏קיימים → ‏מחק (‏תיקון N2)
for s in state["slices"]:
    if s["status"] == "merged" and s.get("worktree"):
        wt = Path(s["worktree"])
        if wt.exists():
            run(["git", "-C", state["repo_root"],
                 "worktree", "remove", "--force", str(wt)])
            if s.get("branch"):
                run(["git", "-C", state["repo_root"],
                     "branch", "-D", s["branch"]])
