#!/usr/bin/env python3
"""TDQ Archify Artifacts Module.

Provides core functions for managing Archify artifacts, manifests, and lifecycle:
- document_digest: hashes document content excluding the binding block
- source_fingerprint: generates map of relative paths to SHA-256 for project sources
- build_manifest: constructs schema_version=1 manifest with portable paths & hashes
- check_manifest: validates freshness and integrity of manifest against current state
- bind_document: embeds or updates manifest binding block into a document
- check_binding: verifies manifest digest and document digest against binding block
- publish_bundle: atomically publishes staging bundle to destination with rollback
- mark_stale: checks master architecture freshness and records status.json

Strictly stdlib-only. No model or delivery imports.
"""

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

BINDING_START = "<!-- tdq-archify-binding:start -->"
BINDING_END = "<!-- tdq-archify-binding:end -->"

EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "__pycache__",
    "graphify-out",
    "logs",
    ".tdq-worktrees",
    ".claude",
}

EXCLUDED_PREFIXES = (
    ("docs", "architecture"),
    ("docs", "tdq"),
    ("docs", "workinglog"),
)

EXCLUDED_FILE_PATTERNS = (
    ".env",
    "id_rsa",
    "id_ed25519",
)

EXCLUDED_FILE_SUFFIXES = (
    ".pem",
    ".key",
    ".candidate.json",
    ".receipt.json",
    "-candidate.json",
    "-receipt.json",
)

SENSITIVE_KEY_SUBSTRINGS = (
    "secret",
    "token",
    "password",
    "api_key",
    "apikey",
    "credential",
    "auth_",
    "authorization",
    "access_token",
)


def _is_within(path: Path, parent: Path) -> bool:
    """Checks whether path resolves within parent directory."""
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


def _is_excluded_dir(parts: Tuple[str, ...]) -> bool:
    """Checks if directory path parts match excluded directory rules."""
    for part in parts:
        if part in EXCLUDED_DIR_NAMES:
            return True
    if len(parts) >= 2 and parts[:2] in EXCLUDED_PREFIXES:
        return True
    return False


def _is_excluded_filename(name: str) -> bool:
    """Checks if filename matches excluded file patterns or extensions."""
    if name in ("candidate.json", "receipt.json"):
        return True
    for suffix in EXCLUDED_FILE_SUFFIXES:
        if name.endswith(suffix):
            return True
    if name.startswith(".env") or name == ".env":
        return True
    if "credential" in name.lower():
        return True
    for pat in EXCLUDED_FILE_PATTERNS:
        if pat in name:
            return True
    return False


def _is_excluded(rel_path: Path) -> bool:
    """Checks if a relative path matches source exclusion rules."""
    if _is_excluded_dir(rel_path.parts):
        return True
    return _is_excluded_filename(rel_path.name)


def _hash_file(file_path: Path) -> str:
    """Computes SHA-256 hex digest of file content in chunks."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _sanitize_secrets(obj: Any) -> Any:
    """Recursively redacts values for sensitive keys in dictionaries."""
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            k_lower = str(k).lower()
            if any(sub in k_lower for sub in SENSITIVE_KEY_SUBSTRINGS):
                clean[k] = "[REDACTED]"
            else:
                clean[k] = _sanitize_secrets(v)
        return clean
    if isinstance(obj, list):
        return [_sanitize_secrets(item) for item in obj]
    return obj


class BundleLock:
    """Exclusive filesystem lock placed beside destination directory.

    Fail-closed: never auto-removes existing locks; times out with owner info
    if lock is held by another process.
    """

    def __init__(self, lock_path: Path, timeout: float = 5.0, poll_interval: float = 0.05):
        self.lock_path = lock_path
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.fd: Optional[int] = None
        self.acquired = False

    def acquire(self) -> "BundleLock":
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(
                    str(self.lock_path),
                    os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                payload = json.dumps({
                    "pid": os.getpid(),
                    "time": time.time(),
                    "host": platform.node(),
                })
                os.write(self.fd, payload.encode("utf-8"))
                os.fsync(self.fd)
                self.acquired = True
                return self
            except FileExistsError:
                if time.time() - start_time >= self.timeout:
                    owner_info = "unknown"
                    try:
                        owner_info = self.lock_path.read_text(encoding="utf-8")
                    except OSError:
                        pass
                    raise TimeoutError(
                        f"Could not acquire lock on {self.lock_path}: lock held by existing process ({owner_info})"
                    )
                time.sleep(self.poll_interval)

    def release(self) -> None:
        if self.acquired:
            if self.fd is not None:
                try:
                    os.close(self.fd)
                except OSError:
                    pass
                self.fd = None
            if self.lock_path.exists():
                try:
                    self.lock_path.unlink()
                except OSError:
                    pass
            self.acquired = False

    def __enter__(self) -> "BundleLock":
        return self.acquire()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.release()


def document_digest(path: Union[str, Path]) -> str:
    """Computes SHA-256 UTF-8 bytes of doc after stripping binding block.

    Rejects multiple blocks or unmatched/inverted markers.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Document file not found: {path}")

    content = file_path.read_text(encoding="utf-8")
    start_count = content.count(BINDING_START)
    end_count = content.count(BINDING_END)

    if start_count > 1 or end_count > 1:
        raise ValueError(
            f"Multiple binding markers found in {path}: start={start_count}, end={end_count}"
        )
    if start_count != end_count:
        raise ValueError(
            f"Unmatched binding markers in {path}: start={start_count}, end={end_count}"
        )

    if start_count == 1:
        start_idx = content.find(BINDING_START)
        end_idx = content.find(BINDING_END)
        if end_idx < start_idx:
            raise ValueError(f"End marker appears before start marker in {path}")
        end_pos = end_idx + len(BINDING_END)
        stripped = content[:start_idx] + content[end_pos:]
    else:
        stripped = content

    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()


