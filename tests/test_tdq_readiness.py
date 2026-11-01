"""Readiness reuse must preserve live checks and invalidate content changes."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from helper import ROOT
import sys
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_lsp
import tdq_readiness


class ReadinessCache(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input.py"
        self.input.write_text("one", encoding="utf-8")

    def probe(self, callback, **kwargs):
        return tdq_readiness.cached_probe(self.root, "request-a", "probe", callback,
                                         inputs=[self.input], **kwargs)

    def test_default_off_executes_and_writes_nothing(self):
        call = mock.Mock(return_value={"version": 1})
        self.probe(call)
        self.probe(call)
        self.assertEqual(call.call_count, 2)
        self.assertFalse((self.root / "docs/tdq/cache").exists())

    def test_telemetry_records_real_probes_and_hash_work_without_double_counting(self):
        stats = {}
        call = mock.Mock(return_value={"version": 1})
        self.probe(call, mode="auto", stats=stats)
        self.probe(call, mode="auto", stats=stats)
        self.assertEqual((stats["hits"], stats["misses"], stats["probe_calls"]), (1, 1, 1))
        self.assertGreater(stats["verify_seconds"], 0)
        self.assertGreaterEqual(stats["execute_seconds"], 0)
        self.assertGreater(stats["write_seconds"], 0)
        self.assertEqual(stats["wait_seconds"], 0)

    def test_auto_reuses_content_but_same_mtime_mutation_misses(self):
        call = mock.Mock(return_value={"version": 1})
        self.probe(call, mode="auto")
        self.probe(call, mode="auto")
        self.assertEqual(call.call_count, 1)
        stamp = self.input.stat()
        self.input.write_text("two", encoding="utf-8")
        os.utime(self.input, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.probe(call, mode="auto")
        self.assertEqual(call.call_count, 2)

    def test_missing_deleted_changed_inputs_and_environment_miss(self):
        call = mock.Mock(return_value={"version": 1})
        self.probe(call, mode="auto", environment={"TOKEN": "secret-one"})
        self.probe(call, mode="auto", environment={"TOKEN": "secret-two"})
        self.input.unlink()
        self.probe(call, mode="auto", environment={"TOKEN": "secret-two"})
        self.assertEqual(call.call_count, 3)
        cache = "".join(p.read_text(encoding="utf-8") for p in self.root.rglob("*.json"))
        self.assertNotIn("secret-", cache)

    def test_mutation_during_probe_is_not_published(self):
        def change():
            self.input.write_text("changed", encoding="utf-8")
            return {"version": 1}
        self.probe(change, mode="auto")
        self.assertEqual(list(self.root.rglob("probe.json")), [])

    def test_corrupt_receipt_cannot_supply_a_verdict(self):
        call = mock.Mock(return_value={"version": 1})
        self.probe(call, mode="auto")
        file = next(self.root.rglob("probe.json"))
        value = json.loads(file.read_text(encoding="utf-8"))
        value["value"] = {"version": 999}
        file.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.probe(call, mode="auto"), {"version": 1})
        self.assertEqual(call.call_count, 2)

    def test_request_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            tdq_readiness.cached_probe(self.root, "../escape", "probe", lambda: 1,
                                       inputs=[], mode="auto")

    def test_handoff_rechecks_input_before_using_memory(self):
        call, handoff = mock.Mock(return_value={"version": 1}), {}
        self.probe(call, mode="auto", handoff=handoff)
        self.probe(call, mode="auto", handoff=handoff)
        self.input.write_text("new", encoding="utf-8")
        self.probe(call, mode="auto", handoff=handoff)
        self.assertEqual(call.call_count, 2)

    def test_input_change_while_reading_receipt_does_not_return_cached_value(self):
        call = mock.Mock(side_effect=[{"version": 1}, {"version": 2}])
        self.probe(call, mode="auto")
        real_load = tdq_readiness._load_entry
        def changed_during_read(path):
            entry = real_load(path)
            self.input.write_text("new input", encoding="utf-8")
            return entry
        with mock.patch.object(tdq_readiness, "_load_entry", side_effect=changed_during_read):
            self.assertEqual(self.probe(call, mode="auto"), {"version": 2})
        self.assertEqual(call.call_count, 2)

    def test_input_becoming_unreadable_on_hit_runs_live_probe(self):
        call = mock.Mock(return_value={"version": 1})
        self.probe(call, mode="auto")
        key = tdq_readiness.fingerprint(self.root, [self.input])
        with mock.patch.object(tdq_readiness, "fingerprint", side_effect=[key, PermissionError(), key]):
            self.assertEqual(self.probe(call, mode="auto"), {"version": 1})
        self.assertEqual(call.call_count, 2)

    def test_live_rungs_and_smoke_always_run_even_warm(self):
        names = ["bac1_binary", "bac2_mcp", "bac3_language_server", "bac4_quyen_tool",
                 "bac5_hook_xung_dot", "bac6_cau_hinh_goc_import", "bac7_graphify", "bac8_module"]
        with contextlib.ExitStack() as stack:
            probes = [stack.enter_context(mock.patch.object(tdq_lsp, name,
                      return_value=tdq_lsp.Bac(i, name, True))) for i, name in enumerate(names, 1)]
            smoke = stack.enter_context(mock.patch.object(tdq_lsp, "chay_smoke",
                                        side_effect=[[('lsp', True, '')], [('lsp', False, 'disconnected')]]))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            self.assertEqual(tdq_lsp.kiem_mot_lenh(self.root, cache_mode="auto", request="request-a")[0], 0)
            self.assertEqual(tdq_lsp.kiem_mot_lenh(self.root, cache_mode="auto", request="request-a")[0], 4)
        self.assertEqual(smoke.call_count, 2)
        self.assertTrue(all(probe.call_count == 2 for probe in probes))

    def test_cli_cache_is_explicit_and_default_off(self):
        self.assertEqual(tdq_lsp.parse_args(["check"]).readiness_cache, "off")
        self.assertEqual(tdq_lsp.parse_args(["check", "--readiness-cache", "auto"]).readiness_cache, "auto")

    def test_language_cache_is_reused_and_invalidates_source_graph_config(self):
        graph = self.root / "graphify-out/graph.json"
        graph.parent.mkdir()
        graph.write_text("{}", encoding="utf-8")
        config = self.root / "pyproject.toml"
        config.write_text("# one", encoding="utf-8")
        with mock.patch.object(tdq_lsp, "_do_ngon_ngu", return_value={"python": 3}) as scan:
            def run():
                with tdq_readiness.probe_context(self.root, mode="auto", request="request-a"):
                    return tdq_lsp.do_ngon_ngu(self.root)
            self.assertEqual(run(), run())
            self.assertEqual(scan.call_count, 1)
            for file in (self.input, graph, config):
                file.write_text("changed", encoding="utf-8")
                run()
            self.assertEqual(scan.call_count, 4)
            (self.root / "new.py").write_text("new", encoding="utf-8")
            run()
            self.assertEqual(scan.call_count, 5)

    def test_file_added_during_scan_prevents_publication(self):
        def scan(project):
            (self.root / "new.py").write_text("new", encoding="utf-8")
            return {"python": 3}
        with mock.patch.object(tdq_lsp, "_do_ngon_ngu", side_effect=scan):
            with tdq_readiness.probe_context(self.root, mode="auto", request="request-a"):
                tdq_lsp.do_ngon_ngu(self.root)
        self.assertEqual(list(self.root.rglob("language-inventory.json")), [])

    def test_generated_cache_sources_are_excluded_from_both_inventory_paths(self):
        generated = self.root / "docs/tdq/cache/request-a/fixture"
        with tdq_readiness.probe_context(self.root, mode="auto", request="request-a"):
            before = tdq_lsp.do_ngon_ngu(self.root)
            generated.mkdir(parents=True)
            for number in range(tdq_lsp.NGUONG_FILE):
                (generated / f"m{number}.ts").write_text("export const a=1", encoding="utf-8")
            self.assertEqual(tdq_lsp.do_ngon_ngu(self.root), before)
        self.assertEqual(tdq_lsp.do_ngon_ngu(self.root), before)

    def test_actual_language_rung_reuses_inventory_but_runs_doctor_twice(self):
        for number in range(tdq_lsp.NGUONG_FILE):
            (self.root / f"m{number}.py").write_text("x=1", encoding="utf-8")
        with mock.patch.object(tdq_lsp.shutil, "which", return_value="fixture-binary"), \
                mock.patch.object(tdq_lsp, "mcp_args", return_value=["python:fixture-binary"]), \
                mock.patch.object(tdq_lsp, "_do_ngon_ngu", wraps=tdq_lsp._do_ngon_ngu) as scan, \
                mock.patch.object(tdq_lsp, "_chay_doctor", side_effect=[
                    ({"python": ("running", "")}, ""),
                    ({"python": ("failed", "disconnected")}, "")]) as doctor:
            with tdq_readiness.probe_context(self.root, mode="auto", request="request-a", handoff={}):
                self.assertTrue(tdq_lsp.bac3_language_server(self.root).dat)
                release = self.root / "docs/tdq/.tdq-phat-hanh.json"
                release.write_text('{"cap_nhat":"later"}', encoding="utf-8")
                self.assertFalse(tdq_lsp.bac3_language_server(self.root).dat)
        self.assertEqual(scan.call_count, 1)
        self.assertEqual(doctor.call_count, 2)

    def test_binary_content_change_invalidates_version_and_disconnect_is_live(self):
        binary = self.root / "agent-lsp.exe"
        binary.write_bytes(b"one")
        with mock.patch.object(tdq_lsp.shutil, "which", return_value=str(binary)), \
                mock.patch.object(tdq_lsp, "_run", return_value=(0, "version one")) as run:
            with tdq_readiness.probe_context(self.root, mode="auto", request="request-a"):
                tdq_lsp.bac1_binary()
                tdq_lsp.bac1_binary()
                self.assertEqual(run.call_count, 1)
                binary.write_bytes(b"two")
                tdq_lsp.bac1_binary()
                self.assertEqual(run.call_count, 2)
                with mock.patch.object(tdq_lsp.shutil, "which", return_value=None):
                    self.assertFalse(tdq_lsp.bac1_binary().dat)

    def test_graph_freshness_memo_cleared_each_ladder(self):
        names = ["bac1_binary", "bac2_mcp", "bac3_language_server", "bac4_quyen_tool",
                 "bac5_hook_xung_dot", "bac6_cau_hinh_goc_import", "bac7_graphify", "bac8_module"]
        with contextlib.ExitStack() as stack:
            for i, name in enumerate(names, 1):
                stack.enter_context(mock.patch.object(tdq_lsp, name, return_value=tdq_lsp.Bac(i, name, True)))
            clear = stack.enter_context(mock.patch.object(tdq_lsp._moc_code_moi_nhat, "cache_clear"))
            tdq_lsp.chay_kiem(self.root)
            tdq_lsp.chay_kiem(self.root)
        self.assertEqual(clear.call_count, 2)


if __name__ == "__main__":
    unittest.main()
