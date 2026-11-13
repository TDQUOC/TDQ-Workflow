"""V5 & V6 Empirical Verification: Live MCP stdio JSON-RPC, 7 companion extensions, & full 10-step E2E pipeline."""
import datetime
import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_DIR = WORKSPACE / "plugins" / "tdq-workflow"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
HOOKS_DIR = PLUGIN_DIR / "hooks" / "scripts"


def _run_py(script_path: Path, *args: str, cwd: Path, env_extra: dict | None = None, stdin_text: str | None = None):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env_extra:
        env.update(env_extra)
    kw = {
        "cwd": str(cwd),
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "timeout": 45,
        "env": env,
    }
    if stdin_text is not None:
        kw["input"] = stdin_text
    return subprocess.run([sys.executable, "-X", "utf8", str(script_path), *args], **kw)


def _git(repo: Path, *args: str, check: bool = True):
    return subprocess.run(
        ["git", "-c", "core.longpaths=true", *args],
        cwd=str(repo),
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_v5_live_mcp_agent_lsp_stdio_and_7_companion_extensions():
    """V5: Live stdio JSON-RPC handshake on agent-lsp + checks across all 7 companion extensions."""
    mcp_cfg = json.loads((PLUGIN_DIR / "mcp_config.json").read_text(encoding="utf-8"))
    servers = mcp_cfg["mcpServers"]
    assert {"lsp", "chrome-devtools", "tavily-primary"}.issubset(servers.keys())

    # 1. Agent-LSP MCP live stdio JSON-RPC initialize + tools/list
    lsp = servers["lsp"]
    assert Path(lsp["command"]).is_file(), f"Missing agent-lsp binary: {lsp['command']}"
    kw = {"stdin": subprocess.PIPE, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    proc = subprocess.Popen([lsp["command"], *lsp["args"]], **kw)
    lines: list[str] = []

    def _read():
        for _ in range(16):
            raw = proc.stdout.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if line:
                lines.append(line)
                if '"id":2' in line or '"id": 2' in line:
                    break

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    req = (
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "tdq-v5", "version": "1.0"}}}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n"
    )
    proc.stdin.write(req.encode("utf-8"))
    proc.stdin.flush()
    t.join(8)
    proc.terminate()
    proc.wait(5)

    parsed = [json.loads(l) for l in lines]
    tools_resp = next((r for r in parsed if r.get("id") == 2), None)
    assert tools_resp is not None, f"No tools/list response from agent-lsp: {lines}"
    tools = tools_resp["result"]["tools"]
    tool_names = {t_obj["name"] for t_obj in tools}
    assert len(tools) >= 20
    assert {"start_lsp", "open_document", "find_references", "blast_radius"}.issubset(tool_names)

    # 2 & 3. Chrome DevTools MCP + Tavily MCP config & npx host availability
    assert shutil.which("npx") is not None or shutil.which("npx.cmd") is not None
    assert "chrome-devtools-mcp" in " ".join(servers["chrome-devtools"]["args"])
    assert "tavily-mcp" in " ".join(servers["tavily-primary"]["args"])
    assert "variables" not in mcp_cfg

    # 4. Archify Visual BA engine check (--kiem-archify)
    arch = _run_py(SCRIPTS_DIR / "tdq_setup.py", "--kiem-archify", cwd=PLUGIN_DIR)
    assert arch.returncode == 0, arch.stderr

    # 5. Graphify AST engine check
    gf = _run_py(SCRIPTS_DIR / "tdq_graphify.py", "--help", cwd=PLUGIN_DIR)
    assert gf.returncode == 0, gf.stderr

    # 6. Vision Diff engine check
    vd = _run_py(SCRIPTS_DIR / "tdq_vision_diff.py", "--help", cwd=PLUGIN_DIR)
    assert vd.returncode == 0, vd.stderr

    # 7. Codex CLI availability
    codex_bin = shutil.which("codex") or shutil.which("codex.cmd")
    assert codex_bin is not None, "codex CLI not found on PATH"
    cx = subprocess.run([codex_bin, "--version"], capture_output=True, text=True, encoding="utf-8", timeout=15)
    assert cx.returncode == 0, cx.stderr


