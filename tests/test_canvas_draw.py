"""Test cho scripts/canvas_draw.py — bộ dựng chương khổ A4 dọc."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import canvas_draw as cd  # noqa: E402


def test_kho_trang_la_a4_doc_1240():
    assert cd.W == 1240
    assert cd.X == 40


def chapter():
    return cd.Chapter(9, "Thử", y=0, height=1000)


def test_stack_xep_doc_cach_deu_theo_chieu_cao_that():
    ch = chapter()
    assert ch.stack(100, [50, 80, 30], gap=20) == [100, 170, 270]


def test_stack_gap_mac_dinh_la_24():
    ch = chapter()
    assert ch.stack(0, [100, 100]) == [0, 124]


def test_stack_rong_tra_ve_danh_sach_rong():
    assert chapter().stack(100, []) == []


def test_tieu_de_chuong_co_tien_to_so_va_co_chu_30():
    ch = chapter()
    title = ch.els[1]
    assert title["text"].startswith("9. ")
    assert title["fontSize"] == 30


def test_khung_chuong_rong_dung_kho():
    assert chapter().els[0]["width"] == cd.W


def test_text_mac_dinh_co_chu_16():
    ch = chapter()
    ch.text(60, 100, "một dòng")
    assert ch.els[-1]["fontSize"] == 16


def test_card_dung_co_chu_than_16():
    ch = chapter()
    ch.card(60, 100, 400, 120, "Tiêu đề", "Thân")
    assert ch.els[-1]["fontSize"] == 16


def test_fit_canh_bao_khi_dong_qua_70_phan_tram(capsys):
    cd.fit("x" * 200, 400, 16, "thử")
    assert "quá 70%" in capsys.readouterr().err


def test_fit_khong_canh_bao_khi_dong_ngan(capsys):
    cd.fit("ngắn", 400, 16, "thử")
    assert capsys.readouterr().err == ""


def test_row_chia_deu_het_be_ngang():
    ch = chapter()
    cols = ch.row(2, top=0, height=100)
    x0, w0 = cols[0]
    x1, w1 = cols[1]
    assert x0 == cd.X + 40
    assert w0 == w1
    assert x1 + w1 == cd.X + cd.W - 40


# ── dòng cây thư mục (canvas_a4_rebuild) ─────────────────────────────────

import canvas_a4_rebuild as car  # noqa: E402


def test_dong_cay_bi_bop_dem_chu_khong_ngat_tu():
    line = "├── hooks/" + " " * 30 + "hooks.json + 6 script Python"
    out = car.rewrap(line, 1120, 16)
    assert "\n" not in out                      # không bị ngắt thành 2 dòng
    assert out.startswith("├── hooks/")
    assert out.rstrip().endswith("script Python")
    assert len(out) <= car.max_chars(1120, 16)


def test_dong_cay_ngan_giu_nguyen():
    line = "└── tests/   unit test"
    assert car.rewrap(line, 1120, 16) == line


def test_unwrap_khong_noi_dong_cay():
    text = "├── scripts/     11 script Python (0 package ngoài)\n├── skills/   6 skill"
    assert car.unwrap(text, 400, 16) == text
