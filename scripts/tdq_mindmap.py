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
    python3 scripts/tdq_mindmap.py kiem <file>

Exit codes: 0 done · 1 violation found · 2 bad argument or unreadable/unwritable path ·
3 the feature already has a diagram (update mode — the file is left untouched).
Env: TDQ_PROJECT_DIR anchors the project (default: the git root, else the cwd) ·
TDQ_LOG=0 turns the log service off (on by default, one ISO-timestamped line to stderr).
"""
import argparse
import collections
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


# A line that opens with `B<digits>` is MEANT to be a step even when the rest of it is
# wrong. Without this hint a broken step would read as prose and slip through unnoticed,
# which is the one failure mode a shape checker must not have.
STEP_HINT_RE = re.compile(r"^B\d+")

# An HTML comment block is guidance for the human filling the file in, not content: the
# blank template ships one, so its example lines must never count as real declarations.
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"

# ------------------------------------------------------------------- rule codes
# One code per KIND of breakage, all sharing a prefix. They are constants because
# doc_lint.py imports them for the mind-map lint rule instead of re-running this CLI,
# so a code is a name two modules agree on, never a literal typed twice.
RULE_PREFIX = "SD"
RULE_TITLE_MISSING = "SD1"       # no `# <feature name>` as the first content line
RULE_BRANCH_MISSING = "SD2"      # no usable branch line at all
RULE_BRANCH_DUPLICATE = "SD3"    # more than one branch line
RULE_BRANCH_SYNTAX = "SD4"       # a branch line that does not match the shape
RULE_DEPENDS_SYNTAX = "SD5"      # a depends line that does not match the shape
RULE_STEP_SYNTAX = "SD6"         # a step line (or its location) that misses the shape
RULE_STEP_ORDER = "SD7"          # step numbers that jump, repeat, or dangle
ALL_RULES = (RULE_TITLE_MISSING, RULE_BRANCH_MISSING, RULE_BRANCH_DUPLICATE,
             RULE_BRANCH_SYNTAX, RULE_DEPENDS_SYNTAX, RULE_STEP_SYNTAX, RULE_STEP_ORDER)

# Same report shape as doc_lint.py, so one pair of eyes reads both tools' output.
VIOLATION_FORMAT = "{path}:{line}: [{rule}] {message}"


class Violation(collections.namedtuple("Violation", "path line rule message")):
    """One broken rule, at one 1-based line. `str()` renders the report line."""

    __slots__ = ()

    def __str__(self):
        return VIOLATION_FORMAT.format(
            path=self.path, line=self.line, rule=self.rule, message=self.message)


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


# ------------------------------------------------------------- command: kiem
def comment_mask(lines):
    """True for every line that sits inside (or opens) an HTML comment block."""
    mask = []
    inside = False
    for line in lines:
        opens = COMMENT_OPEN in line
        closes = COMMENT_CLOSE in line
        mask.append(inside or opens)
        if closes:
            inside = False
        elif opens:
            inside = True
    return mask


def _check_title(lines, mask, path):
    """The first content line must be the title; anything else loses the feature name."""
    for i, line in enumerate(lines):
        if mask[i] or not line.strip():
            continue
        if TITLE_LINE_RE.match(line):
            return []
        return [Violation(path, i + 1, RULE_TITLE_MISSING,
                          f'the first content line must be the title '
                          f'"{TITLE_PREFIX}<feature name>"')]
    return [Violation(path, 1, RULE_TITLE_MISSING,
                      f'missing the title line "{TITLE_PREFIX}<feature name>"')]


def _check_branch(lines, mask, path):
    """Exactly one branch line: none leaves the feature unplaced, two place it twice."""
    out = []
    good = []
    for i, line in enumerate(lines):
        if mask[i] or not line.startswith(BRANCH_KEY + ":"):
            continue
        if BRANCH_LINE_RE.match(line):
            good.append(i)
        else:
            out.append(Violation(
                path, i + 1, RULE_BRANCH_SYNTAX,
                f'malformed branch line — expected '
                f'"{BRANCH_KEY}: <top branch> {BRANCH_SEP} <sub branch>"'))
    if not good:
        # Reported at line 1: the file as a whole lacks the line, and a malformed
        # attempt already has its own violation at the line where it sits.
        out.append(Violation(
            path, 1, RULE_BRANCH_MISSING,
            f'missing the mandatory line "{BRANCH_KEY}: <top branch> '
            f'{BRANCH_SEP} <sub branch>"'))
    for extra in good[1:]:
        out.append(Violation(path, extra + 1, RULE_BRANCH_DUPLICATE,
                             f'a second "{BRANCH_KEY}:" line — exactly one is allowed'))
    return out


def _check_depends(lines, mask, path):
    """Every depends line needs both halves: which feature, and why."""
    out = []
    for i, line in enumerate(lines):
        if mask[i] or not line.startswith(DEPENDS_KEY + ":"):
            continue
        if not DEPENDS_LINE_RE.match(line):
            out.append(Violation(
                path, i + 1, RULE_DEPENDS_SYNTAX,
                f'malformed depends line — expected "{DEPENDS_KEY}: <feature-slug> '
                f'{FIELD_SEP} <one-sentence reason>"'))
    return out


def _check_steps(lines, mask, path):
    """Steps must keep their shape, carry a location, and be numbered 1, 2, 3…"""
    out = []
    steps = []
    for i, line in enumerate(lines):
        if mask[i] or not STEP_HINT_RE.match(line):
            continue
        found = STEP_LINE_RE.match(line)
        if not found:
            out.append(Violation(
                path, i + 1, RULE_STEP_SYNTAX,
                f'malformed step line — expected "B<n> {FIELD_SEP} <description> '
                f'(<file>::<function>)"'))
            continue
        location = found.group("location")
        if location != UNKNOWN_LOCATION and (
                location is None or not LOCATION_RE.match(location)):
            out.append(Violation(
                path, i + 1, RULE_STEP_SYNTAX,
                f'step B{found.group("num")} has no usable location — expected '
                f'"(<file>::<function>)", or "({UNKNOWN_LOCATION})" while the code '
                f'is unknown'))
        steps.append((i, int(found.group("num")),
                      found.group("error") == STEP_ERROR_MARK))

    expected = 1
    main_numbers = {num for _, num, is_error in steps if not is_error}
    for i, num, is_error in steps:
        if is_error:
            if num not in main_numbers:
                out.append(Violation(
                    path, i + 1, RULE_STEP_ORDER,
                    f'error branch B{num}{STEP_ERROR_MARK} has no step B{num} to branch from'))
            continue
        if num != expected:
            out.append(Violation(
                path, i + 1, RULE_STEP_ORDER,
                f'step B{num} breaks the numbering — expected B{expected}'))
        expected = num + 1
    return out


def check_diagram(lines, path):
    """Every shape violation of one diagram, in line order. Pure: no I/O, no exit.

    Kept apart from printing and from the exit code on purpose: doc_lint.py imports
    THIS function for its mind-map rule, so the two tools cannot disagree about what
    a valid diagram is — there is only one answer, and it lives here.
    """
    lines = list(lines)
    mask = comment_mask(lines)
    out = (_check_title(lines, mask, path)
           + _check_branch(lines, mask, path)
           + _check_depends(lines, mask, path)
           + _check_steps(lines, mask, path))
    return sorted(out, key=lambda v: (v.line, v.rule))


def read_diagram(path):
    """The lines of a diagram file, or None when it cannot be read."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return None


