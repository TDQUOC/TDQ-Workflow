"""P6 — doc không được mô tả hành vi mà 0.3.0 đã bỏ.

Doc nói "hook chặn" trong khi hook chỉ nhắc là kiểu sai nguy hiểm: user tin rằng có
rào an toàn không tồn tại. Nên câu chữ của thời gate cứng bị cấm ở doc đang hiệu lực.
"""
import os
import re
import unittest

from helper import ROOT

# doc lịch sử / doc do workflow sinh ra trong lúc chạy → không soát
SKIP_DIRS = {".git", "__pycache__", "docs/archive", "docs/tdq", "docs/workinglog",
             "graphify-out", "node_modules"}
BANNED = {
    "gate cứng": "0.3.0 không còn gate chặn vì chưa duyệt",
    "the hook confirms": "hook không xác nhận thay user",
    "hooks enforce": "hook nhắc, không enforce",
    "hook chặn": "chỉ working log mới chặn — nói rõ ra thay vì nói chung",
    "tdq-approve": "skill này đã bỏ",
}
# ngoại lệ: file nói VỀ việc đã bỏ gate (changelog, lưu trữ)
ALLOW_FILES = {"CHANGELOG.md"}


def relevant_files():
    for dirpath, dirnames, files in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        if any(rel_dir == s or rel_dir.startswith(s + os.sep) for s in SKIP_DIRS):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(files):
            if name.endswith(".md") and name not in ALLOW_FILES:
                yield os.path.join(dirpath, name)


class DocsConsistencyTest(unittest.TestCase):
    def test_no_hard_gate_language(self):
        hits = []
        for path in relevant_files():
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
            for i, line in enumerate(lines, 1):
                low = line.lower()
                for phrase, why in BANNED.items():
                    if phrase in low:
                        rel = os.path.relpath(path, ROOT)
                        hits.append(f"{rel}:{i}: \"{phrase}\" — {why}")
        self.assertEqual(hits, [], "doc còn mô tả hành vi đã bỏ:\n" + "\n".join(hits))

    def test_marketplace_and_plugin_agree(self):
        import json
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            plugin = json.load(f)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
            market = json.load(f)
        self.assertEqual(plugin["name"], market["plugins"][0]["name"])
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        for text in (plugin["description"], market["description"]):
            self.assertNotIn("gate duyệt cứng", text.lower())

    def test_changelog_documents_current_version(self):
        import json
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            version = json.load(f)["version"]
        with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as f:
            text = f.read()
        heads = re.findall(r"^## (\d+\.\d+\.\d+)", text, re.MULTILINE)
        self.assertIn(version, heads, "changelog chưa có mục cho bản đang phát hành")
        self.assertEqual(heads[0], version, "mục đầu changelog phải là bản đang phát hành")

    def test_archive_marked_as_historical(self):
        path = os.path.join(ROOT, "docs", "archive", "v0.1", "README.md")
        self.assertTrue(os.path.isfile(path), "thiếu README giải thích thư mục lưu trữ")

    def test_no_ds_store(self):
        junk = []
        for dirpath, dirnames, files in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            junk += [os.path.join(dirpath, n) for n in files if n == ".DS_Store"]
        self.assertEqual(junk, [])


if __name__ == "__main__":
    unittest.main()
