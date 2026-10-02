"""Sổ tìm kiếm — `hooks/scripts/search_observe.py` (T2.2).

Sổ này là thứ duy nhất cổng tìm kiếm dựa vào để biết "request này đã hỏi tầng khái niệm chưa".
Nó phải ghi bằng HIỆU ỨNG (lần gọi tool thật), phải sống qua nhiều lượt (sổ lượt chung bị xoá ở
mỗi prompt — bài học của cổng đọc lại 2026-10-02), và không được lưu nguyên văn prompt.

Chạy riêng từng nhóm bằng `-k`: `khai_niem`, `prompt`, `qua_luot`, `trang_thai`, `hong`, `log`.
"""
import io
import json
import os
import sys
import tempfile
import unittest

from helper import ROOT, run_hook

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
import search_observe  # noqa: E402
import tdq_state  # noqa: E402

HOOK = "search_observe.py"
PHIEN = "phien-thu-search-observe"


class BaseSo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)

    def mo_request(self, slug="2026-10-03-0000-thu"):
        with io.open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w",
                     encoding="utf-8") as fh:
            json.dump({"request": slug, "phase": "analyze"}, fh)
        return f"yc:{slug}"

    def goi(self, payload, log="0"):
        payload = dict(payload, session_id=PHIEN, cwd=self.cwd)
        rc, out, err = run_hook(HOOK, payload,
                                env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": log})
        self.assertEqual(rc, 0, f"sổ phải luôn thoát 0: {err}")
        self.assertEqual(out, "", "sổ không được in gì ra stdout — nó chỉ ghi")
        return err

    def tool(self, ten, **vao):
        return self.goi({"hook_event_name": "PostToolUse", "tool_name": ten, "tool_input": vao})

    def rows(self, khoa):
        return search_observe.doc_so(self.cwd, khoa)


class GhiKhaiNiem(BaseSo):
    def test_khai_niem_lumen_duoc_ghi(self):
        khoa = self.mo_request()
        self.tool("mcp__plugin_lumen_lumen__semantic_search", query="how fonts register")
        self.assertEqual([r["loai"] for r in self.rows(khoa)], ["khai_niem"])

    def test_khai_niem_lsp_hoi_that_duoc_ghi(self):
        khoa = self.mo_request()
        self.tool("mcp__lsp__find_references", symbol="saveFileToDisk")
        self.assertEqual(self.rows(khoa)[0]["cong_cu"], "lsp:find_references")

    def test_khai_niem_lsp_don_dep_khong_tinh(self):
        """`start_lsp` không hỏi gì — tính nó là cho `start_lsp` mở khoá grep mà không hỏi một câu."""
        khoa = self.mo_request()
        for ten in ("mcp__lsp__start_lsp", "mcp__lsp__open_document",
                    "mcp__lsp__get_server_capabilities"):
            self.tool(ten)
        self.assertEqual(self.rows(khoa), [])

    def test_khai_niem_graphify_query_qua_bash(self):
        khoa = self.mo_request()
        self.tool("Bash", command="graphify query \"how does saving work\"")
        self.assertEqual(self.rows(khoa)[0]["cong_cu"], "graphify:query")

    def test_khai_niem_bash_thuong_khong_tinh(self):
        khoa = self.mo_request()
        self.tool("Bash", command="grep -rn saveFileToDisk packages/")
        self.tool("Bash", command="graphify extract . --code-only")
        self.assertEqual(self.rows(khoa), [], "grep và dựng đồ thị không phải câu hỏi khái niệm")


class GhiPrompt(BaseSo):
    def test_prompt_chi_luu_token_khong_luu_nguyen_van(self):
        khoa = self.mo_request()
        self.goi({"hook_event_name": "UserPromptSubmit",
                  "prompt": "hãy sửa hàm saveFileToDisk trong file json.ts giúp tôi"})
        row = self.rows(khoa)[0]
        self.assertEqual(row["loai"], "prompt")
        self.assertIn("saveFileToDisk", row["token"])
        self.assertNotIn("prompt", row, "không được lưu nguyên văn prompt")
        so = io.open(search_observe.duong_so(self.cwd), encoding="utf-8").read()
        self.assertNotIn("giúp tôi", so)

    def test_prompt_moi_thay_prompt_cu(self):
        khoa = self.mo_request()
        self.goi({"hook_event_name": "UserPromptSubmit", "prompt": "about fileHandle"})
        self.goi({"hook_event_name": "UserPromptSubmit", "prompt": "now about loadScene"})
        tt = search_observe.trang_thai(self.rows(khoa))
        self.assertIn("loadScene", tt["token_prompt"])
        self.assertNotIn("fileHandle", tt["token_prompt"], "chỉ prompt GẦN NHẤT được tính")


class SongQuaLuot(BaseSo):
    def test_qua_luot_so_con_sau_khi_so_luot_bi_xoa(self):
        """Đúng việc `prompt_context.py` làm ở mỗi prompt — sổ tìm kiếm không được mất theo."""
        khoa = self.mo_request()
        self.tool("mcp__plugin_lumen_lumen__semantic_search", query="x")
        tdq_state.turn_log_clear(self.cwd, PHIEN)
        self.assertTrue(search_observe.trang_thai(self.rows(khoa))["da_goi_khai_niem"])

    def test_qua_luot_khong_request_thi_theo_phien(self):
        self.tool("mcp__plugin_lumen_lumen__semantic_search", query="x")
        self.assertEqual(len(self.rows(f"phien:{PHIEN}")), 1)

    def test_qua_luot_request_khac_khong_dung_chung(self):
        self.mo_request("2026-10-03-0000-mot")
        self.tool("mcp__plugin_lumen_lumen__semantic_search", query="x")
        khoa_hai = self.mo_request("2026-10-03-0001-hai")
        self.assertFalse(search_observe.trang_thai(self.rows(khoa_hai))["da_goi_khai_niem"],
                         "request mới phải hỏi tầng khái niệm lại từ đầu")


class TrangThai(unittest.TestCase):
    def test_trang_thai_cua_so_tinh_tu_lan_goi_gan_nhat(self):
        rows = [{"loai": "khai_niem"}, {"loai": "tim"}, {"loai": "tim"},
                {"loai": "khai_niem"}, {"loai": "tim"}]
        tt = search_observe.trang_thai(rows)
        self.assertEqual(tt["so_lan_tim_tu_lan_goi"], 1, "gọi lumen lần nữa phải mở lại cửa sổ")

    def test_trang_thai_rong(self):
        self.assertEqual(search_observe.trang_thai([]),
                         {"da_goi_khai_niem": False, "so_lan_tim_tu_lan_goi": 0,
                          "token_prompt": set()})

    def test_trang_thai_so_co_tran(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(search_observe.TRAN_DONG + 20):
                search_observe.ghi_so(tmp, {"ts": 0, "khoa": "yc:x", "loai": "tim", "i": i})
            dong = io.open(search_observe.duong_so(tmp), encoding="utf-8").read().splitlines()
            self.assertLessEqual(len(dong), search_observe.TRAN_DONG)


class KhongLamVo(BaseSo):
    def test_hong_payload_rong_van_thoat_0(self):
        rc, _, _ = run_hook(HOOK, {}, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})
        self.assertEqual(rc, 0)

    def test_hong_so_hong_doc_ra_rong(self):
        khoa = self.mo_request()
        with io.open(search_observe.duong_so(self.cwd), "w", encoding="utf-8") as fh:
            fh.write("{khong phai json\n[1,2]\n")
        self.assertEqual(self.rows(khoa), [])
        self.tool("mcp__plugin_lumen_lumen__semantic_search", query="x")
        self.assertEqual(len(self.rows(khoa)), 1, "dòng hỏng không được chặn dòng mới")


class LogService(BaseSo):
    def test_log_tat_duoc_bang_bien_moi_truong(self):
        self.assertEqual(self.tool("mcp__plugin_lumen_lumen__semantic_search"), "")

    def test_log_bat_mac_dinh_co_timestamp(self):
        err = self.goi({"hook_event_name": "PostToolUse",
                        "tool_name": "mcp__plugin_lumen_lumen__semantic_search",
                        "tool_input": {}}, log="1")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] search_observe")


if __name__ == "__main__":
    unittest.main()
