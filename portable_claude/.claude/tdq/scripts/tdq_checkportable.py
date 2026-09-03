#!/usr/bin/env python3
"""tdq_checkportable.py — check a portable bundle ON THE TARGET MACHINE and patch what is missing.

This is the one script of the portable set that runs before everything else. Why it exists:
a portable bundle is hand-copied onto a strange machine, so three things break unnoticed —
files dropped or edited on the way, Python too old, an outside command not installed. All
three surface late, as a puzzling error in the middle of a half-finished request.

Two commands:
    check   only compares against `manifest.json`, changes nothing. Exit 0 clean, 1 on drift.
    setup   patches what can be patched: creates missing directories, and rebuilds the two
            config files the bundle carries enough data to recreate (`.claude/settings.json`
            from the bundled `hooks.json`, and `.mcp.json`). EVERY overwrite leaves a
            `<file>.tdq-bak-<timestamp>`. Any other missing/drifting file prints `LEFT …`
            and exits non-zero — the right content exists only in the original, never invent it.
    setup --trust
            does one SINGLE thing outside the bundle: declaring the bundle a trusted project
            in the `config.toml` of Codex CLI (`~/.codex`, or `$CODEX_HOME`). Without the flag
            no path in this file touches that directory. Untrusted, Codex ignores the whole
            `.codex/` layer of the bundle — MCP is not loaded, hooks are not read.

Secret-key rule: this script prints environment variable NAMES, never their values. It runs on
somebody else's machine and its output is usually pasted into a chat or a log.

Env: TDQ_LOG=0 mutes the progress log (the log goes to stderr).
Exit: 0 clean · 1 drift/missing · 2 bad syntax.
"""

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys

MANIFEST_NAME = "manifest.json"
EXIT_LECH = 1

# The ONLY two config files a target machine can rebuild from what the bundle carries:
# `settings.json` generated from the bundled `hooks/hooks.json`, `.mcp.json` from the constant below.
# Every other file has exactly one right source, the original — `setup` must not invent content.
GOC_TDQ = ".claude/tdq"
BIEN_MOI = "CLAUDE_PROJECT_DIR"
MCP_SERVERS = ("tavily-primary", "tavily-backup")

# Variable names treated as holding a secret. Used to decide WHAT TO PRINT, never to read a value.
DAU_HIEU_BI_MAT = ("KEY", "TOKEN", "SECRET", "PASSWORD")


