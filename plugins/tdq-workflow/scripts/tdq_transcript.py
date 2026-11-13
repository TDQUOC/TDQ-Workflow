"""Read host transcripts into verified timing spans, without writing state.

Only identities, timestamps and diagnostic counters leave this module. API
time is host-observed request latency, never model compute time. The supported
Claude/Codex schemas do not establish a background job's complete lifecycle.
"""
import os as _tdq_os, sys as _tdq_sys
_tdq_here = _tdq_os.path.dirname(_tdq_os.path.abspath(__file__))
_tdq_scripts = _tdq_os.path.normpath(_tdq_os.path.join(_tdq_here, '..', '..', 'scripts'))
for _p in (_tdq_scripts, _tdq_here):
    if _tdq_os.path.isdir(_p) and _p not in _tdq_sys.path:
        _tdq_sys.path.insert(0, _p)
import utf8_io  # noqa: E402,F401

import collections
import datetime
import functools
import io
import json
import ntpath
import os
import posixpath
import re
import sys
from pathlib import Path

import tdq_transcript_cache

KINDS = ("api", "tool", "job")
PARSER_VERSION = "normalized-trace-1"
UTC = datetime.timezone.utc
CLAUDE_TYPES = {"api-request", "assistant", "user", "system", "progress"}
CODEX_TYPES = {"session_meta", "response_item", "event_msg", "turn_context"}
AGY_TYPES = {"USER_INPUT", "PLANNER_RESPONSE", "SYSTEM", "TOOL_RESPONSE"}
UNTIMED_TYPES = {"api-request-shape", "api-request-blob", "last-prompt", "cost-state",
                 "file-history-snapshot", "queue-operation", "summary", "custom-title",
                 "agent-name", "agent-color", "tag", "saved_hook_context", "pr-link",
                 "token_usage_record", "compacted", "world_state"}


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] transcript: {message}", file=sys.stderr)


def _windows_path(path):
    return bool(re.match(r"^[A-Za-z]:[/\\]", path) or path.startswith("\\\\"))


def _absolute_project(project_dir):
    project = os.path.expanduser(os.fspath(project_dir or os.getcwd()))
    if _windows_path(project):
        return ntpath.normpath(project)
    if project.startswith("/"):
        return posixpath.normpath(project)
    return os.path.abspath(project)


def normalize_project(project_dir):
    """Normalize an absolute project identity using its own path dialect."""
    project = _absolute_project(project_dir)
    return ntpath.normcase(project) if _windows_path(project) else project


def claude_transcript_dir(project_dir=None, home=None):
    """Return the Claude-only project directory, including Windows drive."""
    project = _absolute_project(project_dir)
    slug = re.sub(r"[^A-Za-z0-9]", "-", project)
    return str(Path(home or Path.home()) / ".claude" / "projects" / slug)


