#!/usr/bin/env python3
"""One table mapping every CLI sub-command name to its official English name.

Why this module exists: the sub-commands were first written as Vietnamese
abbreviations (`hop`, `kiem`, `mo-phong`). They read badly, so the official names
are now English. The old names are kept as HIDDEN aliases — they still appear in
hooks, portable bundles and older docs, and dropping them would break those at run
time for no gain. `--help` advertises the English names only, so nothing drifts back.

The table is the single source of truth: docs, tests and all five CLI scripts read
it from here instead of each keeping its own copy.
"""

# script file name → {name a user may type: the one official name}
# An official name maps to itself, so resolving is a single dict lookup.
BANG_DOI_TEN = {
    "tdq_team.py": {
        "phan-cong": "assign", "assign": "assign",
        "kiem-ke": "audit", "audit": "audit",
        "cum": "wave", "wave": "wave",
        "mo": "open", "open": "open",
        "kiem": "check", "check": "check",
        "hop": "merge", "merge": "merge",
        "soat": "sweep", "sweep": "sweep",
        "don": "clean", "clean": "clean",
        # `resolve` is new in this request and never had a Vietnamese name.
        "resolve": "resolve",
    },
    "tdq_bench.py": {
        "dung-plan": "gen-plan", "gen-plan": "gen-plan",
        "thuc-do": "calibrate", "calibrate": "calibrate",
        "mo-phong": "simulate", "simulate": "simulate",
        "quet": "scan", "scan": "scan",
    },
    "tdq_eval.py": {
        "dung-nhanh": "setup", "setup": "setup",
        "chay": "run", "run": "run",
        "cham": "score", "score": "score",
        "bao-cao": "report", "report": "report",
    },
    "tdq_lsp.py": {
        "kiem": "check", "check": "check",
        "danh-thuc": "wake", "wake": "wake",
        "nha": "release", "release": "release",
    },
    "tdq_state.py": {
        "tam-hoan": "pause", "pause": "pause",
        "tiep-tuc": "resume", "resume": "resume",
    },
}


def giai_ten(ten, bang):
    """Return the official name for what the user typed, or None if unknown."""
    return bang.get(ten)


def ten_chinh_thuc(bang):
    """The official names of one script, in declaration order, no duplicates."""
    thay = []
    for ten_moi in bang.values():
        if ten_moi not in thay:
            thay.append(ten_moi)
    return thay


def bi_danh(bang):
    """Only the old names — what `--help` must NOT advertise."""
    return [cu for cu, moi in bang.items() if cu != moi]
