#!/usr/bin/env python3
"""context_surface.py — measure the SURFACE of the tdq-workflow plugin the way "an LLM reads it".

Two questions, two tables:

  1. By default: how heavy each documentation file is and which **load tier** it sits in —
        `always loaded` (present in every session) · `loaded on skill call` · `read on demand`.
        The load tier is what decides the cost, not the file size: a 1,000-character file in the
        `always loaded` tier costs more than a 10,000-character file read once a month.
  2. `--hooks`: how many milliseconds each hook costs per turn, measured repeatedly, median taken.

Usage:
        python3 scripts/context_surface.py                  # the surface table
        python3 scripts/context_surface.py --hooks           # the hook speed table
        python3 scripts/context_surface.py --hooks --runs 9  # change the number of runs
        python3 scripts/context_surface.py --quiet           # turn the progress log off

Log service: ISO timestamp, printed to **stderr**, on by default, turned off with `--quiet`
(or `TDQ_SURFACE_LOG=0`). The table always goes to **stdout** so it can be piped.
Exit: 0 finished · 2 bad syntax — the same contract as `tdq_state.py`.
"""

import argparse
import datetime
import glob
import json
import os
import statistics
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402 — shared, used to build a temp state for the hook measurement

# Token estimate: the SAME factor for every file so comparing files stays fair.
# 4 bytes/token is the factor `token_audit.py` uses; for accented text the real number is
# higher, so the token column here is a FLOOR ESTIMATE, not a tokenizer number.
BYTES_PER_TOKEN = 4

TIER_ALWAYS = "always loaded"
TIER_SKILL = "loaded on skill call"
TIER_LAZY = "read on demand"

FREQ_SESSION = "every session"
FREQ_ON_SKILL = "every skill call"
FREQ_ON_REF = "when the body links to it"
FREQ_ON_AGENT = "when a sub-agent runs"
FREQ_CODE = "0 — code runs outside the context"

HEADERS = ("file", "load tier", "chars (wc -c)", "est. tokens", "how often it enters context")


# ----------------------------------------------------------------- log service

_QUIET = False


def _log_enabled():
    return not _QUIET and os.environ.get("TDQ_SURFACE_LOG", "1") != "0"


def _log(message):
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------------- read files

def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _split_frontmatter(raw):
    """Split the YAML frontmatter off the body of a .md file.

    Returns `(frontmatter_bytes, body_bytes)`. No frontmatter → an empty first part.
    Why the split matters: the `description` in the frontmatter sits in EVERY session while the
    body is only loaded when the skill is called — merging the two would lie about the frequency.
    """
    if not raw.startswith(b"---"):
        return b"", raw
    end = raw.find(b"\n---", 3)
    if end < 0:
        return b"", raw
    cut = raw.find(b"\n", end + 1)
    if cut < 0:
        return raw, b""
    return raw[:cut + 1], raw[cut + 1:]


def _rel(path):
    return os.path.relpath(path, ROOT)


def _row(name, tier, size, freq):
    return [name, tier, f"{size:,}".replace(",", "."),
            f"{round(size / BYTES_PER_TOKEN):,}".replace(",", "."), freq]


# ---------------------------------------------------------------- surface scan

def scan(root=ROOT):
    """Scan the whole documentation surface, returning the list of table rows."""
    rows = []

    for skill in sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))):
        head, body = _split_frontmatter(_read(skill))
        rows.append(_row(f"{_rel(skill)} (description)", TIER_ALWAYS,
                         len(head), FREQ_SESSION))
        rows.append(_row(f"{_rel(skill)} (body)", TIER_SKILL,
                         len(body), FREQ_ON_SKILL))

    for ref in sorted(glob.glob(os.path.join(root, "skills", "*", "references", "*.md"))):
        rows.append(_row(_rel(ref), TIER_LAZY, len(_read(ref)), FREQ_ON_REF))

    for agent in sorted(glob.glob(os.path.join(root, "agents", "*.md"))):
        head, body = _split_frontmatter(_read(agent))
        rows.append(_row(f"{_rel(agent)} (description)", TIER_ALWAYS,
                         len(head), FREQ_SESSION))
        rows.append(_row(_rel(agent), TIER_LAZY, len(body), FREQ_ON_AGENT))

    for hook in sorted(glob.glob(os.path.join(root, "hooks", "scripts", "*.py"))):
        rows.append(_row(_rel(hook), TIER_LAZY, len(_read(hook)), FREQ_CODE))

    for doc in sorted(glob.glob(os.path.join(root, "portable", "**", "*.md"),
                                recursive=True)):
        rows.append(_row(_rel(doc), TIER_LAZY, len(_read(doc)), FREQ_ON_REF))

    mau = os.path.join(root, "docs", "claude-md-mau.md")
    if os.path.exists(mau):
        rows.append(_row(_rel(mau), TIER_ALWAYS, len(_read(mau)),
                         "every session (copied into CLAUDE.md)"))

    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    if os.path.exists(manifest):
        rows.append(_row(_rel(manifest), TIER_LAZY, len(_read(manifest)),
                         FREQ_CODE))

    _log(f"scanned {len(rows)} surface row(s)")
    return rows


