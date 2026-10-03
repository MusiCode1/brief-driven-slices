import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "completion-ledger"
REAL_RECEIPT = Path("/home/user/projects/aac-migration-20261002/orchestrator-h2-20261003/reader-verifier-run/result.json")


class CompletionLedgerProbeTests(unittest.TestCase):
    def run_receipt(self, path, **overrides):
        args = {
            "task": "H2",
            "verdict": "FUNCTIONAL_GO",
            "scope": "Local exact-SHA H2 functional full-caption reader acceptance under canonical b364436; root retains delivery/live gates",
            "sha": "ec65b8fe65a6d9d2878d4c4d4803c53dcfcdebaa",
        }
        args.update(overrides)
        command = ["python3", str(ROOT / "receipt-probe.py"), str(path)]
        for key, value in args.items():
            command.extend([f"--{key}", value])
        return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()

    def test_receipt_valid_missing_and_wrong_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = Path(temp) / "receipt.json"
            receipt.write_text(json.dumps({
                "verdict": "FUNCTIONAL_GO",
                "scope": "Local exact-SHA H2 functional full-caption reader acceptance under canonical b364436; root retains delivery/live gates",
                "sourceSHA": "ec65b8fe65a6d9d2878d4c4d4803c53dcfcdebaa",
            }))
            self.assertEqual(self.run_receipt(receipt), "1")
            self.assertEqual(self.run_receipt(receipt.with_name("missing.json")), "0")
            self.assertEqual(self.run_receipt(receipt, task="H3"), "0")
            self.assertEqual(self.run_receipt(receipt, sha="a" * 40), "0")
            self.assertEqual(self.run_receipt(receipt, scope="all H2 work"), "0")
            self.assertEqual(self.run_receipt(receipt, verdict="REVISE"), "0")
            failed = json.loads(receipt.read_text())
            failed["verdict"] = "NO_GO"
            receipt.write_text(json.dumps(failed))
            self.assertEqual(self.run_receipt(receipt, verdict="NO_GO"), "0")
            bad = Path(temp) / "receipt.json"
            bad.write_text(json.dumps({"verdict": "FUNCTIONAL_GO", "scope": "H2 only"}))
            self.assertEqual(self.run_receipt(bad), "0")

    @unittest.skipUnless(REAL_RECEIPT.exists(), "private read-only AAC receipt unavailable")
    def test_existing_private_receipt(self):
        self.assertEqual(self.run_receipt(REAL_RECEIPT), "1")

    def test_negative_verdicts_and_embedded_task_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = Path(temp) / "receipt.json"
            base = {
                "verdict": "FUNCTIONAL_GO", "scope": "Accepted H2 only",
                "sourceSHA": "ec65b8fe65a6d9d2878d4c4d4803c53dcfcdebaa",
            }
            for verdict in ("NOT_GO", "NO_GO", "FUNCTIONAL_GO_PENDING", "GO_REVISE"):
                with self.subTest(verdict=verdict):
                    receipt.write_text(json.dumps({**base, "verdict": verdict}))
                    self.assertEqual(self.run_receipt(receipt, verdict=verdict, scope=base["scope"]), "0")
            for scope in ("Accepted H2-old only", "Accepted pre-H2 only", "Accepted H2.1 only", "Accepted H2_more only"):
                with self.subTest(scope=scope):
                    receipt.write_text(json.dumps({**base, "scope": scope}))
                    self.assertEqual(self.run_receipt(receipt, scope=scope), "0")
            receipt.write_text(json.dumps(base))
            self.assertEqual(self.run_receipt(receipt, scope=base["scope"]), "1")

    def test_dotted_and_legacy_ids_and_checkbox(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "ledger.md"
            ledger.write_text("""- [x] **A4.1** · dotted
  ⟂ `echo 1` → `=1`
- [ ] **B3** · legacy open
  ⟂ `echo 1` → `=1`
- [x] **A7.5n** · dotted suffix
  ⟂ `echo 1` → `=1`
- [x] **C2** · marked without proof
  ⟂ `echo 0` → `=1`
""")
            result = subprocess.run(["bash", str(ROOT / "ledger-status.sh"), str(ledger)], capture_output=True, text=True, check=True)
            self.assertIn("✅ A4.1", result.stdout)
            self.assertIn("⬜ B3", result.stdout)
            self.assertIn("✅ A7.5n", result.stdout)
            self.assertIn("⬜ C2", result.stdout)
            self.assertIn("פתוחים: 2 · ‏סגורים: 2", result.stdout)

    def test_unconverted_ledger_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "ledger.md"
            ledger.write_text("- [ ] **A4.1** · unconverted\n")
            result = subprocess.run(["bash", str(ROOT / "ledger-status.sh"), str(ledger)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            self.assertIn("פנקס לא-מוסב", result.stderr)
            self.assertNotIn("פתוחים: 0", result.stdout)

    def test_indented_child_and_conflicting_second_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "ledger.md"
            ledger.write_text("""- [x] **A1** · parent
  ⟂ `echo 1` → `=1`
  ⟂ `echo 0` → `=1`
  - [ ] A2n · measuring child
    ⟂ `echo 0` → `=1`
""")
            result = subprocess.run(["bash", str(ROOT / "ledger-status.sh"), str(ledger)], capture_output=True, text=True, check=True)
            self.assertIn("⬜ A1", result.stdout)
            self.assertIn("יותר משורת ⟂ אחת", result.stdout)
            self.assertIn("⬜ A2n", result.stdout)
            self.assertIn("פתוחים: 2 · ‏סגורים: 0", result.stdout)

    def test_unrecognized_child_is_rejected_even_with_valid_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "ledger.md"
            ledger.write_text("""- [x] **A1** · closed
  ⟂ `echo 1` → `=1`
  - [ ] A2n: malformed child
""")
            result = subprocess.run(["bash", str(ROOT / "ledger-status.sh"), str(ledger)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            self.assertNotIn("פתוחים: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