def _resolve_explicit_source(
    p: Union[str, Path],
    project_path: Path,
) -> Tuple[Path, str]:
    """Resolves and confines an explicit source path within project_path."""
    raw_p = Path(p)
    if raw_p.is_absolute():
        resolved = raw_p.resolve()
        if not _is_within(resolved, project_path):
            raise ValueError(f"Path outside project root: {p}")
        return resolved, resolved.relative_to(project_path).as_posix()

    full_path = project_path / raw_p
    resolved = full_path.resolve()
    if not _is_within(resolved, project_path):
        raise ValueError(f"Path escapes project root: {p}")
    return full_path, resolved.relative_to(project_path).as_posix()


def _walk_explicit_dir(
    dir_path: Path,
    project_path: Path,
    fingerprints: Dict[str, str],
) -> None:
    """Walks an explicit directory confining all paths relative to project_path."""
    for root, dirs, files in os.walk(dir_path, followlinks=False):
        current_dir = Path(root)
        dirs[:] = _filter_walk_dirs(current_dir, dirs, project_path)
        for f in files:
            entry = _process_walk_file(current_dir / f, project_path)
            if entry:
                fingerprints[entry[0]] = entry[1]


def _fingerprint_explicit_paths(
    project_path: Path,
    paths: Iterable[Union[str, Path]],
) -> Dict[str, str]:
    """Fingerprints an explicit list of source paths with confinement checks."""
    fingerprints: Dict[str, str] = {}
    for p in paths:
        full_path, rel_str = _resolve_explicit_source(p, project_path)

        if full_path.is_symlink() and not _is_within(full_path.resolve(), project_path):
            continue

        if not full_path.exists():
            continue

        if full_path.is_file():
            try:
                fingerprints[rel_str] = _hash_file(full_path)
            except OSError as e:
                raise OSError(f"Unreadable source file {full_path}: {e}") from e
        elif full_path.is_dir():
            _walk_explicit_dir(full_path, project_path, fingerprints)

    return dict(sorted(fingerprints.items()))


def _filter_walk_dirs(
    current_dir: Path,
    dirs: List[str],
    project_path: Path,
) -> List[str]:
    """Filters child directories during walk to prune excluded and symlinked dirs."""
    dirs_to_keep = []
    for d in dirs:
        dir_full = current_dir / d
        if dir_full.is_symlink():
            continue
        try:
            rel_d = dir_full.resolve().relative_to(project_path)
            if not _is_excluded(rel_d):
                dirs_to_keep.append(d)
        except (ValueError, OSError):
            continue
    return dirs_to_keep


def _process_walk_file(
    file_full: Path,
    project_path: Path,
) -> Optional[Tuple[str, str]]:
    """Hashes a single file found during walk if not excluded or leaking symlink."""
    if file_full.is_symlink() and not _is_within(file_full.resolve(), project_path):
        return None

    try:
        rel_f = file_full.relative_to(project_path)
    except ValueError:
        return None

    if _is_excluded(rel_f):
        return None

    if not file_full.is_file():
        return None

    try:
        return rel_f.as_posix(), _hash_file(file_full)
    except OSError as e:
        raise OSError(f"Unreadable source file {file_full}: {e}") from e


