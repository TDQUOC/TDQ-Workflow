"""Unit test cho scripts/lsp_module.py — module LSP (ngôn ngữ, gốc), kịch bản MCP, bảng kết quả, broker.

Ca gốc 2026-10-07: `agent-lsp doctor` ĐẠT trong cả ba lỗi đo được (thiếu `language_id`, tsserver
"No Project", phạm vi một file). Bảng module là thứ biến "mỗi project nhiều ngôn ngữ/nhiều gốc"
thành danh sách kịch bản cụ thể — nên dò sai một gốc là kiểm sai cả module.
Mọi ca chạy trên cây tạm; không ca nào gọi tiến trình thật hay đọc ~/.claude.json thật.
"""
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lsp_module  # noqa: E402

ARGS = ["typescript:tsls,--stdio", "python:pyright-langserver,--stdio", "html:html-ls,--stdio"]


def _ghi(goc, rel, noi_dung=""):
    duong = os.path.join(goc, *rel.split("/"))
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as fh:
        fh.write(noi_dung)


PY_LIB = "def tinh_tong_hop(a, b):\n    return a + b\n\n\ndef khong_ai_goi():\n    return 1\n"
PY_DUNG = "from lib import tinh_tong_hop\n\nprint(tinh_tong_hop(1, 2))\n"


class CayTam(unittest.TestCase):
    def setUp(self):
        self.goc = tempfile.mkdtemp(prefix="tdq-lsp-module-")
        self.addCleanup(shutil.rmtree, self.goc, True)

    def cay_python(self):
        _ghi(self.goc, "pyproject.toml", "[project]\nname='x'\n")
        _ghi(self.goc, "lib.py", PY_LIB)
        _ghi(self.goc, "app.py", PY_DUNG)
        _ghi(self.goc, "khac.py", "x = 1\n")


