"""Chỉ mục dòng sinh tự động — `scripts/doc_index.py`.

Vì sao cần: 17 file luật đã CÓ mục lục, nhưng mục lục chỉ cho biết tên mục, không cho biết mục đó
nằm ở dòng nào. Không biết dòng thì không `offset/limit` được, nên agent đọc trọn file — và đó là
78% chi phí đọc luật của một request (đo 2026-10-02: 38 file `references/` chiếm 65k token).

Khối chỉ mục là một comment HTML gọn, KHÔNG phải bảng: bảng tốn ~230 token mỗi file, mà chính nó
cũng bị tính vào trần 3.500. Comment còn một lợi thế nữa — nó vô hình khi render markdown, nên
người đọc không bị rác.

Năm nhóm, chạy riêng bằng `-k`: `sinh`, `idempotent`, `khop`, `co_mat`, `log`.
"""
import io
import json
import os
import sys
import contextlib
import tempfile
import unittest
from unittest import mock

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_index  # noqa: E402

VAN_BAN = """# Tiêu đề file

Một đoạn mở đầu.

## Mục một

Nội dung một.
Thêm một dòng.

## Mục hai

Nội dung hai.

### Mục hai chấm một

Chi tiết.

## Mục ba

Hết.
"""

CO_FENCE = """# Tiêu đề

## Mục thật

Khuôn mẫu bên dưới, các dấu thăng trong đó KHÔNG phải mục của file này:

```markdown
## Mục giả trong fence
### Mục giả hai
```

## Mục thật hai

Hết.
"""


MUC_CO_CHU_THICH = """# T

## Mục một <!-- i18n-allow: ghi chú -->

Nội dung.

## Mục hai

Nội dung.
"""

BA_MUC_CO_CHU_THICH = """# T

## A <!-- x -->

n.

## B

n.

## C

n.
"""


CO_FRONTMATTER = """---
name: thu-nghiem
description: Một skill thử nghiệm.
---

# Tiêu đề skill

## Mục một

Nội dung.

## Mục hai

Nội dung.
"""


class BaseDocIndex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def ghi(self, noi_dung, ten="f.md"):
        """Ghi một file dưới thư mục tạm. `ten` nhận cả đường dẫn con, vì phép kiểm ngưỡng token
        cần file nằm đúng dưới `skills/<skill>/references/` mới được `file_can_chi_muc` nhìn thấy."""
        duong = os.path.join(self.tmp.name, ten)
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(noi_dung)
        return duong

    def doc(self, duong):
        with io.open(duong, encoding="utf-8") as fh:
            return fh.read()


class SinhChiMuc(BaseDocIndex):
    def test_sinh_khoi_nam_ngay_sau_tieu_de(self):
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        dong = self.doc(duong).split("\n")
        self.assertTrue(dong[0].startswith("# Tiêu đề"))
        self.assertIn(doc_index.MOC_MO, "\n".join(dong[1:4]),
                      "khối phải nằm ngay sau dòng tiêu đề, không trôi xuống giữa file")

    def test_sinh_du_moi_muc_hai_va_ba_thang(self):
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        khoi = doc_index.doc_chi_muc(duong)
        self.assertEqual(sorted(khoi), sorted(["Mục một", "Mục hai", "Mục hai chấm một", "Mục ba"]))

    def test_sinh_dong_tro_dung_cho(self):
        """Con số phải trỏ đúng dòng mở đầu của mục TRONG FILE ĐÃ CÓ KHỐI — nếu tính trước khi
        chèn thì mọi số đều lệch đúng bằng độ dài khối, và agent đọc sai đoạn."""
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        dong = self.doc(duong).split("\n")
        for ten, (dau, _cuoi) in doc_index.doc_chi_muc(duong).items():
            self.assertIn(ten, dong[dau - 1], f"dòng {dau} không phải mục {ten!r}")

    def test_sinh_bo_qua_muc_trong_fence(self):
        duong = self.ghi(CO_FENCE)
        doc_index.ghi_chi_muc(duong)
        khoi = doc_index.doc_chi_muc(duong)
        self.assertNotIn("Mục giả trong fence", khoi)
        self.assertEqual(sorted(khoi), ["Mục thật", "Mục thật hai"])

    def test_sinh_dong_khong_qua_100_ky_tu(self):
        """`doc_lint` chặn dòng dài; khối sinh ra phải tự gói, không được làm file đỏ lint."""
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        for d in self.doc(duong).split("\n"):
            self.assertLessEqual(len(d), 100, d[:60])

    def test_sinh_file_khong_co_muc_nao_thi_khong_chen_gi(self):
        duong = self.ghi("# Chỉ có tiêu đề\n\nMột đoạn.\n")
        self.assertFalse(doc_index.ghi_chi_muc(duong))
        self.assertNotIn(doc_index.MOC_MO, self.doc(duong))


