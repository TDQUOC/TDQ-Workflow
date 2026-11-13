"""Patcher for CLI scripts fixes NEW-15 through NEW-28 (transcript AGY, eval hosts, test harness)."""
from pathlib import Path

from .common_utils import ensure_utf8_import, read_utf8, replace_exact, write_utf8


def _patch_tdq_transcript(scripts_dir: Path) -> None:
    """NEW-19: Add Antigravity brain transcript.jsonl + Double-JSON tool_calls parser."""
    path = scripts_dir / "tdq_transcript.py"
    ensure_utf8_import(path)
    replace_exact(
        path,
        'CLAUDE_TYPES = {"api-request", "assistant", "user", "system", "progress"}\n'
        'CODEX_TYPES = {"session_meta", "response_item", "event_msg", "turn_context"}',
        'CLAUDE_TYPES = {"api-request", "assistant", "user", "system", "progress"}\n'
        'CODEX_TYPES = {"session_meta", "response_item", "event_msg", "turn_context"}\n'
        'AGY_TYPES = {"USER_INPUT", "PLANNER_RESPONSE", "SYSTEM", "TOOL_RESPONSE"}',
        label="NEW-19 AGY_TYPES",
    )
    replace_exact(
        path,
        '    else:\n        roots = _claude_directories(project_dir, home) if host != "codex" else []\n'
        '        if host != "claude":\n'
        '            roots.append(Path(home or Path.home()) / ".codex" / "sessions")',
        '    else:\n'
        '        roots = _claude_directories(project_dir, home) if host in ("auto", "claude") else []\n'
        '        if host in ("auto", "codex"):\n'
        '            roots.append(Path(home or Path.home()) / ".codex" / "sessions")\n'
        '        if host in ("auto", "antigravity", "agy"):\n'
        '            roots.extend(_agy_directories(home))',
        label="NEW-19 _candidate_paths AGY",
    )
    replace_exact(
        path,
        '        _read_metadata(record, metadata)\n        _read_claude(record, events)\n        _read_codex(record, events)',
        '        _read_metadata(record, metadata)\n        _read_claude(record, events)\n        _read_codex(record, events)\n        _read_agy(record, events)',
        label="NEW-19 _normalize_line _read_agy",
    )
    replace_exact(
        path,
        '    elif event_type not in UNTIMED_TYPES:\n        _issue(source, "unknown_events")',
        '    elif event_type in AGY_TYPES:\n'
        '        source["_hosts"].add("antigravity")\n'
        '        _identity_value(source, record.get("conversation_id") or record.get("conversationId"), "_sessions")\n'
        '    elif event_type not in UNTIMED_TYPES:\n        _issue(source, "unknown_events")',
        label="NEW-19 _read_metadata AGY",
    )
    agy_funcs = '''
def _agy_directories(home=None):
    """Return Antigravity brain log directories under ~/.gemini/antigravity/brain/*/.system_generated/logs."""
    base = Path(home or Path.home()) / ".gemini" / "antigravity" / "brain"
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob("*/.system_generated/logs") if p.is_dir())


def _decode_double_json(raw_args):
    """Unwrap Double-JSON stringified args in Antigravity PLANNER_RESPONSE tool_calls."""
    val = raw_args
    for _ in range(2):
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except ValueError:
                break
    return val


def _read_agy(record, source):
    """Extract API and Double-JSON tool timing marks from Antigravity transcript.jsonl records."""
    event_type = record.get("type")
    if event_type not in AGY_TYPES:
        return
    at_val = record.get("created_at") or record.get("timestamp")
    ts_rec = {"timestamp": at_val}
    step_id = str(record.get("step_index") if record.get("step_index") is not None else "0")
    if event_type == "USER_INPUT":
        source["_capabilities"].add("api")
        _mark(source, ts_rec, "api", "start", f"step:{step_id}", step_id)
        return
    if event_type == "PLANNER_RESPONSE":
        _mark(source, ts_rec, "api", "end", f"step:{step_id}", step_id)
        tcalls = record.get("tool_calls") or []
        if isinstance(tcalls, list) and tcalls:
            source["_capabilities"].add("tool")
            for idx, call in enumerate(tcalls):
                if not isinstance(call, dict):
                    continue
                _ = _decode_double_json(call.get("arguments") or call.get("args"))
                cid = str(call.get("id") or f"agy:{step_id}:{idx}")
                _mark(source, ts_rec, "tool", "start", cid, step_id)
                _mark(source, ts_rec, "tool", "end", cid, step_id)
'''
    text = read_utf8(path) + "\n" + agy_funcs
    write_utf8(path, text)


