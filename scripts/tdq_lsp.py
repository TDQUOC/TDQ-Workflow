#!/usr/bin/env python3
"""Diagnose the agent-lsp setup of the machine and of this project (stdlib only).

Sub-commands:
  kiem       — run the diagnostic ladder and print one line per rung
  danh-thuc  — wake Ollama up on demand (added at T1.3)
  nha        — release the embedding model right after use (added at T1.3)

The ladder (`kiem`):
  1. the `agent-lsp` binary is on PATH
  2. the `lsp` MCP server is registered for Claude Code
  3. a language server exists for every language this project actually uses, and really starts
     (`agent-lsp doctor` run in the project)
  4. the `mcp__lsp__*` tools are allowed without a prompt
  5. lumen's health — the fallback layer, measured by EFFECT: a real round trip plus an index
     that actually holds the working tree's newest content (added at T1.2, deepened 2026-09-28)
  6. an outside plugin hook pushing a different search order (added at T1.2)
  7. the import-root config each language needs
  8. the graphify graph the fourth search layer reads (added 2026-09-28)
Then the four-layer smoke test (grep, LSP, graphify, lumen each asked one real question), and
ONE total line: ĐẠT only when no rung blocks AND every layer answered. There is deliberately no
"ladder only" mode — having one is how a smoke failure went unseen on 2026-10-02.

Exit codes of `check`: 0 total ĐẠT · 3 an actionable rung is missing · 4 rungs fine but a smoke
layer could not answer.

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
import functools
import glob
import json
import os
import re
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
EXIT_SMOKE = 4
OLLAMA_PORT = 11434
# Trần riêng cho hai phép đo hiệu ứng của bậc 5. Chúng chạy ở intake bước 1b của MỌI request nên
# không được phép kéo dài: đo 2026-09-28 trên repo này, dựng lại tăng trưởng mất 0,2 s khi không
# có gì đổi và 2,6 s cho một file sửa; một lần tìm mất dưới 2 s.
TIMEOUT_LUMEN_SEARCH = 15
# `agent-lsp doctor` starts every declared language server for real; measured 6.0 s for 14 servers
# (setup_status.py), so 90 s is generous without letting a hung server stall the ladder.
TIMEOUT_DOCTOR = 90
# How much of a failed server's `Error:` line rung 3 quotes — enough to name the cause.
DAI_LOI_DOCTOR = 100
# `agent-lsp doctor` prints one block per server: "● <lang> (<binary>)", then "Status:"/"Error:".
_RE_DOCTOR_DAU = re.compile(r"^\s*●\s+(?P<lang>\S+)\s+\(")
_RE_DOCTOR_TRUONG = re.compile(r"^\s+(?P<khoa>Status|Error):\s*(?P<gia_tri>.*)$")
# Dấu mốc `tdq_finish` để lại sau mỗi lần dựng index. Bậc 5 chỉ ĐỌC mốc này, không bao giờ ghi —
# chủ sở hữu duy nhất của việc dựng lại là bước kết lượt.
DAU_MOC_INDEX = os.path.join("docs", "tdq", ".tdq-lumen-index")
# Câu hỏi dùng làm phép thử vòng đi-về: khái niệm chung, không gắn với ký hiệu nào của repo nào,
# nên nó không mục nát khi code đổi tên.
PROBE_LUMEN = "ghi trạng thái ra file"
MODEL_LUMEN_MAC_DINH = "ordis/jina-embeddings-v2-base-code"   # mặc định của chính lumen
CONFIG_LUMEN = os.path.expanduser("~/.config/lumen/config.yaml")
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
    "go": ("Go", "gopls", "brew install go gopls  # gopls gọi lệnh `go` lúc chạy, thiếu Go là panic"),
    "rust": ("Rust", "rust-analyzer", "rustup component add rust-analyzer"),
    "java": ("Java", "jdtls", "tải từ https://download.eclipse.org/jdtls/snapshots/"),
    "c": ("C", "clangd", "brew install llvm"),
    "cpp": ("C++", "clangd", "brew install llvm"),
    "ruby": ("Ruby", "solargraph", "gem install solargraph"),
    "php": ("PHP", "intelephense", "npm i -g intelephense"),
    "csharp": ("C#", "omnisharp", "tải omnisharp-osx-arm64-net6.0.tar.gz từ github.com/OmniSharp/omnisharp-roslyn "
                                 "→ giải nén vào ~/.local/share/omnisharp → ln -sf .../OmniSharp ~/.local/bin/omnisharp "
                                 "# bản framework-dependent, phải có DOTNET_ROOT lúc chạy"),
    "dockerfile": ("Dockerfile", "docker-language-server", "brew install docker-language-server"),
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
    "dockerfile": ([], "A"),
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


def _run(cmd, cwd=None, timeout=CHECK_TIMEOUT):
    """Run a read-only probe, return (rc, output). Infrastructure errors become results, never raised.

    `cwd` matters for any tool that answers about the directory it runs in — `agent-lsp doctor`
    and `graphify god-nodes` both do. It lives here rather than in a second copy of this wrapper:
    `tdq_setup.py` had grown its own, identical but for that one argument.
    """
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True,
                           encoding="utf-8", errors="replace", text=True, timeout=timeout)
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


def doc_doctor(text):
    """Parse `agent-lsp doctor` output into {lang: (status, error_or_empty)}; pure, never raises."""
    ket_qua = {}
    lang = None
    for dong in (text or "").splitlines():
        dau = _RE_DOCTOR_DAU.match(dong)
        if dau:
            lang = dau.group("lang").casefold()
            ket_qua[lang] = ("", "")
            continue
        truong = _RE_DOCTOR_TRUONG.match(dong)
        if truong and lang:
            status, loi = ket_qua[lang]
            gia_tri = truong.group("gia_tri").strip()
            if truong.group("khoa") == "Status":
                status = gia_tri.casefold()
            elif not loi:
                loi = gia_tri
            ket_qua[lang] = (status, loi)
    return {k: v for k, v in ket_qua.items() if v[0]}


def _chay_doctor(project):
    """Start the language servers for real via `agent-lsp doctor` in the project.

    Returns (parsed, reason): `parsed` is doc_doctor's dict, or None with a reason when the
    probe could not run or printed nothing parseable. The binary is called by its resolved
    path, and with the same server arguments Claude Code registered, so the probe exercises
    the exact setup the MCP server uses.
    """
    agent_lsp = shutil.which("agent-lsp")
    if not agent_lsp:
        return None, "không thấy agent-lsp trên PATH"
    server = (_doc_json("~/.claude.json").get("mcpServers") or {}).get(MCP_SERVER_NAME) or {}
    args = [str(a) for a in (server.get("args") or []) if isinstance(a, str)]
    rc, out = _run([agent_lsp, "doctor"] + args, cwd=project, timeout=TIMEOUT_DOCTOR)
    parsed = doc_doctor(out)
    if parsed:
        return parsed, ""
    ly_do = (out.splitlines()[0].strip() if out else f"mã thoát {rc}, không in gì")
    return None, ly_do[:DAI_LOI_DOCTOR]


def bac3_language_server(project):
    """Rung 3 — one language server per language the project uses, and it really starts.

    Gate 1: the server binary is on PATH. Gate 2: `agent-lsp doctor` actually starts it; a
    `failed` status fails the rung with the server's own error. Languages doctor does not
    report (e.g. CSS) are judged by gate 1 alone; when doctor itself cannot run, the gate-1
    verdict stands and the detail says the start was not tried.
    """
    dung = do_ngon_ngu(project)
    if not dung:
        return Bac(3, "language server theo project", True, "project không có ngôn ngữ nào cần server")
    thieu = []
    for lang in sorted(dung, key=lambda k: -dung[k]):
        ten, binary, lenh = LANG_SERVER[lang]
        if not shutil.which(binary):
            thieu.append((ten, binary, lenh))
    if thieu:
        chi_tiet = "thiếu " + ", ".join(f"{ten} ({binary})" for ten, binary, _ in thieu)
        lenh = " ; ".join(sorted({lenh for _, _, lenh in thieu}))
        return Bac(3, "language server theo project", False, chi_tiet, lenh)
    du = f"đủ cho {len(dung)} ngôn ngữ: " + ", ".join(LANG_SERVER[l][0] for l in sorted(dung))
    doctor, ly_do = _chay_doctor(project)
    if doctor is None:
        return Bac(3, "language server theo project", True,
                   f"{du} (chưa khởi động thử được: {ly_do})")
    hong = []
    for lang in sorted(dung):
        status, loi = doctor.get(lang.casefold(), ("", ""))
        if status == "failed":
            hong.append((lang, loi, LANG_SERVER[lang][2]))
    if not hong:
        return Bac(3, "language server theo project", True, f"{du}, khởi động thử ok")
    chi_tiet = "không khởi động được: " + "; ".join(
        f"{lang} — {' '.join(loi.split())[:DAI_LOI_DOCTOR] or 'không rõ lỗi'}" for lang, loi, _ in hong)
    lenh = " ; ".join(sorted({lenh for _, _, lenh in hong}))
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


def _model_lumen():
    """Model embedding lumen ĐANG dùng, theo đúng thứ tự lumen tự quyết.

    config.yaml → $LUMEN_EMBED_MODEL → mặc định. Hằng số cứng ở đây từng làm bậc 5 đòi một
    model mà máy đã cố ý thay, nên giá trị phải đọc từ cấu hình thật.
    Parser tối giản, chỉ stdlib: file chỉ có một trường `model` lặp lại cho mỗi server, và
    lumen bắt buộc mọi server cùng model (dims lệch thì vector không khớp index) → lấy cái đầu.
    Config hỏng/không đọc được là chuyện của lumen: rơi về lớp sau, không bao giờ ném lên bậc 5.
    """
    try:
        with open(CONFIG_LUMEN, encoding="utf-8", errors="replace") as f:
            for dong in f:
                dong = dong.split("#", 1)[0]
                khoa, dau, gia_tri = dong.partition("model:")
                if dau and not khoa.strip(" -\t"):
                    ten = gia_tri.strip().strip("'\"")
                    if ten:
                        return ten
    except OSError:
        pass
    return os.environ.get("LUMEN_EMBED_MODEL") or MODEL_LUMEN_MAC_DINH


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


def _duong_dan_manifest(model):
    """Manifest của một model trong kho Ollama, theo đúng cách Ollama đặt tên.

    Tên đầy đủ là `namespace/ten:tag`; thiếu namespace thì Ollama hiểu là `library`, thiếu tag
    thì hiểu là `latest`. Ghép thẳng chuỗi (bản cũ) chỉ đúng với tên có sẵn "/" và không có tag.
    """
    ten, _, tag = model.partition(":")
    namespace, dau, ten_ngan = ten.partition("/")
    if not dau:
        namespace, ten_ngan = "library", ten
    goc = os.path.expanduser("~/.ollama/models/manifests/registry.ollama.ai")
    return os.path.join(goc, namespace, ten_ngan, tag or "latest")


def _model_da_pull(model):
    """Is lumen's embedding model on disk? The manifest is readable even with the daemon down."""
    return os.path.exists(_duong_dan_manifest(model))


