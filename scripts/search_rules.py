#!/usr/bin/env python3
"""Search rules: classify a search command and decide allow/deny (spec §3, three rules).

Pure functions — no file, network or process I/O, no imports from hooks/ — because the gate calls
them before EVERY shell command.

- `phan_loai(cong_cu, lenh)` -> {"loai", "tu_khoa", "doan_mo"}:
  loai "loc_file" (grep over a file listing), "tim_code" (search that reads code) or
  "khong_phai_tim"; tu_khoa = the search alternatives; doan_mo = guess-list shape
  (>= 3 alternatives, or a natural-language phrase of >= 3 words).
- `quyet_dinh(pl, trang_thai)` -> (allowed, reason), rules in order: not a code search -> allow;
  every name already in the user's latest prompt -> allow; no concept query yet in this request
  -> deny; window of `cua_so` searches since the last concept query used up and guess-list shape
  -> deny; otherwise allow.
"""
import re
import shlex

# How many code searches one concept-layer query unlocks. Settled 2026-10-03 (T2.5) by REASON, not
# by measurement, and said so: replaying the excalidraw session gave the same result for N = 5, 10,
# 15 and 20 (16 denied, 0 wrongly, 0 slipped through), because every denial sits before the first
# lumen call and only 3 code searches come after it — the data only says N >= 2. Ten is one page
# of `semantic_search` results (default limit 8) plus a margin: one lumen answer names up to ~8
# places, and grepping them is exactly what the unlock is for. Re-measure once more real sessions
# exist: `python scripts/search_replay.py <transcript.jsonl> --cua-so N`.
CUA_SO = 10
# Same tokenizer the ledger uses for prompts (hooks/scripts/search_observe.py).
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

TIM_CODE, LOC_FILE, KHONG = "tim_code", "loc_file", "khong_phai_tim"
CONG_CU_SHELL = {"bash", "shell", "exec_command", "local_shell"}
CO_SCRIPT = {"-c", "-lc", "-ic", "-command", "/c"}

CHUONG_TRINH_TIM = {"grep", "egrep", "fgrep", "rg", "ag", "ack", "findstr", "select-string", "sls"}
LIET_KE = {"ls", "dir", "find", "fd", "fdfind", "tree", "get-childitem", "gci"}
DOC_FILE = {"cat", "type", "get-content", "gc"}
TU_KHOA_SHELL = {"do", "then", "else", "elif", "if", "while", "until", "!", "time", "{", "(", "(("}
TIEN_TO = {"sudo", "command", "nice", "exec", "builtin", "noglob", "nohup"}
GAN_BIEN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Short options whose value is the next argument (or the rest of the cluster).
GIA_TRI_NGAN = {
    "grep": "eAfBCmdD", "egrep": "eAfBCmdD", "fgrep": "eAfBCmdD", "git": "eAfBCm",
    "rg": "eAfBCmgtTjMErd", "ag": "ABCGgm", "ack": "ABCm",
}
GIA_TRI_DAI = {
    "--file", "--after-context", "--before-context", "--context", "--max-count", "--include",
    "--exclude", "--exclude-dir", "--exclude-from", "--label", "--glob", "--iglob", "--type",
    "--type-not", "--type-add", "--type-clear", "--max-depth", "--max-columns", "--max-filesize",
    "--encoding", "--replace", "--sort", "--sortr", "--threads", "--path-separator", "--pre",
    "--pre-glob", "--ignore-file", "--ignore", "--ignore-dir", "--devices", "--directories",
    "--binary-files", "--context-separator", "--group-separator",
}
SLS_CONG_TAC = {"simplematch", "casesensitive", "quiet", "list", "notmatch", "allmatches", "raw",
                "noemphasis"}
CHO_THAY = "$()"  # stands in for an extracted $( ... ) / `...` body inside its parent command
ONG = re.compile(r"\\\||(?<!\\)\|")
THOAT_CHU = re.compile(r"\\[A-Za-z]")
CAU_TU_NHIEN = re.compile(r"[A-Za-z]+(?: +[A-Za-z]+){2,}")
DO_SAU_TOI_DA = 8

LOI_RA = ("Ask first: mcp__plugin_lumen_lumen__semantic_search with a natural-language query "
          "(what/how/where), mcp__lsp__find_symbol / find_references (a symbol and its callers), "
          "or graphify query \"...\" (architecture).")


# ---------------------------------------------------------------- shell splitting