class TestDoModule(CayTam):
    def test_do_module_mot_ngon_ngu_la_mot_dong(self):
        self.cay_python()
        modules = lsp_module.do_module(self.goc)
        self.assertEqual([m["id"] for m in modules], ["python:."])
        self.assertEqual(modules[0]["moc"], "pyproject.toml")
        self.assertEqual(modules[0]["so_file"], 3)

    def test_do_module_python_cong_html(self):
        self.cay_python()
        for i in range(3):
            _ghi(self.goc, f"web/p{i}.html", "<p>x</p>")
        ids = [m["id"] for m in lsp_module.do_module(self.goc)]
        self.assertEqual(ids, ["html:.", "python:."])

    def test_do_module_ts_hai_tsconfig_la_hai_module(self):
        # Đúng hình claudecodeui: tsconfig gốc cho src/, server/ có tsconfig riêng.
        _ghi(self.goc, "package.json", "{}")
        _ghi(self.goc, "tsconfig.json", "{}")
        _ghi(self.goc, "server/tsconfig.json", "{}")
        for i in range(3):
            _ghi(self.goc, f"src/a{i}.tsx", "export const x = 1\n")
            _ghi(self.goc, f"server/b{i}.ts", "export const y = 1\n")
        modules = {m["id"]: m for m in lsp_module.do_module(self.goc)}
        self.assertEqual(sorted(modules), ["typescript:.", "typescript:server"])
        self.assertEqual(modules["typescript:server"]["moc"], "tsconfig.json")
        self.assertTrue(all(f.startswith("src/") for f in modules["typescript:."]["files"]))

    def test_do_module_python_cong_ts_va_js_thuoc_ho_ts(self):
        self.cay_python()
        _ghi(self.goc, "web/package.json", "{}")
        _ghi(self.goc, "web/tsconfig.json", "{}")
        _ghi(self.goc, "web/a.ts", "export const a = 1\n")
        _ghi(self.goc, "web/b.js", "export const b = 1\n")
        _ghi(self.goc, "web/c.js", "export const c = 1\n")
        ids = [m["id"] for m in lsp_module.do_module(self.goc)]
        self.assertEqual(ids, ["python:.", "typescript:web"])

    def test_do_module_js_thuan_la_javascript(self):
        _ghi(self.goc, "package.json", "{}")
        for i in range(3):
            _ghi(self.goc, f"src/m{i}.js", "export const v = 1\n")
        self.assertEqual([m["id"] for m in lsp_module.do_module(self.goc)], ["javascript:."])

    def test_do_module_module_nho_gop_len_cha(self):
        self.cay_python()
        _ghi(self.goc, "tools/pyproject.toml", "[project]\nname='t'\n")
        _ghi(self.goc, "tools/mot.py", "y = 2\n")
        modules = lsp_module.do_module(self.goc)
        self.assertEqual([m["id"] for m in modules], ["python:."])
        self.assertEqual(modules[0]["so_file"], 4)

    def test_do_module_gop_nhieu_tang_khong_mat_file(self):
        """Review 2026-10-08: nhóm nhỏ gộp vào gốc không có file nguồn riêng phải gộp tiếp lên."""
        _ghi(self.goc, "pkg/pyproject.toml", "")
        _ghi(self.goc, "pkg/sub/pyproject.toml", "")
        for i in range(2):
            _ghi(self.goc, f"pkg/sub/m{i}.py", "x = 1\n")
        _ghi(self.goc, "a.py", "y = 1\n")
        modules = lsp_module.do_module(self.goc)
        self.assertEqual([(m["id"], m["so_file"]) for m in modules], [("python:.", 3)])

    def test_do_module_bo_node_modules_va_thu_muc_an(self):
        self.cay_python()
        for i in range(5):
            _ghi(self.goc, f"node_modules/p/x{i}.ts", "export const z = 1\n")
            _ghi(self.goc, f".venv/y{i}.py", "z = 1\n")
        self.assertEqual([m["id"] for m in lsp_module.do_module(self.goc)], ["python:."])

    def test_do_module_ton_trong_gitignore(self):
        """claudecodeui: `dist-server/` (đầu ra build) nằm trong .gitignore, không thuộc module nào."""
        import subprocess
        self.cay_python()
        for i in range(4):
            _ghi(self.goc, f"dist-server/x{i}.js", "export const z = 1\n")
        _ghi(self.goc, ".gitignore", "dist-server/\n")
        if subprocess.run(["git", "init", "-q", self.goc], capture_output=True).returncode != 0:
            self.skipTest("không có git")
        self.assertEqual([m["id"] for m in lsp_module.do_module(self.goc)], ["python:."])

    def test_bang_khong_lam_ban_git_status(self):
        """Bảng ghi ở intake 1b không được làm bẩn cây — bước 3b dừng khi `git status` không rỗng."""
        import subprocess
        if subprocess.run(["git", "init", "-q", self.goc], capture_output=True).returncode != 0:
            self.skipTest("không có git")
        self.cay_python()
        lsp_module.lap_kich_ban(self.goc, args=ARGS)
        lsp_module.lap_kich_ban(self.goc, args=ARGS)
        ra = subprocess.run(["git", "-C", self.goc, "status", "--porcelain"], capture_output=True, text=True,
                            encoding="utf-8").stdout
        self.assertNotIn(".tdq-lsp-module.json", ra)
        with open(os.path.join(self.goc, ".git", "info", "exclude"), encoding="utf-8") as fh:
            self.assertEqual(fh.read().count("/docs/tdq/.tdq-lsp-module.json"), 1)
        self.assertFalse(os.path.exists(os.path.join(self.goc, ".gitignore")))

    def test_do_module_ngon_ngu_moi_xuat_hien_sinh_module_moi(self):
        # Ca của user: ban đầu chỉ Python, sau thêm JS + HTML.
        self.cay_python()
        truoc = lsp_module.ngon_ngu_cua(lsp_module.do_module(self.goc))
        for i in range(3):
            _ghi(self.goc, f"static/s{i}.js", "export function f%d() {}\n" % i)
            _ghi(self.goc, f"static/t{i}.html", "<p></p>")
        sau = lsp_module.ngon_ngu_cua(lsp_module.do_module(self.goc))
        self.assertEqual(truoc, ["python"])
        self.assertEqual(sau, ["html", "javascript", "python"])


