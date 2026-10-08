#!/usr/bin/env python3
"""The LSP modules of a project, the MCP script that proves each one answers, and the table of results.

A module is one (language, root) pair: the root is the directory holding the marker the language
server walks up to (`tsconfig.json`, `pyproject.toml`, `go.mod`…). A single-language repo is a table
of one row; a monorepo with two tsconfig files is two rows. Every row has to be PROVEN through the
same MCP path the agent uses — `start_lsp(root, language_id)` → `open_document` → `find_references`
— because `agent-lsp doctor` reported healthy in all three failures measured on 2026-10-07
(wrong server picked without `language_id`, tsserver "No Project", a one-file scope).

This module never talks to a language server itself: a script cannot call MCP tools. It picks the
symbol, prints the calls, and judges the number the agent reports back (`ghi_ket_qua`).

Pass rule: references returned by LSP (declaration included) > occurrences of the name in its own
file. `find_references` through agent-lsp prints namespaces, not file paths, so files cannot be
counted; but every failure above yields zero references outside the defining file, which this
rule catches.

Also here: the orphan `agent-lsp daemon-broker` sweep and the free-commit probe — the
`0xc0000409` crash of 2026-10-07 was `VirtualAlloc failed` with 3.7 GB of commit left.

Env: TDQ_LOG=0 silences the log.
"""
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
import tdq_lsp  # noqa: E402

FILE_BANG = os.path.join("docs", "tdq", ".tdq-lsp-module.json")
HAN_GIAY = 24 * 3600
DAT, TRUOT, CHUA_KIEM, HET_HAN, KHONG_DU_MAU = "DAT", "TRUOT", "CHUA_KIEM", "HET_HAN", "KHONG_DU_MAU"
CHAN = (TRUOT, CHUA_KIEM, HET_HAN)
NGUONG_COMMIT_GB = 4.0
# `find_references` answers "still being indexed" for the first seconds after a daemon start
# (measured 2026-10-08 on a fresh clone: refused at 2 s and 6 s); `start_lsp` can wait for it.
CHO_CHI_MUC_GIAY = 60
# A file this large is generated or vendored; reading it to pick a symbol costs more than it tells.
TRAN_DOC_FILE = 1_000_000
# JavaScript is served by the TypeScript server and shares its roots, so the two are one family.
HO = {"javascript": "typescript"}
# Markup and data formats have no import graph: nothing for `find_references` to prove.
DANH_DAU = {lang for lang, (moc, _nhom) in tdq_lsp.LANG_CONFIG.items() if not moc}

_RE_DINH_NGHIA = {
    "python": r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w{3,})",
    "typescript": r"^\s*export\s+(?:default\s+)?(?:async\s+)?"
                  r"(?:function\*?|class|const|let|interface|type|enum)\s+([A-Za-z_$][\w$]{3,})",
    "go": r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w{3,})",
    "rust": r"^\s*pub\s+(?:async\s+)?(?:fn|struct|enum|trait)\s+([A-Za-z_]\w{3,})",
}
_RE_DINH_NGHIA["javascript"] = _RE_DINH_NGHIA["typescript"]
_RE_DINH_NGHIA_CHUNG = r"^\s*(?:def|function|func|fn|class)\s+([A-Za-z_]\w{3,})"
_RE_TU = re.compile(r"[A-Za-z_$][\w$]*")
_RE_CHUOI = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\\n])*"'
                       r"|'(?:\\.|[^'\\\n])*'|`[^`]*`")
_RE_CHU_THICH_HASH = re.compile(r"#[^\n]*")
_RE_CHU_THICH_C = re.compile(r"//[^\n]*|/\*[\s\S]*?\*/")
_RE_BROKER_GOC = re.compile(r"--root-dir[= ](\"[^\"]+\"|\S+)")
_RE_BROKER_LANG = re.compile(r"--language[= ](\S+)")
_RE_NGAY_WMI = re.compile(r"/Date\((\d+)")


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _log(message):
    """Log service: one ISO-timestamped line to stderr. Silenced by TDQ_LOG=0 (shared with tdq_lsp)."""
    tdq_lsp._log(f"lsp_module: {message}")


