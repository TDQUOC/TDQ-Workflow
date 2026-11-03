"""
Unit tests for TDQ Stop-Batching Hook and Real-Time Gates:
- stop_batch_checker.py
- strategic_compact_gate.py
- doc_file_gate.py
"""

import os
import sys
from pathlib import Path

# Add hooks/scripts to sys.path
HOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks", "scripts")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

from stop_batch_checker import run_batch_checks  # pyright: ignore[reportMissingImports]
from strategic_compact_gate import (  # pyright: ignore[reportMissingImports]
    record_tool_call,
    check_compaction_advisory,
    reset_tracker,
    COMPACTION_THRESHOLD,
)
from doc_file_gate import is_markdown_allowed  # pyright: ignore[reportMissingImports]


def test_stop_batch_checker_empty_and_missing(tmp_path: Path):
    """Verify stop_batch_checker handles missing and empty buffer cleanly."""
    non_existent = tmp_path / "does_not_exist.txt"
    assert run_batch_checks(non_existent) == 0

    empty_buf = tmp_path / "empty_buffer.txt"
    empty_buf.write_text("   \n\n", encoding="utf-8")
    assert run_batch_checks(empty_buf) == 0
    assert not empty_buf.exists()


def test_stop_batch_checker_valid_python_files(tmp_path: Path):
    """Verify stop_batch_checker compiles python files and cleans buffer."""
    py_file = tmp_path / "sample.py"
    py_file.write_text("print('hello world')\n", encoding="utf-8")

    buf = tmp_path / "buffer.txt"
    buf.write_text(f"{py_file}\n", encoding="utf-8")

    exit_code = run_batch_checks(buf)
    assert exit_code == 0
    assert not buf.exists()


def test_strategic_compaction_weighted_counter(tmp_path: Path):
    """Verify weighted score calculation and natural boundary gating."""
    tracker_file = tmp_path / "tracker.json"
    reset_tracker(tracker_file)

    # Record tools with weights
    score1 = record_tool_call("Bash", tracker_path=tracker_file)  # weight 1
    assert score1 == 1

    score2 = record_tool_call("Read", tracker_path=tracker_file)  # weight 5
    assert score2 == 6

    score3 = record_tool_call("WebFetch", tracker_path=tracker_file)  # weight 10
    assert score3 == 16

    # Mid-implementation phase: should NEVER compact even if score is high
    for _ in range(6):
        record_tool_call("WebFetch", tracker_path=tracker_file)  # +60 -> score 76

    mid_impl_res = check_compaction_advisory("implement", tracker_path=tracker_file)
    assert not mid_impl_res["should_compact"]

    # Natural boundary phase: SHOULD compact when score >= COMPACTION_THRESHOLD
    boundary_res = check_compaction_advisory("plan_approved", tracker_path=tracker_file)
    assert boundary_res["should_compact"]
    assert boundary_res["score"] >= COMPACTION_THRESHOLD

    reset_tracker(tracker_file)
    assert not tracker_file.exists()


def test_doc_file_gate_placement_rules(tmp_path: Path):
    """Verify markdown placement rules enforce governed directory layout."""
    # Permitted locations
    assert is_markdown_allowed("docs/tdq/spec/sample.md", repo_root=tmp_path)
    assert is_markdown_allowed("docs/workinglog/2026-10-18.md", repo_root=tmp_path)
    assert is_markdown_allowed("skills/tdq-intake/SKILL.md", repo_root=tmp_path)
    assert is_markdown_allowed("agents/tdq-reviewer.md", repo_path=tmp_path) if hasattr(is_markdown_allowed, "repo_path") else is_markdown_allowed("agents/tdq-reviewer.md", repo_root=tmp_path)
    assert is_markdown_allowed("README.md", repo_root=tmp_path)
    assert is_markdown_allowed("CHANGELOG.md", repo_root=tmp_path)

    # Disallowed rogue locations
    assert not is_markdown_allowed("notes.md", repo_root=tmp_path)
    assert not is_markdown_allowed("src/components/SUMMARY.md", repo_root=tmp_path)
    assert not is_markdown_allowed("scripts/TODO.md", repo_root=tmp_path)

    # Non-markdown files are exempt
    assert is_markdown_allowed("src/index.ts", repo_root=tmp_path)
    assert is_markdown_allowed("scripts/worker.py", repo_root=tmp_path)
