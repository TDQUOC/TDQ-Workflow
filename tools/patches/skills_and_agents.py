"""Translate all 12 skills (M01-M20), 6 subagents, handoff schema, and relock token budgets."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from .common_utils import read_utf8, write_utf8


# Compact M01-M20 terminology replacements preserving token caps (notably qc.md <= 3500 tokens).
M01_M20_REPLACEMENTS: Tuple[Tuple[str, str], ...] = (
    ("~/.claude/CLAUDE.md", "rules/AGENTS.md"),
    ("${CLAUDE_PLUGIN_ROOT}", "${PLUGIN_ROOT}"),
    ("$CLAUDE_PLUGIN_ROOT", "${PLUGIN_ROOT}"),
    ("CLAUDE.md", "AGENTS.md"),
    ("EnterPlanMode", "enter_plan_mode"),
    ("ExitPlanMode", "exit_plan_mode"),
    ("AskUserQuestion", "ask_question"),
    ("UserPromptSubmit", "PreInvocation"),
    ("SubagentStart", "PreInvocation"),
    ("mcp__lsp__", "mcp_tdq-workflow_lsp_"),
    ("mcp__plugin_tdq-workflow_lsp__", "mcp_tdq-workflow_lsp_"),
    ("mcp__chrome-devtools__", "mcp_tdq-workflow_chrome-devtools_"),
    ("mcp__tavily-primary__", "mcp_tdq-workflow_tavily-primary_"),
)

# Strictly verified Antigravity 2.0 subagent specs (model in {inherit, flash_lite, flash, pro},
# tools as YAML array of real Antigravity tool names).
AGENT_FRONTMATTERS: Dict[str, Dict[str, object]] = {
    "tdq-implementer.md": {
        "name": "tdq-implementer",
        "description": "Implements one assigned task of an approved TDQ plan in an isolated git worktree, red-green, and reports structured handoff data.",
        "tools": ["read_file", "edit_file", "write_file", "run_command", "send_message"],
        "model": "flash",
    },
    "tdq-qc-tester.md": {
        "name": "tdq-qc-tester",
        "description": "Independently verifies an implemented TDQ plan against its Definition of Done - reruns tests, probes edge cases and logging, reports PASS/FAIL with evidence.",
        "tools": ["read_file", "run_command", "send_message"],
        "model": "inherit",
    },
    "tdq-reviewer.md": {
        "name": "tdq-reviewer",
        "description": "Reviews a TDQ spec or plan file for gaps, contradictions, missing tests, and over-engineering. Read-only - reports findings, never edits.",
        "tools": ["read_file", "run_command", "send_message"],
        "model": "inherit",
    },
    "tdq-security-reviewer.md": {
        "name": "tdq-security-reviewer",
        "description": "Independent security auditor checking code changes for OWASP Top 10, hardcoded secrets, injection vulnerabilities, and least-privilege compliance. Read-only.",
        "tools": ["read_file", "run_command", "send_message"],
        "model": "pro",
    },
    "tdq-build-resolver.md": {
        "name": "tdq-build-resolver",
        "description": "Rapid-response subagent fixing compiler errors, build failures, syntax faults, and type check breaks with surgical, minimal diffs.",
        "tools": ["read_file", "edit_file", "write_file", "run_command", "send_message"],
        "model": "flash",
    },
    "tdq-refactor-cleaner.md": {
        "name": "tdq-refactor-cleaner",
        "description": "Code cleaner eliminating dead code, removing duplicates, and enforcing clean code invariants with zero functional regression and deletion audit logs.",
        "tools": ["read_file", "edit_file", "write_file", "run_command", "send_message"],
        "model": "inherit",
    },
}


def _rewrite_skill_text(text: str) -> str:
    """Apply M01-M20 replacements carefully without inflating qc.md above 3,500 tokens."""
    out = text
    for old, new in M01_M20_REPLACEMENTS:
        out = out.replace(old, new)
    # Tool names inside backticks only, avoiding prose corruptions
    tool_subs = (
        ("`Bash`", "`run_command`"),
        ("`Read`", "`read_file`"),
        ("`Edit`", "`edit_file`"),
        ("`Write`", "`write_file`"),
        ("`Grep`", "`grep_search`"),
        ("`Glob`", "`find_by_name`"),
        ("`Task`", "`invoke_subagent`"),
    )
    for old, new in tool_subs:
        out = out.replace(old, new)
    return out


def transform_skills(plugin_root: Path) -> int:
    """Transform all markdown files across the 12 skills and add handoff-schema.json."""
    skills_dir = plugin_root / "skills"
    changed = 0
    for md in sorted(skills_dir.rglob("*.md")):
        raw = read_utf8(md)
        updated = _rewrite_skill_text(raw)
        if updated != raw:
            write_utf8(md, updated)
            changed += 1

    handoff_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "TDQ_HANDOFF_PAYLOAD",
        "type": "object",
        "required": ["task_id", "status", "files", "test_result", "branch", "merge_ready", "tick_ready"],
        "properties": {
            "task_id": {"type": "string"},
            "status": {"type": "string", "enum": ["done", "blocked", "completed", "failed"]},
            "files": {"type": "array", "items": {"type": "string"}},
            "test_result": {"type": "string"},
            "branch": {"type": "string"},
            "merge_ready": {"type": "boolean"},
            "tick_ready": {"type": "boolean"},
            "notes": {"type": "string", "maxLength": 1500},
        },
    }
    schema_path = skills_dir / "tdq-conventions" / "references" / "handoff-schema.json"
    write_utf8(schema_path, json.dumps(handoff_schema, indent=2, ensure_ascii=False) + "\n")
    return changed


def transform_agents(plugin_root: Path) -> int:
    """Rewrite all 6 agents/tdq-*.md to valid Antigravity 2.0 frontmatter & tool names."""
    agents_dir = plugin_root / "agents"
    converted = 0
    for md in sorted(agents_dir.glob("tdq-*.md")):
        meta = AGENT_FRONTMATTERS.get(md.name)
        if not meta:
            continue
        raw = read_utf8(md)
        body = raw
        if raw.startswith("---\n"):
            end = raw.find("\n---\n", 4)
            if end > 0:
                body = raw[end + 5:]
        body = _rewrite_skill_text(body)
        tools_yaml = ", ".join(meta["tools"])  # type: ignore[arg-type]
        fm = (
            "---\n"
            f"name: {meta['name']}\n"
            f"description: {meta['description']}\n"
            f"tools: [{tools_yaml}]\n"
            f"model: {meta['model']}\n"
            "---\n\n"
        )
        # Note explicit read-only guard reminder for reviewers using run_command
        if md.name in ("tdq-reviewer.md", "tdq-security-reviewer.md", "tdq-qc-tester.md"):
            body += "\n> **Host Enforcement:** Write tools are omitted and shell mutations are blocked by TDQ `bash_gate.py` (`[TDQ:READONLY]`).\n"
        write_utf8(md, fm + body.lstrip())
        converted += 1
    return converted


def relock_token_budget(plugin_root: Path) -> int:
    """Run token_budget.py against plugin_root so docs/tdq/token-budget.json is exact."""
    tb_script = plugin_root / "scripts" / "token_budget.py"
    env = dict(os.environ)
    up_venv = Path(r"C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\.venv-tokens\Scripts\python.exe")
    if up_venv.is_file() and "TDQ_TOKENS_VENV" not in env:
        env["TDQ_TOKENS_VENV"] = str(up_venv)
    kw = {"capture_output": True, "text": True, "encoding": "utf-8", "timeout": 60, "env": env}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    res = subprocess.run([sys.executable, "-X", "utf8", str(tb_script), "--goc", str(plugin_root)], **kw)
    if res.returncode != 0:
        raise RuntimeError(f"token_budget.py failed ({res.returncode}): {res.stderr or res.stdout}")
    check = subprocess.run([sys.executable, "-X", "utf8", str(tb_script), "--kiem", "--goc", str(plugin_root)], **kw)
    if check.returncode != 0:
        raise RuntimeError(f"token_budget --kiem failed:\n{check.stdout}\n{check.stderr}")
    return 0
