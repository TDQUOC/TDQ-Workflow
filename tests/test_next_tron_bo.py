"""`next` ở implement/qc nhắc chạy `vung-cham` khi số lần trọn bộ của request vượt ngân sách.

Ngân sách lấy từ `tdq_test.dem`: 2, hoặc 3 khi request đã có một lần trọn bộ đỏ.
Chỉ nhắc, không chặn; sổ hỏng/thiếu → im lặng, không bao giờ vỡ `next`.
"""
import json
import os
import tempfile
import unittest

from helper import read_state, run_state_cli, write_state
import tdq_state

REQ = "2026-10-03-1907-demo"
DAU_HIEU = "vung-cham; the full suite belongs to the QC gates"   # CLI đổi đường dẫn thành tuyệt đối


def _dong(ok=True, request=REQ):
    return {"ts": "2026-10-05T10:00:00+07:00", "kind": "tron-bo", "request": request,
            "phase": "implement", "ok": ok, "seconds": 1.0, "failed_modules": []}


class NextNhacTronBo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _state(self, phase):
        write_state(self.cwd, active_request=REQ, lane="full", phase=phase)
        return read_state(self.cwd)

    def _so(self, rows=None, raw=None):
        path = os.path.join(self.cwd, "docs", "tdq", ".tdq-test.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            if raw is not None:
                f.write(raw)
            for row in rows or []:
                f.write(json.dumps(row) + "\n")

    def _next(self, *args):
        rc, out, err = run_state_cli(self.cwd, "next", *args)
        self.assertEqual(rc, 0, err)
        return out

    def test_vuot_ngan_sach_o_implement_co_dong_nhac(self):
        self._state("implement")
        self._so([_dong(), _dong(), _dong()])
        out = self._next()
        self.assertIn(DAU_HIEU, out)
        self.assertIn("ran 3 times", out)
        self.assertIn("budget 2", out)

    def test_vuot_ngan_sach_o_qc_co_dong_nhac(self):
        self._state("qc")
        self._so([_dong(), _dong(), _dong()])
        self.assertIn(DAU_HIEU, self._next())

    def test_bang_ngan_sach_thi_im(self):
        self._state("implement")
        self._so([_dong(), _dong()])
        self.assertNotIn(DAU_HIEU, self._next())

    def test_dong_cua_request_khac_khong_tinh(self):
        self._state("implement")
        self._so([_dong(), _dong(request="khac"), _dong(request="khac")])
        self.assertNotIn(DAU_HIEU, self._next())

    def test_phase_spec_thi_im(self):
        self._state("spec")
        self._so([_dong()] * 5)
        self.assertNotIn(DAU_HIEU, self._next())

    def test_lan_do_nang_ngan_sach_len_3(self):
        self._state("qc")
        self._so([_dong(ok=False), _dong(), _dong()])
        self.assertNotIn(DAU_HIEU, self._next())
        self._so([_dong(ok=False), _dong(), _dong(), _dong()])
        out = self._next()
        self.assertIn(DAU_HIEU, out)
        self.assertIn("budget 3", out)

    def test_brief_van_mot_dong(self):
        self._state("implement")
        self._so([_dong()] * 3)
        out = self._next("--brief")
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertIn("full suite 3/2", out)

    def test_brief_chua_vuot_khong_co_dau(self):
        self._state("implement")
        self._so([_dong()])
        self.assertNotIn("full suite", self._next("--brief"))

    def test_compact_van_nhac(self):
        state = self._state("implement")
        self._so([_dong()] * 3)
        out = tdq_state.render_next(self.cwd, state, compact=True)
        self.assertIn("full suite 3/2", out)

    def test_khong_co_so_thi_im(self):
        self._state("implement")
        self.assertNotIn(DAU_HIEU, self._next())

    def test_so_hong_khong_vo(self):
        self._state("implement")
        self._so(raw="{khong phai json\n[1,2]\n\x00\x01\n")
        self.assertNotIn(DAU_HIEU, self._next())

    def test_so_la_thu_muc_khong_vo(self):
        state = self._state("implement")
        os.makedirs(os.path.join(self.cwd, "docs", "tdq", ".tdq-test.jsonl"))
        out = tdq_state.render_next(self.cwd, state)
        self.assertNotIn(DAU_HIEU, out)

    def test_loi_doc_bat_ky_thi_im(self):
        state = self._state("implement")
        self._so([_dong()] * 3)
        import tdq_test
        goc = tdq_test._doc_so

        def hong(repo):
            raise RuntimeError("boom")
        tdq_test._doc_so = hong
        try:
            out = tdq_state.render_next(self.cwd, state)
        finally:
            tdq_test._doc_so = goc
        self.assertNotIn(DAU_HIEU, out)


if __name__ == "__main__":
    unittest.main()
