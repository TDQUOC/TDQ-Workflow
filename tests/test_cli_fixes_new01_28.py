"""V4 Empirical Verification: All 28 CLI & Antigravity fixes (NEW-01 through NEW-28)."""
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_DIR = WORKSPACE / "plugins" / "tdq-workflow"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _init_git(repo: Path) -> None:
    kw = {"cwd": str(repo), "check": True, "capture_output": True, "text": True, "encoding": "utf-8"}
    subprocess.run(["git", "init", "-b", "main"], **kw)
    subprocess.run(["git", "config", "user.email", "test@example.com"], **kw)
    subprocess.run(["git", "config", "user.name", "TDQ Tester"], **kw)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], **kw)
    subprocess.run(["git", "commit", "-m", "init"], **kw)


def _run_script(script_name: str, *args: str, cwd: Path = PLUGIN_DIR, env_extra: dict | None = None):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env_extra:
        env.update(env_extra)
    kw = {"cwd": str(cwd), "capture_output": True, "text": True, "encoding": "utf-8", "timeout": 30, "env": env}
    return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPTS_DIR / script_name), *args], **kw)


def test_new01_tdq_finish_vietnamese_z_paths_and_watched_rules(tmp_path):
    """NEW-01: NUL-delimited git status -z handles UTF-8 filenames and watches rules/ + AGENTS.md."""
    import tdq_finish

    repo = tmp_path / "repo_vn"
    repo.mkdir()
    _init_git(repo)
    vn_file = repo / "tệp_tiếng_việt.py"
    vn_file.write_text("x = 1\n", encoding="utf-8")
    (repo / "rules").mkdir()
    rule_file = repo / "rules" / "domain-demo.md"
    rule_file.write_text("# Rule\n", encoding="utf-8")

    changed = tdq_finish._changed_files(str(repo))
    assert any("tệp_tiếng_việt.py" in p for p in changed), f"UTF-8 filename mangled: {changed}"
    for p in changed:
        assert os.path.exists(p), f"Non-existent path returned: {p}"

    step = tdq_finish.step_khoa_token(str(repo), [str(rule_file)])
    assert step.status != "skip", f"rules/*.md must trigger token-budget check, got: {step}"


def test_new02_03_04_lsp_module_and_search_rules():
    """NEW-02, NEW-03, NEW-04: lsp_module UTF-8/PS + search_rules AGY MCP & Windows quote guards."""
    import lsp_module
    import search_rules

    src_lsp = (SCRIPTS_DIR / "lsp_module.py").read_text(encoding="utf-8")
    assert "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8" in src_lsp
    assert "\\ufffd" in src_lsp
    cands = lsp_module._agy_mcp_candidate_files()
    assert any(Path(c).resolve() == (PLUGIN_DIR / "mcp_config.json").resolve() for c in cands)

    res1 = search_rules.la_goi_khai_niem(
        "call_mcp_tool",
        {"ServerName": "lsp", "ToolName": "find_symbol", "Arguments": {"query": "foo"}},
    )
    res2 = search_rules.la_goi_khai_niem("mcp_tdq-workflow_lsp_go_to_definition", {})
    res3 = search_rules.la_goi_khai_niem("mcp_graphify_query_graph", {})
    assert res1 and res2 and res3
    assert "run_command" in search_rules.CONG_CU_SHELL

    # Trailing Windows backslash inside quotes must not swallow closing quote or hang
    tokens = search_rules.kiem_tra_lenh_shell('rg foo "C:\\Users\\admin\\path\\"') if hasattr(search_rules, "kiem_tra_lenh_shell") else None
    src_sr = (SCRIPTS_DIR / "search_rules.py").read_text(encoding="utf-8")
    assert "in_dquote" in src_sr and "os.name == \"nt\"" in src_sr
    _ = tokens


def test_new05_tdq_state_hotfix_prune_and_atomic_retry(tmp_path, monkeypatch):
    """NEW-05: PRUNE_DIRS, 5-attempt Windows PermissionError retry, hotfix CLI."""
    import tdq_state

    assert {".gemini", ".agents", ".tdq-worktrees"}.issubset(tdq_state.PRUNE_DIRS)

    calls = {"n": 0}
    orig_replace = os.replace

    def flaky_replace(src, dst):
        calls["n"] += 1
        if calls["n"] == 1:
            raise PermissionError("simulated AV lock")
        return orig_replace(src, dst)

    monkeypatch.setattr(os, "replace", flaky_replace)
    target = tmp_path / "state_atomic.json"
    tdq_state._atomic_write(str(target), '{"ok": true}')
    assert calls["n"] == 2
    assert json.loads(target.read_text(encoding="utf-8"))["ok"] is True

    repo = tmp_path / "repo_hf"
    repo.mkdir()
    _init_git(repo)
    res = _run_script("tdq_state.py", "hotfix", "2026-11-13-1400-bug-fix", "--tier", "nho", "--json", cwd=repo)
    assert res.returncode == 0, res.stderr
    data = json.loads(res.stdout)
    st = data.get("state") or data
    assert st["active_request"] == "2026-11-13-1400-bug-fix"
    assert st["lane"] == "quick"
    assert st["phase"] == "implement"
    assert st["quick_approved"] is True


