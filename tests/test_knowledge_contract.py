#!/usr/bin/env python3
"""Tests for knowledge curation contract, candidate states, and validation (O12 / T3.5).

Covers:
1. Lifecycle states: candidate, reviewed, rejected, superseded.
2. Candidate / legacy unverified cannot auto-promote to active system policy.
3. Reviewed requires human reviewer, review date, and evidence pointer.
4. Superseded / revoked requires replacement reference.
5. Secret scanning: synthetic secrets detected and rejected, zero secret leakage in logs.
"""
import io
import os
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(GOC, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import tdq_knowledge


class TestKnowledgeLifecycleStates(unittest.TestCase):
    """Kiểm tra các trạng thái vòng đời bài học tri thức (O12)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write_doc(self, filename, content):
        path = os.path.join(self.tmp.name, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_candidate_cannot_be_auto_policy(self):
        """Bài học candidate không được phép tự nới quyền hoặc tự kích hoạt thành policy."""
        doc = (
            "---\n"
            "tieu_de: Bai hoc test\n"
            "trang_thai: candidate\n"
            "nguon:\n"
            "  request: 2026-10-17-test\n"
            "  commit: abc1234\n"
            "  evidence: docs/tdq/qc/test.md\n"
            "pham_vi: skills/tdq-build\n"
            "auto_policy: true\n"  # Không được phép true ở candidate
            "---\n\n"
            "Noi dung bai hoc kinh nghiem.\n"
        )
        path = self.write_doc("candidate_invalid.md", doc)
        hop_le, ly_do, _ = tdq_knowledge.xac_thuc_bai_hoc(path)
        self.assertFalse(hop_le)
        self.assertIn("auto_policy", ly_do)

    def test_candidate_hop_le_khi_auto_policy_false(self):
        """Bài học candidate hợp lệ khi auto_policy là false hoặc không có."""
        doc = (
            "---\n"
            "tieu_de: Bai hoc candidate hop le\n"
            "trang_thai: candidate\n"
            "nguon:\n"
            "  request: 2026-10-17-test\n"
            "  commit: abc1234\n"
            "  evidence: docs/tdq/qc/test.md\n"
            "pham_vi: scripts/tdq_eval.py\n"
            "auto_policy: false\n"
            "---\n\n"
            "Kinh nghiem ve offline trace evaluation.\n"
        )
        path = self.write_doc("candidate_valid.md", doc)
        hop_le, ly_do, metadata = tdq_knowledge.xac_thuc_bai_hoc(path)
        self.assertTrue(hop_le, f"Le ra hop le: {ly_do}")
        self.assertEqual(metadata["trang_thai"], "candidate")
        self.assertFalse(metadata.get("auto_policy", False))

    def test_reviewed_requires_human_reviewer_and_evidence(self):
        """Bài học reviewed bắt buộc phải có người duyệt, ngày duyệt và bằng chứng."""
        # Thiếu người duyệt
        doc1 = (
            "---\n"
            "tieu_de: Reviewed thieu nguoi duyet\n"
            "trang_thai: reviewed\n"
            "nguon:\n"
            "  request: 2026-10-17-test\n"
            "  commit: abc1234\n"
            "  evidence: docs/tdq/qc/test.md\n"
            "pham_vi: global\n"
            "---\n\n"
            "Noi dung.\n"
        )
        path1 = self.write_doc("reviewed_no_reviewer.md", doc1)
        hop_le1, ly_do1, _ = tdq_knowledge.xac_thuc_bai_hoc(path1)
        self.assertFalse(hop_le1)
        self.assertIn("nguoi_duyet", ly_do1)

        # Đầy đủ thông tin
        doc2 = (
            "---\n"
            "tieu_de: Reviewed day du\n"
            "trang_thai: reviewed\n"
            "nguon:\n"
            "  request: 2026-10-17-test\n"
            "  commit: abc1234\n"
            "  evidence: docs/tdq/qc/test.md\n"
            "pham_vi: global\n"
            "nguoi_duyet: tdq-team\n"
            "ngay_duyet: 2026-10-17T18:00:00\n"
            "---\n\n"
            "Noi dung chuan muc.\n"
        )
        path2 = self.write_doc("reviewed_valid.md", doc2)
        hop_le2, ly_do2, meta2 = tdq_knowledge.xac_thuc_bai_hoc(path2)
        self.assertTrue(hop_le2, f"Le ra hop le: {ly_do2}")
        self.assertEqual(meta2["trang_thai"], "reviewed")
        self.assertEqual(meta2["nguoi_duyet"], "tdq-team")

    def test_superseded_requires_replacement_pointer(self):
        """Bài học superseded bắt buộc phải khai báo thay_the (superseded_by)."""
        doc = (
            "---\n"
            "tieu_de: Bai hoc da cu\n"
            "trang_thai: superseded\n"
            "nguon:\n"
            "  request: 2026-10-17-test\n"
            "---\n\n"
            "Bai hoc nay da bi thay the.\n"
        )
        path = self.write_doc("superseded_missing.md", doc)
        hop_le, ly_do, _ = tdq_knowledge.xac_thuc_bai_hoc(path)
        self.assertFalse(hop_le)
        self.assertIn("thay_the", ly_do)

    def test_legacy_unverified_handled_without_auto_promotion(self):
        """Tài liệu legacy không có frontmatter chuẩn được xếp loại legacy_unverified, không tự promote."""
        doc = "# Bai hoc cu khong co frontmatter\n\nNoi dung ghi chep tu xua."
        path = self.write_doc("legacy.md", doc)
        hop_le, _, meta = tdq_knowledge.xac_thuc_bai_hoc(path)
        self.assertTrue(hop_le)
        self.assertEqual(meta["trang_thai"], "legacy_unverified")
        self.assertFalse(meta.get("auto_policy", False))


class TestKnowledgeSecretScreening(unittest.TestCase):
    """Kiểm tra phát hiện và ngăn chặn lưu trữ secret (O12)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write_doc(self, filename, content):
        path = os.path.join(self.tmp.name, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_detects_synthetic_secrets_and_rejects(self):
        """Từ chối bài học chứa secret/token (API key, Bearer token, private key)."""
        secret_sample = "sk-ant-api03-abcdef1234567890abcdef1234567890"
        doc = (
            f"---\n"
            f"tieu_de: Bai hoc lo secret\n"
            f"trang_thai: candidate\n"
            f"---\n\n"
            f"Dung token sau de goi API: {secret_sample}\n"
        )
        path = self.write_doc("secret.md", doc)
        hop_le, ly_do, _ = tdq_knowledge.xac_thuc_bai_hoc(path)
        self.assertFalse(hop_le)
        self.assertIn("secret", ly_do.lower())
        # Không được để lộ raw secret trong chuỗi lý do lỗi
        self.assertNotIn(secret_sample, ly_do)

    def test_logs_do_not_leak_secrets(self):
        """Khi kiểm tra bài học chứa bí mật, stderr/log không in raw secret ra màn hình."""
        raw_secret = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        doc = (
            f"---\n"
            f"tieu_de: GitHub token leak\n"
            f"trang_thai: candidate\n"
            f"---\n\n"
            f"Token: {raw_secret}\n"
        )
        path = self.write_doc("gh_secret.md", doc)
        captured_err = io.StringIO()
        old_stderr = sys.stderr
        try:
            sys.stderr = captured_err
            tdq_knowledge.kiem_tra_file(path)
        finally:
            sys.stderr = old_stderr

        log_output = captured_err.getvalue()
        self.assertNotIn(raw_secret, log_output, "Raw secret bi ro ri ra log!")


class TestKnowledgeCli(unittest.TestCase):
    """Kiểm tra giao diện dòng lệnh của tdq_knowledge."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write_doc(self, filename, content):
        path = os.path.join(self.tmp.name, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_cli_check_valid_file(self):
        doc = (
            "---\n"
            "tieu_de: Valid candidate\n"
            "trang_thai: candidate\n"
            "---\n\n"
            "Noi dung an toan.\n"
        )
        path = self.write_doc("valid.md", doc)
        rc = tdq_knowledge.main(["check", path])
        self.assertEqual(rc, 0)

    def test_cli_check_invalid_file(self):
        doc = (
            "---\n"
            "tieu_de: Invalid candidate\n"
            "trang_thai: candidate\n"
            "auto_policy: true\n"
            "---\n\n"
            "Noi dung.\n"
        )
        path = self.write_doc("invalid.md", doc)
        rc = tdq_knowledge.main(["check", path])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
