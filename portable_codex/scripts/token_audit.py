#!/usr/bin/env python3
"""token_audit.py — measure the real token cost of one Claude Code session.

Cost model: every tool call = 1 API call = the model re-reads the WHOLE context.
So a tool output `n` characters long does not cost `n/4` tokens, it costs
`n/4 × the number of API calls left after it`. That quantity is the **carry-cost**.

The script reads the jsonl transcript of Claude Code (changing nothing), sums carry-cost
per tool group and prints a table showing where the tokens burn.

Usage:
        python3 scripts/token_audit.py                     # current project, 3 newest sessions
    python3 scripts/token_audit.py --sessions 5
    python3 scripts/token_audit.py --transcript-dir <dir>
        python3 scripts/token_audit.py --top 20            # plus a table of the priciest tool outputs

Tokens are counted with a real tokenizer (`anthropic-tokenizer` in the `.venv-tokens/` venv,
the same counter `skill_tokens.py` uses). Missing library → the script ERRORS, it NEVER
falls back to characters/4: this table decides what gets cut, and the characters/4 estimate
is most wrong exactly in the priciest group — repeated strings and base64 compress very well,
accented text does the opposite.

Env: TDQ_AUDIT_LOG=0 turns the progress log off (log to stderr, table to stdout).
Exit: 0 even when no session is found (a warning only). 2 = bad syntax.
          3 = the token-counting library is missing.
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
import skill_tokens  # noqa: E402 — share ONE token counter with the skill table

EXIT_THIEU_THU_VIEN = skill_tokens.EXIT_THIEU_THU_VIEN

# Normalisation factors to "equivalent input tokens" — taken from the multiplier table of the
# official pricing page (platform.claude.com/docs/en/about-claude/pricing, read 2026-08-05):
# cache hit 0.1x · cache write TTL 5 min 1.25x · cache write TTL 1 hour 2x · output 5x.
COST_WEIGHTS = {"cache_read": 0.1, "input": 1.0, "output": 5.0}
CACHE_WRITE_WEIGHT = {"5m": 1.25, "1h": 2.0}
DEFAULT_CACHE_TTL = "1h"        # Claude Code sessions currently run on a 1-hour TTL

Row = collections.namedtuple("Row", "group count tokens")
Item = collections.namedtuple("Item", "tokens chars group label size")
Phan = collections.namedtuple("Phan", "group count trung_vi p90 p99 lon_nhat tong")
HanhViRead = collections.namedtuple("HanhViRead", "tong co_pham_vi doc_lai")


# ----------------------------------------------------------------- token counting

# Cache by content: a transcript repeats a great many identical chunks (the same file read
# again, the same command re-run). Keyed by digest rather than by the string itself so the
# dict does not hold a second copy of the whole transcript in memory.
_CACHE = {}
_BO_DEM = None
_DA_THU_TRONG_TIEN_TRINH = False


def _khoa(text):
    return hashlib.blake2b(text.encode("utf-8"), digest_size=16).digest()


def dem_nhieu(doan):
    """Count tokens for a batch of chunks, returning a list in the same order. Raises
    `ThieuThuVienDem` when a real count is impossible — guessing is banned."""
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
            _log(f"counted {len(can)} chunk(s) through the python of .venv-tokens")
            so = skill_tokens.dem_qua_venv(list(can.values()))
        _CACHE.update(zip(can, so))
    return [_CACHE[k] if k is not None else 0 for k in khoa]


def dem_token(text):
    """The real token count of one chunk."""
    return dem_nhieu([text])[0]


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_AUDIT_LOG", "1") != "0"


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _log(message):
    """Log progress to stderr with an ISO timestamp. Turn it off with TDQ_AUDIT_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


# ----------------------------------------------------------------- reading the transcript

def iter_events(path):
    """Yield the jsonl records one by one. A broken/empty line is skipped without spoiling the read."""
    try:
        fh = open(path, encoding="utf-8")
    except OSError as exc:
        _log(f"skipping {os.path.basename(str(path))}: {exc}")
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
        _log(f"{os.path.basename(str(path))}: skipped {bad} unreadable line(s)")


def default_transcript_dir(project_dir=None):
    """The Claude Code transcript folder for a project (~/.claude/projects/<slug>)."""
    project = os.path.abspath(os.path.expanduser(project_dir or os.getcwd()))
    # Claude Code turns BOTH the folder separator AND the underscore into `-` when it builds
    # the transcript folder name. Without the `_` half, a project with an underscore
    # (Heineken_AppKetNoi) always yields a path that does not exist — read as "no session at all".
    slug = project.replace(os.sep, "-").replace("_", "-")
    return os.path.join(os.path.expanduser("~"), ".claude", "projects", slug)


