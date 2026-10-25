#!/usr/bin/env python3
"""build_portable.py — generate the Antigravity layout, rewrite hooks/hooks.json, or publish main.

2026-09-21: this script used to build THREE portable bundles (claude, codex, antigravity) by
copying `skills/`, `hooks/`, `agents/` and `scripts/` into three separate trees — 357 duplicated
files. That model is gone. Claude Code reads the repo via `.claude-plugin/marketplace.json`,
Codex via `.agents/plugins/marketplace.json`, OpenCode via `.opencode/plugins/tdq-workflow.js`;
all three point straight at the shared source instead of a copy.

Actions:

    --sinh-agy    Antigravity requires a plugin directory at a fixed path under `$HOME`, with no
                  way to point elsewhere. Generate that layout IN PLACE on the machine that will
                  run it instead of committing a prebuilt copy with baked home paths.
    --sinh-hook-claude
                  Rewrite the Python command prefix in `hooks/hooks.json` for the target OS.
    --sinh-main   Publish a clean release snapshot from `dev` onto `main` using git plumbing.

Env: TDQ_LOG=0 turns off progress logging (logged to stderr).
Exit: 0 done · 1 build error · 2 bad arguments.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import utf8_io  # noqa: E402,F401 — imported for its side effect: stdout/stderr become UTF-8
from claude_export import plugin_version, sha256_of  # noqa: E402
# The logic that builds the two config files lives in `tdq_checkportable.py`, not here: only
# that file ships with the bundle. Importing it back keeps exactly one copy of the logic.
from tdq_checkportable import sinh_mcp  # noqa: E402
import tdq_ten_lenh  # noqa: E402 — owns the interpreter name

EXIT_LOI = 1

# Junk must never leak into the generated bundle. `docs/tdq` heads the list because it holds the
# state, brief, spec and plan of THIS source repo — shipping that elsewhere leaks internal data.
EXCLUDE_DIRS = frozenset({
    ".git", "docs", "graphify-out", "__pycache__", ".pytest_cache", ".venv",
    "tests", "node_modules", ".remember", "ClaudeExport", "claude-export",
    "portable", "portable_claude", "portable_codex",
})
EXCLUDE_FILES = frozenset({
    ".DS_Store", "state.json", ".tdq-turn.jsonl",
    # The generator itself does not ship with what it generates: it only means something in the
    # source repo, and it quotes the plugin variable verbatim, so a rewrite would break its constant.
    "build_portable.py",
    # Same for the compliance measurement suite: it only runs in the source repo, and it SETS the
    # `CLAUDE_PLUGIN_ROOT` variable for the child processes of a measured session — a rewrite would
    # change the very constant it needs kept intact.
    "tdq_eval.py",
})

RELEASE_EXCLUDE_DIRS = frozenset({
    ".git", "docs", "tests", "evals", "graphify-out", ".taskmaster",
    "tools_kiem", ".github", "portable", "portable_claude", "portable_codex",
    "__pycache__", ".pytest_cache", ".venv", "node_modules", ".remember",
    "ClaudeExport",
})
RELEASE_EXCLUDE_FILES = frozenset({
    ".DS_Store", "CHANGELOG-archive.md", "pyrightconfig.json",
    "state.json", ".tdq-turn.jsonl",
})
RELEASE_EXCLUDE_SCRIPTS = frozenset({
    "canvas_a4_ch4_ch7.py", "canvas_a4_rebuild.py", "canvas_draw.py",
    "canvas_layout_apply.py", "canvas_move_block.py", "check_canvas_layout.py",
    "doc_dup.py", "doc_index.py", "i18n_check.py", "luat_phan_loai.py",
    "skill_router.py", "tdq_eval.py", "tdq_knowledge.py",
})

# The skill that only means something on the TARGET machine (`tdq-checkportable`) lives here and
# not in `skills/`: putting it there would make every session pay for one more description in its
# context budget, for a skill this repo never runs. The agy layout still ships it.
PORTABLE_SRC = "portable_src"

MANIFEST_NAME = "manifest.json"
# 2026-09-27: 3.8 -> 3.11. Python 3.11 is the first standard library release with `tomllib`
# and the lowest version tested in the CI matrix.
PYTHON_MIN = "3.11"
EXTERNAL_COMMANDS = ("git", "graphify")
MCP_SERVERS = ("tavily-primary", "tavily-backup")

BIEN_CU = "CLAUDE_PLUGIN_ROOT"
BIEN_MOI = "CLAUDE_PROJECT_DIR"


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """Log progress to stderr with a timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------ variable rewrite

