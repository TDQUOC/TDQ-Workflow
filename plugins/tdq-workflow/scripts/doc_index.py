#!/usr/bin/env python3
"""doc_index.py — write a LINE index into long rule files so they can be read one section at a time.

Why this exists, measured 2026-10-02: the 38 files under `skills/**/references/` hold 65k tokens
and are 78% of what a lane-`full` request must read. Five of the heaviest use only 27-77% of their
own content for one typical use — the rest is a conditional section or infrastructure lore. The
files already carry a table of contents, but a table of contents gives a NAME, and `offset/limit`
needs a LINE. So the index exists to turn "read the whole file" into "read section 4".

The block is one compact HTML comment, not a table. A table of the same information costs ~230
tokens per file, and those tokens count against the 3,500-token cap the files have to respect —
an index that eats the budget it is trying to save is not a saving. The comment form also stays
invisible when the markdown is rendered, so a human reader sees no clutter.

Two commands:
    python3 scripts/doc_index.py --tat-ca        # write/refresh every long rule file
    python3 scripts/doc_index.py <file> [<file>] # one or more files

Exit: 0 finished (prints how many files changed) · 2 bad syntax · 3 a path does not exist.
Env: TDQ_LOG=0 silences the log.
"""
import argparse
import glob
import io
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import utf8_io  # noqa: E402,F401 — imported so stdout/stderr become UTF-8, like every entrypoint
MOC_MO = "<!-- muc-luc-dong:"
MOC_DONG = "-->"
# Only a file LONG ENOUGH needs an index: below this threshold, reading the whole file is cheaper
# than reading the index and then one section. Counted in LINES, not tokens, because this script
# has to run in CI where there is no tokenizer — and lines are good enough here, since the number
# only decides WHETHER a file needs an index, not a cap.
NGUONG_DONG = 90
# A DENSE file needs an index even with few lines: `bang-lech.md` is 51 lines and 2,111 tokens,
# because it is one tight table. The token threshold is read from `docs/tdq/token-budget.json` —
# a plain JSON file, NO tokenizer call, so this still runs in CI. No lock -> fall back to lines.
NGUONG_TOKEN = 2000
TRAN_KY_TU = 100
VUNG_LUAT = ("skills",)


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] doc_index: {message}",
              file=sys.stderr)


def _doc(duong):
    with io.open(duong, encoding="utf-8") as fh:
        return fh.read()


def _ghi(duong, noi_dung):
    with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(noi_dung)


def _bo_khoi(dong):
    """-> the lines with the old index block removed. Removed before counting, or the numbers
    would be measured over the block itself."""
    ra, trong_khoi = [], False
    for d in dong:
        if d.startswith(MOC_MO):
            trong_khoi = True
        if trong_khoi:
            if d.rstrip().endswith(MOC_DONG):
                trong_khoi = False
            continue
        ra.append(d)
    return ra


def _sach_ten(ten):
    """Strip HTML comments out of a section name before it goes into the index.

    Required, not tidying: the index block IS an HTML comment, so a section name carrying
    `<!-- i18n-allow: … -->` closes that very block early. Measured on `soul.md`: the heading of
    section 2 had a comment, and the index was cut right there — four later sections vanished and
    the tail leaked out as plain text in the middle of the document. `·` is replaced as well,
    because it is the separator of the block itself.
    """
    ten = re.sub(r"<!--.*?-->", "", ten)
    return ten.replace("-->", "").replace("·", "-").strip()


def quet_muc(dong):
    """-> [(section name, 1-based start line)] for every `##`/`###` OUTSIDE a code fence.

    Skipping the sections inside a fence is required, not a nicety: `plan-template.md` and
    `spec-template.md` each hold a whole markdown template inside a fence, and the hashes in
    there are not sections of the file — indexing them points very confidently at the wrong place.
    """
    ra, trong_fence = [], False
    for i, d in enumerate(dong, start=1):
        if d.lstrip().startswith("```"):
            trong_fence = not trong_fence
            continue
        if trong_fence:
            continue
        khop = re.match(r"^(#{2,3})\s+(.+?)\s*$", d)
        if khop:
            ra.append((_sach_ten(khop.group(2)), i))
    return ra