class TenMucCoChuThich(BaseDocIndex):
    """Tiêu đề mang chú thích HTML không được làm vỡ khối chỉ mục.

    Đo được trên `soul.md`: tiêu đề §2 có `<!-- i18n-allow: … -->`, mà khối chỉ mục LÀ một chú
    thích HTML — nên dấu `-->` trong tên đóng sớm khối, bốn mục sau mất hẳn và phần đuôi lọt ra
    thành chữ thường giữa tài liệu.
    """

    def test_sinh_ten_muc_bo_chu_thich_html(self):
        duong = self.ghi(MUC_CO_CHU_THICH)
        doc_index.ghi_chi_muc(duong)
        khoi = doc_index.doc_chi_muc(duong)
        self.assertEqual(sorted(khoi), ["Mục hai", "Mục một"])
        self.assertNotIn("i18n-allow", self.doc(duong).split("-->", 1)[0])

    def test_sinh_du_moi_muc_du_co_chu_thich(self):
        duong = self.ghi(BA_MUC_CO_CHU_THICH)
        doc_index.ghi_chi_muc(duong)
        self.assertEqual(len(doc_index.doc_chi_muc(duong)), 3,
                         "chú thích trong tên không được cắt mất các mục sau")


class Idempotent(BaseDocIndex):
    def test_idempotent_chay_hai_lan_khong_sinh_hai_khoi(self):
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        mot = self.doc(duong)
        doc_index.ghi_chi_muc(duong)
        self.assertEqual(self.doc(duong), mot)
        self.assertEqual(self.doc(duong).count(doc_index.MOC_MO), 1)

    def test_idempotent_lan_hai_bao_khong_doi(self):
        duong = self.ghi(VAN_BAN)
        self.assertTrue(doc_index.ghi_chi_muc(duong), "lần đầu phải báo có đổi")
        self.assertFalse(doc_index.ghi_chi_muc(duong), "lần hai phải báo không đổi")

    def test_idempotent_cap_nhat_khi_noi_dung_doi(self):
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        with io.open(duong, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n## Mục bốn thêm sau\n\nNội dung.\n")
        self.assertTrue(doc_index.ghi_chi_muc(duong))
        self.assertIn("Mục bốn thêm sau", doc_index.doc_chi_muc(duong))


class KhopVoiNoiDung(BaseDocIndex):
    def test_khop_bat_duoc_chi_muc_lech(self):
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        with io.open(duong, encoding="utf-8") as fh:
            noi_dung = fh.read()
        # Chèn 5 dòng vào giữa mà KHÔNG sinh lại chỉ mục -> mọi số sau đó lệch.
        dong = noi_dung.split("\n")
        vi_tri = next(i for i, d in enumerate(dong) if d.startswith("## Mục một"))
        dong[vi_tri:vi_tri] = ["thêm", "thêm", "thêm", "thêm", "thêm"]
        with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(dong))
        self.assertFalse(doc_index.chi_muc_con_dung(duong), "chỉ mục đã lệch mà vẫn báo đúng")

    def test_khop_bao_dung_khi_vua_sinh(self):
        duong = self.ghi(VAN_BAN)
        doc_index.ghi_chi_muc(duong)
        self.assertTrue(doc_index.chi_muc_con_dung(duong))

    def test_khop_file_khong_co_khoi_thi_coi_la_dung(self):
        """Không có khối không phải lệch — việc 'phải có khối' do phép kiểm khác lo."""
        duong = self.ghi(VAN_BAN)
        self.assertTrue(doc_index.chi_muc_con_dung(duong))


