"""Test `scripts/tdq_test.py` — bán kính ảnh hưởng của một tập file sửa (T1.1, 2026-10-03).

Nhóm theo DoD (tên nhóm nằm trong tên method để `-k` chọn được):
- `ca_da_do`: các ca đã đo ở brief, chạy trên repo THẬT;
- `tien_trinh_con`: test chỉ gọi hook qua tiến trình con vẫn được chọn;
- `duong_dan`: file luật dò theo đường dẫn tương đối, không theo tên trần;
- `quet_thu_muc`: test quét thư mục cha của file sửa được chọn (dò bằng AST);
- `tron_bo_khi`: các lúc phải rơi về trọn bộ.
"""
import os
import shutil
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_test  # noqa: E402


def ghi(goc, duong, noi_dung):
    full = os.path.join(goc, *duong.split("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(noi_dung)


class RepoTam(unittest.TestCase):
    """Repo tạm: vài module nguồn + nhiều test 'đệm' để bán kính nhỏ không chạm ngưỡng 60%."""

    SO_TEST_DEM = 10

    def setUp(self):
        self.goc = tempfile.mkdtemp(prefix="tdq-test-ban-kinh-")
        self.addCleanup(shutil.rmtree, self.goc, ignore_errors=True)
        ghi(self.goc, "scripts/lib_a.py", "X = 1\n")
        ghi(self.goc, "scripts/lib_b.py", "import lib_a\n")
        ghi(self.goc, "hooks/scripts/_common.py", "Y = 2\n")
        ghi(self.goc, "hooks/scripts/stop_gate.py",
            "def main():\n    from _common import Y\n    return Y\n")
        ghi(self.goc, "skills/a/SKILL.md", "# a\n")
        ghi(self.goc, "skills/b/SKILL.md", "# b\n")
        ghi(self.goc, "tests/helper.py", "ROOT = '.'\n")
        for i in range(self.SO_TEST_DEM):
            ghi(self.goc, f"tests/test_dem_{i:02d}.py", "import unittest\n")

    def ban_kinh(self, *files):
        return tdq_test.ban_kinh(list(files), self.goc)


class BanKinhCoBanTest(RepoTam):
    def test_ban_kinh_tat_ca_module_sap_xep(self):
        ghi(self.goc, "tests/test_aaa.py", "pass\n")
        mods = tdq_test.tat_ca_module(self.goc)
        self.assertEqual(mods, sorted(mods))
        self.assertIn("test_aaa.py", mods)
        self.assertNotIn("helper.py", mods)

    def test_ban_kinh_file_test_sua_chon_chinh_no(self):
        mods, ly_do = self.ban_kinh("tests/test_dem_03.py")
        self.assertIsNone(ly_do)
        self.assertEqual(mods, ["test_dem_03.py"])

    def test_ban_kinh_import_bac_cau(self):
        """lib_b import lib_a → test nhắc lib_b được chọn khi lib_a đổi."""
        ghi(self.goc, "tests/test_lib_b.py", "import lib_b\n")
        mods, ly_do = self.ban_kinh("scripts/lib_a.py")
        self.assertIsNone(ly_do)
        self.assertEqual(mods, ["test_lib_b.py"])

    def test_ban_kinh_import_trong_ham_cung_tinh(self):
        ghi(self.goc, "tests/test_sg.py", "import stop_gate\n")
        mods, _ = self.ban_kinh("hooks/scripts/_common.py")
        self.assertEqual(mods, ["test_sg.py"])

    def test_ban_kinh_tap_rong(self):
        self.assertEqual(self.ban_kinh(), ([], None))

    def test_ban_kinh_xuyet_nguoc_va_dot_slash(self):
        ghi(self.goc, "tests/test_lib_a.py", "import lib_a\n")
        mods, ly_do = self.ban_kinh(".\\scripts\\lib_a.py")
        self.assertIsNone(ly_do)
        self.assertIn("test_lib_a.py", mods)


class TienTrinhConTest(RepoTam):
    def test_ban_kinh_tien_trinh_con_run_hook(self):
        """Test chỉ gọi `run_hook("stop_gate.py", …)`, không import, vẫn được chọn."""
        ghi(self.goc, "tests/test_qua_tien_trinh.py",
            "from helper import run_hook\n"
            "def test_x():\n    run_hook(\"stop_gate.py\", {})\n")
        mods, ly_do = self.ban_kinh("hooks/scripts/stop_gate.py")
        self.assertIsNone(ly_do)
        self.assertEqual(mods, ["test_qua_tien_trinh.py"])

    def test_ban_kinh_tien_trinh_con_qua_module_bi_import(self):
        """Đổi `_common.py` → test gọi `stop_gate.py` (import `_common`) cũng được chọn."""
        ghi(self.goc, "tests/test_qua_tien_trinh.py", "run_hook('stop_gate.py', {})\n")
        mods, _ = self.ban_kinh("hooks/scripts/_common.py")
        self.assertEqual(mods, ["test_qua_tien_trinh.py"])


class DuongDanTest(RepoTam):
    def test_ban_kinh_duong_dan_khong_theo_ten_tran(self):
        ghi(self.goc, "tests/test_skill_a.py", "P = 'skills/a/SKILL.md'\n")
        mods, ly_do = self.ban_kinh("skills/b/SKILL.md")
        self.assertIsNone(ly_do)
        self.assertNotIn("test_skill_a.py", mods)

    def test_ban_kinh_duong_dan_khop_dung_file(self):
        ghi(self.goc, "tests/test_skill_a.py", "P = 'skills/a/SKILL.md'\n")
        mods, _ = self.ban_kinh("skills/a/SKILL.md")
        self.assertEqual(mods, ["test_skill_a.py"])

    def test_ban_kinh_duong_dan_tach_thanh_doan(self):
        """`os.path.join(ROOT, "skills", "a", "SKILL.md")` cũng là nhắc đường dẫn."""
        ghi(self.goc, "tests/test_join.py",
            "import os\nP = os.path.join(ROOT, \"skills\", \"a\", \"SKILL.md\")\n")
        self.assertEqual(self.ban_kinh("skills/a/SKILL.md")[0], ["test_join.py"])
        self.assertEqual(self.ban_kinh("skills/b/SKILL.md")[0], [])

    def test_ban_kinh_duong_dan_xuyet_nguoc(self):
        ghi(self.goc, "tests/test_win.py", "P = r'skills\\a\\SKILL.md'\n")
        self.assertEqual(self.ban_kinh("skills/a/SKILL.md")[0], ["test_win.py"])


class QuetThuMucTest(RepoTam):
    def setUp(self):
        super().setUp()
        ghi(self.goc, "tests/test_duyet_skills.py",
            "import os\nfrom helper import ROOT\n"
            "X = os.path.join(ROOT, \"skills\")\n"
            "def test_x():\n"
            "    for r, d, f in os.walk(X):\n"
            "        pass\n")

    def test_ban_kinh_quet_thu_muc_chon_khi_sua_skills(self):
        for f in ("skills/a/SKILL.md", "skills/b/SKILL.md"):
            mods, ly_do = self.ban_kinh(f)
            self.assertIsNone(ly_do)
            self.assertEqual(mods, ["test_duyet_skills.py"], f)

    def test_ban_kinh_quet_thu_muc_khong_chon_khi_sua_hooks(self):
        mods, _ = self.ban_kinh("hooks/scripts/stop_gate.py")
        self.assertNotIn("test_duyet_skills.py", mods)

    def test_ban_kinh_quet_thu_muc_qua_tham_so_ham(self):
        """`def duyet(goc): os.walk(goc)` gọi với `duyet(SKILLS)` — giải qua chỗ gọi hàm."""
        ghi(self.goc, "tests/test_tham_so.py",
            "import os\nSKILLS = os.path.join(ROOT, 'skills')\n"
            "def duyet(goc):\n    return list(os.walk(goc))\n"
            "def test_x():\n    duyet(SKILLS)\n")
        self.assertIn("test_tham_so.py", self.ban_kinh("skills/a/SKILL.md")[0])
        self.assertNotIn("test_tham_so.py", self.ban_kinh("hooks/scripts/stop_gate.py")[0])

    def test_ban_kinh_quet_thu_muc_vong_for_va_path_glob(self):
        ghi(self.goc, "tests/test_vong_for.py",
            "import os\nfor folder in ('hooks', 'scripts'):\n"
            "    for r, _, f in os.walk(os.path.join(ROOT, folder)):\n        pass\n")
        ghi(self.goc, "tests/test_path_glob.py",
            "from pathlib import Path\nD = Path(ROOT) / 'agents'\nN = [p for p in D.glob('*.md')]\n")
        self.assertEqual(self.ban_kinh("hooks/hooks.json")[0], ["test_vong_for.py"])
        self.assertEqual(self.ban_kinh("agents/x.md")[0], ["test_path_glob.py"])


class TronBoKhiTest(RepoTam):
    def test_ban_kinh_tron_bo_khi_file_ngoai_5_thu_muc(self):
        for f in (".gitignore", "README.md", "docs/kien-truc.md"):
            mods, ly_do = self.ban_kinh("scripts/lib_a.py", f)
            self.assertTrue(ly_do, f)
            self.assertEqual(mods, tdq_test.tat_ca_module(self.goc))

    def test_ban_kinh_tron_bo_khi_vuot_nguong(self):
        so = len(tdq_test.tat_ca_module(self.goc))
        for i in range(so * 2):  # 2/3 số module nhắc lib_a → vượt 60%
            ghi(self.goc, f"tests/test_nhac_{i:02d}.py", "import lib_a\n")
        mods, ly_do = self.ban_kinh("scripts/lib_a.py")
        self.assertTrue(ly_do)
        self.assertIn("60", ly_do)

    def test_ban_kinh_tron_bo_khi_khong_doc_duoc_py(self):
        ghi(self.goc, "scripts/hong.py", "def (:\n")
        mods, ly_do = self.ban_kinh("scripts/hong.py")
        self.assertTrue(ly_do)
        self.assertIn("hong.py", ly_do)

    def test_ban_kinh_tron_bo_khi_py_da_xoa(self):
        mods, ly_do = self.ban_kinh("scripts/khong_co.py")
        self.assertTrue(ly_do)

    def test_ban_kinh_duoi_nguong_khong_tron_bo(self):
        ghi(self.goc, "tests/test_lib_a.py", "import lib_a\n")
        self.assertIsNone(self.ban_kinh("scripts/lib_a.py")[1])


class CaDaDoTest(unittest.TestCase):
    """Repo THẬT — các ca đã đo ở brief (nguyên mẫu: 2 · 11 · 7 · 96 module)."""

    @classmethod
    def setUpClass(cls):
        cls.tong = len(tdq_test.tat_ca_module(ROOT))

    def test_ban_kinh_ca_da_do_ask_gate_nho(self):
        mods, ly_do = tdq_test.ban_kinh(["hooks/scripts/ask_gate.py"], ROOT)
        self.assertIsNone(ly_do)
        self.assertIn("test_ask_gate.py", mods)
        # Nguyên mẫu đo 2 (chỉ dò tên). Bản 1.1 dò thêm test QUÉT `hooks/` (2026-10-05 đo:
        # 6 module — utf8_io, ma_hoa_subprocess, compliance_protocol, skill_shape, lumenignore,
        # build_portable — đọc/duyệt mọi file dưới `hooks/`, sửa ask_gate.py làm đỏ được chúng).
        # Nên: phần ngoài các test nhắc tên ask_gate phải đúng là test quét `hooks/`.
        nhac = tdq_test.chon_theo_ten_module({"ask_gate"}, tdq_test._nguon_test(ROOT))
        for ten in set(mods) - nhac:
            with open(os.path.join(ROOT, "tests", ten), encoding="utf-8") as f:
                self.assertIn("hooks", tdq_test.thu_muc_bi_quet(f.read()), ten)
        self.assertLessEqual(len(nhac), 3, sorted(nhac))
        self.assertLessEqual(len(mods), 10, mods)

    def test_ban_kinh_ca_da_do_stop_gate(self):
        mods, ly_do = tdq_test.ban_kinh(["hooks/scripts/stop_gate.py"], ROOT)
        self.assertIsNone(ly_do)
        self.assertIn("test_stop_gate.py", mods)
        self.assertLessEqual(len(mods), 20, mods)

    def test_ban_kinh_ca_da_do_qc_md(self):
        duong = "skills/tdq-build/references/qc.md"
        mods, ly_do = tdq_test.ban_kinh([duong], ROOT)
        self.assertIsNone(ly_do)
        self.assertIn("test_luat_dung.py", mods)  # duyệt mọi file dưới skills/
        nhac = []
        for ten in tdq_test.tat_ca_module(ROOT):
            with open(os.path.join(ROOT, "tests", ten), encoding="utf-8") as f:
                if duong in f.read():
                    nhac.append(ten)
        self.assertTrue(nhac)
        for ten in nhac:
            self.assertIn(ten, mods)
        self.assertLess(len(mods), tdq_test.NGUONG_TRON_BO * self.tong, mods)

    def test_ban_kinh_ca_da_do_tdq_state_tron_bo(self):
        mods, ly_do = tdq_test.ban_kinh(["scripts/tdq_state.py"], ROOT)
        self.assertTrue(ly_do)
        self.assertEqual(len(mods), self.tong)


if __name__ == "__main__":
    unittest.main()
