#!/usr/bin/env python3
"""Mind-map files of the TDQ workflow — one living diagram per feature.

A diagram is the outline a feature gets approved against, and `docs/tdq/mind-map/
<feature>.md` is that feature's single living copy: many requests edit it in turn,
so nothing here ever overwrites an existing file.

The constants of "the file shape" section below ARE the shared contract. Every later
command (kiem, doi-chieu, lien-he, xem) and the HTML renderer import them instead of
growing a regex of their own — one shape written once, so the tools cannot drift apart.

Usage:
    python3 scripts/tdq_mindmap.py sinh <feature-slug>

Exit codes: 0 done · 1 violation found · 2 bad argument or unwritable path ·
3 the feature already has a diagram (update mode — the file is left untouched).
Env: TDQ_PROJECT_DIR anchors the project (default: the git root, else the cwd) ·
TDQ_LOG=0 turns the log service off (on by default, one ISO-timestamped line to stderr).
"""
import argparse
import os
import re
import sys
from datetime import datetime

# ------------------------------------------------------------------- exit codes
EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_SYNTAX = 2          # a bad argument, or a path that cannot be read/written
EXIT_UPDATE = 3          # the feature already exists: update mode, nothing written

# --------------------------------------------------------------- the file shape
# Where a feature's living diagram lives, relative to the project root.
MIND_MAP_DIR_REL = os.path.join("docs", "tdq", "mind-map")
FILE_SUFFIX = ".md"

# A feature is addressed by a slug: kebab-case, ASCII only. It doubles as the file
# name, so the shape below also keeps `..` and separators out of the path.
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Line 1 of every diagram: `# <feature name>`.
TITLE_PREFIX = "# "
TITLE_LINE_RE = re.compile(r"^#\s+(?P<title>\S.*?)\s*$")

# Exactly one branch line, mandatory: `@nhánh: <top branch> > <sub branch>`.  # i18n-allow
BRANCH_KEY = "@nhánh"  # i18n-allow — document syntax, stays Vietnamese on purpose
BRANCH_SEP = ">"
BRANCH_LINE_RE = re.compile(
    r"^@nhánh:\s*(?P<top>[^>]*\S)\s*>\s*(?P<sub>\S.*?)\s*$")  # i18n-allow

# Optional, repeatable: `@phụ-thuộc: <feature-slug> · <reason>`.  # i18n-allow
DEPENDS_KEY = "@phụ-thuộc"  # i18n-allow — document syntax, stays Vietnamese
FIELD_SEP = "·"
DEPENDS_LINE_RE = re.compile(
    r"^@phụ-thuộc:\s*(?P<feature>[a-z0-9-]+)\s*·\s*(?P<reason>\S.*?)\s*$")  # i18n-allow

# A step: `B<n> · <description> (<file>::<function>)`; `!` right after the number
# marks the error branch of that step. The location is optional at parse time so a
# half-written line is still recognised as a step and reported as one, not as prose.
STEP_LINE_RE = re.compile(
    r"^B(?P<num>\d+)(?P<error>!?)\s*·\s*(?P<desc>\S.*?)"
    r"(?:\s*\((?P<location>[^()]*)\))?\s*$")
STEP_ERROR_MARK = "!"

# Inside the parentheses: `<file>::<function>`, or `?` while the code is unknown.
LOCATION_RE = re.compile(r"^(?P<file>[^\s:]+)::(?P<func>\S+)$")
UNKNOWN_LOCATION = "?"

# The blank file a brand-new feature starts from. Written for the human who fills it
# in, hence Vietnamese; every placeholder sits in [square brackets] so a half-filled
# file is obvious at a glance.
NEW_FILE_TEMPLATE = (
    "# {title}\n"
    "@nhánh: [nhánh tổng] > [nhánh con]\n"  # i18n-allow — user-facing template
    "\n"
    "<!-- Sửa dòng tiêu đề thành tên feature có dấu, thay mọi [ngoặc vuông] bằng nội\n"  # i18n-allow
    "     dung thật, rồi xoá đúng dòng chú thích này.\n"  # i18n-allow
    "     Bước thường: `B1 · mô tả (file::hàm)` — chưa biết code thì để `(?)`.\n"  # i18n-allow
    "     Nhánh lỗi:   `B1! · mô tả (file::hàm)`.\n"  # i18n-allow
    "     Phụ thuộc feature khác: thêm dòng `@phụ-thuộc: slug-feature · lý do một câu`. -->\n"  # i18n-allow
    "\n"
    "B1 · [mô tả bước đầu tiên] (?)\n"  # i18n-allow — user-facing template
)

