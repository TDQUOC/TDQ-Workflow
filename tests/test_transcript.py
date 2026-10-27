"""Synthesized transcript contracts: identity first, then timed evidence."""

import contextlib
import datetime
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_transcript as transcript  # noqa: E402

PROJECT = "/work/example"
BASE = datetime.datetime(2026, 10, 26, 23, 59, 55, tzinfo=datetime.timezone.utc)


def timestamp(seconds):
    return (BASE + datetime.timedelta(seconds=seconds)).isoformat()


def claude(event_type, seconds, **values):
    return {"type": event_type, "timestamp": timestamp(seconds),
            "cwd": PROJECT, "sessionId": "s1", **values}


def api_start(seconds=0, identity="r1"):
    return claude("api-request", seconds, id=identity)


def reply(seconds=10, final=True, identity="r1", uuid="reply", content=None):
    return claude("assistant", seconds, requestRef=identity, uuid=uuid,
                  message={"id": "message", "stop_reason": "end_turn" if final else None,
                           "content": content or []})


def tool_start(seconds=0, identity="t1"):
    return claude("assistant", seconds, message={"content": [
        {"type": "tool_use", "id": identity, "name": "Read", "input": {}}]})


def tool_end(seconds=10, identity="t1", output="synthetic result"):
    return claude("user", seconds, message={"content": [
        {"type": "tool_result", "tool_use_id": identity, "content": output}]})


def codex_meta(session="c1", cwd=PROJECT):
    return {"type": "session_meta", "timestamp": timestamp(0),
            "payload": {"id": session, "cwd": cwd}}


def codex_tool(event_type, seconds, identity="t1", **values):
    return {"type": "response_item", "timestamp": timestamp(seconds),
            "payload": {"type": event_type, "call_id": identity, **values}}


class TranscriptTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.directory = self.home / "explicit"
        self.directory.mkdir()
        self.quiet = patch.dict(os.environ, {"TDQ_LOG": "0"})
        self.quiet.start()
        self.addCleanup(self.quiet.stop)

    def write(self, records, name="s1.jsonl", directory=None):
        path = Path(directory or self.directory) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return path

    def read(self, **kwargs):
        return transcript.read_transcripts(PROJECT, self.directory, **kwargs)

    def assert_quality(self, result, kind, quality):
        self.assertEqual(result["quality"][kind]["quality"], quality, result["sources"])

    def test_claude_stream_uses_final_reply_and_tool_end(self):
        self.write([api_start(), reply(5, False, uuid="part"), reply(),
                    tool_start(5), tool_end(15)])
        result = self.read()
        spans = {span["kind"]: span for span in result["spans"]}
        self.assertEqual((spans["api"]["end"] - spans["api"]["start"]).total_seconds(), 10)
        self.assertEqual((spans["tool"]["end"] - spans["tool"]["start"]).total_seconds(), 10)
        self.assert_quality(result, "api", "complete")
        self.assert_quality(result, "tool", "complete")
        self.assert_quality(result, "job", "unavailable")

    def test_out_of_order_records_pair_by_identity(self):
        records = [api_start(), reply(), tool_start(), tool_end()]
        self.write(list(reversed(records)))
        result = self.read()
        self.assertEqual(len(result["spans"]), 2)
        self.assertEqual({span["id"] for span in result["spans"]}, {"r1", "t1"})

    def test_stream_without_final_reply_remains_partial(self):
        self.write([api_start(), reply(7, False)])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assert_quality(result, "api", "partial")
        self.assertEqual(result["sources"][0]["counters"]["missing_pairs"], 1)

    def test_progress_after_final_is_not_a_complete_stream(self):
        self.write([api_start(), reply(4), reply(8, False, uuid="later")])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assert_quality(result, "api", "partial")

    def test_stream_fragments_can_share_request_and_message_id(self):
        self.write([api_start(), reply(2, True, uuid="block1"),
                    reply(10, True, uuid="block2")])
        result = self.read()
        self.assertEqual(len(result["spans"]), 1)
        self.assertEqual(result["spans"][0]["end"], BASE + datetime.timedelta(seconds=10))
        self.assert_quality(result, "api", "complete")

    def test_duplicate_start_and_end_across_parent_child_copies(self):
        records = [api_start(), reply(), tool_start(), tool_end()]
        self.write(records)
        self.write(records, "s1/subagents/agent-copy.jsonl")
        result = self.read()
        self.assertEqual(len(result["spans"]), 2)
        self.assertEqual(sum(s["counters"].get("duplicates", 0) for s in result["sources"]), 4)
        self.assert_quality(result, "tool", "complete")

    def test_unrelated_sessions_do_not_merge_matching_call_ids(self):
        self.write([tool_start(), tool_end()])
        records = [{**event, "sessionId": "s2"} for event in [tool_start(5), tool_end(20)]]
        self.write(records, "s2.jsonl")
        result = self.read()
        self.assertEqual({span["session_id"] for span in result["spans"]}, {"s1", "s2"})
        self.assertEqual(result["attribution"], "project_window")

    def test_conflicting_tool_start_drops_only_ambiguous_pair(self):
        self.write([tool_start(), tool_start(1), tool_end(),
                    tool_start(2, "good"), tool_end(5, "good")])
        result = self.read()
        self.assertEqual([span["id"] for span in result["spans"]], ["good"])
        self.assert_quality(result, "tool", "partial")
        self.assertGreater(result["sources"][0]["counters"]["conflicts"], 0)

    def test_conflicting_tool_end_is_not_arbitrarily_selected(self):
        self.write([tool_start(), tool_end(4), tool_end(8)])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assert_quality(result, "tool", "partial")

    def test_same_api_event_uuid_with_different_time_conflicts(self):
        self.write([api_start(), reply(4), reply(8)])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assert_quality(result, "api", "partial")
        self.assertEqual(result["sources"][0]["counters"]["conflicts"], 1)

    def test_missing_start_or_end_remains_partial(self):
        for records in ([tool_start()], [tool_end()], [reply()]):
            with self.subTest(records=records):
                self.write(records)
                result = self.read()
                self.assertEqual(result["spans"], [])
                self.assertIn("partial", {value["quality"] for value in result["quality"].values()})

    def test_naive_or_invalid_timestamp_is_not_assumed_local(self):
        for value in ("2026-10-26T12:00:00", "broken", None, 19):
            with self.subTest(value=value):
                self.write([{**tool_start(), "timestamp": value}, tool_end()])
                result = self.read()
                self.assertEqual(result["spans"], [])
                self.assert_quality(result, "tool", "partial")
                self.assertEqual(result["sources"][0]["counters"]["invalid_timestamps"], 1)

    def test_negative_interval_is_diagnosed(self):
        self.write([tool_start(9), tool_end(3)])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["counters"]["invalid_spans"], 1)

    def test_missing_call_id_is_diagnosed(self):
        self.write([tool_start(identity=None), tool_end()])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["counters"]["missing_ids"], 1)

    def test_codex_function_and_custom_call_spans_without_api_inference(self):
        self.write([codex_meta(), codex_tool("function_call", 0),
                    codex_tool("function_call_output", 2),
                    codex_tool("custom_tool_call", 3, "custom"),
                    codex_tool("custom_tool_call_output", 10, "custom"),
                    {"type": "event_msg", "timestamp": timestamp(0),
                     "payload": {"type": "task_started", "turn_id": "turn"}},
                    {"type": "event_msg", "timestamp": timestamp(100),
                     "payload": {"type": "task_complete", "turn_id": "turn"}}])
        result = self.read()
        self.assertEqual([span["kind"] for span in result["spans"]], ["tool", "tool"])
        self.assert_quality(result, "api", "unavailable")
        self.assert_quality(result, "job", "unavailable")
        self.assert_quality(result, "tool", "complete")

    def test_background_return_does_not_close_job(self):
        self.write([codex_meta(), codex_tool("custom_tool_call", 0),
                    codex_tool("custom_tool_call_output", 1,
                               output="Script running with cell ID 123, session_id 456")])
        result = self.read()
        self.assertEqual(len(result["spans"]), 1)
        self.assertEqual(result["spans"][0]["kind"], "tool")
        self.assert_quality(result, "job", "unavailable")

    def test_supported_empty_tool_history_is_complete(self):
        self.write([codex_meta()])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assert_quality(result, "tool", "complete")
        self.assert_quality(result, "api", "unavailable")

    def test_mixed_host_api_measurement_has_partial_coverage(self):
        self.write([api_start(), reply()])
        self.write([codex_meta()], "codex.jsonl")
        result = self.read()
        self.assert_quality(result, "api", "partial")
        self.assertIn("unsupported_source_schema", result["quality"]["api"]["reason"])

    def test_explicit_host_filters_other_host(self):
        self.write([api_start(), reply()])
        self.write([codex_meta()], "codex.jsonl")
        result = self.read(host="claude")
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "api", "complete")
        self.assertIn("host_filtered", [source["reason"] for source in result["sources"]])

    def test_explicit_session_filters_concurrent_logs(self):
        self.write([tool_start(), tool_end()])
        self.write([{**event, "sessionId": "s2"} for event in [tool_start(), tool_end()]], "s2.jsonl")
        result = self.read(session_ids=["s2"])
        self.assertEqual([span["session_id"] for span in result["spans"]], ["s2"])
        self.assertEqual(result["attribution"], "session")

    def test_explicit_source_does_not_override_project_mismatch(self):
        self.write([{**event, "cwd": PROJECT + "-other"} for event in [tool_start(), tool_end()]])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["reason"], "project_mismatch")

    def test_conflicting_project_metadata_rejects_whole_file(self):
        self.write([tool_start(), {**tool_end(), "cwd": "/other"}])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["status"], "rejected")

    def test_conflicting_session_metadata_rejects_whole_file(self):
        self.write([tool_start(), {**tool_end(), "sessionId": "other"}])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["reason"], "conflicting_metadata")

    def test_bad_metadata_does_not_use_missing_metadata_escape(self):
        self.write([{**event, "cwd": 42} for event in [tool_start(), tool_end()]])
        result = self.read()
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["reason"], "conflicting_metadata")

    def test_missing_metadata_explicit_source_is_partial(self):
        records = [tool_start(), tool_end()]
        for event in records:
            event.pop("cwd")
        self.write(records)
        result = self.read()
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "tool", "partial")
        self.assertEqual(result["sources"][0]["counters"]["missing_metadata"], 1)

    def test_missing_session_filename_can_match_explicit_filter(self):
        records = [tool_start(), tool_end()]
        for event in records:
            event.pop("sessionId")
        self.write(records)
        result = self.read(session_ids=["s1"])
        self.assertEqual([span["session_id"] for span in result["spans"]], ["s1"])
        self.assert_quality(result, "tool", "partial")

    def test_missing_metadata_auto_discovery_is_rejected(self):
        directory = transcript.claude_transcript_dir(PROJECT, self.home)
        records = [tool_start(), tool_end()]
        for event in records:
            event.pop("cwd")
        self.write(records, directory=directory)
        result = transcript.read_transcripts(PROJECT, home=self.home)
        self.assertEqual(result["spans"], [])
        self.assertEqual(result["sources"][0]["reason"], "missing_metadata")

    def test_auto_discovery_session_filter_permits_missing_cwd(self):
        directory = transcript.claude_transcript_dir(PROJECT, self.home)
        records = [{key: value for key, value in event.items() if key != "cwd"}
                   for event in [tool_start(), tool_end()]]
        self.write(records, directory=directory)
        result = transcript.read_transcripts(PROJECT, session_ids=["s1"], home=self.home)
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "tool", "partial")

    def test_slug_collision_cannot_merge_different_projects(self):
        project = "/work/example_a"
        directory = transcript.claude_transcript_dir(project, self.home)
        self.assertEqual(directory, transcript.claude_transcript_dir("/work/example-a", self.home))
        self.write([{**event, "cwd": project} for event in [tool_start(), tool_end()]], directory=directory)
        self.write([{**event, "cwd": "/work/example-a", "sessionId": "wrong"}
                    for event in [tool_start(), tool_end()]], "wrong.jsonl", directory)
        result = transcript.read_transcripts(project, home=self.home)
        self.assertEqual([span["session_id"] for span in result["spans"]], ["s1"])
        self.assert_quality(result, "tool", "complete")

    def test_windows_case_separators_drive_and_unicode_metadata(self):
        project = "C:/Users/Example/Dự án_test"
        directory = transcript.claude_transcript_dir(project, self.home)
        self.write([{**event, "cwd": r"c:\users\EXAMPLE\Dự án_test"}
                    for event in [tool_start(), tool_end()]], directory=directory)
        result = transcript.read_transcripts(project.lower(), home=self.home)
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "tool", "complete")

    def test_posix_project_paths_remain_case_sensitive(self):
        self.write([{**event, "cwd": "/work/EXAMPLE"} for event in [tool_start(), tool_end()]])
        self.assertEqual(self.read()["spans"], [])

    def test_codex_nested_old_day_session_crosses_midnight(self):
        directory = self.home / ".codex" / "sessions" / "2026" / "01" / "01"
        path = self.write([codex_meta(), codex_tool("function_call", 0),
                           codex_tool("function_call_output", 20)], directory=directory)
        os.utime(path, (1, 1))
        result = transcript.read_transcripts(PROJECT, host="codex", home=self.home)
        self.assertEqual(len(result["spans"]), 1)
        span = result["spans"][0]
        self.assertEqual((span["end"] - span["start"]).total_seconds(), 20)
        self.assertNotEqual(span["start"].day, span["end"].day)

    def test_codex_turn_context_must_match_session_project(self):
        self.write([codex_meta(), {"type": "turn_context", "payload": {"cwd": "/other"}},
                    codex_tool("function_call", 0), codex_tool("function_call_output", 2)])
        self.assertEqual(self.read()["spans"], [])

    def test_foreign_project_metadata_stops_before_malformed_tail(self):
        path = self.write([codex_meta(cwd="/foreign")])
        with path.open("ab") as stream:
            stream.write(b'{malformed private tail\n')
        result = self.read()
        self.assertEqual(result["sources"][0]["reason"], "project_mismatch")
        self.assertEqual(result["sources"][0]["counters"].get("malformed_lines", 0), 0)
        self.assertEqual(result["spans"], [])

    def test_filtered_host_stops_before_malformed_tail(self):
        path = self.write([codex_meta()])
        with path.open("ab") as stream:
            stream.write(b'{malformed tail\n')
        result = self.read(host="claude")
        self.assertEqual(result["sources"][0]["reason"], "host_filtered")
        self.assertEqual(result["sources"][0]["counters"].get("malformed_lines", 0), 0)

    def test_uncertain_rejected_source_reduces_coverage(self):
        directory = transcript.claude_transcript_dir(PROJECT, self.home)
        self.write([tool_start(), tool_end()], directory=directory)
        missing = [{key: value for key, value in event.items() if key != "cwd"}
                   for event in [tool_start(), tool_end()]]
        self.write(missing, "missing.jsonl", directory)
        result = transcript.read_transcripts(PROJECT, home=self.home)
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "tool", "partial")

    def test_bad_typed_fields_reduce_quality_without_crashing(self):
        self.write([tool_start(), {"type": []}, {"type": {}},
                    api_start(), reply(uuid={}), reply(12, uuid=[]), tool_end()])
        result = self.read()
        self.assertEqual([span["kind"] for span in result["spans"]], ["tool"])
        self.assert_quality(result, "tool", "partial")
        self.assert_quality(result, "api", "partial")

    def test_malformed_non_object_and_invalid_utf8_lines_reduce_quality(self):
        path = self.write([tool_start(), tool_end()])
        with path.open("ab") as stream:
            stream.write(b'{broken\n[1,2]\n\xff\n\n')
        result = self.read()
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "tool", "partial")
        self.assertEqual(result["sources"][0]["counters"]["malformed_lines"], 2)
        self.assertEqual(result["sources"][0]["counters"]["non_object_lines"], 1)

    def test_unreadable_source_reports_failure_without_raw_error(self):
        path = self.write([tool_start(), tool_end()])
        with patch("builtins.open", side_effect=PermissionError("secret message")):
            result = transcript.read_transcripts(PROJECT, path)
        self.assertEqual(result["sources"][0]["counters"]["unreadable_files"], 1)
        self.assert_quality(result, "tool", "unavailable")
        self.assertNotIn("secret message", repr(result))

    def test_empty_missing_and_unknown_sources_are_unavailable(self):
        for records in ([], [{"type": "future-schema", "data": "unknown"}]):
            with self.subTest(records=records):
                self.write(records)
                result = self.read()
                self.assertEqual(result["spans"], [])
                self.assert_quality(result, "tool", "unavailable")
        result = transcript.read_transcripts(PROJECT, self.directory / "missing.jsonl")
        self.assert_quality(result, "tool", "unavailable")

    def test_unknown_schema_alongside_valid_events_is_partial(self):
        self.write([tool_start(), {"type": "future-schema"}, tool_end()])
        result = self.read()
        self.assertEqual(len(result["spans"]), 1)
        self.assert_quality(result, "tool", "partial")
        self.assertEqual(result["sources"][0]["counters"]["unknown_events"], 1)

    def test_explicit_file_replaces_automatic_discovery(self):
        self.write([tool_start(), tool_end()], directory=transcript.claude_transcript_dir(PROJECT, self.home))
        path = self.write([codex_meta(), codex_tool("function_call", 3),
                           codex_tool("function_call_output", 6)])
        result = transcript.read_transcripts(PROJECT, path, home=self.home)
        self.assertEqual([span["host"] for span in result["spans"]], ["codex"])
        self.assertEqual(len(result["sources"]), 1)

    def test_payload_content_is_never_retained_or_logged(self):
        self.write([tool_start(), tool_end(output="private command api_key=SECRET")])
        stderr = io.StringIO()
        with patch.dict(os.environ, {"TDQ_LOG": "1"}), contextlib.redirect_stderr(stderr):
            result = self.read()
        self.assertNotIn("SECRET", repr(result) + stderr.getvalue())
        self.assertNotIn("private command", repr(result) + stderr.getvalue())

    def test_logging_default_timestamp_and_off_switch(self):
        self.write([tool_start(), tool_end()])
        enabled, disabled = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stderr(enabled):
            self.read()
        with contextlib.redirect_stderr(disabled):
            self.read()
        self.assertRegex(enabled.getvalue(), r"\[\d{4}-\d{2}-\d{2}T.*\] transcript:")
        self.assertEqual(disabled.getvalue(), "")

    def test_reader_never_writes_state_or_source(self):
        path = self.write([tool_start(), tool_end()])
        before = path.read_bytes()
        self.read()
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list(self.directory.iterdir()), [path])


class PathAndTimeTest(unittest.TestCase):
    def test_windows_normalization(self):
        self.assertEqual(transcript.normalize_project(r"C:\Users\Example\..\Code"),
                         transcript.normalize_project("c:/users/code"))

    def test_unc_normalization(self):
        self.assertEqual(transcript.normalize_project(r"\\Server\Share\Path"),
                         r"\\server\share\path")

    def test_posix_normalization(self):
        self.assertEqual(transcript.normalize_project("/work/a/../Project"), "/work/Project")
        self.assertNotEqual(transcript.normalize_project("/work/project"), "/work/Project")

    def test_timestamp_offsets_share_a_utc_axis(self):
        self.assertEqual(transcript.parse_timestamp("2026-10-27T07:00:00+07:00"),
                         transcript.parse_timestamp("2026-10-27T00:00:00Z"))

    def test_invalid_host_is_explicit_error(self):
        with self.assertRaisesRegex(ValueError, "host"):
            transcript.read_transcripts(PROJECT, host="unknown")


if __name__ == "__main__":
    unittest.main()
