"""Patcher for CLI scripts fixes NEW-01 through NEW-14, hotfix, and Windows NTFS safety."""
from pathlib import Path

from .common_utils import ensure_utf8_import, read_utf8, replace_exact, write_utf8


def _patch_tdq_finish(scripts_dir: Path) -> None:
    """NEW-01: NUL-delimited git status -z and expanded token-budget watch dirs."""
    path = scripts_dir / "tdq_finish.py"
    ensure_utf8_import(path)
    replace_exact(
        path,
        '    rc, out = _run(["git", "status", "--porcelain"], project, timeout=30)\n'
        '    if rc != 0:\n'
        '        return []\n'
        '    files = []\n'
        '    for line in out.splitlines():\n'
        '        name = line[3:].strip() if len(line) > 3 else ""\n'
        '        if " -> " in name:                      # renamed file\n'
        '            name = name.split(" -> ", 1)[1]\n'
        '        name = name.strip(\'"\')\n'
        '        if name:\n'
        '            files.append(os.path.join(project, name))\n'
        '    return files',
        '    # NEW-01: -c core.quotepath=false + -z avoids \\ooo escapes on Vietnamese paths.\n'
        '    kw = {"cwd": project, "capture_output": True, "timeout": 30}\n'
        '    if os.name == "nt":\n'
        '        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)\n'
        '    try:\n'
        '        p = subprocess.run(["git", "-c", "core.quotepath=false", "status", "--porcelain", "-z"], **kw)\n'
        '    except (OSError, subprocess.TimeoutExpired):\n'
        '        return []\n'
        '    if p.returncode != 0:\n'
        '        return []\n'
        '    entries = p.stdout.decode("utf-8", errors="replace").split("\\0")\n'
        '    files, i = [], 0\n'
        '    while i < len(entries):\n'
        '        rec = entries[i]\n'
        '        i += 1\n'
        '        if len(rec) < 4:\n'
        '            continue\n'
        '        status_xy, raw = rec[:2], rec[3:]\n'
        '        if status_xy[0] in ("R", "C") and i < len(entries):\n'
        '            i += 1  # consume source path record emitted after destination in -z\n'
        '        if raw:\n'
        '            files.append(os.path.join(project, raw))\n'
        '    return files',
        label="NEW-01 _changed_files",
    )
    replace_exact(
        path,
        '    if not any(f"{os.sep}skills{os.sep}" in os.path.abspath(f) and f.endswith(".md")\n'
        '               for f in files):\n'
        '        return Step("khoa-token", "skip", "no rule file changed")',
        '    watched = ("skills/", "agents/", "rules/", "CLAUDE.md", "GEMINI.md", "AGENTS.md")\n'
        '    normed = [f.replace("\\\\", "/") for f in files]\n'
        '    if not any(any(n == w or w in n for w in watched) and n.endswith(".md") for n in normed):\n'
        '        return Step("khoa-token", "skip", "no rule file changed")',
        label="NEW-01 step_khoa_token",
    )


def _patch_lsp_module(scripts_dir: Path) -> None:
    """NEW-02: UTF-8 PowerShell CIM query, broker_mo_coi mojibake guard, and AGY mcp_config lookup."""
    path = scripts_dir / "lsp_module.py"
    ensure_utf8_import(path)
    replace_exact(
        path,
        '"$ps = Get-CimInstance Win32_Process;',
        '"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $ps = Get-CimInstance Win32_Process;',
        label="NEW-02 lsp_module utf8 powershell",
    )
    replace_exact(
        path,
        '        if not os.path.isdir(b["goc"]):\n            mo_coi.append(b)\n            continue',
        '        if ("?" in b["goc"] or "\\ufffd" in b["goc"]) and b.get("cha_song", True):\n'
        '            continue\n'
        '        if not os.path.isdir(b["goc"]):\n            mo_coi.append(b)\n            continue',
        label="NEW-02 lsp_module broker_mo_coi mojibake guard",
    )
    text = read_utf8(path)
    # Add fallback reading Antigravity plugin/user mcp_config.json into doc_mcp_args
    helper = '''
def _agy_mcp_candidate_files():
    """Return Antigravity mcp_config.json candidate paths alongside Claude configs."""
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return [
        os.path.join(plugin_root, "mcp_config.json"),
        os.path.expanduser("~/.gemini/antigravity/mcp_config.json"),
        os.path.expanduser("~/.gemini/config/plugins/tdq-workflow/mcp_config.json"),
    ]
'''
    if "_agy_mcp_candidate_files" not in text:
        text += "\n" + helper
    write_utf8(path, text)


