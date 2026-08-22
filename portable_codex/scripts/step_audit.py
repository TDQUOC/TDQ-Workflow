#!/usr/bin/env python3
"""step_audit.py — measure the STEP cost of one Claude Code session.

Unlike `token_audit.py`: that file measures tokens (layer 3 — context cost), this one measures
the number of steps (layer 2 — runtime). One tool call = one round-trip; the total time of a
request is DIRECTLY proportional to the step count, so the step count is the main speed variable.

The five metrics printed:
      1. Step count         — the number of distinct model `requestId`s (each one an API call).
            NOT counted per jsonl record: Claude Code splits one answer across several records
            and copies `usage` into each, so counting records inflates the step count.
      2. Tool calls per turn — total tool calls / turns THAT HAVE tool calls. A value of 1.00
            means the batch-into-one-turn rule has never once been applied.
      3. Repeat Read        — how many times a file already read is read again in one session.
      4. Median latency     — seconds between the previous record and the next model turn.
      5. p90 latency        — nearest-rank: element ceil(0.9 × n) after sorting.

Usage:
        python3 scripts/step_audit.py                       # current project, 3 latest sessions
    python3 scripts/step_audit.py --sessions 5
    python3 scripts/step_audit.py --project ~/Documents/Heineken_AppKetNoi
    python3 scripts/step_audit.py --transcript-dir <dir>

Env: TDQ_LOG=0 turns the progress log off (log to stderr, table to stdout).
Exit: 0 even when no session is found (a warning only). 2 = bad syntax.
"""

import argparse
import datetime
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from token_audit import default_transcript_dir, find_sessions, iter_events  # noqa: E402

# A gap larger than this threshold means the user went away and came back, not model
# latency — dropped from the statistics so the median is not skewed.
MAX_GAP_SECONDS = 300


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _log(message):
    """Log progress to stderr with an ISO timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


# --------------------------------------------------------------- read & measure

def _parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _blocks(event):
    message = event.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    return content if isinstance(content, list) else []


def _has_usage(event):
    message = event.get("message")
    return isinstance(message, dict) and isinstance(message.get("usage"), dict)


def _request_id(event, index):
    """One model turn = one `requestId`.

    Claude Code SPLITS every content block of one answer into its own jsonl record (text on one
    line, each tool_use on a line) and copies `usage` into every line. Counting records makes one
    turn firing 3 tool calls look exactly like 3 turns firing 1 — the "tool calls per turn" metric
    always comes out at 1.00 whether the model batched or not. Grouping by `requestId` is what
    gives the real number.
    """
    message = event.get("message")
    rid = event.get("requestId") or (message or {}).get("id")
    return rid or f"_no_request_{index}"


def scan(path):
    """Read the transcript LINE by LINE (never loading the whole file) and collect the raw data."""
    stats = {"steps": 0, "tool_calls": 0, "turns_with_tools": 0,
             "repeat_reads": 0, "latencies": []}
    seen_reads = set()
    turns_with_tools = set()
    prev_time = None
    current_request = None
    for index, event in enumerate(iter_events(path)):
        now = _parse_time(event.get("timestamp"))
        is_step = event.get("type") == "assistant" and _has_usage(event)
        if is_step:
            rid = _request_id(event, index)
            if rid != current_request:            # first record of a new turn
                current_request = rid
                stats["steps"] += 1
                if prev_time and now:
                    gap = (now - prev_time).total_seconds()
                    if 0 <= gap <= MAX_GAP_SECONDS:
                        stats["latencies"].append(gap)
            for block in _blocks(event):
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                stats["tool_calls"] += 1
                turns_with_tools.add(rid)
                if block.get("name") == "Read":
                    target = (block.get("input") or {}).get("file_path")
                    if target:
                        if target in seen_reads:
                            stats["repeat_reads"] += 1
                        seen_reads.add(target)
        if now:
            prev_time = now
    stats["turns_with_tools"] = len(turns_with_tools)
    return stats


def merge(all_stats):
    total = {"steps": 0, "tool_calls": 0, "turns_with_tools": 0,
             "repeat_reads": 0, "latencies": []}
    for stats in all_stats:
        for key in ("steps", "tool_calls", "turns_with_tools", "repeat_reads"):
            total[key] += stats[key]
        total["latencies"].extend(stats["latencies"])
    return total


def percentile(values, share):
    """Nearest-rank: element ceil(share × n) of the sorted series (1-indexed)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(share * len(ordered)))
    return float(ordered[min(rank, len(ordered)) - 1])


def median(values):
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2


def report(total):
    """The five metrics, as a markdown table to paste straight into the QC file."""
    per_turn = (total["tool_calls"] / total["turns_with_tools"]
                if total["turns_with_tools"] else 0.0)
    lines = [
        "| Metric | Value |",
        "|---|---|",
        f"| Model steps | {total['steps']} |",
        f"| Tool calls per turn | {per_turn:.2f} ({total['turns_with_tools']} turn(s)) |",
        f"| Repeat Read of one file | {total['repeat_reads']} |",
        f"| Median latency | {median(total['latencies']):.1f} s |",
        f"| p90 latency | {percentile(total['latencies'], 0.9):.1f} s |",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="step_audit.py",
        description="Measure the step cost (runtime layer) of a Claude Code session.")
    parser.add_argument("--transcript-dir",
                        help="folder holding the .jsonl files; defaults to one derived from the project")
    parser.add_argument("--project",
                        help="project folder to measure; defaults to the current folder")
    parser.add_argument("--sessions", type=int, default=3,
                        help="how many latest sessions to measure (default 3)")
    args = parser.parse_args(argv)

    transcript_dir = args.transcript_dir or default_transcript_dir(args.project)
    paths = find_sessions(transcript_dir, args.sessions)
    if not paths:
        _log(f"no session found in {transcript_dir}")
        print("No transcript to measure.")
        return 0

    all_stats = []
    for path in paths:
        _log(f"reading {os.path.basename(path)}")
        all_stats.append(scan(path))
    total = merge(all_stats)
    _log(f"done {len(paths)} session(s) · {total['steps']} step(s)")
    print(report(total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
