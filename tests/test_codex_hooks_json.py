"""`.codex/hooks.json` ở GỐC REPO — file viết tay, chỉ hai cổng `PreToolUse`.

Vì sao khoá bằng test thay vì để nó "hiển nhiên": hàm sinh bundle
`build_portable._sinh_hooks_codex` đi hết bảng 5 hook của bộ TDQ. Dùng nó cho file ở gốc
repo nghĩa là mỗi lượt `codex exec` sẽ bị chính `Stop → stop_gate.py` giữ lại ở cuối lượt
và bị `UserPromptSubmit → prompt_context.py` bơm `[TDQ:*]` vào prompt — lượt Codex tự vướng
vào cổng của pipeline đang lái nó. Ở gốc repo chỉ được có hàng rào vùng file.
"""
import ast
import json
import os
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUONG = os.path.join(GOC, ".codex", "hooks.json")
CAM = ("Stop", "UserPromptSubmit", "SessionStart", "PostToolUse", "SubagentStop")


class TestHooksJsonGocRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DUONG, encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.hooks = cls.data.get("hooks") or {}

    def test_chi_co_pretooluse(self):
        self.assertEqual(list(self.hooks), ["PreToolUse"])
        for khoa in CAM:
            with self.subTest(khoa=khoa):
                self.assertNotIn(khoa, self.hooks, f"{khoa} sẽ tự vướng vào lượt Codex")

    def test_dung_hai_matcher(self):
        matcher = sorted(nhom.get("matcher") for nhom in self.hooks["PreToolUse"])
        self.assertEqual(matcher, ["Bash", "apply_patch"])

    def test_ca_hai_deu_tro_ve_hang_rao_vung(self):
        """Cả hai cổng cùng một file: luật vùng chỉ được viết ở MỘT chỗ."""
        for nhom in self.hooks["PreToolUse"]:
            with self.subTest(matcher=nhom.get("matcher")):
                lenh = nhom["hooks"][0]["command"]
                self.assertIn("codex_edit_gate.py", lenh)
                self.assertEqual(nhom["hooks"][0]["type"], "command")
                self.assertNotIn(GOC, lenh, "đường dẫn phải TƯƠNG ĐỐI gốc repo")

    def test_file_hook_duoc_tro_toi_co_that(self):
        for nhom in self.hooks["PreToolUse"]:
            duong = nhom["hooks"][0]["command"].split('"')[1]
            with self.subTest(duong=duong):
                self.assertTrue(os.path.isfile(os.path.join(GOC, duong)), duong)


class TestBuildPortableKhongDungToiGocRepo(unittest.TestCase):
    """Hàm sinh bundle chỉ được ghi vào thư mục đích, không bao giờ vào `.codex/` gốc repo."""

    def test_khong_co_loi_goi_sinh_hooks_vao_goc_repo(self):
        with open(os.path.join(GOC, "scripts", "build_portable.py"), encoding="utf-8") as f:
            cay = ast.parse(f.read())
        for nut in ast.walk(cay):
            if not (isinstance(nut, ast.Call) and isinstance(nut.func, ast.Name)
                    and nut.func.id == "_sinh_hooks_codex"):
                continue
            nguon = ast.dump(nut.args[0]) if nut.args else ""
            self.assertNotIn("'repo'", nguon,
                             "hàm sinh bundle đang ghi hooks.json vào gốc repo")
            self.assertIn("goc", nguon, "đích phải là thư mục bundle")


if __name__ == "__main__":
    unittest.main()
