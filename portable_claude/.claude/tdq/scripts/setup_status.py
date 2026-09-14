#!/usr/bin/env python3
"""setup_status.py — collect how TDQ-Workflow is really set up on this machine.

The page this script feeds answers one question the config files alone cannot: what does
Claude Code ACTUALLY receive? So every number here comes from RUNNING the tool, never from
reading a declaration. Four blocks are collected:

  1. workflow   — skills on disk, hooks and their measured cost, the current request state,
                  and the seven rungs of the LSP ladder.
  2. dependency — graphify, lumen, agent-lsp, ollama: present or not, version, binary path.
  3. detail     — which embedding model lumen uses and through which endpoints; which
                  language servers agent-lsp declares versus how many really start.
  4. mcp        — the MCP servers Claude Code has registered, with their connection state.

Usage:
        python3 scripts/setup_status.py            # write setup_status.html at the repo root

Log service: one ISO-timestamped line per source on **stderr**, on by default, muted with
`TDQ_LOG=0` — the same contract as every other script in `scripts/`.
Exit: 0 always when the page could be written; a source that fails becomes a "không đọc được"
cell instead of an exception, because a half-known machine is still worth showing.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import context_surface  # noqa: E402 — the documentation surface and the hook timings
import skill_inventory  # noqa: E402 — the skills that really sit on disk
import tdq_lsp  # noqa: E402 — reuse its rung ladder and its lumen-model resolution
import setup_status_render  # noqa: E402 — the renderer, kept free of any machine access
import tdq_state  # noqa: E402 — the request state, read-only

CONFIG_LUMEN = os.path.expanduser("~/.config/lumen/config.yaml")
CAU_HINH_CLAUDE = os.path.expanduser("~/.claude.json")

# The MCP server that owns the language servers; its `args` are the DECLARED list and
# its `env` (DOTNET_ROOT for omnisharp) must be reproduced or the probe fails falsely.
MCP_LSP = "lsp"

# How many characters of an unparseable output are quoted back on the page. Enough to
# recognise a changed format, short enough not to paste a whole log into a table cell.
DAI_NGUYEN_VAN = 200

# One row per tool: (name, the argv that prints its version, the install hint).
# `lumen` has no `--version` flag — the sub-command is `lumen version`, and getting that wrong
# is exactly the kind of silent "chưa cài" this page exists to stop reporting.
CONG_CU = (
    ("graphify", ["--version"], "xem https://github.com/Graphify-Labs/graphify"),
    ("lumen", ["version"], "cài lumen rồi đặt ~/.config/lumen/config.yaml"),
    # Single source of truth: `tdq_lsp` is the module that owns the ladder, so the install
    # command lives there and is never re-typed here.
    ("agent-lsp", ["--version"], tdq_lsp.INSTALL_AGENT_LSP),
    ("ollama", ["--version"], "brew install ollama"),
)

# How long any single external command may take. `agent-lsp doctor` starts 14 real language
# servers and measured 6.0s on this machine, so 90s is generous without hanging a terminal.
TIMEOUT_MAC_DINH = 90

# How many times each hook is run before taking the median. `context_surface`
# defaults to 5; 3 keeps the page under a few seconds without losing the median.
LAN_DO_HOOK = 3

# Claude Code ships skills of its own, and no script can see them: they live inside
# the binary, not on disk. Saying so on the page is the honest alternative to a list
# that silently omits them.
GHI_CHU_SKILL_BUILTIN = (
    "Bảng này chỉ liệt kê skill có trên đĩa. Các skill built-in của Claude Code nằm trong "
    "chính binary nên script không đọc được — muốn xem đủ phải hỏi trong phiên chat.")

MASK = "***"

# The page lands at the repository root and is listed in .gitignore: it carries local paths,
# the tailnet address of the lumen primary and the MCP inventory of this machine.
DUONG_DAN_RA = os.path.join(ROOT, "setup_status.html")

# Query parameters whose VALUE is a credential. Matched case-insensitively on the parameter
# name, so `tavilyApiKey` is caught by the `key` fragment without naming every vendor.
_TU_KHOA_BI_MAT = ("key", "token", "secret", "password", "passwd", "pwd", "credential", "auth")

_RE_THAM_SO = re.compile(
    r"(?i)([?&][^=&\s]*(?:" + "|".join(_TU_KHOA_BI_MAT) + r")[^=&\s]*=)([^&\s]+)")
_RE_HEADER = re.compile(r"(?i)\b(authorization\s*:\s*(?:bearer|basic|token)?\s*)(\S+)")
# A key does not only travel in a URL: a stdio MCP server takes it as a command-line flag
# (`--api-key=...`) and Claude Code passes others through the server's `env` block
# (`TAVILY_API_KEY=...`). Both shapes reach this page, so both are fenced here.
_RE_CO_LENH = re.compile(
    r"(?i)(--?[\w.-]*(?:" + "|".join(_TU_KHOA_BI_MAT) + r")[\w.-]*[=\s])([^\s&]+)")
_RE_BIEN_MT = re.compile(
    r"\b([A-Z][A-Z0-9_]*(?:" + "|".join(k.upper() for k in _TU_KHOA_BI_MAT)
    + r")[A-Z0-9_]*=)([^\s&]+)")


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """One ISO-timestamped line on stderr. Muted with TDQ_LOG=0 — the tdq_state contract."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] setup_status: {message}", file=sys.stderr)


