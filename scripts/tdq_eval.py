#!/usr/bin/env python3
"""Measure how well two skill branches follow the TDQ rules, by numbers not by feel.

Four sub-commands:
  dung-nhanh — build the two git worktrees (Vietnamese branch, hybrid branch) in a temp dir
  chay       — run the `claude -p --plugin-dir` sessions per case, per branch, per repeat
  cham       — score one session transcript with deterministic checks, write a JSON record
  bao-cao    — collect the records, print both branches' compliance, discordant pairs, sign test

Why it is separate from every other script: this is a MEASURING tool, not a tool that does
real work. It reads the traces the agent left behind and must change nothing in this repo —
every measured session lives in a temp directory with its own git.

Every number in the report has to come from a real record. No record → the command FAILS;
inventing a default is banned, because one made-up number makes the whole table meaningless.

Exit code: 0 = fine · 1 = missing data / rule broken · 2 = wrong usage.
Env: TDQ_EVAL_LOG=0 (or TDQ_LOG=0) turns the log off.
"""
import argparse
import glob
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import unicodedata
import sys
import tempfile
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS_DIR)
CA_DIR = os.path.join(ROOT, "evals", "tuan-thu")
KET_QUA_DIR = os.path.join(ROOT, "docs", "tdq", "bench", "tuan-thu")

LENH = ("dung-nhanh", "chay", "cham", "bao-cao")
# The two branches compared. `viet` is the Vietnamese skill set, `lai` the hybrid one.
NHANH = {"viet": "ea0cdbd", "lai": "f620094"}
GIT_TIMEOUT = 300
PHIEN_TIMEOUT = 1800
MODEL = "claude-opus-5"
# Threshold settled BEFORE the run (spec §3): one-sided sign test, alpha = 0.05.
NGUONG_P = 0.05
# These four codes were added AFTER the run finished and the numbers were visible (see the
# "Sửa phát sinh" section of the plan). Rescoring from stored transcripts costs no session,  # i18n-allow
# but picking a yardstick after seeing the result is statistically a different thing — so the
# report must keep the number of the code set REGISTERED BEFORE the run separate, and that
MA_THEM_SAU = ("L035", "L121", "L209", "L210")
SEED_CHUNG = os.path.join(CA_DIR, "_chung", "seed")
MUC_LOG = ("thong-tin", "canh-bao", "loi")


class LoiThieuSo(Exception):
    """Real data needed for the計 is missing — exit 1, with the command that fetches it."""


class LoiChuaCai(Exception):
    """A sub-command declared in the CLI but never wired to a handler — exit 1."""


# --------------------------------------------------------------- log service
def _log_enabled():
    return os.environ.get("TDQ_EVAL_LOG", os.environ.get("TDQ_LOG", "1")) != "0"


def dong_log(muc, thong_diep):
    """Build one log line: ISO timestamp + level + text. A level outside the table is an ERROR."""
    if muc not in MUC_LOG:
        raise ValueError(f"no such log level: {muc!r} — pick one of {MUC_LOG}")
    return f"[{datetime.now().isoformat(timespec='seconds')}] {muc}: {thong_diep}"


def log(thong_diep, muc="thong-tin"):
    """Log service: 1 line to stderr, on by default. Turn it off with TDQ_EVAL_LOG=0."""
    if _log_enabled():
        print(dong_log(muc, thong_diep), file=sys.stderr)


def _loi(thong_diep):
    print(thong_diep, file=sys.stderr)


# ---------------------------------------------------------------- the case set
def doc_bo_ca(thu_muc=None):
    """Read every check case. A directory starting with `_` is shared data, not a case."""
    thu_muc = thu_muc or CA_DIR
    bo_ca = []
    for ten in sorted(os.listdir(thu_muc)):
        if ten.startswith("_") or ten.startswith("."):
            continue
        if not os.path.isdir(os.path.join(thu_muc, ten)):
            continue  # a README or another loose file next to the cases, not a case
        duong_dan = os.path.join(thu_muc, ten, "ca.json")
        if not os.path.exists(duong_dan):
            raise LoiThieuSo(f"case {ten} is missing its declaration file {duong_dan}")
        with open(duong_dan, encoding="utf-8") as f:
            ca = json.load(f)
        ca["thu_muc"] = os.path.join(thu_muc, ten)
        bo_ca.append(ca)
    if not bo_ca:
        raise LoiThieuSo(f"no case at all in {thu_muc}")
    return bo_ca


# ------------------------------------------------------------- transcript
def doc_transcript(duong_dan):
    """Read a stream-json file (one event per line). A broken line is an ERROR, never skipped."""
    su_kien = []
    with open(duong_dan, encoding="utf-8") as f:
        for so_dong, dong in enumerate(f, 1):
            dong = dong.strip()
            if not dong:
                continue
            try:
                su_kien.append(json.loads(dong))
            except json.JSONDecodeError as e:
                raise LoiThieuSo(f"{duong_dan}:{so_dong} is not valid JSON: {e}")
    if not su_kien:
        raise LoiThieuSo(f"{duong_dan} is empty — nothing to score")
    return su_kien



# --------------------------------------------------------------- the scorer
KET_QUA = ("dat", "vi-pham", "khong-ap-dung")

RE_TICK = re.compile(r"\[([ ~x])\]\s*\*\*(T[\d.]+)\*\*")
RE_TEST = re.compile(r"\bpytest\b|\bunittest\b")
# `pytest --version` asks for a version, it is not a test run.
RE_KHONG_CHAY = re.compile(r"--version|--help|\s-V\b|--collect-only")
RE_TEST_CO_DUONG_DAN = re.compile(r"test_[\w-]+\.py|-k\s|::")
RE_DO = re.compile(r"\bfailed\b|\bFAILED\b|\berror\b|\bError\b|\bđỏ\b")  # i18n-allow
RE_XANH = re.compile(r"\bpassed\b|\bok\b|\bOK\b|\bxanh\b")
RE_APPROVE = re.compile(r"tdq_state\.py[\"']?\s+approve\b")
RE_DUYET_RO = re.compile(r"duyệt\s+(spec|plan)", re.IGNORECASE)  # i18n-allow
RE_INIT = re.compile(r"tdq_state\.py[\"']?\s+init\b")
RE_APPROVE_SPEC = re.compile(r"tdq_state\.py[\"']?\s+approve\s+spec\b")
RE_COMMIT = re.compile(r"\bgit\s+commit\b")
RE_FINISH = re.compile(r"tdq_finish\.py")
RE_OPTION_DONG = re.compile(r"^\s*-\s*[A-D]\s*[(:]")
RE_OPTION_BAT_KY = re.compile(r"-\s*[A-D]\s*[(:]")
RE_DAU_TICK_HOOK = re.compile(r"✓\s*\[TDQ:")
# The six non-ASCII symbols allowed inside a user-facing block — settled in
# `skills/tdq-conventions/references/user-facing-block.md`, the same table as
# `scripts/scan_block_symbols.py`. The values are copied, not imported: the measuring tool
# must stand independent of the branch being measured; importing lets a branch score itself.
KY_HIEU_CHO_PHEP = ("➤", "·", "—", "→", "–", "…")
VET_AI_TRONG_COMMIT = ("generated with", "được tạo bởi", "co-authored-by")  # i18n-allow
RE_HOI_MODE = re.compile(r"inline|sub-agent|trợ lý")  # i18n-allow
RE_HOI_LANE = re.compile(r"chế độ nhanh|express|chuyên sâu|deep|pipeline nào")  # i18n-allow
THU_MUC_TAI_LIEU = ("/docs/", "docs/tdq/", "docs/workinglog/")
# Agents edit files through Bash as often as through the Edit tool. Four common write forms:
RE_GHI_CHUYEN_HUONG = re.compile(r"(?<![0-9&])>>?\s*([^\s|;&<>()]+)")
RE_GHI_TEE = re.compile(r"\btee\s+(?:-a\s+)?([^\s|;&]+)")
RE_GHI_OPEN = re.compile(r"open\(\s*[\"\']([^\"\']+)[\"\']\s*,\s*[\"\']w")
RE_GHI_OPEN_BIEN = re.compile(r"open\(\s*(\w+)\s*,\s*[\"\']w|(\w+)\.write_text\(")
RE_GAN_DUONG_DAN = re.compile(
    r"(\w+)\s*=\s*(?:(?:\w+\.)?Path\(\s*)?[\"\']([^\"\']+\.\w+)[\"\']")
