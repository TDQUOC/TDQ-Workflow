#!/usr/bin/env python3
"""token_audit.py — đo chi phí token thật của một session Claude Code.

Mô hình chi phí: mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context.
Vì vậy một output tool dài `n` ký tự không tốn `n/4` token, mà tốn
`n/4 × số API call còn lại sau nó`. Đại lượng đó gọi là **carry-cost**.

Script đọc transcript jsonl của Claude Code (không sửa gì), gom carry-cost theo
nhóm tool và in bảng để biết chỗ nào đang đốt token.

Dùng:
    python3 scripts/token_audit.py                     # project hiện tại, 3 session mới nhất
    python3 scripts/token_audit.py --sessions 5
    python3 scripts/token_audit.py --transcript-dir <dir>
    python3 scripts/token_audit.py --top 20            # thêm bảng top tool output đắt nhất

Env: TDQ_AUDIT_LOG=0 tắt log tiến trình (log ra stderr, bảng ra stdout).
Exit: 0 kể cả khi không tìm thấy session (chỉ cảnh báo). 2 = sai cú pháp.
"""

import argparse
import bisect
import collections
import datetime
import glob
import json
import os
import sys

CHARS_PER_TOKEN = 4

# Hệ số quy hoá đơn về "input-token tương đương" — lấy từ bảng nhân của trang giá
# chính thức (platform.claude.com/docs/en/about-claude/pricing, đọc 2026-08-05):
# cache hit 0.1x · cache write TTL 5 phút 1.25x · cache write TTL 1 giờ 2x · output 5x.
COST_WEIGHTS = {"cache_read": 0.1, "input": 1.0, "output": 5.0}
CACHE_WRITE_WEIGHT = {"5m": 1.25, "1h": 2.0}
DEFAULT_CACHE_TTL = "1h"        # phiên Claude Code hiện chạy TTL 1 giờ

