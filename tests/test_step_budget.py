"""Khoá luật một lượt (tầng runtime) và bộ đo chi phí bước.

Request 2026-08-15-0900-toi-uu-thoi-gian-phase. Hai nhóm test:
  - nhóm LUẬT: luật gộp phải nằm ở thân skill, luật đọc lại phải MỀM, luật cũ còn nguyên.
  - nhóm ĐO: `step_audit.py` ra đúng số liệu tính tay trên transcript mẫu.
"""

import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

import step_audit  # noqa: E402
import token_audit  # noqa: E402

SKILL = os.path.join(ROOT, "skills", "tdq-conventions", "SKILL.md")
BUDGET = os.path.join(ROOT, "skills", "tdq-conventions", "references", "context-budget.md")
SOUL = os.path.join(ROOT, "skills", "tdq-conventions", "references", "soul.md")
SAMPLE = os.path.join(SCRIPTS, "samples", "transcript-step-audit.jsonl")

# Độ dài mục "## 10." của SKILL.md trước request này (đo bằng `git show HEAD`
# ngày 2026-08-15). Trần thêm chữ do spec chốt là 900 ký tự.
SECTION_10_BEFORE = 242
SECTION_10_BUDGET = 900

# Sáu gạch đầu dòng luật đã có trong context-budget.md trước request này. Plan cấm
# xoá hoặc rút gọn bất kỳ dòng nào — chỉ được đổi chỗ và đổi nhãn tầng. Từ 2026-08-19
# (hướng A hybrid) file viết tiếng Anh: vẫn đủ sáu dòng, chỉ đổi ngôn ngữ của nhãn.
OLD_BULLETS = [
    "- **Batch tool calls.**",
    "- **Lint the exact file.**",
    "- **Quiet CLI.**",
    "- **Read just enough.**",
    "- **Give heavy work to a subagent.**",
    "- **Soul decides.**",
]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def section(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j]


class LuatMotLuot(unittest.TestCase):
    """Luật gộp phải ở THÂN skill (nạp mỗi turn), không nằm trong file reference."""

    def test_luat_o_than_skill(self):
        # Thân skill viết tiếng Anh từ 2026-08-19 (hướng A hybrid); luật vẫn phải nằm
        # đúng §10 với đủ ba mục, chỉ đổi ngôn ngữ của nhãn.
        body = read(SKILL)
        self.assertIn("## 10. One-batch rule", body)
        block = section(body, "## 10.", "## 11.")
        self.assertIn("runtime", block)
        for muc in ("When it applies", "What to do", "Self-check"):
            self.assertIn(muc, block, f"thiếu mục {muc} trong §10")

    def test_tran_ky_tu(self):
        block = section(read(SKILL), "## 10.", "## 11.")
        them = len(block) - SECTION_10_BEFORE
        self.assertLessEqual(them, SECTION_10_BUDGET,
                             f"§10 thêm {them} ký tự > trần {SECTION_10_BUDGET}")

    def test_cam_gop_du_bon_ca(self):
        budget = read(BUDGET)
        self.assertIn("### Never batch these", budget)
        table = section(budget, "### Never batch these", "## Context cost")
        rows = [r for r in table.splitlines()
                if r.startswith("|") and "---" not in r and "Why batching" not in r]
        self.assertEqual(len(rows), 4, "bảng cấm gộp phải có đúng 4 ca")
        for dau_hieu in ("red", "Isolating", "Destructive", "previous command's result"):
            self.assertIn(dau_hieu, table)

    def test_doc_lai_mem(self):
        """Luật đọc lại là luật MỀM: user chốt không đổi chất lượng lấy tốc độ."""
        budget = read(BUDGET)
        self.assertNotIn("cấm đọc lại", budget.lower())
        self.assertNotIn("never re-read", budget.lower())
        self.assertIn("when in doubt, re-read", budget.lower())
        cases = section(budget, "### Five cases where re-reading is MANDATORY",
                        "### Re-reading by RULE")
        numbered = [l for l in cases.splitlines() if re.match(r"^\d+\.", l)]
        self.assertEqual(len(numbered), 5, "phải liệt kê đủ 5 ca bắt buộc đọc lại")

    def test_luat_cu_con_nguyen(self):
        budget = read(BUDGET)
        for bullet in OLD_BULLETS:
            self.assertIn(bullet, budget, f"mất luật cũ: {bullet}")

    def test_ba_tang_soul_khong_doi(self):
        soul = read(SOUL)
        # Từ 2026-08-22 soul.md viết tiếng Anh; nhận cả hai cách viết để bản cũ vẫn xanh.
        for tang in (("**Tier 1 — quality**", "**Tầng 1 — chất lượng**"),
                     ("**Tier 2 — runtime**", "**Tầng 2 — runtime**"),
                     ("**Tier 3 — context cost**", "**Tầng 3 — context cost**")):
            self.assertTrue(any(t in soul for t in tang), f"mất tầng: {tang[0]}")
        self.assertTrue("## Which tier a law belongs to" in soul
                        or "## Xếp luật vào tầng nào" in soul)


