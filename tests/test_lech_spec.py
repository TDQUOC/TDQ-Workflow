"""Lệch spec: khoá state `lech_spec` + lệnh `lech add/list/duyet/bac` (Q8 vòng đời lệch)."""
import json
import os
import tempfile
import unittest

from helper import read_state, run_state_cli, write_state
import tdq_state
import tdq_ten_lenh

THEM = ("lech", "add", "--q", "Q3", "--nguong", "installer <= 200 MB",
        "--do", "232 MB", "--chon", "keep the bundled runtime",
        "--ly-do", "stripping it breaks offline install")


class _CoState(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        write_state(self.cwd, active_request="2026-10-03-0732-demo",
                    lane="full", phase="implement")

    def tearDown(self):
        self._tmp.cleanup()

    def lech(self):
        return read_state(self.cwd)["lech_spec"]


class TestKhoaState(unittest.TestCase):
    def test_default_state_co_danh_sach_rong(self):
        self.assertEqual(tdq_state.default_state()["lech_spec"], [])

    def test_lech_cho_loc_dung_muc_dang_cho(self):
        state = {"lech_spec": [{"id": 1, "trang_thai": "cho"},
                               {"id": 2, "trang_thai": "duyet"},
                               {"id": 3, "trang_thai": "cho"}]}
        self.assertEqual([m["id"] for m in tdq_state.lech_cho(state)], [1, 3])

    def test_lech_cho_chiu_state_cu_thieu_khoa(self):
        self.assertEqual(tdq_state.lech_cho({}), [])
        self.assertEqual(tdq_state.lech_cho({"lech_spec": None}), [])


class TestVongDoi(_CoState):
    def test_add_list_duyet(self):
        rc, out, err = run_state_cli(self.cwd, *THEM)
        self.assertEqual(rc, 0, err)
        self.assertIn("1", out)
        muc = self.lech()[0]
        self.assertEqual(muc["id"], 1)
        self.assertEqual(muc["q"], "Q3")
        self.assertEqual(muc["nguong"], "installer <= 200 MB")
        self.assertEqual(muc["do"], "232 MB")
        self.assertEqual(muc["chon"], "keep the bundled runtime")
        self.assertEqual(muc["ly_do"], "stripping it breaks offline install")
        self.assertEqual(muc["trang_thai"], "cho")
        self.assertEqual(muc["by"], "claude")
        self.assertTrue(muc["at"])

        rc, out, _ = run_state_cli(self.cwd, "lech", "list")
        self.assertEqual(rc, 0)
        self.assertIn("Q3", out)
        self.assertIn("cho", out)

        rc, _, err = run_state_cli(self.cwd, "lech", "duyet", "1", "--by", "ok, 232 MB là được")
        self.assertEqual(rc, 0, err)
        muc = self.lech()[0]
        self.assertEqual(muc["trang_thai"], "duyet")
        self.assertEqual(muc["quyet_by"], "ok, 232 MB là được")
        self.assertTrue(muc["quyet_at"])
        self.assertEqual(tdq_state.lech_cho(read_state(self.cwd)), [])

    def test_bac(self):
        run_state_cli(self.cwd, *THEM)
        rc, _, err = run_state_cli(self.cwd, "lech", "bac", "1", "--by", "không, phải dưới 200")
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.lech()[0]["trang_thai"], "bac")

    def test_id_tang_dan_on_dinh(self):
        run_state_cli(self.cwd, *THEM)
        rc, out, _ = run_state_cli(self.cwd, *THEM)
        self.assertEqual(rc, 0)
        self.assertEqual([m["id"] for m in self.lech()], [1, 2])
        self.assertIn("2", out)

    def test_list_json(self):
        run_state_cli(self.cwd, *THEM)
        rc, out, _ = run_state_cli(self.cwd, "lech", "list", "--json")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["q"], "Q3")

    def test_list_rong(self):
        rc, out, _ = run_state_cli(self.cwd, "lech", "list")
        self.assertEqual(rc, 0)
        self.assertIn("no spec deviation recorded", out)
        rc, out, _ = run_state_cli(self.cwd, "lech", "list", "--json")
        self.assertEqual(json.loads(out), [])

    def test_quyet_lai_duoc_nhung_co_ghi_chu(self):
        run_state_cli(self.cwd, *THEM)
        run_state_cli(self.cwd, "lech", "duyet", "1", "--by", "ok")
        rc, out, err = run_state_cli(self.cwd, "lech", "bac", "1", "--by", "đổi ý")
        self.assertEqual(rc, 0, err)
        self.assertIn("already", (out + err).lower())
        self.assertEqual(self.lech()[0]["trang_thai"], "bac")

    def test_bi_danh_lech_spec(self):
        self.assertEqual(tdq_ten_lenh.giai_ten(
            "lech-spec", tdq_ten_lenh.BANG_DOI_TEN["tdq_state.py"]), "lech")
        rc, _, err = run_state_cli(self.cwd, "lech-spec", *THEM[1:])
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.lech()), 1)


class TestLoiCuPhap(_CoState):
    def _sai(self, *args):
        rc, _, _ = run_state_cli(self.cwd, *args)
        self.assertNotEqual(rc, 0, args)

    def test_add_thieu_truong(self):
        for bo in ("--q", "--nguong", "--do", "--chon", "--ly-do"):
            args = list(THEM)
            i = args.index(bo)
            del args[i:i + 2]
            self._sai(*args)
        self.assertEqual(self.lech(), [])

    def test_add_q_sai_khuon(self):
        args = list(THEM)
        args[args.index("--q") + 1] = "3"
        self._sai(*args)
        self.assertEqual(self.lech(), [])

    def test_duyet_thieu_by(self):
        run_state_cli(self.cwd, *THEM)
        self._sai("lech", "duyet", "1")
        self.assertEqual(self.lech()[0]["trang_thai"], "cho")

    def test_id_khong_ton_tai(self):
        self._sai("lech", "duyet", "9", "--by", "ok")
        self._sai("lech", "bac", "abc", "--by", "ok")

    def test_lenh_con_la(self):
        self._sai("lech", "xoa", "1")
        self._sai("lech")


class TestLog(_CoState):
    """Chọn bằng `-k log`: mỗi lệnh ghi một dòng có mốc ISO ra stderr; TDQ_LOG=0 tắt."""

    def test_log_mot_dong_iso(self):
        _, _, err = run_state_cli(self.cwd, *THEM)
        dong = [d for d in err.splitlines() if "deviation" in d]
        self.assertEqual(len(dong), 1, err)
        self.assertRegex(dong[0], r"^\[\d{4}-\d{2}-\d{2}T")

    def test_log_tat_bang_tdq_log_0(self):
        cu = os.environ.get("TDQ_LOG")
        os.environ["TDQ_LOG"] = "0"
        try:
            rc, _, err = run_state_cli(self.cwd, *THEM)
        finally:
            if cu is None:
                os.environ.pop("TDQ_LOG", None)
            else:
                os.environ["TDQ_LOG"] = cu
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
