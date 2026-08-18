"""Khoá từng luật trong `docs/tdq/audit/luat-hien-co.md` vào file skill nguồn.

Đây là lưới an toàn cho MỌI việc tối ưu bộ workflow về sau — rút gọn, gộp file, hay
dịch sang tiếng Anh. Luật của lưới: sửa skill làm mất một điểm neo thì test này phải
đỏ và phải NÊU ĐÚNG mã `L###` mất, chứ không đỏ chung chung "có gì đó đổi".

Vì sao khoá bằng NỘI DUNG chứ không bằng số dòng: chỉ cần chèn một dòng vào đầu file
là mọi số dòng phía dưới lệch hết, test sẽ đỏ hàng loạt trong khi không luật nào mất.
Đỏ sai chỗ nhiều lần thì người ta tắt test — mất luôn lưới. Nên số dòng ở
`luat-hien-co.md` chỉ để CON NGƯỜI mở đúng chỗ; máy đối chiếu bằng chữ.
"""
import os
import re
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANG = os.path.join(ROOT, "docs", "tdq", "audit", "luat-hien-co.md")
DONG_RE = re.compile(r"^\| (L\d+) \| `([^`:]+):(\d+)` \| (.*?) \|$")

# Đối chiếu trên bao nhiêu ký tự đầu của luật. Đủ dài để không trùng nhau lung tung,
# đủ ngắn để sửa dấu câu cuối câu không làm đỏ oan.
DAI_NEO = 40


def doc_bang(path=BANG):
    """Bảng luật → [(mã, file, dòng, chữ neo)]. Chữ neo đã gỡ escape của markdown."""
    ban = []
    with open(path, encoding="utf-8") as f:
        for dong in f:
            m = DONG_RE.match(dong.rstrip("\n"))
            if not m:
                continue
            chu = m.group(4).replace("\\|", "|").rstrip("…")
            ban.append((m.group(1), m.group(2), int(m.group(3)), chu))
    return ban


def chuan(chu):
    """Gộp mọi khoảng trắng — xuống dòng hay thụt lề đổi thì luật vẫn là luật đó."""
    return re.sub(r"\s+", " ", chu).strip()


def neo(chu):
    return chuan(chu)[:DAI_NEO]


def luat_con_khong(chu_neo, noi_dung):
    return chu_neo in chuan(noi_dung)


class BangLuatTest(unittest.TestCase):
    """Bảng phải đọc được và đủ dày, nếu không thì lưới rách ngay từ nguồn."""

    def test_bang_ton_tai_va_doc_ra_hang(self):
        self.assertTrue(os.path.exists(BANG), f"thiếu {BANG}")
        self.assertGreater(len(doc_bang()), 100)

    def test_ma_khong_trung_nhau(self):
        ma = [b[0] for b in doc_bang()]
        self.assertEqual(len(ma), len(set(ma)), "mã L### bị trùng — tra ra nhầm luật")

    def test_moi_file_nguon_deu_ton_tai(self):
        for ma, p, _dong, _chu in doc_bang():
            with self.subTest(ma=ma):
                self.assertTrue(os.path.exists(os.path.join(ROOT, p)), p)


class KhoaLuatTest(unittest.TestCase):
    """Phần chính: mọi điểm neo phải còn nguyên trong file skill thật."""

    @classmethod
    def setUpClass(cls):
        cls.bang = doc_bang()
        cls.noi_dung = {}
        for _ma, p, _d, _c in cls.bang:
            if p not in cls.noi_dung:
                with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                    cls.noi_dung[p] = f.read()

    def test_moi_luat_con_nguyen_trong_skill(self):
        mat = []
        for ma, p, dong, chu in self.bang:
            if not luat_con_khong(neo(chu), self.noi_dung[p]):
                mat.append(f"{ma} ({p}:{dong}): {chu[:60]}")
        self.assertEqual(mat, [], f"{len(mat)} luật biến mất khỏi skill:\n" +
                         "\n".join(mat))

    def test_so_dong_ghi_trong_bang_van_tro_dung_cho(self):
        """Mềm hơn test trên: số dòng lệch thì CẢNH BÁO qua tên test, không phải mất
        luật. Vẫn kiểm, vì lệch nhiều nghĩa là bảng cũ so với skill."""
        lech = 0
        for _ma, p, dong, chu in self.bang:
            dòng_thật = self.noi_dung[p].splitlines()
            if dong - 1 >= len(dòng_thật) or not luat_con_khong(
                    neo(chu), dòng_thật[dong - 1]):
                lech += 1
        ti_le = lech / len(self.bang) * 100
        self.assertLess(ti_le, 5.0,
                        f"{lech}/{len(self.bang)} dòng lệch ({ti_le:.1f}%) — "
                        "dựng lại luat-hien-co.md")


class LuoiBatDuocMatLuatTest(unittest.TestCase):
    """Test của chính cái lưới: xoá một luật khỏi BẢN SAO → lưới phải bắt được.

    Không có lớp này thì `test_moi_luat_con_nguyen_trong_skill` xanh vĩnh viễn cũng
    không ai biết là nó xanh vì luật còn đủ hay vì nó không kiểm gì cả.
    """

    def test_xoa_mot_luat_khoi_ban_sao_thi_bat_duoc_dung_ma_do(self):
        bang = doc_bang()
        ma, p, _dong, chu = bang[len(bang) // 2]
        goc = os.path.join(ROOT, p)
        with tempfile.TemporaryDirectory() as tam:
            sao = os.path.join(tam, os.path.basename(p))
            shutil.copy(goc, sao)
            with open(sao, encoding="utf-8") as f:
                noi_dung = f.read()
            self.assertTrue(luat_con_khong(neo(chu), noi_dung),
                            f"{ma} chưa có trong bản sao thì phép thử vô nghĩa")

            # Xoá đúng dòng mang luật đó khỏi bản sao.
            con_lai = [d for d in noi_dung.splitlines()
                       if neo(chu) not in chuan(d)]
            self.assertLess(len(con_lai), len(noi_dung.splitlines()),
                            "không xoá được dòng nào — phép thử vô nghĩa")
            with open(sao, "w", encoding="utf-8") as f:
                f.write("\n".join(con_lai))

            with open(sao, encoding="utf-8") as f:
                sau = f.read()
            self.assertFalse(luat_con_khong(neo(chu), sau),
                             f"lưới KHÔNG bắt được: {ma} đã xoá mà vẫn báo còn")

        with open(goc, encoding="utf-8") as f:
            self.assertTrue(luat_con_khong(neo(chu), f.read()),
                            "file gốc phải nguyên vẹn — test này cấm chạm skills/")


if __name__ == "__main__":
    unittest.main()
