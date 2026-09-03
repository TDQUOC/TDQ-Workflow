#!/usr/bin/env python3
"""Rediscover an unfinished TDQ request and report how to continue without losing data.

Principle: **the disk is the evidence, `state.json` is only testimony**. The assets under
`docs/tdq/**`, git and the working log travel with the repo across machines; `state.json`
may be stale, on an old schema, or left behind by another agent. When they disagree, trust the disk.

This script is READ-ONLY. It never writes `state.json` — it only PRINTS the patch commands
it proposes, for the user to approve once before a skill runs them. Every patch command
must belong to exactly the two families `tdq_state.py set …` and `tdq_state.py approve …`.

Usage:
  python3 scripts/tdq_checkstatus.py report
  python3 scripts/tdq_checkstatus.py report --json
  python3 scripts/tdq_checkstatus.py report --project /duong/dan --now 2026-08-16T10:00:00+07:00

Env: TDQ_PROJECT_DIR overrides the project root · TDQ_LOG=0 mutes progress logs on stderr.
Exit: 0 on every state (even when a mismatch is found); 2 on WRONG COMMAND SYNTAX.
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
GIT_LOG_LIMIT = 20                      # cap that keeps `report` under 2.0 seconds
LOAI_TAI_SAN = ("brief", "spec", "plan", "qc", "reports")
MUC_HOP_LE = ("ok", "canh-bao", "chan")   # order = rising severity

# The three verdicts — this exact wording goes into the report and the skill branches on it.
TIEP_TUC = "TIẾP TỤC ĐƯỢC"  # i18n-allow
VA_ROI_TIEP = "VÁ RỒI TIẾP TỤC"  # i18n-allow
CAN_USER = "CẦN USER QUYẾT"  # i18n-allow

# Only these two command families may be produced. Anything else is a way to lose data.
#
# A WHITELIST matching the WHOLE string, not a blacklist. A blacklist used to let through
# `>docs/x.md` (no space), `;mv …`, `&& git checkout --`, `| truncate …` — every one of them
# can erase data. Here: exactly one command, exactly one key=value or one approval target,
# and no shell character. A value holding the word "reset"/"init" is DATA and still passes.
MAU_LENH_VA = re.compile(
    r"^python3 scripts/tdq_state\.py "
    r"(set [a-z_]+=\S+"
    r"|approve (spec|plan|quick)( --by \"[^\"]*\")?)$"
)
KY_TU_SHELL_CAM = ";|&<>$`\\\n\r\t*?(){}[]!"

_TASK = re.compile(r"^\s*-\s*\[( |~|x|>)\]\s*\*\*([A-Za-z][\w.]*)\*\*")

# ------------------------------------------------------- the 11 mismatch cases
#
# A hard table, never a diagnosis the model invents: a weak model meeting a strange state
# would make up a wrong command and lose the spec/plan. The human-readable copy lives in
# skills/tdq-check-status/references/bang-lech.md, and a test locks the two together.
CA_LECH = {
    "D1": {
        "dau_hieu": "không đọc được request nào (không có, phase = idle, hoặc state hỏng)",  # i18n-allow
        "muc": "ok",
        "chan_doan": "Đĩa trống thì mở request mới bằng tdq-intake; đĩa còn spec/plan thì "  # i18n-allow
                     "CẤM chạy `init`, khôi phục state trước.",  # i18n-allow
        "lenh_va": None,
    },
    "D2": {
        "dau_hieu": "phase trong state lệch bằng chứng đĩa",  # i18n-allow
        "muc": "canh-bao",
        "chan_doan": "Phase khai trong state không khớp thứ đã có trên đĩa.",  # i18n-allow
        "lenh_va": "set phase=PHASE_ĐÚNG",  # i18n-allow
    },
    "D3": {
        "dau_hieu": "sha256 của spec lệch với lúc duyệt (plan lệch chỉ là `ok`)",  # i18n-allow
        "muc": "chan",
        "chan_doan": "File đã sửa sau khi duyệt — cần user duyệt lại, cấm tự approve.",  # i18n-allow
        "lenh_va": None,
    },
    "D4": {
        "dau_hieu": "nhiều hơn một task mang dấu `[~]`",  # i18n-allow
        "muc": "canh-bao",
        "chan_doan": "Không xác định được chỗ dừng: chỉ một task được phép `[~]`.",  # i18n-allow
        "lenh_va": None,
    },
    "D5": {
        "dau_hieu": "file đăng ký trong state nhưng mất trên đĩa",  # i18n-allow
        "muc": "chan",
        "chan_doan": "Mất tài sản của request — khôi phục file trước, đừng đi tiếp.",  # i18n-allow
        "lenh_va": None,
    },
    "D6": {
        "dau_hieu": "cờ duyệt bật nhưng thiếu `*_approved_by` hoặc `*_approved_at`",  # i18n-allow
        "muc": "canh-bao",
        "chan_doan": "Không truy được ai duyệt — xin user nhắc lại câu duyệt rồi ghi lại.",  # i18n-allow
        "lenh_va": "approve TARGET --by \"CÂU_DUYỆT_NGUYÊN_VĂN_CỦA_USER\"",  # i18n-allow
    },
    "D7": {
        "dau_hieu": "có commit git mới hơn `updated_at` của state",  # i18n-allow
        "muc": "canh-bao",
        "chan_doan": "Ai đó (agent khác/máy khác) đã làm việc mà state chưa ghi nhận.",  # i18n-allow
        "lenh_va": None,
    },
    "D8": {
        "dau_hieu": "working log hôm nay không nhắc slug đang mở",  # i18n-allow
        "muc": "ok",
        "chan_doan": "Chưa có dòng log nào cho request này hôm nay — bình thường nếu vừa mở.",  # i18n-allow
        "lenh_va": None,
    },
    "D9": {
        "dau_hieu": "`schema_version` cũ hơn bản hiện tại",  # i18n-allow
        "muc": "canh-bao",
        "chan_doan": "State do bản plugin cũ ghi — nâng schema trước khi đọc tiếp.",  # i18n-allow
        "lenh_va": f"set schema_version={SCHEMA_HIEN_TAI}",
    },
    "D10": {
        "dau_hieu": "thiếu `started_at` hoặc `phase_history` rỗng",  # i18n-allow
        "muc": "canh-bao",
        "chan_doan": "Mất mốc thời gian — bảng thời gian của report sẽ sai nếu không vá.",  # i18n-allow
        "lenh_va": "set started_at=ISO_MỐC_MỞ_REQUEST",  # i18n-allow
    },
    "D11": {
        "dau_hieu": "có `state.json` lạc chỗ ngoài project root",  # i18n-allow
        "muc": "chan",
        "chan_doan": "Hai state cùng sống: hook ghi một nơi, model đọc một nơi khác.",  # i18n-allow
        "lenh_va": None,
    },
    # Team mode: `[>]` = handed to a sub-agent. Sitting at `[>]` is not an error —
    # but it answers "where did this stop", so it has to be said out loud.
    "D12": {
        "dau_hieu": "có task mang dấu `[>]`: đã giao agent con mà chưa hợp nhánh về",  # i18n-allow
        "muc": "ok",
        "chan_doan": "Việc còn nằm ở nhánh riêng — dò xung đột rồi hợp về nhánh tích hợp.",  # i18n-allow
        "lenh_va": None,
    },
}


# ------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Progress log on stderr with a timestamp. Muted with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------ patch-command guard

def kiem_lenh_va(lenh):
    """Internal guard: raise ValueError when the command is outside the set/approve families.

    This is the last fence of the no-data-loss rule. Every command PRINTED to the user passes
    through here, so a sloppily written template blows up in the tests, never on the user.
    """
    xau = next((c for c in KY_TU_SHELL_CAM if c in lenh), None)
    if xau:
        raise ValueError(f"the patch command holds the shell character {xau!r}: {lenh!r}")
    if not MAU_LENH_VA.match(lenh):
        raise ValueError(f"the patch command matches no set/approve whitelist entry: {lenh!r}")
    return lenh


def _lenh(phan_con_lai):
    return kiem_lenh_va(f"python3 scripts/tdq_state.py {phan_con_lai}")


# --------------------------------------------------- gather the evidence

def _duong_tai_san(slug, loai):
    return os.path.join("docs", "tdq", loai, f"{slug}.md")


def _dau_file(cwd, rel):
    """One asset on disk: present or not, sha256, line count."""
    if not rel:
        return {"co": False, "rel": None, "sha": None, "dong": 0}
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    if not os.path.isfile(path):
        return {"co": False, "rel": rel, "sha": None, "dong": 0}
    with open(path, encoding="utf-8", errors="replace") as f:
        dong = sum(1 for _ in f)
    # Hash the CONTENT with the very function `tdq_state` uses when recording an approval.
    # A different hash makes case D3 cry wolf on every request, comparing two unlike numbers.
    return {"co": True, "rel": rel, "sha": tdq_state.sha256_noi_dung(path), "dong": dong}


def _dem_tick(cwd, rel):
    """Count the plan checkboxes AND collect the codes of the `[~]` tasks.

    Reuses `tdq_state.plan_tick_state()` for path/sha/total (already there, found with
    `graphify query "plan_tick_state"`). One extra scan is needed because that function
    deliberately returns no task CODE — and the code is what answers "where did this stop".
    """
    goc = tdq_state.plan_tick_state(cwd)
    tick = {"tong": goc["total"], "xong": 0, "dang_lam": [], "da_giao": [],
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
    giao = []
    for dong in dong_file:
        m = _TASK.match(dong)
        if not m:
            continue
        tong += 1
        if m.group(1) == "x":
            xong += 1
        elif m.group(1) == "~":
            dang.append(m.group(2))
        elif m.group(1) == ">":
            giao.append(m.group(2))
    tick.update(tong=tong, xong=xong, dang_lam=dang, da_giao=giao, co=True)
    return tick


def _gom_git(cwd):
    """Branch, recent commits and dirty files. Not a git repo → return the reason, never raise."""
    out = tdq_state._git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    if out is None:
        return {"co": False, "ly_do": "không phải git repo, hoặc chưa có commit nào",  # i18n-allow
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
    """The working log of day `moc`: the last entry mark, and where the slug is mentioned.

    Two flags on purpose: `nhac_slug` scans the whole file (used by case D8, so it does not cry
    wolf when the slug sits in a mid-day entry), while `nhac_slug_entry_cuoi` looks only at the
    last entry, answering "was the most recent work of the day this request".
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
    """Read the state file directly, NOT through `tdq_state.load()`. Returns (status, raw dict).

    Three statuses: `ok` · `khong-co` (no request ever) · `hong` (the file is there but does not
    parse). Telling the last two apart is mandatory: treating a broken state as "no request"
    makes the next step open a new request, and the unfinished one is lost for good.
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
    """`schema_version` EXACTLY as the file holds it, coerced to int.

    `tdq_state.load()` patches this field up to the current version before returning, so reading
    through it means D9 never catches a state written by an old plugin build. A strange value
    (a string, or missing) counts as 0 — reporting D9 beats a `TypeError` losing the report.
    """
    if not tho:
        return None
    try:
        return int(tho.get("schema_version"))
    except (TypeError, ValueError):
        return 0


def slug_ung_vien(cwd):
    """Slug guessed off the DISK when state is unusable: newest plan file, then spec, then brief.

    Only a hint so the user recognises which request is unfinished — never written into state.
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
    """Everything readable off the DISK, with no judgement yet. Input of the scoring step."""
    tinh_trang_state, tho = doc_state_tho(cwd)
    slug = (state or {}).get("active_request")
    # A broken state leaves no slug to hold on to; guess off the disk so the user still knows.
    ung_vien = slug_ung_vien(cwd) if not slug else None
    slug_dung = slug or ung_vien
    _log(f"gathering evidence for slug={slug_dung or '—'} at {cwd} "
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
    _log(f"evidence: ticks {tick['xong']}/{tick['tong']} · "
         f"git {'yes' if bang_chung['git']['co'] else 'no'} · "
         f"stray state files {len(bang_chung['state_lac_cho'])}")
    return bang_chung


# ---------------------------------------------------- score the 11 cases

def _ca(ma, chi_tiet, muc=None, lenh_va=None):
    luat = CA_LECH[ma]
    if muc and muc not in MUC_HOP_LE:
        raise ValueError(f"{ma}: level {muc!r} outside {MUC_HOP_LE}")
    return {"ma": ma, "muc": muc or luat["muc"], "dau_hieu": luat["dau_hieu"],
            "chan_doan": luat["chan_doan"], "chi_tiet": chi_tiet,
            "lenh_va": _lenh(lenh_va) if lenh_va else None}


def _cham_d2(state, bang_chung):
    """The phase state claims, against what the disk actually holds."""
    phase = state.get("phase")
    tai_san, tick = bang_chung["tai_san"], bang_chung["tick"]
    if phase == "spec" and not tai_san["spec"]["co"]:
        return _ca("D2", "phase=spec nhưng chưa có file spec trên đĩa — viết tiếp spec",  # i18n-allow
                   muc="ok")
    if phase == "plan" and not tai_san["plan"]["co"]:
        return _ca("D2", "phase=plan nhưng chưa có file plan trên đĩa — viết tiếp plan",  # i18n-allow
                   muc="ok")
    if phase == "implement" and tick["co"] and tick["tong"] and tick["xong"] == 0 \
            and not tick["dang_lam"]:
        return _ca("D2", "phase=implement nhưng plan chưa có task nào được tick — "  # i18n-allow
                         "bắt đầu từ task đầu tiên", muc="ok")  # i18n-allow
    if phase == "implement" and tick["tong"] and tick["xong"] == tick["tong"]:
        return _ca("D2", f"mọi task ({tick['tong']}/{tick['tong']}) đã `[x]` mà phase vẫn "  # i18n-allow
                         "là implement", lenh_va="set phase=qc")  # i18n-allow
    if phase == "qc" and not tai_san["qc"]["co"]:
        return _ca("D2", "phase=qc nhưng chưa có file qc trên đĩa — chạy QC rồi ghi file",  # i18n-allow
                   muc="ok")
    if phase == "report" and not tai_san["reports"]["co"]:
        return _ca("D2", "phase=report nhưng chưa có file report trên đĩa", muc="ok")  # i18n-allow
    return None


def _cham_d3(state, bang_chung):
    """sha256 at approval vs sha256 now — catches a file edited after the approval gate.

    A spec mismatch is `chan`: the approved content is gone and the user must approve again.
    A plan mismatch is only `ok`: ticking one task changes the plan sha, so it happens every
    day. Raising it to `chan` would falsely block every request in implement.
    """
    ra = []
    for loai in ("spec", "plan"):
        if not state.get(f"{loai}_approved"):
            continue
        da_ghi = state.get(f"{loai}_sha256")
        that = bang_chung["tai_san"][loai]["sha"]
        if not (da_ghi and that) or da_ghi == that:
            continue
        chi_tiet = f"{loai}: sha lúc duyệt {da_ghi[:8]} ≠ trên đĩa {that[:8]}"  # i18n-allow
        if loai == "plan":
            ra.append(_ca("D3", chi_tiet + " (bình thường nếu chỉ là tick checkbox; "  # i18n-allow
                                           "soi mắt nếu có task mới hay đổi phạm vi)",  # i18n-allow
                          muc="ok"))
        else:
            ra.append(_ca("D3", chi_tiet))
    return ra


def _cham_d5(state, bang_chung):
    ra = []
    for loai in ("spec", "plan"):
        dau = bang_chung["tai_san"][loai]
        if state.get(f"{loai}_file") and not dau["co"]:
            ra.append(_ca("D5", f"state khai {loai}_file = {dau['rel']} nhưng file không còn"))  # i18n-allow
    return ra


def _cham_d6(state):
    ra = []
    for loai in ("spec", "plan", "quick"):
        if not state.get(f"{loai}_approved"):
            continue
        thieu = [k for k in ("_approved_by", "_approved_at") if not state.get(loai + k)]
        if thieu:
            muc_tieu = loai if loai != "quick" else "quick"
            ra.append(_ca("D6", f"{loai}_approved = true nhưng thiếu {', '.join(thieu)}",  # i18n-allow
                          lenh_va=f"approve {muc_tieu} --by "
                                  "\"CÂU_DUYỆT_NGUYÊN_VĂN_CỦA_USER\""))  # i18n-allow
    return ra


def _cham_d7(state, bang_chung):
    """A commit newer than `updated_at` = the trace of another agent or another machine."""
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
    return _ca("D7", f"{len(moi)} commit sau mốc {state['updated_at']}: " + " · ".join(moi))  # i18n-allow


def cham_ca_lech(cwd, state, bang_chung):
    """Score all 11 cases off the hard table. Returns the cases hit, in D1→D11 order."""
    # "Cannot be read" is NOT "does not exist". Merging the two is the fastest way to lose a
    # request: a weak model seeing "no request" runs `init` straight over the spec/plan.
    if bang_chung["tinh_trang_state"] == "hong":
        ung_vien = bang_chung["slug_ung_vien"]
        return [_ca("D1", "`state.json` có trên đĩa nhưng đọc không được (JSON hỏng) — "  # i18n-allow
                          f"tài sản còn trên đĩa của slug `{ung_vien or '—'}`. "  # i18n-allow
                          "CẤM chạy `init`: sẽ xoá sạch state và mất dấu request này.",  # i18n-allow
                    muc="chan")]
    if not state or not state.get("active_request") or state.get("phase") == "idle":
        return [_ca("D1", "state không có request nào đang mở")]  # i18n-allow

    ra = []
    d2 = _cham_d2(state, bang_chung)
    if d2:
        ra.append(d2)
    ra += _cham_d3(state, bang_chung)

    dang_lam = bang_chung["tick"]["dang_lam"]
    if len(dang_lam) > 1:
        ra.append(_ca("D4", "nhiều task cùng mang `[~]`: " + ", ".join(dang_lam)))  # i18n-allow

    ra += _cham_d5(state, bang_chung)
    ra += _cham_d6(state)

    d7 = _cham_d7(state, bang_chung)
    if d7:
        ra.append(d7)

    log = bang_chung["working_log"]
    if not log["nhac_slug"]:
        ly_do = "chưa có file log hôm nay" if not log["co"] else "log hôm nay không nhắc slug"  # i18n-allow
        ra.append(_ca("D8", f"{ly_do} ({log['rel']})"))

    tren_dia = bang_chung["schema_tren_dia"]
    if tren_dia is not None and tren_dia < SCHEMA_HIEN_TAI:
        ra.append(_ca("D9", f"schema_version trên đĩa = {tren_dia} "  # i18n-allow
                            f"< bản hiện tại {SCHEMA_HIEN_TAI}",  # i18n-allow
                      lenh_va=f"set schema_version={SCHEMA_HIEN_TAI}"))

    thieu_moc = [k for k in ("started_at", "phase_history") if not state.get(k)]
    if thieu_moc:
        # Only `started_at` is patchable with `set`. An empty `phase_history` cannot be rebuilt by
        # any command — report level `ok` instead of promising a patch that cures nothing.
        va_duoc = not state.get("started_at")
        ra.append(_ca("D10", "thiếu " + ", ".join(thieu_moc),  # i18n-allow
                      muc=None if va_duoc else "ok",
                      lenh_va="set started_at=ISO_MỐC_MỞ_REQUEST" if va_duoc else None))  # i18n-allow

    if bang_chung["state_lac_cho"]:
        ra.append(_ca("D11", "state lạc chỗ: " + ", ".join(bang_chung["state_lac_cho"])))  # i18n-allow

    da_giao = bang_chung["tick"]["da_giao"]
    if da_giao:
        ra.append(_ca("D12", "đã giao agent con, chưa hợp nhánh: " + ", ".join(da_giao)))  # i18n-allow

    _log(f"scored: {len(ra)} mismatch case(s)")
    return ra


def ket_luan(ca_lech):
    """The three verdicts — the skill branches on this exact wording, so never reword it."""
    if any(c["muc"] == "chan" for c in ca_lech):
        return CAN_USER
    canh_bao = [c for c in ca_lech if c["muc"] == "canh-bao"]
    if not canh_bao:
        return TIEP_TUC
    if all(c["lenh_va"] for c in canh_bao):
        return VA_ROI_TIEP
    return CAN_USER


def viec_ke_tiep(state, bang_chung, muc_ket_luan, ca_lech=()):
    """A single sentence answering 'once approved, what do I do'."""
    if bang_chung.get("tinh_trang_state") == "hong":
        ung_vien = bang_chung.get("slug_ung_vien")
        return ("Trình user: `state.json` hỏng, đĩa còn tài sản của "  # i18n-allow
                f"`{ung_vien or 'một request chưa rõ'}`. Xin user dựng lại state; "  # i18n-allow
                "CẤM chạy lệnh khởi tạo.")  # i18n-allow
    if not state or not state.get("active_request"):
        return "Mở request mới bằng skill tdq-intake."  # i18n-allow
    if muc_ket_luan == CAN_USER:
        # Name the blocking case: the generic "the cases at level chan" is plain wrong when the
        # thing pushing it to the user-decision verdict is a warning carrying no patch command.
        chan = [c["ma"] for c in ca_lech if c["muc"] == "chan"]
        con_lai = [c["ma"] for c in ca_lech if c["muc"] == "canh-bao" and not c["lenh_va"]]
        ma = chan or con_lai
        return (f"Trình ca {', '.join(ma)} cho user quyết, KHÔNG tự đi tiếp."  # i18n-allow
                if ma else "Trình bảng ca lệch cho user quyết, KHÔNG tự đi tiếp.")  # i18n-allow
    phase = state.get("phase")
    dang_lam = bang_chung["tick"]["dang_lam"]
    if phase == "implement" and dang_lam:
        return f"Làm tiếp đúng task {dang_lam[0]} trong plan (task duy nhất mang `[~]`)."  # i18n-allow
    da_giao = bang_chung["tick"]["da_giao"]
    if phase == "implement" and da_giao:
        return (f"Task đã giao mà chưa hợp về: {', '.join(da_giao)}. Dò xung đột rồi hợp — "  # i18n-allow
                f"python3 scripts/tdq_team.py check {da_giao[0]} "
                f"&& python3 scripts/tdq_team.py merge {da_giao[0]}.")
    return f"Chạy tiếp phase `{phase}` theo skill tương ứng."  # i18n-allow


# ------------------------------------------------------------- report output

def bao_cao_markdown(state, bang_chung, ca_lech, muc_ket_luan):
    """Exactly 6 sections, in that order. Human-readable template: references/report-template.md."""
    state = state or {}
    slug = state.get("active_request")
    tick = bang_chung["tick"]
    git = bang_chung["git"]
    out = ["# Check status — request đang dở", ""]  # i18n-allow

    out += ["## Request", ""]
    if bang_chung.get("tinh_trang_state") == "hong":
        out += ["- `state.json` HỎNG, không đọc được (ca D1 mức `chan`).",  # i18n-allow
                f"- Slug đoán từ đĩa: `{bang_chung.get('slug_ung_vien') or '—'}`",  # i18n-allow
                "- Mọi trường dưới đây lấy từ ĐĨA, không lấy từ state.", ""]  # i18n-allow
    elif not slug:
        out += ["Chưa có request TDQ nào đang chạy (ca D1).", ""]  # i18n-allow
    else:
        out += [f"- Slug: `{slug}`",
                f"- Lane: {state.get('lane') or '—'} · Phase: `{state.get('phase')}`",
                f"- Mode thực thi: {state.get('implement_mode') or '—'}",  # i18n-allow
                f"- Mở lúc: {state.get('started_at') or '—'} · "  # i18n-allow
                f"Ghi lần cuối: {state.get('updated_at') or '—'}", ""]  # i18n-allow

    out += ["## Bằng chứng trên đĩa", "",  # i18n-allow
            "| Nguồn | Thấy gì |", "|---|---|"]  # i18n-allow
    for loai in LOAI_TAI_SAN:
        dau = bang_chung["tai_san"][loai]
        out.append(f"| {loai} | {'có, ' + str(dau['dong']) + ' dòng' if dau['co'] else 'không có'}"  # i18n-allow
                   f" ({dau['rel'] or '—'}) |")
    out.append(f"| plan tick | {tick['xong']}/{tick['tong']} xong · đang làm: "  # i18n-allow
               f"{', '.join(tick['dang_lam']) or '—'} · đã giao: "  # i18n-allow
               f"{', '.join(tick.get('da_giao') or []) or '—'} |")
    out.append(f"| git | {git['nhanh']} · {len(git['commit'])} commit gần đây · "  # i18n-allow
               f"{len(git['ban'])} file bẩn{'' if git['co'] else ' — ' + git['ly_do']} |")  # i18n-allow
    log = bang_chung["working_log"]
    out.append(f"| working log | {log['rel']} · entry cuối: {log['entry_cuoi'] or '—'} · "  # i18n-allow
               f"{'nhắc slug' if log['nhac_slug'] else 'không nhắc slug'} |")  # i18n-allow
    out.append("")

    out += ["## Ca lệch phát hiện", ""]  # i18n-allow
    if not ca_lech:
        out += ["Không ca nào — state khớp đĩa.", ""]  # i18n-allow
    else:
        out += ["| Mã | Mức | Chi tiết | Chẩn đoán |", "|---|---|---|---|"]  # i18n-allow
        out += [f"| {c['ma']} | {c['muc']} | {c['chi_tiet']} | {c['chan_doan']} |"
                for c in ca_lech]
        out.append("")

    out += ["## Kết luận", "", f"**{muc_ket_luan}**", ""]  # i18n-allow

    lenh = [c["lenh_va"] for c in ca_lech if c["lenh_va"]]
    out += ["## Lệnh vá đề xuất", ""]  # i18n-allow
    if not lenh:
        out += ["Không có lệnh vá nào cần chạy.", ""]  # i18n-allow
    else:
        out += ["Chạy sau khi user gật ĐÚNG MỘT lần. Chỉ hai họ `set` và `approve`; "  # i18n-allow
                "không có lệnh nào xoá hay ghi đè dữ liệu cũ.", "", "```bash"]  # i18n-allow
        out += lenh
        out += ["```", ""]

    out += ["## Việc kế tiếp", "",  # i18n-allow
            viec_ke_tiep(state, bang_chung, muc_ket_luan, ca_lech), ""]
    return "\n".join(out)


def thu_thap(cwd, moc):
    """One pass over the disk → (state, evidence, mismatch cases, verdict)."""
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
        raise argparse.ArgumentTypeError(f"--now must be ISO 8601, got {raw!r}")


def cli(argv):
    parser = argparse.ArgumentParser(
        prog="tdq_checkstatus.py", description=__doc__.splitlines()[0])
    con = parser.add_subparsers(dest="lenh", required=True)
    rep = con.add_parser("report", help="probe the unfinished request and print the report")
    rep.add_argument("--json", action="store_true", dest="ra_json",
                     help="print machine-readable data instead of markdown")
    rep.add_argument("--project", default=None, help="project root (default: auto-detect)")
    rep.add_argument("--now", default=None, type=_moc, help="the 'today' mark, ISO 8601")
    args = parser.parse_args(argv)

    cwd = args.project or tdq_state.resolve_project_dir()
    moc = args.now or datetime.datetime.now().astimezone()
    _log(f"check-status: project={cwd}")
    state, bang_chung, ca_lech, muc = thu_thap(cwd, moc)

    if args.ra_json:
        print(json.dumps(_json_ra(state, bang_chung, ca_lech, muc), ensure_ascii=False))
    else:
        print(bao_cao_markdown(state, bang_chung, ca_lech, muc))
    _log(f"verdict: {muc}")
    return 0


if __name__ == "__main__":
    # argparse exits 2 on bad syntax by itself — the contract stated in the module docstring.
    sys.exit(cli(sys.argv[1:]))