def doi_bien_plugin_root(text, thay_bang=None):
    """`${CLAUDE_PLUGIN_ROOT}` and `$CLAUDE_PLUGIN_ROOT` → `${CLAUDE_PROJECT_DIR}`.

    `thay_bang` replaces the variable with a fixed path instead. The agy layout needs that: agy
    expands no plugin variable at all, so every hook command must carry the absolute install root
    — a bare variable there leaves the script call silently finding no file.

    Returns `(new text, number of replacements)`. The count is worth more than the result: grepping
    the generated bundle for 0 matches only proves "gone from the files ALREADY COPIED", while
    comparing the count with the number counted in the source catches a file that should have been
    copied and was not — a hook broken by an empty variable fails silently on the other machine.
    """
    dang_ngoac = "${" + BIEN_CU + "}"
    dang_tran = "$" + BIEN_CU
    moi = thay_bang or ("${" + BIEN_MOI + "}")
    so_lan = text.count(dang_ngoac)
    text = text.replace(dang_ngoac, moi)
    # Once the braced form is replaced, whatever still carries a bare `$` is the real bare form.
    so_lan += text.count(dang_tran)
    text = text.replace(dang_tran, moi)
    return text, so_lan


def dem_bien_trong_cay(goc):
    """Count every use of the plugin variable in a folder tree — the reference number for QC."""
    tong = 0
    for thu_muc, _, files in os.walk(goc):
        for ten in files:
            noi_dung = _doc_text(os.path.join(thu_muc, ten))
            if noi_dung is not None:
                tong += noi_dung.count(BIEN_CU)
    return tong


# --------------------------------------------------------------------- copy

def _bo_qua_thu_muc(ten):
    return ten in EXCLUDE_DIRS


def _bo_qua_file(ten):
    return ten in EXCLUDE_FILES or ten.endswith((".pyc", ".pyo"))


def _doc_text(path):
    """Read a file as text; return None if it is binary (left untouched so it cannot be broken)."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None


def copy_loc(nguon, dich, doi_bien=False, thay_bang=None):
    """Copy a folder tree through the filter, keeping the executable bit. Returns the rewrite count.

    `doi_bien=True` rewrites the plugin-root variable in text files as they are written (the agy
    layout needs absolute paths); binary files are copied as-is. Keeping the `x` bit is
    mandatory — without it the hook cannot run.
    """
    so_lan_doi = 0
    for thu_muc, thu_muc_con, files in os.walk(nguon):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        tuong_doi = os.path.relpath(thu_muc, nguon)
        dich_hien_tai = dich if tuong_doi == "." else os.path.join(dich, tuong_doi)
        os.makedirs(dich_hien_tai, exist_ok=True)
        for ten in files:
            if _bo_qua_file(ten):
                continue
            src = os.path.join(thu_muc, ten)
            dst = os.path.join(dich_hien_tai, ten)
            noi_dung = _doc_text(src) if doi_bien else None
            if noi_dung is None:
                shutil.copy2(src, dst)
            else:
                noi_dung, lan = doi_bien_plugin_root(noi_dung, thay_bang)
                so_lan_doi += lan
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(noi_dung)
                shutil.copystat(src, dst)
    return so_lan_doi


def _ghi_json(duong, du_lieu):
    """Write JSON byte-for-byte the way `tdq_checkportable._ghi_json_co_backup` writes it.

    One newline off here is a different sha256: `setup` regenerates the file and the very next
    `check` reports DRIFT, even though the content means exactly the same thing.
    """
    with open(duong, "w", encoding="utf-8") as f:
        f.write(json.dumps(du_lieu, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


# ------------------------------------------------ skills carried by the agy layout

# Reading order, not alphabetical order: it is the order the pipeline uses them in.
THU_TU_SKILL = (
    "tdq-conventions",
    "tdq-setup",  # read before intake: it settles the search layer every later phase uses
    "tdq-intake",
    "tdq-spec",
    "tdq-plan",
    "tdq-build",
    # 2026-09-17: read right after build, because that is when it is used — it hunts
    # over-engineering in what build just produced, and reading it earlier would have nothing
    # to look at.
    "tdq-lean",
    "tdq-checkportable",  # source in PORTABLE_SRC, not in `skills/`
    "tdq-status",
    "tdq-check-status",
)

# ---------------------------------------------------- antigravity (agy) bundle

TEN_BAN_AGY = "antigravity_portable"

# 2026-09-03: the older "spray the config into 6 guessed paths" design is gone. It was written
# when no source pinned agy's real layout; a READ-ONLY survey of a live `agy 1.1.11` install
# settled the question — none of those 6 candidate paths existed on disk. The real layout is a
# plain plugin directory:
#     ~/.gemini/config/plugins/<name>/{plugin.json, skills/, hooks.json, mcp_config.json}
# switched on by the key `plugins.<name>.enabled` in ~/.gemini/config/config.json, with extra
# skill roots registered as `entries[].path` in ~/.gemini/config/skills.json. So this bundle IS
# that plugin directory: the install is one copy plus two small config keys.
TEN_PLUGIN_AGY = "tdq-workflow"
GOC_AGY = f"~/.gemini/config/plugins/{TEN_PLUGIN_AGY}"

# The two user-owned config files the install has to touch. Neither is ever written by this
# script nor shipped in the bundle — the README names the one key to add, because both files
# hold unrelated user settings an overwrite would destroy.
AGY_CONFIG_JSON = "~/.gemini/config/config.json"
AGY_SKILLS_JSON = "~/.gemini/config/skills.json"

HOOK_AGY = (
    ("PreToolUse", "agy_pretooluse_gate.py"),
    # 2026-10-02: the read gate goes into the agy bundle too, but it only fires when the payload
    # carries `tool_input.file_path`. agy's own PreToolUse gate speaks `run_command` and has no
    # notion of reading a file, so under agy this entry is a no-op until that host grows a read
    # tool with the same field. Shipping it anyway keeps ONE hook table instead of two that drift.
    ("PreToolUse", "read_gate.py"),
    ("Stop", "agy_stop_gate.py"),
)

# The bundle used to ship a `settings.json` mirroring the branch-name ban into agy's permissions
# engine. Dropped 2026-09-03: the real `~/.gemini/antigravity-cli/settings.json` holds the user's
# `model`/`colorScheme`/`trustedWorkspaces` and has no `permissions` block at all, so the copy
# step destroyed user settings while adding no guard. The hook is the guard.

README_AGY = """# TDQ Workflow — plugin bundle for Antigravity CLI (agy)

