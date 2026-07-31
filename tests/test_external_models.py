"""Test external_models.py — list model available thật (stub binary, không mạng)."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "external_models.py")

AGY_MODELS = "gemini-3.6-flash-high\ngemini-3.6-flash-low\nclaude-sonnet-4-6\n"


class ModelsBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tdq-models-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin_dir = os.path.join(self.tmp, "bin")
        self.home = os.path.join(self.tmp, "home")
        self.project = os.path.join(self.tmp, "project")
        for d in (self.bin_dir, self.home, self.project):
            os.makedirs(d)
        self.count = os.path.join(self.tmp, "count.txt")
        # stub agy: in danh sách model
        self._write_stub("agy", f'printf \'%s\' "{AGY_MODELS}"\nexit 0\n')
        # stub codex: exit theo file exit_<slug>; đếm số lần probe
        self._write_stub("codex", (
            f'n=$(cat "{self.count}" 2>/dev/null || echo 0); n=$((n+1)); '
            f'echo $n > "{self.count}"\n'
            'slug=""; prev=""\n'
            'for a in "$@"; do [ "$prev" = "-m" ] && slug="$a"; prev="$a"; done\n'
            f'exit $(cat "{self.tmp}/exit_$slug" 2>/dev/null || echo 0)\n'))

    def _write_stub(self, name, body):
        path = os.path.join(self.bin_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\nPATH=/bin:/usr/bin\n" + body)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def set_exit(self, slug, code):
        with open(os.path.join(self.tmp, f"exit_{slug}"), "w") as f:
            f.write(str(code))

    def probes(self):
        try:
            with open(self.count, encoding="utf-8") as f:
                return int(f.read().strip())
        except OSError:
            return 0

    def run_cli(self, *args, env=None, with_stub=True):
        full_env = dict(os.environ, HOME=self.home, **(env or {}))
        full_env["PATH"] = self.bin_dir if with_stub else os.path.join(self.tmp, "x")
        proc = subprocess.run(
            [sys.executable, SCRIPT, *args], capture_output=True, text=True,
            timeout=60, cwd=self.project, env=full_env)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

    def cache_path(self):
        return os.path.join(self.home, ".claude", "cache",
                            "tdq-external-models.json")


class AgyListTest(ModelsBase):
    def test_lists_real_slugs(self):
        code, out, _ = self.run_cli("list", "agy")
        self.assertEqual(code, 0)
        self.assertIn("gemini-3.6-flash-high", out.splitlines())
        self.assertIn("claude-sonnet-4-6", out.splitlines())

    def test_missing_binary_exit_1(self):
        code, _, err = self.run_cli("list", "agy", with_stub=False)
        self.assertEqual(code, 1)
        self.assertIn("⚠️", err)

    def test_log_anchored_to_project_dir(self):
        # A17: chạy từ cwd lạ + TDQ_PROJECT_DIR → models.log nằm trong project
        elsewhere = os.path.join(self.tmp, "elsewhere")
        os.makedirs(elsewhere)
        full_env = dict(os.environ, HOME=self.home,
                        TDQ_PROJECT_DIR=self.project)
        full_env["PATH"] = self.bin_dir
        proc = subprocess.run(
            [sys.executable, SCRIPT, "list", "agy"], capture_output=True,
            text=True, timeout=60, cwd=elsewhere, env=full_env)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(
            self.project, "docs", "tdq", "external", "models.log")))
        self.assertFalse(os.path.exists(os.path.join(elsewhere, "docs")))


class CodexProbeTest(ModelsBase):
    ENV = {"TDQ_CODEX_MODELS": "m-ok,m-bad"}

    def test_probe_ok_and_unverified(self):
        self.set_exit("m-ok", 0)
        self.set_exit("m-bad", 1)
        code, out, _ = self.run_cli("list", "codex", env=self.ENV)
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertIn("m-ok", lines)
        self.assertIn("m-bad (chưa xác minh)", lines)
        self.assertEqual(self.probes(), 2)
        with open(self.cache_path(), encoding="utf-8") as f:
            cache = json.load(f)
        self.assertEqual(cache["ok"], ["m-ok"])

    def test_cache_hit_skips_probe(self):
        self.set_exit("m-ok", 0)
        self.set_exit("m-bad", 1)
        self.run_cli("list", "codex", env=self.ENV)
        before = self.probes()
        code, out, _ = self.run_cli("list", "codex", env=self.ENV)
        self.assertEqual(code, 0)
        self.assertEqual(self.probes(), before)          # không probe lại
        self.assertIn("(cache", out)
        self.assertIn("m-ok", out.splitlines()[0] if out else "")

    def test_all_fail_still_exit_0(self):
        self.set_exit("m-ok", 1)
        self.set_exit("m-bad", 1)
        code, out, _ = self.run_cli("list", "codex", env=self.ENV)
        self.assertEqual(code, 0)
        for line in out.splitlines():
            if line.startswith("m-"):
                self.assertIn("(chưa xác minh)", line)

    def test_missing_binary_all_unverified_exit_0(self):
        code, out, _ = self.run_cli("list", "codex", env=self.ENV, with_stub=False)
        self.assertEqual(code, 0)
        self.assertIn("(chưa xác minh)", out)

    def test_bad_usage_exit_2(self):
        for args in (("list",), ("list", "gemini"), ("nope",)):
            code, _, err = self.run_cli(*args)
            self.assertEqual(code, 2, args)
            self.assertIn("usage", err)


if __name__ == "__main__":
    unittest.main()
