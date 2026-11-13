"""V3 Stress & Live Transcript Verification: 8-process NTFS concurrency + real brain transcript."""
import json
import multiprocessing
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_DIR = WORKSPACE / "plugins" / "tdq-workflow"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
HOOKS_DIR = PLUGIN_DIR / "hooks" / "scripts"
REAL_SUBAGENT_TRANSCRIPT = Path(
    r"C:\Users\admin\.gemini\antigravity\brain\3b9ddf2b-58ed-4fbd-86f1-72cd99655459\.system_generated\logs\transcript.jsonl"
)


def _worker_observe(args):
    cwd_str, hook_dir_str, worker_id, count = args
    sys.path.insert(0, hook_dir_str)
    import _common
    for idx in range(count):
        _common.observe(cwd_str, {"conversation_id": "stress-conv"}, "stress", worker=worker_id, seq=idx)


def test_ntfs_8process_320_writes_zero_loss(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    tasks = [(str(tmp_path), str(HOOKS_DIR), w, 40) for w in range(8)]
    with ctx.Pool(processes=8) as pool:
        pool.map(_worker_observe, tasks)

    shard = tmp_path / "docs" / "tdq" / ".tdq-runtime" / "turns-stress-conv.jsonl"
    assert shard.is_file()
    lines = [l for l in shard.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 320, f"Expected 320 rows, got {len(lines)}"
    parsed = [json.loads(l) for l in lines]
    assert len({(r["worker"], r["seq"]) for r in parsed}) == 320


def test_real_antigravity_transcript_parsing():
    assert REAL_SUBAGENT_TRANSCRIPT.is_file(), "Real subagent transcript missing for empirical test"
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    import tdq_transcript

    content = REAL_SUBAGENT_TRANSCRIPT.read_bytes()
    trace = tdq_transcript._parse_snapshot(content)
    assert len(trace) > 0
    hosts = {h for row in trace for h in row[0].get("_hosts", [])}
    caps = {c for row in trace for c in row[1].get("_capabilities", [])}
    assert "antigravity" in hosts
    assert "tool" in caps
    assert tdq_transcript._decode_double_json('{"CommandLine": "py -3 --version"}') == {"CommandLine": "py -3 --version"}