def parse_timestamp(value):
    """Parse an explicitly zoned timestamp as UTC; never assume a timezone."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(UTC) if parsed.utcoffset() is not None else None
    except (ValueError, OverflowError):
        return None


def _walk_jsonl(directory):
    files, errors = [], []
    try:
        Path(directory).stat()
    except FileNotFoundError:
        return files, errors
    except OSError:
        return files, [Path(directory)]
    for base, _, names in os.walk(directory, onerror=errors.append):
        files.extend(Path(base) / name for name in names if name.endswith(".jsonl"))
    return files, [Path(error.filename or directory) for error in errors]


def _claude_directories(project_dir, home):
    expected = Path(claude_transcript_dir(project_dir, home))
    if not _windows_path(_absolute_project(project_dir)) or not expected.parent.is_dir():
        return [expected]
    # Windows project identity is case-insensitive, including the directory slug.
    try:
        return [path for path in expected.parent.iterdir()
                if path.name.casefold() == expected.name.casefold()] or [expected]
    except OSError:
        return [expected]


def _candidate_paths(project_dir, transcript_dir, host, home):
    if transcript_dir is not None:
        explicit = Path(transcript_dir)
        if not explicit.is_dir():
            return [explicit]
        roots = [explicit]
    else:
        roots = _claude_directories(project_dir, home) if host in ("auto", "claude") else []
        if host in ("auto", "codex"):
            roots.append(Path(home or Path.home()) / ".codex" / "sessions")
        if host in ("auto", "antigravity", "agy"):
            roots.extend(_agy_directories(home))
    candidates = []
    for root in roots:
        files, errors = _walk_jsonl(root)
        candidates.extend(files + errors)
    return sorted(set(candidates), key=str)


def _new_source(path):
    return {"path": str(path), "host": None, "session_id": None,
            "status": "unavailable", "reason": "unrecognized_schema",
            "counters": collections.Counter(), "_hosts": set(),
            "_projects": set(), "_sessions": set(), "_marks": [],
            "_issues": {kind: set() for kind in KINDS}, "_general": set(),
            "_capabilities": set()}


def _issue(source, reason, kind=None):
    source["counters"][reason] += 1
    target = source["_issues"][kind] if kind else source["_general"]
    target.add(reason)


def _normalized_delta(source):
    delta = {key: sorted(source[key]) for key in
             ("_hosts", "_projects", "_sessions", "_general", "_capabilities")
             if source[key]}
    if source["counters"]:
        delta["counters"] = dict(source["counters"])
    if any(source["_issues"].values()):
        delta["_issues"] = {key: sorted(value) for key, value in source["_issues"].items() if value}
    if source["_marks"]:
        delta["_marks"] = [{**mark, "at": mark["at"].isoformat()} for mark in source["_marks"]]
    return delta


def _normalize_line(line):
    metadata, events = _new_source(""), _new_source("")
    try:
        record = json.loads(line.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        _issue(metadata, "malformed_lines")
        return [_normalized_delta(metadata), {}]
    if not isinstance(record, dict):
        _issue(metadata, "non_object_lines")
    elif not isinstance(record.get("type"), str):
        _issue(metadata, "invalid_records")
    else:
        _read_metadata(record, metadata)
        _read_claude(record, events)
        _read_codex(record, events)
        _read_agy(record, events)
    return [_normalized_delta(metadata), _normalized_delta(events)]


def _parse_snapshot(content):
    return [_normalize_line(line) for line in io.BytesIO(content) if line.strip()]


def _parse_selected_snapshot(content, project, host, session_ids):
    """Off keeps the legacy early stop for foreign logs, after snapshot hashing."""
    trace, identity = [], _new_source("")
    for line in io.BytesIO(content):
        if not line.strip():
            continue
        row = _normalize_line(line)
        trace.append(row)
        _apply_delta(identity, row[0])
        if _selection_rejection(identity, project, host, session_ids):
            break
    return trace


def _valid_delta(delta):
    sets = {"_hosts", "_projects", "_sessions", "_general", "_capabilities"}
    if not isinstance(delta, dict) or set(delta).difference(sets | {"counters", "_issues", "_marks"}):
        return False
    for key in sets.intersection(delta):
        if not isinstance(delta[key], list) or not all(isinstance(item, str) for item in delta[key]):
            return False
    return _valid_delta_details(delta)


def _valid_delta_details(delta):
    counters = delta.get("counters", {})
    if not isinstance(counters, dict) or not all(
            isinstance(key, str) and isinstance(value, int) and value >= 0
            for key, value in counters.items()):
        return False
    marks = delta.get("_marks", [])
    return (_valid_issues(delta.get("_issues", {})) and isinstance(marks, list)
            and all(_valid_mark(mark) for mark in marks))


def _valid_issues(issues):
    if not isinstance(issues, dict) or any(key not in KINDS for key in issues):
        return False
    return all(isinstance(value, list) and all(isinstance(item, str) for item in value)
               for value in issues.values())


def _valid_mark(mark):
    if not isinstance(mark, dict) or set(mark) != {"kind", "phase", "id", "at", "event_id"}:
        return False
    return (mark["kind"] in KINDS and mark["phase"] in ("start", "end", "progress")
            and isinstance(mark["id"], str) and bool(mark["id"])
            and parse_timestamp(mark["at"]) is not None
            and (mark["event_id"] is None or isinstance(mark["event_id"], (str, int))))


def _valid_trace(trace):
    return isinstance(trace, list) and all(
        isinstance(row, list) and len(row) == 2 and all(_valid_delta(delta) for delta in row)
        for row in trace)


def _apply_delta(source, delta):
    for key in ("_hosts", "_projects", "_sessions", "_general", "_capabilities"):
        source[key].update(delta.get(key, []))
    source["counters"].update(delta.get("counters", {}))
    for key, values in delta.get("_issues", {}).items():
        source["_issues"][key].update(values)
    source["_marks"].extend({**mark, "at": parse_timestamp(mark["at"])}
                             for mark in delta.get("_marks", []))


def _identity_value(source, value, target):
    if value is None:
        return
    if not isinstance(value, str) or not value:
        _issue(source, "invalid_metadata")
    elif target == "_projects":
        if not (_windows_path(value) or value.startswith("/")):
            _issue(source, "invalid_metadata")
        else:
            source[target].add(normalize_project(value))
    else:
        source[target].add(value)


def _read_metadata(record, source):
    event_type = record.get("type")
    if event_type in CLAUDE_TYPES:
        source["_hosts"].add("claude")
        _identity_value(source, record.get("cwd"), "_projects")
        _identity_value(source, record.get("sessionId"), "_sessions")
    elif event_type in CODEX_TYPES:
        source["_hosts"].add("codex")
        payload = record.get("payload")
        if not isinstance(payload, dict):
            _issue(source, "invalid_records")
            return
        if event_type in ("session_meta", "turn_context"):
            _identity_value(source, payload.get("cwd"), "_projects")
        if event_type == "session_meta":
            _identity_value(source, payload.get("id", payload.get("session_id")), "_sessions")
    elif event_type in AGY_TYPES:
        source["_hosts"].add("antigravity")
        _identity_value(source, record.get("conversation_id") or record.get("conversationId"), "_sessions")
    elif event_type not in UNTIMED_TYPES:
        _issue(source, "unknown_events")


def _mark(source, record, kind, phase, identity, event_id=None):
    source["_capabilities"].add(kind)
    if event_id is not None and not isinstance(event_id, (str, int)):
        _issue(source, "invalid_records", kind)
        return
    if not isinstance(identity, str) or not identity:
        _issue(source, "missing_ids", kind)
        return
    at = parse_timestamp(record.get("timestamp"))
    if at is None:
        _issue(source, "invalid_timestamps", kind)
        return
    source["_marks"].append({"kind": kind, "phase": phase, "id": identity,
                             "at": at, "event_id": event_id})


def _claude_blocks(record, source):
    message = record.get("message")
    if not isinstance(message, dict):
        _issue(source, "invalid_records")
        return []
    blocks = message.get("content", [])
    if isinstance(blocks, str):
        return []
    if not isinstance(blocks, list):
        _issue(source, "invalid_records")
        return []
    result = []
    for block in blocks:
        if isinstance(block, dict):
            result.append(block)
        else:
            _issue(source, "invalid_records")
    return result


def _claude_response(record, source):
    message = record.get("message")
    if not isinstance(message, dict) or not record.get("requestRef"):
        return
    stop_reason = message.get("stop_reason")
    if stop_reason is not None and not isinstance(stop_reason, str):
        _issue(source, "invalid_records", "api")
        return
    phase = "end" if stop_reason else "progress"
    event_id = record.get("uuid")
    if event_id is None and "apiBlockIndex" in record:
        event_id = f"{message.get('id')}:{record['apiBlockIndex']}"
    _mark(source, record, "api", phase, record["requestRef"], event_id)


def _read_claude(record, source):
    event_type = record.get("type")
    if event_type == "api-request":
        _mark(source, record, "api", "start", record.get("id"))
    elif event_type in ("assistant", "user"):
        source["_capabilities"].add("tool")
        if event_type == "assistant":
            _claude_response(record, source)
        for block in _claude_blocks(record, source):
            if block.get("type") == "tool_use":
                _mark(source, record, "tool", "start", block.get("id"))
            elif block.get("type") == "tool_result":
                _mark(source, record, "tool", "end", block.get("tool_use_id"))


def _read_codex(record, source):
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return
    if record.get("type") == "session_meta":
        source["_capabilities"].add("tool")
    if record.get("type") != "response_item":
        return
    event_type = payload.get("type")
    if event_type in ("function_call", "custom_tool_call"):
        _mark(source, record, "tool", "start", payload.get("call_id"))
    elif event_type in ("function_call_output", "custom_tool_call_output"):
        _mark(source, record, "tool", "end", payload.get("call_id"))


def _fallback_session(path, session_ids):
    matches = [identity for identity in session_ids
               if path.stem == identity or path.stem.endswith("-" + identity)]
    return matches[0] if len(matches) == 1 else None


def _metadata_conflicts(source):
    keys = ("_hosts", "_projects", "_sessions")
    return any(len(source[key]) > 1 for key in keys) or source["counters"]["invalid_metadata"]


def _selection_rejection(source, project, host, session_ids):
    if _metadata_conflicts(source):
        return "conflicting_metadata"
    hosts, projects, sessions = (source[key] for key in ("_hosts", "_projects", "_sessions"))
    if host != "auto" and hosts.difference({host}):
        return "host_filtered"
    if projects.difference({project}):
        return "project_mismatch"
    if session_ids and sessions.difference(session_ids):
        return "session_filtered"
    return None


def _select_session(source, path, sessions, session_ids):
    identity = next(iter(sessions), None) or _fallback_session(path, session_ids)
    if session_ids and identity not in session_ids:
        return "session_filtered"
    source["session_id"] = identity or "file:" + str(path.absolute())
    return None


def _select_source(source, path, project, host, session_ids, explicit):
    hosts, projects, sessions = (source[key] for key in ("_hosts", "_projects", "_sessions"))
    source["host"] = next(iter(hosts), None)
    rejection = _selection_rejection(source, project, host, session_ids)
    if rejection:
        return rejection
    if not hosts:
        return "unreadable_source" if source["counters"]["unreadable_files"] else "unrecognized_schema"
    if not projects or not sessions:
        _issue(source, "missing_metadata")
        if not explicit and not session_ids:
            return "missing_metadata"
    return _select_session(source, path, sessions, session_ids)


def _read_source(path, project, host, session_ids, explicit, *, cache):
    source = _new_source(path)
    parser = _parse_snapshot
    if cache.directory is None:
        parser = functools.partial(_parse_selected_snapshot, project=project,
                                   host=host, session_ids=session_ids)
    trace, issue = cache.read(path, host=host, parser_version=PARSER_VERSION,
                              parse=parser, validate=_valid_trace)
    if issue:
        _issue(source, issue)
    for metadata, events in trace:
        _apply_delta(source, metadata)
        if _selection_rejection(source, project, host, session_ids):
            break
        _apply_delta(source, events)
    reason = _select_source(source, path, project, host, session_ids, explicit)
    if reason is None:
        reason = "metadata_partial" if "missing_metadata" in source["_general"] else "metadata_matched"
        source.update(status="accepted", reason=reason)
    else:
        source["reason"] = reason
        source["status"] = "rejected" if source["_hosts"] else "unavailable"
    return source


def _collect_marks(sources):
    buckets, seen = {}, {}
    for index, source in enumerate(sources):
        if source["status"] != "accepted":
            continue
        for mark in source["_marks"]:
            key = (source["host"], source["session_id"], mark["kind"], mark["id"])
            bucket = buckets.setdefault(key, {"start": set(), "end": set(),
                                             "progress": set(), "sources": set(),
                                             "conflict": False})
            bucket["sources"].add(index)
            _collect_mark(key, mark, bucket, seen, source)
    return buckets


def _collect_mark(key, mark, bucket, seen, source):
    phase = mark["phase"]
    streaming = mark["kind"] == "api" and phase != "start"
    identity = (mark["event_id"] or mark["at"]) if streaming else None
    event_key = key + (("stream" if streaming else phase), identity)
    signature = (phase, mark["at"])
    previous = seen.get(event_key)
    if previous is not None:
        if previous == signature:
            source["counters"]["duplicates"] += 1
        else:
            bucket["conflict"] = True
        return
    seen[event_key] = signature
    bucket[phase].add(mark["at"])


def _bucket_span(key, bucket):
    host, session, kind, identity = key
    if bucket["conflict"] or len(bucket["start"]) > 1:
        return None, "conflicts"
    if kind != "api" and len(bucket["end"]) > 1:
        return None, "conflicts"
    if not bucket["start"] or not bucket["end"]:
        return None, "missing_pairs"
    start, end = min(bucket["start"]), max(bucket["end"])
    if bucket["progress"] and max(bucket["progress"]) > end:
        return None, "missing_pairs"
    if end < start:
        return None, "invalid_spans"
    return {"kind": kind, "start": start, "end": end, "host": host,
            "session_id": session, "id": identity}, None


def _pair_spans(sources):
    spans = []
    for key, bucket in _collect_marks(sources).items():
        span, reason = _bucket_span(key, bucket)
        if span is not None:
            spans.append(span)
        else:
            for index in bucket["sources"]:
                _issue(sources[index], reason, key[2])
    return sorted(spans, key=lambda span: (span["start"], span["end"], span["id"]))


def _coverage_issues(sources, accepted, kind):
    issues = set()
    for source in accepted:
        issues.update(source["_general"] | source["_issues"][kind])
        if kind not in source["_capabilities"]:
            issues.add("unsupported_source_schema")
    uncertain = {"missing_metadata", "conflicting_metadata"}
    if any(source["status"] == "unavailable" or source["reason"] in uncertain for source in sources):
        issues.add("unreadable_or_uncertain_source")
    return issues


def _quality(sources, kind):
    accepted = [source for source in sources if source["status"] == "accepted"]
    if not any(kind in source["_capabilities"] for source in accepted):
        reason = "schema_has_no_confirmed_lifecycle" if accepted else "no_usable_source"
        return {"quality": "unavailable", "reason": reason}
    issues = _coverage_issues(sources, accepted, kind)
    return {"quality": "partial" if issues else "complete",
            "reason": ",".join(sorted(issues)) if issues else "selected_logs_complete"}


def _public_sources(sources):
    result = [{key: value for key, value in source.items() if not key.startswith("_")}
              for source in sources]
    for source in result:
        source["counters"] = dict(source["counters"])
        _log(f"{source['host'] or 'unknown'} {source['status']}: {source['reason']}; "
             f"counters={source['counters']}")
    return result


def read_transcripts(project_dir, transcript_dir=None, host="auto", session_ids=None, home=None,
                     *, cache="off", request_id=None, cache_stats=None,
                     cache_max_bytes=tdq_transcript_cache.DEFAULT_MAX_BYTES,
                     cache_max_age_seconds=tdq_transcript_cache.DEFAULT_MAX_AGE):
    """Resolve Claude/Codex files and return spans, sources, quality, attribution.

    Spans contain UTC datetime objects. No time-window filter is applied here:
    callers clip spans, so sessions crossing midnight remain measurable. Only
    explicit sources/session IDs permit missing metadata, marked partial. The
    optional home argument isolates discovery in tests without changing env.
    Cache is off by default; auto requires a request_id. Optional cache_stats is
    filled with lookup/timing counters without altering the business result.
    """
    if host not in ("auto", "claude", "codex"):
        raise ValueError("host must be auto, claude or codex")
    if isinstance(session_ids, str):
        session_ids = [session_ids]
    selected = set(session_ids or [])
    project = normalize_project(project_dir)
    paths = _candidate_paths(project_dir, transcript_dir, host, home)
    reader = tdq_transcript_cache.TranscriptCache(
        project, request_id, mode=cache, stats=cache_stats,
        max_bytes=cache_max_bytes, max_age_seconds=cache_max_age_seconds)
    sources = [_read_source(path, project, host, selected, transcript_dir is not None, cache=reader)
               for path in paths]
    spans = _pair_spans(sources)
    qualities = {kind: _quality(sources, kind) for kind in KINDS}
    if not paths:
        _log("no transcript source found; timing unavailable")
    result = {"spans": spans, "sources": _public_sources(sources), "quality": qualities,
              "attribution": "session" if selected else "project_window"}
    reader.finish()
    return result


def _agy_directories(home=None):
    """Return Antigravity brain log directories under ~/.gemini/antigravity/brain/*/.system_generated/logs."""
    base = Path(home or Path.home()) / ".gemini" / "antigravity" / "brain"
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob("*/.system_generated/logs") if p.is_dir())