# ------------------------------------------------------------------- masking

def mask_secrets(text):
    """Replace every credential value in `text` with `***`.

    This is the LAST fence before a string reaches the HTML file: `claude mcp list` prints the
    Tavily API key inline inside the server URL, and this repository is public. Masking keeps
    the parameter NAME so the page still shows that a key is configured.
    """
    if not text:
        return ""
    masked = str(text)
    for regex in (_RE_THAM_SO, _RE_CO_LENH, _RE_BIEN_MT, _RE_HEADER):
        masked = regex.sub(lambda m: m.group(1) + MASK, masked)
    return masked


# ------------------------------------------------------------ external commands

def _run_tool(binary, args, goi_y="", timeout=TIMEOUT_MAC_DINH, env=None):
    """Run one external command and describe the outcome instead of raising.

    A machine missing `graphify` is a normal state of the world, not a crash: the caller gets
    `co=False` plus the command that would install it, and the page shows a "chưa cài" cell.
    Every captured stream goes through `mask_secrets` before it leaves this function.
    """
    duong_dan = shutil.which(binary)
    if not duong_dan:
        _log(f"{binary}: not installed")
        return {"co": False, "chay_duoc": False, "duong_dan": "", "ma": None,
                "ra": "", "loi": "", "chi_tiet": "chưa cài", "goi_y": goi_y}

    bat_dau = datetime.datetime.now()
    try:
        moi_truong = None if env is None else {**os.environ, **env}
        # `encoding=` rather than a bare `text=True`: on Windows text mode would otherwise
        # decode through the active code page — the cross-platform rule this repo tracks.
        ket_qua = subprocess.run([duong_dan] + list(args), capture_output=True,
                                 encoding="utf-8", errors="replace",
                                 timeout=timeout, env=moi_truong)
    except subprocess.TimeoutExpired:
        _log(f"{binary}: timed out after {timeout}s")
        return {"co": True, "chay_duoc": False, "duong_dan": duong_dan, "ma": None,
                "ra": "", "loi": "", "chi_tiet": f"quá hạn {timeout}s", "goi_y": goi_y}
    except OSError as err:
        _log(f"{binary}: failed to start — {err}")
        return {"co": True, "chay_duoc": False, "duong_dan": duong_dan, "ma": None,
                "ra": "", "loi": "", "chi_tiet": f"không chạy được: {err}", "goi_y": goi_y}

    giay = (datetime.datetime.now() - bat_dau).total_seconds()
    _log(f"{binary} {' '.join(args)}: rc={ket_qua.returncode} in {giay:.1f}s")
    return {"co": True, "chay_duoc": True, "duong_dan": duong_dan,
            "ma": ket_qua.returncode,
            "ra": mask_secrets(ket_qua.stdout or ""),
            "loi": mask_secrets(ket_qua.stderr or ""),
            "chi_tiet": "", "goi_y": goi_y}


# --------------------------------------------------------------- data skeleton

def khung_du_lieu():
    """The exact shape the renderer consumes — four blocks, always present, never partial.

    Fixing the shape here is what lets a failing source degrade into a "không đọc được" cell:
    the renderer never has to ask whether a key exists, only whether it was filled in.
    """
    return {
        "meta": {
            "sinh_luc": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "project": ROOT,
            "python": sys.version.split()[0],
        },
        "workflow": {"skill": [], "hook": [], "state": {}, "bac": [], "loi": {}},
        "dependency": [],
        "chi_tiet": {"lumen": {}, "lsp": {}},
        "mcp": {"server": [], "loi": ""},
    }


# ------------------------------------------------------------------ collectors

def _dong_dau(text):
    """First non-empty line of `text`, or "" — version banners often carry trailing noise."""
    for dong in (text or "").splitlines():
        if dong.strip():
            return dong.strip()
    return ""


