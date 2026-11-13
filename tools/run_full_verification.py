#!/usr/bin/env python3
"""Run empirical verification across V1-V6 and emit docs/verification_evidence.json."""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_DIR = WORKSPACE / "plugins" / "tdq-workflow"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
HOOKS_DIR = PLUGIN_DIR / "hooks" / "scripts"
UPSTREAM_REPO = Path(r"C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow")
TOOLS_DIR = WORKSPACE / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))


def _find_agy() -> str:
    found = shutil.which("agy.EXE") or shutil.which("agy")
    if found:
        return found
    cand = Path(os.path.expanduser("~")) / "AppData" / "Local" / "Programs" / "Antigravity" / "bin" / "agy.EXE"
    return str(cand)


def _run(cmd, cwd=WORKSPACE, timeout=90):
    t0 = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
    return {
        "cmd": cmd if isinstance(cmd, str) else " ".join(str(x) for x in cmd),
        "returncode": p.returncode,
        "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def _probe_agent_lsp(mcp_cfg: dict) -> dict:
    lsp = mcp_cfg["mcpServers"]["lsp"]
    t0 = time.perf_counter()
    kw = {"stdin": subprocess.PIPE, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    proc = subprocess.Popen([lsp["command"], *lsp["args"]], **kw)
    lines = []

    def _read():
        for _ in range(16):
            raw = proc.stdout.readline()
            if not raw:
                break
            s = raw.decode("utf-8", errors="replace").strip()
            if s:
                lines.append(s)
                if '"id":2' in s or '"id": 2' in s:
                    break

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    reqs = (
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "tdq-evidence", "version": "1.0"}}}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n"
    )
    proc.stdin.write(reqs.encode("utf-8"))
    proc.stdin.flush()
    t.join(8)
    proc.terminate()
    proc.wait(5)
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    parsed = [json.loads(l) for l in lines]
    init_res = next((r.get("result", {}) for r in parsed if r.get("id") == 1), {})
    tools_res = next((r.get("result", {}) for r in parsed if r.get("id") == 2), {})
    tools = [t_obj["name"] for t_obj in tools_res.get("tools", [])]
    return {
        "binary": lsp["command"],
        "binary_exists": Path(lsp["command"]).is_file(),
        "latency_ms": latency_ms,
        "instructions": init_res.get("instructions", ""),
        "tools_count": len(tools),
        "tools": sorted(tools),
    }


