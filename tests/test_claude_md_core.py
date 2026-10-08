"""Chống bỏ sót khi rút gọn ~/.claude/CLAUDE.md (spec 2026-08-05 §2).

3 điều kiện, đo trên BẢN MẪU trong repo `docs/claude-md-mau.md`:
  (a) mọi luật bị CHUYỂN phải tìm được ở đúng file đích;
  (b) luật bất biến (git, trình bày, logging, 5 luật kích hoạt TDQ) vẫn còn trong bản mẫu;
  (c) bản mẫu ≤ 3.500 byte.

Không so với `~/.claude/CLAUDE.md`: suite phải chạy được ở máy chưa cài,
và file ngoài repo không phải thứ test của repo được phép đòi hỏi.
"""

import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO, "docs", "claude-md-mau.md")
sys.path.insert(0, os.path.join(REPO, "scripts"))
import tdq_setup  # noqa: E402 — chủ của khối ghim, để test và sản phẩm dùng chung một dấu mốc
# 2026-09-20: 3500 → 3800. The template stood at 3533 bytes, and every section of it is a
# tier-1 or tier-2 law (approval, git, secrets, the TDQ gates); §7 already forbids copying
# details in, so there is nothing redundant left to squeeze. `soul.md` settles which side
# gives: a size cap is a tier-3 constraint, so hitting it means RAISING THE CAP, never
# compressing a law to fit. Same ruling the repo already applied to `chung.md` (150 → 240
# lines). The cap still exists because this file is loaded every session.
# 2026-09-28: 3800 → 4300. Khối `TDQ:TOOLS` ghim luật 4 tầng vào instruction user-level, thứ một
# agent phải biết TRƯỚC khi nạp bất kỳ skill nào — chưa biết thì nó grep mọi thứ. Cùng phán quyết
# của soul.md như lần trước: trần kích thước là ràng buộc tầng 3, nên chạm trần là NÂNG TRẦN chứ
# không nén luật. Khối đo được 466 byte, trần chừa phần cho một lần sửa chữ sau này.
MAX_BYTES = 4300