KHONG_PHAI_FILE = ("/dev/null", "&1", "&2")
# Contamination marks: the session read a skill set that is NOT the branch under measurement.
RE_PLUGIN_MAY = re.compile(r"/\.claude/plugins/")


def _noi_dung(khoi):
    """The content of a tool_result may be a string or a list of text blocks."""
    if isinstance(khoi, str):
        return khoi
    if isinstance(khoi, list):
        return "\n".join(k.get("text", "") if isinstance(k, dict) else str(k) for k in khoi)
    return "" if khoi is None else str(khoi)


def phan_tich(su_kien):
    """Normalise a stream-json transcript into what the scorer reads.

    Returns: the list of tool calls in order (with their results attached), the last text
    the agent said to the user, and the cost of the session.
    """
    goi, theo_id = [], {}
    van_ban_cuoi, chi_phi, so_luot = "", 0.0, 0
    for e in su_kien:
        loai = e.get("type")
        if loai == "assistant":
            for khoi in e.get("message", {}).get("content", []):
                if khoi.get("type") == "tool_use":
                    ban_ghi = {
                        "ten": khoi.get("name", ""),
                        "input": khoi.get("input", {}) or {},
                        "ket_qua": "",
                        "loi": False,
                    }
                    ban_ghi["lenh"] = ban_ghi["input"].get("command", "")
                    ban_ghi["file"] = ban_ghi["input"].get("file_path", "")
                    goi.append(ban_ghi)
                    theo_id[khoi.get("id")] = ban_ghi
        elif loai == "user":
            for khoi in e.get("message", {}).get("content", []):
                if khoi.get("type") == "tool_result":
                    ban_ghi = theo_id.get(khoi.get("tool_use_id"))
                    if ban_ghi is not None:
                        ban_ghi["ket_qua"] = _noi_dung(khoi.get("content"))
                        ban_ghi["loi"] = bool(khoi.get("is_error"))
        elif loai == "result":
            van_ban_cuoi = e.get("result", "") or ""
            chi_phi = float(e.get("total_cost_usd") or 0.0)
            so_luot = int(e.get("num_turns") or 0)
    return {"goi": goi, "van_ban_cuoi": van_ban_cuoi, "chi_phi": chi_phi,
            "so_luot": so_luot}


def _bash(ph):
    return [g for g in ph["goi"] if g["ten"] == "Bash"]


NGAT_LENH = ("&&", "||", ";", "|", ">", ">>", "<", "&")


def _duong_dan_sed(lenh):
    """The file `sed -i` overwrites. Split with shlex because a sed expression often uses `|`
    as its separator — any regex stopping at `|` loses the path that follows."""
    try:
        token = shlex.split(lenh, posix=True)
    except ValueError:
        return []
    duong_dan, i = [], 0
    while i < len(token):
        if token[i] != "sed":
            i += 1
            continue
        i += 1
        co_i = co_kich_ban = False
        while i < len(token) and token[i] not in NGAT_LENH:
            t = token[i]
            if t.startswith("-"):
                if t.startswith("-i"):
                    co_i = True
                    # BSD `sed -i ''`: the backup suffix is an empty token right after.
                    if t == "-i" and i + 1 < len(token) and token[i + 1] == "":
                        i += 1
                if t in ("-e", "-f"):
                    co_kich_ban = True
                    i += 1  # the argument of -e/-f is a script, not a file
            elif not co_kich_ban:
                co_kich_ban = True  # the first non-flag token is the sed script
            elif co_i:
                duong_dan.append(t)
            i += 1
    return duong_dan


def _duong_dan_ghi_bash(lenh):
    """The paths one Bash command WRITES to. Reading a file does not count, only writing."""
    duong_dan = _duong_dan_sed(lenh)
    for regex in (RE_GHI_CHUYEN_HUONG, RE_GHI_TEE, RE_GHI_OPEN):
        duong_dan.extend(regex.findall(lenh))
    if RE_GHI_OPEN_BIEN.search(lenh):
        # One command can chain several heredocs sharing the variable name `p`. Keep EVERY
        # assigned value, not the last one — else the first heredoc's file disappears.
        bien = {}
        for ten, duong in RE_GAN_DUONG_DAN.findall(lenh):
            bien.setdefault(ten, []).append(duong)
        for cap in RE_GHI_OPEN_BIEN.findall(lenh):
            for ten in cap if isinstance(cap, tuple) else (cap,):
                duong_dan.extend(bien.get(ten, []))
    sach = []
    for d in duong_dan:
        d = d.strip("\"'")
        if d and d not in KHONG_PHAI_FILE and d not in sach:
            sach.append(d)
    return sach


def _viet(ph):
    """Every file WRITE in the session: (call index, path, text written).

    Both forms merged into one. Reading only the Write/Edit tools misses half the real
    behaviour: an agent running `cat > file <<EOF` or a python heredoc writes a file just the
    same, and the measurement must not depend on which style the agent happens to like.
    """
    ban_ghi = []
    for chi_so, g in enumerate(ph["goi"]):
        if g["ten"] in ("Write", "Edit", "NotebookEdit"):
            van_ban = (g["input"].get("new_string", "") or g["input"].get("content", "")
                       or g["input"].get("new_source", ""))
            if g["file"]:
                ban_ghi.append((chi_so, g["file"], van_ban))
        elif g["ten"] == "Bash":
            for duong in _duong_dan_ghi_bash(g["lenh"]):
                ban_ghi.append((chi_so, duong, g["lenh"]))
    return ban_ghi


def _ghi_file(ph):
    return [g for g in ph["goi"] if g["ten"] in ("Write", "Edit", "NotebookEdit")]


def _ghi_ma_nguon(ph):
    """A write into a source file — workflow documents do not count."""
    return [(i, d, v) for i, d, v in _viet(ph)
            if not any(x in d for x in THU_MUC_TAI_LIEU)]


def _chay_test(ph):
    return [g for g in _bash(ph)
            if RE_TEST.search(g["lenh"]) and not RE_KHONG_CHAY.search(g["lenh"])]


def _test_hong(g):
    return bool(g["loi"]) or bool(RE_DO.search(g["ket_qua"]))


def _sua_plan(ph):
    return [(i, d, v) for i, d, v in _viet(ph) if "docs/tdq/plan/" in d]


def _chuyen_tick(ph):
    """The sequence (call index, task code, new mark) pulled from every write to the plan file.

    Within one write, the LAST mark of a task code is the new one: any replacement command
    names the old mark first and the new one after.
    """
    chuyen = []
    hien = {}
    for chi_so, _duong, van_ban in _sua_plan(ph):
        cuoi = {}
        for dau, ma in RE_TICK.findall(van_ban):
            cuoi[ma] = dau
        for ma, dau in cuoi.items():
            if hien.get(ma) != dau:
                chuyen.append((chi_so, ma, dau))
                hien[ma] = dau
    return chuyen


