"""T4.1 (2026-09-17) — skill `tdq-lean`: một skill, ba chế độ soi over-engineer.

Ba chế độ vay từ ba command của Ponytail (`review` soi diff, `audit` soi cả repo, `debt`
gom marker `ponytail:` thành sổ nợ). KHÔNG vay `/ponytail-gain` — phán quyết của user.
Test khoá ba chuyện: đủ ba mục chế độ, `argument-hint` khai đúng ba chế độ, và chế độ
`debt` phải gọi tên marker thiếu đường nâng là nợ thối.
"""
import os
import re
import subprocess
import sys
import unittest

from helper import ROOT

SKILL = os.path.join(ROOT, "skills", "tdq-lean", "SKILL.md")


def doc():
    with open(SKILL, encoding="utf-8") as f:
        return f.read()


class TestHinhDangSkillLean(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.isfile(SKILL), f"thiếu {SKILL}")
        self.text = doc()

    def test_frontmatter_khai_ten_va_argument_hint(self):
        head = self.text.split("---", 2)[1]
        self.assertIn("name: tdq-lean", head)
        self.assertIn("description:", head)
        hint = re.search(r'^argument-hint:\s*"?\[?([^"\]\n]+)', head, re.MULTILINE)
        self.assertIsNotNone(hint, "thiếu dòng argument-hint")
        for che_do in ("review", "audit", "debt"):
            self.assertIn(che_do, hint.group(1), hint.group(1))

    def test_du_ba_muc_che_do(self):
        for che_do in ("review", "audit", "debt"):
            with self.subTest(che_do=che_do):
                self.assertRegex(self.text, rf"(?m)^##+ .*`{che_do}`")

    def test_review_soi_diff_audit_soi_ca_repo(self):
        """Hai chế độ phải khác nhau ở PHẠM VI, nếu không thì gộp một là đủ."""
        review = self.text.split("`review`", 1)[1].split("`audit`", 1)[0]
        self.assertIn("diff", review.lower())
        audit = self.text.split("`audit`", 1)[1].split("`debt`", 1)[0]
        self.assertTrue(any(w in audit.lower() for w in ("whole tree", "whole repo",
                                                         "entire repo")), audit[:200])

    def test_debt_goi_ten_no_thoi(self):
        debt = self.text.split("`debt`", 1)[1]
        self.assertIn("ponytail:", debt)
        self.assertTrue(any(w in debt.lower() for w in ("no-trigger", "rotten", "rots")),
                        debt[:300])
        self.assertIn("kiem_no_marker.py", debt, "chế độ debt phải chạy lệnh sổ nợ đã có")

    def test_nam_tag_cua_ponytail_con_du(self):
        """Năm tag là bộ từ vựng chung với Ponytail — thiếu một tag là mất một lối soi."""
        for tag in ("delete", "stdlib", "native", "yagni", "shrink"):
            with self.subTest(tag=tag):
                self.assertIn(tag, self.text)

    def test_khong_vay_gain(self):
        self.assertNotIn("ponytail-gain", self.text)
        self.assertNotIn("/gain", self.text)

    def test_router_tro_dung_duong_dan_skill(self):
        """T6.3 (2026-09-17) — tầng "đọc SKILL.md trực tiếp" phải tìm ra file này.

        Đây là phép kiểm CHẠY ĐƯỢC của T6.3, thay cho phép kiểm cũ (grep `tdq-lean` trong
        `docs/tdq/audit/skill-index.json`): chỉ mục dựng từ skill của plugin ĐÃ CÀI, không
        từ `skills/` của repo, nên nó chỉ nhận skill mới sau lần cài kế tiếp. Bản đồ
        SKILL.md thì đọc thẳng repo, nên khoá được ngay hôm nay.
        """
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import skill_tokens
        ban_do = skill_tokens.ban_do_skill_md()
        duong = ban_do.get(skill_tokens.khoa_tra("tdq-lean")) or []
        self.assertIn(SKILL, duong, f"router không trỏ được tới tdq-lean: {duong}")

    def test_i18n_check_xanh(self):
        rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "i18n_check.py"),
                             SKILL], capture_output=True, encoding="utf-8", text=True)
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)

    def test_doc_lint_xanh(self):
        rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "doc_lint.py"),
                             SKILL], capture_output=True, encoding="utf-8", text=True)
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)


if __name__ == "__main__":
    unittest.main()
