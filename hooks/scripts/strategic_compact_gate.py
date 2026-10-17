#!/usr/bin/env python3
"""
Strategic Compaction Gate: Tracks weighted tool calls and advises strategic context compaction
ONLY at natural gate boundaries (post-spec, post-plan, wave-transitions), preventing mid-task disruption.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

TRACKER_FILE = Path(".claude/tmp/tool_weights_tracker.json")
NATURAL_BOUNDARIES = {"spec", "plan", "wave_transition", "spec_approved", "plan_approved"}

# Weighted tool costs (Context consumption burden)
TOOL_WEIGHTS = {
    "WebFetch": 10,
    "WebSearch": 8,
    "Read": 5,
    "mcp__lsp__explore": 4,
    "mcp__lsp__inspect_symbol": 3,
    "Grep": 2,
    "Glob": 2,
    "Edit": 2,
    "Write": 2,
    "Bash": 1,
    "PowerShell": 1,
}

COMPACTION_THRESHOLD = 60


def load_tracker(tracker_path: Path = TRACKER_FILE) -> Dict[str, Any]:
    """Load existing tool call tracker from temporary cache."""
    if not tracker_path.exists():
        return {"total_score": 0, "tool_counts": {}}
    try:
        return json.loads(tracker_path.read_text(encoding="utf-8"))
    except Exception:
        return {"total_score": 0, "tool_counts": {}}


def save_tracker(data: Dict[str, Any], tracker_path: Path = TRACKER_FILE) -> None:
    """Save tool call tracker to temporary cache."""
    tracker_path.parent.mkdir(parents=True, exist_ok=True)
    tracker_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_tool_call(tool_name: str, tracker_path: Path = TRACKER_FILE) -> int:
    """Increment tool call count and update weighted score."""
    data = load_tracker(tracker_path)
    weight = TOOL_WEIGHTS.get(tool_name, 1)

    counts = data.get("tool_counts", {})
    counts[tool_name] = counts.get(tool_name, 0) + 1
    data["tool_counts"] = counts
    data["total_score"] = data.get("total_score", 0) + weight

    save_tracker(data, tracker_path)
    return data["total_score"]


def check_compaction_advisory(phase: str, tracker_path: Path = TRACKER_FILE) -> Dict[str, Any]:
    """Evaluate whether strategic compaction is recommended at this phase."""
    data = load_tracker(tracker_path)
    score = data.get("total_score", 0)

    # Only recommend at natural boundaries, never mid-implementation
    if phase in NATURAL_BOUNDARIES and score >= COMPACTION_THRESHOLD:
        return {
            "should_compact": True,
            "score": score,
            "message": (
                f"[TDQ Strategic Compaction Advisory] Context burden reached {score} points. "
                "You are at a natural phase boundary. Consider compacting conversation context "
                "before starting heavy execution to maintain optimal reasoning quality."
            ),
        }

    return {"should_compact": False, "score": score, "message": "Context within optimal limits."}


def reset_tracker(tracker_path: Path = TRACKER_FILE) -> None:
    """Reset tracker after a context compaction or request reset."""
    tracker_path.unlink(missing_ok=True)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "record":
        tool = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
        score = record_tool_call(tool)
        print(f"Recorded {tool}. Current burden score: {score}")
    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        phase = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        res = check_compaction_advisory(phase)
        if res["should_compact"]:
            print(res["message"], file=sys.stderr)
            sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