def bac5_lumen(project=None):
    """Rung 5 — lumen's health. Warning only: lumen is the FALLBACK, agent-lsp is the main layer.

    The socket is asked FIRST, and `which` only decides between "installed but asleep" and
    "not installed at all". Measured 2026-09-28 on the user's macOS: `/opt/homebrew/bin/ollama`
    exists and a login shell finds it, while `shutil.which` from a non-login process returns
    None — the old order concluded "missing" and printed an install command for something that
    was serving requests at that very moment. A live socket IS the proof; PATH is not.
    """
    dang_chay = _ollama_dang_chay()
    if not dang_chay and not shutil.which("ollama"):
        return Bac(5, "sức khoẻ lumen", False, "thiếu ollama — lumen không chạy được",
                   "brew install ollama", chi_canh_bao=True)
    model = _model_lumen()
    if not _model_da_pull(model):
        return Bac(5, "sức khoẻ lumen", False, f"thiếu model {model}",
                   f"ollama pull {model}", chi_canh_bao=True)
    if not dang_chay:
        return Bac(5, "sức khoẻ lumen", False,
                   "ollama chưa chạy — sẽ đánh thức khi cần bằng `tdq_lsp.py wake`",
                   chi_canh_bao=True)
    thieu_binary, lenh_va = _lumen_thieu_binary_windows()
    if thieu_binary:
        return Bac(5, "sức khoẻ lumen", False, thieu_binary, lenh_va, chi_canh_bao=True)
    # Nhận project qua tham số: thang bậc được gọi với MỘT thư mục, và bậc 5 từng tự suy ra thư
    # mục khác bằng `_project_dir()` — nên `setup_status.py` và test nhận một phán quyết nói về
    # thư mục khác với các bậc còn lại.
    project = project or _project_dir()
    cu, mo_ta = _index_cu_hon_code(project)
    if cu:
        return Bac(5, "sức khoẻ lumen", False, f"index chưa có nội dung mới nhất — {mo_ta}",
                   f"lumen index {project}", chi_canh_bao=True)
    tra_loi, chi_tiet = _lumen_tra_loi_duoc(project)
    if not tra_loi:
        return Bac(5, "sức khoẻ lumen", False,
                   f"vòng đi-về lumen hỏng — {chi_tiet}",
                   f"lumen search \"{PROBE_LUMEN}\" -p {project}", chi_canh_bao=True)
    return Bac(5, "sức khoẻ lumen", True, f"ollama đang chạy, có {model}, lumen trả lời được")


