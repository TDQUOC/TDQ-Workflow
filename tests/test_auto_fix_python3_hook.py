"""Test auto-fix python3 hook error, fallback commands, auto-check & auto-setup.

Đảm bảo:
1. 100% command trong hooks.json đều có chuỗi fallback đa nền tảng.
2. Logic tìm thư mục Scripts dự phòng trong tdq_checkportable hoạt động chuẩn xác.
3. tdq_setup tự động kiểm tra shim python3 và chạy dry-run hook thành công.
4. session_start nhận diện đúng lần đầu chạy plugin để kích hoạt setup.
5. KHOI_HUONG_DAN mang lệnh tương thích và nguyên tắc Self-healing.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))

import tdq_checkportable as cp  # noqa: E402
import tdq_setup  # noqa: E402
import tdq_ten_lenh as tl  # noqa: E402
import session_start  # noqa: E402


class HookFallbackTest(unittest.TestCase):
    """Kiểm tra cấu hình fallback chuỗi lệnh trong hooks/hooks.json."""

    def test_all_hook_commands_have_fallback(self):
        duong = os.path.join(ROOT, "hooks", "hooks.json")
        with open(duong, encoding="utf-8") as fh:
            data = json.load(fh)

        commands = []

        def _scan(obj):
            if isinstance(obj, dict):
                if "command" in obj and isinstance(obj["command"], str):
                    commands.append(obj["command"])
                for v in obj.values():
                    _scan(v)
            elif isinstance(obj, list):
                for item in obj:
                    _scan(item)

        _scan(data.get("hooks", {}))
        self.assertGreater(len(commands), 0, "hooks.json không có command nào")
        for cmd in commands:
            with self.subTest(cmd=cmd):
                self.assertIn("python3", cmd)
                self.assertIn("py -3", cmd)
                self.assertIn("python", cmd)
                self.assertIn("||", cmd)


class CheckPortableScriptsTest(unittest.TestCase):
    """Kiểm tra tìm thư mục Scripts fallback trong tdq_checkportable."""

    def test_chon_thu_muc_du_phong_scripts_khong_chua_stub(self):
        muc = cp.chon_thu_muc_du_phong_scripts()
        if muc is not None:
            self.assertNotIn("windowsapps", muc.lower().replace(os.sep, "/"))


class SetupShimAndDryRunTest(unittest.TestCase):
    """Kiểm tra logic kiểm tra shim và smoke test dry-run trong tdq_setup."""

    def test_kiem_dryrun_hook_thanh_cong(self):
        dat, chi_tiet = tdq_setup.kiem_dryrun_hook(ROOT)
        self.assertTrue(dat, f"Dry-run hook thất bại: {chi_tiet}")

    def test_kiem_va_cai_shim_python3(self):
        if not tl.la_windows():
            self.skipTest("Chỉ chạy trên Windows")
        da_cai, _, no = tdq_setup.kiem_va_cai_shim_python3()
        self.assertEqual(no, [], f"Không được để lại nợ shim: {no}")
        self.assertTrue(len(da_cai) > 0, "Phải báo cáo trạng thái shim đã cài hoặc sẵn sàng")


class SessionStartAutoSetupTest(unittest.TestCase):
    """Kiểm tra logic nhận diện lần đầu chạy plugin của session_start."""

    def test_kiem_can_setup_lan_dau_khong_phai_project(self):
        self.assertFalse(session_start.kiem_can_setup_lan_dau("C:\\"))
        self.assertFalse(session_start.kiem_can_setup_lan_dau(os.path.expanduser("~")))

    def test_kiem_can_setup_lan_dau_khi_thieu_phat_hanh(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            # Tạo thư mục .git để giả lập project thật
            os.makedirs(os.path.join(td, ".git"), exist_ok=True)
            self.assertTrue(session_start.kiem_can_setup_lan_dau(td))


class InstructionHardeningTest(unittest.TestCase):
    """Kiểm tra khối instruction KHOI_HUONG_DAN."""

    def test_khoi_huong_dan_co_fallback_va_self_healing(self):
        khoi = tdq_setup.KHOI_HUONG_DAN
        self.assertIn("py -3", khoi)
        self.assertIn("Self-healing", khoi)
        self.assertIn("Python was not found", khoi)


if __name__ == "__main__":
    unittest.main()
