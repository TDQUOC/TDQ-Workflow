"""Bộ kiểm thử xác thực báo cáo nghiên cứu chuyên sâu kiến trúc ECC (ecc-universal v2.2.3).

Kiểm tra cả hai định dạng xuất bản:
1. Báo cáo kỹ thuật Markdown 11 chương (`docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md`).
2. Standalone HTML Dashboard Report 100% offline (`docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html`).

Acceptance requires artifacts in this checkout; fixtures exercise validators only.
"""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REL_MD = "docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md"
REL_HTML = "docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html"

MA_PHAN_HE = tuple(f"SA{i}" for i in range(1, 11))
TU_KHOA_MD = (
    "TCAS",
    "Szymkiewicz-Simpson",
    "GateGuard",
    "scanShell",
    "ecc2",
    "orch-review",
    "Cryptographic Digest Chain",
    "TDQ Workflow",
)
SO_LIEU_MD = ("311", "71", "97", "122", "497", "333")
TU_KHOA_HTML = (
    "TCAS",
    "Szymkiewicz-Simpson",
    "GateGuard",
    "ecc2",
    "orch-review",
    "TDQ Workflow",
)
CUM_PLACEHOLDER = ("TODO:", "FIXME:", "lorem ipsum", "[placeholder]")


class _BoDemHTML(HTMLParser):
    """Bộ phân tích cú pháp HTML đếm thẻ mở/đóng <svg> và kiểm tra ô tìm kiếm."""

    def __init__(self):
        super().__init__()
        self.svg_mo = 0
        self.svg_dong = 0
        self.co_o_tim_kiem = False

    def handle_starttag(self, tag, attrs):
        if tag == "svg":
            self.svg_mo += 1
        if tag == "input" and self._la_input_tim_kiem(dict(attrs)):
            self.co_o_tim_kiem = True

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg_dong += 1

    @staticmethod
    def _la_input_tim_kiem(attrs):
        kieu = (attrs.get("type") or "").lower()
        goi_y = f"{attrs.get('id') or ''} {attrs.get('placeholder') or ''}".lower()
        return kieu in ("search", "text") and any(
            t in goi_y for t in ("search", "tìm", "loc", "filter")
        )


def tim_file_bao_cao(rel_path):
    """Find a report only in the checkout under acceptance testing."""
    duong_dan = ROOT / rel_path
    return duong_dan if duong_dan.is_file() else None


def _tim_muc_thieu(text, danh_sach):
    """Trả về danh sách các từ khóa bị thiếu trong văn bản."""
    return [muc for muc in danh_sach if muc not in text]


def _co_placeholder(text):
    """Kiểm tra xem văn bản có chứa dấu vết placeholder rút gọn hay không."""
    ban_thuong = text.lower()
    return [cum for cum in CUM_PLACEHOLDER if cum.lower() in ban_thuong]


def kiem_tra_noi_dung_markdown(text):
    """Xác thực toàn diện nội dung báo cáo Markdown; trả về danh sách lỗi (rỗng nếu đạt)."""
    loi = []
    if len(text.splitlines()) < 450:
        loi.append("Số dòng Markdown nhỏ hơn 450")
    for nhom, ds in (
        ("phân hệ", MA_PHAN_HE),
        ("từ khóa giải thuật", TU_KHOA_MD),
        ("số liệu thực tế", SO_LIEU_MD),
    ):
        thieu = _tim_muc_thieu(text, ds)
        if thieu:
            loi.append(f"Thiếu {nhom}: {', '.join(thieu)}")
    if _co_placeholder(text):
        loi.append("Phát hiện placeholder rút gọn")
    return loi


def _kiem_tra_dom_svg_va_search(text):
    """Phân tích HTML để kiểm tra cân bằng thẻ <svg>, số lượng >= 4 và ô tìm kiếm."""
    bo_dem = _BoDemHTML()
    bo_dem.feed(text)
    loi = []
    if bo_dem.svg_mo < 4 or bo_dem.svg_mo != bo_dem.svg_dong:
        loi.append(f"Thẻ SVG không hợp lệ: mở={bo_dem.svg_mo}, đóng={bo_dem.svg_dong}")
    if not bo_dem.co_o_tim_kiem:
        loi.append("Thiếu ô input tìm kiếm/lọc tương tác")
    return loi


def _co_chuc_nang_theme(text):
    """Kiểm tra HTML có hỗ trợ chuyển đổi giao diện Dark/Light mode."""
    ha_tang = text.lower()
    return "theme" in ha_tang and ("dark" in ha_tang or "light" in ha_tang)


def kiem_tra_noi_dung_html(text):
    """Xác thực toàn diện nội dung Standalone HTML Dashboard; trả về danh sách lỗi."""
    loi = []
    if len(text.splitlines()) < 700:
        loi.append("Số dòng HTML nhỏ hơn 700")
    if "cdn." in text.lower():
        loi.append("Phát hiện rò rỉ liên kết CDN ngoài (vi phạm 100% offline)")
    thieu = _tim_muc_thieu(text, MA_PHAN_HE + TU_KHOA_HTML)
    if thieu:
        loi.append(f"Thiếu mã phân hệ hoặc từ khóa: {', '.join(thieu)}")
    if not _co_chuc_nang_theme(text):
        loi.append("Thiếu cơ chế chuyển đổi giao diện Dark/Light mode")
    return loi + _kiem_tra_dom_svg_va_search(text)


