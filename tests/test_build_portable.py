"""Test cho scripts/build_portable.py.

2026-09-21: bản này bỏ chín lớp test cùng lúc với hai hàm chúng kiểm — `sinh_ban_claude` và
`sinh_ban_codex`. Hai bundle đó không còn tồn tại: Claude Code đọc repo qua
`.claude-plugin/marketplace.json`, Codex đọc qua `.agents/plugins/marketplace.json`, cả hai trỏ
thẳng vào `skills/` dùng chung thay vì một bản sao được dựng ra. Phần còn lại của file này vẫn
áp dụng: đổi biến plugin, copy lọc, manifest, và bản agy — thứ duy nhất còn sinh ra file thật.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

import helper  # noqa: F401  — nạp sys.path cho scripts/
import build_portable
import tdq_checkportable  # chủ của phép kiểm dấu ~

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "build_portable.py")


def chay(*args, env=None):
    """Gọi build_portable.py như tiến trình con — kiểm cả CLI lẫn log ra stderr."""
    proc = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True, encoding="utf-8", text=True, timeout=120,
        env=dict(os.environ, **(env or {})),
    )
    return proc.returncode, proc.stdout, proc.stderr


class TempDest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dest = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()


class TestCLI(TempDest):
    def test_help_co_du_ba_co(self):
        ma, out, _ = chay("--help")
        self.assertEqual(ma, 0)
        for co in ("--dest", "--sinh-agy", "--sinh-hook-claude"):
            self.assertIn(co, out)
        # 2026-09-21: `--only` từng được nhận rồi lờ đi — cờ không làm gì còn tệ hơn không có cờ.
        self.assertNotIn("--only", out)
        self.assertNotIn("two portable bundles", out)

    def test_khong_co_hanh_dong_thi_thoat_2_va_khong_ghi_gi(self):
        """Không cờ nào từng mặc định dựng `antigravity_portable/` NGAY TRONG repo — tức mọc lại
        đúng bundle vừa xoá. Giờ phải chọn hành động rõ ràng."""
        truoc = sorted(os.listdir(ROOT))
        ma, _, err = chay()
        self.assertEqual(ma, 2)
        self.assertIn("--sinh-agy", err)
        self.assertEqual(sorted(os.listdir(ROOT)), truoc)

    def test_dest_la_chinh_repo_bi_tu_choi(self):
        ma, _, err = chay("--dest", ROOT)
        self.assertEqual(ma, 2)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "antigravity_portable")))
        self.assertIn("repo", err)

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        _, _, bat = chay("--dest", self.dest)
        self.assertTrue(bat.strip(), "log mặc định phải BẬT, ghi ra stderr")
        with tempfile.TemporaryDirectory() as d2:
            _, _, tat = chay("--dest", d2, env={"TDQ_LOG": "0"})
        self.assertEqual(tat.strip(), "", "TDQ_LOG=0 phải im hoàn toàn")


class TestManifest(TempDest):
    def test_manifest_du_5_khoi(self):
        os.makedirs(os.path.join(self.dest, "sub"), exist_ok=True)
        with open(os.path.join(self.dest, "sub", "a.txt"), "w", encoding="utf-8") as f:
            f.write("xin chao")
        man = build_portable.sinh_manifest(self.dest)
        for khoi in ("files", "version", "python_min", "external_commands", "mcp_servers"):
            self.assertIn(khoi, man, f"manifest thiếu khối {khoi}")
        self.assertIn("sub/a.txt", man["files"], "đường dẫn trong manifest phải dùng dấu /")

    def test_sha256_khop_file_that(self):
        noi_dung = "nội dung kiểm tra"
        with open(os.path.join(self.dest, "b.txt"), "w", encoding="utf-8") as f:
            f.write(noi_dung)
        man = build_portable.sinh_manifest(self.dest)
        cho_doi = hashlib.sha256(noi_dung.encode("utf-8")).hexdigest()
        self.assertEqual(man["files"]["b.txt"], cho_doi)

    def test_manifest_khong_tu_liet_ke_chinh_no(self):
        with open(os.path.join(self.dest, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({}, f)
        man = build_portable.sinh_manifest(self.dest)
        self.assertNotIn("manifest.json", man["files"],
                         "manifest tự liệt kê chính nó thì sha256 không bao giờ khớp")


class TestDoiBien(unittest.TestCase):
    def test_doi_bien_dem_dung_so_lan(self):
        goc = 'a ${CLAUDE_PLUGIN_ROOT}/x và $CLAUDE_PLUGIN_ROOT/y'
        moi, so_lan = build_portable.doi_bien_plugin_root(goc)
        self.assertEqual(so_lan, 2, "phải đếm cả dạng ngoặc nhọn lẫn dạng trần")
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", moi)
        self.assertEqual(moi.count("${CLAUDE_PROJECT_DIR}"), 2)

    def test_khong_co_bien_thi_khong_doi_gi(self):
        moi, so_lan = build_portable.doi_bien_plugin_root("khong co gi")
        self.assertEqual(so_lan, 0)
        self.assertEqual(moi, "khong co gi")


class TestCopyLoc(TempDest):
    def _dung_nguon_gia(self):
        """Dựng cây nguồn giả có sẵn đúng loại rác cần bị loại."""
        nguon = os.path.join(self.dest, "nguon")
        for duong in ("skills/tdq-x", "docs/tdq", ".git", "graphify-out", "__pycache__"):
            os.makedirs(os.path.join(nguon, duong), exist_ok=True)
        ghi = {
            "skills/tdq-x/SKILL.md": "noi dung skill",
            "docs/tdq/state.json": "{}",
            ".git/config": "x",
            "graphify-out/g.json": "{}",
            "__pycache__/a.pyc": "x",
        }
        for duong, noi in ghi.items():
            with open(os.path.join(nguon, duong), "w", encoding="utf-8") as f:
                f.write(noi)
        return nguon

    def test_copy_khong_mang_rac(self):
        nguon = self._dung_nguon_gia()
        dich = os.path.join(self.dest, "dich")
        build_portable.copy_loc(nguon, dich)
        self.assertTrue(os.path.exists(os.path.join(dich, "skills/tdq-x/SKILL.md")))
        for rac in ("docs/tdq/state.json", ".git/config", "graphify-out/g.json",
                    "__pycache__/a.pyc"):
            self.assertFalse(os.path.exists(os.path.join(dich, rac)),
                             f"bản sinh không được mang theo {rac}")

    def test_bo_do_khong_di_theo_ban_sinh(self):
        """`tdq_eval.py` là bộ đo của repo nguồn, không phải phần workflow đem đi.

        Nó cố ý ĐẶT biến `CLAUDE_PLUGIN_ROOT` cho tiến trình con của phiên đo, nên copy kèm
        rewrite sẽ đổi đúng cái hằng số nó cần giữ — y hệt lý do `build_portable.py` bị loại.
        """
        nguon = os.path.join(self.dest, "n3", "scripts")
        os.makedirs(nguon, exist_ok=True)
        for ten in ("tdq_eval.py", "tdq_state.py"):
            with open(os.path.join(nguon, ten), "w", encoding="utf-8") as f:
                f.write("x = 1\n")
        dich = os.path.join(self.dest, "d3")
        build_portable.copy_loc(os.path.join(self.dest, "n3"), dich)
        self.assertTrue(os.path.exists(os.path.join(dich, "scripts", "tdq_state.py")))
        self.assertFalse(os.path.exists(os.path.join(dich, "scripts", "tdq_eval.py")),
                         "bộ đo không được lọt vào bản portable")

    def test_giu_quyen_thuc_thi(self):
        nguon = os.path.join(self.dest, "n2")
        os.makedirs(nguon, exist_ok=True)
        kich_ban = os.path.join(nguon, "run.sh")
        with open(kich_ban, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
        os.chmod(kich_ban, 0o755)
        dich = os.path.join(self.dest, "d2")
        build_portable.copy_loc(nguon, dich)
        self.assertTrue(os.access(os.path.join(dich, "run.sh"), os.X_OK))


class TestBanAntigravity(TempDest):
    """Bản antigravity: user-level/global cho agy, đối xứng `TestCodexNativeLayers`.

    Khác codex (project-level, cwd = gốc project): agy cài ở path CỐ ĐỊNH dưới $HOME, nên
    mọi `command`/tham chiếu path trong bundle phải là absolute path cố định (`GOC_AGY`),
    không phải relative "." như codex.
    """

    def setUp(self):
        super().setUp()
        self.goc = build_portable.sinh_ban_antigravity(ROOT, self.dest)

    def test_du_skill_theo_dung_thu_tu_va_frontmatter_hop_le(self):
        for ten in build_portable.THU_TU_SKILL:
            duong = os.path.join(self.goc, "skills", ten, "SKILL.md")
            self.assertTrue(os.path.isfile(duong), f"thiếu {ten}/SKILL.md")
            # Đọc tại chỗ thay vì gọi `doc_frontmatter`: helper đó sinh ra để phục vụ
            # adapter của bundle codex, mà bundle đó đã bỏ. Một helper chỉ còn test gọi là
            # code chết đội lốt code sống.
            noi_dung = build_portable._doc_text(duong)
            khoi = noi_dung.split("---", 2)
            self.assertEqual(len(khoi), 3, f"{ten}/SKILL.md thiếu khối frontmatter")
            for khoa in ("name:", "description:"):
                self.assertIn(khoa, khoi[1], f"{ten}/SKILL.md thiếu frontmatter {khoa}")

    def test_skill_giu_duoc_references_di_kem(self):
        duong = os.path.join(self.goc, "skills", "tdq-conventions", "references")
        self.assertTrue(os.path.isdir(duong))
        self.assertTrue(os.listdir(duong))

    def test_khong_con_bien_plugin_hay_duong_dan_tuong_doi_tran(self):
        tien_to = build_portable.GOC_AGY + "/"
        for thu_muc, thu_muc_con, files in os.walk(os.path.join(self.goc, "skills")):
            thu_muc_con[:] = [d for d in thu_muc_con if d != "__pycache__"]
            for ten in files:
                if not ten.endswith(".md"):
                    continue
                duong = os.path.join(thu_muc, ten)
                noi = build_portable._doc_text(duong) or ""
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", noi, f"còn biến plugin ở {duong}")
                for tu in ("scripts/", "hooks/"):
                    for m in re.finditer(re.escape(tu), noi):
                        truoc = noi[max(0, m.start() - len(tien_to)):m.start()]
                        self.assertEqual(truoc, tien_to,
                                         f"{duong}: '{tu}' trần chưa được thay absolute path")

    def test_moi_hook_khai_trong_hooks_json_deu_co_file_that(self):
        """Bản dựng từng khai một hook mà không chép file của nó — PreToolUse chạy vào hư vô.

        Nên phép kiểm này đọc đúng `hooks.json` ĐÃ SINH RA, lấy tên file từ đó, chứ không chép
        tay một danh sách thứ ba để rồi lệch tiếp.
        """
        with open(os.path.join(self.goc, "hooks.json"), encoding="utf-8") as f:
            du_lieu = json.load(f)
        ten_file = set()
        for muc in du_lieu["hooks"].values():
            for matcher in muc:
                for hook in matcher.get("hooks", []):
                    ten_file.add(os.path.basename(hook["command"].split()[-1].strip("\"")))
        self.assertTrue(ten_file, "hooks.json không khai hook nào")
        for ten in sorted(ten_file):
            duong = os.path.join(self.goc, "hooks", "scripts", ten)
            self.assertTrue(os.path.isfile(duong), f"hooks.json khai {ten} mà bản dựng không chép")
            self.assertTrue(os.access(duong, os.X_OK), f"{ten} phải có quyền thực thi")

    def test_phu_thuoc_chung_cua_hook_cung_duoc_chep(self):
        """`read_gate.py` import `_common.py`; thiếu nó thì hook có mặt vẫn chết lúc nạp."""
        duong = os.path.join(self.goc, "hooks", "scripts", "_common.py")
        self.assertTrue(os.path.isfile(duong), "bản agy thiếu hooks/scripts/_common.py")

    def test_hooks_json_dung_2_event_va_command_tro_path_co_dinh(self):
        duong = os.path.join(self.goc, "hooks.json")
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
        su_kien = du_lieu["hooks"]
        self.assertEqual(sorted(su_kien), ["PreToolUse", "Stop"])
        for nhom_list in su_kien.values():
            for nhom in nhom_list:
                for hook in nhom["hooks"]:
                    lenh = hook["command"]
                    self.assertNotIn("${", lenh, "command không được còn biến chưa thay")
                    self.assertFalse(tdq_checkportable.con_dau_nga_chua_bung(lenh),
                                     "dấu ~ chưa bung → shell không bung trong nháy → exit 127")
                    self.assertIn(build_portable.goc_agy_tuyet_doi(), lenh,
                                  "command phải là absolute path đã bung dưới gốc plugin")

    def test_khong_ship_settings_json(self):
        """Bundle KHÔNG được mang `settings.json`: file thật của agy giữ model/colorScheme/
        trustedWorkspaces và không có mục permissions — copy đè là xoá cấu hình người dùng mà
        không thêm được hàng rào nào. Hook mới là hàng rào."""
        self.assertFalse(os.path.exists(os.path.join(self.goc, "config", "settings.json")))
        self.assertFalse(os.path.exists(os.path.join(self.goc, "settings.json")))

    def test_plugin_json_dung_khuon_agy(self):
        """`plugin.json` ở GỐC là thứ duy nhất khiến agy 1.1.11 coi thư mục này là plugin."""
        duong = os.path.join(self.goc, "plugin.json")
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
        self.assertEqual(du_lieu["name"], build_portable.TEN_PLUGIN_AGY)
        self.assertTrue(du_lieu["description"])

    def test_mcp_config_du_2_server_va_khong_lo_khoa(self):
        duong = os.path.join(self.goc, "mcp_config.json")
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
        self.assertEqual(sorted(du_lieu["mcpServers"]), sorted(build_portable.MCP_SERVERS))
        noi_dung = build_portable._doc_text(duong)
        for ten_bien, gia_tri in os.environ.items():
            if any(d in ten_bien for d in ("KEY", "TOKEN", "SECRET")) and len(gia_tri) > 8:
                self.assertNotIn(gia_tri, noi_dung, f"mcp_config.json lộ giá trị của {ten_bien}")

    def test_readme_du_3_cum_bat_buoc(self):
        noi_dung = build_portable._doc_text(os.path.join(self.goc, "README.md"))
        for cum in ("/skills", "/mcp", "agy plugin list"):
            self.assertIn(cum, noi_dung, f"README thiếu cụm bắt buộc {cum}")

    def test_manifest_liet_ke_du_file_moi(self):
        with open(os.path.join(self.goc, "manifest.json"), encoding="utf-8") as f:
            files = json.load(f)["files"]
        for duong in ("plugin.json", "hooks.json", "mcp_config.json",
                      "skills/tdq-intake/SKILL.md", "hooks/scripts/agy_pretooluse_gate.py",
                      "hooks/scripts/agy_stop_gate.py", "scripts/tdq_state.py"):
            self.assertIn(duong, files, f"manifest thiếu {duong}")

    @unittest.skipUnless(helper.co_lenh("graphify"), "chưa cài graphify — check báo MISSING, thoát 1")
    def test_checkportable_xac_nhan_ban_sach(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(self.goc, "scripts", "tdq_checkportable.py"),
             "check", "--root", self.goc],
            capture_output=True, encoding="utf-8", text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class TestTachPatch(unittest.TestCase):
    """Rút đường dẫn ra khỏi thân patch của `apply_patch` — hàm thuần, kiểm riêng.

    Nạp thẳng từ file NGUỒN `hooks/scripts/codex_edit_gate.py`: trước đây hàm này có hai
    bản (một bản sống trong chuỗi sinh bundle, một bản chép lại trong `build_portable.py`
    chỉ để test bám vào) và hai bản đó có thể lệch nhau mà không ai biết.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        duong = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "hooks", "scripts", "codex_edit_gate.py")
        spec = importlib.util.spec_from_file_location("codex_edit_gate_thuan", duong)
        mo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mo)
        cls.tach = staticmethod(mo.tach_duong_dan_patch)

    def test_ba_dang_lenh_patch(self):
        tach = self.tach
        self.assertEqual(tach("*** Update File: a/b.py\n"), "a/b.py")
        self.assertEqual(tach("*** Add File: c.md\n@@\n+x\n"), "c.md")
        self.assertEqual(tach("*** Delete File: d.txt\n"), "d.txt")

    def test_khong_co_gi_thi_tra_chuoi_rong(self):
        tach = self.tach
        self.assertEqual(tach("khong phai patch"), "")
        self.assertEqual(tach(""), "")

    def test_lay_file_dau_tien_khi_patch_nhieu_file(self):
        than = "*** Begin Patch\n*** Update File: mot.py\n*** Update File: hai.py\n"
        self.assertEqual(self.tach(than), "mot.py")