# ── Modules ────────────────────────────────────────────────────────────────────────────────

def _moc_theo_ho():
    """family → marker names in priority order, merged over the languages of that family."""
    moc_ho = {}
    for lang, (moc, _nhom) in tdq_lsp.LANG_CONFIG.items():
        danh_sach = moc_ho.setdefault(HO.get(lang, lang), [])
        danh_sach.extend(m for m in moc if m not in danh_sach)
    return moc_ho


MOC_HO = _moc_theo_ho()


def _moc_co_mat(ho, ten_files):
    """-> the first marker of `ho` present among `ten_files`, or ''."""
    for moc in MOC_HO.get(ho, ()):
        if moc.startswith("*."):
            khop = next((f for f in sorted(ten_files) if f.endswith(moc[1:])), "")
            if khop:
                return khop
        elif moc in ten_files:
            return moc
    return ""


def _to_tien(rel):
    """'a/b' -> ['a/b', 'a', '.'] — the directory itself first, the repo root last."""
    ket_qua = []
    while rel not in ("", "."):
        ket_qua.append(rel)
        rel = os.path.dirname(rel)
    return ket_qua + ["."]


def _goc_sau_nhat(rel, goc_cua_ho):
    return next((g for g in _to_tien(rel) if g in goc_cua_ho), ".")


def _thu_muc_bo(phan):
    return phan in tdq_lsp.SKIP_DIRS or phan.startswith(tdq_lsp.SKIP_PREFIX) or phan.startswith(".")


def _file_cua_git(project):
    """-> {dir: [file]} of tracked + untracked-not-ignored files, or None outside a git work tree.

    `.gitignore` is the project's own word on what is build output: claudecodeui ignores
    `dist-server/`, which no fixed skip-list knew, and a script picked its symbol from that
    compiled copy (measured 2026-10-08). `git ls-files` took 0.05–0.08 s on 1,127 files.
    """
    rc, ra = tdq_lsp._run(["git", "-C", project, "ls-files", "-co", "--exclude-standard", "-z"], timeout=30)
    if rc != 0:
        return None
    theo_thu_muc = {}
    for duong in ra.split("\0"):
        duong = duong.strip().replace("\\", "/")
        if not duong:
            continue
        thu_muc, _, ten = duong.rpartition("/")
        if any(_thu_muc_bo(p) for p in thu_muc.split("/") if p):
            continue
        theo_thu_muc.setdefault(thu_muc or ".", []).append(ten)
    return theo_thu_muc


def _file_cua_cay(project):
    """-> {dir: [file]} by walking the tree, for a project that is not a git work tree."""
    theo_thu_muc = {}
    for thu_muc, con, files in os.walk(project):
        con[:] = [d for d in con if not _thu_muc_bo(d)]
        rel = os.path.relpath(thu_muc, project).replace(os.sep, "/")
        theo_thu_muc[rel] = list(files)
    return theo_thu_muc


def _quet(project):
    """-> ({family: {root: marker}}, {family: [(dir, file, language)]})."""
    theo_thu_muc = _file_cua_git(project) if os.path.exists(os.path.join(project, ".git")) else None
    if theo_thu_muc is None:
        theo_thu_muc = _file_cua_cay(project)
    goc, nguon = {}, {}
    for rel, files in theo_thu_muc.items():
        ten_files = set(files)
        for ho in MOC_HO:
            moc = _moc_co_mat(ho, ten_files)
            if moc:
                goc.setdefault(ho, {})[rel] = moc
        for ten in files:
            lang = tdq_lsp.EXT_LANG.get(os.path.splitext(ten)[1])
            if lang:
                nguon.setdefault(HO.get(lang, lang), []).append((rel, ten, lang))
    return goc, nguon