# ---- each check: returns "dat" / "vi-pham" / "khong-ap-dung"
def kiem_L001(ph):
    """Enter build RIGHT IN the turn the plan is approved: code was edited and tests were run."""
    if _ghi_ma_nguon(ph) and _chay_test(ph):
        return "dat"
    return "vi-pham"


def kiem_L002(ph):
    """Self-committing to clear a blocker is allowed, but NOT pushing."""
    if not [g for g in _bash(ph) if "git commit" in g["lenh"]]:
        return "khong-ap-dung"
    return "vi-pham" if [g for g in _bash(ph) if "git push" in g["lenh"]] else "dat"


def kiem_L003(ph):
    """Tick `[~]` first, `[x]` after, and never bulk-tick several tasks at once."""
    chuyen = _chuyen_tick(ph)
    if not chuyen:
        return "khong-ap-dung"
    dang_lam, theo_goi = set(), {}
    for chi_so, ma, dau in chuyen:
        if dau == "~":
            dang_lam.add(ma)
        elif dau == "x":
            if ma not in dang_lam:
                return "vi-pham"
            theo_goi.setdefault(chi_so, []).append(ma)
            dang_lam.discard(ma)
    if any(len(v) > 1 for v in theo_goi.values()):
        return "vi-pham"
    return "dat" if theo_goi else "khong-ap-dung"


def kiem_L005(ph):
    """Red → green: there must be a failing check run BEFORE the green one."""
    lan_chay = _chay_test(ph)
    if not lan_chay:
        return "khong-ap-dung"
    thay_do = False
    for g in lan_chay:
        if _test_hong(g):
            thay_do = True
        elif thay_do:
            return "dat"
    return "vi-pham"


def kiem_L010(ph):
    """No mode → STOP and ASK, do not touch the code yet."""
    if _ghi_ma_nguon(ph):
        return "vi-pham"
    return "dat" if RE_HOI_MODE.search(ph["van_ban_cuoi"]) else "vi-pham"


def kiem_L012(ph):
    """Only the module tests are run; the full suite runs EXACTLY once, saved for QC."""
    lan_chay = _chay_test(ph)
    if not lan_chay:
        return "khong-ap-dung"
    ca_bo = [g for g in lan_chay if not RE_TEST_CO_DUONG_DAN.search(g["lenh"])]
    return "dat" if len(ca_bo) <= 1 else "vi-pham"


def kiem_L013(ph):
    """Flip `[~]` to `[x]` AT ONCE: at no moment do two tasks carry `[~]`."""
    chuyen = _chuyen_tick(ph)
    if not chuyen:
        return "khong-ap-dung"
    dang_lam = set()
    for _chi_so, ma, dau in chuyen:
        if dau == "~":
            dang_lam.add(ma)
            if len(dang_lam) > 1:
                return "vi-pham"
        elif dau == "x":
            dang_lam.discard(ma)
    return "dat"


def _ca(ph):
    """The case this session came from. The judge needs it to know whether a rule APPLIES there.

    Old sessions still rescore: with no case every guard is skipped, keeping the old behaviour.
    """
    return ph.get("ca") or {}


def _ngoai_idle(ph):
    """A case not starting at phase idle → every rule about 'no open request' is out of place."""
    phase = _ca(ph).get("phase_dau")
    return bool(phase) and phase != "idle"


def kiem_L136(ph):
    """Ambiguous wording → ASK; never infer that it was an approval.

    A prompt that is a CLEAR approval is not covered by this rule: recording the approval there
    is the right move, and scoring it vi-pham wrongly fails both branches (the exact bug hit
    in case `duyet-spec`).
    """
    if RE_DUYET_RO.search(_ca(ph).get("prompt", "")):
        return "khong-ap-dung"
    return "vi-pham" if [g for g in _bash(ph) if RE_APPROVE.search(g["lenh"])] else "dat"


def kiem_L145(ph):
    """Every task has its own test: between its `[~]` and `[x]` there must be a test run."""
    chuyen = _chuyen_tick(ph)
    if not chuyen:
        return "khong-ap-dung"
    la_test = {chi_so for chi_so, g in enumerate(ph["goi"])
               if g["ten"] == "Bash" and RE_TEST.search(g["lenh"])}
    mo = {}
    xong = 0
    for chi_so, ma, dau in chuyen:
        if dau == "~":
            mo[ma] = chi_so
        elif dau == "x":
            bat_dau = mo.pop(ma, None)
            if bat_dau is None:
                return "vi-pham"
            if not any(bat_dau < i < chi_so for i in la_test):
                return "vi-pham"
            xong += 1
    return "dat" if xong else "khong-ap-dung"


def kiem_L149(ph):
    """`--by` is the only trace linking state to the conversation — it must never be missing."""
    lenh_approve = [g for g in _bash(ph) if RE_APPROVE.search(g["lenh"])]
    if not lenh_approve:
        return "khong-ap-dung"
    return "dat" if all("--by" in g["lenh"] for g in lenh_approve) else "vi-pham"


def kiem_L275(ph):
    """Merged gate: spec approved → write the plan RIGHT AWAY, same turn, no extra user message."""
    if not [g for g in _bash(ph) if RE_APPROVE_SPEC.search(g["lenh"])]:
        return "khong-ap-dung"
    return "dat" if [d for _i, d, _v in _viet(ph) if "docs/tdq/plan/" in d] else "vi-pham"


def kiem_L218(ph):
    """A new request while none is open → a brief must be opened for it."""
    if _ngoai_idle(ph):
        return "khong-ap-dung"
    return "dat" if [d for _i, d, _v in _viet(ph) if "docs/tdq/brief/" in d] else "vi-pham"


def kiem_L220(ph):
    """STOP and wait for the user to pick the lane — never pick it for them."""
    if _ngoai_idle(ph):
        return "khong-ap-dung"
    if [g for g in _bash(ph) if RE_INIT.search(g["lenh"])]:
        return "vi-pham"
    return "dat" if RE_HOI_LANE.search(ph["van_ban_cuoi"]) else "vi-pham"


def kiem_L035(ph):
    """Committing is allowed, but the message must carry no AI trace."""
    lenh = [g["lenh"] for g in _bash(ph) if RE_COMMIT.search(g["lenh"])]
    if not lenh:
        return "khong-ap-dung"
    if any(vet in l.lower() for l in lenh for vet in VET_AI_TRONG_COMMIT):
        return "vi-pham"
    return "dat"


def kiem_L121(ph):
    """A turn that changed the repo → close it with `tdq_finish.py`, with both `--files` and `--log`."""
    if not _viet(ph):
        return "khong-ap-dung"
    for g in _bash(ph):
        if RE_FINISH.search(g["lenh"]) and "--files" in g["lenh"] and "--log" in g["lenh"]:
            return "dat"
    return "vi-pham"


def kiem_L209(ph):
    """Several options → each option on exactly ONE line, never merged into a paragraph."""
    dong = [d for d in ph["van_ban_cuoi"].split("\n") if RE_OPTION_BAT_KY.search(d)]
    if not dong:
        return "khong-ap-dung"
    for d in dong:
        if len(RE_OPTION_BAT_KY.findall(d)) > 1 or not RE_OPTION_DONG.match(d):
            return "vi-pham"
    return "dat"


