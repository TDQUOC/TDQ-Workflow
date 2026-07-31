#!/usr/bin/env python3
"""external_models.py — liệt kê model AVAILABLE THẬT trên máy cho engine ngoài.

Dùng ở bước duyệt plan mode external: Claude chạy script này rồi trình danh sách
cho user chọn 1–3 tên (khó/TB/dễ).

Cách dùng:
  external_models.py list agy    → in từng slug một dòng (từ `agy models`).
  external_models.py list codex  → probe từng slug ứng viên bằng đúng lệnh
      `codex exec -m <slug> --sandbox read-only "reply with exactly: OK"`;
      exit 0 = available, khác = in kèm nhãn `(chưa xác minh)`.
      Kết quả cache 7 ngày tại ~/.claude/cache/tdq-external-models.json.

Ứng viên codex: hằng CODEX_MODEL_CANDIDATES, override bằng env TDQ_CODEX_MODELS
(danh sách phẩy). Env chung: TDQ_EXTERNAL_LOG=0 tắt log.
Exit: 0 (kể cả mọi probe fail — offline vẫn dùng được với nhãn), 1 = agy lỗi,
2 = sai cú pháp.
"""
import datetime
import json
import os
import subprocess
import sys
import time

CODEX_MODEL_CANDIDATES = ("gpt-5.5", "gpt-5.4", "gpt-5.4-mini",
                          "gpt-5-codex", "gpt-5.3-codex")
PROBE_PROMPT = "reply with exactly: OK"
PROBE_TIMEOUT = 120
CACHE_TTL_SECS = 7 * 24 * 3600
USAGE = "usage: external_models.py list <codex|agy>"


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _warn(msg):
    print(f"⚠️ {msg}", file=sys.stderr)


def _project_dir():
    """A17: neo output theo project (TDQ_PROJECT_DIR > git root > cwd) — chạy
    từ thư mục con không được rắc docs/ theo cwd."""
    env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = os.getcwd()
    current = start
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return start
        current = parent


def _log(message):
    if os.environ.get("TDQ_EXTERNAL_LOG", "1") == "0":
        return
    log_dir = os.path.join(_project_dir(), "docs", "tdq", "external")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "models.log"), "a", encoding="utf-8") as f:
            f.write(f"[{_now()}] {message}\n")
    except OSError as exc:
        _warn(f"không ghi được log: {exc}")


def _cache_path():
    return os.path.join(os.path.expanduser("~"), ".claude", "cache",
                        "tdq-external-models.json")


def _candidates():
    raw = os.environ.get("TDQ_CODEX_MODELS", "").strip()
    if raw:
        return [s.strip() for s in raw.split(",") if s.strip()]
    return list(CODEX_MODEL_CANDIDATES)


def _read_cache(candidates):
    try:
        with open(_cache_path(), encoding="utf-8") as f:
            cache = json.load(f)
        if (time.time() - float(cache.get("checked_at_epoch", 0)) < CACHE_TTL_SECS
                and cache.get("candidates") == candidates):
            return cache
    except (OSError, ValueError):
        pass
    return None


def _write_cache(candidates, ok, unverified):
    path = _cache_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"checked_at": _now(), "checked_at_epoch": time.time(),
                       "candidates": candidates, "ok": ok,
                       "unverified": unverified}, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as exc:
        _warn(f"không ghi được cache: {exc}")


def list_agy():
    try:
        proc = subprocess.run(["agy", "models"], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=PROBE_TIMEOUT)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        _warn(f"không chạy được `agy models`: {exc}")
        return 1
    if proc.returncode != 0:
        _warn(f"`agy models` exit {proc.returncode}: {proc.stderr.strip()[:200]}")
        return 1
    slugs = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    for slug in slugs:
        print(slug)
    _log(f"list agy: {len(slugs)} slug")
    return 0


def _probe_codex(slug):
    try:
        proc = subprocess.run(
            ["codex", "exec", "-m", slug, "--sandbox", "read-only", PROBE_PROMPT],
            capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=PROBE_TIMEOUT)
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_codex():
    candidates = _candidates()
    cache = _read_cache(candidates)
    if cache is not None:
        for slug in cache["ok"]:
            print(slug)
        for slug in cache["unverified"]:
            print(f"{slug} (chưa xác minh)")
        print(f"# (cache {cache.get('checked_at', '?')} — xoá "
              f"{_cache_path()} để probe lại)")
        _log(f"list codex: cache hit ({len(cache['ok'])} ok)")
        return 0
    ok, unverified = [], []
    for slug in candidates:
        (ok if _probe_codex(slug) else unverified).append(slug)
    for slug in ok:
        print(slug)
    for slug in unverified:
        print(f"{slug} (chưa xác minh)")
    _write_cache(candidates, ok, unverified)
    _log(f"list codex: probe {len(candidates)} slug — ok={len(ok)} "
         f"unverified={len(unverified)}")
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "list" and argv[1] in ("codex", "agy"):
        return list_agy() if argv[1] == "agy" else list_codex()
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