def _fingerprint_walk(project_path: Path) -> Dict[str, str]:
    """Walks project directory and hashes all non-excluded source files."""
    fingerprints: Dict[str, str] = {}
    for root, dirs, files in os.walk(project_path, followlinks=False):
        current_dir = Path(root)
        dirs[:] = _filter_walk_dirs(current_dir, dirs, project_path)
        for f in files:
            entry = _process_walk_file(current_dir / f, project_path)
            if entry:
                fingerprints[entry[0]] = entry[1]

    return dict(sorted(fingerprints.items()))


def source_fingerprint(
    project: Union[str, Path],
    paths: Optional[Iterable[Union[str, Path]]] = None,
) -> Dict[str, str]:
    """Generates map of relative POSIX path -> SHA-256 for source files.

    Excludes .git, node_modules, .venv, __pycache__, graphify-out,
    docs/architecture, docs/tdq, logs, docs/workinglog, and output candidates/receipts.
    Confines explicit paths to project root and skips symlinks pointing outside.
    """
    project_path = Path(project).resolve()
    if not project_path.is_dir():
        raise FileNotFoundError(f"Project directory not found: {project}")

    if paths is not None:
        return _fingerprint_explicit_paths(project_path, paths)
    return _fingerprint_walk(project_path)


def _resolve_and_relativize(
    path: Union[str, Path],
    name: str,
    project_path: Path,
) -> Tuple[Path, str]:
    """Validates and resolves a path relative to project_path."""
    if not isinstance(path, (str, Path)) or not str(path).strip():
        raise TypeError(f"{name} path must be a non-empty string or Path, got {type(path).__name__}")
    p = Path(path)
    if p.is_absolute():
        resolved = p.resolve()
        if not _is_within(resolved, project_path):
            raise ValueError(f"{name} path escapes project root: {path}")
        return resolved, resolved.relative_to(project_path).as_posix()

    full = project_path / p
    resolved = full.resolve()
    if not _is_within(resolved, project_path):
        raise ValueError(f"{name} path escapes project root: {path}")
    return resolved, resolved.relative_to(project_path).as_posix()


