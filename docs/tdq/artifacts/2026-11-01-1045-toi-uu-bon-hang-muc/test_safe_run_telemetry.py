"""Synthetic personal-config fixtures plus real isolated child processes."""
from contextlib import ExitStack, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

import safe_run_telemetry as adapter


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="tdq-telemetry-fixture-")
        self.addCleanup(folder.cleanup)
        self.base = Path(folder.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.config = self.home / ".claude.json"
        self.value = {"setting": "PRIVATE_CONFIG_SENTINEL", "pluginUsage": {
            "example": {"usageCount": 1, "lastUsedAt": 123, "enabled": True}}}
        self.config.write_text(json.dumps(self.value), encoding="utf-8")

    def execute(self, replacement, label="fixture", **patches):
        payload = self.base / "replacement.json"
        payload.write_text(replacement, encoding="utf-8")
        code = "from pathlib import Path; Path(" + repr(str(self.config)) + ").write_bytes(Path(" + repr(str(payload)) + ").read_bytes())"
        return self.execute_code(code, label, **patches)

    def execute_code(self, code, label="fixture", **patches):
        with ExitStack() as stack:
            stack.enter_context(redirect_stdout(io.StringIO()))
            for name, value in patches.items():
                stack.enter_context(patch.object(adapter.legacy, name, value))
            status, path = adapter.run_command([sys.executable, "-c", code], label,
                self.base / "evidence", 15, adapter.ROOT, protected_home=self.home)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertNotIn("PRIVATE_CONFIG_SENTINEL", path.read_text(encoding="utf-8"))
        return status, path, receipt

    def test_telemetry_values_only_pass(self):
        changed = deepcopy(self.value)
        changed["pluginUsage"]["example"].update(usageCount=4, lastUsedAt=456)
        status, path, receipt = self.execute(json.dumps(changed))
        self.assertEqual(status, 0)
        adapter.validate_receipt(path, adapter.ROOT)
        self.assertNotEqual(receipt["config_raw_before"], receipt["config_raw_after"])
        self.assertEqual(receipt["config_before"], receipt["config_after"])
        self.assertEqual(receipt["isolation"]["cleanup"], "complete")
        self.assertEqual(receipt["source_before"], receipt["source_after"])

    def test_setting_change_fails(self):
        changed = deepcopy(self.value)
        changed["setting"] = "other"
        status, path, receipt = self.execute(json.dumps(changed))
        self.assertEqual(status, 126)
        self.assertEqual(receipt["failure_stage"], "config_guard")
        with self.assertRaises(ValueError):
            adapter.validate_receipt(path, adapter.ROOT)

    def test_projection_protects_presence_type_unknown_and_plugins(self):
        before = adapter.telemetry_projection(json.dumps(self.value))
        variants = []
        for key in ("usageCount", "lastUsedAt", "enabled"):
            changed = deepcopy(self.value)
            del changed["pluginUsage"]["example"][key]
            variants.append(changed)
        changed = deepcopy(self.value)
        changed["pluginUsage"]["new"] = {"usageCount": 1}
        variants.append(changed)
        changed = deepcopy(self.value)
        changed["pluginUsage"]["example"]["usageCount"] = "1"
        variants.append(changed)
        changed = deepcopy(self.value)
        changed["pluginUsage"]["example"]["enabled"] = False
        variants.append(changed)
        for changed in variants:
            with self.subTest(change=variants.index(changed)):
                self.assertNotEqual(before, adapter.telemetry_projection(json.dumps(changed)))

    def test_invalid_json_shapes_failclosed(self):
        for value in ('{bad', '{"setting":1,"setting":2}', '[]',
                      '{"value":NaN}', '{"value":Infinity}', '{"value":1e999}', '{"pluginUsage":[]}',
                      '{"pluginUsage":{"a":null}}',
                      '{"pluginUsage":{"a":{"usageCount":{}}}}'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                adapter.telemetry_projection(value)

    def test_scalar_types_remain_distinct(self):
        digests = []
        for value in (None, False, 0, 0.0, "0"):
            config = {"pluginUsage": {"a": {"usageCount": value}}}
            digests.append(adapter.legacy.digest(adapter.telemetry_projection(json.dumps(config))))
        self.assertEqual(len(set(digests)), 5)

    def test_missing_both_pass_but_presence_change_fails(self):
        self.config.unlink()
        status, path, receipt = self.execute_code("print('fixture control')")
        self.assertEqual(status, 0)
        adapter.validate_receipt(path, adapter.ROOT)
        self.assertEqual(receipt["config_raw_before"][".claude.json"], "MISSING")
        status, path, _ = self.execute(json.dumps(self.value))
        self.assertEqual(status, 126)
        with self.assertRaises(ValueError):
            adapter.validate_receipt(path, adapter.ROOT)
        status, _, _ = self.execute_code("from pathlib import Path; Path(" + repr(str(self.config)) + ").unlink()")
        self.assertEqual(status, 126)

    def test_missing_telemetry_key_and_invalid_post_json_fail(self):
        changed = deepcopy(self.value)
        del changed["pluginUsage"]["example"]["usageCount"]
        status, _, _ = self.execute(json.dumps(changed))
        self.assertEqual(status, 126)
        status, path, receipt = self.execute('{bad')
        self.assertEqual(status, 125)
        self.assertEqual(receipt["failure_stage"], "config_after")
        with self.assertRaises(ValueError):
            adapter.validate_receipt(path, adapter.ROOT)

    def test_read_error_fails_closed_without_child(self):
        read = Path.read_bytes
        def unreadable(path):
            if path == self.config:
                raise PermissionError("fixture permission denied")
            return read(path)
        with patch.object(Path, "read_bytes", unreadable):
            status, _, receipt = self.execute_code("raise RuntimeError('child must not execute')")
        self.assertEqual(status, 125)
        self.assertIsNone(receipt["exit_code"])
        self.assertEqual(receipt["failure_stage"], "config_before")

    def test_source_and_dependency_guards_still_fail(self):
        source = adapter.legacy.source_snapshot(adapter.ROOT)
        for name, operation in (
            ("source_snapshot", unittest.mock.Mock(side_effect=[source, {"changed": True}])),
            ("dependency_snapshot", lambda before: {**before, "changed": True}),
        ):
            with self.subTest(guard=name):
                status, path, receipt = self.execute(json.dumps(self.value), **{name: operation})
                self.assertEqual(status, 126)
                self.assertIn(name.split("_")[0] + "_guard", [row["stage"] for row in receipt["failures"]])
                with self.assertRaises(ValueError):
                    adapter.validate_receipt(path, adapter.ROOT)

    def test_cleanup_failure_still_fails(self):
        cleanup = adapter.legacy.cleanup_sandbox
        def denied(*args):
            raise PermissionError("fixture cleanup denied")
        status, path, receipt = self.execute(json.dumps(self.value), cleanup_sandbox=denied)
        cleanup(Path(receipt["isolation"]["sandbox"]), Path(receipt["isolation"]["parent"]))
        self.assertEqual(status, 125)
        self.assertEqual(receipt["isolation"]["cleanup"], "failed")
        with self.assertRaises(ValueError):
            adapter.validate_receipt(path, adapter.ROOT)

    def test_validator_rejects_policy_audit_capture_and_raw_mutation(self):
        status, path, receipt = self.execute(json.dumps(self.value))
        self.assertEqual(status, 0)
        variants = []
        for key in ("config_policy", "config_raw_before", "policy_after"):
            changed = deepcopy(receipt)
            del changed[key]
            variants.append(changed)
        changed = deepcopy(receipt)
        changed["schema"] = "tdq-safe-run/unknown"
        variants.append(changed)
        for key in ("exit_code", "harness_exit_code"):
            changed = deepcopy(receipt)
            changed[key] = False
            variants.append(changed)
        changed = deepcopy(receipt)
        changed["capture"]["stdout.txt"] = "failed"
        variants.append(changed)
        changed = deepcopy(receipt)
        del changed["config_raw_before"][".codex/auth.json"]
        variants.append(changed)
        changed = deepcopy(receipt)
        changed["config_raw_before"][".codex/auth.json"] = "a" * 64
        variants.append(changed)
        for changed in variants:
            with self.subTest(variant=variants.index(changed)):
                changed["sha256"] = adapter.legacy.digest({key: value for key, value in changed.items() if key != "sha256"})
                adapter.legacy.write_json(path, changed)
                with self.assertRaises(ValueError):
                    adapter.validate_receipt(path, adapter.ROOT)
        adapter.legacy.write_json(path, receipt)
        (path.parent / "stdout.txt").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "digest"):
            adapter.validate_receipt(path, adapter.ROOT)

    def test_normal_dispatch_relaunches_adapter_and_restores_globals(self):
        original_file, original_run = adapter.legacy.__file__, adapter.legacy.run_command
        seen = []
        def cli():
            seen.append(adapter.legacy.__file__)
            return 0
        with patch.object(adapter.legacy, "main", cli):
            self.assertEqual(adapter.main(), 0)
        self.assertEqual(seen, [str(Path(adapter.__file__).resolve())])
        self.assertEqual(adapter.legacy.__file__, original_file)
        self.assertIs(adapter.legacy.run_command, original_run)

    def test_scope_dispatch_requires_explicit_current_bindings(self):
        scope = adapter._load("_tdq_telemetry_scope_fixture", adapter.HERE / "verify_scope.py")
        scope.load_helpers(adapter.ROOT)
        index = scope.read_json(adapter.HERE / "evidence-index.json")
        scope.load_policy_adapter(index, adapter.ROOT)
        self.assertIsNotNone(scope.POLICY_ADAPTER)
        status, path, _ = self.execute(json.dumps(self.value))
        self.assertEqual(status, 0)
        binding = {"path": str(path), "sha256": adapter.legacy.file_hash(path)}
        scope.guarded_receipt(binding, self.base, current=False)
        scope.POLICY_ADAPTER = None
        with self.assertRaisesRegex(ValueError, "explicitly bound"):
            scope.guarded_receipt(binding, self.base, current=False)
        index["receipt_policy"]["adapter"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            scope.load_policy_adapter(index, adapter.ROOT)

    def test_legacy_strict_validator_does_not_accept_new_schema(self):
        status, path, _ = self.execute(json.dumps(self.value))
        self.assertEqual(status, 0)
        with self.assertRaisesRegex(ValueError, "schema"):
            adapter.validator.validate_receipt(path, adapter.ROOT)

    def test_mismatched_frozen_helper_is_rejected_before_module_execution(self):
        read = Path.read_bytes
        def changed(path):
            if path == adapter.OLD / "safe_run.py":
                return b"raise RuntimeError('untrusted module executed')"
            return read(path)
        with patch.object(Path, "read_bytes", changed), patch.object(
                adapter.importlib.util, "spec_from_file_location",
                side_effect=AssertionError("Module execution attempted before hash verification")):
            with self.assertRaisesRegex(ValueError, "Frozen legacy helper"):
                runpy.run_path(str(Path(adapter.__file__)), run_name="_untrusted_helper_fixture")

    def test_receipt_duplicate_keys_and_nonfinite_values_fail_closed(self):
        status, path, receipt = self.execute(json.dumps(self.value))
        self.assertEqual(status, 0)
        original = path.read_text(encoding="utf-8")
        duplicate = '{"schema":"unknown",' + original.lstrip()[1:]
        path.write_text(duplicate, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            adapter.validate_receipt(path, adapter.ROOT)
        for value in (float("nan"), float("inf"), -float("inf")):
            receipt["unexpected_number"] = value
            receipt["sha256"] = adapter.legacy.digest({key: item for key, item in receipt.items() if key != "sha256"})
            adapter.legacy.write_json(path, receipt)
            with self.subTest(value=str(value)), self.assertRaisesRegex(ValueError, "Non-finite"):
                adapter.validate_receipt(path, adapter.ROOT)

    def test_existing_strict_scope_validator_selftests_remain_green(self):
        scope = adapter._load("_tdq_telemetry_strict_selftests", adapter.HERE / "verify_scope.py")
        scope.load_helpers(adapter.ROOT)
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(scope.self_test(adapter.HERE), 0)
        self.assertIn('"tests_run": 14', output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
