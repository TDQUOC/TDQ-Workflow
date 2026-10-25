"""Real-engine acceptance checks; missing dependencies fail, never silently skip."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "tdq_archify.py"
FIXTURES = ROOT / "tests" / "fixtures" / "archify"


class RealArchifyE2E(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        (self.project / "src").mkdir()
        (self.project / "src" / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.models = self.project / "docs" / "tdq" / "artifacts"
        self.models.mkdir(parents=True)
        for name in ("workflow.json", "ba.json", "master.json"):
            shutil.copy2(FIXTURES / name, self.models / name)
        for command in (["git", "init", "-q"], ["git", "add", "src"],
                        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "commit", "-qm", "fixture source"]):
            result = subprocess.run(command, cwd=self.project, capture_output=True,
                                    text=True, encoding="utf-8", timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)

    def run_cli(self, *args, expected=0):
        env = dict(os.environ, ARCHIFY_UPDATE_CHECK_DISABLED="1", TDQ_LOG="0")
        result = subprocess.run([sys.executable, str(CLI), *map(str, args)],
                                cwd=self.project, capture_output=True, text=True,
                                encoding="utf-8", timeout=120, env=env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_full_and_quick_native_binding_and_mutation(self):
        for lane, folder, suffix in (("full", "spec", "preview"), ("quick", "plan", "flow")):
            with self.subTest(lane=lane):
                directory = self.project / "docs" / "tdq" / folder
                directory.mkdir(parents=True, exist_ok=True)
                document = directory / "task.md"
                document.write_text("# Task\n\nValidate input before saving.\n", encoding="utf-8")
                output = directory / f"task-{suffix}.html"
                rendered = self.run_cli("render", "--type", "workflow", "--candidate",
                                        self.models / "workflow.json", "--out", output,
                                        "--document", document, "--lane", lane, "--request", "fixture",
                                        "--quality", "standard")
                receipt = json.loads(rendered.stdout)
                self.assertEqual(receipt["gates"]["browser-check"], "pass")
                self.assertTrue(output.is_file())
                manifest = output.with_suffix(".manifest.json")
                self.run_cli("verify", "--document", document, "--manifest", manifest)
                document.write_text(document.read_text(encoding="utf-8") + "Changed design.\n", encoding="utf-8")
                self.run_cli("verify", "--document", document, "--manifest", manifest, expected=1)

    def test_master_html_freshness_and_refresh(self):
        args = ("sync-master", "--model", self.models / "master.json", "--project", self.project,
                "--quality", "standard")
        self.run_cli(*args)
        index = self.project / "docs" / "architecture" / "index.html"
        self.assertTrue(index.is_file())
        status = json.loads(self.run_cli("status").stdout)
        self.assertEqual(status["status"], "current")
        (self.project / "src" / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        stale = json.loads(self.run_cli("status", expected=1).stdout)
        self.assertEqual(stale["status"], "stale")
        self.run_cli(*args)
        self.assertEqual(json.loads(self.run_cli("status").stdout)["status"], "current")
