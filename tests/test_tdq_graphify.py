"""Contract tests for TDQ's full Graphify transaction."""
import json
import os
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_graphify  # noqa: E402


class FakeRun:
    def __init__(self, results):
        self.results = iter(results)
        self.calls = []

    def __call__(self, command, cwd, timeout):
        self.calls.append((command, cwd, timeout))
        result = next(self.results)
        if command == ["graphify", "wiki"] and result[0] == 0:
            output = os.path.join(cwd, "graphify-out", "wiki")
            os.makedirs(output, exist_ok=True)
            with open(os.path.join(output, "index.md"), "w", encoding="utf-8") as handle:
                handle.write("# Derived wiki\n")
        return result


class FullTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        with open(os.path.join(self.temp.name, "app.py"), "w", encoding="utf-8") as handle:
            handle.write("print('ok')\n")
        with open(os.path.join(self.temp.name, "README.md"), "w", encoding="utf-8") as handle:
            handle.write("# Docs\n")

    def test_success_runs_full_then_wiki_and_writes_manifest(self):
        runner = FakeRun([(0, "extract ok"), (0, "wiki ok")])
        result = tdq_graphify.full_extract(self.temp.name, runner=runner)
        self.assertTrue(result.ok, result.message)
        self.assertEqual(runner.calls[0][0], ["graphify", "extract", "."])
        self.assertNotIn("--code-only", runner.calls[0][0])
        self.assertEqual(runner.calls[1][0], ["graphify", "wiki"])
        manifest = os.path.join(self.temp.name, "graphify-out", "tdq-full-manifest.json")
        with open(manifest, encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(data["status"], "fresh")
        self.assertTrue(data["inputs"])
        self.assertNotIn("token", json.dumps(data).lower())

    def test_extract_failure_is_closed_and_skips_wiki(self):
        runner = FakeRun([(1, "backend unavailable")])
        result = tdq_graphify.full_extract(self.temp.name, runner=runner)
        self.assertFalse(result.ok)
        self.assertTrue(result.stale)
        self.assertIn("LSP + grep", result.message)
        self.assertEqual(len(runner.calls), 1)
        self.assertFalse(os.path.exists(os.path.join(self.temp.name, "graphify-out", "tdq-full-manifest.json")))

    def test_wiki_failure_is_closed_and_does_not_publish_manifest(self):
        runner = FakeRun([(0, "extract ok"), (1, "wiki failed")])
        result = tdq_graphify.full_extract(self.temp.name, runner=runner)
        self.assertFalse(result.ok)
        self.assertIn("wiki failed", result.message)
        self.assertFalse(os.path.exists(os.path.join(self.temp.name, "graphify-out", "tdq-full-manifest.json")))

    def test_stale_detects_doc_or_config_change(self):
        runner = FakeRun([(0, "extract ok"), (0, "wiki ok")])
        self.assertTrue(tdq_graphify.full_extract(self.temp.name, runner=runner).ok)
        self.assertFalse(tdq_graphify.freshness(self.temp.name).stale)
        with open(os.path.join(self.temp.name, "README.md"), "a", encoding="utf-8") as handle:
            handle.write("changed\n")
        self.assertTrue(tdq_graphify.freshness(self.temp.name).stale)

    def test_log_metadata_does_not_include_secrets(self):
        previous = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "secret-value"
        try:
            runner = FakeRun([(0, "extract ok"), (0, "wiki ok")])
            result = tdq_graphify.full_extract(self.temp.name, runner=runner)
            self.assertTrue(result.ok)
            manifest = os.path.join(self.temp.name, "graphify-out", "tdq-full-manifest.json")
            with open(manifest, encoding="utf-8") as handle:
                self.assertNotIn("secret-value", handle.read())
        finally:
            if previous is None:
                os.environ.pop("OPENAI_API_KEY")
            else:
                os.environ["OPENAI_API_KEY"] = previous

    def test_graphify_output_is_not_an_input(self):
        os.makedirs(os.path.join(self.temp.name, "graphify-out", "wiki"))
        with open(os.path.join(self.temp.name, "graphify-out", "wiki", "index.md"), "w", encoding="utf-8") as handle:
            handle.write("derived wiki\n")
        paths = tdq_graphify.input_files(self.temp.name)
        self.assertEqual(sorted(path.name for path in paths), ["README.md", "app.py"])


if __name__ == "__main__":
    unittest.main()
