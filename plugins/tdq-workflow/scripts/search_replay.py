#!/usr/bin/env python3
"""Replay a recorded session's searches through the search-rule decision function.

Usage:
    python scripts/search_replay.py <fixture.json | transcript.jsonl> [--cua-so N] [--json]

Input: a fixture shaped like `tests/fixtures/phien_excalidraw_tim.json`
({"nguon", "ghi_chu", "su_kien": [{"luot", "loai", "cong_cu", "lenh", "token"}]}), or a raw
Claude transcript `.jsonl`, which is first turned into the same event list (see
`su_kien_tu_transcript`).

Rules: `scripts/search_rules.py` — the SAME pure functions the gate runs (`phan_loai`,
`quyet_dinh`, `la_goi_khai_niem`, `trang_thai`, `CUA_SO`); a test may pass its own `luat`.

Replay semantics (the whole input is treated as ONE request), mirroring `search_gate.quyet`:
- the replay keeps ledger rows exactly like `search_observe` + the gate write them, and builds
  the state with `search_rules.trang_thai(rows)` plus cua_so=CUA_SO (or --cua-so).
- "prompt"     -> a prompt row (latest prompt's tokens win).
- any tool event whose `la_goi_khai_niem` label is set -> a concept row (re-opens the window);
  `start_lsp`/`open_document` and other housekeeping are NOT concept queries.
- every other Bash/Grep/shell event -> pl = phan_loai(cong_cu, lenh); skipped when
  "khong_phai_tim"; otherwise (ok, why) = quyet_dinh(pl, state) and a table row is recorded.
  A "tim_code" search adds a ledger row that counts toward the window only when it RAN (allowed).
Counts: bat = denied rows; bat_oan = denied rows whose loai is "loc_file"; lot = allowed
"tim_code" rows while no concept query had been made.

Log service: ISO timestamps on stderr, on by default; TDQ_LOG=0 turns the log off.
This module never imports from hooks/ (repo law: scripts/ does not import hooks/).
"""
import argparse
import io
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import utf8_io  # noqa: E402,F401 — imported so stdout/stderr become UTF-8

import search_rules  # noqa: E402

DO_DAI_LENH = 70
TU_DINH_DANH = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] search_replay: {message}",
              file=sys.stderr)


def ten_luat(luat):
    return getattr(luat, "TEN", None) or getattr(luat, "__name__", "search_rules")


def phat_lai(su_kien, cua_so=None, luat=None):
    """Run events through the rules. Returns {"hang", "bat", "bat_oan", "lot", "bi_chan", "luat"}."""
    luat = luat or search_rules
    cua_so = cua_so if cua_so is not None else luat.CUA_SO
    so, hang, bat, bat_oan, lot, bi_chan = [], [], 0, 0, 0, []
    for sk in su_kien:
        loai, cong_cu, lenh = sk.get("loai"), sk.get("cong_cu", ""), sk.get("lenh", "")
        if loai == "prompt":
            so.append({"loai": "prompt", "token": list(sk.get("token") or [])})
            continue
        if not cong_cu:
            continue  # he_thong and other bookkeeping: no state change, no row
        vao = {"command": lenh} if cong_cu != "Grep" else {"pattern": lenh}
        if search_rules.la_goi_khai_niem(cong_cu, vao):
            so.append({"loai": "khai_niem"})
            continue
        pl = luat.phan_loai(cong_cu, lenh)
        if pl.get("status") != "unknown" and pl.get("loai") == "khong_phai_tim":
            continue
        tt = dict(search_rules.trang_thai(so), cua_so=cua_so)
        ok, ly_do = luat.quyet_dinh(pl, tt)
        hang.append({"luot": sk.get("luot"), "cong_cu": cong_cu, "lenh": lenh,
                     "loai": pl.get("loai"), "status": pl.get("status"), "kind": pl.get("kind"),
                     "cho_phep": ok, "ly_do": ly_do})
        if not ok:
            bat += 1
            bi_chan.append(sk.get("luot"))
            if pl.get("loai") == "loc_file":
                bat_oan += 1
        elif pl.get("loai") == "tim_code" and not tt["da_goi_khai_niem"]:
            lot += 1
        if pl.get("loai") == "tim_code" or pl.get("status") == "unknown":
            so.append({"loai": "tim", "cho_phep": ok, "tinh_cua_so": ok})
    _log(f"{len(su_kien)} events · {len(hang)} searches · denied {bat} · "
         f"false denials {bat_oan} · leaks {lot}")
    return {"hang": hang, "bat": bat, "bat_oan": bat_oan, "lot": lot, "bi_chan": bi_chan,
            "luat": ten_luat(luat)}


