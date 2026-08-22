#!/usr/bin/env python3
"""tdq_timing.py — time a TDQ request and each of its phases.

Two numbers from two different sources, deliberately side by side:

        Wall clock  — the marks in `state.json` (`started_at` + `phase_history`). It includes
                                    the time waiting for user approval, so this is "how long the request cost me".
        Model time  — the sum of the gaps between model steps in the transcript, counting only
                                    gaps ≤ MAX_GAP_SECONDS (reusing the threshold of `step_audit.py`).
                                    This is "how long the machine worked". A phase that waited 2 hours for
                                    approval while the model ran 3 minutes splits the two columns where it matters.

This script does NOT write `state.json` (architecture rule: only `tdq_state.py` may write).
It only reads state and writes `docs/tdq/timing.jsonl` — historical data, not state.

Usage:
        python3 scripts/tdq_timing.py show              # markdown table of the open request
        python3 scripts/tdq_timing.py show --json       # the same data as JSON
        python3 scripts/tdq_timing.py close             # close the books: append 1 line to timing.jsonl

Env: TDQ_PROJECT_DIR picks the project · TDQ_LOG=0 turns the progress log off (log to stderr).
Exit: 0 even with no open request or no transcript found. 2 = bad syntax.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tdq_state  # noqa: E402
from step_audit import MAX_GAP_SECONDS, _has_usage, _parse_time  # noqa: E402
from token_audit import default_transcript_dir, find_sessions, iter_events  # noqa: E402

TIMING_REL = os.path.join("docs", "tdq", "timing.jsonl")
EXIT_SYNTAX = 2


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log progress to stderr with a timestamp. Turn it off with TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------------- formatting

def dinh_dang(giay):
    """Seconds → a human string. `None` → '—' (not measurable, different from 0)."""
    if giay is None:
        return "—"
    giay = int(round(giay))
    if giay < 60:
        return f"{giay}s"
    phut, du = divmod(giay, 60)
    if phut < 60:
        return f"{phut} min" if du < 30 else f"{phut + 1} min"
    gio, phut = divmod(phut, 60)
    return f"{gio}h" if phut == 0 else f"{gio}h {phut:02d}min"


# ------------------------------------------------------------------ phase windows

def cua_so_phase(state, ket_thuc):
    """`phase_history` → the list of windows [(phase, start, end)] in order.

    The last mark runs until `ket_thuc` (the moment being considered). Broken marks are dropped
    in `tdq_state.load`, so all that matters here is a mark whose time cannot be parsed.
    """
    moc = []
    for item in state.get("phase_history") or []:
        at = _parse_time(item.get("at"))
        if at:
            moc.append((item.get("phase"), at))
    cua_so = []
    for i, (phase, bat_dau) in enumerate(moc):
        het = moc[i + 1][1] if i + 1 < len(moc) else ket_thuc
        if het and het >= bat_dau:
            cua_so.append((phase, bat_dau, het))
    return cua_so


def moc_model(transcript_dir, tu, den):
    """The sorted list of model STEP timestamps falling inside [tu, den].

    Returns `None` when no transcript could be read — quite different from 'there is a transcript
    but the model ran 0 seconds', so the model column prints '—' instead of '0s'.
    """
    if not transcript_dir or not os.path.isdir(transcript_dir):
        _log(f"no transcript folder: {transcript_dir} — dropping the model time column")
        return None
    files = find_sessions(transcript_dir, limit=0)
    if not files:
        _log(f"empty transcript folder: {transcript_dir} — dropping the model time column")
        return None
    thoi_diem = []
    for path in files:
        for event in iter_events(path):
            if event.get("type") != "assistant" or not _has_usage(event):
                continue
            at = _parse_time(event.get("timestamp"))
            if at and (tu is None or at >= tu) and (den is None or at <= den):
                thoi_diem.append(at)
    _log(f"read {len(files)} transcript(s), took {len(thoi_diem)} model step(s) inside the request window")
    return sorted(thoi_diem)


def _giay_model(thoi_diem, bat_dau, het):
    """Sum the gaps between consecutive model steps inside one window.

    A gap longer than `MAX_GAP_SECONDS` means the user went away and came back, not the model
    working — dropped, exactly as `step_audit.py` does with latency.
    """
    trong = [t for t in thoi_diem if bat_dau <= t <= het]
    tong = 0.0
    for truoc, sau in zip(trong, trong[1:]):
        gap = (sau - truoc).total_seconds()
        if 0 <= gap <= MAX_GAP_SECONDS:
            tong += gap
    return tong


def tong_hop(state, ket_thuc, transcript_dir):
    """The full data of the open request. Returns None when there is no request yet."""
    slug = state.get("active_request")
    if not slug:
        return None
    bat_dau = _parse_time(state.get("started_at"))
    cua_so = cua_so_phase(state, ket_thuc)
    if bat_dau is None and cua_so:
        bat_dau = cua_so[0][1]
    thoi_diem = moc_model(transcript_dir, bat_dau, ket_thuc)

    gop = {}
    thu_tu = []
    for phase, tu, den in cua_so:
        if phase not in gop:
            gop[phase] = {"phase": phase, "treo_tuong_giay": 0, "model_giay": 0, "so_lan": 0}
            thu_tu.append(phase)
        muc = gop[phase]
        muc["treo_tuong_giay"] += int(round((den - tu).total_seconds()))
        muc["so_lan"] += 1
        if thoi_diem is not None:
            muc["model_giay"] += int(round(_giay_model(thoi_diem, tu, den)))
    phases = [gop[p] for p in thu_tu]
    if thoi_diem is None:
        for muc in phases:
            muc["model_giay"] = None

    # Both totals are measured over the SAME window (started_at → the closing moment), not as the
    # sum of the phase windows: an old state whose `started_at` was patched later can have model
    # steps outside every phase window, and summing per phase would miss them and split the totals.
    tong_treo = int(round((ket_thuc - bat_dau).total_seconds())) if bat_dau else 0
    tong_model = (None if thoi_diem is None or bat_dau is None
                  else int(round(_giay_model(thoi_diem, bat_dau, ket_thuc))))
    return {
        "slug": slug,
        "lane": state.get("lane"),
        "started_at": state.get("started_at") or (bat_dau.isoformat() if bat_dau else None),
        "closed_at": ket_thuc.isoformat(timespec="seconds"),
        "treo_tuong_giay": tong_treo,
        "model_giay": tong_model,
        "phases": phases,
    }


def bang_markdown(so_lieu):
    """The 4-column markdown table — the shared template for the report and `tdq-status`."""
    dong = [f"Request `{so_lieu['slug']}` · lane {so_lieu['lane'] or '—'} · "
            f"opened at {so_lieu['started_at'] or '—'}",
            "",
            "| Phase | Wall clock | Model time | Times entered |",
            "|---|---|---|---|"]
    for muc in so_lieu["phases"]:
        dong.append(f"| {muc['phase']} | {dinh_dang(muc['treo_tuong_giay'])} | "
                    f"{dinh_dang(muc['model_giay'])} | {muc['so_lan']} |")
    dong.append(f"| **Total** | **{dinh_dang(so_lieu['treo_tuong_giay'])}** | "
                f"**{dinh_dang(so_lieu['model_giay'])}** | |")
    if so_lieu["model_giay"] is None:
        dong.append("")
        dong.append("Model column is `—`: the transcript of this session could not be read.")
    return "\n".join(dong)


def dong_ho_ngan(so_lieu):
    """One line for `tdq-status`: how long the running phase has cost, and the whole request."""
    dang = so_lieu["phases"][-1] if so_lieu["phases"] else None
    if dang is None:
        return f"⏱ {so_lieu['slug']}: {dinh_dang(so_lieu['treo_tuong_giay'])}"
    return (f"⏱ {dang['phase']} {dinh_dang(dang['treo_tuong_giay'])}"
            f" (model {dinh_dang(dang['model_giay'])})"
            f" · whole request {dinh_dang(so_lieu['treo_tuong_giay'])}")


# --------------------------------------------------------------------- close the books

def da_dong_so(cwd, slug, started_at):
    """Does this request already have a line in timing.jsonl — guards against double counting.

    `init` and `tdq_finish --phase idle` both call the close step; without the guard one request
    appears twice and every statistic after it is wrong.
    """
    path = os.path.join(cwd, TIMING_REL)
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ban_ghi = json.loads(line)
                except ValueError:
                    continue
                if ban_ghi.get("slug") == slug and ban_ghi.get("started_at") == started_at:
                    return True
    except OSError:
        return False
    return False


def dong_so(cwd, so_lieu):
    """Append exactly one JSON line to timing.jsonl. Returns False if it was closed before."""
    if da_dong_so(cwd, so_lieu["slug"], so_lieu["started_at"]):
        _log(f"request {so_lieu['slug']} already in {TIMING_REL} — not written again")
        return False
    path = os.path.join(cwd, TIMING_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(so_lieu, ensure_ascii=False) + "\n")
    _log(f"closed the books on {so_lieu['slug']} into {TIMING_REL}")
    return True


# -------------------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tdq_timing.py",
        description="Time a TDQ request: wall clock and model time, per phase.")
    parser.add_argument("cmd", choices=("show", "close", "status"),
                        help="show = print the table · close = close the books into timing.jsonl · "
                             "status = a one-line clock")
    parser.add_argument("--json", action="store_true", dest="want_json",
                        help="print the raw data as JSON")
    parser.add_argument("--now", help="the 'now' mark in ISO form (so tests are reproducible)")
    parser.add_argument("--transcript-dir", help="transcript folder, defaults to the project one")
    parser.add_argument("--project", help="project folder, defaults to TDQ_PROJECT_DIR/git root")
    args = parser.parse_args(argv)

    cwd = args.project or tdq_state.resolve_project_dir()
    ket_thuc = _parse_time(args.now) if args.now else datetime.datetime.now().astimezone()
    if args.now and ket_thuc is None:
        print(f"--now is not an ISO timestamp: {args.now}", file=sys.stderr)
        return EXIT_SYNTAX

    state = tdq_state.load(cwd)
    if not state or not state.get("active_request"):
        # Having no open request is NOT an error: hooks and the report call this unconditionally.
        print("No open request yet — nothing to time.")
        return 0

    transcript_dir = args.transcript_dir or default_transcript_dir(cwd)
    so_lieu = tong_hop(state, ket_thuc, transcript_dir)

    if args.cmd == "close":
        dong_so(cwd, so_lieu)
        if args.want_json:
            print(json.dumps(so_lieu, ensure_ascii=False))
        else:
            print(bang_markdown(so_lieu))
        return 0
    if args.cmd == "status":
        print(dong_ho_ngan(so_lieu))
        return 0
    print(json.dumps(so_lieu, ensure_ascii=False) if args.want_json else bang_markdown(so_lieu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