class TestNgonNguMoi(CayTam):
    def test_ngon_ngu_moi_so_voi_bang(self):
        self.cay_python()
        self.assertEqual(lsp_module.ngon_ngu_moi(self.goc), [], "chưa có bảng → không hỏi")
        lsp_module.ghi_ngon_ngu(self.goc)
        self.assertEqual(lsp_module.ngon_ngu_moi(self.goc), [])
        for i in range(3):
            _ghi(self.goc, f"w{i}.html", "<p></p>")
        self.assertEqual(lsp_module.ngon_ngu_moi(self.goc), ["html"])
        lsp_module.ghi_ngon_ngu(self.goc)
        self.assertEqual(lsp_module.ngon_ngu_moi(self.goc), [])


class TestBangVaHan(CayTam):
    def test_van_tay_doi_khi_moc_hoac_dong_mcp_doi(self):
        self.cay_python()
        m = lsp_module.do_module(self.goc)[0]
        goc_vt = lsp_module.van_tay(self.goc, m, ARGS)
        self.assertNotEqual(goc_vt, lsp_module.van_tay(self.goc, m, ["python:khac,--stdio"]))
        moc = os.path.join(self.goc, "pyproject.toml")
        os.utime(moc, (time.time() + 100, time.time() + 100))
        self.assertNotEqual(goc_vt, lsp_module.van_tay(self.goc, m, ARGS))

    def test_ghi_ket_qua_dat_khi_co_tham_chieu_ngoai_file(self):
        self.cay_python()
        [(m, kb)] = lsp_module.lap_kich_ban(self.goc, args=ARGS)
        self.assertEqual(kb["symbol"], "tinh_tong_hop")
        self.assertEqual(kb["so_lan_file_dinh_nghia"], 1)
        self.assertEqual(lsp_module.ghi_ket_qua(self.goc, m["id"], 3, args=ARGS), lsp_module.DAT)
        [(_m, tt, _ct)] = lsp_module.trang_thai(self.goc, args=ARGS)
        self.assertEqual(tt, lsp_module.DAT)

    def test_ghi_ket_qua_truot_khi_chi_thay_file_dinh_nghia(self):
        self.cay_python()
        [(m, _kb)] = lsp_module.lap_kich_ban(self.goc, args=ARGS)
        self.assertEqual(lsp_module.ghi_ket_qua(self.goc, m["id"], 1, args=ARGS), lsp_module.TRUOT)
        ok, dong = lsp_module.cong_init(self.goc, args=ARGS)
        self.assertFalse(ok)
        self.assertIn("python:. → TRUOT", dong[0])

    def test_ghi_ket_qua_khi_chua_co_kich_ban_bao_loi(self):
        self.cay_python()
        with self.assertRaises(ValueError):
            lsp_module.ghi_ket_qua(self.goc, "python:.", 3, args=ARGS)

    def test_het_han_sau_24h_va_khi_doi_mcp(self):
        self.cay_python()
        [(m, _kb)] = lsp_module.lap_kich_ban(self.goc, args=ARGS)
        lsp_module.ghi_ket_qua(self.goc, m["id"], 3, args=ARGS)
        mai = time.time() + lsp_module.HAN_GIAY + 60
        self.assertEqual(lsp_module.trang_thai(self.goc, args=ARGS, bay_gio=mai)[0][1], lsp_module.HET_HAN)
        self.assertEqual(lsp_module.trang_thai(self.goc, args=["python:moi"])[0][1], lsp_module.HET_HAN)

    def test_chua_kiem_chan_init_html_khong_chan(self):
        self.cay_python()
        for i in range(3):
            _ghi(self.goc, f"p{i}.html", "<p></p>")
        tt = {m["id"]: s for m, s, _ in lsp_module.trang_thai(self.goc, args=ARGS)}
        self.assertEqual(tt, {"html:.": lsp_module.KHONG_DU_MAU, "python:.": lsp_module.CHUA_KIEM})
        self.assertFalse(lsp_module.cong_init(self.goc, args=ARGS)[0])

    def test_repo_khong_co_ma_nguon_khong_chan(self):
        _ghi(self.goc, "README.md", "x")
        self.assertEqual(lsp_module.cong_init(self.goc, args=ARGS), (True, []))

    def test_bang_hong_doc_ra_rong(self):
        _ghi(self.goc, lsp_module.FILE_BANG.replace(os.sep, "/"), "{không phải json")
        self.assertEqual(lsp_module.doc_bang(self.goc), {"module": {}})

    def test_doc_mcp_args_lay_dung_server_lsp(self):
        duong = os.path.join(self.goc, "claude.json")
        with open(duong, "w", encoding="utf-8") as fh:
            json.dump({"mcpServers": {"lsp": {"args": ARGS}, "khac": {"args": ["x"]}}}, fh)
        self.assertEqual(lsp_module.doc_mcp_args(duong), ARGS)
        self.assertEqual(lsp_module.dong_mcp(ARGS, "python"), ARGS[1])
        self.assertEqual(lsp_module.dong_mcp(ARGS, "go"), "")