def _patch_eval_hosts(scripts_dir: Path) -> None:
    """NEW-20 & NEW-21: Add antigravity host adapter to tdq_eval_hosts.py."""
    path = scripts_dir / "tdq_eval_hosts.py"
    ensure_utf8_import(path)
    replace_exact(
        path,
        'SUPPORTED_HOSTS = ("claude", "codex")',
        'SUPPORTED_HOSTS = ("claude", "codex", "antigravity")',
        label="NEW-20 SUPPORTED_HOSTS",
    )
    replace_exact(
        path,
        'KNOWN_EVENT_TYPES = (\n    CLAUDE_EVENT_TYPES | CODEX_EVENT_TYPES | tdq_transcript.UNTIMED_TYPES\n)',
        'AGY_EVENT_TYPES = {"USER_INPUT", "PLANNER_RESPONSE", "SYSTEM", "TOOL_RESPONSE"}\n'
        'KNOWN_EVENT_TYPES = (\n'
        '    CLAUDE_EVENT_TYPES | CODEX_EVENT_TYPES | AGY_EVENT_TYPES | tdq_transcript.UNTIMED_TYPES\n)',
        label="NEW-20 KNOWN_EVENT_TYPES",
    )
    replace_exact(
        path,
        '    if normalized == "codex":\n        return "codex"',
        '    if normalized == "codex":\n        return "codex"\n'
        '    if normalized in ("antigravity", "agy"):\n        return "antigravity"',
        label="NEW-20 canonical_host_name",
    )
    replace_exact(
        path,
        '    raise ValueError("unsupported_host")',
        '    if host == "antigravity":\n'
        '        return ["agy", "agent", "--prompt", prompt]\n'
        '    raise ValueError("unsupported_host")',
        label="NEW-20 build_host_command",
    )


