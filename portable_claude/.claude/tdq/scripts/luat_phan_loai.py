#!/usr/bin/env python3
"""Suggest a label for each rule anchor: `ly-luan` or `user-facing`.

Precondition (a) of direction A. The workflow may be written in English only in the
REASONING RULE part; the USER-FACING TEMPLATE part (lines printed to chat, report
templates, few-shot examples) must stay Vietnamese. This script does NOT decide — it
suggests so a human reviews faster, and the final word lives in
`docs/tdq/audit/ranh-gioi-luat.md`, settled by a person.
Usage:
    python3 scripts/luat_phan_loai.py --bang docs/tdq/audit/luat-hien-co.md

Prints a markdown table on stdout: `| code | source | suggested label | why |`.
Env: TDQ_LOG=0 mutes the log service (on by default, ISO timestamps on stderr).
"""
import argparse
import collections
import os
import re
import sys
from datetime import datetime

Goi = collections.namedtuple("Goi", "nhan ly_do")
Dong = collections.namedtuple("Dong", "nhan chu")

LY_LUAN = "ly-luan"
USER_FACING = "user-facing"

# Anchor table: `| L001 | `file:line` | anchor text |`. The same shape tests/test_luat_skill.py
# reads — changing it in one place forces the other, so keep it as is.
DONG_BANG = re.compile(r"^\| (L\d+) \| `([^`:]+):(\d+)` \|")
# Cells are split on `|` WITHOUT unescaping: rule text may carry a markdown `\|`.
# The table has a fourth column `neo bản mới` (empty until the rule is rewritten); the  # i18n-allow
# classifier only needs the content column, but must still split cells properly instead
# of reaching to the last `|` of the line.
O_BANG = re.compile(r"(?<!\\)\|")
DONG_RANH_GIOI = re.compile(r"^\| (L\d+) \| ([\w-]+) \| (.*?) \|$")

# Files whose WHOLE content is a template the user reads: changing a word there changes
# what the user sees.
FILE_KHUON = ("-template.md", "user-facing-block.md", "interview.md",
              "lane-decision.md", "scope-round.md")

# Signs inside the rule sentence itself. Each sign carries a reason so the suggestion
# table can be read, instead of a bare label leaving the reviewer to guess the machine.
DAU_HIEU = (
    (re.compile(r"➤"), "carries the symbol of the approval block the user sees"),  # i18n-allow
    (re.compile(r"\bin ra chat\b", re.I), "says outright it is printed to chat"),  # i18n-allow
    (re.compile(r"\bin đúng dòng\b", re.I), "orders one line printed verbatim"),  # i18n-allow
    (re.compile(r"\bnhắn\b", re.I), "describes the sentence the user replies with"),  # i18n-allow
    (re.compile(r"\bkhuôn\b", re.I), "talks about a text template"),  # i18n-allow
    (re.compile(r"\boption\b", re.I), "talks about the options of a question"),  # i18n-allow
    (re.compile(r"\bcâu hỏi\b", re.I), "talks about a question for the user"),  # i18n-allow
    (re.compile(r"\btrình bày\b", re.I), "talks about how it is presented to the user"),  # i18n-allow
    (re.compile(r"\bnguyên văn\b", re.I), "demands the wording be kept verbatim"),  # i18n-allow
    (re.compile(r"\buser thấy\b", re.I), "talks about what the user sees"),  # i18n-allow
    (re.compile(r"\btiếng Việt\b", re.I), "declares the output language"),  # i18n-allow
)


def _log(message):
    """Log service: one ISO-timestamped line on stderr. Muted with TDQ_LOG=0.

    On stderr because stdout is a machine-read table — mixing the log in breaks that contract.
    """
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().isoformat(timespec='seconds')}] luat_phan_loai: {message}",
              file=sys.stderr)


def doc_bang(path):
    """Anchor table → [(code, path, line number, anchor text)] in file order."""
    ban = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = DONG_BANG.match(line.rstrip("\n"))
            if m:
                o = O_BANG.split(line.rstrip("\n").strip())[1:-1]
                ban.append((m.group(1), m.group(2), int(m.group(3)), o[2].strip()))
    return ban


def doc_ranh_gioi(path):
    """The table a reviewer settled → {code: Dong(label, text)}."""
    ban = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = DONG_RANH_GIOI.match(line.rstrip("\n"))
            if m and m.group(2) in (LY_LUAN, USER_FACING):
                ban[m.group(1)] = Dong(m.group(2), m.group(3).strip())
    return ban


def liet_ke_ma(path):
    """The list of codes in file order, KEEPING duplicates.

    `doc_ranh_gioi` returns a dict, so a duplicate line is silently overwritten; catching
    duplicates has to happen on this raw list.
    """
    thu = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = DONG_RANH_GIOI.match(line.rstrip("\n"))
            if m and m.group(2) in (LY_LUAN, USER_FACING):
                thu.append(m.group(1))
    return thu


def goi_y_nhan(duong_dan, chu, trong_khoi_ma=False):
    """The suggested label for one anchor, with its reason.

    The order runs from the SUREST sign to the softest: inside a skill code block → it is a
    copyable template; inside a template file → the whole file is a template; otherwise read
    the sentence itself. No sign matching means a reasoning rule by default, that being the
    majority — but the reason is still recorded so the reviewer sees what the machine used.
    """
    if trong_khoi_ma:
        return Goi(USER_FACING, "inside a code block — a copyable template")
    ten = os.path.basename(duong_dan)
    for duoi in FILE_KHUON:
        if ten.endswith(duoi):
            return Goi(USER_FACING, f"the whole file `{ten}` is a user template")
    for mau, ly_do in DAU_HIEU:
        if mau.search(chu):
            return Goi(USER_FACING, ly_do)
    return Goi(LY_LUAN, "no user-facing sign in the sentence")


def bang_nhap(ban):
    """[(code, path, line, text)] → the markdown lines of the draft table."""
    ra = ["| Mã | Nguồn | Nhãn gợi ý | Vì sao |", "|---|---|---|---|"]  # i18n-allow
    for ma, duong_dan, dong, chu in ban:
        goi = goi_y_nhan(duong_dan, chu)
        ra.append(f"| {ma} | `{duong_dan}:{dong}` | {goi.nhan} | {goi.ly_do} |")
    return ra


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bang", required=True, help="path to the anchor table")
    args = parser.parse_args(argv)
    _log(f"reading the anchor table: {args.bang}")
    ban = doc_bang(args.bang)
    _log(f"read {len(ban)} anchor(s)")
    dong = bang_nhap(ban)
    print("\n".join(dong))
    so_uf = sum(1 for d in dong if f"| {USER_FACING} |" in d)
    _log(f"suggestion: {so_uf} user-facing, {len(ban) - so_uf} ly-luan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