def find_sessions(transcript_dir, limit=3):
    """The list of newest jsonl files (by mtime), at most `limit` of them."""
    files = glob.glob(os.path.join(transcript_dir, "*.jsonl"))
    files.sort(key=os.path.getmtime)
    return files[-limit:] if limit and limit > 0 else files


# ----------------------------------------------------------------- grouping

def classify(tool_name, tool_input):
    """Group tool calls into readable buckets — the bucket is the unit for deciding what to cut."""
    if tool_name == "Bash":
        cmd = (tool_input or {}).get("command", "") or ""
        if "tdq_state.py" in cmd:
            return "tdq_state.py (dump JSON)"
        if "unittest" in cmd or "pytest" in cmd:
            return "test suite run"
        if "doc_lint" in cmd:
            return "doc_lint"
        if "graphify" in cmd:
            return "graphify"
        return "other Bash"
    if tool_name == "Read":
        return "Read file"
    if tool_name in ("Edit", "MultiEdit"):
        return "Edit (echoes the diff back)"
    if tool_name and "tavily" in tool_name:
        return "tavily search"
    return tool_name or "?"


def _label(tool_name, tool_input):
    """A short label identifying one specific tool call in the top table."""
    inp = tool_input or {}
    for key in ("file_path", "command", "query", "description", "pattern"):
        if inp.get(key):
            return f"{tool_name}: {str(inp[key])[:70]}"
    return tool_name or "?"


# Images are counted by patch rather than by base64 string length: each 28×28 px patch is one
# vision token, so an image costs ⌈w/28⌉ × ⌈h/28⌉ tokens (Claude's Vision docs,
# platform.claude.com/docs/build-with-claude/vision, read 2026-08-19). When the size cannot be
# read, 1,600 is used — the level the docs give for a max-size image that is not downscaled.
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
    """The tokens of one image block. Reads the real size from the header, never decoding the image."""
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
    """The TEXT part of a tool_result, with the image payload lifted out (see `_tach_anh`)."""
    return _tach_anh(block)[0]