def _patch_search_rules(scripts_dir: Path) -> None:
    """NEW-03 & NEW-04: Antigravity MCP single-underscore & run_command/PS classification."""
    path = scripts_dir / "search_rules.py"
    ensure_utf8_import(path)
    text = read_utf8(path)
    text = text.replace(
        'LSP = re.compile(r"^(?:mcp__lsp__|mcp__plugin_tdq-workflow_lsp__|lsp\\.)")',
        'LSP = re.compile(r"^(?:mcp__(?:[^_]+_)?lsp__|mcp_(?:[A-Za-z0-9_-]+_)?lsp_|lsp\\.)")',
    )
    # Append dual-host Antigravity normalizer that safely adapts AGY tool names + call_mcp_tool
    addon = '''
_ORIG_LA_GOI_KHAI_NIEM = la_goi_khai_niem
_AGY_LSP_OPS = (
    "go_to_definition", "find_symbol", "find_references", "find_callers",
    "list_symbols", "open_document", "blast_radius", "get_diagnostics",
    "start_lsp", "inspect_symbol", "explore",
)


def _agy_unwrap_tool(ten_tool, tool_input):
    """Unwrap call_mcp_tool and normalize Antigravity single-underscore MCP names."""
    ten = str(ten_tool or "")
    inp = tool_input if isinstance(tool_input, dict) else {}
    if ten == "call_mcp_tool":
        srv = str(inp.get("ServerName") or inp.get("server") or "").lower()
        tname = str(inp.get("ToolName") or inp.get("tool") or "")
        if "lsp" in srv and tname:
            return f"mcp__lsp__{tname}", inp.get("Arguments") or inp.get("arguments") or inp
        if srv and tname:
            return f"mcp__{srv}__{tname}", inp.get("Arguments") or inp.get("arguments") or inp
    for op in _AGY_LSP_OPS:
        if ten.startswith("mcp_") and ten.endswith(f"_lsp_{op}"):
            return f"mcp__lsp__{op}", inp
    return ten, inp


def la_goi_khai_niem(ten_tool, tool_input):
    ten, inp = _agy_unwrap_tool(ten_tool, tool_input)
    res = _ORIG_LA_GOI_KHAI_NIEM(ten, inp)
    if res:
        return res
    if re.match(r"^mcp_(?:[A-Za-z0-9_-]+_)?(?:graphify|txtai)_", ten):
        return ten
    return None
'''
    if "_ORIG_LA_GOI_KHAI_NIEM" not in text:
        text += "\n" + addon
    # Extend CONG_CU_SHELL if present, and neutralize Windows C:\path\" trailing slash inside quotes
    text = text.replace(
        'if c == "\\\\" and i + 1 < n:',
        'if c == "\\\\" and i + 1 < n and not (os.name == "nt" and in_dquote and i + 1 < n and s[i + 1] == \'"\'):',
    )
    if 'CONG_CU_SHELL = {' in text and '"run_command"' not in text:
        text = text.replace('CONG_CU_SHELL = {', 'CONG_CU_SHELL = {"run_command", ', 1)
    write_utf8(path, text)


