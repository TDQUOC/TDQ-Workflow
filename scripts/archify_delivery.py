#!/usr/bin/env python3
"""Archify Delivery Module — handles engine discovery, command execution, and artifact verification.

Contract responsibilities:
- find_archify_root: locate Archify installation; explicit ARCHIFY_ROOT error does not fall back.
- get_archify_bin: resolve entrypoint script archify.mjs.
- check_environment: pre-flight check for Node.js (>= 18) and Archify with clear error explanations.
- build_finalize_command: construct safe CLI invocation arguments.
- atomic_delivery: safe exclusive atomic file delivery with fsync and symlink rejection.
- open_artifact: safely open HTML artifacts in default browser without shell interpolation.
- run_finalize / execute_finalize: execute finalize CLI, parse receipt, verify artifact and gates.

Strictly stdlib-only.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union


@dataclass
class FinalizeResult:
    """Result returned by run_finalize."""

    status: bool
    receipt: dict

    def get(self, key: str, default: Any = None) -> Any:
        if key == "status":
            return self.status
        if key == "receipt":
            return self.receipt
        if isinstance(self.receipt, dict):
            return self.receipt.get(key, default)
        return default


def _log_enabled() -> bool:
    """True unless muted via TDQ_LOG=0."""
    return os.environ.get("TDQ_LOG", "1") != "0"


def _now() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def _log(message: str) -> None:
    if _log_enabled():
        print(f"[{_now()}] archify_delivery: {message}", file=sys.stderr)


def _is_valid_archify_dir(cand: Path) -> bool:
    """Check if candidate directory contains a valid archify package or bin entry."""
    try:
        if not cand.exists() or not cand.is_dir():
            return False
        if (cand / "bin" / "archify.mjs").is_file():
            return True
        if (cand / "archify" / "bin" / "archify.mjs").is_file():
            return True
    except Exception:
        return False
    return False


def _check_env_archify_root() -> tuple[bool, Optional[str]]:
    """Check ARCHIFY_ROOT environment variable. Returns (is_set, path_or_none)."""
    env_root = os.environ.get("ARCHIFY_ROOT")
    if env_root is None or not env_root.strip():
        return False, None
    cand = Path(env_root)
    if _is_valid_archify_dir(cand):
        return True, str(cand)
    _log(f"Warning: ARCHIFY_ROOT is set to '{env_root}' but is not a valid Archify root.")
    return True, None


def _gather_candidate_roots() -> list[Path]:
    """Collect standard candidate root directories when ARCHIFY_ROOT is unset."""
    candidates: list[Path] = []
    try:
        candidates.append(Path.home() / "Documents" / "archify")
    except Exception:
        pass

    try:
        current_file = Path(__file__).resolve()
        repo_root = current_file.parent.parent
        candidates.append(repo_root.parent / "archify")
        for parent in current_file.parents[:3]:
            candidates.append(parent / "archify")
    except Exception:
        pass

    try:
        candidates.append(Path.cwd().parent / "archify")
    except Exception:
        pass
    return candidates


def find_archify_root() -> Optional[str]:
    """Find Archify root directory. Explicit ARCHIFY_ROOT never falls back."""
    env_set, env_path = _check_env_archify_root()
    if env_set:
        return env_path

    seen: set[str] = set()
    for cand in _gather_candidate_roots():
        cand_str = str(cand)
        if cand_str in seen:
            continue
        seen.add(cand_str)
        if _is_valid_archify_dir(cand):
            return cand_str
    return None


def get_archify_bin(archify_root: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """Resolve the archify.mjs executable entry point."""
    root_str = str(archify_root) if archify_root else find_archify_root()
    if not root_str:
        return None

    root = Path(root_str)
    if root.name == "archify.mjs" and root.is_file():
        return root

    direct_bin = root / "bin" / "archify.mjs"
    if direct_bin.is_file():
        return direct_bin

    nested_bin = root / "archify" / "bin" / "archify.mjs"
    if nested_bin.is_file():
        return nested_bin

    return None


def _check_node_environment() -> tuple[bool, str, list[str]]:
    """Validate Node.js presence and version >= 18."""
    node_path = shutil.which("node")
    if not node_path:
        return False, "", ["Node.js executable not found in PATH"]

    try:
        proc = subprocess.run(
            [node_path, "-v"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=10,
        )
        raw_v = proc.stdout.strip()
        match = re.search(r"v?(\d+)", raw_v)
        if match and int(match.group(1)) >= 18:
            return True, raw_v, []
        return False, raw_v, [f"Node.js version {raw_v} is < 18; Node.js >= 18 is required"]
    except Exception as exc:
        return False, "", [f"Failed to check Node.js version: {exc}"]


def _check_archify_environment() -> tuple[Optional[str], bool, list[str]]:
    """Validate Archify root and binary presence."""
    archify_root = find_archify_root()
    archify_bin = get_archify_bin(archify_root) if archify_root else None
    archify_ok = bool(archify_root and archify_bin)
    if archify_ok:
        return archify_root, True, []

    if os.environ.get("ARCHIFY_ROOT"):
        msg = f"ARCHIFY_ROOT is set to '{os.environ.get('ARCHIFY_ROOT')}' but is not a valid Archify root"
    else:
        msg = "Archify root directory not found (set ARCHIFY_ROOT or install to ~/Documents/archify)"
    return archify_root, False, [msg]


def check_environment() -> dict:
    """Pre-flight check for Node.js (>= 18) and Archify installation."""
    node_ok, node_version, node_errors = _check_node_environment()
    archify_root, archify_ok, archify_errors = _check_archify_environment()

    ready = bool(node_ok and archify_ok)
    all_errors = node_errors + archify_errors
    error_msg = "; ".join(all_errors) if not ready else None

    return {
        "node_ok": node_ok,
        "node_version": node_version,
        "archify_root": archify_root or "",
        "ready": ready,
        "error": error_msg,
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
    bin_script = get_archify_bin(archify_root)
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


def _validate_delivery_paths(target_path: Union[str, Path]) -> tuple[Path, Path]:
    """Validate paths and refuse symlinks for target and its parent."""
    raw_path = Path(target_path)
    if raw_path.is_symlink():
        raise ValueError(f"Target path cannot be a symlink: {raw_path}")

    parent = raw_path.parent
    if parent.is_symlink():
        raise ValueError(f"Target parent directory cannot be a symlink: {parent}")
    parent.mkdir(parents=True, exist_ok=True)

    target = raw_path.resolve()
    if raw_path.is_symlink() or target.is_symlink():
        raise ValueError(f"Target path cannot be a symlink: {target}")
    return raw_path, target


def _write_temp_exclusive(temp_path: Path, data: bytes) -> None:
    """Write data to temporary path with exclusive creation and fsync."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(str(temp_path), flags, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def atomic_delivery(target_path: Union[str, Path], content: Union[str, bytes]) -> Path:
    """Write content atomically using an exclusive temporary file, fsync, and replace."""
    raw_path, target = _validate_delivery_paths(target_path)
    data = content.encode("utf-8") if isinstance(content, str) else content

    temp_path = target.parent / f".{target.name}.tmp.{os.getpid()}.{uuid.uuid4().hex}"
    try:
        _write_temp_exclusive(temp_path, data)
        if raw_path.is_symlink() or target.is_symlink():
            raise ValueError(f"Target path became a symlink: {target}")
        os.replace(temp_path, target)
        return target
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def open_artifact(file_path: Union[str, Path]) -> bool:
    """Safely open an existing HTML artifact in the default browser without shell interpolation."""
    path_obj = Path(file_path).resolve()
    if not path_obj.is_file() or path_obj.suffix.lower() not in (".html", ".htm"):
        _log(f"Error: Target artifact is not an existing HTML file: {path_obj}")
        return False

    file_uri = path_obj.as_uri()
    system = platform.system()
    try:
        if system == "Windows":
            if callable(getattr(os, "startfile", None)):
                os.startfile(file_uri)
                return True
            import webbrowser

            return bool(webbrowser.open(file_uri))
        cmd = ["open", file_uri] if system == "Darwin" else ["xdg-open", file_uri]
        proc = subprocess.run(cmd, check=False)
        return proc.returncode == 0
    except Exception as exc:
        _log(f"Failed to open artifact: {exc}")
        return False


