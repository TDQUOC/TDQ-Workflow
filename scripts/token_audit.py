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

Đếm token bằng tokenizer thật (`anthropic-tokenizer` trong venv `.venv-tokens/`,
dùng chung bộ đếm với `skill_tokens.py`). Thiếu thư viện thì script LỖI, tuyệt đối
không rơi về ước lượng ký tự/4: bảng này dùng để quyết định cắt cái gì, mà ước lượng
ký tự/4 lệch mạnh đúng ở nhóm tốn nhất — chuỗi lặp và base64 nén rất tốt, tiếng Việt
có dấu thì ngược lại.

Env: TDQ_AUDIT_LOG=0 tắt log tiến trình (log ra stderr, bảng ra stdout).
Exit: 0 kể cả khi không tìm thấy session (chỉ cảnh báo). 2 = sai cú pháp.
     3 = thiếu thư viện đếm token.
"""

import argparse
import bisect
import collections
import datetime
import base64
import glob
import hashlib
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import skill_tokens  # noqa: E402 — dùng chung MỘT bộ đếm token với bảng skill

EXIT_THIEU_THU_VIEN = skill_tokens.EXIT_THIEU_THU_VIEN

# Hệ số quy hoá đơn về "input-token tương đương" — lấy từ bảng nhân của trang giá
# chính thức (platform.claude.com/docs/en/about-claude/pricing, đọc 2026-08-05):
# cache hit 0.1x · cache write TTL 5 phút 1.25x · cache write TTL 1 giờ 2x · output 5x.
COST_WEIGHTS = {"cache_read": 0.1, "input": 1.0, "output": 5.0}
CACHE_WRITE_WEIGHT = {"5m": 1.25, "1h": 2.0}
DEFAULT_CACHE_TTL = "1h"        # phiên Claude Code hiện chạy TTL 1 giờ

Row = collections.namedtuple("Row", "group count tokens")
Item = collections.namedtuple("Item", "tokens chars group label size")
Phan = collections.namedtuple("Phan", "group count trung_vi p90 p99 lon_nhat tong")
HanhViRead = collections.namedtuple("HanhViRead", "tong co_pham_vi doc_lai")


# ----------------------------------------------------------------- đếm token

# Cache theo nội dung: transcript lặp lại rất nhiều đoạn giống hệt (cùng file đọc lại,
# cùng lệnh chạy lại). Khoá bằng digest chứ không bằng chính chuỗi để dict không giữ
# thêm một bản sao của toàn bộ transcript trong bộ nhớ.
_CACHE = {}
_BO_DEM = None
_DA_THU_TRONG_TIEN_TRINH = False


def _khoa(text):
    return hashlib.blake2b(text.encode("utf-8"), digest_size=16).digest()


def dem_nhieu(doan):
    """Đếm token cho một lô đoạn, trả list cùng thứ tự. Ném `ThieuThuVienDem` nếu
    không đếm thật được — cấm đoán."""
    global _BO_DEM, _DA_THU_TRONG_TIEN_TRINH
    khoa = [_khoa(t) if t else None for t in doan]
    can = {}
    for k, t in zip(khoa, doan):
        if k is not None and k not in _CACHE:
            can[k] = t
    if can:
        if not _DA_THU_TRONG_TIEN_TRINH:
            try:
                _BO_DEM = skill_tokens.nap_bo_dem()
            except skill_tokens.ThieuThuVienDem:
                _BO_DEM = None
            _DA_THU_TRONG_TIEN_TRINH = True
        if _BO_DEM is not None:
            so = [_BO_DEM(t) for t in can.values()]
        else:
            _log(f"đếm {len(can)} đoạn qua python của .venv-tokens")
            so = skill_tokens.dem_qua_venv(list(can.values()))
        _CACHE.update(zip(can, so))
    return [_CACHE[k] if k is not None else 0 for k in khoa]


def dem_token(text):
    """Số token thật của một đoạn."""
    return dem_nhieu([text])[0]


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
    project = os.path.abspath(os.path.expanduser(project_dir or os.getcwd()))
    # Claude Code đổi CẢ dấu phân cách thư mục LẪN gạch dưới thành `-` khi dựng tên
    # thư mục transcript. Thiếu vế `_` thì project có gạch dưới (Heineken_AppKetNoi)
    # luôn ra đường dẫn không tồn tại — đo nhầm thành "không có session nào".
    slug = project.replace(os.sep, "-").replace("_", "-")
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


# Ảnh tính theo patch chứ không theo độ dài chuỗi base64: mỗi patch 28×28 px là một
# token thị giác, ảnh tốn ⌈w/28⌉ × ⌈h/28⌉ token (tài liệu Vision của Claude,
# platform.claude.com/docs/build-with-claude/vision, đọc 2026-08-19). Không đọc được
# kích thước thì lấy 1.600 — mức tài liệu ghi cho ảnh cỡ tối đa không phải thu nhỏ.
PATCH_PX = 28
TOKEN_ANH_KHONG_RO = 1600


def _kich_thuoc_png(raw):
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", raw[16:24])


def _kich_thuoc_jpeg(raw):
    if raw[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(raw):
        if raw[i] != 0xFF:
            i += 1
            continue
        marker = raw[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        do_dai = int.from_bytes(raw[i + 2:i + 4], "big")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            cao, rong = struct.unpack(">HH", raw[i + 5:i + 9])
            return rong, cao
        i += 2 + do_dai
    return None


def dem_anh(media_type, data_base64):
    """Token của một khối ảnh. Đọc kích thước thật từ header, không giải nén cả ảnh."""
    try:
        raw = base64.b64decode(data_base64[:512], validate=False)
    except Exception:
        return TOKEN_ANH_KHONG_RO
    kich_thuoc = _kich_thuoc_png(raw)
    if kich_thuoc is None and "jpeg" in (media_type or ""):
        kich_thuoc = _kich_thuoc_jpeg(base64.b64decode(data_base64, validate=False))
    if not kich_thuoc or not all(kich_thuoc):
        return TOKEN_ANH_KHONG_RO
    rong, cao = kich_thuoc
    return -(-rong // PATCH_PX) * -(-cao // PATCH_PX)


def _content_text(block):
    """Phần CHỮ của tool_result, đã bỏ payload ảnh ra ngoài (xem `_tach_anh`)."""
    return _tach_anh(block)[0]


def _tach_anh(block):
    """Tách tool_result thành (phần chữ, tổng token ảnh).

    Payload base64 của ảnh bị thay bằng nhãn ngắn trước khi đếm: giữ nó lại thì một
    ảnh chụp màn hình đội lên hàng trăm nghìn token trong khi model chỉ tốn vài nghìn.
    """
    content = block.get("content")
    if isinstance(content, str):
        return content, 0
    if not isinstance(content, list):
        return json.dumps(content, ensure_ascii=False), 0
    anh = 0
    sach = []
    for khoi in content:
        if isinstance(khoi, dict) and khoi.get("type") == "image":
            src = khoi.get("source") or {}
            anh += dem_anh(src.get("media_type"), src.get("data") or "")
            sach.append({"type": "image", "media_type": src.get("media_type")})
        else:
            sach.append(khoi)
    return json.dumps(sach, ensure_ascii=False), anh


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

    tho = []
    for i, ev in enumerate(events):
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            name, inp = names.get(block.get("tool_use_id"), (None, {}))
            text, anh = _tach_anh(block)
            remaining = len(call_idx) - bisect.bisect_left(call_idx, i)
            tho.append((text, anh, remaining, classify(name, inp), _label(name, inp)))
    # Đếm cả file trong MỘT lô: chi phí nằm ở lần dựng tiến trình python của venv.
    so = dem_nhieu([t[0] for t in tho])
    items = [Item((n + anh) * con_lai, len(text), group, label, n + anh)
             for (text, anh, con_lai, group, label), n in zip(tho, so)]
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


def _phan_vi(day_sap_xep, q):
    """Phân vị theo hạng gần nhất (nearest-rank): vị trí `ceil(q×n)`, đếm từ 1.

    Chọn kiểu này chứ không nội suy vì mọi giá trị in ra phải là một output CÓ THẬT
    trong transcript — số nội suy không ứng với lần gọi nào thì không truy ngược được.
    """
    if not day_sap_xep:
        return 0
    n = len(day_sap_xep)
    hang = max(1, min(n, -(-int(round(q * n * 1000)) // 1000)))
    return day_sap_xep[hang - 1]


def phan_ra(paths):
    """Phân rã kích thước output theo nhóm tool: n, trung vị, p90, p99, lớn nhất.

    Khác `carry_cost`: ở đây là token THẬT của từng output, chưa nhân số call còn
    lại. Tổng carry-cost cao có hai nguyên nhân rất khác nhau — gọi nhiều lần mỗi
    lần nhỏ (phải sửa hành vi) hay vài lần khổng lồ (phải đặt trần output) — và chỉ
    bảng này phân biệt được.
    """
    theo_nhom = collections.defaultdict(list)
    for item in _all_items(paths):
        theo_nhom[item.group].append(item.size)
    rows = []
    for group, sizes in theo_nhom.items():
        sizes.sort()
        rows.append(Phan(group, len(sizes), _phan_vi(sizes, 0.5), _phan_vi(sizes, 0.9),
                         _phan_vi(sizes, 0.99), sizes[-1], sum(sizes)))
    return sorted(rows, key=lambda r: r.tong, reverse=True)


def hanh_vi_read(paths):
    """Đo hành vi `Read`: bao nhiêu lần, bao nhiêu lần có `offset`/`limit`, bao nhiêu
    lần đọc lại file đã đọc trong CÙNG session.

    Bảng này chỉ ĐO, không phán: luật TDQ bắt đọc lại ở nhiều ca (`cấm làm theo trí
    nhớ`), nên số đọc lại cao KHÔNG đồng nghĩa với lãng phí.
    """
    tong = co_pham_vi = doc_lai = 0
    for path in paths:
        da_doc = set()
        for ev in iter_events(path):
            content = (ev.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if (not isinstance(block, dict) or block.get("type") != "tool_use"
                        or block.get("name") != "Read"):
                    continue
                inp = block.get("input") or {}
                tong += 1
                if inp.get("offset") is not None or inp.get("limit") is not None:
                    co_pham_vi += 1
                duong_dan = inp.get("file_path")
                if duong_dan in da_doc:
                    doc_lai += 1
                else:
                    da_doc.add(duong_dan)
    return HanhViRead(tong, co_pham_vi, doc_lai)


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

    try:
        totals = usage_totals(paths)
        rows = carry_cost(paths)
    except skill_tokens.ThieuThuVienDem as exc:
        print("token_audit.py: thiếu thư viện đếm token `anthropic-tokenizer`.\n"
              "Script này CẤM ước lượng ký tự/4, nên dừng ở đây.\n"
              f"Cài bằng: {exc}", file=sys.stderr)
        return EXIT_THIEU_THU_VIEN
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

    print()
    print("# Phân rã kích thước output (token thật của từng lần gọi)")
    print(f"{'nhóm':<28}{'lần':>7}{'trung vị':>10}{'p90':>10}{'p99':>10}{'lớn nhất':>11}")
    print("-" * 76)
    for pr in phan_ra(paths):
        print(f"{pr.group:<28}{pr.count:>7}{_fmt(pr.trung_vi):>10}{_fmt(pr.p90):>10}"
              f"{_fmt(pr.p99):>10}{_fmt(pr.lon_nhat):>11}")
    hv = hanh_vi_read(paths)
    if hv.tong:
        print()
        print(f"Read: {_fmt(hv.tong)} lần · có offset/limit {hv.co_pham_vi} "
              f"({hv.co_pham_vi / hv.tong * 100:.1f}%) · đọc lại file đã đọc "
              f"{hv.doc_lai} ({hv.doc_lai / hv.tong * 100:.1f}%)")
        print("  (đọc lại là hành vi ĐÚNG ở 5 ca luật bắt buộc — bảng chỉ đo, không phán)")

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
