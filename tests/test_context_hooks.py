"""session_start.py + prompt_context.py (0.3.0) — bơm context theo state."""
import datetime
import json
import tempfile
import unittest

import importlib.util
import os

from helper import (HOOKS, run_hook, load_fixture, write_state, write_file,
                    tdq_state)


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# 2026-09-17 (T3.1): session_start bơm thêm KHỐI THÂN LUẬT sau khối đầu, nên trần
# 12 dòng / 600 ký tự của spec §2.7 đo trên KHỐI ĐẦU chứ không phải toàn đầu ra — số trần
# không đổi một đơn vị nào, chỉ đổi chỗ đo. Trần toàn đầu ra khai riêng: 160 dòng / 8200 ký tự
# (2026-09-17, sửa số ƯỚC 140/7000 của chính plan sau khi đo — lý do ghi ở test_tran_toan_dau_ra).
MOC_LUAT = "[TDQ:GON]"


def khoi_dau(out):
    """Phần trước mốc thân luật — chỗ duy nhất trần 12/600 áp vào."""
    return out.split(MOC_LUAT, 1)[0].rstrip()


class TestSessionStart(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_active_request_prints_next_and_rule(self):
        write_state(self.cwd, active_request="2026-07-27-0900-demo", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd, "session_id": "s1"})
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:NEXT]", out)
        self.assertIn("2026-07-27-0900-demo", out)
        self.assertIn("Next:", out)
        self.assertIn("[TDQ] Rule", out)          # instruction: nghe theo mã của hook
        self.assertLessEqual(len(khoi_dau(out).splitlines()), 12)   # trần spec §2.7
        self.assertLessEqual(len(khoi_dau(out)), 600)   # 2026-09-17: đo trên khối đầu

    def test_never_truncated_in_any_phase(self):
        """Trần 600 ký tự không được cắt mất dòng luật hay dòng lệnh."""
        for phase in ("analyze", "spec", "plan", "implement", "qc", "report"):
            with self.subTest(phase=phase):
                write_state(self.cwd, active_request="2026-07-27-0900-mot-request-ten-kha-dai",
                            lane="full", phase=phase, spec_approved=True, plan_approved=True,
                            spec_file="docs/tdq/spec/x.md", plan_file="docs/tdq/plan/x.md")
                rc, out, _ = run_hook("session_start.py",
                                      {"cwd": self.cwd, "session_id": f"s1-{phase}"})
                dau = khoi_dau(out)
                self.assertNotIn("…", dau, phase)
                self.assertIn("[TDQ] Rule", dau)
                self.assertIn("Command:", dau)
                self.assertIn("Done when:", dau)
                # 2026-09-17: trần giữ nguyên 600/12, chỉ đo trên khối đầu (xem khoi_dau).
                self.assertLessEqual(len(dau), 600, phase)
                self.assertLessEqual(len(dau.splitlines()), 12, phase)

    def test_no_state_still_guides(self):
        rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd, "session_id": "s1"})
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:NEXT]", out)          # chưa có request → hướng dẫn mở request
        self.assertLessEqual(len(khoi_dau(out).splitlines()), 12)


