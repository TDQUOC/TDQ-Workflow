"""Test external_task.py — lõi mode external (stub binary, không mạng)."""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "external_task.py")
SCHEMA = os.path.join(ROOT, "scripts", "external_report_schema.json")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import external_task  # noqa: E402


def good_report(**overrides):
    report = {
        "task_id": "T1",
        "status": "done",
        "files_changed": ["a.py"],
        "test_cmd": "python3 -m unittest tests.test_a",
        "test_result": "OK",
        "notes": "",
    }
    report.update(overrides)
    return report


class SchemaTest(unittest.TestCase):
    def test_schema_file_exists_and_valid_json(self):
        with open(SCHEMA, encoding="utf-8") as f:
            schema = json.load(f)
        # T1.1: schema oneOf [task, plan] — nhánh task giữ required cũ
        kinds = schema["oneOf"]
        self.assertEqual(len(kinds), 2)
        self.assertIn("task_id", kinds[0]["required"])
        self.assertIn("tasks", kinds[1]["required"])

    def test_good_report_passes(self):
        self.assertEqual(external_task.validate_report(good_report()), [])

    def test_fallback_claude_passes(self):
        self.assertEqual(
            external_task.validate_report(good_report(fallback="claude")), [])

    def test_missing_key_fails(self):
        report = good_report()
        del report["test_cmd"]
        self.assertNotEqual(external_task.validate_report(report), [])

    def test_bad_status_enum_fails(self):
        errs = external_task.validate_report(good_report(status="maybe"))
        self.assertNotEqual(errs, [])

    def test_bad_types_fail(self):
        self.assertNotEqual(
            external_task.validate_report(good_report(files_changed="a.py")), [])
        self.assertNotEqual(
            external_task.validate_report(good_report(notes=None)), [])

    def test_unknown_key_fails(self):
        self.assertNotEqual(
            external_task.validate_report(good_report(extra="x")), [])


class TaskTemplateTest(unittest.TestCase):
    """Khuôn gói task (skills/tdq-build/references/external-task.md) đủ mục và
    ví dụ report mẫu phải pass validate."""
    PATH = os.path.join(ROOT, "skills", "tdq-build", "references",
                        "external-task.md")

    def test_template_has_all_sections(self):
        with open(self.PATH, encoding="utf-8") as f:
            text = f.read()
        for section in ("# TASK", "Mục tiêu:", "File:", "Test:", "Ràng buộc:",
                        "Report mẫu"):
            self.assertIn(section, text)
        self.assertIn("không commit", text.lower())
        self.assertIn("worktree", text.lower())

    def test_example_report_validates(self):
        with open(self.PATH, encoding="utf-8") as f:
            text = f.read()
        match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
        self.assertIsNotNone(match, "khuôn thiếu khối ```json report mẫu")
        self.assertEqual(external_task.validate_report(json.loads(match.group(1))), [])


class RunnerAgentsTest(unittest.TestCase):
    """2 agent runner: tồn tại, frontmatter hợp lệ, nêu đúng chữ ký lệnh lõi."""
    PATHS = [os.path.join(ROOT, "agents", name)
             for name in ("codex-runner.md", "agy-runner.md")]

    def test_files_exist_with_frontmatter(self):
        for path in self.PATHS:
            with self.subTest(agent=os.path.basename(path)):
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                self.assertTrue(text.startswith("---\n"))
                head = text.split("---", 2)[1]
                self.assertRegex(head, r"name:\s*(codex|agy)-runner")
                self.assertIn("description:", head)

    def test_agents_state_command_signature(self):
        for path in self.PATHS:
            with self.subTest(agent=os.path.basename(path)):
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                self.assertIn("external_task.py run --engine", text)
                for part in ("--model", "--task-file", "--worktree", "--slug",
                             "run_in_background"):
                    self.assertIn(part, text)
                # runner không tự quyết fallback
                self.assertIn("orchestrator", text.lower())

    def test_wait_mechanism_and_exit_table(self):
        for path in self.PATHS:
            with self.subTest(agent=os.path.basename(path)):
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                low = text.lower()
                # A5: chờ theo cơ chế thật — Bash nền đánh thức agent khi xong;
                # cấm watcher sleep và luật "never end early" sai cơ chế
                self.assertNotIn("sleep", low)
                self.assertNotIn("end early", low)
                self.assertIn("re-invoke", low)
                # A9: bảng exit code đủ mã + hành xử từng mã
                for code in ("| 0 |", "| 1 |", "| 2 |"):
                    self.assertIn(code, text, code)