def cmd_kiem(args):
    """Check one diagram file against the shape and report every violation."""
    path = args.file
    lines = read_diagram(path)
    if lines is None:
        _log(f"kiem: cannot read {path}")
        print(f"kiem: cannot read {path}", file=sys.stderr)
        return EXIT_SYNTAX

    violations = check_diagram(lines, path)
    for violation in violations:
        print(violation)
    _log(f"kiem: {path} — {len(lines)} line(s), {len(violations)} violation(s)")
    return EXIT_VIOLATION if violations else EXIT_OK


# ---------------------------------------------------------- command: lien-he
def extract_depends(lines):
    """The feature slugs one diagram's depends lines point to, in file order.

    Pure: comment lines are masked out the same way `check_diagram` does, and a
    malformed depends line (already reported by `kiem`) is simply skipped here —
    this command only cares about the links that parse.
    """
    mask = comment_mask(lines)
    deps = []
    for i, line in enumerate(lines):
        if mask[i] or not line.startswith(DEPENDS_KEY + ":"):
            continue
        found = DEPENDS_LINE_RE.match(line)
        if found:
            deps.append(found.group("feature"))
    return deps


def read_all_features(root=None):
    """Read every `*.md` diagram under the mind-map dir of a project.

    I/O only: parsing is delegated to `extract_depends` so the graph logic below
    stays pure. Returns `(feature_deps, unreadable)` — `feature_deps` maps every
    feature slug found to the list of slugs its depends lines point to;
    `unreadable` lists the project-relative paths that could not be read.
    """
    directory = mind_map_dir(root)
    feature_deps = {}
    unreadable = []
    if not os.path.isdir(directory):
        return feature_deps, unreadable
    for name in sorted(os.listdir(directory)):
        if not name.endswith(FILE_SUFFIX):
            continue
        feature = name[:-len(FILE_SUFFIX)]
        lines = read_diagram(os.path.join(directory, name))
        if lines is None:
            unreadable.append(os.path.join(MIND_MAP_DIR_REL, name))
            continue
        feature_deps[feature] = extract_depends(lines)
    return feature_deps, unreadable


