"""Opt-in reuse of static probes; live readiness verdicts are never stored here."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time


_CONTEXT = ContextVar("tdq_readiness", default=None)
SCHEMA_VERSION = 1


def _log(action, seconds):
    if os.environ.get("TDQ_LOG", "1").lower() not in {"0", "false", "off"}:
        print(f"[{datetime.now(timezone.utc).isoformat()}] readiness {action} "
              f"verify_seconds={seconds:.6f}", file=sys.stderr)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    separators=(",", ":")).encode()).hexdigest()


def _file_digest(path):
    try:
        with Path(path).open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()
    except FileNotFoundError:
        return "missing"


def fingerprint(project, inputs, environment=None):
    """Hash contents, canonical paths and environment values without storing secrets."""
    paths = inputs() if callable(inputs) else inputs
    files = [(str(Path(path).resolve()), _file_digest(path)) for path in paths]
    return _digest({"schema": SCHEMA_VERSION, "project": str(Path(project).resolve()),
                    "files": sorted(files), "environment": _digest(environment or {}),
                    "implementation": _file_digest(__file__)})


def _cache_path(project, request, name):
    for part in (request, name):
        if not isinstance(part, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", part):
            raise ValueError("Cache request/name must be a single safe path component")
    root = Path(project).resolve()
    path = root / "docs" / "tdq" / "cache" / request / "readiness" / (name + ".json")
    if not path.resolve().is_relative_to(root):
        raise ValueError("Readiness cache redirects outside the project")
    return path


def _valid_entry(entry, key):
    if not isinstance(entry, dict) or entry.get("schema") != SCHEMA_VERSION:
        return False
    unsigned = {name: value for name, value in entry.items() if name != "digest"}
    return entry.get("key") == key and "value" in entry and entry.get("digest") == _digest(unsigned)


def _load_entry(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None


def _publish(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".readiness-", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(entry, stream, ensure_ascii=True, sort_keys=True)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _verified_entry(path, key, read_key, handoff):
    entry = handoff.get(str(path)) if handoff is not None else None
    entry = entry if _valid_entry(entry, key) else _load_entry(path)
    try:
        return entry if _valid_entry(entry, key) and key == read_key() else None
    except OSError:
        return None


def _save_probe(path, key, read_key, value, handoff, stats):
    started = time.monotonic()
    try:
        stable = key == read_key()
        stats["verify_seconds"] += time.monotonic() - started
        started = time.monotonic()
        if stable:
            entry = {"schema": SCHEMA_VERSION, "key": key, "value": value}
            entry["digest"] = _digest(entry)
            _publish(path, entry)
            if handoff is not None:
                handoff[str(path)] = entry
    except OSError:
        _log("write-miss", 0)
    finally:
        stats["write_seconds"] += time.monotonic() - started


def _execute_probe(probe, stats):
    started = time.monotonic()
    stats["probe_calls"] += 1
    try:
        return probe()
    finally:
        stats["execute_seconds"] += time.monotonic() - started


def _probe_stats(stats):
    stats = {} if stats is None else stats
    for name in ("hits", "misses", "probe_calls", "verify_seconds", "execute_seconds",
                 "write_seconds", "wait_seconds"):
        stats.setdefault(name, 0)
    return stats


def cached_probe(project, request, name, probe, *, inputs, mode="off",
                 environment=None, handoff=None, stats=None):
    """Reuse a declared static JSON result only while its complete input digest matches."""
    if mode not in {"off", "auto"}:
        raise ValueError("readiness cache mode must be off or auto")
    stats = _probe_stats(stats)
    if mode == "off":
        return _execute_probe(probe, stats)
    path = _cache_path(project, request, name)
    started = time.monotonic()
    def read_key():
        return fingerprint(project, inputs, environment)
    try:
        key = read_key()
    except OSError:
        stats["verify_seconds"] += time.monotonic() - started
        stats["misses"] += 1
        _log("unreadable-fresh", stats["verify_seconds"])
        return _execute_probe(probe, stats)
    entry = _verified_entry(path, key, read_key, handoff)
    stats["verify_seconds"] += time.monotonic() - started
    if entry is not None:
        stats["hits"] += 1
        _log("reused-static", time.monotonic() - started)
        return json.loads(json.dumps(entry["value"]))
    verify_seconds = time.monotonic() - started
    stats["misses"] += 1
    value = _execute_probe(probe, stats)
    _save_probe(path, key, read_key, value, handoff, stats)
    _log("executed-static", verify_seconds)
    return value


def request_id(project):
    """Read the current namespace without healing or mutating workflow state."""
    try:
        value = json.loads((Path(project) / "docs/tdq/state.json").read_text(encoding="utf-8"))
        return value.get("active_request") if isinstance(value, dict) else None
    except (OSError, UnicodeError, ValueError):
        return None


@contextmanager
def probe_context(project, *, mode="off", request=None, handoff=None, stats=None):
    """Scope static reuse to one invocation; nested and concurrent callers stay isolated."""
    context = {"project": project, "mode": mode, "request": request or request_id(project),
               "handoff": handoff, "stats": stats}
    token = _CONTEXT.set(context)
    try:
        yield
    finally:
        _CONTEXT.reset(token)


def static_probe(name, probe, inputs, *, environment=None):
    """Use invocation policy; no request or default-off always calls the real probe."""
    context = _CONTEXT.get()
    if not context:
        return probe()
    mode = context["mode"] if context["request"] else "off"
    return cached_probe(context["project"], context["request"], name, probe,
                        inputs=inputs, mode=mode, environment=environment,
                        handoff=context["handoff"], stats=context["stats"])