def test_v6_full_10_step_e2e_pipeline(tmp_path):
    """V6: Execute full 10-step TDQ workflow inside an isolated repo strictly via plugins/tdq-workflow."""
    repo = tmp_path / "calc_app"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir(parents=True)
    (repo / "src" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pyproject.toml").write_text('[tool.pytest.ini_options]\npythonpath = ["."]\n', encoding="utf-8")
    (repo / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    (repo / "tests" / "test_calc.py").write_text(
        "from src.calc import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "e2e@example.com")
    _git(repo, "config", "user.name", "TDQ E2E")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "chore: initial calc repo")

    slug = "2026-11-13-1500-calc-demo"
    env_p = {"TDQ_PROJECT_DIR": str(repo)}

    # Step 1: init full/deep request
    r1 = _run_py(SCRIPTS_DIR / "tdq_state.py", "init", slug, "deep", "--bo-qua-lsp", "e2e test", cwd=repo, env_extra=env_p)
    assert r1.returncode == 0, r1.stderr

    # Step 2: write spec & approve spec (conforming to doc_lint R8/R10/R11/R12)
    spec_rel = f"docs/tdq/spec/{slug}.md"
    spec_path = repo / spec_rel
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(
        f"# Đặc tả: {slug} · Lane: full\n\n"
        "## 1. Mục tiêu\n"
        "Sửa hàm `add(a, b)` trong `src/calc.py` để trả về tổng `a + b` chính xác.\n\n"
        "## 2b. Ranh giới module\n"
        "- Module `src/calc.py`: phép cộng số học độc lập.\n\n"
        "## 3b. Năng lực & công cụ\n"
        "| Tên | Loại | Quyết định | Lý do |\n"
        "| --- | --- | --- | --- |\n"
        "| tdq-build | skill | NỀN | Luồng chuẩn TDQ |\n\n"
        "## 6. Tiêu chí nghiệm thu\n"
        "| Mã | Mô tả | Điều kiện PASS |\n"
        "| --- | --- | --- |\n"
        "| Q1 | Phép cộng đúng | Hàm `add(2, 3)` trả về đúng giá trị tổng |\n",
        encoding="utf-8",
    )
    _run_py(SCRIPTS_DIR / "tdq_state.py", "set", f"spec_file={spec_rel}", cwd=repo, env_extra=env_p)
    r2 = _run_py(SCRIPTS_DIR / "tdq_state.py", "approve", "spec", "--by", "approve spec", "--bo-qua-archify", "e2e cli", cwd=repo, env_extra=env_p)
    assert r2.returncode == 0, r2.stderr

    # Step 3: write plan + doc_lint --pair + approve plan --mode subagent
    plan_rel = f"docs/tdq/plan/{slug}.md"
    plan_path = repo / plan_rel
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_text = (
        f"# Kế hoạch: {slug}\n\n"
        "## Cụm song song\n"
        "Một cụm duy nhất vì chỉ sửa module `src/calc.py`.\n\n"
        "## P1 — Sửa phép cộng\n"
        "- [ ] **T1.1** (n1 e5m): Sửa hàm `add(a, b)` trong `src/calc.py` — Test: `pytest tests/test_calc.py`\n"
        "  - Chạm: src/calc.py, tests/test_calc.py\n"
        "  - Logic: đổi `return a - b` thành `return a + b` (pseudo-code: `return a + b`).\n\n"
        "## Definition of Done\n"
        "- [ ] DoD-1 (Q1): `pytest tests/test_calc.py` chạy xanh hoàn toàn.\n"
    )
    plan_path.write_text(plan_text, encoding="utf-8")
    _run_py(SCRIPTS_DIR / "tdq_state.py", "set", f"plan_file={plan_rel}", cwd=repo, env_extra=env_p)

    pair_lint = _run_py(SCRIPTS_DIR / "doc_lint.py", "--pair", spec_rel, plan_rel, cwd=repo, env_extra=env_p)
    assert pair_lint.returncode == 0, pair_lint.stdout + pair_lint.stderr

    r3 = _run_py(
        SCRIPTS_DIR / "tdq_state.py", "approve", "plan", "--mode", "subagent",
        "--by", "approve plan, use subagent", "--bo-qua-archify", "e2e cli", cwd=repo, env_extra=env_p,
    )
    assert r3.returncode == 0, r3.stderr
    r3_phase = _run_py(SCRIPTS_DIR / "tdq_state.py", "set", "phase=implement", cwd=repo, env_extra=env_p)
    assert r3_phase.returncode == 0, r3_phase.stderr

    # Commit spec/plan baseline cleanly before branching worktree
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "docs: add approved spec and plan")

    # Step 4: tdq_team assign -> audit -> wave -> open T1.1
    assert _run_py(SCRIPTS_DIR / "tdq_team.py", "assign", cwd=repo, env_extra=env_p).returncode == 0
    assert _run_py(SCRIPTS_DIR / "tdq_team.py", "audit", cwd=repo, env_extra=env_p).returncode == 0
    assert _run_py(SCRIPTS_DIR / "tdq_team.py", "wave", cwd=repo, env_extra=env_p).returncode == 0
    open_res = _run_py(SCRIPTS_DIR / "tdq_team.py", "open", "T1.1", cwd=repo, env_extra=env_p)
    assert open_res.returncode == 0, open_res.stdout + open_res.stderr

    wt = repo / ".tdq-worktrees" / slug / "t1.1"
    assert wt.is_dir(), f"Expected worktree at {wt}"

    # Step 5: RED test fails -> GREEN fix -> test passes -> commit in worktree
    red = subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_calc.py"], cwd=str(wt), capture_output=True, text=True)
    assert red.returncode != 0, "Expected RED failing test before fix"

    (wt / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    green = subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_calc.py"], cwd=str(wt), capture_output=True, text=True)
    assert green.returncode == 0, green.stdout + green.stderr
    _git(wt, "add", "src/calc.py")
    _git(wt, "commit", "-m", "fix: implement addition in add")

    # Step 6: Hook enforcement check (out-of-zone write in worktree blocked [TDQ:VUNG]) + check -> merge -> clean
    eg = _run_py(
        HOOKS_DIR / "edit_gate.py",
        "--event", "PreToolUse",
        cwd=repo,
        env_extra=env_p,
        stdin_text=json.dumps({
            "cwd": str(repo),
            "conversation_id": "conv-e2e",
            "tool_name": "edit_file",
            "tool_input": {"TargetFile": str(wt / "src" / "secret_extra.py")},
        }),
    )
    assert eg.returncode == 0
    eg_out = json.loads(eg.stdout.strip())
    assert eg_out["decision"] == "deny" and "TDQ:" in eg_out["reason"]

    assert _run_py(SCRIPTS_DIR / "tdq_team.py", "check", "T1.1", cwd=repo, env_extra=env_p).returncode == 0
    assert _run_py(SCRIPTS_DIR / "tdq_team.py", "merge", "T1.1", cwd=repo, env_extra=env_p).returncode == 0
    # Bring integration branch commits onto main before cleaning worktrees
    _git(repo, "merge", "--ff-only", f"tdq/{slug}/tich-hop")
    assert _run_py(SCRIPTS_DIR / "tdq_team.py", "clean", cwd=repo, env_extra=env_p).returncode == 0
    assert (repo / "src" / "calc.py").read_text(encoding="utf-8").strip().endswith("return a + b")

    # Step 7: Tick plan [x] & run QC suite
    plan_path.write_text(
        plan_text.replace("- [ ] **T1.1**", "- [x] **T1.1**").replace("- [ ] DoD-1", "- [x] DoD-1"),
        encoding="utf-8",
    )
    assert _run_py(SCRIPTS_DIR / "tdq_state.py", "set", "phase=qc", cwd=repo, env_extra=env_p).returncode == 0
    qc_run = subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_calc.py"], cwd=str(repo), capture_output=True, text=True)
    assert qc_run.returncode == 0

    # Step 8: Report phase + 4-section report + tdq_harvest scan + tdq_knowledge check
    assert _run_py(SCRIPTS_DIR / "tdq_state.py", "set", "phase=report", cwd=repo, env_extra=env_p).returncode == 0
    rep_path = repo / "docs" / "tdq" / "reports" / f"{slug}.md"
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    rep_path.write_text(
        f"# Report: {slug}\n\n"
        "## Before request\n`add(a, b)` returned `a - b`.\n\n"
        "## After request\n`add(a, b)` returns `a + b` via worktree `t1.1`.\n\n"
        "## What was tested\n`pytest tests/test_calc.py` (RED -> GREEN).\n\n"
        "## Test result\nPASS (1/1 passed).\n",
        encoding="utf-8",
    )
    assert _run_py(SCRIPTS_DIR / "tdq_harvest.py", "scan", "--project", str(repo), cwd=repo, env_extra=env_p).returncode == 0
    note = repo / "docs" / "tdq" / "knowledge-demo.md"
    note.write_text("---\nid: e2e-demo\nstatus: approved\nnguoi_duyet: tester\nngay_duyet: 2026-11-13\nevidence: pytest\n---\n# Note\nPASS\n", encoding="utf-8")
    assert _run_py(SCRIPTS_DIR / "tdq_knowledge.py", "check", str(note), cwd=repo).returncode == 0

    # Step 9: Finish steps (in phase=report) -> append working log + tdq_finish
    today = datetime.date.today().isoformat()
    wl = repo / "docs" / "workinglog" / f"{today}.md"
    wl.parent.mkdir(parents=True, exist_ok=True)
    wl.write_text(f"## 15:10 — {slug}\nImplemented add(a,b)=a+b and verified pytest PASS.\n", encoding="utf-8")
    fin = _run_py(SCRIPTS_DIR / "tdq_finish.py", "--files", "src/calc.py", "--log", "Completed calc-demo", cwd=repo, env_extra=env_p)
    assert fin.returncode == 0, fin.stdout + fin.stderr

    # Step 10: Close to idle & confirm clean worktree registry
    assert _run_py(SCRIPTS_DIR / "tdq_state.py", "set", "phase=idle", cwd=repo, env_extra=env_p).returncode == 0
    final_st = _run_py(SCRIPTS_DIR / "tdq_state.py", "get", cwd=repo, env_extra=env_p)
    assert final_st.returncode == 0
    assert json.loads(final_st.stdout).get("phase") == "idle"
    wt_dir = repo / ".tdq" / "worktrees"
    assert not wt_dir.exists() or not any(wt_dir.iterdir())