def _gop_module_nho(nhom, goc_cua_ho):
    """Fold every group under NGUONG_FILE files into its nearest ancestor root, to a fixed point.

    One pass is not enough: a small group can land on an ancestor root holding no source of its
    own, which is itself small and must climb again — a single pass dropped those files from
    every module (code review 2026-10-08).
    """
    while True:
        nho = [g for g in nhom if g != "." and len(nhom[g]) < tdq_lsp.NGUONG_FILE]
        if not nho:
            break
        g = max(nho, key=lambda r: r.count("/"))
        cha = _goc_sau_nhat(os.path.dirname(g) or ".", set(nhom) | set(goc_cua_ho))
        nhom.setdefault(cha, []).extend(nhom.pop(g))
    return {g: f for g, f in nhom.items() if len(f) >= tdq_lsp.NGUONG_FILE}


def do_module(project):
    """-> [{id, lang, goc, so_file, moc, files}] sorted by id; `files` are paths relative to the project.

    Root = deepest directory holding a marker of the file's language family; none → the repo root.
    A module under NGUONG_FILE files joins its nearest ancestor root. A TS-family module is
    `typescript` when it holds any TypeScript file, else `javascript`.
    """
    bat_dau = time.time()
    goc, nguon = _quet(project)
    ket_qua = []
    for ho, danh_sach in nguon.items():
        goc_cua_ho = goc.get(ho, {})
        nhom = {}
        for rel, ten, lang in danh_sach:
            duong = ten if rel == "." else f"{rel}/{ten}"
            nhom.setdefault(_goc_sau_nhat(rel, goc_cua_ho), []).append((duong, lang))
        for g, files in sorted(_gop_module_nho(nhom, goc_cua_ho).items()):
            lang = ho
            if ho == "typescript" and all(l != "typescript" for _, l in files):
                lang = "javascript"
            ket_qua.append({"id": f"{lang}:{g}", "lang": lang, "goc": g, "so_file": len(files),
                            "moc": goc_cua_ho.get(g, ""), "files": sorted(d for d, _ in files)})
    ket_qua.sort(key=lambda m: m["id"])
    _log(f"do_module {project} → {len(ket_qua)} module trong {time.time() - bat_dau:.2f}s")
    return ket_qua


def ngon_ngu_cua(modules):
    return sorted({m["lang"] for m in modules})


# ── Table & fingerprint ──────────────────────────────────────────────────────────────────

def doc_mcp_args(duong=None):
    """-> the `args` list of the `lsp` MCP server in ~/.claude.json ([] when absent)."""
    return tdq_lsp.mcp_args(duong or "~/.claude.json") or []


def dong_mcp(args, lang):
    """-> the `args` entry that serves `lang` (JavaScript falls back to TypeScript's), or ''."""
    khai = tdq_lsp.lang_mcp(args, lang)
    return next((a for a in args if khai and a.split(":", 1)[0] == khai), "")


def van_tay(project, module, args):
    """Fingerprint of what a verified result depends on: the marker file and the server entry."""
    moc = module.get("moc") or ""
    duong = os.path.join(project, module["goc"], moc) if moc else ""
    try:
        mtime = int(os.path.getmtime(duong)) if duong else 0
    except OSError:
        mtime = 0
    tho = json.dumps([module["lang"], module["goc"], moc, mtime, dong_mcp(args, module["lang"])])
    return hashlib.sha1(tho.encode("utf-8")).hexdigest()[:16]


def duong_bang(project):
    return os.path.join(project, FILE_BANG)


def doc_bang(project) -> dict:
    try:
        with open(duong_bang(project), encoding="utf-8") as fh:
            bang = json.load(fh)
    except (OSError, ValueError):
        return {"module": {}}
    if not isinstance(bang, dict) or not isinstance(bang.get("module"), dict):
        return {"module": {}}
    return bang


