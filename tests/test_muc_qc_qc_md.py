"""Bảng mức QC và luật trần thời gian — `skills/tdq-build/references/qc.md`.

Vì sao kiểm bằng máy: mức QC chỉ có nghĩa khi CÓ MỘT bảng nói rõ mức nào chạy gì. Một bảng
thiếu ô, hay một mức mô tả bằng chữ "kỹ hơn", là thứ mỗi lượt agent đọc ra một kiểu — đúng thứ
mà việc thêm khoá `muc_qc` định chấm dứt.

Trần 120 giây có lý do đo được: user đã gặp runtime test treo rất lâu. Nên luật chạm trần phải
nằm trong file, không nằm trong trí nhớ, và phải cấm agent tự nâng trần.

Hai nhóm chạy riêng được bằng `-k`: `bang`, `tran`.
"""
import os
import re
import unittest

from helper import ROOT

QC_MD = os.path.join(ROOT, "skills", "tdq-build", "references", "qc.md")
BUILD_SKILL = os.path.join(ROOT, "skills", "tdq-build", "SKILL.md")
MUC = ("lite", "full", "ultra")
LOAI_KIEM = ("DoD", "unit test", "smoke test", "runtime test")


def doc(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def bang_muc(van_ban):
    """Các dòng bảng mô tả mức — dòng bắt đầu bằng `| ` và có tên một mức trong ô đầu."""
    ra = {}
    for dong in van_ban.splitlines():
        if not dong.startswith("|"):
            continue
        o = [c.strip().strip("`") for c in dong.strip("|").split("|")]
        if o and o[0] in MUC:
            ra[o[0]] = o
    return ra


class BangMucTest(unittest.TestCase):
    def setUp(self):
        self.qc = doc(QC_MD)
        self.bang = bang_muc(self.qc)

    def test_bang_du_ba_muc(self):
        self.assertEqual(set(self.bang), set(MUC), f"bảng mức thiếu/thừa dòng: {list(self.bang)}")

    def test_bang_du_bon_loai_kiem_o_tieu_de(self):
        for loai in LOAI_KIEM:
            with self.subTest(loai=loai):
                self.assertIn(loai, self.qc, f"bảng không nêu loại kiểm `{loai}`")

    def test_bang_moi_o_la_co_hoac_khong(self):
        """Ô mô tả bằng chữ mơ hồ ("tuỳ", "nếu cần") là ô sẽ bị đọc mỗi lượt một kiểu."""
        hop_le = {"CÓ", "KHÔNG", "CÓ (vùng chạm)", "CÓ (trọn suite)"}
        for muc, o in self.bang.items():
            for gia_tri in o[1:6]:
                with self.subTest(muc=muc, o=gia_tri):
                    self.assertIn(gia_tri, hop_le, f"ô của mức {muc} không phải CÓ/KHÔNG")

    def test_bang_muc_mac_dinh_khong_co_runtime(self):
        """Quyết định của user 2026-09-23: mặc định KHÔNG chạy runtime test, vì đã từng treo."""
        tieu_de = [c.strip() for c in
                   re.search(r"\|\s*Mức\s*\|(.+)\|", self.qc).group(0).strip("|").split("|")]
        cot = tieu_de.index("runtime test")
        self.assertEqual(self.bang["full"][cot], "KHÔNG",
                         "mức mặc định `full` không được chạy runtime test")
        self.assertEqual(self.bang["ultra"][cot], "CÓ", "mức `ultra` phải chạy runtime test")

    def test_bang_chi_ultra_goi_agent_doc_lap(self):
        """Đọc thẳng cột cuối của bảng: chỉ `ultra` mới gọi agent QC độc lập."""
        self.assertIn("tdq-qc-tester", self.qc, "bảng phải nói mức nào gọi agent QC độc lập")
        self.assertEqual(self.bang["ultra"][-1], "CÓ")
        for muc in ("lite", "full"):
            with self.subTest(muc=muc):
                self.assertEqual(self.bang[muc][-1], "KHÔNG")

    def test_bang_agent_doc_lap_khong_con_nguong_mo_ho(self):
        """Trước 2026-09-23 việc gọi agent QC treo vào câu "việc lớn hoặc rủi ro cao" — không
        ngưỡng nào, nên thực tế là không bao giờ gọi. Giờ nó thuộc về mức."""
        self.assertNotIn("Large or high-risk work → also call", self.qc,
                         "ngưỡng cũ không được còn là LUẬT (nhắc lại như lịch sử thì được)")
        self.assertRegex(self.qc, r"`tdq-qc-tester` agent runs at `ultra`",
                         "phải nói thẳng agent chạy ở mức nào")

    def test_bang_doc_muc_tu_state(self):
        self.assertIn("muc_qc", self.qc, "qc.md phải đọc mức từ state, không cố định một bộ")
        self.assertIn("get muc_qc", self.qc, "phải nêu lệnh đọc mức")


class TranThoiGianTest(unittest.TestCase):
    def setUp(self):
        self.qc = doc(QC_MD)
        self.skill = doc(BUILD_SKILL)

    def test_tran_co_so_120_giay(self):
        self.assertRegex(self.qc, r"120[ -]?(giây|second|s\b)",
                         "phải ghi rõ trần 120 giây, không nói 'đừng chạy lâu'")

    def test_tran_noi_ro_hanh_vi_khi_cham(self):
        # Cắt theo TIÊU ĐỀ mục, không cắt theo chữ "120": chữ đó xuất hiện nhiều lần nên
        # split() trả về đúng mẩu nằm giữa hai lần xuất hiện.
        khoi = self.qc.split("## The 120-second cap", 1)[1].split("\n## ", 1)[0]
        self.assertRegex(khoi, r"(?i)(kill|giết|dừng|terminate)",
                         "chạm trần phải giết tiến trình")
        self.assertIn("FAIL", khoi, "chạm trần phải ghi FAIL, không im lặng bỏ qua")

    def test_tran_cam_tu_nang(self):
        """Luật của user: phân tích trước, và HỎI trước khi nâng trần."""
        self.assertRegex(self.qc, r"(?i)(never raise|không được tự nâng|cấm tự nâng)",
                         "phải cấm agent tự nâng trần")
        self.assertRegex(self.qc, r"(?i)(ask the user|hỏi user|hỏi người dùng)",
                         "nâng trần phải hỏi user trước")

    def test_tran_duoc_nhac_trong_than_skill(self):
        self.assertIn("120", self.skill, "thân skill tdq-build phải nhắc trần thời gian")


if __name__ == "__main__":
    unittest.main()
