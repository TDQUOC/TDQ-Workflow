#!/usr/bin/env python3
"""Scan the non-ASCII symbols in the files that hold the blocks spoken to the user.

Why it exists: before tightening `tests/test_user_facing_block.py` into a symbol whitelist, we
must know which characters the 12 files in scope actually use. Tightening blind would turn the
test red over a legitimate character that was already there (spec §5, risk 2).

Only characters in Unicode category P* (punctuation) and S* (symbols) outside ASCII are counted.
Accented letters are category L* so they are never touched — that is what makes a whitelist viable.

Usage:
        python3 scripts/scan_block_symbols.py              # markdown table, exit 0
        python3 scripts/scan_block_symbols.py --lieu-ke    # add a per-file count column
        python3 scripts/scan_block_symbols.py --chi-khoi   # only what is printed to the user
"""
import argparse
import os
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Whitelist settled at T0.2 (see `docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md`): six characters,
# each with evidence of really running in a sample block printed to the user. The first three were
# picked by the user at interview round 2; the last three were admitted under rule 2A (evidence of
# really running). The character `▸` was rejected because grepping the whole repo returns 0 hits.
WHITELIST = ("➤", "·", "—", "→", "–", "…")

# The 12 files holding a template or copying a sample block — the scope the whitelist will cover.
SCOPE = (
    "skills/tdq-conventions/references/user-facing-block.md",
    "skills/tdq-spec/SKILL.md",
    "skills/tdq-plan/SKILL.md",
    "skills/tdq-plan/references/mode-gate.md",
    "skills/tdq-intake/references/lane-decision.md",
    "skills/tdq-intake/references/quick-lane.md",
    "skills/tdq-intake/references/interview.md",
    "skills/tdq-build/references/report-template.md",
    "skills/tdq-status/SKILL.md",
    "portable/workflow/02-spec.md",
    "portable/workflow/03-plan.md",
    "portable/workflow/references/user-facing-block.md",
)


def la_ky_hieu(ch):
    """True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern."""
    if ord(ch) < 128:
        return False
    return unicodedata.category(ch)[0] in ("P", "S")


def khoi_mau(text):
    """The content of the ``` blocks in a file — this is what is REALLY printed to the user.

    Prose guidance around a block never reaches the user's eyes, so the whitelist ignores it.
    """
    ra, trong_khoi = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            trong_khoi = not trong_khoi
            continue
        if trong_khoi:
            ra.append(line)
    return "\n".join(ra)


def quet(paths, chi_khoi=False):
    """{character: (total count, {file: count})} for every non-ASCII symbol."""
    tong = Counter()
    theo_file = defaultdict(Counter)
    for rel in paths:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print(f"WARNING: missing file {rel}", file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if chi_khoi:
            text = khoi_mau(text)
        for ch in text:
            if la_ky_hieu(ch):
                tong[ch] += 1
                theo_file[ch][rel] += 1
    return tong, theo_file


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lieu-ke", action="store_true",
                    help="add a column listing the files using that character")
    ap.add_argument("--chi-khoi", action="store_true",
                    help="scan only the content of ``` blocks (what is really printed to the user)")
    args = ap.parse_args(argv)

    tong, theo_file = quet(SCOPE, chi_khoi=args.chi_khoi)
    print(f"| Char | Codepoint | Unicode name | Count | In whitelist? |"
          + (" File |" if args.lieu_ke else ""))
    print("|---|---|---|---|---|" + ("---|" if args.lieu_ke else ""))
    for ch, n in sorted(tong.items(), key=lambda kv: (-kv[1], ord(kv[0]))):
        ten = unicodedata.name(ch, "?")
        trong = "YES" if ch in WHITELIST else "**NO**"
        dong = f"| `{ch}` | U+{ord(ch):04X} | {ten} | {n} | {trong} |"
        if args.lieu_ke:
            dong += " " + ", ".join(sorted(theo_file[ch])) + " |"
        print(dong)

    la = [ch for ch in tong if ch not in WHITELIST]
    print()
    print(f"Total: {len(tong)} distinct symbol(s) across {len(SCOPE)} file(s) · "
          f"{len(la)} character(s) OUTSIDE the whitelist need a decision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