def _khop_ngoac(s, i):
    """Index of the ')' closing a '(' opened just before s[i]; len(s) when unbalanced."""
    sau, ngoac, n = 1, None, len(s)
    while i < n:
        c = s[i]
        if ngoac == "'":
            if c == "'":
                ngoac = None
        elif c == "\\":
            i += 1
        elif ngoac == '"':
            if c == '"':
                ngoac = None
        elif c in "'\"":
            ngoac = c
        elif c == "(":
            sau += 1
        elif c == ")":
            sau -= 1
            if sau == 0:
                return i
        i += 1
    return n


def _tach_script(s, do_sau=0):
    """Split a shell script into pipelines (lists of command strings), quote-aware.

    Separators: && || ; & newline; pipes: | and |&. Bodies of $( ... ), <( ... ) and backticks
    are parsed as pipelines of their own and replaced in the parent by a placeholder.
    """
    ong_list, phan, buf, con = [], [], [], []
    ngoac, i, n = None, 0, len(s)

    def het_phan():
        phan.append("".join(buf))
        buf.clear()

    def het_ong():
        het_phan()
        ong_list.append([p for p in phan if p.strip()])
        phan.clear()

    while i < n:
        c = s[i]
        if ngoac == "'":
            buf.append(c)
            if c == "'":
                ngoac = None
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            buf.append(s[i:i + 2])
            i += 2
            continue
        if (c == "$" or (c == "<" and ngoac is None)) and s.startswith("(", i + 1):
            j = _khop_ngoac(s, i + 2)
            con.append(s[i + 2:j])
            buf.append(CHO_THAY)
            i = j + 1
            continue
        if c == "`":
            j = s.find("`", i + 1)
            j = n if j < 0 else j
            con.append(s[i + 1:j])
            buf.append(CHO_THAY)
            i = j + 1
            continue
        if ngoac == '"':
            buf.append(c)
            if c == '"':
                ngoac = None
            i += 1
            continue
        if c in "'\"":
            ngoac = c
            buf.append(c)
        elif c == "#" and (i == 0 or s[i - 1].isspace()):
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        elif c == "|":
            if s.startswith("||", i):
                het_ong()
                i += 2
                continue
            het_phan()
            i += 2 if s.startswith("|&", i) else 1
            continue
        elif c == "&":
            if s.startswith("&&", i):
                het_ong()
                i += 2
                continue
            if (i and s[i - 1] in "<>") or s.startswith(">", i + 1):
                buf.append(c)
            else:
                het_ong()
        elif c in ";\n":
            het_ong()
        else:
            buf.append(c)
        i += 1
    het_ong()
    if do_sau < DO_SAU_TOI_DA:
        for than in con:
            ong_list.extend(_tach_script(than, do_sau + 1))
    return [o for o in ong_list if o]


def _tach_tu(phan):
    """argv of one command; best effort when quotes are unbalanced."""
    try:
        return shlex.split(phan, posix=True)
    except ValueError:
        return [t.strip("'\"") for t in re.findall(r"\"[^\"]*\"?|'[^']*'?|\S+", phan)]


def _bo_tuy_chon(argv):
    while argv and argv[0].startswith("-"):
        argv = argv[1:]
    return argv


def _chuan_hoa(argv):
    """Strip VAR=x, sudo, env, timeout N, xargs, shell keywords. Returns (program, args, via_xargs)."""
    qua_xargs = False
    while argv:
        t = argv[0]
        tl = t.lower()
        if tl in TU_KHOA_SHELL or GAN_BIEN.match(t):
            argv = argv[1:]
        elif t[:1] in "({" and len(t) > 1:
            argv = [t.lstrip("({")] + argv[1:]
        elif tl in TIEN_TO:
            argv = _bo_tuy_chon(argv[1:])
        elif tl == "env":
            argv = argv[1:]
            while argv and (argv[0].startswith("-") or GAN_BIEN.match(argv[0])):
                argv = argv[1:]
        elif tl == "timeout":
            argv = _bo_tuy_chon(argv[1:])[1:]
        elif tl == "xargs":
            qua_xargs = True
            argv = argv[1:]
            while argv and argv[0].startswith("-"):
                argv = argv[2:] if argv[0] in ("-I", "-n", "-P", "-d", "-L", "-s", "-E") else argv[1:]
        else:
            break
    if not argv:
        return "", [], qua_xargs
    ten = argv[0].replace("\\", "/").rsplit("/", 1)[-1].lower().rstrip(")}")
    if ten.endswith(".exe"):
        ten = ten[:-4]
    return ten, argv[1:], qua_xargs


