#!/usr/bin/env python3
"""Quản tier plugin user-level của Claude Code.

Lệnh:
  status          — in `tên | tier | true/false` cho mọi plugin trong plugin-tiers.json
  reset           — ép false mọi plugin thuộc always_off + on_demand (hook SessionEnd/SessionStart)
  enable <tên>    — bật một plugin thuộc on_demand

Mọi lỗi dữ liệu (JSON hỏng, thiếu file) → 1 dòng ⚠️ stderr + exit 0, không ghi file.
Exit 2 chỉ khi sai cú pháp lệnh. Log: ~/.claude/logs/plugin-tiers.log (PLUGIN_TIERS_LOG=0 tắt).
"""
import json
import os
import sys
import tempfile
from datetime import datetime

MARKETPLACE = "@claude-plugins-official"
USAGE = "usage: plugin_tiers.py status | reset | enable <tên-plugin>"


def _claude_dir():
    return os.path.join(os.path.expanduser("~"), ".claude")


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _log_on():
    return os.environ.get("PLUGIN_TIERS_LOG", "1") != "0"


def _warn(msg):
    if _log_on():
        print(f"[{_now()}] ⚠️ {msg}", file=sys.stderr)


def _log(msg):
    if not _log_on():
        return
    try:
        log_dir = os.path.join(_claude_dir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "plugin-tiers.log"), "a",
                  encoding="utf-8") as f:
            f.write(f"[{_now()}] {msg}\n")
    except OSError as exc:
        print(f"[{_now()}] ⚠️ không ghi được log: {exc}", file=sys.stderr)


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, ValueError) as exc:
        return None, str(exc)


def _tiers():
    path = os.path.join(_claude_dir(), "plugin-tiers.json")
    data, err = _load_json(path)
    if err is not None or not isinstance(data, dict):
        _warn(f"không đọc được {path}: {err or 'không phải object JSON'}")
        return None
    off, ond = data.get("always_off"), data.get("on_demand")
    if not isinstance(off, list) or not isinstance(ond, list):
        _warn(f"{path} thiếu always_off/on_demand dạng list")
        return None
    return [str(x) for x in off], [str(x) for x in ond]


def _settings():
    path = os.path.join(_claude_dir(), "settings.json")
    data, err = _load_json(path)
    if err is not None or not isinstance(data, dict):
        _warn(f"không đọc được {path}: {err or 'không phải object JSON'}")
        return None, path
    return data, path


def _key_for(enabled, name):
    """Khóa enabledPlugins của plugin `name` (khớp sẵn có, mặc định marketplace chính)."""
    for key in enabled:
        if key == name or key.startswith(name + "@"):
            return key
    return name + MARKETPLACE


def _write_settings(data, path):
    """Ghi settings atomic (tmp + rename), backup .bak = bản trước khi ghi."""
    try:
        with open(path, encoding="utf-8") as f:
            original = f.read()
        with open(path + ".bak", "w", encoding="utf-8") as f:
            f.write(original)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".",
                                   prefix=".settings-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
        return True
    except OSError as exc:
        _warn(f"không ghi được {path}: {exc}")
        return False


def cmd_reset():
    tiers = _tiers()
    if tiers is None:
        return 0
    settings, path = _settings()
    if settings is None:
        return 0
    enabled = settings.setdefault("enabledPlugins", {})
    if not isinstance(enabled, dict):
        _warn(f"{path}: enabledPlugins không phải object — bỏ qua")
        return 0
    changes = []
    for name in tiers[0] + tiers[1]:
        key = _key_for(enabled, name)
        old = enabled.get(key, "chưa có key")
        if old is not False:
            enabled[key] = False
            changes.append(f"{key}: {old}→False")
    if not changes:
        _log("reset: 0 thay đổi")
        return 0
    if _write_settings(settings, path):
        _log(f"reset: {len(changes)} thay đổi — " + ", ".join(changes))
    return 0


def cmd_enable(name):
    tiers = _tiers()
    if tiers is None:
        return 0
    always_off, on_demand = tiers
    if name in always_off:
        _warn(f"'{name}' thuộc always_off — không bật qua lệnh này")
        return 0
    if name not in on_demand:
        _warn(f"'{name}' không thuộc on_demand trong plugin-tiers.json")
        return 0
    settings, path = _settings()
    if settings is None:
        return 0
    enabled = settings.setdefault("enabledPlugins", {})
    if not isinstance(enabled, dict):
        _warn(f"{path}: enabledPlugins không phải object — bỏ qua")
        return 0
    key = _key_for(enabled, name)
    old = enabled.get(key, "chưa có key")
    if old is True:
        _log(f"enable {key}: đã bật sẵn, 0 thay đổi")
        return 0
    enabled[key] = True
    if _write_settings(settings, path):
        _log(f"enable {key}: {old}→True")
    return 0


def cmd_status():
    tiers = _tiers()
    if tiers is None:
        return 0
    settings, _ = _settings()
    enabled = settings.get("enabledPlugins", {}) if settings else {}
    if not isinstance(enabled, dict):
        enabled = {}
    for tier_name, names in (("always_off", tiers[0]), ("on_demand", tiers[1])):
        for name in names:
            value = enabled.get(_key_for(enabled, name), "chưa có key")
            print(f"{name} | {tier_name} | {value}")
    return 0


def main(argv):
    if len(argv) == 1 and argv[0] == "status":
        return cmd_status()
    if len(argv) == 1 and argv[0] == "reset":
        return cmd_reset()
    if len(argv) == 2 and argv[0] == "enable":
        return cmd_enable(argv[1])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
