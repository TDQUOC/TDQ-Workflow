"""Lệnh hook in ra phải chạy được ở project ĐANG mở — T5.1, yêu cầu 2026-10-03-0015.

Đo 2026-10-02 trên một bản cài project-level ở repo khác (excalidraw): mọi lệnh hook in ra đều là
`python3 scripts/tdq_state.py …`, mà project đó không có thư mục `scripts/` — lệnh đầu tiên agent
được bảo chạy đã hỏng. Trong chính repo plugin thì dạng tương đối chạy được và được giữ nguyên.

Chạy riêng bằng `-k`: `ham`, `next`, `hook`.
"""
import json
import os
import re
import sys
import tempfile
import unittest

from helper import ROOT, run_hook

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402

LENH = re.compile(r'python3 "([^"]+\.py)"')


class BaseProjectKhac(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)

    def duong_dan_trong(self, text):
        return LENH.findall(text or "")

    def khong_con_tuong_doi(self, text):
        self.assertNotIn("python3 scripts/", text,
                         "ở project khác, lệnh tương đối `scripts/…` là lệnh chạy không được")


class HamDoi(BaseProjectKhac):
    def test_ham_project_khac_thanh_duong_dan_that(self):
        ra = tdq_state.lenh_cho_project("Run: python3 scripts/tdq_state.py next", self.cwd)
        self.khong_con_tuong_doi(ra)
        duong = self.duong_dan_trong(ra)
        self.assertEqual(len(duong), 1)
        self.assertTrue(os.path.isfile(duong[0]), f"đường dẫn in ra không có thật: {duong[0]}")

    def test_ham_trong_repo_plugin_giu_nguyen(self):
        """Repo plugin có `scripts/` thật — dạng ngắn chạy được và là thứ docs/test của repo đọc."""
        goc = "Run: python3 scripts/tdq_state.py next"
        self.assertEqual(tdq_state.lenh_cho_project(goc, ROOT), goc)

    def test_ham_khong_co_lenh_thi_khong_dong_toi(self):
        self.assertEqual(tdq_state.lenh_cho_project("không có lệnh nào", self.cwd),
                         "không có lệnh nào")
        self.assertEqual(tdq_state.lenh_cho_project("", self.cwd), "")

    def test_ham_nhieu_lenh_moi_lenh_deu_doi(self):
        ra = tdq_state.lenh_cho_project(
            "python3 scripts/tdq_team.py assign rồi python3 scripts/tdq_state.py next", self.cwd)
        self.khong_con_tuong_doi(ra)
        self.assertEqual(len(self.duong_dan_trong(ra)), 2)


class NextVaState(BaseProjectKhac):
    def test_next_project_khac_lenh_chay_duoc(self):
        """Đo trên CLI `next` thật — `render_next` cố ý trả dạng tương đối cho người gọi tự cắt
        trần trước, rồi mới đổi đường dẫn (xem chú thích trong `render_next`)."""
        import subprocess
        ra = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "tdq_state.py"), "next"],
                            capture_output=True, encoding="utf-8",
                            env=dict(os.environ, TDQ_PROJECT_DIR=self.cwd, TDQ_LOG="0")).stdout
        self.assertIn("Command:", ra)
        self.khong_con_tuong_doi(ra)
        for d in self.duong_dan_trong(ra):
            self.assertTrue(os.path.isfile(d), d)

    def test_next_render_next_giu_tuong_doi_de_cat_tran(self):
        self.assertIn("python3 scripts/", tdq_state.render_next(self.cwd, None))

    def test_next_state_md_project_khac(self):
        ra = tdq_state.render_state_md(self.cwd, None)
        self.khong_con_tuong_doi(ra)


class Hook(BaseProjectKhac):
    def test_hook_bash_gate_nhac_state_chay_duoc(self):
        """`[TDQ:STATE]` dạy agent dùng CLI — ở project khác CLI đó phải là đường dẫn thật."""
        payload = {"session_id": "thu-duong-dan", "cwd": self.cwd, "tool_name": "Bash",
                   "tool_input": {"command": "echo '{}' > docs/tdq/state.json"}}
        rc, out, _ = run_hook("bash_gate.py", payload,
                              env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})
        self.assertEqual(rc, 0)
        nhac = (json.loads(out).get("hookSpecificOutput") or {}).get("additionalContext", "")
        self.assertIn("TDQ:STATE", nhac)
        self.khong_con_tuong_doi(nhac)
        for d in self.duong_dan_trong(nhac):
            self.assertTrue(os.path.isfile(d), d)

    def test_hook_session_start_project_khac(self):
        payload = {"session_id": "thu-duong-dan", "cwd": self.cwd,
                   "hook_event_name": "SessionStart"}
        rc, out, _ = run_hook("session_start.py", payload,
                              env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})
        self.assertEqual(rc, 0)
        self.khong_con_tuong_doi(out)


if __name__ == "__main__":
    unittest.main()
