"""Test cho scripts/tdq_finish.py — gộp 4 việc bookkeeping cuối turn thành 1 lệnh."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "tdq_finish.py")


def _project(tmp):
    """Dựng project giả có state TDQ + 1 file .md sạch để lint."""
    os.makedirs(os.path.join(tmp, "docs", "tdq"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "docs", "workinglog"), exist_ok=True)
    doc = os.path.join(tmp, "docs", "ghi-chu.md")
    with open(doc, "w", encoding="utf-8") as fh:
        fh.write("# Ghi chú\n\n- Một dòng ngắn.\n")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "tdq_state.py"),
                    "init", "2026-08-05-0900-thu", "full"],
                   cwd=tmp, capture_output=True, text=True,
                   env={**os.environ, "TDQ_PROJECT_DIR": tmp})
    return doc


def _run(args, tmp, env=None):
    e = {**os.environ, "TDQ_PROJECT_DIR": tmp}
    if env:
        e.update(env)
    return subprocess.run([sys.executable, SCRIPT] + args,
                          cwd=tmp, capture_output=True, text=True, env=e)


class DryRunTest(unittest.TestCase):
    """T3.1 — xem trước không đụng gì, in đúng 1 dòng."""

    def test_dry_run_in_dung_1_dong_va_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            r = _run(["--dry-run", "--phase", "qc", "--log", "thử"], tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len([l for l in r.stdout.splitlines() if l.strip()]), 1, r.stdout)

    def test_dry_run_khong_ghi_working_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            _run(["--dry-run", "--log", "thử"], tmp)
            logs = os.listdir(os.path.join(tmp, "docs", "workinglog"))
        self.assertEqual(logs, [])

    def test_dry_run_khong_doi_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            _run(["--dry-run", "--phase", "qc"], tmp)
            with open(os.path.join(tmp, "docs", "tdq", "state.json"), encoding="utf-8") as fh:
                self.assertNotEqual(json.load(fh)["phase"], "qc")


class StepsTest(unittest.TestCase):
    """T3.2 — 4 bước đúng thứ tự, chạy hết kể cả khi một bước fail."""

    def test_chay_du_4_buoc_dung_thu_tu(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = _project(tmp)
            r = _run(["--files", doc, "--log", "tóm tắt việc", "--phase", "qc", "--verbose"], tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        order = [s for s in ("lint", "worklog", "phase", "graphify")
                 if s in r.stdout]
        self.assertEqual(order, ["lint", "worklog", "phase", "graphify"], r.stdout)

    def test_ghi_working_log_dung_file_ngay(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            _run(["--log", "tóm tắt việc hôm nay"], tmp)
            files = os.listdir(os.path.join(tmp, "docs", "workinglog"))
            self.assertEqual(len(files), 1, files)
            with open(os.path.join(tmp, "docs", "workinglog", files[0]), encoding="utf-8") as fh:
                self.assertIn("tóm tắt việc hôm nay", fh.read())

    def test_append_khong_de_len_entry_cu(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            _run(["--log", "entry một"], tmp)
            _run(["--log", "entry hai"], tmp)
            files = os.listdir(os.path.join(tmp, "docs", "workinglog"))
            with open(os.path.join(tmp, "docs", "workinglog", files[0]), encoding="utf-8") as fh:
                text = fh.read()
        self.assertIn("entry một", text)
        self.assertIn("entry hai", text)

    def test_doi_phase_qua_tdq_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            _run(["--phase", "qc"], tmp)
            with open(os.path.join(tmp, "docs", "tdq", "state.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["phase"], "qc")

    def test_lint_fail_van_chay_ba_buoc_con_lai_va_exit_khac_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            xau = os.path.join(tmp, "docs", "hong.md")
            with open(xau, "w", encoding="utf-8") as fh:
                # R2: lệnh nằm ngoài code block → doc_lint báo lỗi
                fh.write("# Hỏng\n\nChạy python3 scripts/tdq_state.py next để xem.\n")
            r = _run(["--files", xau, "--log", "vẫn phải ghi", "--phase", "qc"], tmp)
            with open(os.path.join(tmp, "docs", "tdq", "state.json"), encoding="utf-8") as fh:
                phase = json.load(fh)["phase"]
            files = os.listdir(os.path.join(tmp, "docs", "workinglog"))
        self.assertNotEqual(r.returncode, 0, "lint fail phải làm exit khác 0")
        self.assertEqual(phase, "qc", "bước phase vẫn phải chạy")
        self.assertEqual(len(files), 1, "bước working log vẫn phải chạy")

    def test_khong_co_viec_gi_van_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            r = _run([], tmp)
        self.assertEqual(r.returncode, 0, r.stderr)


class LogServiceTest(unittest.TestCase):
    """T3.3 — log service bật mặc định, tắt bằng TDQ_LOG=0."""

    def test_log_bat_mac_dinh_co_timestamp_va_ten_buoc(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            r = _run(["--log", "x", "--phase", "qc"], tmp)
        self.assertTrue(r.stderr.strip(), "log phải bật mặc định")
        self.assertIn("worklog", r.stderr)
        self.assertRegex(r.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_tat_log_bang_TDQ_LOG_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            r = _run(["--log", "x", "--phase", "qc"], tmp, env={"TDQ_LOG": "0"})
        self.assertEqual(r.stderr.strip(), "")

    def test_bat_log_nhieu_dong_hon_tat_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            on = _run(["--log", "x", "--phase", "qc"], tmp)
            off = _run(["--log", "y", "--phase", "report"], tmp, env={"TDQ_LOG": "0"})
        self.assertGreater(len(on.stderr.splitlines()), len(off.stderr.splitlines()))


class OutputSizeTest(unittest.TestCase):
    """T3.4 — mọi bước pass thì stdout ≤ 200 ký tự; chi tiết chỉ khi --verbose."""

    def test_stdout_ngan_khi_moi_buoc_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = _project(tmp)
            r = _run(["--files", doc, "--log", "x", "--phase", "qc"], tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertLessEqual(len(r.stdout), 200, r.stdout)

    def test_verbose_in_nhieu_hon(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = _project(tmp)
            ngan = _run(["--files", doc, "--log", "x", "--phase", "qc"], tmp)
            dai = _run(["--files", doc, "--log", "y", "--phase", "report", "--verbose"], tmp)
        self.assertGreater(len(dai.stdout), len(ngan.stdout))

    def test_buoc_fail_van_bao_ly_do_du_khong_verbose(self):
        with tempfile.TemporaryDirectory() as tmp:
            _project(tmp)
            xau = os.path.join(tmp, "docs", "hong.md")
            with open(xau, "w", encoding="utf-8") as fh:
                fh.write("# Hỏng\n\nChạy python3 scripts/tdq_state.py next để xem.\n")
            r = _run(["--files", xau], tmp)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("lint", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
