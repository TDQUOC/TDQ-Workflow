"""Luật tìm kiếm — `scripts/search_rules.py` (T2.1).

Hàm thuần: phân loại một lệnh Bash / mẫu Grep, rồi quyết `allow`/`deny` theo 3 luật spec §3.
Chạy riêng từng nhóm bằng `-k`: `loc_file`, `doan_mo`, `ghep`, `codex`, `mo_dau`,
`ten_trong_prompt`, `mo_khoa`, `cua_so`, `het_han`, `fixture`, `phan_loai`.
"""
import io
import json
import os
import re
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import search_rules as sr  # noqa: E402
import search_replay  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "phien_excalidraw_tim.json")


def _bash(lenh):
    return sr.phan_loai("Bash", lenh)


def _tt(da_goi=False, so_lan=0, token=(), cua_so=None, tang_song=None):
    return {"da_goi_khai_niem": da_goi, "so_lan_tim_tu_lan_goi": so_lan,
            "token_prompt": set(token), "cua_so": sr.CUA_SO if cua_so is None else cua_so,
            "tang_song": tang_song}


def _qd(lenh, cong_cu="Bash", **tt):
    return sr.quyet_dinh(sr.phan_loai(cong_cu, lenh), _tt(**tt))


class TestLocFile(unittest.TestCase):
    def test_loc_file_git_ls_files(self):
        self.assertEqual(_bash(r"git ls-files | grep -cE '\.test\.tsx?$'")["loai"], "loc_file")

    def test_loc_file_trong_lenh_con(self):
        lenh = ('for d in packages/*; do echo "$d: $(git ls-files $d | grep -E \'\\.(ts|tsx)$\' '
                '| wc -l)"; done')
        self.assertEqual(_bash(lenh)["loai"], "loc_file")

    def test_loc_file_ls_va_find(self):
        self.assertEqual(_bash("ls src | grep Font")["loai"], "loc_file")
        self.assertEqual(_bash("find . -name '*.ts' | grep -v test")["loai"], "loc_file")
        self.assertEqual(_bash("rg --files | grep Font")["loai"], "loc_file")

    def test_loc_file_loc_output_khac_khong_phai_tim(self):
        self.assertEqual(_bash("npm ls | grep react")["loai"], "khong_phai_tim")
        self.assertEqual(_bash("git log --oneline | grep fix")["loai"], "khong_phai_tim")

    def test_loc_file_liet_ke_don_khong_phai_tim(self):
        for lenh in ("rg --files", "find . -name '*.ts'", "ls -la src", "sed -n 1,5p a.ts"):
            self.assertEqual(_bash(lenh)["loai"], "khong_phai_tim", lenh)

    def test_loc_file_cho_qua_truoc_khai_niem(self):
        ok, ly_do = _qd(r"git ls-files | grep -E '\.tsx?$|a|b'")
        self.assertTrue(ok, ly_do)


class TestDoanMo(unittest.TestCase):
    def test_doan_mo_bon_nhanh(self):
        pl = _bash(r'grep -rn "saveFileToDisk\|saveToActiveFile\|isSaved\|beforeunload" packages/')
        self.assertEqual(pl["loai"], "tim_code")
        self.assertTrue(pl["doan_mo"])
        self.assertEqual(pl["tu_khoa"],
                         ["saveFileToDisk", "saveToActiveFile", "isSaved", "beforeunload"])

    def test_doan_mo_rg_ong_khong_thoat(self):
        pl = _bash('rg -n "static|register|export|class " src')
        self.assertEqual(pl["loai"], "tim_code")
        self.assertTrue(pl["doan_mo"])

    def test_doan_mo_ten_don_false(self):
        pl = _bash('grep -rn "fileHandle" a.ts b.ts | head -15')
        self.assertEqual(pl["loai"], "tim_code")
        self.assertFalse(pl["doan_mo"])
        self.assertEqual(pl["tu_khoa"], ["fileHandle"])

    def test_doan_mo_cau_tu_nhien(self):
        pl = _bash('grep -rn "how fonts are registered" .')
        self.assertTrue(pl["doan_mo"])
        self.assertFalse(_bash('grep -rn "export const" .')["doan_mo"])
        self.assertFalse(_bash(r'grep -rn "a b \w+" .')["doan_mo"])

    def test_doan_mo_hai_nhanh_false(self):
        self.assertFalse(_bash(r'grep -n "foo\|bar" x.ts')["doan_mo"])

    def test_doan_mo_bo_qua_tuy_chon_co_gia_tri(self):
        pl = _bash('grep -A3 -m 5 --include=*.ts -rn "ASSETS_URL" packages')
        self.assertEqual(pl["tu_khoa"], ["ASSETS_URL"])
        pl = _bash("rg -g '*.ts' -t ts -e alpha -e beta --regexp=gamma src")
        self.assertEqual(pl["tu_khoa"], ["alpha", "beta", "gamma"])
        self.assertTrue(pl["doan_mo"])

    def test_doan_mo_cac_cong_cu(self):
        pl = _bash('git grep -n "a\\|b\\|c" -- src')
        self.assertEqual((pl["loai"], pl["doan_mo"]), ("tim_code", True))
        pl = _bash('findstr /S /N "alpha beta gamma" *.ts')
        self.assertEqual((pl["loai"], pl["doan_mo"]), ("tim_code", True))
        pl = _bash('findstr /S /C:"one long phrase" *.ts')
        self.assertEqual(pl["tu_khoa"], ["one long phrase"])
        pl = _bash("Select-String -Path *.ts -Pattern 'fileHandle'")
        self.assertEqual((pl["loai"], pl["tu_khoa"]), ("tim_code", ["fileHandle"]))
        pl = _bash("ag 'x|y|z' src")
        self.assertTrue(pl["doan_mo"])

    def test_doan_mo_grep_tool(self):
        pl = sr.phan_loai("Grep", "lowPerf|isLowEnd|hardwareConcurrency")
        self.assertEqual((pl["loai"], pl["doan_mo"]), ("tim_code", True))
        self.assertEqual(sr.phan_loai("Grep", "fileHandle")["doan_mo"], False)

    def test_doan_mo_cong_cu_khac_khong_phai_tim(self):
        self.assertEqual(sr.phan_loai("Read", "a.ts")["loai"], "khong_phai_tim")


