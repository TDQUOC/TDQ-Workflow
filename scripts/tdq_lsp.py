#!/usr/bin/env python3
"""Diagnose the agent-lsp setup of the machine and of this project (stdlib only).

Sub-commands:
  kiem       — run the diagnostic ladder and print one line per rung
  danh-thuc  — wake Ollama up on demand (added at T1.3)
  nha        — release the embedding model right after use (added at T1.3)

The ladder (`kiem`):
  1. the `agent-lsp` binary is on PATH
  2. the `lsp` MCP server is registered for Claude Code
  3. a language server exists for every language this project actually uses
  4. the `mcp__lsp__*` tools are allowed without a prompt
  5. lumen's health — the fallback layer (added at T1.2)
  6. an outside plugin hook pushing a different search order (added at T1.2)

Principles:
- **This script NEVER installs anything.** A missing rung prints the exact command; a human
  approves it and runs it. Starting or stopping a process already present on the machine is
  not installing, so `danh-thuc`/`nha` stay inside that rule.
- Rungs 1–4 are actionable → a gap makes the exit code 3. Rungs 5–6 only warn: they never
  change the exit code, because search still works through agent-lsp and grep without them.
- The log service is on by default to stderr (ISO timestamp), off with `--khong-log` or TDQ_LOG=0.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

CHECK_TIMEOUT = 20
MCP_SERVER_NAME = "lsp"
TOOL_PATTERN = "mcp__lsp__"
INSTALL_AGENT_LSP = "curl -fsSL https://raw.githubusercontent.com/blackwell-systems/agent-lsp/main/install.sh | sh"
EXIT_OK = 0
EXIT_THIEU = 3
OLLAMA_PORT = 11434
MODEL_LUMEN = "ordis/jina-embeddings-v2-base-code"
PLUGIN_NHA = "tdq-workflow"          # our own plugin — its hooks are the reference, not a conflict
TOOL_TIM_KIEM = ("Grep", "Glob", "Bash")

# Directories never worth scanning when sniffing which languages a project uses.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
             "graphify-out", ".pytest_cache", ".mypy_cache", "target", "vendor"}
SKIP_PREFIX = ("portable_",)

# extension → language key. Only languages agent-lsp actually supports appear here.
EXT_LANG = {
    ".py": "python", ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".go": "go", ".rs": "rust", ".java": "java", ".rb": "ruby", ".php": "php",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".cs": "csharp", ".kt": "kotlin", ".kts": "kotlin", ".lua": "lua",
    ".swift": "swift", ".zig": "zig", ".css": "css", ".scss": "css",
    ".html": "html", ".tf": "terraform", ".scala": "scala", ".gleam": "gleam",
    ".ex": "elixir", ".exs": "elixir", ".prisma": "prisma", ".sql": "sql",
    ".clj": "clojure", ".cljs": "clojure", ".nix": "nix", ".dart": "dart",
}
# YAML and JSON are config formats present in nearly every repo; asking for their server on
# every project is noise, so they stay out of the sniff and only live in the reference table.

# language key → (display name, server binary on PATH, install command)
LANG_SERVER = {
    "typescript": ("TypeScript", "typescript-language-server", "npm i -g typescript-language-server typescript"),
    "javascript": ("JavaScript", "typescript-language-server", "npm i -g typescript-language-server typescript"),
    "python": ("Python", "pyright-langserver", "npm i -g pyright"),
    "go": ("Go", "gopls", "go install golang.org/x/tools/gopls@latest"),
    "rust": ("Rust", "rust-analyzer", "rustup component add rust-analyzer"),
    "java": ("Java", "jdtls", "tải từ https://download.eclipse.org/jdtls/snapshots/"),
    "c": ("C", "clangd", "brew install llvm"),
    "cpp": ("C++", "clangd", "brew install llvm"),
    "ruby": ("Ruby", "solargraph", "gem install solargraph"),
    "php": ("PHP", "intelephense", "npm i -g intelephense"),
    "csharp": ("C#", "csharp-ls", "dotnet tool install -g csharp-ls"),
    "kotlin": ("Kotlin", "kotlin-language-server", "tải từ https://github.com/fwcd/kotlin-language-server/releases"),
    "lua": ("Lua", "lua-language-server", "brew install lua-language-server"),
    "swift": ("Swift", "sourcekit-lsp", "cài Xcode hoặc Swift toolchain"),
    "zig": ("Zig", "zls", "tải từ https://github.com/zigtools/zls/releases"),
    "css": ("CSS", "vscode-css-language-server", "npm i -g vscode-langservers-extracted"),
    "html": ("HTML", "vscode-html-language-server", "npm i -g vscode-langservers-extracted"),
    "terraform": ("Terraform", "terraform-ls", "tải từ https://releases.hashicorp.com/terraform-ls/"),
    "scala": ("Scala", "metals", "cs install metals"),
    "gleam": ("Gleam", "gleam", "tải từ https://github.com/gleam-lang/gleam/releases"),
    "elixir": ("Elixir", "elixir-ls", "tải từ https://github.com/elixir-lsp/elixir-ls/releases"),
    "prisma": ("Prisma", "prisma-language-server", "npm i -g @prisma/language-server"),
    "sql": ("SQL", "sqls", "go install github.com/sqls-server/sqls@latest"),
    "clojure": ("Clojure", "clojure-lsp", "tải từ https://github.com/clojure-lsp/clojure-lsp/releases"),
    "nix": ("Nix", "nil", "tải từ https://github.com/oxalica/nil/releases"),
    "dart": ("Dart", "dart", "brew install dart"),
    "yaml": ("YAML", "yaml-language-server", "npm i -g yaml-language-server"),
    "json": ("JSON", "vscode-json-language-server", "npm i -g vscode-langservers-extracted"),
}

# language key → (root-marker files, group). The marker is what the language server walks up the
# tree to find; without it the server takes the open file's directory as the whole project and
# every cross-file answer comes back nearly empty.
#
# Group "B" — the config is OPTIONAL, so a missing marker fails SILENTLY: the project runs, the
# tests stay green, and only relationship queries quietly collapse. That is the trap this repo
# walked into (7 % file coverage while all six older rungs reported ĐẠT), so B blocks.
# Group "A" — the marker is a build manifest. Without it the project does not build at all, so
# the gap announces itself long before this rung; A only warns.
LANG_CONFIG = {
    "typescript": (["tsconfig.json", "jsconfig.json", "package.json"], "B"),
    "javascript": (["jsconfig.json", "tsconfig.json", "package.json"], "B"),
    "python": (["pyrightconfig.json", "pyproject.toml", "setup.py", "setup.cfg"], "B"),
    "lua": ([".luarc.json", ".luarc.jsonc"], "B"),
    "c": (["compile_commands.json", "compile_flags.txt"], "B"),
    "cpp": (["compile_commands.json", "compile_flags.txt"], "B"),
    "go": (["go.mod"], "A"),
    "rust": (["Cargo.toml"], "A"),
    "java": (["pom.xml", "build.gradle", "build.gradle.kts"], "A"),
    "ruby": (["Gemfile", "*.gemspec"], "A"),
    "php": (["composer.json"], "A"),
    "csharp": (["*.csproj", "*.sln"], "A"),
    "kotlin": (["build.gradle", "build.gradle.kts", "pom.xml"], "A"),
    "swift": (["Package.swift"], "A"),
    "zig": (["build.zig"], "A"),
    "scala": (["build.sbt", "build.sc"], "A"),
    "gleam": (["gleam.toml"], "A"),
    "elixir": (["mix.exs"], "A"),
    "dart": (["pubspec.yaml"], "A"),
    "clojure": (["deps.edn", "project.clj"], "A"),
    "nix": (["flake.nix", "default.nix"], "A"),
    "terraform": (["main.tf", ".terraform.lock.hcl"], "A"),
    "prisma": (["schema.prisma", "package.json"], "A"),
    "sql": ([".sqls.yml", "config.yml"], "A"),
    # Markup and data formats have no import graph, so there is no root to configure and nothing
    # for this rung to check. An empty marker list means "not applicable", never "missing".
    "css": ([], "A"),
    "html": ([], "A"),
    "yaml": ([], "A"),
    "json": ([], "A"),
}

# Content the rung offers to create when a group-B marker is missing. It only ever PRINTS this and
# asks — writing the file is the user's call, per the one hard rule of the skill.
GOI_Y_CAU_HINH = {
    "python": 'pyrightconfig.json: {"include": ["<thư mục mã>"], "extraPaths": ["<gốc import>"]}',
    "typescript": 'tsconfig.json: {"compilerOptions": {"baseUrl": "."}, "include": ["<thư mục mã>"]}',
    "javascript": 'jsconfig.json: {"compilerOptions": {"baseUrl": "."}, "include": ["<thư mục mã>"]}',
    "lua": '.luarc.json: {"workspace": {"library": ["<thư mục thư viện>"]}}',
    "c": "compile_commands.json — sinh bằng `bear -- make` hoặc `cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`",
    "cpp": "compile_commands.json — sinh bằng `bear -- make` hoặc `cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`",
}

# A language showing up in only one or two files is noise, not a stack worth a server.
NGUONG_FILE = 3

_LOG_TAT = False


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _log_enabled():
    return not _LOG_TAT and os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: one ISO-timestamped line to stderr. Silenced by --khong-log or TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


def _project_dir():
    """Anchor on the project: TDQ_PROJECT_DIR > git root > cwd."""
    env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = current = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return start
        current = parent


def _run(cmd, timeout=CHECK_TIMEOUT):
    """Run a read-only probe, return (rc, output). Infrastructure errors become results, never raised."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, f"quá {timeout}s"
    except OSError as exc:
        return 1, str(exc)


