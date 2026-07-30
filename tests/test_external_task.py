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
        self.assertEqual(schema["type"], "object")
        self.assertIn("task_id", schema["required"])

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


if __name__ == "__main__":
    unittest.main()
