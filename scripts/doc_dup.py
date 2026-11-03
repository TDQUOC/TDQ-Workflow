#!/usr/bin/env python3
"""doc_dup.py — find passages repeated across the documentation files an LLM reads.

Why this exists: the workflow's rules live in 44 markdown files. When the same paragraph is
written twice, both copies are loaded, both cost tokens, and the two copies drift apart with
no check catching it. Reading 44 files by eye does not produce a number that can be measured
again next month, so the duplication has to be found by a program.

How it works: every file is cut into "shingles" — `--min-dong` consecutive non-empty lines.
Two shingles with the same text are a hit; hits that continue each other are merged into one
block, so five repeated lines are reported as one 5-line block, not three 3-line blocks.

Normalisation before hashing is deliberately shallow: leading/trailing space is dropped and
runs of whitespace collapse to one space, but CASE IS KEPT. A rule written twice with a
different capital letter is a real difference worth seeing, and lowercasing everything makes
tables and code fences collide with each other.

Usage:
    python3 scripts/doc_dup.py --vung skills --vung agents --vung docs/claude-md-mau.md
    python3 scripts/doc_dup.py --vung skills --min-dong 5      # only longer blocks
    python3 scripts/doc_dup.py --vung skills --top 20          # 20 heaviest blocks
    python3 scripts/doc_dup.py --vung skills --quiet           # no progress log

Only `*.md` files are scanned; a `--vung` may be a directory (walked) or a single file.

Tokens are counted with the real tokenizer (`anthropic-tokenizer` in `.venv-tokens/`, the same
counter `skill_tokens.py` uses). Missing library → this script ERRORS with exit 3. It never
falls back to characters/4: this table decides what gets cut, and that estimate is most wrong
exactly on the repeated text it measures.

Log service: ISO timestamp, printed to **stderr**, on by default, turned off with `--quiet`
or `TDQ_DUP_LOG=0`. The table always goes to **stdout** so it can be piped.
Exit: 0 finished · 2 bad syntax · 3 the token-counting library is missing.
"""

import argparse
import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import tdq_state  # noqa: E402 — shares the log service (now_iso)
import skill_tokens  # noqa: E402 — shares the real token counter and its missing-library error

ThieuThuVienDem = skill_tokens.ThieuThuVienDem
EXIT_THIEU_THU_VIEN = 3
MIN_DONG_MAC_DINH = 3

_log_bat = True


def log(msg):
    """Progress line to stderr. Silent when the log service is off."""
    if _log_bat:
        print(f"[{tdq_state.now_iso()}] doc_dup: {msg}", file=sys.stderr)


def dem_token_loat(doan):
    """Count tokens for a batch of texts. Own function so a test can replace it."""
    try:
        dem = skill_tokens.nap_bo_dem()
    except ThieuThuVienDem:
        return skill_tokens.dem_qua_venv(doan)
    return [dem(t) for t in doan]


def thu_thap_file(vung):
    """Every `*.md` under the given areas, sorted, each path appearing once."""
    ra = []
    for muc in vung:
        if os.path.isfile(muc):
            if muc.endswith(".md"):
                ra.append(os.path.abspath(muc))
            continue
        for cha, _, ten_file in os.walk(muc):
            ra.extend(os.path.join(cha, t) for t in ten_file if t.endswith(".md"))
    return sorted(set(os.path.abspath(p) for p in ra))


def doc_dong(duong):
    """File → [(line number, normalised text, raw text)], blank lines dropped.

    The line number is the REAL one in the file, so a report line can be opened directly.
    """
    with open(duong, encoding="utf-8", errors="replace") as f:
        tho = f.read().splitlines()
    ra = []
    for so, dong in enumerate(tho, start=1):
        chuan = " ".join(dong.split())
        if chuan:
            ra.append((so, chuan, dong))
    return ra


def _bam_shingle(dong, min_dong):
    """[(index of the first line, the tuple of texts)] for every window of `min_dong` lines."""
    return [(i, tuple(d[1] for d in dong[i:i + min_dong]))
            for i in range(len(dong) - min_dong + 1)]


def _cap_tho(theo_file, min_dong):
    """Raw hits: every pair of positions sharing one shingle, before merging."""
    bang = {}
    for duong, dong in theo_file.items():
        for i, khoa in _bam_shingle(dong, min_dong):
            bang.setdefault(khoa, []).append((duong, i))
    ra = []
    for vi_tri in bang.values():
        if len(vi_tri) < 2:
            continue
        for (fa, ia), (fb, ib) in itertools.combinations(sorted(vi_tri), 2):
            # Two windows of the same file that overlap are one passage, not a repetition.
            if fa == fb and abs(ia - ib) < min_dong:
                continue
            ra.append((fa, ia, fb, ib))
    return sorted(set(ra))


