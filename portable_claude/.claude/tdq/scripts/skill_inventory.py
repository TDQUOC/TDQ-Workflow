#!/usr/bin/env python3
"""Inventory the skills present ON DISK for step B0 of tdq-intake (0.3.3).

Scans exactly 3 sources — NOT the cache (the cache keeps every old version, hundreds of junk files):
1. `~/.claude/skills/<x>/SKILL.md`         → source `user`
2. `<project>/.claude/skills/<x>/SKILL.md` → source `project`
3. ENABLED plugins: `enabledPlugins` merged over the 3 settings layers (user → project →
      settings.local.json, later layers win), looked up in `installed_plugins.json`,
      reading only the `installPath` directory of the installed version. An entry with
      `scope: "project"` belonging to ANOTHER project is dropped.

The BUILT-IN skills of Claude Code are not on disk (measured: 7 on disk / 18 in context),
so the table always ends with 2 lines reminding the model to copy that part from context.

Usage:  python3 scripts/skill_inventory.py [--project <dir>] [--loc <keyword>] [--tat-ca]
No flag = the full table (original behaviour, ~39.7KB on a real machine ≈ 9,774 tokens per
B0 run). `--loc <keyword>` keeps only the lines matching the keyword, PLUS every line of
source `project` and `plugin:tdq-workflow` — the two sources that settle the USE verdict,
so hiding them is banned — then prints a last line saying how many were hidden and the
command to see them all. `--tat-ca` prints everything, like the default (so that reminder
line points at a command that really exists). Exit 0 for every data hiccup (missing file,
broken JSON → warn and print the rest); exit 2 only on bad command syntax.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tdq_state  # noqa: E402 — shares the log service (_warn, TDQ_LOG, timestamp)

DESC_MAX = 60
TRIGGER_TAIL = 50   # characters taken from the trigger phrase on, when it sits past DESC_MAX
# A trigger phrase starting just BEFORE the threshold still gets cut in half (measured:
# `huggingface-trackio` has `Use when` at character 58, the cell ends at `Us`). Back the
# probe point up a stretch to catch that case; the overlap is at most that same stretch.
TRIGGER_LOOKBACK = 15
# Skill descriptions follow the shape "sentence 1 = what it is, sentence 2 = when to use it".
# Measured over 268 SKILL.md files: 146/211 skills have the trigger phrase AFTER character 60,
# so truncating loses exactly the part the USE/NO verdict needs. `_condense` keeps the head
# and appends the trigger stretch.
# The Vietnamese branch serves skills whose description is Vietnamese (the 6 tdq-* skills are
# the local example): same shape, other language. Measured over 274 skills: 0 false matches.
TRIGGER_RE = re.compile(
    r"use when|use this|whenever|when the user|trigger"
    r"|dùng khi|dùng cho|gọi khi|áp dụng khi|khi cần|khi user", re.I)  # i18n-allow
FRONTMATTER_MAX_LINES = 80
# YAML block scalar: `description: |` and variants. Before 2026-08-09 the parser read `|` as
# content → 18 skills (firecrawl, tavily, mongodb-search-and-ai) came out with no description.
BLOCK_MARKERS = ("|", "|-", "|+", ">", ">-", ">+")
REMINDER = (
    "— The table above only holds the skills on disk.",
    "— ALSO COPY the built-in skills visible in context "
    "into the inventory table, then give a verdict per line.",
)
USAGE = ("Usage: skill_inventory.py [--project <dir>] "
         "[--loc <keyword>] [--tat-ca]")
# Sources `--loc` may NEVER hide: the skills of the project itself and of plugin
# tdq-workflow are the two sources that settle the USE verdict at step B0.
KEEP_SOURCES = ("project",)
KEEP_SOURCE_PREFIX = "plugin:tdq-workflow"
FULL_CMD = "python3 scripts/skill_inventory.py --tat-ca"


def _load_json(path, missing_ok=False):
    """dict from a JSON file, or None. Broken/missing (when missing_ok=False) → warning."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if not missing_ok:
            tdq_state._warn(f"skill_inventory: missing {path}")
        return None
    except (OSError, ValueError) as exc:
        tdq_state._warn(f"skill_inventory: cannot read {path} ({type(exc).__name__})")
        return None


def _clean(text):
    """Drop control characters — an ugly SKILL.md must not drive the user's terminal (Q9)."""
    return "".join(ch for ch in text if ch >= " " or ch == "\t")


def _frontmatter(path):
    """(name, description) from the frontmatter; a read error → (None, None) + a warning.

    A multi-line description (block scalar `|`, `>`, or an indented plain scalar) is joined
    into one line: every indented line up to the next level-0 key or the closing `---`.
    """
    name = desc = ""
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(16384).splitlines()[:FRONTMATTER_MAX_LINES]
    except OSError as exc:
        tdq_state._warn(f"skill_inventory: cannot read {path} ({type(exc).__name__})")
        return None, None
    if head and head[0].strip() == "---":
        head = head[1:]
    i = 0
    while i < len(head):
        line = head[i]
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            name = _clean(line[5:].strip())
        elif line.startswith("description:"):
            rest = line[12:].strip()
            parts = [] if rest in BLOCK_MARKERS else [rest]
            i += 1
            while i < len(head) and head[i].strip() != "---" and \
                    (not head[i].strip() or head[i][:1] in (" ", "\t")):
                parts.append(head[i].strip())
                i += 1
            desc = _clean(" ".join(p for p in parts if p).strip().strip('"'))
            continue
        i += 1
    return name or _clean(os.path.basename(os.path.dirname(path))), desc


