#!/usr/bin/env python3
"""Ledger check for the debt markers the lean rules leave in the source (spec item 8).

A debt marker is a comment whose text starts with the marker prefix. It is honest debt
only when it names BOTH halves — the ceiling it accepts and the upgrade path out of it —
separated by a comma:

    # ponytail: global lock, per-account locks if throughput matters

A marker naming only a ceiling is rotten debt: the corner is cut and nobody knows what to
build when it starts to hurt. This check prints those and exits non-zero.

Usage:
    python3 scripts/kiem_no_marker.py                   # scripts/ and hooks/ of this repo
    python3 scripts/kiem_no_marker.py <path>...          # any file or directory
    python3 scripts/kiem_no_marker.py --quiet scripts/   # same, log service off

Prints `file:line: <marker>` for every marker missing its upgrade path; exit 1 when any is
missing, 0 when clean (a tree carrying no marker at all is clean), 2 on a path that does
not exist. A line that only names the pattern instead of declaring debt (this file, a doc
about the convention) carries `no-marker: allow` and is skipped.
Env: TDQ_LOG=0 turns the log service off (on by default, one ISO-timestamped line).
"""
import os
import sys
from datetime import datetime

EXIT_SYNTAX = 2
MARKER = "ponytail:"  # no-marker: allow — the pattern itself, not a debt entry
ALLOW = "no-marker: allow"
DEFAULT_DIRS = ("scripts", "hooks")
SCAN_SUFFIXES = (".py", ".md", ".json", ".sh", ".txt", ".toml", ".yml", ".yaml")
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".tdq-worktrees",
             "portable_claude", "portable_codex"}


def _log(message, quiet=False):
    """Log service: one ISO-timestamped line. Off with --quiet or TDQ_LOG=0."""
    if quiet or os.environ.get("TDQ_LOG", "1") == "0":
        return
    print(f"[{datetime.now().isoformat(timespec='seconds')}] kiem_no_marker: {message}")


def default_paths():
    """scripts/ and hooks/ of the repo THIS file lives in — never a hardcoded path."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return [p for p in (os.path.join(root, d) for d in DEFAULT_DIRS) if os.path.isdir(p)]


def collect(paths):
    """Expand files and directories into a sorted list of files to scan."""
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
            continue
        for root, dirs, names in os.walk(path):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            files += [os.path.join(root, n) for n in sorted(names)
                      if n.endswith(SCAN_SUFFIXES)]
    return sorted(set(files))


def marker_text(line):
    """The text after the marker prefix, or None when this line declares no marker.

    Matched on the raw line instead of parsed per language: the marker shows up in Python
    comments, markdown bullets and JSON strings alike, and a parser per file type buys
    nothing a substring search does not already get right.
    """
    if ALLOW in line:
        return None
    at = line.find(MARKER)
    if at < 0:
        return None
    return line[at + len(MARKER):].strip()


def has_upgrade_path(text):
    """True when the marker names both halves: a ceiling, a comma, an upgrade path."""
    ceiling, comma, upgrade = text.partition(",")
    return bool(comma) and bool(ceiling.strip()) and bool(upgrade.strip())


def scan_file(path):
    """Every marker of one file, as (line number, marker text, has upgrade path)."""
    rows = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for number, line in enumerate(f, 1):
                text = marker_text(line)
                if text is not None:
                    rows.append((number, text, has_upgrade_path(text)))
    except OSError:
        return []
    return rows


def quet(files):
    """Scan every file → (marker count, rows missing an upgrade path)."""
    total, rotten = 0, []
    for path in files:
        for number, text, ok in scan_file(path):
            total += 1
            if not ok:
                rotten.append((path, number, text))
    return total, rotten


def main(argv):
    quiet = False
    paths = []
    for arg in argv:
        if arg in ("--quiet", "-q"):
            quiet = True
        elif arg.startswith("-"):
            print("Usage: kiem_no_marker.py [--quiet] [<path>...]", file=sys.stderr)
            return EXIT_SYNTAX
        else:
            paths.append(arg)
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        for path in missing:
            print(f"⚠️ not found: {path}", file=sys.stderr)
        return EXIT_SYNTAX

    total, rotten = quet(collect(paths or default_paths()))
    for path, number, text in rotten:
        print(f"{path}:{number}: {MARKER} {text}".rstrip())
    _log(f"{total} marker(s), {len(rotten)} missing an upgrade path", quiet)
    return 1 if rotten else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