def _tach_anh(block):
    """Split a tool_result into (text part, total image tokens).

    The base64 payload of an image is replaced by a short label before counting: keeping it makes
    one screenshot swell to hundreds of thousands of tokens while the model spends a few thousand.
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


# ----------------------------------------------------------------- computation

def _message_key(ev, index):
    """The key that groups jsonl lines back into one message.

    Claude Code writes ONE message (thinking + text + tool_use) as SEVERAL jsonl lines sharing
    a `message.id`, each line repeating the whole `usage` block. Summing per line double-counts.
    A line with no `id` (old transcript) counts as a message of its own.
    """
    mid = (ev.get("message") or {}).get("id")
    return mid if mid else f"__line_{index}"


def _scan(path):
    """Returns (the list of Items of this file, the usage totals)."""
    events = list(iter_events(path))
    names = {}
    for ev in events:
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    names[block.get("id")] = (block.get("name"), block.get("input") or {})

    usage_by_msg = {}       # message key -> usage (the first occurrence wins)
    call_idx = []           # index of the FIRST line of each API call, ascending
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
    totals["tool_calls"] = len(names)        # already deduped by `tool_use.id`
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
    # Count the whole file in ONE batch: the cost lies in starting the venv python.
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
    """The carry-cost table grouped by bucket, descending. `paths` empty → empty table."""
    agg_tokens = collections.Counter()
    agg_count = collections.Counter()
    for item in _all_items(paths):
        agg_tokens[item.group] += item.tokens
        agg_count[item.group] += 1
    rows = [Row(g, agg_count[g], t) for g, t in agg_tokens.items()]
    rows.sort(key=lambda r: r.tokens, reverse=True)
    return rows


def top_items(paths, limit=15):
    """The priciest tool outputs by carry-cost."""
    return sorted(_all_items(paths), key=lambda it: it.tokens, reverse=True)[:limit]


def _phan_vi(day_sap_xep, q):
    """Nearest-rank percentile: position `ceil(q×n)`, counting from 1.

    This kind, not interpolation, because every printed value must be a REAL output present in
    the transcript — an interpolated number matches no call and cannot be traced back.
    """
    if not day_sap_xep:
        return 0
    n = len(day_sap_xep)
    hang = max(1, min(n, -(-int(round(q * n * 1000)) // 1000)))
    return day_sap_xep[hang - 1]


def phan_ra(paths):
    """Output size broken down per tool group: n, median, p90, p99, largest.

    Different from `carry_cost`: here are the REAL tokens of each output, not yet multiplied by
    the calls remaining. A high total carry-cost has two very different causes — many small calls
    (behaviour must change) or a few huge ones (an output ceiling must be set) — and only this
    table tells them apart.
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
    """Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how many
    re-read a file already read in the SAME session.

    This table only MEASURES, it does not judge: TDQ rules demand a re-read in several cases
    (`đọc lại, cấm làm theo trí nhớ`), so a high re-read count does NOT mean waste.  # i18n-allow
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
    """Sum the real usage the API returned: API calls, output, cache read/write."""
    totals = collections.Counter()
    for path in paths:
        _, got = _scan(path)
        totals.update(got)
    return dict(totals)


def cost_equivalent(totals, cache_ttl=DEFAULT_CACHE_TTL):
    """Normalise the bill into equivalent input tokens.

    `cache_read×0,1 + cache_write×W + input×1 + output×5`, W theo TTL cache
    (1 hour = 2.0 · 5 minutes = 1.25). Returns (total, {part: equivalent tokens}).
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
        description="Measure the token carry-cost of a Claude Code transcript.")
    parser.add_argument("--project", help="project folder (default: the current folder)")
    parser.add_argument("--transcript-dir", help="point straight at the folder holding *.jsonl")
    parser.add_argument("--sessions", type=int, default=3,
                        help="how many newest sessions to measure (default 3, 0 = all)")
    parser.add_argument("--top", type=int, default=0,
                        help="also print the N priciest tool outputs (default 0 = do not print)")
    parser.add_argument("--cache-ttl", choices=sorted(CACHE_WRITE_WEIGHT),
                        default=DEFAULT_CACHE_TTL,
                        help="cache TTL used to convert the cost (default 1h = factor 2.0)")
    args = parser.parse_args(argv)

    tdir = args.transcript_dir or default_transcript_dir(args.project)
    _log(f"reading transcripts from {tdir}")
    paths = find_sessions(tdir, args.sessions)
    if not paths:
        _log(f"no session found in {tdir} — nothing to measure")
        print("No session to measure.")
        return 0
    _log(f"measuring {len(paths)} session(s)")

    try:
        totals = usage_totals(paths)
        rows = carry_cost(paths)
    except skill_tokens.ThieuThuVienDem as exc:
        print("token_audit.py: the token-counting library `anthropic-tokenizer` is missing.\n"
              "This script is FORBIDDEN to estimate characters/4, so it stops here.\n"
              f"Install with: {exc}", file=sys.stderr)
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
    print(f"Converted cost (TTL {args.cache_ttl}): {_fmt(round(equiv))} equivalent "
          f"input tokens — {share}")
    print()
    print(f"{'group':<28}{'calls':>7}{'carry-cost (tokens)':>22}")
    print("-" * 57)
    for row in rows:
        print(f"{row.group:<28}{row.count:>7}{_fmt(row.tokens):>22}")
    print("-" * 57)
    print(f"{'TOTAL':<28}{sum(r.count for r in rows):>7}{_fmt(total_carry):>22}")

    print()
    print("# Output size breakdown (real tokens of each call)")
    print(f"{'group':<28}{'calls':>7}{'median':>10}{'p90':>10}{'p99':>10}{'largest':>11}")
    print("-" * 76)
    for pr in phan_ra(paths):
        print(f"{pr.group:<28}{pr.count:>7}{_fmt(pr.trung_vi):>10}{_fmt(pr.p90):>10}"
              f"{_fmt(pr.p99):>10}{_fmt(pr.lon_nhat):>11}")
    hv = hanh_vi_read(paths)
    if hv.tong:
        print()
        print(f"Read: {_fmt(hv.tong)} call(s) · with offset/limit {hv.co_pham_vi} "
              f"({hv.co_pham_vi / hv.tong * 100:.1f}%) · re-read an already-read file "
              f"{hv.doc_lai} ({hv.doc_lai / hv.tong * 100:.1f}%)")
        print("  (re-reading is the RIGHT behaviour in the 5 cases the rules demand — this only measures)")

    if args.top:
        print()
        print(f"# Top {args.top} priciest tool outputs")
        for item in top_items(paths, args.top):
            print(f"  {_fmt(item.tokens):>12} tok | {_fmt(item.chars):>8} chars | "
                  f"{item.group:<26} {item.label[:70]}")

    _log(f"done — total carry-cost {_fmt(total_carry)} tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
