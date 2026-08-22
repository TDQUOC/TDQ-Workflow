"""P1 — xử lý state file: S1–S8 của spec 0.3.0 (mỗi yêu cầu 1 test)."""
import glob
import json
import os
import tempfile
import unittest
from unittest import mock

from helper import ROOT, run_state_cli, run_state_cli_in, tdq_state  # noqa: F401


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class StateFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _init(self, lane="full"):
        rc, _, err = run_state_cli(self.cwd, "init", "2026-07-29-0900-demo", lane)
        self.assertEqual(rc, 0, err)

    # S1 -------------------------------------------------------------
    def test_atomic_write_keeps_old_on_failure(self):
        self._init()
        before = _read(tdq_state.state_path(self.cwd))
        state = tdq_state.load(self.cwd)
        state["phase"] = "spec"
        with mock.patch("tdq_state.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                tdq_state.save(self.cwd, state)
        after = _read(tdq_state.state_path(self.cwd))
        self.assertEqual(before, after)
        self.assertEqual(glob.glob(os.path.join(self.cwd, "docs", "tdq", ".tdq-*.tmp")), [])

    # S2 -------------------------------------------------------------
    def test_corrupt_state_recovers(self):
        self._init()
        with open(tdq_state.state_path(self.cwd), "w", encoding="utf-8") as f:
            f.write("{ khong phai json")
        rc, out, err = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0, err)
        self.assertIn("[TDQ:NEXT]", out)
        kept = glob.glob(os.path.join(self.cwd, "docs", "tdq", "state.json.corrupt-*"))
        self.assertEqual(len(kept), 1, kept)
        self.assertIn("is corrupt", err)

    def test_corrupt_non_dict_recovers(self):
        self._init()
        with open(tdq_state.state_path(self.cwd), "w", encoding="utf-8") as f:
            f.write("[1,2,3]")
        self.assertIsNone(tdq_state.load(self.cwd))
        self.assertTrue(glob.glob(os.path.join(self.cwd, "docs", "tdq", "state.json.corrupt-*")))

    # S3 -------------------------------------------------------------
    def test_backfill_and_preserve_unknown_keys(self):
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"))
        with open(tdq_state.state_path(self.cwd), "w", encoding="utf-8") as f:
            json.dump({"schema_version": 2, "active_request": "r1", "cua_toi": 42}, f)
        state = tdq_state.load(self.cwd)
        self.assertEqual(state["schema_version"], 4)
        self.assertEqual(state["active_request"], "r1")
        self.assertFalse(state["spec_approved"])          # khoá thiếu được bù
        self.assertEqual(state["cua_toi"], 42)            # khoá lạ được giữ
        tdq_state.save(self.cwd, state)
        self.assertEqual(tdq_state.load(self.cwd)["cua_toi"], 42)

    # S4 -------------------------------------------------------------
    def test_invalid_enum_tolerated(self):
        self._init()
        state = tdq_state.load(self.cwd)
        state["phase"] = "xyz"
        state["lane"] = "sai"
        state["implement_mode"] = "bay"
        tdq_state.save(self.cwd, state)
        rc, out, err = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0, err)
        self.assertIn("phase idle", out)
        self.assertIn("set phase=", err)                   # có hướng dẫn khôi phục

    # S5 -------------------------------------------------------------
    def test_project_path_printed(self):
        self._init()
        rc, out, _ = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0)
        self.assertIn(f"Project: {os.path.abspath(self.cwd)}", out)
        md = _read(tdq_state.state_md_path(self.cwd))
        self.assertIn(f"Project: {os.path.abspath(self.cwd)}", md)

    # S6 -------------------------------------------------------------
    def test_shadow_and_orphan_warning(self):
        self._init()
        sub = os.path.join(self.cwd, "sub", "docs", "tdq")
        os.makedirs(sub)
        with open(os.path.join(sub, "state.json"), "w", encoding="utf-8") as f:
            json.dump(tdq_state.default_state(), f)
        found = tdq_state.find_shadow_states(self.cwd)
        self.assertTrue(any("sub" in f for f in found), found)

        orphan = os.path.join(self.cwd, "other", "docs", "tdq")
        os.makedirs(orphan)
        with open(os.path.join(orphan, "STATE.md"), "w", encoding="utf-8") as f:
            f.write("# x\n")
        found = tdq_state.find_shadow_states(self.cwd)
        self.assertTrue(any("orphan mirror" in f for f in found), found)

    # S7 -------------------------------------------------------------
    def test_concurrent_write_warns_but_writes(self):
        self._init()
        state = tdq_state.load(self.cwd)
        stamp = state["updated_at"]
        other = tdq_state.load(self.cwd)
        other["phase"] = "analyze"
        other["updated_at"] = "2099-01-01T00:00:00+07:00"
        with open(tdq_state.state_path(self.cwd), "w", encoding="utf-8") as f:
            json.dump(other, f)
        state["phase"] = "spec"
        with mock.patch("tdq_state._warn") as warned:
            tdq_state.save(self.cwd, state, expect_updated_at=stamp)
        self.assertTrue(warned.called)
        self.assertEqual(tdq_state.load(self.cwd)["phase"], "spec")   # vẫn ghi

    # S8 -------------------------------------------------------------
    def test_exit_codes_matrix(self):
        commands = [("next",), ("get",), ("get", "lane"), ("set", "phase=spec"),
                    ("approve", "spec"), ("reset",)]
        broken = [
            ("thieu state", lambda: None),
            ("state hong", lambda: self._write_raw("{{{")),
            ("enum sai", lambda: self._write_raw(json.dumps({"phase": "xyz", "lane": "z"}))),
            ("khoa la", lambda: self._write_raw(json.dumps({"la": 1}))),
        ]
        for label, prepare in broken:
            for cmd in commands:
                with self.subTest(state=label, cmd=cmd):
                    for path in glob.glob(os.path.join(self.cwd, "docs", "tdq", "*")):
                        os.remove(path)
                    prepare()
                    rc, _, err = run_state_cli(self.cwd, *cmd)
                    self.assertEqual(rc, 0, f"{label}/{cmd}: {err}")

    def test_syntax_error_exits_2(self):
        self._init()
        for cmd in [("khong-co-lenh",), ("set", "khong_co_key=1"), ("set", "phase=xyz"),
                    ("approve", "linh-tinh"), ("init",), ("next", "--sai")]:
            with self.subTest(cmd=cmd):
                rc, _, err = run_state_cli(self.cwd, *cmd)
                self.assertEqual(rc, 2, f"{cmd}: rc={rc}")
                self.assertIn("Usage:", err)

    def _write_raw(self, text):
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        with open(tdq_state.state_path(self.cwd), "w", encoding="utf-8") as f:
            f.write(text)

    # mirror ---------------------------------------------------------
    def test_state_md_shape(self):
        self._init()
        md = _read(tdq_state.state_md_path(self.cwd))
        lines = [l for l in md.splitlines() if l.strip()]
        self.assertLessEqual(len(md.splitlines()), 30, md)
        self.assertTrue(md.startswith("# TDQ STATE (generated — do not hand-edit)"))
        for heading in ("## Where we are", "## What comes next"):
            self.assertIn(heading, md)
        for label in ("| Request |", "| Lane |", "| Phase |", "| Spec |", "| Plan |",
                      "| Run mode |"):
            self.assertIn(label, md)
        self.assertTrue(any("tdq_state.py" in l for l in lines))

    def test_save_writes_mirror(self):
        self._init()
        run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/x.md", "phase=spec")
        md = _read(tdq_state.state_md_path(self.cwd))
        self.assertIn("docs/tdq/spec/x.md — ⏳ awaiting approval", md)
        run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        md = _read(tdq_state.state_md_path(self.cwd))
        self.assertIn("✔ approved", md)
        self.assertIn("| Phase | spec |", md)

    # log service ----------------------------------------------------
    def test_log_toggle(self):
        self._init()
        self._write_raw(json.dumps({"phase": "xyz", "active_request": "r"}))
        rc, _, err = run_state_cli(self.cwd, "next")
        self.assertEqual(rc, 0)
        self.assertIn("invalid phase in state", err)
        self.assertRegex(err, r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")   # có timestamp
        env = dict(os.environ, TDQ_PROJECT_DIR=self.cwd, TDQ_LOG="0")
        import subprocess
        import sys
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "tdq_state.py"), "next"],
                              capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
