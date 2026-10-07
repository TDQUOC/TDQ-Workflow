"""Cổng tìm kiếm — `hooks/scripts/search_gate.py` (T2.3, T6.3).

Phần QUYẾT ĐỊNH đã khoá ở `test_search_rules.py`. File này khoá phần của HOOK: đọc đúng lệnh, đọc
đúng sổ của request, ghi lần tìm vào sổ, in `deny` đúng khuôn mà cả Claude Code lẫn Codex đọc, và
không bao giờ làm vỡ một lần gọi tool vì lỗi của chính nó.

Chạy riêng bằng `-k`: `chan`, `cho`, `ghi_so`, `codex`, `nhe`, `hong`, `chua_san_sang`, `log`.
"""
import ast
import io
import json
import os
import sys
import tempfile
import time
import unittest

from helper import ROOT, run_hook

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
import search_observe  # noqa: E402
import search_rules  # noqa: E402

GATE = "search_gate.py"
PHIEN = "phien-thu-search-gate"
SLUG = "2026-10-03-0000-thu-cong"


class BaseCong(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        with io.open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w",
                     encoding="utf-8") as fh:
            json.dump({"active_request": SLUG, "phase": "analyze"}, fh)
        self.khoa = f"yc:{SLUG}"

    def ghi(self, **row):
        search_observe.ghi_so(self.cwd, dict({"ts": time.time(), "khoa": self.khoa}, **row))

    def goi(self, ten_tool, log="0", **vao):
        payload = {"session_id": PHIEN, "cwd": self.cwd, "hook_event_name": "PreToolUse",
                   "tool_name": ten_tool, "tool_input": vao}
        rc, out, err = run_hook(GATE, payload, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": log})
        self.assertEqual(rc, 0, f"cổng phải luôn thoát 0: {err}")
        return out, err

    def bi_chan(self, out):
        if not out:
            return ""
        goi = json.loads(out).get("hookSpecificOutput") or {}
        self.assertEqual(goi.get("permissionDecision"), "deny")
        return goi.get("permissionDecisionReason") or ""


class Chan(BaseCong):
    def test_chan_grep_ten_doan_truoc_tang_khai_niem(self):
        """Lượt 7 của phiên excalidraw: `fileHandle` là tên agent tự đoán, user chưa từng gõ."""
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" packages/excalidraw/data/json.ts')
        ly_do = self.bi_chan(out)
        self.assertIn("TDQ:SEARCH", ly_do)
        self.assertIn("find_symbol", ly_do)
        self.assertNotIn("lumen", ly_do)

    def test_chan_cong_cu_grep_danh_sach_doan(self):
        out, _ = self.goi("Grep", pattern="static|register|export|class ")
        self.assertIn("TDQ:SEARCH", self.bi_chan(out))

    def test_chan_doan_mo_sau_khi_cua_so_het(self):
        self.ghi(loai="khai_niem", cong_cu="graphify:query")
        for _ in range(search_rules.CUA_SO):
            self.ghi(loai="tim", tinh_cua_so=True)
        out, _ = self.goi("Bash", command='grep -rn "saveFileToDisk\\|isSaved\\|beforeunload" .')
        self.assertIn("window", self.bi_chan(out))


class Cho(BaseCong):
    def test_cho_loc_danh_sach_file(self):
        out, _ = self.goi("Bash", command="git ls-files | grep -cE '\\.test\\.tsx?$'")
        self.assertEqual(out, "")

    def test_cho_lenh_khong_phai_tim(self):
        out, _ = self.goi("Bash", command="npm test -- --run")
        self.assertEqual(out, "")
        self.assertEqual(search_observe.doc_so(self.cwd, self.khoa), [],
                         "lệnh không phải tìm thì không được ghi vào sổ")

    def test_cho_ten_co_trong_prompt(self):
        self.ghi(loai="prompt", token=["fileHandle"])
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" packages/')
        self.assertEqual(out, "")

    def test_cho_sau_khi_hoi_tang_khai_niem(self):
        self.ghi(loai="khai_niem", cong_cu="graphify:query")
        out, _ = self.goi("Bash", command='grep -rn "saveFileToDisk\\|isSaved\\|beforeunload" .')
        self.assertEqual(out, "", "trong cửa sổ mở khoá, kể cả danh sách nhiều nhánh cũng đi qua")

    def test_cho_tool_khac_khong_dong_toi(self):
        out, _ = self.goi("Read", file_path="a.ts")
        self.assertEqual(out, "")


class GhiSo(BaseCong):
    def test_ghi_so_lan_tim_duoc_cho_moi_tinh_cua_so(self):
        """Lần bị chặn không chạy — nó không được ăn vào cửa sổ mở khoá."""
        self.goi("Bash", command='grep -rn "fileHandle" .')            # bị chặn
        self.ghi(loai="khai_niem", cong_cu="graphify:query")
        self.goi("Bash", command='grep -rn "fileHandle" .')            # được cho
        tt = search_observe.trang_thai(search_observe.doc_so(self.cwd, self.khoa))
        self.assertEqual(tt["so_lan_tim_tu_lan_goi"], 1)
        tim = [r for r in search_observe.doc_so(self.cwd, self.khoa) if r.get("loai") == "tim"]
        self.assertEqual([r["cho_phep"] for r in tim], [False, True])


class PowerShell(BaseCong):
    def test_codex_cong_cu_powershell_cung_bi_gac(self):
        """Trên Windows, `Select-String` qua tool PowerShell từng đi vòng qua cổng (R1#6)."""
        out, _ = self.goi("PowerShell", command="Select-String -Pattern 'fileHandle' -Path src\\*.ts")
        self.assertIn("TDQ:SEARCH", self.bi_chan(out))


class Codex(BaseCong):
    def test_codex_lenh_dang_danh_sach_bi_chan(self):
        """Codex gửi lệnh shell dạng argv; khuôn `deny` giống hệt khuôn Claude Code đọc."""
        out, _ = self.goi("shell", command=["bash", "-lc", "grep -rn 'a\\|b\\|c' src"])
        self.assertIn("TDQ:SEARCH", self.bi_chan(out))


class ChuaSanSang(BaseCong):
    """T6.3 — chặn khi tầng khái niệm còn đang dựng là bắt agent đứng chờ, không có đường đúng."""

    def ghi_moc(self, dang_dung=True, tuoi_giay=0, graphify=False, lumen=None):
        from datetime import datetime, timedelta
        cap_nhat = (datetime.now() - timedelta(seconds=tuoi_giay)).strftime("%Y-%m-%dT%H:%M:%S")
        moc = {"cap_nhat": cap_nhat, "dang_dung": dang_dung, "pid": 1,
               "tang": {"grep": {"san_sang": True, "chi_tiet": ""},
                        "lsp": {"san_sang": False, "chi_tiet": ""},
                        "graphify": {"san_sang": graphify, "chi_tiet": ""}}}
        if lumen is not None:          # mốc ghi trước 0.58.0 còn khoá này
            moc["tang"]["lumen"] = {"san_sang": lumen, "chi_tiet": ""}
        with io.open(os.path.join(self.cwd, "docs", "tdq", ".tdq-san-sang.json"), "w",
                     encoding="utf-8") as fh:
            json.dump(moc, fh)

    def dung_xuong_va_noi_ra(self, out):
        """Đứng xuống = cho qua (`allow`) VÀ nói ra bằng `[TDQ:SEARCH]` (V3, review 2026-10-03)."""
        goi = json.loads(out).get("hookSpecificOutput") or {}
        self.assertEqual(goi.get("permissionDecision"), "allow")
        self.assertIn("TDQ:SEARCH", goi.get("additionalContext") or "")
        return goi.get("additionalContext")

    def test_chua_san_sang_dang_dung_thi_khong_chan(self):
        self.ghi_moc(dang_dung=True)
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.assertIn("being built", self.dung_xuong_va_noi_ra(out))

    def test_chua_san_sang_dung_xong_ma_khong_tang_nao_song_thi_dung_xuong(self):
        """V2: bản dựng XONG mà LSP/graphify đều không trả lời được — chặn lúc
        này là đẩy agent tới công cụ không trả lời. Bản đầu chặn đúng ở đây; ca này khoá ngược lại."""
        self.ghi_moc(dang_dung=False)
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.assertIn("not available", self.dung_xuong_va_noi_ra(out))

    def test_chua_san_sang_moc_cu_khong_tang_nao_song_van_dung_xuong(self):
        self.ghi_moc(dang_dung=True, tuoi_giay=3 * 3600)
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.dung_xuong_va_noi_ra(out)

    def test_chua_san_sang_cau_dao_khong_moc_bi_chan_3_lan(self):
        """Không mốc (Codex, tắt dựng nền) + chặn 3 lần mà chưa từng ghi được lần gọi khái niệm
        nào → máy này không có tầng khái niệm: đứng xuống thay vì khoá cứng."""
        for _ in range(3):
            out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
            self.assertIn("TDQ:SEARCH", self.bi_chan(out))
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.assertIn("tdq-setup", self.dung_xuong_va_noi_ra(out))

    def test_chua_san_sang_cau_dao_khong_mo_khi_moc_bao_graphify_song(self):
        """Có mốc nói graphify sống → "thử lại 3 lần" KHÔNG được thành đường vòng qua luật."""
        self.ghi_moc(dang_dung=False, graphify=True)
        for _ in range(5):
            out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
            self.assertIn("TDQ:SEARCH", self.bi_chan(out))

    def test_chua_san_sang_mot_tang_da_xong_thi_chan(self):
        """Đang dựng nhưng graphify đã trả lời được → có đường đúng để đi → cổng áp luật."""
        self.ghi_moc(dang_dung=True, graphify=True)
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.assertIn("TDQ:SEARCH", self.bi_chan(out))

    def test_chua_san_sang_chi_graphify_song_thi_loi_chan_chi_nhac_graphify(self):
        """0.58.0: lời chặn sinh từ tầng sống — không nhắc LSP khi mốc nói LSP không trả lời."""
        self.ghi_moc(dang_dung=False, graphify=True)
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        ly_do = self.bi_chan(out)
        self.assertIn('graphify query "', ly_do)
        self.assertNotIn("mcp__lsp__", ly_do)

    def test_chua_san_sang_moc_cu_chi_lumen_song_thi_dung_xuong(self):
        """Mốc trước 0.58.0: lumen sống, LSP/graphify không. Lumen đã gỡ nên không còn tầng nào
        để chỉ tới — chặn lúc này là đẩy agent vào ngõ cụt."""
        self.ghi_moc(dang_dung=False, lumen=True)
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.dung_xuong_va_noi_ra(out)


class Nhe(unittest.TestCase):
    def _nguon(self):
        nguon = io.open(os.path.join(ROOT, "hooks", "scripts", "search_gate.py"),
                        encoding="utf-8").read()
        cay = ast.parse(nguon)
        for nut in ast.walk(cay):
            if isinstance(nut, (ast.Module, ast.FunctionDef)) and ast.get_docstring(nut):
                nut.body = nut.body[1:]
        return ast.unparse(cay)

    def test_nhe_khong_spawn_tien_trinh_con(self):
        nguon = self._nguon()
        for xau in ("subprocess", "os.system(", "os.popen(", "os.spawn"):
            self.assertNotIn(xau, nguon)

    def test_nhe_khong_mo_file_code_cua_project(self):
        """Cổng chỉ tự mở ĐÚNG MỘT file: mốc sẵn sàng (T6.3). State và sổ đi qua search_observe;
        file code mà agent đang tìm thì không bao giờ được mở ở đây."""
        lan_mo = [d for d in self._nguon().splitlines() if "open(" in d]
        self.assertEqual(len(lan_mo), 1, lan_mo)
        self.assertIn("MOC_SAN_SANG", lan_mo[0])


class KhongLamVo(BaseCong):
    def test_hong_payload_rong(self):
        rc, out, _ = run_hook(GATE, {}, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})
        self.assertEqual((rc, out), (0, ""))

    def test_hong_so_hong_van_quyet_dinh_duoc(self):
        with io.open(search_observe.duong_so(self.cwd), "w", encoding="utf-8") as fh:
            fh.write("{hong\n")
        out, _ = self.goi("Bash", command='grep -rn "fileHandle" .')
        self.assertIn("TDQ:SEARCH", self.bi_chan(out), "sổ hỏng đọc ra rỗng → luật mở đầu vẫn áp")

    def test_hong_lenh_thieu_ngoac_khong_no(self):
        out, _ = self.goi("Bash", command="grep -rn 'chua dong ngoac .")
        self.assertIsInstance(out, str)


class LogService(BaseCong):
    def test_log_tat_duoc_bang_bien_moi_truong(self):
        _, err = self.goi("Bash", command='grep -rn "x" .')
        self.assertEqual(err, "")

    def test_log_bat_mac_dinh_co_timestamp(self):
        _, err = self.goi("Bash", command='grep -rn "x" .', log="1")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] search_gate")

    def test_log_ghi_tang_duoc_nhac_khi_chan(self):
        """0.58.0: lời chặn sinh từ tầng sống — log nói nó đã nhắc tầng nào, để soát lại được."""
        _, err = self.goi("Bash", command='grep -rn "fileHandle" .', log="1")
        self.assertIn("nhắc tầng: mọi tầng (không có mốc)", err)
        _, im = self.goi("Bash", command='grep -rn "fileHandle" .', log="0")
        self.assertEqual(im, "")


if __name__ == "__main__":
    unittest.main()
