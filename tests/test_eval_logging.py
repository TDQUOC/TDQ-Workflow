"""Unit tests for Eval logging service.

Verifies:
1. Log service enabled by default across tdq_eval_contract, tdq_eval_hosts, tdq_skill_eval.
2. Clean suppression via TDQ_LOG=0 / TDQ_EVAL_LOG=0 (and false/off values).
3. ISO UTC timestamp formatting `[YYYY-MM-DDTHH:MM:SS...]` and allowed log levels.
4. Metadata field whitelisting (experiment, cell, trial, reason, cleanup).
5. Strict redaction of sensitive tokens (secret, token, prompt, payload, bearer, password, api_key, sk-).
6. Newline injection prevention via character escaping.
7. Subprocess CLI integration and env var propagation.
"""

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import tdq_eval_contract
import tdq_eval_hosts
import tdq_skill_eval

LOG_FUNCS = [
    tdq_eval_contract.log,
    tdq_eval_hosts.log,
    tdq_skill_eval._log,
]

ISO_UTC_PATTERN = re.compile(
    r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)?\]"
)

SENSITIVE_PROBES = [
    ("secret_phrase", "contains sensitive secret word"),
    ("token_xyz", "authorization token value"),
    ("my_prompt", "system prompt instructions"),
    ("big_payload", "request payload body"),
    ("bearer_token", "Bearer eyJhbGciOi..."),
    ("admin_password", "database password123"),
    ("api_key_val", "api_key=ab12cd34"),
    ("api-key-val", "api-key: xyz"),
    ("sk_key", "sk-proj-1234567890abcdef"),
]


@pytest.fixture(autouse=True)
def clean_log_env(monkeypatch):
    """Ensure clean default environment with log enabled unless test specifies."""
    monkeypatch.delenv("TDQ_LOG", raising=False)
    monkeypatch.delenv("TDQ_EVAL_LOG", raising=False)


@pytest.mark.parametrize("log_func", LOG_FUNCS)
def test_default_logging_enabled(log_func, capsys):
    """Log service must be active by default without explicit env vars."""
    log_func("khoi-tao-danh-gia", muc="thong-tin")
    captured = capsys.readouterr()
    err = captured.err.strip()

    assert err != ""
    assert ISO_UTC_PATTERN.search(err) is not None
    assert "thong-tin: khoi-tao-danh-gia" in err


@pytest.mark.parametrize("log_func", LOG_FUNCS)
@pytest.mark.parametrize("muc", ["thong-tin", "canh-bao", "loi"])
def test_allowed_log_levels(log_func, muc, capsys):
    """Supported log levels (thong-tin, canh-bao, loi) must be accepted and formatted."""
    log_func(f"thong diep {muc}", muc=muc)
    captured = capsys.readouterr()
    err = captured.err.strip()

    assert err != ""
    assert f"{muc}: thong diep {muc}" in err


@pytest.mark.parametrize("log_func", LOG_FUNCS)
@pytest.mark.parametrize("bad_muc", ["debug", "warn", "error", "INFO", "CRITICAL", "", "unknown"])
def test_invalid_log_level_rejected(log_func, bad_muc):
    """Unsupported log levels must raise ValueError."""
    with pytest.raises(ValueError, match="invalid log level"):
        log_func("thong diep sai muc", muc=bad_muc)


@pytest.mark.parametrize("log_func", LOG_FUNCS)
@pytest.mark.parametrize("env_var", ["TDQ_LOG", "TDQ_EVAL_LOG"])
@pytest.mark.parametrize("off_val", ["0", "false", "off", "0 ", "FALSE", "Off"])
def test_clean_silencing_via_env(log_func, env_var, off_val, monkeypatch, capsys):
    """Setting TDQ_LOG=0 or TDQ_EVAL_LOG=0 (or false/off) must cleanly silence stderr."""
    monkeypatch.setenv(env_var, off_val)
    log_func("thong diep bi tat", muc="thong-tin", experiment="exp-1")
    captured = capsys.readouterr()

    assert captured.err == ""
    assert captured.out == ""


@pytest.mark.parametrize("log_func", LOG_FUNCS)
def test_either_env_var_can_silence(log_func, monkeypatch, capsys):
    """If either TDQ_LOG=0 or TDQ_EVAL_LOG=0 is set, logging must be silenced."""
    monkeypatch.setenv("TDQ_LOG", "1")
    monkeypatch.setenv("TDQ_EVAL_LOG", "0")
    log_func("tat qua eval", muc="thong-tin")
    assert capsys.readouterr().err == ""

    monkeypatch.setenv("TDQ_LOG", "0")
    monkeypatch.setenv("TDQ_EVAL_LOG", "1")
    log_func("tat qua tdq_log", muc="thong-tin")
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("log_func", LOG_FUNCS)
def test_metadata_fields_whitelisting(log_func, capsys):
    """Only documented metadata fields (experiment, cell, trial, reason, cleanup) must be emitted."""
    log_func(
        "kiem tra metadata",
        muc="thong-tin",
        experiment="exp-001",
        cell="claude:sonnet",
        trial="trial-42",
        reason="baseline_eval",
        cleanup="cleanup_proc",
        # Disallowed metadata fields:
        user="admin",
        secret_token="leaked",
        raw_prompt="banned",
        arbitrary_data="ignore_me",
    )
    captured = capsys.readouterr()
    err = captured.err.strip()

    assert "experiment=exp-001" in err
    assert "cell=claude:sonnet" in err
    assert "trial=trial-42" in err
    assert "reason=baseline_eval" in err
    assert "cleanup=cleanup_proc" in err

    assert "user=" not in err
    assert "secret_token=" not in err
    assert "raw_prompt=" not in err
    assert "arbitrary_data=" not in err


