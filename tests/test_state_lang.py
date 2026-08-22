"""Tests for the document-language field of the workflow state."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "scripts", "tdq_state.py")


class DocLangTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def run_tool(self, *args):
        env = dict(os.environ, TDQ_PROJECT_DIR=self.dir)
        return subprocess.run([sys.executable, TOOL, *args], capture_output=True,
                              text=True, env=env)

    def state(self):
        with open(os.path.join(self.dir, "docs", "tdq", "state.json"),
                  encoding="utf-8") as fh:
            return json.load(fh)

    def test_init_without_flag_defaults_to_vietnamese(self):
        self.run_tool("init", "2026-08-22-0100-demo", "full")
        self.assertEqual(self.state()["doc_lang"], "vi")

    def test_init_with_flag_stores_the_code(self):
        self.run_tool("init", "2026-08-22-0100-demo", "full", "--lang", "en")
        self.assertEqual(self.state()["doc_lang"], "en")

    def test_flag_may_come_before_the_lane(self):
        self.run_tool("init", "2026-08-22-0100-demo", "--lang", "ja", "full")
        state = self.state()
        self.assertEqual(state["doc_lang"], "ja")
        self.assertEqual(state["lane"], "full")

    def test_bad_code_is_refused_and_nothing_is_written(self):
        out = self.run_tool("init", "2026-08-22-0100-demo", "full", "--lang", "tiếng việt")
        self.assertNotEqual(out.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "docs", "tdq",
                                                     "state.json")))

    def test_set_accepts_a_valid_code_and_refuses_a_bad_one(self):
        self.run_tool("init", "2026-08-22-0100-demo", "full")
        self.assertEqual(self.run_tool("set", "doc_lang=fr").returncode, 0)
        self.assertEqual(self.state()["doc_lang"], "fr")
        self.assertNotEqual(self.run_tool("set", "doc_lang=???").returncode, 0)
        self.assertEqual(self.state()["doc_lang"], "fr")

    def test_get_prints_the_field(self):
        self.run_tool("init", "2026-08-22-0100-demo", "full", "--lang", "en")
        self.assertEqual(self.run_tool("get", "doc_lang").stdout.strip(), "en")

    def test_older_state_without_the_field_reads_as_vietnamese(self):
        path = os.path.join(self.dir, "docs", "tdq")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "state.json"), "w", encoding="utf-8") as fh:
            json.dump({"schema_version": 4, "active_request": "cu", "lane": "full",
                       "phase": "spec"}, fh)
        out = self.run_tool("get", "doc_lang")
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout.strip(), "vi")


if __name__ == "__main__":
    unittest.main()
