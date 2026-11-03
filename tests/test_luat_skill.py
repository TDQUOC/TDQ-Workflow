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
RANH_GIOI = os.path.join(ROOT, "docs", "tdq", "audit", "ranh-gioi-luat.md")
DONG_RE = re.compile(r"^\| (L\d+) \| `([^`:]+):(\d+)` \|")
# Tách ô theo dấu `|` KHÔNG bị escape — nội dung luật có thể chứa `\|` của markdown.
O_RE = re.compile(r"(?<!\\)\|")
RANH_GIOI_RE = re.compile(r"^\| (L\d+) \| ([\w-]+) \|")

# Đối chiếu trên bao nhiêu ký tự đầu của luật. Đủ dài để không trùng nhau lung tung,
# đủ ngắn để sửa dấu câu cuối câu không làm đỏ oan.
DAI_NEO = 40


def doc_bang(path=BANG):
    """Bảng luật → [(mã, file, dòng, chữ neo cũ, neo bản mới)].

    Chữ neo đã gỡ escape của markdown. Ô `neo bản mới` rỗng là trạng thái bình thường
    của một luật chưa viết lại.
    """
    ban = []
    with open(path, encoding="utf-8") as f:
        for dong in f:
            m = DONG_RE.match(dong.rstrip("\n"))
            if not m:
                continue
            o = [c.strip() for c in O_RE.split(dong.rstrip("\n").strip())[1:-1]]
            go = lambda c: c.replace("\\|", "|").rstrip("…")
            ban.append((m.group(1), m.group(2), int(m.group(3)),
                        go(o[2]), go(o[3]) if len(o) > 3 else ""))
    return ban


def doc_nhan(path=RANH_GIOI):
    """Bảng ranh giới → {mã: nhãn}. Thiếu file thì trả dict rỗng, phần kiểm tự bỏ qua."""
    nhan = {}
    if not os.path.exists(path):
        return nhan
    with open(path, encoding="utf-8") as f:
        for dong in f:
            m = RANH_GIOI_RE.match(dong.rstrip("\n"))
            if m and m.group(2) in ("ly-luan", "user-facing"):
                nhan[m.group(1)] = m.group(2)
    return nhan


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

    def test_bang_co_cot_neo_ban_moi(self):
        with open(BANG, encoding="utf-8") as f:
            self.assertIn("neo bản mới", f.read(),
                          "bảng thiếu cột neo bản mới — lưới không sống qua bản dịch")

    def test_ma_khong_trung_nhau(self):
        ma = [b[0] for b in doc_bang()]
        self.assertEqual(len(ma), len(set(ma)), "mã L### bị trùng — tra ra nhầm luật")

    def test_moi_file_nguon_deu_ton_tai(self):
        for ma, p, _dong, _chu, _moi in doc_bang():
            with self.subTest(ma=ma):
                self.assertTrue(os.path.exists(os.path.join(ROOT, p)), p)


class KhoaLuatTest(unittest.TestCase):
    """Phần chính: mọi điểm neo phải còn nguyên trong file skill thật."""

    @classmethod
    def setUpClass(cls):
        cls.bang = doc_bang()
        cls.noi_dung = {}
        for _ma, p, _d, _c, _m in cls.bang:
            if p not in cls.noi_dung:
                with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                    cls.noi_dung[p] = f.read()

    def test_moi_luat_con_nguyen_trong_skill(self):
        """Chưa viết lại thì dò chữ cũ; đã viết lại thì dò chữ mới. Mất cái đang hiệu
        lực mới là mất luật."""
        mat = []
        for ma, p, dong, chu, moi in self.bang:
            dang_hieu_luc = moi or chu
            if not luat_con_khong(neo(dang_hieu_luc), self.noi_dung[p]):
                mat.append(f"{ma} ({p}:{dong}): {dang_hieu_luc[:60]}")
        self.assertEqual(mat, [], f"{len(mat)} luật biến mất khỏi skill:\n" +
                         "\n".join(mat))

    def test_so_dong_ghi_trong_bang_van_tro_dung_cho(self):
        """Mềm hơn test trên: số dòng lệch thì CẢNH BÁO qua tên test, không phải mất
        luật. Vẫn kiểm, vì lệch nhiều nghĩa là bảng cũ so với skill."""
        lech = 0
        for _ma, p, dong, chu, moi in self.bang:
            dòng_thật = self.noi_dung[p].splitlines()
            # Neo đang hiệu lực mới là thứ số dòng phải trỏ tới: luật đã viết lại thì
            # câu tiếng Việt cũ không còn nằm ở dòng nào cả.
            if dong - 1 >= len(dòng_thật) or not luat_con_khong(
                    neo(moi or chu), dòng_thật[dong - 1]):
                lech += 1
        ti_le = lech / len(self.bang) * 100
        self.assertLess(ti_le, 5.0,
                        f"{lech}/{len(self.bang)} dòng lệch ({ti_le:.1f}%) — "
                        "dựng lại luat-hien-co.md")


class SongNguTest(unittest.TestCase):
    """Luật của cột neo mới — thứ giữ cho lưới không bị tháo trong lúc dịch."""

    @classmethod
    def setUpClass(cls):
        cls.bang = doc_bang()
        cls.nhan = doc_nhan()

    def test_bang_ranh_gioi_ton_tai(self):
        """Bảng ranh giới mất là hai test dưới mất luôn ý nghĩa — bắt ngay ở đây, thay
        vì để chúng tự bỏ qua trong im lặng."""
        self.assertTrue(self.nhan, f"thiếu hoặc rỗng: {RANH_GIOI}")

    def test_moi_ma_deu_co_loi_khai_ranh_gioi(self):
        thieu = [b[0] for b in self.bang if b[0] not in self.nhan]
        self.assertEqual(thieu, [], f"{len(thieu)} mã chưa phân loại: {thieu[:5]}")

    def test_ma_user_facing_khong_duoc_doi_neo(self):
        pham = [ma for ma, _p, _d, _c, moi in self.bang
                if moi and self.nhan.get(ma) == "user-facing"]
        self.assertEqual(pham, [], f"mã user-facing bị đổi neo: {pham}")

    def test_neo_moi_phai_du_dai(self):
        """Neo mới ngắn hơn ngưỡng thì khớp bừa với câu khác — lưới xanh giả."""
        ngan = [ma for ma, _p, _d, _c, moi in self.bang
                if moi and len(chuan(moi)) < DAI_NEO]
        self.assertEqual(ngan, [], f"neo mới quá ngắn: {ngan}")


class LuoiBatDuocMatLuatTest(unittest.TestCase):
    """Test của chính cái lưới: xoá một luật khỏi BẢN SAO → lưới phải bắt được.

    Không có lớp này thì `test_moi_luat_con_nguyen_trong_skill` xanh vĩnh viễn cũng
    không ai biết là nó xanh vì luật còn đủ hay vì nó không kiểm gì cả.
    """

    def test_xoa_mot_luat_khoi_ban_sao_thi_bat_duoc_dung_ma_do(self):
        bang = doc_bang()
        ma, p, _dong, chu, moi = bang[len(bang) // 2]
        chu = moi or chu
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
