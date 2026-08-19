"""Ranh giới hai loại nội dung trong bộ luật: luật-lý-luận vs khuôn-user-facing.

Điều kiện tiền đề (a) của hướng A. Viết luật bằng tiếng Anh chỉ an toàn khi biết CHÍNH
XÁC dòng nào được phép đổi ngôn ngữ và dòng nào không. Máy gợi ý nhãn theo dấu hiệu,
người soát từng dòng — test này khoá cả hai: bộ gợi ý phải đúng ở các ca rõ ràng, và
bảng người chốt phải phủ đủ mọi mã, mỗi mã đúng một nhãn.
"""
import os
import re
import subprocess
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import luat_phan_loai  # noqa: E402

BANG = os.path.join(ROOT, "docs", "tdq", "audit", "luat-hien-co.md")
RANH_GIOI = os.path.join(ROOT, "docs", "tdq", "audit", "ranh-gioi-luat.md")
SCRIPT = os.path.join(ROOT, "scripts", "luat_phan_loai.py")


class GoiYTest(unittest.TestCase):
    """Bộ gợi ý nhãn — chỉ đòi đúng ở các ca rõ ràng, phần mờ để người soát."""

    def nhan(self, duong_dan, chu, trong_khoi_ma=False):
        return luat_phan_loai.goi_y_nhan(duong_dan, chu, trong_khoi_ma).nhan

    def test_cau_in_ra_chat_la_user_facing(self):
        self.assertEqual(
            self.nhan("skills/tdq-intake/SKILL.md",
                      'In đúng dòng: `➤ Duyệt: nhắn "duyệt nhanh"` rồi DỪNG.'),
            "user-facing")

    def test_file_khuon_la_user_facing(self):
        self.assertEqual(
            self.nhan("skills/tdq-spec/references/spec-template.md",
                      "Mục câu hỏi còn mở PHẢI rỗng."),
            "user-facing")

    def test_dong_trong_khoi_ma_la_user_facing(self):
        """Khối mã trong skill là khuôn copy được — đổi chữ trong đó là đổi đầu ra."""
        self.assertEqual(
            self.nhan("skills/tdq-build/SKILL.md", "Trạng thái: CHỜ DUYỆT",
                      trong_khoi_ma=True),
            "user-facing")

    def test_luat_thuan_la_ly_luan(self):
        self.assertEqual(
            self.nhan("skills/tdq-build/SKILL.md",
                      "Red → green. Mỗi task: chạy check trước, phải fail, rồi code."),
            "ly-luan")

    def test_moi_dong_chi_mot_nhan(self):
        for ma, duong_dan, _, chu in luat_phan_loai.doc_bang(BANG):
            nhan = luat_phan_loai.goi_y_nhan(duong_dan, chu).nhan
            self.assertIn(nhan, ("ly-luan", "user-facing"), f"{ma}: nhãn lạ {nhan}")

    def test_moi_goi_y_co_ly_do(self):
        for ma, duong_dan, _, chu in luat_phan_loai.doc_bang(BANG)[:50]:
            self.assertTrue(luat_phan_loai.goi_y_nhan(duong_dan, chu).ly_do,
                            f"{ma}: gợi ý không kèm lý do")


class CliTest(unittest.TestCase):
    def chay(self, *args, env=None):
        moi = dict(os.environ)
        moi.update(env or {})
        return subprocess.run([sys.executable, SCRIPT, *args],
                              capture_output=True, text=True, env=moi)

    def test_in_bang_nhap_du_dong(self):
        proc = self.chay("--bang", BANG)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len([d for d in proc.stdout.splitlines()
                              if re.match(r"^\| L\d+ \|", d)]), 329)

    def test_log_bat_mac_dinh_co_timestamp(self):
        proc = self.chay("--bang", BANG)
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]")

    def test_tat_log_bang_bien_moi_truong(self):
        proc = self.chay("--bang", BANG, env={"TDQ_LOG": "0"})
        self.assertEqual(proc.stderr.strip(), "")


class BangDaChotTest(unittest.TestCase):
    """Bảng người soát chốt — lưới thật, máy chỉ gợi ý còn đây là lời khai cuối cùng."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(RANH_GIOI):
            raise unittest.SkipTest("chưa có bảng ranh giới")
        cls.bang = luat_phan_loai.doc_ranh_gioi(RANH_GIOI)

    def test_phu_du_moi_ma(self):
        goc = {ma for ma, _, _, _ in luat_phan_loai.doc_bang(BANG)}
        self.assertEqual(set(self.bang), goc, "bảng ranh giới lệch mã so với bảng điểm neo")

    def test_khong_ma_nao_khai_hai_lan(self):
        """Dict nuốt dòng trùng: L010 khai hai lần thì lời khai sau đè lời khai trước mà
        không ai biết. Phải đếm trên danh sách thô, không đếm trên dict."""
        thu = luat_phan_loai.liet_ke_ma(RANH_GIOI)
        trung = sorted({ma for ma in thu if thu.count(ma) > 1})
        self.assertEqual(trung, [], f"mã khai nhiều lần: {trung}")
        self.assertEqual(len(thu), len(self.bang))

    def test_du_329_ma(self):
        self.assertEqual(len(self.bang), 329)

    def test_moi_dong_co_ly_do(self):
        for ma, dong in self.bang.items():
            self.assertTrue(dong.chu.strip(), f"{ma}: thiếu lý do")

    def test_ma_user_facing_co_ly_do_rieng(self):
        """Nhãn user-facing là nhãn CHẶN dịch — nó phải kèm lý do cụ thể, không được
        mang câu mặc định của bộ gợi ý máy."""
        chung = "không thấy dấu hiệu user-facing trong câu"
        for ma, dong in self.bang.items():
            if dong.nhan == "user-facing":
                self.assertNotEqual(dong.chu.strip(), chung, f"{ma}: lý do mặc định")

    def test_moi_ma_dung_mot_nhan(self):
        for ma, dong in self.bang.items():
            self.assertIn(dong.nhan, ("ly-luan", "user-facing"), f"{ma}: nhãn lạ")


if __name__ == "__main__":
    unittest.main()
