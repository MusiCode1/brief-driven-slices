"""
tests/test_distill.py — unittest (stdlib) for distill.py
TDD: these tests are written BEFORE the implementation.
Run with: python3 tests/test_distill.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent dir to path so we can import distill
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import distill


FIXTURES = Path(__file__).parent / "fixtures" / "sample-reports"


# ─── Tests: parse_report_file ──────────────────────────────────────────────

class TestParseReportFile(unittest.TestCase):

    def test_md_with_front_matter(self):
        """Valid .md with YAML front-matter loads correctly."""
        p = FIXTURES / "projA" / "slice-1-avigail.md"
        r = distill.parse_report_file(p)
        self.assertIsNotNone(r)
        self.assertEqual(r["project"], "projA")
        self.assertEqual(r["slice"], "slice-1")
        self.assertEqual(r["verifier"], "avigail")
        self.assertEqual(r["verdict"], "USABLE-AFTER-FIX")
        self.assertIsInstance(r["findings"], list)
        self.assertEqual(len(r["findings"]), 3)

    def test_md_empty_findings(self):
        """Valid .md with findings=[] loads with empty findings list."""
        p = FIXTURES / "projA" / "slice-2-avigail.md"
        r = distill.parse_report_file(p)
        self.assertIsNotNone(r)
        self.assertEqual(r["verdict"], "READY")
        self.assertEqual(r.get("findings", []), [])

    def test_md_date_iso8601_normalized_to_string(self):
        """Date as ISO 8601 datetime is normalized to string .isoformat()."""
        p = FIXTURES / "projA" / "slice-2-avigail.md"
        r = distill.parse_report_file(p)
        self.assertIsNotNone(r)
        # Should be a string, not datetime object
        self.assertIsInstance(r.get("date"), str)

    def test_md_date_as_date_object_normalized(self):
        """Date as date-only ISO 8601 (YYYY-MM-DD) is normalized to string."""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            # date-only ISO 8601 is parsed by YAML as datetime.date, not datetime
            f.write("---\nproject: x\nslice: s\nverifier: avigail\ndate: 2026-05-01\nverdict: READY\nfindings: []\n---\n# body\n")
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNotNone(r)
        # Must be string, not datetime.date object
        self.assertIsInstance(r.get("date"), str)
        self.assertEqual(r.get("date"), "2026-05-01")
        fpath.unlink()

    def test_md_summary_with_colon(self):
        """Summary field containing colons is parsed correctly."""
        p = FIXTURES / "projA" / "slice-2-avigail.md"
        r = distill.parse_report_file(p)
        self.assertIsNotNone(r)
        # summary with "passes string|boolean: fails" should not break YAML
        self.assertIn("passes", r.get("summary", ""))

    def test_md_triple_dash_inside_front_matter_string(self):
        """A '---' *inside* a front-matter string must not truncate the block.

        רגרסיה: split("---", 2) גולמי חתך את ה-front-matter באמצע מחרוזת
        (`ב---distinct`) והדוח כולו נשמט מהזיקוק בשקט — כולל blocker.
        המפריד חייב להיות מעוגן לתחילת שורה.
        """
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write(
                "---\n"
                'project: "p"\n'
                'verifier: "calev"\n'
                'verdict: "PARTIAL"\n'
                "findings:\n"
                "  - id: 1\n"
                '    severity: "blocker"\n'
                '    summary: "key fails on ב---distinct with a --- inside"\n'
                "---\n\n"
                "# body\n"
            )
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNotNone(r)
        self.assertEqual(r["verdict"], "PARTIAL")
        self.assertEqual(len(r["findings"]), 1)
        self.assertEqual(r["findings"][0]["severity"], "blocker")
        fpath.unlink()

    def test_json_old_format_loads(self):
        """.json old format still loads (backward-compat)."""
        p = FIXTURES / "projA" / "slice-3-calev.json"
        r = distill.parse_report_file(p)
        self.assertIsNotNone(r)
        self.assertEqual(r["project"], "projA")
        self.assertEqual(r["verifier"], "calev")
        self.assertEqual(r["verdict"], "PARTIAL")
        self.assertEqual(len(r["findings"]), 1)

    def test_md_without_front_matter_returns_none(self):
        """A .md without front-matter returns None (not a crash)."""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# just a plain markdown file\n\nNo front-matter here.\n")
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNone(r)
        fpath.unlink()

    def test_md_empty_front_matter_returns_none(self):
        """A .md with empty front-matter block returns None."""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("---\n---\n\n# No data\n")
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNone(r)
        fpath.unlink()

    def test_broken_yaml_returns_none(self):
        """A .md with broken YAML returns None, no crash."""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("---\nproject: projX\nbroken: [\n---\n# body\n")
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNone(r)
        fpath.unlink()

    def test_broken_json_returns_none(self):
        """A .json with broken JSON returns None, no crash."""
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write('{"project": "x", broken}')
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNone(r)
        fpath.unlink()

    def test_unknown_extension_returns_none(self):
        """A file with unknown extension returns None."""
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("some text\n")
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNone(r)
        fpath.unlink()

    def test_report_without_findings_field(self):
        """Report without findings field loads with findings=[]."""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("---\nproject: x\nslice: s\nverifier: avigail\ndate: 2026-01-01\nverdict: READY\n---\n# body\n")
            fpath = Path(f.name)
        r = distill.parse_report_file(fpath)
        self.assertIsNotNone(r)
        self.assertEqual(r.get("findings", []), [])
        fpath.unlink()

    def test_calev_extra_fields_load_ok(self):
        """calev report with mode/dod_items/spot_check loads without error."""
        p = FIXTURES / "projB" / "slice-1-calev.md"
        r = distill.parse_report_file(p)
        self.assertIsNotNone(r)
        self.assertEqual(r["verifier"], "calev")
        # extra fields preserved
        self.assertEqual(r.get("mode"), "light")


# ─── Tests: load_reports ──────────────────────────────────────────────────

class TestLoadReports(unittest.TestCase):

    def test_loads_all_valid_reports(self):
        """load_reports loads both .md and .json formats from fixtures."""
        reports = distill.load_reports(FIXTURES)
        # We have 5 reports (3 projA .md + 1 projA .json + 1 projB .md + 1 projB .md)
        self.assertGreaterEqual(len(reports), 4)

    def test_both_formats_present(self):
        """Both .md and .json format reports appear in load_reports output."""
        reports = distill.load_reports(FIXTURES)
        verifiers_and_formats = [(r.get("project"), r.get("slice")) for r in reports]
        # projA/slice-3 is JSON format
        self.assertIn(("projA", "slice-3"), verifiers_and_formats)
        # projA/slice-1 is MD format
        self.assertIn(("projA", "slice-1"), verifiers_and_formats)

    def test_skips_readme_gitkeep(self):
        """README.md and .gitkeep files are skipped without warning."""
        # Create a fake README in a temp dir alongside a valid report
        with tempfile.TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            subdir = td / "projX"
            subdir.mkdir()
            # Write README
            (subdir / "README.md").write_text("# readme\n")
            # Write .gitkeep
            (subdir / ".gitkeep").write_text("")
            # Write one valid report
            (subdir / "s1-avigail.md").write_text(
                "---\nproject: projX\nslice: s1\nverifier: avigail\n"
                "date: 2026-01-01\nverdict: READY\nfindings: []\n---\n# body\n"
            )
            reports = distill.load_reports(td)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["project"], "projX")


# ─── Tests: count_by_severity_category ───────────────────────────────────

class TestCountBySeverityCategory(unittest.TestCase):

    def _make_reports(self):
        """Helper — return synthetic list of Report dicts."""
        return [
            {
                "project": "projA", "slice": "s1", "verifier": "avigail", "date": "2026-01-01",
                "verdict": "USABLE-AFTER-FIX",
                "findings": [
                    {"id": 1, "severity": "blocker", "category": "missing-symbol", "summary": "x"},
                    {"id": 2, "severity": "blocker", "category": "missing-symbol", "summary": "y"},
                ],
            },
            {
                "project": "projA", "slice": "s2", "verifier": "avigail", "date": "2026-01-02",
                "verdict": "READY",
                "findings": [],
            },
            {
                "project": "projB", "slice": "s1", "verifier": "calev", "date": "2026-01-03",
                "verdict": "GO",
                "findings": [
                    {"id": 1, "severity": "minor", "category": "bubble-grouping", "summary": "z"},
                ],
            },
        ]

    def test_filter_by_verifier(self):
        """count_by_severity_category filters to given verifier."""
        reports = self._make_reports()
        result = distill.count_by_severity_category(reports, "avigail")
        self.assertEqual(result["by_severity"]["blocker"], 2)
        self.assertEqual(result["total_findings"], 2)
        self.assertEqual(result["total_reports"], 2)

    def test_empty_findings_counted_in_reports_not_findings(self):
        """Report with no findings is counted in total_reports but not findings."""
        reports = self._make_reports()
        result = distill.count_by_severity_category(reports, "avigail")
        self.assertEqual(result["total_reports"], 2)
        self.assertEqual(result["total_findings"], 2)

    def test_same_category_two_reports(self):
        """Same category in multiple reports is summed correctly."""
        reports = [
            {"project": "p1", "slice": "s1", "verifier": "avigail", "date": "2026-01-01",
             "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "blocker", "category": "wrong-path", "summary": "a"}]},
            {"project": "p2", "slice": "s2", "verifier": "avigail", "date": "2026-01-02",
             "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "wrong-path", "summary": "b"}]},
        ]
        result = distill.count_by_severity_category(reports, "avigail")
        self.assertEqual(result["by_category"]["wrong-path"], 2)

    def test_calev_findings(self):
        """calev findings counted separately."""
        reports = self._make_reports()
        result = distill.count_by_severity_category(reports, "calev")
        self.assertEqual(result["by_severity"]["minor"], 1)
        self.assertEqual(result["total_reports"], 1)


# ─── Tests: compute_hitrate ───────────────────────────────────────────────

class TestComputeHitrate(unittest.TestCase):

    def test_hitrate_basic(self):
        """3 avigail reports, 2 with findings → reports=3, reports_with_findings=2."""
        reports = [
            {"project": "p", "slice": "s1", "verifier": "avigail",
             "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "blocker", "category": "missing-symbol", "summary": "x"}]},
            {"project": "p", "slice": "s2", "verifier": "avigail",
             "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "wrong-path", "summary": "y"}]},
            {"project": "p", "slice": "s3", "verifier": "avigail",
             "verdict": "READY",
             "findings": []},
        ]
        result = distill.compute_hitrate(reports, "avigail")
        self.assertEqual(result["reports"], 3)
        self.assertEqual(result["reports_with_findings"], 2)
        # avg: (1+1+0)/3 rounded to 2
        self.assertAlmostEqual(result["avg_findings"], 0.67)

    def test_verdict_counts(self):
        """Verdicts are counted correctly."""
        reports = [
            {"project": "p", "slice": "s1", "verifier": "avigail", "verdict": "READY", "findings": []},
            {"project": "p", "slice": "s2", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "wrong-path", "summary": "x"}]},
            {"project": "p", "slice": "s3", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "blocker", "category": "missing-symbol", "summary": "y"}]},
        ]
        result = distill.compute_hitrate(reports, "avigail")
        self.assertEqual(result["verdicts"]["READY"], 1)
        self.assertEqual(result["verdicts"]["USABLE-AFTER-FIX"], 2)


# ─── Tests: traceability_index ────────────────────────────────────────────

class TestTraceabilityIndex(unittest.TestCase):

    def test_same_category_two_projects(self):
        """Two reports with same category from different projects."""
        reports = [
            {"project": "projA", "slice": "s1", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "blocker", "category": "missing-symbol", "summary": "x"}]},
            {"project": "projB", "slice": "s2", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "missing-symbol", "summary": "y"}]},
        ]
        result = distill.traceability_index(reports, "avigail")
        self.assertIn("missing-symbol", result)
        self.assertIn("projA/s1", result["missing-symbol"])
        self.assertIn("projB/s2", result["missing-symbol"])
        # Must be sorted
        self.assertEqual(result["missing-symbol"], sorted(result["missing-symbol"]))


# ─── Tests: flag_noncanonical ─────────────────────────────────────────────

class TestFlagNoncanonical(unittest.TestCase):

    def test_noncanonical_category_flagged(self):
        """Category not in canonical set for avigail is flagged."""
        reports = [
            {"project": "p", "slice": "s1", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "weird-new-thing", "summary": "x"}]},
        ]
        result = distill.flag_noncanonical(reports, "avigail")
        self.assertIn("weird-new-thing", result)
        self.assertIn("p/s1", result["weird-new-thing"])

    def test_unique_always_flagged(self):
        """'unique' category is always flagged (non-canonical by design)."""
        reports = [
            {"project": "p", "slice": "s1", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "unique", "summary": "x"}]},
        ]
        result = distill.flag_noncanonical(reports, "avigail")
        self.assertIn("unique", result)

    def test_canonical_avigail_not_flagged(self):
        """Canonical avigail category is NOT flagged."""
        reports = [
            {"project": "p", "slice": "s1", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "blocker", "category": "missing-symbol", "summary": "x"}]},
        ]
        result = distill.flag_noncanonical(reports, "avigail")
        self.assertNotIn("missing-symbol", result)

    def test_calev_canonical_in_avigail_report_is_flagged(self):
        """Calev-canonical category in an avigail report IS flagged (wrong verifier)."""
        reports = [
            {"project": "p", "slice": "s1", "verifier": "avigail", "verdict": "USABLE-AFTER-FIX",
             "findings": [{"id": 1, "severity": "minor", "category": "bubble-grouping", "summary": "x"}]},
        ]
        result = distill.flag_noncanonical(reports, "avigail")
        self.assertIn("bubble-grouping", result)


# ─── Tests: compute_delta ─────────────────────────────────────────────────

class TestComputeDelta(unittest.TestCase):

    def test_prev_none_all_new(self):
        """When prev=None, all categories get trend='new'."""
        current = {"by_category": {"missing-symbol": 5, "wrong-path": 2}}
        result = distill.compute_delta(current, None)
        for cat in ["missing-symbol", "wrong-path"]:
            self.assertEqual(result["by_category"][cat]["trend"], "new")

    def test_down_trend(self):
        """Category decreasing gets trend='down'."""
        current = {"by_category": {"missing-symbol": 3}}
        prev = {"avigail": {"counts": {"by_category": {"missing-symbol": 5}}}}
        result = distill.compute_delta(current, prev)
        self.assertEqual(result["by_category"]["missing-symbol"]["trend"], "down")
        self.assertEqual(result["by_category"]["missing-symbol"]["now"], 3)
        self.assertEqual(result["by_category"]["missing-symbol"]["prev"], 5)

    def test_up_trend(self):
        """Category increasing gets trend='up'."""
        current = {"by_category": {"missing-symbol": 7}}
        prev = {"avigail": {"counts": {"by_category": {"missing-symbol": 5}}}}
        result = distill.compute_delta(current, prev)
        self.assertEqual(result["by_category"]["missing-symbol"]["trend"], "up")

    def test_same_trend(self):
        """Category unchanged gets trend='same'."""
        current = {"by_category": {"missing-symbol": 5}}
        prev = {"avigail": {"counts": {"by_category": {"missing-symbol": 5}}}}
        result = distill.compute_delta(current, prev)
        self.assertEqual(result["by_category"]["missing-symbol"]["trend"], "same")

    def test_new_category_not_in_prev(self):
        """Category in current but not in prev gets trend='new'."""
        current = {"by_category": {"new-cat": 3}}
        prev = {"avigail": {"counts": {"by_category": {"missing-symbol": 5}}}}
        result = distill.compute_delta(current, prev)
        self.assertEqual(result["by_category"]["new-cat"]["trend"], "new")

    def test_gone_category(self):
        """Category in prev but now=0 gets trend='gone'."""
        current = {"by_category": {"missing-symbol": 0}}
        prev = {"avigail": {"counts": {"by_category": {"missing-symbol": 2}}}}
        result = distill.compute_delta(current, prev)
        self.assertEqual(result["by_category"]["missing-symbol"]["trend"], "gone")


# ─── Tests: count_new_reports_since ───────────────────────────────────────

class TestCountNewReportsSince(unittest.TestCase):

    def test_no_prev_all_new(self):
        """With last_data=None, all reports are 'new'."""
        n = distill.count_new_reports_since(FIXTURES, None)
        # We have at least 5 report files in fixtures (not counting README)
        self.assertGreaterEqual(n, 4)

    def test_prev_with_known_ids(self):
        """With last_data containing 3 report_ids, returns count of unknowns."""
        # Build a fake prev data with some IDs already seen
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump({
                "report_ids": ["projA/slice-1-avigail.md", "projA/slice-2-avigail.md",
                               "projA/slice-3-calev.json"]
            }, f)
            prev_path = Path(f.name)

        n = distill.count_new_reports_since(FIXTURES, prev_path)
        # Should be total_reports - 3 known
        total = distill.count_new_reports_since(FIXTURES, None)
        self.assertEqual(n, total - 3)
        prev_path.unlink()


# ─── Tests: build_data ────────────────────────────────────────────────────

class TestBuildData(unittest.TestCase):

    def test_structure(self):
        """build_data returns correct top-level keys."""
        result = distill.build_data(FIXTURES, None)
        self.assertIn("date", result)
        self.assertIn("report_ids", result)
        self.assertIn("avigail", result)
        self.assertIn("calev", result)

    def test_avigail_counts_nonzero(self):
        """build_data has nonzero avigail report count."""
        result = distill.build_data(FIXTURES, None)
        self.assertGreater(result["avigail"]["hitrate"]["reports"], 0)

    def test_no_interpretation(self):
        """build_data contains only numbers, no narrative strings in counts."""
        result = distill.build_data(FIXTURES, None)
        counts = result["avigail"]["counts"]
        # by_severity values should be ints
        for v in counts["by_severity"].values():
            self.assertIsInstance(v, int)


if __name__ == "__main__":
    unittest.main()
