#!/usr/bin/env python3
"""step_audit.py — đo chi phí BƯỚC của một session Claude Code.

Khác `token_audit.py`: file kia đo token (tầng 3 — context cost), file này đo số
bước (tầng 2 — runtime). Một tool call = một vòng round-trip; tổng thời gian của
request tỉ lệ THẲNG với số bước, nên số bước mới là biến chính của tốc độ.

Năm chỉ số in ra:
    1. Số bước           — số `requestId` khác nhau của model (mỗi cái là một API call).
       KHÔNG đếm theo bản ghi jsonl: Claude Code tách một câu trả lời thành nhiều bản
       ghi và chép `usage` vào từng bản, đếm theo bản ghi sẽ thổi phồng số bước.
    2. Tool call mỗi lượt — tổng tool call / số lượt CÓ tool call. Bằng 1,00 nghĩa
       là luật gộp một lượt chưa được thi hành lần nào.
    3. Read lặp          — số lần Read lại file đã đọc trong cùng session.
    4. Độ trễ trung vị   — giây giữa bản ghi trước và lượt model kế tiếp.
    5. Độ trễ p90        — nearest-rank: phần tử thứ ceil(0.9 × n) sau khi sắp xếp.

Dùng:
    python3 scripts/step_audit.py                       # project hiện tại, 3 session mới nhất
    python3 scripts/step_audit.py --sessions 5
    python3 scripts/step_audit.py --project ~/Documents/Heineken_AppKetNoi
    python3 scripts/step_audit.py --transcript-dir <dir>

Env: TDQ_LOG=0 tắt log tiến trình (log ra stderr, bảng ra stdout).
Exit: 0 kể cả khi không tìm thấy session (chỉ cảnh báo). 2 = sai cú pháp.
"""

import argparse
import datetime
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from token_audit import default_transcript_dir, find_sessions, iter_events  # noqa: E402

# Khoảng cách lớn hơn ngưỡng này là user đi làm việc khác rồi quay lại, không phải
# độ trễ của model — bỏ ra khỏi thống kê để trung vị không bị kéo lệch.
MAX_GAP_SECONDS = 300


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _log(message):
    """Log tiến trình ra stderr, có timestamp ISO. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


# ----------------------------------------------------------------- đọc & đo

def _parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _blocks(event):
    message = event.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    return content if isinstance(content, list) else []


def _has_usage(event):
    message = event.get("message")
    return isinstance(message, dict) and isinstance(message.get("usage"), dict)


def _request_id(event, index):
    """Một lượt model = một `requestId`.

    Claude Code TÁCH mỗi khối nội dung của cùng một câu trả lời thành nhiều bản ghi
    jsonl riêng (text một dòng, mỗi tool_use một dòng), và chép lại `usage` vào từng
    dòng. Đếm theo bản ghi thì một lượt phát 3 tool call trông y hệt 3 lượt phát 1 —
    chỉ số "tool call mỗi lượt" luôn ra 1,00 dù model có gộp hay không. Gom theo
    `requestId` mới ra con số thật.
    """
    message = event.get("message")
    rid = event.get("requestId") or (message or {}).get("id")
    return rid or f"_no_request_{index}"


def scan(path):
    """Đọc transcript theo DÒNG (không nạp cả file) và gom số liệu thô."""
    stats = {"steps": 0, "tool_calls": 0, "turns_with_tools": 0,
             "repeat_reads": 0, "latencies": []}
    seen_reads = set()
    turns_with_tools = set()
    prev_time = None
    current_request = None
    for index, event in enumerate(iter_events(path)):
        now = _parse_time(event.get("timestamp"))
        is_step = event.get("type") == "assistant" and _has_usage(event)
        if is_step:
            rid = _request_id(event, index)
            if rid != current_request:            # bản ghi đầu của một lượt mới
                current_request = rid
                stats["steps"] += 1
                if prev_time and now:
                    gap = (now - prev_time).total_seconds()
                    if 0 <= gap <= MAX_GAP_SECONDS:
                        stats["latencies"].append(gap)
            for block in _blocks(event):
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                stats["tool_calls"] += 1
                turns_with_tools.add(rid)
                if block.get("name") == "Read":
                    target = (block.get("input") or {}).get("file_path")
                    if target:
                        if target in seen_reads:
                            stats["repeat_reads"] += 1
                        seen_reads.add(target)
        if now:
            prev_time = now
    stats["turns_with_tools"] = len(turns_with_tools)
    return stats


def merge(all_stats):
    total = {"steps": 0, "tool_calls": 0, "turns_with_tools": 0,
             "repeat_reads": 0, "latencies": []}
    for stats in all_stats:
        for key in ("steps", "tool_calls", "turns_with_tools", "repeat_reads"):
            total[key] += stats[key]
        total["latencies"].extend(stats["latencies"])
    return total


def percentile(values, share):
    """Nearest-rank: phần tử thứ ceil(share × n) của dãy đã sắp xếp (1-indexed)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(share * len(ordered)))
    return float(ordered[min(rank, len(ordered)) - 1])


def median(values):
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2


def report(total):
    """Năm chỉ số, dạng bảng markdown để dán thẳng vào file QC."""
    per_turn = (total["tool_calls"] / total["turns_with_tools"]
                if total["turns_with_tools"] else 0.0)
    lines = [
        "| Chỉ số | Giá trị |",
        "|---|---|",
        f"| Số bước model | {total['steps']} |",
        f"| Tool call trên mỗi lượt | {per_turn:.2f} ({total['turns_with_tools']} lượt) |",
        f"| Read lặp lại cùng file | {total['repeat_reads']} |",
        f"| Độ trễ trung vị | {median(total['latencies']):.1f} s |",
        f"| Độ trễ p90 | {percentile(total['latencies'], 0.9):.1f} s |",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="step_audit.py",
        description="Đo chi phí bước (tầng runtime) của session Claude Code.")
    parser.add_argument("--transcript-dir",
                        help="thư mục chứa file .jsonl; mặc định suy từ project")
    parser.add_argument("--project",
                        help="thư mục project cần đo; mặc định là thư mục hiện tại")
    parser.add_argument("--sessions", type=int, default=3,
                        help="số session mới nhất cần đo (mặc định 3)")
    args = parser.parse_args(argv)

    transcript_dir = args.transcript_dir or default_transcript_dir(args.project)
    paths = find_sessions(transcript_dir, args.sessions)
    if not paths:
        _log(f"không thấy session nào trong {transcript_dir}")
        print("Không có transcript để đo.")
        return 0

    all_stats = []
    for path in paths:
        _log(f"đọc {os.path.basename(path)}")
        all_stats.append(scan(path))
    total = merge(all_stats)
    _log(f"xong {len(paths)} session · {total['steps']} bước")
    print(report(total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
