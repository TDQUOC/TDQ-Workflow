#!/usr/bin/env python3
"""claude_export.py — sinh và kiểm bundle export cấu hình Claude Code sang máy khác.

Thay bộ 7 bước tay của `claude-export/INSTRUCTIONS.md` (bản trước 0.7.0) bằng 2 lệnh:

  claude_export.py build --dest <dir> [--zip]
      Sinh bundle: clone repo (giữ `.git`, chỉ file tracked), copy cấu hình `~/.claude`
      đã lọc secret, xuất `config/mcp-servers.json` để máy đích khôi phục MCP server,
      ghi `manifest.json` (phiên bản plugin, commit SHA, sha256 từng file nguồn).

  claude_export.py check --dest <dir>
      Đo độ lệch giữa máy nguồn HIỆN TẠI và bundle đã sinh: file cấu hình đổi nội dung,
      repo đã sang commit khác, phiên bản plugin đã bump. exit 0 = sạch, 1 = có lệch.

Vì sao clone thay vì `rsync --exclude`: rsync không đọc `.gitignore` nên bản cũ mang
theo 15 MB `graphify-out/`, `docs/tdq/state.json` của request đang dở, `.tdq-turn.jsonl`
và cả `.DS_Store`. `git clone` chỉ lấy file tracked nên 4 lỗi đó biến mất cùng lúc.

Bảo mật: script chỉ ĐỌC `~/.claude.json` (chứa `oauthAccount`/`machineID`) và không bao
giờ copy đè file đó — máy đích khôi phục MCP bằng `claude mcp add-json --scope user`.
Giá trị key thật trong `settings.json` bị thay bằng placeholder trước khi ghi ra bundle,
sau đó bundle được quét lại; còn sót thì XOÁ bundle và exit 3.

Exit code: 0 ok · 1 có drift (`check`) · 2 đích/bundle không hợp lệ · 3 lộ secret.
Env: TDQ_EXPORT_CLI_VERSIONS=0 tắt bước dò version CLI (dùng cho test, nhanh hơn).
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATE_DIR = os.path.join(REPO_ROOT, "claude-export")
REPO_DIR_NAME = "tdqworkflow-repo"

# File đơn của `~/.claude` mang theo → vị trí trong bundle.
CONFIG_FILES = (
    ("settings.json", "config/settings.json"),
    ("CLAUDE.md", "config/CLAUDE.md"),
    ("plugin-tiers.json", "config/plugin-tiers.json"),
    ("statusline.sh", "config/statusline.sh"),
    ("plugins/installed_plugins.json", "config/installed_plugins.json"),
    ("plugins/known_marketplaces.json", "config/known_marketplaces.json"),
)
# Thư mục của `~/.claude` mang theo → vị trí trong bundle.
CONFIG_DIRS = (
    ("skills/graphify", "config/skills-graphify"),
    (".remember", "config/remember"),
    ("scripts", "config/scripts"),
)
# Rác runtime: không bao giờ đưa vào bundle, dù nằm ở đâu.
SKIP_DIRS = {"__pycache__", "tmp", "logs", "cache", ".git"}
SKIP_NAMES = {".DS_Store"}
# Tên biến môi trường coi là bí mật → giá trị thật bị thay placeholder.
SECRET_NAME = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD)", re.IGNORECASE)
MIN_SECRET_LEN = 8
MAX_TEXT_BYTES = 8 * 1024 * 1024
CLI_TOOLS = ("claude", "node", "python3", "git", "uv", "graphify", "codex", "agy")

_LOG = {"level": 1}   # 0 = quiet, 1 = info, 2 = debug


# ------------------------------------------------------------------ log service

def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def set_log_level(quiet=False, verbose=False):
    _LOG["level"] = 0 if quiet else (2 if verbose else 1)


def log(message, level="info"):
    """In 1 dòng có timestamp ISO ra stderr. Bật mặc định, tắt bằng `--quiet`."""
    if _LOG["level"] < (2 if level == "debug" else 1):
        return
    print(f"[{_now()}] {level:5s} {message}", file=sys.stderr)


# ------------------------------------------------------------------ hàm nền

def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_mcp_servers(path):
    """Đọc khoá `mcpServers` của một file kiểu `~/.claude.json`. Chỉ đọc, không ghi."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    servers = data.get("mcpServers")
    return servers if isinstance(servers, dict) else {}