def _git_lenh_con(args):
    """(subcommand, rest) of a git invocation, skipping global options like -C dir."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    return (args[i], args[i + 1:]) if i < len(args) else ("", [])


def _kieu(ten, args):
    """'search' | 'listing' | 'reader' | 'other' for one pipeline part."""
    if ten == "git":
        con, _ = _git_lenh_con(args)
        return {"grep": "search", "ls-files": "listing"}.get(con, "other")
    if ten == "rg" and "--files" in args:
        return "listing"
    if ten in CHUONG_TRINH_TIM:
        return "search"
    if ten in LIET_KE:
        return "listing"
    if ten in DOC_FILE:
        return "reader"
    return "other"


# ---------------------------------------------------------------- pattern extraction

def _mau_kieu_grep(ten, args):
    """Patterns of grep/rg/ag/ack/git grep: every -e/--regexp, else the first positional."""
    ngan = GIA_TRI_NGAN.get(ten, GIA_TRI_NGAN["grep"])
    mau, vi_tri, tu_file, het_tuy_chon, i = [], None, False, False, 0
    while i < len(args):
        a = args[i]
        if not het_tuy_chon and a == "--":
            het_tuy_chon = True
        elif not het_tuy_chon and a.startswith("--"):
            ten_dai, co_bang, gia_tri = a.partition("=")
            if ten_dai == "--regexp":
                if not co_bang:
                    i += 1
                    gia_tri = args[i] if i < len(args) else ""
                mau.append(gia_tri)
            elif ten_dai == "--file":
                tu_file = True
                i += 0 if co_bang else 1
            elif not co_bang and ten_dai in GIA_TRI_DAI:
                i += 1
        elif not het_tuy_chon and a.startswith("-") and len(a) > 1:
            chu = a[1:]
            for k, ch in enumerate(chu):
                if ch in ngan:
                    gia_tri = chu[k + 1:]
                    if not gia_tri:
                        i += 1
                        gia_tri = args[i] if i < len(args) else ""
                    if ch == "e":
                        mau.append(gia_tri)
                    elif ch == "f":
                        tu_file = True
                    break
        elif vi_tri is None:
            vi_tri = a
        i += 1
    if mau:
        return mau
    if tu_file or vi_tri is None:
        return []
    return [vi_tri]


def _mau_findstr(args):
    """findstr: /C:"text" is one literal; otherwise the first argument's words are alternatives."""
    for a in args:
        if a[:3].lower() == "/c:":
            return [a[3:]], False
    for a in args:
        if a[:3].lower() == "/g:":
            return [], False
        if not a.startswith("/"):
            return a.split(), True
    return [], False


def _mau_select_string(args):
    vi_tri, i = None, 0
    while i < len(args):
        a = args[i]
        if a.startswith("-") and len(a) > 1:
            ten = a[1:].lower().rstrip(":")
            if len(ten) >= 3 and "pattern".startswith(ten):
                return [args[i + 1]] if i + 1 < len(args) else []
            if ten not in SLS_CONG_TAC:
                i += 1
        elif vi_tri is None:
            vi_tri = a
        i += 1
    return [vi_tri] if vi_tri is not None else []


def _nhanh(mau):
    """Alternatives of a regex: split on `\\|` and unescaped `|`."""
    return [p.strip() for p in ONG.split(mau) if p.strip()]


def _hinh_mau(cac_mau):
    """(alternatives, guess-list shape) for a list of patterns."""
    nhanh = []
    for m in cac_mau:
        nhanh.extend(_nhanh(m))
    doan_mo = len(nhanh) >= 3 or any(CAU_TU_NHIEN.fullmatch(m.strip()) for m in cac_mau)
    return nhanh, bool(doan_mo)


def _lan_tim(ten, args):
    """(alternatives, doan_mo) of one search part."""
    if ten == "findstr":
        cac_mau, la_tu = _mau_findstr(args)
        if la_tu:
            return cac_mau, len(cac_mau) >= 3
        return _hinh_mau(cac_mau)
    if ten in ("select-string", "sls"):
        return _hinh_mau(_mau_select_string(args))
    if ten == "git":
        args = _git_lenh_con(args)[1]
    return _hinh_mau(_mau_kieu_grep(ten, args))


# ---------------------------------------------------------------- classification

def _script_cua(lenh):
    """Script text of a command given as a string or as an argv list (Codex)."""
    if isinstance(lenh, (list, tuple)):
        phan = [str(x) for x in lenh]
        for k, a in enumerate(phan[:-1]):
            if a.lower() in CO_SCRIPT:
                return phan[k + 1]
        return " ".join(shlex.quote(a) for a in phan)
    return "" if lenh is None else str(lenh)


