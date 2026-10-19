#!/usr/bin/env python3
"""
Stop-Batching Hook: Runs batch syntax and document lint checks on all modified files
at the Stop event, replacing per-edit latency bottlenecks on Windows 11.
"""

import sys
import subprocess
from pathlib import Path

BUFFER_FILE = Path(".claude/tmp/edited_files.txt")


def run_batch_checks(buffer_path: Path = BUFFER_FILE) -> int:
    """Read the buffer file, deduplicate modified paths, and run static checks."""
    if not buffer_path.exists():
        return 0

    try:
        content = buffer_path.read_text(encoding="utf-8").strip()
        if not content:
            buffer_path.unlink(missing_ok=True)
            return 0

        # Deduplicate paths and filter existing files
        raw_paths = [line.strip() for line in content.splitlines() if line.strip()]
        unique_files = []
        for p in raw_paths:
            resolved = Path(p)
            if resolved.exists() and resolved not in unique_files:
                unique_files.append(resolved)

        if not unique_files:
            buffer_path.unlink(missing_ok=True)
            return 0

        errors = []
        doc_files = [str(f) for f in unique_files if f.suffix == ".md"]
        py_files = [str(f) for f in unique_files if f.suffix == ".py"]

        # 1. Batch document linting
        kw: dict = {"capture_output": True, "text": True, "encoding": "utf-8"}
        if sys.platform == "win32":
            kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        if doc_files and Path("scripts/doc_lint.py").exists():
            res = subprocess.run([sys.executable, "scripts/doc_lint.py"] + doc_files, **kw)  # type: ignore[call-overload]
            if res.returncode != 0:
                errors.append(f"[TDQ Stop-Batch: DocLint Error]\n{res.stdout}\n{res.stderr}")

        # 2. Batch Python syntax compilation check
        if py_files:
            res = subprocess.run([sys.executable, "-m", "py_compile"] + py_files, **kw)  # type: ignore[call-overload]
            if res.returncode != 0:
                errors.append(f"[TDQ Stop-Batch: Python Syntax Error]\n{res.stderr}")

        # Clean buffer only on successful check run
        buffer_path.unlink(missing_ok=True)

        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1

        return 0
    except Exception as exc:
        print(f"[TDQ Stop-Batch Warning] Failed to complete batch checks: {exc}", file=sys.stderr)
        return 0


def main():
    sys.exit(run_batch_checks())


if __name__ == "__main__":
    main()