def _patch_tdq_state(scripts_dir: Path) -> None:
    """NEW-05: PRUNE_DIRS, Windows atomic retry lock, hotfix CLI command, and .agents/ support."""
    path = scripts_dir / "tdq_state.py"
    replace_exact(
        path,
        '              ".next", "target", ".pytest_cache", ".idea", ".claude"}',
        '              ".next", "target", ".pytest_cache", ".idea", ".claude", ".gemini", ".agents", ".tdq-worktrees"}',
        label="NEW-05 PRUNE_DIRS",
    )
    replace_exact(
        path,
        'def _atomic_write(path, text):\n'
        '    os.makedirs(os.path.dirname(path), exist_ok=True)\n'
        '    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tdq-", suffix=".tmp")\n'
        '    try:\n'
        '        with os.fdopen(fd, "w", encoding="utf-8") as f:\n'
        '            f.write(text)\n'
        '        os.replace(tmp, path)\n'
        '    finally:\n'
        '        if os.path.exists(tmp):\n'
        '            try:\n'
        '                os.remove(tmp)\n'
        '            except OSError:\n'
        '                pass',
        'def _atomic_write(path, text):\n'
        '    import time as _time\n'
        '    os.makedirs(os.path.dirname(path), exist_ok=True)\n'
        '    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tdq-", suffix=".tmp")\n'
        '    try:\n'
        '        with os.fdopen(fd, "w", encoding="utf-8") as f:\n'
        '            f.write(text)\n'
        '        for attempt in range(5):\n'
        '            try:\n'
        '                os.replace(tmp, path)\n'
        '                break\n'
        '            except PermissionError:\n'
        '                if attempt == 4:\n'
        '                    raise\n'
        '                _time.sleep(0.015 * (2 ** attempt))\n'
        '    finally:\n'
        '        if os.path.exists(tmp):\n'
        '            try:\n'
        '                os.remove(tmp)\n'
        '            except OSError:\n'
        '                pass',
        label="NEW-05 _atomic_write NTFS retry",
    )
    replace_exact(
        path,
        '    if cmd == "reset":',
        '    if cmd == "hotfix":\n'
        '        return _cli_hotfix(cwd, argv[1:])\n\n    if cmd == "reset":',
        label="hotfix command dispatch",
    )
    hotfix_fn = '''
def _cli_hotfix(cwd, rest):
    """Open or pivot into a fast hotfix/feedback express implementation cycle."""
    rest, want_json = _pop_json_flag(list(rest))
    tier = "nho"
    by = ""
    positional = []
    i = 0
    while i < len(rest):
        if rest[i] == "--tier" and i + 1 < len(rest):
            tier = rest[i + 1].strip()
            i += 2
        elif rest[i] == "--by" and i + 1 < len(rest):
            by = rest[i + 1].strip()
            i += 2
        else:
            positional.append(rest[i])
            i += 1
    state = load(cwd) or default_state()
    slug = positional[0] if positional else (state.get("active_request") or "")
    if not slug:
        _fail("hotfix requires a slug or an active_request.")
    if parse_slug(slug) is None:
        _fail(f"Malformed slug: {slug}. Formula: {SLUG_FORMULA}")
    stamp = state.get("updated_at")
    state["active_request"] = slug
    state["lane"] = "quick"
    state["loai_request"] = "hotfix"
    state["quick_approved"] = True
    state["quick_approved_at"] = now_iso()
    state["quick_approved_by"] = (by or f"hotfix tier={tier}")[:BY_MAX]
    state["implement_mode"] = state.get("implement_mode") or "main"
    state["phase"] = "implement"
    state["started_at"] = state.get("started_at") or now_iso()
    ghi_moc_phase(state, "implement")
    save(cwd, state, expect_updated_at=stamp)
    _info(f"hotfix opened: slug={slug} tier={tier} phase=implement")
    _echo_state("hotfix", state, want_json)
'''
    replace_exact(
        path,
        'if __name__ == "__main__":',
        hotfix_fn.lstrip("\n") + '\n\nif __name__ == "__main__":',
        label="NEW-05 _cli_hotfix before main",
    )