def _phan_loai_ong(cac_phan):
    """Yield (loai, alternatives, doan_mo) for every search part of one pipeline."""
    da_chuan = [_chuan_hoa(_tach_tu(p)) for p in cac_phan]
    kieu = [_kieu(ten, args) for ten, args, _ in da_chuan]
    for k, (ten, args, qua_xargs) in enumerate(da_chuan):
        if kieu[k] != "search":
            continue
        if k == 0 or qua_xargs:
            loai = TIM_CODE
        elif kieu[0] == "listing":
            # PowerShell pipes file objects: Select-String then reads the files themselves.
            loai = TIM_CODE if ten in ("select-string", "sls") else LOC_FILE
        elif kieu[0] == "reader":
            loai = TIM_CODE
        else:
            loai = KHONG
        nhanh, doan_mo = _lan_tim(ten, args) if loai == TIM_CODE else ([], False)
        yield loai, nhanh, doan_mo


def _du_phong(script):
    """Regex best effort when the structured parse fails: any search program -> tim_code."""
    m = re.search(r"(?<![\w-])(grep|egrep|fgrep|rg|ag|ack|findstr|select-string|sls)(?![\w-])"
                  r"[^\n'\"]*?(['\"])(.*?)\2", script, re.I)
    if m:
        nhanh, doan_mo = _hinh_mau([m.group(3)])
        return {"loai": TIM_CODE, "tu_khoa": nhanh, "doan_mo": doan_mo}
    if re.search(r"(?<![\w-])(grep|egrep|fgrep|rg|ag|ack|findstr|select-string|sls)(?![\w-])",
                 script, re.I):
        return {"loai": TIM_CODE, "tu_khoa": [], "doan_mo": False}
    return {"loai": KHONG, "tu_khoa": [], "doan_mo": False}


def phan_loai(cong_cu, lenh):
    """Classify a Grep pattern or a shell command. Returns {"loai", "tu_khoa", "doan_mo"}."""
    if cong_cu == "Grep":
        mau = lenh.get("pattern", "") if isinstance(lenh, dict) else _script_cua(lenh)
        nhanh, doan_mo = _hinh_mau([mau])
        return {"loai": TIM_CODE, "tu_khoa": nhanh, "doan_mo": doan_mo}
    if str(cong_cu).lower() not in CONG_CU_SHELL:
        return {"loai": KHONG, "tu_khoa": [], "doan_mo": False}
    script = _script_cua(lenh)
    try:
        ket_qua = [r for ong in _tach_script(script) for r in _phan_loai_ong(ong)]
    except Exception:  # noqa: BLE001 — the gate must never break on an odd command
        return _du_phong(script)
    tim = [r for r in ket_qua if r[0] == TIM_CODE]
    if tim:
        tu_khoa = []
        for _, nhanh, _ in tim:
            tu_khoa.extend(x for x in nhanh if x not in tu_khoa)
        return {"loai": TIM_CODE, "tu_khoa": tu_khoa, "doan_mo": any(r[2] for r in tim)}
    loai = LOC_FILE if any(r[0] == LOC_FILE for r in ket_qua) else KHONG
    return {"loai": loai, "tu_khoa": [], "doan_mo": False}


# ---------------------------------------------------------------- decision

def _token(nhanh):
    toks = []
    for x in nhanh:
        toks.extend(TOKEN.findall(THOAT_CHU.sub(" ", x)))
    return toks


def quyet_dinh(pl, trang_thai):
    """Apply the three rules of spec §3 in order. Returns (allowed, reason)."""
    loai = pl.get("loai")
    if loai == LOC_FILE:
        return True, "file-list filtering"
    if loai != TIM_CODE:
        return True, "not a code search"
    nhanh = pl.get("tu_khoa") or []
    toks = _token(nhanh)
    prompt = {str(t).lower() for t in trang_thai.get("token_prompt") or ()}
    if toks and all(t.lower() in prompt for t in toks):
        return True, "every name is in the user's prompt"
    cua_so = trang_thai.get("cua_so", CUA_SO)
    sau_cua_so = (f"Then exact names may be grepped for the next {cua_so} searches; "
                  "a name the user typed in the prompt is exempt.")
    if not trang_thai.get("da_goi_khai_niem"):
        return False, ("[TDQ:SEARCH] Code search before any concept query in this request.\n"
                       f"{LOI_RA}\n{sau_cua_so}")
    so_lan = trang_thai.get("so_lan_tim_tu_lan_goi", 0)
    if so_lan >= cua_so and pl.get("doan_mo"):
        return False, (f"[TDQ:SEARCH] Guess-list search ({len(nhanh)} alternatives); the last "
                       f"concept query was {so_lan} searches ago (window {cua_so}).\n"
                       f"{LOI_RA.replace('Ask first', 'Ask again')}\n{sau_cua_so}")
    if so_lan < cua_so:
        return True, "inside the unlock window"
    return True, "exact name after a concept query"