class StubBase(unittest.TestCase):
    """Dựng stub binary codex/agy trong PATH + worktree/cwd tạm."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tdq-ext-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin_dir = os.path.join(self.tmp, "bin")
        self.resp_dir = os.path.join(self.tmp, "resp")
        self.worktree = os.path.join(self.tmp, "worktree")
        self.project = os.path.join(self.tmp, "project")
        self.empty_bin = os.path.join(self.tmp, "emptybin")
        for d in (self.bin_dir, self.resp_dir, self.worktree, self.project,
                  self.empty_bin):
            os.makedirs(d)
        self.capture = os.path.join(self.tmp, "capture.txt")
        self.count = os.path.join(self.tmp, "count.txt")
        self.task_file = os.path.join(self.tmp, "task.md")
        with open(self.task_file, "w", encoding="utf-8") as f:
            f.write("# TASK T9\nMục tiêu: demo.\n")
        for name in ("codex", "agy"):
            path = os.path.join(self.bin_dir, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    '#!/bin/sh\n'
                    'PATH=/bin:/usr/bin\n'
                    f'n=$(cat "{self.count}" 2>/dev/null || echo 0)\n'
                    'n=$((n+1))\n'
                    f'echo $n > "{self.count}"\n'
                    f'printf \'CALL%s: %s\\n\' "$n" "$*" >> "{self.capture}"\n'
                    f'if [ -f "{self.resp_dir}/sleep$n" ]; then sleep 5; fi\n'
                    f'cat "{self.resp_dir}/resp$n.json" 2>/dev/null\n'
                    f'exit $(cat "{self.resp_dir}/exit$n" 2>/dev/null || echo 0)\n')
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def set_response(self, n, data, exit_code=0):
        with open(os.path.join(self.resp_dir, f"resp{n}.json"), "w",
                  encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
        with open(os.path.join(self.resp_dir, f"exit{n}"), "w") as f:
            f.write(str(exit_code))

    def run_cli(self, *args, env=None, path_with_stub=True):
        full_env = dict(os.environ, **(env or {}))
        # PATH cô lập tuyệt đối: chỉ stub (hoặc rỗng) — cấm chạm binary thật.
        full_env["PATH"] = self.bin_dir if path_with_stub else self.empty_bin
        proc = subprocess.run(
            [sys.executable, SCRIPT, *args], capture_output=True, text=True,
            timeout=60, cwd=self.project, env=full_env)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

    def run_task(self, engine="codex", env=None, path_with_stub=True):
        return self.run_cli(
            "run", "--engine", engine, "--model", "m-test", "--task-file",
            self.task_file, "--worktree", self.worktree, "--slug", "s1",
            env=env, path_with_stub=path_with_stub)

    def calls(self):
        """-> [khối args của từng lần gọi] (prompt nhiều dòng nằm trọn trong khối)."""
        try:
            with open(self.capture, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return []
        return re.split(r"(?m)^CALL\d+: ", text)[1:]

    def report_path(self):
        return os.path.join(self.project, "docs", "tdq", "external", "s1", "T9.json")

    def log_path(self):
        return os.path.join(self.project, "docs", "tdq", "external", "s1", "run.log")


class RunTest(StubBase):
    def test_ok_codex(self):
        self.set_response(1, good_report(task_id="T9"))
        code, out, _ = self.run_task("codex")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["task_id"], "T9")
        with open(self.report_path(), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["status"], "done")
        call = self.calls()[0]
        for flag in ("exec", "--cd", "-m m-test", "--sandbox danger-full-access",
                     "--output-schema"):
            self.assertIn(flag, call)

    def test_ok_agy(self):
        # agy bọc report trong {status, response}
        self.set_response(1, {"status": "ok",
                              "response": good_report(task_id="T9")})
        code, out, _ = self.run_task("agy")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["task_id"], "T9")
        call = self.calls()[0]
        for flag in ("-p", "--model m-test", "--output-format json",
                     "--json-schema", "--dangerously-skip-permissions",
                     "--add-dir", "--print-timeout"):
            self.assertIn(flag, call)

    def test_bad_usage_exit_2(self):
        code, _, err = self.run_cli("run", "--engine", "codex")
        self.assertEqual(code, 2)
        self.assertIn("usage", err)

    def test_engine_emitted_fallback_rejected(self):
        # khóa fallback chỉ orchestrator được ghi — engine phát ra phải bị retry
        self.set_response(1, good_report(task_id="T9", fallback="claude"))
        self.set_response(2, good_report(task_id="T9"))
        code, out, _ = self.run_task("codex")
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertIn("orchestrator", self.calls()[1])
        self.assertNotIn("fallback", json.loads(out))


class RetryTest(StubBase):
    def test_bad_schema_then_ok(self):
        self.set_response(1, {"task_id": "T9"})          # thiếu khóa → fail
        self.set_response(2, good_report(task_id="T9"))
        code, out, _ = self.run_task("codex")
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), 2)
        # attempt 2 phải kèm nguyên văn lỗi attempt 1 trong prompt
        self.assertIn("LỖI LẦN TRƯỚC", self.calls()[1])
        self.assertIn("thiếu khóa bắt buộc", self.calls()[1])


class FailTest(StubBase):
    def test_three_bad_attempts_exit_1(self):
        for n in (1, 2, 3):
            self.set_response(n, "not json at all")
        code, _, err = self.run_task("codex")
        self.assertEqual(code, 1)
        self.assertEqual(len(self.calls()), 3)
        self.assertIn("fallback", err)
        with open(self.log_path(), encoding="utf-8") as f:
            log = f.read()
        self.assertEqual(log.count("attempt="), 3)

    def test_timeout_counts_as_failed_attempt(self):
        with open(os.path.join(self.resp_dir, "sleep1"), "w") as f:
            f.write("1")
        self.set_response(2, good_report(task_id="T9"))
        code, _, _ = self.run_task("codex", env={"TDQ_EXTERNAL_TIMEOUT": "1"})
        self.assertEqual(code, 0)
        with open(self.log_path(), encoding="utf-8") as f:
            self.assertIn("timeout", f.read())

    def test_missing_binary_exit_1(self):
        code, _, err = self.run_task("codex", path_with_stub=False)
        self.assertEqual(code, 1)
        self.assertIn("PATH", err)
        self.assertFalse(os.path.exists(self.report_path()))

    def test_nonzero_exit_with_valid_json_accepted(self):
        self.set_response(1, good_report(task_id="T9"), exit_code=3)
        code, out, _ = self.run_task("codex")
        self.assertEqual(code, 0)
        self.assertIn("engine exit 3", json.loads(out)["notes"])


class LogTest(StubBase):
    def test_log_lines_have_timestamp_and_no_env(self):
        self.set_response(1, good_report(task_id="T9"))
        self.run_task("codex")
        with open(self.log_path(), encoding="utf-8") as f:
            line = f.read().splitlines()[0]
        self.assertRegex(line, r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertNotIn("PATH=", line)

    def test_log_disabled(self):
        self.set_response(1, good_report(task_id="T9"))
        self.run_task("codex", env={"TDQ_EXTERNAL_LOG": "0"})
        self.assertFalse(os.path.exists(self.log_path()))

    def test_timeout_env_feeds_agy_print_timeout(self):
        self.set_response(1, {"response": good_report(task_id="T9")})
        self.run_task("agy", env={"TDQ_EXTERNAL_TIMEOUT": "7"})
        self.assertIn("--print-timeout 7s", self.calls()[0])


class HardenTest(StubBase):
    """A4/A12/A13/A24 — artifact debug + feedback + stagger timeout + atomic write."""

    def raw_path(self, attempt):
        return os.path.join(self.project, "docs", "tdq", "external", "s1",
                            f"T9.attempt{attempt}.raw.txt")

    def test_failed_attempt_persists_raw_output(self):
        # A4: attempt fail phải để lại raw stdout để debug prompt/model
        self.set_response(1, "not json at all")
        self.set_response(2, good_report(task_id="T9"))
        code, _, _ = self.run_task("codex")
        self.assertEqual(code, 0)
        with open(self.raw_path(1), encoding="utf-8") as f:
            self.assertIn("not json at all", f.read())

    def test_retry_prompt_includes_prev_output_excerpt(self):
        # A12: feedback retry phải kèm trích output attempt trước
        self.set_response(1, "day la output sai DAUVET123")
        self.set_response(2, good_report(task_id="T9"))
        self.run_task("codex")
        self.assertIn("DAUVET123", self.calls()[1])

    def test_agy_print_timeout_staggered(self):
        # A13: engine phải được deadline sớm hơn wrapper 30s (sàn 30, trần = wrapper)
        self.set_response(1, {"response": good_report(task_id="T9")})
        self.run_task("agy", env={"TDQ_EXTERNAL_TIMEOUT": "540"})
        self.assertIn("--print-timeout 510s", self.calls()[0])

    def test_report_write_leaves_no_tmp(self):
        # A24: ghi report atomic — không còn file *.tmp sau khi xong
        self.set_response(1, good_report(task_id="T9"))
        self.run_task("codex")
        report_dir = os.path.dirname(self.report_path())
        self.assertTrue(os.path.exists(self.report_path()))
        self.assertEqual([f for f in os.listdir(report_dir) if f.endswith(".tmp")], [])

    def test_dirs_anchored_to_project_dir(self):
        # A17: chạy từ cwd lạ + TDQ_PROJECT_DIR → report/log nằm trong project,
        # không rắc docs/ theo cwd
        elsewhere = os.path.join(self.tmp, "elsewhere")
        os.makedirs(elsewhere)
        self.set_response(1, good_report(task_id="T9"))
        full_env = dict(os.environ, TDQ_PROJECT_DIR=self.project)
        full_env["PATH"] = self.bin_dir
        proc = subprocess.run(
            [sys.executable, SCRIPT, "run", "--engine", "codex", "--model",
             "m-test", "--task-file", self.task_file, "--worktree",
             self.worktree, "--slug", "s1"],
            capture_output=True, text=True, timeout=60, cwd=elsewhere,
            env=full_env)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(os.path.exists(self.report_path()))
        self.assertFalse(os.path.exists(os.path.join(elsewhere, "docs")))


class ParsePlanTest(StubBase):
    def _plan(self, line):
        path = os.path.join(self.tmp, "plan.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# PLAN\n\n{line}\n\n- [ ] T1\n")
        return path

    def test_three_names(self):
        code, out, _ = self.run_cli("parse-plan", self._plan(
            "Thực thi external: engine=codex · khó=a · TB=b · dễ=c"))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out),
                         {"engine": "codex", "models": {"khó": "a", "TB": "b", "dễ": "c"}})

    def test_two_names_mid_uses_hard(self):
        code, out, _ = self.run_cli("parse-plan", self._plan(
            "Thực thi external: engine=agy · khó=a · dễ=c"))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["models"], {"khó": "a", "TB": "a", "dễ": "c"})

    def test_one_name_all_same(self):
        code, out, _ = self.run_cli("parse-plan", self._plan(
            "Thực thi external: engine=codex · khó=a"))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["models"], {"khó": "a", "TB": "a", "dễ": "a"})

    def test_malformed_exit_1(self):
        for line in ("Thực thi external: engine=gemini · khó=a",
                     "Thực thi external: khó=a",
                     "không có dòng nào"):
            code, _, err = self.run_cli("parse-plan", self._plan(line))
            self.assertEqual(code, 1, line)
            self.assertIn("⚠️", err)


def good_plan_report(**overrides):
    report = {
        "kind": "plan",
        "status": "done",
        "tasks": [good_report(task_id="T1"), good_report(task_id="T2")],
        "notes": "",
    }
    report.update(overrides)
    return report


class PlanSchemaTest(unittest.TestCase):
    """T1.1 — discriminator kind: task|plan; vắng kind = task (hồi quy)."""

    def test_task_report_without_kind_still_passes(self):
        self.assertEqual(external_task.validate_report(good_report()), [])

    def test_task_report_with_kind_task_passes(self):
        self.assertEqual(
            external_task.validate_report(good_report(kind="task")), [])

    def test_plan_report_passes(self):
        self.assertEqual(external_task.validate_report(good_plan_report()), [])

    def test_plan_report_missing_tasks_fails(self):
        report = good_plan_report()
        del report["tasks"]
        self.assertNotEqual(external_task.validate_report(report), [])

    def test_plan_report_empty_tasks_fails(self):
        self.assertNotEqual(
            external_task.validate_report(good_plan_report(tasks=[])), [])

    def test_plan_report_task_empty_test_result_fails(self):
        # Q9: engine phải tự verify — test_result rỗng là chưa chạy test
        bad = good_plan_report(tasks=[good_report(test_result="  ")])
        self.assertNotEqual(external_task.validate_report(bad), [])

    def test_plan_report_unknown_key_fails(self):
        self.assertNotEqual(
            external_task.validate_report(good_plan_report(extra="x")), [])

    def test_schema_file_has_kind(self):
        with open(SCHEMA, encoding="utf-8") as f:
            self.assertIn("kind", f.read())


class PlanTimeoutTest(unittest.TestCase):
    """T1.2/Q7 — timeout theo số task trong gói: 540×n, trần 3600, env thắng."""

    def setUp(self):
        os.environ.pop("TDQ_EXTERNAL_TIMEOUT", None)

    def tearDown(self):
        os.environ.pop("TDQ_EXTERNAL_TIMEOUT", None)

    def test_scale(self):
        self.assertEqual(external_task.plan_timeout_secs(3), 1620)
        self.assertEqual(external_task.plan_timeout_secs(7), 3600)
        self.assertEqual(external_task.plan_timeout_secs(2), 1080)

    def test_env_override_wins(self):
        os.environ["TDQ_EXTERNAL_TIMEOUT"] = "99"
        self.assertEqual(external_task.plan_timeout_secs(7), 99)

    def test_count_tasks_from_packet(self):
        text = "# GÓI PLAN\n## TASK T1\n...\n## TASK T2\n...\n## TASK T3\n"
        self.assertEqual(external_task.count_packet_tasks(text), 3)
        self.assertEqual(external_task.count_packet_tasks("no tasks"), 1)


class RunPlanTest(StubBase):
    """T1.3/Q2/Q9 — subcommand run-plan: 2 attempt, report plan-round-<n>.json."""

    def _packet(self, n_tasks=2):
        path = os.path.join(self.tmp, "packet.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# GÓI PLAN s1\n")
            for i in range(1, n_tasks + 1):
                f.write(f"## TASK T{i}\nMục tiêu: demo.\n")
        return path

    def run_plan(self, engine="codex", env=None, n_tasks=2, extra=()):
        return self.run_cli(
            "run-plan", "--engine", engine, "--model", "m-test", "--task-file",
            self._packet(n_tasks), "--worktree", self.worktree, "--slug", "s1",
            *extra, env=env)

    def plan_report_path(self, n=1):
        return os.path.join(self.project, "docs", "tdq", "external", "s1",
                            f"plan-round-{n}.json")

    def test_ok_writes_plan_round_report(self):
        self.set_response(1, good_plan_report())
        code, out, _ = self.run_plan()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["kind"], "plan")
        with open(self.plan_report_path(1), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["status"], "done")

    def test_round_flag_names_report(self):
        self.set_response(1, good_plan_report())
        code, _, _ = self.run_plan(extra=("--round", "2"))
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(self.plan_report_path(2)))

    def test_two_attempts_only(self):
        for n in (1, 2, 3):
            self.set_response(n, "not json at all")
        code, _, err = self.run_plan()
        self.assertEqual(code, 1)
        self.assertEqual(len(self.calls()), 2)
        self.assertIn("fallback", err)

    def test_task_report_rejected_retries(self):
        # run-plan đòi kind=plan — report task đơn phải bị retry
        self.set_response(1, good_report())
        self.set_response(2, good_plan_report())
        code, _, _ = self.run_plan()
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), 2)

    def test_empty_test_result_retries(self):
        # Q9: engine chưa tự verify → retry
        self.set_response(1, good_plan_report(
            tasks=[good_report(test_result="")]))
        self.set_response(2, good_plan_report())
        code, _, _ = self.run_plan()
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), 2)

    def test_timeout_scales_with_packet_tasks(self):
        # agy để lộ deadline qua --print-timeout: 2 task → 1080-30 = 1050s
        self.set_response(1, {"response": good_plan_report()})
        code, _, _ = self.run_plan("agy", n_tasks=2)
        self.assertEqual(code, 0)
        self.assertIn("--print-timeout 1050s", self.calls()[0])

    def test_run_plan_logs_attempts(self):
        # T5.1: run-plan ghi run.log; TDQ_EXTERNAL_LOG=0 tắt
        self.set_response(1, good_plan_report())
        self.run_plan()
        with open(self.log_path(), encoding="utf-8") as f:
            self.assertIn("plan-round-1", f.read())

    def test_run_plan_log_disabled(self):
        self.set_response(1, good_plan_report())
        self.run_plan(env={"TDQ_EXTERNAL_LOG": "0"})
        self.assertFalse(os.path.exists(self.log_path()))


class SplitPlanTest(StubBase):
    """T2.1/Q8 — chia gói ≤6 task, tôn trọng ranh giới phase."""

    def _plan(self, text):
        path = os.path.join(self.tmp, "bigplan.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_seven_tasks_no_phase_two_packets(self):
        body = "# PLAN\n" + "".join(
            f"- [ ] **T{i}** việc — Test: t\n" for i in range(1, 8))
        code, out, _ = self.run_cli("split-plan", self._plan(body))
        self.assertEqual(code, 0)
        packets = json.loads(out)
        self.assertEqual(len(packets), 2)
        self.assertEqual(packets[0]["tasks"],
                         ["T1", "T2", "T3", "T4", "T5", "T6"])
        self.assertEqual(packets[1]["tasks"], ["T7"])

    def test_phase_boundaries_respected(self):
        body = ("# PLAN\n## P1 — a\n" +
                "".join(f"- [ ] **T1.{i}** v — Test: t\n" for i in range(1, 5)) +
                "## P2 — b\n" +
                "".join(f"- [ ] **T2.{i}** v — Test: t\n" for i in range(1, 4)))
        code, out, _ = self.run_cli("split-plan", self._plan(body))
        self.assertEqual(code, 0)
        packets = json.loads(out)
        self.assertEqual(len(packets), 2)
        self.assertEqual(packets[0]["tasks"], ["T1.1", "T1.2", "T1.3", "T1.4"])
        self.assertEqual(packets[1]["tasks"], ["T2.1", "T2.2", "T2.3"])


class FixRoundsTest(StubBase):
    """T2.2/Q6 — fix-rounds.json: luật dừng sau 2 vòng → fallback."""

    def fx(self, *args, env=None):
        return self.run_cli("fix-rounds", "--slug", "s1", *args, env=env)

    def rounds_path(self):
        return os.path.join(self.project, "docs", "tdq", "external", "s1",
                            "fix-rounds.json")

    def test_add_and_status(self):
        code, _, _ = self.fx("add", "--tasks", "T1,T2", "--result", "fail")
        self.assertEqual(code, 0)
        code, out, _ = self.fx("status")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["rounds"], 1)
        self.assertEqual(data["next"], "fix")
        with open(self.rounds_path(), encoding="utf-8") as f:
            stored = json.load(f)
        self.assertEqual(stored["rounds"][0]["tasks"], ["T1", "T2"])

    def test_two_fails_then_fallback_no_round_three(self):
        self.fx("add", "--tasks", "T1", "--result", "fail")
        self.fx("add", "--tasks", "T1", "--result", "fail")
        code, out, _ = self.fx("status")
        self.assertEqual(json.loads(out)["next"], "fallback")
        code, _, err = self.fx("add", "--tasks", "T1", "--result", "fail")
        self.assertEqual(code, 1)
        self.assertIn("fallback", err)

    def test_pass_round_means_done(self):
        self.fx("add", "--tasks", "T1", "--result", "pass")
        _, out, _ = self.fx("status")
        self.assertEqual(json.loads(out)["next"], "done")


class TwoPhaseE2ETest(StubBase):
    """T5.2/Q1/Q8 — E2E mock tầng script, vai orchestrator: chia 7 task
    thành 2 gói theo phase, gọi run-plan tuần tự, gói 2 chỉ giao khi
    report gói 1 status pass."""

    def _write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def _packet_file(self, n, task_ids):
        body = f"# GÓI PLAN s1 — round {n}\n" + "".join(
            f"## TASK {t}\nMục tiêu: demo.\nTest: true\n" for t in task_ids)
        return self._write(f"plan-round-{n}.task.md", body)

    def _run_packet(self, packet, round_no):
        return self.run_cli(
            "run-plan", "--engine", "codex", "--model", "m-test",
            "--task-file", packet, "--worktree", self.worktree,
            "--slug", "s1", "--round", str(round_no))

    def test_two_phase_sequential_dispatch(self):
        plan = self._write("plan.md", (
            "# PLAN\n## P1 — a\n" +
            "".join(f"- [ ] **T1.{i}** v — Test: t\n" for i in range(1, 5)) +
            "## P2 — b\n" +
            "".join(f"- [ ] **T2.{i}** v — Test: t\n" for i in range(1, 4))))
        code, out, _ = self.run_cli("split-plan", plan)
        self.assertEqual(code, 0)
        packets = json.loads(out)
        self.assertEqual(len(packets), 2)

        # Gói 1
        self.set_response(1, good_plan_report(tasks=[
            good_report(task_id=t) for t in packets[0]["tasks"]]))
        p1 = self._packet_file(1, packets[0]["tasks"])
        code, out, _ = self._run_packet(p1, 1)
        self.assertEqual(code, 0)
        rep1 = json.loads(out)
        self.assertEqual(rep1["status"], "done")
        self.assertEqual(len(self.calls()), 1)  # gói 2 chưa được giao

        # Gói 2 CHỈ giao khi gói 1 pass
        self.assertTrue(all(t["status"] == "done" for t in rep1["tasks"]))
        self.set_response(2, good_plan_report(tasks=[
            good_report(task_id=t) for t in packets[1]["tasks"]]))
        p2 = self._packet_file(2, packets[1]["tasks"])
        code, out, _ = self._run_packet(p2, 2)
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), 2)
        for n in (1, 2):
            path = os.path.join(self.project, "docs", "tdq", "external",
                                "s1", f"plan-round-{n}.json")
            self.assertTrue(os.path.exists(path))

    def test_blocked_first_packet_stops_dispatch(self):
        self.set_response(1, good_plan_report(
            status="blocked",
            tasks=[good_report(task_id="T1.1", status="blocked")],
            notes="thiếu quyết định"))
        p1 = self._packet_file(1, ["T1.1"])
        code, out, _ = self._run_packet(p1, 1)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["status"], "blocked")
        # Orchestrator thấy blocked → không giao gói 2: không có call thứ 2
        self.assertEqual(len(self.calls()), 1)


class SplitPlanMcpTest(StubBase):
    """T1.2 (skill-vao-goi-external) — task (mcp) tách gói riêng, khóa skills."""

    def _plan(self, text):
        path = os.path.join(self.tmp, "mcpplan.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_mcp_task_mid_phase_three_packets(self):
        body = ("# PLAN\n## P1 — a\n"
                "- [ ] **T1.1** v — Test: t\n"
                "  - Dùng: `graphify`\n"
                "- [ ] **T1.2** v — Test: t\n"
                "  - Dùng: `notion` (mcp)\n"
                "- [ ] **T1.3** v — Test: t\n")
        code, out, err = self.run_cli("split-plan", self._plan(body))
        self.assertEqual(code, 0)
        packets = json.loads(out)
        self.assertEqual(len(packets), 3)
        self.assertEqual(packets[0]["tasks"], ["T1.1"])
        self.assertNotIn("mcp", packets[0])
        self.assertEqual(packets[0]["skills"], ["graphify"])
        self.assertEqual(packets[1]["tasks"], ["T1.2"])
        self.assertIs(packets[1]["mcp"], True)
        self.assertEqual(packets[2]["tasks"], ["T1.3"])
        self.assertEqual(packets[2]["skills"], [])
        # Log service: lệnh không có slug → stderr có dòng timestamp
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T")

    def test_no_mcp_keeps_single_packet(self):
        body = ("# PLAN\n## P1 — a\n"
                "- [ ] **T1.1** v — Test: t\n"
                "  - Dùng: `tdq-build`\n"
                "- [ ] **T1.2** v — Test: t\n")
        code, out, _ = self.run_cli("split-plan", self._plan(body))
        self.assertEqual(code, 0)
        packets = json.loads(out)
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]["tasks"], ["T1.1", "T1.2"])
        self.assertEqual(packets[0]["skills"], ["tdq-build"])


class StripSkillSectionsTest(unittest.TestCase):
    """T1.3 (skill-vao-goi-external) — nội dung sau `## SKILL` đầu tiên
    không được đếm là TASK."""

    PACKET = ("# GÓI PLAN s — round 1\n"
              "## TASK T1\nMục tiêu: a.\nTest: true\n"
              "## TASK T2\nMục tiêu: b.\nTest: true\n"
              "## SKILL graphify — SKILL.md\n"
              "nội dung skill có ví dụ:\n"
              "## TASK T9\n(chỉ là ví dụ trong skill)\n"
              "## SKILL graphify — references/usage.md\nthêm nữa\n")

    def test_count_ignores_skill_sections(self):
        self.assertEqual(external_task.count_packet_tasks(self.PACKET), 2)

    def test_task_id_ignores_skill_sections(self):
        text = ("## SKILL x — SKILL.md\n# TASK FAKE\n")
        self.assertEqual(external_task._task_id(text, "/tmp/goi-abc.md"),
                         "goi-abc")


class SkillResolveTest(StubBase):
    """T2.1 (skill-vao-goi-external) — resolver 3 tầng: repo → ~/.claude/skills
    → plugin; trùng tên → nguồn trước thắng + cảnh báo."""

    def _mk_skill(self, root, name, body="---\nname: x\n---\nNội dung.\n"):
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(body)
        return d

    def setUp(self):
        super().setUp()
        self.home = os.path.join(self.tmp, "home")
        self.repo_skills = os.path.join(self.project, "skills")
        self.user_skills = os.path.join(self.home, ".claude", "skills")
        os.makedirs(self.user_skills, exist_ok=True)
        # Plugin giả: settings bật plugin, installed_plugins trỏ installPath
        plug_install = os.path.join(self.home, "plug", "demo")
        self.plugin_skills = os.path.join(plug_install, "skills")
        os.makedirs(os.path.join(self.home, ".claude", "plugins"), exist_ok=True)
        with open(os.path.join(self.home, ".claude", "settings.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"enabledPlugins": {"demo@m": True}}, f)
        with open(os.path.join(self.home, ".claude", "plugins",
                               "installed_plugins.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"plugins": {"demo@m": [
                {"installPath": plug_install}]}}, f)
        self._mk_skill(self.plugin_skills, "plug-only")

    def env(self):
        return {"HOME": self.home}

    def test_tier2_user_skills(self):
        self._mk_skill(self.user_skills, "user-only")
        code, out, _ = self.run_cli("skill-dump", "user-only", env=self.env())
        self.assertEqual(code, 0)
        self.assertIn("## SKILL user-only — SKILL.md", out)

    def test_tier3_plugin_skills(self):
        code, out, _ = self.run_cli("skill-dump", "plug-only", env=self.env())
        self.assertEqual(code, 0)
        self.assertIn("## SKILL plug-only — SKILL.md", out)

    def test_duplicate_repo_wins_with_warning(self):
        self._mk_skill(self.repo_skills, "dup", "---\nname: d\n---\nREPO-BODY\n")
        self._mk_skill(self.user_skills, "dup", "---\nname: d\n---\nUSER-BODY\n")
        code, out, err = self.run_cli("skill-dump", "dup", env=self.env())
        self.assertEqual(code, 0)
        self.assertIn("REPO-BODY", out)
        self.assertNotIn("USER-BODY", out)
        self.assertIn("trùng tên", err)


class SkillDumpTest(SkillResolveTest):
    """T2.2 (skill-vao-goi-external) — dump nguyên văn + references, skill ma."""

    def test_dump_body_and_references_in_order(self):
        d = self._mk_skill(self.repo_skills, "full-skill",
                           "---\nname: f\ndescription: x\n---\nBODY-CHÍNH\n")
        refs = os.path.join(d, "references")
        os.makedirs(refs)
        for fname, content in (("a-ref.md", "REF-A"), ("b-ref.md", "REF-B")):
            with open(os.path.join(refs, fname), "w", encoding="utf-8") as f:
                f.write(content + "\n")
        code, out, err = self.run_cli("skill-dump", "full-skill", env=self.env())
        self.assertEqual(code, 0)
        self.assertNotIn("frontmatter", out)
        self.assertNotIn("name: f", out)          # frontmatter đã bỏ
        i_skill = out.index("## SKILL full-skill — SKILL.md")
        i_a = out.index("## SKILL full-skill — references/a-ref.md")
        i_b = out.index("## SKILL full-skill — references/b-ref.md")
        self.assertLess(i_skill, i_a)
        self.assertLess(i_a, i_b)
        self.assertIn("BODY-CHÍNH", out)
        self.assertIn("REF-A", out)
        self.assertIn("REF-B", out)
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T")   # log stderr timestamp

    def test_missing_skill_exit_1(self):
        code, _, err = self.run_cli("skill-dump", "khong-ton-tai",
                                    env=self.env())
        self.assertEqual(code, 1)
        self.assertIn("khong-ton-tai", err)


class SkillDumpCompressionTest(SkillResolveTest):
    """T1.4 (toi-uu-p0-p1-workflow) — chỉ giữ khối hợp đồng máy-đọc + lệnh CLI,
    bỏ phần diễn giải dài, dump skill tdq-build THẬT trong repo (21.960 byte
    nguyên văn — số đo trong knowledge P1-5)."""

    def _raw_dump_bytes(self):
        skill_dir = os.path.join(ROOT, "skills", "tdq-build")
        total = 0
        with open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8") as f:
            total += len(external_task._strip_frontmatter(f.read()).encode("utf-8"))
        refs_dir = os.path.join(skill_dir, "references")
        for name in sorted(os.listdir(refs_dir)):
            if name.endswith(".md"):
                with open(os.path.join(refs_dir, name), encoding="utf-8") as f:
                    total += len(f.read().encode("utf-8"))
        return total

    def test_dump_real_tdq_build_shrinks_and_keeps_contract_fields(self):
        env = dict(self.env(), TDQ_PROJECT_DIR=ROOT)
        code, out, _ = self.run_cli("skill-dump", "tdq-build", env=env)
        self.assertEqual(code, 0)
        for field in ("Dùng", "Nạp", "Để", "Ra", "Kiểm"):
            self.assertIn(field, out)
        self.assertIn("scripts/tdq_finish.py", out)  # lệnh CLI cụ thể phải còn
        raw_bytes = self._raw_dump_bytes()
        self.assertLess(len(out.encode("utf-8")), raw_bytes)


class CheckPacketSkillsTest(unittest.TestCase):
    """T3.1 (skill-vao-goi-external) — hàm thuần đối chiếu gói ↔ plan."""

    PLAN = ("# PLAN\n## P1 — a\n"
            "- [ ] **T1** v — Test: t\n"
            "  - Dùng: `notion` (mcp)\n"
            "- [ ] **T2** v — Test: t\n"
            "  - Dùng: `graphify`\n"
            "- [ ] **T3** v — Test: t\n"
            "  - Dùng: `notion-db`\n")

    def packet(self, tasks, skills=()):
        body = "# GÓI PLAN\n" + "".join(
            f"## TASK {t}\nTest: true\n" for t in tasks)
        for s in skills:
            body += f"## SKILL {s} — SKILL.md\nnội dung\n"
        return body

    def test_missing_skill_warns(self):
        warns = external_task.check_packet_skills(
            self.packet(["T2"]), self.PLAN)
        self.assertEqual(len(warns), 1)
        self.assertIn("graphify", warns[0])

    def test_full_packet_silent(self):
        warns = external_task.check_packet_skills(
            self.packet(["T2"], skills=["graphify"]), self.PLAN)
        self.assertEqual(warns, [])

    def test_mcp_leak_warns(self):
        warns = external_task.check_packet_skills(
            self.packet(["T1"]), self.PLAN)
        self.assertEqual(len(warns), 1)
        self.assertIn("mcp", warns[0])

    def test_no_prefix_match(self):
        # Gói có `## SKILL notion-db` KHÔNG được tính là có `notion` và ngược lại
        warns = external_task.check_packet_skills(
            self.packet(["T3"], skills=["notion"]), self.PLAN)
        self.assertEqual(len(warns), 1)
        self.assertIn("notion-db", warns[0])


class RunPlanFileWarningTest(StubBase):
    """T3.2 (skill-vao-goi-external) — run-plan --plan-file: cảnh báo, vẫn chạy."""

    def _write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def _go(self, with_flag):
        plan = self._write("plan.md",
                           "# PLAN\n## P1 — a\n"
                           "- [ ] **T1** v — Test: t\n"
                           "  - Dùng: `graphify`\n")
        packet = self._write("packet.md",
                             "# GÓI PLAN s1 — round 1\n"
                             "## TASK T1\nMục tiêu: demo.\nTest: true\n")
        self.set_response(1, good_plan_report(
            tasks=[good_report(task_id="T1")]))
        args = ["run-plan", "--engine", "codex", "--model", "m", "--task-file",
                packet, "--worktree", self.worktree, "--slug", "s1",
                "--round", "1"]
        if with_flag:
            args += ["--plan-file", plan]
        return self.run_cli(*args)

    def test_missing_skill_warns_but_runs(self):
        code, out, err = self._go(with_flag=True)
        self.assertEqual(code, 0)                      # exit theo engine (stub OK)
        self.assertIn("## SKILL graphify", err)        # cảnh báo thiếu skill
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T") # timestamp stderr
        self.assertIn("dòng", err)                     # log số dòng gói
        self.assertEqual(json.loads(out)["kind"], "plan")

    def test_without_flag_no_check(self):
        code, _, err = self._go(with_flag=False)
        self.assertEqual(code, 0)
        self.assertNotIn("## SKILL", err)


class LogServiceUnifiedTest(RunPlanFileWarningTest):
    """T5.2 (skill-vao-goi-external) — 3 đường log cùng cơ chế: không slug →
    stderr timestamp; có slug → run.log; TDQ_EXTERNAL_LOG=0 tắt cả."""

    TS = r"\[\d{4}-\d{2}-\d{2}T"

    def _skill_fixture(self):
        d = os.path.join(self.project, "skills", "log-demo")
        os.makedirs(d)
        with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("Nội dung.\n")

    def test_skill_dump_stderr_timestamp_and_off_switch(self):
        self._skill_fixture()
        _, _, err = self.run_cli("skill-dump", "log-demo")
        self.assertRegex(err, self.TS)
        _, _, err = self.run_cli("skill-dump", "log-demo",
                                 env={"TDQ_EXTERNAL_LOG": "0"})
        self.assertNotRegex(err, self.TS)

    def test_split_plan_stderr_timestamp_and_off_switch(self):
        plan = self._write("lplan.md",
                           "# PLAN\n## P1 — a\n- [ ] **T1** v — Test: t\n")
        _, _, err = self.run_cli("split-plan", plan)
        self.assertRegex(err, self.TS)
        _, _, err = self.run_cli("split-plan", plan,
                                 env={"TDQ_EXTERNAL_LOG": "0"})
        self.assertNotRegex(err, self.TS)

    def test_run_plan_warning_lands_in_slug_run_log(self):
        self._go(with_flag=True)
        with open(self.log_path(), encoding="utf-8") as f:
            log = f.read()
        self.assertRegex(log, self.TS)
        self.assertIn("cảnh báo skill", log)
        self.assertIn("dòng", log)          # số dòng gói


class ParseDungLinesTest(unittest.TestCase):
    """T1.1 (skill-vao-goi-external) — cú pháp chuẩn dòng `Dùng:` + nhãn (mcp)."""

    PLAN = (
        "# PLAN\n## P1 — a\n"
        "- [ ] **T1.1** việc — Test: t\n"
        "  - Dùng: `tdq-build`\n"
        "  - Nạp: đọc skill.\n"
        "- [ ] **T1.2** việc — Test: t\n"
        "  - Dùng: `notion` (mcp)\n"
        "- [ ] **T1.3** việc hai skill — Test: t\n"
        "  - Dùng: `graphify`\n"
        "  - Kiểm: lệnh\n"
        "  - Dùng: `mongodb` (mcp)\n"
        "- [ ] **T1.4** không skill — Test: t\n"
    )

    def test_variants(self):
        parsed = external_task.parse_dung_lines(self.PLAN)
        self.assertEqual(parsed["T1.1"], [("tdq-build", False)])
        self.assertEqual(parsed["T1.2"], [("notion", True)])
        self.assertEqual(parsed["T1.3"], [("graphify", False), ("mongodb", True)])
        self.assertNotIn("T1.4", parsed)

    def test_malformed_lines_ignored(self):
        text = ("- [ ] **T2.1** v — Test: t\n"
                "  - Dùng: no-backtick\n"
                "  - Dùng: `bad name` (mcp)\n"
                "  - Dùng: `ok-skill` (mcp) thừa đuôi\n")
        self.assertEqual(external_task.parse_dung_lines(text), {})


if __name__ == "__main__":
    unittest.main()