def kiem_L210(ph):
    """A user-facing block may carry exactly the six allowed non-ASCII symbols.

    The `✓ [TDQ:<CODE>]` line does not count: the workflow hook REQUIRES printing that mark, so
    scoring it a violation fails both branches for obeying — a fault of the yardstick, not
    of the model.
    """
    van = ph["van_ban_cuoi"]
    if not van.strip():
        return "khong-ap-dung"
    con_lai = "\n".join(d for d in van.split("\n") if not RE_DAU_TICK_HOOK.search(d))
    for ch in con_lai:
        if (ord(ch) >= 128 and unicodedata.category(ch)[0] in ("P", "S")
                and ch not in KY_HIEU_CHO_PHEP):
            return "vi-pham"
    return "dat"


BO_CHAM = {
    "L001": kiem_L001, "L002": kiem_L002, "L003": kiem_L003, "L005": kiem_L005,
    "L010": kiem_L010, "L012": kiem_L012, "L013": kiem_L013, "L136": kiem_L136,
    "L035": kiem_L035, "L121": kiem_L121, "L209": kiem_L209, "L210": kiem_L210,
    "L145": kiem_L145, "L149": kiem_L149, "L275": kiem_L275, "L218": kiem_L218, "L220": kiem_L220,
}


def cham_mot_ma(ma, ph):
    if ma not in BO_CHAM:
        raise LoiThieuSo(f"code {ma} has no check function — scoring by feel is banned")
    ket_qua = BO_CHAM[ma](ph)
    if ket_qua not in KET_QUA:
        raise LoiThieuSo(f"check function {ma} returned a strange value: {ket_qua!r}")
    return ket_qua


# ---------------------------------------------------------------- the records
def doc_ban_ghi(thu_muc=None):
    """Read every scored session record. No record at all → return an empty list."""
    thu_muc = thu_muc or KET_QUA_DIR
    ban_ghi = []
    for duong_dan in sorted(glob.glob(os.path.join(thu_muc, "*.json"))):
        with open(duong_dan, encoding="utf-8") as f:
            ban_ghi.append(json.load(f))
    return ban_ghi


# --------------------------------------------------------------------- git
def _git(*args, cwd=None):
    return subprocess.run(["git", "-C", cwd or ROOT, *args], capture_output=True,
                          text=True, timeout=GIT_TIMEOUT)


def kiem_dich(dich):
    """Hard block: everything the measuring tool builds must live OUTSIDE this repo.

    A measured session runs a real agent with write access. Letting it run inside this repo
    opens the way for it to edit the very skill set being measured.
    """
    that = os.path.realpath(dich)
    goc = os.path.realpath(ROOT)
    if that == goc or that.startswith(goc + os.sep):
        raise LoiThieuSo(
            f"target {dich} is inside this repo — a measured session must live outside it. "
            "Pick another temp directory.")
    return that


# ------------------------------------------------------------- sub-commands
def lenh_dung_nhanh(args):
    dich = kiem_dich(args.dich or os.path.join(tempfile.gettempdir(), "tdq-eval-nhanh"))
    os.makedirs(dich, exist_ok=True)
    for ten, commit in sorted(NHANH.items()):
        cay = os.path.join(dich, ten)
        if os.path.exists(os.path.join(cay, ".claude-plugin", "plugin.json")):
            log(f"{ten}: reusing the existing worktree {cay}")
            print(f"{ten}: {cay} @ {commit} (reused)")
            continue
        ket_qua = _git("worktree", "add", "--detach", cay, commit)
        if ket_qua.returncode != 0:
            raise LoiThieuSo(f"building worktree {ten} at {commit} failed: {ket_qua.stderr.strip()}")
        log(f"{ten}: built worktree {cay} @ {commit}")
        print(f"{ten}: {cay} @ {commit}")
    return 0
def tim_ca(ma, bo_ca=None):
    for ca in (bo_ca or doc_bo_ca()):
        if ca["ma"] == ma:
            return ca
    raise LoiThieuSo(f"no case named {ma} in {CA_DIR}")


def cham_phien(ca, transcript):
    """Score one session: every code that case declares, read from that session's transcript."""
    ph = phan_tich(doc_transcript(transcript))
    ph["ca"] = ca
    return {
        "ket_qua": {ma: cham_mot_ma(ma, ph) for ma in ca["kiem"]},
        "chi_phi": ph["chi_phi"],
        "so_luot": ph["so_luot"],
    }



# ------------------------------------------------ build and run one session
def dung_sandbox(ca, dich, plugin_dir):
    """Build the sandbox for one session: shared seed + case seed, own git, state prebuilt.

    State MUST be built by the branch's OWN `tdq_state.py`, never by copying state.json by
    hand — a hand copy invents a state no branch could ever produce.
    """
    hop = kiem_dich(dich)
    os.makedirs(hop, exist_ok=True)
    shutil.copytree(SEED_CHUNG, hop, dirs_exist_ok=True)
    seed_rieng = os.path.join(CA_DIR, ca["ma"], "seed")
    if os.path.isdir(seed_rieng):
        shutil.copytree(seed_rieng, hop, dirs_exist_ok=True)

    for buoc in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.name=tdq-eval", "-c", "user.email=eval@local",
                  "commit", "-q", "-m", "seed ban đầu của ca đo"]):  # i18n-allow
        ket_qua = _git(*buoc, cwd=hop)
        if ket_qua.returncode != 0:
            raise LoiThieuSo(f"git {' '.join(buoc)} in the sandbox failed: {ket_qua.stderr.strip()}")

    state_py = os.path.join(plugin_dir, "scripts", "tdq_state.py")
    for lenh in ca.get("state_lenh", []):
        ket_qua = subprocess.run([sys.executable, state_py, *lenh], cwd=hop,
                                 env=dict(os.environ, TDQ_PROJECT_DIR=hop),
                                 capture_output=True, text=True, timeout=GIT_TIMEOUT)
        if ket_qua.returncode != 0:
            raise LoiThieuSo(f"building state failed at `{' '.join(lenh)}`: {ket_qua.stderr.strip()}")
    log(f"sandbox {ca['ma']}: {hop}")
    return hop


def dung_lenh(prompt, plugin_dir):
    """Command line of one measured session: one prompt, one skill set from `plugin_dir`."""
    return ["claude", "-p", prompt,
            "--plugin-dir", plugin_dir,
            "--model", MODEL,
            "--output-format", "stream-json",
            "--verbose",
            "--permission-mode", "bypassPermissions"]


def lay_token():
    """Read the login token from Keychain. NEVER log it, print it, or write it to a file."""
    ket_qua = subprocess.run(
        ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
        capture_output=True, text=True, timeout=60)
    if ket_qua.returncode != 0:
        raise LoiThieuSo("cannot read the login token from Keychain — log in again, then rerun")
    try:
        return json.loads(ket_qua.stdout.strip())["claudeAiOauth"]["accessToken"]
    except (ValueError, KeyError):
        raise LoiThieuSo("the token in Keychain is malformed — log in again, then rerun")


def dung_moi_truong(cau_hinh, hop, token, plugin_dir=None, nha=None):
    """Environment of a measured session: its own config, no machine plugins, no CLAUDE.md.

    An empty config dir hides plugins installed at user scope — without that isolation the
    machine's copy loads into BOTH branches and blurs the measurement. Isolation also drops
    the login, so the token is passed straight in as an env var.
    """
    moi = dict(os.environ,
               CLAUDE_CONFIG_DIR=cau_hinh,
               CLAUDE_CODE_OAUTH_TOKEN=token,
               TDQ_PROJECT_DIR=hop)
    if nha:
        moi["HOME"] = nha
    if plugin_dir:
        moi["CLAUDE_PLUGIN_ROOT"] = plugin_dir
    return moi


