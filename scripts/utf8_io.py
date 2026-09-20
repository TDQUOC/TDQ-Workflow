#!/usr/bin/env python3
"""Force stdout/stderr to UTF-8 so one Vietnamese line cannot kill a run.

Why this module exists, measured on a stock Windows 11 + Python 3.13 machine: Python takes the
console encoding from the locale, which is cp1252 there. Every `print` carrying `✓`, `✗` or
Vietnamese then raises UnicodeEncodeError and the process dies. The SessionStart hook died on
exactly that line, and a dead hook costs the whole turn. Across the suite it was 670 failures
and 97 errors, dropping to 357 and 7 the moment UTF-8 was forced.

`errors="replace"` is deliberate: a single unmappable character must degrade to `?`, never kill
a hook. It applies to what we PRINT only — reading files keeps its own strict handling, so a
corrupt input still fails loudly where it should.

Importing this module runs `force_utf8()` once, which is why one import line at the top of an
entry point is the whole integration. Importing it again in the same process is a no-op.

Log service: ISO timestamps on stderr, on by default, muted with `TDQ_LOG=0`. It stays silent
when nothing changed, so a normal run on macOS adds no noise; set `TDQ_UTF8_LOG_FORCE=1` to log
the no-op case too.

This module deliberately keeps its own two-line log helper instead of importing the shared one
from `tdq_state`: `tdq_state` imports THIS module, and reaching back would be a circular import.
"""
import datetime
import os
import sys

TARGET_ENCODING = "utf-8"
# How an unmappable character is handled on the way OUT. Never used for reading.
ERROR_POLICY = "replace"

_already_forced = False


def log_enabled():
    """True unless the caller muted logging with TDQ_LOG=0."""
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    if log_enabled():
        stamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        print(f"[{stamp}] utf8_io: {message}", file=sys.stderr)


def _needs_switch(stream):
    """True when the stream exists, can be reconfigured, and is not UTF-8 yet."""
    if stream is None or not hasattr(stream, "reconfigure"):
        return False
    return (getattr(stream, "encoding", "") or "").lower() not in ("utf-8", "utf8")


def force_utf8(out=None, err=None):
    """Switch `out` and `err` to UTF-8. Returns how many streams actually changed.

    Defaults to the real `sys.stdout`/`sys.stderr`. A stream that is None, that carries no
    `reconfigure` (a test harness often swaps one in), or that already speaks UTF-8 is left
    alone rather than treated as an error.
    """
    streams = ((sys.stdout if out is None else out), (sys.stderr if err is None else err))
    changed = 0
    for stream in streams:
        if not _needs_switch(stream):
            continue
        stream.reconfigure(encoding=TARGET_ENCODING, errors=ERROR_POLICY)
        changed += 1
    if changed:
        _log(f"forced {changed} stream(s) to {TARGET_ENCODING}/{ERROR_POLICY}")
    elif os.environ.get("TDQ_UTF8_LOG_FORCE") == "1":
        _log(f"no stream needed switching (already {TARGET_ENCODING})")
    return changed


def _force_once():
    """Run the switch the first time this module is imported in a process."""
    global _already_forced
    if _already_forced:
        return 0
    _already_forced = True
    return force_utf8()


_force_once()

if __name__ == "__main__":
    print(f"utf8_io: stdout={getattr(sys.stdout, 'encoding', None)} "
          f"stderr={getattr(sys.stderr, 'encoding', None)}")
