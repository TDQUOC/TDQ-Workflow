"""Unit tests cho tính năng tự động cập nhật setup khi phát hiện version mới qua SessionStart."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
import search_rules  # noqa: E402
import tdq_setup  # noqa: E402
import session_start  # noqa: E402


class TestAutoUpdateSetup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = self.tmp.name
        self.plugin_dir = os.path.join(self.project, "fake_plugin")
        os.makedirs(os.path.join(self.plugin_dir, ".claude-plugin"), exist_ok=True)
        with open(os.path.join(self.plugin_dir, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "tdq-workflow", "version": "0.62.0"}, f)

    def tearDown(self):
        self.tmp.cleanup()

    def test_doc_phien_ban_plugin(self):
        ver = tdq_setup.doc_phien_ban_plugin(self.plugin_dir)
        self.assertEqual(ver, "0.62.0")

    def test_can_cap_nhat_phien_ban_khi_chua_co_stamp(self):
        self.assertTrue(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))

    def test_khong_can_cap_nhat_khi_stamp_khop(self):
        tdq_setup.ghi_phat_hanh(self.project, "0.62.0")
        self.assertFalse(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))

    def test_can_cap_nhat_khi_version_stamp_cu(self):
        tdq_setup.ghi_phat_hanh(self.project, "0.61.0")
        self.assertTrue(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))

    def test_tu_dong_cap_nhat_khi_doi_phien_ban(self):
        inst_path = os.path.join(self.project, "CLAUDE.md")
        with mock.patch("tdq_setup.DUONG_INSTRUCTION", inst_path), \
             mock.patch("tdq_setup._tim_cong_cu", return_value=None), \
             mock.patch("tdq_setup.don_may", return_value=([], [])):
            ok = tdq_setup.tu_dong_cap_nhat_khi_doi_phien_ban(self.project, self.plugin_dir)
            self.assertTrue(ok)
            # Stamp đã ghi version 0.62.0
            stamp = tdq_setup.doc_phat_hanh(self.project)
            self.assertIsNotNone(stamp)
            self.assertEqual(stamp.get("phien_ban"), "0.62.0")
            # Instruction đã ghim nội dung
            with open(inst_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("## Bộ tìm kiếm 3 tầng", content)
            self.assertIn("## Nguyên tắc TDQ Workflow bắt buộc", content)

    def test_session_start_kich_hoat_tu_dong_cap_nhat(self):
        inst_path = os.path.join(self.project, "CLAUDE.md")
        with mock.patch("tdq_setup.DUONG_INSTRUCTION", inst_path), \
             mock.patch.object(session_start, "la_project_that", return_value=True), \
             mock.patch.object(session_start, "can_khoi_tao", return_value=False), \
             mock.patch("tdq_setup._tim_cong_cu", return_value=None), \
             mock.patch("tdq_setup.don_may", return_value=([], [])), \
             mock.patch("sys.stdout", new_callable=unittest.mock.MagicMock):
            # Lần 1: version mới -> tự cập nhật
            tdq_setup.ghi_phat_hanh(self.project, "0.61.0")
            with mock.patch.object(session_start, "GOC_PLUGIN", self.plugin_dir):
                self.assertTrue(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))
                tdq_setup.tu_dong_cap_nhat_khi_doi_phien_ban(self.project, self.plugin_dir)
                self.assertFalse(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))
