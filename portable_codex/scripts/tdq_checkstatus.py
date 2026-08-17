#!/usr/bin/env python3
"""Dò lại request TDQ đang dở và báo cáo để tiếp tục mà không mất dữ liệu.

Nguyên tắc: **đĩa là bằng chứng, `state.json` là lời khai**. Tài sản trong
`docs/tdq/**`, git và working log đi theo repo khi đổi máy; `state.json` có thể cũ,
sai schema, hoặc do một agent khác bỏ quên. Lệch nhau thì tin đĩa.

Script này CHỈ ĐỌC. Nó không bao giờ ghi `state.json` — chỉ IN ra lệnh vá đề xuất
để người dùng gật một lần rồi skill mới chạy. Mọi lệnh vá bắt buộc thuộc đúng hai
họ `tdq_state.py set …` và `tdq_state.py approve …`.

Dùng:
  python3 scripts/tdq_checkstatus.py report
  python3 scripts/tdq_checkstatus.py report --json
  python3 scripts/tdq_checkstatus.py report --project /duong/dan --now 2026-08-16T10:00:00+07:00

Env: TDQ_PROJECT_DIR ghi đè project root · TDQ_LOG=0 tắt log tiến trình ra stderr.
Exit: 0 mọi trạng thái (kể cả khi phát hiện lệch); 2 khi SAI CÚ PHÁP LỆNH.
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tdq_state  # noqa: E402

SCHEMA_HIEN_TAI = tdq_state.default_state()["schema_version"]
GIT_LOG_LIMIT = 20                      # trần để `report` giữ dưới 2,0 giây
LOAI_TAI_SAN = ("brief", "spec", "plan", "qc", "reports")
MUC_HOP_LE = ("ok", "canh-bao", "chan")   # thứ tự = mức nghiêm trọng tăng dần

# Ba mức kết luận — chữ này đi thẳng vào báo cáo, skill đọc đúng chữ để rẽ nhánh.
TIEP_TUC = "TIẾP TỤC ĐƯỢC"
VA_ROI_TIEP = "VÁ RỒI TIẾP TỤC"
CAN_USER = "CẦN USER QUYẾT"

# Chỉ hai họ lệnh này được phép sinh ra. Mọi thứ khác là đường làm mất dữ liệu.
#
# DANH SÁCH TRẮNG khớp NGUYÊN chuỗi, không phải danh sách đen. Danh sách đen từng để lọt
# `>docs/x.md` (không space), `;mv …`, `&& git checkout --`, `| truncate …` — mỗi thứ đều
# xoá được dữ liệu. Ở đây: đúng một lệnh, đúng một cặp khoá=giá trị hoặc một target duyệt,
# và không ký tự shell nào. Giá trị chứa chữ "reset"/"init" là DỮ LIỆU, vẫn cho qua.
MAU_LENH_VA = re.compile(
    r"^python3 scripts/tdq_state\.py "
    r"(set [a-z_]+=\S+"
    r"|approve (spec|plan|quick)( --by \"[^\"]*\")?)$"
)
KY_TU_SHELL_CAM = ";|&<>$`\\\n\r\t*?(){}[]!"

_TASK = re.compile(r"^\s*-\s*\[( |~|x)\]\s*\*\*([A-Za-z][\w.]*)\*\*")

# ---------------------------------------------------------------- 11 ca lệch
#
# Bảng cứng, không để model tự nghĩ ra chẩn đoán: model yếu gặp state lạ sẽ bịa
# lệnh sai và làm mất spec/plan. Bản người đọc nằm ở
# skills/tdq-check-status/references/bang-lech.md và bị test khoá cho khớp bảng này.
CA_LECH = {
    "D1": {
        "dau_hieu": "không đọc được request nào (không có, phase = idle, hoặc state hỏng)",
        "muc": "ok",
        "chan_doan": "Đĩa trống thì mở request mới bằng tdq-intake; đĩa còn spec/plan thì "
                     "CẤM chạy `init`, khôi phục state trước.",
        "lenh_va": None,
    },
    "D2": {
        "dau_hieu": "phase trong state lệch bằng chứng đĩa",
        "muc": "canh-bao",
        "chan_doan": "Phase khai trong state không khớp thứ đã có trên đĩa.",
        "lenh_va": "set phase=PHASE_ĐÚNG",
    },
    "D3": {
        "dau_hieu": "sha256 của spec lệch với lúc duyệt (plan lệch chỉ là `ok`)",
        "muc": "chan",
        "chan_doan": "File đã sửa sau khi duyệt — cần user duyệt lại, cấm tự approve.",
        "lenh_va": None,
    },
    "D4": {
        "dau_hieu": "nhiều hơn một task mang dấu `[~]`",
        "muc": "canh-bao",
        "chan_doan": "Không xác định được chỗ dừng: chỉ một task được phép `[~]`.",
        "lenh_va": None,
    },
    "D5": {
        "dau_hieu": "file đăng ký trong state nhưng mất trên đĩa",
        "muc": "chan",
        "chan_doan": "Mất tài sản của request — khôi phục file trước, đừng đi tiếp.",
        "lenh_va": None,
    },
    "D6": {
        "dau_hieu": "cờ duyệt bật nhưng thiếu `*_approved_by` hoặc `*_approved_at`",
        "muc": "canh-bao",
        "chan_doan": "Không truy được ai duyệt — xin user nhắc lại câu duyệt rồi ghi lại.",
        "lenh_va": "approve TARGET --by \"CÂU_DUYỆT_NGUYÊN_VĂN_CỦA_USER\"",
    },
    "D7": {
        "dau_hieu": "có commit git mới hơn `updated_at` của state",
        "muc": "canh-bao",
        "chan_doan": "Ai đó (agent khác/máy khác) đã làm việc mà state chưa ghi nhận.",
        "lenh_va": None,
    },
    "D8": {
        "dau_hieu": "working log hôm nay không nhắc slug đang mở",
        "muc": "ok",
        "chan_doan": "Chưa có dòng log nào cho request này hôm nay — bình thường nếu vừa mở.",
        "lenh_va": None,
    },
    "D9": {
        "dau_hieu": "`schema_version` cũ hơn bản hiện tại",
        "muc": "canh-bao",
        "chan_doan": "State do bản plugin cũ ghi — nâng schema trước khi đọc tiếp.",
        "lenh_va": f"set schema_version={SCHEMA_HIEN_TAI}",
    },
    "D10": {
        "dau_hieu": "thiếu `started_at` hoặc `phase_history` rỗng",
        "muc": "canh-bao",
        "chan_doan": "Mất mốc thời gian — bảng thời gian của report sẽ sai nếu không vá.",
        "lenh_va": "set started_at=ISO_MỐC_MỞ_REQUEST",
    },
    "D11": {
        "dau_hieu": "có `state.json` lạc chỗ ngoài project root",
        "muc": "chan",
        "chan_doan": "Hai state cùng sống: hook ghi một nơi, model đọc một nơi khác.",
        "lenh_va": None,
    },
}


# ------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log tiến trình ra stderr kèm timestamp. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------ chặn lệnh vá

def kiem_lenh_va(lenh):
    """Chặn nội bộ: raise ValueError nếu lệnh không thuộc hai họ set/approve.

    Đây là hàng rào cuối cùng của luật không mất dữ liệu. Mọi lệnh IN RA cho user
    đều đi qua đây, nên một mẫu lệnh viết ẩu sẽ nổ ở test chứ không tới tay user.
    """
    xau = next((c for c in KY_TU_SHELL_CAM if c in lenh), None)
    if xau:
        raise ValueError(f"lệnh vá chứa ký tự shell {xau!r}: {lenh!r}")
    if not MAU_LENH_VA.match(lenh):
        raise ValueError(f"lệnh vá không khớp danh sách trắng set/approve: {lenh!r}")
    return lenh


def _lenh(phan_con_lai):
    return kiem_lenh_va(f"python3 scripts/tdq_state.py {phan_con_lai}")


# --------------------------------------------------------- gom bằng chứng

def _duong_tai_san(slug, loai):
    return os.path.join("docs", "tdq", loai, f"{slug}.md")


def _dau_file(cwd, rel):
    """Một tài sản trên đĩa: có/không, sha256, số dòng."""
    if not rel:
        return {"co": False, "rel": None, "sha": None, "dong": 0}
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    if not os.path.isfile(path):
        return {"co": False, "rel": rel, "sha": None, "dong": 0}
    with open(path, encoding="utf-8", errors="replace") as f:
        dong = sum(1 for _ in f)
    return {"co": True, "rel": rel, "sha": tdq_state.sha256_file(path), "dong": dong}


def _dem_tick(cwd, rel):
    """Đếm checkbox plan VÀ lấy mã của các task `[~]`.

    Tái dùng `tdq_state.plan_tick_state()` cho path/sha/tổng (đã có sẵn, tra bằng
    `graphify query "plan_tick_state"`). Phải quét thêm một lượt vì hàm đó cố tình
    không trả MÃ task — mà mã task chính là thứ trả lời "đang dừng ở đâu".
    """
    goc = tdq_state.plan_tick_state(cwd)
    tick = {"tong": goc["total"], "xong": 0, "dang_lam": [],
            "sha": goc["sha"], "co": goc["exists"]}
    if not rel:
        return tick
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            dong_file = f.readlines()
    except OSError:
        return tick
    tong = xong = 0
    dang = []
    for dong in dong_file:
        m = _TASK.match(dong)
        if not m:
            continue
        tong += 1
        if m.group(1) == "x":
            xong += 1
        elif m.group(1) == "~":
            dang.append(m.group(2))
    tick.update(tong=tong, xong=xong, dang_lam=dang, co=True)
    return tick


def _gom_git(cwd):
    """Nhánh, commit gần đây và file bẩn. Repo không phải git thì trả lý do, không ném."""
    out = tdq_state._git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    if out is None:
        return {"co": False, "ly_do": "không phải git repo, hoặc chưa có commit nào",
                "nhanh": "—", "commit": [], "ban": []}
    nhanh = out.decode("utf-8", "replace").strip()
    log = tdq_state._git(cwd, "log", f"-{GIT_LOG_LIMIT}", "--format=%H%x09%cI%x09%s")
    commit = []
    for dong in (log or b"").decode("utf-8", "replace").splitlines():
        phan = dong.split("\t", 2)
        if len(phan) == 3:
            commit.append({"sha": phan[0][:8], "luc": phan[1], "tieu_de": phan[2]})
    status = tdq_state._git(cwd, "status", "--short")
    ban = (status or b"").decode("utf-8", "replace").splitlines()
    return {"co": True, "ly_do": None, "nhanh": nhanh, "commit": commit, "ban": ban}


def _gom_working_log(cwd, moc, slug):
    """Working log của ngày `moc`: mốc entry cuối, và slug được nhắc ở đâu.

    Hai cờ tách bạch có chủ ý: `nhac_slug` quét cả file (dùng chấm D8, tránh báo oan khi
    slug nằm ở entry giữa ngày), `nhac_slug_entry_cuoi` chỉ soi entry cuối để trả lời
    "việc gần nhất trong ngày có phải request này không".
    """
    rel = os.path.join("docs", "workinglog", moc.strftime("%Y-%m-%d") + ".md")
    path = os.path.join(cwd, rel)
    trong = {"rel": rel, "co": False, "nhac_slug": False,
             "entry_cuoi": None, "nhac_slug_entry_cuoi": False}
    if not os.path.isfile(path):
        return trong
    with open(path, encoding="utf-8", errors="replace") as f:
        noi_dung = f.read()
    dong = [d for d in noi_dung.splitlines() if d.strip()]
    tieu_de = [i for i, d in enumerate(dong) if d.startswith("#")]
    khoi_cuoi = dong[tieu_de[-1]:] if tieu_de else dong
    trong.update(co=True, nhac_slug=bool(slug) and slug in noi_dung,
                 entry_cuoi=khoi_cuoi[0] if khoi_cuoi else None,
                 nhac_slug_entry_cuoi=bool(slug) and slug in "\n".join(khoi_cuoi))
    return trong


def doc_state_tho(cwd):
    """Đọc thẳng file state, KHÔNG qua `tdq_state.load()`. Trả (tình trạng, dict thô).

    Ba tình trạng: `ok` · `khong-co` (chưa từng có request) · `hong` (file còn đó nhưng
    không parse được). Phân biệt hai cái sau là bắt buộc: coi state hỏng là "chưa có
    request" thì bước kế tiếp sẽ là mở request mới, và request đang dở mất sạch.
    """
    path = tdq_state.state_path(cwd)
    if not os.path.isfile(path):
        return "khong-co", None
    try:
        with open(path, encoding="utf-8") as f:
            tho = json.load(f)
    except (OSError, ValueError):
        return "hong", None
    return ("ok", tho) if isinstance(tho, dict) else ("hong", None)


def _schema_tren_dia(tho):
    """`schema_version` ĐÚNG NHƯ trong file, ép về int.

    `tdq_state.load()` vá trường này về bản hiện tại trước khi trả ra, nên đọc qua nó
    thì D9 không bao giờ bắt được state do bản plugin cũ ghi. Giá trị lạ (chuỗi, thiếu
    hẳn) coi như 0 — báo D9 còn hơn nổ `TypeError` và mất cả báo cáo.
    """
    if not tho:
        return None
    try:
        return int(tho.get("schema_version"))
    except (TypeError, ValueError):
        return 0


def slug_ung_vien(cwd):
    """Slug đoán từ ĐĨA khi state không dùng được: file plan mới nhất, rồi spec, rồi brief.

    Chỉ là gợi ý để user nhận ra request nào đang dở — không bao giờ được ghi vào state.
    """
    for loai in ("plan", "spec", "brief"):
        thu_muc = os.path.join(cwd, "docs", "tdq", loai)
        if not os.path.isdir(thu_muc):
            continue
        ten = [f for f in os.listdir(thu_muc) if f.endswith(".md")]
        if not ten:
            continue
        moi_nhat = max(ten, key=lambda f: os.path.getmtime(os.path.join(thu_muc, f)))
        return moi_nhat[:-3]
    return None


def gom_bang_chung(cwd, state, moc):
    """Mọi thứ đọc được từ ĐĨA, chưa phán xét gì. Đây là đầu vào của bước chấm lệch."""
    tinh_trang_state, tho = doc_state_tho(cwd)
    slug = (state or {}).get("active_request")
    # State hỏng thì không có slug để bám; đoán từ đĩa để user còn nhận ra request nào dở.
    ung_vien = slug_ung_vien(cwd) if not slug else None
    slug_dung = slug or ung_vien
    _log(f"gom bằng chứng cho slug={slug_dung or '—'} tại {cwd} "
         f"(state: {tinh_trang_state})")
    tai_san = {}
    for loai in LOAI_TAI_SAN:
        khai = (state or {}).get(f"{loai}_file") if loai in ("spec", "plan") else None
        rel = khai or (_duong_tai_san(slug_dung, loai) if slug_dung else None)
        tai_san[loai] = _dau_file(cwd, rel)
        tai_san[loai]["khai_trong_state"] = bool(khai)
    tick = _dem_tick(cwd, tai_san["plan"]["rel"])
    bang_chung = {
        "project": cwd,
        "tinh_trang_state": tinh_trang_state,
        "slug_ung_vien": ung_vien,
        "tai_san": tai_san,
        "tick": tick,
        "git": _gom_git(cwd),
        "working_log": _gom_working_log(cwd, moc, slug_dung),
        "state_lac_cho": tdq_state.find_shadow_states(cwd),
        "schema_tren_dia": _schema_tren_dia(tho),
    }
    _log(f"bằng chứng: tick {tick['xong']}/{tick['tong']} · "
         f"git {'có' if bang_chung['git']['co'] else 'không'} · "
         f"state lạc chỗ {len(bang_chung['state_lac_cho'])}")
    return bang_chung


# ---------------------------------------------------------- chấm 11 ca lệch

def _ca(ma, chi_tiet, muc=None, lenh_va=None):
    luat = CA_LECH[ma]
    if muc and muc not in MUC_HOP_LE:
        raise ValueError(f"{ma}: mức {muc!r} ngoài {MUC_HOP_LE}")
    return {"ma": ma, "muc": muc or luat["muc"], "dau_hieu": luat["dau_hieu"],
            "chan_doan": luat["chan_doan"], "chi_tiet": chi_tiet,
            "lenh_va": _lenh(lenh_va) if lenh_va else None}


def _cham_d2(state, bang_chung):
    """Phase khai trong state so với thứ thật sự có trên đĩa."""
    phase = state.get("phase")
    tai_san, tick = bang_chung["tai_san"], bang_chung["tick"]
    if phase == "spec" and not tai_san["spec"]["co"]:
        return _ca("D2", "phase=spec nhưng chưa có file spec trên đĩa — viết tiếp spec",
                   muc="ok")
    if phase == "plan" and not tai_san["plan"]["co"]:
        return _ca("D2", "phase=plan nhưng chưa có file plan trên đĩa — viết tiếp plan",
                   muc="ok")
    if phase == "implement" and tick["co"] and tick["tong"] and tick["xong"] == 0 \
            and not tick["dang_lam"]:
        return _ca("D2", "phase=implement nhưng plan chưa có task nào được tick — "
                         "bắt đầu từ task đầu tiên", muc="ok")
    if phase == "implement" and tick["tong"] and tick["xong"] == tick["tong"]:
        return _ca("D2", f"mọi task ({tick['tong']}/{tick['tong']}) đã `[x]` mà phase vẫn "
                         "là implement", lenh_va="set phase=qc")
    if phase == "qc" and not tai_san["qc"]["co"]:
        return _ca("D2", "phase=qc nhưng chưa có file qc trên đĩa — chạy QC rồi ghi file",
                   muc="ok")
    if phase == "report" and not tai_san["reports"]["co"]:
        return _ca("D2", "phase=report nhưng chưa có file report trên đĩa", muc="ok")
    return None


def _cham_d3(state, bang_chung):
    """sha256 lúc duyệt so với sha256 hiện tại — bắt file bị sửa sau cổng duyệt.

    Spec lệch = `chan`: nội dung đã duyệt không còn, phải xin user duyệt lại.
    Plan lệch chỉ là `ok`: mỗi lần tick một task là plan đổi sha, nên đây là chuyện
    xảy ra hằng ngày. Nâng nó lên `chan` sẽ chặn oan mọi request đang implement.
    """
    ra = []
    for loai in ("spec", "plan"):
        if not state.get(f"{loai}_approved"):
            continue
        da_ghi = state.get(f"{loai}_sha256")
        that = bang_chung["tai_san"][loai]["sha"]
        if not (da_ghi and that) or da_ghi == that:
            continue
        chi_tiet = f"{loai}: sha lúc duyệt {da_ghi[:8]} ≠ trên đĩa {that[:8]}"
        if loai == "plan":
            ra.append(_ca("D3", chi_tiet + " (bình thường nếu chỉ là tick checkbox; "
                                           "soi mắt nếu có task mới hay đổi phạm vi)",
                          muc="ok"))
        else:
            ra.append(_ca("D3", chi_tiet))
    return ra


def _cham_d5(state, bang_chung):
    ra = []
    for loai in ("spec", "plan"):
        dau = bang_chung["tai_san"][loai]
        if state.get(f"{loai}_file") and not dau["co"]:
            ra.append(_ca("D5", f"state khai {loai}_file = {dau['rel']} nhưng file không còn"))
    return ra


def _cham_d6(state):
    ra = []
    for loai in ("spec", "plan", "quick"):
        if not state.get(f"{loai}_approved"):
            continue
        thieu = [k for k in ("_approved_by", "_approved_at") if not state.get(loai + k)]
        if thieu:
            muc_tieu = loai if loai != "quick" else "quick"
            ra.append(_ca("D6", f"{loai}_approved = true nhưng thiếu {', '.join(thieu)}",
                          lenh_va=f"approve {muc_tieu} --by "
                                  "\"CÂU_DUYỆT_NGUYÊN_VĂN_CỦA_USER\""))
    return ra


def _cham_d7(state, bang_chung):
    """Commit mới hơn `updated_at` = dấu vết của agent khác hoặc máy khác."""
    git = bang_chung["git"]
    if not git["co"] or not state.get("updated_at"):
        return None
    try:
        moc = datetime.datetime.fromisoformat(state["updated_at"])
    except ValueError:
        return None
    moi = []
    for c in git["commit"]:
        try:
            luc = datetime.datetime.fromisoformat(c["luc"])
        except ValueError:
            continue
        if luc > moc:
            moi.append(f"{c['sha']} {c['tieu_de']}")
    if not moi:
        return None
    return _ca("D7", f"{len(moi)} commit sau mốc {state['updated_at']}: " + " · ".join(moi))


def cham_ca_lech(cwd, state, bang_chung):
    """Chấm đủ 11 ca theo bảng cứng. Trả list ca ĐANG dính, giữ thứ tự D1→D11."""
    # "Đọc không được" KHÁC "không có". Gộp hai ca lại là cách nhanh nhất làm mất
    # cả request: model yếu thấy "chưa có request" sẽ chạy `init` đè lên spec/plan.
    if bang_chung["tinh_trang_state"] == "hong":
        ung_vien = bang_chung["slug_ung_vien"]
        return [_ca("D1", "`state.json` có trên đĩa nhưng đọc không được (JSON hỏng) — "
                          f"tài sản còn trên đĩa của slug `{ung_vien or '—'}`. "
                          "CẤM chạy `init`: sẽ xoá sạch state và mất dấu request này.",
                    muc="chan")]
    if not state or not state.get("active_request") or state.get("phase") == "idle":
        return [_ca("D1", "state không có request nào đang mở")]

    ra = []
    d2 = _cham_d2(state, bang_chung)
    if d2:
        ra.append(d2)
    ra += _cham_d3(state, bang_chung)

    dang_lam = bang_chung["tick"]["dang_lam"]
    if len(dang_lam) > 1:
        ra.append(_ca("D4", "nhiều task cùng mang `[~]`: " + ", ".join(dang_lam)))

    ra += _cham_d5(state, bang_chung)
    ra += _cham_d6(state)

    d7 = _cham_d7(state, bang_chung)
    if d7:
        ra.append(d7)

    log = bang_chung["working_log"]
    if not log["nhac_slug"]:
        ly_do = "chưa có file log hôm nay" if not log["co"] else "log hôm nay không nhắc slug"
        ra.append(_ca("D8", f"{ly_do} ({log['rel']})"))

    tren_dia = bang_chung["schema_tren_dia"]
    if tren_dia is not None and tren_dia < SCHEMA_HIEN_TAI:
        ra.append(_ca("D9", f"schema_version trên đĩa = {tren_dia} "
                            f"< bản hiện tại {SCHEMA_HIEN_TAI}",
                      lenh_va=f"set schema_version={SCHEMA_HIEN_TAI}"))

    thieu_moc = [k for k in ("started_at", "phase_history") if not state.get(k)]
    if thieu_moc:
        # Chỉ `started_at` mới vá được bằng `set`. `phase_history` rỗng thì không lệnh nào
        # dựng lại lịch sử — báo mức `ok` chứ đừng hứa một lệnh vá không chữa được gì.
        va_duoc = not state.get("started_at")
        ra.append(_ca("D10", "thiếu " + ", ".join(thieu_moc),
                      muc=None if va_duoc else "ok",
                      lenh_va="set started_at=ISO_MỐC_MỞ_REQUEST" if va_duoc else None))

    if bang_chung["state_lac_cho"]:
        ra.append(_ca("D11", "state lạc chỗ: " + ", ".join(bang_chung["state_lac_cho"])))

    _log(f"chấm xong: {len(ra)} ca lệch")
    return ra


def ket_luan(ca_lech):
    """Ba mức kết luận — skill đọc đúng chữ này để rẽ nhánh, đừng đổi chữ."""
    if any(c["muc"] == "chan" for c in ca_lech):
        return CAN_USER
    canh_bao = [c for c in ca_lech if c["muc"] == "canh-bao"]
    if not canh_bao:
        return TIEP_TUC
    if all(c["lenh_va"] for c in canh_bao):
        return VA_ROI_TIEP
    return CAN_USER


def viec_ke_tiep(state, bang_chung, muc_ket_luan, ca_lech=()):
    """Một câu duy nhất trả lời 'gật xong thì làm gì'."""
    if bang_chung.get("tinh_trang_state") == "hong":
        ung_vien = bang_chung.get("slug_ung_vien")
        return ("Trình user: `state.json` hỏng, đĩa còn tài sản của "
                f"`{ung_vien or 'một request chưa rõ'}`. Xin user dựng lại state; "
                "CẤM chạy lệnh khởi tạo.")
    if not state or not state.get("active_request"):
        return "Mở request mới bằng skill tdq-intake."
    if muc_ket_luan == CAN_USER:
        # Gọi đích danh ca đang chặn: câu chung chung "các ca mức chan" sai hẳn khi
        # thứ đẩy sang CẦN USER QUYẾT lại là một cảnh báo không có lệnh vá.
        chan = [c["ma"] for c in ca_lech if c["muc"] == "chan"]
        con_lai = [c["ma"] for c in ca_lech if c["muc"] == "canh-bao" and not c["lenh_va"]]
        ma = chan or con_lai
        return (f"Trình ca {', '.join(ma)} cho user quyết, KHÔNG tự đi tiếp."
                if ma else "Trình bảng ca lệch cho user quyết, KHÔNG tự đi tiếp.")
    phase = state.get("phase")
    dang_lam = bang_chung["tick"]["dang_lam"]
    if phase == "implement" and dang_lam:
        return f"Làm tiếp đúng task {dang_lam[0]} trong plan (task duy nhất mang `[~]`)."
    return f"Chạy tiếp phase `{phase}` theo skill tương ứng."


# ------------------------------------------------------------- báo cáo ra

def bao_cao_markdown(state, bang_chung, ca_lech, muc_ket_luan):
    """Đúng 6 mục, đúng thứ tự. Khuôn người đọc ở references/report-template.md."""
    state = state or {}
    slug = state.get("active_request")
    tick = bang_chung["tick"]
    git = bang_chung["git"]
    out = ["# Check status — request đang dở", ""]

    out += ["## Request", ""]
    if bang_chung.get("tinh_trang_state") == "hong":
        out += ["- `state.json` HỎNG, không đọc được (ca D1 mức `chan`).",
                f"- Slug đoán từ đĩa: `{bang_chung.get('slug_ung_vien') or '—'}`",
                "- Mọi trường dưới đây lấy từ ĐĨA, không lấy từ state.", ""]
    elif not slug:
        out += ["Chưa có request TDQ nào đang chạy (ca D1).", ""]
    else:
        out += [f"- Slug: `{slug}`",
                f"- Lane: {state.get('lane') or '—'} · Phase: `{state.get('phase')}`",
                f"- Mode thực thi: {state.get('implement_mode') or '—'}",
                f"- Mở lúc: {state.get('started_at') or '—'} · "
                f"Ghi lần cuối: {state.get('updated_at') or '—'}", ""]

    out += ["## Bằng chứng trên đĩa", "",
            "| Nguồn | Thấy gì |", "|---|---|"]
    for loai in LOAI_TAI_SAN:
        dau = bang_chung["tai_san"][loai]
        out.append(f"| {loai} | {'có, ' + str(dau['dong']) + ' dòng' if dau['co'] else 'không có'}"
                   f" ({dau['rel'] or '—'}) |")
    out.append(f"| plan tick | {tick['xong']}/{tick['tong']} xong · đang làm: "
               f"{', '.join(tick['dang_lam']) or '—'} |")
    out.append(f"| git | {git['nhanh']} · {len(git['commit'])} commit gần đây · "
               f"{len(git['ban'])} file bẩn{'' if git['co'] else ' — ' + git['ly_do']} |")
    log = bang_chung["working_log"]
    out.append(f"| working log | {log['rel']} · entry cuối: {log['entry_cuoi'] or '—'} · "
               f"{'nhắc slug' if log['nhac_slug'] else 'không nhắc slug'} |")
    out.append("")

    out += ["## Ca lệch phát hiện", ""]
    if not ca_lech:
        out += ["Không ca nào — state khớp đĩa.", ""]
    else:
        out += ["| Mã | Mức | Chi tiết | Chẩn đoán |", "|---|---|---|---|"]
        out += [f"| {c['ma']} | {c['muc']} | {c['chi_tiet']} | {c['chan_doan']} |"
                for c in ca_lech]
        out.append("")

    out += ["## Kết luận", "", f"**{muc_ket_luan}**", ""]

    lenh = [c["lenh_va"] for c in ca_lech if c["lenh_va"]]
    out += ["## Lệnh vá đề xuất", ""]
    if not lenh:
        out += ["Không có lệnh vá nào cần chạy.", ""]
    else:
        out += ["Chạy sau khi user gật ĐÚNG MỘT lần. Chỉ hai họ `set` và `approve`; "
                "không có lệnh nào xoá hay ghi đè dữ liệu cũ.", "", "```bash"]
        out += lenh
        out += ["```", ""]

    out += ["## Việc kế tiếp", "",
            viec_ke_tiep(state, bang_chung, muc_ket_luan, ca_lech), ""]
    return "\n".join(out)


def thu_thap(cwd, moc):
    """Một lượt đọc đĩa → (state, bằng chứng, ca lệch, kết luận)."""
    state = tdq_state.load(cwd, heal=False)
    bang_chung = gom_bang_chung(cwd, state, moc)
    ca_lech = cham_ca_lech(cwd, state, bang_chung)
    return state, bang_chung, ca_lech, ket_luan(ca_lech)


def _json_ra(state, bang_chung, ca_lech, muc_ket_luan):
    state = state or {}
    return {
        "slug": state.get("active_request"),
        "phase": state.get("phase"),
        "lane": state.get("lane"),
        "ket_luan": muc_ket_luan,
        "ca_lech": ca_lech,
        "lenh_va": [c["lenh_va"] for c in ca_lech if c["lenh_va"]],
        "bang_chung": bang_chung,
        "viec_ke_tiep": viec_ke_tiep(state, bang_chung, muc_ket_luan, ca_lech),
    }


# ------------------------------------------------------------------- CLI

def _moc(raw):
    if not raw:
        return datetime.datetime.now().astimezone()
    try:
        return datetime.datetime.fromisoformat(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--now phải là ISO 8601, nhận {raw!r}")


def cli(argv):
    parser = argparse.ArgumentParser(
        prog="tdq_checkstatus.py", description=__doc__.splitlines()[0])
    con = parser.add_subparsers(dest="lenh", required=True)
    rep = con.add_parser("report", help="dò request đang dở và in báo cáo")
    rep.add_argument("--json", action="store_true", dest="ra_json",
                     help="in dữ liệu máy đọc thay vì markdown")
    rep.add_argument("--project", default=None, help="project root (mặc định: tự dò)")
    rep.add_argument("--now", default=None, type=_moc, help="mốc 'hôm nay' dạng ISO 8601")
    args = parser.parse_args(argv)

    cwd = args.project or tdq_state.resolve_project_dir()
    moc = args.now or datetime.datetime.now().astimezone()
    _log(f"check-status: project={cwd}")
    state, bang_chung, ca_lech, muc = thu_thap(cwd, moc)

    if args.ra_json:
        print(json.dumps(_json_ra(state, bang_chung, ca_lech, muc), ensure_ascii=False))
    else:
        print(bao_cao_markdown(state, bang_chung, ca_lech, muc))
    _log(f"kết luận: {muc}")
    return 0


if __name__ == "__main__":
    # argparse tự thoát 2 khi sai cú pháp — đó là hợp đồng ghi ở docstring đầu file.
    sys.exit(cli(sys.argv[1:]))