def _inspect_candidate(cand: Path) -> tuple[Optional[str], Optional[int], list[dict]]:
    """Verify candidate file and return its initial SHA256 and size."""
    if not cand.is_file():
        return None, None, [{
            "code": "delivery/candidate-not-found",
            "severity": "error",
            "message": f"Candidate file not found: {cand}",
        }]

    try:
        cand_bytes = cand.read_bytes()
        return hashlib.sha256(cand_bytes).hexdigest(), len(cand_bytes), []
    except Exception as exc:
        return None, None, [{
            "code": "delivery/candidate-unreadable",
            "severity": "error",
            "message": f"Could not read candidate file: {exc}",
        }]


def _execute_finalize_process(cmd: list[str], timeout: int) -> tuple[Optional[subprocess.CompletedProcess], list[dict]]:
    """Execute finalize subprocess with environment flags and logging."""
    env = os.environ.copy()
    env["ARCHIFY_UPDATE_CHECK_DISABLED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
            check=False,
        )
        if proc.stderr:
            for line in proc.stderr.splitlines():
                if line.strip():
                    _log(f"[stderr] {line.strip()}")
        return proc, []
    except subprocess.TimeoutExpired as exc:
        _log(f"Finalize command timed out after {timeout}s: {exc}")
        return None, [{
            "code": "delivery/timeout",
            "severity": "error",
            "message": f"Finalize command timed out after {timeout} seconds",
        }]
    except Exception as exc:
        _log(f"Finalize command execution failed: {exc}")
        return None, [{
            "code": "delivery/execution-failed",
            "severity": "error",
            "message": str(exc),
        }]


