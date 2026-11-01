"""Request-local cache for normalized transcript traces, never raw messages.

Every lookup reads and hashes all source bytes. Files changing while read or
parsed are not cached. Cache failures fall back to parsing the current snapshot.
TDQ_LOG=0 disables timestamped metadata-only diagnostics.
"""
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import uuid


SCHEMA_VERSION = 1
DEFAULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_AGE = 7 * 24 * 3600


def _log(action):
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] transcript-cache: {action}", file=sys.stderr)


def _read_bytes(path):
    with open(path, "rb") as stream:
        return stream.read()


def _identity(path):
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True).encode("utf-8")).hexdigest()


def _request_directory(project, request_id, mode):
    if mode != "auto" or not request_id or request_id in (".", ".."):
        return None
    if not isinstance(request_id, str) or not re.fullmatch(r"[\w.-]+", request_id):
        return None
    return Path(project).resolve() / "docs/tdq/cache" / request_id / "transcripts"


class TranscriptCache:
    """Hash snapshots and cache parser output within one project/request."""

    def __init__(self, project, request_id, *, mode="off", stats=None,
                 max_bytes=DEFAULT_MAX_BYTES, max_age_seconds=DEFAULT_MAX_AGE):
        if mode not in ("off", "auto"):
            raise ValueError("cache must be off or auto")
        if not all(math.isfinite(value) and value >= 0 for value in (max_bytes, max_age_seconds)):
            raise ValueError("cache retention limits must be nonnegative")
        self.max_bytes, self.max_age = max_bytes, max_age_seconds
        self.stats = stats if stats is not None else {}
        self.stats.update(hits=0, misses=0, bytes_hashed=0, unstable=0,
                          unreadable=0, verify_seconds=0.0, parse_seconds=0.0,
                          write_seconds=0.0, wall_seconds=0.0)
        self.directory = _request_directory(project, request_id, mode)
        self.started = time.perf_counter()
        self.stats["mode"] = "auto" if self.directory else "off"
        if mode == "auto" and self.directory is None:
            _log("disabled: missing-or-invalid-request")

    def _entry(self, path, content_sha, parser_version, host):
        key = {"path": os.path.normcase(str(path.resolve())), "content_sha": content_sha,
               "parser": parser_version, "host": host, "schema": SCHEMA_VERSION}
        return key, self.directory / (_digest(key) + ".json") if self.directory else None

    def _load(self, entry, key, validate):
        if entry is None or not self._local_entry(entry):
            return None
        try:
            stat = entry.stat()
            if stat.st_size > self.max_bytes or time.time() - stat.st_mtime > self.max_age:
                return None
            envelope = json.loads(entry.read_text(encoding="utf-8"))
            trace = envelope["trace"]
            if envelope["key"] == key and envelope["digest"] == _digest(trace) and validate(trace):
                return trace
        except (OSError, ValueError, KeyError, TypeError, RecursionError):
            _log("miss: cache-unavailable-or-invalid")
        return None

    def _local_entry(self, entry):
        try:
            return entry.parent.resolve() == self.directory and not entry.is_symlink()
        except OSError:
            return False

    def _write(self, entry, key, trace):
        if entry is None or not self._local_entry(entry):
            return
        started = time.perf_counter()
        # Keep atomic replacement local without repeating the 64-byte cache key.
        temporary = entry.parent / (".tc-" + uuid.uuid4().hex + ".tmp")
        try:
            encoded = json.dumps({"key": key, "trace": trace, "digest": _digest(trace)},
                                 ensure_ascii=True, separators=(",", ":")).encode("utf-8")
            if len(encoded) > self.max_bytes:
                return
            entry.parent.mkdir(parents=True, exist_ok=True)
            if not self._local_entry(entry):
                _log("miss: cache-path-redirected")
                return
            with temporary.open("xb") as stream:
                stream.write(encoded)
            temporary.replace(entry)
        except OSError:
            _log("write-unavailable")
        finally:
            self._remove_temporary(temporary)
            self.stats["write_seconds"] += time.perf_counter() - started

    def _remove_temporary(self, temporary):
        try:
            if self._local_entry(temporary):
                temporary.unlink(missing_ok=True)
        except OSError:
            _log("temporary-cleanup-unavailable")

    def read(self, path, *, host, parser_version, parse, validate):
        """Return (normalized trace, issue); unreadable bytes never hit cache."""
        path = Path(path)
        started = time.perf_counter()
        try:
            before = _identity(path)
            content = _read_bytes(path)
            after = _identity(path)
        except OSError:
            self.stats["unreadable"] += 1
            self.stats["verify_seconds"] += time.perf_counter() - started
            return [], "unreadable_files"
        self.stats["bytes_hashed"] += len(content)
        key, entry = self._entry(path, hashlib.sha256(content).hexdigest(), parser_version, host)
        stable = before == after
        trace = self._load(entry, key, validate) if stable else None
        self.stats["verify_seconds"] += time.perf_counter() - started
        if trace is not None:
            if not self._unchanged(path, after):
                self.stats["unstable"] += 1
                return trace, "unstable_source"
            self.stats["hits"] += 1
            _log("hit: content-verified")
            return trace, None
        return self._parse_current(path, content, after, stable, entry, key, parse)

    @staticmethod
    def _unchanged(path, identity):
        try:
            return _identity(path) == identity
        except OSError:
            return False

    def _parse_current(self, path, content, identity, stable, entry, key, parse):
        self.stats["misses"] += 1
        started = time.perf_counter()
        trace = parse(content)
        self.stats["parse_seconds"] += time.perf_counter() - started
        stable = stable and self._unchanged(path, identity)
        if not stable:
            self.stats["unstable"] += 1
            _log("miss: unstable-source")
            return trace, "unstable_source"
        self._write(entry, key, trace)
        _log("miss: parsed-current-snapshot")
        return trace, None

    def finish(self):
        """Apply request-local age/size retention once, without changing evidence."""
        if self.directory is not None:
            self._prune()
        self.stats["wall_seconds"] = time.perf_counter() - self.started

    def _prune(self):
        try:
            if self.directory.resolve() != self.directory:
                return
            entries = [(path.stat().st_mtime, path.stat().st_size, path)
                       for path in self.directory.glob("*.json") if not path.is_symlink()]
            total = sum(size for _, size, _ in entries)
            for modified, size, path in sorted(entries):
                if time.time() - modified > self.max_age or total > self.max_bytes:
                    path.unlink(missing_ok=True)
                    total -= size
        except OSError:
            _log("retention-unavailable")