class TestKichBan(CayTam):
    def test_kich_ban_chon_symbol_dung_o_file_khac_va_vi_tri_dung(self):
        self.cay_python()
        m = lsp_module.do_module(self.goc)[0]
        kb = lsp_module.kich_ban(self.goc, m)
        assert kb is not None
        self.assertEqual((kb["symbol"], kb["line"], kb["column"]), ("tinh_tong_hop", 1, 5))
        self.assertEqual(kb["so_file_grep"], 2)
        goi = lsp_module.loi_goi_mcp(m, kb, ARGS)
        self.assertIn('"language_id": "python"', goi[0])
        self.assertTrue(goi[2].startswith("mcp__lsp__find_references"))

    def test_kich_ban_bo_qua_ten_trong_chu_thich_va_chuoi(self):
        _ghi(self.goc, "pyproject.toml", "")
        _ghi(self.goc, "a.py", "def don_doc_lap():\n    pass\n")
        _ghi(self.goc, "b.py", "# don_doc_lap chỉ nhắc trong chú thích\nx = 'don_doc_lap'\n")
        _ghi(self.goc, "c.py", "y = 1\n")
        self.assertIsNone(lsp_module.kich_ban(self.goc, lsp_module.do_module(self.goc)[0]))

    def test_loi_goi_javascript_dung_language_id_cua_entry_typescript(self):
        m = {"lang": "javascript", "goc": "."}
        kb = {"goc_tuyet_doi": self.goc, "file": os.path.join(self.goc, "a.js"), "line": 1, "column": 1}
        self.assertIn('"language_id": "typescript"', lsp_module.loi_goi_mcp(m, kb, ARGS)[0])

    def test_kich_ban_typescript_dung_export(self):
        _ghi(self.goc, "tsconfig.json", "{}")
        _ghi(self.goc, "a.ts", "export function taoModule() {}\n")
        _ghi(self.goc, "b.ts", "import { taoModule } from './a'\ntaoModule()\n")
        _ghi(self.goc, "c.ts", "export const z = 1\n")
        kb = lsp_module.kich_ban(self.goc, lsp_module.do_module(self.goc)[0])
        assert kb is not None
        self.assertEqual((kb["symbol"], kb["line"], kb["column"]), ("taoModule", 1, 17))

    def test_lap_kich_ban_ghi_moi_module_va_bo_module_da_mat(self):
        self.cay_python()
        for i in range(3):
            _ghi(self.goc, f"p{i}.html", "<p></p>")
        bang = lsp_module.doc_bang(self.goc)
        bang["module"]["go:cu"] = {"lang": "go", "goc": "cu"}
        lsp_module.ghi_bang(self.goc, bang)
        lsp_module.lap_kich_ban(self.goc, args=ARGS)
        self.assertEqual(sorted(lsp_module.doc_bang(self.goc)["module"]), ["html:.", "python:."])

    def test_khong_du_mau_ghi_vao_bang_va_khong_chan(self):
        _ghi(self.goc, "pyproject.toml", "")
        for i in range(3):
            _ghi(self.goc, f"m{i}.py", f"def rieng_{i}_xyz():\n    pass\n")
        [(m, kb)] = lsp_module.lap_kich_ban(self.goc, args=ARGS)
        self.assertIsNone(kb)
        self.assertEqual(lsp_module.trang_thai(self.goc, args=ARGS)[0][1], lsp_module.KHONG_DU_MAU)
        self.assertTrue(lsp_module.cong_init(self.goc, args=ARGS)[0])