@functools.lru_cache(maxsize=8)
def _moc_code_moi_nhat(project):
    """Mốc sửa gần nhất trong các file mã nguồn của project (epoch), hoặc None khi không có file nào.

    So với MÃ NGUỒN chứ không so với commit mới nhất. Bản đầu so với commit, và nó sai theo một
    cách khó thấy: `tdq_finish` dựng lại đồ thị TRONG lượt, còn commit xảy ra SAU đó — nên ngay
    sau mỗi lần commit, đồ thị luôn "cũ hơn commit" và bậc 8 cảnh báo vĩnh viễn. Chiều ngược lại
    còn tệ hơn: một đồ thị dựng trước các sửa đổi chưa commit của lượt này vẫn được cho là mới.
    Câu hỏi thật là "đồ thị có cũ hơn code không", nên hãy hỏi đúng câu đó.
    """
    moi_nhat = None
    for goc, thu_muc, tep in os.walk(project):
        thu_muc[:] = [t for t in thu_muc if t not in SKIP_DIRS and t != "graphify-out"]
        for ten in tep:
            if os.path.splitext(ten)[1] not in EXT_LANG:
                continue
            try:
                moc = os.path.getmtime(os.path.join(goc, ten))
            except OSError:
                continue
            if moi_nhat is None or moc > moi_nhat:
                moi_nhat = moc
    return moi_nhat


