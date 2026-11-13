"""V1 & V2 Verification: Antigravity strict validator, staged installer, AST, and doc linters."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_DIR = WORKSPACE / "plugins" / "tdq-workflow"
TOOLS_DIR = WORKSPACE / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
from patches import common_utils  # noqa: E402


def _run(cmd, cwd=WORKSPACE):
    kw = {"cwd": str(cwd), "capture_output": True, "text": True, "encoding": "utf-8", "timeout": 60}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return subprocess.run(cmd, **kw)


def test_v1_agy_plugin_validate_strict_json():
    res = _run(["agy.EXE", "plugin", "validate", str(PLUGIN_DIR), "--strict", "--json"])
    assert res.returncode == 0, f"agy validate failed: {res.stdout}\n{res.stderr}"
    data = json.loads(res.stdout)
    assert data["name"] == "tdq-workflow"
    assert data["findings"] == []
    assert data["components"] == {
        "agents": 6,
        "hooks": 6,
        "mcpServers": 3,
        "rules": 10,
        "sidecars": 0,
        "skills": 12,
    }


def test_v1_install_dry_run_and_staged_validate(tmp_path):
    installer = WORKSPACE / "tools" / "install_agy_plugin.py"
    dry = _run([sys.executable, str(installer), "--dry-run", "--target", str(tmp_path / "tdq-workflow")])
    assert dry.returncode == 0
    assert json.loads(dry.stdout)["dry_run"] is True

    staged = tmp_path / "tdq-workflow"
    inst = _run([sys.executable, str(installer), "--target", str(staged), "--sync-local-mcp"])
    assert inst.returncode == 0
    val = _run(["agy.EXE", "plugin", "validate", str(staged), "--strict", "--json"])
    assert val.returncode == 0, val.stdout
    assert json.loads(val.stdout)["findings"] == []


def test_v2_python_ast_and_md_budgets_and_no_traps():
    py_count, ast_errs = common_utils.verify_all_py_ast(PLUGIN_DIR)
    assert py_count >= 80
    assert ast_errs == []

    md_count, md_violations = common_utils.check_md_byte_budgets(PLUGIN_DIR)
    assert md_count == 22
    assert md_violations == []

    pjson = json.loads((PLUGIN_DIR / "plugin.json").read_text(encoding="utf-8"))
    assert "userConfig" not in pjson
    mcp = json.loads((PLUGIN_DIR / "mcp_config.json").read_text(encoding="utf-8"))
    assert "variables" not in mcp
    assert set(mcp["mcpServers"].keys()) == {"lsp", "chrome-devtools", "tavily-primary"}

    tb = _run([sys.executable, "-X", "utf8", "scripts/token_budget.py", "--kiem"], cwd=PLUGIN_DIR)
    assert tb.returncode == 0, tb.stdout + tb.stderr

    for folder in ("skills", "rules", "agents"):
        dl = _run([sys.executable, "-X", "utf8", "scripts/doc_lint.py", folder], cwd=PLUGIN_DIR)
        assert dl.returncode == 0, f"doc_lint failed on {folder}: {dl.stdout}\n{dl.stderr}"
