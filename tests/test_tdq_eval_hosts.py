import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import tdq_eval_hosts
from tdq_test_process import _windows_pid_alive


@pytest.fixture
def tmp_path():
    with tempfile.TemporaryDirectory(prefix="tdq-eval-test-") as temp_dir:
        yield Path(temp_dir)


def test_preflight_unsupported_host():
    res = tdq_eval_hosts.preflight_host("cursor")
    assert res["host"] == "cursor"
    assert res["status"] == "UNSUPPORTED"
    assert res["ready"] is False
    assert res["reason"] == "unsupported_host"
    assert res["paid_model_calls"] == 0


def test_preflight_blocks_missing_isolation_or_real_home(tmp_path):
    empty_res = tdq_eval_hosts.preflight_host("claude", profile={})
    assert empty_res["status"] == "BLOCKED"
    assert empty_res["ready"] is False
    assert empty_res["reason"] == "isolation_not_satisfied"
    assert empty_res["paid_model_calls"] == 0

    real_home_profile = {
        "workspace_dir": str(tmp_path / "ws"),
        "home_dir": str(Path.home()),
        "config_dir": str(tmp_path / "cfg"),
    }
    home_res = tdq_eval_hosts.preflight_host("claude", profile=real_home_profile)
    assert home_res["status"] == "BLOCKED"
    assert home_res["ready"] is False
    assert home_res["reason"] == "isolation_not_satisfied"

    mixed_plugin_profile = tdq_eval_hosts.prepare_trial_environment(
        tmp_path, "codex", "trial-mix", plugin_dir=tmp_path / "candidate-plugin"
    )
    mixed_plugin_profile["load_global_plugins"] = True
    mix_res = tdq_eval_hosts.preflight_host("codex", profile=mixed_plugin_profile)
    assert mix_res["status"] == "BLOCKED"
    assert mix_res["ready"] is False
    assert mix_res["reason"] == "isolation_not_satisfied"


def test_preflight_ready_and_failure_with_process_fixture(tmp_path):
    claude_env = tdq_eval_hosts.prepare_trial_environment(tmp_path, "claude-code", "pf-claude")
    res_claude = tdq_eval_hosts.preflight_host(
        "claude-code",
        profile=claude_env,
        command_override=[sys.executable, "-c", "print('claude-code 1.0.99')"],
    )
    assert res_claude["host"] == "claude"
    assert res_claude["status"] == "READY"
    assert res_claude["ready"] is True
    assert res_claude["version"] == "claude-code 1.0.99"
    assert res_claude["isolation_verified"] is True
    assert res_claude["paid_model_calls"] == 0

    codex_env = tdq_eval_hosts.prepare_trial_environment(tmp_path, "codex", "pf-codex")
    res_codex = tdq_eval_hosts.preflight_host(
        "codex",
        profile=codex_env,
        command_override=[sys.executable, "-c", "print('codex-cli 0.42.0')"],
    )
    assert res_codex["host"] == "codex"
    assert res_codex["status"] == "READY"
    assert res_codex["ready"] is True
    assert res_codex["version"] == "codex-cli 0.42.0"
    assert res_codex["isolation_verified"] is True
    assert res_codex["paid_model_calls"] == 0

    res_fail = tdq_eval_hosts.preflight_host(
        "claude",
        profile=claude_env,
        command_override=[sys.executable, "-c", "import sys; sys.exit(2)"],
    )
    assert res_fail["status"] == "BLOCKED"
    assert res_fail["ready"] is False
    assert res_fail["paid_model_calls"] == 0


