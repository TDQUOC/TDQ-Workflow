"""Unit tests for the Vision Test Loop skill rule reference (vision-test-loop.md)."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISION_DOC = ROOT / "skills" / "tdq-build" / "references" / "vision-test-loop.md"
DOC_LINT = ROOT / "scripts" / "doc_lint.py"
I18N_CHECK = ROOT / "scripts" / "i18n_check.py"


class TestVisionTestLoopDoc(unittest.TestCase):
    """Verify that vision-test-loop.md exists and fulfills low-tier model mechanical rules."""

    def test_file_exists_and_has_dynamic_toc(self):
        """Reference file must exist and carry a dynamic line index block."""
        self.assertTrue(VISION_DOC.is_file(), f"Missing reference file: {VISION_DOC}")
        content = VISION_DOC.read_text(encoding="utf-8")
        self.assertIn("<!-- muc-luc-dong:", content)
        self.assertIn("## Table of contents", content)

    def test_trigger_decision_table_covers_all_visual_sources(self):
        """Decision table must cover mockup, wireframe, screenshot, prototype, and Figma."""
        content = VISION_DOC.read_text(encoding="utf-8").lower()
        for source_kind in ("mockup", "wireframe", "screenshot", "prototype", "figma"):
            self.assertIn(source_kind, content, f"Missing visual source type: {source_kind}")
        self.assertIn("--source", content)
        self.assertIn("--figma-url", content)

    def test_three_tier_scenario_and_six_anti_patterns(self):
        """Document must define the 3-tier Given-When-Then framework and ANTI-1..ANTI-6 with WRONG/RIGHT."""
        content = VISION_DOC.read_text(encoding="utf-8")
        for marker in ("Given", "When", "Then", "Tier 1", "Tier 2", "Tier 3"):
            self.assertIn(marker, content, f"Missing scenario marker: {marker}")
        for idx in range(1, 7):
            self.assertIn(f"ANTI-{idx}", content, f"Missing anti-pattern ANTI-{idx}")
        self.assertIn("WRONG", content)
        self.assertIn("RIGHT", content)

    def test_six_mechanical_steps_and_box_mapping(self):
        """Document must have 6 numbered mechanical steps, box-to-CSS mapping, caps, and self-check."""
        content = VISION_DOC.read_text(encoding="utf-8")
        for marker in (
            "tdq_vision_diff.py",
            "diff_highlight.png",
            "metrics.json",
            "--embed-base64",
            "[1]",
            "[2]",
            "pause --loai dau-vao-user",
            "pause --loai tran-qc",
            "## Self-check",
        ):
            self.assertIn(marker, content, f"Missing required marker: {marker}")

    def test_doc_lint_and_i18n_clean(self):
        """Reference file must pass doc_lint.py and i18n_check.py with zero violations."""
        lint_proc = subprocess.run(
            [sys.executable, str(DOC_LINT), str(VISION_DOC)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(lint_proc.returncode, 0, f"doc_lint failed:\n{lint_proc.stdout}\n{lint_proc.stderr}")

        i18n_proc = subprocess.run(
            [sys.executable, str(I18N_CHECK), str(VISION_DOC)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(i18n_proc.returncode, 0, f"i18n_check failed:\n{i18n_proc.stdout}\n{i18n_proc.stderr}")


if __name__ == "__main__":
    unittest.main()