class TestGhep(unittest.TestCase):
    def test_ghep_lenh(self):
        pl = _bash(r'sed -n 1,5p a.ts; grep -n "x\|y" b.ts && echo ok')
        self.assertEqual(pl["loai"], "tim_code")
        self.assertEqual(pl["tu_khoa"], ["x", "y"])

    def test_ghep_hop_nhieu_lan_tim(self):
        pl = _bash('grep -n "alpha" a.ts || grep -n "beta" b.ts; ls | grep gamma')
        self.assertEqual(pl["loai"], "tim_code")
        self.assertEqual(pl["tu_khoa"], ["alpha", "beta"])
        self.assertFalse(pl["doan_mo"])

    def test_ghep_ngoac_lech_khong_no(self):
        for lenh in ('grep -rn "abc\\|def b.ts', "grep 'x", "echo $(grep foo", "`grep a", ""):
            pl = _bash(lenh)
            self.assertIn(pl["loai"], ("tim_code", "khong_phai_tim", "loc_file"), lenh)
        self.assertEqual(_bash('grep -rn "abc\\|def b.ts')["loai"], "tim_code")

    def test_ghep_ong_trong_ngoac_khong_tach(self):
        pl = _bash("grep -n 'a|b' x.ts")
        self.assertEqual(pl["tu_khoa"], ["a", "b"])
        self.assertEqual(pl["loai"], "tim_code")

    def test_ghep_cat_vao_grep_la_tim_code(self):
        self.assertEqual(_bash("cat a.ts | grep -n fileHandle")["loai"], "tim_code")
        self.assertEqual(_bash("Get-Content a.ts | Select-String foo")["loai"], "tim_code")

    def test_ghep_grep_sau_grep_chi_loc_ket_qua(self):
        pl = _bash('grep -rn "alpha" src | grep -v "test|spec|mock"')
        self.assertEqual(pl["tu_khoa"], ["alpha"])
        self.assertFalse(pl["doan_mo"])

    def test_ghep_backtick_va_tien_to(self):
        self.assertEqual(_bash("echo `grep -c foo a.ts`")["loai"], "tim_code")
        self.assertEqual(_bash("LC_ALL=C timeout 5 sudo grep -rn foo .")["tu_khoa"], ["foo"])
        self.assertEqual(_bash("git ls-files | xargs grep -n foo")["loai"], "tim_code")
        self.assertEqual(_bash("(grep -rn foo . || true) 2>&1 | head")["loai"], "tim_code")

    def test_ghep_chu_thich_va_chuyen_huong(self):
        self.assertEqual(_bash("ls 2>&1 # grep foo")["loai"], "khong_phai_tim")


