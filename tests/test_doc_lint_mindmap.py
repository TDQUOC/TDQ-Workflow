"""T2.6 — scripts/doc_lint.py must gate diagram files with tdq_mindmap's own rules.

A diagram file under docs/tdq/mind-map/ carries its OWN shape contract (SD1..SD7,
scripts/tdq_mindmap.py::check_diagram). doc_lint.py must plug that check into its
`is_output` branch and MUST NOT re-implement the shape logic — it imports and calls
the pure function from tdq_mindmap.py, so the two tools can never disagree about
what a valid diagram is. The rule is scoped to docs/tdq/mind-map/ only: any other
file, output directory or not, keeps its existing behaviour untouched.
"""
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

LINT = os.path.join(ROOT, "scripts", "doc_lint.py")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402 — asserts against the real MIND_MAP_DIR constant
import tdq_mindmap  # noqa: E402 — asserts against the real rule codes, not literals


# A minimal valid diagram. English content everywhere except the mandatory branch
# keyword (tdq_mindmap.py's own contract, written in Vietnamese on purpose) — each such
# line carries the same i18n-allow marker tdq_mindmap.py uses for its own template lines.
CLEAN_DIAGRAM = (
    "# Login flow\n"
    "@nhánh: Account > Login\n"  # i18n-allow
    "\n"
    "B1 · Enter email and password (src/login.py::handle_login)\n"
    "B2 · Verify credentials (server/auth.py::AuthController.login)\n"
)


class MindMapLintBase(unittest.TestCase):
    """Fixtures live at <tmp>/docs/tdq/mind-map/<name> so doc_lint.py's own OUTPUT_DIRS
    substring match (docs/tdq) and the mind-map subdirectory both trigger for real —
    no mocking of path logic."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, text, *parts):
        path = os.path.join(self.tmp.name, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def write_diagram(self, text, name="feature.md"):
        return self.write(text, "docs", "tdq", "mind-map", name)

    def lint(self, *paths):
        proc = subprocess.run([sys.executable, LINT, *paths],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout


class TestCleanDiagramPasses(MindMapLintBase):
    def test_clean_diagram_under_mind_map_exits_0_no_output(self):
        path = self.write_diagram(CLEAN_DIAGRAM)
        code, out = self.lint(path)
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip(), "", out)


class TestBrokenDiagramReportsShapeCodes(MindMapLintBase):
    def test_missing_branch_line_reports_sd_code_with_line_number(self):
        broken = CLEAN_DIAGRAM.replace("@nhánh: Account > Login\n", "")  # i18n-allow
        path = self.write_diagram(broken)
        code, out = self.lint(path)
        self.assertEqual(code, 1, out)
        self.assertIn(f"[{tdq_mindmap.RULE_BRANCH_MISSING}]", out)
        self.assertRegex(out, rf"(?m)^{path}:\d+: \[{tdq_mindmap.RULE_BRANCH_MISSING}\] \S")

    def test_step_order_jump_reports_sd_code(self):
        broken = "# T\n@nhánh: A > B\nB1 · x (?)\nB3 · y (?)\n"  # i18n-allow
        path = self.write_diagram(broken)
        code, out = self.lint(path)
        self.assertEqual(code, 1, out)
        self.assertIn(f"[{tdq_mindmap.RULE_STEP_ORDER}]", out)

    def test_output_matches_check_diagram_exactly_no_reimplemented_logic(self):
        """doc_lint.py must call tdq_mindmap.check_diagram, not re-derive its own
        violations — the printed lines must be byte-identical to that function's."""
        broken = CLEAN_DIAGRAM.replace("@nhánh: Account > Login\n", "@nhánh: Account\n")  # i18n-allow
        path = self.write_diagram(broken)
        expected = [str(v) for v in tdq_mindmap.check_diagram(broken.splitlines(), path)]
        self.assertTrue(expected, "fixture must actually be broken")
        _, out = self.lint(path)
        got = [line for line in out.splitlines() if line.strip()]
        self.assertEqual(got, expected)


class TestRuleScopedToMindMapDirOnly(MindMapLintBase):
    """Rule 3 of the task: only docs/tdq/mind-map/ is bound. Everywhere else, even
    other files inside docs/tdq/, must never see an SD code."""

    def test_broken_content_elsewhere_in_docs_tdq_has_no_sd_code(self):
        broken = "not a diagram at all, no title, no branch\n"
        path = self.write(broken, "docs", "tdq", "other.md")
        _, out = self.lint(path)
        for rule in tdq_mindmap.ALL_RULES:
            self.assertNotIn(f"[{rule}]", out)

    def test_broken_content_outside_any_output_dir_has_no_sd_code(self):
        broken = "not a diagram at all, no title, no branch\n"
        path = self.write(broken, "elsewhere", "notes.md")
        _, out = self.lint(path)
        for rule in tdq_mindmap.ALL_RULES:
            self.assertNotIn(f"[{rule}]", out)


class TestManualCheckFromThePlan(unittest.TestCase):
    """Plan's Test line asks for `doc_lint.py docs/tdq/mind-map/dang-nhap.md` exit 0.
    That exact file is created later by T3.1 (runs after this task), so this test
    builds the same fixture in a tmpdir instead of depending on a file this task
    cannot see yet."""

    def test_valid_diagram_file_named_like_the_plan_example_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "docs", "tdq", "mind-map", "dang-nhap.md")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(CLEAN_DIAGRAM)
            proc = subprocess.run([sys.executable, LINT, path],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout)


class TestPluggedIntoIsOutputBranchNotRules(unittest.TestCase):
    """Rule 1 of the task: the mind-map check must not be a member of RULES."""

    def test_check_diagram_not_added_to_rules_list(self):
        self.assertNotIn(tdq_mindmap.check_diagram, doc_lint.RULES)

    def test_doc_lint_imports_check_diagram_instead_of_reimplementing_it(self):
        self.assertIs(doc_lint.check_diagram, tdq_mindmap.check_diagram)


if __name__ == "__main__":
    unittest.main()