def build_manifest(
    project: Union[str, Path],
    document: Union[str, Path],
    candidate: Union[str, Path],
    artifact: Union[str, Path],
    receipt: Dict[str, Any],
    *,
    evidence_kind: str = "planned",
    revision: Optional[str] = None,
    coverage: Optional[Dict[str, Any]] = None,
    request: Optional[str] = None,
    lane: Optional[str] = None,
    source_paths: Optional[Iterable[Union[str, Path]]] = None,
    child_files: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Constructs schema_version=1 manifest with portable paths and hashes.

    Sanitizes secrets from receipt and ensures path confinement.
    Materializes source_paths once to avoid consuming generators twice.
    """
    project_path = Path(project).resolve()
    if not project_path.is_dir():
        raise FileNotFoundError(f"Project directory not found: {project}")

    if not isinstance(receipt, dict):
        raise TypeError(f"Receipt must be a dict, got {type(receipt).__name__}")

    source_paths_tuple: Optional[Tuple[Union[str, Path], ...]] = None
    if source_paths is not None:
        source_paths_tuple = tuple(source_paths)

    doc_abs, doc_rel = _resolve_and_relativize(document, "Document", project_path)
    cand_abs, cand_rel = _resolve_and_relativize(candidate, "Candidate", project_path)
    art_abs, art_rel = _resolve_and_relativize(artifact, "Artifact", project_path)

    doc_digest = document_digest(doc_abs)
    cand_digest = _hash_file(cand_abs)
    art_digest = _hash_file(art_abs)

    source_files = source_fingerprint(project_path, paths=source_paths_tuple)
    clean_receipt = _sanitize_secrets(receipt)
    engine = receipt.get("engine") or receipt.get("generator") or "archify"

    source_paths_list = None
    if source_paths_tuple is not None:
        source_paths_list = [Path(p).as_posix() for p in source_paths_tuple]

    manifest = {
        "schema_version": 1,
        "request": request,
        "lane": lane,
        "evidence_kind": evidence_kind,
        "revision": revision,
        "document_path": doc_rel,
        "document_digest": doc_digest,
        "candidate_path": cand_rel,
        "candidate_digest": cand_digest,
        "artifact_path": art_rel,
        "artifact_digest": art_digest,
        "source_paths": source_paths_list,
        "source_files": source_files,
        "coverage": coverage or {},
        "engine": engine,
        "receipt": clean_receipt,
    }
    if child_files is not None:
        manifest["child_files"] = child_files
    return manifest


def _load_manifest_data(
    manifest: Union[str, Path, Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Loads and validates that manifest is a parsed JSON object."""
    if isinstance(manifest, (str, Path)):
        man_path = Path(manifest)
        if not man_path.is_file():
            return None, f"Manifest file not found: {manifest}"
        try:
            raw = json.loads(man_path.read_text(encoding="utf-8"))
        except Exception as e:
            return None, f"Manifest JSON parsing failed: {e}"
    elif isinstance(manifest, dict):
        raw = manifest
    else:
        return None, "Manifest must be a dict or a file path"

    if not isinstance(raw, dict):
        return None, f"Manifest root must be a JSON object, got {type(raw).__name__}"
    return raw, None


def _check_committed_revision(
    project_path: Path,
    manifest_data: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """Checks git revision for committed evidence kind."""
    rev = manifest_data.get("revision")
    if not rev or not isinstance(rev, str) or not re.match(r"^[0-9a-fA-F]{40}$", rev):
        return ["Committed evidence requires a valid 40-hex revision"], []

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10.0,
            check=False,
        )
        if proc.returncode == 0:
            current_rev = proc.stdout.strip()
            if current_rev.lower() != rev.lower():
                return [], [f"Git revision mismatch: manifest committed {rev} != HEAD {current_rev}"]
            return [], []
        return [], [f"Git revision check failed (exit {proc.returncode}): {proc.stderr.strip()}"]
    except subprocess.TimeoutExpired:
        return [], ["Git revision check timed out after 10s"]
    except OSError as e:
        return [], [f"Git execution error: {e}"]


def _extract_path_and_digest(
    data: Dict[str, Any],
    name: str,
) -> Tuple[Any, Any]:
    """Extracts path and digest fields supporting flat and nested format."""
    path_val = data.get(f"{name}_path")
    digest_val = data.get(f"{name}_digest")
    if (path_val is None or digest_val is None) and isinstance(data.get(name), dict):
        sub = data[name]
        path_val = path_val if path_val is not None else sub.get("path")
        digest_val = digest_val if digest_val is not None else sub.get("digest")
    return path_val, digest_val


def _validate_part_format(
    name: str,
    path_val: Any,
    digest_val: Any,
) -> Optional[str]:
    """Validates types and syntax of path and digest."""
    if not isinstance(path_val, str) or not isinstance(digest_val, str):
        return f"{name} path and digest must be strings in manifest"
    if not path_val.strip() or not digest_val.strip():
        return f"{name} path and digest cannot be empty"
    if not re.match(r"^[0-9a-fA-F]{64}$", digest_val):
        return f"{name} digest must be 64-hex SHA-256"
    return None


def _verify_part_hash(
    abs_path: Path,
    name: str,
    digest_val: str,
    is_doc: bool,
) -> Tuple[List[str], List[str]]:
    """Calculates hash of document or artifact and compares to expected digest."""
    if is_doc:
        try:
            current_digest = document_digest(abs_path)
            if current_digest.lower() != digest_val.lower():
                return [], [f"Document digest mismatch: manifest {digest_val} != current {current_digest}"]
            return [], []
        except ValueError as ve:
            return [f"Document binding markers corrupted: {ve}"], []

    try:
        current_digest = _hash_file(abs_path)
        if current_digest.lower() != digest_val.lower():
            return [], [f"{name.capitalize()} digest mismatch: manifest {digest_val} != current {current_digest}"]
        return [], []
    except OSError as e:
        return [f"Error reading {name} file {abs_path}: {e}"], []


def _check_artifact_part(
    project_path: Path,
    name: str,
    path_val: Any,
    digest_val: Any,
    is_doc: bool = False,
) -> Tuple[List[str], List[str]]:
    """Validates existence and digest for document, candidate, or artifact."""
    err = _validate_part_format(name, path_val, digest_val)
    if err:
        return [err], []

    abs_path = (project_path / path_val).resolve()
    if not _is_within(abs_path, project_path):
        return [f"{name} path {path_val} escapes project root"], []

    if not abs_path.is_file():
        return [], [f"{name} file missing: {path_val}"]

    return _verify_part_hash(abs_path, name, digest_val, is_doc)


def _validate_source_paths_param(source_paths: Any) -> Optional[str]:
    """Validates source_paths parameter syntax if present."""
    if source_paths is None:
        return None
    if not isinstance(source_paths, (list, tuple)):
        return "source_paths must be a list/tuple if present in manifest"
    for sp in source_paths:
        if not isinstance(sp, str):
            return "All items in source_paths must be strings"
    return None


def _diff_source_fingerprints(
    source_files: Dict[str, str],
    current_sources: Dict[str, str],
) -> List[str]:
    """Detects additions, deletions, and modifications between fingerprints."""
    stale_reasons: List[str] = []
    for rel_p, exp_hash in source_files.items():
        if rel_p not in current_sources:
            stale_reasons.append(f"Source file deleted: {rel_p}")
        elif current_sources[rel_p].lower() != exp_hash.lower():
            stale_reasons.append(f"Source file modified: {rel_p}")

    for rel_p in current_sources:
        if rel_p not in source_files:
            stale_reasons.append(f"Source file added: {rel_p}")
    return stale_reasons


def _check_source_files(
    project_path: Path,
    manifest_data: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """Validates source files against fingerprint detecting additions/deletions."""
    source_files = manifest_data.get("source_files")
    if not isinstance(source_files, dict):
        return ["Missing or invalid source_files map in manifest"], []

    source_paths = manifest_data.get("source_paths")
    sp_err = _validate_source_paths_param(source_paths)
    if sp_err:
        return [sp_err], []

    try:
        current_sources = source_fingerprint(project_path, paths=source_paths)
    except ValueError as e:
        return [f"Invalid source_paths in manifest: {e}"], []
    except OSError as e:
        return [f"Unreadable source file during fingerprinting: {e}"], []

    stale_reasons = _diff_source_fingerprints(source_files, current_sources)
    return [], stale_reasons


def _validate_manifest_schema_and_kind(manifest_data: Dict[str, Any]) -> List[str]:
    """Validates schema_version and evidence_kind."""
    reasons: List[str] = []
    if manifest_data.get("schema_version") != 1:
        reasons.append(f"Unsupported schema_version: {manifest_data.get('schema_version')}")
    valid_kinds = {"planned", "working-tree", "committed", "partial"}
    if manifest_data.get("evidence_kind", "planned") not in valid_kinds:
        reasons.append(f"Invalid evidence_kind: {manifest_data.get('evidence_kind')}")
    return reasons


def _check_single_child_file(
    artifact_parent: Path,
    rel_child: Any,
    exp_hash: Any,
    project_path: Path,
) -> Tuple[Optional[str], Optional[str]]:
    """Validates one child file path, confinement, and hash."""
    if not isinstance(rel_child, str) or not isinstance(exp_hash, str):
        return "Child file path and hash must be strings", None
    if not re.match(r"^[0-9a-fA-F]{64}$", exp_hash):
        return f"Child file {rel_child} digest must be 64-hex SHA-256", None

    child_abs = (artifact_parent / rel_child).resolve()
    if not _is_within(child_abs, artifact_parent) or not _is_within(child_abs, project_path):
        return f"Child file {rel_child} escapes artifact directory", None
    if not child_abs.is_file():
        return None, f"Child file missing: {rel_child}"

    try:
        curr_hash = _hash_file(child_abs)
        if curr_hash.lower() != exp_hash.lower():
            return None, f"Child file digest mismatch for {rel_child}: manifest {exp_hash} != current {curr_hash}"
    except OSError as e:
        return None, f"Error reading child file {rel_child}: {e}"
    return None, None


def _check_child_files(
    project_path: Path,
    artifact_path_str: Any,
    manifest_data: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """Validates optional child_files hashes relative to artifact parent."""
    child_files = manifest_data.get("child_files")
    if child_files is None:
        return [], []
    if not isinstance(child_files, dict):
        return ["child_files must be a dictionary in manifest"], []
    if not isinstance(artifact_path_str, str):
        return [], []

    artifact_parent = (project_path / artifact_path_str).parent
    invalid_reasons: List[str] = []
    stale_reasons: List[str] = []

    for rel_child, exp_hash in child_files.items():
        inv_err, st_err = _check_single_child_file(artifact_parent, rel_child, exp_hash, project_path)
        if inv_err:
            invalid_reasons.append(inv_err)
        if st_err:
            stale_reasons.append(st_err)

    return invalid_reasons, stale_reasons


def check_manifest(
    project: Union[str, Path],
    manifest: Union[str, Path, Dict[str, Any]],
) -> Dict[str, Any]:
    """Validates freshness and integrity of manifest against current state.

    Returns {'status': 'current'|'stale'|'invalid', 'reasons': [...]}.
    Missing files are flagged as stale (never current).
    """
    project_path = Path(project).resolve()
    if not project_path.is_dir():
        return {
            "status": "invalid",
            "reasons": [f"Project directory not found: {project}"],
        }

    manifest_data, err = _load_manifest_data(manifest)
    if err or manifest_data is None:
        return {"status": "invalid", "reasons": [err or "Failed to load manifest"]}

    invalid_reasons: List[str] = _validate_manifest_schema_and_kind(manifest_data)
    stale_reasons: List[str] = []

    if manifest_data.get("evidence_kind", "planned") == "committed":
        inv_rev, st_rev = _check_committed_revision(project_path, manifest_data)
        invalid_reasons.extend(inv_rev)
        stale_reasons.extend(st_rev)

    for name, is_doc in (("document", True), ("candidate", False), ("artifact", False)):
        p_val, d_val = _extract_path_and_digest(manifest_data, name)
        inv_p, st_p = _check_artifact_part(project_path, name, p_val, d_val, is_doc=is_doc)
        invalid_reasons.extend(inv_p)
        stale_reasons.extend(st_p)

    art_p_val, _ = _extract_path_and_digest(manifest_data, "artifact")
    inv_child, st_child = _check_child_files(project_path, art_p_val, manifest_data)
    invalid_reasons.extend(inv_child)
    stale_reasons.extend(st_child)

    inv_src, st_src = _check_source_files(project_path, manifest_data)
    invalid_reasons.extend(inv_src)
    stale_reasons.extend(st_src)

    if invalid_reasons:
        return {"status": "invalid", "reasons": invalid_reasons + stale_reasons}
    if stale_reasons:
        return {"status": "stale", "reasons": stale_reasons}
    return {"status": "current", "reasons": []}


def bind_document(
    document: Union[str, Path],
    manifest_path: Union[str, Path],
) -> None:
    """Inserts or replaces the binding block in document without self-cycle.

    Digest of document remains invariant after binding.
    """
    doc_path = Path(document).resolve()
    man_path = Path(manifest_path).resolve()

    if not doc_path.is_file():
        raise FileNotFoundError(f"Document not found: {document}")
    if not man_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    manifest_digest = _hash_file(man_path)

    try:
        rel_manifest = man_path.relative_to(doc_path.parent).as_posix()
    except (ValueError, OSError):
        rel_manifest = man_path.as_posix()

    content = doc_path.read_text(encoding="utf-8")
    start_count = content.count(BINDING_START)
    end_count = content.count(BINDING_END)

    if start_count > 1 or end_count > 1 or start_count != end_count:
        raise ValueError(
            f"Document has multiple or unmatched binding markers: start={start_count}, end={end_count}"
        )

    binding_block = (
        f"{BINDING_START}\n"
        f"<!-- manifest: {rel_manifest} -->\n"
        f"<!-- manifest_digest: {manifest_digest} -->\n"
        f"{BINDING_END}"
    )

    if start_count == 1:
        start_idx = content.find(BINDING_START)
        end_idx = content.find(BINDING_END) + len(BINDING_END)
        new_content = content[:start_idx] + binding_block + content[end_idx:]
    else:
        new_content = content + binding_block

    temp_doc = doc_path.parent / f".{doc_path.name}.tmp.{uuid.uuid4().hex}"
    temp_doc.write_text(new_content, encoding="utf-8")
    os.replace(temp_doc, doc_path)


def _parse_binding_digest(content: str) -> Tuple[Optional[str], Optional[str]]:
    """Extracts manifest digest from binding block in document content."""
    if BINDING_START not in content:
        return None, "Document has no binding block"

    start_idx = content.find(BINDING_START)
    end_idx = content.find(BINDING_END)
    if end_idx == -1 or end_idx < start_idx:
        return None, "Unmatched binding marker in document"

    binding_body = content[start_idx + len(BINDING_START): end_idx]
    digest_match = re.search(r"(?:manifest_digest|digest):\s*([a-fA-F0-9]{64})", binding_body)
    if not digest_match:
        return None, "Binding block missing valid 64-hex manifest digest"
    return digest_match.group(1).lower(), None


def _check_doc_path_matches_manifest(
    doc_path: Path,
    man_path: Path,
    expected_path_str: Any,
) -> bool:
    """Verifies that doc_path corresponds to expected document_path in manifest."""
    if not isinstance(expected_path_str, str) or not expected_path_str.strip():
        return False
    exp_p = Path(expected_path_str)
    if (man_path.parent / exp_p).resolve() == doc_path.resolve():
        return True
    for p in (man_path.parent, *man_path.parents):
        if (p / exp_p).resolve() == doc_path.resolve():
            return True
    return doc_path.name == exp_p.name


def _get_manifest_doc_field(man_data: Dict[str, Any], field: str) -> Any:
    """Extracts document path or digest supporting flat and nested formats."""
    val = man_data.get(f"document_{field}")
    if val is None and isinstance(man_data.get("document"), dict):
        val = man_data["document"].get(field)
    return val


def _check_binding_against_manifest(
    man_path: Path,
    doc_path: Path,
    actual_doc_digest: str,
) -> Tuple[List[str], Optional[str]]:
    """Verifies that manifest recorded document_digest and path match actual document."""
    try:
        man_data = json.loads(man_path.read_text(encoding="utf-8"))
        if not isinstance(man_data, dict):
            return [], "Manifest JSON root must be an object"

        expected_doc_path = _get_manifest_doc_field(man_data, "path")
        if not expected_doc_path or not _check_doc_path_matches_manifest(doc_path, man_path, expected_doc_path):
            return [f"Document path mismatch: bound document {doc_path.name} does not match manifest document_path {expected_doc_path}"], None

        expected_doc = _get_manifest_doc_field(man_data, "digest")
        if not isinstance(expected_doc, str) or not re.match(r"^[0-9a-fA-F]{64}$", expected_doc):
            return [], "Manifest missing valid 64-hex document_digest"
        if expected_doc.lower() != actual_doc_digest.lower():
            return [f"Document digest mismatch: manifest recorded {expected_doc} != actual {actual_doc_digest}"], None
        return [], None
    except Exception as e:
        return [], f"Manifest JSON reading error: {e}"


def check_binding(
    document: Union[str, Path],
    manifest_path: Union[str, Path],
) -> Dict[str, Any]:
    """Verifies manifest digest and document digest against document binding block."""
    doc_path = Path(document).resolve()
    man_path = Path(manifest_path).resolve()

    if not doc_path.is_file():
        return {"status": "invalid", "valid": False, "reasons": [f"Document not found: {document}"]}
    if not man_path.is_file():
        return {"status": "invalid", "valid": False, "reasons": [f"Manifest not found: {manifest_path}"]}

    actual_manifest_digest = _hash_file(man_path)
    try:
        actual_doc_digest = document_digest(doc_path)
    except ValueError as e:
        return {"status": "invalid", "valid": False, "reasons": [f"Document binding markers corrupted: {e}"]}

    bound_digest, err = _parse_binding_digest(doc_path.read_text(encoding="utf-8"))
    if err:
        st = "stale" if "no binding" in err.lower() else "invalid"
        return {"status": st, "valid": False, "reasons": [err],
                "document_digest": actual_doc_digest, "manifest_digest": actual_manifest_digest}

    reasons: List[str] = []
    if bound_digest != actual_manifest_digest.lower():
        reasons.append(f"Manifest digest mismatch: bound {bound_digest} != actual {actual_manifest_digest}")

    doc_mismatch, json_err = _check_binding_against_manifest(man_path, doc_path, actual_doc_digest)
    if json_err:
        return {"status": "invalid", "valid": False, "reasons": [json_err]}
    reasons.extend(doc_mismatch)

    if reasons:
        return {"status": "stale", "valid": False, "reasons": reasons,
                "document_digest": actual_doc_digest, "manifest_digest": actual_manifest_digest}
    return {"status": "current", "valid": True, "reasons": [],
            "document_digest": actual_doc_digest, "manifest_digest": actual_manifest_digest}


def _validate_staging_nesting(staging_path: Path, dest_path: Path) -> None:
    """Verifies staging and destination are not identical or nested."""
    if not staging_path.is_dir():
        raise ValueError(f"Staging directory not found or not a directory: {staging_path}")
    if staging_path == dest_path:
        raise ValueError("Staging and destination cannot be the same directory")
    if _is_within(staging_path, dest_path):
        raise ValueError("Staging directory cannot be nested inside destination")
    if _is_within(dest_path, staging_path):
        raise ValueError("Destination directory cannot be nested inside staging")


def _validate_staging_no_symlinks(staging_path: Path) -> None:
    """Ensures no symlinks exist anywhere in staging bundle."""
    for root, dirs, files in os.walk(staging_path, followlinks=False):
        for d in dirs:
            if (Path(root) / d).is_symlink():
                raise ValueError(f"Symlinks not allowed in staging bundle: {Path(root) / d}")
        for f in files:
            if (Path(root) / f).is_symlink():
                raise ValueError(f"Symlinks not allowed in staging bundle: {Path(root) / f}")


def _validate_staging_hash(staging_path: Path) -> None:
    """Validates staging manifest and artifact hash fail-closed."""
    staging_index = staging_path / "index.html"
    staging_manifest = staging_path / "manifest.json"

    if not staging_index.is_file() or not staging_manifest.is_file():
        raise ValueError("Staging bundle missing required index.html or manifest.json")

    try:
        manifest_data = json.loads(staging_manifest.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Invalid manifest.json in staging bundle: {e}") from e

    if not isinstance(manifest_data, dict):
        raise ValueError(f"Staging manifest.json must be a JSON object, got {type(manifest_data).__name__}")

    expected_art_digest = manifest_data.get("artifact_digest")
    if not expected_art_digest and isinstance(manifest_data.get("artifact"), dict):
        expected_art_digest = manifest_data["artifact"].get("digest")

    if not isinstance(expected_art_digest, str) or not re.match(r"^[0-9a-fA-F]{64}$", expected_art_digest):
        raise ValueError("Staging manifest.json missing required valid 64-hex artifact_digest")

    actual_art_digest = _hash_file(staging_index)
    if actual_art_digest.lower() != expected_art_digest.lower():
        raise ValueError(
            f"Staging artifact hash mismatch: expected {expected_art_digest}, got {actual_art_digest}"
        )


def _validate_staging_bundle(
    staging_path: Path,
    dest_path: Path,
) -> None:
    """Validates staging bundle requirements, symlinks, and hashes before swap."""
    _validate_staging_nesting(staging_path, dest_path)
    _validate_staging_no_symlinks(staging_path)
    _validate_staging_hash(staging_path)


def _atomic_swap_directory(
    staging_path: Path,
    dest_path: Path,
) -> None:
    """Performs atomic directory swap with backup and rollback."""
    temp_dest = dest_path.parent / f".{dest_path.name}.tmp.{uuid.uuid4().hex}"
    backup_dest = dest_path.parent / f".{dest_path.name}.bak.{uuid.uuid4().hex}"

    shutil.copytree(staging_path, temp_dest, symlinks=False)

    if dest_path.exists():
        try:
            os.replace(dest_path, backup_dest)
        except Exception as e:
            shutil.rmtree(temp_dest, ignore_errors=True)
            raise RuntimeError(f"Failed to move existing destination to backup: {e}") from e

        try:
            os.replace(temp_dest, dest_path)
            shutil.rmtree(backup_dest, ignore_errors=True)
        except Exception as swap_err:
            if backup_dest.exists():
                try:
                    os.replace(backup_dest, dest_path)
                except Exception as rollback_err:
                    if temp_dest.exists():
                        shutil.rmtree(temp_dest, ignore_errors=True)
                    raise RuntimeError(
                        f"Publication failed and rollback to destination failed ({rollback_err}). "
                        f"Backup preserved at: {backup_dest}"
                    ) from swap_err
            if temp_dest.exists():
                shutil.rmtree(temp_dest, ignore_errors=True)
            raise RuntimeError(
                f"Publication failed, rolled back to last good: {swap_err}"
            ) from swap_err
    else:
        try:
            os.replace(temp_dest, dest_path)
        except Exception as e:
            if temp_dest.exists():
                shutil.rmtree(temp_dest, ignore_errors=True)
            raise RuntimeError(f"Publication failed: {e}") from e


def publish_bundle(
    staging: Union[str, Path],
    destination: Union[str, Path],
    timeout: float = 5.0,
) -> Path:
    """Atomically publishes staging bundle to destination with exclusive lock.

    Requires index.html and manifest.json in staging.
    Validates hashes before publication (fail-closed) and preserves last good version.
    Rejects symlinks and nested paths.
    Returns destination / 'index.html'.
    """
    staging_path = Path(staging).resolve()
    dest_path = Path(destination).resolve()

    _validate_staging_bundle(staging_path, dest_path)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = dest_path.parent / f".{dest_path.name}.lock"

    with BundleLock(lock_path, timeout=timeout):
        _atomic_swap_directory(staging_path, dest_path)

    return dest_path / "index.html"


def mark_stale(project: Union[str, Path]) -> Dict[str, Any]:
    """Reads docs/architecture/manifest.json if present, checks freshness, writes status.json.

    Absent manifest returns skip; errors return invalid.
    Does NOT modify manifest.json.
    """
    project_path = Path(project).resolve()
    manifest_path = project_path / "docs" / "architecture" / "manifest.json"
    status_path = project_path / "docs" / "architecture" / "status.json"

    if not manifest_path.is_file():
        return {
            "status": "skip",
            "reason": "Manifest absent",
        }

    try:
        check_res = check_manifest(project_path, manifest_path)
        status_data = {
            "schema_version": 1,
            "status": check_res["status"],
            "reasons": check_res.get("reasons", []),
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        status_data = {
            "schema_version": 1,
            "status": "invalid",
            "reasons": [f"Error checking manifest: {e}"],
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    status_path.parent.mkdir(parents=True, exist_ok=True)
    temp_status = status_path.parent / f".status.json.tmp.{uuid.uuid4().hex}"
    temp_status.write_text(json.dumps(status_data, indent=2), encoding="utf-8")
    os.replace(temp_status, status_path)

    return status_data
