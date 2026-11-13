"""V3 Verification: Live cmd.exe /c dual-protocol hooks, all 24 TDQ:* codes, EC-01..EC-14."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_DIR = WORKSPACE / "plugins" / "tdq-workflow"
HOOKS_DIR = PLUGIN_DIR / "hooks" / "scripts"
for _p in (str(PLUGIN_DIR / "scripts"), str(HOOKS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
_spec = importlib.util.spec_from_file_location("_agy_plugin_common", HOOKS_DIR / "_common.py")
_common = importlib.util.module_from_spec(_spec)
sys.modules["_agy_plugin_common"] = _common
_spec.loader.exec_module(_common)


EXPECTED_24_CODES = {
    "EDIT", "TEST", "TICK", "DIRTY", "LOG", "READ", "SEARCH", "NO-PLAN-MODE",
    "LSP", "LSP-WAIT", "COMPACT", "GON", "UNFINISHED", "PAUSE", "LECH",
    "SETUP", "SUBAGENT", "VUNG", "GATE", "ANCHOR", "ZERO-POPUP", "READONLY",
    "SCOPE", "FEEDBACK",
}


def _init_git_repo(repo: Path) -> None:
    kw = {"cwd": str(repo), "capture_output": True, "text": True, "encoding": "utf-8", "timeout": 15}
    subprocess.run(["git", "init", "-b", "main"], check=True, **kw)
    subprocess.run(["git", "config", "user.email", "tdq@example.com"], check=True, **kw)
    subprocess.run(["git", "config", "user.name", "TDQ Tester"], check=True, **kw)
    (repo / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], check=True, **kw)
    subprocess.run(["git", "commit", "-m", "init"], check=True, **kw)


def _run_hook(script_name: str, payload: dict, event: str | None = None, cwd: Path = PLUGIN_DIR, extra_env=None):
    ev_flag = f"--event {event}" if event else ""
    cmd = f'cmd /c py -3 -X utf8 "{HOOKS_DIR / script_name}" {ev_flag}'.strip()
    env = dict(os.environ, TDQ_KHOI_TAO_NEN="0", TDQ_KHONG_CHAM_MAY="1", TDQ_LOG="0")
    if extra_env:
        env.update(extra_env)
    kw = {
        "cwd": str(cwd),
        "input": json.dumps(payload),
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "timeout": 20,
        "env": env,
    }
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return subprocess.run(cmd, **kw)


def _state_cli(repo: Path, *args: str):
    kw = {"cwd": str(repo), "capture_output": True, "text": True, "encoding": "utf-8", "timeout": 20}
    return subprocess.run([sys.executable, "-X", "utf8", str(PLUGIN_DIR / "scripts" / "tdq_state.py"), *args], **kw)


def test_all_24_tdq_codes_registered():
    assert set(_common.CODES) == EXPECTED_24_CODES


def test_ec01_to_ec14_live_cmd_hooks(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    assert _state_cli(repo, "init", "2026-11-13-1200-test-ec", "express", "--bo-qua-lsp", "unit test").returncode == 0
    assert _state_cli(repo, "approve", "quick", "--by", "duyet nhanh", "--bo-qua-archify", "unit test").returncode == 0

    # EC-11: SessionStart emits valid AGY JSON {"additionalContext": ...}
    ss = _run_hook("session_start.py", {"cwd": str(repo), "conversation_id": "conv-ec", "source": "compact"}, event="SessionStart", cwd=repo)
    assert ss.returncode == 0
    ss_json = json.loads(ss.stdout.strip())
    assert "additionalContext" in ss_json
    assert "[TDQ:ANCHOR]" in ss_json["additionalContext"]

    # EC-10: question gate blocks ask_question popup with [TDQ:ZERO-POPUP]
    ak = _run_hook("ask_" + "gate.py", {"cwd": str(repo), "conversation_id": "conv-ec", "tool_name": "ask_question", "tool_input": {"questions": []}}, event="PreToolUse", cwd=repo)
    assert ak.returncode == 0
    ak_json = json.loads(ak.stdout.strip())
    assert ak_json["decision"] == "deny"
    assert "[TDQ:ZERO-POPUP]" in ak_json["reason"]

    # EC-01 + EC-14: step-0 transcriptPath marks subagent tdq-reviewer -> edit_gate denies [TDQ:READONLY]
    tr = tmp_path / "sub_transcript.jsonl"
    tr.write_text(json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "You are tdq-reviewer checking spec."}) + "\n", encoding="utf-8")
    ed_ro = _run_hook(
        "edit_gate.py",
        {"cwd": str(repo), "conversation_id": "conv-rev", "transcriptPath": str(tr), "tool_name": "edit_file", "tool_input": {"TargetFile": str(repo / "app.py")}},
        event="PreToolUse",
        cwd=repo,
    )
    assert ed_ro.returncode == 0
    ed_ro_json = json.loads(ed_ro.stdout.strip())
    assert ed_ro_json["decision"] == "deny"
    assert "[TDQ:READONLY]" in ed_ro_json["reason"]

    # EC-02: subagent_dispatch_gate enforces Workspace='inherit' when WORKTREE: present
    sd = _run_hook(
        "subagent_dispatch_gate.py",
        {"cwd": str(repo), "conversation_id": "conv-ec", "tool_name": "invoke_subagent", "tool_input": {"Role": "tdq-implementer", "Workspace": "branch", "Prompt": "TASK: T1.1\nWORKTREE: C:/tmp/wt\n"}},
        event="PreToolUse",
        cwd=repo,
    )
    assert sd.returncode == 0
    assert json.loads(sd.stdout.strip())["decision"] == "deny"

    # EC-06: bash_gate blocks banned branch name AND PowerShell Set-Content on state.json
    bg_br = _run_hook("bash_gate.py", {"cwd": str(repo), "conversation_id": "conv-ec", "tool_name": "run_command", "tool_input": {"CommandLine": "git checkout -b claude-bad"}}, event="PreToolUse", cwd=repo)
    assert json.loads(bg_br.stdout.strip())["decision"] == "deny"
    bg_ps = _run_hook("bash_gate.py", {"cwd": str(repo), "conversation_id": "conv-ec", "tool_name": "run_command", "tool_input": {"CommandLine": "Set-Content -Path docs/tdq/state.json -Value '{}'"}}, event="PreToolUse", cwd=repo)
    assert json.loads(bg_ps.stdout.strip())["decision"] == "deny"

    # EC-07: search_observe unwraps call_mcp_tool(ServerName='lsp', ToolName='start_lsp')
    so = _run_hook(
        "search_observe.py",
        {"cwd": str(repo), "conversation_id": "conv-ec", "tool_name": "call_mcp_tool", "tool_input": {"ServerName": "lsp", "ToolName": "start_lsp", "Arguments": {"root_dir": str(repo)}}},
        event="PostToolUse",
        cwd=repo,
    )
    assert so.returncode == 0

    # EC-08: prompt_context detects bug/feedback wording and emits [TDQ:FEEDBACK]
    pc = _run_hook("prompt_context.py", {"cwd": str(repo), "conversation_id": "conv-ec", "prompt": "cái này lỗi rồi sửa lại giúp tôi"}, event="PreInvocation", cwd=repo)
    assert pc.returncode == 0
    assert "[TDQ:FEEDBACK]" in json.loads(pc.stdout.strip())["additionalContext"]

    # EC-09: read_gate normalizes read_file StartLine/EndLine without false remind/crash
    rg = _run_hook("read_gate.py", {"cwd": str(repo), "conversation_id": "conv-ec", "tool_name": "read_file", "tool_input": {"AbsolutePath": str(repo / "app.py"), "StartLine": 1, "EndLine": 2}}, event="PreToolUse", cwd=repo)
    assert rg.returncode == 0
    assert "decision" not in rg.stdout

    # EC-14: PostInvocation flushes any queued PreToolUse reminders cleanly
    _common.queue_remind(str(repo), {"conversation_id": "conv-q"}, "TEST", "[TDQ:TEST] run pytest")
    pi = _run_hook("post_invocation.py", {"cwd": str(repo), "conversation_id": "conv-q"}, event="PostInvocation", cwd=repo)
    assert "[TDQ:TEST]" in json.loads(pi.stdout.strip())["additionalContext"]

    # EC-13: codex_edit_gate enforces TDQ_CODEX_VUNG [TDQ:VUNG]
    cx = _run_hook(
        "codex_edit_gate.py",
        {"cwd": str(repo), "tool_name": "apply_patch", "tool_input": {"command": "*** Update File: secret/out.py\n+x=1"}},
        cwd=repo,
        extra_env={"TDQ_CODEX_TASK": "T1.1", "TDQ_CODEX_VUNG": "app.py"},
    )
    assert "[TDQ:VUNG]" in cx.stdout

    # EC-03: stop_gate emits {"decision": "continue"} on AGY when repo edited without working log
    _run_hook("prompt_context.py", {"cwd": str(repo), "conversation_id": "conv-stop", "prompt": "check stop"}, event="PreInvocation", cwd=repo)
    (repo / "app.py").write_text("def add(a, b):\n    return a + b + 1\n", encoding="utf-8")
    sg = _run_hook("stop_gate.py", {"cwd": str(repo), "conversation_id": "conv-stop"}, event="Stop", cwd=repo)
    assert sg.returncode == 0
    sg_json = json.loads(sg.stdout.strip())
    assert sg_json["decision"] == "continue"
    assert "[TDQ:LOG]" in sg_json["reason"]

    # Backward compat: Claude Code payload (no --event, Claude tool names) still emits hookSpecificOutput
    ak_claude = _run_hook("ask_" + "gate.py", {"cwd": str(repo), "session_id": "claude-1", "tool_name": "AskUserQuestion", "tool_input": {}}, event=None, cwd=repo)
    assert ak_claude.returncode == 0
    if ak_claude.stdout.strip():
        assert "hookSpecificOutput" in ak_claude.stdout


def test_ec15_protojson_toolcall_workspacepaths_and_terminal_stop(tmp_path):
    repo = tmp_path / "repo_proto"
    repo.mkdir()
    _init_git_repo(repo)
    assert _state_cli(repo, "init", "2026-11-14-0400-test-proto", "express", "--bo-qua-lsp", "unit test").returncode == 0
    assert _state_cli(repo, "approve", "quick", "--by", "duyet nhanh", "--bo-qua-archify", "unit test").returncode == 0

    # SessionStart with file:// workspacePaths returns both additionalContext and injectSteps
    ss = _run_hook(
        "session_start.py",
        {"workspacePaths": [repo.as_uri()], "conversation_id": "conv-proto", "source": "resume"},
        event="SessionStart",
        cwd=PLUGIN_DIR,
    )
    assert ss.returncode == 0
    ss_json = json.loads(ss.stdout.strip())
    assert "[TDQ:ANCHOR]" in ss_json["additionalContext"]
    assert ss_json["injectSteps"][0]["systemMessage"]["systemMessage"] == ss_json["additionalContext"]

    # EC-02 + EC-15 guard: missing workinglog queues [TDQ:LOG] without skipping [TDQ:TICK] block under toolCall + file://
    plan_file = repo / "docs" / "tdq" / "plan" / "2026-11-14-0400-test-proto.md"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text("- [ ] **T1.1**: Unticked item\n", encoding="utf-8")
    assert _state_cli(repo, "set", "plan_file=docs/tdq/plan/2026-11-14-0400-test-proto.md", "phase=implement").returncode == 0
    assert not (repo / "docs" / "workinglog").exists()
    eg = _run_hook(
        "edit_gate.py",
        {
            "workspacePaths": [repo.as_uri()],
            "conversationId": "conv-proto",
            "toolCall": {"name": "edit_file", "args": {"TargetFile": str(repo / "unticked.py")}},
        },
        event="PreToolUse",
        cwd=PLUGIN_DIR,
    )
    assert eg.returncode == 0
    eg_json = json.loads(eg.stdout.strip())
    assert eg_json["decision"] == "deny"
    assert "[TDQ:TICK]" in eg_json["reason"]
    assert any("[TDQ:LOG]" in r for r in _common.flush_pending_reminders(str(repo), "conv-proto"))

    # PreToolUse with nested toolCall.args.CommandLine + workspacePaths blocks banned branch name
    bg = _run_hook(
        "bash_gate.py",
        {
            "workspacePaths": [str(repo)],
            "conversation_id": "conv-proto",
            "toolCall": {"name": "run_command", "args": {"CommandLine": "git checkout -b gemini-bad"}},
        },
        event="PreToolUse",
        cwd=PLUGIN_DIR,
    )
    assert bg.returncode == 0
    assert json.loads(bg.stdout.strip())["decision"] == "deny"

    # PreInvocation with lastUserInput fallback triggers [TDQ:FEEDBACK]
    pc = _run_hook(
        "prompt_context.py",
        {"workspacePaths": [str(repo)], "conversation_id": "conv-proto", "lastUserInput": "cái này lỗi rồi sửa lại"},
        event="PreInvocation",
        cwd=PLUGIN_DIR,
    )
    assert pc.returncode == 0
    assert "[TDQ:FEEDBACK]" in json.loads(pc.stdout.strip())["additionalContext"]

    # Stop with USER_CANCELED stays silent even if repo changed without working log
    (repo / "app.py").write_text("def add(a, b):\n    return a + b + 99\n", encoding="utf-8")
    sg = _run_hook(
        "stop_gate.py",
        {"workspacePaths": [str(repo)], "conversation_id": "conv-proto", "terminationReason": "USER_CANCELED"},
        event="Stop",
        cwd=PLUGIN_DIR,
    )
    assert sg.returncode == 0
    assert sg.stdout.strip() == ""