def thu_dependency():
    """One row per external tool: present or not, version, binary path, install hint.

    Every tool gets a row even when it is absent, so the page can say "chưa cài" out loud
    instead of quietly leaving a gap the reader has to notice.
    """
    hang = []
    for ten, args, goi_y in CONG_CU:
        ket_qua = _run_tool(ten, args, goi_y=goi_y)
        if not ket_qua["co"]:
            ban = "chưa cài"
        else:
            ban = _dong_dau(ket_qua["ra"]) or _dong_dau(ket_qua["loi"]) or "không đọc được"
        hang.append({
            "ten": ten,
            "co": ket_qua["co"],
            "ban": ban,
            "duong_dan": ket_qua["duong_dan"],
            "chi_tiet": ket_qua["chi_tiet"],
            "goi_y": goi_y,
        })
    return hang


def _endpoint_lumen(duong_dan):
    """Every `host:` value of the lumen config, in priority order (index 0 is the primary).

    Parsed by hand rather than with a YAML library: `scripts/` may not add a dependency the
    machine might lack, and the shape here is two flat keys under a list.
    """
    hosts = []
    with open(duong_dan, encoding="utf-8", errors="replace") as f:
        for dong in f:
            dong = dong.split("#", 1)[0]
            khoa, dau, gia_tri = dong.partition("host:")
            if dau and not khoa.strip(" -\t"):
                host = gia_tri.strip().strip("'\"")
                if host:
                    hosts.append(host)
    return hosts


def thu_lumen():
    """Which embedding model lumen really uses, and through which endpoints.

    The model is resolved by `tdq_lsp._model_lumen()` — the same order lumen itself follows
    (config file, then $LUMEN_EMBED_MODEL, then its built-in default), so this page cannot
    drift away from the rung-5 check the way a hardcoded constant once did.
    """
    model = tdq_lsp._model_lumen()
    try:
        hosts = _endpoint_lumen(CONFIG_LUMEN)
        chi_tiet = "" if hosts else "config không khai host nào"
    except OSError as err:
        hosts, chi_tiet = [], f"không đọc được {CONFIG_LUMEN}: {err}"
    _log(f"lumen: model={model} endpoints={len(hosts)}")
    return {"model": model, "endpoint": hosts, "config": CONFIG_LUMEN, "chi_tiet": chi_tiet}


# The five sources of the workflow block, each wrapped so a test can swap it for a fixture and
# so one broken source cannot take the other four down with it.

def _nguon_skill(project):
    return skill_inventory.inventory(project)


def _im_lang_module_muon():
    """Propagate TDQ_LOG=0 to the borrowed modules that read their OWN env variable.

    `context_surface` mutes on `TDQ_SURFACE_LOG`, not on `TDQ_LOG`. Without this, muting the
    page generator would still leave nine lines of somebody else's log on stderr — and a mute
    switch that only half works is worse than none.
    """
    if not _log_enabled():
        os.environ["TDQ_SURFACE_LOG"] = "0"


def _nguon_hook():
    _im_lang_module_muon()
    return context_surface.scan()


def _nguon_do_hook(runs=LAN_DO_HOOK):
    _im_lang_module_muon()
    return context_surface.measure_hooks(runs=runs)


def _nguon_state():
    return tdq_state.load(ROOT, heal=False)


def _nguon_bac(project):
    return tdq_lsp.chay_kiem(project)


def _thu_mot_nguon(loi, ten, ham, mac_dinh):
    """Call one source; on failure record why in `loi[ten]` and fall back to `mac_dinh`.

    Broad by design: this page must survive any machine it is pointed at, and a source that
    explodes is itself a fact worth displaying rather than a reason to produce nothing.
    """
    try:
        return ham()
    except Exception as err:  # noqa: BLE001 — the failure IS the datum, see the docstring
        loi[ten] = f"{type(err).__name__}: {err}"
        _log(f"source {ten} failed — {err}")
        return mac_dinh


def _hang_bac(bac):
    nhan = "ĐẠT" if bac.dat else ("CẢNH BÁO" if bac.chi_canh_bao else "THIẾU")
    return {"so": bac.so, "ten": bac.ten, "nhan": nhan,
            "chi_tiet": bac.chi_tiet, "lenh_cai": bac.lenh_cai}


