"""Tests for scripts/i18n_check.py — the Vietnamese-leftover scanner."""
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "scripts", "i18n_check.py")


def run(*args, env=None):
    e = dict(os.environ)
    e.setdefault("TDQ_LOG", "0")
    if env:
        e.update(env)
    return subprocess.run([sys.executable, TOOL, *args], capture_output=True,
                          text=True, env=e)


class ScanTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def write(self, name, body):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        return path

    def test_clean_file_exits_zero(self):
        path = self.write("clean.py", "# a comment\nX = 'plain ascii'\n")
        out = run(path)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("0", out.stdout)

    def test_leftover_line_exits_one_and_is_printed(self):
        path = self.write("dirty.py", "# ghi chú tiếng Việt\nX = 1\n")
        out = run(path)
        self.assertEqual(out.returncode, 1)
        self.assertIn("dirty.py:1", out.stdout)

    def test_python_lines_split_into_comment_string_body(self):
        path = self.write("mix.py", "\n".join([
            "# chú thích",
            "X = 'chuỗi máy'",
            "def f():",
            "    biến = 1",
            "",
        ]))
        out = run(path, "--json")
        self.assertEqual(out.returncode, 1)
        import json
        data = json.loads(out.stdout)
        kinds = {row["line"]: row["kind"] for row in data["findings"]}
        self.assertEqual(kinds[1], "comment")
        self.assertEqual(kinds[2], "string")
        self.assertEqual(kinds[4], "body")

    def test_kind_filter_only_reports_that_kind(self):
        path = self.write("mix2.py", "# chú thích\nX = 'chuỗi'\n")
        out = run(path, "--kind", "comment", "--json")
        import json
        data = json.loads(out.stdout)
        self.assertEqual([row["line"] for row in data["findings"]], [1])

    def test_allow_marker_skips_the_line(self):
        path = self.write("allowed.py", "# tiếng Việt cố ý  i18n-allow\n")
        out = run(path)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_markdown_counts_every_line_as_body(self):
        path = self.write("doc.md", "Câu tiếng Việt\n")
        out = run(path, "--json")
        import json
        data = json.loads(out.stdout)
        self.assertEqual(data["findings"][0]["kind"], "body")

    def test_directory_is_walked(self):
        os.mkdir(os.path.join(self.dir, "sub"))
        self.write(os.path.join("sub", "deep.py"), "X = 'lỗi'\n")
        out = run(self.dir)
        self.assertEqual(out.returncode, 1)
        self.assertIn("deep.py", out.stdout)

    def test_missing_path_is_a_syntax_error(self):
        out = run(os.path.join(self.dir, "nope.py"))
        self.assertEqual(out.returncode, 2)

    def test_unparsable_python_still_scanned_as_body(self):
        path = self.write("broken.py", "def (:\n    x = 'lỗi cú pháp'\n")
        out = run(path, "--json")
        self.assertEqual(out.returncode, 1)

    def test_log_service_on_by_default_and_off_by_env(self):
        path = self.write("dirty2.py", "# tiếng Việt\n")
        loud = run(path, env={"TDQ_LOG": "1"})
        self.assertIn("i18n_check:", loud.stderr)
        quiet = run(path, env={"TDQ_LOG": "0"})
        self.assertEqual(quiet.stderr, "")


    def test_comment_above_fence_exempts_the_whole_block(self):
        """Khuôn chép nguyên văn không mang được marker bên trong — marker đứng trên fence."""
        path = self.write("khuon.md", "\n".join([
            "# Doc", "", "<!-- i18n-allow: khuôn user đọc -->", "```",
            "Bạn duyệt plan này chứ?", "```", ""]))
        out = run(path)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_fence_without_the_comment_is_still_reported(self):
        path = self.write("khuon2.md", "\n".join([
            "# Doc", "", "```", "Bạn duyệt plan này chứ?", "```", ""]))
        out = run(path)
        self.assertEqual(out.returncode, 1)
        self.assertIn("khuon2.md:4", out.stdout)

    def test_exemption_stops_at_the_closing_fence(self):
        path = self.write("khuon3.md", "\n".join([
            "<!-- i18n-allow -->", "```", "Bạn duyệt chứ?", "```",
            "câu này ngoài khối", ""]))
        out = run(path)
        self.assertEqual(out.returncode, 1)
        self.assertIn("khuon3.md:5", out.stdout)


if __name__ == "__main__":
    unittest.main()