@pytest.mark.parametrize("log_func", LOG_FUNCS)
@pytest.mark.parametrize("label,probe", SENSITIVE_PROBES)
def test_redaction_sensitive_message(log_func, label, probe, capsys):
    """Messages containing sensitive terms must be replaced by [redacted], never printed raw."""
    log_func(probe, muc="thong-tin")
    captured = capsys.readouterr()
    err = captured.err.strip()

    assert "[redacted]" in err
    assert probe not in err
    assert not re.search(r"secret|token|prompt|payload|bearer|password|api.?key|sk-", err, re.I)


@pytest.mark.parametrize("log_func", LOG_FUNCS)
@pytest.mark.parametrize("label,probe", SENSITIVE_PROBES)
def test_redaction_sensitive_metadata_values(log_func, label, probe, capsys):
    """Metadata values containing sensitive terms must be replaced by [redacted]."""
    log_func(
        "trang thai van hanh",
        muc="canh-bao",
        experiment=probe,
        reason=f"Ly do: {probe}",
    )
    captured = capsys.readouterr()
    err = captured.err.strip()

    assert "experiment=[redacted]" in err
    assert "reason=[redacted]" in err
    assert probe not in err


@pytest.mark.parametrize("log_func", LOG_FUNCS)
def test_newline_sanitization(log_func, capsys):
    """Newlines and carriage returns must be escaped to prevent log injection."""
    log_func("dong 1\ndong 2\rdong 3", muc="thong-tin", reason="ly do\ntren 2 dong")
    captured = capsys.readouterr()
    lines = captured.err.strip().splitlines()

    # Log entry must be strictly 1 physical line in stderr
    assert len(lines) == 1
    assert r"dong 1\ndong 2\rdong 3" in lines[0]
    assert r"ly do\ntren 2 dong" in lines[0]


def test_cli_subprocess_logging_toggle():
    """Subprocess CLI execution must log by default and silence cleanly under TDQ_EVAL_LOG=0."""
    with tempfile.TemporaryDirectory(prefix="tdq-eval-logging-") as tmpdir:
        tmp_path = Path(tmpdir)
        plan_path = tmp_path / "valid_plan.json"
        dummy_plan = {
            "plan_version": "v1",
            "experiment_id": "exp-log-test",
            "targets": {"skills/tdq-build/SKILL.md": "a" * 64},
            "base_identity": "b" * 40,
            "candidate_identity": "c" * 64,
            "change_kind": "behavioral",
            "hypothesis": "Verify logging",
            "evaluation_kind": "mechanism",
            "corpus_id": "corpus-1",
            "dev_cases_sha256": "d" * 64,
            "holdout_cases_sha256": "e" * 64,
            "rubric_version": "v1",
            "scorer_version": "v1",
            "expected_triggers": ["case-1"],
            "negative_cases": ["case-2"],
            "required_metrics": ["trigger_accuracy"],
            "cells": [{
                "host": "fixture",
                "model": "offline-model-v1",
                "permission_profile": "isolated",
                "tool_aliases": {"shell": ["Bash"]},
                "cache_profile": "cold",
            }],
            "repetitions": 1,
            "order_policy": "AB_BA",
            "thresholds": {"min_pairs": 1},
        }
        with plan_path.open("w", encoding="utf-8") as stream:
            json.dump(dummy_plan, stream, indent=2)

        script_path = str(SCRIPTS / "tdq_skill_eval.py")

        # 1. Default run -> stderr must contain timestamp and 'thong-tin: plan validated'
        env_default = dict(os.environ)
        env_default.pop("TDQ_LOG", None)
        env_default.pop("TDQ_EVAL_LOG", None)
        env_default["PYTHONPATH"] = str(SCRIPTS)

        proc_default = subprocess.run(
            [sys.executable, script_path, "plan", "--plan", str(plan_path)],
            capture_output=True,
            text=True,
            env=env_default,
            cwd=str(ROOT),
        )
        assert proc_default.returncode == 0
        assert "thong-tin: plan validated" in proc_default.stderr
        assert ISO_UTC_PATTERN.search(proc_default.stderr.strip()) is not None

        # 2. Silenced run with TDQ_EVAL_LOG=0
        env_silenced = dict(env_default)
        env_silenced["TDQ_EVAL_LOG"] = "0"

        proc_silenced = subprocess.run(
            [sys.executable, script_path, "plan", "--plan", str(plan_path)],
            capture_output=True,
            text=True,
            env=env_silenced,
            cwd=str(ROOT),
        )
        assert proc_silenced.returncode == 0
        assert proc_silenced.stderr == ""

        # 3. Silenced run with TDQ_LOG=0
        env_tdq_log_off = dict(env_default)
        env_tdq_log_off["TDQ_LOG"] = "0"

        proc_tdq_off = subprocess.run(
            [sys.executable, script_path, "plan", "--plan", str(plan_path)],
            capture_output=True,
            text=True,
            env=env_tdq_log_off,
            cwd=str(ROOT),
        )
        assert proc_tdq_off.returncode == 0
        assert proc_tdq_off.stderr == ""