class StepAudit(unittest.TestCase):
    """Số liệu kỳ vọng tính tay trên `scripts/samples/transcript-step-audit.jsonl`.

    Mẫu có 4 `requestId` (A, B, C, D) trải trên 6 bản ghi assistant — đúng kiểu Claude
    Code tách một câu trả lời thành nhiều dòng. Kỳ vọng: 4 bước · 5 tool call trên 4
    lượt có tool → 1,25 · Read `/repo/a.py` hai lần → 1 lần lặp · độ trễ [2, 3, 4, 10]
    → trung vị 3,5 s, p90 (nearest-rank, ceil(0,9×4)=4) 10,0 s.
    """

    def setUp(self):
        self.stats = step_audit.scan(SAMPLE)

    def test_step_audit(self):
        self.assertEqual(self.stats["steps"], 4)
        self.assertEqual(self.stats["tool_calls"], 5)
        self.assertEqual(self.stats["turns_with_tools"], 4)
        self.assertEqual(self.stats["repeat_reads"], 1)
        self.assertEqual(sorted(self.stats["latencies"]), [2.0, 3.0, 4.0, 10.0])
        self.assertEqual(step_audit.median(self.stats["latencies"]), 3.5)
        self.assertEqual(step_audit.percentile(self.stats["latencies"], 0.9), 10.0)

    def test_bang_ket_qua(self):
        out = step_audit.report(self.stats)
        self.assertIn("| Tool calls per turn | 1.25 (4 turn(s)) |", out)
        self.assertIn("| Repeat Read of one file | 1 |", out)

    def test_help_du_ba_co(self):
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "step_audit.py"),
                               "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        for co in ("--transcript-dir", "--project", "--sessions"):
            self.assertIn(co, proc.stdout)

    def test_log_service_bat_mac_dinh_tat_duoc(self):
        env = dict(os.environ)
        env.pop("TDQ_LOG", None)
        cmd = [sys.executable, os.path.join(SCRIPTS, "step_audit.py"),
               "--transcript-dir", os.path.join(SCRIPTS, "samples")]
        on = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertGreaterEqual(len([l for l in on.stderr.splitlines() if l.strip()]), 2)
        env["TDQ_LOG"] = "0"
        off = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertEqual(off.stderr.strip(), "")
        self.assertEqual(off.returncode, 0)


class TokenAuditPath(unittest.TestCase):
    def test_token_audit_underscore(self):
        """Project có gạch dưới cũng phải ra đúng thư mục transcript của Claude Code."""
        got = token_audit.default_transcript_dir("/Users/ai/Documents/Heineken_AppKetNoi")
        self.assertTrue(got.endswith("Users-ai-Documents-Heineken-AppKetNoi"), got)
        self.assertNotIn("_", os.path.basename(got))


if __name__ == "__main__":
    unittest.main()
