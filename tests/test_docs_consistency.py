"""Kiểm tính toàn vẹn repo — manifest và changelog phải khớp bản đang phát hành.

Phần cũ soát câu chữ trong .md đã bỏ (2026-08-08): đó là test văn phong, chặn đúng
việc rút gọn skill mà không bắt được lỗi hành vi nào.
"""
import json
import os
import re
import unittest

from helper import ROOT


class RepoIntegrityTest(unittest.TestCase):
    def test_marketplace_and_plugin_agree(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            plugin = json.load(f)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
            market = json.load(f)
        self.assertEqual(plugin["name"], market["plugins"][0]["name"])
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")

    def test_changelog_documents_current_version(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            version = json.load(f)["version"]
        with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as f:
            text = f.read()
        heads = re.findall(r"^## (\d+\.\d+\.\d+)", text, re.MULTILINE)
        self.assertIn(version, heads, "changelog chưa có mục cho bản đang phát hành")
        self.assertEqual(heads[0], version, "mục đầu changelog phải là bản đang phát hành")

    def test_no_ds_store(self):
        junk = []
        for dirpath, dirnames, files in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            junk += [os.path.join(dirpath, n) for n in files if n == ".DS_Store"]
        self.assertEqual(junk, [])


if __name__ == "__main__":
    unittest.main()
