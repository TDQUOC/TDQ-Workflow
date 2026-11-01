"""Cache parity and invalidation use real files and the production parser."""
import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_transcript as transcript
import tdq_transcript_cache as cache_module
import tdq_timing as timing


@pytest.mark.skipif(os.name != "nt", reason="Windows MAX_PATH regression")
def test_long_directory_keeps_atomic_cache_writable():
    with tempfile.TemporaryDirectory(prefix="tc-") as sandbox:
        root = Path(sandbox)
        suffix = Path("docs/tdq/cache/request-a/transcripts")
        padding = 180 - len(str(root / suffix)) - 1
        assert padding > 0
        project = root / ("p" * padding)
        directory = project / suffix
        directory.mkdir(parents=True)
        destination = directory / ("a" * 64 + ".json")
        old_temporary = destination.with_suffix("." + "b" * 32 + ".tmp")
        assert len(str(destination)) < 260 < len(str(old_temporary))
        destination.write_bytes(b"valid-destination-probe")
        destination.unlink()
        try:
            old_temporary.write_bytes(b"legacy-path-probe")
        except OSError as error:
            assert error.winerror == 206 or error.errno == 2
            assert directory.is_dir()
        else:
            old_temporary.unlink()
            pytest.skip("Windows long paths are enabled for this process")
        source = project / "session.jsonl"
        write(source, records(project))
        cold, warm = {}, {}
        expected = read(project, source)
        assert read(project, source, cache="auto", cache_stats=cold) == expected
        assert read(project, source, cache="auto", cache_stats=warm) == expected
        assert cold["misses"] == 1 and warm["hits"] == 1
        assert len(list(directory.glob("*.json"))) == 1
        assert not list(directory.glob("*.tmp"))


def records(project, session="s1", end=10):
    return [
        {"type": "session_meta", "payload": {"cwd": str(project), "id": session}},
        {"type": "response_item", "timestamp": "2026-10-27T00:00:00Z",
         "payload": {"type": "function_call", "call_id": "tool-1", "arguments": "SECRET"}},
        {"type": "response_item", "timestamp": f"2026-10-27T00:00:{end:02d}Z",
         "payload": {"type": "function_call_output", "call_id": "tool-1", "output": "SECRET"}},
    ]


def write(path, entries):
    path.write_text("".join(json.dumps(row) + "\n" for row in entries), encoding="utf-8")


def read(project, source, **options):
    return transcript.read_transcripts(project, source, request_id="request-a", **options)


