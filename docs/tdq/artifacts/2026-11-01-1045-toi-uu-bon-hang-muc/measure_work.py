"""Run selected tests with an audit/profile observer in every Python descendant."""
import os
from pathlib import Path
import subprocess
import sys
import uuid


def main():
    folder = Path(__file__).resolve().parent
    probe = folder / "work-probe"
    log = folder / ("work-observations-" + uuid.uuid4().hex + ".jsonl")
    log.write_text("", encoding="utf-8")
    environment = {**os.environ, "TDQ_SCOPE_WORK_LOG": str(log),
                   "PYTHONPATH": str(probe) + os.pathsep + os.environ.get("PYTHONPATH", "")}
    command = [sys.executable, "-m", "pytest", "-q", "-s", "-p", "work_probe", *sys.argv[1:]]
    return subprocess.run(command, env=environment, timeout=600).returncode


if __name__ == "__main__":
    raise SystemExit(main())