class TestCodex(unittest.TestCase):
    def test_codex_bash_lc(self):
        pl = sr.phan_loai("shell", ["bash", "-lc", "grep -rn foo ."])
        self.assertEqual((pl["loai"], pl["tu_khoa"]), ("tim_code", ["foo"]))

    def test_codex_powershell(self):
        pl = sr.phan_loai("shell", ["powershell", "-Command",
                                    "Select-String -Pattern 'a|b|c' -Path *.ts"])
        self.assertEqual((pl["loai"], pl["doan_mo"], pl["tu_khoa"]), ("tim_code", True, ["a", "b", "c"]))

    def test_codex_ten_khac_va_argv_tran(self):
        self.assertEqual(sr.phan_loai("exec_command", "grep -rn foo .")["loai"], "tim_code")
        self.assertEqual(sr.phan_loai("local_shell", ["grep", "-rn", "foo", "."])["loai"], "tim_code")

    def test_codex_get_childitem_noi_select_string_doc_file(self):
        # PowerShell pipes FileInfo objects, so Select-String reads the files' contents.
        self.assertEqual(_bash("Get-ChildItem -Recurse *.ts | Select-String 'a|b|c'")["loai"],
                         "tim_code")


class TestMoDau(unittest.TestCase):
    def test_mo_dau_chan(self):
        ok, ly_do = _qd("grep -rn fileHandle .")
        self.assertFalse(ok)
        self.assertTrue(ly_do.startswith("[TDQ:SEARCH]"))
        self.assertNotIn("lumen", ly_do, "0.58.0: lumen đã gỡ, nhắc nó là đẩy agent tới tool không có")
        self.assertIn("mcp__lsp__find_symbol", ly_do)
        self.assertIn("start_lsp", ly_do, "LSP chưa khởi động là lượt thừa đo được 2026-10-07")
        self.assertLess(ly_do.index("start_lsp"), ly_do.index("find_symbol"),
                        "start_lsp phải đứng TRƯỚC: gọi find_symbol trước là ăn lỗi 'not initialized'")
        self.assertIn("language_id", ly_do, "thiếu language_id thì start_lsp mở nhầm server TypeScript")
        self.assertIn('graphify query "', ly_do)
        self.assertNotIn("path", ly_do.lower())
        self.assertLessEqual(len(ly_do.splitlines()), 3)

    def test_mo_dau_mau_khong_co_ten(self):
        ok, _ = _qd('grep -rn "$s" packages')
        self.assertFalse(ok)


class TestLoiNhacTangSong(unittest.TestCase):
    """0.58.0 — lời chặn chỉ nêu tầng khái niệm đang sống, theo dấu mốc sẵn sàng."""

    def test_chi_graphify_song_thi_khong_nhac_lsp(self):
        ok, ly_do = _qd("grep -rn fileHandle .", tang_song=("graphify",))
        self.assertFalse(ok)
        self.assertIn('graphify query "', ly_do)
        self.assertNotIn("mcp__lsp__", ly_do)

    def test_chi_lsp_song_thi_khong_nhac_graphify(self):
        ok, ly_do = _qd("grep -rn fileHandle .", tang_song=("lsp",))
        self.assertFalse(ok)
        self.assertIn("mcp__lsp__find_symbol", ly_do)
        self.assertNotIn("graphify", ly_do)

    def test_khong_biet_tang_nao_song_thi_nhac_ca_hai(self):
        ly_do = sr.loi_nhac(None)
        self.assertIn("mcp__lsp__find_symbol", ly_do)
        self.assertIn('graphify query "', ly_do)

    def test_tang_cu_khong_con_ten_thi_bo_qua(self):
        """Mốc trước 0.58.0 có khoá `lumen`: nó không được lọt vào lời nhắc."""
        self.assertNotIn("lumen", sr.loi_nhac(("lumen", "graphify")))


class TestTenTrongPrompt(unittest.TestCase):
    def test_ten_trong_prompt_cho_qua(self):
        ok, ly_do = _qd("grep -rn fileHandle .", token={"fileHandle"})
        self.assertTrue(ok, ly_do)
        self.assertIn("prompt", ly_do)

    def test_ten_trong_prompt_khong_phan_biet_hoa(self):
        # The replay lower-cases prompt tokens; the ledger keeps them as typed.
        ok, _ = _qd("grep -rn fileHandle .", token={"filehandle"})
        self.assertTrue(ok)

    def test_ten_trong_prompt_danh_sach_van_chan(self):
        ok, _ = _qd(r'grep -rn "fileHandle\|saveToActiveFile\|isSaved\|beforeunload" .',
                    token={"fileHandle"})
        self.assertFalse(ok)

    def test_ten_trong_prompt_mau_rong_khong_mien(self):
        ok, _ = _qd('grep -rn "$s" .', token={"s"})
        self.assertFalse(ok)


