#!/usr/bin/env python3
"""context_surface.py — đo BỀ MẶT của plugin tdq-workflow theo hướng "LLM đọc".

Hai câu hỏi, hai bảng:

1. Mặc định: mỗi file tài liệu nặng bao nhiêu và nằm ở **tầng nạp** nào —
   `luôn nạp` (nằm trong mọi phiên) · `nạp khi gọi skill` · `đọc khi cần`.
   Tầng nạp mới là thứ quyết định chi phí, không phải kích thước file: một file
   1.000 ký tự ở tầng `luôn nạp` đắt hơn file 10.000 ký tự chỉ đọc mỗi tháng một lần.
2. `--hooks`: mỗi hook tốn bao nhiêu mili-giây mỗi lượt, đo nhiều lần lấy trung vị.

Cách dùng:
    python3 scripts/context_surface.py                  # bảng bề mặt
    python3 scripts/context_surface.py --hooks           # bảng tốc độ hook
    python3 scripts/context_surface.py --hooks --runs 9  # đổi số lần đo
    python3 scripts/context_surface.py --quiet           # tắt log tiến trình

Log service: timestamp ISO, in ra **stderr**, bật mặc định, tắt bằng `--quiet`
(hoặc `TDQ_SURFACE_LOG=0`). Bảng luôn ra **stdout** để pipe được.
Exit: 0 chạy xong · 2 sai cú pháp — cùng hợp đồng với `tdq_state.py`.
"""

import argparse
import datetime
import glob
import json
import os
import statistics
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402 — dùng chung để dựng state tạm cho phép đo hook

# Ước tính token: cùng MỘT hệ số cho mọi file để so sánh giữa các file là công bằng.
# 4 byte/token là hệ số `token_audit.py` đang dùng; với tiếng Việt có dấu con số
# thật cao hơn, nên cột token ở đây là ƯỚC TÍNH SÀN, không phải số tokenizer.
BYTES_PER_TOKEN = 4

TIER_ALWAYS = "luôn nạp"
TIER_SKILL = "nạp khi gọi skill"
TIER_LAZY = "đọc khi cần"

FREQ_SESSION = "mọi phiên"
FREQ_ON_SKILL = "mỗi lần gọi skill"
FREQ_ON_REF = "khi thân file trỏ tới"
FREQ_ON_AGENT = "khi chạy agent con"
FREQ_CODE = "0 — mã chạy ngoài context"

HEADERS = ("file", "tầng nạp", "ký tự (wc -c)", "token ước tính", "tần suất vào context")


# ----------------------------------------------------------------- log service

_QUIET = False


def _log_enabled():
    return not _QUIET and os.environ.get("TDQ_SURFACE_LOG", "1") != "0"


def _log(message):
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------------- đọc file

def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _split_frontmatter(raw):
    """Tách phần YAML frontmatter khỏi thân file .md.

    Trả về `(frontmatter_bytes, body_bytes)`. Không có frontmatter → phần đầu rỗng.
    Lý do phải tách: `description` trong frontmatter nằm trong MỌI phiên, còn thân
    file chỉ nạp khi skill được gọi — gộp hai phần lại là nói dối về tần suất.
    """
    if not raw.startswith(b"---"):
        return b"", raw
    end = raw.find(b"\n---", 3)
    if end < 0:
        return b"", raw
    cut = raw.find(b"\n", end + 1)
    if cut < 0:
        return raw, b""
    return raw[:cut + 1], raw[cut + 1:]


def _rel(path):
    return os.path.relpath(path, ROOT)


def _row(name, tier, size, freq):
    return [name, tier, f"{size:,}".replace(",", "."),
            f"{round(size / BYTES_PER_TOKEN):,}".replace(",", "."), freq]


# ---------------------------------------------------------------- quét bề mặt

def scan(root=ROOT):
    """Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng."""
    rows = []

    for skill in sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))):
        head, body = _split_frontmatter(_read(skill))
        rows.append(_row(f"{_rel(skill)} (description)", TIER_ALWAYS,
                         len(head), FREQ_SESSION))
        rows.append(_row(f"{_rel(skill)} (thân)", TIER_SKILL,
                         len(body), FREQ_ON_SKILL))

    for ref in sorted(glob.glob(os.path.join(root, "skills", "*", "references", "*.md"))):
        rows.append(_row(_rel(ref), TIER_LAZY, len(_read(ref)), FREQ_ON_REF))

    for agent in sorted(glob.glob(os.path.join(root, "agents", "*.md"))):
        head, body = _split_frontmatter(_read(agent))
        rows.append(_row(f"{_rel(agent)} (description)", TIER_ALWAYS,
                         len(head), FREQ_SESSION))
        rows.append(_row(_rel(agent), TIER_LAZY, len(body), FREQ_ON_AGENT))

    for hook in sorted(glob.glob(os.path.join(root, "hooks", "scripts", "*.py"))):
        rows.append(_row(_rel(hook), TIER_LAZY, len(_read(hook)), FREQ_CODE))

    for doc in sorted(glob.glob(os.path.join(root, "portable", "**", "*.md"),
                                recursive=True)):
        rows.append(_row(_rel(doc), TIER_LAZY, len(_read(doc)), FREQ_ON_REF))

    mau = os.path.join(root, "docs", "claude-md-mau.md")
    if os.path.exists(mau):
        rows.append(_row(_rel(mau), TIER_ALWAYS, len(_read(mau)),
                         "mọi phiên (chép vào CLAUDE.md)"))

    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    if os.path.exists(manifest):
        rows.append(_row(_rel(manifest), TIER_LAZY, len(_read(manifest)),
                         FREQ_CODE))

    _log(f"quét xong {len(rows)} dòng bề mặt")
    return rows


