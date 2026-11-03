"""Test for scripts/utf8_io.py — the module that keeps a Vietnamese line from killing a run.

Why this test exists, measured on a stock Windows 11 + Python 3.13 machine: Python picks the
console encoding from the locale (cp1252 there), so every `print` carrying `✓`, `✗` or
Vietnamese raises UnicodeEncodeError. The SessionStart hook died on exactly that line and took
the whole turn down with it — 670 failures / 97 errors across the suite, dropping to 357 / 7 the
moment UTF-8 was forced.

Test groups, selectable with `-k`:
    chokepoint  — the two shared modules every other file already goes through
    entrypoint  — every file with a `__main__` block reaches the module somehow
    log         — the log service is on by default and mutes with TDQ_LOG=0
"""
import io
import os
import subprocess
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))

import utf8_io  # noqa: E402 — the module under test


SCRIPT_DIRS = (os.path.join(ROOT, "scripts"), os.path.join(ROOT, "hooks", "scripts"))
# A source line that proves the file reaches the module, directly or through a shared one.
REACHES = ("import utf8_io", "import tdq_state", "_common")


def entry_points():
    """Every .py file under scripts/ and hooks/scripts/ that runs as a program.

    `utf8_io.py` is excluded: it IS the module, and a file cannot import itself.
    """
    found = []
    for folder in SCRIPT_DIRS:
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".py") or name == "utf8_io.py":
                continue
            path = os.path.join(folder, name)
            with io.open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            if '__name__ == "__main__"' in text:
                found.append((path, text))
    return found


class FakeStream:
    """A stream that records how it was reconfigured, like sys.stdout does."""

    def __init__(self, encoding="cp1252"):
        self.encoding = encoding
        self.calls = []

    def reconfigure(self, **kwargs):
        self.calls.append(kwargs)
        self.encoding = kwargs.get("encoding", self.encoding)


class PlainStream:
    """A stream with no `reconfigure` at all — what a test harness usually swaps in."""

    def __init__(self, encoding="cp1252"):
        self.encoding = encoding


class ForceUtf8Test(unittest.TestCase):
    """The core behaviour: switch the stream, and never make things worse."""

    def test_doi_stream_cp1252_sang_utf8(self):
        out, err = FakeStream(), FakeStream()
        changed = utf8_io.force_utf8(out, err)
        self.assertEqual(out.encoding.lower(), "utf-8")
        self.assertEqual(err.encoding.lower(), "utf-8")
        self.assertEqual(changed, 2)

    def test_dung_errors_replace(self):
        """One stray byte must not kill a hook — the whole turn dies with it."""
        out = FakeStream()
        utf8_io.force_utf8(out, FakeStream())
        self.assertEqual(out.calls[0].get("errors"), "replace")

    def test_goi_hai_lan_khong_doi_them_gi(self):
        """Idempotent: several entry points import it in one process."""
        out, err = FakeStream(), FakeStream()
        utf8_io.force_utf8(out, err)
        first = list(out.calls)
        changed = utf8_io.force_utf8(out, err)
        self.assertEqual(out.calls, first)
        self.assertEqual(changed, 0)

    def test_stream_da_utf8_thi_bo_qua(self):
        out = FakeStream(encoding="utf-8")
        changed = utf8_io.force_utf8(out, FakeStream(encoding="UTF-8"))
        self.assertEqual(changed, 0)
        self.assertEqual(out.calls, [])

    def test_stream_khong_reconfigure_duoc_thi_im_lang(self):
        """A stream replaced by a test harness has no reconfigure; that is not an error."""
        changed = utf8_io.force_utf8(FakeStream(), PlainStream())
        self.assertEqual(changed, 1)

    def test_stream_none_khong_no(self):
        """Under pythonw stdout can be None."""
        self.assertEqual(utf8_io.force_utf8(None, None), 0)


class ChokepointTest(unittest.TestCase):
    """The two shared modules every other file already goes through."""

    def test_chokepoint_tdq_state_nap_utf8_io(self):
        path = os.path.join(ROOT, "scripts", "tdq_state.py")
        with io.open(path, encoding="utf-8") as f:
            self.assertIn("import utf8_io", f.read())

    def test_chokepoint_common_nap_utf8_io(self):
        path = os.path.join(ROOT, "hooks", "scripts", "_common.py")
        with io.open(path, encoding="utf-8") as f:
            self.assertIn("import utf8_io", f.read())


class EntryPointTest(unittest.TestCase):
    """Every program file must reach the module, or it dies on the first Vietnamese line."""

    def test_entrypoint_moi_file_deu_toi_duoc_utf8_io(self):
        missing = [os.path.relpath(p, ROOT).replace(os.sep, "/")
                   for p, text in entry_points()
                   if not any(mark in text for mark in REACHES)]
        self.assertEqual(missing, [], f"{len(missing)} entry point(s) never reach utf8_io")

    def test_entrypoint_in_duoc_tieng_viet_duoi_cp1252(self):
        """The real proof: run a child with a cp1252 stdout and print the characters that broke."""
        code = ("import sys, os; sys.path.insert(0, %r); import utf8_io; "
                "print('\\u2713 \\u2717 duy\\u1ec7t')" % os.path.join(ROOT, "scripts"))
        env = dict(os.environ)
        env.pop("PYTHONUTF8", None)
        env.pop("PYTHONIOENCODING", None)
        env["PYTHONLEGACYWINDOWSSTDIO"] = "1"
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                              env=env, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))
        self.assertIn("duy", proc.stdout.decode("utf-8", "replace"))


class LogTest(unittest.TestCase):
    """Log service on by default, muted with TDQ_LOG=0 — the standing requirement."""

    def _run(self, env_extra):
        code = ("import sys; sys.path.insert(0, %r); import utf8_io; "
                "utf8_io.force_utf8()" % os.path.join(ROOT, "scripts"))
        env = dict(os.environ, **env_extra)
        return subprocess.run([sys.executable, "-c", code], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              env=env, timeout=60)

    def test_log_bat_mac_dinh_co_timestamp(self):
        proc = self._run({"TDQ_LOG": "1", "TDQ_UTF8_LOG_FORCE": "1"})
        self.assertRegex(proc.stderr, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        proc = self._run({"TDQ_LOG": "0", "TDQ_UTF8_LOG_FORCE": "1"})
        self.assertEqual(proc.stderr.strip(), "")

    def test_pipe_thi_im_du_co_doi(self):
        """2026-09-21: stderr là pipe thì không in dòng 'forced' — bên gọi không tắt được nó.
        Dựng hai luồng cp1252 giả để có thay đổi thật trên mọi hệ điều hành."""
        code = ("import io, sys; sys.path.insert(0, %r); import utf8_io; "
                "o = io.TextIOWrapper(io.BytesIO(), encoding='cp1252'); "
                "e = io.TextIOWrapper(io.BytesIO(), encoding='cp1252'); "
                "print(utf8_io.force_utf8(o, e))" % os.path.join(ROOT, "scripts"))
        env = dict(os.environ, TDQ_LOG="1")
        env.pop("TDQ_UTF8_LOG_FORCE", None)
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                              encoding="utf-8", errors="replace", env=env, timeout=60)
        self.assertEqual(proc.stdout.strip(), "2")          # có đổi thật
        self.assertNotIn("forced", proc.stderr)             # nhưng im trên pipe
        env["TDQ_UTF8_LOG_FORCE"] = "1"
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                              encoding="utf-8", errors="replace", env=env, timeout=60)
        self.assertIn("forced 2 stream(s)", proc.stderr)    # bật lại được


if __name__ == "__main__":
    unittest.main()
