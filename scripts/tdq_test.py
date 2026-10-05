#!/usr/bin/env python3
"""Impact radius of a set of changed files: which test modules must run.

Intermediate steps run only the tests of the touched zone plus its impact radius; the full
suite runs at two gates only (QC-F1, and after the last QC fix round). This module computes the
radius. `ban_kinh(files, repo)` is pure: it reads files under `repo`, never runs a subprocess,
never writes, and never imports anything from `hooks/` (hook sources are read with `ast`).

A test module is selected when any of these holds (union):

- (a) it IS a changed test file;
- (b) its source mentions the changed file's repo-relative path (forward or back slashes, or
  split into string segments as in `os.path.join(ROOT, "skills", "x", "SKILL.md")`). Files under
  `skills/`, `agents/`, and data files outside `TOP_DIRS` (e.g. `docs/...`) match by PATH only
  — a bare `SKILL.md` matches every skill (the prototype over-selected 37 modules that way).
  Other files also match by bare file name;
- (c) for a changed `.py` under `scripts/` or `hooks/scripts/`: it mentions, as a word or as
  `name.py`, any module of the reverse transitive import closure (AST, imports inside functions
  included) among those two dirs. Matching the NAME, not only the import, catches tests that
  run hooks through a subprocess (`run_hook("stop_gate.py", ...)`). For a changed non-test
  `.py` directly under `tests/` (e.g. `helper.py`): it belongs to that module's reverse
  transitive import closure among `tests/*.py` (AST imports only — a bare word `helper` is too
  common to match by name);
- (d) it SCANS the top-level dir of a changed file: an AST call to `os.walk`, `os.listdir`,
  `os.scandir`, `glob.glob`, `glob.iglob`, `Path.glob`/`rglob`/`iterdir` whose path expression
  holds a string constant naming that dir. Names are resolved through local assignments, `for`
  targets, `with` targets, attribute assignments and the call sites of the enclosing function,
  so `SKILLS = os.path.join(ROOT, "skills")` then `os.walk(SKILLS)` is caught.

The caller must run the full suite instead (`ly_do_tron_bo` is set, `modules` is every module)
when a changed CODE file or file of unknown kind lies outside `TOP_DIRS` (only the kinds in
`DATA_EXTS` / `DATA_NAMES` count as data — when unsure, run everything; a data file outside
`TOP_DIRS` selects only the tests naming its path, and none when no test does — spec deviation
#1, Q4), a changed `.py` cannot be parsed, or the selection
reaches `NGUONG_TRON_BO` of all modules — at that size one full-suite process is cheaper than
picking, and safer.

Measured by the prototype in the brief (2026-10-03, 126 modules, name + import matching only):
leaf files (`ask_gate.py`, `tdq_bench.py`) 2 modules; `stop_gate.py` 11 (29 s instead of 353.9 s);
`qc.md` 7 (22 s); `_common.py` 38 (30%); the hub `tdq_state.py` / `doc_lint.py` 96-102 (76%+),
where the full suite is the right call. Rule (d) adds the directory scanners on top of that.

CLI (`python scripts/tdq_test.py <command>`):

- `vung-cham [--files F ...] [--repo DIR]`: run the tests of the touched zone. Without
  `--files` the file set is `git diff --name-only <nhanh_goc>...HEAD` plus every uncommitted
  change (staged, unstaged, untracked); `nhanh_goc` comes from `docs/tdq/state.json` (fallback
  `main`). When git fails, or `ban_kinh` gives a reason, the full suite runs instead. The
  selected modules run in ONE process (`unittest` loader); exit 0 when green, 1 otherwise. One
  JSON row goes to the ledger `docs/tdq/.tdq-test.jsonl`.
- `tron-bo [--repo DIR]`: run every test module in ONE process; exit 0/1. One `tron-bo` row
  (with `failed_modules`), then one `bo-sot` row per red module that no `vung-cham` row of the
  same request selected (none when such a row fell back to the full suite): the radius missed it.
- `so [--json] [--repo DIR]`: for the active request, the number of `tron-bo` runs, of `bo-sot`
  rows, the missed modules, and the full-suite budget (`dem()`; 2, or 3 after a red `tron-bo`).

Log service: one ISO-timestamped line per command on stderr, on by default; `TDQ_LOG=0` turns
it off. Only paths, counts and reasons are logged, never file contents.
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
import unittest
from datetime import datetime

TOP_DIRS = frozenset({"scripts", "hooks", "skills", "tests", "agents"})
# Under these top dirs a file matches by path only; so does every file outside `TOP_DIRS`.
PATH_ONLY_DIRS = frozenset({"skills", "agents"})
SOURCE_DIRS = ("scripts", "hooks/scripts")
TEST_DIR = "tests"
# Data kinds: outside `TOP_DIRS` these match by path only. Anything else there (`.py .ps1 .sh
# .js .ts .cmd .bat`, or an extension not listed) is code or unknown -> the full suite runs.
DATA_EXTS = frozenset({".md", ".json", ".jsonl", ".txt", ".yml", ".yaml", ".toml", ".csv",
                       ".png", ".svg"})
DATA_NAMES = frozenset({".gitignore", ".gitattributes", "LICENSE"})
NGUONG_TRON_BO = 0.6

# Directory-scanning functions -> the module that owns them (a bare name means `from X import f`).
MODULE_SCAN_FUNCS = {"walk": ("os",), "listdir": ("os",), "scandir": ("os",),
                     "glob": ("glob",), "iglob": ("glob",)}
PATH_SCAN_METHODS = frozenset({"glob", "rglob", "iterdir"})
KNOWN_MODULES = frozenset({"os", "glob", "ast", "re", "fnmatch", "pathlib"})
RESOLVE_DEPTH = 5
# Between two path segments in test source: a slash, or a quote-comma-quote / quote-slash-quote
# seam left by `os.path.join(..., "a", "b")` and `Path(...) / "a" / "b"`.
SEGMENT_SEAM = r"""(?:[/\\]+|["']\s*[,/]\s*r?["'])"""


# ---------- paths and the test universe ----------

def chuan_hoa(path):
    """Repo-relative path with forward slashes and no leading `./`."""
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.strip("/")


def tat_ca_module(repo):
    """Every `tests/test_*.py` file name, sorted."""
    tests_dir = os.path.join(repo, "tests")
    if not os.path.isdir(tests_dir):
        return []
    return sorted(n for n in os.listdir(tests_dir)
                  if n.startswith("test_") and n.endswith(".py"))


def _doc(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _nguon_test(repo):
    """{test module name: source text}."""
    return {m: _doc(os.path.join(repo, "tests", m)) for m in tat_ca_module(repo)}


# ---------- (b) path mentions ----------

def _mau_duong_dan(path):
    """Regexes that count as a mention of `path` inside test source."""
    segs = path.split("/")
    patterns = [SEGMENT_SEAM.join(re.escape(s) for s in segs)]
    if len(segs) >= 3:  # the path below the top dir, e.g. `tdq-build/references/qc.md`
        patterns.append(SEGMENT_SEAM.join(re.escape(s) for s in segs[1:]))
    if segs[0] in TOP_DIRS and segs[0] not in PATH_ONLY_DIRS:
        patterns.append(re.escape(segs[-1]))
    return [re.compile(r"(?<![\w.-])" + p + r"(?![\w-])") for p in patterns]


def chon_theo_duong_dan(path, sources):
    patterns = _mau_duong_dan(path)
    return {m for m, src in sources.items() if any(p.search(src) for p in patterns)}


# ---------- (c) reverse import closure ----------

def _ten_import(tree):
    """Top-level module names a parsed file imports, anywhere in its body."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module and not node.level:
                names.add(node.module.split(".")[0])
            elif not node.module:
                names.update(a.name for a in node.names)
    return names


def do_thi_import(repo, dirs=SOURCE_DIRS):
    """{module name: set of module names it imports} over the `.py` files directly in `dirs`."""
    graph = {}
    for d in dirs:
        folder = os.path.join(repo, *d.split("/"))
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".py"):
                continue
            try:
                tree = ast.parse(_doc(os.path.join(folder, name)))
            except SyntaxError:
                continue
            graph.setdefault(name[:-3], set()).update(_ten_import(tree))
    return graph


def bao_dong_nguoc(start, graph):
    """`start` plus every module that imports it, directly or transitively."""
    closure, frontier = {start}, [start]
    while frontier:
        target = frontier.pop()
        for mod, imports in graph.items():
            if target in imports and mod not in closure:
                closure.add(mod)
                frontier.append(mod)
    return closure


def chon_theo_ten_module(names, sources):
    if not names:
        return set()
    alt = "|".join(re.escape(n) for n in sorted(names))
    pattern = re.compile(r"(?<![\w.])(?:" + alt + r")(?:\.py)?(?!\w)")
    return {m for m, src in sources.items() if pattern.search(src)}


# ---------- (d) directory scanners ----------

class _BangTen(ast.NodeVisitor):
    """name -> expressions it may hold: assignments, loop/with targets, parameters by call site."""

    def __init__(self):
        self.values = {}
        self.params = {}  # function name -> list of parameter names
        self.calls = []

    def _gan(self, target, value):
        if isinstance(target, ast.Name):
            self.values.setdefault(target.id, []).append(value)
        elif isinstance(target, ast.Attribute):
            self.values.setdefault("." + target.attr, []).append(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            same = isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(target.elts)
            for i, elt in enumerate(target.elts):
                self._gan(elt, value.elts[i] if same else value)
        elif isinstance(target, ast.Starred):
            self._gan(target.value, value)

    def visit_Assign(self, node):
        for t in node.targets:
            self._gan(t, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            self._gan(node.target, node.value)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self._gan(node.target, node.value)
        self.generic_visit(node)

    def visit_NamedExpr(self, node):
        self._gan(node.target, node.value)
        self.generic_visit(node)

    def visit_For(self, node):
        self._gan(node.target, node.iter)
        self.generic_visit(node)

    visit_AsyncFor = visit_For

    def visit_comprehension(self, node):
        self._gan(node.target, node.iter)
        self.generic_visit(node)

    def visit_withitem(self, node):
        if node.optional_vars is not None:
            self._gan(node.optional_vars, node.context_expr)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        args = node.args
        names = [a.arg for a in args.posonlyargs + args.args]
        self.params[node.name] = names
        for arg, default in zip(reversed(names), reversed(args.defaults)):
            self.values.setdefault(arg, []).append(default)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        self.calls.append(node)
        self.generic_visit(node)

    def gan_tham_so(self):
        """Bind each function parameter to the arguments its call sites pass."""
        for call in self.calls:
            fn = call.func
            fname = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
            names = self.params.get(fname)
            if not names:
                continue
            skip = 1 if isinstance(fn, ast.Attribute) and names[0] in ("self", "cls") else 0
            for name, arg in zip(names[skip:], call.args):
                self.values.setdefault(name, []).append(arg)
            for kw in call.keywords:
                if kw.arg in names:
                    self.values.setdefault(kw.arg, []).append(kw.value)


def _bieu_thuc_quet(call):
    """Path expressions a scanning call reads, or [] when the call is not a scan.

    `os.walk` / `glob.glob` take the path as an argument; `Path.glob` / `rglob` / `iterdir` scan
    their receiver. Any other receiver of `walk` (e.g. `ast.walk(tree)`) is not a scan."""
    fn = call.func
    args = list(call.args) + [kw.value for kw in call.keywords]
    if isinstance(fn, ast.Name):
        return args if fn.id in MODULE_SCAN_FUNCS else []
    if not isinstance(fn, ast.Attribute):
        return []
    receiver = fn.value
    if isinstance(receiver, ast.Name) and receiver.id in MODULE_SCAN_FUNCS.get(fn.attr, ()):
        return args
    if fn.attr in PATH_SCAN_METHODS and not (
            isinstance(receiver, ast.Name) and receiver.id in KNOWN_MODULES):
        return args + [receiver]
    return []


def _hang_chuoi(expr, table, depth=0, seen=None):
    """Every string constant `expr` may hold, following names up to `RESOLVE_DEPTH` levels."""
    seen = set() if seen is None else seen
    found = set()
    for node in ast.walk(expr):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.add(node.value)
            continue
        key = node.id if isinstance(node, ast.Name) else (
            "." + node.attr if isinstance(node, ast.Attribute) else None)
        if key is None or key in seen or depth >= RESOLVE_DEPTH:
            continue
        seen.add(key)
        for value in table.values.get(key, ()):
            found |= _hang_chuoi(value, table, depth + 1, seen)
    return found


def thu_muc_bi_quet(source):
    """Top-level dirs (of `TOP_DIRS`) a test module scans; None when the source does not parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    table = _BangTen()
    table.visit(tree)
    table.gan_tham_so()
    dirs = set()
    for call in table.calls:
        for expr in _bieu_thuc_quet(call):
            for const in _hang_chuoi(expr, table):
                first = chuan_hoa(const).split("/")[0]
                if first in TOP_DIRS:
                    dirs.add(first)
    return dirs


def chon_theo_quet(top_dirs, sources):
    """Test modules that scan any of `top_dirs`; an unparsable test counts as a scanner."""
    chosen = set()
    for m, src in sources.items():
        scanned = thu_muc_bi_quet(src)
        if scanned is None or scanned & top_dirs:
            chosen.add(m)
    return chosen


# ---------- the radius ----------

def la_du_lieu(path):
    """True when `path` is a data file by kind (`DATA_NAMES`, or an extension in `DATA_EXTS`)."""
    name = path.rsplit("/", 1)[-1]
    return name in DATA_NAMES or os.path.splitext(name)[1].lower() in DATA_EXTS


def _ly_do_ngoai(paths):
    """Reason to run everything: a code or unknown-kind file outside `TOP_DIRS`; else None."""
    outside = sorted(p for p in paths
                     if p.split("/")[0] not in TOP_DIRS and not la_du_lieu(p))
    if outside:
        return "changed code or unknown-kind file outside %s: %s" % (
            "/ ".join(sorted(TOP_DIRS)) + "/", outside[0])
    return None


def _la_nguon_py(path):
    return path.endswith(".py") and os.path.dirname(path) in SOURCE_DIRS


def _la_module_phu_test(path):
    """A non-test `.py` directly under `tests/` (e.g. `helper.py`): importable by tests."""
    name = path.rsplit("/", 1)[-1]
    return (path.endswith(".py") and os.path.dirname(path) == TEST_DIR
            and not name.startswith("test_"))


def _ly_do_khong_doc_duoc(paths, repo):
    for p in paths:
        if not p.endswith(".py"):
            continue
        full = os.path.join(repo, *p.split("/"))
        if not os.path.isfile(full):
            return "changed .py is missing (deleted or renamed): %s" % p
        try:
            ast.parse(_doc(full))
        except SyntaxError:
            return "changed .py cannot be parsed: %s" % p
    return None


def _chon(paths, repo, sources):
    chosen = set()
    graph = test_graph = None
    for p in paths:
        name = p.rsplit("/", 1)[-1]
        if p.startswith("tests/") and name in sources:
            chosen.add(name)
        chosen |= chon_theo_duong_dan(p, sources)
        if _la_nguon_py(p):
            graph = do_thi_import(repo) if graph is None else graph
            chosen |= chon_theo_ten_module(bao_dong_nguoc(name[:-3], graph), sources)
        elif _la_module_phu_test(p):
            if test_graph is None:
                test_graph = do_thi_import(repo, (TEST_DIR,))
            chosen |= {m + ".py" for m in bao_dong_nguoc(name[:-3], test_graph)
                       if m + ".py" in sources}
    chosen |= chon_theo_quet({p.split("/")[0] for p in paths}, sources)
    return chosen


def ban_kinh(files, repo):
    """(sorted test module names, reason to run the full suite instead or None)."""
    paths = sorted({chuan_hoa(f) for f in files if chuan_hoa(f)})
    everything = tat_ca_module(repo)
    if not paths:
        return [], None
    reason = _ly_do_ngoai(paths) or _ly_do_khong_doc_duoc(paths, repo)
    if reason:
        return everything, reason
    sources = _nguon_test(repo)
    chosen = _chon(paths, repo, sources)
    if everything and len(chosen) >= NGUONG_TRON_BO * len(everything):
        return everything, "radius %d/%d modules reaches the %d%% threshold" % (
            len(chosen), len(everything), round(NGUONG_TRON_BO * 100))
    return sorted(chosen), None


# ---------- log, state and ledger ----------

STATE_PATH = ("docs", "tdq", "state.json")
LEDGER_PATH = ("docs", "tdq", ".tdq-test.jsonl")
NHANH_GOC_MAC_DINH = "main"
GIT_TIMEOUT = 30


def log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _log(message):
    if log_enabled():
        print(f"[{_now_iso()}] tdq_test: {message}", file=sys.stderr)


def _warn(message):
    _log(f"warning: {message}")


def _doc_state(repo):
    """`docs/tdq/state.json` as a dict; {} when missing or corrupt (corrupt is warned)."""
    path = os.path.join(repo, *STATE_PATH)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError) as exc:
        _warn(f"cannot read {'/'.join(STATE_PATH)} ({exc.__class__.__name__}); treated as empty")
        return {}
    if not isinstance(state, dict):
        _warn(f"{'/'.join(STATE_PATH)} is not an object; treated as empty")
        return {}
    return state


def _ghi_so(repo, row):
    """Append one JSON row to the ledger. True when written; never raises."""
    path = os.path.join(repo, *LEDGER_PATH)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return True
    except OSError as exc:
        _warn(f"cannot write the ledger {'/'.join(LEDGER_PATH)} ({exc.__class__.__name__})")
        return False


def _doc_so(repo):
    """Every valid row of the ledger, in order; a missing ledger is []; bad lines are skipped."""
    path = os.path.join(repo, *LEDGER_PATH)
    if not os.path.isfile(path):
        return []
    rows, bad = [], 0
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    bad += 1
                    continue
                if isinstance(row, dict):
                    rows.append(row)
                else:
                    bad += 1
    except OSError as exc:
        _warn(f"cannot read the ledger {'/'.join(LEDGER_PATH)} ({exc.__class__.__name__})")
        return []
    if bad:
        _warn(f"skipped {bad} corrupt line(s) in {'/'.join(LEDGER_PATH)}")
    return rows


# ---------- the changed files, from git ----------

def _git(repo, *args):
    """stdout of `git -C repo args...`; raises RuntimeError on any failure."""
    try:
        proc = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                              timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"git {args[0]} could not run ({exc.__class__.__name__})") from exc
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError(f"git {args[0]} failed: {err[0] if err else proc.returncode}")
    return proc.stdout.decode("utf-8", "replace")


def file_doi_git(repo, base):
    """(changed repo-relative paths, reason when git fails or None).

    Committed since `base` (`git diff --name-only base...HEAD`) plus every uncommitted change:
    staged, unstaged and untracked. The ledger itself is left out — the command writes it."""
    try:
        committed = _git(repo, "diff", "--name-only", "-z", f"{base}...HEAD").split("\0")
        status = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    except RuntimeError as exc:
        return [], str(exc)
    uncommitted = []
    entries = status.split("\0")
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        uncommitted.append(entry[3:])
        if entry[0] in "RC":  # with -z the rename source follows as its own entry
            uncommitted.append(entries[i])
            i += 1
    ledger = "/".join(LEDGER_PATH)
    files = {chuan_hoa(p) for p in committed + uncommitted if p.strip()}
    return sorted(f for f in files if f and f != ledger), None


# ---------- running the modules in one process ----------

def _bo_module_cu(tests_dir, modules):
    """Drop cached test modules imported from another tree, so `discover` loads ours."""
    for m in modules:
        cached = sys.modules.get(m[:-3])
        where = getattr(cached, "__file__", None)
        if cached is not None and (not where or os.path.dirname(os.path.abspath(where))
                                   != os.path.abspath(tests_dir)):
            del sys.modules[m[:-3]]


def chay_module(repo, modules, stream=None):
    """Run `modules` (test file names) in THIS process. True when every test passes."""
    if not modules:
        return True
    tests_dir = os.path.join(repo, "tests")
    _bo_module_cu(tests_dir, modules)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for m in modules:
        suite.addTests(loader.discover(tests_dir, pattern=m, top_level_dir=tests_dir))
    # A module that fails to import becomes a failing `_FailedTest` in the suite: still red.
    result = unittest.TextTestRunner(stream=stream or sys.stderr, verbosity=1).run(suite)
    return result.wasSuccessful()


# ---------- commands ----------

def cmd_vung_cham(args):
    """Run the tests of the touched zone; exit 0 when green, 1 otherwise."""
    start = time.monotonic()
    repo = os.path.abspath(args.repo)
    state = _doc_state(repo)
    if args.files is not None:
        files, reason = sorted({chuan_hoa(f) for f in args.files if chuan_hoa(f)}), None
    else:
        base = state.get("nhanh_goc") or NHANH_GOC_MAC_DINH
        files, reason = file_doi_git(repo, base)
    total = len(tat_ca_module(repo))
    if reason:
        modules = tat_ca_module(repo)
    else:
        modules, reason = ban_kinh(files, repo)
    if reason:
        print(f"vung-cham: {len(files)} changed file(s); running the full suite "
              f"({len(modules)} modules): {reason}")
    else:
        print(f"vung-cham: {len(files)} changed file(s); selected {len(modules)}/{total} "
              f"modules: {' '.join(modules) or '(none)'}")
    sys.stdout.flush()
    ok = chay_module(repo, modules)
    seconds = round(time.monotonic() - start, 2)
    _ghi_so(repo, {"ts": _now_iso(), "kind": "vung-cham",
                   "request": state.get("active_request"), "phase": state.get("phase"),
                   "files": files, "modules": modules, "fallback": reason, "ok": ok,
                   "seconds": float(seconds)})
    _log(f"vung-cham files={len(files)} modules={len(modules)}/{total} "
         f"fallback={reason or 'none'} ok={ok} seconds={seconds}")
    return 0 if ok else 1


_ID_TRONG_NGOAC = re.compile(r"\(([\w.]+)\)")


def _module_cua(test):
    """`test_x.py` of a failing/erroring test, or None when it cannot be told.

    A normal test id is `test_x.Class.method`; a module that fails to import is a
    `_FailedTest` whose method name is the module; a fixture error (`setUpClass`,
    `setUpModule`) is an `_ErrorHolder` whose id reads `setUpClass (test_x.Class)`."""
    if isinstance(test, unittest.loader._FailedTest):
        name = test._testMethodName
    else:
        tid = test.id()
        m = _ID_TRONG_NGOAC.search(tid)
        name = (m.group(1) if m else tid).split(".")[0]
    return name + ".py" if name.startswith("test_") else None


def chay_tron_bo(repo, stream=None):
    """Run every `tests/test_*.py` in THIS process. (ok, sorted failing module names)."""
    tests_dir = os.path.join(repo, "tests")
    if not os.path.isdir(tests_dir):
        return True, []
    _bo_module_cu(tests_dir, tat_ca_module(repo))
    suite = unittest.defaultTestLoader.discover(tests_dir, pattern="test_*.py",
                                                top_level_dir=tests_dir)
    result = unittest.TextTestRunner(stream=stream or sys.stderr, verbosity=1).run(suite)
    failed = {_module_cua(t) for t, _ in result.failures + result.errors}
    failed |= {_module_cua(t) for t in getattr(result, "unexpectedSuccesses", [])}
    return result.wasSuccessful(), sorted(m for m in failed if m)


def module_bo_sot(rows, request, failed_modules):
    """Failing modules that no `vung-cham` row of `request` ever selected.

    Nothing is missed when a `vung-cham` row of that request fell back to the full suite."""
    selected = set()
    for row in rows:
        if row.get("kind") != "vung-cham" or row.get("request") != request:
            continue
        if row.get("fallback"):
            return []
        mods = row.get("modules")
        if isinstance(mods, list):
            selected.update(m for m in mods if isinstance(m, str))
    return sorted(m for m in failed_modules if m not in selected)


def dem(rows, request):
    """Counts of one request over ledger rows; pure (reads `rows`, changes nothing).

    `ngan_sach` is the full-suite budget: 2 (QC-F1 + after the last fix round), or 3 once a
    red `tron-bo` exists in the request — a red QC-F1 implies a QC fix round."""
    tron_bo = bo_sot = 0
    missed, red = set(), False
    for row in rows:
        if not isinstance(row, dict) or row.get("request") != request:
            continue
        kind = row.get("kind")
        if kind == "tron-bo":
            tron_bo += 1
            red = red or row.get("ok") is False
        elif kind == "bo-sot":
            bo_sot += 1
            if isinstance(row.get("module"), str):
                missed.add(row["module"])
    return {"request": request, "tron_bo": tron_bo, "bo_sot": bo_sot,
            "modules_bo_sot": sorted(missed), "ngan_sach": 3 if red else 2}


def cmd_tron_bo(args):
    """Run the full suite in one process, log it, and flag the modules the radius missed."""
    start = time.monotonic()
    repo = os.path.abspath(args.repo)
    state = _doc_state(repo)
    request, phase = state.get("active_request"), state.get("phase")
    total = len(tat_ca_module(repo))
    print(f"tron-bo: running the full suite ({total} modules)")
    sys.stdout.flush()
    ok, failed = chay_tron_bo(repo)
    seconds = round(time.monotonic() - start, 2)
    rows = _doc_so(repo)
    _ghi_so(repo, {"ts": _now_iso(), "kind": "tron-bo", "request": request, "phase": phase,
                   "ok": ok, "seconds": float(seconds), "failed_modules": failed})
    missed = module_bo_sot(rows, request, failed)
    for m in missed:
        _ghi_so(repo, {"ts": _now_iso(), "kind": "bo-sot", "request": request, "module": m})
        print(f"tron-bo: {m} is red but no vung-cham run of request {request} selected it "
              f"(the radius missed it)")
    if failed:
        print(f"tron-bo: red modules: {' '.join(failed)}")
    _log(f"tron-bo modules={total} failed={len(failed)} missed={len(missed)} ok={ok} "
         f"seconds={seconds}")
    return 0 if ok else 1


def cmd_so(args):
    """Print how many full-suite runs and radius misses the current request has."""
    repo = os.path.abspath(args.repo)
    state = _doc_state(repo)
    request = state.get("active_request")
    counts = dem(_doc_so(repo), request)
    if args.json:
        print(json.dumps(counts, ensure_ascii=False))
    else:
        print(f"request: {request} (phase {state.get('phase')})")
        print(f"full-suite runs: {counts['tron_bo']} of budget {counts['ngan_sach']}")
        print(f"radius misses: {counts['bo_sot']}"
              + (f" ({' '.join(counts['modules_bo_sot'])})" if counts["modules_bo_sot"] else ""))
    _log(f"so request={request} tron_bo={counts['tron_bo']} bo_sot={counts['bo_sot']} "
         f"budget={counts['ngan_sach']}")
    return 0


def main(argv=None):
    import utf8_io  # noqa: F401 — imported for its side effect: stdout/stderr become UTF-8
    parser = argparse.ArgumentParser(
        prog="tdq_test.py", description="Run the tests a change can reach.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("vung-cham", help="run the tests of the touched zone and its radius")
    p.add_argument("--files", nargs="*", default=None,
                   help="changed files (default: from git against nhanh_goc)")
    p.add_argument("--repo", default=os.getcwd(), help="repo root (default: cwd)")
    p.set_defaults(func=cmd_vung_cham)
    p = sub.add_parser("tron-bo", help="run the full suite in one process and log misses")
    p.add_argument("--repo", default=os.getcwd(), help="repo root (default: cwd)")
    p.set_defaults(func=cmd_tron_bo)
    p = sub.add_parser("so", help="count full-suite runs and radius misses of the request")
    p.add_argument("--json", action="store_true", help="print one JSON object")
    p.add_argument("--repo", default=os.getcwd(), help="repo root (default: cwd)")
    p.set_defaults(func=cmd_so)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
