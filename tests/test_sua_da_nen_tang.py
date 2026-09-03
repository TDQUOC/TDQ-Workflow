"""Giữ bốn bản sửa đa nền tảng P1–P4 khỏi tái phát.

Không có máy Windows để chạy thử, nên mọi ca ở đây kiểm hành vi Windows bằng cách truyền hệ
điều hành vào làm THAM SỐ, chứ không đọc `sys.platform` của máy đang chạy. Đó cũng là ràng buộc
thiết kế của request: chỗ nào quyết định tên lệnh Python thì chỗ đó phải nhận hệ điều hành từ
bên ngoài, nếu không sẽ không kiểm được từ macOS.

Nguồn gốc bốn lỗi: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-tuong-thich.md`.
"""
import json
import os
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))

import build_portable  # noqa: E402
import tdq_checkportable  # noqa: E402
import tdq_team  # noqa: E402


def _dung_bundle_agy(thu_muc, command, mo_ta):
    """Dựng một bundle agy giả tối thiểu: `plugin.json` ở gốc + `hooks.json`."""
    with open(os.path.join(thu_muc, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump({"name": "tdq-workflow"}, f)
    with open(os.path.join(thu_muc, "hooks.json"), "w", encoding="utf-8") as f:
        json.dump({
            "description": mo_ta,
            "hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": command}]}]},
        }, f, ensure_ascii=False)


class CongGacTest(unittest.TestCase):
    """P2 — cổng gác agy phải soi `command`, không soi văn bản thô cả file."""

    def test_cong_gac_khong_no_sai_khi_dau_nga_chi_nam_trong_mo_ta(self):
        nha = os.path.expanduser("~")
        with tempfile.TemporaryDirectory() as thu_muc:
            _dung_bundle_agy(
                thu_muc,
                command=f"python3 {nha}/.gemini/config/plugins/tdq/hooks/scripts/a.py",
                # Dấu `~` nằm ở đây, và CHỈ ở đây — đúng ca làm lỗi cũ luôn nổ.
                mo_ta="bật plugin trong ~/.gemini/config/config.json",
            )
            ghi_chu = tdq_checkportable.kiem_layout_agy(thu_muc, {})
        self.assertFalse([g for g in ghi_chu if "unexpanded" in g],
                         f"cổng gác nổ sai khi `~` chỉ nằm trong mô tả: {ghi_chu}")

    def test_cong_gac_van_no_khi_command_that_su_con_dau_ngan(self):
        with tempfile.TemporaryDirectory() as thu_muc:
            _dung_bundle_agy(thu_muc, command="python3 ~/.gemini/x.py", mo_ta="không có dấu nào")
            ghi_chu = tdq_checkportable.kiem_layout_agy(thu_muc, {})
        self.assertTrue([g for g in ghi_chu if "unexpanded" in g],
                        f"`command` còn `~` thật mà cổng gác im: {ghi_chu}")

    def test_cong_gac_no_dung_khi_bundle_dung_o_thu_muc_nha_khac(self):
        with tempfile.TemporaryDirectory() as thu_muc:
            _dung_bundle_agy(
                thu_muc,
                command="python3 /Users/nguoikhac/.gemini/config/plugins/tdq/hooks/scripts/a.py",
                mo_ta="bật plugin trong ~/.gemini/config/config.json",
            )
            ghi_chu = tdq_checkportable.kiem_layout_agy(thu_muc, {})
        self.assertTrue([g for g in ghi_chu if "another home folder" in g],
                        f"bundle dựng dưới thư mục nhà lạ mà cổng gác không cảnh báo: {ghi_chu}")

    def test_cong_gac_bao_khi_hooks_json_hong_cu_phap(self):
        with tempfile.TemporaryDirectory() as thu_muc:
            with open(os.path.join(thu_muc, "plugin.json"), "w", encoding="utf-8") as f:
                json.dump({"name": "tdq-workflow"}, f)
            with open(os.path.join(thu_muc, "hooks.json"), "w", encoding="utf-8") as f:
                f.write("{ khong phai JSON")
            ghi_chu = tdq_checkportable.kiem_layout_agy(thu_muc, {})
        self.assertTrue([g for g in ghi_chu if "not valid JSON" in g],
                        f"hooks.json hỏng cú pháp mà cổng gác im: {ghi_chu}")


class TienToPythonTest(unittest.TestCase):
    """P1 — tên lệnh Python chọn theo hệ điều hành nhận qua tham số."""

    def test_tien_to_theo_tung_he_dieu_hanh(self):
        for nen_tang, mong_doi in (("win32", "py -3"), ("darwin", "python3"), ("linux", "python3")):
            with self.subTest(nen_tang=nen_tang):
                self.assertEqual(build_portable.tien_to_python(nen_tang), mong_doi)

    def test_tien_to_mac_dinh_theo_may_dang_chay(self):
        self.assertEqual(build_portable.tien_to_python(),
                         build_portable.tien_to_python(sys.platform))


def _command_cua(duong):
    with open(duong, encoding="utf-8") as f:
        return tdq_checkportable._moi_command(json.load(f))