def test_prepare_trial_environment_isolation_and_path_guard(tmp_path):
    plugin_dir = tmp_path / "my-plugin"
    plugin_dir.mkdir()
    env_a = tdq_eval_hosts.prepare_trial_environment(tmp_path, "claude", "trial-a", plugin_dir=plugin_dir)
    env_b = tdq_eval_hosts.prepare_trial_environment(tmp_path, "codex", "trial-b")

    assert env_a["workspace_dir"] != env_b["workspace_dir"]
    assert env_a["home_dir"] != env_b["home_dir"]
    assert env_a["config_dir"] != env_b["config_dir"]
    assert Path(env_a["workspace_dir"]).is_dir()
    assert Path(env_a["home_dir"]).is_dir()
    assert Path(env_a["config_dir"]).is_dir()
    assert env_a["env"]["CLAUDE_CONFIG_DIR"] == env_a["config_dir"]
    assert env_b["env"]["CODEX_HOME"] == env_b["config_dir"]
    assert env_a["env"]["TDQ_DISABLE_GLOBAL_PLUGINS"] == "1"
    assert env_a["plugin_dir"] == str(plugin_dir.resolve())

    with pytest.raises(ValueError):
        tdq_eval_hosts.prepare_trial_environment(tmp_path, "claude", "../escape")


def test_run_host_trial_timeout_and_descendant_cleanup(tmp_path):
    profile = tdq_eval_hosts.prepare_trial_environment(tmp_path, "claude", "trial-timeout")
    profile["timeout_seconds"] = 1.0
    profile["max_retries"] = 0
    pid_file = Path(profile["workspace_dir"]) / "descendant.pid"

    script = (
        "import pathlib, subprocess, sys, time; "
        f"p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)']); "
        f"pathlib.Path({str(pid_file)!r}).write_text(str(p.pid), encoding='utf-8'); "
        "time.sleep(30)"
    )
    trial_spec = {
        "trial_id": "trial-timeout",
        "case_id": "case-timeout",
        "command": [sys.executable, "-c", script],
    }
    result = tdq_eval_hosts.run_host_trial("claude", trial_spec, profile)
    assert result["execution_status"] == "timeout"
    assert result["timed_out"] is True
    assert len(result["attempts"]) == 1
    attempt = result["attempts"][0]
    assert attempt["timed_out"] is True
    assert attempt["cleanup_complete"] is True
    assert attempt["ownership"]["verified"] is True
    assert len(attempt["raw_trace_sha256"]) == 64

    assert pid_file.exists()
    descendant_pid = int(pid_file.read_text(encoding="utf-8").strip())
    if os.name == "nt":
        assert _windows_pid_alive(descendant_pid) is False


def test_run_host_trial_retry_cap_and_attempt_preservation(tmp_path):
    profile = tdq_eval_hosts.prepare_trial_environment(tmp_path, "codex", "trial-retry-cap")
    profile["timeout_seconds"] = 5.0
    profile["max_retries"] = 3
    profile["max_total_attempts"] = 2

    fail_script = "import sys; print('{\"type\":\"session_meta\",\"payload\":{\"id\":\"s1\",\"cwd\":\"C:/tmp\"}}'); sys.exit(1)"
    result = tdq_eval_hosts.run_host_trial(
        "codex",
        {"trial_id": "trial-retry-cap", "case_id": "case-retry", "command": [sys.executable, "-c", fail_script]},
        profile,
    )
    assert result["execution_status"] == "failed"
    assert result["reason"] == "retry_cap_exceeded"
    assert len(result["attempts"]) == 2
    assert all(a["exit_code"] == 1 for a in result["attempts"])
    assert all(len(a["raw_trace_sha256"]) == 64 for a in result["attempts"])

    recover_profile = tdq_eval_hosts.prepare_trial_environment(tmp_path, "claude", "trial-recover")
    recover_profile["timeout_seconds"] = 5.0
    recover_profile["max_retries"] = 1
    marker = Path(recover_profile["workspace_dir"]) / "once.flag"
    recover_script = (
        "import json, pathlib, sys\n"
        f"m = pathlib.Path({str(marker)!r})\n"
        "if not m.exists():\n"
        "    m.write_text('1', encoding='utf-8')\n"
        "    print(json.dumps({'type': 'system', 'sessionId': 's1', 'cwd': 'C:/ws'}))\n"
        "    sys.exit(1)\n"
        "print(json.dumps({'type': 'assistant', 'sessionId': 's1', 'cwd': 'C:/ws', "
        "'message': {'id': 'm1', 'stop_reason': 'end_turn', 'content': [{'type': 'tool_use', 'id': 't1', 'name': 'Skill', 'input': {'skill': 'tdq-intake'}}], "
        "'usage': {'input_tokens': 10, 'output_tokens': 5, 'cache_read_input_tokens': 2, 'cache_creation_input_tokens': 1}}}))\n"
        "print(json.dumps({'type': 'result', 'sessionId': 's1', 'cwd': 'C:/ws', 'is_error': False}))\n"
    )
    rec_result = tdq_eval_hosts.run_host_trial(
        "claude",
        {"trial_id": "trial-recover", "case_id": "case-rec", "expected_trigger": True, "command": [sys.executable, "-c", recover_script]},
        recover_profile,
    )
    assert rec_result["execution_status"] == "completed"
    assert len(rec_result["attempts"]) == 2
    assert rec_result["attempts"][0]["exit_code"] == 1
    assert rec_result["attempts"][1]["exit_code"] == 0
    assert rec_result["retries_count"] == 1
    assert rec_result["observed_trigger"] is True


