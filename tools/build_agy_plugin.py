#!/usr/bin/env python3
"""Compile TDQ-Workflow v0.97.0 source into plugins/tdq-workflow/."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patches import agy_hooks, agy_manifests, cli_fixes_a, cli_fixes_b, common_utils, skills_and_agents


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
_EXTERNAL_UPSTREAM = Path(r"C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow")
DEFAULT_UPSTREAM = (
    WORKSPACE_ROOT
    if (WORKSPACE_ROOT / "portable_src").is_dir() and (WORKSPACE_ROOT / "hooks" / "scripts").is_dir()
    else _EXTERNAL_UPSTREAM
)
PLUGIN_OUT = WORKSPACE_ROOT / "plugins" / "tdq-workflow"


def _upstream_sha(upstream: Path) -> str:
    """Read upstream HEAD commit hash cleanly without mutating upstream."""
    kw = {"capture_output": True, "text": True, "encoding": "utf-8", "timeout": 15}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    res = subprocess.run(["git", "-C", str(upstream), "rev-parse", "--short", "HEAD"], **kw)
    return res.stdout.strip() if res.returncode == 0 else "unknown"


def build(upstream: Path = DEFAULT_UPSTREAM, output: Path = PLUGIN_OUT) -> dict:
    """Compile the full standalone Antigravity native plugin and return verification stats."""
    if not (upstream / "scripts").is_dir() or not (upstream / "skills").is_dir():
        raise FileNotFoundError(f"Upstream TDQ-Workflow repo not found at {upstream}")

    sha = _upstream_sha(upstream)
    common_utils.force_writable_rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    # 1. Copy runtime assets cleanly from upstream read-only source
    n_scripts = common_utils.copy_clean_tree(
        upstream / "scripts", output / "scripts", exclude_names=common_utils.EXCLUDED_SCRIPTS
    )
    n_hooks = common_utils.copy_clean_tree(upstream / "hooks" / "scripts", output / "hooks" / "scripts")
    n_skills = common_utils.copy_clean_tree(upstream / "skills", output / "skills")
    cp_skill = upstream / "portable_src" / "skills" / "tdq-checkportable"
    if cp_skill.is_dir():
        n_skills += common_utils.copy_clean_tree(cp_skill, output / "skills" / "tdq-checkportable")
    n_agents = common_utils.copy_clean_tree(upstream / "agents", output / "agents")

    # 2. Apply CLI & host fixes (NEW-01..NEW-28 + hotfix + AGY parsers)
    cli_fixes_a.apply_all(output / "scripts")
    cli_fixes_b.apply_all(output / "scripts")

    # 3. Generate Antigravity native plugin manifests, hooks.json, mcp_config.json, 2-tier rules
    agy_manifests.generate_plugin_json(output)
    agy_manifests.generate_logo_svg(output)
    agy_manifests.generate_hooks_json(output)
    agy_manifests.generate_mcp_config(output)
    agy_manifests.generate_two_tier_rules(output)

    # 4. Translate 12 skills (M01-M20), 6 subagents, and relock token-budget.json
    skills_and_agents.transform_skills(output)
    skills_and_agents.transform_agents(output)
    agy_hooks.apply_all(output / "hooks" / "scripts")
    skills_and_agents.relock_token_budget(output)

    # 5. Emit final manifest.json & README.md
    agy_manifests.generate_manifest_and_readme(output, sha)

    # 6. Immediate AST & Markdown byte-budget checks
    py_count, ast_errors = common_utils.verify_all_py_ast(output)
    if ast_errors:
        raise RuntimeError("Python AST errors:\n" + "\n".join(ast_errors))
    md_count, md_violations = common_utils.check_md_byte_budgets(output)
    if md_violations:
        raise RuntimeError("Markdown byte budget exceeded:\n" + "\n".join(md_violations))

    return {
        "upstream": str(upstream),
        "upstream_sha": sha,
        "output": str(output),
        "copied": {"scripts": n_scripts, "hooks": n_hooks, "skills_files": n_skills, "agents": n_agents},
        "ast_checked_py": py_count,
        "md_checked_budget": md_count,
        "status": "OK",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compile TDQ-Workflow v0.97.0 into Antigravity plugin.")
    ap.add_argument("--upstream", type=Path, default=DEFAULT_UPSTREAM, help="Source TDQ-Workflow directory.")
    ap.add_argument("--output", type=Path, default=PLUGIN_OUT, help="Destination compiled plugin directory.")
    args = ap.parse_args(argv)
    stats = build(upstream=args.upstream, output=args.output)
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