class TestAdapterLaFileThat(unittest.TestCase):
    """Adapter Codex là FILE nguồn, không còn là chuỗi nằm trong hàm sinh bundle.

    Vì sao khoá: một hook viết dưới dạng chuỗi thì không test được, không lint được,
    không có diff đọc nổi — và mỗi lần sửa phải nhớ escape tay. T6.2 sắp thêm cả nhánh
    `Bash` vào đây, nên nó phải là file thật trước đã.
    """

    GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    NGUON = os.path.join(GOC, "hooks", "scripts", "codex_edit_gate.py")

    def test_file_nguon_ton_tai_va_chay_duoc(self):
        self.assertTrue(os.path.isfile(self.NGUON), "thiếu hooks/scripts/codex_edit_gate.py")
        self.assertTrue(os.access(self.NGUON, os.X_OK), "file adapter phải có cờ chạy")

    def test_khong_con_chuoi_adapter_trong_build_portable(self):
        with open(os.path.join(self.GOC, "scripts", "build_portable.py"),
                  encoding="utf-8") as f:
            nguon = f.read()
        self.assertFalse("ADAPTER_CODEX" in nguon,
                         "adapter vẫn còn dạng chuỗi trong build_portable.py")

    def test_build_portable_doc_file_chu_khong_import(self):
        """Import một file hook nghĩa là nạp — và nạp nhầm là chạy. Chỉ được đọc."""
        import ast
        with open(os.path.join(self.GOC, "scripts", "build_portable.py"),
                  encoding="utf-8") as f:
            cay = ast.parse(f.read())
        for nut in ast.walk(cay):
            if isinstance(nut, ast.Import):
                ten = [a.name for a in nut.names]
            elif isinstance(nut, ast.ImportFrom):
                ten = [nut.module or ""]
            else:
                continue
            for t in ten:
                self.assertNotIn("codex_edit_gate", t,
                                 "build_portable.py phải ĐỌC adapter, không import")