class TestThanLuatKenhPhien(unittest.TestCase):
    """T3.1 — kênh phiên bơm thân luật tinh gọn đã lọc theo `muc_gat`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        self.n = 0

    def chay(self, source="startup", **state):
        """Chạy hook một lần với session_id mới, trả về đầu ra."""
        write_state(self.cwd, active_request="2026-09-17-0900-demo", lane="full",
                    phase="implement", spec_approved=True, plan_approved=True,
                    spec_file="docs/tdq/spec/x.md", plan_file="docs/tdq/plan/x.md",
                    **state)
        self.n += 1
        _, out, _ = run_hook("session_start.py", {
            "cwd": self.cwd, "session_id": f"g{self.n}", "source": source})
        return out

    def test_moi_source_deu_co_than_luat(self):
        for source in ("startup", "resume", "compact"):
            with self.subTest(source=source):
                out = self.chay(source)
                self.assertIn(MOC_LUAT, out, "thiếu mốc thân luật")
                self.assertIn("| 7 |", out, "thân luật thiếu bậc 7")
                self.assertIn("Make it run first", out, "thân luật thiếu món 8")

    def test_muc_off_thi_khong_bom_than_luat(self):
        out = self.chay(muc_gat="off")
        self.assertNotIn(MOC_LUAT, out, "`off` thì không kênh nào được bơm luật")
        self.assertIn("[TDQ] Rule", out, "khối đầu vẫn phải còn")

    def test_lite_ngan_hon_full_ngan_hon_ultra(self):
        dai = {}
        for muc in ("lite", "full", "ultra"):
            dai[muc] = len(self.chay(muc_gat=muc))
        self.assertLess(dai["lite"], dai["full"])
        self.assertLess(dai["full"], dai["ultra"])

    def test_tran_toan_dau_ra(self):
        # 2026-09-17 (T3.1, LỖI PLAN của tôi — cùng loại quy tắc 10): plan khai trần toàn
        # đầu ra 140 dòng / 7000 ký tự khi thân luật CHƯA tồn tại, tức là số ước chứ không
        # phải số đo. Đo thật thân luật đã lọc: `lite` 72 dòng/4404 ký tự · `full`
        # 133/6887 · `ultra` 139/7123; cộng khối đầu (≤ 12 dòng/600 ký tự) và dòng tiêu đề
        # `[TDQ:GON]` thì `full` ≈ 146/7590 và `ultra` ≈ 152/7830 — ở 140/7000 cả hai bị cắt
        # đuôi, mất đúng mấy bậc cuối của cái thang. soul.md:101: trần là ràng buộc bậc 3,
        # luật là bậc 1 → nâng trần lên 160/8200, cấm nén luật cho vừa trần.
        for muc in ("lite", "full", "ultra"):
            with self.subTest(muc=muc):
                out = self.chay(muc_gat=muc)
                self.assertLessEqual(len(out.splitlines()), 160)
                self.assertLessEqual(len(out), 8200)

    def test_khoi_dau_van_trong_tran_cu(self):
        dau = khoi_dau(self.chay())
        self.assertLessEqual(len(dau.splitlines()), 12)
        self.assertLessEqual(len(dau), 600)

    def test_ghi_mot_dong_log_kenh(self):
        self.chay()
        with open(os.path.join(self.cwd, "docs", "tdq", ".tdq-turn.jsonl"),
                  encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        gon = [r for r in rows if r.get("code") == "TDQ:GON"]
        self.assertEqual(len(gon), 1, f"kênh phiên phải ghi đúng một dòng log: {rows}")

    def test_goi_hai_lan_cung_luot_chi_bom_mot_lan(self):
        """T3.4 — bug #10871: hook plugin chạy hai lần với hai PID trong cùng một lượt."""
        write_state(self.cwd, active_request="2026-09-17-0900-demo", lane="full",
                    phase="implement")
        payload = {"cwd": self.cwd, "session_id": "dup1", "source": "startup"}
        lan1 = run_hook("session_start.py", payload)[1]
        lan2 = run_hook("session_start.py", payload)[1]
        self.assertIn(MOC_LUAT, lan1)
        self.assertNotIn(MOC_LUAT, lan2, "lần hai trong cùng lượt không được bơm lại")
        self.assertIn("[TDQ] Rule", lan2, "khối đầu thì lần nào cũng phải có")


class TestTruncation(unittest.TestCase):
    """A22 — cắt MAX_CHARS không được đứt giữa inline-code (nửa lệnh = lệnh sai)."""

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, HOOKS)  # prompt_context import _common cạnh nó
        cls.addClassCleanup(sys.path.remove, HOOKS)
        spec = importlib.util.spec_from_file_location(
            "prompt_context_mod", os.path.join(HOOKS, "prompt_context.py"))
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_truncate_backs_off_before_open_backtick(self):
        text = ("x" * 230
                + " chạy `python3 scripts/tdq_state.py approve spec` xong")
        out = self.mod._truncate(text)
        self.assertLessEqual(len(out), 240)
        self.assertEqual(out.count("`") % 2, 0, out)
        self.assertNotIn("`python3", out)

    def test_truncate_short_text_untouched(self):
        self.assertEqual(self.mod._truncate("ngắn"), "ngắn")

    def test_truncate_outside_inline_code_keeps_closed_span(self):
        text = "`cmd ok` " + "y" * 300
        out = self.mod._truncate(text)
        self.assertLessEqual(len(out), 240)
        self.assertIn("`cmd ok`", out)