def thu_workflow(project=ROOT):
    """Skills on disk, hooks and their measured cost, the request state, the seven rungs."""
    loi = {}
    skill = _thu_mot_nguon(loi, "skill", lambda: _nguon_skill(project), [])
    hook = _thu_mot_nguon(loi, "hook", _nguon_hook, [])
    do_hook = _thu_mot_nguon(loi, "do_hook", _nguon_do_hook, [])
    state = _thu_mot_nguon(loi, "state", _nguon_state, {})
    bac = _thu_mot_nguon(loi, "bac", lambda: _nguon_bac(project), [])
    _log(f"workflow: {len(skill)} skill · {len(hook)} doc row · {len(bac)} rung")
    return {
        "skill": [{"ten": t, "mo_ta": m, "nguon": n} for t, m, n in skill],
        "hook": [list(h) for h in hook],
        "do_hook": [list(h) for h in do_hook],
        "state": dict(state),
        "bac": [_hang_bac(b) for b in bac],
        "ghi_chu_builtin": GHI_CHU_SKILL_BUILTIN,
        "loi": loi,
    }


# ------------------------------------------------- what Claude Code really receives

# `claude mcp list` prints one server per line: "<name>: <url or command> - <mark> <state>".
_RE_MCP = re.compile(r"^(?P<ten>[^:]+):\s+(?P<dich>.*?)\s+-\s+(?P<trang_thai>[^-]+)$")

# `agent-lsp doctor` prints one block per server, opened by "● <lang> (<binary>)".
_RE_DOCTOR_DAU = re.compile(r"^●\s+(?P<lang>\S+)\s+\((?P<binary>[^)]+)\)")
_RE_DOCTOR_TRANG_THAI = re.compile(r"^\s+Status:\s+(?P<trang_thai>\S+)")
_RE_DOCTOR_TOM_TAT = re.compile(
    r"^\s*Summary:\s*(?P<ok>\d+)\s+ok,\s*(?P<hong>\d+)\s+failed", re.M)

DAU_NOI_DUOC = ("✔", "✓", "connected")


def _cau_hinh_lsp():
    """The `lsp` entry of ~/.claude.json — the DECLARED language servers plus their env."""
    with open(CAU_HINH_CLAUDE, encoding="utf-8") as f:
        return (json.load(f).get("mcpServers") or {}).get(MCP_LSP) or {}


def _trich_nguyen_van(text):
    goc = " ".join((text or "").split())
    return goc[:DAI_NGUYEN_VAN]


def _doc_mcp(ket_qua):
    """Parse `claude mcp list` into rows. Unrecognised output is reported, never guessed."""
    if not ket_qua["co"]:
        return [], f"claude {ket_qua['chi_tiet']}"
    server = []
    for dong in ket_qua["ra"].splitlines():
        khop = _RE_MCP.match(dong.rstrip())
        if not khop:
            continue
        trang_thai = khop.group("trang_thai").strip()
        server.append({
            "ten": khop.group("ten").strip(),
            "dich": khop.group("dich").strip(),
            "trang_thai": trang_thai,
            "noi_duoc": any(d in trang_thai.casefold() for d in DAU_NOI_DUOC),
        })
    if server:
        return server, ""
    return [], ("không phân tích được output của `claude mcp list` — nguyên văn: "
                + _trich_nguyen_van(ket_qua["ra"] or ket_qua["loi"]))


def _doc_khai_bao(args):
    """Split the declared `<lang>:<binary>,<flags>` arguments into (lang, binary) pairs."""
    khai = []
    for arg in args or []:
        lang, dau, phan_con_lai = str(arg).partition(":")
        if dau:
            khai.append({"lang": lang, "binary": phan_con_lai.split(",")[0]})
    return khai


def _doc_doctor(ket_qua):
    """Parse `agent-lsp doctor` into {lang: status}. Unrecognised output is reported."""
    trang_thai = {}
    lang_hien_tai = None
    for dong in ket_qua["ra"].splitlines():
        dau = _RE_DOCTOR_DAU.match(dong)
        if dau:
            lang_hien_tai = dau.group("lang")
            continue
        khop = _RE_DOCTOR_TRANG_THAI.match(dong)
        if khop and lang_hien_tai:
            trang_thai[lang_hien_tai] = khop.group("trang_thai").strip()
            lang_hien_tai = None
    return trang_thai


