#!/usr/bin/env python3
"""tdq_timing.py — đếm thời gian một request TDQ và từng phase của nó.

Hai con số, hai nguồn khác nhau, cố ý để cạnh nhau:

    Treo tường  — mốc trong `state.json` (`started_at` + `phase_history`). Bao gồm
                  cả thời gian chờ user duyệt, nên đây là "request tốn của tôi bao lâu".
    Model chạy  — cộng khoảng cách giữa các bước model trong transcript, chỉ tính
                  khoảng ≤ MAX_GAP_SECONDS (tái dùng ngưỡng của `step_audit.py`).
                  Đây là "máy làm bao lâu". Một phase chờ duyệt 2 giờ mà model chỉ
                  chạy 3 phút thì hai cột lệch nhau đúng chỗ đáng nhìn.

Script này KHÔNG ghi `state.json` (luật kiến trúc: chỉ `tdq_state.py` được ghi).
Nó chỉ đọc state và ghi `docs/tdq/timing.jsonl` — dữ liệu lịch sử, không phải state.

Dùng:
    python3 scripts/tdq_timing.py show              # bảng markdown của request đang mở
    python3 scripts/tdq_timing.py show --json       # cùng số liệu, dạng JSON
    python3 scripts/tdq_timing.py close             # đóng sổ: append 1 dòng timing.jsonl

Env: TDQ_PROJECT_DIR chọn project · TDQ_LOG=0 tắt log tiến trình (log ra stderr).
Exit: 0 kể cả khi chưa có request hay không tìm thấy transcript. 2 = sai cú pháp.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tdq_state  # noqa: E402
from step_audit import MAX_GAP_SECONDS, _has_usage, _parse_time  # noqa: E402
from token_audit import default_transcript_dir, find_sessions, iter_events  # noqa: E402

TIMING_REL = os.path.join("docs", "tdq", "timing.jsonl")
EXIT_SYNTAX = 2


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log tiến trình ra stderr kèm timestamp. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------------- định dạng

def dinh_dang(giay):
    """Giây → chuỗi người đọc được. `None` → '—' (không đo được, khác với 0)."""
    if giay is None:
        return "—"
    giay = int(round(giay))
    if giay < 60:
        return f"{giay} giây"
    phut, du = divmod(giay, 60)
    if phut < 60:
        return f"{phut} phút" if du < 30 else f"{phut + 1} phút"
    gio, phut = divmod(phut, 60)
    return f"{gio} giờ" if phut == 0 else f"{gio} giờ {phut:02d} phút"


# ------------------------------------------------------------------ cửa sổ phase

def cua_so_phase(state, ket_thuc):
    """`phase_history` → danh sách cửa sổ [(phase, bắt đầu, kết thúc)] theo thứ tự.

    Mốc cuối cùng kéo dài tới `ket_thuc` (thời điểm đang xét). Mốc hỏng bị bỏ qua
    ở tầng `tdq_state.load`, nên ở đây chỉ cần lo mốc không parse được thời gian.
    """
    moc = []
    for item in state.get("phase_history") or []:
        at = _parse_time(item.get("at"))
        if at:
            moc.append((item.get("phase"), at))
    cua_so = []
    for i, (phase, bat_dau) in enumerate(moc):
        het = moc[i + 1][1] if i + 1 < len(moc) else ket_thuc
        if het and het >= bat_dau:
            cua_so.append((phase, bat_dau, het))
    return cua_so


def moc_model(transcript_dir, tu, den):
    """Danh sách thời điểm các BƯỚC model nằm trong [tu, den], đã sắp xếp.

    Trả `None` khi không có transcript nào đọc được — khác hẳn với 'có transcript
    nhưng model chạy 0 giây', nên cột model in '—' thay vì '0 giây'.
    """
    if not transcript_dir or not os.path.isdir(transcript_dir):
        _log(f"không thấy thư mục transcript: {transcript_dir} — bỏ cột thời gian model")
        return None
    files = find_sessions(transcript_dir, limit=0)
    if not files:
        _log(f"thư mục transcript rỗng: {transcript_dir} — bỏ cột thời gian model")
        return None
    thoi_diem = []
    for path in files:
        for event in iter_events(path):
            if event.get("type") != "assistant" or not _has_usage(event):
                continue
            at = _parse_time(event.get("timestamp"))
            if at and (tu is None or at >= tu) and (den is None or at <= den):
                thoi_diem.append(at)
    _log(f"đọc {len(files)} transcript, lấy {len(thoi_diem)} bước model trong khoảng request")
    return sorted(thoi_diem)


def _giay_model(thoi_diem, bat_dau, het):
    """Cộng khoảng cách giữa các bước model liền nhau trong một cửa sổ.

    Khoảng dài hơn `MAX_GAP_SECONDS` là user đi làm việc khác rồi quay lại, không
    phải model chạy — bỏ ra, đúng như `step_audit.py` làm với độ trễ.
    """
    trong = [t for t in thoi_diem if bat_dau <= t <= het]
    tong = 0.0
    for truoc, sau in zip(trong, trong[1:]):
        gap = (sau - truoc).total_seconds()
        if 0 <= gap <= MAX_GAP_SECONDS:
            tong += gap
    return tong


def tong_hop(state, ket_thuc, transcript_dir):
    """Số liệu đầy đủ của request đang mở. Trả None khi chưa có request nào."""
    slug = state.get("active_request")
    if not slug:
        return None
    bat_dau = _parse_time(state.get("started_at"))
    cua_so = cua_so_phase(state, ket_thuc)
    if bat_dau is None and cua_so:
        bat_dau = cua_so[0][1]
    thoi_diem = moc_model(transcript_dir, bat_dau, ket_thuc)

    gop = {}
    thu_tu = []
    for phase, tu, den in cua_so:
        if phase not in gop:
            gop[phase] = {"phase": phase, "treo_tuong_giay": 0, "model_giay": 0, "so_lan": 0}
            thu_tu.append(phase)
        muc = gop[phase]
        muc["treo_tuong_giay"] += int(round((den - tu).total_seconds()))
        muc["so_lan"] += 1
        if thoi_diem is not None:
            muc["model_giay"] += int(round(_giay_model(thoi_diem, tu, den)))
    phases = [gop[p] for p in thu_tu]
    if thoi_diem is None:
        for muc in phases:
            muc["model_giay"] = None

    # Hai tổng đo trên CÙNG một cửa sổ (started_at → lúc chốt), không phải tổng các cửa
    # sổ phase: state cũ được vá `started_at` về sau có thể có bước model nằm ngoài mọi
    # cửa sổ phase, cộng dồn theo phase sẽ bỏ sót chúng và hai tổng lệch nhau.
    tong_treo = int(round((ket_thuc - bat_dau).total_seconds())) if bat_dau else 0
    tong_model = (None if thoi_diem is None or bat_dau is None
                  else int(round(_giay_model(thoi_diem, bat_dau, ket_thuc))))
    return {
        "slug": slug,
        "lane": state.get("lane"),
        "started_at": state.get("started_at") or (bat_dau.isoformat() if bat_dau else None),
        "closed_at": ket_thuc.isoformat(timespec="seconds"),
        "treo_tuong_giay": tong_treo,
        "model_giay": tong_model,
        "phases": phases,
    }


def bang_markdown(so_lieu):
    """Bảng markdown 4 cột — khuôn dùng chung cho report và `tdq-status`."""
    dong = [f"Request `{so_lieu['slug']}` · lane {so_lieu['lane'] or '—'} · "
            f"mở lúc {so_lieu['started_at'] or '—'}",
            "",
            "| Phase | Treo tường | Model chạy | Số lần vào |",
            "|---|---|---|---|"]
    for muc in so_lieu["phases"]:
        dong.append(f"| {muc['phase']} | {dinh_dang(muc['treo_tuong_giay'])} | "
                    f"{dinh_dang(muc['model_giay'])} | {muc['so_lan']} |")
    dong.append(f"| **Tổng** | **{dinh_dang(so_lieu['treo_tuong_giay'])}** | "
                f"**{dinh_dang(so_lieu['model_giay'])}** | |")
    if so_lieu["model_giay"] is None:
        dong.append("")
        dong.append("Cột model là `—`: không đọc được transcript của session này.")
    return "\n".join(dong)


def dong_ho_ngan(so_lieu):
    """Một dòng cho `tdq-status`: phase đang chạy đã tốn bao lâu, request tổng bao lâu."""
    dang = so_lieu["phases"][-1] if so_lieu["phases"] else None
    if dang is None:
        return f"⏱ {so_lieu['slug']}: {dinh_dang(so_lieu['treo_tuong_giay'])}"
    return (f"⏱ {dang['phase']} {dinh_dang(dang['treo_tuong_giay'])}"
            f" (model {dinh_dang(dang['model_giay'])})"
            f" · cả request {dinh_dang(so_lieu['treo_tuong_giay'])}")


# --------------------------------------------------------------------- đóng sổ

def da_dong_so(cwd, slug, started_at):
    """Request này đã có dòng trong timing.jsonl chưa — chặn đếm hai lần.

    `init` và `tdq_finish --phase idle` đều gọi đóng sổ; không chặn thì một request
    xuất hiện hai lần và mọi thống kê sau đó sai.
    """
    path = os.path.join(cwd, TIMING_REL)
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ban_ghi = json.loads(line)
                except ValueError:
                    continue
                if ban_ghi.get("slug") == slug and ban_ghi.get("started_at") == started_at:
                    return True
    except OSError:
        return False
    return False


def dong_so(cwd, so_lieu):
    """Append đúng một dòng JSON vào timing.jsonl. Trả False nếu đã đóng trước đó."""
    if da_dong_so(cwd, so_lieu["slug"], so_lieu["started_at"]):
        _log(f"request {so_lieu['slug']} đã có trong {TIMING_REL} — không ghi lại")
        return False
    path = os.path.join(cwd, TIMING_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(so_lieu, ensure_ascii=False) + "\n")
    _log(f"đã đóng sổ {so_lieu['slug']} vào {TIMING_REL}")
    return True


# -------------------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tdq_timing.py",
        description="Đếm thời gian request TDQ: treo tường và model chạy, theo từng phase.")
    parser.add_argument("cmd", choices=("show", "close", "status"),
                        help="show = in bảng · close = đóng sổ vào timing.jsonl · "
                             "status = một dòng đồng hồ")
    parser.add_argument("--json", action="store_true", dest="want_json",
                        help="in số liệu thô dạng JSON")
    parser.add_argument("--now", help="mốc 'bây giờ' dạng ISO (để test tái lập được)")
    parser.add_argument("--transcript-dir", help="thư mục transcript, mặc định theo project")
    parser.add_argument("--project", help="thư mục project, mặc định theo TDQ_PROJECT_DIR/git root")
    args = parser.parse_args(argv)

    cwd = args.project or tdq_state.resolve_project_dir()
    ket_thuc = _parse_time(args.now) if args.now else datetime.datetime.now().astimezone()
    if args.now and ket_thuc is None:
        print(f"--now không phải thời điểm ISO: {args.now}", file=sys.stderr)
        return EXIT_SYNTAX

    state = tdq_state.load(cwd)
    if not state or not state.get("active_request"):
        # Không có request đang mở KHÔNG phải lỗi: hook và report gọi lệnh này vô điều kiện.
        print("Chưa có request nào đang mở — không có thời gian để đếm.")
        return 0

    transcript_dir = args.transcript_dir or default_transcript_dir(cwd)
    so_lieu = tong_hop(state, ket_thuc, transcript_dir)

    if args.cmd == "close":
        dong_so(cwd, so_lieu)
        if args.want_json:
            print(json.dumps(so_lieu, ensure_ascii=False))
        else:
            print(bang_markdown(so_lieu))
        return 0
    if args.cmd == "status":
        print(dong_ho_ngan(so_lieu))
        return 0
    print(json.dumps(so_lieu, ensure_ascii=False) if args.want_json else bang_markdown(so_lieu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