class TestPromptContext(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def ctx(self, prompt="tiếp tục", session="s1"):
        payload = load_fixture("prompt.json", cwd=self.cwd, session_id=session)
        payload["prompt"] = prompt
        return run_hook("prompt_context.py", payload)

    def assert_budget(self, out):
        self.assertLessEqual(len(out.splitlines()), 3)
        self.assertLessEqual(len(out), 240)

    def test_repeated_identical_next_only_shrinks_on_second_turn(self):
        """P1-6/P1-7 — không có gì đang chờ duyệt, nội dung NEXT y hệt turn trước
        → turn sau in gọn hơn. Nhánh chờ duyệt mơ hồ KHÔNG được nén (xem
        test_compliance_protocol.test_approve_signal_and_counterexamples) nên bài
        test này dùng state không có pending để không đụng nhánh an toàn đó."""
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    implement_mode="main")
        rc1, out1, _ = self.ctx("tiếp tục", session="dedupe-1")
        self.assertEqual(rc1, 0)
        rc2, out2, _ = self.ctx("tiếp tục", session="dedupe-1")
        self.assertEqual(rc2, 0)
        self.assertNotEqual(out1, out2)
        self.assertLess(len(out2), len(out1))

    def test_changed_state_does_not_shrink(self):
        """Đổi phase giữa 2 turn → KHÔNG được gọn hoá, phải in đủ nội dung mới."""
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc1, out1, _ = self.ctx("tiếp tục", session="dedupe-2")
        self.assertEqual(rc1, 0)
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    plan_file="docs/tdq/plan/x.md")
        rc2, out2, _ = self.ctx("tiếp tục", session="dedupe-2")
        self.assertEqual(rc2, 0)
        self.assertIn("[TDQ:APPROVE]", out2)
        self.assertIn("NOT clearly an", out2)
        self.assertIn("approve plan", out2)

    def test_quick_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, _ = self.ctx("duyệt quick")
        self.assertIn("approve quick", out)
        self.assertIn("--by", out)

    def _pending_plan(self, plan_body):
        # spec đã duyệt, plan đã đăng ký nhưng chưa duyệt → pending = plan
        write_file(self.cwd, "docs/tdq/plan/x.md", plan_body)
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md")

    def _pending_mode(self, plan_body):
        # plan đã duyệt nhưng chưa chốt mode → pending = mode (cổng mode tách riêng)
        write_file(self.cwd, "docs/tdq/plan/x.md", plan_body)
        write_state(self.cwd, active_request="r1", lane="full", phase="mode",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_approved_at=now_iso())

    def test_plan_hint_no_longer_asks_for_mode(self):
        # Cổng plan chỉ còn xin "duyệt plan"; mode hỏi ở phase sau.
        self._pending_plan("# plan\nMode thực thi: subagent — task tự chứa\n")
        rc, out, _ = self.ctx("tiếp tục")
        self.assertIn("approve plan", out)
        self.assertNotIn('duyệt plan mode', out)
        self.assert_budget(out)

    def test_mode_hint_uses_mode_from_plan_file(self):
        # 2026-08-02: plan đề xuất subagent → gợi ý phải nêu subagent, không hardcode main
        # 2026-08-14: mode ĐỀ XUẤT in ra bằng NHÃN người đọc, không phải định danh máy.
        self._pending_mode("# plan\nMode thực thi: subagent — task tự chứa\n")
        rc, out, _ = self.ctx("tiếp tục")
        self.assertIn('the plan proposes sub-agent implement', out)

    def test_mode_hint_without_mode_line_falls_back(self):
        self._pending_mode("# plan\nchưa ghi mode\n")
        rc, out, _ = self.ctx("tiếp tục")
        self.assertIn('the plan proposes inline implement', out)

    def test_mode_answer_is_recognised(self):
        # Trả lời cổng mode thường trống trơn: chỉ mỗi chữ "main".
        self._pending_mode("# plan\nMode thực thi: subagent — lý do\n")
        rc, out, _ = self.ctx("main")
        self.assertIn("approve plan --mode main", out)
        self.assertNotIn("⚠️", out)

    def test_mode_answer_in_new_name_maps_to_machine_value(self):
        # User gõ nhãn mới; lệnh gợi ý vẫn phải là định danh máy hợp lệ.
        self._pending_mode("# plan\nMode thực thi: subagent — lý do\n")
        rc, out, _ = self.ctx("inline")
        self.assertIn("approve plan --mode main", out)

    def test_plan_approval_with_new_name_is_not_a_conflict(self):
        # "sub-agent" và "subagent" là CÙNG một mode — không được báo lệch.
        self._pending_plan("# plan\nMode thực thi: subagent — lý do\n")
        rc, out, _ = self.ctx("duyệt plan, chạy sub-agent")
        self.assertNotIn("⚠️", out)
        self.assertIn("--mode subagent", out)

    def test_plan_approval_mode_mismatch_warns(self):
        # user duyệt "mode main" trong khi plan chốt subagent → phải có cảnh báo lệch
        self._pending_plan("# plan\nMode thực thi: subagent — lý do\n")
        rc, out, _ = self.ctx("duyệt plan mode main")
        self.assertIn("⚠️", out)
        self.assertIn("main", out)
        self.assertIn("subagent", out)
        self.assertIn("ASK", out)
        self.assertNotIn("chạy NGAY", out)
        self.assert_budget(out)

    def test_plan_approval_mode_match_no_warn(self):
        self._pending_plan("# plan\nMode thực thi: subagent — lý do\n")
        rc, out, _ = self.ctx("duyệt plan mode subagent")
        self.assertIn("--mode subagent", out)
        self.assertNotIn("⚠️", out)

    def test_plan_approval_without_mode_no_longer_needs_mode(self):
        # Luồng 2 bước: "duyệt plan" trống mode là HỢP LỆ, ghi nhận rồi mới hỏi mode.
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md")
        rc, out, _ = self.ctx("duyệt plan")
        self.assertIn("approve plan", out)
        self.assertNotIn("--mode <main|subagent>", out)

    def test_quick_approved_terminal_intake_and_next(self):
        # Quick đã duyệt + phase idle = request ĐÃ ĐÓNG → hợp đồng 2026-08-02:
        # nhắc [TDQ:INTAKE] kèm [TDQ:NEXT], không còn [TDQ:APPROVE].
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertEqual(len(out.splitlines()), 2)
        self.assertIn("[TDQ:INTAKE]", out)
        self.assertIn("[TDQ:NEXT]", out)
        self.assertNotIn("[TDQ:APPROVE]", out)

    def test_no_request_prints_intake(self):
        # Hợp đồng 2026-08-02: không state → nhắc [TDQ:INTAKE] (chi tiết ở
        # tests/test_prompt_context.py).
        rc, out, _ = self.ctx()
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:INTAKE]", out)
        self.assertNotIn("[TDQ:NEXT]", out)

    def test_full_implement_phase_line(self):
        spec = write_file(self.cwd, "docs/tdq/spec/x.md", "# spec\n")
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256=tdq_state.sha256_file(spec), spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertIn("phase implement", out)

    def test_next_line_names_open_request_and_project(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = self.ctx()
        self.assertIn("r1", out)
        self.assertIn("Project:", out)

    def test_spec_drift_warning(self):
        write_file(self.cwd, "docs/tdq/spec/x.md", "# changed\n")
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="deadbeef", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertIn("sha256 mismatch", out)

    def test_clears_previous_turn_rows(self):
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        tdq_state.turn_log_append(self.cwd, "observe", session="s1", event="edit", path="a.py")
        self.ctx(session="s1")
        rows = tdq_state.turn_log_read(self.cwd, session="s1")
        # sổ chỉ còn ảnh chụp đầu turn mới, không còn dấu vết turn trước
        self.assertEqual([r["kind"] for r in rows], ["turn_start"])


if __name__ == "__main__":
    unittest.main()


class TestNhacWorktree(unittest.TestCase):
    """T4.1 — nhắc mỗi turn khi sổ worktree còn dòng mở, im lặng khi sổ sạch.

    Nhắc nằm NGOÀI ngân sách 3 dòng/240 ký tự là có chủ ý: nó chỉ xuất hiện trong lúc
    đang phí disk và biến mất ngay khi dọn xong, nên không phải context thường trực.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    plan_file="docs/tdq/plan/x.md", plan_approved=True)

    def _so(self, noi_dung):
        duong = os.path.join(self.cwd, "docs", "tdq", "worktrees.json")
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with open(duong, "w", encoding="utf-8") as f:
            f.write(noi_dung)

    def ctx(self):
        payload = load_fixture("prompt.json", cwd=self.cwd, session_id="s-wt")
        payload["prompt"] = "tiếp tục"
        return run_hook("prompt_context.py", payload)

    def _dong(self, ma):
        return {"slug": "r1", "ma_task": ma, "nhanh": f"tdq/r1/{ma.lower()}",
                "duong_dan": os.path.join(self.cwd, ".tdq-worktrees", "r1", ma.lower()),
                "tao_luc": "2026-08-22T10:00:00", "trang_thai": "mo", "dong_luc": None}

    def test_worktree_con_mo_thi_nhac_dung_mot_dong(self):
        self._so(json.dumps({"schema": 1, "dong": [self._dong("T1.1"),
                                                   self._dong("T1.2")]}))
        rc, out, _err = self.ctx()
        self.assertEqual(rc, 0)
        nhac = [d for d in out.splitlines() if d.startswith("[TDQ:WORKTREE]")]
        self.assertEqual(len(nhac), 1, out)
        self.assertIn("2 worktree", nhac[0])
        self.assertIn("sweep", nhac[0])

    def test_worktree_so_sach_thi_im_lang(self):
        self._so(json.dumps({"schema": 1, "dong": []}))
        rc, out, _err = self.ctx()
        self.assertEqual(rc, 0)
        self.assertNotIn("[TDQ:WORKTREE]", out)

    def test_worktree_khong_co_so_thi_im_lang(self):
        rc, out, _err = self.ctx()
        self.assertEqual(rc, 0)
        self.assertNotIn("[TDQ:WORKTREE]", out)

    def test_worktree_so_hong_khong_nhac_oan(self):
        self._so("{ hong")
        rc, out, _err = self.ctx()
        self.assertEqual(rc, 0)
        self.assertNotIn("[TDQ:WORKTREE]", out)