This directory IS an agy plugin: `plugin.json` at the root, `skills/` beside it, plus
`hooks.json` and `mcp_config.json`. The layout was read off a live `agy 1.1.11` install on
2026-09-03. Installing is one copy plus two config keys.

## Install — this exact order

1. **Copy this whole directory** to the plugin root, keeping the directory name:
   ```
   {goc_agy}/
   ```

2. **Enable the plugin** in `{config_json}` — add the key, keep everything else that file
   already holds:
   ```json
   {{ "plugins": {{ "{ten_plugin}": {{ "enabled": true }} }} }}
   ```

3. **Register the skill root** in `{skills_json}`, appending to the existing `entries` array:
   ```json
   {{ "entries": [ {{ "path": "{goc_agy}/skills" }} ] }}
   ```

4. **Set the environment variables** the MCP servers need. This bundle only ever records
   variable NAMES, never a key value — export `TAVILY_API_KEY` (and the backup server's
   variable) yourself before using MCP.

5. **Restart agy**, then self-check with agy's own commands:
   - `agy plugin list` — is `{ten_plugin}` listed and enabled?
   - `/skills` — do the `{danh_sach_ten}` skills show up?
   - `/mcp` — are `tavily-primary`/`tavily-backup` listed as configured servers?

6. **Smoke-test the hard deny.** Ask agy to run one of the banned cases (e.g.
   `git checkout -b antigravity-test`, or writing straight to `docs/tdq/state.json` through the
   shell) and confirm it is refused. Not refused → the hook did not load; re-check steps 1–2.

## The hook `command` paths are absolute, and baked at build time

agy requires an ABSOLUTE `command`; a `~` inside quotes is not expanded and the hook dies with
exit 127. `hooks.json` therefore carries a real expanded path — the home folder of the machine
that BUILT the bundle. Copying a prebuilt bundle to another user's machine leaves those paths
pointing at the wrong home. Rebuild it locally instead — run the repo's `build_portable.py`
from a clone of TDQ-Workflow, then copy the freshly built directory over.
`python3 scripts/tdq_checkportable.py check --root <this directory>` prints a NOTE when the
baked home does not match the current one.

## Bundle này gắn với MÁY DỰNG — Windows và Linux đọc kỹ mục này <!-- i18n-allow -->

- **Đừng copy bundle dựng sẵn từ máy người khác.** Đường dẫn trong `hooks.json` là thư mục nhà <!-- i18n-allow -->
  của máy dựng, không phải của bạn. Clone repo TDQ-Workflow rồi chạy <!-- i18n-allow -->
  `python3 scripts/build_portable.py` ngay trên máy bạn, sau đó mới copy thư mục vừa dựng. <!-- i18n-allow -->