def bac8_graphify(project):
    """Rung 8 — the graph the fourth search layer reads. Warning only, like rungs 5 and 6.

    Why it exists: graphify was the one tool of the four with no rung at all, and it failed the
    exact way an unwatched index fails. Measured 2026-09-28 on this repo: the graph was 8 days
    old and 34% of its nodes (845 of 2415) pointed into a directory deleted a week earlier, so
    `explain` answered about code that no longer existed. Nobody rebuilt it, and nothing ever
    said so.
    """
    ten = "đồ thị graphify"
    if not shutil.which("graphify"):
        return Bac(8, ten, False, "chưa cài graphify — mất tầng bản đồ quan hệ",
                   "uv tool install graphifyy", chi_canh_bao=True)
    do_thi = os.path.join(project, "graphify-out", "graph.json")
    lenh_dung = f"cd {project} && graphify extract . --code-only"
    if not os.path.isfile(do_thi):
        return Bac(8, ten, False, "chưa có đồ thị nào", lenh_dung, chi_canh_bao=True)
    moc_code = _moc_code_moi_nhat(project)
    if moc_code is None:
        return Bac(8, ten, True, "có đồ thị (không thấy file mã nguồn nào để so mốc)")
    tuoi = moc_code - os.path.getmtime(do_thi)
    if tuoi > 0:
        return Bac(8, ten, False,
                   f"đồ thị cũ hơn mã nguồn {int(tuoi // 60)} phút",
                   lenh_dung, chi_canh_bao=True)
    return Bac(8, ten, True, "đồ thị mới hơn mọi file mã nguồn")


