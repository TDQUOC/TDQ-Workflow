"""Chuỗi pha sau khi gỡ pha `diagram` khỏi quy trình.

Bất biến khoá ở đây:
1. `diagram` không còn là pha hợp lệ: không nằm trong `VALID_PHASES`, không nằm
   trong `PHASE_ORDER`, và `set phase=diagram` bị từ chối.
2. Thứ tự pha là `idle → analyze → spec → plan → mode → implement → qc → report`,
   `spec` đứng ngay trước `plan`.
3. Cổng vào pha `plan` chỉ đòi `spec_approved = true`, không đòi sơ đồ nào.
4. State cũ ghi lúc còn pha `diagram` vẫn nạp được: pha tự nâng về `spec` kèm
   cảnh báo thay vì văng lỗi.
"""
import json
import os
import tempfile
import unittest

from helper import run_state_cli, tdq_state


def doc_state(cwd):
    with open(os.path.join(cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
        return json.load(f)


def ghi_state(cwd, state):
    duong = os.path.join(cwd, "docs", "tdq", "state.json")
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def mo_request(cwd, lane="chuyen-sau"):
    ma, _, err = run_state_cli(cwd, "init", "2026-09-01-1800-bo-so-do", lane)
    assert ma == 0, err


class PhaMoiTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_diagram_khong_con_la_pha_hop_le(self):
        self.assertNotIn("diagram", tdq_state.VALID_PHASES)
        self.assertNotIn("diagram", tdq_state.PHASE_ORDER)
        self.assertNotIn("diagram", tdq_state.PHASE_TABLE)

    def test_set_phase_diagram_bi_tu_choi(self):
        mo_request(self.cwd)
        ma, out, err = run_state_cli(self.cwd, "set", "phase=diagram")
        self.assertNotEqual(ma, 0, "đặt pha diagram phải bị từ chối")
        self.assertIn("removed", (out + err).lower(),
                      "thông điệp phải nói rõ pha đã bị gỡ")

    def test_thu_tu_pha_khong_con_diagram(self):
        self.assertEqual(
            tdq_state.PHASE_ORDER,
            ["no_state", "analyze", "spec", "plan", "mode", "implement", "qc",
             "report", "idle", "quick_analyze", "quick"])

    def test_cong_plan_chi_doi_spec_duyet(self):
        mo_request(self.cwd)
        ma, _, err = run_state_cli(self.cwd, "set", "phase=spec")
        self.assertEqual(ma, 0, err)
        ma, _, err = run_state_cli(self.cwd, "set",
                                   "spec_file=docs/tdq/spec/x.md")
        self.assertEqual(ma, 0, err)
        ma, _, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        self.assertEqual(ma, 0, err)
        ma, out, err = run_state_cli(self.cwd, "set", "phase=plan")
        self.assertEqual(ma, 0, f"vào pha plan chỉ cần spec duyệt: {out}{err}")
        self.assertEqual(doc_state(self.cwd)["phase"], "plan")

    def test_vao_plan_khong_con_doi_so_do(self):
        """Cổng này từng chặn vì danh sách sơ đồ rỗng — nay chỉ còn lý do spec."""
        mo_request(self.cwd)
        ma, _, _ = run_state_cli(self.cwd, "set", "phase=spec")
        self.assertEqual(ma, 0)
        ma, out, err = run_state_cli(self.cwd, "set", "phase=plan")
        self.assertNotEqual(ma, 0, "spec chưa duyệt thì vẫn phải chặn")
        self.assertNotIn("diagram", (out + err).lower(),
                         "lý do chặn phải là spec, không phải sơ đồ")

    def test_vao_plan_bi_chan_khi_spec_chua_duyet(self):
        """Nhánh nghịch của cổng `plan`.

        Nhánh cũ chỉ soi danh sách sơ đồ; gỡ pha sơ đồ mà không thay thế thì cổng
        rỗng, plan viết được trước khi user duyệt spec — đúng rủi ro spec đã nêu.
        """
        mo_request(self.cwd)
        for pair in ("phase=spec", "spec_file=docs/tdq/spec/x.md"):
            ma, _, err = run_state_cli(self.cwd, "set", pair)
            self.assertEqual(ma, 0, err)
        ma, out, err = run_state_cli(self.cwd, "set", "phase=plan")
        self.assertNotEqual(ma, 0, "spec chưa duyệt mà vào được plan là thủng cổng")
        self.assertIn("spec", (out + err).lower())
        self.assertEqual(doc_state(self.cwd)["phase"], "spec")


class StateCuTest(unittest.TestCase):
    """State ghi từ thời còn pha `diagram` phải nạp được, không văng lỗi."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def _state_cu(self, phase):
        mo_request(self.cwd)
        state = doc_state(self.cwd)
        state["phase"] = phase
        state["diagrams"] = [{"file": "docs/tdq/mind-map/dang-nhap.md",
                              "approved": True,
                              "approved_at": "2026-08-23T10:00:00+07:00",
                              "approved_by": "duyệt sơ đồ"}]
        ghi_state(self.cwd, state)

    def test_phase_cu_diagram_tu_nang_ve_spec(self):
        self._state_cu("diagram")
        ma, out, err = run_state_cli(self.cwd, "get", "phase")
        self.assertEqual(ma, 0, err)
        self.assertEqual(out.strip(), "spec")

    def test_phase_cu_diagram_co_canh_bao(self):
        self._state_cu("diagram")
        ma, out, err = run_state_cli(self.cwd, "next")
        self.assertEqual(ma, 0, err)
        self.assertIn("diagram", (out + err).lower(),
                      "phải nói rõ pha diagram cũ đã được nâng về spec")

    def test_state_cu_co_khoa_diagrams_van_chay(self):
        self._state_cu("spec")
        ma, out, err = run_state_cli(self.cwd, "next")
        self.assertEqual(ma, 0, err)
        self.assertNotIn("Diagrams", out)

    def test_ghi_lai_state_thi_khoa_diagrams_bien_mat(self):
        self._state_cu("spec")
        ma, _, err = run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/x.md")
        self.assertEqual(ma, 0, err)
        self.assertNotIn("diagrams", doc_state(self.cwd))


if __name__ == "__main__":
    unittest.main()