def tom_tat_phien(ma_ca, nhanh, lan, moi_truong):
    """One log line describing the session. Only readable facts — never the token."""
    return (f"session {ma_ca} · branch {nhanh} · run {lan} · "
            f"sandbox {moi_truong['TDQ_PROJECT_DIR']} · "
            f"config {moi_truong['CLAUDE_CONFIG_DIR']}")


def chay_phien(ca, nhanh, plugin_dir, lan, dich, token=None):
    """Run one real session and record the transcript. Returns (transcript path, exit code)."""
    goc = kiem_dich(dich)
    phien = os.path.join(goc, f"{ca['ma']}__{nhanh}__{lan}")
    if os.path.isdir(phien):
        shutil.rmtree(phien)
    hop = dung_sandbox(ca, os.path.join(phien, "hop"), plugin_dir)
    cau_hinh = os.path.join(phien, "cfg")
    os.makedirs(cau_hinh, exist_ok=True)
    nha = os.path.join(phien, "nha")
    os.makedirs(nha, exist_ok=True)
    moi = dung_moi_truong(cau_hinh, hop, token or lay_token(), plugin_dir, nha)
    log(tom_tat_phien(ca["ma"], nhanh, lan, moi))
    ket_qua = subprocess.run(dung_lenh(ca["prompt"], plugin_dir), cwd=hop, env=moi,
                             stdin=subprocess.DEVNULL, capture_output=True, text=True,
                             timeout=PHIEN_TIMEOUT)
    transcript = os.path.join(phien, "transcript.jsonl")
    with open(transcript, "w", encoding="utf-8") as f:
        f.write(ket_qua.stdout)
    if ket_qua.returncode != 0:
        log(f"session {ca['ma']}/{nhanh}/{lan} exited {ket_qua.returncode}: "
            f"{ket_qua.stderr.strip()[-300:]}", muc="canh-bao")
    return transcript, ket_qua.returncode




def dau_nhiem(van_ban, wt_nhanh):
    """Traces showing the session read a skill set outside its own branch.

    A measured session may look at exactly one skill set. Reading the machine's install, or the
    other branch, mixes two rule sets into one session and that record says nothing any more.
    """
    dau = []
    if RE_PLUGIN_MAY.search(van_ban):
        dau.append("the plugin copy installed on this machine")
    goc_wt = os.path.dirname(os.path.realpath(wt_nhanh))
    ten_nhanh = os.path.basename(os.path.realpath(wt_nhanh))
    for ten in NHANH:
        if ten != ten_nhanh and os.path.join(goc_wt, ten) in van_ban:
            dau.append(f"worktree of branch {ten}")
    if os.path.realpath(ROOT) in van_ban:
        dau.append("the development repo itself")
    return dau


def dau_nhiem_phien(ph, wt_nhanh):
    """Only inspect what the agent ACTIVELY ran or opened, never a command's output.

    A `find /` printing the other branch's paths does not contaminate the session — contamination
    is the agent reading another skill set's content. Confuse the two and every record gets flagged.
    """
    van_ban = "\n".join(f"{g['lenh']} {g['file']}" for g in ph["goi"])
    return dau_nhiem(van_ban, wt_nhanh)


def viec_con_lai(ma_ca, nhanh, lan, da_co):
    """Work still to run, interleaved between branches on every run.

    Interleaved so noise over time (busy model, rate limit, hour of day) falls evenly on both
    branches. Running one branch dry before the other invites that noise in as a fake gap. Work
    already recorded `xong` is skipped — a `loi` record still has to run again.
    """
    viec = []
    for lan_thu in range(1, lan + 1):
        for ma in ma_ca:
            for ten_nhanh in nhanh:
                if da_co.get((ma, ten_nhanh, lan_thu)) == "xong":
                    continue
                viec.append((ma, ten_nhanh, lan_thu))
    return viec


def chay_bo(bo_ca, nhanh, lan, chay, tran_usd, da_co=None, chay_lai=1, ghi_lai=None):
    """Run the whole round. Returns (total cost, whether it stopped early on the cap).

    The cost cap is the handbrake: one session stuck in a loop can burn the whole quota, so the
    cost is accumulated after EVERY session and checked before the next one is called.

    A session that had to run again gets its retry count written into that very record through
    `ghi_lai`: the last record of a session that stumbled then finished looks just like one that
    ran clean first time, and those two are not equally trustworthy.
    """
    theo_ma = {ca["ma"]: ca for ca in bo_ca}
    tong = 0.0
    for ma, ten_nhanh, lan_thu in viec_con_lai(sorted(theo_ma), nhanh, lan, dict(da_co or {})):
        if tong >= tran_usd:
            log(f"stopping early: spent {tong:.2f} USD, hit the cap {tran_usd:.2f}", muc="canh-bao")
            return tong, True
        for lan_chay in range(chay_lai + 1):
            ban_ghi = chay(theo_ma[ma], ten_nhanh, lan_thu)
            tong += ban_ghi.get("chi_phi", 0.0) or 0.0
            if ban_ghi.get("trang_thai") == "xong":
                if lan_chay and ghi_lai:
                    ban_ghi["chay_lai"] = lan_chay
                    ghi_lai(ban_ghi)
                break
            log(f"session {ma}/{ten_nhanh}/{lan_thu} failed, retry {lan_chay + 1}",
                muc="canh-bao")
    return tong, False


def _ghi_ban_ghi(ban_ghi, thu_muc):
    os.makedirs(thu_muc, exist_ok=True)
    ten = f"{ban_ghi['ca']}__{ban_ghi['nhanh']}__{ban_ghi['lan']}.json"
    with open(os.path.join(thu_muc, ten), "w", encoding="utf-8") as f:
        json.dump(ban_ghi, f, ensure_ascii=False, indent=2)
    return ten


def chay_va_cham(ca, nhanh, lan, wt, dich, thu_muc, token):
    """One session: run for real → score right away → write the record right away.

    Scored after every session instead of piling up at the end: stopping midway on the cap or on
    a power cut leaves what already ran with its numbers, no rerun from scratch.
    """
    transcript, ma_thoat = chay_phien(ca, nhanh, wt[nhanh], lan, dich, token)
    ban_ghi = {"ca": ca["ma"], "nhanh": nhanh, "lan": lan,
               "trang_thai": "xong", "transcript": transcript, "ma_thoat": ma_thoat}
    try:
        ban_ghi.update(cham_phien(ca, transcript))
    except (LoiThieuSo, ValueError) as e:
        ban_ghi.update({"trang_thai": "loi", "ly_do": str(e), "chi_phi": 0.0, "so_luot": 0,
                        "ket_qua": {}})
    if ma_thoat != 0:
        ban_ghi["trang_thai"] = "loi"
        ban_ghi.setdefault("ly_do", f"session exited {ma_thoat}")
    try:
        ban_ghi["nhiem"] = dau_nhiem_phien(phan_tich(doc_transcript(transcript)), wt[nhanh])
    except LoiThieuSo:
        ban_ghi["nhiem"] = ["transcript unreadable"]
    if ban_ghi["nhiem"]:
        log(f"session {ca['ma']}/{nhanh}/{lan} contaminated: {', '.join(ban_ghi['nhiem'])}",
            muc="canh-bao")
    _ghi_ban_ghi(ban_ghi, thu_muc)
    print(f"{ca['ma']} · {nhanh} · run {lan}: {ban_ghi['trang_thai']} · "
          f"{ban_ghi.get('chi_phi', 0):.2f} USD · " +
          " ".join(f"{k}={v}" for k, v in sorted(ban_ghi.get("ket_qua", {}).items())),
          flush=True)
    return ban_ghi