class TestMoKhoaCuaSo(unittest.TestCase):
    def test_cua_so_la_so_nguyen(self):
        self.assertIsInstance(sr.CUA_SO, int)
        self.assertGreater(sr.CUA_SO, 0)

    def test_mo_khoa_doan_mo_trong_cua_so(self):
        ok, ly_do = _qd(r'grep -rn "a1\|b22\|c33" .', da_goi=True, so_lan=0)
        self.assertTrue(ok, ly_do)

    def test_mo_khoa_ten_don(self):
        ok, _ = _qd("grep -rn fileHandle .", da_goi=True, so_lan=0)
        self.assertTrue(ok)

    def test_cua_so_bien(self):
        lenh = r'grep -rn "aaa\|bbb\|ccc" .'
        self.assertTrue(_qd(lenh, da_goi=True, so_lan=4, cua_so=5)[0])
        self.assertFalse(_qd(lenh, da_goi=True, so_lan=5, cua_so=5)[0])


class TestHetHan(unittest.TestCase):
    def test_het_han_doan_mo_bi_chan(self):
        ok, ly_do = _qd(r'grep -rn "aaa\|bbb\|ccc\|ddd" .', da_goi=True, so_lan=12, cua_so=10)
        self.assertFalse(ok)
        self.assertTrue(ly_do.startswith("[TDQ:SEARCH]"))
        self.assertIn("4 alternatives", ly_do)
        self.assertIn("12 searches ago", ly_do)
        self.assertNotIn("lumen", ly_do)
        self.assertIn('graphify query "', ly_do)
        self.assertNotIn("path", ly_do.lower())
        self.assertLessEqual(len(ly_do.splitlines()), 3)

    def test_het_han_ten_don_cho_qua(self):
        ok, _ = _qd("grep -rn fileHandle .", da_goi=True, so_lan=10, cua_so=10)
        self.assertTrue(ok)

    def test_het_han_cau_tu_nhien_bi_chan(self):
        ok, _ = _qd('grep -rn "how fonts are registered" .', da_goi=True, so_lan=10, cua_so=10)
        self.assertFalse(ok)


class TestFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf-8") as fh:
            cls.sk = {x["luot"]: x for x in json.load(fh)["su_kien"]}

    def _pl(self, luot):
        return sr.phan_loai(self.sk[luot]["cong_cu"], self.sk[luot]["lenh"])

    def test_fixture_luot_2_khong_phai_tim_code(self):
        self.assertEqual(self._pl(2)["loai"], "loc_file")

    def test_fixture_luot_4(self):
        # Luot 4 mixes `git ls-files | grep` with a real `grep -r "class (Store|Scene|...)"`
        # over packages/, which reads code — the code search decides the whole script.
        self.assertEqual(self._pl(4)["loai"], "tim_code")
        self.assertTrue(self._pl(4)["doan_mo"])

    def test_fixture_luot_7_9_tim_code(self):
        self.assertEqual(self._pl(7)["loai"], "tim_code")
        self.assertEqual(self._pl(9)["loai"], "tim_code")

    def test_fixture_luot_10_doan_mo(self):
        self.assertTrue(self._pl(10)["doan_mo"])

    def test_fixture_phat_lai(self):
        kq = search_replay.phat_lai(list(self.sk.values()), luat=sr)
        self.assertIn(7, kq["bi_chan"])
        self.assertIn(9, kq["bi_chan"])
        self.assertEqual(kq["bat_oan"], 0)
        self.assertEqual(kq["lot"], 0)


class PhanLoaiBien(unittest.TestCase):
    """F4 (QC vòng 1) — các dạng lệnh làm phân loại lệch: hỏi trợ giúp, heredoc, shell bọc,
    `find -exec`, `-f FILE`, đích chỉ là tài liệu, và Grep có glob/path/type."""

    def test_phan_loai_hoi_tro_giup_khong_phai_tim(self):
        for l in ("grep --help", "rg --version", "rg -V"):
            self.assertEqual(_bash(l)["loai"], "khong_phai_tim", l)

    def test_phan_loai_heredoc_khong_phai_tim(self):
        l = "cat > x.sh <<'EOF'\ngrep -rn foo src\nEOF"
        self.assertEqual(_bash(l)["loai"], "khong_phai_tim")

    def test_phan_loai_shell_boc_van_la_tim(self):
        for l in ("bash -c 'grep -rn foo .'",
                  "powershell -Command \"Select-String -Path src/*.ts -Pattern foo\"",
                  "find . -name '*.ts' -exec grep -n foo {} +"):
            self.assertEqual(_bash(l)["loai"], "tim_code", l)

    def test_phan_loai_file_mau_la_doan_mo(self):
        for l in ("grep -rn -f pats.txt src", "grep -rnf pats.txt src/"):
            kq = _bash(l)
            self.assertEqual((kq["loai"], kq["doan_mo"]), ("tim_code", True), l)

    def test_phan_loai_dich_chi_tai_lieu_khong_phai_tim(self):
        for l in ("grep -rn fileHandle docs/notes.md", "grep -rn fileHandle docs/",
                  "grep -e x -e y README.md"):
            self.assertEqual(_bash(l)["loai"], "khong_phai_tim", l)
        self.assertEqual(_bash("grep -rn foo src/app.ts")["loai"], "tim_code")

    def test_phan_loai_grep_glob_path_type(self):
        for vao in ({"pattern": "foo", "glob": "*.md"}, {"pattern": "foo", "type": "md"},
                    {"pattern": "foo", "path": "docs/notes.md"}):
            self.assertEqual(sr.phan_loai("Grep", vao)["loai"], "khong_phai_tim", vao)
        self.assertEqual(sr.phan_loai("Grep", {"pattern": "foo", "path": "src"})["loai"],
                         "tim_code")