@functools.lru_cache(maxsize=1)
def _binary_lumen():
    """Đường dẫn binary lumen chạy được, hoặc "" khi máy chưa có.

    Ưu tiên `bin/lumen` (bản launcher tự dò), rồi tới binary theo nền tảng. Cùng thư mục cache
    mà `_lumen_thieu_binary_windows` soi, nên hai phép dò không bao giờ nói về hai bản khác nhau.
    """
    tren_path = shutil.which("lumen")
    if tren_path:
        return tren_path
    goc = os.path.expanduser("~/.claude/plugins/cache")
    ung_vien = sorted(glob.glob(os.path.join(goc, "*", "lumen", "*", "bin", "lumen*")))
    for duong in reversed(ung_vien):
        if os.path.isfile(duong) and not duong.endswith((".sha256", ".txt")):
            return duong
    return ""


def _index_cu_hon_code(project):
    """-> (index cũ hơn code?, mô tả). THUẦN ĐỌC: không chạy lệnh nào, không ghi gì.

    Bản đầu của phép đo này chạy `lumen index` ngay trong lúc chẩn đoán. Sai tầng, và sai theo
    ba hướng cùng lúc: `tdq_lsp.py` tự khai ở đầu file là nó KHÔNG BAO GIỜ sửa gì; `chay_kiem`
    chạy ở bước 1b của MỌI request và cả trong trang trạng thái, nên một hàm chỉ để đọc lại đi
    dựng lại index của user; và `tdq_finish` đã dựng lại ở cuối lượt trước, nên lượt sau dựng
    thêm một lần nữa cho cùng tập thay đổi.

    Nay chỉ so hai mốc: dấu mốc mà `tdq_finish` để lại sau mỗi lần dựng, với file mã nguồn mới
    nhất. Cùng kỹ thuật bậc 8 dùng cho đồ thị graphify, và rẻ hơn hai bậc: không spawn tiến
    trình nào.
    """
    dau_moc = os.path.join(project, DAU_MOC_INDEX)
    moc_code = _moc_code_moi_nhat(project)
    if moc_code is None:
        return False, ""
    if not os.path.isfile(dau_moc):
        return True, "chưa có lần dựng index nào của workflow"
    tre = moc_code - os.path.getmtime(dau_moc)
    if tre > 0:
        return True, f"code mới hơn lần dựng index gần nhất {int(tre // 60)} phút"
    return False, ""


def _lumen_tra_loi_duoc(project):
    """-> (trả lời được?, mô tả) — hỏi lumen một câu THẬT rồi đọc câu trả lời.

    Bậc 5 cũ chỉ hỏi "daemon có sống không", nên nó báo ĐẠT suốt một phiên mà MCP `lumen` chết
    (`CONNECTION_CLOSED`, 2026-09-28). Phép đo này đi bằng CLI chứ không qua MCP: CLI không bị
    cache TTL che mắt, và nó còn trả lời được khi lớp MCP đã đứt.
    """
    lumen = _binary_lumen()
    if not lumen:
        return False, "không tìm thấy binary lumen"
    rc, ra = _run([lumen, "search", PROBE_LUMEN, "-p", project, "-n", "1", "--summary"],
                  timeout=TIMEOUT_LUMEN_SEARCH)
    if rc != 0:
        return False, ra.splitlines()[0][:80] if ra else f"thoát {rc}"
    if "<result:file" not in ra:
        return False, "không kết quả nào"
    return True, "có kết quả"