def _num(cell):
    return int(cell.replace(".", ""))


def totals(rows):
    """Sum by load tier — this is the number worth looking at."""
    out = {}
    for row in rows:
        out.setdefault(row[1], 0)
        out[row[1]] += _num(row[2])
    return out


# ---------------------------------------------------------------- hook speed

FIXTURES = os.path.join(ROOT, "tests", "fixtures")

# Every entry = one REAL hook SITUATION, not one script file: the same
# `session_start.py` runs two different branches for `startup` and `compact`, and
# `edit_gate.py` branches on whether the edited file is source code or documentation.
HOOK_CASES = [
    ("session_start.py", "startup",
     {"hook_event_name": "SessionStart", "source": "startup"}),
    ("session_start.py", "compact",
     {"hook_event_name": "SessionStart", "source": "compact"}),
    ("prompt_context.py", "ordinary prompt", "prompt.json"),
    ("edit_gate.py", "editing source code", "edit_src.json"),
    ("edit_gate.py", "editing documentation", "edit_docs_spec.json"),
    ("bash_gate.py", "running a command", "bash_cmd.json"),
    ("stop_gate.py", "ending a turn", "stop.json"),
]


def _payload(spec):
    if isinstance(spec, dict):
        return dict(spec)
    with open(os.path.join(FIXTURES, spec), encoding="utf-8") as f:
        return json.load(f)


def _seed_project(tmp):
    """Build a temp project so the hooks have real state to run against — measuring on the real
    repo would append lines to the turn log of the very request being run."""
    state = tdq_state.default_state()
    state.update(active_request="do-toc-do-hook", lane="full", phase="implement")
    os.makedirs(os.path.join(tmp, "docs", "tdq"), exist_ok=True)
    tdq_state.save(tmp, state)
    return tmp


def measure_hooks(runs=5):
    """Run every hook situation `runs` times and take the median in milliseconds."""
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        cwd = _seed_project(tmp)
        for script, case, spec in HOOK_CASES:
            payload = _payload(spec)
            payload["cwd"] = cwd
            data = json.dumps(payload)
            path = os.path.join(ROOT, "hooks", "scripts", script)
            times = []
            for _ in range(runs):
                start = datetime.datetime.now()
                subprocess.run([sys.executable, path], input=data, text=True,
                               capture_output=True, timeout=60)
                times.append((datetime.datetime.now() - start).total_seconds() * 1000)
            median = statistics.median(times)
            rows.append([f"hooks/scripts/{script}", case,
                         f"{median:.1f}ms", f"{min(times):.1f}ms", f"{max(times):.1f}ms"])
            _log(f"{script} · {case}: median {median:.1f}ms")
    return rows


# ------------------------------------------------------------------------- in

def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        print("| " + " | ".join(row) + " |")


def main(argv=None):
    global _QUIET
    parser = argparse.ArgumentParser(
        description="Measure the context surface and hook speed of tdq-workflow.")
    parser.add_argument("--hooks", action="store_true",
                        help="time each hook instead of scanning the surface")
    parser.add_argument("--runs", type=int, default=5,
                        help="how many runs per hook with --hooks (default 5)")
    parser.add_argument("--quiet", action="store_true", help="turn the progress log off")
    args = parser.parse_args(argv)
    _QUIET = args.quiet

    if args.hooks:
        _log(f"measuring hook speed, {args.runs} run(s) per situation")
        rows = measure_hooks(args.runs)
        print(f"Measurement setup: every situation run {args.runs} time(s), "
              f"empty temp project, median taken.")
        print()
        print_table(("hook", "situation", "median", "fastest", "slowest"), rows)
        return 0

    _log("starting the surface scan")
    rows = scan()
    print_table(HEADERS, rows)
    print()
    for tier, size in sorted(totals(rows).items(), key=lambda kv: -kv[1]):
        print(f"TOTAL `{tier}`: {size:,} chars ≈ {round(size / BYTES_PER_TOKEN):,} tokens"
              .replace(",", "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
