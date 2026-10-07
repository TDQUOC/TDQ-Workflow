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
# concept call and only 3 code searches come after it — the data only says N >= 2. Ten was sized
# from one page of lumen results (~8 places) plus a margin; a `find_references` or `graphify query`
# answer names a similar handful of places, and grepping them is exactly what the unlock is for. Re-measure once more real sessions
# exist: `python scripts/search_replay.py <transcript.jsonl> --cua-so N`.
CUA_SO = 10
# Same tokenizer the ledger uses for prompts (hooks/scripts/search_observe.py).
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

TIM_CODE, LOC_FILE, KHONG = "tim_code", "loc_file", "khong_phai_tim"
CONG_CU_SHELL = {"bash", "powershell", "shell", "exec_command", "local_shell"}
# Readiness stamp: `tdq_setup.khoi_tao_nen` writes it, the gate and session start read it.
# One name for all three (T8.6); a relative path with "/" joins fine on every OS.
MOC_SAN_SANG = "docs/tdq/.tdq-san-sang.json"
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
# Shells whose `-c`/`-Command`/`/c` string is itself a script: `bash -c 'grep foo .'` is a
# search, and the first version read it as one opaque command (review 2026-10-03, R1#7).
SHELL_BOC = {"bash", "sh", "zsh", "dash", "ksh", "pwsh", "powershell", "cmd"}
# Searching only in these is reading documents, not code (review 2026-10-03, R1#5): the rule
# is about how an agent finds CODE. Directory names count too (`grep -rn x docs/`).
DUOI_TAI_LIEU = {".md", ".markdown", ".rst", ".txt", ".log", ".json", ".jsonl", ".yml",
                 ".yaml", ".toml", ".ini", ".cfg", ".csv", ".lock"}