def build_link_graph(feature_deps):
    """Pure: the missing targets and one cycle (if any) across a set of features.

    `feature_deps` maps every known feature slug to the list of slugs its depends
    lines point to. No I/O, no sys.exit — same spirit as `check_diagram`, so a
    later caller (the total-map render) can import this straight instead of
    shelling out to the CLI.

    Returns `{"missing": <sorted distinct slugs referenced but with no file>,
    "cycle": <the chain of slugs forming one detected cycle, first slug repeated
    at the end> or None}`.
    """
    features = set(feature_deps)
    missing = set()
    for deps in feature_deps.values():
        for dep in deps:
            if dep not in features:
                missing.add(dep)

    cycle = None
    visited = set()

    def dfs(node, path, on_path):
        nonlocal cycle
        if cycle is not None:
            return
        if node in on_path:
            # A node already on the current stack IS also in `visited` (added
            # below on first entry), so this must be checked before that set.
            start = path.index(node)
            cycle = path[start:] + [node]
            return
        if node in visited:
            return
        visited.add(node)
        on_path.add(node)
        path.append(node)
        for dep in feature_deps.get(node, []):
            if dep in features:
                dfs(dep, path, on_path)
                if cycle is not None:
                    return
        path.pop()
        on_path.discard(node)

    for feature in sorted(features):
        if cycle is not None:
            break
        dfs(feature, [], set())

    return {"missing": sorted(missing), "cycle": cycle}


def cmd_lien_he(args):
    """Cross-check every depends line under docs/tdq/mind-map/ against the files
    that actually exist there.

    Checked in this order because a dangling link cannot be part of a cycle: a
    missing target is reported first (exit 1), a cycle among the features that do
    exist is reported next (exit 3), a clean graph is exit 0.
    """
    feature_deps, unreadable = read_all_features()
    if unreadable:
        for rel in unreadable:
            _log(f"lien-he: cannot read {rel}")
            print(f"lien-he: cannot read {rel}", file=sys.stderr)
        return EXIT_SYNTAX

    graph = build_link_graph(feature_deps)
    missing = graph["missing"]
    if missing:
        for slug in missing:
            print(f"lien-he: missing feature file for {slug!r} "
                  f"(expected {feature_rel_path(slug)})")
        _log(f"lien-he: {len(feature_deps)} feature(s), {len(missing)} missing target(s)")
        return EXIT_VIOLATION

    cycle = graph["cycle"]
    if cycle:
        print(f"lien-he: dependency cycle: {' -> '.join(cycle)}")
        _log(f"lien-he: {len(feature_deps)} feature(s), cycle: {' -> '.join(cycle)}")
        return EXIT_UPDATE

    print(f"lien-he: {len(feature_deps)} feature(s) checked — "
          f"no missing dependency, no cycle")
    _log(f"lien-he: {len(feature_deps)} feature(s), no violation")
    return EXIT_OK


# ------------------------------------------------------------------------- CLI
def build_parser():
    """The CLI surface. Later commands (doi-chieu, xem) plug in here."""
    parser = argparse.ArgumentParser(
        prog="tdq_mindmap.py",
        description="Mind-map files of the TDQ workflow: one living diagram per feature.")
    subs = parser.add_subparsers(dest="lenh", required=True)

    sinh = subs.add_parser(
        "sinh", help="create the diagram of a feature, or open the existing one")
    sinh.add_argument("feature", help="feature slug, kebab-case ASCII (e.g. dang-nhap)")
    sinh.set_defaults(handler=cmd_sinh)

    kiem = subs.add_parser(
        "kiem", help="check one diagram file against the shape, report every violation")
    kiem.add_argument("file", help="path of the diagram file to check")
    kiem.set_defaults(handler=cmd_kiem)

    lien_he = subs.add_parser(
        "lien-he",
        help=f"cross-check every {DEPENDS_KEY} line under docs/tdq/mind-map/")  # i18n-allow
    lien_he.set_defaults(handler=cmd_lien_he)

    return parser


def main(argv):
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
