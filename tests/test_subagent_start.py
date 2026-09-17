"""T3.3 (2026-09-17) — kênh sub-agent: bơm thân luật gọn vào đầu hội thoại trợ lý.

Kênh này là LỜI NHẮC, không phải hàng rào: issue #23885 đo được `additionalContext` của
sub-agent bị prune, non-compliance 40–60%. Nên test khoá hai chuyện khác nhau:
1. Có bơm thật (đúng nội dung, đúng mức `muc_gat`, đúng một dòng log).
2. Không bao giờ CHẶN: payload thiếu khoá, state hỏng, không có request nào mở → in rỗng
   và **thoát mã 0**.
"""
import json
import os
import tempfile
import unittest

from helper import run_hook, write_state

MOC = "[TDQ:GON]"


class TestKenhSubagent(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def state(self, **thay):
        write_state(self.cwd, active_request="2026-09-16-2234-cong-sinh-ponytail-tdq",
                    lane="full", phase="implement", spec_approved=True, plan_approved=True,
                    implement_mode="subagent", spec_file="docs/tdq/spec/x.md",
                    plan_file="docs/tdq/plan/x.md", **thay)

    def chay(self, session="sa1", **payload):
        goi = {"hook_event_name": "SubagentStart", "cwd": self.cwd,
               "session_id": session, "agent_type": "tdq-implementer"}
        goi.update(payload)
        return run_hook("subagent_start.py", goi)

    def test_bom_than_luat(self):
        self.state()
        rc, out, _err = self.chay()
        self.assertEqual(rc, 0)
        self.assertIn(MOC, out)
        # Nội dung thật của thân luật, không phải một câu tóm tắt
        self.assertIn("| 1 |", out)

    def test_muc_off_thi_im_lang_nhung_van_thoat_0(self):
        self.state(muc_gat="off")
        rc, out, _err = self.chay()
        self.assertEqual(rc, 0)
        self.assertNotIn(MOC, out)

    def test_lite_ngan_hon_full_ngan_hon_ultra(self):
        dai = {}
        for muc in ("lite", "full", "ultra"):
            self.state(muc_gat=muc)
            _rc, out, _err = self.chay(session=f"sa-{muc}")
            dai[muc] = len(out)
        self.assertLess(dai["lite"], dai["full"])
        self.assertLess(dai["full"], dai["ultra"])

    def test_payload_thieu_khoa_van_thoat_0(self):
        """Fail-open: thiếu khoá nào cũng không được chặn lượt của trợ lý."""
        self.state()
        for goi in ({}, {"cwd": self.cwd}, {"session_id": "x"},
                    {"cwd": None, "session_id": None}):
            with self.subTest(goi=goi):
                rc, _out, _err = run_hook("subagent_start.py", goi)
                self.assertEqual(rc, 0)

    def test_khong_co_request_mo_van_thoat_0(self):
        rc, _out, _err = self.chay(session="sa-rong")
        self.assertEqual(rc, 0)

    def test_state_hong_van_thoat_0(self):
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w",
                  encoding="utf-8") as f:
            f.write("{khong phai json")
        rc, _out, _err = self.chay(session="sa-hong")
        self.assertEqual(rc, 0)

    def test_ghi_dung_mot_dong_log(self):
        self.state()
        self.chay()
        with open(os.path.join(self.cwd, "docs", "tdq", ".tdq-turn.jsonl"),
                  encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        gon = [r for r in rows if r.get("code") == "TDQ:GON"]
        self.assertEqual(len(gon), 1, f"kênh sub-agent phải ghi đúng một dòng log: {rows}")
        self.assertEqual(gon[0].get("event"), "SubagentStart")

    def test_noi_ro_la_loi_nhac_khong_phai_hang_rao(self):
        """Docstring phải nói thẳng giới hạn của kênh, để người sau không tin nó là cổng."""
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "hooks", "scripts", "subagent_start.py")
        with open(path, encoding="utf-8") as f:
            doc = f.read().split('"""')[1].lower()
        self.assertIn("reminder", doc)
        self.assertIn("not a fence", doc)
        self.assertIn("23885", doc)


class TestKhaiTrongHooksJson(unittest.TestCase):
    """`hooks.json` phải khai kênh mới: 6 mục trên 5 sự kiện."""

    def setUp(self):
        goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(goc, "hooks", "hooks.json"), encoding="utf-8") as f:
            self.cfg = json.load(f)["hooks"]

    def test_co_su_kien_subagent_start(self):
        self.assertIn("SubagentStart", self.cfg)

    def test_dung_6_muc_tren_5_su_kien(self):
        self.assertEqual(len(self.cfg), 5, sorted(self.cfg))
        muc = sum(len(nhom["hooks"]) for ds in self.cfg.values() for nhom in ds)
        self.assertEqual(muc, 6, self.cfg)

    def test_tro_dung_file(self):
        cmd = self.cfg["SubagentStart"][0]["hooks"][0]["command"]
        self.assertIn("subagent_start.py", cmd)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", cmd)


if __name__ == "__main__":
    unittest.main()
