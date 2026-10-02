#!/usr/bin/env python3
"""Replay a recorded session's searches through the search-rule decision function.

Usage:
    python scripts/search_replay.py <fixture.json | transcript.jsonl> [--cua-so N] [--json]

Input: a fixture shaped like `tests/fixtures/phien_excalidraw_tim.json`
({"nguon", "ghi_chu", "su_kien": [{"luot", "loai", "cong_cu", "lenh", "token"}]}), or a raw
Claude transcript `.jsonl`, which is first turned into the same event list (see
`su_kien_tu_transcript`).

Rules: `scripts/search_rules.py` (`phan_loai`, `quyet_dinh`, `CUA_SO`). Until that module exists
a stub is used that lets every search through; the output header says which one ran.

Replay semantics (the whole input is treated as ONE request):
- state starts as da_goi_khai_niem=False, so_lan_tim_tu_lan_goi=0, token_prompt=set(),
  cua_so=CUA_SO (or --cua-so).
- "prompt"     -> token_prompt = set(event["token"]) (latest prompt only).
- "he_thong", "skill", "doc" -> no state change; "doc" is not a search and gets no row.
- "khai_niem"  -> da_goi_khai_niem=True, so_lan_tim_tu_lan_goi=0.
- "tim"        -> pl = phan_loai(cong_cu, lenh); skipped when pl["loai"] == "khong_phai_tim";
  otherwise (ok, why) = quyet_dinh(pl, state) and a row is recorded. A "tim_code" search bumps
  so_lan_tim_tu_lan_goi whether allowed or denied — the real agent did run it.
Counts: bat = denied rows; bat_oan = denied rows whose loai is "loc_file"; lot = allowed
"tim_code" rows while da_goi_khai_niem was still False.

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

DO_DAI_LENH = 70
# A Bash command counts as a search when it calls one of these tools as a word.
LENH_TIM = re.compile(r"(?<![\w-])(grep|rg|findstr)(?![\w-])")
TU_DINH_DANH = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] search_replay: {message}",
              file=sys.stderr)


class _LuatStub:
    """Stand-in for scripts/search_rules.py until it lands: allows every search."""
    TEN = "stub"
    CUA_SO = 10

    @staticmethod
    def phan_loai(cong_cu, lenh):
        loai = "tim_code" if _la_lenh_tim(cong_cu, lenh) else "khong_phai_tim"
        return {"loai": loai, "tu_khoa": [], "doan_mo": False}

    @staticmethod
    def quyet_dinh(pl, trang_thai):
        return True, "stub: allow all"


def _la_lenh_tim(cong_cu, lenh):
    if cong_cu == "Grep":
        return True
    return cong_cu == "Bash" and bool(LENH_TIM.search(lenh or ""))


def nap_luat():
    """Return the real rules module if importable, else the allow-all stub."""
    try:
        import search_rules  # noqa: WPS433 — optional until T2.1 lands
    except ImportError:
        return _LuatStub
    return search_rules


def ten_luat(luat):
    return getattr(luat, "TEN", None) or (
        "stub" if luat is _LuatStub else getattr(luat, "__name__", "search_rules"))


def phat_lai(su_kien, cua_so=None, luat=None):
    """Run events through the rules. Returns {"hang", "bat", "bat_oan", "lot", "bi_chan", "luat"}."""
    luat = luat or nap_luat()
    trang_thai = {
        "da_goi_khai_niem": False,
        "so_lan_tim_tu_lan_goi": 0,
        "token_prompt": set(),
        "cua_so": cua_so if cua_so is not None else luat.CUA_SO,
    }
    hang, bat, bat_oan, lot, bi_chan = [], 0, 0, 0, []
    for sk in su_kien:
        loai = sk.get("loai")
        if loai == "prompt":
            trang_thai["token_prompt"] = set(sk.get("token") or [])
        elif loai == "khai_niem":
            trang_thai["da_goi_khai_niem"] = True
            trang_thai["so_lan_tim_tu_lan_goi"] = 0
        elif loai == "tim":
            pl = luat.phan_loai(sk.get("cong_cu", ""), sk.get("lenh", ""))
            if pl["loai"] == "khong_phai_tim":
                continue
            # Hand the rules a copy so a buggy rule cannot rewrite the replay's state.
            ok, ly_do = luat.quyet_dinh(pl, dict(trang_thai, token_prompt=set(trang_thai["token_prompt"])))
            hang.append({"luot": sk.get("luot"), "cong_cu": sk.get("cong_cu", ""),
                         "lenh": sk.get("lenh", ""), "loai": pl["loai"], "cho_phep": ok,
                         "ly_do": ly_do})
            if not ok:
                bat += 1
                bi_chan.append(sk.get("luot"))
                if pl["loai"] == "loc_file":
                    bat_oan += 1
            elif pl["loai"] == "tim_code" and not trang_thai["da_goi_khai_niem"]:
                lot += 1
            if pl["loai"] == "tim_code":
                trang_thai["so_lan_tim_tu_lan_goi"] += 1
        # he_thong, skill, doc: no state change, no row.
    _log(f"{len(su_kien)} events · {len(hang)} searches · bat {bat} · bat_oan {bat_oan} · lot {lot}")
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
    if ten.startswith("mcp__lsp__") or ten.startswith("mcp__plugin_lumen"):
        return {"loai": "khai_niem", "cong_cu": ten}
    if ten == "Skill":
        return {"loai": "skill", "cong_cu": ten}
    if ten == "Grep":
        return {"loai": "tim", "cong_cu": ten, "lenh": inp.get("pattern", "")}
    if ten == "Bash":
        lenh = inp.get("command", "")
        return {"loai": "tim" if LENH_TIM.search(lenh) else "doc", "cong_cu": ten, "lenh": lenh}
    if ten in ("Read", "Glob"):
        return {"loai": "doc", "cong_cu": ten, "lenh": inp.get("file_path") or inp.get("pattern", "")}
    return None


def su_kien_tu_transcript(duong):
    """Build the fixture event list from a raw Claude transcript (.jsonl).

    Extraction rules: a user message with plain text (not a tool result) -> "prompt" whose tokens
    are its lower-cased identifier words (3+ chars, text itself not kept); text starting with "<"
    (system/command wrappers) -> "he_thong". Assistant tool_use: Bash with grep/rg/findstr or the
    Grep tool -> "tim"; other Bash, Read, Glob -> "doc"; mcp__lsp__* / lumen -> "khai_niem";
    Skill -> "skill"; any other tool is dropped.
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
    nhan = "search_rules" if kq["luat"] != "stub" else "STUB — cho qua tất cả"
    dong = [f"luật: {nhan}", "", "| luot | cong cu | lenh | quyet dinh | ly do |",
            "|---|---|---|---|---|"]
    for h in kq["hang"]:
        qd = "cho" if h["cho_phep"] else "chan"
        dong.append(f"| {h['luot']} | {h['cong_cu']} | {_cat(h['lenh'])} | {qd} | "
                    f"{str(h['ly_do']).replace('|', '/')} |")
    # "bắt" is every denial (JSON key `bat`); "bắt đúng" is the part that was not a file-list filter.
    dong += ["", f"bắt: {kq['bat']} (bắt đúng: {kq['bat'] - kq['bat_oan']}) · "
                 f"bắt oan: {kq['bat_oan']} · lọt: {kq['lot']}",
             "bị chặn ở lượt: " + (", ".join(str(x) for x in kq["bi_chan"]) or "(none)")]
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