def _doc_json(path):
    """Read a JSON file, returning {} for anything unreadable — a missing config is a finding, not a crash."""
    try:
        with open(os.path.expanduser(path), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        _log(f"đọc {path} → bỏ qua ({exc.__class__.__name__})")
        return {}


class Bac:
    """One rung of the ladder: a verdict plus, when it fails, the exact command that fixes it."""

    def __init__(self, so, ten, dat, chi_tiet="", lenh_cai="", chi_canh_bao=False):
        self.so = so
        self.ten = ten
        self.dat = dat
        self.chi_tiet = chi_tiet
        self.lenh_cai = lenh_cai
        self.chi_canh_bao = chi_canh_bao

    def in_ra(self):
        nhan = "ĐẠT" if self.dat else ("CẢNH BÁO" if self.chi_canh_bao else "THIẾU")
        dong = f"Bậc {self.so} · {self.ten} → {nhan}"
        if self.chi_tiet:
            dong += f" ({self.chi_tiet})"
        print(dong)
        if not self.dat and self.lenh_cai:
            print(f"  {'Xử lý' if self.chi_canh_bao else 'Cài'}: {self.lenh_cai}")


def bac1_binary():
    """Rung 1 — the agent-lsp binary itself."""
    duong_dan = shutil.which("agent-lsp")
    if not duong_dan:
        return Bac(1, "binary agent-lsp", False,
                   "không thấy trên PATH", INSTALL_AGENT_LSP)
    rc, out = _run(["agent-lsp", "--version"])
    ban = out.splitlines()[0].strip() if rc == 0 and out else "không đọc được bản"
    return Bac(1, "binary agent-lsp", True, ban)


def bac2_mcp():
    """Rung 2 — the `lsp` MCP server registered for Claude Code."""
    cau_hinh = _doc_json("~/.claude.json")
    servers = cau_hinh.get("mcpServers") or {}
    if MCP_SERVER_NAME in servers:
        return Bac(2, f"MCP `{MCP_SERVER_NAME}`", True, f"{len(servers)} server đã đăng ký")
    return Bac(2, f"MCP `{MCP_SERVER_NAME}`", False,
               "chưa đăng ký trong ~/.claude.json", "agent-lsp init")


def do_ngon_ngu(project):
    """Count source files per language so rung 3 only asks for servers this project truly needs."""
    dem = {}
    for goc, thu_muc, files in os.walk(project):
        thu_muc[:] = [d for d in thu_muc
                      if d not in SKIP_DIRS and not d.startswith(SKIP_PREFIX) and not d.startswith(".")]
        for ten in files:
            lang = EXT_LANG.get(os.path.splitext(ten)[1])
            if lang:
                dem[lang] = dem.get(lang, 0) + 1
    return {lang: n for lang, n in dem.items() if n >= NGUONG_FILE}


def bac3_language_server(project):
    """Rung 3 — one language server per language the project actually uses."""
    dung = do_ngon_ngu(project)
    if not dung:
        return Bac(3, "language server theo project", True, "project không có ngôn ngữ nào cần server")
    thieu = []
    for lang in sorted(dung, key=lambda k: -dung[k]):
        ten, binary, lenh = LANG_SERVER[lang]
        if not shutil.which(binary):
            thieu.append((ten, binary, lenh))
    if not thieu:
        return Bac(3, "language server theo project", True,
                   f"đủ cho {len(dung)} ngôn ngữ: " + ", ".join(LANG_SERVER[l][0] for l in sorted(dung)))
    chi_tiet = "thiếu " + ", ".join(f"{ten} ({binary})" for ten, binary, _ in thieu)
    lenh = " ; ".join(sorted({lenh for _, _, lenh in thieu}))
    return Bac(3, "language server theo project", False, chi_tiet, lenh)


def bac4_quyen_tool():
    """Rung 4 — the mcp__lsp__* tools allowed without a prompt each time."""
    cau_hinh = _doc_json("~/.claude/settings.json")
    allow = (cau_hinh.get("permissions") or {}).get("allow") or []
    khop = [m for m in allow if isinstance(m, str) and TOOL_PATTERN in m]
    if khop:
        return Bac(4, f"quyền tool `{TOOL_PATTERN}*`", True, f"{len(khop)} mục trong allow")
    return Bac(4, f"quyền tool `{TOOL_PATTERN}*`", False,
               "chưa có mục nào trong allow của ~/.claude/settings.json",
               f'thêm "{TOOL_PATTERN}*" vào permissions.allow của ~/.claude/settings.json')


def _ollama_dang_chay():
    """Is the Ollama daemon answering on its port? A socket probe, no dependency on curl."""
    import socket
    with socket.socket() as s:
        s.settimeout(1.5)
        try:
            s.connect(("127.0.0.1", OLLAMA_PORT))
            return True
        except OSError:
            return False


def _model_da_pull():
    """Is lumen's embedding model on disk? The manifest is readable even with the daemon down."""
    goc = os.path.expanduser("~/.ollama/models/manifests/registry.ollama.ai")
    return os.path.exists(os.path.join(goc, *MODEL_LUMEN.split("/")))


def bac5_lumen():
    """Rung 5 — lumen's health. Warning only: lumen is the FALLBACK, agent-lsp is the main layer."""
    if not shutil.which("ollama"):
        return Bac(5, "sức khoẻ lumen", False, "thiếu ollama — lumen không chạy được",
                   "brew install ollama", chi_canh_bao=True)
    if not _model_da_pull():
        return Bac(5, "sức khoẻ lumen", False, f"thiếu model {MODEL_LUMEN}",
                   f"ollama pull {MODEL_LUMEN}", chi_canh_bao=True)
    if not _ollama_dang_chay():
        return Bac(5, "sức khoẻ lumen", False,
                   "ollama chưa chạy — sẽ đánh thức khi cần bằng `tdq_lsp.py danh-thuc`",
                   chi_canh_bao=True)
    return Bac(5, "sức khoẻ lumen", True, f"ollama đang chạy, có {MODEL_LUMEN}")


def _plugin_dang_bat():
    """The install paths Claude Code actually loads — the cache also holds stale older versions."""
    data = _doc_json("~/.claude/plugins/installed_plugins.json")
    duong_dan = []
    for ten, ban_ghi in (data.get("plugins") or {}).items():
        for b in ban_ghi if isinstance(ban_ghi, list) else []:
            p = b.get("installPath")
            if p:
                duong_dan.append((ten, p))
    return duong_dan


def bac6_hook_xung_dot(project):
    """Rung 6 — an outside plugin hook pushing a search order other than the TDQ one.

    Report only: the script NEVER edits another plugin's file. Fixing it is the user's call.
    """
    xung_dot = []
    for ten, goc in _plugin_dang_bat():
        if ten.startswith(PLUGIN_NHA):
            continue
        f = os.path.join(goc, "hooks", "hooks.json")
        if not os.path.exists(f):
            continue
        khoi = (_doc_json(f).get("hooks") or {}).get("PreToolUse") or []
        for muc in khoi if isinstance(khoi, list) else []:
            matcher = str(muc.get("matcher", ""))
            if any(t in matcher for t in TOOL_TIM_KIEM):
                xung_dot.append((ten, f, matcher))
                break
    if not xung_dot:
        return Bac(6, "hook plugin ngoài xung đột", True, "không plugin nào chèn thứ tự tìm kiếm khác")
    chi_tiet = "; ".join(f"{ten} (matcher {m}) tại {f}" for ten, f, m in xung_dot)
    return Bac(6, "hook plugin ngoài xung đột", False, chi_tiet,
               "BÁO cho user và XIN PHÉP trước khi gỡ khối PreToolUse; script không tự sửa file plugin",
               chi_canh_bao=True)


def bac7_cau_hinh_goc_import(project):
    """Rung 7 — the import-root config each language of THIS project needs.

    Rungs 1–6 all check that something EXISTS. None of them notices a language server that starts
    fine and then answers every cross-file question from a one-file scope, which is what happens
    when the root marker is missing. That gap is invisible: the project runs and the tests pass.
    Group B blocks because there the config is optional and the failure is silent; group A only
    warns because a missing build manifest breaks the build and reports itself.
    """
    ten_bac = "cấu hình gốc import theo ngôn ngữ"
    ngon_ngu = do_ngon_ngu(project)
    if not ngon_ngu:
        return Bac(7, ten_bac, True, "không ngôn ngữ nào vượt ngưỡng file")
    co_san = set(os.listdir(project)) if os.path.isdir(project) else set()

    def co_moc(moc):
        for m in moc:
            if m.startswith("*."):
                if any(f.endswith(m[1:]) for f in co_san):
                    return True
            elif m in co_san:
                return True
        return False

    thieu_b, thieu_a = [], []
    for khoa in ngon_ngu:
        cau_hinh = LANG_CONFIG.get(khoa)
        if not cau_hinh:
            continue
        moc, nhom = cau_hinh
        if not moc or co_moc(moc):
            continue
        ten = LANG_SERVER[khoa][0]
        (thieu_b if nhom == "B" else thieu_a).append((khoa, ten, moc))
    if not thieu_b and not thieu_a:
        return Bac(7, ten_bac, True, f"{len(ngon_ngu)} ngôn ngữ đều có file mốc ở gốc dự án")

    # Chi tiết luôn liệt kê CẢ hai nhóm — thiếu nhóm A vẫn phải hiện dù nhóm B cũng thiếu.
    # Mức nghiêm trọng thì do nhóm B quyết định: có B là CHẶN, chỉ có A là cảnh báo.
    chi_tiet = "; ".join(f"{ten} thiếu {' hoặc '.join(moc)}" for _, ten, moc in thieu_b + thieu_a)
    if thieu_b:
        goi_y = " | ".join(GOI_Y_CAU_HINH[k] for k, _, _ in thieu_b if k in GOI_Y_CAU_HINH)
        return Bac(7, ten_bac, False, chi_tiet,
                   f"XIN PHÉP user rồi tạo tay — {goi_y}", chi_canh_bao=False)
    return Bac(7, ten_bac, False, chi_tiet,
               "dự án thiếu manifest build nên gần như chắc chắn đã hỏng sẵn — báo user, không tự tạo",
               chi_canh_bao=True)


def chay_kiem(project):
    """Run the whole ladder and return the list of rungs, in order."""
    _log(f"kiem · project={project}")
    bac = [bac1_binary(), bac2_mcp(), bac3_language_server(project), bac4_quyen_tool(),
           bac5_lumen(), bac6_hook_xung_dot(project), bac7_cau_hinh_goc_import(project)]
    for b in bac:
        _log(f"bậc {b.so} {b.ten} → {'ĐẠT' if b.dat else 'THIẾU'}")
    return bac


def cmd_kiem(args):
    project = _project_dir()
    bac = chay_kiem(project)
    for b in bac:
        b.in_ra()
    thieu = [b for b in bac if not b.dat and not b.chi_canh_bao]
    canh_bao = [b for b in bac if not b.dat and b.chi_canh_bao]
    print(f"\nTổng: {len(bac) - len(thieu) - len(canh_bao)}/{len(bac)} bậc ĐẠT"
          + (f" · {len(thieu)} bậc cần bạn cho phép cài" if thieu else "")
          + (f" · {len(canh_bao)} cảnh báo không chặn" if canh_bao else ""))
    if thieu:
        print("Script KHÔNG tự cài. Hãy duyệt từng lệnh ở trên rồi chạy tay.")
    _log(f"done · {len(thieu)} bậc thiếu · {len(canh_bao)} cảnh báo")
    return EXIT_THIEU if thieu else EXIT_OK


def _dau_so_huu():
    """Where the marker lives. It must outlive the process, since `danh-thuc` and `nha` are separate runs."""
    import tempfile
    return os.path.join(tempfile.gettempdir(), "tdq_lsp_ollama_owner.json")


def _ghi_dau(pid):
    try:
        with open(_dau_so_huu(), "w", encoding="utf-8") as fh:
            json.dump({"pid": pid, "luc": _now()}, fh)
    except OSError as exc:
        _log(f"ghi dấu sở hữu thất bại ({exc}) — `nha` sẽ không dám tắt daemon")


def _doc_dau():
    d = _doc_json(_dau_so_huu())
    return d.get("pid") if isinstance(d.get("pid"), int) else None


def _xoa_dau():
    try:
        os.remove(_dau_so_huu())
    except OSError:
        pass


def cmd_danh_thuc(args):
    """Wake Ollama up ON DEMAND — only ever called when an LSP query came back empty.

    Starting a process already installed on the machine is not INSTALLING, so this stays
    inside the rule that the script never installs anything.
    """
    import time
    if _ollama_dang_chay():
        print(f"Ollama đã chạy sẵn ở cổng {OLLAMA_PORT} — không bật thêm, không nhận sở hữu.")
        _log("danh-thuc → đã chạy sẵn")
        return EXIT_OK
    if not shutil.which("ollama"):
        print("Ollama chưa cài — bỏ qua lumen, tìm tiếp bằng agent-lsp rồi grep.")
        print("  Cài (cần bạn cho phép): brew install ollama")
        _log("danh-thuc → thiếu binary")
        return EXIT_OK
    _log(f"danh-thuc · bật `ollama serve`, hạn chờ {args.han_cho}s")
    try:
        p = subprocess.Popen(["ollama", "serve"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
    except OSError as exc:
        print(f"Không bật được Ollama ({exc}) — bỏ qua lumen, tìm tiếp bằng grep.")
        return EXIT_OK
    het_han = time.monotonic() + args.han_cho
    while time.monotonic() < het_han:
        if _ollama_dang_chay():
            _ghi_dau(p.pid)
            print(f"Ollama đã dậy ở cổng {OLLAMA_PORT} (pid {p.pid}). Tìm xong nhớ chạy `nha`.")
            _log(f"danh-thuc → dậy sau {args.han_cho}s hạn, pid={p.pid}")
            return EXIT_OK
        time.sleep(0.5)
    p.terminate()
    print(f"Ollama không dậy trong {args.han_cho}s — bỏ qua lumen, tìm tiếp bằng grep.")
    _log("danh-thuc → quá hạn, đã dọn tiến trình vừa bật")
    return EXIT_OK


def cmd_nha(args):
    """Release the embedding model right after the search — keeping it resident eats the machine.

    The daemon itself only gets killed when THIS script started it; a daemon the user runs is
    never touched.
    """
    # Guard on the daemon being up: on macOS the Ollama app STARTS the server the moment any CLI
    # command reaches it, so calling `stop` on a sleeping machine would wake exactly what we mean
    # to keep asleep. Nothing is resident when the daemon is down, so there is nothing to release.
    if shutil.which("ollama") and _ollama_dang_chay():
        rc, out = _run(["ollama", "stop", MODEL_LUMEN])
        print(f"Đã nhả model {MODEL_LUMEN}." if rc == 0 else f"Không nhả được model: {out}")
        _log(f"nha · ollama stop → rc={rc}")
    else:
        print("Ollama không chạy — không model nào đang giữ RAM, khỏi nhả.")
        _log("nha · ollama không chạy, bỏ qua stop")
    pid = _doc_dau()
    if pid is None:
        print("Daemon Ollama không do script này bật — giữ nguyên, không tắt.")
        _log("nha → không có dấu sở hữu, giữ daemon")
        return EXIT_OK
    try:
        os.kill(pid, 15)
        print(f"Đã tắt daemon Ollama do script bật (pid {pid}).")
        _log(f"nha → tắt daemon pid={pid}")
    except OSError as exc:
        _log(f"nha → daemon pid={pid} đã không còn ({exc})")
    _xoa_dau()
    return EXIT_OK


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Chẩn đoán bộ agent-lsp cho máy và cho project này. Script không tự cài gì.")
    ap.add_argument("--khong-log", action="store_true", help="tắt log service")
    sub = ap.add_subparsers(dest="lenh", required=True)
    sub.add_parser("kiem", help="chạy thang chẩn đoán, in từng bậc")
    dt = sub.add_parser("danh-thuc", help="đánh thức Ollama theo yêu cầu, chỉ khi LSP tìm không thấy")
    dt.add_argument("--han-cho", type=float, default=30.0, help="giây chờ Ollama trả lời (mặc định 30)")
    sub.add_parser("nha", help="nhả model embedding ngay sau khi tìm xong")
    return ap.parse_args(argv)


def main(argv):
    global _LOG_TAT
    args = parse_args(argv)
    _LOG_TAT = args.khong_log
    return {"kiem": cmd_kiem, "danh-thuc": cmd_danh_thuc, "nha": cmd_nha}[args.lenh](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
