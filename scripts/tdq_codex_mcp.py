#!/usr/bin/env python3
"""Declare the lumen and lsp MCP servers for Codex, the same ones Claude Code starts.

Contract:
- Only ADDS servers that are missing. An existing `[mcp_servers.<name>]` entry is never edited,
  whatever it contains.
- Writes go through the official CLI (`codex mcp add <name> -- <command> [args...]`), never by
  editing `config.toml` by hand. The file is only READ here (tomllib), plus one backup copy.
- Backs up `config.toml` to `config.toml.truoc-tdq-<YYYYmmddHHMMSS>.bak` before the first add,
  and only when something will actually be added — so a second run makes no second backup.
- lsp: command and args copied verbatim from `~/.claude.json` -> `mcpServers.lsp`, so Codex
  starts exactly the language servers Claude Code starts.
- lumen: `<lumen binary> stdio`, the binary found by `tdq_lsp._binary_lumen` (one resolver only).
- A missing source (no codex, no lumen, no lsp entry) is reported and skipped, never raised.

Usage: python scripts/tdq_codex_mcp.py [--codex-home DIR] [--claude-json FILE]
Env: CODEX_HOME is the default codex home (else ~/.codex); TDQ_LOG=0 silences the stderr log.
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import utf8_io  # noqa: E402,F401 — imported so stdout/stderr become UTF-8

TEN_MAY_CHU = ("lumen", "lsp")
TIMEOUT_GIAY = 60


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] tdq_codex_mcp: {message}",
              file=sys.stderr)


def _tim_codex():
    return shutil.which("codex")


def _tim_lumen():
    """The lumen binary, via the single resolver in tdq_lsp. "" when absent."""
    try:
        import tdq_lsp
        return tdq_lsp._binary_lumen()
    except Exception as exc:  # a broken import must not stop the lsp half
        _log(f"không dò được lumen: {exc}")
        return ""


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
        _log(f"codex mcp list lỗi: {exc}")
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
        _log(f"không đọc được {cfg} ({exc}), chuyển sang codex mcp list")
        return _ten_tu_mcp_list(codex, env, chay)


def _nguon_lsp(claude_json):
    """-> ([command, *args], "") or (None, reason)."""
    try:
        with open(claude_json, encoding="utf-8") as f:
            muc = (json.load(f).get("mcpServers") or {}).get("lsp")
    except (OSError, ValueError) as exc:
        return None, f"không đọc được {claude_json} ({exc.__class__.__name__})"
    if not isinstance(muc, dict) or not muc.get("command"):
        return None, f"{claude_json} không có mcpServers.lsp"
    return [muc["command"], *[str(a) for a in muc.get("args") or []]], ""


def _nguon_lumen():
    duong = _tim_lumen()
    if not duong:
        return None, "không tìm thấy binary lumen"
    return [duong, "stdio"], ""


def khai_mcp_codex(codex_home=None, claude_json=None, chay=None):
    """Add the missing lumen/lsp MCP servers to Codex. -> human-readable result lines."""
    chay = chay or _chay_that
    claude_json = claude_json or os.path.expanduser("~/.claude.json")
    codex = _tim_codex()
    if not codex:
        _log("không thấy codex trên PATH")
        return ["Codex chưa cài (không thấy lệnh codex) — không khai MCP nào."]

    env = dict(os.environ)
    if codex_home:
        env["CODEX_HOME"] = codex_home
    home = codex_home or os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    cfg = os.path.join(home, "config.toml")
    da_co = _ten_da_co(cfg, codex, env, chay)
    _log(f"config={cfg} đã có={sorted(da_co)}")

    nguon = {"lumen": _nguon_lumen, "lsp": lambda: _nguon_lsp(claude_json)}
    dong, can_them = [], []
    for ten in TEN_MAY_CHU:
        if ten in da_co:
            dong.append(f"{ten}: đã có, giữ nguyên")
            continue
        lenh, ly_do = nguon[ten]()
        if lenh is None:
            dong.append(f"{ten}: bỏ qua — {ly_do}")
            continue
        can_them.append((ten, lenh))

    if can_them and os.path.isfile(cfg):
        bak = f"{cfg}.truoc-tdq-{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        shutil.copy2(cfg, bak)
        _log(f"backup {bak}")
        dong.append(f"đã sao lưu config.toml -> {bak}")

    for ten, lenh in can_them:
        argv = [codex, "mcp", "add", ten, "--", *lenh]
        _log("chạy " + " ".join(argv))
        try:
            ma, _, loi = chay(argv, env)
        except Exception as exc:
            dong.append(f"{ten}: thêm thất bại — {exc}")
            continue
        if ma == 0:
            dong.append(f"{ten}: đã thêm ({' '.join(lenh)})")
        else:
            dong.append(f"{ten}: thêm thất bại (mã {ma}) — {loi.strip()[-200:]}")
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
# then decides by name which calls count.
MATCHER_KHAI_NIEM = ".*lumen.*|.*lsp.*"


def _lenh_hook(ten):
    return f'python3 "{GOC_HOOK}/{ten}"'


def _hook_can_co():
    """-> [(event, matcher or None, command)] the search gate needs under Codex.

    `search_observe` is attached on BOTH PreToolUse and PostToolUse of the concept tools:
    PostToolUse is the right moment (the call happened) but its support under Codex is
    unverified; recording at PreToolUse too means a lumen call is never missed, and a duplicate
    row is harmless — a concept row only resets the unlock counter.
    """
    gate, so = _lenh_hook("search_gate.py"), _lenh_hook("search_observe.py")
    return [("PreToolUse", "Bash", gate),
            ("PreToolUse", MATCHER_KHAI_NIEM, so),
            ("PostToolUse", MATCHER_KHAI_NIEM, so),
            ("UserPromptSubmit", None, so)]


def khai_hook_codex(project):
    """Add the search gate to `<project>/.codex/hooks.json`. -> human-readable result lines.

    Same contract as `khai_mcp_codex`: back up before the first change, only ADD, never edit an
    entry that is already there, and running twice changes nothing. A file that is not valid
    JSON is left untouched and reported — overwriting a config we cannot read is how a user's
    hooks get lost.
    """
    duong = os.path.join(project, ".codex", "hooks.json")
    cfg = {"hooks": {}}
    if os.path.isfile(duong):
        try:
            with io.open(duong, encoding="utf-8") as fh:
                cfg = json.load(fh)
            if not isinstance(cfg, dict) or not isinstance(cfg.get("hooks", {}), dict):
                raise ValueError("unexpected shape")
        except (OSError, ValueError) as exc:
            _log(f"hooks.json không đọc được: {exc}")
            return [f"hook Codex: {duong} không phải JSON đọc được — để nguyên, không ghi gì ({exc})."]
    hooks = cfg.setdefault("hooks", {})

    can_them = []
    for event, matcher, lenh in _hook_can_co():
        da_co = any(h.get("command") == lenh
                    for muc in hooks.get(event, []) for h in (muc.get("hooks") or []))
        if not da_co:
            can_them.append((event, matcher, lenh))
    if not can_them:
        return ["hook Codex: cổng tìm kiếm đã có trong .codex/hooks.json, giữ nguyên."]

    dong = []
    if os.path.isfile(duong):
        bak = f"{duong}.truoc-tdq-{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        shutil.copy2(duong, bak)
        dong.append(f"hook Codex: đã sao lưu hooks.json -> {bak}")
    for event, matcher, lenh in can_them:
        muc = {"hooks": [{"type": "command", "command": lenh}]}
        if matcher:
            muc = {"matcher": matcher, **muc}
        hooks.setdefault(event, []).append(muc)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    _log(f"ghi {len(can_them)} entry vào {duong}")
    dong.append(f"hook Codex: đã thêm {len(can_them)} entry cổng tìm kiếm vào {duong}")
    dong.append("hook Codex: hook cấp project phải được TIN CẬY mới chạy — mở `codex` trong project "
                "này rồi duyệt nó ở `/hooks`.")
    return dong


def main(argv=None):
    ap = argparse.ArgumentParser(description="Khai MCP lumen + lsp cho Codex (chỉ thêm, không sửa).")
    ap.add_argument("--codex-home", help="thư mục CODEX_HOME (mặc định $CODEX_HOME hoặc ~/.codex)")
    ap.add_argument("--claude-json", help="file claude.json chứa mcpServers.lsp (mặc định ~/.claude.json)")
    args = ap.parse_args(argv)
    for dong in khai_mcp_codex(codex_home=args.codex_home, claude_json=args.claude_json):
        print(dong)
    return 0


if __name__ == "__main__":
    sys.exit(main())
