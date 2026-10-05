"""Test `scripts/tdq_test.py` — bán kính ảnh hưởng của một tập file sửa (T1.1, 2026-10-03).

Nhóm theo DoD (tên nhóm nằm trong tên method để `-k` chọn được):
- `ca_da_do`: các ca đã đo ở brief, chạy trên repo THẬT;
- `tien_trinh_con`: test chỉ gọi hook qua tiến trình con vẫn được chọn;
- `duong_dan`: file luật dò theo đường dẫn tương đối, không theo tên trần;
- `quet_thu_muc`: test quét thư mục cha của file sửa được chọn (dò bằng AST);
- `tron_bo_khi`: các lúc phải rơi về trọn bộ;
- `vung_cham` (T1.2): lệnh `vung-cham` trên repo tạm — chọn, chạy một tiến trình, ghi sổ, log;
- `so` (T1.3): lệnh `tron-bo` ghi sổ + dòng bỏ sót, lệnh `so` đếm theo request, `dem()` thuần.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
        # T5.6 (lệch spec #1, Q4): chỉ file MÃ / loại không rõ ngoài 5 thư mục mới rơi về trọn
        # bộ; file dữ liệu (.gitignore, README.md, docs/*.md) giờ chỉ dò theo đường dẫn.
        for f in ("setup.py", "tools/build.sh", "Makefile", "docs/x.cfg"):
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


# ---------- T1.2: lệnh `vung-cham` ----------

SCRIPT = os.path.join(ROOT, "scripts", "tdq_test.py")
TEST_DAT = "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"
TEST_TRUOT = ("import unittest\nclass T(unittest.TestCase):\n"
              "    def test_hong(self):\n        self.fail('co y')\n")
SO_DEM = 6


def lam_repo_vung_cham(goc, state=None):
    """Repo tạm nhỏ: `test_a` đạt, `test_b` trượt, `test_c` đạt, 6 module đệm (đạt)."""
    ghi(goc, "scripts/lib_a.py", "X = 1\n")
    ghi(goc, "tests/test_a.py", TEST_DAT)
    ghi(goc, "tests/test_b.py", TEST_TRUOT)
    ghi(goc, "tests/test_c.py", TEST_DAT)
    for i in range(SO_DEM):
        ghi(goc, f"tests/test_dem_{i:02d}.py", TEST_DAT)
    if state is None:
        state = '{"active_request": "req-1", "phase": "implement", "nhanh_goc": "main"}\n'
    ghi(goc, "docs/tdq/state.json", state)


def chay_cli(goc, *args, log=True):
    env = dict(os.environ)
    env["TDQ_LOG"] = "1" if log else "0"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, SCRIPT, "vung-cham", "--repo", goc, *args],
                          capture_output=True, text=True, encoding="utf-8", env=env,
                          timeout=120)


def doc_so(goc):
    duong = os.path.join(goc, "docs", "tdq", ".tdq-test.jsonl")
    with open(duong, encoding="utf-8") as f:
        return [json.loads(d) for d in f if d.strip().startswith("{")]


DONG_LOG = re.compile(r"^\[\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d", re.M)


class VungCham(unittest.TestCase):
    def setUp(self):
        self.goc = tempfile.mkdtemp(prefix="tdq-test-vung-cham-")
        self.addCleanup(shutil.rmtree, self.goc, ignore_errors=True)
        lam_repo_vung_cham(self.goc)

    def test_vung_cham_files_chi_chay_module_chon_dat(self):
        p = chay_cli(self.goc, "--files", "tests/test_a.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("Ran 1 test", p.stderr)
        self.assertIn("1/9", p.stdout)

    def test_vung_cham_files_module_truot_thi_exit_1(self):
        p = chay_cli(self.goc, "--files", "tests/test_a.py", "tests/test_b.py")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("Ran 2 tests", p.stderr)

    def test_vung_cham_ly_do_tron_bo_chay_het(self):
        p = chay_cli(self.goc, "--files", "tools/build.sh")  # T5.6: mã ngoài 5 thư mục
        self.assertEqual(p.returncode, 1)  # test_b trượt nằm trong trọn bộ
        self.assertIn("Ran 9 tests", p.stderr)
        self.assertIn("full suite", p.stdout)
        dong = doc_so(self.goc)[-1]
        self.assertTrue(dong["fallback"])
        self.assertEqual(len(dong["modules"]), 9)

    def test_vung_cham_ghi_so_du_truong(self):
        p = chay_cli(self.goc, "--files", "tests\\test_a.py", "tests/test_a.py")
        self.assertEqual(p.returncode, 0, p.stderr)
        rows = doc_so(self.goc)
        self.assertEqual(len(rows), 1)
        dong = rows[0]
        self.assertEqual(dong["kind"], "vung-cham")
        self.assertEqual(dong["request"], "req-1")
        self.assertEqual(dong["phase"], "implement")
        self.assertEqual(dong["files"], ["tests/test_a.py"])
        self.assertEqual(dong["modules"], ["test_a.py"])
        self.assertIsNone(dong["fallback"])
        self.assertIs(dong["ok"], True)
        self.assertIsInstance(dong["seconds"], float)
        self.assertRegex(dong["ts"], r"^\d{4}-\d\d-\d\dT")

    def test_vung_cham_so_hong_va_state_hong_van_chay(self):
        ghi(self.goc, "docs/tdq/.tdq-test.jsonl", "khong phai json\n{\"cut\n")
        ghi(self.goc, "docs/tdq/state.json", "{hong")
        p = chay_cli(self.goc, "--files", "tests/test_a.py")
        self.assertEqual(p.returncode, 0, p.stderr)
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}):
            rows = tdq_test._doc_so(self.goc)
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["request"])
        self.assertEqual(rows[0]["modules"], ["test_a.py"])

    def test_vung_cham_doc_so_khong_co_file(self):
        self.assertEqual(tdq_test._doc_so(self.goc), [])

    def test_vung_cham_log_iso_va_tdq_log_0_tat(self):
        bat = chay_cli(self.goc, "--files", "tests/test_a.py")
        self.assertTrue(DONG_LOG.search(bat.stderr), bat.stderr)
        self.assertIn("vung-cham", bat.stderr)
        tat = chay_cli(self.goc, "--files", "tests/test_a.py", log=False)
        self.assertEqual(tat.returncode, 0)
        self.assertIsNone(DONG_LOG.search(tat.stderr), tat.stderr)

    def test_vung_cham_tap_rong_khong_chay_gi(self):
        p = chay_cli(self.goc, "--files")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(doc_so(self.goc)[-1]["modules"], [])

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_vung_cham_lay_file_tu_git(self):
        g = self.goc

        def git(*args):
            subprocess.run(["git", "-C", g, *args], check=True, capture_output=True)

        ghi(g, ".gitignore", "__pycache__/\ndocs/tdq/state.json\n")
        git("init", "-q")
        git("symbolic-ref", "HEAD", "refs/heads/main")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "t")
        git("config", "core.autocrlf", "false")
        git("add", "-A")
        git("commit", "-q", "-m", "goc")
        git("checkout", "-q", "-b", "nhanh")
        ghi(g, "tests/test_a.py", TEST_DAT + "# doi\n")           # commit trên nhánh
        git("commit", "-q", "-am", "doi a")
        ghi(g, "tests/test_c.py", TEST_DAT + "# staged\n")        # staged
        git("add", "tests/test_c.py")
        ghi(g, "tests/test_dem_00.py", TEST_DAT + "# unstaged\n")  # chưa stage
        ghi(g, "tests/test_d.py", TEST_DAT)                        # untracked
        p = chay_cli(g)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        dong = doc_so(g)[-1]
        self.assertEqual(dong["files"], ["tests/test_a.py", "tests/test_c.py",
                                         "tests/test_d.py", "tests/test_dem_00.py"])
        self.assertEqual(dong["modules"], ["test_a.py", "test_c.py", "test_d.py",
                                           "test_dem_00.py"])
        self.assertIsNone(dong["fallback"])
        # Sổ của chính lệnh (untracked) không được tự kéo vào lần chạy sau.
        p2 = chay_cli(g)
        self.assertNotIn("docs/tdq/.tdq-test.jsonl", doc_so(g)[-1]["files"])
        self.assertEqual(p2.returncode, 0)

    def test_vung_cham_git_hong_thi_tron_bo(self):
        ghi(self.goc, "docs/tdq/state.json", '{"nhanh_goc": "khong-ton-tai"}')
        p = chay_cli(self.goc)  # không phải repo git
        self.assertEqual(p.returncode, 1)
        dong = doc_so(self.goc)[-1]
        self.assertIn("git", dong["fallback"])
        self.assertEqual(len(dong["modules"]), 9)


# ---------- T5.6: sửa 2 lỗi từ soát lỗi T5.3 ----------

class SuaLoi(RepoTam):
    """Lỗi 1: file DỮ LIỆU ngoài 5 thư mục không còn ép trọn bộ (lệch spec #1, Q4).
    Lỗi 2: `.py` không phải test trong `tests/` được dò import ngược như module."""

    def test_sua_loi_du_lieu_docs_chi_chon_test_nhac_duong_dan(self):
        ghi(self.goc, "docs/tdq/plan/x.md", "# plan\n")
        ghi(self.goc, "tests/test_doc_plan.py", "P = 'docs/tdq/plan/x.md'\n")
        ghi(self.goc, "tests/test_ten_tran.py", "P = 'x.md'\n")  # tên trần không tính
        mods, ly_do = self.ban_kinh("docs/tdq/plan/x.md")
        self.assertIsNone(ly_do)
        self.assertEqual(mods, ["test_doc_plan.py"])

    def test_sua_loi_du_lieu_khong_ai_nhac_khong_chon_khong_tron_bo(self):
        for f in ("docs/tdq/STATE.md", "docs/tdq/timing.jsonl", ".gitignore", "README.md",
                  "LICENSE", ".gitattributes", "docs/a.yaml", "docs/hinh.PNG"):
            self.assertEqual(self.ban_kinh(f), ([], None), f)

    def test_sua_loi_du_lieu_cung_ma_trong_5_thu_muc(self):
        ghi(self.goc, "tests/test_lib_a.py", "import lib_a\n")
        mods, ly_do = self.ban_kinh("scripts/lib_a.py", "docs/tdq/plan/x.md", ".gitignore")
        self.assertIsNone(ly_do)
        self.assertEqual(mods, ["test_lib_a.py"])

    def test_sua_loi_py_ngoai_5_thu_muc_tron_bo(self):
        for f in ("setup.py", "docs/gen.py", "tools/run.ps1", "build.sh", "x.js"):
            mods, ly_do = self.ban_kinh(f)
            self.assertTrue(ly_do, f)
            self.assertIn(f, ly_do)
            self.assertEqual(mods, tdq_test.tat_ca_module(self.goc))

    def test_sua_loi_duoi_khong_ro_tron_bo(self):
        for f in ("docs/x.cfg", "Makefile", "data.bin"):
            mods, ly_do = self.ban_kinh(f)
            self.assertTrue(ly_do, f)
            self.assertEqual(mods, tdq_test.tat_ca_module(self.goc))

    def test_sua_loi_helper_chon_moi_test_import_no(self):
        ghi(self.goc, "tests/helper2.py", "from helper import ROOT\n")
        ghi(self.goc, "tests/test_h1.py", "import helper\n")
        ghi(self.goc, "tests/test_h2.py", "def f():\n    from helper import ROOT\n")
        ghi(self.goc, "tests/test_h3.py", "import helper2\n")  # qua helper khác
        ghi(self.goc, "tests/test_khong.py", "X = 'helper'\nimport helperx\n")
        mods, ly_do = self.ban_kinh("tests/helper.py")
        self.assertIsNone(ly_do)
        self.assertEqual(mods, ["test_h1.py", "test_h2.py", "test_h3.py"])
        # Sửa helper2 → chỉ test import helper2.
        self.assertEqual(self.ban_kinh("tests/helper2.py")[0], ["test_h3.py"])

    def test_sua_loi_helper_vuot_nguong_thi_tron_bo(self):
        for i in range(self.SO_TEST_DEM):
            ghi(self.goc, f"tests/test_dem_{i:02d}.py", "import unittest\nimport helper\n")
        mods, ly_do = self.ban_kinh("tests/helper.py")
        self.assertTrue(ly_do)
        self.assertIn("60", ly_do)

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_sua_loi_vung_cham_git_doi_docs_va_script_la_khong_tron_bo(self):
        g = tempfile.mkdtemp(prefix="tdq-test-sua-loi-")
        self.addCleanup(shutil.rmtree, g, ignore_errors=True)
        lam_repo_vung_cham(g)
        ghi(g, "tests/test_a.py", TEST_DAT + "# dung lib_a\n")

        def git(*args):
            subprocess.run(["git", "-C", g, *args], check=True, capture_output=True)

        ghi(g, ".gitignore", "__pycache__/\ndocs/tdq/state.json\n")
        git("init", "-q")
        git("symbolic-ref", "HEAD", "refs/heads/main")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "t")
        git("config", "core.autocrlf", "false")
        git("add", "-A")
        git("commit", "-q", "-m", "goc")
        git("checkout", "-q", "-b", "nhanh")
        ghi(g, "docs/tdq/plan.md", "# plan\n")                  # commit trên nhánh
        ghi(g, ".gitignore", "__pycache__/\ndocs/tdq/state.json\n*.tmp\n")
        git("add", "-A")
        git("commit", "-q", "-m", "plan")
        ghi(g, "scripts/lib_a.py", "X = 2\n")                    # chưa stage, script lá
        ghi(g, "docs/tdq/STATE.md", "# state\n")                 # untracked
        p = chay_cli(g)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        dong = doc_so(g)[-1]
        self.assertIn("docs/tdq/plan.md", dong["files"])
        self.assertIn(".gitignore", dong["files"])
        self.assertIsNone(dong["fallback"])
        self.assertEqual(dong["modules"], ["test_a.py"])


# ---------- T1.3: lệnh `tron-bo` + `so` ----------

def chay_lenh(goc, lenh, *args, log=True):
    env = dict(os.environ)
    env["TDQ_LOG"] = "1" if log else "0"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, SCRIPT, lenh, "--repo", goc, *args],
                          capture_output=True, text=True, encoding="utf-8", env=env,
                          timeout=120)


def dong_vung_cham(request, modules, fallback=None):
    return {"ts": "2026-10-05T10:00:00+07:00", "kind": "vung-cham", "request": request,
            "phase": "implement", "files": [], "modules": modules, "fallback": fallback,
            "ok": True, "seconds": 0.1}


def ghi_so_tay(goc, *rows):
    ghi(goc, "docs/tdq/.tdq-test.jsonl", "".join(json.dumps(r) + "\n" for r in rows))


class So(unittest.TestCase):
    """`tron-bo` ghi sổ + dòng bỏ sót; `so` đếm theo request (spec §2 hàng 3, 4b; Q6, Q6b)."""

    def setUp(self):
        self.goc = tempfile.mkdtemp(prefix="tdq-test-so-")
        self.addCleanup(shutil.rmtree, self.goc, ignore_errors=True)
        lam_repo_vung_cham(self.goc)

    def test_so_tron_bo_ghi_dong_va_module_do(self):
        p = chay_lenh(self.goc, "tron-bo")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("Ran 9 tests", p.stderr)
        rows = doc_so(self.goc)
        tron = [r for r in rows if r["kind"] == "tron-bo"]
        self.assertEqual(len(tron), 1)
        dong = tron[0]
        self.assertEqual(dong["request"], "req-1")
        self.assertEqual(dong["phase"], "implement")
        self.assertIs(dong["ok"], False)
        self.assertEqual(dong["failed_modules"], ["test_b.py"])
        self.assertIsInstance(dong["seconds"], float)
        self.assertRegex(dong["ts"], r"^\d{4}-\d\d-\d\dT")

    def test_so_tron_bo_xanh_exit_0(self):
        ghi(self.goc, "tests/test_b.py", TEST_DAT)
        p = chay_lenh(self.goc, "tron-bo")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        rows = doc_so(self.goc)
        self.assertEqual([r["kind"] for r in rows], ["tron-bo"])
        self.assertEqual(rows[0]["failed_modules"], [])

    def test_so_tron_bo_module_import_hong_tinh_la_do(self):
        ghi(self.goc, "tests/test_hong.py", "import khong_ton_tai_xyz\n")
        chay_lenh(self.goc, "tron-bo")
        dong = [r for r in doc_so(self.goc) if r["kind"] == "tron-bo"][-1]
        self.assertEqual(dong["failed_modules"], ["test_b.py", "test_hong.py"])

    def test_so_bo_sot_khi_module_do_chua_tung_duoc_chon(self):
        ghi_so_tay(self.goc, dong_vung_cham("req-1", ["test_a.py"]))
        p = chay_lenh(self.goc, "tron-bo")
        bo_sot = [r for r in doc_so(self.goc) if r["kind"] == "bo-sot"]
        self.assertEqual(len(bo_sot), 1)
        self.assertEqual(bo_sot[0]["module"], "test_b.py")
        self.assertEqual(bo_sot[0]["request"], "req-1")
        self.assertIn("test_b.py", p.stdout)
        self.assertIn("missed", p.stdout)

    def test_so_khong_bo_sot_khi_da_chon_truoc(self):
        ghi_so_tay(self.goc, dong_vung_cham("req-1", ["test_a.py", "test_b.py"]))
        chay_lenh(self.goc, "tron-bo")
        self.assertEqual([r for r in doc_so(self.goc) if r["kind"] == "bo-sot"], [])

    def test_so_khong_bo_sot_khi_vung_cham_da_roi_ve_tron_bo(self):
        ghi_so_tay(self.goc, dong_vung_cham("req-1", ["test_a.py"], fallback="outside"))
        chay_lenh(self.goc, "tron-bo")
        self.assertEqual([r for r in doc_so(self.goc) if r["kind"] == "bo-sot"], [])

    def test_so_request_khac_khong_tinh(self):
        ghi_so_tay(self.goc, dong_vung_cham("req-0", ["test_b.py"]),
                   dong_vung_cham("req-0", [], fallback="outside"))
        chay_lenh(self.goc, "tron-bo")
        bo_sot = [r for r in doc_so(self.goc) if r["kind"] == "bo-sot"]
        self.assertEqual([r["module"] for r in bo_sot], ["test_b.py"])

    def test_so_json_dem_va_ngan_sach(self):
        p = chay_lenh(self.goc, "so", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), {"request": "req-1", "tron_bo": 0, "bo_sot": 0,
                                                "modules_bo_sot": [], "ngan_sach": 2})
        chay_lenh(self.goc, "tron-bo")  # đỏ → có vòng sửa QC → ngân sách 3
        chay_lenh(self.goc, "tron-bo")
        d = json.loads(chay_lenh(self.goc, "so", "--json").stdout)
        self.assertEqual(d["tron_bo"], 2)
        self.assertEqual(d["bo_sot"], 2)
        self.assertEqual(d["modules_bo_sot"], ["test_b.py"])
        self.assertEqual(d["ngan_sach"], 3)
        chu = chay_lenh(self.goc, "so")
        self.assertEqual(chu.returncode, 0)
        self.assertIn("req-1", chu.stdout)
        self.assertIn("test_b.py", chu.stdout)

    def test_so_dem_thuan(self):
        rows = [
            {"kind": "tron-bo", "request": "r", "ok": True},
            {"kind": "bo-sot", "request": "r", "module": "test_x.py"},
            {"kind": "bo-sot", "request": "r", "module": "test_x.py"},
            {"kind": "bo-sot", "request": "khac", "module": "test_y.py"},
            {"kind": "tron-bo", "request": "khac", "ok": False},
            {"kind": "vung-cham", "request": "r", "modules": []},
        ]
        truoc = json.dumps(rows)
        d = tdq_test.dem(rows, "r")
        self.assertEqual(d, {"request": "r", "tron_bo": 1, "bo_sot": 2,
                             "modules_bo_sot": ["test_x.py"], "ngan_sach": 2})
        self.assertEqual(json.dumps(rows), truoc)  # không đổi đầu vào
        self.assertEqual(tdq_test.dem(rows, "khac")["ngan_sach"], 3)
        self.assertEqual(tdq_test.dem([], None)["tron_bo"], 0)

    def test_so_hong_va_state_hong_coi_la_rong(self):
        ghi(self.goc, "docs/tdq/.tdq-test.jsonl", "hong\n")
        ghi(self.goc, "docs/tdq/state.json", "{hong")
        p = chay_lenh(self.goc, "so", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["tron_bo"], 0)
        self.assertIn("warning", p.stderr)

    def test_so_log_iso_va_tdq_log_0_tat(self):
        bat = chay_lenh(self.goc, "so")
        self.assertTrue(DONG_LOG.search(bat.stderr), bat.stderr)
        tat = chay_lenh(self.goc, "tron-bo", log=False)
        self.assertIsNone(DONG_LOG.search(tat.stderr), tat.stderr)
        tat = chay_lenh(self.goc, "so", log=False)
        self.assertIsNone(DONG_LOG.search(tat.stderr), tat.stderr)

    def test_so_gitignore_co_so_test(self):
        with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as f:
            self.assertIn("docs/tdq/.tdq-test.jsonl", f.read().splitlines())


if __name__ == "__main__":
    unittest.main()