def _patch_test_and_skills_tools(scripts_dir: Path) -> None:
    """NEW-22..NEW-28: Isolate .gemini in tests, accept py -3 in checkstatus, scan AGY skills."""
    tp = scripts_dir / "tdq_test_process.py"
    replace_exact(
        tp,
        '        "CLAUDE_CONFIG_DIR": str(home / ".claude"),',
        '        "CLAUDE_CONFIG_DIR": str(home / ".claude"),\n'
        '        "GEMINI_CONFIG_DIR": str(home / ".gemini"),',
        label="NEW-22 tdq_test_process GEMINI_CONFIG_DIR",
    )
    tr = scripts_dir / "tdq_test_receipt.py"
    replace_exact(
        tr,
        'GENERATED_PREFIXES = ("docs/tdq/", ".claude/worktrees/", "docs/workinglog/", "docs/working-log/")',
        'GENERATED_PREFIXES = ("docs/tdq/", ".claude/worktrees/", ".tdq-worktrees/", "docs/workinglog/", "docs/working-log/")',
        label="NEW-22 tdq_test_receipt GENERATED_PREFIXES",
    )
    cs = scripts_dir / "tdq_checkstatus.py"
    ensure_utf8_import(cs)
    replace_exact(
        cs,
        '    r"^python3 scripts/tdq_state\\.py "',
        '    r"^(?:python3|py -3) scripts/tdq_state\\.py "',
        label="NEW-24 tdq_checkstatus py -3 allow",
    )
    si = scripts_dir / "skill_inventory.py"
    ensure_utf8_import(si)
    replace_exact(
        si,
        '    if not any(enabled.values()):\n        return []',
        '    if not any(enabled.values()):\n        return _agy_plugin_skill_dirs(home, project)',
        label="NEW-27 skill_inventory empty claude fallback",
    )
    replace_exact(
        si,
        'def _plugin_skill_dirs(home, project):',
        'def _agy_plugin_skill_dirs(home, project):\n'
        '    dirs, seen = [], set()\n'
        '    for base in (\n'
        '        os.path.join(home, ".gemini", "config", "plugins"),\n'
        '        os.path.join(project, "plugins"),\n'
        '    ):\n'
        '        if not os.path.isdir(base):\n            continue\n'
        '        for name in sorted(os.listdir(base)):\n'
        '            sdir = os.path.join(base, name, "skills")\n'
        '            if os.path.isdir(sdir) and sdir not in seen:\n'
        '                seen.add(sdir)\n'
        '                dirs.append((name, sdir))\n'
        '    return dirs\n\n\n'
        'def _plugin_skill_dirs(home, project):',
        label="NEW-27 skill_inventory AGY helper",
    )
    replace_exact(
        si,
        '                    break\n    return dirs',
        '                    break\n'
        '    for item in _agy_plugin_skill_dirs(home, project):\n'
        '        if item[1] not in seen:\n'
        '            seen.add(item[1])\n'
        '            dirs.append(item)\n'
        '    return dirs',
        label="NEW-27 skill_inventory merge AGY",
    )

    # Ensure utf8_io across remaining standalone CLI scripts on Windows
    for name in (
        "tdq_graphify.py", "tdq_archify.py", "tdq_vision_diff.py", "tdq_bench.py",
        "tdq_timing.py", "tdq_vungfile.py", "tdq_no.py", "tdq_eval.py",
        "tdq_eval_contract.py", "tdq_skill_eval.py", "tdq_test.py",
        "tdq_checkportable.py", "i18n_check.py", "scan_block_symbols.py",
        "skill_tokens.py", "doc_index.py", "doc_dup.py", "step_audit.py",
    ):
        cand = scripts_dir / name
        if cand.is_file():
            ensure_utf8_import(cand)
    sbs = scripts_dir / "scan_block_symbols.py"
    if sbs.is_file():
        replace_exact(
            sbs,
            '    "portable/workflow/02-spec.md",\n    "portable/workflow/03-plan.md",\n    "portable/workflow/references/user-facing-block.md",\n)',
            '    "portable/workflow/02-spec.md",\n    "portable/workflow/03-plan.md",\n    "portable/workflow/references/user-facing-block.md",\n)\nSCOPE = tuple(p for p in SCOPE if os.path.exists(os.path.join(ROOT, p)))',
            label="scan_block_symbols filter existing SCOPE",
        )


def apply_all(scripts_dir: Path) -> None:
    """Apply all NEW-15 through NEW-28 CLI fixes."""
    _patch_tdq_transcript(scripts_dir)
    _patch_eval_hosts(scripts_dir)
    _patch_test_and_skills_tools(scripts_dir)
    st_path = scripts_dir / "skill_tokens.py"
    if st_path.is_file():
        replace_exact(
            st_path,
            '    try:\n        from anthropic_tokenizer import count_tokens\n        return count_tokens\n    except ImportError as exc:\n        raise ThieuThuVienDem(CAI_DAT) from exc',
            '    try:\n'
            '        from anthropic_tokenizer import count_tokens\n'
            '        return count_tokens\n'
            '    except ImportError:\n'
            '        try:\n'
            '            import tiktoken\n'
            '            _enc = tiktoken.get_encoding("cl100k_base")\n'
            '            return lambda text: len(_enc.encode(text or ""))\n'
            '        except ImportError as exc:\n'
            '            raise ThieuThuVienDem(CAI_DAT) from exc',
            label="skill_tokens tiktoken fallback",
        )
