"""Chống bỏ sót khi rút gọn ~/.claude/CLAUDE.md (spec 2026-08-05 §2).

3 điều kiện, đo trên BẢN MẪU trong repo `docs/claude-md-mau.md`:
  (a) mọi luật bị CHUYỂN phải tìm được ở đúng file đích;
  (b) luật bất biến (git, trình bày, logging, 5 luật kích hoạt TDQ) vẫn còn trong bản mẫu;
  (c) bản mẫu ≤ 3.500 byte.

Không so với `~/.claude/CLAUDE.md`: suite phải chạy được ở máy chưa cài,
và file ngoài repo không phải thứ test của repo được phép đòi hỏi.
"""

import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO, "docs", "claude-md-mau.md")
MAX_BYTES = 3500

# (mô tả, đường dẫn file đích tương đối repo, các chuỗi phải có mặt)
MOVED = [
    ("§3 failover Tavily", "skills/tdq-conventions/references/tavily.md",
     ["tavily-primary", "tavily-backup", "websearch"]),
    ("§6 quy ước working log", "skills/tdq-conventions/SKILL.md",
     ["docs/workinglog", "working log"]),
    ("§7 xử lý issue user báo", "skills/tdq-intake/references/issue-triage.md",
     ["log", "computer use", "spec"]),
    ("§8 checklist lập spec", "skills/tdq-spec/references/spec-template.md",
     ["qc", "download"]),
    ("§10 bảng định tuyến plugin", "skills/tdq-conventions/references/plugin-routing.md",
     ["data-engineering", "desktop-commander", "notion", "mongodb"]),
    ("§9 chi tiết mode thực thi", "skills/tdq-plan/SKILL.md",
     ["main", "subagent"]),
]

# Luật KHÔNG được rời bản lõi — mất một dòng là mất một hàng rào an toàn.
INVARIANTS = [
    ("§2 cấm tiền tố tên branch", ["antigravity", "gemini", "codex"]),
    ("§2 cấm trailer AI trong commit", ["co-authored-by"]),
    ("§2 chỉ commit khi user yêu cầu", ["commit"]),
    ("§3 cấm lộ API key", ["api key"]),
    ("§3 không bịa thông tin", ["không được bịa"]),
    ("§4 trình bày ngắn gọn", ["ngắn gọn"]),
    ("§5 log service cho sản phẩm", ["log"]),
    ("§9①  mọi prompt mới vào intake", ["tdq-intake"]),
    ("§9② chỉ user duyệt", ["chỉ người dùng duyệt", "hỏi"]),
    ("§9③ state chỉ ghi qua script", ["tdq_state.py"]),
    ("§9④ gộp gate duyệt", ["duyệt plan"]),
    ("§9⑤ doc tiếng Việt, report ngắn gọn 10-20 dòng", ["tiếng việt", "10-20 dòng"]),
]


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class CoreFileTest(unittest.TestCase):
    def test_ban_mau_ton_tai_trong_repo(self):
        self.assertTrue(os.path.exists(CORE), f"thiếu nguồn sự thật {CORE}")

    def test_c_kich_thuoc_khong_qua_tran(self):
        size = os.path.getsize(CORE)
        self.assertLessEqual(size, MAX_BYTES, f"bản mẫu {size} byte > {MAX_BYTES}")


class MovedRulesTest(unittest.TestCase):
    """(a) Luật đã chuyển phải nằm ở file đích, nếu không là mất luật."""

    def test_moi_luat_chuyen_deu_co_o_file_dich(self):
        for label, rel, needles in MOVED:
            path = os.path.join(REPO, rel)
            with self.subTest(luat=label):
                self.assertTrue(os.path.exists(path), f"{label}: thiếu file đích {rel}")
                text = _read(path).lower()
                for needle in needles:
                    self.assertIn(needle, text, f"{label}: {rel} thiếu \"{needle}\"")


class InvariantRulesTest(unittest.TestCase):
    """(b) Luật bất biến phải còn nguyên trong bản mẫu."""

    def test_luat_bat_bien_con_trong_ban_loi(self):
        text = _read(CORE).lower()
        for label, needles in INVARIANTS:
            with self.subTest(luat=label):
                for needle in needles:
                    self.assertIn(needle, text, f"{label}: bản mẫu thiếu \"{needle}\"")


if __name__ == "__main__":
    unittest.main()
