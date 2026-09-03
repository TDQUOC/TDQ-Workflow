#!/usr/bin/env python3
"""The worktree ledger: the single source of truth about worktrees the workflow opened.

Why a file of its own instead of a field in `docs/tdq/state.json`: `tdq_state.py init`
WIPES the state on every new request, while a worktree outlives the request that opened
it. A ledger that dies with the request can never answer "what is still lying around from
last week", which is the whole reason this file exists.

Three readers share it — `tdq_team.py` writes, `tdq_state.py` reads to block a phase, and
the prompt hook reads to nudge. That is why the schema is locked in `TRUONG` and why every
reader goes through this module instead of parsing the JSON itself: three hand-rolled
parsers drift apart and no check catches it.

This module is pure data: it never calls git and never removes a directory. Deciding
whether a worktree MAY be removed belongs to `tdq_team.py`, which is the module that knows
about git; keeping the two apart is what makes the ledger testable without a repo.
"""
import json
import os
import sys
from datetime import datetime

SCHEMA_VERSION = 1

# The seven locked fields. Adding one is a breaking change for all three readers, so the
# test grid pins both the names and the count.
TRUONG = ("slug", "ma_task", "nhanh", "duong_dan", "tao_luc", "trang_thai", "dong_luc")

TRANG_THAI_MO = "mo"
TRANG_THAI_DONG = "dong"

# Disk thresholds that turn a report into a warning. Approved with the spec of request
# 2026-08-22-1033: 500 MB total, or a single worktree older than 7 days.
TRAN_TONG_MB = 500
TRAN_TUOI_NGAY = 7

# CLOSED set of reasons a worktree cannot be cleaned up yet. Each reason MUST carry at
# least one option with a runnable command: a blocked worktree with no way out printed is
# exactly the worktree that gets forgotten and keeps eating disk.
LY_DO_CHAN = {
    "ban": {
        "mo_ta": "the worktree still holds uncommitted changes",
        "phuong_an": [
            {"mo_ta": "commit them onto the task branch",
             "lenh": 'git -C {duong_dan} add -A && git -C {duong_dan} commit -m "wip {ma_task}"'},
            {"mo_ta": "throw the changes away",
             "lenh": "git -C {duong_dan} restore -SW . && git -C {duong_dan} clean -fd"},
            {"mo_ta": "keep it for now and look at it yourself",
             "lenh": "git -C {duong_dan} status"},
        ],
    },
    "bo-qua": {
        "mo_ta": "ignored files here do not regenerate, and cleaning up would delete them",
        "phuong_an": [
            {"mo_ta": "look at the list first — these are files git hides",
             "lenh": "git -C {duong_dan} status --porcelain --ignored=matching"},
            {"mo_ta": "move what matters somewhere safe, then sweep again",
             "lenh": "mv {duong_dan}/<file> <a folder you keep> "
                     "&& python3 scripts/tdq_team.py sweep --clean"},
            {"mo_ta": "delete them for good — this frees the worktree in one step",
             "lenh": "git -C {duong_dan} clean -fdx && python3 scripts/tdq_team.py sweep --clean"},
        ],
    },
    "rebase-hong": {
        "mo_ta": "the branch does not rebase onto the integration branch",
        "phuong_an": [
            {"mo_ta": "rebase it by hand inside the worktree and settle the conflict",
             "lenh": "git -C {duong_dan} rebase tdq/<slug>/tich-hop"},
            {"mo_ta": "see which files are in the way",
             "lenh": "python3 scripts/tdq_team.py resolve {ma_task}"},
        ],
    },
    "test-code": {
        "mo_ta": "the task's own test is red, so the branch may not merge",
        "phuong_an": [
            {"mo_ta": "fix the code in the worktree, then verify again",
             "lenh": "python3 scripts/tdq_team.py check {ma_task}"},
        ],
    },
    "test-plan": {
        "mo_ta": "the plan names no runnable command in the task's `Test:` line",
        "phuong_an": [
            {"mo_ta": "write the check as a command in backticks in the plan, then verify again",
             "lenh": "python3 scripts/tdq_team.py check {ma_task}"},
        ],
    },
    "xung-dot": {
        "mo_ta": "the branch conflicts with the integration branch",
        "phuong_an": [
            {"mo_ta": "resolve it inside the worktree, then probe again",
             "lenh": "python3 scripts/tdq_team.py check {ma_task}"},
            {"mo_ta": "drop the task branch and redo the task",
             "lenh": "git worktree remove --force {duong_dan} && git branch -D {nhanh}"},
        ],
    },
    "chua-merge": {
        "mo_ta": "the branch is not in the integration branch yet",
        "phuong_an": [
            {"mo_ta": "merge it in — this also cleans up when it lands",
             "lenh": "python3 scripts/tdq_team.py merge {ma_task}"},
        ],
    },
    "git-tu-choi": {
        "mo_ta": "git refused to remove this worktree — its own words are in brackets",
        "phuong_an": [
            {"mo_ta": "fix what git named there, then sweep again",
             "lenh": "python3 scripts/tdq_team.py sweep --clean"},
            {"mo_ta": "see what still holds the directory",
             "lenh": "git worktree list --porcelain && ls -la {duong_dan}"},
        ],
    },
    "khoa": {
        "mo_ta": "git has this worktree locked",
        "phuong_an": [
            {"mo_ta": "unlock it, then sweep again",
             "lenh": "git worktree unlock {duong_dan} && python3 scripts/tdq_team.py soat"},
        ],
    },
}


