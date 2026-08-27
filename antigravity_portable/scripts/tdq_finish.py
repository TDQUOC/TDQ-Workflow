#!/usr/bin/env python3
"""Fold the end-of-turn bookkeeping of the TDQ workflow into ONE command (stdlib only).

Four steps, always run in this order:
  1. lint     — `doc_lint.py` over the .md files just edited
  2. worklog  — append the summary to docs/workinglog/<today>.md
  3. phase    — `tdq_state.py set phase=<phase>`
  4. graphify — `graphify extract . --code-only` when a code file changed

Principles:
- A failing step does NOT block the steps after it; the exit code is the aggregate (0 = nothing failed).
- stdout stays <= 200 characters while every step passes; details print only with `--verbose` or on a failure.
- The log service is on by default to stderr (ISO timestamp + step name + result), off with TDQ_LOG=0.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb",
            ".php", ".c", ".h", ".cpp", ".swift", ".kt", ".lua", ".sh"}
STEP_TIMEOUT = 120
GRAPHIFY_TIMEOUT = 300
MAX_SHORT_OUT = 200
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: one ISO-timestamped line to stderr. Silenced by TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


def _project_dir():
    """Anchor on the project: TDQ_PROJECT_DIR > git root > cwd."""
    env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = current = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return start
        current = parent


def _run(cmd, cwd, timeout=STEP_TIMEOUT):
    """Run a child command, return (rc, output). Infrastructure errors become results too, never raised."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, f"over {timeout}s"
    except OSError as exc:
        return 1, str(exc)


def _changed_files(project):
    """The files git reports as changed (absolute paths). Not a git repo → empty."""
    rc, out = _run(["git", "status", "--porcelain"], project, timeout=30)
    if rc != 0:
        return []
    files = []
    for line in out.splitlines():
        name = line[3:].strip() if len(line) > 3 else ""
        if " -> " in name:                      # renamed file
            name = name.split(" -> ", 1)[1]
        name = name.strip('"')
        if name:
            files.append(os.path.join(project, name))
    return files


class Step:
    """One bookkeeping step: name, status (ok|skip|fail), short detail."""

    def __init__(self, name, status, detail=""):
        self.name, self.status, self.detail = name, status, detail

    def line(self):
        return f"{self.name} {self.status}" + (f" ({self.detail})" if self.detail else "")


def step_lint(project, files):
    docs = [f for f in files if f.endswith(".md") and os.path.exists(f)]
    if not docs:
        return Step("lint", "skip", "no .md file")
    rc, out = _run([sys.executable, os.path.join(SCRIPTS_DIR, "doc_lint.py")] + docs, project)
    if rc == 0:
        return Step("lint", "ok", f"{len(docs)} file")
    first = out.splitlines()[0] if out else "unknown error"
    return Step("lint", "fail", first[:120])


def step_worklog(project, summary):
    if not summary:
        return Step("worklog", "skip", "no --log")
    now = datetime.now()
    path = os.path.join(project, "docs", "workinglog", f"{now:%Y-%m-%d}.md")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as fh:
            if new:
                fh.write(f"# Working log {now:%Y-%m-%d}\n")
            fh.write(f"\n## {now:%H:%M}\n\n{summary.strip()}\n")
    except OSError as exc:
        return Step("worklog", "fail", str(exc)[:120])
    return Step("worklog", "ok", f"{now:%Y-%m-%d} {now:%H:%M}")


def step_phase(project, phase):
    if not phase:
        return Step("phase", "skip", "no --phase")
    env = dict(os.environ, TDQ_PROJECT_DIR=project)
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "tdq_state.py"), "set", f"phase={phase}"]
    try:
        p = subprocess.run(cmd, cwd=project, capture_output=True, text=True,
                           timeout=STEP_TIMEOUT, env=env)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return Step("phase", "fail", str(exc)[:120])
    if p.returncode != 0:
        return Step("phase", "fail", (p.stdout + p.stderr).strip()[:120])
    return Step("phase", "ok", phase)


def step_dong_so(project, phase):
    """Back to `idle` = the request is over → close the timing books into docs/tdq/timing.jsonl.

    Runs BEFORE the phase step: close the books first, then lower the flag, so the last
    phase window shuts at the right moment instead of bleeding into the `idle` stretch after it.
    """
    if phase != "idle":
        return Step("timing", "skip", "books close only on idle")
    env = dict(os.environ, TDQ_PROJECT_DIR=project)
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "tdq_timing.py"), "close"]
    try:
        p = subprocess.run(cmd, cwd=project, capture_output=True, text=True,
                           timeout=STEP_TIMEOUT, env=env)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return Step("timing", "fail", str(exc)[:120])
    if p.returncode != 0:
        return Step("timing", "fail", (p.stdout + p.stderr).strip()[:120])
    return Step("timing", "ok", "timing.jsonl written")


def step_graphify(project, files, skip):
    if skip:
        return Step("graphify", "skip", "--skip-graphify")
    if not any(os.path.splitext(f)[1] in CODE_EXT for f in files):
        return Step("graphify", "skip", "no code file changed")
    if not shutil.which("graphify"):
        return Step("graphify", "skip", "graphify not installed")
    rc, out = _run(["graphify", "extract", ".", "--code-only"], project, GRAPHIFY_TIMEOUT)
    if rc != 0:
        first = out.splitlines()[-1] if out else "unknown error"
        return Step("graphify", "fail", first[:120])
    return Step("graphify", "ok")


def summarize(steps):
    """One line of at most 200 characters for the everything-passed case."""
    mark = "✗" if any(s.status == "fail" for s in steps) else "✓"
    body = " · ".join(f"{s.name}={s.status}" for s in steps)
    line = f"{mark} tdq_finish: {body}"
    return line if len(line) <= MAX_SHORT_OUT else line[:MAX_SHORT_OUT - 1] + "…"


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="End-of-turn bookkeeping: lint → working log → phase → graphify.")
    ap.add_argument("--phase", help="the new phase, written through tdq_state.py")
    ap.add_argument("--log", dest="summary", help="summary appended to today's working log")
    ap.add_argument("--files", nargs="*", default=None,
                    help="the files just edited; left out, they come from `git status --porcelain`")
    ap.add_argument("--skip-graphify", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the 1-line intention, write nothing")
    ap.add_argument("--verbose", action="store_true", help="print the detail of every step")
    return ap.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    project = _project_dir()
    files = args.files if args.files is not None else _changed_files(project)
    files = [os.path.abspath(os.path.join(project, f)) for f in files]

    if args.dry_run:
        docs = sum(1 for f in files if f.endswith(".md"))
        print(f"dry-run: lint {docs} .md file(s) · worklog "
              f"{'yes' if args.summary else 'no'} · phase {args.phase or 'unchanged'} · "
              f"graphify {'no' if args.skip_graphify else 'if code changed'}")
        return 0

    _log(f"start · project={project} · {len(files)} file(s) changed")
    steps = []
    for run_step in (lambda: step_lint(project, files),
                     lambda: step_worklog(project, args.summary),
                     lambda: step_dong_so(project, args.phase),
                     lambda: step_phase(project, args.phase),
                     lambda: step_graphify(project, files, args.skip_graphify)):
        step = run_step()
        steps.append(step)
        _log(f"{step.name} → {step.status}" + (f" ({step.detail})" if step.detail else ""))

    failed = [s for s in steps if s.status == "fail"]
    print(summarize(steps))
    if args.verbose or failed:
        for s in (steps if args.verbose else failed):
            print(f"  - {s.line()}")
    _log(f"done · {len(failed)} step(s) failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