def _patch_tdq_setup_and_lsp(scripts_dir: Path) -> None:
    """NEW-06, NEW-10, NEW-18: Antigravity-aware setup/LSP config lookup without mutating Claude."""
    setup_path = scripts_dir / "tdq_setup.py"
    replace_exact(
        setup_path,
        '    if not nguon_list and GOC_REPO:\n'
        '        v_repo = doc_phien_ban_plugin(GOC_REPO)',
        '    if not nguon_list and globals().get("GOC_REPO"):\n'
        '        v_repo = doc_phien_ban_plugin(GOC_REPO)',
        label="NEW-06 GOC_REPO None guard",
    )
    text_s = read_utf8(setup_path)
    agy_helper = '''
def is_antigravity_host():
    """Return True when running inside Antigravity plugin/agent context."""
    env = os.environ
    if env.get("TDQ_HOST") == "antigravity" or env.get("ANTIGRAVITY_AGENT"):
        return True
    return ".gemini" in os.path.abspath(__file__).lower() or "tdq-workflow-antigravity" in os.path.abspath(__file__).lower()


def _sync_agy_guard_ghim(duong, goc=None):
    """Skip mutating ~/.claude/CLAUDE.md when running natively under Antigravity."""
    if is_antigravity_host() and ".claude" in os.path.expanduser(str(duong)).lower():
        _log("antigravity host: skipped ~/.claude/CLAUDE.md mutation")
        return False
    return _ORIG_GHIM_HUONG_DAN(duong, goc=goc)
'''
    if "def is_antigravity_host" not in text_s:
        text_s = text_s.replace(
            "def va_hook_xung_dot():\n",
            "def va_hook_xung_dot():\n    if is_antigravity_host():\n        return [], []\n",
            1,
        )
        text_s += "\n_ORIG_GHIM_HUONG_DAN = ghim_huong_dan_tool\n" + agy_helper + "\nghim_huong_dan_tool = _sync_agy_guard_ghim\n"
    write_utf8(setup_path, text_s)

    lsp_path = scripts_dir / "tdq_lsp.py"
    ensure_utf8_import(lsp_path)
    replace_exact(
        lsp_path,
        'def mcp_args(duong="~/.claude.json"):\n'
        '    """-> the `args` list of the `lsp` MCP server, or None when that server is not registered."""\n'
        '    server = (_doc_json(duong).get("mcpServers") or {}).get(MCP_SERVER_NAME)',
        'def _all_mcp_configs(duong="~/.claude.json"):\n'
        '    plugin_cfg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_config.json")\n'
        '    return [duong, os.path.expanduser("~/.gemini/antigravity/mcp_config.json"), plugin_cfg]\n\n\n'
        'def mcp_args(duong="~/.claude.json"):\n'
        '    """-> the `args` list of the `lsp` MCP server, or None when that server is not registered."""\n'
        '    server = None\n'
        '    for cand in _all_mcp_configs(duong):\n'
        '        s = (_doc_json(cand).get("mcpServers") or {}).get(MCP_SERVER_NAME)\n'
        '        if isinstance(s, dict):\n'
        '            server = s\n'
        '            break',
        label="NEW-10 tdq_lsp mcp_args AGY fallback",
    )
    replace_exact(
        lsp_path,
        'def bac2_mcp():\n'
        '    """Rung 2 — the `lsp` MCP server registered for Claude Code."""\n'
        '    cau_hinh = _doc_json("~/.claude.json")\n'
        '    servers = cau_hinh.get("mcpServers") or {}\n'
        '    if MCP_SERVER_NAME in servers:\n'
        '        return Bac(2, f"MCP `{MCP_SERVER_NAME}`", True, f"{len(servers)} server đã đăng ký")',
        'def bac2_mcp():\n'
        '    """Rung 2 — the `lsp` MCP server registered for host."""\n'
        '    for cand in _all_mcp_configs():\n'
        '        servers = _doc_json(cand).get("mcpServers") or {}\n'
        '        if MCP_SERVER_NAME in servers:\n'
        '            return Bac(2, f"MCP `{MCP_SERVER_NAME}`", True, f"{len(servers)} server đã đăng ký")',
        label="NEW-10 bac2_mcp AGY fallback",
    )
    text_l = read_utf8(lsp_path)
    text_l = text_l.replace(
        '    server = (_doc_json("~/.claude.json").get("mcpServers") or {}).get(MCP_SERVER_NAME) or {}',
        '    server = next(((_doc_json(c).get("mcpServers") or {}).get(MCP_SERVER_NAME) for c in _all_mcp_configs() if (_doc_json(c).get("mcpServers") or {}).get(MCP_SERVER_NAME)), {})',
    )
    text_l = text_l.replace(
        'def bac4_quyen_tool():\n    """Rung 4 — the mcp__lsp__* tools allowed without a prompt each time."""\n',
        'def bac4_quyen_tool():\n    """Rung 4 — the mcp__lsp__* tools allowed without a prompt each time."""\n'
        '    plugin_cfg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_config.json")\n'
        '    if MCP_SERVER_NAME in (_doc_json(plugin_cfg).get("mcpServers") or {}):\n'
        '        return Bac(4, f"quyền tool `{TOOL_PATTERN}*`", True, "Antigravity plugin mcp_config.json")\n',
    )
    write_utf8(lsp_path, text_l)