class LoiSo(Exception):
    """A ledger rule was broken. Never raised for a missing file — that is normal."""


def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: one ISO-timestamped line on stderr. Muted with TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{datetime.now().isoformat(timespec='seconds')}] worktree-so: {message}",
              file=sys.stderr)


def duong_so(project):
    return os.path.join(project, "docs", "tdq", "worktrees.json")


def duong_md(project):
    return os.path.join(project, "docs", "tdq", "worktrees.md")


def _so_rong():
    return {"schema_version": SCHEMA_VERSION, "dong": []}


def doc(project):
    """Read the ledger. A missing file is normal; a broken file yields an EMPTY ledger.

    Returning empty instead of raising is deliberate: the prompt hook reads this on every
    single turn, and a ledger someone hand-edited into invalid JSON must never be able to
    kill a turn. The broken file is left untouched on disk — see `_ghi`, which refuses to
    write over a file it could not parse.
    """
    duong = duong_so(project)
    if not os.path.exists(duong):
        return _so_rong()
    try:
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
    except (OSError, ValueError) as exc:
        _log(f"unreadable ledger, treating it as empty and leaving it alone: {exc}")
        return _so_rong()
    if not isinstance(du_lieu, dict) or not isinstance(du_lieu.get("dong"), list):
        _log("ledger has an unexpected shape, treating it as empty")
        return _so_rong()
    return du_lieu


def _doc_de_ghi(project):
    """Same read, but a broken file is an ERROR: writing on top of it would lose rows."""
    duong = duong_so(project)
    if not os.path.exists(duong):
        return _so_rong()
    try:
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
    except (OSError, ValueError) as exc:
        raise LoiSo(f"The ledger {duong} cannot be read ({exc}). Fix or delete it by hand "
                    f"— writing over it would drop every row it still holds.")
    if not isinstance(du_lieu, dict) or not isinstance(du_lieu.get("dong"), list):
        raise LoiSo(f"The ledger {duong} has an unexpected shape. Fix it by hand.")
    return du_lieu


def _ghi(project, du_lieu):
    duong = duong_so(project)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _khoa(ban_ghi):
    return (ban_ghi["slug"], ban_ghi["ma_task"])


def kiem_ghi_duoc(project):
    """Raise LoiSo when the ledger could not be written to right now.

    Callers use this BEFORE the irreversible step (creating a worktree): a row that
    cannot be written turns the thing it describes into an orphan nobody can find again.
    """
    _doc_de_ghi(project)


def mo_dong(project, slug, ma_task, nhanh, duong_dan, tao_luc=None):
    """Open a row. Called right after `git worktree add` reports success."""
    du_lieu = _doc_de_ghi(project)
    ban_ghi = {
        "slug": slug,
        "ma_task": ma_task,
        "nhanh": nhanh,
        "duong_dan": duong_dan,
        "tao_luc": tao_luc or datetime.now().isoformat(timespec="seconds"),
        "trang_thai": TRANG_THAI_MO,
        "dong_luc": None,
    }
    for cu in du_lieu["dong"]:
        if _khoa(cu) == _khoa(ban_ghi) and cu["trang_thai"] == TRANG_THAI_MO:
            raise LoiSo(f"{slug}/{ma_task} already has an open row in the ledger "
                        f"({cu['duong_dan']}). Close it before opening another.")
    du_lieu["dong"].append(ban_ghi)
    _ghi(project, du_lieu)
    _log(f"open {slug}/{ma_task} → {duong_dan}")
    return ban_ghi


