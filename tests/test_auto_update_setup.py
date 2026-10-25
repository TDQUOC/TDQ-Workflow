"""Unit tests cho tính năng tự động cập nhật setup khi phát hiện version mới qua SessionStart."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
            assert stamp is not None
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
             mock.patch("sys.stdout", new_callable=mock.MagicMock):
            # Lần 1: version mới -> tự cập nhật
            tdq_setup.ghi_phat_hanh(self.project, "0.61.0")
            with mock.patch.object(session_start, "GOC_PLUGIN", self.plugin_dir):
                self.assertTrue(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))
                tdq_setup.tu_dong_cap_nhat_khi_doi_phien_ban(self.project, self.plugin_dir)
                self.assertFalse(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))

    def test_tach_version(self):
        self.assertEqual(tdq_setup.tach_version("0.82.0"), (0, 82, 0))
        self.assertEqual(tdq_setup.tach_version("v1.2.3-rc1"), (1, 2, 3, 1))
        self.assertTrue(tdq_setup.tach_version("0.82.0") > tdq_setup.tach_version("0.81.0"))
        self.assertFalse(tdq_setup.tach_version("0.81.0") > tdq_setup.tach_version("0.82.0"))

    def test_khong_downgrade_phat_hanh_khi_stamp_cao_hon(self):
        # Mốc dự án ghi 0.82.0, plugin cũ 0.62.0 -> KHÔNG được cập nhật (chống downgrade)
        tdq_setup.ghi_phat_hanh(self.project, "0.82.0")
        self.assertFalse(tdq_setup.can_cap_nhat_phien_ban(self.project, self.plugin_dir))

    def test_tu_dong_cap_nhat_plugin_user_tu_cwd(self):
        fake_home = os.path.join(self.project, "fake_home")
        plugins_dir = os.path.join(fake_home, ".claude", "plugins")
        os.makedirs(plugins_dir, exist_ok=True)
        installed = {
            "version": 2,
            "plugins": {
                "tdq-workflow@tdq-local": [
                    {
                        "scope": "user",
                        "installPath": os.path.join(plugins_dir, "cache", "0.60.0"),
                        "version": "0.60.0",
                    }
                ]
            }
        }
        with open(os.path.join(plugins_dir, "installed_plugins.json"), "w", encoding="utf-8") as f:
            json.dump(installed, f)

        # Giả lập cwd là repo có plugin.json version 0.62.0
        calls = []
        def fake_runner(cmd):
            calls.append(cmd)
            return 0, "updated successfully"

        old_val = os.environ.get("TDQ_KHONG_CHAM_MAY")
        try:
            os.environ["TDQ_KHONG_CHAM_MAY"] = "0"
            ok, msg = tdq_setup.tu_dong_cap_nhat_plugin_user(
                home=fake_home, goc_plugin=None, chay_lenh=fake_runner, cwd=self.plugin_dir)
            self.assertTrue(ok)
            self.assertIn("0.62.0", msg)
            self.assertTrue(any("plugin update" in c for c in calls))
        finally:
            if old_val is None:
                os.environ.pop("TDQ_KHONG_CHAM_MAY", None)
            else:
                os.environ["TDQ_KHONG_CHAM_MAY"] = old_val

    def test_can_kiem_tra_remote_throttle(self):
        fake_home = os.path.join(self.project, "fake_home_remote")
        # Chưa có stamp -> True
        self.assertTrue(tdq_setup.can_kiem_tra_remote(fake_home, throttle_seconds=3600))
        # Vừa check -> False
        tdq_setup.ghi_update_stamp(fake_home, {"last_check": tdq_setup._now()})
        self.assertFalse(tdq_setup.can_kiem_tra_remote(fake_home, throttle_seconds=3600))

    def test_thuc_hien_cap_nhat_remote_va_thong_bao(self):
        fake_home = os.path.join(self.project, "fake_home_mkt")
        plugins_dir = os.path.join(fake_home, ".claude", "plugins")
        mkt_dir = os.path.join(plugins_dir, "marketplaces", "tdq-local", ".claude-plugin")
        os.makedirs(mkt_dir, exist_ok=True)
        with open(os.path.join(mkt_dir, "plugin.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "tdq-workflow", "version": "0.63.0"}, f)

        installed = {
            "version": 2,
            "plugins": {
                "tdq-workflow@tdq-local": [
                    {
                        "scope": "user",
                        "installPath": os.path.join(plugins_dir, "cache", "0.60.0"),
                        "version": "0.60.0",
                    }
                ]
            }
        }
        with open(os.path.join(plugins_dir, "installed_plugins.json"), "w", encoding="utf-8") as f:
            json.dump(installed, f)

        calls = []
        def fake_runner(cmd):
            calls.append(cmd)
            return 0, "ok"

        with mock.patch("shutil.which", return_value="claude"), \
             mock.patch.dict(os.environ, {"TDQ_KHONG_CHAM_MAY": "0"}):
            ok, msg = tdq_setup.thuc_hien_cap_nhat_remote(home=fake_home, chay_lenh=fake_runner)
            self.assertTrue(ok)
            self.assertIn("0.63.0", msg)
            self.assertTrue(any("marketplace update" in c for c in calls))
            self.assertTrue(any("plugin update" in c for c in calls))

            # Thông báo update mới được đọc và xóa
            tb = tdq_setup.doc_thong_bao_update_moi(home=fake_home)
            self.assertIn("0.63.0", tb)
            # Lần 2 đã xóa -> rỗng
            self.assertEqual(tdq_setup.doc_thong_bao_update_moi(home=fake_home), "")
