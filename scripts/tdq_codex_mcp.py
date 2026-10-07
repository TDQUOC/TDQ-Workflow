#!/usr/bin/env python3
"""Declare the lsp MCP server for Codex, the same one Claude Code starts (lumen left in 0.58.0).

Contract:
- Only ADDS servers that are missing. An existing `[mcp_servers.<name>]` entry is never edited,
  whatever it contains.
- Writes go through the official CLI (`codex mcp add <name> -- <command> [args...]`), never by
  editing `config.toml` by hand. The file is only READ here (tomllib), plus one backup copy.
- Backs up `config.toml` to `config.toml.truoc-tdq-<YYYYmmddHHMMSS>.bak` before the first add,
  and only when something will actually be added — so a second run makes no second backup.
- lsp: command and args copied verbatim from `~/.claude.json` -> `mcpServers.lsp`, so Codex
  starts exactly the language servers Claude Code starts.
- A missing source (no codex, no lsp entry) is reported and skipped, never raised.
- An old `[mcp_servers.lumen]` entry is left alone like any other existing entry: Codex starts
  fine with it pointing at a deleted binary (measured 2026-10-07); removing it is the user's call.

Usage: python scripts/tdq_codex_mcp.py [--codex-home DIR] [--claude-json FILE]
Env: CODEX_HOME is the default codex home (else ~/.codex); TDQ_LOG=0 silences the stderr log.
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import utf8_io  # noqa: E402,F401 — imported so stdout/stderr become UTF-8

TEN_MAY_CHU = ("lsp",)
TIMEOUT_GIAY = 60


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] tdq_codex_mcp: {message}",
              file=sys.stderr)


def _tim_codex():
    return shutil.which("codex")


def _chay_that(argv, env=None):
    """Default runner: list argv, no shell, bounded time. -> (returncode, stdout, stderr)."""
    proc = subprocess.run(argv, capture_output=True, encoding="utf-8", errors="replace",
                          env=env, timeout=TIMEOUT_GIAY)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _ten_tu_mcp_list(codex, env, chay):
    """Fallback: server names from the first column of `codex mcp list`."""
    try:
        ma, out, _ = chay([codex, "mcp", "list"], env)
    except Exception as exc:
        _log(f"codex mcp list failed: {exc}")
        return set()
    if ma != 0:
        return set()
    ten = set()
    for dong in out.splitlines():
        cot = dong.split()
        if not cot or cot[0] in ("Name", "WARNING:") or set(cot[0]) <= set("-─"):
            continue
        ten.add(cot[0])
    return ten


def _ten_da_co(cfg, codex, env, chay):
    """Names already declared. Read-only parse of config.toml; `codex mcp list` if unparsable."""
    if not os.path.isfile(cfg):
        return set()
    try:
        with open(cfg, "rb") as f:
            return set((tomllib.load(f).get("mcp_servers") or {}).keys())
    except (OSError, tomllib.TOMLDecodeError) as exc:
        _log(f"cannot read {cfg} ({exc}), falling back to codex mcp list")
        return _ten_tu_mcp_list(codex, env, chay)


def _nguon_lsp(claude_json):
    """-> ([command, *args], "") or (None, reason)."""
    try:
        with open(claude_json, encoding="utf-8") as f:
            muc = (json.load(f).get("mcpServers") or {}).get("lsp")
    except (OSError, ValueError) as exc:
        return None, f"cannot read {claude_json} ({exc.__class__.__name__})"
    if not isinstance(muc, dict) or not muc.get("command"):
        return None, f"{claude_json} has no mcpServers.lsp"
    return [muc["command"], *[str(a) for a in muc.get("args") or []]], ""


def khai_mcp_codex(codex_home=None, claude_json=None, chay=None):
    """Add the missing lsp MCP server to Codex. -> human-readable result lines."""
    chay = chay or _chay_that
    claude_json = claude_json or os.path.expanduser("~/.claude.json")
    codex = _tim_codex()
    if not codex:
        _log("codex not found on PATH")
        return ["Codex is not installed (no codex command found) - no MCP server declared."]

    env = dict(os.environ)
    if codex_home:
        env["CODEX_HOME"] = codex_home
    home = codex_home or os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    cfg = os.path.join(home, "config.toml")
    da_co = _ten_da_co(cfg, codex, env, chay)
    _log(f"config={cfg} present={sorted(da_co)}")

    nguon = {"lsp": lambda: _nguon_lsp(claude_json)}
    dong, can_them = [], []
    for ten in TEN_MAY_CHU:
        if ten in da_co:
            dong.append(f"{ten}: already present, left unchanged")
            continue
        lenh, ly_do = nguon[ten]()
        if lenh is None:
            dong.append(f"{ten}: skipped - {ly_do}")
            continue
        can_them.append((ten, lenh))

    if can_them and os.path.isfile(cfg):
        bak = f"{cfg}.truoc-tdq-{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        shutil.copy2(cfg, bak)
        _log(f"backup {bak}")
        dong.append(f"backed up config.toml -> {bak}")

    for ten, lenh in can_them:
        argv = [codex, "mcp", "add", ten, "--", *lenh]
        _log("running " + " ".join(argv))
        try:
            ma, _, loi = chay(argv, env)
        except Exception as exc:
            dong.append(f"{ten}: add failed - {exc}")
            continue
        if ma == 0:
            dong.append(f"{ten}: added ({' '.join(lenh)})")
        else:
            dong.append(f"{ten}: add failed (exit {ma}) - {loi.strip()[-200:]}")
    return dong


# --------------------------------------------------------------- the search gate, for Codex
# Codex dropped plugin-shipped hooks: `codex features list` on codex-cli 0.155.1 prints
# `plugin_hooks  removed  false` (measured 2026-10-03), while `hooks` is `stable true`. So the gate
# cannot travel inside the plugin the way it does for Claude Code; it has to be written into each
# project's `.codex/hooks.json`. Codex runs no `${CLAUDE_PLUGIN_ROOT}`, so commands carry the
# absolute path of THIS plugin copy.
GOC_HOOK = os.path.join(ROOT, "hooks", "scripts").replace(os.sep, "/")
# Concept-layer MCP tools under Codex. Their exact names could not be observed on this machine
# (Codex is not logged in here — 401), so the matcher is deliberately broad; `search_observe.py`
# then decides by name which calls count. lumen tools matched here too until 0.58.0.
MATCHER_KHAI_NIEM = ".*lsp.*"


def _lenh_hook(ten):
    return f'python3 "{GOC_HOOK}/{ten}"'


def _hook_can_co():
    """-> [(event, matcher or None, script, command)] the search gate needs under Codex.

    `search_observe` is attached on BOTH PreToolUse and PostToolUse of the concept tools:
    PostToolUse is the right moment (the call happened) but its support under Codex is
    unverified; recording at PreToolUse too means a concept call is never missed, and a duplicate
    row is harmless — a concept row only resets the unlock counter.
    It is also attached to PreToolUse `Bash`, in its own entry next to the gate's: under Codex
    a `graphify query|explain|path|god-nodes|affected` shell command is a concept-layer call,
    and without this entry it would never be recorded.
    """
    gate, so = "search_gate.py", "search_observe.py"
    return [(e, m, s, _lenh_hook(s)) for e, m, s in (
        ("PreToolUse", "Bash", gate),
        ("PreToolUse", "Bash", so),
        ("PreToolUse", MATCHER_KHAI_NIEM, so),
        ("PostToolUse", MATCHER_KHAI_NIEM, so),
        ("UserPromptSubmit", None, so))]


def _la_cua_minh(command, script):
    """True when `command` runs a script named `script` (any directory, quoted or not)."""
    return isinstance(command, str) and re.search(
        r'(^|[\\/"\'\s])' + re.escape(script) + r'["\']?\s*$', command) is not None


def _event_hong(entries):
    """Why a `hooks[event]` value cannot be handled safely, or "" when it can."""
    if not isinstance(entries, list):
        return f"is {type(entries).__name__}, not a list"
    for muc in entries:
        if not isinstance(muc, dict) or not isinstance(muc.get("hooks"), list):
            return "has an entry without a `hooks` list"
        if not all(isinstance(h, dict) for h in muc["hooks"]):
            return "has a hook that is not an object"
    return ""


# The two conditions a written hook needs before Codex runs it, both measured on Windows
# 2026-10-07 (`docs/tdq/research/2026-10-07-2041-hook-codex.md`). Neither is visible from inside a
# `codex exec` run: an untrusted hook is skipped without a warning, and a blocked process looks
# like "the environment blocks commands". Said on every write, because every write changes the
# hook hash and so needs a new review.
DIEU_KIEN_CHAY = (
    "Codex hook: project-level hooks only run once TRUSTED, and every rewrite of hooks.json needs "
    "a new review - open `codex` in this project and approve them under `/hooks`.",
    "Codex hook: on Windows the `read-only` and `workspace-write` sandboxes block every new process, "
    "hook processes included - the gate only runs where Codex may start processes.",
)


def _la_repo_plugin(project):
    """True when `project` is this plugin's own source repo, whose `.codex/hooks.json` is the
    hand-written fence of `codex implement` (locked by `tests/test_codex_hooks_json.py`)."""
    try:
        return os.path.samefile(project, ROOT)
    except OSError:
        return False


def khai_hook_codex(project):
    """Add the search gate to `<project>/.codex/hooks.json`. -> human-readable result lines.

    Same contract as `khai_mcp_codex`: back up before the first change, and running twice
    changes nothing. An entry is OURS when, in the same event and with the same matcher, its
    command runs a script with the same file name (`search_gate.py` / `search_observe.py`):
    if its path is stale (the plugin cache path carries the version, so every plugin update
    moves it) the command is rewritten in place to the current path, never duplicated — a stale
    path to a deleted file makes `python3` exit 2 on every call. Every other entry is left as is.
    A file that is not valid JSON, or whose shape for one of our events is unexpected, is left
    untouched and reported — overwriting a config we cannot read is how a user's hooks get lost.
    """
    if _la_repo_plugin(project):
        _log(f"{project} is the plugin's own repo - its .codex/hooks.json is hand-written")
        return ["Codex hook: this is the TDQ plugin's own repo - its .codex/hooks.json is the "
                "hand-written file fence of `codex implement`, left unchanged."]
    duong = os.path.join(project, ".codex", "hooks.json")
    cfg = {"hooks": {}}
    if os.path.isfile(duong):
        try:
            with io.open(duong, encoding="utf-8") as fh:
                cfg = json.load(fh)
            if not isinstance(cfg, dict) or not isinstance(cfg.get("hooks", {}), dict):
                raise ValueError("unexpected shape")
        except (OSError, ValueError) as exc:
            _log(f"hooks.json unreadable: {exc}")
            return [f"Codex hook: {duong} is not readable JSON - left untouched, nothing written ({exc})."]
    hooks = cfg.setdefault("hooks", {})

    can_co = _hook_can_co()
    for event in dict.fromkeys(e for e, _, _, _ in can_co):
        ly_do = _event_hong(hooks.get(event, []))
        if ly_do:
            _log(f"hooks.json event {event} {ly_do}")
            return [f"Codex hook: in {duong}, hooks.{event} {ly_do} - left untouched, "
                    "nothing written."]

    can_them, so_sua = [], 0
    for event, matcher, script, lenh in can_co:
        cua_minh = [h for muc in hooks.get(event, []) if muc.get("matcher") == matcher
                    for h in muc["hooks"] if _la_cua_minh(h.get("command"), script)]
        if not cua_minh:
            can_them.append((event, matcher, lenh))
        for h in cua_minh:
            if h["command"] != lenh:
                h["command"] = lenh
                so_sua += 1
    if not can_them and not so_sua:
        return ["Codex hook: the search gate is already in .codex/hooks.json, left unchanged.",
                *DIEU_KIEN_CHAY]

    dong = []
    if os.path.isfile(duong):
        bak = f"{duong}.truoc-tdq-{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        shutil.copy2(duong, bak)
        dong.append(f"Codex hook: backed up hooks.json -> {bak}")
    for event, matcher, lenh in can_them:
        muc = {"hooks": [{"type": "command", "command": lenh}]}
        if matcher:
            muc = {"matcher": matcher, **muc}
        hooks.setdefault(event, []).append(muc)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    _log(f"added {len(can_them)}, updated {so_sua} entries in {duong}")
    if so_sua:
        dong.append(f"Codex hook: updated {so_sua} search-gate command(s) to the current plugin "
                    f"path in {duong}")
    if can_them:
        dong.append(f"Codex hook: added {len(can_them)} search-gate entries to {duong}")
    dong.extend(DIEU_KIEN_CHAY)
    return dong


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Declare the lsp MCP server for Codex (add only, never edit).")
    ap.add_argument("--codex-home", help="CODEX_HOME directory (default $CODEX_HOME or ~/.codex)")
    ap.add_argument("--claude-json",
                    help="claude.json file holding mcpServers.lsp (default ~/.claude.json)")
    args = ap.parse_args(argv)
    for dong in khai_mcp_codex(codex_home=args.codex_home, claude_json=args.claude_json):
        print(dong)
    return 0


if __name__ == "__main__":
    sys.exit(main())
