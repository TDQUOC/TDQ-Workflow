"""Host adapters and runtime execution primitives for Claude Code and Codex on Windows.

Provides native preflight without model calls, per-trial directory and environment
isolation, process tree lifecycle management via OwnedProcessJob, bounded retries,
and streaming JSONL trace parsing with artifact hashing.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import tdq_eval_contract
import tdq_transcript
from tdq_test_process import OwnedProcessJob, _private_environment

SUPPORTED_HOSTS = ("claude", "codex", "antigravity")
CHUNK_SIZE = 64 * 1024
DEFAULT_MAX_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_EVENTS = 50000

CLAUDE_EVENT_TYPES = {
    "api-request", "assistant", "user", "system", "progress", "result",
    "tool_use", "tool_result",
}
CODEX_EVENT_TYPES = {
    "session_meta", "response_item", "event_msg", "turn_context",
    "thread.started", "turn.started", "turn.completed", "turn.failed",
    "item.started", "item.updated", "item.completed", "error",
}
AGY_EVENT_TYPES = {"USER_INPUT", "PLANNER_RESPONSE", "SYSTEM", "TOOL_RESPONSE"}
KNOWN_EVENT_TYPES = (
    CLAUDE_EVENT_TYPES | CODEX_EVENT_TYPES | AGY_EVENT_TYPES | tdq_transcript.UNTIMED_TYPES
)


def log(thong_diep: str, muc: str = "thong-tin", **fields: Any) -> None:
    """Relay to tdq_eval_contract.log for sanitized and redacted ISO UTC logging."""
    tdq_eval_contract.log(thong_diep, muc=muc, **fields)


def canonical_host_name(host: Optional[str]) -> Optional[str]:
    """Normalize supported host aliases; unknown values returned as-is."""
    if not isinstance(host, str):
        return None
    normalized = host.strip().lower()
    if normalized in ("claude", "claude-code"):
        return "claude"
    if normalized == "codex":
        return "codex"
    if normalized in ("antigravity", "agy"):
        return "antigravity"
    return normalized


def _safe_segment(name: str) -> bool:
    if not isinstance(name, str) or not name.strip():
        return False
    if re.search(r"[:\x00-\x1f%/\\]", name):
        return False
    return name not in {".", ".."}


def hash_file_streaming(path: Union[str, Path]) -> str:
    """Compute SHA-256 digest of file by 64KB chunks."""
    target = Path(path).resolve(strict=True)
    hasher = hashlib.sha256()
    with target.open("rb") as stream:
        while True:
            chunk = stream.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def prepare_trial_environment(
    base_dir: Union[str, Path],
    host: str,
    trial_id: str,
    plugin_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Create isolated workspace, home, and config directory structure for a trial."""
    canonical = canonical_host_name(host)
    if canonical not in SUPPORTED_HOSTS:
        raise ValueError(f"unsupported host: {host}")
    if not _safe_segment(trial_id):
        raise ValueError("invalid trial_id")

    base = Path(base_dir).resolve()
    base.mkdir(parents=True, exist_ok=True)
    trial_root = base / f"{canonical}-{trial_id}"
    trial_root.mkdir(parents=True, exist_ok=True)

    isolated_env = _private_environment(trial_root)
    workspace_dir = trial_root / "workspace"
    home_dir = Path(isolated_env["HOME"]).resolve()
    config_dir = trial_root / "config"
    for directory in (workspace_dir, config_dir):
        directory.mkdir(parents=True, exist_ok=True)

    isolated_env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    isolated_env["CODEX_HOME"] = str(config_dir)
    isolated_env["TDQ_DISABLE_GLOBAL_PLUGINS"] = "1"

    profile: Dict[str, Any] = {
        "host": canonical,
        "trial_id": trial_id,
        "trial_root": str(trial_root),
        "workspace_dir": str(workspace_dir),
        "home_dir": str(home_dir),
        "config_dir": str(config_dir),
        "env": isolated_env,
        "load_global_plugins": False,
    }

    if plugin_dir is not None:
        p_path = Path(plugin_dir).resolve()
        profile["plugin_dir"] = str(p_path)

    return profile