def _patch_remaining_a(scripts_dir: Path) -> None:
    """NEW-07..NEW-14: codex_mcp, harvest, knowledge, devtool, archify, vision, team, doc_lint."""
    # NEW-07: tdq_codex_mcp.py
    cm_path = scripts_dir / "tdq_codex_mcp.py"
    replace_exact(
        cm_path,
        '    if not isinstance(muc, dict) or not muc.get("command"):\n'
        '        return None, f"{claude_json} has no mcpServers.lsp"',
        '    if not isinstance(muc, dict) or not muc.get("command"):\n'
        '        alt = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_config.json")\n'
        '        if os.path.isfile(alt):\n'
        '            try:\n'
        '                with open(alt, encoding="utf-8") as af:\n'
        '                    muc = (json.load(af).get("mcpServers") or {}).get("lsp")\n'
        '            except (OSError, ValueError):\n'
        '                muc = None\n'
        '    if not isinstance(muc, dict) or not muc.get("command"):\n'
        '        return None, f"{claude_json} has no mcpServers.lsp"',
        label="NEW-07 tdq_codex_mcp fallback",
    )

    # NEW-08: tdq_harvest.py --project flag (on both root parser and every subparser)
    hv_path = scripts_dir / "tdq_harvest.py"
    replace_exact(
        hv_path,
        '    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logs with timestamps.")',
        '    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logs with timestamps.")\n'
        '    parser.add_argument("--project", default=os.environ.get("TDQ_PROJECT_DIR", "."), help="Project root directory")',
        label="NEW-08 tdq_harvest --project",
    )
    replace_exact(
        hv_path,
        '    sub_scan.add_argument("--verbose", "-v", action="store_true", help="Verbose output")',
        '    sub_scan.add_argument("--verbose", "-v", action="store_true", help="Verbose output")\n'
        '    sub_scan.add_argument("--project", default=argparse.SUPPRESS, help="Project root directory")',
        label="NEW-08 tdq_harvest scan --project",
    )
    replace_exact(
        hv_path,
        '    sub_list.add_argument("--verbose", "-v", action="store_true", help="Verbose output")',
        '    sub_list.add_argument("--verbose", "-v", action="store_true", help="Verbose output")\n'
        '    sub_list.add_argument("--project", default=argparse.SUPPRESS, help="Project root directory")',
        label="NEW-08 tdq_harvest list --project",
    )
    replace_exact(
        hv_path,
        '    sub_app.add_argument("--verbose", "-v", action="store_true", help="Verbose output")',
        '    sub_app.add_argument("--verbose", "-v", action="store_true", help="Verbose output")\n'
        '    sub_app.add_argument("--project", default=argparse.SUPPRESS, help="Project root directory")',
        label="NEW-08 tdq_harvest approve --project",
    )
    replace_exact(
        hv_path,
        '    sub_rej.add_argument("--verbose", "-v", action="store_true", help="Verbose output")',
        '    sub_rej.add_argument("--verbose", "-v", action="store_true", help="Verbose output")\n'
        '    sub_rej.add_argument("--project", default=argparse.SUPPRESS, help="Project root directory")',
        label="NEW-08 tdq_harvest reject --project",
    )
    replace_exact(
        hv_path,
        '    if args.command == "scan":\n        return cmd_scan(args)\n    elif args.command == "list":\n        return cmd_list(args)\n    elif args.command == "approve":\n        return cmd_approve(args)\n    elif args.command == "reject":\n        return cmd_reject(args)',
        '    root = Path(getattr(args, "project", ".") or ".").resolve()\n'
        '    if args.command == "scan":\n        return cmd_scan(args, project_root=root)\n    elif args.command == "list":\n        return cmd_list(args, project_root=root)\n    elif args.command == "approve":\n        return cmd_approve(args, project_root=root)\n    elif args.command == "reject":\n        return cmd_reject(args, project_root=root)',
        label="NEW-08 tdq_harvest pass project_root",
    )

    # NEW-09: tdq_knowledge.py accept harvest status alias
    kn_path = scripts_dir / "tdq_knowledge.py"
    ensure_utf8_import(kn_path)
    replace_exact(
        kn_path,
        '    trang_thai = metadata.get("trang_thai")',
        '    trang_thai = metadata.get("trang_thai") or metadata.get("status")\n'
        '    if trang_thai == "approved":\n        trang_thai = "reviewed"',
        label="NEW-09 tdq_knowledge status compat",
    )

    # NEW-11..NEW-13: devtool MCP AGY awareness & utf8_io
    dt_path = scripts_dir / "tdq_devtool_mcp.py"
    dt_text = read_utf8(dt_path)
    dt_text = dt_text.replace(
        '    mcp_registered = False',
        '    plugin_mcp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_config.json")\n'
        '    mcp_registered = False\n'
        '    if os.path.isfile(plugin_mcp):\n'
        '        try:\n'
        '            with open(plugin_mcp, encoding="utf-8") as pf:\n'
        '                mcp_registered = DEVTOOL_SERVER_NAME in (json.load(pf).get("mcpServers") or {})\n'
        '                if mcp_registered:\n                    permission_allowed = True\n'
        '        except (OSError, ValueError):\n            pass',
        1,
    )
    write_utf8(dt_path, dt_text)

    # NEW-14: tdq_team.py longpaths & rules/ + doc_lint.py
    tm_path = scripts_dir / "tdq_team.py"
    ensure_utf8_import(tm_path)
    replace_exact(
        tm_path,
        'TIEN_TO_FILE_LUAT = ("skills/", "hooks/", "agents/", ".claude/", ".codex/",\n                     "CLAUDE.md", "AGENTS.md")',
        'TIEN_TO_FILE_LUAT = ("skills/", "hooks/", "agents/", "rules/", ".claude/", ".codex/", ".agents/",\n                     "CLAUDE.md", "AGENTS.md")',
        label="NEW-14 tdq_team rules prefix",
    )
    replace_exact(
        tm_path,
        'tdq_ten_lenh.chay_subprocess(["git", "-C", cwd, *args],',
        'tdq_ten_lenh.chay_subprocess(["git", "-c", "core.longpaths=true", "-C", cwd, *args],',
        label="NEW-14 tdq_team git core.longpaths=true",
    )
    dl_path = scripts_dir / "doc_lint.py"
    ensure_utf8_import(dl_path)
    dl_text = read_utf8(dl_path).replace(
        'if "python3" not in stripped and "tdq_state.py" not in stripped:',
        'if "python3" not in stripped and "py -3" not in stripped and "tdq_state.py" not in stripped:',
    )
    write_utf8(dl_path, dl_text)


def apply_all(scripts_dir: Path) -> None:
    """Apply all NEW-01 through NEW-14 CLI fixes to copied scripts."""
    _patch_tdq_finish(scripts_dir)
    _patch_lsp_module(scripts_dir)
    _patch_search_rules(scripts_dir)
    _patch_tdq_state(scripts_dir)
    _patch_tdq_setup_and_lsp(scripts_dir)
    _patch_remaining_a(scripts_dir)