class FileDayItDong(BaseDocIndex):
    """File DÀY mà ít dòng vẫn cần chỉ mục — ngưỡng dòng một mình bỏ sót nó.

    Ca thật: `skills/tdq-check-status/references/bang-lech.md` có 51 dòng mà 2.111 token, vì nó
    là một bảng đặc. Tiêu chí Q8 của spec đo bằng TOKEN, nên ngưỡng dòng một mình không đủ. Số
    token lấy từ tệp khoá (`docs/tdq/token-budget.json`) — một tệp JSON, không cần tokenizer, nên
    luật này vẫn chạy được ở CI.
    """

    def _ghi_khoa(self, rel, token):
        duong = os.path.join(self.tmp.name, "docs", "tdq", "token-budget.json")
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({rel: {"token": token, "sha256": "0" * 64}}, fh)

    def _ghi_file_ngan(self):
        return self.ghi("# Thử\n\n## Mục một\n\n" + "| a | b |\n" * 20
                        + "\n## Mục hai\n\n" + "| c | d |\n" * 20,
                        os.path.join("skills", "tdq-thu", "references", "day.md"))

    def test_file_day_it_dong_duoc_tinh_la_can_chi_muc(self):
        duong = self._ghi_file_ngan()
        self._ghi_khoa("skills/tdq-thu/references/day.md", doc_index.NGUONG_TOKEN)
        self.assertIn(duong, doc_index.file_can_chi_muc(self.tmp.name))

    def test_file_day_duoi_nguong_token_thi_khong_tinh(self):
        duong = self._ghi_file_ngan()
        self._ghi_khoa("skills/tdq-thu/references/day.md", doc_index.NGUONG_TOKEN - 1)
        self.assertNotIn(duong, doc_index.file_can_chi_muc(self.tmp.name))

    def test_khong_co_tep_khoa_thi_roi_ve_nguong_dong(self):
        """Khoá thiếu không được làm script nổ, cũng không được đoán: rơi về đếm dòng."""
        duong = self._ghi_file_ngan()
        self.assertNotIn(duong, doc_index.file_can_chi_muc(self.tmp.name))


class BaDefectTungLotLuoi(BaseDocIndex):
    """Ba ca `code-review` 2026-10-02 tìm ra — đều LATENT, nên chúng cần test chứ không phải chú
    thích: cả ba đều im lặng trên cây file hôm nay và chỉ nổ khi nội dung lớn thêm một chút.
    """

    def test_ten_muc_co_dau_phan_cach_van_kiem_duoc(self):
        """`_sach_ten` đổi `·` thành `-`, nên so với dòng tiêu đề THÔ là không bao giờ khớp."""
        duong = self.ghi("# T\n\n## Luật tick — `[ ]` · `[~]` · `[x]`\n\n"
                         "nội dung\n\n## Mục hai\n\nnội dung\n")
        doc_index.ghi_chi_muc(duong)
        self.assertTrue(doc_index.chi_muc_con_dung(duong),
                        "tên mục có `·` làm phép kiểm đỏ oan — và lệnh nó khuyên không sửa được gì")

    def test_frontmatter_khong_bi_pha_khi_file_mo_dau_bang_dong_trang(self):
        """Ca tự chữa: bản cũ để lại một dòng trắng trước frontmatter, và bản vá đó chèn khối vào
        GIỮA frontmatter."""
        duong = self.ghi("\n---\nname: x\ndescription: y\n---\n# T\n\n## Mục một\n\n"
                         "nội dung\n\n## Mục hai\n\nnội dung\n")
        doc_index.ghi_chi_muc(duong)
        dong = self.doc(duong).split("\n")
        than = [d for d in dong if d.strip()]
        self.assertEqual(than[0].strip(), "---", "frontmatter phải còn ở dòng đầu")
        ket = [k for k, d in enumerate(than) if d.strip() == "---"]
        self.assertGreaterEqual(len(ket), 2, 'frontmatter mất dấu đóng')
        giua = "\n".join(than[ket[0] + 1:ket[1]])
        self.assertNotIn(doc_index.MOC_MO, giua, "khối bị chèn vào GIỮA frontmatter")
        self.assertTrue(doc_index.chi_muc_con_dung(duong))

    def test_muc_dau_tien_qua_dai_khong_sinh_dong_rac(self):
        """Mục đầu dài hơn trần ký tự: bản cũ đẩy ra một dòng chỉ có `" ·"`."""
        ten_dai = "Mục đầu tiên dài quá trần ký tự của một dòng trong khối chỉ mục dòng này"
        duong = self.ghi(f"# T\n\n## {ten_dai}\n\nnội dung\n")
        doc_index.ghi_chi_muc(duong)
        for d in self.doc(duong).split("\n"):
            self.assertNotEqual(d.strip(), "·", "khối có dòng rác chỉ mang dấu phân cách")


