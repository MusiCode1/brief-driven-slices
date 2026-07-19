"""
tests/test_path_substitution.py — unittest (stdlib) for scripts/install-cli-configs.sh
TDD: these tests are written BEFORE the substitution mechanism (Commit 1).
Run with: python3 tests/test_path_substitution.py
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
INSTALL_SCRIPT = ROOT / "scripts" / "install-cli-configs.sh"

FAKE_ENV = {
    "BDS_REPORTS": "/tmp/fk-r",
    "BDS_SCRIPTS": "/tmp/fk-s",
    "BDS_LESSONS": "/tmp/fk-l",
    "BDS_ORCH": "/tmp/fk-o",
}


def run_bash(snippet, env_overrides=None, unset=None):
    """מקור (source) install-cli-configs.sh — מוגן ע"י BASH_SOURCE!=$0 guard
    כך שה-main (generate_configs + case) לא רץ — ואז מריץ snippet שקורא
    לפונקציות עצמן (resolve_paths / substitute_into / install_*)."""
    env = os.environ.copy()
    env.update(FAKE_ENV)
    if env_overrides:
        env.update(env_overrides)
    if unset:
        for k in unset:
            env.pop(k, None)
    script = f'source "{INSTALL_SCRIPT}"\n{snippet}'
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        env=env,
    )


class TestSubstituteInto(unittest.TestCase):
    """(א) החלפה תקינה של 4 ה-placeholders."""

    def test_replaces_all_four_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.md"
            dst = Path(tmp) / "dst.md"
            src.write_text(
                "{{BDS_REPORTS}} {{BDS_SCRIPTS}} {{BDS_LESSONS}} {{BDS_ORCH}}\n"
            )
            result = run_bash(f'substitute_into "{src}" "{dst}"')
            self.assertEqual(result.returncode, 0, result.stderr)
            content = dst.read_text()
            self.assertIn("/tmp/fk-r", content)
            self.assertIn("/tmp/fk-s", content)
            self.assertIn("/tmp/fk-l", content)
            self.assertIn("/tmp/fk-o", content)
            self.assertNotIn("{{BDS_", content)

    def test_replacement_value_containing_ampersand(self):
        """calev finding (Commit 1 phase-review): & בערך BDS_* הוא sed backreference
        מיוחד ("כל ההתאמה") — בלי escaping הוא מחדיר בחזרה {{BDS_...}} ומפיל את
        שכבת-ההגנה בטעות. חייב לצאת עם הנתיב האמיתי, לא exit 1."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.md"
            dst = Path(tmp) / "dst.md"
            src.write_text("{{BDS_REPORTS}}\n")
            result = run_bash(
                f'substitute_into "{src}" "{dst}"',
                env_overrides={"BDS_REPORTS": "/tmp/r&d"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("/tmp/r&d", dst.read_text())

    def test_replacement_value_containing_pipe(self):
        """calev finding: | הוא ה-delimiter של sed בסקריפט — ערך שמכיל | חייב
        לעבוד (escape), לא לקרוס בשגיאת syntax גולמית של sed."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.md"
            dst = Path(tmp) / "dst.md"
            src.write_text("{{BDS_REPORTS}}\n")
            result = run_bash(
                f'substitute_into "{src}" "{dst}"',
                env_overrides={"BDS_REPORTS": "/tmp/r|d"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("/tmp/r|d", dst.read_text())

    def test_unrecognized_placeholder_fails_noisily(self):
        """(ג) placeholder לא-מוכר (לא אחד מ-4) נשאר אחרי ההחלפה → כשל-רועש."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.md"
            dst = Path(tmp) / "dst.md"
            src.write_text("{{BDS_UNKNOWN}}\n")
            result = run_bash(f'substitute_into "{src}" "{dst}"')
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stderr.strip(), "expected a noisy error on stderr")


class TestResolvePaths(unittest.TestCase):
    """(ב) משתנה חסר → כשל-רועש (exit≠0)."""

    def test_all_vars_set_succeeds(self):
        result = run_bash("resolve_paths")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_var_fails_noisily(self):
        result = run_bash("resolve_paths", unset=["BDS_REPORTS"])
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip(), "expected an error message on stderr")

    def test_missing_each_var_fails_noisily(self):
        for var in ("BDS_REPORTS", "BDS_SCRIPTS", "BDS_LESSONS", "BDS_ORCH"):
            with self.subTest(var=var):
                result = run_bash("resolve_paths", unset=[var])
                self.assertNotEqual(result.returncode, 0)


class TestInstallersUseSubstituteInto(unittest.TestCase):
    """finding אביגיל #1: שני ה-installers (לא רק opencode) חייבים
    לעבור דרך substitute_into — codex לא יתקין placeholder מילולי."""

    def test_install_opencode_substitutes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_bash(
                "install_opencode",
                env_overrides={"OPENCODE_AGENTS_DIR": tmp},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            found = list(Path(tmp).glob("*.md"))
            self.assertTrue(found, "no files installed")
            combined = "\n".join(f.read_text() for f in found)
            self.assertNotIn("{{BDS_", combined)
            self.assertIn("/tmp/fk-r", combined)

    def test_install_codex_substitutes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_bash(
                "install_codex",
                env_overrides={"CODEX_AGENTS_DIR": tmp},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            found = list(Path(tmp).glob("*.toml"))
            self.assertTrue(found, "no files installed")
            combined = "\n".join(f.read_text() for f in found)
            self.assertNotIn("{{BDS_", combined)
            self.assertIn("/tmp/fk-r", combined)


if __name__ == "__main__":
    unittest.main()