def _gop_lien_ke(cap_tho, min_dong):
    """Merge hits that continue each other: five repeated lines = ONE 5-line block."""
    con_lai = set(cap_tho)
    khoi = []
    for fa, ia, fb, ib in cap_tho:
        if (fa, ia, fb, ib) not in con_lai:
            continue  # already swallowed by the block starting one line above
        so_dong = min_dong
        while (fa, ia + so_dong - min_dong + 1, fb, ib + so_dong - min_dong + 1) in con_lai:
            so_dong += 1
        khoi.append({"file_a": fa, "idx_a": ia, "file_b": fb, "idx_b": ib, "so_dong": so_dong})
        for buoc in range(so_dong - min_dong + 1):
            con_lai.discard((fa, ia + buoc, fb, ib + buoc))
    return khoi


def quet(vung, min_dong=MIN_DONG_MAC_DINH, dem_token=True):
    """Scan the areas and return the duplicate blocks, heaviest first.

    Each block: file_a, dong_a, file_b, dong_b, so_dong, token (None when dem_token is False).
    `dong_*` are real line numbers in the file, 1-based.
    """
    duong_file = thu_thap_file(vung)
    theo_file = {p: doc_dong(p) for p in duong_file}
    log(f"scanning {len(duong_file)} file(s), window {min_dong} line(s)")
    tho = _cap_tho(theo_file, min_dong)
    khoi = _gop_lien_ke(tho, min_dong)

    ra = []
    for k in khoi:
        dong_a = theo_file[k["file_a"]]
        ra.append({
            "file_a": k["file_a"],
            "dong_a": dong_a[k["idx_a"]][0],
            "file_b": k["file_b"],
            "dong_b": theo_file[k["file_b"]][k["idx_b"]][0],
            "so_dong": k["so_dong"],
            "token": None,
            "_van": "\n".join(d[2] for d in dong_a[k["idx_a"]:k["idx_a"] + k["so_dong"]]),
        })

    if dem_token and ra:
        for k, so in zip(ra, dem_token_loat([k["_van"] for k in ra])):
            k["token"] = so
    for k in ra:
        k.pop("_van")
    log(f"found {len(ra)} duplicate block(s)")
    return sorted(ra, key=lambda k: (-(k["token"] or 0), -k["so_dong"], k["file_a"]))


def _tuong_doi(duong):
    """Path relative to the repo root when it sits inside it — shorter to read in the table."""
    try:
        return os.path.relpath(duong, ROOT)
    except ValueError:
        return duong


def in_bang(khoi, top=None):
    """Print the result as a markdown table on stdout."""
    if not khoi:
        print("No duplicate block found in the scanned area.")
        return
    hien = khoi[:top] if top else khoi
    print("| file A | line | file B | line | lines | tokens |")
    print("|---|---|---|---|---|---|")
    for k in hien:
        token = "—" if k["token"] is None else f"{k['token']:,}".replace(",", ".")
        print(f"| `{_tuong_doi(k['file_a'])}` | {k['dong_a']} | `{_tuong_doi(k['file_b'])}` "
              f"| {k['dong_b']} | {k['so_dong']} | {token} |")
    tong = sum(k["token"] or 0 for k in khoi)
    print(f"\nTOTAL duplicated: {len(khoi)} block(s), {tong} token(s) in the second copy.")
    if top and len(khoi) > top:
        print(f"({len(khoi) - top} lighter block(s) not shown — raise --top to see them.)")


def cli(argv=None):
    """Command line layer: parse, validate, run, print. Returns the exit code."""
    global _log_bat
    bo = argparse.ArgumentParser(
        prog="doc_dup.py",
        description="Find passages repeated across markdown documentation files.")
    bo.add_argument("--vung", action="append", required=True, metavar="PATH",
                    help="a directory to walk or a single .md file; repeatable")
    bo.add_argument("--min-dong", type=int, default=MIN_DONG_MAC_DINH, metavar="N",
                    help=f"shortest block counted as a repetition (default {MIN_DONG_MAC_DINH})")
    bo.add_argument("--top", type=int, default=None, metavar="N",
                    help="show only the N heaviest blocks")
    bo.add_argument("--khong-dem-token", action="store_true",
                    help="skip token counting — faster, and needs no tokenizer")
    bo.add_argument("--quiet", action="store_true", help="turn the progress log off")
    tham = bo.parse_args(argv)

    if tham.min_dong < 1:
        bo.error("--min-dong must be 1 or more")
    if tham.top is not None and tham.top < 1:
        bo.error("--top must be 1 or more")
    for muc in tham.vung:
        if not os.path.exists(muc):
            bo.error(f"--vung points at something that does not exist: {muc}")

    _log_bat = not tham.quiet and os.environ.get("TDQ_DUP_LOG") != "0"
    try:
        khoi = quet(tham.vung, min_dong=tham.min_dong, dem_token=not tham.khong_dem_token)
    except ThieuThuVienDem as loi:
        print("doc_dup.py: the token-counting library `anthropic-tokenizer` is missing.\n"
              "This script is FORBIDDEN to estimate characters/4, so it stops here.\n"
              f"Install with: {loi}", file=sys.stderr)
        return EXIT_THIEU_THU_VIEN
    in_bang(khoi, top=tham.top)
    return 0


def main():
    sys.exit(cli())


if __name__ == "__main__":
    main()