def test_cold_warm_off_parity_and_privacy(tmp_path, monkeypatch):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    expected = read(tmp_path, source)
    cold, warm = {}, {}
    assert read(tmp_path, source, cache="auto", cache_stats=cold) == expected
    monkeypatch.setattr(transcript, "_parse_snapshot", lambda *a: pytest.fail("warm reparsed"))
    assert read(tmp_path, source, cache="auto", cache_stats=warm) == expected
    assert cold["misses"] == 1 and warm["hits"] == 1
    assert warm["bytes_hashed"] == source.stat().st_size
    for path in (tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"):
        assert "SECRET" not in path.read_text()


@pytest.mark.parametrize("mutation", ["append", "truncate", "replace", "same-mtime"])
def test_changed_bytes_always_miss(tmp_path, mutation):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    read(tmp_path, source, cache="auto")
    before = source.stat()
    if mutation == "append":
        with source.open("a") as stream:
            stream.write('{bad\n')
    elif mutation == "truncate":
        write(source, records(tmp_path)[:2])
    elif mutation == "replace":
        replacement = tmp_path / "replacement"
        write(replacement, records(tmp_path, end=20))
        replacement.replace(source)
    else:
        write(source, records(tmp_path, end=11))
        os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
    stats = {}
    assert read(tmp_path, source, cache="auto", cache_stats=stats) == read(tmp_path, source)
    assert stats["misses"] == 1


def test_delete_and_corrupt_cache(tmp_path):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    expected = read(tmp_path, source, cache="auto")
    cached = next((tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"))
    cached.write_text('{broken', encoding="utf-8")
    stats = {}
    assert read(tmp_path, source, cache="auto", cache_stats=stats) == expected
    assert stats["misses"] == 1
    source.unlink()
    result = read(tmp_path, source, cache="auto")
    assert result["quality"]["tool"]["quality"] == "unavailable"


def test_parser_version_and_request_namespace(tmp_path, monkeypatch):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    read(tmp_path, source, cache="auto")
    monkeypatch.setattr(transcript, "PARSER_VERSION", "test-version-change")
    stats = {}
    read(tmp_path, source, cache="auto", cache_stats=stats)
    assert stats["misses"] == 1
    other = {}
    transcript.read_transcripts(tmp_path, source, cache="auto", request_id="request-b", cache_stats=other)
    assert other["misses"] == 1
    host_changed = {}
    read(tmp_path, source, cache="auto", host="codex", cache_stats=host_changed)
    assert host_changed["misses"] == 1


def test_selection_and_window_recomputed(tmp_path):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    read(tmp_path, source, cache="auto")
    for selected in (["s1"], ["other"]):
        assert read(tmp_path, source, cache="auto", session_ids=selected) == read(
            tmp_path, source, session_ids=selected)
    state = {"active_request": "request-a", "started_at": "2026-10-27T00:00:00Z",
             "phase_history": [], "lane": "full"}
    for end in (5, 20):
        at = datetime.datetime(2026, 10, 27, 0, 0, end, tzinfo=datetime.timezone.utc)
        assert timing.tong_hop(state, at, source, project_dir=tmp_path, cache="auto") == timing.tong_hop(
            state, at, source, project_dir=tmp_path)


def test_duplicate_aggregation_never_accumulates(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    for name in ("first", "second"):
        write(logs / f"{name}.jsonl", records(tmp_path))
    expected = read(tmp_path, logs)
    assert read(tmp_path, logs, cache="auto") == expected
    assert read(tmp_path, logs, cache="auto") == expected
    (logs / "second.jsonl").unlink()
    assert read(tmp_path, logs, cache="auto") == read(tmp_path, logs)


def test_mutating_read_is_partial_and_not_cached(tmp_path, monkeypatch):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    original = cache_module._read_bytes
    def mutate(path):
        content = original(path)
        with path.open("ab") as stream:
            stream.write(b"\n")
        return content
    monkeypatch.setattr(cache_module, "_read_bytes", mutate)
    result = read(tmp_path, source, cache="auto")
    assert result["quality"]["tool"]["quality"] == "partial"
    assert "unstable_source" in result["quality"]["tool"]["reason"]
    assert not list((tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"))


def test_unreadable_never_uses_previous_hit(tmp_path, monkeypatch):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    read(tmp_path, source, cache="auto")
    def denied(path):
        raise PermissionError("SECRET")
    monkeypatch.setattr(cache_module, "_read_bytes", denied)
    result = read(tmp_path, source, cache="auto")
    assert result["quality"]["tool"]["quality"] == "unavailable"


def test_file_changes_during_cache_lookup_is_partial(tmp_path, monkeypatch):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    read(tmp_path, source, cache="auto")
    original = cache_module.TranscriptCache._load
    def change(self, *args):
        result = original(self, *args)
        with source.open("a") as stream:
            stream.write("\n")
        return result
    monkeypatch.setattr(cache_module.TranscriptCache, "_load", change)
    result = read(tmp_path, source, cache="auto")
    assert result["quality"]["tool"]["quality"] == "partial"


def test_cache_cleanup_error_falls_back_without_losing_spans(tmp_path, monkeypatch):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    expected = read(tmp_path, source)
    def denied(*args, **kwargs):
        raise PermissionError("do not leak this")
    monkeypatch.setattr(cache_module.Path, "unlink", denied)
    assert read(tmp_path, source, cache="auto") == expected


def test_failed_atomic_replace_preserves_entry_and_removes_temporary(tmp_path, monkeypatch):
    cache = cache_module.TranscriptCache(tmp_path, "request-a", mode="auto")
    key, entry = cache._entry(tmp_path / "session.jsonl", "content", "parser", "codex")
    cache._write(entry, key, ["original"])
    original = entry.read_bytes()

    def denied(source, destination):
        assert source.parent == destination.parent
        raise PermissionError("replacement denied")

    monkeypatch.setattr(Path, "replace", denied)
    cache._write(entry, key, ["replacement"])
    assert entry.read_bytes() == original
    assert not list(entry.parent.glob("*.tmp"))


def test_corrupt_normalized_trace_is_reparsed(tmp_path):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    expected = read(tmp_path, source, cache="auto")
    cached = next((tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"))
    envelope = json.loads(cached.read_text())
    envelope["trace"] = [[{"_marks": [{"arbitrary": True}]}, {}]]
    envelope["digest"] = cache_module._digest(envelope["trace"])
    cached.write_text(json.dumps(envelope))
    stats = {}
    assert read(tmp_path, source, cache="auto", cache_stats=stats) == expected
    assert stats["misses"] == 1


def test_foreign_metadata_does_not_count_malformed_tail(tmp_path):
    source = tmp_path / "foreign.jsonl"
    write(source, records(tmp_path / "other"))
    with source.open("a") as stream:
        stream.write('{malformed private tail\n')
    cold = read(tmp_path, source, cache="auto")
    assert cold == read(tmp_path, source)
    assert cold == read(tmp_path, source, cache="auto")
    assert cold["sources"][0]["counters"].get("malformed_lines", 0) == 0


def test_off_stops_normalizing_foreign_log_after_metadata(tmp_path, monkeypatch):
    source = tmp_path / "foreign.jsonl"
    write(source, records(tmp_path / "other"))
    original = transcript._normalize_line
    calls = []
    def count(line):
        calls.append(1)
        return original(line)
    monkeypatch.setattr(transcript, "_normalize_line", count)
    read(tmp_path, source)
    assert len(calls) == 1


def test_default_off_and_missing_request_no_cache(tmp_path):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    transcript.read_transcripts(tmp_path, source)
    transcript.read_transcripts(tmp_path, source, cache="auto")
    assert not (tmp_path / "docs/tdq/cache").exists()


def test_retention_does_not_change_results(tmp_path):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    expected = read(tmp_path, source)
    assert read(tmp_path, source, cache="auto", cache_max_bytes=1) == expected
    assert not list((tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"))


def test_expired_entry_and_invalid_namespace(tmp_path):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    expected = read(tmp_path, source, cache="auto")
    cached = next((tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"))
    os.utime(cached, (1, 1))
    stats = {}
    assert read(tmp_path, source, cache="auto", cache_stats=stats) == expected
    assert stats["misses"] == 1
    assert transcript.read_transcripts(tmp_path, source, cache="auto", request_id="../../escape") == expected
    assert not (tmp_path / "docs/escape").exists()


def test_cache_log_has_no_payload_and_can_disable(tmp_path, monkeypatch, capsys):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    monkeypatch.setenv("TDQ_LOG", "1")
    read(tmp_path, source, cache="auto")
    log = capsys.readouterr().err
    assert "transcript-cache" in log and "SECRET" not in log
    monkeypatch.setenv("TDQ_LOG", "0")
    read(tmp_path, source, cache="auto")
    assert capsys.readouterr().err == ""


def test_timing_cli_opt_in_keeps_json_business_parity(tmp_path, monkeypatch, capsys):
    source = tmp_path / "session.jsonl"
    write(source, records(tmp_path))
    state = {"active_request": "request-a", "started_at": "2026-10-27T00:00:00Z",
             "phase_history": [], "lane": "full"}
    monkeypatch.setattr(timing.tdq_state, "load", lambda path: state)
    command = ["show", "--project", str(tmp_path), "--transcript-dir", str(source),
               "--now", "2026-10-27T00:00:20Z", "--json"]
    assert timing.main(command) == 0
    expected = json.loads(capsys.readouterr().out)
    assert timing.main([*command, "--transcript-cache", "auto"]) == 0
    assert json.loads(capsys.readouterr().out) == expected
    assert list((tmp_path / "docs/tdq/cache/request-a/transcripts").glob("*.json"))