# (mô tả, đường dẫn file đích tương đối repo, các chuỗi phải có mặt)
# Đích có thể là MỘT file hay MỘT CẶP file: 2026-10-02 vài file luật bị tách làm file anh + file
# em để xuống dưới trần token, và luật không rời skill — nó sang file em, vẫn được trỏ tới từ cùng
# `SKILL.md`. Đòi needle nằm đúng file anh là đòi một chi tiết sắp xếp, không phải đòi luật còn.
MOVED = [
    ("§3 failover Tavily", "skills/tdq-conventions/references/tavily.md",
     ["tavily-primary", "tavily-backup", "websearch"]),
    ("§6 quy ước working log", "skills/tdq-conventions/SKILL.md",
     ["docs/workinglog", "working log"]),
    ("§7 xử lý issue user báo", "skills/tdq-intake/references/issue-triage.md",
     ["log", "computer use", "spec"]),
    ("§8 checklist lập spec", ("skills/tdq-spec/references/spec-template.md",
                               "skills/tdq-spec/references/spec-template-huong-dan.md"),
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
        # Measured as git stores it (LF): a Windows checkout with core.autocrlf adds one byte per
        # line, and read 4314 bytes for a 4250-byte template (2026-10-08).
        with open(CORE, "rb") as fh:
            size = len(fh.read().replace(b"\r\n", b"\n"))
        self.assertLessEqual(size, MAX_BYTES, f"bản mẫu {size} byte > {MAX_BYTES}")


class MovedRulesTest(unittest.TestCase):
    """(a) Luật đã chuyển phải nằm ở file đích, nếu không là mất luật."""

    def test_moi_luat_chuyen_deu_co_o_file_dich(self):
        for label, dich, needles in MOVED:
            rels = (dich,) if isinstance(dich, str) else dich
            with self.subTest(luat=label):
                van = []
                for rel in rels:
                    path = os.path.join(REPO, rel)
                    self.assertTrue(os.path.exists(path), f"{label}: thiếu file đích {rel}")
                    van.append(_read(path).lower())
                text = chr(10).join(van)
                for needle in needles:
                    self.assertIn(needle, text,
                                  f"{label}: {' + '.join(rels)} thiếu \"{needle}\"")


class InvariantRulesTest(unittest.TestCase):
    """(b) Luật bất biến phải còn nguyên trong bản mẫu."""

    def test_luat_bat_bien_con_trong_ban_loi(self):
        text = _read(CORE).lower()
        for label, needles in INVARIANTS:
            with self.subTest(luat=label):
                for needle in needles:
                    self.assertIn(needle, text, f"{label}: bản mẫu thiếu \"{needle}\"")




class KhoiHuongDanToolTest(unittest.TestCase):
    """(d) Bản ngắn của luật 3 tầng phải được GHIM vào instruction user-level.

    Vì sao phải ghim: luật đầy đủ nằm trong `skills/`, thứ chỉ được nạp khi router gọi đúng skill.
    Một agent chưa nạp skill nào vẫn phải biết dùng công cụ nào khi nào, nếu không nó mặc định
    grep mọi thứ. Khối có dấu mốc để `scripts/tdq_setup.py` ghi lại được mà không đụng phần user
    tự viết — Claude Code không có cách tắt/ghi đè từng phần nào khác.
    """

    def test_khoi_co_dau_moc_dong_mo_va_dong_dong(self):
        text = _read(CORE)
        self.assertIn(tdq_setup.MOC_MO, text)
        self.assertIn(tdq_setup.MOC_DONG, text)
        self.assertEqual(text.count(tdq_setup.MOC_MO), 1, "khối bị nhân bản")

    def test_khoi_ke_du_ba_tang(self):
        text = _read(CORE)
        khoi = text.split(tdq_setup.MOC_MO)[1].split(tdq_setup.MOC_DONG)[0]
        for ten in ("lsp", "grep", "graphify"):
            self.assertIn(ten, khoi.lower(), f"khối ghim thiếu tầng {ten}")
        self.assertNotIn("lumen", khoi.lower(), "0.58.0: khối ghim không được dẫn tới lumen")

    def test_khoi_ghi_hai_lan_khong_nhan_ban(self):
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "CLAUDE.md")
            with open(dich, "w", encoding="utf-8") as fh:
                fh.write("# Luật của tôi\n\n- một dòng của user\n")
            tdq_setup.ghim_huong_dan_tool(dich)
            tdq_setup.ghim_huong_dan_tool(dich)
            noi_dung = _read(dich)
        self.assertEqual(noi_dung.count(tdq_setup.MOC_MO), 1)
        self.assertIn("một dòng của user", noi_dung, "không được đụng phần user tự viết")

    def test_khoi_cap_nhat_lai_dung_cho_cu(self):
        """Ghi lần hai với nội dung mới phải THAY khối cũ, không nối thêm khối thứ hai."""
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "CLAUDE.md")
            with open(dich, "w", encoding="utf-8") as fh:
                fh.write(f"# Đầu\n\n{tdq_setup.MOC_MO}\nnội dung cũ\n{tdq_setup.MOC_DONG}\n\n# Cuối\n")
            tdq_setup.ghim_huong_dan_tool(dich)
            noi_dung = _read(dich)
        self.assertNotIn("nội dung cũ", noi_dung)
        self.assertIn("# Cuối", noi_dung, "phần sau khối phải còn nguyên")

    def test_khoi_trong_ban_mau_khop_nguyen_van_voi_hang_so(self):
        """Bản mẫu và hằng số trong code là MỘT, không phải hai bản chép tay.

        Chúng đã lệch một lần trong chính request sinh ra khối này: hằng số được sửa sang đường
        dẫn khác sau khi bản mẫu đã ghi, và không phép kiểm nào thấy. Bản được GHI RA MÁY USER
        lại là bản không ai soi, nên chỗ này phải có một ca so nguyên văn.
        """
        text = _read(CORE)
        trong_mau = text.split(tdq_setup.MOC_MO)[1].split(tdq_setup.MOC_DONG)[0].strip()
        self.assertEqual(trong_mau, tdq_setup.khoi_huong_dan(tdq_setup.GOC_MAU).strip())

    def test_khoi_trong_ban_mau_khong_mang_duong_dan_cua_mot_may_cu_the(self):
        """Bản mẫu là tài liệu chung — đường dẫn tuyệt đối của máy người dựng không được lọt vào."""
        text = _read(CORE)
        trong_mau = text.split(tdq_setup.MOC_MO)[1].split(tdq_setup.MOC_DONG)[0]
        for dau_hieu in ("C:/Users/", "C:" + os.sep + "Users", "/home/", "/Users/"):
            self.assertNotIn(dau_hieu, trong_mau, f"bản mẫu lọt đường dẫn máy: {dau_hieu}")

    def test_byte_tran_da_duoc_nang_kem_ly_do(self):
        """soul.md: trần kích thước là ràng buộc tầng 3 — chạm trần thì NÂNG TRẦN, không nén luật."""
        nguon = _read(os.path.join(REPO, "tests", "test_claude_md_core.py"))
        self.assertGreater(MAX_BYTES, 3800, "thêm luật mà không nâng trần là sẽ phải nén luật")
        self.assertIn("2026-09-28", nguon, "mỗi lần nâng trần phải ghi lý do kèm ngày")


if __name__ == "__main__":
    unittest.main()