def _lumen_thieu_binary_windows():
    """-> (lý do, lệnh vá) khi launcher bash của lumen không tìm ra binary trên Windows.

    Đo được trên máy Windows: `scripts/run` của lumen dò nền tảng bằng `uname -s`, mà Git Bash
    trả `mingw64_nt-10.0-26100` chứ không phải `windows`. Không có nhánh nào ánh xạ `mingw*`, nên
    nó tìm `bin/lumen-mingw64_nt-...-amd64`, bỏ qua `lumen-windows-amd64.exe` đã nằm sẵn, rồi đi
    tải một asset cùng tên đó — GitHub trả 404 và hook `SessionStart` chết. Nhánh `.cmd` của
    chính file đó làm đúng; chỉ nhánh bash thiếu, mà Claude Code khai `"shell": "bash"`.

    Launcher kiểm `bin/lumen` TRƯỚC tiên, không kèm tên hệ — nên một bản sao tên đó vá được mà
    không phải sửa một dòng code nào của plugin khác. Hàm này chỉ BÁO và in lệnh; theo đúng
    nguyên tắc đầu file, script không bao giờ tự sửa file của plugin khác.

    Bản vá không sống qua một lần update lumen, vì update tạo thư mục phiên bản mới. Đó chính là
    lý do phép dò này tồn tại: để lần sau nó hỏng thì bậc thang nói ra, thay vì hook chết im lặng.
    """
    if not sys.platform.startswith("win"):
        return "", ""
    goc = os.path.expanduser("~/.claude/plugins/cache")
    ung_vien = sorted(glob.glob(os.path.join(goc, "*", "lumen", "*", "scripts", "run")))
    if not ung_vien:
        return "", ""
    thu_muc = os.path.dirname(os.path.dirname(ung_vien[-1]))
    if os.path.isfile(os.path.join(thu_muc, "bin", "lumen")):
        return "", ""
    exe = glob.glob(os.path.join(thu_muc, "bin", "lumen-windows-*.exe"))
    if not exe:
        return ("lumen chưa tải binary cho Windows — chạy `scripts/run.cmd --version` một lần",
                f'"{os.path.join(thu_muc, "scripts", "run.cmd")}" --version')
    return ("launcher bash của lumen không dò ra binary trên Windows (uname trả `mingw*`), "
            "hook SessionStart sẽ chết với 404",
            f'cp "{exe[-1]}" "{os.path.join(thu_muc, "bin", "lumen")}"')


def _plugin_dang_bat():
    """The install paths Claude Code actually loads — the cache also holds stale older versions.

    Two sources, because one of them is not always there. `installed_plugins.json` covers what
    was installed on this machine; it is missing entirely on a machine that never ran
    `plugin install`, and even when present it does not list the plugins Claude Code syncs from
    the account into `~/.claude/plugins/synced/<uuid>/<name>/`. Measured on the user's machine:
    the file named one plugin while a second sat, unlisted, under `synced/`. Rung 6 asks
    "does another plugin push a different search order" — a plugin it cannot see is a plugin it
    cannot answer for.
    """
    duong_dan = []
    data = _doc_json("~/.claude/plugins/installed_plugins.json")
    for ten, ban_ghi in (data.get("plugins") or {}).items():
        for b in ban_ghi if isinstance(ban_ghi, list) else []:
            p = b.get("installPath")
            if p:
                duong_dan.append((ten, p))

    da_co = {os.path.normpath(p) for _, p in duong_dan}
    goc_synced = os.path.expanduser("~/.claude/plugins/synced")
    for uuid in sorted(glob.glob(os.path.join(goc_synced, "*"))):
        for duong in sorted(glob.glob(os.path.join(uuid, "*"))):
            if not os.path.isdir(duong) or os.path.normpath(duong) in da_co:
                continue
            duong_dan.append((os.path.basename(duong), duong))
    return duong_dan


