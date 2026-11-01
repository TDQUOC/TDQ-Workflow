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

SUPPORTED_HOSTS = ("claude", "codex")
CHUNK_SIZE = 64 * 1024
DEFAULT_MAX_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_EVENTS = 50000

CLAUDE_EVENT_TYPES = {
    "api-request", "assistant", "user", "system", "progress", "result",
    "tool_use", "tool_result",
}
CODEX_EVENT_TYPES = {
    "session_meta", "response_item", "event_msg", "turn_context",
}
KNOWN_EVENT_TYPES = (
    CLAUDE_EVENT_TYPES | CODEX_EVENT_TYPES | tdq_transcript.UNTIMED_TYPES
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


def parse_trace_stream(
    path_or_lines: Union[str, Path, Iterable[Any]],
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_events: int = DEFAULT_MAX_EVENTS,
    expected_trigger: Optional[bool] = None,
) -> Dict[str, Any]:
    """Parse JSONL trace events line by line within explicit byte and count budgets."""
    total_bytes = 0
    event_count = 0
    detected_host: Optional[str] = None

    stats: Dict[str, Any] = {
        "tool_calls": 0,
        "model_calls": 0,
        "user_interventions": 0,
        "observed_trigger": False,
        "trigger_provenance": "unavailable",
    }
    tokens: Dict[str, Optional[int]] = {
        "input_tokens": None,
        "output_tokens": None,
        "cache_read_tokens": None,
        "cache_write_tokens": None,
    }

    for line_bytes, byte_len in _iter_lines(path_or_lines):
        total_bytes += byte_len
        event_count += 1
        if total_bytes > max_bytes or event_count > max_events:
            return {
                "execution_status": "failed",
                "reason": "budget_exceeded",
                "truncated": True,
                "paid_model_calls": 0,
            }

        line_str = line_bytes.decode("utf-8-sig", errors="replace").strip()
        if not line_str:
            continue

        try:
            record = json.loads(line_str)
        except Exception:
            return {
                "execution_status": "failed",
                "reason": "malformed_json",
                "paid_model_calls": 0,
            }

        if not isinstance(record, dict) or not isinstance(record.get("type"), str):
            return {
                "execution_status": "unknown_schema",
                "reason": "unknown_schema",
                "paid_model_calls": 0,
            }

        event_type = record["type"]
        if event_type not in KNOWN_EVENT_TYPES:
            return {
                "execution_status": "unknown_schema",
                "reason": "unknown_schema",
                "paid_model_calls": 0,
            }

        if event_type in CLAUDE_EVENT_TYPES:
            detected_host = "claude"
            _process_claude_event(record, stats, tokens)
        elif event_type in CODEX_EVENT_TYPES:
            detected_host = "codex"
            _process_codex_event(record, stats, tokens)

    raw_record: Dict[str, Any] = {
        "execution_status": "completed",
        "passed": True,
        "score": 1.0,
        "expected_trigger": expected_trigger,
        "observed_trigger": stats["observed_trigger"],
        "trigger_provenance": stats["trigger_provenance"],
        "tool_calls_count": stats["tool_calls"],
        "model_calls_count": stats["model_calls"],
        "user_interventions_count": stats["user_interventions"],
        "retries_count": 0,
        "tokens": tokens,
        "total_cost_usd": None,
        "billed_cost_usd": None,
    }

    normalized = tdq_eval_contract.normalize_trial_metrics(raw_record)

    return {
        "host": detected_host,
        "execution_status": "completed",
        "observed_trigger": stats["observed_trigger"],
        "trigger_provenance": stats["trigger_provenance"],
        "tool_calls_count": stats["tool_calls"],
        "model_calls_count": stats["model_calls"],
        "user_interventions_count": stats["user_interventions"],
        "tokens": tokens,
        "total_cost_usd": None,
        "billed_cost_usd": None,
        "normalized_metrics": normalized,
    }


def _record_attempt(
    result: Dict[str, Any],
    trace_path: Path,
) -> Dict[str, Any]:
    trace_sha = hash_file_streaming(trace_path) if trace_path.exists() else "0" * 64
    return {
        "exit_code": result.get("exit_code"),
        "timed_out": bool(result.get("timed_out")),
        "duration_seconds": result.get("duration_seconds", 0.0),
        "cleanup_complete": bool(result.get("cleanup_complete")),
        "ownership": result.get("ownership", {}),
        "raw_trace_sha256": trace_sha,
    }


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

    timeout_sec = int(max(1, round(float(profile.get("timeout_seconds", 1800)))))
    max_retries = int(profile.get("max_retries", 0))
    max_attempts = int(profile.get("max_total_attempts", max_retries + 1))
    attempts_cap = min(max_retries + 1, max_attempts)

    workspace = Path(profile["workspace_dir"]).resolve()
    active_env = dict(profile.get("env", {}))
    command = trial_spec.get("command") or (command_builder(trial_spec, profile) if command_builder else [canonical])

    attempts: List[Dict[str, Any]] = []
    final_execution_status = "failed"
    final_reason = "attempts_exhausted"
    last_parsed: Optional[Dict[str, Any]] = None

    for attempt_idx in range(attempts_cap):
        trace_file = workspace / f"trace_{attempt_idx + 1}.jsonl"
        with OwnedProcessJob(workspace, timeout_seconds=timeout_sec, env=active_env) as job:
            res = job.run(command, phase=f"trial_attempt_{attempt_idx + 1}")
            stdout_text = res.get("stdout", "")
            trace_file.write_text(stdout_text, encoding="utf-8")
            attempt_rec = _record_attempt(res, trace_file)
            attempts.append(attempt_rec)

            if res.get("timed_out"):
                final_execution_status = "timeout"
                final_reason = "process_timeout"
            elif res.get("exit_code") == 0:
                parsed = parse_trace_stream(trace_file, expected_trigger=trial_spec.get("expected_trigger"))
                last_parsed = parsed
                final_execution_status = parsed.get("execution_status", "completed")
                final_reason = parsed.get("reason", "success")
                break
            else:
                final_execution_status = "failed"
                final_reason = res.get("reason", f"exit_{res.get('exit_code')}")

    if final_execution_status != "completed" and len(attempts) >= attempts_cap:
        if final_execution_status != "timeout":
            final_reason = "retry_cap_exceeded"

    output: Dict[str, Any] = {
        "trial_id": trial_spec.get("trial_id"),
        "case_id": trial_spec.get("case_id"),
        "host": canonical,
        "execution_status": final_execution_status,
        "reason": final_reason,
        "timed_out": final_execution_status == "timeout",
        "attempts": attempts,
        "retries_count": max(0, len(attempts) - 1),
    }

    if last_parsed and final_execution_status == "completed":
        output.update({
            "observed_trigger": last_parsed.get("observed_trigger"),
            "trigger_provenance": last_parsed.get("trigger_provenance"),
            "tool_calls_count": last_parsed.get("tool_calls_count"),
            "model_calls_count": last_parsed.get("model_calls_count"),
            "tokens": last_parsed.get("tokens"),
            "normalized_metrics": last_parsed.get("normalized_metrics"),
        })

    return output
