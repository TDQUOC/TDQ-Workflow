"""Test cho scripts/check_canvas_layout.py — kiểm hình học scene Excalidraw."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_canvas_layout as ccl  # noqa: E402


def frame(n, y, height=100, x=0, width=1000):
    return {"id": f"ch{n}-frame", "type": "rectangle", "x": x, "y": y,
            "width": width, "height": height}


def title(n, text, y, x=10):
    return {"id": f"ch{n}-title", "type": "text", "x": x, "y": y,
            "width": 300, "height": 20, "text": text}


def toc_line(n, text, y):
    return {"id": f"toc-{n}", "type": "text", "x": 10, "y": y,
            "width": 300, "height": 20, "text": text}


def good_scene():
    """Hai chương hợp lệ + mục lục ở chương 0."""
    return [
        frame(0, 0, height=100),
        toc_line(1, "1. Tổng quan", 10),
        toc_line(2, "2. Kiến trúc", 40),
        frame(1, 200),
        title(1, "1. Tổng quan", 210),
        {"id": "ch1-box", "type": "rectangle", "x": 10, "y": 240,
         "width": 200, "height": 40},
        frame(2, 400),
        title(2, "2. Kiến trúc", 410),
    ]


def write(tmp_path, elements):
    path = tmp_path / "scene.excalidraw"
    path.write_text(json.dumps({"elements": elements}), encoding="utf-8")
    return str(path)


def run(scene_path, *flags):
    return ccl.main([scene_path, *flags])


# ── ca đúng ───────────────────────────────────────────────────────────────

def test_scene_hop_le_pass_moi_phep_kiem(tmp_path):
    path = write(tmp_path, good_scene())
    assert run(path, "--chapters", "--overlap", "--contain", "--order",
               "--toc", "--expect", "2") == 0


# ── ca sai ────────────────────────────────────────────────────────────────

def test_hai_khung_chong_lan_thi_fail(tmp_path):
    els = good_scene()
    # kéo khung chương 2 lên đè khung chương 1
    els[6]["y"] = 250
    path = write(tmp_path, els)
    assert run(path, "--overlap") == 1


def test_phan_tu_tran_ra_ngoai_khung_thi_fail(tmp_path):
    els = good_scene()
    # ch1-box rộng vượt bề ngang khung
    els[5]["width"] = 5000
    path = write(tmp_path, els)
    assert run(path, "--contain") == 1


def test_sai_thu_tu_doc_thi_fail(tmp_path):
    els = good_scene()
    # đảo y: chương 2 nằm trên chương 1
    els[3]["y"], els[6]["y"] = 400, 200
    els[4]["y"], els[7]["y"] = 410, 210
    els[5]["y"] = 440
    path = write(tmp_path, els)
    assert run(path, "--order") == 1


def test_muc_luc_lech_tieu_de_thi_fail(tmp_path):
    els = good_scene()
    els[2]["text"] = "2. Tên khác hẳn"
    path = write(tmp_path, els)
    assert run(path, "--toc") == 1


def test_thieu_chuong_thi_fail(tmp_path):
    els = [e for e in good_scene() if not e["id"].startswith("ch2-")]
    path = write(tmp_path, els)
    assert run(path, "--chapters", "--expect", "2") == 1


def test_tieu_de_khong_co_tien_to_so_thi_fail(tmp_path):
    els = good_scene()
    els[4]["text"] = "Tổng quan"
    path = write(tmp_path, els)
    assert run(path, "--chapters", "--expect", "2") == 1


def test_phan_tu_ngoai_moi_khung_thi_fail(tmp_path):
    els = good_scene()
    els.append({"id": "lac-loi", "type": "rectangle", "x": 9000, "y": 9000,
                "width": 10, "height": 10})
    path = write(tmp_path, els)
    assert run(path, "--contain") == 1


# ── cờ --width: mọi khung rộng đúng khổ ───────────────────────────────────

def test_moi_khung_dung_be_ngang_thi_pass(tmp_path):
    path = write(tmp_path, good_scene())  # mọi khung width=1000
    assert run(path, "--width", "1000") == 0


def test_mot_khung_lech_be_ngang_thi_fail(tmp_path):
    els = good_scene()
    els[6]["width"] = 1240  # khung chương 2 lệch khổ
    path = write(tmp_path, els)
    assert run(path, "--width", "1000") == 1


def test_be_ngang_lech_duoi_TOL_van_pass(tmp_path):
    els = good_scene()
    els[6]["width"] = 1000.4
    path = write(tmp_path, els)
    assert run(path, "--width", "1000") == 0


# ── cờ --fontsize: không chữ nào nhỏ hơn ngưỡng ───────────────────────────

def test_moi_chu_du_lon_thi_pass(tmp_path):
    els = good_scene()
    for el in els:
        if el["type"] == "text":
            el["fontSize"] = 16
    path = write(tmp_path, els)
    assert run(path, "--fontsize", "14") == 0


def test_co_chu_nho_hon_nguong_thi_fail(tmp_path, capsys):
    els = good_scene()
    for el in els:
        if el["type"] == "text":
            el["fontSize"] = 16
    els[1]["fontSize"] = 11
    path = write(tmp_path, els)
    assert run(path, "--fontsize", "14") == 1
    assert "toc-1" in capsys.readouterr().out


def test_text_thieu_fontSize_thi_khong_bao_loi(tmp_path):
    # good_scene() không element nào có fontSize — mặc định Excalidraw là 20
    path = write(tmp_path, good_scene())
    assert run(path, "--fontsize", "14") == 0


# ── hành vi phụ trợ ───────────────────────────────────────────────────────

def test_bbox_cua_arrow_tinh_theo_points():
    arrow = {"id": "a1", "type": "arrow", "x": 100, "y": 50,
             "width": 0, "height": 0, "points": [[0, 0], [200, 0]]}
    assert ccl.bbox(arrow) == (100, 50, 300, 50)


def test_dem_theo_khung_gom_ca_element_id_ngau_nhien(tmp_path, capsys):
    els = good_scene()
    els.append({"id": "mspjtprgxyz", "type": "text", "x": 20, "y": 250,
                "width": 50, "height": 15, "text": "label"})
    path = write(tmp_path, els)
    assert run(path, "--count-by-region") == 0
    out = capsys.readouterr().out
    assert "chapter 1" in out


def test_khong_chon_phep_kiem_nao_thi_bao_loi(tmp_path):
    path = write(tmp_path, good_scene())
    with pytest.raises(SystemExit):
        run(path)