def lenh_chay(args):
    if not args.wt:
        raise LoiThieuSo("missing --wt <dir holding the two worktrees> — run `dung-nhanh` first")
    nhanh = sorted(NHANH) if args.nhanh == "ca-hai" else [args.nhanh]
    wt = {ten: os.path.join(args.wt, ten) for ten in nhanh}
    for ten, duong in wt.items():
        if not os.path.exists(os.path.join(duong, ".claude-plugin", "plugin.json")):
            raise LoiThieuSo(f"no worktree for branch {ten} at {duong} — run `dung-nhanh` first")
    bo_ca = [tim_ca(args.ca)] if args.ca else doc_bo_ca()
    dich = args.dich or os.path.join(tempfile.gettempdir(), "tdq-eval-phien")
    thu_muc = args.ra or KET_QUA_DIR
    da_co = {(b["ca"], b["nhanh"], b["lan"]): b.get("trang_thai")
             for b in doc_ban_ghi(thu_muc)} if args.tiep_tuc else {}
    token = lay_token()

    def chay(ca, ten_nhanh, lan):
        return chay_va_cham(ca, ten_nhanh, lan, wt, dich, thu_muc, token)

    tong, dung_som = chay_bo(bo_ca, nhanh, args.lan or 1, chay, args.tran_usd, da_co,
                             ghi_lai=lambda bg: _ghi_ban_ghi(bg, thu_muc))
    print(f"total cost of the round: {tong:.2f} USD")
    if dung_som:
        _loi(f"STOPPED EARLY on the {args.tran_usd:.2f} USD cap — continue with --tiep-tuc "
             "after raising the cap.")
        return 1
    return 0


def cham_lai_tat_ca(thu_muc):
    """Rescore every record from its stored transcript with the CURRENT scorer.

    Only the verdict changes; the session's measurements (cost, turns, exit code) stay put — they
    are facts of that run, not conclusions of the judge.
    """
    xong, bo_qua = [], []
    for duong_dan in sorted(glob.glob(os.path.join(thu_muc, "*.json"))):
        with open(duong_dan, encoding="utf-8") as f:
            ban_ghi = json.load(f)
        transcript = ban_ghi.get("transcript") or ""
        if not os.path.exists(transcript):
            bo_qua.append(os.path.basename(duong_dan))
            continue
        ca = tim_ca(ban_ghi["ca"])
        moi = cham_phien(ca, transcript)
        ban_ghi["ket_qua"] = moi["ket_qua"]
        ban_ghi["nhiem"] = moi.get("nhiem", ban_ghi.get("nhiem", []))
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(ban_ghi, f, ensure_ascii=False, indent=2)
        xong.append(os.path.basename(duong_dan))
    return xong, bo_qua


def lenh_cham(args):
    if args.tat_ca:
        xong, bo_qua = cham_lai_tat_ca(args.ra or KET_QUA_DIR)
        print(f"rescored: {len(xong)} records · skipped (transcript missing): {len(bo_qua)}")
        for ten in bo_qua:
            print(f"  skipped {ten}")
        return 0
    thieu = [c for c in ("ca", "nhanh", "lan") if getattr(args, c) is None]
    if thieu:
        raise LoiThieuSo("scoring one session needs --" + ", --".join(thieu) +
                         " (or use --tat-ca to rescore the whole directory)")
    if not args.transcript or not os.path.exists(args.transcript):
        raise LoiThieuSo(f"transcript to score is missing: {args.transcript!r}")
    ca = tim_ca(args.ca)
    ra = args.ra or KET_QUA_DIR
    os.makedirs(ra, exist_ok=True)
    ban_ghi = {
        "ca": ca["ma"],
        "nhanh": args.nhanh,
        "lan": args.lan,
        "trang_thai": "xong",
        "transcript": os.path.abspath(args.transcript),
        **cham_phien(ca, args.transcript),
    }
    ten = f"{ca['ma']}__{args.nhanh}__{args.lan}.json"
    with open(os.path.join(ra, ten), "w", encoding="utf-8") as f:
        json.dump(ban_ghi, f, ensure_ascii=False, indent=2)
    log(f"scored {ten}")
    print(f"{ca['ma']} · {args.nhanh} · run {args.lan}: " +
          " ".join(f"{k}={v}" for k, v in sorted(ban_ghi["ket_qua"].items())))
    return 0


def kiem_dinh_dau(so_xau, so_tot):
    """EXACT one-sided sign test over the discordant pairs.

    Null hypothesis: discordant pairs lean both ways equally (p = 1/2). Alternative: the hybrid
    branch is worse. p = P(X >= so_xau) with X ~ Binomial(so_xau + so_tot, 1/2).
    Tied pairs carry no direction, so they drop out of n — exactly the sign test's rule.
    """
    n = so_xau + so_tot
    if n == 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(so_xau, n + 1)) / (2 ** n)


def don_vi_kiem(ban_ghi):
    """Group records into tests — one test is one (case, rule code) pair.

    Only runs with a real verdict count (`dat` or `vi-pham`); `khong-ap-dung` means that case did
    not touch that rule on that run, so it says nothing. Records in state `loi` are dropped
    entirely.
    """
    gom = {}
    for b in ban_ghi:
        if b.get("trang_thai") != "xong":
            continue
        for ma, phan_quyet in (b.get("ket_qua") or {}).items():
            if phan_quyet not in ("dat", "vi-pham"):
                continue
            o = gom.setdefault((b["ca"], ma), {n: [0, 0] for n in NHANH})
            o[b["nhanh"]][1] += 1
            if phan_quyet == "dat":
                o[b["nhanh"]][0] += 1
    return gom