Row = collections.namedtuple("Row", "group count tokens")
Item = collections.namedtuple("Item", "tokens chars group label")


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_AUDIT_LOG", "1") != "0"


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _log(message):
    """Log tiến trình ra stderr, có timestamp ISO. Tắt bằng TDQ_AUDIT_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


# ----------------------------------------------------------------- đọc transcript

def iter_events(path):
    """Sinh từng bản ghi jsonl. Dòng hỏng/rỗng bị bỏ qua, không làm hỏng cả lượt đọc."""
    try:
        fh = open(path, encoding="utf-8")
    except OSError as exc:
        _log(f"bỏ qua {os.path.basename(str(path))}: {exc}")
        return
    bad = 0
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except (ValueError, TypeError):
                bad += 1
    if bad:
        _log(f"{os.path.basename(str(path))}: bỏ qua {bad} dòng không đọc được")


def default_transcript_dir(project_dir=None):
    """Thư mục transcript của Claude Code cho một project (~/.claude/projects/<slug>)."""
    project = os.path.abspath(project_dir or os.getcwd())
    slug = project.replace(os.sep, "-")
    return os.path.join(os.path.expanduser("~"), ".claude", "projects", slug)


def find_sessions(transcript_dir, limit=3):
    """Trả danh sách file jsonl mới nhất (theo mtime), nhiều nhất `limit` file."""
    files = glob.glob(os.path.join(transcript_dir, "*.jsonl"))
    files.sort(key=os.path.getmtime)
    return files[-limit:] if limit and limit > 0 else files


# ----------------------------------------------------------------- phân nhóm

def classify(tool_name, tool_input):
    """Gom tool call về nhóm dễ đọc — nhóm là đơn vị để quyết định cắt cái gì."""
    if tool_name == "Bash":
        cmd = (tool_input or {}).get("command", "") or ""
        if "tdq_state.py" in cmd:
            return "tdq_state.py (dump JSON)"
        if "unittest" in cmd or "pytest" in cmd:
            return "chạy test suite"
        if "doc_lint" in cmd:
            return "doc_lint"
        if "graphify" in cmd:
            return "graphify"
        return "Bash khác"
    if tool_name == "Read":
        return "Read file"
    if tool_name in ("Edit", "MultiEdit"):
        return "Edit (echo lại diff)"
    if tool_name and "tavily" in tool_name:
        return "tavily search"
    return tool_name or "?"


def _label(tool_name, tool_input):
    """Nhãn ngắn để nhận ra một tool call cụ thể trong bảng top."""
    inp = tool_input or {}
    for key in ("file_path", "command", "query", "description", "pattern"):
        if inp.get(key):
            return f"{tool_name}: {str(inp[key])[:70]}"
    return tool_name or "?"


def _content_text(block):
    content = block.get("content")
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)


# ----------------------------------------------------------------- tính toán

def _message_key(ev, index):
    """Khoá gom các dòng jsonl về đúng một message.

    Claude Code ghi MỘT message (thinking + text + tool_use) thành NHIỀU dòng jsonl
    chung `message.id`, mỗi dòng chép lại nguyên khối `usage`. Cộng theo dòng là đếm
    trùng. Dòng không có `id` (transcript cũ) coi như một message riêng.
    """
    mid = (ev.get("message") or {}).get("id")
    return mid if mid else f"__line_{index}"


def _scan(path):
    """Trả (danh sách Item của file này, thống kê usage)."""
    events = list(iter_events(path))
    names = {}
    for ev in events:
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    names[block.get("id")] = (block.get("name"), block.get("input") or {})

    usage_by_msg = {}       # khoá message -> usage (lấy lần gặp đầu tiên)
    call_idx = []           # chỉ số dòng ĐẦU TIÊN của mỗi API call, tăng dần
    for i, ev in enumerate(events):
        usage = (ev.get("message") or {}).get("usage")
        if not usage:
            continue
        key = _message_key(ev, i)
        if key in usage_by_msg:
            continue
        usage_by_msg[key] = usage
        call_idx.append(i)

    totals = collections.Counter()
    totals["api_calls"] = len(usage_by_msg)
    totals["tool_calls"] = len(names)        # dedup sẵn theo `tool_use.id`
    for field in ("output", "input", "cache_read", "cache_write"):
        totals[field] += 0
    for usage in usage_by_msg.values():
        totals["output"] += usage.get("output_tokens", 0)
        totals["input"] += usage.get("input_tokens", 0)
        totals["cache_read"] += usage.get("cache_read_input_tokens", 0)
        totals["cache_write"] += usage.get("cache_creation_input_tokens", 0)

    items = []
    for i, ev in enumerate(events):
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            name, inp = names.get(block.get("tool_use_id"), (None, {}))
            text = _content_text(block)
            remaining = len(call_idx) - bisect.bisect_left(call_idx, i)
            tokens = len(text) // CHARS_PER_TOKEN * remaining
            items.append(Item(tokens, len(text), classify(name, inp), _label(name, inp)))
    return items, totals


def _all_items(paths):
    items = []
    for path in paths:
        got, _ = _scan(path)
        _log(f"{os.path.basename(str(path))}: {len(got)} tool result")
        items.extend(got)
    return items


def carry_cost(paths):
    """Bảng carry-cost gom theo nhóm, sắp giảm dần. `paths` rỗng → bảng rỗng."""
    agg_tokens = collections.Counter()
    agg_count = collections.Counter()
    for item in _all_items(paths):
        agg_tokens[item.group] += item.tokens
        agg_count[item.group] += 1
    rows = [Row(g, agg_count[g], t) for g, t in agg_tokens.items()]
    rows.sort(key=lambda r: r.tokens, reverse=True)
    return rows


def top_items(paths, limit=15):
    """Những tool output đắt nhất tính theo carry-cost."""
    return sorted(_all_items(paths), key=lambda it: it.tokens, reverse=True)[:limit]


def usage_totals(paths):
    """Cộng dồn usage thật do API trả về: số API call, output, cache read/write."""
    totals = collections.Counter()
    for path in paths:
        _, got = _scan(path)
        totals.update(got)
    return dict(totals)


def cost_equivalent(totals, cache_ttl=DEFAULT_CACHE_TTL):
    """Quy hóa đơn về input-token tương đương.

    `cache_read×0,1 + cache_write×W + input×1 + output×5`, W theo TTL cache
    (1 giờ = 2,0 · 5 phút = 1,25). Trả (tổng, {phần: số token tương đương}).
    """
    weight = dict(COST_WEIGHTS)
    weight["cache_write"] = CACHE_WRITE_WEIGHT.get(cache_ttl, CACHE_WRITE_WEIGHT["1h"])
    parts = {k: totals.get(k, 0) * w for k, w in weight.items()}
    return sum(parts.values()), parts


# ----------------------------------------------------------------- CLI

def _fmt(n):
    return f"{n:,}"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Đo carry-cost token của transcript Claude Code.")
    parser.add_argument("--project", help="thư mục project (mặc định: thư mục hiện tại)")
    parser.add_argument("--transcript-dir", help="chỉ định thẳng thư mục chứa *.jsonl")
    parser.add_argument("--sessions", type=int, default=3,
                        help="số session mới nhất cần đo (mặc định 3, 0 = tất cả)")
    parser.add_argument("--top", type=int, default=0,
                        help="in thêm N tool output đắt nhất (mặc định 0 = không in)")
    parser.add_argument("--cache-ttl", choices=sorted(CACHE_WRITE_WEIGHT),
                        default=DEFAULT_CACHE_TTL,
                        help="TTL cache để quy đổi chi phí (mặc định 1h = hệ số 2,0)")
    args = parser.parse_args(argv)

    tdir = args.transcript_dir or default_transcript_dir(args.project)
    _log(f"đọc transcript từ {tdir}")
    paths = find_sessions(tdir, args.sessions)
    if not paths:
        _log(f"không tìm thấy session nào trong {tdir} — không có gì để đo")
        print("Không có session nào để đo.")
        return 0
    _log(f"đo {len(paths)} session")

    totals = usage_totals(paths)
    rows = carry_cost(paths)
    total_carry = sum(r.tokens for r in rows)

    print(f"# Token audit — {len(paths)} session · {tdir}")
    print()
    print(f"API call: {_fmt(totals.get('api_calls', 0))} · "
          f"tool call: {_fmt(totals.get('tool_calls', 0))} · "
          f"output: {_fmt(totals.get('output', 0))} · "
          f"input: {_fmt(totals.get('input', 0))} · "
          f"cache_read: {_fmt(totals.get('cache_read', 0))} · "
          f"cache_write: {_fmt(totals.get('cache_write', 0))}")
    equiv, parts = cost_equivalent(totals, args.cache_ttl)
    share = " · ".join(f"{k} {parts[k] / equiv * 100:.0f}%"
                       for k in ("cache_read", "cache_write", "input", "output")) if equiv else "—"
    print(f"Chi phí quy đổi (TTL {args.cache_ttl}): {_fmt(round(equiv))} input-token "
          f"tương đương — {share}")
    print()
    print(f"{'nhóm':<28}{'lần':>7}{'carry-cost (token)':>22}")
    print("-" * 57)
    for row in rows:
        print(f"{row.group:<28}{row.count:>7}{_fmt(row.tokens):>22}")
    print("-" * 57)
    print(f"{'TỔNG':<28}{sum(r.count for r in rows):>7}{_fmt(total_carry):>22}")

    if args.top:
        print()
        print(f"# Top {args.top} tool output đắt nhất")
        for item in top_items(paths, args.top):
            print(f"  {_fmt(item.tokens):>12} tok | {_fmt(item.chars):>8} ký tự | "
                  f"{item.group:<26} {item.label[:70]}")

    _log(f"xong — tổng carry-cost {_fmt(total_carry)} token")
    return 0


if __name__ == "__main__":
    sys.exit(main())
