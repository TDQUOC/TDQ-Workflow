"""P5 (toi-uu-p0-p1-workflow) — ngưỡng digest "≤1.500 ký tự" phải đồng bộ giữa
7 file `agents/*.md` và nơi tdq-intake định nghĩa nó cho `search-scout`
(`skills/tdq-intake/references/analyze-full.md`, sau khi T3.1 tách Phần B ra khỏi
SKILL.md — SKILL.md không còn chứa con số này).

Lệch số ở một chỗ nghĩa là agent digest theo ngưỡng cũ trong khi tài liệu điều
phối nói ngưỡng mới, hoặc ngược lại.
"""
import glob
import os
import re
import unittest

from helper import ROOT

AGENTS_DIR = os.path.join(ROOT, "agents")
ANALYZE_FULL = os.path.join(ROOT, "skills", "tdq-intake", "references", "analyze-full.md")

THRESHOLD_RE = re.compile(r"digest\s*≤\s*([\d.]+)\s*ký tự")


def _find_threshold(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    matches = THRESHOLD_RE.findall(text)
    return matches


class AgentDigestSyncTest(unittest.TestCase):
    def test_seven_agent_files_present(self):
        agent_files = sorted(glob.glob(os.path.join(AGENTS_DIR, "*.md")))
        self.assertEqual(len(agent_files), 7, agent_files)

    def test_all_thresholds_match(self):
        agent_files = sorted(glob.glob(os.path.join(AGENTS_DIR, "*.md")))
        sources = agent_files + [ANALYZE_FULL]
        found = {}
        for path in sources:
            matches = _find_threshold(path)
            self.assertTrue(matches, f"{path}: không tìm thấy ngưỡng digest ≤N ký tự")
            found[path] = matches[0]
        values = set(found.values())
        self.assertEqual(
            len(values), 1,
            f"Ngưỡng digest lệch nhau giữa các file: {found}",
        )


if __name__ == "__main__":
    unittest.main()
