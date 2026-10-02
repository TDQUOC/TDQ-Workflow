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
        if pl["loai"] == "khong_phai_tim":
            continue
        tt = dict(search_rules.trang_thai(so), cua_so=cua_so)
        ok, ly_do = luat.quyet_dinh(pl, tt)
        hang.append({"luot": sk.get("luot"), "cong_cu": cong_cu, "lenh": lenh,
                     "loai": pl["loai"], "cho_phep": ok, "ly_do": ly_do})
        if not ok:
            bat += 1
            bi_chan.append(sk.get("luot"))
            if pl["loai"] == "loc_file":
                bat_oan += 1
        elif pl["loai"] == "tim_code" and not tt["da_goi_khai_niem"]:
            lot += 1
        if pl["loai"] == "tim_code":
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
        qd = "allow" if h["cho_phep"] else "deny"
        dong.append(f"| {h['luot']} | {h['cong_cu']} | {_cat(h['lenh'])} | {qd} | "
                    f"{str(h['ly_do']).replace('|', '/')} |")
    # "denied" is every denial (JSON key `bat`); "right" is the part that was not a file-list filter.
    dong += ["", f"denied: {kq['bat']} (right: {kq['bat'] - kq['bat_oan']}) · "
                 f"false denials: {kq['bat_oan']} · leaks: {kq['lot']}",
             "denied at events: " + (", ".join(str(x) for x in kq["bi_chan"]) or "(none)")]
    return "\n".join(dong)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Replay a session's searches through the search rules.")
    ap.add_argument("duong", help="fixture .json or Claude transcript .jsonl")
    ap.add_argument("--cua-so", type=int, default=None, help="override CUA_SO (search window)")
    ap.add_argument("--json", action="store_true", help="print counts as JSON")
    args = ap.parse_args(argv)
    _log(f"reading {args.duong}")
    kq = phat_lai(doc_dau_vao(args.duong), cua_so=args.cua_so)
    if args.json:
        print(json.dumps({k: kq[k] for k in ("bat", "bat_oan", "lot", "bi_chan", "luat")},
                         ensure_ascii=False))
    else:
        print(in_bang(kq))
    return 0


if __name__ == "__main__":
    sys.exit(main())