def _condense(desc):
    """Shorten a description for one table cell: keep the head, append the trigger stretch.

    `|` becomes `/` — the printed table splits columns on `|`, leaving it breaks the columns.
    """
    text = " ".join((desc or "").split()).replace("|", "/")
    if len(text) <= DESC_MAX:
        return text
    found = TRIGGER_RE.search(text, DESC_MAX - TRIGGER_LOOKBACK)
    if not found:
        return text[:DESC_MAX]
    # Trigger across the threshold: cut the head right BEFORE it, no repeat on both sides.
    head = text[:min(DESC_MAX, found.start())].rstrip()
    return f"{head} … {text[found.start():found.start() + TRIGGER_TAIL]}"


def _scan_skill_dir(root):
    """[(name, desc)] from one directory holding <skill>/SKILL.md."""
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "*", "SKILL.md"))):
        name, desc = _frontmatter(path)
        if name is not None:
            rows.append((name, desc))
    return rows


def _enabled_plugins(home, project):
    """enabledPlugins merged over 3 layers — later layers win (like Claude Code)."""
    merged = {}
    layers = (
        (os.path.join(home, ".claude", "settings.json"), False),
        (os.path.join(project, ".claude", "settings.json"), True),
        (os.path.join(project, ".claude", "settings.local.json"), True),
    )
    for path, missing_ok in layers:
        data = _load_json(path, missing_ok=missing_ok)
        if isinstance(data, dict) and isinstance(data.get("enabledPlugins"), dict):
            merged.update(data["enabledPlugins"])
    return merged


def _plugin_skill_dirs(home, project):
    """[(plugin name, skills directory)] of the plugins enabled for this project."""
    enabled = _enabled_plugins(home, project)
    if not any(enabled.values()):
        return []
    data = _load_json(os.path.join(home, ".claude", "plugins", "installed_plugins.json"))
    entries = data.get("plugins", {}) if isinstance(data, dict) else {}
    project_real = os.path.realpath(project)
    dirs, seen = [], set()
    for key in sorted(k for k, on in enabled.items() if on):
        for entry in entries.get(key, []) or []:
            if not isinstance(entry, dict):
                continue
            # A plugin installed for another project only: not part of this project's table.
            if entry.get("scope") == "project" and \
                    os.path.realpath(str(entry.get("projectPath", ""))) != project_real:
                continue
            # Two layouts in the wild: `<installPath>/skills` and `<installPath>/.claude/skills`.
            # Try the first, fall back to the second; a plugin with neither adds no row.
            root = str(entry.get("installPath", ""))
            for phan in (("skills",), (".claude", "skills")):
                skills = os.path.join(root, *phan)
                if os.path.isdir(skills):
                    if skills not in seen:
                        seen.add(skills)
                        dirs.append((key.split("@")[0], skills))
                    break
    return dirs


def inventory(project):
    """[(name, shortened desc, source)] — on a name clash the source scanned first wins."""
    home = os.path.expanduser("~")
    rows, seen = [], set()

    def add(name, desc, source):
        if name in seen:
            return
        seen.add(name)
        rows.append((name, _condense(desc), source))

    for name, desc in _scan_skill_dir(os.path.join(home, ".claude", "skills")):
        add(name, desc, "user")
    for name, desc in _scan_skill_dir(os.path.join(project, ".claude", "skills")):
        add(name, desc, "project")
    for plugin, skill_dir in _plugin_skill_dirs(home, project):
        for name, desc in _scan_skill_dir(skill_dir):
            add(name, desc, f"plugin:{plugin}")
    return rows


def _filter(rows, keyword):
    """(rows kept, rows hidden) — matching the keyword OR belonging to a never-hidden source."""
    needle = keyword.casefold()
    kept, hidden = [], 0
    for name, desc, source in rows:
        protected = source in KEEP_SOURCES or source.startswith(KEEP_SOURCE_PREFIX)
        if protected or needle in f"{name} {desc}".casefold():
            kept.append((name, desc, source))
        else:
            hidden += 1
    return kept, hidden


def main(argv):
    # A23: anchor on the real project (TDQ_PROJECT_DIR > git root > cwd) — running from a
    # sub-directory must not lose the `project` skill source.
    project = tdq_state.resolve_project_dir()
    keyword = ""
    show_all = False
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--project" and args:
            project = args.pop(0)
        elif arg == "--loc" and args:
            keyword = args.pop(0)
        elif arg == "--tat-ca":
            show_all = True
        else:
            print(f"unknown argument: {arg}", file=sys.stderr)
            print(USAGE, file=sys.stderr)
            return 2
    rows = inventory(project)
    # `--tat-ca` beats `--loc`: typing both means wanting to see everything.
    hidden = 0
    if keyword and not show_all:
        rows, hidden = _filter(rows, keyword)
        tdq_state._info(
            f"skill_inventory: filtered on {keyword!r} — kept {len(rows)}, hid {hidden}")
    if rows:
        for name, desc, source in rows:
            print(f"{name} | {desc} | {source}")
    else:
        print("(no skill on disk)")
    for line in REMINDER:
        print(line)
    if keyword and not show_all:
        # The last line is MANDATORY: once the table is cut, the reader must see right away how
        # much went missing and which command shows it all — cut tokens, never hide the cut.
        print(f'— Hid {hidden} skill(s) not matching "{keyword}"; see them all: {FULL_CMD}')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