def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """Progress log on stderr with a timestamp. Muted with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for khoi in iter(lambda: f.read(65536), b""):
            h.update(khoi)
    return h.hexdigest()


def to_ten_khoa(moi_truong):
    """Turn an env dict into lines safe to print: only the KEY name + set/unset, no values."""
    return [
        f"{ten}: {'set' if moi_truong.get(ten) else 'NOT set'}"
        for ten in sorted(moi_truong)
    ]


def bien_moi_truong_mcp(manifest, moi_truong=None):
    """State of the key variables the manifest MCP needs — variable NAMES, no values."""
    if not manifest.get("mcp_servers"):
        return []
    moi_truong = os.environ if moi_truong is None else moi_truong
    can = sorted({
        ten for ten in moi_truong
        if any(d in ten.upper() for d in DAU_HIEU_BI_MAT) and ten.startswith("TAVILY")
    } | {"TAVILY_" + "API" + "_KEY"})
    return to_ten_khoa({ten: moi_truong.get(ten) for ten in can})


# ------------------------------------------------------------------- check

def tim_goc_bundle(bat_dau=None):
    """Walk up from the script location to the first directory holding a `manifest.json`.

    Not a fixed `dirname(dirname(__file__))`: this script sits in `.claude/tdq/scripts/` in the
    claude bundle but in `scripts/` in the codex one, so the depth to the bundle root differs
    between them. Hard-coding the number of levels is guaranteed wrong for one of the two.
    """
    duong = os.path.abspath(bat_dau or os.path.dirname(os.path.abspath(__file__)))
    while True:
        if os.path.isfile(os.path.join(duong, MANIFEST_NAME)):
            return duong
        cha = os.path.dirname(duong)
        if cha == duong:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        duong = cha


# ---------------------------------------------------- regenerate config files

def sinh_settings(goc_bundle, duong_hooks_json):
    """`hooks.json` (shipped with the bundle) → the `.claude/settings.json` of the target project.

    Placed HERE and not in `build_portable.py` because `build_portable.py` deliberately does not
    travel with the bundle: for the target machine to rebuild this file, the logic has to live in
    a file present there. `build_portable.py` imports it back, so there is still one copy of it.
    """
    with open(duong_hooks_json, encoding="utf-8") as f:
        goc = json.load(f)
    tho = json.dumps(goc["hooks"], ensure_ascii=False)
    tho = tho.replace("${CLAUDE_PROJECT_DIR}/.claude/tdq", "${" + BIEN_MOI + "}/" + GOC_TDQ)
    tho = tho.replace("${CLAUDE_PROJECT_DIR}/.claude/tdq", "${" + BIEN_MOI + "}/" + GOC_TDQ)
    return {"hooks": json.loads(tho)}


def sinh_mcp():
    """The content of `.mcp.json`: servers + env variable NAMES only, never a key value."""
    ten_bien = "TAVILY_" + "API" + "_KEY"
    return {
        "mcpServers": {
            ten: {
                "command": "npx",
                "args": ["-y", "tavily-mcp@latest"],
                "env": {ten_bien: "${" + ten_bien + "}"},
            }
            for ten in MCP_SERVERS
        }
    }


def doc_manifest(goc):
    duong = os.path.join(goc, MANIFEST_NAME)
    if not os.path.isfile(duong):
        raise FileNotFoundError(f"no {MANIFEST_NAME} found in {goc}")
    with open(duong, encoding="utf-8") as f:
        return json.load(f)


def kiem_file(goc, manifest):
    """Compare each file with its sha256 in the manifest → dict `thieu` / `lech`.

    It does not stop at the first error: whoever sits at the target machine needs the WHOLE list
    in one run, because each rerun may cost another round of copying files over a network.
    """
    thieu, lech = [], []
    for tuong_doi, cho_doi in sorted(manifest.get("files", {}).items()):
        duong = os.path.join(goc, tuong_doi.replace("/", os.sep))
        if not os.path.isfile(duong):
            thieu.append(tuong_doi)
        elif sha256_of(duong) != cho_doi:
            lech.append(tuong_doi)
    return {"thieu": thieu, "lech": lech}


def kiem_moi_truong(manifest, tim_lenh=None):
    """Check the minimum Python, outside commands, MCP servers → dict `thieu` / `luu_y`.

    `tim_lenh` is injectable so tests do not depend on the running machine. Everything absent is
    returned as data, never raised: this script runs on a strange machine, and a traceback here
    means the user loses the way to patch things.
    """
    tim_lenh = tim_lenh or shutil.which
    thieu, luu_y = [], []

    toi_thieu = str(manifest.get("python_min") or "3.8")
    can = tuple(int(p) for p in toi_thieu.split("."))
    if sys.version_info[:len(can)] < can:
        dang_co = ".".join(str(p) for p in sys.version_info[:3])
        thieu.append(f"Python >= {toi_thieu} (found {dang_co})")

    for lenh in manifest.get("external_commands", []):
        if tim_lenh(lenh) is None:
            thieu.append(f"outside command `{lenh}` is not on PATH")

    for may_chu in manifest.get("mcp_servers", []):
        # Only a person can approve an MCP server in the harness UI — no machine can do it for them.
        luu_y.append(f"MCP `{may_chu}` needs you to approve it manually once")

    return {"thieu": thieu, "luu_y": luu_y}


# ------------------------------------------------------------------- setup

def ghi_de_co_backup(duong, noi_dung_moi):
    """Overwrite a file but always leave a `<file>.tdq-bak-<timestamp>`. Returns the backup path.

    There is no option to skip the backup: an overwritten file may carry something the user added
    (an `env` block, say), so being able to undo is the only thing keeping self-patching safe.
    """
    sao_luu = None
    if os.path.isfile(duong):
        dau = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        sao_luu = f"{duong}.tdq-bak-{dau}"
        shutil.copy2(duong, sao_luu)
        log(f"backed up {os.path.basename(duong)} → {os.path.basename(sao_luu)}")
    with open(duong, "w", encoding="utf-8") as f:
        f.write(noi_dung_moi)
    return sao_luu


def _ghi_json_co_backup(duong, du_lieu):
    noi_dung = json.dumps(du_lieu, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if _doc(duong) == noi_dung:
        return None
    ghi_de_co_backup(duong, noi_dung)
    return duong


def _doc(duong):
    try:
        with open(duong, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def chay_setup(goc, manifest):
    """Patch what can be patched, returning `(what was done, what could NOT be patched)`.

    The boundary is deliberately narrow: only the two config files rebuildable from bundle data.
    For any other drifting file the only right source is the original — inventing content for it
    is worse than leaving it, because `check` would then call a broken bundle clean.
    """
    da_lam, chiu = [], []

    for tuong_doi in kiem_file(goc, manifest)["thieu"]:
        thu_muc = os.path.dirname(os.path.join(goc, tuong_doi.replace("/", os.sep)))
        if thu_muc and not os.path.isdir(thu_muc):
            os.makedirs(thu_muc, exist_ok=True)
            da_lam.append(f"created directory {os.path.relpath(thu_muc, goc)}")

    # Patch only what the manifest really asks for: the codex bundle has no `.mcp.json`, and
    # adding one dirties the bundle — the next `check` finds a stray file nobody can explain.
    trong_manifest = set(manifest.get("files", {}))
    if ".mcp.json" in trong_manifest:
        if _ghi_json_co_backup(os.path.join(goc, ".mcp.json"), sinh_mcp()):
            da_lam.append("regenerated .mcp.json")

    duong_hooks = os.path.join(goc, GOC_TDQ.replace("/", os.sep), "hooks", "hooks.json")
    duong_settings = os.path.join(goc, ".claude", "settings.json")
    if ".claude/settings.json" in trong_manifest and os.path.isfile(duong_hooks):
        cai_dat = sinh_settings(goc, duong_hooks)
        cu = _doc(duong_settings)
        if cu:  # keep the user's existing `env` block — only the hook part is rebuilt
            try:
                cai_dat.setdefault("env", json.loads(cu).get("env", {}))
            except ValueError:
                pass
        mat_trang = cu is None
        if _ghi_json_co_backup(duong_settings, cai_dat):
            da_lam.append(
                "regenerated .claude/settings.json (the hook part; the `env` block cannot be"
                " recreated — copy it back from the original if you ever added variables there)"
                if mat_trang else "regenerated .claude/settings.json")

    con = kiem_file(goc, manifest)
    chiu = [f"{t} (copy it back from the original)" for t in con["thieu"] + con["lech"]]
    return da_lam, chiu


# -------------------------------------------------- project trust for Codex CLI

# The config directory of Codex. `CODEX_HOME` is the variable Codex itself reads, so honouring
# it is also what lets the tests run without ever touching the real `~/.codex`.
THU_MUC_CODEX_MAC_DINH = "~/.codex"


def duong_config_codex(moi_truong=None):
    """The path of the Codex CLI `config.toml` on this machine (it may not exist)."""
    moi_truong = os.environ if moi_truong is None else moi_truong
    goc = moi_truong.get("CODEX_HOME") or os.path.expanduser(THU_MUC_CODEX_MAC_DINH)
    return os.path.join(goc, "config.toml")


def _khoa_project(goc_bundle):
    """The TOML key of a project — Codex matches on the absolute, symlink-resolved path."""
    return f'[projects."{os.path.realpath(goc_bundle)}"]'


def da_trusted(goc_bundle, moi_truong=None):
    """Whether the project is declared `trust_level = "trusted"`. Missing file/permission → False.

    It raises on no input: this function runs on the `check` path, and a `check` that crashes on a
    strange machine means the user loses the way to diagnose anything.
    """
    noi_dung = _doc(duong_config_codex(moi_truong))
    if not noi_dung:
        return False
    khoa = _khoa_project(goc_bundle)
    vi_tri = noi_dung.find(khoa)
    if vi_tri < 0:
        return False
    # Read only up to the next block: the `trust_level` of ANOTHER project does not count.
    con_lai = noi_dung[vi_tri + len(khoa):]
    ket = con_lai.find("\n[")
    return 'trust_level = "trusted"' in (con_lai if ket < 0 else con_lai[:ket])


def bat_trusted(goc_bundle, moi_truong=None):
    """Write the block `[projects."<bundle>"] trust_level = "trusted"` into the Codex config.

    This is the ONLY path in this whole file writing outside the bundle tree, so three hard rules
    bind it: it runs only with the `--trust` flag, it always leaves a `<file>.tdq-bak-<timestamp>`
    before editing an existing file, and it never writes over the block of a declared project.

    Why it is needed anyway: until the project is trusted Codex ignores its ENTIRE `.codex/` layer
    — MCP is not loaded, hooks are not read. The bundle looks like it holds nothing, which is the
    very question that started this request.

    Returns `(written?, config path, reason it was skipped)`.
    """
    duong = duong_config_codex(moi_truong)
    if da_trusted(goc_bundle, moi_truong):
        return False, duong, "the project was already declared trusted"
    cu = _doc(duong)
    khoi = f'\n{_khoa_project(goc_bundle)}\ntrust_level = "trusted"\n'
    if cu is None:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with open(duong, "w", encoding="utf-8") as f:
            f.write("# TDQ Workflow added the block below via `setup --trust`.\n" + khoi)
        log(f"created {duong} and declared the project trusted")
        return True, duong, ""
    moi = cu if cu.endswith("\n") else cu + "\n"
    ghi_de_co_backup(duong, moi + khoi)
    log(f"writing {duong}: adding a projects block for {os.path.realpath(goc_bundle)}")
    return True, duong, ""


# ------------------------------------------------------- agy plugin layout

def kiem_layout_agy(goc, manifest):
    """Notes specific to the agy bundle → list of strings (never raises, never blocks).

    Recognised by `plugin.json` sitting at the bundle ROOT — that is the file that makes agy
    treat a directory as a plugin, and it exists in no other bundle. Two things are worth
    saying that the manifest hash check cannot say by itself:

    1. `config/settings.json` must be gone. Older bundles shipped one and told the user to
       copy it over `~/.gemini/antigravity-cli/settings.json`, which destroyed their own
       `model`/`colorScheme`/`trustedWorkspaces` while adding no guard.
    2. `hooks.json` carries an ABSOLUTE `command`, expanded at BUILD time. A bundle built
       under a different `$HOME` points its hooks at a path that does not exist here, and agy
       fails such a hook silently — which is indistinguishable from a hook with nothing to say.
    """
    if not os.path.isfile(os.path.join(goc, "plugin.json")):
        return []
    ghi_chu = []
    if os.path.isfile(os.path.join(goc, "config", "settings.json")):
        ghi_chu.append("stale config/settings.json — an old bundle; rebuild it, do NOT copy that "
                       "file over your own ~/.gemini/antigravity-cli/settings.json")
    duong_hooks = os.path.join(goc, "hooks.json")
    noi_dung = _doc(duong_hooks)
    if noi_dung is None:
        ghi_chu.append("hooks.json is missing from the plugin root — the hooks will never load")
        return ghi_chu
    nha = os.path.expanduser("~")
    if "~" in noi_dung:
        ghi_chu.append("hooks.json still holds an unexpanded `~` — agy needs an absolute command")
    elif nha not in noi_dung:
        ghi_chu.append(f"hooks.json was built under another home folder (not {nha}) — rebuild "
                       "with `python3 scripts/build_portable.py` before installing")
    return ghi_chu


# ---------------------------------------------------------------------- CLI

def _in_ket_qua(goc, manifest):
    file_ = kiem_file(goc, manifest)
    moi_truong = kiem_moi_truong(manifest)
    for tuong_doi in file_["thieu"]:
        print(f"MISSING  {tuong_doi}")
    for tuong_doi in file_["lech"]:
        print(f"DRIFT    {tuong_doi}")
    for dong in moi_truong["thieu"]:
        print(f"MISSING  {dong}")
    for dong in moi_truong["luu_y"]:
        print(f"NOTE     {dong}")
    for dong in bien_moi_truong_mcp(manifest):
        print(f"NOTE     variable {dong}")
    for dong in kiem_layout_agy(goc, manifest):
        print(f"NOTE     {dong}")
    # Only the codex bundle has a `.codex/` layer, and only that layer depends on the trust state.
    if ".codex/config.toml" in manifest.get("files", {}):
        if da_trusted(goc):
            print(f"NOTE     the project is trusted in {duong_config_codex()}")
        else:
            print("NOTE     the project is not trusted — Codex ignores the WHOLE .codex/ (MCP + hooks)"
                  " until you run `setup --trust` or click approve inside Codex")
    # A manifest listing no file proves nothing. Reporting "clean, 0 files" here turns a broken
    # manifest into a certificate of safety.
    if not manifest.get("files"):
        print("ERROR    the manifest lists no file — the portable bundle is broken, copy it again")
        return False
    sach = not (file_["thieu"] or file_["lech"] or moi_truong["thieu"])
    if sach:
        print(f"CLEAN    {len(manifest.get('files', {}))} file(s) match the manifest")
    return sach


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tdq_checkportable.py",
        description="Check a portable bundle against its manifest and patch what is missing.")
    parser.add_argument("lenh", choices=("check", "setup"))
    parser.add_argument("--root", help="bundle root, by default derived from the script location")
    parser.add_argument(
        "--trust", action="store_true",
        help="only with `setup`: declare this bundle a trusted project in the config.toml of "
             "Codex CLI (default ~/.codex, or $CODEX_HOME). This is the ONLY path writing outside "
             "the bundle; it always leaves a .tdq-bak-<timestamp> backup.")
    args = parser.parse_args(argv)

    goc = args.root or tim_goc_bundle()
    try:
        manifest = doc_manifest(goc)
    except (FileNotFoundError, ValueError) as loi:
        print(f"ERROR    {loi}")
        return EXIT_LECH

    log(f"{args.lenh} · root={goc}")
    if args.lenh == "setup":
        try:
            da_lam, chiu = chay_setup(goc, manifest)
        except OSError as loi:
            # A bundle unpacked with wrong permissions, or sitting on a read-only mount, is a common
            # case on a strange machine. A traceback here only makes the user think the script broke.
            print(f"ERROR    cannot write into the bundle: {loi}")
            print("         fix the directory permissions (chmod -R u+w), then run `setup` again")
            return EXIT_LECH
        if args.trust:
            try:
                da_ghi, duong, ly_do = bat_trusted(goc)
            except OSError as loi:
                print(f"ERROR    cannot write the Codex config: {loi}")
                return EXIT_LECH
            da_lam.append(f"khai project trusted trong {duong}" if da_ghi
                          else f"skipped --trust: {ly_do}")
        for viec in da_lam:
            print(f"DONE     {viec}")
        if not da_lam:
            print("DONE     (nothing needed patching)")
        for viec in chiu:
            print(f"LEFT     {viec}")
        sach = _in_ket_qua(goc, manifest)
        # Patched and still broken means exit 0 would be a lie — the user walks on and hits the
        # real error in the middle of a half-finished request.
        return 0 if sach else EXIT_LECH

    return 0 if _in_ket_qua(goc, manifest) else EXIT_LECH


if __name__ == "__main__":
    sys.exit(main())