def _doi_chieu_doctor(ket_qua, trang_thai):
    """Cross-check the probe against its own verdict; return a warning, "" when they agree.

    The per-server `Status:` lines and the final `Summary:` line are two independent claims by
    the same tool, and the exit code is a third. They agreeing is what makes the "received"
    column trustworthy; a silent disagreement is exactly the failure this page exists to catch.

    Deliberately NOT a signal: the `[error] LSP server ... exited with error after 0s` lines on
    stderr. Measured three runs in a row, they named a different set of servers each time
    (4 → 7 → 5 lines) while `Summary` and the exit code stayed put — shutdown noise, not a dead
    server. Counting them would report failures that are not real.
    """
    canh_bao = []
    ma = ket_qua.get("ma")
    if ma not in (0, None):
        canh_bao.append(f"`agent-lsp doctor` thoát mã {ma}")
    dem_ok = sum(1 for t in trang_thai.values() if t == "ok")
    khop = _RE_DOCTOR_TOM_TAT.search(ket_qua.get("ra") or "")
    if not khop:
        canh_bao.append("không thấy dòng Summary của `agent-lsp doctor` để đối chiếu")
    elif int(khop.group("ok")) != dem_ok:
        canh_bao.append(
            f"doctor tự tổng kết {khop.group('ok')} ok / {khop.group('hong')} failed nhưng "
            f"đếm theo từng server chỉ ra {dem_ok} ok")
    return " · ".join(canh_bao)


def _ghep_lsp(khai_bao, trang_thai, chi_tiet):
    """Pair each DECLARED server with what the live probe said about it."""
    may = []
    for muc in khai_bao:
        may.append({**muc, "trang_thai": trang_thai.get(muc["lang"], "không rõ")})
    chet = [m for m in may if m["trang_thai"] != "ok"]
    return {
        "may": may,
        "so_khai_bao": len(may),
        "so_song": len(may) - len(chet),
        "chet": chet,
        "chi_tiet": chi_tiet,
    }


def thu_thuc_nhan():
    """The "declared versus received" block: MCP servers and language servers, probed live.

    Nothing here is read off a config file alone. `claude mcp list` is the only authority on
    what Claude Code registered, and `agent-lsp doctor` starts every declared language server
    for real — the case that motivated this page was a server declared fine and dead on the
    first request.
    """
    mcp_ket_qua = _run_tool("claude", ["mcp", "list"],
                            goi_y="cài Claude Code CLI để đọc danh sách MCP")
    server, mcp_chi_tiet = _doc_mcp(mcp_ket_qua)

    try:
        cau_hinh = _cau_hinh_lsp()
        loi_cau_hinh = ""
    except (OSError, ValueError) as err:
        cau_hinh, loi_cau_hinh = {}, f"không đọc được {CAU_HINH_CLAUDE}: {err}"

    khai_bao = _doc_khai_bao(cau_hinh.get("args"))
    doctor = _run_tool("agent-lsp", ["doctor"] + list(cau_hinh.get("args") or []),
                       goi_y="cài agent-lsp để dò sống language server",
                       env=cau_hinh.get("env") or None)
    if not doctor["co"]:
        trang_thai, lsp_chi_tiet = {}, f"agent-lsp {doctor['chi_tiet']}"
    else:
        trang_thai = _doc_doctor(doctor)
        lsp_chi_tiet = _doi_chieu_doctor(doctor, trang_thai) if trang_thai else (
            "không phân tích được output của `agent-lsp doctor` — nguyên văn: "
            + _trich_nguyen_van(doctor["ra"] or doctor["loi"]))
    lsp_chi_tiet = " · ".join(x for x in (loi_cau_hinh, lsp_chi_tiet) if x)

    _log(f"received: {len(server)} MCP server · {len(trang_thai)}/{len(khai_bao)} LSP answered")
    return {
        "mcp": {"server": server, "chi_tiet": mcp_chi_tiet},
        "lsp": _ghep_lsp(khai_bao, trang_thai, lsp_chi_tiet),
    }


def thu_tat_ca(project=ROOT):
    """Fill the skeleton of `khung_du_lieu()` from every source — the renderer's whole input."""
    _log("collecting all four blocks")
    du_lieu = khung_du_lieu()
    du_lieu["meta"]["project"] = project
    du_lieu["workflow"] = thu_workflow(project)
    du_lieu["dependency"] = thu_dependency()
    thuc_nhan = thu_thuc_nhan()
    du_lieu["chi_tiet"] = {"lumen": thu_lumen(), "lsp": thuc_nhan["lsp"]}
    du_lieu["mcp"] = thuc_nhan["mcp"]
    return du_lieu


def main(argv=None):
    """Collect, render, write the page. Exit 0 whenever the file could be written."""
    del argv  # the command takes no option yet; the signature keeps main() testable
    bat_dau = datetime.datetime.now()
    du_lieu = thu_tat_ca()
    html = setup_status_render.render(du_lieu)
    with open(DUONG_DAN_RA, "w", encoding="utf-8") as f:
        f.write(html)
    giay = (datetime.datetime.now() - bat_dau).total_seconds()
    _log(f"wrote {DUONG_DAN_RA} in {giay:.1f}s")
    print(DUONG_DAN_RA)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