THU_MUC_TAI_LIEU = {"docs", "doc", "documentation"}
LOAI_TAI_LIEU = {"md", "markdown", "txt", "json", "yaml", "yml", "toml", "csv", "log", "rst"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
CHI_HOI = {"--help", "--version"}
TUY_CHON_CO_GIA_TRI = {"--file", "--regexp", "--glob", "-g", "--type", "-t", "--include",
                       "--exclude", "--max-count", "-Path", "-Pattern", "-Include", "-Exclude"}

# The concept layers a denial may point to, each with the call that asks it, in the order of the
# search rule. lumen was the first entry until 0.58.0: measured 2026-10-07, a denial that opened
# with it sent the agent hunting for a tool that no longer existed (one wasted `ToolSearch`).
# `start_lsp` comes FIRST and names `language_id`: in a fresh session `find_symbol` answers "LSP
# client not initialized", and `start_lsp` without a language started the TypeScript server on a
# Python repo ("No Project", a crashed server) — 2-3 wasted calls per session, measured the same day.
LOP_KHAI_NIEM = (
    ("lsp", "mcp__lsp__start_lsp (root_dir = the project root, language_id = the language of the "
            "code, e.g. python) then mcp__lsp__find_symbol / find_references (a symbol and its "
            "callers)"),
    ("graphify", "graphify query \"<question>\" (a concept in plain words, or the architecture)"),
)


def loi_nhac(tang_song=None):
    """-> the "ask first" line, naming only the live concept layers.

    `tang_song` comes from the readiness stamp; None means no stamp (Codex, or never built) and
    names every layer. A layer the stamp does not mark live is left out: pointing an agent at a
    tool that cannot answer is the wasted turn this function exists to remove.
    """
    lop = [cach for ten, cach in LOP_KHAI_NIEM if tang_song is None or ten in tang_song]
    return "Ask first: " + "; or ".join(lop or [cach for _, cach in LOP_KHAI_NIEM]) + "."



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
    _mau_kieu_grep.tu_file = tu_file
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
    nhanh, doan_mo = _hinh_mau(_mau_kieu_grep(ten, args))
    if getattr(_mau_kieu_grep, "tu_file", False):
        # `-f patterns.txt`: a guess-list moved into a file is still a guess-list (R1#9).
        doan_mo = True
    return nhanh, doan_mo


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


def _bo_heredoc(script):
    """Drop heredoc BODIES: `cat > x.sh <<'EOF'` followed by a `grep` line is writing a file, not
    searching. The first version split the body into commands (review 2026-10-03, R1#4)."""
    if "<<" not in script:
        return script
    ra, cho = [], []
    for dong in script.split("\n"):
        if cho:
            if dong.strip() == cho[0]:
                cho.pop(0)
            continue
        ra.append(dong)
        cho = [m.group(2) for m in HEREDOC.finditer(dong)]
    return "\n".join(ra)


def _la_tai_lieu(duong):
    """A path that is a document, not code: its extension, or a docs directory in it."""
    p = str(duong).replace("\\", "/").strip("'\"").rstrip("/")
    if not p or p.startswith("-"):
        return False
    phan = [x for x in p.split("/") if x not in ("", ".")]
    if any(x.lower() in THU_MUC_TAI_LIEU for x in phan):
        return True
    ten = phan[-1].lower() if phan else ""
    return any(ten.endswith(d) for d in DUOI_TAI_LIEU)


def _chi_tim_tai_lieu(args, nhanh):
    """True when the search names explicit targets and ALL of them are documents.

    The VALUE of an option is never a target: in `grep -f pats.txt src` the `.txt` is the pattern
    file, and counting it made a code search look like reading documents.
    """
    dich, bo_qua = [], False
    for a in args:
        if bo_qua:
            bo_qua = False
            continue
        if a.startswith("-"):
            ten = a.split("=", 1)[0]
            bo_qua = "=" not in a and (ten in TUY_CHON_CO_GIA_TRI
                                       or (not ten.startswith("--") and ten[-1:] in "efABCm"))
            continue
        if a not in nhanh and ("/" in a or "\\" in a or "." in a.lstrip(".")):
            dich.append(a)
    return bool(dich) and all(_la_tai_lieu(a) for a in dich)


def _script_boc(ten, args):
    """The inner script of `bash -c '…'`, `pwsh -Command …`, `cmd /c …`, else None."""
    if ten not in SHELL_BOC:
        return None
    for k, a in enumerate(args):
        if a.lower() in CO_SCRIPT and k + 1 < len(args):
            return " ".join(args[k + 1:]) if ten == "cmd" else args[k + 1]
    return None


def _tim_trong_exec(args):
    """(program, args) of `find … -exec <prog> … ;` when <prog> is a search program."""
    for k, a in enumerate(args):
        if a in ("-exec", "-execdir", "-ok") and k + 1 < len(args):
            con = []
            for b in args[k + 1:]:
                if b in (";", "\\;", "+"):
                    break
                con.append(b)
            if con:
                ten, rest, _ = _chuan_hoa(con)
                if _kieu(ten, rest) == "search":
                    return ten, rest
    return None


def _phan_loai_ong(cac_phan, do_sau=0):
    """Yield (loai, alternatives, doan_mo) for every search part of one pipeline."""
    da_chuan = [_chuan_hoa(_tach_tu(p)) for p in cac_phan]
    kieu = [_kieu(ten, args) for ten, args, _ in da_chuan]
    for k, (ten, args, qua_xargs) in enumerate(da_chuan):
        boc = _script_boc(ten, args)
        if boc is not None and do_sau < DO_SAU_TOI_DA:
            for ong in _tach_script(_bo_heredoc(boc)):
                yield from _phan_loai_ong(ong, do_sau + 1)
            continue
        if ten == "find":
            ex = _tim_trong_exec(args)
            if ex:
                nhanh, doan_mo = _lan_tim(*ex)
                yield (KHONG if _chi_tim_tai_lieu(args, nhanh) else TIM_CODE), nhanh, doan_mo
            continue
        if kieu[k] != "search":
            continue
        if CHI_HOI & set(args) or args == ["-V"]:
            continue                      # `grep --help` asks the program, not the code (R1#3)
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
        if loai == TIM_CODE and _chi_tim_tai_lieu(args, nhanh):
            loai, nhanh, doan_mo = KHONG, [], False
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
        vao = lenh if isinstance(lenh, dict) else {"pattern": _script_cua(lenh)}
        nhanh, doan_mo = _hinh_mau([vao.get("pattern") or ""])
        loc = str(vao.get("glob") or "")
        if (str(vao.get("type") or "").lower() in LOAI_TAI_LIEU
                or (loc and _la_tai_lieu(loc.replace("*", "x")))
                or (vao.get("path") and _la_tai_lieu(vao.get("path")))):
            return {"loai": KHONG, "tu_khoa": [], "doan_mo": False}
        return {"loai": TIM_CODE, "tu_khoa": nhanh, "doan_mo": doan_mo}
    if str(cong_cu).lower() not in CONG_CU_SHELL:
        return {"loai": KHONG, "tu_khoa": [], "doan_mo": False}
    script = _bo_heredoc(_script_cua(lenh))
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
    nhac = loi_nhac(trang_thai.get("tang_song"))
    if not trang_thai.get("da_goi_khai_niem"):
        return False, ("[TDQ:SEARCH] Code search before any concept query in this request.\n"
                       f"{nhac}\n{sau_cua_so}")
    so_lan = trang_thai.get("so_lan_tim_tu_lan_goi", 0)
    if so_lan >= cua_so and pl.get("doan_mo"):
        return False, (f"[TDQ:SEARCH] Guess-list search ({len(nhanh)} alternatives); the last "
                       f"concept query was {so_lan} searches ago (window {cua_so}).\n"
                       f"{nhac.replace('Ask first', 'Ask again')}\n{sau_cua_so}")
    if so_lan < cua_so:
        return True, "inside the unlock window"
    return True, "exact name after a concept query"


# ---------------------------------------- concept-layer calls and request state (pure, shared)
# These two used to live in `hooks/scripts/search_observe.py`, and the replay kept its OWN copy of
# the state logic — with a different meaning (it counted denied searches toward the window and
# every `mcp__lsp__*` call as a concept query). The replay is in `scripts/` and may not import
# `hooks/`, so the one shared copy has to live here; the ledger hook imports it from here.

# Name shapes differ by host: Claude Code says `mcp__lsp__find_references`; Codex MCP names could
# not be observed yet (Codex not logged in on the dev machine, 2026-10-03), so the match is on the
# server name and the last segment. lumen `semantic_search` counted until 0.58.0.
LSP = re.compile(r"(^|__|\.)lsp(__|\.)")
# LSP tools that ASK a question about the code — an ALLOWLIST. The first version excluded a list
# of housekeeping tools instead, which let `run_tests`, `apply_edit` or `format_document` count as
# a concept query and unlock grep without a single question asked.
LSP_HOI = re.compile(r"^(find_\w+|go_to_\w+|inspect_symbol|explore\w*|list_symbols|blast_radius|"
                     r"type_hierarchy|get_cross_repo_references|get_document_highlights|"
                     r"get_symbol_\w+|get_tests_for_file)$")
GRAPHIFY_HOI = {"query", "explain", "path", "god-nodes", "affected"}


def la_goi_khai_niem(ten_tool, tool_input):
    """-> a short label when this tool call is a concept-layer QUERY, else None.

    `graphify` is recognised by PARSING the shell command — its program and its subcommand — not
    by searching the text: `echo graphify query x` or a commit message mentioning it must not
    unlock anything (both did, in the first version).
    """
    ten = str(ten_tool or "")
    if LSP.search(ten):
        cuoi = re.split(r"__|\.", ten)[-1]
        return f"lsp:{cuoi}" if LSP_HOI.match(cuoi) else None
    if ten.lower() in CONG_CU_SHELL or ten.lower() == "powershell":
        vao = tool_input or {}
        script = _script_cua(vao.get("command") or vao.get("cmd") or "")
        try:
            cac_ong = _tach_script(script)
        except Exception:  # noqa: BLE001 — a recognizer never raises into a hook
            return None
        for ong in cac_ong:
            for phan in ong:
                ten_ct, args, _ = _chuan_hoa(_tach_tu(phan))
                if ten_ct == "graphify" and args and args[0] in GRAPHIFY_HOI:
                    return f"graphify:{args[0]}"
    return None


def trang_thai(rows):
    """-> the state `quyet_dinh` needs, built from one scope's ledger rows (oldest first).

    * `so_lan_tim_tu_lan_goi` counts code searches that RAN after the latest concept query —
      a denied search never executed, so it never eats into the window. Asking again re-opens it.
    * `so_lan_bi_chan` counts searches DENIED since the latest concept query (or since the
      start): the gate's breaker for a machine where no concept tool can answer.
    * `token_prompt` is the token set of the latest prompt only.
    """
    da_goi, dem, bi_chan, token = False, 0, 0, set()
    for row in rows:
        loai = row.get("loai")
        if loai == "khai_niem":
            da_goi, dem, bi_chan = True, 0, 0
        elif loai == "tim":
            if row.get("tinh_cua_so", True):
                dem += 1
            if row.get("cho_phep") is False:
                bi_chan += 1
        elif loai == "prompt":
            token = set(row.get("token") or [])
    return {"da_goi_khai_niem": da_goi, "so_lan_tim_tu_lan_goi": dem,
            "so_lan_bi_chan": bi_chan, "token_prompt": token}
