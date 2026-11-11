"""R15: Task can thiệp mã nguồn trong Plan phải có khối đặc tả kỹ thuật/pseudo-code."""
import os
import shutil
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402


class TestRuleR15(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp_dir, True)
        self.plan_dir = os.path.join(self.tmp_dir, "docs", "tdq", "plan")
        os.makedirs(self.plan_dir, exist_ok=True)

    def _create_plan(self, task_content, filename="2026-11-11-0230-thu-nghiem.md"):
        path = os.path.join(self.plan_dir, filename)
        content = (
            "# PLAN — Thử nghiệm\n\n"
            "Ngày: 2026-11-11 · Spec: ../spec/2026-11-11-0230-thu.md · Lane: full\n\n"
            "## P1 — Thử nghiệm\n\n"
            f"{task_content}\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_r15_fails_on_single_line_code_task(self):
        task = (
            "- [ ] **T1.1** (e5m) Sửa mã nguồn đơn dòng — Test: pytest tests/test_foo.py\n"
            "  - Chạm: `scripts/demo.py`\n"
        )
        plan_path = self._create_plan(task)
        loi = [d for d in doc_lint.lint_file(plan_path) if "[R15]" in d]
        self.assertEqual(len(loi), 1)
        self.assertIn("[R15]", loi[0])

    def test_r15_passes_on_detailed_code_task(self):
        task = (
            "- [ ] **T1.1** (e5m) Sửa mã nguồn chi tiết — Test: pytest tests/test_foo.py\n"
            "  - Chạm: `scripts/demo.py`\n"
            "  - Đặc tả: Khởi tạo module và xử lý sự kiện\n"
            "  - Logic: Kiểm tra điều kiện đầu vào và cập nhật trạng thái\n"
        )
        plan_path = self._create_plan(task)
        loi = [d for d in doc_lint.lint_file(plan_path) if "[R15]" in d]
        self.assertEqual(loi, [])

    def test_r15_passes_on_doc_only_task(self):
        task = (
            "- [ ] **T1.1** (e5m) Sửa tài liệu đơn dòng — Test: python scripts/doc_lint.py\n"
            "  - Chạm: `docs/tdq/spec/test.md`, `data/config.json`\n"
        )
        plan_path = self._create_plan(task)
        loi = [d for d in doc_lint.lint_file(plan_path) if "[R15]" in d]
        self.assertEqual(loi, [])


if __name__ == "__main__":
    unittest.main()
