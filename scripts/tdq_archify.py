#!/usr/bin/env python3
"""TDQ Archify Adapter Module.

Provides core functions for integrating Archify engine into TDQ-Workflow:
- find_archify_root: locates the local Archify installation
- check_environment: pre-flight validation of Node.js (>= 18) and Archify
- build_finalize_command: prepares arguments for archify finalize CLI
- run_finalize / execute_finalize: compiles candidate JSON to standalone HTML
- atomic_delivery: safe atomic file writes
- open_artifact: opens generated diagrams in default browser

Strictly stdlib-only.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional, Union


class FinalizeResult(NamedTuple):
    """Result returned by run_finalize."""

    status: bool
    receipt: dict

    def get(self, key, default=None):
        if key == "status":
            return self.status
        if key == "receipt":
            return self.receipt
        return self.receipt.get(key, default)

    def __getitem__(self, item):
        if item == 0:
            return self.status
        if item == 1:
            return self.receipt
        if item == "status":
            return self.status
        if item == "receipt":
            return self.receipt
        return self.receipt[item]


def find_archify_root() -> Optional[str]:
    """Find Archify root directory.

    Search priority:
    1. ARCHIFY_ROOT environment variable
    2. C:\\Users\\admin\\Documents\\archify (or ~/Documents/archify)
    3. Sibling directory ../archify relative to repo root / worktrees
    4. Searches for archify/bin/archify.mjs or bin/archify.mjs
    """
    candidates = []

    env_root = os.environ.get("ARCHIFY_ROOT")
    if env_root:
        candidates.append(Path(env_root))

    # Windows user path & home
    candidates.append(Path(r"C:\Users\admin\Documents\archify"))
    try:
        candidates.append(Path.home() / "Documents" / "archify")
    except Exception:
        pass

    # Sibling relative to this file
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent
    candidates.append(repo_root.parent / "archify")
    # Worktree nested check
    if len(current_file.parents) >= 3:
        candidates.append(current_file.parents[2] / "archify")
    if len(current_file.parents) >= 4:
        candidates.append(current_file.parents[3] / "archify")
    if len(current_file.parents) >= 5:
        candidates.append(current_file.parents[4] / "archify")

    # Current working dir sibling
    try:
        candidates.append(Path.cwd().parent / "archify")
    except Exception:
        pass

    seen = set()
    for cand in candidates:
        try:
            resolved = cand.resolve()
        except Exception:
            resolved = cand

        resolved_str = str(resolved)
        if resolved_str in seen:
            continue
        seen.add(resolved_str)

        if not cand.exists() or not cand.is_dir():
            continue

        # Check for archify/bin/archify.mjs or bin/archify.mjs
        if (cand / "archify" / "bin" / "archify.mjs").is_file():
            return str(cand)
        if (cand / "bin" / "archify.mjs").is_file():
            return str(cand)

    return None


def get_archify_bin(archify_root: Optional[str] = None) -> Optional[Path]:
    """Resolve the archify.mjs executable entry point."""
    root_str = archify_root or find_archify_root()
    if not root_str:
        return None

    root = Path(root_str)
    # Check directly under bin/
    direct_bin = root / "bin" / "archify.mjs"
    if direct_bin.is_file():
        return direct_bin

    # Check under archify/bin/
    nested_bin = root / "archify" / "bin" / "archify.mjs"
    if nested_bin.is_file():
        return nested_bin

    # If root itself points to archify.mjs
    if root.name == "archify.mjs" and root.is_file():
        return root

    return None


def check_environment() -> dict:
    """Pre-flight check for Node.js (>= 18) and Archify installation."""
    node_path = shutil.which("node")
    node_ok = False
    node_version = ""

    if node_path:
        try:
            proc = subprocess.run(
                [node_path, "-v"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            raw_v = proc.stdout.strip()
            node_version = raw_v
            # Extract major version number (e.g. v24.19.0 -> 24)
            match = re.search(r"v?(\d+)", raw_v)
            if match:
                major = int(match.group(1))
                node_ok = major >= 18
        except Exception:
            node_ok = False

    archify_root = find_archify_root()
    archify_bin = get_archify_bin(archify_root) if archify_root else None
    archify_ok = bool(archify_root and archify_bin)

    ready = bool(node_ok and archify_ok)

    return {
        "node_ok": node_ok,
        "node_version": node_version,
        "archify_root": archify_root or "",
        "ready": ready,
    }


def build_finalize_command(
    diagram_type: str,
    candidate_path: Union[str, Path],
    output_path: Union[str, Path],
    quality: str = "showcase",
    repo_root: Optional[Union[str, Path]] = None,
    archify_root: Optional[Union[str, Path]] = None,
) -> list[str]:
    """Build the CLI command arguments to execute archify finalize."""
    node_bin = shutil.which("node") or "node"
    bin_script = get_archify_bin(str(archify_root) if archify_root else None)
    if not bin_script:
        raise FileNotFoundError("Archify binary script (archify.mjs) not found")

    cmd = [
        node_bin,
        str(bin_script),
        "finalize",
        diagram_type,
        str(candidate_path),
        str(output_path),
        "--quality",
        quality,
        "--json",
    ]
    if repo_root:
        cmd.extend(["--repo-root", str(repo_root)])
    return cmd


def atomic_delivery(target_path: Union[str, Path], content: Union[str, bytes]) -> Path:
    """Write content atomically using a temporary file and rename."""
    target = Path(target_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(f"{target.suffix}.tmp.{os.getpid()}")
    try:
        if isinstance(content, str):
            temp_path.write_text(content, encoding="utf-8")
        else:
            temp_path.write_bytes(content)
        temp_path.replace(target)
        return target
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise


def run_finalize(
    diagram_type: str,
    candidate_path: Union[str, Path],
    output_path: Union[str, Path],
    quality: str = "showcase",
    repo_root: Optional[Union[str, Path]] = None,
    archify_root: Optional[Union[str, Path]] = None,
) -> FinalizeResult:
    """Run archify finalize and return status and receipt JSON."""
    cand = Path(candidate_path).resolve()
    if not cand.is_file():
        return FinalizeResult(
            status=False,
            receipt={"ok": False, "error": f"Candidate file not found: {cand}"},
        )

    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        cmd = build_finalize_command(
            diagram_type=diagram_type,
            candidate_path=cand,
            output_path=out,
            quality=quality,
            repo_root=repo_root,
            archify_root=archify_root,
        )
    except Exception as e:
        return FinalizeResult(
            status=False,
            receipt={"ok": False, "error": str(e)},
        )

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    receipt = {}
    if proc.stdout:
        raw = proc.stdout.strip()
        try:
            receipt = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    receipt = json.loads(raw[start : end + 1])
                except Exception:
                    receipt = {"raw_output": raw}
            else:
                receipt = {"raw_output": raw}

    # Evaluate execution status:
    # Exit 0 or receipt.ok == True is success.
    # If out exists and deliver gate passed, the HTML artifact is successfully delivered.
    delivered = out.is_file() and receipt.get("gates", {}).get("deliver") == "pass"
    if proc.returncode == 0 or receipt.get("ok") is True:
        status = True
    elif delivered:
        status = True
    else:
        status = False

    return FinalizeResult(status=status, receipt=receipt)


execute_finalize = run_finalize


def open_artifact(file_path: Union[str, Path]) -> bool:
    """Safely open an artifact in the default browser."""
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        sys.stderr.write(f"Error: File not found: {path_obj}\n")
        return False

    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    f'Start-Process "{path_obj}"',
                ],
                check=False,
            )
            return True
        elif system == "Darwin":
            subprocess.run(["open", str(path_obj)], check=False)
            return True
        else:
            subprocess.run(["xdg-open", str(path_obj)], check=False)
            return True
    except Exception as e:
        sys.stderr.write(f"Failed to open artifact: {e}\n")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TDQ Archify Adapter CLI — orchestrate diagram generation and environment pre-flight."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # check
    subparsers.add_parser("check", help="Check Node.js and Archify environment")

    # render
    render_parser = subparsers.add_parser(
        "render", help="Render diagram to standalone HTML via finalize"
    )
    render_parser.add_argument(
        "--type",
        required=True,
        help="Diagram type (workflow, architecture, sequence, ...)",
    )
    render_parser.add_argument(
        "--candidate", required=True, help="Path to input candidate JSON"
    )
    render_parser.add_argument(
        "--out", required=True, help="Path to output HTML artifact"
    )
    render_parser.add_argument(
        "--quality",
        default="showcase",
        choices=["standard", "showcase"],
        help="Rendering quality",
    )
    render_parser.add_argument(
        "--repo-root", default=None, help="Root path of target repository"
    )

    # open
    open_parser = subparsers.add_parser(
        "open", help="Open artifact safely in default browser"
    )
    open_parser.add_argument("file_path", help="Path to file to open")

    args = parser.parse_args()

    if args.command == "check":
        res = check_environment()
        print(json.dumps(res, indent=2))
        return 0 if res.get("ready") else 1

    elif args.command == "render":
        result = run_finalize(
            diagram_type=args.type,
            candidate_path=args.candidate,
            output_path=args.out,
            quality=args.quality,
            repo_root=args.repo_root,
        )
        print(json.dumps(result.receipt, indent=2))
        return 0 if result.status else 1

    elif args.command == "open":
        ok = open_artifact(args.file_path)
        return 0 if ok else 1

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