- **Tên lệnh Python khác nhau giữa các hệ.** Bản dựng chọn `python3` trên macOS/Linux và <!-- i18n-allow -->
  `py -3` trên Windows — Windows không có `python3` trên PATH (cái tên đó chỉ là stub của <!-- i18n-allow -->
  Microsoft Store mở cửa hàng ứng dụng). Dựng lại tại máy đích là cách duy nhất để `command` <!-- i18n-allow -->
  mang đúng tên lệnh của máy đó. <!-- i18n-allow -->
- **Kiểm lại sau khi copy:** `python3 scripts/tdq_checkportable.py check --root <thư mục này>` <!-- i18n-allow -->
  in cảnh báo khi bundle được dựng dưới thư mục nhà của người khác. <!-- i18n-allow -->

## What this bundle cannot do for you

1. **Restart agy** — step 5. Skip it and the files just sit there, unloaded.
2. **Set the MCP environment variables** — step 4.
3. **Guarantee the layout on a different agy version.** It was verified against `agy 1.1.11`
   only; step 5's self-check is how you find out on YOUR machine.

## Secret keys

`mcp_config.json` records only the NAMES of environment variables, never a key value.
"""


def _sua_duong_dan_tuong_doi_agy(goc, goc_cai=None):
    """Second-pass rewrite, agy bundle only, `.md` text under `skills/` — a bare `scripts/`/
    `hooks/` mention NOT already prefixed by `GOC_AGY` becomes absolute too.

    `doi_bien_plugin_root` only rewrites `${CLAUDE_PLUGIN_ROOT}`. Several skill files were
    written assuming a project-relative cwd (true for Codex, whose bundle sets `moi="."`) —
    false here, since agy installs its core at one fixed absolute path outside any project.
    Scoped to `.md` only: touching `.py` source would corrupt real import paths.
    """
    tien_to = (goc_cai or GOC_AGY) + "/"
    mau = re.compile(r"(?<!" + re.escape(tien_to) + r")\b(scripts/|hooks/)")
    so_lan = 0
    for thu_muc, thu_muc_con, files in os.walk(goc):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        for ten in files:
            if not ten.endswith(".md"):
                continue
            duong = os.path.join(thu_muc, ten)
            noi_dung = _doc_text(duong)
            if noi_dung is None:
                continue
            # A replacement FUNCTION, not a string: `tien_to` can now be an absolute Windows
            # path, and `re` reads a backslash in a replacement string as an escape — a path
            # under `C:\Users` died with "bad escape". A function is handed the match and
            # interprets nothing.
            moi, n = mau.subn(lambda k: tien_to + k.group(1), noi_dung)
            if n:
                so_lan += n
                with open(duong, "w", encoding="utf-8") as f:
                    f.write(moi)
    return so_lan


def tien_to_python(nen_tang=None):
    """The command name that runs Python 3 on `nen_tang` (default: the running machine).

    Kept as a thin alias: the answer itself moved to `tdq_ten_lenh.ten_lenh_python` so a hook
    can ask for it without importing this bundle builder. Five call sites here and one in the
    hook layer now read the same constant instead of two copies drifting apart.
    """
    return tdq_ten_lenh.ten_lenh_python(nen_tang)


TIEN_TO_PYTHON_BIET = ("py -3", "python3", "python")


def sinh_hook_claude(duong, nen_tang=None):
    """Rewrite the Python command prefix in `hooks/hooks.json` for the target OS.

    Unlike generated hook bundles, `hooks/hooks.json` is a hand-maintained source file committed
    and shared across machines. It defaults to `python3` for macOS and Linux; Windows users run
    this command once to switch the prefix while keeping `${CLAUDE_PLUGIN_ROOT}` and event order.

    Returns True when the file changed, False when already up to date.
    """
    tien_to = tien_to_python(nen_tang)
    with open(duong, encoding="utf-8") as f:
        goc_van_ban = f.read()
    du_lieu = json.loads(goc_van_ban)

    def _doi(nut):
        if isinstance(nut, dict):
            lenh = nut.get("command")
            if isinstance(lenh, str):
                for cu in TIEN_TO_PYTHON_BIET:
                    if lenh.startswith(cu + " "):
                        nut["command"] = tien_to + lenh[len(cu):]
                        break
            for gia_tri in nut.values():
                _doi(gia_tri)
        elif isinstance(nut, list):
            for gia_tri in nut:
                _doi(gia_tri)

    _doi(du_lieu)
    moi = json.dumps(du_lieu, ensure_ascii=False, indent=2) + "\n"
    if moi == goc_van_ban:
        return False
    with open(duong, "w", encoding="utf-8") as f:
        f.write(moi)
    return True


def goc_agy_tuyet_doi(goc_cai=None):
    """`GOC_AGY` with `~` expanded — agy needs an ABSOLUTE `command`.

    A `~` inside the double quotes of a `command` string is NOT expanded by the shell, so the
    old form died with exit 127 (source N5). Expansion happens at BUILD time, which means a
    bundle built on one machine carries that machine's `$HOME`: rebuild locally
    (`python3 scripts/build_portable.py`) rather than copying a prebuilt bundle between users.
    `tdq_checkportable.py check` prints a NOTE when the baked home is not the current one.
    """
    return os.path.expanduser(goc_cai or GOC_AGY)


def _sinh_hooks_agy(duong, nen_tang=None, goc_cai=None):
    """`hooks.json` at the plugin root — commands are absolute paths into the plugin's own tree.

    Wire shape follows the agent-hooks contract documented for agy (source N5, 2026-09-03):
    an event map whose entries carry `hooks[].type = "command"`.
    """
    su_kien = {}
    goc = goc_agy_tuyet_doi(goc_cai)
    for ten_event, ten_file in HOOK_AGY:
        su_kien.setdefault(ten_event, []).append({"hooks": [{
            "type": "command",
            "command": f'{tien_to_python(nen_tang)} "{goc}/hooks/scripts/{ten_file}"',
        }]})
    _ghi_json(duong, {
        "description": "TDQ workflow for Antigravity CLI (agy) — auto-generated, never edited "
                        "by hand. Lives at the plugin root; agy reads it once the plugin is "
                        "enabled in ~/.gemini/config/config.json — see README.md.",
        "hooks": su_kien,
    })


def _sinh_plugin_json_agy(duong, version):
    """`plugin.json` at the plugin root — the one file that makes agy treat this directory as a
    plugin. A live `agy 1.1.11` install ships plugins whose manifest is as small as
    `{"name": "firebase"}`, so only `name` is load-bearing; the rest is for humans."""
    _ghi_json(duong, {
        "name": TEN_PLUGIN_AGY,
        "version": version or "0",
        "description": "Spec-driven TDQ workflow: intake → spec → plan → build → QC → report.",
    })


def _sinh_mcp_agy(duong):
    _ghi_json(duong, sinh_mcp())


def sinh_ban_antigravity(repo, dest, version="", ten_thu_muc=None, goc_cai=None):
    """Build `<dest>/antigravity_portable/` — bundle for Antigravity CLI (agy), user-level/global.

    agy reads plugins only from its GLOBAL config paths under `$HOME` — see `README_AGY` — so
    unlike every other host it cannot read this repo in place.
    The bundle's own core (`skills/`, `scripts/`, `hooks/scripts/`) sits at one FIXED canonical
    path (`GOC_AGY`) that every generated config file's `command`/path field points at.
    """
    goc = os.path.join(dest, ten_thu_muc or TEN_BAN_AGY)
    if os.path.isdir(goc):
        shutil.rmtree(goc)
    os.makedirs(goc, exist_ok=True)

    # No `CLAUDE_*` variable exists outside Claude Code, and the install path is fixed and
    # absolute rather than relative to a project cwd — every `${CLAUDE_PLUGIN_ROOT}` becomes
    # that fixed absolute path directly.
    moi = goc_cai or GOC_AGY
    copy_loc(os.path.join(repo, "scripts"), os.path.join(goc, "scripts"), True, moi)

    dong_danh_sach = []
    for ten_skill in THU_TU_SKILL:
        thu_muc_skill = os.path.join(repo, "skills", ten_skill)
        if not os.path.isdir(thu_muc_skill):
            thu_muc_skill = os.path.join(repo, PORTABLE_SRC, "skills", ten_skill)
        nguon = os.path.join(thu_muc_skill, "SKILL.md")
        if not os.path.isfile(nguon):
            continue
        copy_loc(thu_muc_skill, os.path.join(goc, "skills", ten_skill), True, moi)
        dong_danh_sach.append(ten_skill)
    _sua_duong_dan_tuong_doi_agy(os.path.join(goc, "skills"), goc_cai)

    os.makedirs(os.path.join(goc, "hooks", "scripts"), exist_ok=True)
    # The copy list is DERIVED from HOOK_AGY, never written twice: the bundle shipped a
    # `hooks.json` entry for `read_gate.py` while the copy list was a hardcoded pair, so every
    # PreToolUse under agy ran a file that was not there. `_common.py` rides along because the
    # shared gates import it (the rest of its imports resolve: `scripts/` is copied above).
    for ten_file in sorted({t for _e, t in HOOK_AGY} | {"_common.py"}):
        src = os.path.join(repo, "hooks", "scripts", ten_file)
        dst = os.path.join(goc, "hooks", "scripts", ten_file)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)

    _sinh_plugin_json_agy(os.path.join(goc, "plugin.json"), version)
    _sinh_hooks_agy(os.path.join(goc, "hooks.json"), goc_cai=goc_cai)
    _sinh_mcp_agy(os.path.join(goc, "mcp_config.json"))

    with open(os.path.join(goc, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_AGY.format(
            goc_agy=goc_cai or GOC_AGY,
            ten_plugin=TEN_PLUGIN_AGY,
            config_json=AGY_CONFIG_JSON,
            skills_json=AGY_SKILLS_JSON,
            danh_sach_ten=", ".join(dong_danh_sach),
        ))

    con_lai = dem_bien_trong_cay(goc)
    if con_lai:
        raise RuntimeError(f"the antigravity bundle still has {con_lai} use(s) of {BIEN_CU}")
    log(f"{TEN_BAN_AGY}: {len(dong_danh_sach)} skill(s), {len(HOOK_AGY)} hook(s), "
        f"{len(MCP_SERVERS)} MCP server(s), 0 plugin variable left")

    ghi_manifest(goc, version)
    return goc


# ------------------------------------------------------------------ manifest

def sinh_manifest(goc, version=""):
    """Scan the folder tree → a manifest dict with all 5 blocks.

    `manifest.json` leaves itself out of the list: it is written AFTER the scan, so listing itself
    would record a sha256 that never matches its own final content.
    """
    files = {}
    for thu_muc, thu_muc_con, ten_files in os.walk(goc):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        for ten in ten_files:
            if _bo_qua_file(ten):
                continue
            duong_day_du = os.path.join(thu_muc, ten)
            tuong_doi = os.path.relpath(duong_day_du, goc).replace(os.sep, "/")
            if tuong_doi == MANIFEST_NAME:
                continue
            files[tuong_doi] = sha256_of(duong_day_du)
    return {
        "files": files,
        "version": version,
        "python_min": PYTHON_MIN,
        "external_commands": list(EXTERNAL_COMMANDS),
        "mcp_servers": list(MCP_SERVERS),
    }


def ghi_manifest(goc, version=""):
    man = sinh_manifest(goc, version)
    with open(os.path.join(goc, MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2, sort_keys=True)
    log(f"manifest: {len(man['files'])} file(s) in {os.path.basename(goc)}")
    return man


# -------------------------------------------------------------------------- CLI

def la_ban_cua_minh(goc):
    """Return True when `goc` is missing, empty, or an existing tdq-workflow installation."""
    if not os.path.isdir(goc):
        return True
    if not os.listdir(goc):
        return True
    dau = os.path.join(goc, "plugin.json")
    try:
        with open(dau, encoding="utf-8") as f:
            return json.load(f).get("name") == TEN_PLUGIN_AGY
    except (OSError, ValueError):
        return False


def sinh_agy_tai_cho(repo, dich, version=""):
    """Generate the Antigravity layout directly into `dich` on the target machine.

    Returns the generated directory path; raises RuntimeError if `dich` belongs to another tool.
    """
    dich = os.path.abspath(os.path.expanduser(dich))
    if not la_ban_cua_minh(dich):
        raise RuntimeError(
            f"{dich} đang có sẵn nội dung không phải của tdq-workflow — "  # i18n-allow
            "chọn đích khác, hoặc tự xoá thư mục đó trước")  # i18n-allow
    cha, ten = os.path.dirname(dich), os.path.basename(dich)
    os.makedirs(cha, exist_ok=True)
    sinh_ban_antigravity(repo, cha, version, ten_thu_muc=ten, goc_cai=dich)
    log(f"agy: đã sinh {dich}")  # i18n-allow
    return dich


def la_duong_dan_release(rel_path):
    """Return True if the repo-relative path belongs on the clean release branch."""
    norm = rel_path.replace("\\", "/").strip("/")
    if not norm:
        return False
    parts = norm.split("/")
    if any(p in RELEASE_EXCLUDE_DIRS for p in parts[:-1]):
        return False
    if parts[-1] in RELEASE_EXCLUDE_FILES:
        return False
    if parts[0] == "scripts":
        if len(parts) > 2 and parts[1] == "samples":
            return False
        if len(parts) == 2 and parts[1] in RELEASE_EXCLUDE_SCRIPTS:
            return False
    return True


def tinh_bao_dong_import(scripts_dir, diem_vao=None):
    """Tính bao đóng import (transitive import closure) của các script runtime trong `scripts/`.

    Nếu `diem_vao` được chỉ định (tập hợp tên module không kèm đuôi .py), bắt đầu từ các điểm vào
    đó và lần theo tất cả import nội bộ trong `scripts/`.
    Nếu `diem_vao` là None, lấy tất cả module trong `scripts/` thoả mãn `la_duong_dan_release`.
    Trả về tập hợp tên các module (không đuôi .py) thuộc bao đóng.
    """
    import ast

    all_py = {f[:-3] for f in os.listdir(scripts_dir) if f.endswith(".py")}
    if diem_vao is None:
        tap_xet = {m for m in all_py if la_duong_dan_release(f"scripts/{m}.py")}
    else:
        tap_xet = set(diem_vao)

    bao_dong = set(tap_xet)
    hang_doi = list(tap_xet)

    while hang_doi:
        mod = hang_doi.pop()
        duong = os.path.join(scripts_dir, f"{mod}.py")
        if not os.path.isfile(duong):
            continue
        try:
            with open(duong, encoding="utf-8") as f:
                cay = ast.parse(f.read(), duong)
        except Exception:
            continue

        for nut in ast.walk(cay):
            targets = []
            if isinstance(nut, ast.Import):
                targets = [a.name.split(".")[0] for a in nut.names]
            elif isinstance(nut, ast.ImportFrom) and nut.module:
                targets = [nut.module.split(".")[0]]
            for t in targets:
                if t in all_py and t not in bao_dong:
                    bao_dong.add(t)
                    hang_doi.append(t)

    return bao_dong


def loc_muc_ls_tree(raw_bytes):
    """Filter NUL-delimited `git ls-tree -r -z` output, keeping only release paths."""
    kept = []
    for entry in raw_bytes.split(b"\0"):
        if not entry or b"\t" not in entry:
            continue
        rel_path = entry.split(b"\t", 1)[1].decode("utf-8")
        if la_duong_dan_release(rel_path):
            kept.append(entry)
    return kept


def _git_text(repo, *args, check=True):
    """Run git in text mode and return stripped stdout."""
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, encoding="utf-8", text=True, check=check, timeout=60,
    )
    return proc.stdout.strip()


def _tao_tree_release(repo, kept_entries):
    """Write filtered ls-tree entries into a temporary git index and return tree SHA."""
    with tempfile.TemporaryDirectory(prefix="tdq-release-idx-") as tmp_dir:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tmp_dir, "index"))
        payload = b"\0".join(kept_entries) + (b"\0" if kept_entries else b"")
        subprocess.run(
            ["git", "-C", repo, "update-index", "-z", "--index-info"],
            input=payload, capture_output=True, check=True, env=env, timeout=60,
        )
        proc = subprocess.run(
            ["git", "-C", repo, "write-tree"],
            capture_output=True, encoding="utf-8", text=True, check=True, env=env, timeout=60,
        )
        return proc.stdout.strip()


def sinh_nhanh_main(repo, nguon="dev", nhanh_dich="main", dry_run=False):
    """Build or update the clean release branch from `nguon` without touching the working tree."""
    source_sha = _git_text(repo, "rev-parse", "--verify", f"{nguon}^{{commit}}")
    ls_proc = subprocess.run(
        ["git", "-C", repo, "ls-tree", "-r", "-z", source_sha],
        capture_output=True, check=True, timeout=60,
    )
    all_entries = [e for e in ls_proc.stdout.split(b"\0") if e and b"\t" in e]
    kept_entries = loc_muc_ls_tree(ls_proc.stdout)
    kept = len(kept_entries)
    dropped = len(all_entries) - kept
    if dry_run:
        log(f"build_portable: dry-run {nguon}@{source_sha[:7]} -> {nhanh_dich} · "
            f"kept={kept} dropped={dropped}")
        return {
            "kept": kept, "dropped": dropped, "source_sha": source_sha,
            "tree_sha": None, "commit_sha": None, "changed": True,
        }
    tree_sha = _tao_tree_release(repo, kept_entries)
    ref_name = f"refs/heads/{nhanh_dich}"
    ref_proc = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", "--quiet", ref_name],
        capture_output=True, encoding="utf-8", text=True, timeout=30,
    )
    parent_sha = ref_proc.stdout.strip() if ref_proc.returncode == 0 else ""
    if parent_sha and _git_text(repo, "rev-parse", f"{parent_sha}^{{tree}}") == tree_sha:
        log(f"build_portable: {nhanh_dich} already up to date with {nguon}@{source_sha[:7]} "
            f"(tree={tree_sha[:7]}, kept={kept}, dropped={dropped})")
        return {
            "kept": kept, "dropped": dropped, "source_sha": source_sha,
            "tree_sha": tree_sha, "commit_sha": parent_sha, "changed": False,
        }
    version = plugin_version(repo) or "0.0.0"
    msg = f"release: v{version} (from {nguon}@{source_sha[:7]})"
    cmd = ["commit-tree", tree_sha] + (["-p", parent_sha] if parent_sha else []) + ["-m", msg]
    commit_sha = _git_text(repo, *cmd)
    _git_text(repo, "update-ref", ref_name, commit_sha)
    log(f"build_portable: published {nhanh_dich}@{commit_sha[:7]} from {nguon}@{source_sha[:7]} · "
        f"tree={tree_sha[:7]} · kept={kept} · dropped={dropped}")
    return {
        "kept": kept, "dropped": dropped, "source_sha": source_sha,
        "tree_sha": tree_sha, "commit_sha": commit_sha, "changed": True,
    }


def _xay_parser():
    parser = argparse.ArgumentParser(
        prog="build_portable.py",
        description="Generate what a host cannot read straight from this repo: the Antigravity "
                    "layout, hooks/hooks.json for the target OS, or the clean release branch. "
                    "Pick one action.")
    parser.add_argument("--dest", help="build the Antigravity bundle into DEST/antigravity_portable "
                                       "(a release step; never the repo itself)")
    parser.add_argument("--repo", help="source repo root, defaults to the script location")
    parser.add_argument("--sinh-hook-claude", action="store_true",
                        help="rewrite hooks/hooks.json for the target OS instead of building; "
                             "Windows needs this once, since `python3` is not a command there")
    parser.add_argument("--he-dich", help="target OS for the command name (win32/linux/darwin), "
                                          "defaults to the machine running this")
    parser.add_argument("--sinh-agy", action="store_true",
                        help="generate the Antigravity layout straight into its install "
                             "directory ON THIS MACHINE, instead of building a bundle to commit")
    parser.add_argument("--dich", default=GOC_AGY,
                        help=f"only with --sinh-agy: where to generate (default {GOC_AGY})")
    parser.add_argument("--sinh-main", action="store_true",
                        help="publish a clean release snapshot from --nguon onto --nhanh-dich")
    parser.add_argument("--nguon", default="dev",
                        help="only with --sinh-main: source branch or ref (default: dev)")
    parser.add_argument("--nhanh-dich", default="main",
                        help="only with --sinh-main: target release branch (default: main)")
    parser.add_argument("--dry-run", action="store_true",
                        help="only with --sinh-main: compute kept/dropped counts without updating refs")
    return parser


def _chay_dest(parser, repo, dest):
    if os.path.realpath(dest) == os.path.realpath(repo):
        parser.error("--dest must not be the repo itself: the repo ships no bundle since 0.50.0")
    version = plugin_version(repo)
    log(f"start · repo={repo} · dest={dest} · version={version or '—'}")
    os.makedirs(dest, exist_ok=True)
    try:
        sinh_ban_antigravity(repo, dest, version)
    except (OSError, RuntimeError) as loi:
        log(f"ERROR {loi}")
        return EXIT_LOI
    log("done")
    return 0


def main(argv=None):
    parser = _xay_parser()
    args = parser.parse_args(argv)
    repo = args.repo or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.sinh_hook_claude:
        duong = os.path.join(repo, "hooks", "hooks.json")
        doi = sinh_hook_claude(duong, args.he_dich)
        log(f"{duong}: {'rewritten' if doi else 'already correct'} · "
            f"command = {tien_to_python(args.he_dich)}")
        return 0
    if args.sinh_agy:
        try:
            sinh_agy_tai_cho(repo, args.dich, plugin_version(repo))
        except (OSError, RuntimeError) as loi:
            log(f"ERROR {loi}")
            return EXIT_LOI
        return 0
    if args.sinh_main:
        try:
            sinh_nhanh_main(repo, nguon=args.nguon, nhanh_dich=args.nhanh_dich, dry_run=args.dry_run)
        except (OSError, RuntimeError, subprocess.CalledProcessError) as loi:
            log(f"ERROR {loi}")
            return EXIT_LOI
        return 0
    if not args.dest:
        parser.error("pick an action: --sinh-agy, --sinh-hook-claude, --sinh-main or --dest DEST")
    return _chay_dest(parser, repo, args.dest)


if __name__ == "__main__":
    sys.exit(main())
