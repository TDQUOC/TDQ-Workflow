#!/usr/bin/env python3
"""Measure request wall time and the union of verified host timing spans.

Schema v2 never estimates model compute time from assistant-message gaps.
API latency includes network/provider time; tool time is the host's wait.
Unattributed wall time is not assumed to be user idle or model compute time.
Only tdq_state writes state. This module appends historical timing records.

Usage:
        python3 scripts/tdq_timing.py show              # markdown table of the open request
        python3 scripts/tdq_timing.py show --json       # the same data as JSON
        python3 scripts/tdq_timing.py close             # close the books: append 1 line to timing.jsonl

Env: TDQ_PROJECT_DIR picks the project · TDQ_LOG=0 turns the progress log off (log to stderr).
Exit: 0 even with no open request or no transcript found. 2 = bad syntax.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tdq_state  # noqa: E402
from tdq_transcript import (  # noqa: E402
    claude_transcript_dir as default_transcript_dir,  # noqa: F401 - legacy callers
    parse_timestamp,
    read_transcripts,
)

TIMING_REL = os.path.join("docs", "tdq", "timing.jsonl")
EXIT_SYNTAX = 2
METRIC_NAMES = {"api": "api_request_seconds", "tool": "tool_call_seconds",
                "job": "background_job_seconds", "observed": "observed_union_seconds"}
METRIC_LABELS = ("API request", "Tool wait", "Background job", "Observed union", "Unattributed")
METRIC_KEYS = tuple(METRIC_NAMES.values()) + ("unattributed_seconds",)


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log progress to stderr with a timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------------- formatting

def dinh_dang(giay):
    """Seconds → a human string. `None` → '—' (not measurable, different from 0)."""
    if giay is None:
        return "—"
    giay = int(round(giay))
    if giay < 60:
        return f"{giay}s"
    phut, du = divmod(giay, 60)
    if phut < 60:
        return f"{phut} min" if du < 30 else f"{phut + 1} min"
    gio, phut = divmod(phut, 60)
    return f"{gio}h" if phut == 0 else f"{gio}h {phut:02d}min"


# ------------------------------------------------------------------ phase windows

def _aware_time(value):
    if isinstance(value, datetime.datetime):
        return value.astimezone(datetime.timezone.utc) if value.utcoffset() is not None else None
    return parse_timestamp(value)


def _phase_mark(item):
    if not isinstance(item, dict):
        return None
    phase = item.get("phase")
    at = parse_timestamp(item.get("at"))
    return (phase, at) if isinstance(phase, str) and phase and at is not None else None


def _phase_marks(history, diagnostics):
    if not isinstance(history, list):
        diagnostics.append("invalid_phase_history")
        return []
    marks = []
    for item in history:
        mark = _phase_mark(item)
        if mark is None:
            diagnostics.append("invalid_phase_mark")
        elif marks and mark[1] < marks[-1][1]:
            diagnostics.append("phase_out_of_order")
        elif marks and mark == marks[-1]:
            diagnostics.append("duplicate_phase_mark")
        else:
            marks.append(mark)
    return marks


def _phase_window(phase, at, stop, start, end):
    left, right = max(start, at), min(end, stop)
    # Retain instantaneous transitions inside the window, not old entries
    # that only touch its boundary. Ordering resolves equal timestamps.
    if left < right or (left == right and start <= at < end):
        return phase, left, right
    return None


def cua_so_phase(state, ket_thuc, diagnostics=None):
    """Return ordered, disjoint phase windows clipped to the request [start,end)."""
    issues = diagnostics if diagnostics is not None else []
    start, end = _aware_time(state.get("started_at")), _aware_time(ket_thuc)
    if start is None or end is None or end < start:
        issues.append("invalid_request_window")
        return []
    marks = _phase_marks(state.get("phase_history", []), issues)
    windows = []
    for index, (phase, at) in enumerate(marks):
        stop = marks[index + 1][1] if index + 1 < len(marks) else end
        window = _phase_window(phase, at, stop, start, end)
        if window is not None:
            windows.append(window)
    return windows


def _merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def _clip_intervals(intervals, start, end):
    return [(max(left, start), min(right, end)) for left, right in intervals
            if right > start and left < end]


def _phase_intersections(intervals, windows):
    """Sweep two sorted lists in O(intervals + windows + intersections)."""
    parts = [[] for _ in windows]
    i = j = 0
    while i < len(intervals) and j < len(windows):
        start, end = intervals[i]
        _, left, right = windows[j]
        if max(start, left) < min(end, right):
            parts[j].append((max(start, left), min(end, right)))
        if end <= right:
            i += 1
        else:
            j += 1
    return parts


def _prepared_intervals(spans):
    intervals = {kind: [] for kind in ("api", "tool", "job")}
    for span in spans:
        intervals[span["kind"]].append((span["start"], span["end"]))
    merged = {kind: _merge_intervals(values) for kind, values in intervals.items()}
    merged["observed"] = _merge_intervals(pair for values in merged.values() for pair in values)
    return merged


def _observation_quality(qualities):
    supported = [value for value in qualities.values() if value["quality"] != "unavailable"]
    if not supported:
        return {"quality": "unavailable", "reason": "no_usable_observations"}
    partial = [value["reason"] for value in supported if value["quality"] == "partial"]
    return {"quality": "partial" if partial else "complete",
            "reason": ";".join(sorted(set(partial))) if partial else "union_of_supported_observations"}


def _metric(intervals, quality, diagnostics):
    level, reason = quality["quality"], quality["reason"]
    if level == "unavailable":
        return {"seconds": None, "quality": level, "reason": reason}
    if diagnostics:
        level, reason = "partial", reason + ";" + ",".join(sorted(set(diagnostics)))
    seconds = sum((end - start).total_seconds() for start, end in intervals)
    if level == "partial" and not intervals:
        seconds = None
        reason += ";no_confirmed_span_in_window"
    return {"seconds": seconds, "quality": level, "reason": reason}


def _metrics(intervals, wall, qualities, diagnostics=()):
    if wall is None:
        return {key: {"seconds": None, "quality": "unavailable", "reason": "invalid_request_window"}
                for key in METRIC_KEYS}
    coverage = dict(qualities, observed=_observation_quality(qualities))
    metrics = {name: _metric(intervals[kind], coverage[kind], diagnostics)
               for kind, name in METRIC_NAMES.items()}
    observed = metrics["observed_union_seconds"]
    seconds = None if observed["seconds"] is None else max(0.0, wall - observed["seconds"])
    metrics["unattributed_seconds"] = {"seconds": seconds, "quality": observed["quality"],
                                       "reason": "wall_minus_observed_union;" + observed["reason"]}
    return metrics


def _phase_totals(windows, intervals, qualities, diagnostics):
    intersections = {kind: _phase_intersections(values, windows) for kind, values in intervals.items()}
    groups = {}
    for index, (phase, start, end) in enumerate(windows):
        row = groups.setdefault(phase, {"phase": phase, "treo_tuong_giay": 0.0,
                                       "model_giay": None, "so_lan": 0,
                                       "_intervals": {kind: [] for kind in intervals}})
        row["treo_tuong_giay"] += (end - start).total_seconds()
        row["so_lan"] += 1
        for kind in intervals:
            row["_intervals"][kind].extend(intersections[kind][index])
    for row in groups.values():
        row["metrics"] = _metrics(row.pop("_intervals"), row["treo_tuong_giay"], qualities, diagnostics)
    return list(groups.values())


def tong_hop(state, ket_thuc, transcript_dir=None, *, project_dir=None, host="auto", session_ids=None,
             cache="off", cache_stats=None):
    """Return timing v2; retain the legacy positional caller and never write state."""
    if not state.get("active_request"):
        return None
    start, end = _aware_time(state.get("started_at")), _aware_time(ket_thuc)
    diagnostics = []
    windows = cua_so_phase(state, ket_thuc, diagnostics)
    source = read_transcripts(project_dir or tdq_state.resolve_project_dir(), transcript_dir,
                              host=host, session_ids=session_ids, cache=cache,
                              request_id=state["active_request"], cache_stats=cache_stats)
    intervals = _prepared_intervals(source["spans"])
    wall = None
    if start is not None and end is not None and end >= start:
        wall = (end - start).total_seconds()
        intervals = {kind: _clip_intervals(values, start, end) for kind, values in intervals.items()}
    phases = _phase_totals(windows, intervals, source["quality"], diagnostics)
    for reason in sorted(set(diagnostics)):
        _log(f"timing diagnostics: {reason}")
    return {"schema_version": 2, "slug": state["active_request"], "lane": state.get("lane"),
            "started_at": state.get("started_at"),
            "closed_at": ket_thuc.isoformat() if isinstance(ket_thuc, datetime.datetime) else ket_thuc,
            "treo_tuong_giay": wall, "model_giay": None, "phases": phases,
            "metrics": _metrics(intervals, wall, source["quality"]),
            "sources": source["sources"], "attribution": source["attribution"],
            "current_phase": windows[-1][0] if windows else None,
            "diagnostics": sorted(set(diagnostics))}


def _legacy_markdown(data):
    lines = ["| Phase | Wall clock | legacy assistant-gap estimate | Times entered |",
             "|---|---|---|---|"]
    rows = data["phases"] + [dict(data, phase="Total", so_lan="")]
    for row in rows:
        lines.append(f"| {row['phase']} | {dinh_dang(row['treo_tuong_giay'])} | "
                     f"{dinh_dang(row.get('model_giay'))} | {row['so_lan']} |")
    return lines


def _metric_text(metric):
    return f"{dinh_dang(metric['seconds'])} [{metric['quality']}]"


def bang_markdown(so_lieu):
    """Present the same measured values and quality as JSON, including v1 labels."""
    lines = [f"Request `{so_lieu['slug']}` · lane {so_lieu['lane'] or '—'} · "
             f"opened at {so_lieu['started_at'] or '—'}", ""]
    if so_lieu.get("schema_version", 1) != 2:
        return "\n".join(lines + _legacy_markdown(so_lieu))
    columns = ("Phase", "Wall clock", *METRIC_LABELS, "Times entered")
    lines.extend(["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)])
    for row in so_lieu["phases"] + [dict(so_lieu, phase="Total", so_lan="")]:
        cells = [row["phase"], dinh_dang(row["treo_tuong_giay"])]
        cells.extend(_metric_text(row["metrics"][key]) for key in METRIC_KEYS)
        lines.append("| " + " | ".join(cells + [str(row["so_lan"])]) + " |")
    lines.extend(["", "Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; "
                  "tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.",
                  f"Transcript attribution: {so_lieu['attribution']}. Complete covers selected supported observations only."])
    lines.extend(f"- {key}: {so_lieu['metrics'][key]['reason']}" for key in METRIC_KEYS)
    if so_lieu["diagnostics"]:
        lines.append("Phase diagnostics: " + ", ".join(so_lieu["diagnostics"]))
    return "\n".join(lines)


def _current_phase_clock(data):
    current = data.get("current_phase")
    row = next((item for item in data["phases"] if item["phase"] == current), None)
    if row is None:
        return data["slug"]
    observed = _metric_text(row["metrics"]["observed_union_seconds"])
    return f"{current} (all entries) wall {dinh_dang(row['treo_tuong_giay'])} · phase observed {observed}"


def dong_ho_ngan(so_lieu):
    """Return a single-line status using the same values and completeness labels."""
    wall = dinh_dang(so_lieu["treo_tuong_giay"])
    if so_lieu.get("schema_version", 1) != 2:
        return f"⏱ {so_lieu['slug']}: {wall} · legacy assistant-gap estimate {dinh_dang(so_lieu.get('model_giay'))}"
    current = _current_phase_clock(so_lieu)
    metrics = " · ".join(f"{label} {_metric_text(so_lieu['metrics'][key])}"
                         for label, key in zip(METRIC_LABELS, METRIC_KEYS))
    diagnostics = " · phase diagnostics: " + ",".join(so_lieu["diagnostics"]) if so_lieu["diagnostics"] else ""
    return f"⏱ {current} · whole request {wall} · {metrics}{diagnostics}"


# --------------------------------------------------------------------- close the books

def da_dong_so(cwd, slug, started_at):
    """Does this request already have a line in timing.jsonl — guards against double counting.

    `init` and `tdq_finish --phase idle` both call the close step; without the guard one request
    appears twice and every statistic after it is wrong.
    """
    path = os.path.join(cwd, TIMING_REL)
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ban_ghi = json.loads(line)
                except ValueError:
                    continue
                if isinstance(ban_ghi, dict) and ban_ghi.get("slug") == slug and ban_ghi.get("started_at") == started_at:
                    return True
    except OSError:
        return False
    return False


def dong_so(cwd, so_lieu):
    """Append exactly one JSON line to timing.jsonl. Returns False if it was closed before."""
    if da_dong_so(cwd, so_lieu["slug"], so_lieu["started_at"]):
        _log(f"request {so_lieu['slug']} already in {TIMING_REL} — not written again")
        return False
    path = os.path.join(cwd, TIMING_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(so_lieu, ensure_ascii=False) + "\n")
    _log(f"closed the books on {so_lieu['slug']} into {TIMING_REL}")
    return True


# -------------------------------------------------------------------------- CLI

def _cli_time(value):
    if value is None:
        return datetime.datetime.now().astimezone()
    if parse_timestamp(value) is None:
        raise ValueError("--now must be an ISO timestamp with an explicit timezone")
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tdq_timing.py",
        description="Time a TDQ request: wall clock, observed spans and data quality.")
    parser.add_argument("cmd", choices=("show", "close", "status"),
                        help="show = print the table · close = close the books into timing.jsonl · "
                             "status = a one-line clock")
    parser.add_argument("--json", action="store_true", dest="want_json",
                        help="print the raw data as JSON")
    parser.add_argument("--now", help="the 'now' mark in ISO form (so tests are reproducible)")
    parser.add_argument("--transcript-dir", help="transcript folder, defaults to the project one")
    parser.add_argument("--project", help="project folder, defaults to TDQ_PROJECT_DIR/git root")
    parser.add_argument("--host", choices=("auto", "claude", "codex"), default="auto")
    parser.add_argument("--session-id", action="append", default=[], help="select a session; repeatable")
    parser.add_argument("--transcript-cache", choices=("off", "auto"), default="off",
                        help="request-local normalized parse cache (default: off)")
    args = parser.parse_args(argv)

    cwd = args.project or tdq_state.resolve_project_dir()
    try:
        ket_thuc = _cli_time(args.now)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_SYNTAX

    state = tdq_state.load(cwd)
    if not state or not state.get("active_request"):
        # Having no open request is NOT an error: hooks and the report call this unconditionally.
        print("null" if args.want_json else "No open request yet — nothing to time.")
        return 0

    so_lieu = tong_hop(state, ket_thuc, args.transcript_dir, project_dir=cwd,
                       host=args.host, session_ids=args.session_id, cache=args.transcript_cache)

    if args.cmd == "close":
        dong_so(cwd, so_lieu)
    if args.want_json:
        print(json.dumps(so_lieu, ensure_ascii=False))
    elif args.cmd == "status":
        print(dong_ho_ngan(so_lieu))
    else:
        print(bang_markdown(so_lieu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