def _ten_chet(duong, goc_repo):
    """Tên cấp module (hàm LẪN hằng) không với tới được từ `main`, khối `__main__`, hay từ bất
    kỳ module nào khác của repo. Đi theo chuỗi: hằng chỉ được một hằng chết dùng cũng là chết."""
    import ast
    import glob
    with open(duong, encoding="utf-8") as f:
        cay = ast.parse(f.read())
    dinh = {}
    for nut in cay.body:
        if isinstance(nut, (ast.FunctionDef, ast.ClassDef)):
            dinh[nut.name] = nut
        elif isinstance(nut, ast.Assign):
            dinh.update({t.id: nut for t in nut.targets if isinstance(t, ast.Name)})

    def ten_dung(nut):
        return ({x.id for x in ast.walk(nut) if isinstance(x, ast.Name)}
                | {x.attr for x in ast.walk(nut) if isinstance(x, ast.Attribute)})

    nguon_khac = []
    for mau in ("scripts/*.py", "hooks/scripts/*.py", "tests/*.py"):
        for f in glob.glob(os.path.join(goc_repo, mau)):
            if os.path.abspath(f) != os.path.abspath(duong):
                with open(f, encoding="utf-8") as g:
                    nguon_khac.append(g.read())
    nguon_khac = "\n".join(nguon_khac)
    # Chỉ tính lời gọi QUA TÊN MODULE. Khớp tên trần thì một hằng trùng tên ở module khác
    # (`GOC_TDQ` có ở cả `tdq_checkportable`) làm hằng chết trông như còn sống.
    mod = os.path.splitext(os.path.basename(duong))[0]
    ngoai = set(re.findall(rf"\b{mod}\.(\w+)", nguon_khac))
    for cum in re.findall(rf"from {mod} import \(?([\w\s,]+)\)?", nguon_khac):
        ngoai |= {t.strip() for t in cum.split(",") if t.strip()}
    song = {"main"} | (set(dinh) & ngoai)
    for nut in cay.body:
        if isinstance(nut, ast.If):
            song |= ten_dung(nut)
    hang_doi = list(song)
    while hang_doi:
        ten = hang_doi.pop()
        for dung in ten_dung(dinh[ten]) if ten in dinh else ():
            if dung in dinh and dung not in song:
                song.add(dung)
                hang_doi.append(dung)
    return sorted(set(dinh) - song)


class TestKhongConTenChet(unittest.TestCase):
    """QC vòng 1 (2026-09-21): lượt cắt ở T2.3 chỉ đo HÀM, nên 9 hằng của hai bundle đã gỡ
    (61 dòng) nằm lại mà không phép kiểm nào thấy. Đo cả hằng, và đo bằng máy."""

    def test_khong_con_ten_chet(self):
        self.assertEqual(_ten_chet(SCRIPT, ROOT), [])

    def test_bo_do_bat_duoc_hang_chet_theo_chuoi(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scripts"))
            duong = os.path.join(d, "scripts", "mau.py")
            with open(duong, "w", encoding="utf-8") as f:
                f.write("A = 1\nB = A + 1\nC = 3\n\ndef main():\n    return C\n")
            self.assertEqual(_ten_chet(duong, d), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
