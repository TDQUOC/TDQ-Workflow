#!/usr/bin/env python3
"""claude_export.py — build and check the bundle that exports a Claude Code setup to another machine.

Replaces the 7 manual steps of `claude-export/INSTRUCTIONS.md` (before 0.7.0) with 2 commands:

  claude_export.py build --dest <dir> [--zip]
            Build the bundle: clone the repo (keeping `.git`, tracked files only), copy the `~/.claude`
            config with secrets filtered out, emit `config/mcp-servers.json` so the target machine can
            restore its MCP servers, write `manifest.json` (plugin version, commit SHA, sha256 per source file).

  claude_export.py check --dest <dir>
            Measure the drift between the source machine RIGHT NOW and the built bundle: a config file
            whose content changed, a repo moved to another commit, a plugin version bumped. exit 0 = clean, 1 = drift.

Why clone instead of `rsync --exclude`: rsync does not read `.gitignore`, so the old version dragged
along 15 MB of `graphify-out/`, the `docs/tdq/state.json` of a half-finished request, `.tdq-turn.jsonl`
and even `.DS_Store`. `git clone` takes only tracked files, so all 4 faults disappear at once.

Security: the script only READS `~/.claude.json` (which holds `oauthAccount`/`machineID`) and never
copies over that file — the target machine restores MCP with `claude mcp add-json --scope user`.
Real key values in `settings.json` are replaced by a placeholder before being written into the bundle,
and the bundle is then rescanned; anything left over DELETES the bundle and exits 3.

Exit code: 0 ok · 1 drift found (`check`) · 2 invalid destination/bundle · 3 secret leaked.
Env: TDQ_EXPORT_CLI_VERSIONS=0 turns the CLI-version probe off (used by tests, faster).
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

# Single files of `~/.claude` to carry along → their place in the bundle.
CONFIG_FILES = (
    ("settings.json", "config/settings.json"),
    ("CLAUDE.md", "config/CLAUDE.md"),
    ("plugin-tiers.json", "config/plugin-tiers.json"),
    ("statusline.sh", "config/statusline.sh"),
    ("plugins/installed_plugins.json", "config/installed_plugins.json"),
    ("plugins/known_marketplaces.json", "config/known_marketplaces.json"),
)
# FIXED folders of `~/.claude` to carry along → their place in the bundle. `skills/` alone is
# not hard-coded name by name here — `_skill_dirs()` scans so a new skill is never missed.
CONFIG_DIRS = (
    (".remember", "config/remember"),
    ("scripts", "config/scripts"),
)
# Runtime junk: never put into the bundle, wherever it sits.
SKIP_DIRS = {"__pycache__", "tmp", "logs", "cache", ".git"}
SKIP_NAMES = {".DS_Store"}
# Environment variable names treated as secret → the real value is replaced by a placeholder.
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
    """Print 1 line with an ISO timestamp to stderr. On by default, off with `--quiet`."""
    if _LOG["level"] < (2 if level == "debug" else 1):
        return
    print(f"[{_now()}] {level:5s} {message}", file=sys.stderr)


# ------------------------------------------------------------------ helpers

def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_mcp_servers(path):
    """Read the `mcpServers` key of a `~/.claude.json`-style file. Read only, never written."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    servers = data.get("mcpServers")
    return servers if isinstance(servers, dict) else {}