def test_hash_file_streaming_and_trace_budget_exceeded(tmp_path):
    blob = (b'{"type":"system","sessionId":"s1","cwd":"C:/ws"}\n' * 3000)
    trace_file = tmp_path / "large.jsonl"
    trace_file.write_bytes(blob)

    expected_sha = hashlib.sha256(blob).hexdigest()
    assert tdq_eval_hosts.hash_file_streaming(trace_file) == expected_sha

    over_bytes = tdq_eval_hosts.parse_trace_stream(trace_file, max_bytes=256, max_events=50000)
    assert over_bytes["execution_status"] == "failed"
    assert over_bytes["reason"] == "budget_exceeded"
    assert over_bytes["truncated"] is True

    over_events = tdq_eval_hosts.parse_trace_stream(trace_file, max_bytes=10 * 1024 * 1024, max_events=5)
    assert over_events["execution_status"] == "failed"
    assert over_events["reason"] == "budget_exceeded"
    assert over_events["truncated"] is True


def test_parse_trace_stream_unknown_schema_and_malformed_json():
    unknown = tdq_eval_hosts.parse_trace_stream([
        json.dumps({"type": "vendor_magic_event", "foo": "bar"}),
    ])
    assert unknown["execution_status"] == "unknown_schema"
    assert unknown["reason"] == "unknown_schema"

    malformed = tdq_eval_hosts.parse_trace_stream([
        '{"type": "assistant", broken_json',
    ])
    assert malformed["execution_status"] == "failed"
    assert malformed["reason"] == "malformed_json"