def _bo_qua_trong_git(project):
    """Keep the table out of `git status` via `.git/info/exclude` — local, the project's own
    `.gitignore` is never touched.

    The table is machine data (server paths, timestamps). Left untracked it makes the tree dirty,
    and intake step 3b STOPS on a dirty tree before opening the request branch — the table written
    at step 1b would block step 3b of the very same intake (seen in claudecodeui, 2026-10-08).
    Any git failure is silent: outside a repo there is nothing to keep clean.
    """
    rc, tien_to = tdq_lsp._run(["git", "-C", project, "rev-parse", "--show-prefix"], timeout=15)
    rc2, duong = tdq_lsp._run(["git", "-C", project, "rev-parse", "--git-path", "info/exclude"], timeout=15)
    if rc or rc2 or not duong.strip():
        return
    duong = duong.strip().splitlines()[-1]
    duong = duong if os.path.isabs(duong) else os.path.join(project, duong)
    mau = "/" + (tien_to.strip().splitlines()[-1] if tien_to.strip() else "") + FILE_BANG.replace(os.sep, "/")
    try:
        with open(duong, encoding="utf-8") as fh:
            if mau in fh.read().splitlines():
                return
    except OSError:
        pass
    try:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with open(duong, "a", encoding="utf-8") as fh:
            fh.write(f"\n# TDQ: LSP module table, machine data (0.59.0)\n{mau}\n")
    except OSError:
        return


