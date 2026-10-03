#!/usr/bin/env python3
"""Print 1 only when an existing JSON acceptance receipt matches a bounded claim."""

import argparse
import json
import re
from pathlib import Path


def matches(receipt: Path, task: str, verdict: str, scope: str, sha: str) -> bool:
    try:
        data = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False

    recorded_scope = data.get("scope")
    recorded_task = data.get("taskId", data.get("taskID", data.get("task_id", data.get("task"))))
    if recorded_task is None and isinstance(recorded_scope, str):
        # Some existing receipts put the task ID in their scoped acceptance sentence.
        recorded_task = task if re.search(rf"(?<![A-Za-z0-9.]){re.escape(task)}(?![A-Za-z0-9.])", recorded_scope) else None
    recorded_sha = next((data[key] for key in ("candidateSHA", "sourceSHA", "codeSHA", "sha", "head") if key in data), None)
    return (
        isinstance(recorded_task, str)
        and recorded_task == task
        and data.get("verdict") == verdict
        and re.search(r"(^|_)GO($|_)", verdict) is not None
        and "NO_GO" not in verdict
        and recorded_scope == scope
        and isinstance(recorded_sha, str)
        and recorded_sha.lower() == sha.lower()
        and re.fullmatch(r"[0-9a-fA-F]{7,40}", sha) is not None
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--task", required=True)
    parser.add_argument("--verdict", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()
    print(int(matches(args.receipt, args.task, args.verdict, args.scope, args.sha)))


if __name__ == "__main__":
    main()
