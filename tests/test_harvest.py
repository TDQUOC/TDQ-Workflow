"""
Unit tests for TDQ Governed Continuous Learning CLI (scripts/tdq_harvest.py)
"""

import argparse
import os
import sys
from pathlib import Path

# Add scripts to sys.path
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from tdq_harvest import (  # pyright: ignore[reportMissingImports]
    extract_insights_from_text,
    cmd_scan,
    cmd_list,
    cmd_approve,
    cmd_reject,
    CANDIDATES_DIR,
    APPROVED_DIR,
)


def test_extract_insights_from_text():
    """Verify regex extraction of issue-resolution pairs from log texts."""
    sample_log = """
# Working Log 2026-10-18

Lỗi: Pyright unused import os in hook script
Khắc phục: Remove import os and recompile py_compile cleanly.

Lỗi: DocLint R11 failure due to concrete test path in spec
Khắc phục: Replace concrete test path with generalized testing directory description.
"""
    insights = extract_insights_from_text(sample_log, "docs/workinglog/2026-10-18.md")
    assert len(insights) == 2
    assert "Pyright unused import os" in insights[0]["issue"]
    assert "Remove import os" in insights[0]["resolution"]
    assert "DocLint R11 failure" in insights[1]["issue"]


def test_harvest_scan_and_lifecycle(tmp_path: Path):
    """Verify full lifecycle: scan -> list -> approve -> reject."""
    log_dir = tmp_path / "docs" / "workinglog"
    log_dir.mkdir(parents=True)
    log_file = log_dir / "2026-10-18.md"
    log_file.write_text(
        "Lỗi: Stop-batching buffer missing\nKhắc phục: Create parent dir and write file safely.\n",
        encoding="utf-8",
    )

    args = argparse.Namespace(verbose=True)

    # 1. Scan
    exit_code = cmd_scan(args, project_root=tmp_path)
    assert exit_code == 0

    staged_files = list((tmp_path / CANDIDATES_DIR).glob("*.md"))
    assert len(staged_files) == 1
    cand_id = staged_files[0].stem

    # 2. List
    list_code = cmd_list(args, project_root=tmp_path)
    assert list_code == 0

    # 3. Approve
    app_args = argparse.Namespace(candidate_id=cand_id, verbose=True)
    app_code = cmd_approve(app_args, project_root=tmp_path)
    assert app_code == 0

    approved_files = list((tmp_path / APPROVED_DIR).glob("*.md"))
    assert len(approved_files) == 1
    assert "status: approved" in approved_files[0].read_text(encoding="utf-8")
    assert not (tmp_path / CANDIDATES_DIR / f"{cand_id}.md").exists()

    # 4. Reject workflow on another candidate
    cand_file2 = tmp_path / CANDIDATES_DIR / "test_cand_2.md"
    cand_file2.write_text("status: candidate\n", encoding="utf-8")

    rej_args = argparse.Namespace(candidate_id="test_cand_2", verbose=True)
    rej_code = cmd_reject(rej_args, project_root=tmp_path)
    assert rej_code == 0
    assert not cand_file2.exists()