def _khoi_chu(muc, so_dong_khoi):
    """Build the index block; `so_dong_khoi` is the number of lines it will take, which offsets
    every number in it.

    Why the offset is needed: the block lives INSIDE the file, so inserting it pushes every
    section down by exactly its own line count. Computing the numbers first and inserting without
    the offset leaves every one of them wrong by the same amount — enough for the agent to read
    the wrong section while believing it read the right one.
    """
    phan = []
    for j, (ten, dau) in enumerate(muc):
        cuoi = (muc[j + 1][1] - 1 + so_dong_khoi) if j + 1 < len(muc) else 0
        dau += so_dong_khoi
        phan.append(f"{ten}={dau}-{cuoi}" if cuoi else f"{ten}={dau}")
    dong = [MOC_MO]
    hien = ""
    for p in phan:
        them = (hien + " · " + p) if hien else "  " + p
        if len(them) > TRAN_KY_TU - 2 and hien:
            # The separator has to sit at the END of a wrapped line. The first version broke the
            # line INSTEAD of writing `·`, so the last entry of one line glued itself to the first
            # entry of the next when read back — and the number read out belonged to the LATER
            # section. Short files never showed it; only a block long enough to wrap did.
            dong.append(hien + " ·")
            hien = "  " + p
        else:
            hien = them
    if hien:
        dong.append(hien)
    dong.append(MOC_DONG)
    return dong


def _dung_khoi(muc):
    """Build the block with the RIGHT line count — iterate until its length stops changing (4 max).

    The line count of the block depends on the numbers inside it, and those numbers depend on the
    line count of the block. The loop converges after a step or two; without it the number has to
    be guessed, and a wrong guess is a skewed index.
    """
    so = len(muc) + 2
    for _ in range(4):
        khoi = _khoi_chu(muc, so)
        if len(khoi) == so:
            return khoi
        so = len(khoi)
    return _khoi_chu(muc, so)


def _cho_chen(dong):
    """Where the block goes: RIGHT AFTER the frontmatter (if any) and after the `# ` title line.

    Accounting for frontmatter is required, not a nicety: a `SKILL.md` opens with the YAML `---`,
    so the first version inserted the block ABOVE the frontmatter and broke it — three skill-shape
    checks reported a missing frontmatter.
    """
    # Skip leading blank lines before asking about frontmatter: a misplaced block from an older
    # version left its own blank line behind, and that blank line pushed the frontmatter down —
    # the `SKILL.md` stopped starting with `---`, and the host stopped treating it as a skill.
    i = 0
    while i < len(dong) and not dong[i].strip():
        i += 1
    if i < len(dong) and dong[i].strip() == "---":
        # Scan for the closing marker from the line AFTER the opening one, not from line 1: an
        # older version set `i = 1` here, so a file starting with a blank line stopped the scan at
        # the OPENING marker and the block landed INSIDE the frontmatter — the very breakage this
        # function exists to prevent.
        j = i + 1
        while j < len(dong) and dong[j].strip() != "---":
            j += 1
        i = min(j + 1, len(dong))
    while i < len(dong) and not dong[i].strip():
        i += 1
    if i < len(dong) and dong[i].startswith("# "):
        i += 1
    return i


def ghi_chi_muc(duong):
    """Write or refresh one file's index block. -> True when the file content changed."""
    cu = _doc(duong)
    dong = _bo_khoi(cu.split("\n"))
    cho_tieu_de = _cho_chen(dong)
    if not quet_muc(dong):
        moi = "\n".join(dong)
        if moi != cu:
            _ghi(duong, moi)
            _log(f"{os.path.basename(duong)} · no sections · old block removed")
            return True
        return False
    # Normalise the shape BEFORE counting: drop every blank line right after the title. Without
    # this step every write adds one blank line — `_bo_khoi` removes the block but not the blank
    # line beside it, so the function stops being idempotent and the file grows a line per run.
    while len(dong) > cho_tieu_de and not dong[cho_tieu_de].strip():
        del dong[cho_tieu_de]
    muc = quet_muc(dong)
    # The inserted block takes `len(khoi)` lines PLUS one blank line after it, so every section
    # moves down one line more than `_dung_khoi` already accounts for.
    khoi = _dung_khoi([(t, d + 1) for t, d in muc])
    moi = "\n".join(dong[:cho_tieu_de] + khoi + [""] + dong[cho_tieu_de:])
    if moi == cu:
        return False
    _ghi(duong, moi)
    _log(f"{os.path.basename(duong)} · {len(muc)} section(s) · block {len(khoi)} line(s)")
    return True


