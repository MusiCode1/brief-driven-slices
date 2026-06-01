#!/usr/bin/env python3
"""
scripts/distill.py — מנוע כמותי דטרמיניסטי לזיקוק דוחות אביגיל/כלב.

סופר, מודד, מחשב דלתא, traceability.
לא מפרש. לא מנסח כללים. זו עבודת מרדכי.

שימוש:
    python3 scripts/distill.py [--reports-dir <path>] [--out <path>]
                                [--prev <path>] [--threshold N]
                                [--check-only] [--quiet]
"""
import argparse
import json
import sys
import warnings
from datetime import date as date_type, datetime
from pathlib import Path
from typing import TypedDict

import yaml


# ─── Types ────────────────────────────────────────────────────────────────

class Finding(TypedDict, total=False):
    id: int
    severity: str          # blocker|regression|confusion|type-error|outdated|minor
    category: str
    summary: str
    source_brief: str
    source_code: str
    cost_estimate: str


class Report(TypedDict, total=False):
    project: str
    slice: str
    verifier: str          # "avigail" | "calev"
    date: str
    verdict: str
    findings: list          # list[Finding] — type system would say Finding but total=False
    # Extra fields calev uses: mode, dod_items, spot_check, evidence, summary


# ─── Canonical taxonomy ───────────────────────────────────────────────────

CANONICAL_CATEGORIES = {
    "avigail": {
        "missing-symbol", "dropped-branch", "type-error", "wrong-line-number",
        "naming-inconsistency", "wrong-path", "outdated-risk", "missing-dependency",
    },
    "calev": {
        "bubble-grouping", "cross-store-null", "spec-drift", "regression",
        "mobile-desktop", "reload-reconnect", "library-compat",
    },
}

# Files to silently ignore (no warning) when iterating report dirs
_SKIP_FILES = {"README.md", ".gitkeep"}


# ─── Parser ───────────────────────────────────────────────────────────────

def parse_report_file(path: Path) -> "Report | None":
    """פרסר קובץ-דוח יחיד. תומך בשני פורמטים:
      - `.json` (פורמט ישן): json.loads ישיר.
      - `.md`  (פורמט חדש):  חילוץ YAML front-matter בין שני '---', yaml.safe_load.
    נרמול: אם front-matter['date'] נטען כ-datetime (YAML ISO 8601) → המר ל-.isoformat()
    (string) לעקביות עם הפורמט הישן.
    סלחני: כל כשל (JSON פגום / אין front-matter / YAML שבור) → return None (לא קריסה).
    קובץ בלי סיומת .json/.md → None."""
    if path.name in _SKIP_FILES:
        return None

    suffix = path.suffix.lower()

    if suffix == ".json":
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
            if not isinstance(data, dict):
                print(f"[distill warn] {path}: JSON root is not a dict", file=sys.stderr)
                return None
            data.setdefault("findings", [])
            return data  # type: ignore[return-value]
        except (json.JSONDecodeError, OSError) as e:
            print(f"[distill warn] {path}: {e}", file=sys.stderr)
            return None

    elif suffix == ".md":
        try:
            text = path.read_text(encoding="utf-8")
            # Extract front-matter between the first pair of '---' lines
            if not text.startswith("---"):
                print(f"[distill warn] {path}: no YAML front-matter", file=sys.stderr)
                return None
            parts = text.split("---", 2)
            if len(parts) < 3:
                print(f"[distill warn] {path}: malformed front-matter (missing closing ---)", file=sys.stderr)
                return None
            front_matter_text = parts[1].strip()
            if not front_matter_text:
                print(f"[distill warn] {path}: empty front-matter", file=sys.stderr)
                return None
            data = yaml.safe_load(front_matter_text)
            if not isinstance(data, dict):
                print(f"[distill warn] {path}: front-matter is not a dict", file=sys.stderr)
                return None
            # Normalize date: datetime or date → string
            # YAML parses ISO 8601 "2026-05-01" as datetime.date
            # and "2026-05-01T14:30:00" as datetime.datetime
            # Both must be converted to string for consistency
            d = data.get("date")
            if isinstance(d, datetime):
                data["date"] = d.isoformat()
            elif isinstance(d, date_type):
                data["date"] = d.isoformat()
            data.setdefault("findings", [])
            return data  # type: ignore[return-value]
        except (yaml.YAMLError, OSError) as e:
            print(f"[distill warn] {path}: {e}", file=sys.stderr)
            return None

    else:
        # Unknown extension — silently skip
        return None