def bao_cao_so(ban_ghi):
    """The whole round's table of numbers. Every number is read off the records, never typed."""
    gom = don_vi_kiem(ban_ghi)
    don_vi, bo_qua, cap_xau, cap_tot, cap_hoa, sut_cung = [], [], 0, 0, 0, []
    for (ca, ma), o in sorted(gom.items()):
        if any(o[n][1] == 0 for n in NHANH):
            bo_qua.append((ca, ma))
            continue
        ti = {n: o[n][0] / o[n][1] for n in NHANH}
        chieu = "hoa" if ti["lai"] == ti["viet"] else ("xau" if ti["lai"] < ti["viet"] else "tot")
        don_vi.append({"ca": ca, "ma": ma, "viet": tuple(o["viet"]), "lai": tuple(o["lai"]),
                       "chieu": chieu})
        cap_xau += chieu == "xau"
        cap_tot += chieu == "tot"
        cap_hoa += chieu == "hoa"
        if o["viet"][0] == o["viet"][1] and o["lai"][0] == 0:
            sut_cung.append((ca, ma))

    ti_le = {}
    for d in don_vi:
        muc = ti_le.setdefault(d["ma"], {n: [0, 0] for n in NHANH})
        for n in NHANH:
            muc[n][0] += d[n][0]
            muc[n][1] += d[n][1]
    ti_le = {ma: {n: tuple(v) for n, v in muc.items()} for ma, muc in ti_le.items()}

    phu = {}
    for d in don_vi:
        phu.setdefault(d["ca"], []).append(d["ma"])
    phu = {ca: sorted(set(ma)) for ca, ma in phu.items()}

    theo_nhanh = {n: {"phien": 0, "chi_phi": 0.0, "so_luot": 0} for n in NHANH}
    for b in ban_ghi:
        m = theo_nhanh.get(b.get("nhanh"))
        if m is None:
            continue
        m["phien"] += 1
        m["chi_phi"] += b.get("chi_phi") or 0.0
        m["so_luot"] += b.get("so_luot") or 0

    p = kiem_dinh_dau(cap_xau, cap_tot)
    dk = [x for x in don_vi if x["ma"] not in MA_THEM_SAU]
    dk_xau = sum(1 for x in dk if x["chieu"] == "xau")
    dk_tot = sum(1 for x in dk if x["chieu"] == "tot")
    p_dk = kiem_dinh_dau(dk_xau, dk_tot)
    return {
        "so_don_vi_dang_ky": len(dk),
        "cap_xau_dang_ky": dk_xau,
        "cap_tot_dang_ky": dk_tot,
        "cap_hoa_dang_ky": len(dk) - dk_xau - dk_tot,
        "p_dang_ky": p_dk,
        "ket_luan_dang_ky": "sut" if p_dk < NGUONG_P and dk_xau > dk_tot else "chua-du",
        "so_ban_ghi": len(ban_ghi),
        "so_chay_lai": sum(b.get("chay_lai", 0) for b in ban_ghi),
        "so_loi": sum(1 for b in ban_ghi if b.get("trang_thai") == "loi"),
        "chi_phi": sum(b.get("chi_phi") or 0.0 for b in ban_ghi),
        "so_don_vi": len(don_vi),
        "don_vi": don_vi,
        "bo_qua": bo_qua,
        "cap_xau": cap_xau,
        "cap_tot": cap_tot,
        "cap_hoa": cap_hoa,
        "p": p,
        "ket_luan": "sut" if p < NGUONG_P and cap_xau > cap_tot else "chua-du",
        "sut_cung": sut_cung,
        "ti_le": ti_le,
        "phu": phu,
        "theo_nhanh": theo_nhanh,
    }


DONG_SOUL = ("Soul: chất lượng > runtime > context cost · "  # i18n-allow
             "luật gốc: skills/tdq-conventions/references/soul.md")  # i18n-allow


def viet_audit(bc, ngay):
    """Build the whole audit file out of the table. No hand-typed number gets in."""
    d = []
    d.append("# ĐO ĐỘ TUÂN THỦ — bộ skill tiếng Việt so với bộ lai")  # i18n-allow
    d.append("")
    d.append(f"Ngày: {ngay} · {DONG_SOUL}")  # i18n-allow
    d.append("")
    d.append(f"Hai nhánh đem so: `viet` = commit `{NHANH['viet']}` (bộ skill tiếng Việt) · "  # i18n-allow
             f"`lai` = commit `{NHANH['lai']}` (luật lý luận tiếng Anh, khuôn user-facing "  # i18n-allow
             "tiếng Việt).")  # i18n-allow
    d.append("File này do `python3 scripts/tdq_eval.py bao-cao --ghi` sinh ra từ bản ghi "  # i18n-allow
             "JSON trong `docs/tdq/bench/tuan-thu/`; sửa tay là mất tính đối chiếu.")  # i18n-allow
    d.append("")
    d.append("## Vòng chạy")  # i18n-allow
    d.append("")
    d.append(f"- Bản ghi: {bc['so_ban_ghi']} · lỗi chưa xử: {bc['so_loi']}")  # i18n-allow
    d.append(f"- Phép kiểm ghép cặp: {bc['so_don_vi']} · bỏ qua vì một nhánh không có lần "  # i18n-allow
             f"nào áp dụng: {len(bc['bo_qua'])}")  # i18n-allow
    for ca, ma in bc["bo_qua"]:
        d.append(f"  - bỏ qua: {ca} · {ma}")  # i18n-allow
    d.append(f"- Chi phí: {bc['chi_phi']:.2f} USD")  # i18n-allow
    for ten in sorted(NHANH):
        m = bc["theo_nhanh"][ten]
        d.append(f"- Nhánh `{ten}`: {m['phien']} phiên · {m['chi_phi']:.2f} USD · "  # i18n-allow
                 f"{m['so_luot']} lượt")  # i18n-allow
    d.append("")
    d.append("## Tuân thủ theo mã luật")  # i18n-allow
    d.append("")
    d.append("Số đọc là: số lần ĐẠT trên số lần luật đó thật sự áp dụng. Lần "  # i18n-allow
             "`khong-ap-dung` không vào mẫu số.")  # i18n-allow
    d.append("")
    d.append("| mã | viet | lai |")  # i18n-allow
    d.append("|---|---|---|")
    for ma in sorted(bc["ti_le"]):
        v, l = bc["ti_le"][ma]["viet"], bc["ti_le"][ma]["lai"]
        d.append(f"| {ma} | {v[0]}/{v[1]} | {l[0]}/{l[1]} |")
    d.append("")
    d.append("## Cặp lệch")  # i18n-allow
    d.append("")
    d.append(f"- Nghiêng xấu (lai kém hơn): {bc['cap_xau']}")  # i18n-allow
    d.append(f"- Nghiêng tốt (lai khá hơn): {bc['cap_tot']}")  # i18n-allow
    d.append(f"- Hoà: {bc['cap_hoa']}")  # i18n-allow
    d.append("")
    lech = [x for x in bc["don_vi"] if x["chieu"] != "hoa"]
    if lech:
        d.append("| ca | mã | viet | lai | chiều |")  # i18n-allow
        d.append("|---|---|---|---|---|")
        for x in lech:
            d.append(f"| {x['ca']} | {x['ma']} | {x['viet'][0]}/{x['viet'][1]} | "
                     f"{x['lai'][0]}/{x['lai'][1]} | {x['chieu']} |")
    else:
        d.append("Không cặp nào lệch.")  # i18n-allow
    d.append("")
    d.append("## Kết luận")  # i18n-allow
    d.append("")
    d.append("Hai con số, đọc theo đúng thứ tự này:")  # i18n-allow
    d.append("")
    d.append(f"1. **Bộ mã đăng ký TRƯỚC vòng chạy** ({bc['so_don_vi_dang_ky']} phép kiểm — "  # i18n-allow
             f"{bc['cap_xau_dang_ky']} nghiêng xấu · {bc['cap_tot_dang_ky']} nghiêng tốt · "  # i18n-allow
             f"{bc['cap_hoa_dang_ky']} hoà): p = {bc['p_dang_ky']:.4f}. **Đây là con số "  # i18n-allow
             "chốt.**")  # i18n-allow
    d.append(f"2. Cả bộ, kể cả {len(MA_THEM_SAU)} mã thêm sau vòng chạy "  # i18n-allow
             f"({' '.join(MA_THEM_SAU)}): p = {bc['p']:.4f}. Bốn mã này chấm lại từ "  # i18n-allow
             "transcript đã lưu nên không tốn phiên nào, nhưng chúng được chọn KHI ĐÃ THẤY "  # i18n-allow
             "số của vòng chạy, nên con số này chỉ để tham khảo, không dùng để kết luận.")  # i18n-allow
    d.append("")
    d.append(f"p = {bc['p_dang_ky']:.4f} — kiểm định dấu chính xác một phía trên các cặp "  # i18n-allow
             f"lệch của bộ đăng ký trước, ngưỡng chốt trước khi chạy là {NGUONG_P}.")  # i18n-allow
    d.append("")
    if bc["ket_luan_dang_ky"] == "sut":
        d.append("**SỤT.** Bộ lai tuân thủ kém hơn bộ tiếng Việt ở mức vượt ngưỡng đã chốt.")  # i18n-allow
    else:
        d.append("**CHƯA ĐỦ BẰNG CHỨNG** để kết luận bộ lai sụt. Đây KHÔNG phải bằng chứng "  # i18n-allow
                 "hai bộ ngang nhau — chỉ là phép đo này không thấy chênh lệch đủ lớn.")  # i18n-allow
    d.append("")
    d.append("### Sụt cứng")  # i18n-allow
    d.append("")
    if bc["sut_cung"]:
        d.append("Mã tuân thủ trọn ở nhánh `viet` mà trượt sạch ở nhánh `lai` — phải soi tay:")  # i18n-allow
        for ca, ma in bc["sut_cung"]:
            d.append(f"- `{ca}` / `{ma}`")
    else:
        d.append("Không mã nào tuân thủ trọn ở `viet` mà trượt sạch ở `lai`.")  # i18n-allow
    d.append("")
    d.append("### Độ nhạy")  # i18n-allow
    d.append("")
    d.append(f"Với {bc['so_don_vi']} phép kiểm ghép cặp, độ nhạy của phép đo chỉ đủ để "  # i18n-allow
             "thấy sụt lớn. Chênh lệch vài điểm phần trăm nằm trong nhiễu và báo cáo KHÔNG "  # i18n-allow
             "kết luận gì về nó.")  # i18n-allow
    if bc["bo_qua"]:
        d.append("")
        d.append("### Phép kiểm bị loại")  # i18n-allow
        d.append("")
        d.append("Một nhánh không có lần nào luật thật sự áp dụng, nên không ghép cặp được:")  # i18n-allow
        for ca, ma in bc["bo_qua"]:
            d.append(f"- `{ca}` / `{ma}`")
    d.append("")
    return "\n".join(d)


