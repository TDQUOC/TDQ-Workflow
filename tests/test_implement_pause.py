"""The declared pause of phase `implement`: state key + the tam-hoan/tiep-tuc CLI."""
import tempfile
import unittest

from helper import read_state, run_state_cli, write_state
import tdq_state


class TestImplementPauseKey(unittest.TestCase):
    def test_default_state_carries_the_key_empty(self):
        state = tdq_state.default_state()
        self.assertIn("implement_pause", state)
        self.assertIsNone(state["implement_pause"])

    def test_loai_dung_lists_exactly_four_kinds(self):
        self.assertEqual(set(tdq_state.LOAI_DUNG),
                         {"mat-truy-cap", "pha-huy", "dau-vao-user", "tran-qc"})


class TestPauseCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        write_state(self.cwd, active_request="2026-08-24-1427-demo",
                    lane="full", phase="implement")

    def tearDown(self):
        self._tmp.cleanup()

    def test_tam_hoan_ghi_ly_do(self):
        rc, _, _ = run_state_cli(self.cwd, "tam-hoan", "--loai", "mat-truy-cap",
                                 "--ly-do", "thiếu quyền ghi ổ đĩa")
        self.assertEqual(rc, 0)
        pause = read_state(self.cwd)["implement_pause"]
        self.assertEqual(pause["ly_do"], "thiếu quyền ghi ổ đĩa")
        self.assertEqual(pause["loai"], "mat-truy-cap")
        self.assertTrue(pause["at"])
        self.assertEqual(pause["by"], "claude")

    def test_bon_loai_deu_duoc_nhan_va_luu(self):
        for loai in ("mat-truy-cap", "pha-huy", "dau-vao-user", "tran-qc"):
            with self.subTest(loai=loai):
                rc, _, err = run_state_cli(self.cwd, "pause", "--loai", loai,
                                           "--ly-do", f"ly do {loai}")
                self.assertEqual(rc, 0, err)
                pause = read_state(self.cwd)["implement_pause"]
                self.assertEqual(pause["loai"], loai)
                self.assertEqual(pause["ly_do"], f"ly do {loai}")

    def test_thu_tu_co_tuy_y(self):
        rc, _, err = run_state_cli(self.cwd, "pause", "--ly-do", "vong QC thu 3",
                                   "--loai", "tran-qc")
        self.assertEqual(rc, 0, err)
        pause = read_state(self.cwd)["implement_pause"]
        self.assertEqual(pause["loai"], "tran-qc")
        self.assertEqual(pause["ly_do"], "vong QC thu 3")

    def test_tam_hoan_thieu_ly_do_thoat_khac_0(self):
        rc, _, _ = run_state_cli(self.cwd, "tam-hoan")
        self.assertNotEqual(rc, 0)
        self.assertIsNone(read_state(self.cwd)["implement_pause"])

    def test_thieu_ly_do_co_loai_bi_tu_choi(self):
        rc, _, _ = run_state_cli(self.cwd, "pause", "--loai", "pha-huy")
        self.assertNotEqual(rc, 0)
        self.assertIsNone(read_state(self.cwd)["implement_pause"])

    def test_thieu_loai_bi_tu_choi_state_giu_nguyen(self):
        before = read_state(self.cwd)
        rc, _, err = run_state_cli(self.cwd, "pause", "--ly-do", "nguong spec khong dat")
        self.assertNotEqual(rc, 0)
        self.assertEqual(read_state(self.cwd), before)
        for loai in tdq_state.LOAI_DUNG:
            self.assertIn(loai, err)
        self.assertIn("lech add", err)

    def test_doi_spec_bi_tu_choi_va_chi_sang_lech_add(self):
        before = read_state(self.cwd)
        rc, _, err = run_state_cli(self.cwd, "pause", "--loai", "doi-spec",
                                   "--ly-do", "nguong p95 khong dat, hoi user")
        self.assertNotEqual(rc, 0)
        self.assertEqual(read_state(self.cwd), before)
        self.assertIn("lech add", err)
        for loai in tdq_state.LOAI_DUNG:
            self.assertIn(loai, err)

    def test_tiep_tuc_xoa_khoa(self):
        run_state_cli(self.cwd, "tam-hoan", "--loai", "dau-vao-user",
                      "--ly-do", "chờ khoá API của user")
        rc, _, _ = run_state_cli(self.cwd, "tiep-tuc")
        self.assertEqual(rc, 0)
        self.assertIsNone(read_state(self.cwd)["implement_pause"])


class TestPhaseTableWording(unittest.TestCase):
    def test_implement_forbidden_names_loai_and_lech_add(self):
        text = tdq_state.PHASE_TABLE["implement"]["forbidden"]
        self.assertIn("pause --loai", text)
        self.assertIn("lech add", text)
        for loai in tdq_state.LOAI_DUNG:
            self.assertIn(loai, text)


if __name__ == "__main__":
    unittest.main()