def _parse_finalize_receipt(stdout: str) -> Optional[dict]:
    """Parse JSON object from stdout."""
    raw = stdout.strip() if stdout else ""
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            try:
                parsed = json.loads(raw[start : end + 1])
                return parsed if isinstance(parsed, dict) else None
            except Exception:
                return None
    return None


def _is_hex64(val: Any) -> bool:
    """True if val is a 64-character lowercase hex string."""
    return isinstance(val, str) and bool(re.match(r"^[0-9a-f]{64}$", val))


def _verify_candidate_unmodified(cand: Path, pre_sha: str, pre_len: int, spec_receipt: Any) -> list[str]:
    """Verify that candidate file did not mutate and receipt specification has matching 64-hex hash."""
    if not cand.is_file():
        return [f"Candidate file disappeared after finalize: {cand}"]

    try:
        after_bytes = cand.read_bytes()
        after_sha = hashlib.sha256(after_bytes).hexdigest()
        if after_sha != pre_sha or len(after_bytes) != pre_len:
            return ["Candidate file was modified during finalize execution"]
    except Exception as exc:
        return [f"Failed to re-read candidate file: {exc}"]

    if not isinstance(spec_receipt, dict):
        return ["Receipt missing 'specification' object"]

    spec_sha = spec_receipt.get("sha256")
    if not _is_hex64(spec_sha):
        return [f"Receipt specification missing valid 64-hex 'sha256' (got '{spec_sha}')"]
    if spec_sha != pre_sha:
        return [f"Receipt specification sha256 '{spec_sha}' does not match candidate '{pre_sha}'"]
    return []


