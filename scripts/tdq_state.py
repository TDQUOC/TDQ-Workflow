#!/usr/bin/env python3
"""State helper for the TDQ workflow plugin (stdlib only).

State lives at <project>/docs/tdq/state.json. All mutations must go through
this module. Approval fields are PROTECTED: the CLI refuses to set them; only
the approve gate hook (which imports this module directly) may change them,
and it only does so when the user typed the approve command themselves.
"""
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

STATE_REL = os.path.join("docs", "tdq", "state.json")

PROTECTED_KEYS = {
    "spec_approved", "spec_sha256", "spec_approved_at",
    "plan_approved", "plan_sha256", "plan_approved_at",
    "quick_approved", "quick_approved_at",
}
VALID_LANES = {"quick", "full", None}
VALID_PHASES = {"idle", "analyze", "spec", "plan", "implement", "qc", "report"}


def default_state():
    return {
        "schema_version": 1,
        "active_request": None,
        "lane": None,
        "phase": "idle",
        "spec_file": None,
        "spec_approved": False,
        "spec_sha256": None,
        "spec_approved_at": None,
        "plan_file": None,
        "plan_approved": False,
        "plan_sha256": None,
        "plan_approved_at": None,
        "quick_approved": False,
        "quick_approved_at": None,
        "implement_mode": None,
        "updated_at": None,
    }


def state_path(cwd):
    return os.path.join(cwd, STATE_REL)


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load(cwd):
    """Return the state dict, or None if missing/corrupt."""
    try:
        with open(state_path(cwd), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    base = default_state()
    base.update({k: v for k, v in data.items() if k in base})
    return base


def save(cwd, state):
    """Atomic write (temp file + rename). Returns the saved state."""
    state["updated_at"] = now_iso()
    path = state_path(cwd)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".state-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
    return state


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_value(raw):
    lowered = raw.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return raw


def _fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def cli(argv):
    cwd = os.environ.get("TDQ_PROJECT_DIR") or os.getcwd()
    if not argv:
        _fail("Cách dùng: tdq_state.py get [key] | init <slug> [lane] | set k=v ... | reset")
    cmd = argv[0]

    if cmd == "get":
        state = load(cwd) or default_state()
        if len(argv) > 1:
            print(json.dumps(state.get(argv[1]), ensure_ascii=False))
        else:
            print(json.dumps(state, ensure_ascii=False, indent=2))
        return

    if cmd == "init":
        if len(argv) < 2:
            _fail("Cách dùng: tdq_state.py init <slug> [quick|full]")
        state = default_state()
        state["active_request"] = argv[1]
        if len(argv) > 2:
            if argv[2] not in ("quick", "full"):
                _fail("Lane không hợp lệ (quick|full).")
            state["lane"] = argv[2]
        save(cwd, state)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return

    if cmd == "set":
        state = load(cwd)
        if state is None:
            _fail("Chưa có state — chạy init trước.")
        for pair in argv[1:]:
            if "=" not in pair:
                _fail(f"Tham số không hợp lệ: {pair} (cần dạng key=value)")
            key, raw = pair.split("=", 1)
            if key in PROTECTED_KEYS:
                _fail(
                    f"Từ chối: '{key}' là field duyệt được bảo vệ — chỉ user gõ "
                    "/tdq-workflow:tdq-approve mới set được (qua approve gate hook)."
                )
            if key not in default_state():
                _fail(f"Key không tồn tại trong schema: {key}")
            value = _parse_value(raw)
            if key == "lane" and value not in VALID_LANES:
                _fail("Lane không hợp lệ (quick|full|null).")
            if key == "phase" and value not in VALID_PHASES:
                _fail("Phase không hợp lệ (idle|analyze|spec|plan|implement|qc|report).")
            state[key] = value
        save(cwd, state)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return

    if cmd == "reset":
        save(cwd, default_state())
        print("OK")
        return

    _fail(f"Lệnh không hợp lệ: {cmd}")


if __name__ == "__main__":
    cli(sys.argv[1:])
