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


class TestPauseCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        write_state(self.cwd, active_request="2026-08-24-1427-demo",
                    lane="full", phase="implement")

    def tearDown(self):
        self._tmp.cleanup()

    def test_tam_hoan_ghi_ly_do(self):
        rc, _, _ = run_state_cli(self.cwd, "tam-hoan", "--ly-do", "thiếu quyền ghi ổ đĩa")
        self.assertEqual(rc, 0)
        pause = read_state(self.cwd)["implement_pause"]
        self.assertEqual(pause["ly_do"], "thiếu quyền ghi ổ đĩa")
        self.assertTrue(pause["at"])

    def test_tam_hoan_thieu_ly_do_thoat_khac_0(self):
        rc, _, _ = run_state_cli(self.cwd, "tam-hoan")
        self.assertNotEqual(rc, 0)
        self.assertIsNone(read_state(self.cwd)["implement_pause"])

    def test_tiep_tuc_xoa_khoa(self):
        run_state_cli(self.cwd, "tam-hoan", "--ly-do", "chờ khoá API của user")
        rc, _, _ = run_state_cli(self.cwd, "tiep-tuc")
        self.assertEqual(rc, 0)
        self.assertIsNone(read_state(self.cwd)["implement_pause"])


if __name__ == "__main__":
    unittest.main()