class SinhCommandTest(unittest.TestCase):
    """P1 — hai chỗ sinh `command` cho codex và agy đi qua hàm chọn tên lệnh."""

    def test_sinh_command_codex_theo_he_dich(self):
        for nen_tang, tien_to in (("win32", "py -3 "), ("darwin", "python3 ")):
            with self.subTest(nen_tang=nen_tang), tempfile.TemporaryDirectory() as thu_muc:
                duong = os.path.join(thu_muc, "hooks.json")
                build_portable._sinh_hooks_codex(duong, nen_tang)
                lenh = _command_cua(duong)
                self.assertTrue(lenh, "không sinh được `command` nào")
                for c in lenh:
                    self.assertTrue(c.startswith(tien_to), f"{nen_tang}: {c!r}")

    def test_sinh_command_agy_theo_he_dich(self):
        for nen_tang, tien_to in (("win32", "py -3 "), ("linux", "python3 ")):
            with self.subTest(nen_tang=nen_tang), tempfile.TemporaryDirectory() as thu_muc:
                duong = os.path.join(thu_muc, "hooks.json")
                build_portable._sinh_hooks_agy(duong, nen_tang)
                lenh = _command_cua(duong)
                self.assertTrue(lenh, "không sinh được `command` nào")
                for c in lenh:
                    self.assertTrue(c.startswith(tien_to), f"{nen_tang}: {c!r}")

    def test_khong_con_ten_lenh_python3_viet_cung_trong_ma_sinh(self):
        """Chuỗi `python3` chỉ được nằm trong hàm chọn tên lệnh, không nằm ở chỗ sinh `command`."""
        with open(os.path.join(GOC, "scripts", "build_portable.py"), encoding="utf-8") as f:
            dong_command = [d for d in f.read().splitlines()
                            if '"command"' in d and "python3" in d]
        self.assertEqual(dong_command, [], f"còn tên lệnh viết cứng: {dong_command}")


class HookClaudeTest(unittest.TestCase):
    """P1 nhóm hai — `hooks/hooks.json` là file nguồn viết tay, sinh lại tại máy đích."""

    def _ban_sao(self, thu_muc):
        goc = os.path.join(GOC, "hooks", "hooks.json")
        dich = os.path.join(thu_muc, "hooks.json")
        with open(goc, encoding="utf-8") as f:
            noi_dung = f.read()
        with open(dich, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return dich

    def test_hook_claude_win_doi_sang_trinh_khoi_chay(self):
        with tempfile.TemporaryDirectory() as thu_muc:
            duong = self._ban_sao(thu_muc)
            build_portable.sinh_hook_claude(duong, "win32")
            lenh = _command_cua(duong)
            self.assertTrue(lenh)
            for c in lenh:
                self.assertTrue(c.startswith("py -3 "), c)
                # Biến của host phải còn nguyên, nếu mất thì hook trỏ vào hư không.
                self.assertIn("${CLAUDE_PLUGIN_ROOT}", c)

    def test_bat_bien_chay_hai_lan_ra_cung_mot_file(self):
        for nen_tang in ("win32", "darwin"):
            with self.subTest(nen_tang=nen_tang), tempfile.TemporaryDirectory() as thu_muc:
                duong = self._ban_sao(thu_muc)
                build_portable.sinh_hook_claude(duong, nen_tang)
                with open(duong, encoding="utf-8") as f:
                    lan_mot = f.read()
                doi = build_portable.sinh_hook_claude(duong, nen_tang)
                with open(duong, encoding="utf-8") as f:
                    lan_hai = f.read()
                self.assertFalse(doi, "lần chạy thứ hai vẫn báo có thay đổi")
                self.assertEqual(lan_mot, lan_hai)

    def test_he_posix_khong_lam_ban_file_nguon(self):
        """Trên macOS/Linux lệnh này phải là no-op — nếu không, git của user bẩn vô cớ."""
        with tempfile.TemporaryDirectory() as thu_muc:
            duong = self._ban_sao(thu_muc)
            self.assertFalse(build_portable.sinh_hook_claude(duong, "darwin"),
                             "sinh lại trên POSIX mà vẫn đổi file nguồn")


class ChuanHoaLenhTestTest(unittest.TestCase):
    """P4 — dòng `Test:` của plan chạy được ở máy không có tên lệnh `python3`."""

    def test_chuan_hoa_doi_token_dau_tien(self):
        lenh, _ = tdq_team.chuan_hoa_lenh_test("python3 -m pytest -q")
        self.assertNotEqual(lenh, "python3 -m pytest -q", "token đầu tiên không được đổi")
        self.assertTrue(lenh.endswith(" -m pytest -q"), lenh)
        self.assertTrue(lenh.split(" ", 1)[0].strip('"') == sys.executable, lenh)

    def test_chuan_hoa_khong_dung_toi_dang_khac(self):
        for nguyen in ("pytest -q", "mypython3 x", "python -m pytest", "echo python3"):
            with self.subTest(lenh=nguyen):
                lenh, _ = tdq_team.chuan_hoa_lenh_test(nguyen)
                self.assertEqual(lenh, nguyen)

    def test_canh_bao_shell_van_tra_lenh_chay_duoc(self):
        lenh, canh_bao = tdq_team.chuan_hoa_lenh_test("python3 -m pytest && echo ok")
        self.assertTrue(canh_bao, "dòng có `&&` mà không cảnh báo")
        self.assertTrue(lenh.endswith("-m pytest && echo ok"), lenh)

    def test_canh_bao_shell_im_khi_lenh_don(self):
        _, canh_bao = tdq_team.chuan_hoa_lenh_test("python3 -m pytest -q")
        self.assertEqual(canh_bao, [])


class ReadmeAgyTest(unittest.TestCase):
    """P3 — người ở máy khác phải đọc được cảnh báo, không chỉ docstring của code."""

    def test_readme_agy_canh_bao_gan_may_dung_va_ten_lenh(self):
        with open(os.path.join(GOC, "antigravity_portable", "README.md"), encoding="utf-8") as f:
            noi_dung = f.read()
        self.assertIn("build_portable.py", noi_dung)
        for tu_khoa in ("máy dựng", "py -3"):
            with self.subTest(tu_khoa=tu_khoa):
                self.assertIn(tu_khoa, noi_dung)


if __name__ == "__main__":
    unittest.main()
