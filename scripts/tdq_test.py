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
  `skills/`, `agents/`, `docs/` match by PATH only — a bare `SKILL.md` matches every skill (the
  prototype over-selected 37 modules that way). Other files also match by bare file name;
- (c) for a changed `.py` under `scripts/` or `hooks/scripts/`: it mentions, as a word or as
  `name.py`, any module of the reverse transitive import closure (AST, imports inside functions
  included) among those two dirs. Matching the NAME, not only the import, catches tests that
  run hooks through a subprocess (`run_hook("stop_gate.py", ...)`);
- (d) it SCANS the top-level dir of a changed file: an AST call to `os.walk`, `os.listdir`,
  `os.scandir`, `glob.glob`, `glob.iglob`, `Path.glob`/`rglob`/`iterdir` whose path expression
  holds a string constant naming that dir. Names are resolved through local assignments, `for`
  targets, `with` targets, attribute assignments and the call sites of the enclosing function,
  so `SKILLS = os.path.join(ROOT, "skills")` then `os.walk(SKILLS)` is caught.

The caller must run the full suite instead (`ly_do_tron_bo` is set, `modules` is every module)
when a changed path lies outside `TOP_DIRS`, a changed `.py` cannot be parsed, or the selection
reaches `NGUONG_TRON_BO` of all modules — at that size one full-suite process is cheaper than
picking, and safer.

Measured by the prototype in the brief (2026-10-03, 126 modules, name + import matching only):
leaf files (`ask_gate.py`, `tdq_bench.py`) 2 modules; `stop_gate.py` 11 (29 s instead of 353.9 s);
`qc.md` 7 (22 s); `_common.py` 38 (30%); the hub `tdq_state.py` / `doc_lint.py` 96-102 (76%+),
where the full suite is the right call. Rule (d) adds the directory scanners on top of that.
"""
import ast
import os
import re

TOP_DIRS = frozenset({"scripts", "hooks", "skills", "tests", "agents"})
PATH_ONLY_DIRS = frozenset({"skills", "agents", "docs"})
SOURCE_DIRS = ("scripts", "hooks/scripts")
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
    if segs[0] not in PATH_ONLY_DIRS:
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


def do_thi_import(repo):
    """{module name: set of module names it imports} over `SOURCE_DIRS`."""
    graph = {}
    for d in SOURCE_DIRS:
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

def _ly_do_ngoai(paths):
    outside = sorted(p for p in paths if p.split("/")[0] not in TOP_DIRS)
    if outside:
        return "changed file outside %s: %s" % ("/ ".join(sorted(TOP_DIRS)) + "/", outside[0])
    return None


def _la_nguon_py(path):
    return path.endswith(".py") and os.path.dirname(path) in SOURCE_DIRS


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
    graph = None
    for p in paths:
        name = p.rsplit("/", 1)[-1]
        if p.startswith("tests/") and name in sources:
            chosen.add(name)
        chosen |= chon_theo_duong_dan(p, sources)
        if _la_nguon_py(p):
            graph = do_thi_import(repo) if graph is None else graph
            chosen |= chon_theo_ten_module(bao_dong_nguoc(name[:-3], graph), sources)
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
