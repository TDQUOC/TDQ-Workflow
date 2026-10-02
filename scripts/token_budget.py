#!/usr/bin/env python3
"""token_budget.py — lock the measured token count of every rule file so CI can enforce the cap.

The problem. A token cap on `skills/**/*.md` only means something if somebody enforces it, and the
place that enforces it is `doc_lint` in CI — where this repo DELIBERATELY installs no outside tool,
so there is no tokenizer. And no substitute quantity is trustworthy enough: measured over 43
reference files (2026-10-02), tokens per line ranged 11.6-47.2 (a 4.1× spread) and bytes per token
2.20-3.98 (1.81×). A cap on lines or bytes either reddens a sparse file unfairly or lets a dense
one through.

The answer: separate MEASURING from CHECKING.
  * `sinh_khoa()` runs on a machine that HAS a tokenizer and writes `docs/tdq/token-budget.json` =
    `{path: {token, sha256}}`.
  * `kiem_khoa()` runs ANYWHERE: it compares the file's `sha256` against the record. A match means
    that token number still describes this exact content, so it can be compared to the cap. A
    mismatch means the measurement is stale — and it says exactly that, rather than guessing.

This is npm/pip's lockfile mechanism applied to tokens: the measured number is locked by a hash of
the thing that was measured.

    python3 scripts/token_budget.py            # regenerate the lock (needs a tokenizer)
    python3 scripts/token_budget.py --kiem     # check only, exit 1 on findings (no tokenizer)

Exit: 0 clean · 1 findings under `--kiem` · 2 bad syntax · 3 no token counter when generating.
Env: TDQ_LOG=0 turns the log off.
"""
import argparse
import glob
import hashlib
import io
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import utf8_io  # noqa: E402,F401 — imported so stdout/stderr become UTF-8

FILE_KHOA = os.path.join("docs", "tdq", "token-budget.json")
# The cap for one rule file. Settled 2026-10-02 by the user's choice: 3,500 NOW, not a cap relaxed
# to fit the current state. The three files that were over it (plan-template 5,067, quick-lane
# 4,356, team-mode 3,652) had their CONDITIONAL parts moved to a sibling file rather than squeezed
# — `soul.md` does not allow squeezing a law.
TRAN_TOKEN = 3500
# `references/` only. A `SKILL.md` body already has its OWN cap, counted in lines, in `doc_lint`
# (`SKILL_LINE_LIMITS`), and two caps over the same file are two numbers that have to be raised
# together on every edit — one of them would be forgotten.
VUNG = os.path.join("skills", "*", "references", "**", "*.md")


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}] token_budget: {message}",
              file=sys.stderr)


def _doc(duong):
    with io.open(duong, encoding="utf-8") as fh:
        return fh.read()


def sha_file(duong):
    """sha256 of the CONTENT with line endings normalised.

    Normalising `\\r\\n` to `\\n` is required, not over-caution: Windows can hand the file back with
    CRLF once git touches it, and a lock that breaks over a line ending teaches people to switch
    the check off. The token count does not change with the line ending either.
    """
    return hashlib.sha256(_doc(duong).replace("\r\n", "\n").encode("utf-8")).hexdigest()


def file_luat(goc=ROOT):
    """-> every rule file's path, relative and with `/`, sorted by name."""
    ra = []
    for duong in glob.glob(os.path.join(goc, VUNG), recursive=True):
        ra.append(os.path.relpath(duong, goc).replace(os.sep, "/"))
    return sorted(ra)


def doc_khoa(goc=ROOT):
    """-> the lock's content; {} when there is none. A corrupt lock also yields {} — the check
    is what says so."""
    duong = os.path.join(goc, FILE_KHOA)
    if not os.path.isfile(duong):
        return {}
    try:
        return json.loads(_doc(duong))
    except ValueError:
        return {}


def sinh_khoa(goc=ROOT):
    """Measure every rule file and write the lock. -> number of records. Needs a real counter.

    Counts in ONE BATCH through the venv when the running python lacks the library, rather than
    `execv`-ing into the venv: a test calling this function in-process would have its own test
    runner replaced by that `execv` (the lesson is recorded in `skill_tokens.nap_bo_dem`). The cost
    is in starting the process, so one batch is enough.
    """
    import skill_tokens
    rels = file_luat(goc)
    duong_file = [os.path.join(goc, r.replace("/", os.sep)) for r in rels]
    van = [_doc(d) for d in duong_file]
    try:
        dem = skill_tokens.nap_bo_dem()
        so = [dem(v) for v in van]
    except skill_tokens.ThieuThuVienDem:
        so = skill_tokens.dem_qua_venv(van)
    ban = {rel: {"token": tk, "sha256": sha_file(d)}
           for rel, d, tk in zip(rels, duong_file, so)}
    duong_khoa = os.path.join(goc, FILE_KHOA)
    os.makedirs(os.path.dirname(duong_khoa), exist_ok=True)
    with io.open(duong_khoa, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(ban, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    _log(f"{len(ban)} file · cap {TRAN_TOKEN} · {FILE_KHOA}")
    return len(ban)


def kiem_khoa(goc=ROOT):
    """-> the list of findings. Uses NO tokenizer: it reads the lock and compares sha256.

    Three failures, three different sentences — merging them into one "bad lock" line would force
    the reader to guess what they have to do: regenerate the lock, or cut the file.
    """
    if not os.path.isfile(os.path.join(goc, FILE_KHOA)):
        # Never having generated a lock is not the rule file's fault. An EMPTY lock is different:
        # somebody did generate it, and every file is missing its record — that has to be said.
        return []
    khoa = doc_khoa(goc)
    loi = []
    for rel in file_luat(goc):
        duong = os.path.join(goc, rel.replace("/", os.sep))
        ban = khoa.get(rel)
        if ban is None:
            loi.append(f"{rel}: no record in the token lock — run `token_budget.py`")
            continue
        if ban.get("sha256") != sha_file(duong):
            loi.append(f"{rel}: the token measurement is stale (sha256 differs) — run `token_budget.py`")
            continue
        if ban.get("token", 0) > TRAN_TOKEN:
            loi.append(f"{rel}: {ban['token']} tokens > the cap of {TRAN_TOKEN} — "
                       "move the CONDITIONAL part to a sibling file, do not squeeze the law")
    return loi


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Lock each rule file's token count so CI can enforce "
                                             "the cap.")
    ap.add_argument("--kiem", action="store_true", help="check only, write nothing; exit 1 on "
                                                        "findings")
    ap.add_argument("--goc", default=ROOT, help="the repo root (default: this repo)")
    return ap.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    if args.kiem:
        loi = kiem_khoa(args.goc)
        for d in loi:
            print(d)
        return 1 if loi else 0
    import skill_tokens
    try:
        sinh_khoa(args.goc)
    except skill_tokens.ThieuThuVienDem:
        print("token_budget.py: no token counter — see `scripts/skill_tokens.py` to install one",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