def test_parse_trace_stream_claude_and_codex_metrics_and_null_cost(tmp_path):
    claude_lines = [
        json.dumps({"type": "api-request", "id": "req-1", "sessionId": "s1", "cwd": "C:/ws", "timestamp": "2026-11-01T10:00:00Z"}),
        json.dumps({
            "type": "assistant",
            "sessionId": "s1",
            "cwd": "C:/ws",
            "requestRef": "req-1",
            "timestamp": "2026-11-01T10:00:01Z",
            "message": {
                "id": "msg-1",
                "stop_reason": "tool_use",
                "content": [
                    {"type": "tool_use", "id": "tu-1", "name": "Skill", "input": {"skill": "tdq-intake"}}
                ],
                "usage": {
                    "input_tokens": 120,
                    "output_tokens": 45,
                    "cache_read_input_tokens": 30,
                    "cache_creation_input_tokens": 10,
                },
            },
        }),
        json.dumps({
            "type": "user",
            "sessionId": "s1",
            "cwd": "C:/ws",
            "timestamp": "2026-11-01T10:00:02Z",
            "message": {"content": [{"type": "tool_result", "tool_use_id": "tu-1", "content": "ok"}]},
        }),
        json.dumps({"type": "result", "sessionId": "s1", "cwd": "C:/ws", "is_error": False}),
    ]
    claude_parsed = tdq_eval_hosts.parse_trace_stream(claude_lines, expected_trigger=True)
    assert claude_parsed["host"] == "claude"
    assert claude_parsed["execution_status"] == "completed"
    assert claude_parsed["observed_trigger"] is True
    assert claude_parsed["trigger_provenance"].startswith("event:")
    assert claude_parsed["tool_calls_count"] == 1
    assert claude_parsed["model_calls_count"] == 1
    assert claude_parsed["user_interventions_count"] == 0
    assert claude_parsed["tokens"] == {
        "input_tokens": 120,
        "output_tokens": 45,
        "cache_read_tokens": 30,
        "cache_write_tokens": 10,
    }
    assert claude_parsed["total_cost_usd"] is None
    assert claude_parsed["billed_cost_usd"] is None
    assert claude_parsed["normalized_metrics"]["efficiency_metrics"]["cost"]["total_cost_usd"] is None
    assert claude_parsed["normalized_metrics"]["trigger_accuracy"]["matched"] is True

    codex_lines = [
        json.dumps({"type": "session_meta", "timestamp": "2026-11-01T10:00:00Z", "payload": {"id": "cx-1", "cwd": "C:/ws"}}),
        json.dumps({"type": "turn_context", "timestamp": "2026-11-01T10:00:01Z", "payload": {"cwd": "C:/ws"}}),
        json.dumps({
            "type": "response_item",
            "timestamp": "2026-11-01T10:00:02Z",
            "payload": {"type": "function_call", "call_id": "c1", "name": "exec_command", "arguments": "{}"},
        }),
        json.dumps({
            "type": "response_item",
            "timestamp": "2026-11-01T10:00:03Z",
            "payload": {"type": "function_call_output", "call_id": "c1", "output": "done"},
        }),
        json.dumps({
            "type": "response_item",
            "timestamp": "2026-11-01T10:00:04Z",
            "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "finished"}]},
        }),
        json.dumps({
            "type": "event_msg",
            "timestamp": "2026-11-01T10:00:05Z",
            "payload": {"type": "token_count", "usage": {"input_tokens": 200, "output_tokens": 80, "cached_input_tokens": 50}},
        }),
    ]
    codex_parsed = tdq_eval_hosts.parse_trace_stream(codex_lines, expected_trigger=False)
    assert codex_parsed["host"] == "codex"
    assert codex_parsed["execution_status"] == "completed"
    assert codex_parsed["observed_trigger"] is False
    assert codex_parsed["tool_calls_count"] == 1
    assert codex_parsed["model_calls_count"] == 1
    assert codex_parsed["tokens"]["input_tokens"] == 200
    assert codex_parsed["tokens"]["output_tokens"] == 80
    assert codex_parsed["tokens"]["cache_read_tokens"] == 50
    assert codex_parsed["tokens"]["cache_write_tokens"] is None
    assert codex_parsed["normalized_metrics"]["efficiency_metrics"]["tokens"]["availability"] == "partial"
    assert codex_parsed["total_cost_usd"] is None


def test_logging_on_off_and_redaction(monkeypatch, capsys):
    monkeypatch.setenv("TDQ_EVAL_LOG", "1")
    monkeypatch.setenv("TDQ_LOG", "1")
    tdq_eval_hosts.log("trial started", experiment="exp-1", reason="api_key=sk-secret-value")
    err_on = capsys.readouterr().err
    assert "trial started" in err_on
    assert "sk-secret-value" not in err_on
    assert "[redacted]" in err_on

    monkeypatch.setenv("TDQ_EVAL_LOG", "0")
    tdq_eval_hosts.log("should not appear", experiment="exp-1")
    assert capsys.readouterr().err == ""