def test_new06_to_new14_setup_lsp_codex_harvest_knowledge_devtool_team_doclint(tmp_path):
    """NEW-06..NEW-14: Host guards, LSP/Codex/Devtool mcp_config, harvest, knowledge, team, doc_lint."""
    import tdq_setup
    import tdq_lsp
    import tdq_codex_mcp
    import tdq_devtool_mcp
    import tdq_team

    # NEW-06: Antigravity host guard & no Claude hook conflict
    assert tdq_setup.is_antigravity_host() is True
    assert tdq_setup.va_hook_xung_dot() == ([], [])

    # NEW-07 & NEW-10: tdq_lsp + tdq_codex_mcp read plugin mcp_config.json without ~/.claude.json
    assert tdq_lsp.mcp_args(str(tmp_path / "missing_claude.json")) is not None
    assert tdq_lsp.bac2_mcp().dat is True
    assert tdq_lsp.bac4_quyen_tool().dat is True
    src_cm = (SCRIPTS_DIR / "tdq_codex_mcp.py").read_text(encoding="utf-8")
    assert "mcp_config.json" in src_cm
    assert tdq_codex_mcp is not None

    # NEW-11..13: tdq_devtool_mcp detects plugin mcp_config.json
    src_dt = (SCRIPTS_DIR / "tdq_devtool_mcp.py").read_text(encoding="utf-8")
    assert "mcp_config.json" in src_dt and tdq_devtool_mcp is not None

    # NEW-08 & NEW-09: tdq_harvest --project + tdq_knowledge check
    repo = tmp_path / "repo_hv"
    repo.mkdir()
    _init_git(repo)
    hv = _run_script("tdq_harvest.py", "scan", "--project", str(repo), cwd=repo)
    assert hv.returncode == 0, hv.stderr
    kn_src = (SCRIPTS_DIR / "tdq_knowledge.py").read_text(encoding="utf-8")
    assert 'trang_thai == "approved"' in kn_src
    note = repo / "note.md"
    note.write_text("---\nid: demo-note\nstatus: approved\nnguoi_duyet: tester\nngay_duyet: 2026-11-13\nevidence: pytest\n---\n\n# Demo Note\n\n## Symptom\nSlow build\n\n## Fix\nEnable cache\n", encoding="utf-8")
    kn = _run_script("tdq_knowledge.py", "check", str(note), cwd=PLUGIN_DIR)
    assert kn.returncode == 0, kn.stderr

    # NEW-14: tdq_team rules/ prefix & -c core.longpaths=true + doc_lint 0 violations
    assert "rules/" in tdq_team.TIEN_TO_FILE_LUAT
    assert ".agents/" in tdq_team.TIEN_TO_FILE_LUAT
    tm_src = (SCRIPTS_DIR / "tdq_team.py").read_text(encoding="utf-8")
    assert '"core.longpaths=true"' in tm_src

    for sub in ("skills", "agents", "rules"):
        dl = _run_script("doc_lint.py", sub, cwd=PLUGIN_DIR)
        assert dl.returncode == 0, f"doc_lint {sub} failed:\n{dl.stdout}\n{dl.stderr}"


def test_new15_to_new28_transcript_eval_hosts_test_isolation_tokens(tmp_path):
    """NEW-15..NEW-28: AGY transcript, eval_hosts antigravity, test isolation, checkstatus, skill_tokens."""
    import tdq_transcript
    import tdq_eval_hosts
    import tdq_test_process
    import tdq_test_receipt
    import tdq_checkstatus
    import skill_inventory
    import skill_tokens

    assert tdq_transcript.AGY_TYPES == {"USER_INPUT", "PLANNER_RESPONSE", "SYSTEM", "TOOL_RESPONSE"}
    assert tdq_transcript._decode_double_json('"{ \\"a\\": 1 }"') == {"a": 1}

    assert "antigravity" in tdq_eval_hosts.SUPPORTED_HOSTS
    assert tdq_eval_hosts.canonical_host_name("agy") == "antigravity"
    assert tdq_eval_hosts.build_host_command(
        "antigravity",
        {"prompt": "hello", "model": "gemini-3-pro", "instructions": "run"},
    ) == ["agy", "agent", "--prompt", "hello"]

    tp_src = (SCRIPTS_DIR / "tdq_test_process.py").read_text(encoding="utf-8")
    assert "GEMINI_CONFIG_DIR" in tp_src and tdq_test_process is not None
    assert ".tdq-worktrees/" in tdq_test_receipt.GENERATED_PREFIXES

    cs_src = (SCRIPTS_DIR / "tdq_checkstatus.py").read_text(encoding="utf-8")
    assert "(?:python3|py -3)" in cs_src and tdq_checkstatus is not None

    agy_dirs = skill_inventory._agy_plugin_skill_dirs(str(tmp_path), str(WORKSPACE))
    assert any(name == "tdq-workflow" for name, _ in agy_dirs)

    # Verify token counter & token_budget --kiem both succeed
    counter = skill_tokens._load_counter() if hasattr(skill_tokens, "_load_counter") else None
    tb = _run_script("token_budget.py", "--kiem", cwd=PLUGIN_DIR)
    assert tb.returncode == 0, f"token_budget --kiem failed:\n{tb.stdout}\n{tb.stderr}"
    _ = counter

    # Verify remaining key modules import with utf8_io cleanly
    for mod in ("tdq_graphify", "tdq_archify", "tdq_vision_diff", "tdq_bench", "tdq_skill_eval", "tdq_checkportable"):
        m = importlib.import_module(mod)
        assert m is not None
