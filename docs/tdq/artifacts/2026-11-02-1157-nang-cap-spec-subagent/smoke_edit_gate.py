"""QC smoke: real edit_gate.py process, temp project, payload shaped like Claude Code docs. 120 s cap."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
GATE = os.path.join(ROOT, "hooks", "scripts", "edit_gate.py")
STATE = os.path.join(ROOT, "scripts", "tdq_state.py")

with tempfile.TemporaryDirectory() as d:
    env = dict(os.environ, TDQ_PROJECT_DIR=d)
    os.makedirs(os.path.join(d, "docs", "tdq"))
    run = lambda *a: subprocess.run([sys.executable, STATE, *a], env=env, capture_output=True, text=True, timeout=120)
    run("init", "2026-11-02-0000-smoke", "full", "--bo-qua-lsp", "smoke qc")
    run("set", "phase=spec")

    def gate(rel, agent):
        p = {"cwd": d, "session_id": "smk", "hook_event_name": "PreToolUse", "tool_name": "Edit",
             "tool_input": {"file_path": os.path.join(d, rel)}}
        if agent:
            p.update(agent_id="agent-x", agent_type="Explore")
        out = subprocess.run([sys.executable, GATE], input=json.dumps(p), env=env,
                             capture_output=True, text=True, timeout=120).stdout
        return "deny" in out, "TDQ:TEAM" in out

    cases = {"subagent src": gate("src/a.py", True), "subagent docs": gate("docs/tdq/research/r.md", True),
             "main src": gate("src/a.py", False)}
    for k, v in cases.items():
        print(f"{k}: deny={v[0]} team={v[1]}")
    assert cases["subagent src"] == (True, True)
    assert not cases["subagent docs"][0] and not cases["main src"][0]
    print("SMOKE PASS")