class TestBroker(unittest.TestCase):
    def setUp(self):
        self.goc = tempfile.mkdtemp(prefix="tdq-broker-")
        self.addCleanup(shutil.rmtree, self.goc, True)

    def _ds(self):
        lenh = "C:\\bin\\agent-lsp.exe daemon-broker --root-dir={} --language={} --command=x"
        return lambda: [
            {"pid": 1, "khoi_dong": 100.0, "lenh": lenh.format(self.goc, "python"), "cha_song": False},
            {"pid": 2, "khoi_dong": 200.0, "lenh": lenh.format(self.goc, "python"), "cha_song": True},
            {"pid": 3, "khoi_dong": 150.0, "lenh": lenh.format(os.path.join(self.goc, "da-xoa"), "typescript")},
            {"pid": 4, "khoi_dong": 120.0, "lenh": lenh.format(self.goc, "typescript"), "cha_song": True},
            {"pid": 5, "khoi_dong": 50.0, "lenh": "C:\\bin\\agent-lsp.exe typescript:tsls,--stdio"},
            {"pid": 6, "khoi_dong": 90.0, "lenh": lenh.format(self.goc, "typescript"), "cha_song": True},
            {"pid": 7, "khoi_dong": 80.0, "lenh": "agent-lsp daemon-broker --language python", "cha_song": False},
            {"pid": 8, "khoi_dong": 70.0, "lenh": f"agent-lsp daemon-broker --root-dir {self.goc} --language go"},
        ]

    def test_broker_khong_tat_ban_trung_con_cha_song_hoac_khong_doc_duoc_goc(self):
        mo_coi = {b["pid"] for b in lsp_module.broker_mo_coi(lsp_module.liet_ke_broker(self._ds()))}
        self.assertNotIn(6, mo_coi, "bản trùng nhưng cha còn sống: có thể đang phục vụ phiên khác")
        self.assertNotIn(7, mo_coi, "không đọc được gốc thì không bao giờ là mồ côi")
        self.assertNotIn(8, mo_coi, "dạng `--root-dir <path>` có dấu cách vẫn đọc được gốc")

    def test_broker_mo_coi_la_goc_mat_hoac_trung_cap_cu_hon(self):
        mo_coi = lsp_module.broker_mo_coi(lsp_module.liet_ke_broker(self._ds()))
        self.assertEqual(sorted(b["pid"] for b in mo_coi), [1, 3])

    def test_broker_don_chi_tat_daemon_broker(self):
        da_goi = []
        tat = lambda pid: da_goi.append(pid) or True  # noqa: E731
        self.assertEqual(sorted(lsp_module.don_broker(self._ds(), tat)), [1, 3])
        self.assertNotIn(5, da_goi)

    def test_commit_canh_bao_duoi_nguong(self):
        self.assertIn("2.2 GB", lsp_module.canh_bao_commit(2.2))
        self.assertEqual(lsp_module.canh_bao_commit(10.0), "")

    def test_commit_trong_gb_tra_so_hoac_none(self):
        trong = lsp_module.commit_trong_gb()
        self.assertTrue(trong is None or trong > 0)


class TestLog(unittest.TestCase):
    def test_log_bat_mac_dinh_va_tat_bang_bien(self):
        with mock.patch.dict(os.environ, {"TDQ_LOG": "1"}), mock.patch("sys.stderr") as err:
            lsp_module._log("thử")
            self.assertTrue(err.write.called)
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}), mock.patch("sys.stderr") as err:
            lsp_module._log("thử")
            self.assertFalse(err.write.called)


if __name__ == "__main__":
    unittest.main()