def co_chi_muc(duong):
    return MOC_MO in _doc(duong)


def doc_chi_muc(duong):
    """-> {section name: (first line, last line)} read from the block; {} when there is none."""
    noi_dung = _doc(duong)
    if MOC_MO not in noi_dung:
        return {}
    than = noi_dung.split(MOC_MO, 1)[1].split(MOC_DONG, 1)[0]
    ra = {}
    for muc in than.replace("\n", " ").split("·"):
        muc = muc.strip()
        if "=" not in muc:
            continue
        ten, _, so = muc.rpartition("=")
        dau, _, cuoi = so.partition("-")
        try:
            ra[ten.strip()] = (int(dau), int(cuoi) if cuoi else 0)
        except ValueError:
            continue
    return ra


def chi_muc_con_dung(duong):
    """-> False when the index block no longer points at the right lines. No block counts as
    right."""
    khoi = doc_chi_muc(duong)
    if not khoi:
        return True
    dong = _doc(duong).split("\n")
    for ten, (dau, _cuoi) in khoi.items():
        if dau < 1 or dau > len(dong):
            return False
        # Compare SANITIZED names on both sides. The name in the block went through `_sach_ten`
        # (HTML comments gone, `·` turned into `-`), so comparing it against the RAW heading line
        # never matches: the check would report a skewed index forever, and the command it
        # suggests would fix nothing, because the block is correct.
        if ten not in _sach_ten(dong[dau - 1]):
            return False
    return True


def _token_da_do(goc):
    """-> {relative path: token} from the lock file; {} when there is no lock."""
    import token_budget
    return {rel: ban.get("token", 0) for rel, ban in token_budget.doc_khoa(goc).items()}


def file_can_chi_muc(goc=ROOT):
    """-> the rule files needing an index (long in lines, OR dense in tokens), sorted by path."""
    token = _token_da_do(goc)
    ra = []
    for vung in VUNG_LUAT:
        for duong in glob.glob(os.path.join(goc, vung, "**", "*.md"), recursive=True):
            than = _bo_khoi(_doc(duong).split("\n"))
            rel = os.path.relpath(duong, goc).replace(os.sep, "/")
            du_dai = len(than) >= NGUONG_DONG or token.get(rel, 0) >= NGUONG_TOKEN
            if du_dai and quet_muc(than):
                ra.append(duong)
    return sorted(ra)


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Write a line index into long rule files.")
    ap.add_argument("duong", nargs="*", help=".md file(s) to write; empty means use --tat-ca")
    ap.add_argument("--tat-ca", action="store_true", help="every long enough rule file in skills/")
    ap.add_argument("--kiem", action="store_true", help="check only, write nothing; exit 1 when skewed")
    return ap.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    if not args.duong and not args.tat_ca:
        print("doc_index.py: needs a path, or --tat-ca", file=sys.stderr)
        return 2
    ds = file_can_chi_muc() if args.tat_ca else list(args.duong)
    for d in ds:
        if not os.path.isfile(d):
            print(f"doc_index.py: no such file {d}", file=sys.stderr)
            return 3
    if args.kiem:
        lech = [d for d in ds if co_chi_muc(d) and not chi_muc_con_dung(d)]
        thieu = [d for d in ds if not co_chi_muc(d)]
        for d in lech:
            print(f"{d}: the line index is skewed — run `doc_index.py --tat-ca`")
        for d in thieu:
            print(f"{d}: no line index — run `doc_index.py --tat-ca`")
        return 1 if (lech or thieu) else 0
    doi = sum(1 for d in ds if ghi_chi_muc(d))
    print(f"doc_index: {doi}/{len(ds)} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