def _in_bang(bc):
    print(f"records: {bc['so_ban_ghi']} · unhandled errors: {bc['so_loi']} · "
          f"tests: {bc['so_don_vi']} · skipped: {len(bc['bo_qua'])}")
    print()
    print("| code | viet pass/applied | lai pass/applied |")
    print("|---|---|---|")
    for ma in sorted(bc["ti_le"]):
        v, l = bc["ti_le"][ma]["viet"], bc["ti_le"][ma]["lai"]
        print(f"| {ma} | {v[0]}/{v[1]} | {l[0]}/{l[1]} |")
    print()
    print(f"discordant pairs: {bc['cap_xau']} worse · {bc['cap_tot']} better · "
          f"{bc['cap_hoa']} tied")
    print(f"p = {bc['p']:.4f} (exact one-sided sign test, threshold {NGUONG_P})")
    print("conclusion: " + ("REGRESSION — the hybrid branch complies worse"
                          if bc["ket_luan"] == "sut" else "NOT ENOUGH EVIDENCE for a regression"))
    if bc["sut_cung"]:
        print("hard regression (viet full, lai zero): " +
              ", ".join(f"{ca}/{ma}" for ca, ma in bc["sut_cung"]))
    print(f"sensitivity: {bc['so_don_vi']} paired tests only catch a large regression; "
          "a few percentage points sit inside the noise and nothing is concluded from them")


def lenh_bao_cao(args):
    ban_ghi = doc_ban_ghi(args.thu_muc)
    bc = bao_cao_so(ban_ghi)
    da_in = False
    if args.dem:
        print(f"records: {bc['so_ban_ghi']} · unhandled errors: {bc['so_loi']} · "
              f"retries: {bc['so_chay_lai']}")
        da_in = True
    if args.phu:
        print(f"tests: {bc['so_don_vi']}")
        for ca in sorted(bc["phu"]):
            print(f"{ca}: {len(bc['phu'][ca])} codes — {' '.join(bc['phu'][ca])}")
        da_in = True
    if args.ghi:
        ngay = datetime.now().strftime("%Y-%m-%d")
        van = viet_audit(bc, ngay)
        os.makedirs(os.path.dirname(os.path.abspath(args.ghi)), exist_ok=True)
        with open(args.ghi, "w", encoding="utf-8") as f:
            f.write(van)
        log(f"ghi audit: {args.ghi}")
        print(f"wrote {args.ghi} from {bc['so_ban_ghi']} records")
        da_in = True
    if args.chi_phi:
        print(f"round cost: {bc['chi_phi']:.2f} USD over {bc['so_ban_ghi']} sessions")
        da_in = True
    if not da_in:
        _in_bang(bc)
    return 0


XU_LY = {"dung-nhanh": lenh_dung_nhanh, "chay": lenh_chay,
         "cham": lenh_cham, "bao-cao": lenh_bao_cao}


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tdq_eval.py",
        description="Measure how well two skill branches comply with the TDQ rules.")
    sub = parser.add_subparsers(dest="lenh")

    p_dung = sub.add_parser("dung-nhanh", help="build the two worktrees in a temp dir")
    p_dung.add_argument("--dich", help="temp dir holding the two worktrees")

    p_chay = sub.add_parser("chay", help="run measured sessions for the declared cases")
    p_chay.add_argument("--ca", help="case code; empty means run them all")
    p_chay.add_argument("--lan", type=int, help="how many runs per case per branch")
    p_chay.add_argument("--nhanh", required=True, choices=sorted(NHANH) + ["ca-hai"],
                        help="branch to measure; `ca-hai` interleaves both")
    p_chay.add_argument("--wt", help="worktree dir of the branch (from `dung-nhanh`)")
    p_chay.add_argument("--dich", help="temp dir holding the measured sessions")
    p_chay.add_argument("--ra", help="dir to write records into (default docs/tdq/bench/tuan-thu)")
    p_chay.add_argument("--tran-usd", type=float, default=150.0,
                        help="cost cap for the whole round, in USD")
    p_chay.add_argument("--tiep-tuc", action="store_true",
                        help="skip work that already has a `xong` record")

    p_cham = sub.add_parser("cham", help="score one session transcript")
    p_cham.add_argument("--transcript", help="path to the stream-json transcript")
    p_cham.add_argument("--ca", help="case code of the session")
    p_cham.add_argument("--nhanh", choices=sorted(NHANH), help="branch to measure")
    p_cham.add_argument("--lan", type=int, help="which run this is")
    p_cham.add_argument("--tat-ca", action="store_true",
                        help="rescore EVERY record in --ra from its stored transcript")
    p_cham.add_argument("--ra", help="dir to write records into (default docs/tdq/bench/tuan-thu)")

    p_bao = sub.add_parser("bao-cao", help="print the round's table of numbers")
    p_bao.add_argument("--dem", action="store_true", help="only count records and errors")
    p_bao.add_argument("--phu", action="store_true", help="only print coverage: codes per case")
    p_bao.add_argument("--chi-phi", action="store_true", help="only print the round cost")
    p_bao.add_argument("--ghi", help="write the markdown audit file out of the table")
    p_bao.add_argument("--thu-muc", help="record dir (default docs/tdq/bench/tuan-thu)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.lenh:
        _loi("Missing sub-command. Run `tdq_eval.py --help` to see the four commands.")
        return 2
    log(f"{args.lenh} · {' '.join(sys.argv[1:])}")
    try:
        return XU_LY[args.lenh](args)
    except KeyError:
        _loi(f"Command `{args.lenh}` is not wired to a handler.")
        return 1
    except (LoiThieuSo, LoiChuaCai) as e:
        _loi(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