def _verify_isolation(profile: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    if not isinstance(profile, dict):
        return False, "isolation_not_satisfied"

    req_keys = ("workspace_dir", "home_dir", "config_dir")
    if not all(k in profile and isinstance(profile[k], str) for k in req_keys):
        return False, "isolation_not_satisfied"

    home = Path(profile["home_dir"]).resolve()
    user_home = Path.home().resolve()
    if home == user_home:
        return False, "isolation_not_satisfied"

    if profile.get("load_global_plugins") and profile.get("plugin_dir"):
        return False, "isolation_not_satisfied"

    return True, "isolation_verified"


def preflight_host(
    host: str,
    profile: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, str]] = None,
    command_override: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Execute native capability check without calling model or credential stores."""
    canonical = canonical_host_name(host)
    if canonical not in SUPPORTED_HOSTS:
        return {
            "host": host,
            "status": "UNSUPPORTED",
            "ready": False,
            "reason": "unsupported_host",
            "paid_model_calls": 0,
        }

    iso_ok, iso_reason = _verify_isolation(profile)
    if not iso_ok:
        return {
            "host": canonical,
            "status": "BLOCKED",
            "ready": False,
            "reason": iso_reason,
            "paid_model_calls": 0,
        }

    assert profile is not None
    workspace = Path(profile["workspace_dir"]).resolve()
    active_env = dict(profile.get("env", {}))
    if env:
        active_env.update(env)

    command = command_override or ([canonical, "--version"] if canonical == "codex" else ["claude", "--version"])

    try:
        with OwnedProcessJob(workspace, timeout_seconds=10, env=active_env) as job:
            res = job.run(command, phase="preflight")
            if res.get("exit_code") == 0 and not res.get("timed_out"):
                version_line = (res.get("stdout") or "").splitlines()
                v_text = version_line[0].strip() if version_line else "unknown"
                return {
                    "host": canonical,
                    "status": "READY",
                    "ready": True,
                    "version": v_text,
                    "capabilities": ["tool", "trace_streaming"],
                    "isolation_verified": True,
                    "paid_model_calls": 0,
                }
            return {
                "host": canonical,
                "status": "BLOCKED",
                "ready": False,
                "reason": res.get("reason", "command_failed"),
                "paid_model_calls": 0,
            }
    except Exception as exc:
        return {
            "host": canonical,
            "status": "BLOCKED",
            "ready": False,
            "reason": f"launch_exception: {exc}",
            "paid_model_calls": 0,
        }


def _extract_claude_usage(message: Dict[str, Any], tokens: Dict[str, Optional[int]]) -> None:
    usage = message.get("usage")
    if not isinstance(usage, dict):
        return
    if "input_tokens" in usage and isinstance(usage["input_tokens"], int):
        tokens["input_tokens"] = (tokens["input_tokens"] or 0) + usage["input_tokens"]
    if "output_tokens" in usage and isinstance(usage["output_tokens"], int):
        tokens["output_tokens"] = (tokens["output_tokens"] or 0) + usage["output_tokens"]
    if "cache_read_input_tokens" in usage and isinstance(usage["cache_read_input_tokens"], int):
        tokens["cache_read_tokens"] = (tokens["cache_read_tokens"] or 0) + usage["cache_read_input_tokens"]
    if "cache_creation_input_tokens" in usage and isinstance(usage["cache_creation_input_tokens"], int):
        tokens["cache_write_tokens"] = (tokens["cache_write_tokens"] or 0) + usage["cache_creation_input_tokens"]


def _process_claude_event(
    record: Dict[str, Any],
    stats: Dict[str, Any],
    tokens: Dict[str, Optional[int]],
) -> None:
    event_type = record.get("type")
    if event_type == "api-request":
        stats["model_calls"] += 1
    elif event_type == "assistant":
        msg = record.get("message")
        if isinstance(msg, dict):
            _extract_claude_usage(msg, tokens)
            for block in msg.get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    stats["tool_calls"] += 1
                    stats["observed_trigger"] = True
                    t_name = block.get("name", "tool")
                    stats["trigger_provenance"] = f"event:tool_use:{t_name}"
    elif event_type == "user":
        content = record.get("message", {}).get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") != "tool_result":
                    stats["user_interventions"] += 1


def _extract_codex_usage(payload: Dict[str, Any], tokens: Dict[str, Optional[int]]) -> None:
    if payload.get("type") != "token_count":
        return
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return
    if isinstance(usage.get("input_tokens"), int):
        tokens["input_tokens"] = (tokens["input_tokens"] or 0) + usage["input_tokens"]
    if isinstance(usage.get("output_tokens"), int):
        tokens["output_tokens"] = (tokens["output_tokens"] or 0) + usage["output_tokens"]
    if isinstance(usage.get("cached_input_tokens"), int):
        tokens["cache_read_tokens"] = (tokens["cache_read_tokens"] or 0) + usage["cached_input_tokens"]


def _process_codex_event(
    record: Dict[str, Any],
    stats: Dict[str, Any],
    tokens: Dict[str, Optional[int]],
) -> None:
    event_type = record.get("type")
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return
    if event_type == "response_item":
        p_type = payload.get("type")
        if p_type in ("function_call", "custom_tool_call"):
            stats["tool_calls"] += 1
            t_name = payload.get("name", "tool")
            stats["trigger_provenance"] = f"event:codex_call:{t_name}"
        elif p_type == "message" and payload.get("role") == "assistant":
            stats["model_calls"] += 1
    elif event_type == "event_msg":
        _extract_codex_usage(payload, tokens)


def _iter_lines(path_or_lines: Union[str, Path, Iterable[Any]]) -> Iterable[Tuple[bytes, int]]:
    if isinstance(path_or_lines, (str, Path)) and os.path.exists(path_or_lines):
        with open(path_or_lines, "rb") as stream:
            for line in stream:
                yield line, len(line)
    elif isinstance(path_or_lines, Iterable):
        for item in path_or_lines:
            raw = item.encode("utf-8") if isinstance(item, str) else bytes(item)
            if not raw.endswith(b"\n"):
                raw += b"\n"
            yield raw, len(raw)


def _decode_trace_event(line: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    try:
        record = json.loads(line)
    except ValueError:
        return None, {"execution_status": "failed", "reason": "malformed_json", "paid_model_calls": 0}
    if (not isinstance(record, dict) or not isinstance(record.get("type"), str)
            or record["type"] not in KNOWN_EVENT_TYPES):
        return None, {"execution_status": "unknown_schema", "reason": "unknown_schema", "paid_model_calls": 0}
    return record, None


def _valid_trace_content(content) -> bool:
    if isinstance(content, str):
        return True
    if not isinstance(content, list):
        return False
    for block in content:
        if not isinstance(block, dict) or not isinstance(block.get("type"), str):
            return False
        if "text" in block and not isinstance(block["text"], str):
            return False
    return True


def _valid_trace_usage(usage) -> bool:
    if not isinstance(usage, dict):
        return False
    fields = ("input_tokens", "output_tokens", "cache_read_input_tokens",
              "cache_creation_input_tokens", "cached_input_tokens")
    return all(type(usage[key]) is int and usage[key] >= 0 for key in fields if key in usage)


def _validate_trace_fields(record) -> Optional[Dict[str, Any]]:
    containers = [record]
    for key in ("message", "payload"):
        value = record.get(key, {})
        if not isinstance(value, dict):
            return {"execution_status": "unknown_schema", "reason": "invalid_message"}
        containers.append(value)
    for container in containers:
        if "content" in container and not _valid_trace_content(container["content"]):
            return {"execution_status": "unknown_schema", "reason": "invalid_content"}
        if "usage" in container and not _valid_trace_usage(container["usage"]):
            return {"execution_status": "unknown_schema", "reason": "invalid_usage"}
    return None


def _bind_trace_model(record: Dict[str, Any], state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    error = _validate_trace_fields(record)
    if error:
        return error
    payload = record.get("payload", {})
    message = record.get("message", {})
    model = message.get("model") or record.get("model") or payload.get("model")
    if isinstance(model, str) and model.strip():
        if state["observed_model"] not in (None, model):
            return {"execution_status": "failed", "reason": "mixed_models"}
        state["observed_model"] = model
    return None


def _validate_trace_event(record, event_host, state) -> Optional[Dict[str, Any]]:
    if event_host and state["host"] not in (None, event_host):
        return {"execution_status": "failed", "reason": "mixed_hosts"}
    state["host"] = event_host or state["host"]
    error = _bind_trace_model(record, state)
    if error:
        return error
    event_type = record["type"]
    if record.get("is_error") or event_type in {"error", "turn.failed"} or (
        event_type == "result" and record.get("subtype", "success") != "success"
    ):
        return {"execution_status": "failed", "reason": "host_error"}
    if state["terminal"]:
        return {"execution_status": "failed", "reason": "events_after_terminal"}
    return None


def _process_codex_response(record, state, stats, tokens) -> Optional[Dict[str, Any]]:
    event_type = record["type"]
    payload = record.get("payload") or {}
    _process_codex_event(record, stats, tokens)
    if event_type == "item.completed":
        item = record.get("item")
        if not isinstance(item, dict):
            return {"execution_status": "unknown_schema", "reason": "invalid_item"}
        if item.get("type") == "agent_message":
            state["response_text"] = item.get("text", "")
            stats["model_calls"] += 1
        elif item.get("type") in {"command_execution", "mcp_tool_call"}:
            stats["tool_calls"] += 1
    elif event_type == "turn.completed":
        state["terminal"] = True
        _extract_codex_usage({"type": "token_count", "usage": record.get("usage")}, tokens)
    elif event_type == "event_msg" and payload.get("type") in {"task_complete", "turn_complete"}:
        state["terminal"] = True
        state["response_text"] = payload.get("last_agent_message", "")
    return None


def _consume_trace_event(record, state, stats, tokens) -> Optional[Dict[str, Any]]:
    event_type = record["type"]
    event_host = "claude" if event_type in CLAUDE_EVENT_TYPES else (
        "codex" if event_type in CODEX_EVENT_TYPES else None
    )
    error = _validate_trace_event(record, event_host, state)
    if error:
        return error
    if event_host == "claude":
        _process_claude_event(record, stats, tokens)
        if event_type == "result":
            state["terminal"] = record.get("is_error") is False
            state["response_text"] = record.get("result", "")
    elif event_host == "codex":
        return _process_codex_response(record, state, stats, tokens)
    return None


def _trace_result(state, stats, tokens, expected_trigger) -> Dict[str, Any]:
    response = state["response_text"]
    if not state["terminal"] or not isinstance(response, str) or not response.strip():
        return {"execution_status": "incomplete", "reason": "missing_terminal_response"}
    metrics = {
        "execution_status": "completed",
        "observed_trigger": stats["observed_trigger"],
        "trigger_provenance": stats["trigger_provenance"],
        "tool_calls_count": stats["tool_calls"],
        "model_calls_count": stats["model_calls"],
        "user_interventions_count": stats["user_interventions"],
        "tokens": tokens,
        "total_cost_usd": None,
        "billed_cost_usd": None,
    }
    normalized = tdq_eval_contract.normalize_trial_metrics(dict(
        metrics, passed=None, score=None, expected_trigger=expected_trigger, retries_count=0,
    ))
    return dict(metrics, host=state["host"], observed_model=state["observed_model"],
                response_text=response, normalized_metrics=normalized)


def parse_trace_stream(
    path_or_lines: Union[str, Path, Iterable[Any]],
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_events: int = DEFAULT_MAX_EVENTS,
    expected_trigger: Optional[bool] = None,
) -> Dict[str, Any]:
    """Parse JSONL trace events line by line within explicit byte and count budgets."""
    total_bytes = 0
    state = {"host": None, "terminal": False, "response_text": "", "observed_model": None}
    stats = {"tool_calls": 0, "model_calls": 0, "user_interventions": 0,
             "observed_trigger": False, "trigger_provenance": "unavailable"}
    tokens = {key: None for key in tdq_eval_contract.TOKEN_FIELDS}
    for event_count, (line_bytes, byte_len) in enumerate(_iter_lines(path_or_lines), 1):
        total_bytes += byte_len
        if total_bytes > max_bytes or event_count > max_events:
            return {"execution_status": "failed", "reason": "budget_exceeded",
                    "truncated": True, "paid_model_calls": 0}
        try:
            line_str = line_bytes.decode("utf-8-sig").strip()
        except UnicodeDecodeError:
            return {"execution_status": "failed", "reason": "invalid_utf8", "paid_model_calls": 0}
        if not line_str:
            continue
        record, error = _decode_trace_event(line_str)
        if error:
            return error
        error = _consume_trace_event(record, state, stats, tokens)
        if error:
            return error
    return _trace_result(state, stats, tokens, expected_trigger)


def _record_attempt(
    result: Dict[str, Any],
    trace_path: Path,
) -> Dict[str, Any]:
    trace_sha = hash_file_streaming(trace_path) if trace_path.exists() else "0" * 64
    return {
        "exit_code": result.get("exit_code"),
        "timed_out": bool(result.get("timed_out")),
        "duration_seconds": result.get("duration_seconds"),
        "cleanup_complete": bool(result.get("cleanup_complete")),
        "ownership": result.get("ownership", {}),
        "raw_trace_sha256": trace_sha,
    }


def build_host_command(host: str, trial_spec: Dict[str, Any]) -> List[str]:
    """Instruction-only trials; no plugin loading or permission bypass flags."""
    prompt, model, instructions = (trial_spec.get(k) for k in ("prompt", "model", "instructions"))
    if not all(isinstance(v, str) and v.strip() for v in (prompt, model, instructions)):
        raise ValueError("missing_prompt_model_or_instructions")
    if host == "claude":
        return ["claude", "--print", "--verbose", "--output-format", "stream-json",
                "--model", model, "--system-prompt", instructions, "--tools", "",
                "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                "--setting-sources", "", "--", prompt]
    if host == "codex":
        return ["codex", "exec", "--json", "--model", model, "--sandbox", "read-only",
                "--skip-git-repo-check", "-c", "developer_instructions=" + json.dumps(instructions),
                "--", prompt]
    if host == "antigravity":
        return ["agy", "agent", "--prompt", prompt]
    raise ValueError("unsupported_host")


def _parse_attempt(result, trace_file, trial_spec, canonical) -> Dict[str, Any]:
    if result.get("timed_out"):
        return {"execution_status": "timeout", "reason": "process_timeout"}
    if result.get("exit_code") != 0:
        return {"execution_status": "failed", "reason": result.get("reason", f"exit_{result.get('exit_code')}")}
    parsed = parse_trace_stream(trace_file, expected_trigger=trial_spec.get("expected_trigger"))
    parsed.setdefault("reason", "success")
    if parsed.get("execution_status") == "completed" and trial_spec.get("model") and (
        parsed.get("observed_model") != trial_spec["model"] or parsed.get("host") != canonical
    ):
        parsed.update(execution_status="incomplete", reason="unverified_host_model")
    return parsed


def _run_attempts(command, workspace, active_env, profile, trial_spec, canonical):
    timeout_sec = int(max(1, round(float(profile.get("timeout_seconds", 1800)))))
    max_retries = int(profile.get("max_retries", 0))
    max_attempts = int(profile.get("max_total_attempts", max_retries + 1))
    attempts_cap = min(max_retries + 1, max_attempts)
    attempts = []
    parsed = {"execution_status": "failed", "reason": "retry_cap_exceeded"}
    for attempt_idx in range(attempts_cap):
        trace_file = workspace / f"trace_{attempt_idx + 1}.jsonl"
        with OwnedProcessJob(workspace, timeout_seconds=timeout_sec, env=active_env) as job:
            result = job.run(command, phase=f"trial_attempt_{attempt_idx + 1}")
            trace_file.write_text(result.get("stdout", ""), encoding="utf-8")
            attempts.append(_record_attempt(result, trace_file))
            parsed = _parse_attempt(result, trace_file, trial_spec, canonical)
            if result.get("exit_code") == 0 and not result.get("timed_out"):
                return attempts, parsed
    if parsed["execution_status"] != "timeout":
        parsed["reason"] = "retry_cap_exceeded"
    return attempts, parsed


def _trial_output(trial_spec, canonical, attempts, parsed) -> Dict[str, Any]:
    durations = [attempt["duration_seconds"] for attempt in attempts]
    latency = sum(durations) if durations and all(value is not None for value in durations) else None
    output = {
        "trial_id": trial_spec.get("trial_id"),
        "case_id": trial_spec.get("case_id"),
        "host": canonical,
        "execution_status": parsed["execution_status"],
        "reason": parsed["reason"],
        "timed_out": parsed["execution_status"] == "timeout",
        "attempts": attempts,
        "retries_count": max(0, len(attempts) - 1),
        "wall_latency_seconds": latency,
    }
    output.update({key: parsed[key] for key in (
        "response_text", "observed_model", "observed_trigger", "trigger_provenance",
        "tool_calls_count", "model_calls_count", "user_interventions_count", "tokens",
        "total_cost_usd", "billed_cost_usd", "normalized_metrics",
    ) if key in parsed})
    return output


def run_host_trial(
    host: str,
    trial_spec: Dict[str, Any],
    profile: Dict[str, Any],
    command_builder: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute bounded trial with retry constraints, recording all attempts."""
    canonical = canonical_host_name(host)
    if canonical not in SUPPORTED_HOSTS:
        return {"execution_status": "failed", "reason": "unsupported_host", "attempts": []}
    iso_ok, iso_reason = _verify_isolation(profile)
    if not iso_ok:
        return {"execution_status": "failed", "reason": iso_reason, "attempts": []}
    workspace = Path(profile["workspace_dir"]).resolve()
    active_env = dict(profile.get("env", {}))
    if "CLAUDECODE" in os.environ:
        active_env["CLAUDECODE"] = os.environ["CLAUDECODE"]
    command = trial_spec.get("command") or (command_builder(trial_spec, profile) if command_builder
                                             else build_host_command(canonical, trial_spec))
    attempts, parsed = _run_attempts(command, workspace, active_env, profile, trial_spec, canonical)
    return _trial_output(trial_spec, canonical, attempts, parsed)