class CoMatDuTrenRepo(unittest.TestCase):
    def test_co_mat_moi_file_luat_dai_deu_co_chi_muc(self):
        thieu = [d for d in doc_index.file_can_chi_muc(ROOT)
                 if not doc_index.co_chi_muc(d)]
        self.assertEqual(thieu, [], f"{len(thieu)} file luật dài chưa có chỉ mục dòng")

    def test_khop_moi_chi_muc_tren_repo_con_dung(self):
        lech = [d for d in doc_index.file_can_chi_muc(ROOT)
                if doc_index.co_chi_muc(d) and not doc_index.chi_muc_con_dung(d)]
        self.assertEqual(lech, [], f"{len(lech)} file có chỉ mục đã lệch với nội dung")


class LogService(BaseDocIndex):
    def test_log_tat_duoc_bang_bien_moi_truong(self):
        duong = self.ghi(VAN_BAN)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}):
                doc_index.ghi_chi_muc(duong)
        self.assertEqual(err.getvalue(), "")

    def test_log_bat_mac_dinh_co_timestamp(self):
        duong = self.ghi(VAN_BAN)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with mock.patch.dict(os.environ, {"TDQ_LOG": "1"}):
                doc_index.ghi_chi_muc(duong)
        self.assertRegex(err.getvalue(), r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


class FrontmatterKhongBiPha(BaseDocIndex):
    """Khối phải nằm SAU frontmatter YAML.

    `SKILL.md` mở đầu bằng `---`, không phải `# Tiêu đề`. Bản đầu chèn khối lên trên frontmatter,
    và ba phép kiểm hình dạng skill báo "thiếu frontmatter" — một file skill mất frontmatter thì
    host không nạp nó nữa.
    """

    def test_sinh_khoi_nam_sau_frontmatter(self):
        duong = self.ghi(CO_FRONTMATTER)
        doc_index.ghi_chi_muc(duong)
        dong = self.doc(duong).splitlines()
        self.assertEqual(dong[0].strip(), "---")
        self.assertEqual(dong[3].strip(), "---", "frontmatter phải còn nguyên, cả hai dấu `---`")
        self.assertTrue(any(d.startswith(doc_index.MOC_MO) for d in dong[4:10]),
                        "khối phải nằm sau frontmatter, không được chèn lên trên nó")

    def test_sinh_khoi_sau_ca_frontmatter_va_tieu_de(self):
        duong = self.ghi(CO_FRONTMATTER)
        doc_index.ghi_chi_muc(duong)
        dong = self.doc(duong).splitlines()
        vi_tri_khoi = next(i for i, d in enumerate(dong) if d.startswith(doc_index.MOC_MO))
        vi_tri_tieu_de = next(i for i, d in enumerate(dong) if d.startswith("# "))
        self.assertLess(vi_tri_tieu_de, vi_tri_khoi)


if __name__ == "__main__":
    unittest.main()