class TestThuan(unittest.TestCase):
    def test_khong_import_hooks_hay_io(self):
        with open(os.path.join(ROOT, "scripts", "search_rules.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIsNone(re.search(r"^\s*(from|import)\s+hooks", src, re.M))
        self.assertIsNone(re.search(r"^\s*import\s+(os|subprocess|io|socket)\b", src, re.M))
        self.assertNotIn("open(", src)


class GoiKhaiNiem(unittest.TestCase):
    """F1 — nhận diện lần gọi tầng khái niệm ở MỘT chỗ thuần, dùng chung cho sổ và bộ phát lại."""

    def test_mo_khoa_gia_bang_chu_khong_tinh(self):
        """`echo graphify query x` và commit message nhắc tới nó từng mở khoá grep (R1#10)."""
        for cmd in ("echo graphify query x", 'git commit -m "note: graphify query later"',
                    "grep -rn 'graphify query' docs"):
            self.assertIsNone(sr.la_goi_khai_niem("Bash", {"command": cmd}), cmd)

    def test_mo_khoa_graphify_that_thi_tinh(self):
        self.assertEqual(sr.la_goi_khai_niem("Bash", {"command": 'graphify query "how saving works"'}),
                         "graphify:query")
        self.assertEqual(sr.la_goi_khai_niem("Bash", {"command": "cd x && graphify explain Foo"}),
                         "graphify:explain")

    def test_mo_khoa_lsp_chi_tool_hoi(self):
        """Danh sách CHO PHÉP: `run_tests`, `apply_edit`, `format_document` không hỏi gì cả."""
        for ten in ("mcp__lsp__run_tests", "mcp__lsp__apply_edit", "mcp__lsp__format_document",
                    "mcp__lsp__start_lsp", "mcp__lsp__open_document"):
            self.assertIsNone(sr.la_goi_khai_niem(ten, {}), ten)
        for ten in ("mcp__lsp__find_references", "mcp__lsp__inspect_symbol",
                    "mcp__lsp__explore_symbol", "mcp__lsp__blast_radius"):
            self.assertIsNotNone(sr.la_goi_khai_niem(ten, {}), ten)

    def test_mo_khoa_bi_chan_khong_an_vao_cua_so(self):
        tt = sr.trang_thai([{"loai": "khai_niem"},
                            {"loai": "tim", "cho_phep": False, "tinh_cua_so": False},
                            {"loai": "tim", "cho_phep": True, "tinh_cua_so": True}])
        self.assertEqual((tt["so_lan_tim_tu_lan_goi"], tt["so_lan_bi_chan"]), (1, 1))


class LogQuaNguoiGoi(unittest.TestCase):
    """Ngoại lệ CÓ CHỦ ĐÍCH của luật log service: `search_rules` là module thuần, không I/O — nó
    chạy trước MỌI lệnh Bash. Log của nó đi qua người gọi: `search_gate.py` ghi loại + quyết định
    + lý do mỗi lần, `search_replay.py` in cả bảng. Ca này khoá cho nó luôn thuần, để không ai
    thêm `print` vào rồi tưởng thế là có log."""

    def test_log_module_thuan_khong_tu_in(self):
        import ast
        nguon = io.open(os.path.join(ROOT, "scripts", "search_rules.py"), encoding="utf-8").read()
        goi = {n.func.id for n in ast.walk(ast.parse(nguon))
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertNotIn("print", goi)
        self.assertNotIn("open", goi)


if __name__ == "__main__":
    unittest.main()