def _num(cell):
    return int(cell.replace(".", ""))


def totals(rows):
    """Cộng theo tầng nạp — đây mới là con số đáng nhìn."""
    out = {}
    for row in rows:
        out.setdefault(row[1], 0)
        out[row[1]] += _num(row[2])
    return out


# ---------------------------------------------------------------- đo tốc độ hook

FIXTURES = os.path.join(ROOT, "tests", "fixtures")

# Mỗi mục = một TÌNH HUỐNG hook thật, không phải một file script: cùng
# `session_start.py` nhưng `startup` và `compact` chạy hai nhánh khác nhau, và
# `edit_gate.py` rẽ nhánh theo việc file bị sửa là mã nguồn hay tài liệu.
HOOK_CASES = [
    ("session_start.py", "startup",
     {"hook_event_name": "SessionStart", "source": "startup"}),
    ("session_start.py", "compact",
     {"hook_event_name": "SessionStart", "source": "compact"}),
    ("prompt_context.py", "prompt thường", "prompt.json"),
    ("edit_gate.py", "sửa mã nguồn", "edit_src.json"),
    ("edit_gate.py", "sửa tài liệu", "edit_docs_spec.json"),
    ("bash_gate.py", "chạy lệnh", "bash_cmd.json"),
    ("stop_gate.py", "kết thúc turn", "stop.json"),
]


def _payload(spec):
    if isinstance(spec, dict):
        return dict(spec)
    with open(os.path.join(FIXTURES, spec), encoding="utf-8") as f:
        return json.load(f)


def _seed_project(tmp):
    """Dựng project tạm để hook có state thật mà chạy — đo trên repo thật sẽ
    ghi thêm dòng vào sổ turn của chính request đang chạy."""
    state = tdq_state.default_state()
    state.update(active_request="do-toc-do-hook", lane="full", phase="implement")
    os.makedirs(os.path.join(tmp, "docs", "tdq"), exist_ok=True)
    tdq_state.save(tmp, state)
    return tmp


def measure_hooks(runs=5):
    """Chạy mỗi tình huống hook `runs` lần, lấy trung vị mili-giây."""
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        cwd = _seed_project(tmp)
        for script, case, spec in HOOK_CASES:
            payload = _payload(spec)
            payload["cwd"] = cwd
            data = json.dumps(payload)
            path = os.path.join(ROOT, "hooks", "scripts", script)
            times = []
            for _ in range(runs):
                start = datetime.datetime.now()
                subprocess.run([sys.executable, path], input=data, text=True,
                               capture_output=True, timeout=60)
                times.append((datetime.datetime.now() - start).total_seconds() * 1000)
            median = statistics.median(times)
            rows.append([f"hooks/scripts/{script}", case,
                         f"{median:.1f}ms", f"{min(times):.1f}ms", f"{max(times):.1f}ms"])
            _log(f"{script} · {case}: trung vị {median:.1f}ms")
    return rows


# ------------------------------------------------------------------------- in

def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        print("| " + " | ".join(row) + " |")


def main(argv=None):
    global _QUIET
    parser = argparse.ArgumentParser(
        description="Đo bề mặt vào context và tốc độ hook của tdq-workflow.")
    parser.add_argument("--hooks", action="store_true",
                        help="đo thời gian chạy từng hook thay vì quét bề mặt")
    parser.add_argument("--runs", type=int, default=5,
                        help="số lần chạy mỗi hook khi có --hooks (mặc định 5)")
    parser.add_argument("--quiet", action="store_true", help="tắt log tiến trình")
    args = parser.parse_args(argv)
    _QUIET = args.quiet

    if args.hooks:
        _log(f"đo tốc độ hook, {args.runs} lần mỗi tình huống")
        rows = measure_hooks(args.runs)
        print(f"Điều kiện đo: mỗi tình huống chạy {args.runs} lần, "
              f"project tạm rỗng, lấy trung vị.")
        print()
        print_table(("hook", "tình huống", "trung vị", "nhanh nhất", "chậm nhất"), rows)
        return 0

    _log("bắt đầu quét bề mặt")
    rows = scan()
    print_table(HEADERS, rows)
    print()
    for tier, size in sorted(totals(rows).items(), key=lambda kv: -kv[1]):
        print(f"TỔNG `{tier}`: {size:,} ký tự ≈ {round(size / BYTES_PER_TOKEN):,} token"
              .replace(",", "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