def harvest_secrets(settings_path):
    """{variable name: real value} taken from the `env` block of settings.json.

    Skips a `${VAR}`-shaped value — that is an environment reference, not a key.
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
    """The path of every text file under `root` that still holds one of `values`."""
    wanted = [v for v in values if isinstance(v, str) and len(v) >= MIN_SECRET_LEN]
    if not wanted:
        return []
    return sorted(path for path, text in _text_files(root)
                  if any(v in text for v in wanted))


def redact_bundle(root, secrets):
    """Replace every real key value in the bundle with a placeholder. Returns the edited files."""
    if not secrets:
        return []
    changed = []
    for path, text in _text_files(root):
        new = text
        for name, value in secrets.items():
            new = new.replace(value, f"<{name} — fill this in>")
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            changed.append(path)
    return changed


def _skill_dirs(claude_home):
    """(rel_src, rel_dest) for EVERY user-level skill under `~/.claude/skills/`.

    General instead of hard-coded name by name: a newly installed skill (such as `mem0-memory`)
    is carried along on its own, with no code change each time a skill is added.
    """
    root = os.path.join(claude_home, "skills")
    if not os.path.isdir(root):
        return ()
    return tuple(
        (f"skills/{name}", f"config/skills-{name}")
        for name in sorted(os.listdir(root))
        if os.path.isdir(os.path.join(root, name)) and name not in SKIP_DIRS
    )


def collect_config_files(claude_home):
    """{path in the bundle: source path} for every config file carried along."""
    found = {}
    for rel_src, rel_dest in CONFIG_FILES:
        src = os.path.join(claude_home, rel_src)
        if os.path.isfile(src):
            found[rel_dest] = src
    for rel_src, rel_dest in CONFIG_DIRS + _skill_dirs(claude_home):
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


# ------------------------------------------------------------------ the build command

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
    """(may we overwrite?, reason). Only an empty folder or a bundle this script built."""
    if not os.path.exists(dest):
        return True, "the destination does not exist yet"
    if not os.path.isdir(dest):
        return False, "the destination exists but is not a folder"
    entries = sorted(os.listdir(dest))
    if not entries:
        return True, "the destination is empty"
    manifest = os.path.join(dest, "manifest.json")
    if os.path.isfile(manifest):
        try:
            with open(manifest, encoding="utf-8") as f:
                if "exported_at" in json.load(f):
                    return True, "the destination is a bundle built by this script"
        except (OSError, ValueError):
            pass
    return False, "the destination holds foreign data: " + ", ".join(entries[:3])


def resolve_repos(args):
    """{name in the bundle: absolute path on the source machine} for EVERY repo to clone.

    `local-repos.json` wins (many repos); the file being absent/missing → fall back to the old
    behaviour: exactly 1 repo taken from `--repo`, named `tdqworkflow-repo`.
    """
    path = args.local_repos
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        repos = {name: os.path.abspath(os.path.expanduser(p)) for name, p in data.items()}
        log(f"read {len(repos)} repo(s) from {path}: {', '.join(sorted(repos))}")
        return repos
    repo = os.path.abspath(os.path.expanduser(args.repo))
    log(f"no local-repos.json ({path}) — using 1 repo via --repo: {repo}", level="debug")
    return {REPO_DIR_NAME: repo}


def clone_repo(name, repo, dest):
    target = os.path.join(dest, name)
    dirty = _git_out(repo, "status", "--porcelain")
    if dirty:
        log(f"the source of repo {name} still has {len(dirty.splitlines())} uncommitted file(s) — "
            "the clone takes only what is committed", level="info")
    subprocess.run(["git", "clone", "--quiet", repo, target], check=True, timeout=600)
    log(f"clone {name} → {target}")
    return target


def copy_repo_memory(name, repo, dest):
    """The `.remember/` of a repo is untracked, so a clone leaves it behind — copied separately."""
    src = os.path.join(repo, ".remember")
    if not os.path.isdir(src):
        return 0
    target = os.path.join(dest, name, ".remember")
    count = 0
    for dirpath, dirnames, names in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name_ in sorted(names):
            if name_ in SKIP_NAMES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, name_), src)
            out = os.path.join(target, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(os.path.join(dirpath, name_), out)
            count += 1
    log(f"copied {count} .remember file(s) of {name} (dropping tmp/ and logs/)")
    return count


def copy_config(claude_home, dest):
    files = collect_config_files(claude_home)
    for rel_dest, src in files.items():
        out = os.path.join(dest, rel_dest)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy2(src, out)
    log(f"copied {len(files)} config file(s) from {claude_home}")
    return files


def rewrite_marketplace_path(dest):
    """Point the `tdq-local` marketplace at the repo INSIDE the bundle, else the plugins never load."""
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


def copy_launch_agents(repos, launch_agents_dir, dest):
    """Copy the LaunchAgent plist matching a local repo name — FOR REFERENCE only, never restored.

    Naming rule: `com.<repo name minus the "-repo" suffix>.gateway.plist`. `tdqworkflow-repo`
    has no LaunchAgent of its own, so it is skipped. No matching file → skipped silently,
    not an error (that repo's LaunchAgent may simply not exist on this machine).
    """
    copied = []
    out_dir = os.path.join(dest, "config", "launch-agents")
    for name in sorted(repos):
        if name == REPO_DIR_NAME:
            continue
        base = name[:-len("-repo")] if name.endswith("-repo") else name
        fname = f"com.{base}.gateway.plist"
        src = os.path.join(launch_agents_dir, fname)
        if not os.path.isfile(src):
            continue
        os.makedirs(out_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(out_dir, fname))
        copied.append(fname)
    log(f"copied {len(copied)} LaunchAgent plist(s) for reference: {', '.join(copied) or 'none'}")
    return copied


def write_mcp_servers(claude_json, dest):
    servers = read_mcp_servers(claude_json)
    out = os.path.join(dest, "config", "mcp-servers.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(servers, f, ensure_ascii=False, indent=2)
    log(f"exported {len(servers)} MCP server(s) → config/mcp-servers.json")
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
    log(f"probed the version of {len(found)} CLI(s)")
    return found


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_manifest(dest, repos, claude_home, files, servers):
    """The key frame taken from MANIFEST.template.json so template and code never drift apart.

    `repos`: {name: source path} — 1 or many. `repo_commit`/`plugin_version` keep their old
    meaning (the SHA + version of `tdqworkflow-repo`) so backward compatibility holds; the new
    `repos` key lists EVERY repo in full with its own commit.
    """
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
    main_repo = repos.get(REPO_DIR_NAME, "")
    manifest["plugin_version"] = plugin_version(main_repo)
    manifest["repo_commit"] = _git_out(main_repo, "rev-parse", "HEAD")
    manifest["repos"] = {
        name: {"source": path, "commit": _git_out(path, "rev-parse", "HEAD")}
        for name, path in sorted(repos.items())
    }
    manifest["exported_at"] = _now()
    manifest["source_files"] = {
        rel: {"source": src, "sha256": sha256_of(src)} for rel, src in sorted(files.items())
    }
    with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    log(f"ghi manifest.json ({len(manifest['repos'])} repo, "
        f"{len(manifest['source_files'])} source file(s) with sha256)")
    return manifest


def write_readme(dest, manifest):
    template = os.path.join(TEMPLATE_DIR, "README.template.md")
    with open(template, encoding="utf-8") as f:
        text = f.read()
    lines = ["| Repo local dependency | Path nguồn | Commit |", "|---|---|---|"]  # i18n-allow
    for name, entry in sorted(manifest.get("repos", {}).items()):
        lines.append(f"| `{name}` | `{entry.get('source', '?')}` | "
                     f"`{(entry.get('commit') or '?')[:8]}` |")
    lines += ["", "| Marketplace | Nguồn |", "|---|---|"]  # i18n-allow
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
    """Compress to a temp file before overwriting — a crash midway leaves the old zip intact."""
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
    log(f"compressed {final} ({os.path.getsize(final) / 1048576:.1f} MB)")
    return final


def cmd_build(args):
    dest = os.path.abspath(os.path.expanduser(args.dest))
    home = os.path.abspath(os.path.expanduser(args.claude_home))
    claude_json = os.path.abspath(os.path.expanduser(
        args.claude_json or os.path.join(os.path.dirname(home), ".claude.json")))
    log(f"build → {dest}")
    ok, why = dest_is_writable(dest)
    if not ok:
        log(f"refusing to overwrite: {why}", level="info")
        return 2
    log(f"destination is valid ({why})", level="debug")

    secrets = harvest_secrets(os.path.join(home, "settings.json"))
    log(f"found {len(secrets)} secret variable(s) needing a placeholder: "
        f"{', '.join(sorted(secrets)) or 'none'}")

    repos = resolve_repos(args)

    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for name, repo_path in sorted(repos.items()):
        clone_repo(name, repo_path, dest)
        copy_repo_memory(name, repo_path, dest)
    files = copy_config(home, dest)
    servers = write_mcp_servers(claude_json, dest)
    rewrite_marketplace_path(dest)
    copy_launch_agents(repos, os.path.abspath(os.path.expanduser(args.launch_agents_dir)), dest)
    manifest = write_manifest(dest, repos, home, files, servers)
    write_readme(dest, manifest)

    changed = redact_bundle(dest, secrets)
    log(f"replaced the placeholder in {len(changed)} file(s)")
    hits = scan_secrets(dest, list(secrets.values()) + list(args.extra_secret or []))
    if hits:
        shutil.rmtree(dest, ignore_errors=True)
        log(f"SECRET STILL PRESENT in {len(hits)} file(s) → the bundle {dest} was deleted. "
            f"First file: {os.path.relpath(hits[0], dest)}")
        return 3
    log("secret scan: clean")

    if args.zip:
        make_zip(dest)
    total = sum(len(names) for _, _, names in os.walk(dest))
    log(f"xong · {total} file · {len(repos)} repo · commit {manifest['repo_commit'][:8]} · "
        f"plugin {manifest['plugin_version']}")
    return 0


# ------------------------------------------------------------------ the check command

def cmd_check(args):
    dest = os.path.abspath(os.path.expanduser(args.dest))
    manifest_path = os.path.join(dest, "manifest.json")
    if not os.path.isfile(manifest_path):
        log(f"no manifest.json found in {dest} — this is not a bundle")
        return 2
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        log(f"manifest.json cannot be read ({err}) — broken bundle, rebuild it with build")
        return 2
    log(f"checking the bundle built at {manifest.get('exported_at', '?')}")

    drift = []
    for rel, entry in sorted(manifest.get("source_files", {}).items()):
        src = entry.get("source", "")
        if not os.path.isfile(src):
            drift.append((rel, "missing at the source"))
        elif sha256_of(src) != entry.get("sha256"):
            drift.append((rel, "content changed"))

    # `repos`: a new bundle (N repos). An old manifest (before N-repo support) has no such key
    # — fall back to exactly 1 repo via `--repo`, using the old `repo_commit` for compatibility.
    repos = dict(manifest.get("repos") or {})
    if REPO_DIR_NAME not in repos:
        repos[REPO_DIR_NAME] = {"source": os.path.abspath(os.path.expanduser(args.repo)),
                                "commit": manifest.get("repo_commit", "")}
    for name, entry in sorted(repos.items()):
        src = entry.get("source", "")
        # `tdqworkflow-repo` against the old `repo_commit` key (backward compatible with a bundle
        # from before multi-repo); any other repo against the commit recorded in `repos`.
        old = manifest.get("repo_commit", "") if name == REPO_DIR_NAME else entry.get("commit", "")
        head = _git_out(src, "rev-parse", "HEAD") if src else ""
        if head and old and head != old:
            behind = _git_out(src, "rev-list", "--count", f"{old}..{head}")
            gap = f"(+{behind})" if behind else "(distance not measurable — the old SHA is not in the repo)"
            drift.append((name, f"commit {old[:8]} → {head[:8]} {gap}"))
    main_source = repos.get(REPO_DIR_NAME, {}).get("source", "") \
        or os.path.abspath(os.path.expanduser(args.repo))
    now_version = plugin_version(main_source)
    if now_version and now_version != manifest.get("plugin_version"):
        drift.append((".claude-plugin/plugin.json",
                      f"version {manifest.get('plugin_version')} → {now_version}"))

    if drift:
        print("| Item | Drift |")
        print("|---|---|")
        for rel, why in drift:
            print(f"| {rel} | {why} |")
    print(f"{len(drift)} drift item(s)")
    return 1 if drift else 0


# ------------------------------------------------------------------ CLI

def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="claude_export.py", description="Build and check a Claude Code export bundle")
    subs = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext in (("build", "build the bundle"), ("check", "measure bundle ↔ source drift")):
        sub = subs.add_parser(name, help=helptext)
        sub.add_argument("--dest", required=True, help="the bundle folder")
        sub.add_argument("--repo", default=REPO_ROOT, help="the source TDQWorkflow repo")
        sub.add_argument("--claude-home", default=os.path.expanduser("~/.claude"),
                         help="the Claude Code config folder of the source machine")
        sub.add_argument("--claude-json", default=None,
                         help="the file holding mcpServers (default <parent of claude-home>/.claude.json)")
        sub.add_argument("--quiet", action="store_true", help="turn the log off")
        sub.add_argument("--verbose", action="store_true", help="also log at debug level")
        if name == "build":
            sub.add_argument("--zip", action="store_true", help="compress the bundle into a .zip")
            sub.add_argument("--extra-secret", action="append", default=[],
                             help="extra secret string to scan for; a hit destroys the bundle")
            sub.add_argument("--local-repos",
                             default=os.path.join(TEMPLATE_DIR, "local-repos.json"),
                             help="JSON {name: path} listing EVERY local repo dependency; "
                                  "absent/missing → falls back to 1 repo via --repo")
            sub.add_argument("--launch-agents-dir",
                             default=os.path.expanduser("~/Library/LaunchAgents"),
                             help="folder holding the LaunchAgent .plist files copied for reference")
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    set_log_level(quiet=args.quiet, verbose=args.verbose)
    try:
        return cmd_build(args) if args.cmd == "build" else cmd_check(args)
    except subprocess.CalledProcessError as exc:
        log(f"an external command failed: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