def load_reports(reports_dir: Path) -> "list[Report]":
    """קורא את כל reports/<project>/*.{json,md} דרך parse_report_file.
    סלחני: parse_report_file שמחזיר None → דלג + warn ל-stderr, לא קריסה.
    מתעלם מ-README.md/.gitkeep (אין להם front-matter → None ממילא, אבל סנן מפורשות
    כדי לא להציף warnings). מחזיר רשימה שטוחה של Report תקינים."""
    result: list = []
    if not reports_dir.is_dir():
        return result
    for project_dir in sorted(reports_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        for fpath in sorted(project_dir.iterdir()):
            if fpath.name in _SKIP_FILES:
                continue
            r = parse_report_file(fpath)
            if r is not None:
                result.append(r)
    return result


# ─── Counting / measurement functions (all pure) ─────────────────────────

def count_by_severity_category(reports: "list[Report]", verifier: str) -> dict:
    """מסנן ל-verifier נתון, סופר findings.
    מחזיר: {"by_severity": {sev: n}, "by_category": {cat: n}, "total_findings": n,
            "total_reports": n}"""
    filtered = [r for r in reports if r.get("verifier") == verifier]
    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    total_findings = 0

    for r in filtered:
        for f in r.get("findings", []):
            sev = f.get("severity", "unknown")
            cat = f.get("category", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
            total_findings += 1

    return {
        "by_severity": by_severity,
        "by_category": by_category,
        "total_findings": total_findings,
        "total_reports": len(filtered),
    }


def compute_hitrate(reports: "list[Report]", verifier: str) -> dict:
    """מחזיר: {"reports": n, "reports_with_findings": k, "avg_findings": float,
            "verdicts": {verdict: n}}. avg_findings מעוגל ל-2."""
    filtered = [r for r in reports if r.get("verifier") == verifier]
    n = len(filtered)
    with_findings = sum(1 for r in filtered if r.get("findings"))
    total_f = sum(len(r.get("findings", [])) for r in filtered)
    avg = round(total_f / n, 2) if n > 0 else 0.0

    verdicts: dict[str, int] = {}
    for r in filtered:
        v = r.get("verdict", "unknown")
        verdicts[v] = verdicts.get(v, 0) + 1

    return {
        "reports": n,
        "reports_with_findings": with_findings,
        "avg_findings": avg,
        "verdicts": verdicts,
    }


def traceability_index(reports: "list[Report]", verifier: str) -> "dict[str, list[str]]":
    """category → רשימת מזהי-דוח שתרמו אליה. מזהה-דוח = "<project>/<slice>".
    ממוין. כך קטלוג יכול להצביע חזרה למקור."""
    filtered = [r for r in reports if r.get("verifier") == verifier]
    index: dict[str, list[str]] = {}

    for r in filtered:
        report_id = f"{r.get('project', 'unknown')}/{r.get('slice', 'unknown')}"
        for f in r.get("findings", []):
            cat = f.get("category", "unknown")
            if cat not in index:
                index[cat] = []
            if report_id not in index[cat]:
                index[cat].append(report_id)

    # Sort each list
    for cat in index:
        index[cat] = sorted(index[cat])

    return index


def flag_noncanonical(reports: "list[Report]", verifier: str) -> "dict[str, list[str]]":
    """מחזיר categories שמופיעים בדוחות אבל לא ב-CANONICAL_CATEGORIES[verifier]
    (כולל "unique"). → {category: [report-ids]}. אלה מועמדים לזיקוק-טקסונומיה.
    'unique' תמיד מועמד (לא קנוני בכוונה)."""
    canonical = CANONICAL_CATEGORIES.get(verifier, set())
    filtered = [r for r in reports if r.get("verifier") == verifier]
    noncanonical: dict[str, list[str]] = {}

    for r in filtered:
        report_id = f"{r.get('project', 'unknown')}/{r.get('slice', 'unknown')}"
        for f in r.get("findings", []):
            cat = f.get("category", "unknown")
            if cat not in canonical:
                if cat not in noncanonical:
                    noncanonical[cat] = []
                if report_id not in noncanonical[cat]:
                    noncanonical[cat].append(report_id)

    for cat in noncanonical:
        noncanonical[cat] = sorted(noncanonical[cat])

    return noncanonical


def compute_delta(current: dict, previous_data: "dict | None") -> dict:
    """משווה התפלגות נוכחית מול ה-data.json הקודם.
    previous_data=None (אין קודם) → כל הקטגוריות "new".
    מחזיר: {"by_category": {cat: {"now": n, "prev": m, "trend": "up|down|same|new|gone"}}}.
    trend לפי now מול prev: now>prev=up, <prev=down, ==same, prev חסר=new, now=0&prev>0=gone."""

    # Determine verifier from current (if it contains a by_category key directly)
    # current is {"by_category": {...}} (output of count_by_severity_category)
    current_cats: dict[str, int] = current.get("by_category", {})

    # prev_data could be a full build_data dict; we need to find by_category
    # We'll look in "avigail" and "calev" sections based on what makes sense,
    # but since compute_delta is called per-verifier with a counts dict,
    # we accept prev as full build_data and let caller pass the right section.
    # For flexibility: if previous_data is full build_data, caller must pass
    # the relevant sub-dict or we handle it here.
    # Per brief: "previous_data = full data.json or None"
    # We try to find the right section by looking for "avigail" or "calev" keys.
    prev_cats: dict[str, int] = {}
    if previous_data is not None:
        # Try to find by_category: either it's at top level or under a verifier key
        if "by_category" in previous_data:
            prev_cats = previous_data["by_category"]
        else:
            # Search in avigail/calev sub-dicts
            for key in ("avigail", "calev"):
                if key in previous_data:
                    subsection = previous_data[key]
                    if isinstance(subsection, dict) and "counts" in subsection:
                        prev_cats = subsection["counts"].get("by_category", {})
                        break

    result: dict[str, dict] = {}

    # All categories that appear in current
    all_cats = set(current_cats.keys())
    # Also include categories that were in prev but are now 0 (gone)
    all_cats |= set(prev_cats.keys())

    for cat in all_cats:
        now = current_cats.get(cat, 0)
        prev = prev_cats.get(cat)  # None if not in prev

        if prev is None:
            trend = "new"
            prev_val = 0
        elif now > prev:
            trend = "up"
            prev_val = prev
        elif now < prev:
            if now == 0:
                trend = "gone"
            else:
                trend = "down"
            prev_val = prev
        else:
            trend = "same"
            prev_val = prev

        result[cat] = {"now": now, "prev": prev_val, "trend": trend}

    return {"by_category": result}


def _collect_report_ids(reports_dir: Path) -> set:
    """Collect all relative report file IDs from a directory (project/filename)."""
    ids = set()
    if not reports_dir.is_dir():
        return ids
    for project_dir in reports_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for fpath in project_dir.iterdir():
            if fpath.name in _SKIP_FILES:
                continue
            if fpath.suffix.lower() in (".json", ".md"):
                ids.add(f"{project_dir.name}/{fpath.name}")
    return ids


def count_new_reports_since(reports_dir: Path, last_data: "Path | None") -> int:
    """כמה דוחות חדשים מאז ה-snapshot האחרון (לפי last_data["report_ids"]).
    last_data=None → כל הדוחות חדשים. משמש את הטריגר הכמותי (§Commit 3)."""
    all_ids = _collect_report_ids(reports_dir)

    if last_data is None:
        return len(all_ids)

    try:
        prev = json.loads(last_data.read_text(encoding="utf-8"))
        known_ids = set(prev.get("report_ids", []))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[distill warn] count_new_reports_since: could not read {last_data}: {e}", file=sys.stderr)
        return len(all_ids)

    new_ids = all_ids - known_ids
    return len(new_ids)


def build_data(reports_dir: Path, prev_data_path: "Path | None") -> dict:
    """מאחד הכל ל-data.json אחד. מבנה:
    {"date": ISO, "report_ids": [...],
     "avigail": {"counts":..., "hitrate":..., "trace":..., "noncanonical":..., "delta":...},
     "calev":   {...same...}}.
    זה הפלט היחיד ל-stdout/קובץ. כל המספרים, אפס פרשנות."""
    reports = load_reports(reports_dir)
    all_ids = sorted(_collect_report_ids(reports_dir))

    prev_data: "dict | None" = None
    if prev_data_path is not None and prev_data_path.exists():
        try:
            prev_data = json.loads(prev_data_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"[distill warn] could not load prev data: {e}", file=sys.stderr)

    result: dict = {
        "date": datetime.now().isoformat(),
        "report_ids": all_ids,
    }

    for verifier in ("avigail", "calev"):
        counts = count_by_severity_category(reports, verifier)
        hitrate = compute_hitrate(reports, verifier)
        trace = traceability_index(reports, verifier)
        noncanonical = flag_noncanonical(reports, verifier)
        delta = compute_delta(counts, prev_data)

        result[verifier] = {
            "counts": counts,
            "hitrate": hitrate,
            "trace": trace,
            "noncanonical": noncanonical,
            "delta": delta,
        }

    return result


# ─── CLI (main) ──────────────────────────────────────────────────────────

def _find_latest_data(distillations_dir: Path) -> "Path | None":
    """Find the most recent *-data.json in distillations/."""
    if not distillations_dir.is_dir():
        return None
    candidates = sorted(distillations_dir.glob("*-data.json"))
    return candidates[-1] if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="distill.py — כמותי בלבד. ספירה, hitrate, דלתא, traceability."
    )
    parser.add_argument(
        "--reports-dir", default="reports/",
        help="נתיב לתיקיית הדוחות (ברירת מחדל: reports/)"
    )
    parser.add_argument(
        "--out", default=None,
        help="נתיב קובץ הפלט (ברירת מחדל: distillations/<date>-data.json)"
    )
    parser.add_argument(
        "--prev", default=None,
        help="נתיב ל-data.json קודם (ברירת מחדל: האחרון ב-distillations/ אם קיים)"
    )
    parser.add_argument(
        "--threshold", type=int, default=10,
        help="סף הטריגר הכמותי (ברירת מחדל: 10)"
    )
    parser.add_argument(
        "--check-only", action="store_true",
        help="בדוק רק אם יש מספיק דוחות חדשים. exit 0=כן, 1=לא"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="פחות פלט ל-stdout"
    )
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    distillations_dir = Path("distillations")

    # Resolve prev data path
    if args.prev:
        prev_data_path: "Path | None" = Path(args.prev)
    else:
        prev_data_path = _find_latest_data(distillations_dir)

    # --check-only mode: return 0 if ≥threshold new reports, 1 otherwise
    if args.check_only:
        n_new = count_new_reports_since(reports_dir, prev_data_path)
        if not args.quiet:
            print(f"distill: {n_new} דוחות חדשים (סף: {args.threshold})")
        return 0 if n_new >= args.threshold else 1

    # Build the data
    data = build_data(reports_dir, prev_data_path)

    # Resolve output path
    if args.out:
        out_path = Path(args.out)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        distillations_dir.mkdir(parents=True, exist_ok=True)
        out_path = distillations_dir / f"{date_str}-data.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.quiet:
        n_avigail = data["avigail"]["hitrate"]["reports"]
        n_calev = data["calev"]["hitrate"]["reports"]
        print(f"distill: {n_avigail} דוחות אביגיל, {n_calev} דוחות כלב → {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