# What the caller shows the user when the feature already has a diagram. The sentence
# is fixed so every request presents an update the same way (spec §3).
UPDATE_PREFACE = (
    "Feature `{feature}` đã có sơ đồ rồi. "  # i18n-allow — sentence shown to the user
    "Sau cập nhật của request này nó sẽ thành như sau:")  # i18n-allow


# ------------------------------------------------------------------ log service
def log_enabled():
    """The log service is on by default; TDQ_LOG=0 is the config switch."""
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: one ISO-timestamped line to stderr. Silenced by TDQ_LOG=0.

    On stderr, not stdout: stdout carries the diagram content this tool hands to its
    caller, and mixing the log into it would corrupt what the caller reads back.
    """
    if log_enabled():
        print(f"[{datetime.now().isoformat(timespec='seconds')}] tdq_mindmap: {message}",
              file=sys.stderr)


# ------------------------------------------------------------------ path anchors
def project_dir():
    """Anchor on the project: TDQ_PROJECT_DIR > git root > cwd."""
    env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = current = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return start
        current = parent


def mind_map_dir(root=None):
    """Absolute path of the diagram directory of a project."""
    return os.path.join(root or project_dir(), MIND_MAP_DIR_REL)


def feature_rel_path(feature):
    """Project-relative path of one feature's diagram."""
    return os.path.join(MIND_MAP_DIR_REL, feature + FILE_SUFFIX)


def feature_path(feature, root=None):
    """Absolute path of one feature's diagram."""
    return os.path.join(root or project_dir(), feature_rel_path(feature))


def valid_slug(feature):
    """True when the feature name is a usable slug (and thus a usable file name)."""
    return bool(feature) and SLUG_RE.match(feature) is not None


def default_title(feature):
    """First guess at the title line: the slug, spaced out, first letter raised."""
    words = feature.replace("-", " ")
    return words[:1].upper() + words[1:]


# ---------------------------------------------------------------- command: sinh
def cmd_sinh(args):
    """Create the diagram of a feature, or hand back the one it already has.

    Never overwrites: the existing file is the living copy of that feature, and a
    request that silently replaced it would destroy work approved earlier.
    """
    feature = args.feature
    if not valid_slug(feature):
        _log(f"sinh: rejected slug {feature!r}")
        print(f"sinh: {feature!r} is not a valid feature slug — expected kebab-case "
              f"ASCII matching {SLUG_RE.pattern}", file=sys.stderr)
        return EXIT_SYNTAX

    path = feature_path(feature)
    rel = feature_rel_path(feature)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                current = f.read()
        except OSError as exc:
            _log(f"sinh: cannot read {rel} ({exc})")
            print(f"sinh: cannot read {rel} ({exc})", file=sys.stderr)
            return EXIT_SYNTAX
        _log(f"sinh: {rel} already exists ({len(current.splitlines())} line(s)) "
             f"— update mode, nothing written")
        print(UPDATE_PREFACE.format(feature=feature))
        print()
        print(current, end="" if current.endswith("\n") else "\n")
        return EXIT_UPDATE

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(NEW_FILE_TEMPLATE.format(title=default_title(feature)))
    except OSError as exc:
        _log(f"sinh: cannot write {rel} ({exc})")
        print(f"sinh: cannot write {rel} ({exc})", file=sys.stderr)
        return EXIT_SYNTAX

    _log(f"sinh: created {rel} from the blank template")
    print(f"sinh: created {rel} — fill in the placeholders, then get it approved")
    return EXIT_OK


# ------------------------------------------------------------------------- CLI
def build_parser():
    """The CLI surface. Later commands (kiem, doi-chieu, lien-he, xem) plug in here."""
    parser = argparse.ArgumentParser(
        prog="tdq_mindmap.py",
        description="Mind-map files of the TDQ workflow: one living diagram per feature.")
    subs = parser.add_subparsers(dest="lenh", required=True)

    sinh = subs.add_parser(
        "sinh", help="create the diagram of a feature, or open the existing one")
    sinh.add_argument("feature", help="feature slug, kebab-case ASCII (e.g. dang-nhap)")
    sinh.set_defaults(handler=cmd_sinh)

    return parser


def main(argv):
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
