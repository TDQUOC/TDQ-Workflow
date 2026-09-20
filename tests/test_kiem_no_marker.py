"""Tests for scripts/kiem_no_marker.py — the debt-marker ledger check (spec item 8).

Every case is built in a throwaway directory from tempfile.mkdtemp(): the check has to
work on any tree, and a fixture committed to this repo would itself become a debt marker
the real run trips over.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "scripts", "kiem_no_marker.py")

# Built at runtime so no line of this file is itself a marker the tool would report.
PREFIX = "ponytail" + ":"
GOOD = f"# {PREFIX} global lock, per-account locks if throughput matters"
BAD = f"# {PREFIX} global lock"


class MarkerLedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="kiem-no-marker-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def write(self, relpath, text):
        path = os.path.join(self.tmp, relpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_tool(self, *args, env=None):
        proc = subprocess.run([sys.executable, TOOL, *args], capture_output=True,
                              text=True, timeout=60,
                              env=dict(os.environ, **(env or {})))
        return proc.returncode, proc.stdout, proc.stderr

    # --- the two cases spec Q8 names ------------------------------------------------

    def test_marker_without_upgrade_path_fails_with_path_and_line(self):
        path = self.write("scripts/a.py", f"x = 1\n{BAD}\ny = 2\n")
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 1, out)
        # The tool prints `path:line:` with forward slashes so an editor and a CI log can
        # both jump to it; compare against the same shape rather than the host's separator.
        self.assertIn(f"{path.replace(os.sep, '/')}:2", out)
        self.assertIn("global lock", out)

    def test_marker_with_upgrade_path_passes(self):
        self.write("scripts/a.py", f"x = 1\n{GOOD}\n")
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 0, out)

    # --- the edges of "has an upgrade path" -----------------------------------------

    def test_empty_side_of_the_comma_is_missing_debt(self):
        self.write("scripts/a.py", f"# {PREFIX} global lock,\n")
        self.assertEqual(self.run_tool(self.tmp)[0], 1)

    def test_empty_ceiling_is_missing_debt(self):
        self.write("scripts/a.py", f"# {PREFIX} , per-account locks later\n")
        self.assertEqual(self.run_tool(self.tmp)[0], 1)

    def test_empty_marker_text_is_missing_debt(self):
        self.write("scripts/a.py", f"# {PREFIX}\n")
        self.assertEqual(self.run_tool(self.tmp)[0], 1)

    def test_tree_with_no_marker_passes(self):
        self.write("scripts/a.py", "x = 1\n")
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 0, out)

    def test_markdown_and_json_lines_are_scanned(self):
        self.write("docs/note.md", f"- {BAD}\n")
        self.write("conf/a.json", f'{{"note": "{PREFIX} global lock"}}\n')
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn("note.md:1", out)
        self.assertIn("a.json:1", out)

    def test_pycache_and_worktrees_are_skipped(self):
        self.write("scripts/__pycache__/a.py", f"{BAD}\n")
        self.write(".tdq-worktrees/t1/scripts/a.py", f"{BAD}\n")
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 0, out)

    def test_every_missing_marker_is_reported_not_just_the_first(self):
        self.write("scripts/a.py", f"{BAD}\n{BAD}\n")
        self.write("scripts/b.py", f"{BAD}\n")
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 1, out)
        self.assertEqual(len([ln for ln in out.splitlines() if PREFIX in ln]), 3, out)

    def test_allow_marker_exempts_a_line_that_only_names_the_pattern(self):
        self.write("scripts/a.py", f'MARKER = "{PREFIX}"  # no-marker: allow\n')
        code, out, _ = self.run_tool(self.tmp)
        self.assertEqual(code, 0, out)

    # --- log service -----------------------------------------------------------------

    def test_log_line_is_on_by_default_and_carries_a_timestamp(self):
        self.write("scripts/a.py", f"{GOOD}\n")
        _, out, err = self.run_tool(self.tmp)
        line = [ln for ln in (out + err).splitlines() if "kiem_no_marker" in ln]
        self.assertTrue(line, out + err)
        self.assertRegex(line[0], r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] kiem_no_marker")
        self.assertRegex(line[0], r"1 marker")

    def test_quiet_flag_and_env_both_silence_the_log(self):
        self.write("scripts/a.py", f"{GOOD}\n")
        for args, env in ((("--quiet", self.tmp), None), ((self.tmp,), {"TDQ_LOG": "0"})):
            code, out, err = self.run_tool(*args, env=env)
            self.assertEqual(code, 0, out)
            self.assertNotIn("kiem_no_marker", out + err)

    # --- the check as one runnable command -------------------------------------------

    def test_bad_path_is_a_syntax_exit(self):
        code, _, err = self.run_tool(os.path.join(self.tmp, "nope"))
        self.assertEqual(code, 2, err)

    def test_no_argument_scans_this_repo_and_is_clean(self):
        code, out, err = self.run_tool()
        self.assertEqual(code, 0, out + err)

    def test_tool_stays_a_flat_set_of_functions(self):
        """DoD Q13: no class, no new namespace — grep -c '^class ' must be 0."""
        with open(TOOL, encoding="utf-8") as f:
            source = f.read()
        self.assertEqual(re.findall(r"(?m)^class ", source), [])
        self.assertNotIn("import unittest", source)


if __name__ == "__main__":
    unittest.main()