def _tao_mau_markdown_hop_le():
    """Sinh văn bản Markdown mẫu đạt mọi tiêu chuẩn để kiểm thử validator."""
    dau = [
        "# Báo cáo Kiến trúc ECC",
        "Phân hệ: " + " ".join(MA_PHAN_HE),
        "Giải thuật: " + " ".join(TU_KHOA_MD),
        "Số liệu: " + " ".join(SO_LIEU_MD),
    ]
    than = [f"Dòng phân tích kỹ thuật chuyên sâu thứ {i}." for i in range(460)]
    return "\n".join(dau + than)


def _tao_mau_html_hop_le():
    """Sinh văn bản HTML mẫu đạt mọi tiêu chuẩn để kiểm thử validator."""
    svgs = ["<svg viewBox='0 0 100 50'><rect width='10' height='10'/></svg>" for _ in range(4)]
    dau = [
        "<!DOCTYPE html><html><head><title>ECC Report</title></head>",
        "<body data-theme='dark'><button id='theme-toggle'>Dark / Light</button>",
        "<input type='search' id='search-input' placeholder='Tìm kiếm phân hệ...'/>",
        "<div>" + " ".join(MA_PHAN_HE + TU_KHOA_HTML) + "</div>",
    ] + svgs
    than = [f"<p>Đoạn phân tích chi tiết số {i}</p>" for i in range(705)]
    return "\n".join(dau + than + ["</body></html>"])


class KiemThuValidatorBaoCaoTest(unittest.TestCase):
    """Kiểm thử trực tiếp các hàm xác thực trên cả dữ liệu hợp lệ lẫn dữ liệu lỗi."""

    def test_validator_markdown_nhan_mau_hop_le(self):
        mau = _tao_mau_markdown_hop_le()
        self.assertEqual(kiem_tra_noi_dung_markdown(mau), [])

    def test_validator_markdown_bat_loi_thieu_dong_va_thieu_muc(self):
        mau_loi = "# Báo cáo ngắn\nChỉ có SA1 và TCAS nhưng TODO: viết tiếp"
        loi = kiem_tra_noi_dung_markdown(mau_loi)
        self.assertGreaterEqual(len(loi), 4)
        self.assertTrue(any("450" in m for m in loi))
        self.assertTrue(any("SA2" in m for m in loi))
        self.assertTrue(any("placeholder" in m for m in loi))

    def test_validator_html_nhan_mau_hop_le(self):
        mau = _tao_mau_html_hop_le()
        self.assertEqual(kiem_tra_noi_dung_html(mau), [])

    def test_validator_html_bat_loi_cdn_thieu_svg_va_lech_the(self):
        mau_loi = (
            "<html><head><script src='https://cdn.jsdelivr.net/npm/chart.js'></script></head>"
            "<body><svg><g></svg><svg></body></html>"
        )
        loi = kiem_tra_noi_dung_html(mau_loi)
        self.assertTrue(any("700" in m for m in loi))
        self.assertTrue(any("CDN" in m for m in loi))
        self.assertTrue(any("SVG" in m for m in loi))
        self.assertTrue(any("Dark/Light" in m for m in loi))


class KiemThuFileBaoCaoThucTeTest(unittest.TestCase):
    """Kiểm thử hai file báo cáo thực tế (.md và .html) khi có mặt trên đĩa."""

    def test_khong_muon_bao_cao_tu_sibling_hoac_ancestor(self):
        with tempfile.TemporaryDirectory() as tmp:
            cha = Path(tmp)
            root = cha / "t1.0"
            root.mkdir()
            for base in (cha, cha / "t1.1", cha / "t1.2"):
                file = base / REL_MD
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(_tao_mau_markdown_hop_le(), encoding="utf-8")
            with mock.patch(f"{__name__}.ROOT", root):
                self.assertIsNone(tim_file_bao_cao(REL_MD))

    def test_thieu_artifact_khong_duoc_thay_bang_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch(f"{__name__}.ROOT", Path(tmp)):
                for ten in ("test_bao_cao_markdown_thuc_te_dat_chuan",
                            "test_bao_cao_html_thuc_te_dat_chuan"):
                    ket = unittest.TestResult()
                    type(self)(ten).run(ket)
                    self.assertEqual(len(ket.failures), 1, ten)
                    self.assertFalse(ket.errors, ket.errors)

    def test_tim_file_bao_cao_tra_ve_none_khi_khong_ton_tai(self):
        self.assertIsNone(tim_file_bao_cao("docs/tdq/reports/khong-ton-tai-xyz.md"))

    def test_bao_cao_markdown_thuc_te_dat_chuan(self):
        duong_dan = tim_file_bao_cao(REL_MD)
        if duong_dan is None:
            self.fail(f"Missing required artifact: {REL_MD}")
        noi_dung = duong_dan.read_text(encoding="utf-8")
        self.assertEqual(kiem_tra_noi_dung_markdown(noi_dung), [])

    def test_bao_cao_html_thuc_te_dat_chuan(self):
        duong_dan = tim_file_bao_cao(REL_HTML)
        if duong_dan is None:
            self.fail(f"Missing required artifact: {REL_HTML}")
        noi_dung = duong_dan.read_text(encoding="utf-8")
        self.assertEqual(kiem_tra_noi_dung_html(noi_dung), [])


if __name__ == "__main__":
    unittest.main()