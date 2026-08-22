#!/usr/bin/env python3
"""skill_tokens.py — measure the REAL token count of the skill set, not characters over four.

Why a separate script when `context_surface.py` exists: that one uses the factor
`BYTES_PER_TOKEN = 4` for every file. The factor holds for English and falls far short for
accented Vietnamese (measured: 1.89 characters/token against 4.68 for English). And the text
that most needs an exact number is precisely the Vietnamese one. This script counts with a
real tokenizer, so the two tables may disagree — the number HERE is the one decisions use.

Two commands:
        python3 scripts/skill_tokens.py --theo-phase   # body tokens of the skills loaded per phase
        python3 scripts/skill_tokens.py --mo-ta        # DESCRIPTION tokens of the enabled skills

The two commands measure TWO DIFFERENT BLOCKS; never add them together:
    * `--theo-phase` measures the skill **body** — it enters context only when that skill runs.
    * `--mo-ta` measures the skill **description** — it sits in the system prompt of EVERY call.

Token-counting library: `anthropic-tokenizer`, installed in its own venv `.venv-tokens/`.
Without the library the script ERRORS; falling back to characters/4 is absolutely banned —
spec §4 forbids guessing token counts. Running under the system `python3` still works: the
script re-executes itself with the venv python when it finds one.

Log service: ISO timestamps on stderr, on by default, muted with `TDQ_LOG=0`.
The table always goes to stdout so it can be piped.
Exit: 0 finished · 2 bad syntax · 3 token-counting library missing.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402 — shares the log service (log_enabled, timestamp)
import context_surface  # noqa: E402 — shares _read / _split_frontmatter
import skill_inventory  # noqa: E402 — shares the list of ENABLED skills

# Another python can be pointed at through an environment variable: the tests need to stage
# a "no venv" world without touching the real venv of the repo.
VENV_PYTHON = os.environ.get(
    "TDQ_TOKENS_VENV", os.path.join(ROOT, ".venv-tokens", "bin", "python"))
CAI_DAT = (f"python3 -m venv {os.path.relpath(os.path.join(ROOT, '.venv-tokens'), ROOT)} "
           "&& .venv-tokens/bin/pip install anthropic-tokenizer==0.1.0")
EXIT_THIEU_THU_VIEN = 3

# Six phase blocks. Each block = the skill BODY files entering context when that phase runs.
# The order inside the tuple is the print order; keep it so measurements stay comparable.
KHOI_PHASE = (
    ("always loaded", ("tdq-conventions",)),
    ("intake", ("tdq-intake",)),
    ("spec", ("tdq-spec",)),
    ("plan", ("tdq-plan",)),
    ("build", ("tdq-build",)),
)
KHOI_LUAT_KEM = "attached rules (every reference)"

# Grouping for `--mo-ta`. Matched on the source name (`plugin:<x>` or `user`/`project`).
# A source belongs to EXACTLY one group — the first match wins, so the order matters.
MUC = (
    ("workflow", ("tdq-workflow", "superpowers", "claude-md-management",
                  "remember", "hookify")),
    ("code", ("plugin-dev", "mcp-server-dev", "skill-creator", "sonarqube",
              "code-simplifier", "feature-dev", "lumen", "playground")),
    ("design", ("figma", "canva", "adobe-for-creativity", "frontend-design")),
    ("game engine", ("unity", "unreal", "qt-development-skills")),
    ("web", ("playwright", "chrome-devtools-mcp", "firecrawl", "tavily",
             "cloudflare", "base44", "postman", "hyperframes")),
    ("data", ("data-engineering", "mongodb", "redis-development",
                 "datarobot-agent-skills", "huggingface-skills")),
)
MUC_KHAC = "other"


def _log(msg):
    """One log line on stderr with a timestamp. Muted with TDQ_LOG=0 — the tdq_state contract."""
    if tdq_state.log_enabled():
        print(f"[{tdq_state.now_iso()}] {msg}", file=sys.stderr)


class ThieuThuVienDem(Exception):
    """No real tokenizer. Raised instead of guessing — spec §4 bans the characters/4 estimate."""


def nap_bo_dem():
    """Return a real token-counting function, or raise `ThieuThuVienDem`.

    This function is pure: it does NOT exit the process and does NOT `execv`. Safe to call from
    a test or another script. Jumping to the venv python belongs to the CLI layer
    (`nhay_sang_venv`), because it replaces the running process — doing that inside a library
    function swallows the test runner too (measured: pytest got replaced and exited 2).
    """
    try:
        from anthropic_tokenizer import count_tokens
        return count_tokens
    except ImportError as exc:
        raise ThieuThuVienDem(CAI_DAT) from exc


LENH_DEM_LO = (
    "import json, sys\n"
    "from anthropic_tokenizer import count_tokens\n"
    "json.dump([count_tokens(t) for t in json.load(sys.stdin)], sys.stdout)"
)


def dem_qua_venv(doan):
    """Count tokens for a WHOLE BATCH of texts with the venv python, one process for the batch.

    For a script running under a python without the library that also must not `execv`
    (e.g. `token_audit.py` when a test calls the function in-process). Batched because the
    cost sits in starting the process, not in the number of texts.
    """
    if not doan:
        return []
    if not os.path.exists(VENV_PYTHON):
        raise ThieuThuVienDem(CAI_DAT)
    proc = subprocess.run([VENV_PYTHON, "-c", LENH_DEM_LO],
                          input=json.dumps(doan), capture_output=True, text=True)
    if proc.returncode != 0:
        raise ThieuThuVienDem(CAI_DAT)
    return json.loads(proc.stdout)


def nhay_sang_venv():
    """Re-run this very script with the venv python. Jumps exactly once, then stops."""
    if os.environ.get("TDQ_TOKENS_DA_NHAY") == "1" or not os.path.exists(VENV_PYTHON):
        return False
    _log(f"library missing in the current python — jumping to {os.path.relpath(VENV_PYTHON, ROOT)}")
    os.environ["TDQ_TOKENS_DA_NHAY"] = "1"
    os.execv(VENV_PYTHON, [VENV_PYTHON, os.path.abspath(__file__)] + sys.argv[1:])


def nap_bo_dem_cho_cli():
    """The counter for the CLI layer: try this python → try the venv → exit 3 with how to install."""
    try:
        return nap_bo_dem()
    except ThieuThuVienDem:
        pass
    nhay_sang_venv()
    print("skill_tokens.py: the token-counting library `anthropic-tokenizer` is missing.\n"
          "This script is FORBIDDEN to estimate characters/4 (spec §4), so it stops here.\n"
          f"Install with: {CAI_DAT}", file=sys.stderr)
    sys.exit(EXIT_THIEU_THU_VIEN)


def _chu(raw):
    """bytes → str. `context_surface` reads bytes to measure size; the tokenizer needs text."""
    return raw.decode("utf-8", errors="replace")


def _than_skill(ten_skill):
    """Body tokens of one SKILL.md (frontmatter dropped) + its path, or None."""
    path = os.path.join(ROOT, "skills", ten_skill, "SKILL.md")
    if not os.path.exists(path):
        return None
    _, body = context_surface._split_frontmatter(context_surface._read(path))
    return _chu(body)


def _references(ten_skill):
    """Every reference file of a skill — the `read on demand` layer, merged into attached rules.

    Scanned RECURSIVELY. The previous version used `references/*.md`, so it skipped the whole
    sub-directory `references/rules/` (10 files, 14,554 tokens) and reported a ceiling nearly
    20% under reality. A measure that reads low makes every optimisation built on it wrong too.
    """
    goc = os.path.join(ROOT, "skills", ten_skill, "references")
    return sorted(glob.glob(os.path.join(goc, "**", "*.md"), recursive=True))


def do_theo_phase(dem):
    """Token table over the 6 phase blocks. Returns rows of [block name, file count, tokens]."""
    rows = []
    for ten_khoi, skills in KHOI_PHASE:
        tong, so_file = 0, 0
        for skill in skills:
            body = _than_skill(skill)
            if body is None:
                _log(f"warning: no skills/{skill}/SKILL.md found — skipped")
                continue
            tong += dem(body)
            so_file += 1
        rows.append([ten_khoi, so_file, tong])

    tong_ref, so_ref = 0, 0
    for _, skills in KHOI_PHASE:
        for skill in skills:
            for ref in _references(skill):
                tong_ref += dem(_chu(context_surface._read(ref)))
                so_ref += 1
    rows.append([KHOI_LUAT_KEM, so_ref, tong_ref])
    _log(f"measured {len(rows)} phase block(s)")
    return rows


def phan_muc(nguon):
    """The group name of a skill source. No group matches → `other`."""
    goc = nguon.split(":", 1)[-1]
    for ten_muc, khoa in MUC:
        if any(k in goc for k in khoa):
            return ten_muc
    return MUC_KHAC


# `[\w-]+:` and not `\w+:` — frontmatter keys carry hyphens (`argument-hint`,
# `allowed-tools`). With `\w+:` the description swallows those lines, inflating the token
# count and adding noise to the router (measured: `sonar-analyze` swallowed its allowed-tools).
DESC_RE = re.compile(r"^description:\s*(.*(?:\n(?![\w-]+:|---).*)*)", re.M)


TEN_KHAI_RE = re.compile(r"^name:\s*(.+?)\s*$", re.M)


def ban_do_skill_md():
    """Scan every SKILL.md on disk ONCE → {lookup key: [path]}.

    Re-scanning per skill means 284 recursive globs over `~/.claude`, taking over two minutes
    (measured, the process had to be killed). Scan once and look up: under a second.

    Every file enters the map under TWO keys: the directory name, and the name DECLARED in the
    frontmatter. The two disagree more often than expected — `canva-brand-check` lives in the
    directory `brand-check/`, `unity-mcp-orchestrator` in `unity-mcp-skill/`. Looking up by
    directory name alone loses the file for 10/284 skills, and the price is not one missing log
    line: every "hide the description, read SKILL.md on demand" layer is blind to exactly those
    10 skills.
    """
    home = os.path.expanduser("~")
    ban_do = {}
    for pattern in (os.path.join(home, ".claude", "**", "skills", "*", "SKILL.md"),
                    os.path.join(ROOT, "skills", "*", "SKILL.md"),
                    os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md")):
        for path in glob.glob(pattern, recursive=True):
            khoa = {os.path.basename(os.path.dirname(path))}
            m = TEN_KHAI_RE.search(_chu(context_surface._read(path))[:2000])
            if m:
                khoa.add(m.group(1).strip().strip('"').strip("'"))
            for k in khoa:
                ban_do.setdefault(k, []).append(path)
    _log(f"SKILL.md map: {len(ban_do)} lookup key(s)")
    return ban_do


def khoa_tra(ten_skill):
    """Skill name → map lookup key. Strips the plugin prefix and quotes stuck on by frontmatter.

    The quotes are a real data defect: one skill declares `name: "adobe-batch-edit-photos"`
    with double quotes, and a name carrying quotes matches no key.
    """
    return ten_skill.split(":")[-1].strip().strip('"').strip("'")


def _mo_ta_day_du(ten_skill, mac_dinh, ban_do):
    """The FULL description read straight from SKILL.md. No file found → the shortened one.

    `skill_inventory` shortens descriptions to fit the inventory table; measuring tokens needs
    the full text, because the full text is what really sits in the system prompt.
    """
    for path in ban_do.get(khoa_tra(ten_skill), []):
        m = DESC_RE.search(_chu(context_surface._read(path))[:4000])
        if m and m.group(1).strip():
            return m.group(1).strip()
    return mac_dinh


def do_mo_ta(dem, project=ROOT):
    """Description-token table of the ENABLED skills, with source and group.

    Returns (rows, tong_skill). Each row: [source, group, skill count, desc tokens, name tokens].
    """
    hang = skill_inventory.inventory(project)
    ban_do = ban_do_skill_md()
    gop = {}
    for ten, mo_ta_ngan, nguon in hang:
        day_du = _mo_ta_day_du(ten, mo_ta_ngan, ban_do)
        khoa = (nguon, phan_muc(nguon))
        o = gop.setdefault(khoa, [0, 0, 0])
        o[0] += 1
        # +6: the framing cost of each entry in the skill list (newline, separator).
        o[1] += dem(day_du) + dem(ten) + 6
        o[2] += dem(ten) + 6
    rows = [[nguon, muc, n, tok, ten_tok]
            for (nguon, muc), (n, tok, ten_tok) in
            sorted(gop.items(), key=lambda kv: -kv[1][1])]
    _log(f"measured the descriptions of {len(hang)} enabled skill(s), {len(rows)} source group(s)")
    return rows, len(hang)


def _in_bang(headers, rows):
    """Print a markdown table on stdout — pipeable, and pasteable into a report."""
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        print("| " + " | ".join(f"{c:,}".replace(",", ".") if isinstance(c, int)
                                else str(c) for c in row) + " |")


def lenh_theo_phase(dem):
    rows = do_theo_phase(dem)
    _in_bang(("phase block", "files", "tokens"), rows)
    tong = sum(r[2] for r in rows)
    print(f"\nUPPER BOUND for one lane-full request: "
          f"{tong:,}".replace(",", ".") + " token")
    print("This is a CEILING, not the real number of a request: the `attached rules` block merges\n"
          "EVERY reference file, while a request opens only the references its skill bodies point at.\n"
          "A before/after comparison must use this same way of measuring, never mix the two.")
    return 0


def lenh_mo_ta(dem, project):
    rows, tong_skill = do_mo_ta(dem, project)
    _in_bang(("source", "group", "skills", "desc tokens", "tokens if names only"), rows)
    tong_tok = sum(r[3] for r in rows)
    tong_ten = sum(r[4] for r in rows)
    print(f"\nTotal: {tong_skill} enabled skill(s) · "
          f"{tong_tok:,}".replace(",", ".") + " description token(s) · "
          f"{tong_ten:,}".replace(",", ".") + " token(s) if only names are kept")
    theo_muc = {}
    for nguon, muc, n, tok, ten_tok in rows:
        o = theo_muc.setdefault(muc, [0, 0])
        o[0] += n
        o[1] += tok
    print()
    _in_bang(("group", "skills", "desc tokens"),
             [[muc, n, tok] for muc, (n, tok) in
              sorted(theo_muc.items(), key=lambda kv: -kv[1][1])])
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="skill_tokens.py",
        description="Measure the real token count of the skill set (bodies per phase, descriptions per group).")
    parser.add_argument("--theo-phase", action="store_true", dest="theo_phase",
                        help="table of skill-body tokens over the 6 phase blocks")
    parser.add_argument("--mo-ta", action="store_true", dest="mo_ta",
                        help="table of description tokens of the enabled skills, by source and group")
    parser.add_argument("--project", default=ROOT,
                        help="project directory to inventory skills in (default: the repo root)")
    args = parser.parse_args(argv)

    if args.theo_phase == args.mo_ta:
        parser.error("pick exactly one: --theo-phase or --mo-ta")

    lenh = "--theo-phase" if args.theo_phase else "--mo-ta"
    _log(f"skill_tokens · {lenh}")
    dem = nap_bo_dem_cho_cli()
    if args.theo_phase:
        return lenh_theo_phase(dem)
    return lenh_mo_ta(dem, args.project)


if __name__ == "__main__":
    sys.exit(main())