def _collect_inventory() -> dict:
    from patches.common_utils import EXCLUDED_SCRIPTS
    import _common

    rules = []
    for p in sorted((PLUGIN_DIR / "rules").glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"^trigger:\s*(.+)$", txt, re.MULTILINE)
        rules.append({"file": p.name, "bytes": len(txt.encode("utf-8")), "trigger": m.group(1).strip() if m else "always_on"})

    skills = []
    total_skill_files = 0
    for d in sorted((PLUGIN_DIR / "skills").iterdir()):
        if not d.is_dir():
            continue
        files = [f for f in d.rglob("*") if f.is_file()]
        total_skill_files += len(files)
        sk = d / "SKILL.md"
        skills.append({
            "name": d.name,
            "files_count": len(files),
            "skill_md_bytes": len(sk.read_bytes()) if sk.is_file() else 0,
        })

    agents = []
    for p in sorted((PLUGIN_DIR / "agents").glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        m_mod = re.search(r"^model:\s*(.+)$", txt, re.MULTILINE)
        m_tls = re.search(r"^tools:\s*(.+)$", txt, re.MULTILINE)
        agents.append({
            "file": p.name,
            "bytes": len(txt.encode("utf-8")),
            "model": m_mod.group(1).strip() if m_mod else "",
            "tools": m_tls.group(1).strip() if m_tls else "",
        })

    hooks_json = json.loads((PLUGIN_DIR / "hooks.json").read_text(encoding="utf-8"))
    hooks_events = []
    for grp in hooks_json.values():
        if isinstance(grp, dict):
            for k in grp:
                if k != "enabled" and k not in hooks_events:
                    hooks_events.append(k)
    hook_py_files = sorted(p.name for p in HOOKS_DIR.glob("*.py"))
    script_py_files = sorted(p.name for p in SCRIPTS_DIR.glob("*.py"))
    script_other_files = sorted(str(p.relative_to(SCRIPTS_DIR)).replace("\\", "/") for p in SCRIPTS_DIR.rglob("*") if p.is_file() and p.suffix != ".py")

    return {
        "rules_count": len(rules),
        "rules": rules,
        "skills_count": len(skills),
        "skills_total_files": total_skill_files,
        "skills": skills,
        "agents_count": len(agents),
        "agents": agents,
        "hooks_events": hooks_events,
        "hook_py_count": len(hook_py_files),
        "hook_py_files": hook_py_files,
        "tdq_codes_count": len(_common.CODES),
        "tdq_codes": list(_common.CODES),
        "scripts_count": len(script_py_files),
        "scripts": script_py_files,
        "scripts_other_files": script_other_files,
        "excluded_scripts_count": len(EXCLUDED_SCRIPTS),
        "excluded_scripts": sorted(EXCLUDED_SCRIPTS),
    }


def main() -> int:
    agy = _find_agy()
    mcp_cfg = json.loads((PLUGIN_DIR / "mcp_config.json").read_text(encoding="utf-8"))

    # 1. Build check
    build_res = _run([sys.executable, "-B", "tools/build_agy_plugin.py"])
    build_json = json.loads(build_res["stdout"]) if build_res["returncode"] == 0 else {}

    # 2. Validator & staged install
    val_res = _run([agy, "plugin", "validate", str(PLUGIN_DIR), "--strict", "--json"])
    val_json = json.loads(val_res["stdout"]) if val_res["stdout"].startswith("{") else {}

    dry_res = _run([sys.executable, "-B", "tools/install_agy_plugin.py", "--dry-run"])
    with tempfile.TemporaryDirectory() as tmpdir:
        inst_res = _run([sys.executable, "-B", "tools/install_agy_plugin.py", "--target", tmpdir])
        staged_val = _run([agy, "plugin", "validate", str(tmpdir), "--strict", "--json"])

    # 3. Full Antigravity pytest suite (14 gates)
    agy_test_files = [
        "tests/test_agy_plugin_validate.py",
        "tests/test_cli_fixes_new01_28.py",
        "tests/test_e2e_workflow.py",
        "tests/test_hooks_dual_protocol.py",
        "tests/test_ntfs_concurrency.py",
    ]
    pt_res = _run([sys.executable, "-m", "pytest", *agy_test_files, "-v", "--basetemp=.pytest_tmp"], timeout=120)
    pt_cases = []
    for line in pt_res["stdout"].splitlines():
        m = re.match(r"^(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED)", line.strip())
        if m:
            pt_cases.append({"nodeid": m.group(1), "status": m.group(2)})

    # 4. Linters
    linters = {
        "doc_lint_skills": _run([sys.executable, "-X", "utf8", "scripts/doc_lint.py", "skills"], cwd=PLUGIN_DIR),
        "doc_lint_agents": _run([sys.executable, "-X", "utf8", "scripts/doc_lint.py", "agents"], cwd=PLUGIN_DIR),
        "doc_lint_rules": _run([sys.executable, "-X", "utf8", "scripts/doc_lint.py", "rules"], cwd=PLUGIN_DIR),
        "token_budget_kiem": _run([sys.executable, "-X", "utf8", "scripts/token_budget.py", "--kiem"], cwd=PLUGIN_DIR),
        "scan_block_symbols": _run([sys.executable, "-X", "utf8", "scripts/scan_block_symbols.py", "--chi-khoi"], cwd=PLUGIN_DIR),
        "i18n_new_hooks": _run([
            sys.executable, "-X", "utf8", "scripts/i18n_check.py",
            "hooks/scripts/_common.py", "hooks/scripts/post_invocation.py", "hooks/scripts/subagent_dispatch_gate.py",
        ], cwd=PLUGIN_DIR),
    }

    # 5. Live MCP + 7 companion extensions
    codex_bin = shutil.which("codex") or shutil.which("codex.cmd") or "codex"
    npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
    extensions = {
        "agent_lsp_mcp": _probe_agent_lsp(mcp_cfg),
        "chrome_devtools_mcp": {
            "configured": "chrome-devtools" in mcp_cfg["mcpServers"],
            "args": mcp_cfg["mcpServers"]["chrome-devtools"]["args"],
            "npx_version": _run([npx_bin, "--version"]),
        },
        "tavily_mcp": {
            "configured": "tavily-primary" in mcp_cfg["mcpServers"],
            "args": mcp_cfg["mcpServers"]["tavily-primary"]["args"],
            "no_variables_trap": "variables" not in mcp_cfg,
        },
        "archify_visual_ba": _run([sys.executable, "-X", "utf8", "scripts/tdq_setup.py", "--kiem-archify"], cwd=PLUGIN_DIR),
        "graphify_ast": {
            "tdq_graphify": _run([sys.executable, "-X", "utf8", "scripts/tdq_graphify.py", "--help"], cwd=PLUGIN_DIR),
            "graphify_cli": _run(["graphify", "--help"]) if shutil.which("graphify") else {"returncode": -1, "stdout": "not on PATH"},
        },
        "vision_diff": _run([sys.executable, "-X", "utf8", "scripts/tdq_vision_diff.py", "--help"], cwd=PLUGIN_DIR),
        "codex_cli": _run([codex_bin, "--version"]),
    }

    # 6. Safety & isolation checks (zero mutations to upstream & global AGY config)
    up_head = _run(["git", "-C", str(UPSTREAM_REPO), "rev-parse", "--short", "HEAD"])
    up_status = _run(["git", "-C", str(UPSTREAM_REPO), "status", "--short"])
    up_code_status = _run(["git", "-C", str(UPSTREAM_REPO), "status", "--short", "--", "plugins/", ".claude-plugin/", "scripts/", "hooks/", "tools/"])
    global_cfg = Path(os.path.expanduser("~/.gemini/config/config.json"))
    global_cfg_hash = hashlib.sha256(global_cfg.read_bytes()).hexdigest() if global_cfg.is_file() else None
    ws_plugins_json = json.loads((WORKSPACE / ".agents" / "plugins.json").read_text(encoding="utf-8"))

    evidence = {
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "plugin_dir": str(PLUGIN_DIR),
        "build": build_json,
        "agy_validate": {
            "strict_json": val_json,
            "returncode": val_res["returncode"],
            "install_dry_run_rc": dry_res["returncode"],
            "install_staged_rc": inst_res["returncode"],
            "staged_validate_json": json.loads(staged_val["stdout"]) if staged_val["stdout"].startswith("{") else {},
        },
        "pytest": {
            "returncode": pt_res["returncode"],
            "duration_ms": pt_res["duration_ms"],
            "total": len(pt_cases),
            "passed": sum(1 for c in pt_cases if c["status"] == "PASSED"),
            "failed": sum(1 for c in pt_cases if c["status"] == "FAILED"),
            "cases": pt_cases,
        },
        "linters": linters,
        "extensions": extensions,
        "inventory": _collect_inventory(),
        "safety_isolation": {
            "upstream_repo": str(UPSTREAM_REPO),
            "upstream_head_sha": up_head["stdout"],
            "upstream_git_status_short": up_status["stdout"],
            "upstream_code_clean": up_head["returncode"] == 0 and up_code_status["stdout"] == "",
            "upstream_clean": up_head["returncode"] == 0 and up_status["stdout"] == "",
            "global_config_exists": global_cfg.is_file(),
            "global_config_sha256": global_cfg_hash,
            "workspace_agents_plugins_json": ws_plugins_json,
        },
    }

    out_path = WORKSPACE / "docs" / "verification_evidence.json"
    out_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "evidence_path": str(out_path),
        "pytest_passed": f"{evidence['pytest']['passed']}/{evidence['pytest']['total']}",
        "agy_validate_findings": len(evidence["agy_validate"]["strict_json"].get("findings", [])),
        "agent_lsp_tools": evidence["extensions"]["agent_lsp_mcp"]["tools_count"],
        "upstream_clean": evidence["safety_isolation"]["upstream_clean"],
    }, indent=2))
    return 0 if evidence["pytest"]["failed"] == 0 and val_res["returncode"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