def harvest_secrets(settings_path):
    """{tên biến: giá trị thật} lấy từ khối `env` của settings.json.

    Bỏ qua giá trị dạng `${VAR}` — đó là tham chiếu biến môi trường, không phải key.
    """
    try:
        with open(settings_path, encoding="utf-8") as f:
            env = json.load(f).get("env", {})
    except (OSError, ValueError):
        return {}
    return {name: value for name, value in env.items()
            if isinstance(value, str) and SECRET_NAME.search(name)
            and len(value) >= MIN_SECRET_LEN and not value.startswith("${")}


def _text_files(root):
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(names):
            if name in SKIP_NAMES:
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_TEXT_BYTES:
                    continue
                with open(path, encoding="utf-8") as f:
                    yield path, f.read()
            except (OSError, UnicodeDecodeError):
                continue


def scan_secrets(root, values):
    """Đường dẫn mọi file văn bản dưới `root` còn chứa một trong `values`."""
    wanted = [v for v in values if isinstance(v, str) and len(v) >= MIN_SECRET_LEN]
    if not wanted:
        return []
    return sorted(path for path, text in _text_files(root)
                  if any(v in text for v in wanted))


def redact_bundle(root, secrets):
    """Thay mọi giá trị key thật trong bundle bằng placeholder. Trả file đã sửa."""
    if not secrets:
        return []
    changed = []
    for path, text in _text_files(root):
        new = text
        for name, value in secrets.items():
            new = new.replace(value, f"<{name} — điền lại>")
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            changed.append(path)
    return changed