def dong_dong(project, slug, ma_task, ly_do):
    """Close a row. `ly_do` says WHY it closed — merged, or the directory vanished."""
    du_lieu = _doc_de_ghi(project)
    for ban_ghi in du_lieu["dong"]:
        if _khoa(ban_ghi) == (slug, ma_task) and ban_ghi["trang_thai"] == TRANG_THAI_MO:
            ban_ghi["trang_thai"] = TRANG_THAI_DONG
            ban_ghi["dong_luc"] = datetime.now().isoformat(timespec="seconds")
            _ghi(project, du_lieu)
            _log(f"close {slug}/{ma_task} ({ly_do})")
            return ban_ghi
    return None


def dong_mo(project, slug=None):
    """Every row still open, optionally narrowed to one request."""
    return [d for d in doc(project)["dong"]
            if d.get("trang_thai") == TRANG_THAI_MO
            and (slug is None or d.get("slug") == slug)]


def _sap_xep(dong):
    """One stable order for rendering: newest first, then slug, then task code.

    Without this the `.md` reshuffles whenever a row is appended, and every diff of the
    file turns into noise nobody reads.
    """
    return sorted(dong, key=lambda d: (d.get("tao_luc") or "", d.get("slug") or "",
                                       d.get("ma_task") or ""), reverse=True)


def render_md(du_lieu):
    """The human-readable ledger. Same input → same bytes, always."""
    dong = _sap_xep(du_lieu.get("dong", []))
    mo = [d for d in dong if d.get("trang_thai") == TRANG_THAI_MO]
    # English, like its sibling `docs/tdq/STATE.md`: this is a GENERATED ledger, not a
    # document written for one request. It outlives the request that opened its rows, so
    # it has no single `doc_lang` to follow, and giving it one would mean a translation
    # table — the one thing the language rule rules out.
    ra = [
        "# TDQ WORKTREE LEDGER (generated — do not hand-edit)",
        "",
        "Source: `docs/tdq/worktrees.json` · written only by "
        "`scripts/tdq_worktree_registry.py`.",
        "Clean up with `python3 scripts/tdq_team.py sweep --clean`.",
        "",
        f"Open: **{len(mo)}** · rows in total: **{len(dong)}**",
        "",
        "| State | Request | Task | Branch | Path | Opened | Closed |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in dong:
        ra.append("| {trang_thai} | {slug} | {ma_task} | `{nhanh}` | `{duong_dan}` | "
                  "{tao_luc} | {dong_luc} |".format(
                      trang_thai=d.get("trang_thai", "?"),
                      slug=d.get("slug", "?"),
                      ma_task=d.get("ma_task", "?"),
                      nhanh=d.get("nhanh", "?"),
                      duong_dan=d.get("duong_dan", "?"),
                      tao_luc=d.get("tao_luc", "?"),
                      dong_luc=d.get("dong_luc") or "—"))
    if not dong:
        ra.append("| — | — | — | — | — | — | — |")
    ra.append("")
    return "\n".join(ra)


def ghi_md(project):
    duong = duong_md(project)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        f.write(render_md(doc(project)))
    return duong


def khoi_goi_y(muc):
    """The suggestion block for worktrees that cannot be cleaned up yet.

    `muc` is a list of dicts carrying ma_task / duong_dan / nhanh / ly_do (+ optional
    chi_tiet). A reason outside `LY_DO_CHAN` raises instead of printing an empty block:
    silence here is how a worktree gets forgotten, which is the exact failure this whole
    ledger exists to prevent.
    """
    if not muc:
        return ""
    ra = [f"NOT CLEANED UP YET: {len(muc)} worktree(s)"]
    for m in muc:
        ly_do = m.get("ly_do")
        if ly_do not in LY_DO_CHAN:
            raise LoiSo(f"Unknown blocking reason {ly_do!r}. The set is closed: "
                        f"{', '.join(sorted(LY_DO_CHAN))}. Add the reason together with "
                        f"its options, never print a block with no way out.")
        luat = LY_DO_CHAN[ly_do]
        chi_tiet = f" ({m['chi_tiet']})" if m.get("chi_tiet") else ""
        ra.append(f"  {m.get('ma_task', '?')}  {m.get('duong_dan', '?')}")
        ra.append(f"        reason: {luat['mo_ta']}{chi_tiet}")
        for pa in luat["phuong_an"]:
            lenh = pa["lenh"].format(duong_dan=m.get("duong_dan", ""),
                                     ma_task=m.get("ma_task", ""),
                                     nhanh=m.get("nhanh", ""))
            ra.append(f"        → {pa['mo_ta']}: {lenh}")
    return "\n".join(ra)