def hook_xung_dot():
    """-> [(tên plugin, file hooks.json, matcher)] của mọi hook ngoài đang đè thứ tự tìm kiếm.

    Tách riêng khỏi bậc 6 để `tdq_setup.py` dùng lại đúng PHÉP DÒ này khi nó đi vá. Hai nơi cùng
    một danh sách thì không bao giờ có chuyện bậc thang báo một đằng, lệnh vá làm một nẻo.
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
    return xung_dot


def bac6_hook_xung_dot(project):
    """Rung 6 — an outside plugin hook pushing a search order other than the TDQ one.

    Report only: THIS script never edits another plugin's file. The one command allowed to do
    that is `tdq_setup.py`, which the user types themselves.
    """
    xung_dot = hook_xung_dot()
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
           bac5_lumen(project), bac6_hook_xung_dot(project), bac7_cau_hinh_goc_import(project),
           bac8_graphify(project)]
    for b in bac:
        _log(f"bậc {b.so} {b.ten} → {'ĐẠT' if b.dat else 'THIẾU'}")
    return bac


def chay_smoke(project):
    """Ask each of the four search layers one real question -> [(layer, passed?, detail)].

    The smoke functions stay in `tdq_setup.py` (their public names and the tests that patch them
    keep working); the import is lazy because `tdq_setup` imports this module at top level.
    Importing it installs nothing — every install there sits behind its own `main`.
    """
    import tdq_setup
    return tdq_setup.smoke_bon_tang(project)


def kiem_mot_lenh(project):
    """THE one check: the 8 rungs, then the 4-layer smoke, then ONE total line.

    Observed 2026-10-02: with the smoke living only in `tdq_setup.py`, an agent ran just
    `check`, read "8/8 bậc ĐẠT" and skipped the smoke while two layers could not answer. So the
    total is ĐẠT only when no rung blocks (warnings do not) AND every smoke layer answered.
    `tdq_setup.py` calls this same function instead of keeping its own copy.

    -> (exit code, rungs, smoke rows). Exit: EXIT_THIEU when a rung blocks, else EXIT_SMOKE when
    a layer failed, else EXIT_OK.
    """
    bac = chay_kiem(project)
    for b in bac:
        b.in_ra()
    thieu = [b for b in bac if not b.dat and not b.chi_canh_bao]
    canh_bao = [b for b in bac if not b.dat and b.chi_canh_bao]

    print("\nSmoke test bốn tầng:")
    smoke = chay_smoke(project)
    for ten, dat, chi_tiet in smoke:
        print(f"  {ten:<9} {'ĐẠT ' if dat else 'TRƯỢT'} · {chi_tiet}")
    truot = [ten for ten, dat, _ in smoke if not dat]

    phan = [f"{len(bac) - len(thieu) - len(canh_bao)}/{len(bac)} bậc ĐẠT",
            f"smoke {len(smoke) - len(truot)}/{len(smoke)} tầng trả lời được"]
    if thieu:
        phan.append(f"{len(thieu)} bậc cần bạn cho phép cài")
    if canh_bao:
        phan.append(f"{len(canh_bao)} cảnh báo không chặn")
    if truot:
        phan.append(f"{len(truot)} tầng trượt: {', '.join(truot)}")
    print(f"\nTổng: {'CHƯA ĐẠT' if thieu or truot else 'ĐẠT'} · " + " · ".join(phan))
    if thieu:
        print("Script KHÔNG tự cài. Hãy duyệt từng lệnh ở trên rồi chạy tay.")
    _log(f"done · {len(thieu)} bậc thiếu · {len(canh_bao)} cảnh báo · {len(truot)} tầng trượt")
    rc = EXIT_THIEU if thieu else (EXIT_SMOKE if truot else EXIT_OK)
    return rc, bac, smoke


def cmd_kiem(args):
    return kiem_mot_lenh(_project_dir())[0]


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
        model = _model_lumen()
        rc, out = _run(["ollama", "stop", model])
        print(f"Đã nhả model {model}." if rc == 0 else f"Không nhả được model: {out}")
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
        _log(f"release → tắt daemon pid={pid}")
    except OSError as exc:
        _log(f"release → daemon pid={pid} đã không còn ({exc})")
    _xoa_dau()
    return EXIT_OK


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
import utf8_io  # noqa: E402,F401 — imported for its side effect: stdout/stderr become UTF-8
import tdq_ten_lenh  # noqa: E402

BANG_TEN = tdq_ten_lenh.BANG_DOI_TEN["tdq_lsp.py"]


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Chẩn đoán bộ agent-lsp cho máy và cho project này. Script không tự cài gì.")
    ap.add_argument("--khong-log", action="store_true", help="tắt log service")
    sub = ap.add_subparsers(dest="lenh", required=True)
    sub.add_parser("check", help="chạy 8 bậc rồi smoke 4 tầng, in một dòng tổng")
    dt = sub.add_parser("wake", help="đánh thức Ollama theo yêu cầu, chỉ khi LSP tìm không thấy")
    dt.add_argument("--han-cho", type=float, default=30.0, help="giây chờ Ollama trả lời (mặc định 30)")
    sub.add_parser("release", help="nhả model embedding ngay sau khi tìm xong")
    return ap.parse_args(argv)


def main(argv):
    global _LOG_TAT
    argv = list(argv)
    # Hidden alias (`kiem` → `check`), resolved before argparse sees it.
    if argv and not argv[0].startswith("-"):
        chinh_thuc = tdq_ten_lenh.giai_ten(argv[0], BANG_TEN)
        if chinh_thuc is not None:
            argv[0] = chinh_thuc
    args = parse_args(argv)
    _LOG_TAT = args.khong_log
    return {"check": cmd_kiem, "wake": cmd_danh_thuc, "release": cmd_nha}[args.lenh](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