def collect_config_files(claude_home):
    """{đường dẫn trong bundle: đường dẫn nguồn} cho mọi file cấu hình mang theo."""
    found = {}
    for rel_src, rel_dest in CONFIG_FILES:
        src = os.path.join(claude_home, rel_src)
        if os.path.isfile(src):
            found[rel_dest] = src
    for rel_src, rel_dest in CONFIG_DIRS:
        src_dir = os.path.join(claude_home, rel_src)
        if not os.path.isdir(src_dir):
            continue
        for dirpath, dirnames, names in os.walk(src_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in sorted(names):
                if name in SKIP_NAMES:
                    continue
                src = os.path.join(dirpath, name)
                rel = os.path.relpath(src, src_dir).replace(os.sep, "/")
                found[f"{rel_dest}/{rel}"] = src
    return found


# ------------------------------------------------------------------ lệnh build

def _git_out(repo, *args):
    proc = subprocess.run(["git", "-C", repo, *args],
                          capture_output=True, text=True, timeout=120)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def plugin_version(repo):
    try:
        with open(os.path.join(repo, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("version", "")
    except (OSError, ValueError):
        return ""


def dest_is_writable(dest):
    """(được ghi đè?, lý do). Chỉ ghi đè thư mục trống hoặc bundle do chính script sinh."""
    if not os.path.exists(dest):
        return True, "đích chưa tồn tại"
    if not os.path.isdir(dest):
        return False, "đích đã tồn tại nhưng không phải thư mục"
    entries = sorted(os.listdir(dest))
    if not entries:
        return True, "đích rỗng"
    manifest = os.path.join(dest, "manifest.json")
    if os.path.isfile(manifest):
        try:
            with open(manifest, encoding="utf-8") as f:
                if "exported_at" in json.load(f):
                    return True, "đích là bundle do script này sinh"
        except (OSError, ValueError):
            pass
    return False, "đích có dữ liệu lạ: " + ", ".join(entries[:3])


def clone_repo(repo, dest):
    target = os.path.join(dest, REPO_DIR_NAME)
    dirty = _git_out(repo, "status", "--porcelain")
    if dirty:
        log(f"repo nguồn còn {len(dirty.splitlines())} file chưa commit — "
            "clone chỉ lấy phần đã commit", level="info")
    subprocess.run(["git", "clone", "--quiet", repo, target], check=True, timeout=600)
    log(f"clone repo → {target}", level="debug")
    return target


def copy_repo_memory(repo, dest):
    """`.remember/` của repo là untracked nên clone không mang theo — copy riêng."""
    src = os.path.join(repo, ".remember")
    if not os.path.isdir(src):
        return 0
    target = os.path.join(dest, REPO_DIR_NAME, ".remember")
    count = 0
    for dirpath, dirnames, names in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(names):
            if name in SKIP_NAMES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), src)
            out = os.path.join(target, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(os.path.join(dirpath, name), out)
            count += 1
    log(f"copy {count} file .remember của repo (bỏ tmp/ và logs/)")
    return count


def copy_config(claude_home, dest):
    files = collect_config_files(claude_home)
    for rel_dest, src in files.items():
        out = os.path.join(dest, rel_dest)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy2(src, out)
    log(f"copy {len(files)} file cấu hình từ {claude_home}")
    return files


def rewrite_marketplace_path(dest):
    """Trỏ marketplace `tdq-local` vào repo NẰM TRONG bundle, nếu không plugin không load."""
    new_path = os.path.join(dest, REPO_DIR_NAME)
    source = {"source": "directory", "path": new_path}
    settings_path = os.path.join(dest, "config", "settings.json")
    if os.path.isfile(settings_path):
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
        settings.setdefault("extraKnownMarketplaces", {}) \
                .setdefault("tdq-local", {})["source"] = source
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    known_path = os.path.join(dest, "config", "known_marketplaces.json")
    if os.path.isfile(known_path):
        with open(known_path, encoding="utf-8") as f:
            known = json.load(f)
        entry = known.setdefault("tdq-local", {})
        entry["source"] = source
        entry["installLocation"] = new_path
        with open(known_path, "w", encoding="utf-8") as f:
            json.dump(known, f, ensure_ascii=False, indent=2)
    log(f"rewrite path marketplace tdq-local → {new_path}")


def write_mcp_servers(claude_json, dest):
    servers = read_mcp_servers(claude_json)
    out = os.path.join(dest, "config", "mcp-servers.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(servers, f, ensure_ascii=False, indent=2)
    log(f"xuất {len(servers)} MCP server → config/mcp-servers.json")
    return servers


def cli_versions():
    if os.environ.get("TDQ_EXPORT_CLI_VERSIONS", "1") == "0":
        return {}
    found = {}
    for tool in CLI_TOOLS:
        if not shutil.which(tool):
            continue
        try:
            proc = subprocess.run([tool, "--version"], capture_output=True,
                                  text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if proc.returncode == 0:
            found[tool] = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    log(f"dò được version của {len(found)} CLI")
    return found


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_manifest(dest, repo, claude_home, files, servers):
    """Khung khoá lấy từ MANIFEST.template.json để template và code không lệch nhau."""
    manifest = _load_json(os.path.join(TEMPLATE_DIR, "MANIFEST.template.json"), {})
    plugins = _load_json(os.path.join(claude_home, "plugins", "installed_plugins.json"),
                         {}).get("plugins", {})
    manifest["plugins"] = {
        name: entries for name, entries in plugins.items()
        if isinstance(entries, list) and any(e.get("scope") == "user" for e in entries)
    }
    manifest["marketplaces"] = _load_json(
        os.path.join(claude_home, "plugins", "known_marketplaces.json"), {})
    manifest["mcp_servers"] = servers
    manifest["cli_dependencies"] = cli_versions()
    manifest["plugin_version"] = plugin_version(repo)
    manifest["repo_commit"] = _git_out(repo, "rev-parse", "HEAD")
    manifest["exported_at"] = _now()
    manifest["source_files"] = {
        rel: {"source": src, "sha256": sha256_of(src)} for rel, src in sorted(files.items())
    }
    with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    log(f"ghi manifest.json ({len(manifest['source_files'])} file nguồn có sha256)")
    return manifest


def write_readme(dest, manifest):
    template = os.path.join(TEMPLATE_DIR, "README.template.md")
    with open(template, encoding="utf-8") as f:
        text = f.read()
    lines = ["| Marketplace | Nguồn |", "|---|---|"]
    for name, entry in sorted(manifest["marketplaces"].items()):
        source = entry.get("source", {}) if isinstance(entry, dict) else {}
        lines.append(f"| `{name}` | `{source.get('path') or source.get('source', '?')}` |")
    lines += ["", "| Plugin | Marketplace |", "|---|---|"]
    for full in sorted(manifest["plugins"]):
        name, _, market = full.partition("@")
        lines.append(f"| `{name}` | `{market or '?'}` |")
    values = {
        "BUNDLE_NAME": os.path.basename(dest.rstrip(os.sep)),
        "SOURCE_MACHINE_NOTE": f"{sys.platform}, plugin tdq-workflow {manifest['plugin_version']}",
        "EXPORT_DATE": manifest["exported_at"],
        "EXPORT_DEST": dest,
        "PLUGIN_MARKETPLACE_LIST": "\n".join(lines),
        "REPO_COMMIT": manifest["repo_commit"][:8] or "?",
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    with open(os.path.join(dest, "README.md"), "w", encoding="utf-8") as f:
        f.write(text)
    log(f"ghi README.md ({len(manifest['plugins'])} plugin, "
        f"{len(manifest['marketplaces'])} marketplace)")


def make_zip(dest):
    """Nén ra file tạm rồi mới đè — hỏng giữa chừng thì bản zip cũ vẫn còn."""
    final = dest + ".zip"
    tmp = final + ".tmp"
    base = os.path.basename(dest.rstrip(os.sep))
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, names in os.walk(dest):
                dirnames[:] = sorted(dirnames)
                for name in sorted(names):
                    path = os.path.join(dirpath, name)
                    zf.write(path, os.path.join(base, os.path.relpath(path, dest)))
        os.replace(tmp, final)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    log(f"nén xong {final} ({os.path.getsize(final) / 1048576:.1f} MB)")
    return final


def cmd_build(args):
    dest = os.path.abspath(os.path.expanduser(args.dest))
    repo = os.path.abspath(os.path.expanduser(args.repo))
    home = os.path.abspath(os.path.expanduser(args.claude_home))
    claude_json = os.path.abspath(os.path.expanduser(
        args.claude_json or os.path.join(os.path.dirname(home), ".claude.json")))
    log(f"build → {dest}")
    ok, why = dest_is_writable(dest)
    if not ok:
        log(f"từ chối ghi đè: {why}", level="info")
        return 2
    log(f"đích hợp lệ ({why})", level="debug")

    secrets = harvest_secrets(os.path.join(home, "settings.json"))
    log(f"tìm thấy {len(secrets)} biến bí mật cần thay placeholder: "
        f"{', '.join(sorted(secrets)) or 'không có'}")

    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    clone_repo(repo, dest)
    copy_repo_memory(repo, dest)
    files = copy_config(home, dest)
    servers = write_mcp_servers(claude_json, dest)
    rewrite_marketplace_path(dest)
    manifest = write_manifest(dest, repo, home, files, servers)
    write_readme(dest, manifest)

    changed = redact_bundle(dest, secrets)
    log(f"thay placeholder ở {len(changed)} file")
    hits = scan_secrets(dest, list(secrets.values()) + list(args.extra_secret or []))
    if hits:
        shutil.rmtree(dest, ignore_errors=True)
        log(f"PHÁT HIỆN secret còn sót ở {len(hits)} file → đã xoá bundle "
            f"{dest}. File đầu tiên: {os.path.relpath(hits[0], dest)}")
        return 3
    log("quét secret: sạch")

    if args.zip:
        make_zip(dest)
    total = sum(len(names) for _, _, names in os.walk(dest))
    log(f"xong · {total} file · commit {manifest['repo_commit'][:8]} · "
        f"plugin {manifest['plugin_version']}")
    return 0


# ------------------------------------------------------------------ lệnh check

def cmd_check(args):
    dest = os.path.abspath(os.path.expanduser(args.dest))
    repo = os.path.abspath(os.path.expanduser(args.repo))
    manifest_path = os.path.join(dest, "manifest.json")
    if not os.path.isfile(manifest_path):
        log(f"không tìm thấy manifest.json trong {dest} — đây không phải bundle")
        return 2
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        log(f"manifest.json đọc không được ({err}) — bundle hỏng, sinh lại bằng build")
        return 2
    log(f"check bundle sinh lúc {manifest.get('exported_at', '?')}")

    drift = []
    for rel, entry in sorted(manifest.get("source_files", {}).items()):
        src = entry.get("source", "")
        if not os.path.isfile(src):
            drift.append((rel, "thiếu ở nguồn"))
        elif sha256_of(src) != entry.get("sha256"):
            drift.append((rel, "nội dung đã đổi"))
    head = _git_out(repo, "rev-parse", "HEAD")
    old = manifest.get("repo_commit", "")
    if head and old and head != old:
        behind = _git_out(repo, "rev-list", "--count", f"{old}..{head}")
        gap = f"(+{behind})" if behind else "(không so được khoảng cách — SHA cũ không có trong repo)"
        drift.append((REPO_DIR_NAME, f"commit {old[:8]} → {head[:8]} {gap}"))
    now_version = plugin_version(repo)
    if now_version and now_version != manifest.get("plugin_version"):
        drift.append((".claude-plugin/plugin.json",
                      f"version {manifest.get('plugin_version')} → {now_version}"))

    if drift:
        print("| Mục | Lệch thế nào |")
        print("|---|---|")
        for rel, why in drift:
            print(f"| {rel} | {why} |")
    print(f"{len(drift)} mục lệch")
    return 1 if drift else 0


# ------------------------------------------------------------------ CLI

def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="claude_export.py", description="Sinh và kiểm bundle export Claude Code")
    subs = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext in (("build", "sinh bundle"), ("check", "đo drift bundle ↔ nguồn")):
        sub = subs.add_parser(name, help=helptext)
        sub.add_argument("--dest", required=True, help="thư mục bundle")
        sub.add_argument("--repo", default=REPO_ROOT, help="repo TDQWorkflow nguồn")
        sub.add_argument("--claude-home", default=os.path.expanduser("~/.claude"),
                         help="thư mục cấu hình Claude Code của máy nguồn")
        sub.add_argument("--claude-json", default=None,
                         help="file chứa mcpServers (mặc định <cha của claude-home>/.claude.json)")
        sub.add_argument("--quiet", action="store_true", help="tắt log")
        sub.add_argument("--verbose", action="store_true", help="log thêm mức debug")
        if name == "build":
            sub.add_argument("--zip", action="store_true", help="nén bundle thành .zip")
            sub.add_argument("--extra-secret", action="append", default=[],
                             help="chuỗi bí mật cần quét thêm; dính là huỷ bundle")
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    set_log_level(quiet=args.quiet, verbose=args.verbose)
    try:
        return cmd_build(args) if args.cmd == "build" else cmd_check(args)
    except subprocess.CalledProcessError as exc:
        log(f"lệnh ngoài thất bại: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