def _noi_dung_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
            return None
        return " ".join(c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text")
    return None


def _su_kien_cong_cu(ten, inp):
    if ten == "Skill":
        return {"loai": "skill", "cong_cu": ten}
    if search_rules.la_goi_khai_niem(ten, inp):
        return {"loai": "khai_niem", "cong_cu": ten}
    if ten == "Grep":
        return {"loai": "tim", "cong_cu": ten, "lenh": inp.get("pattern", "")}
    if str(ten).lower() in search_rules.CONG_CU_SHELL:
        # Every shell command goes to the rules — the gate sees them all, not a pre-filtered few.
        return {"loai": "tim", "cong_cu": ten, "lenh": inp.get("command", "")}
    if ten in ("Read", "Glob"):
        return {"loai": "doc", "cong_cu": ten, "lenh": inp.get("file_path") or inp.get("pattern", "")}
    return None


def su_kien_tu_transcript(duong):
    """Build the fixture event list from a raw Claude transcript (.jsonl).

    Extraction rules: a user message with plain text (not a tool result) -> "prompt" whose tokens
    are its lower-cased identifier words (3+ chars, text itself not kept); text starting with "<"
    (system/command wrappers) -> "he_thong". Assistant tool_use: a concept query per
    `search_rules.la_goi_khai_niem` -> "khai_niem"; Grep and every shell command -> "tim" (the
    rules decide); Read, Glob -> "doc"; Skill -> "skill"; any other tool is dropped.
    """
    su_kien = []
    with io.open(duong, encoding="utf-8") as fh:
        for dong in fh:
            dong = dong.strip()
            if not dong:
                continue
            try:
                ban_ghi = json.loads(dong)
            except ValueError:
                continue
            msg = ban_ghi.get("message") or {}
            if ban_ghi.get("type") == "user":
                text = _noi_dung_text(msg.get("content"))
                if text is None:
                    continue
                if text.lstrip().startswith("<"):
                    su_kien.append({"loai": "he_thong"})
                else:
                    token = sorted({t.lower() for t in TU_DINH_DANH.findall(text)})
                    su_kien.append({"loai": "prompt", "token": token})
            elif ban_ghi.get("type") == "assistant" and isinstance(msg.get("content"), list):
                for c in msg["content"]:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        sk = _su_kien_cong_cu(c.get("name", ""), c.get("input") or {})
                        if sk:
                            su_kien.append(sk)
    for i, sk in enumerate(su_kien):
        sk["luot"] = i
    return su_kien


def phan_tich_lsp_telemetry(duong):
    """Trích xuất và tổng hợp telemetry LSP từ transcript JSONL hoặc file sổ (O5)."""
    rows_lsp = []
    if duong.lower().endswith(".jsonl"):
        # Ghép cặp tool_use và tool_result từ transcript JSONL
        pending_use = {}
        with io.open(duong, encoding="utf-8") as fh:
            for dong in fh:
                dong = dong.strip()
                if not dong:
                    continue
                try:
                    ban_ghi = json.loads(dong)
                except ValueError:
                    continue
                msg = ban_ghi.get("message") or {}
                if ban_ghi.get("type") == "assistant" and isinstance(msg.get("content"), list):
                    for c in msg["content"]:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            name = str(c.get("name") or "")
                            if "lsp" in name.lower():
                                call_id = c.get("id")
                                if call_id:
                                    pending_use[call_id] = {
                                        "name": name,
                                        "ts": float(ban_ghi.get("timestamp") or 0)
                                    }
                elif ban_ghi.get("type") == "user" and isinstance(msg.get("content"), list):
                    for c in msg["content"]:
                        if isinstance(c, dict) and c.get("type") == "tool_result":
                            call_id = c.get("tool_use_id")
                            if call_id and call_id in pending_use:
                                info = pending_use.pop(call_id)
                                ts_end = float(ban_ghi.get("timestamp") or 0)
                                dur = int(round((ts_end - info["ts"]) * 1000)) if (ts_end and info["ts"]) else None
                                outcome = search_rules.phan_loai_ket_qua_lsp("PostToolUse", {"tool_response": c.get("content")})
                                rows_lsp.append({
                                    "loai": "lsp_ket_qua",
                                    "cong_cu": info["name"],
                                    "outcome": outcome,
                                    "duration_ms": max(0, dur) if dur is not None else 0,
                                    "tool_use_id": call_id,
                                })
    elif duong.lower().endswith(".json"):
        # Fixture hoặc file JSON xuất
        with io.open(duong, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            rows_lsp = [r for r in data if r.get("loai") == "lsp_ket_qua"]
        elif isinstance(data, dict):
            su_kien = data.get("su_kien") or []
            rows_lsp = [r for r in su_kien if r.get("loai") == "lsp_ket_qua"]

    return search_rules.thong_ke_lsp(rows_lsp)


def doc_dau_vao(duong):
    if duong.lower().endswith(".jsonl"):
        return su_kien_tu_transcript(duong)
    with io.open(duong, encoding="utf-8") as fh:
        return json.load(fh)["su_kien"]


def _cat(lenh):
    mot_dong = " ".join((lenh or "").split()).replace("|", "\\|")
    return mot_dong if len(mot_dong) <= DO_DAI_LENH else mot_dong[:DO_DAI_LENH - 1] + "…"


def in_bang(kq):
    dong = [f"rules: {kq['luat']}", "", "| event | tool | command | decision | reason |",
            "|---|---|---|---|---|"]
    for h in kq["hang"]:
        qd = "allow" if h["cho_phep"] else "blocked"
        dong.append(f"| {h['luot']} | {h['cong_cu']} | {_cat(h['lenh'])} | {qd} | "
                    f"{str(h['ly_do']).replace('|', '/')} |")
    # "denied" is every denial (JSON key `bat`); "right" is the part that was not a file-list filter.
    dong += ["", f"denied: {kq['bat']} (right: {kq['bat'] - kq['bat_oan']}) · "
                 f"false denials: {kq['bat_oan']} · leaks: {kq['lot']}",
             "denied at events: " + (", ".join(str(x) for x in kq["bi_chan"]) or "(none)")]
    return "\n".join(dong)


def in_bang_lsp_telemetry(tk):
    dong = [
        "LSP Telemetry & Circuit Breaker Report",
        "",
        f"Total LSP Calls: {tk.get('tong_so', 0)}",
        f"Circuit Breaker Status: {'OPEN (HALTED)' if tk.get('mach_ngat_mo') else 'CLOSED (HEALTHY)'}",
        "",
        "Outcome Breakdown:",
        f"  - ok:      {tk.get('dem_outcome', {}).get('ok', 0)}",
        f"  - empty:   {tk.get('dem_outcome', {}).get('empty', 0)}",
        f"  - error:   {tk.get('dem_outcome', {}).get('error', 0)}",
        f"  - timeout: {tk.get('dem_outcome', {}).get('timeout', 0)}",
        "",
        "Latency Percentiles:",
        f"  - p50: {tk.get('p50_ms', 0)} ms",
        f"  - p95: {tk.get('p95_ms', 0)} ms",
        f"  - max: {tk.get('max_ms', 0)} ms",
    ]
    return "\n".join(dong)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Replay a session's searches through the search rules.")
    ap.add_argument("duong", help="fixture .json or Claude transcript .jsonl")
    ap.add_argument("--cua-so", type=int, default=None, help="override CUA_SO (search window)")
    ap.add_argument("--json", action="store_true", help="print counts as JSON")
    ap.add_argument("--lsp-telemetry", action="store_true", help="extract and report LSP latency and outcome telemetry")
    args = ap.parse_args(argv)
    _log(f"reading {args.duong}")
    if args.lsp_telemetry:
        tk = phan_tich_lsp_telemetry(args.duong)
        if args.json:
            print(json.dumps(tk, ensure_ascii=False))
        else:
            print(in_bang_lsp_telemetry(tk))
        return 0

    kq = phat_lai(doc_dau_vao(args.duong), cua_so=args.cua_so)
    if args.json:
        print(json.dumps({k: kq[k] for k in ("bat", "bat_oan", "lot", "bi_chan", "luat")},
                         ensure_ascii=False))
    else:
        print(in_bang(kq))
    return 0



if __name__ == "__main__":
    sys.exit(main())