def _match_artifact_path(raw_path: Any, out: Path) -> list[str]:
    """Validate artifact path: must be non-empty string resolving safely to out."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        return ["Receipt artifact missing valid 'path' string"]
    try:
        if Path(raw_path).resolve() != out:
            return [f"Receipt artifact path '{raw_path}' does not match output '{out}'"]
    except Exception:
        return [f"Receipt artifact path '{raw_path}' is invalid"]
    return []


def _match_artifact_hash_and_size(art_receipt: dict, art_sha: str, art_size: int) -> list[str]:
    """Validate artifact sha256 (64-hex) and bytes (non-negative int) matching disk."""
    reasons: list[str] = []
    raw_sha = art_receipt.get("sha256")
    if not _is_hex64(raw_sha):
        reasons.append(f"Receipt artifact missing valid 64-hex 'sha256' string (got '{raw_sha}')")
    elif raw_sha != art_sha:
        reasons.append(f"Artifact hash mismatch: disk '{art_sha}' vs receipt '{raw_sha}'")

    raw_bytes = art_receipt.get("bytes")
    if not isinstance(raw_bytes, int) or isinstance(raw_bytes, bool) or raw_bytes < 0:
        reasons.append(f"Receipt artifact missing valid non-negative integer 'bytes' (got '{raw_bytes}')")
    elif raw_bytes != art_size:
        reasons.append(f"Artifact size mismatch: disk {art_size} vs receipt {raw_bytes}")
    return reasons


def _match_artifact_metadata(art_receipt: dict, out: Path, art_sha: str, art_size: int) -> list[str]:
    """Strictly require path:str, sha256:64hex, bytes:int non-bool >=0 matching output."""
    reasons = _match_artifact_path(art_receipt.get("path"), out)
    reasons.extend(_match_artifact_hash_and_size(art_receipt, art_sha, art_size))
    return reasons


def _verify_artifact_identity(out: Path, art_receipt: Any) -> list[str]:
    """Verify output artifact file existence and match against receipt artifact."""
    if not out.is_file():
        return [f"Output artifact HTML not found on disk: {out}"]

    try:
        art_bytes = out.read_bytes()
        art_sha = hashlib.sha256(art_bytes).hexdigest()
        art_size = len(art_bytes)
    except Exception as exc:
        return [f"Failed to verify output artifact on disk: {exc}"]

    if not isinstance(art_receipt, dict):
        return ["Receipt missing 'artifact' object"]

    return _match_artifact_metadata(art_receipt, out, art_sha, art_size)


def _verify_finalize_gates(gates: Any, diagram_type: str) -> list[str]:
    """Verify validate, deliver, check, and browser-check gates."""
    if not isinstance(gates, dict):
        return ["Receipt is missing 'gates' object"]

    reasons: list[str] = []
    for g in ("validate", "deliver", "check"):
        if gates.get(g) != "pass":
            reasons.append(f"Gate '{g}' status is '{gates.get(g)}', expected 'pass'")

    browser_gate = gates.get("browser-check")
    if diagram_type == "explainer":
        if browser_gate not in ("pass", "not-run"):
            reasons.append(f"Explainer browser-check gate status is '{browser_gate}', expected 'pass' or 'not-run'")
    elif browser_gate != "pass":
        reasons.append(f"Native diagram browser-check gate status is '{browser_gate}', expected 'pass'")
    return reasons


def _evaluate_finalize(
    returncode: int,
    receipt: dict,
    cand: Path,
    pre_sha: str,
    pre_len: int,
    out: Path,
    diagram_type: str,
) -> tuple[bool, list[str]]:
    """Aggregate all verification rules for finalize success."""
    reasons: list[str] = []
    if returncode != 0:
        reasons.append(f"Process exited with non-zero code {returncode}")
    if receipt.get("ok") is not True:
        reasons.append("Receipt 'ok' is not True")
    if receipt.get("status") != "pass":
        reasons.append(f"Receipt status is '{receipt.get('status')}', expected 'pass'")

    reasons.extend(_verify_finalize_gates(receipt.get("gates"), diagram_type))
    reasons.extend(_verify_candidate_unmodified(cand, pre_sha, pre_len, receipt.get("specification")))
    reasons.extend(_verify_artifact_identity(out, receipt.get("artifact")))
    return len(reasons) == 0, reasons


def _record_finalize_failure(receipt: dict, reasons: list[str]) -> None:
    """Append failure diagnostics to receipt and mark status as fail."""
    diags = list(receipt.get("diagnostics") or [])
    for r in reasons:
        diags.append({"code": "delivery/finalize-failed", "severity": "error", "message": r})
    receipt["status"] = "fail"
    receipt["ok"] = False
    receipt["diagnostics"] = diags


def _execute_and_parse(
    cmd: list[str], timeout: int
) -> tuple[Optional[subprocess.CompletedProcess], Optional[dict], list[dict]]:
    """Execute finalize command and parse receipt from stdout."""
    proc, exec_diags = _execute_finalize_process(cmd, timeout)
    if exec_diags or proc is None:
        return None, None, exec_diags
    receipt = _parse_finalize_receipt(proc.stdout)
    if receipt is None:
        return proc, None, [{
            "code": "delivery/malformed-receipt",
            "severity": "error",
            "message": "Finalize stdout did not contain a valid JSON object",
            "raw_output": (proc.stdout or "")[:2000],
        }]
    return proc, receipt, []


def run_finalize(
    diagram_type: str,
    candidate_path: Union[str, Path],
    output_path: Union[str, Path],
    quality: str = "showcase",
    repo_root: Optional[Union[str, Path]] = None,
    archify_root: Optional[Union[str, Path]] = None,
    timeout: int = 120,
) -> FinalizeResult:
    """Execute archify finalize CLI with strict receipt and artifact verification."""
    cand = Path(candidate_path).resolve()
    pre_sha, pre_len, cand_diags = _inspect_candidate(cand)
    if cand_diags:
        return FinalizeResult(status=False, receipt={"ok": False, "status": "fail", "diagnostics": cand_diags})

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
    except Exception as exc:
        return FinalizeResult(status=False, receipt={
            "ok": False, "status": "fail",
            "diagnostics": [{"code": "delivery/command-build-failed", "severity": "error", "message": str(exc)}],
        })

    proc, receipt, run_diags = _execute_and_parse(cmd, timeout)
    if run_diags or proc is None or receipt is None:
        return FinalizeResult(status=False, receipt={"ok": False, "status": "fail", "diagnostics": run_diags})

    status, reasons = _evaluate_finalize(
        returncode=proc.returncode,
        receipt=receipt,
        cand=cand,
        pre_sha=pre_sha or "",
        pre_len=pre_len or 0,
        out=out,
        diagram_type=diagram_type,
    )
    if not status:
        _record_finalize_failure(receipt, reasons)

    return FinalizeResult(status=status, receipt=receipt)


execute_finalize = run_finalize