def ghi_bang(project, bang):
    """Atomic write: a crash mid-write must never leave a half table that reads as 'all verified'."""
    duong = duong_bang(project)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    fd, tam = tempfile.mkstemp(dir=os.path.dirname(duong), prefix=".tdq-lsp-module-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(bang, fh, ensure_ascii=False, indent=2)
        os.replace(tam, duong)
    except BaseException:
        if os.path.exists(tam):
            os.remove(tam)
        raise
    _bo_qua_trong_git(project)


def _tuoi_giay(luc, bay_gio):
    try:
        return bay_gio - datetime.fromisoformat(luc).timestamp()
    except (TypeError, ValueError):
        return float("inf")


def _phan_xu(project, module, muc, args, bay_gio):
    """-> (status, detail) of one module against its table entry."""
    if module["lang"] in DANH_DAU:
        return KHONG_DU_MAU, "ngôn ngữ đánh dấu, không có đồ thị import để kiểm"
    ket_qua = (muc or {}).get("ket_qua")
    if not ket_qua:
        return CHUA_KIEM, "chưa chạy kịch bản"
    if ket_qua.get("van_tay") != van_tay(project, module, args):
        return HET_HAN, "file mốc hoặc dòng MCP của ngôn ngữ đã đổi"
    if _tuoi_giay(ket_qua.get("luc"), bay_gio) > HAN_GIAY:
        return HET_HAN, f"kết quả cũ hơn {HAN_GIAY // 3600} giờ"
    return ket_qua.get("trang_thai", CHUA_KIEM), ket_qua.get("chi_tiet", "")


def trang_thai(project, args=None, bay_gio=None, modules=None):
    """-> [(module, status, detail)] for every current module of the project. Reads only."""
    args = doc_mcp_args() if args is None else args
    bay_gio = time.time() if bay_gio is None else bay_gio
    modules = do_module(project) if modules is None else modules
    bang = doc_bang(project)["module"]
    return [(m, *_phan_xu(project, m, bang.get(m["id"]), args, bay_gio)) for m in modules]


def cong_init(project, args=None):
    """The `init` gate -> (passed, lines). Passes when no module is unverified, stale or failed."""
    chan = [(m, tt, ct) for m, tt, ct in trang_thai(project, args) if tt in CHAN]
    if not chan:
        return True, []
    dong = [f"{m['id']} → {tt} ({ct})" for m, tt, ct in chan]
    return False, dong


# ── The MCP script ───────────────────────────────────────────────────────────────────────

def _bo_chuoi_va_chu_thich(text, lang):
    text = _RE_CHUOI.sub(" ", text)
    return (_RE_CHU_THICH_HASH if lang == "python" else _RE_CHU_THICH_C).sub(" ", text)


def _doc(duong):
    try:
        if os.path.getsize(duong) > TRAN_DOC_FILE:
            return ""
        with open(duong, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _ung_vien(project, module):
    """-> ({name: (file, line, col)} defined exactly once, {file: Counter-like dict of code words})."""
    mau = re.compile(_RE_DINH_NGHIA.get(module["lang"], _RE_DINH_NGHIA_CHUNG), re.M)
    dinh_nghia, so_lan, tu_theo_file = {}, {}, {}
    for rel in module["files"]:
        text = _doc(os.path.join(project, rel))
        dem = {}
        for tu in _RE_TU.findall(_bo_chuoi_va_chu_thich(text, module["lang"])):
            dem[tu] = dem.get(tu, 0) + 1
        tu_theo_file[rel] = dem
        for khop in mau.finditer(text):
            ten = khop.group(1)
            if ten.startswith("__") or ten.startswith("test"):
                continue
            so_lan[ten] = so_lan.get(ten, 0) + 1
            dong = text.count("\n", 0, khop.start(1)) + 1
            cot = khop.start(1) - (text.rfind("\n", 0, khop.start(1)) + 1) + 1
            dinh_nghia[ten] = (rel, dong, cot)
    return {t: v for t, v in dinh_nghia.items() if so_lan[t] == 1}, tu_theo_file


def kich_ban(project, module):
    """-> the script for one module, or None when no symbol is used from a second file.

    Picks the uniquely-defined symbol used in the FEWEST other files (at least one): the fewer
    the files, the smaller the chance grep and LSP disagree for reasons that are not a fault.
    """
    dinh_nghia, tu_theo_file = _ung_vien(project, module)
    tot_nhat = None
    for ten, (rel, dong, cot) in dinh_nghia.items():
        so_file = sum(1 for dem in tu_theo_file.values() if ten in dem)
        if so_file < 2:
            continue
        khoa = (so_file, -len(ten), ten)
        if tot_nhat is None or khoa < tot_nhat[0]:
            tot_nhat = (khoa, ten, rel, dong, cot, so_file)
    if tot_nhat is None:
        return None
    _khoa, ten, rel, dong, cot, so_file = tot_nhat
    return {"symbol": ten, "file": os.path.normpath(os.path.join(project, rel)), "line": dong,
            "column": cot, "so_file_grep": so_file,
            "so_lan_file_dinh_nghia": tu_theo_file[rel].get(ten, 1),
            "goc_tuyet_doi": os.path.normpath(os.path.join(project, module["goc"]))}


def loi_goi_mcp(module, kb, args=None):
    """The three MCP calls of a script, printed exactly as the agent should send them.

    `language_id` is the id the MCP server declares: a JavaScript module served by the TypeScript
    entry is started as `typescript`, or agent-lsp finds no server for it.
    """
    lang = tdq_lsp.lang_mcp(doc_mcp_args() if args is None else args, module["lang"]) or module["lang"]
    return [
        f'mcp__lsp__start_lsp {{"root_dir": {json.dumps(kb["goc_tuyet_doi"])}, "language_id": "{lang}", '
        f'"ready_timeout_seconds": {CHO_CHI_MUC_GIAY}}}',
        f'mcp__lsp__open_document {{"file_path": {json.dumps(kb["file"])}, "language_id": "{lang}"}}',
        f'mcp__lsp__find_references {{"file_path": {json.dumps(kb["file"])}, "line": {kb["line"]}, '
        f'"column": {kb["column"]}, "language_id": "{lang}", "include_declaration": true}}',
    ]


def ngon_ngu_moi(project):
    """-> languages the project has now that the module table has not seen ([] when no table).

    SessionStart asks this: a project that started as Python and later grew JS + HTML needs the
    background setup again (install the servers, declare them in MCP `lsp`) before intake.
    """
    da_biet = doc_bang(project).get("ngon_ngu")
    if not isinstance(da_biet, list):
        return []
    return sorted(set(ngon_ngu_cua(do_module(project))) - set(da_biet))


def ghi_ngon_ngu(project):
    # Called at the START of the background build, before any install: a build that dies midway
    # must not leave the language set unrecorded, or every new session would rebuild in a loop.
    """Record the current language set in the table, so SessionStart stops re-triggering."""
    bang = doc_bang(project)
    bang["ngon_ngu"] = ngon_ngu_cua(do_module(project))
    ghi_bang(project, bang)


def lap_kich_ban(project, args=None, chi_module=None):
    """Write a fresh script for every module still blocking; -> [(module, script or None)].

    The table is rewritten to the CURRENT module list: every module gets a row (the `start_lsp`
    hook reads the rows to know the valid (root, language) pairs, markup ones included), and
    rows of modules that no longer exist are dropped.
    """
    args = doc_mcp_args() if args is None else args
    cu = doc_bang(project)["module"]
    modules = do_module(project)
    bang = {"ngon_ngu": ngon_ngu_cua(modules), "module": {}}
    for m in modules:
        bang["module"][m["id"]] = dict(cu.get(m["id"]) or {}, **{k: m[k] for k in ("lang", "goc", "so_file", "moc")})
    ket_qua = []
    for m, tt, _ct in trang_thai(project, args, modules=modules):
        if tt not in CHAN or (chi_module and m["id"] != chi_module):
            continue
        kb = kich_ban(project, m)
        muc = {k: m[k] for k in ("lang", "goc", "so_file", "moc")}
        if kb is None:
            muc["ket_qua"] = {"trang_thai": KHONG_DU_MAU, "luc": _now(), "van_tay": van_tay(project, m, args),
                              "chi_tiet": "không symbol nào được dùng từ file thứ hai"}
        else:
            muc["kich_ban"] = kb
        bang["module"][m["id"]] = muc
        ket_qua.append((m, kb))
    ghi_bang(project, bang)
    return ket_qua


def ghi_ket_qua(project, module_id, so_tham_chieu, args=None):
    """Judge the reference count the agent got from `find_references` -> status. Raises ValueError."""
    args = doc_mcp_args() if args is None else args
    bang = doc_bang(project)
    muc = bang["module"].get(module_id)
    if not muc or not muc.get("kich_ban"):
        raise ValueError(f"module {module_id} chưa có kịch bản — chạy `tdq_lsp.py kich-ban` trước")
    kb = muc["kich_ban"]
    nguong = kb["so_lan_file_dinh_nghia"]
    dat = so_tham_chieu > nguong
    module = {"lang": muc["lang"], "goc": muc["goc"], "moc": muc.get("moc", "")}
    muc["ket_qua"] = {
        "trang_thai": DAT if dat else TRUOT, "luc": _now(), "van_tay": van_tay(project, module, args),
        "so_tham_chieu": so_tham_chieu,
        "chi_tiet": f"`{kb['symbol']}`: {so_tham_chieu} tham chiếu LSP so với {nguong} lần trong file định nghĩa"
                    + ("" if dat else " — LSP không thấy tham chiếu từ file khác"),
    }
    ghi_bang(project, bang)
    _log(f"ghi_ket_qua {module_id} → {muc['ket_qua']['trang_thai']}")
    return muc["ket_qua"]["trang_thai"]


# ── Brokers & memory ─────────────────────────────────────────────────────────────────────

def _doc_tien_trinh_mac_dinh():
    """-> [{pid, khoi_dong (epoch), lenh}] of agent-lsp processes. Infrastructure errors -> []."""
    if os.name == "nt":
        lenh = ["powershell", "-NoProfile", "-Command",
                "$ps = Get-CimInstance Win32_Process; $song = @{}; $ps | ForEach-Object { $song[$_.ProcessId] = 1 }; "
                "$ps | Where-Object { $_.Name -like 'agent-lsp*' } | Select-Object ProcessId,CreationDate,CommandLine,"
                "@{n='ChaSong';e={[bool]$song[$_.ParentProcessId]}} | ConvertTo-Json -Compress"]
        rc, ra = tdq_lsp._run(lenh, timeout=30)
        if rc != 0 or not ra.strip():
            return []
        try:
            du_lieu = json.loads(ra)
        except ValueError:
            return []
        du_lieu = du_lieu if isinstance(du_lieu, list) else [du_lieu]
        ket_qua = []
        for p in du_lieu:
            ngay = _RE_NGAY_WMI.search(str(p.get("CreationDate") or ""))
            ket_qua.append({"pid": int(p.get("ProcessId") or 0),
                            "khoi_dong": int(ngay.group(1)) / 1000 if ngay else 0.0,
                            "lenh": str(p.get("CommandLine") or ""), "cha_song": bool(p.get("ChaSong"))})
        return ket_qua
    rc, ra = tdq_lsp._run(["ps", "-eo", "pid=,ppid=,etimes=,args="], timeout=30)
    if rc != 0:
        return []
    bay_gio, ket_qua, dong_ps = time.time(), [], []
    for dong in ra.splitlines():
        phan = dong.split(None, 3)
        if len(phan) == 4 and all(x.isdigit() for x in phan[:3]):
            dong_ps.append(phan)
    song = {int(p[0]) for p in dong_ps}
    for pid, ppid, giay, lenh in dong_ps:
        if "agent-lsp" in lenh:
            ket_qua.append({"pid": int(pid), "khoi_dong": bay_gio - int(giay), "lenh": lenh,
                            "cha_song": int(ppid) in song and int(ppid) != 1})
    return ket_qua


def liet_ke_broker(doc=None):
    """-> [{pid, khoi_dong, lenh, goc, lang}] of `agent-lsp daemon-broker` processes only."""
    ket_qua = []
    for p in (doc or _doc_tien_trinh_mac_dinh)():
        lenh = p.get("lenh", "")
        if "agent-lsp" not in lenh or "daemon-broker" not in lenh:
            continue
        goc, lang = _RE_BROKER_GOC.search(lenh), _RE_BROKER_LANG.search(lenh)
        ket_qua.append(dict(p, goc=goc.group(1).strip('"') if goc else "", lang=lang.group(1) if lang else ""))
    return ket_qua


def broker_mo_coi(brokers):
    """Orphan = its root no longer exists, or a newer broker serves the same (root, language) AND
    nothing alive started it. Fail-safe both ways (code review 2026-10-08): a root that cannot be
    read off the command line is never an orphan, and an older duplicate whose parent is alive may
    still serve another live session, so it is left alone.
    """
    mo_coi, moi_nhat = [], {}
    for b in sorted(brokers, key=lambda b: -b["khoi_dong"]):
        if not b["goc"]:
            continue
        if not os.path.isdir(b["goc"]):
            mo_coi.append(b)
            continue
        cap = (os.path.normcase(os.path.normpath(b["goc"])), b["lang"])
        if cap not in moi_nhat:
            moi_nhat[cap] = b
        elif not b.get("cha_song", True):
            mo_coi.append(b)
    return mo_coi


def _tat_mac_dinh(pid):
    lenh = ["taskkill", "/PID", str(pid), "/F"] if os.name == "nt" else ["kill", str(pid)]
    return tdq_lsp._run(lenh, timeout=30)[0] == 0


def don_broker(doc=None, tat=None):
    """Stop orphan brokers -> [pid stopped]. Only processes whose command line names daemon-broker."""
    tat = tat or _tat_mac_dinh
    da_tat = []
    for b in broker_mo_coi(liet_ke_broker(doc)):
        if "daemon-broker" in b["lenh"] and tat(b["pid"]):
            da_tat.append(b["pid"])
            _log(f"tắt broker mồ côi pid={b['pid']} goc={b['goc'] or '?'} lang={b['lang'] or '?'}")
    return da_tat


def commit_trong_gb():
    """-> free commit memory in GB (Windows: commit limit; Linux: MemAvailable + SwapFree), or None."""
    if os.name == "nt":
        import ctypes

        class _TrangThaiBoNho(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        tt = _TrangThaiBoNho()
        tt.dwLength = ctypes.sizeof(tt)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(tt)):
            return None
        return tt.ullAvailPageFile / 1024 ** 3
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            kb = {d.split(":")[0]: int(d.split()[1]) for d in fh if d.split()[1:2] and d.split()[1].isdigit()}
    except OSError:
        return None
    return (kb.get("MemAvailable", 0) + kb.get("SwapFree", 0)) / 1024 ** 2


def canh_bao_commit(trong=None):
    """-> one warning line when free commit is under NGUONG_COMMIT_GB, else ''."""
    trong = commit_trong_gb() if trong is None else trong
    if trong is None or trong >= NGUONG_COMMIT_GB:
        return ""
    return (f"bộ nhớ commit chỉ còn {trong:.1f} GB trống (< {NGUONG_COMMIT_GB:.0f} GB) — language server có thể "
            "crash 0xc0000409. Tăng pagefile: System Properties → Advanced → Performance → Virtual memory "
            "(đặt System managed hoặc tăng kích thước), rồi đóng bớt ứng dụng/VM nặng.")