def _decode_double_json(raw_args):
    """Unwrap Double-JSON stringified args in Antigravity PLANNER_RESPONSE tool_calls."""
    val = raw_args
    for _ in range(2):
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except ValueError:
                break
    return val


def _read_agy(record, source):
    """Extract API and Double-JSON tool timing marks from Antigravity transcript.jsonl records."""
    event_type = record.get("type")
    if event_type not in AGY_TYPES:
        return
    at_val = record.get("created_at") or record.get("timestamp")
    ts_rec = {"timestamp": at_val}
    step_id = str(record.get("step_index") if record.get("step_index") is not None else "0")
    if event_type == "USER_INPUT":
        source["_capabilities"].add("api")
        _mark(source, ts_rec, "api", "start", f"step:{step_id}", step_id)
        return
    if event_type == "PLANNER_RESPONSE":
        _mark(source, ts_rec, "api", "end", f"step:{step_id}", step_id)
        tcalls = record.get("tool_calls") or []
        if isinstance(tcalls, list) and tcalls:
            source["_capabilities"].add("tool")
            for idx, call in enumerate(tcalls):
                if not isinstance(call, dict):
                    continue
                _ = _decode_double_json(call.get("arguments") or call.get("args"))
                cid = str(call.get("id") or f"agy:{step_id}:{idx}")
                _mark(source, ts_rec, "tool", "start", cid, step_id)
                _mark(source, ts_rec, "tool", "end", cid, step_id)
