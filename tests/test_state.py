"""A3 — tdq_state.py: default schema, CLI, protected keys, atomic write."""
import json
import os
import tempfile
import unittest

import helper
from helper import run_state_cli, run_state_cli_in, read_state, write_state
import tdq_state


class TestState(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_missing_returns_none(self):
        self.assertIsNone(tdq_state.load(self.cwd))

    def test_default_schema_keys(self):
        state = tdq_state.default_state()
        for key in ("active_request", "lane", "phase", "spec_file", "spec_approved",
                    "spec_sha256", "spec_approved_at", "plan_file", "plan_approved",
                    "plan_sha256", "plan_approved_at", "quick_approved",
                    "quick_approved_at", "implement_mode", "updated_at"):
            self.assertIn(key, state)
        self.assertEqual(state["phase"], "idle")

    def test_cli_init_and_get(self):
        rc, out, _ = run_state_cli(self.cwd, "init", "2026-07-27-demo", "full")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertEqual(state["active_request"], "2026-07-27-demo")
        self.assertEqual(state["lane"], "full")
        # 0.3.0: `get <key>` in giá trị trần (dễ dùng trong shell), không phải JSON.
        rc, out, _ = run_state_cli(self.cwd, "get", "lane")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "full")

    def test_init_set_reset_in_mot_dong_khong_json(self):
        """Tối ưu token: init/set/reset mặc định in 1 dòng, không dump nguyên state."""
        for args in (("init", "2026-08-04-demo", "quick"),
                     ("set", "phase=implement"),
                     ("reset",)):
            rc, out, _ = run_state_cli(self.cwd, *args)
            with self.subTest(cmd=args[0]):
                self.assertEqual(rc, 0)
                self.assertEqual(len(out.splitlines()), 1, f"{args[0]}: phải đúng 1 dòng")
                self.assertNotIn("{", out, f"{args[0]}: không được dump JSON")

    def test_co_co_json_thi_in_lai_nguyen_state(self):
        """Cần soi đầy đủ thì `--json` phải trả lại hành vi cũ."""
        rc, out, _ = run_state_cli(self.cwd, "init", "2026-08-04-demo", "quick", "--json")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["active_request"], "2026-08-04-demo")
        rc, out, _ = run_state_cli(self.cwd, "set", "phase=spec", "--json")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["phase"], "spec")

    def test_dong_tom_tat_co_du_request_lane_phase(self):
        run_state_cli(self.cwd, "init", "2026-08-04-demo", "quick")
        rc, out, _ = run_state_cli(self.cwd, "set", "phase=implement")
        self.assertEqual(rc, 0)
        for chunk in ("2026-08-04-demo", "quick", "implement"):
            self.assertIn(chunk, out)

    def test_cli_set_roundtrip(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        rc, _, _ = run_state_cli(self.cwd, "set", "phase=spec", "spec_file=docs/tdq/spec/x.md")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertEqual(state["phase"], "spec")
        self.assertEqual(state["spec_file"], "docs/tdq/spec/x.md")

    def test_cli_can_set_approval_keys(self):
        # 0.2.0: không còn field bảo vệ — không còn hook độc quyền ghi state.
        run_state_cli(self.cwd, "init", "r1", "full")
        for pair in ("spec_approved=true", "plan_approved=true", "quick_approved=true",
                     "spec_sha256=abc", "plan_approved_at=now", "implement_mode=main"):
            rc, _, err = run_state_cli(self.cwd, "set", pair)
            self.assertEqual(rc, 0, f"{pair}: {err}")
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertTrue(state["plan_approved"])
        self.assertTrue(state["quick_approved"])
        self.assertEqual(state["implement_mode"], "main")

    def test_cli_rejects_invalid_lane_phase_key(self):
        # 0.3.0 exit code: 2 = sai cú pháp lệnh; mọi vấn đề của state chỉ cảnh báo (0).
        run_state_cli(self.cwd, "init", "r1")
        self.assertEqual(run_state_cli(self.cwd, "set", "lane=turbo")[0], 2)
        self.assertEqual(run_state_cli(self.cwd, "set", "phase=deploy")[0], 2)
        self.assertEqual(run_state_cli(self.cwd, "set", "nonexistent=1")[0], 2)

    def test_load_backfills_missing_keys(self):
        # State ghi bởi schema cũ (thiếu previous_request) vẫn nạp được, không mất dữ liệu.
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w", encoding="utf-8") as f:
            json.dump({"schema_version": 1, "active_request": "cu", "lane": "full",
                       "phase": "implement"}, f)
        state = tdq_state.load(self.cwd)
        self.assertEqual(state["active_request"], "cu")
        self.assertEqual(state["phase"], "implement")
        self.assertIn("previous_request", state)
        self.assertIsNone(state["previous_request"])

    def test_init_over_unfinished_request_warns(self):
        run_state_cli(self.cwd, "init", "req-cu", "full")
        run_state_cli(self.cwd, "set", "phase=implement", "spec_file=docs/tdq/spec/x.md")
        rc, _, err = run_state_cli(self.cwd, "init", "req-moi", "quick")
        self.assertEqual(rc, 0)
        self.assertIn("Ghi đè", err)
        self.assertIn("req-cu", err)
        state = read_state(self.cwd)
        self.assertEqual(state["active_request"], "req-moi")
        self.assertEqual(state["lane"], "quick")
        self.assertEqual(state["previous_request"], "req-cu")
        self.assertEqual(state["phase"], "idle")
        self.assertIsNone(state["spec_file"])
        self.assertIsNone(state["plan_file"])
        self.assertIsNone(state["implement_mode"])
        for key in ("spec_approved", "plan_approved", "quick_approved"):
            self.assertFalse(state[key], key)

    def test_init_clean_state_is_silent(self):
        rc, _, err = run_state_cli(self.cwd, "init", "req-dau", "quick")
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        self.assertIsNone(read_state(self.cwd)["previous_request"])

    def test_init_over_finished_request_is_silent(self):
        run_state_cli(self.cwd, "init", "req-cu", "full")
        run_state_cli(self.cwd, "set", "phase=report")
        rc, _, err = run_state_cli(self.cwd, "init", "req-moi", "quick")
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        self.assertEqual(read_state(self.cwd)["previous_request"], "req-cu")

    def test_previous_request_is_settable(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        rc, _, _ = run_state_cli(self.cwd, "set", "previous_request=r0")
        self.assertEqual(rc, 0)
        self.assertEqual(read_state(self.cwd)["previous_request"], "r0")

    def test_load_backfills_approved_by(self):
        # state ghi bởi schema 2 (chưa có *_approved_by) vẫn nạp đủ, không mất dữ liệu
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w", encoding="utf-8") as f:
            json.dump({"schema_version": 2, "active_request": "cu", "lane": "full",
                       "phase": "plan", "spec_approved": True}, f)
        state = tdq_state.load(self.cwd)
        self.assertEqual(state["schema_version"], 3)
        self.assertTrue(state["spec_approved"])
        for key in ("spec_approved_by", "plan_approved_by", "quick_approved_by"):
            self.assertIn(key, state)
            self.assertIsNone(state[key])

    def test_approve_writes_all_fields(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        spec = os.path.join(self.cwd, "docs", "tdq", "spec", "x.md")
        os.makedirs(os.path.dirname(spec), exist_ok=True)
        with open(spec, "w", encoding="utf-8") as f:
            f.write("# spec\n")
        run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/x.md")
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("Đã ghi nhận", out)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertIsNotNone(state["spec_approved_at"])
        self.assertEqual(state["spec_approved_by"], "duyệt spec")
        self.assertEqual(state["spec_sha256"], tdq_state.sha256_file(spec))

        rc, _, err = run_state_cli(self.cwd, "set", "plan_file=docs/tdq/plan/x.md")
        rc, out, err = run_state_cli(self.cwd, "approve", "plan", "--mode", "main",
                                     "--by", "x" * 500)
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state["plan_approved"])
        self.assertEqual(state["implement_mode"], "main")
        self.assertEqual(len(state["plan_approved_by"]), 200)

    def test_reapprove_refreshes_sha256_after_file_changed(self):
        """Sửa spec trong lúc QC rồi xin duyệt lại phải ghi được — nếu không,
        cảnh báo "spec đã đổi sau khi duyệt" treo vĩnh viễn."""
        run_state_cli(self.cwd, "init", "r1", "full")
        spec = os.path.join(self.cwd, "docs", "tdq", "spec", "x.md")
        os.makedirs(os.path.dirname(spec), exist_ok=True)
        with open(spec, "w", encoding="utf-8") as f:
            f.write("# spec\n")
        run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/x.md")
        run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        first = read_state(self.cwd)["spec_approved_at"]

        with open(spec, "a", encoding="utf-8") as f:
            f.write("\n## 7. Câu hỏi còn mở\n\n- thêm sau QC\n")
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "approve spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("duyệt lại", out)
        state = read_state(self.cwd)
        self.assertEqual(state["spec_sha256"], tdq_state.sha256_file(spec))
        self.assertEqual(state["spec_approved_by"], "approve spec")
        # dấu thời gian chỉ tới giây nên duyệt lại trong cùng giây vẫn bằng nhau —
        # chỉ đòi không lùi về quá khứ.
        self.assertGreaterEqual(state["spec_approved_at"], first)

    def test_reapprove_unchanged_file_stays_idempotent(self):
        """File không đổi thì duyệt lại là lệnh thừa — không ghi đè dấu duyệt cũ."""
        run_state_cli(self.cwd, "init", "r1", "full")
        spec = os.path.join(self.cwd, "docs", "tdq", "spec", "x.md")
        os.makedirs(os.path.dirname(spec), exist_ok=True)
        with open(spec, "w", encoding="utf-8") as f:
            f.write("# spec\n")
        run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/x.md")
        run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        first = read_state(self.cwd)["spec_approved_at"]
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "approve spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("đã duyệt lúc", out)
        state = read_state(self.cwd)
        self.assertEqual(state["spec_approved_at"], first)
        self.assertEqual(state["spec_approved_by"], "duyệt spec")

    def test_approve_accepts_bare_mode(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        run_state_cli(self.cwd, "approve", "spec")
        rc, _, err = run_state_cli(self.cwd, "approve", "plan", "subagent")
        self.assertEqual(rc, 0, err)
        self.assertEqual(read_state(self.cwd)["implement_mode"], "subagent")

    def test_mode_external_bi_tu_choi(self):
        """Nhánh external đã bỏ: mode này phải bị chặn, không âm thầm nhận."""
        run_state_cli(self.cwd, "init", "r1", "full")
        run_state_cli(self.cwd, "approve", "spec")
        rc, _, _ = run_state_cli(self.cwd, "approve", "plan", "--mode", "external",
                                 "--by", "duyệt plan mode external")
        self.assertNotEqual(rc, 0)
        self.assertIsNone(read_state(self.cwd)["implement_mode"])

    def test_mode_mentions_chi_con_main_subagent(self):
        for text in (tdq_state.USAGE, tdq_state.PHASE_TABLE["plan"]["cmd"],
                     " ".join(tdq_state.PHASE_TABLE["plan"]["checklist"])):
            self.assertNotIn("external", text)
        self.assertIn("main", tdq_state.PHASE_TABLE["plan"]["cmd"])
        self.assertIn("subagent", tdq_state.PHASE_TABLE["plan"]["cmd"])

    def test_approve_quick_moves_phase_to_implement(self):
        """A6: duyệt quick phải đẩy phase=implement để idle sau đó thành terminal."""
        run_state_cli(self.cwd, "init", "r1", "quick")
        run_state_cli(self.cwd, "approve", "quick", "--by", "duyệt quick")
        self.assertEqual(read_state(self.cwd)["phase"], "implement")

    def test_row_age_ok_bad_ts_types(self):
        """A18: ts kiểu số/None/thiếu không được crash hook."""
        self.assertFalse(tdq_state._row_age_ok({"ts": 123}))
        self.assertFalse(tdq_state._row_age_ok({"ts": None}))
        self.assertFalse(tdq_state._row_age_ok({}))

    def test_approve_is_idempotent(self):
        run_state_cli(self.cwd, "init", "r1", "quick")
        rc, _, err = run_state_cli(self.cwd, "approve", "quick", "--by", "duyệt quick")
        self.assertEqual(rc, 0, err)
        first_at = read_state(self.cwd)["quick_approved_at"]
        rc, out, err = run_state_cli(self.cwd, "approve", "quick")
        self.assertEqual(rc, 0, err)  # duyệt lần hai KHÔNG phải lỗi
        self.assertIn("đã duyệt lúc", out)
        self.assertEqual(read_state(self.cwd)["quick_approved_at"], first_at)

    def test_approve_warns_but_records(self):
        run_state_cli(self.cwd, "init", "r1", "quick")
        # sai lane + duyệt plan trước spec + chưa đăng ký plan_file → cảnh báo, vẫn ghi
        rc, _, err = run_state_cli(self.cwd, "approve", "plan", "--mode", "main", "--by", "ok plan")
        self.assertEqual(rc, 0)
        self.assertIn("lane quick", err)
        self.assertIn("spec chưa", err)
        state = read_state(self.cwd)
        self.assertTrue(state["plan_approved"])
        self.assertEqual(state["implement_mode"], "main")

    def test_approve_rejects_bad_syntax(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        self.assertEqual(run_state_cli(self.cwd, "approve")[0], 2)
        self.assertEqual(run_state_cli(self.cwd, "approve", "design")[0], 2)
        self.assertEqual(run_state_cli(self.cwd, "approve", "spec", "--mode", "turbo")[0], 2)
        self.assertFalse(read_state(self.cwd)["spec_approved"])

    def test_atomic_overwrite_keeps_valid_json(self):
        write_state(self.cwd, active_request="r1", lane="full")
        state = tdq_state.load(self.cwd)
        state["phase"] = "plan"
        tdq_state.save(self.cwd, state)
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["phase"], "plan")
        self.assertIsNotNone(data["updated_at"])
        leftovers = [n for n in os.listdir(os.path.join(self.cwd, "docs", "tdq")) if n.startswith(".state-")]
        self.assertEqual(leftovers, [])


class TestProjectRootResolution(unittest.TestCase):
    """State phải luôn về MỘT file ở project root — chạy CLI từ thư mục con
    không được đẻ ra 'state bóng'."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self._tmp.name)
        self.sub = os.path.join(self.root, "frontend", "src")
        os.makedirs(self.sub)

    def tearDown(self):
        self._tmp.cleanup()

    def shadow_states(self):
        found = []
        for dirpath, _, files in os.walk(self.root):
            if "state.json" in files and dirpath.endswith(os.path.join("docs", "tdq")):
                found.append(os.path.relpath(dirpath, self.root))
        return sorted(found)

    def test_env_var_always_wins(self):
        os.makedirs(os.path.join(self.root, ".git"))
        env_dir = os.path.join(self.root, "elsewhere")
        os.makedirs(env_dir)
        self.assertEqual(os.path.realpath(tdq_state.resolve_project_dir(self.sub, env=env_dir)),
                         os.path.realpath(env_dir))

    def test_resolve_uses_git_root_from_subdir(self):
        os.makedirs(os.path.join(self.root, ".git"))
        self.assertEqual(os.path.realpath(tdq_state.resolve_project_dir(self.sub, env=None)),
                         self.root)

    def test_resolve_uses_existing_state_root(self):
        write_state(self.root, active_request="r1", lane="quick")
        self.assertEqual(os.path.realpath(tdq_state.resolve_project_dir(self.sub, env=None)),
                         self.root)

    def test_resolve_fallback_to_cwd(self):
        self.assertEqual(os.path.realpath(tdq_state.resolve_project_dir(self.sub, env=None)),
                         os.path.realpath(self.sub))

    def test_cli_from_subdir_writes_root_state(self):
        os.makedirs(os.path.join(self.root, ".git"))
        rc, out, err = run_state_cli_in(self.sub, "init", "r1", "quick")
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.shadow_states(), [os.path.join("docs", "tdq")])
        self.assertEqual(read_state(self.root)["active_request"], "r1")
        self.assertIn("Project root", err)

        rc, _, err = run_state_cli_in(self.sub, "set", "phase=implement")
        self.assertEqual(rc, 0, err)
        self.assertEqual(read_state(self.root)["phase"], "implement")
        self.assertEqual(self.shadow_states(), [os.path.join("docs", "tdq")])

    def test_cli_warns_about_shadow_states(self):
        os.makedirs(os.path.join(self.root, ".git"))
        write_state(self.root, active_request="r1", lane="quick")
        write_state(os.path.join(self.root, "frontend"), active_request="r1", lane="quick")
        rc, _, err = run_state_cli_in(self.sub, "get")
        self.assertEqual(rc, 0)
        self.assertIn("state", err.lower())
        self.assertIn("frontend", err)


if __name__ == "__main__":
    unittest.main()
