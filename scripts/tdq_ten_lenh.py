#!/usr/bin/env python3
"""The names TDQ types: CLI sub-commands, and the name of the Python interpreter itself.

Why this module exists: the sub-commands were first written as Vietnamese
abbreviations (`hop`, `kiem`, `mo-phong`). They read badly, so the official names
are now English. The old names are kept as HIDDEN aliases — they still appear in
hooks, portable bundles and older docs, and dropping them would break those at run
time for no gain. `--help` advertises the English names only, so nothing drifts back.

The table is the single source of truth: docs, tests and all five CLI scripts read
it from here instead of each keeping its own copy.

It also owns `ten_lenh_python()`. That answer used to live in `build_portable.py`, but a
hook cannot import that module — it is the bundle builder, far too heavy to pull into a
hook that must answer in milliseconds. So the canonical answer moved here (this module is
stdlib-only and already imported by `tdq_state`) and `build_portable` now calls back into
it. One answer, two callers, no second copy to drift.
"""
import os
import shutil
import sys

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
    },
    "tdq_state.py": {
        "tam-hoan": "pause", "pause": "pause",
        "tiep-tuc": "resume", "resume": "resume",
        # `lech` is the spec-fixed official name; `lech-spec` mirrors the state key.
        "lech-spec": "lech", "lech": "lech",
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


# --------------------------------------------------------------- the interpreter's own name

# Windows has no `python3` on PATH: the official installer lays down `python` and the `py`
# launcher, while `python3` is only the Microsoft Store stub that opens the store instead of
# running Python (measured: it exits 49). `python` in turn is missing from many Linux builds.
# So `py -3` for Windows, `python3` everywhere else.
LENH_PYTHON_WINDOWS = "py -3"
LENH_PYTHON_KHAC = "python3"
# The stub lives under this folder. A `python3` resolving there is the store shim, not Python.
THU_MUC_STUB = "windowsapps"


def la_windows(nen_tang=None):
    """True when the target OS is Windows. Takes the platform as an ARGUMENT on purpose.

    Reading `sys.platform` in secret would make the Windows branch untestable from a macOS
    machine — which is exactly how this whole class of bug shipped in the first place.
    """
    return (nen_tang or sys.platform).startswith("win")


def ten_lenh_python(nen_tang=None):
    """The command name that runs Python 3 on `nen_tang` (default: the running machine)."""
    return LENH_PYTHON_WINDOWS if la_windows(nen_tang) else LENH_PYTHON_KHAC


def co_shim_python3(tim_lenh=None):
    """True when typing `python3` really starts Python on this machine.

    Windows resolves `python3` to the Microsoft Store stub unless a shim sits earlier on PATH,
    so "the name exists" is not the question — "does it resolve to something other than the
    stub" is. Checking the resolved PATH rather than running the binary keeps this cheap enough
    for a hook: spawning a process on every SessionStart would cost more than the answer.
    """
    duong = (tim_lenh or shutil.which)("python3")
    if not duong:
        return False
    return THU_MUC_STUB not in duong.replace(os.sep, "/").lower()


def can_nhac_ten_lenh(nen_tang=None, tim_lenh=None):
    """The one reminder line for a machine where `python3` is not typeable, else "".

    Empty string on macOS, on Linux, and on a Windows box that already has the shim — a hook
    must stay silent when there is nothing to say.
    """
    if not la_windows(nen_tang) or co_shim_python3(tim_lenh):
        return ""
    return (f"[TDQ] On this machine `python3` is not a command: type `{LENH_PYTHON_WINDOWS}` "
            f"instead, or install the shim once with "
            f"`{LENH_PYTHON_WINDOWS} scripts/tdq_checkportable.py setup --shim`.")
