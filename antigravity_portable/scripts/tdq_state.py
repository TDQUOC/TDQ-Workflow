#!/usr/bin/env python3
"""State helper for the TDQ workflow plugin (stdlib only).

Machine-read state: <project>/docs/tdq/state.json — EVERY change must go through
this module. The mirror humans and models read: <project>/docs/tdq/STATE.md,
regenerated after every write (never hand-edited).

Principles since 0.3.0:
- Never exit != 0 because of STATE (corrupt state, bad enum, missing request...).
  Only a bad COMMAND SYNTAX exits 2. State must never become a dead end.
- `next` is the single source answering "where am I, what comes next" — hooks call
  that same function instead of copying its words into a second place.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tdq_ten_lenh  # noqa: E402

STATE_REL = os.path.join("docs", "tdq", "state.json")
STATE_MD_REL = os.path.join("docs", "tdq", "STATE.md")
TURN_LOG_REL = os.path.join("docs", "tdq", ".tdq-turn.jsonl")

APPROVE_TARGETS = ("spec", "plan", "quick")
VALID_MODES = ("main", "subagent")
BY_MAX = 200
VALID_LANES = {"quick", "full", None}

# READER-FACING labels. The machine identifiers stay "quick"/"full" — two separate
# layers so the wording can change without migrating live state or touching tests
# that pin the identifiers.
LANE_LABELS = {
    "quick": "express mode",
    "full": "deep mode",
}

# TYPED aliases -> machine identifier. The old words (quick/full) keep working so
# existing users are not broken. Keys are lowercase, already stripped of accents
# and spaces by normalize_lane. Vietnamese spellings stay on purpose: they are what
# a Vietnamese user types, not text this tool prints.
LANE_ALIASES = {
    "quick": "quick", "nhanh": "quick", "express": "quick",
    "full": "full", "deep": "full",
    "chuyen-sau": "full", "chuyensau": "full", "chuyên sâu": "full",  # i18n-allow
    "chuyen sau": "full", "chuyên-sâu": "full",  # i18n-allow
}
# Mode uses the same two layers as lane: the machine identifiers stay "main"/
# "subagent", so old state, old plans (the `Mode thực thi:` line) and tests that  # i18n-allow
# pin those names need no migration.
MODE_LABELS = {
    "main": "inline implement",
    "subagent": "sub-agent implement",
}

# TYPED aliases -> machine identifier. Old names keep working; the newer ones are
# accepted with a hyphen, with a space and with the "implement" tail, because that
# is the wording the user reads at the mode gate.
MODE_ALIASES = {
    "main": "main", "inline": "main",
    "inline implement": "main", "inline-implement": "main",
    "subagent": "subagent", "sub-agent": "subagent", "sub agent": "subagent",
    "sub-agent implement": "subagent", "sub agent implement": "subagent",
    "subagent implement": "subagent", "sub-agent-implement": "subagent",
}
VALID_PHASES = {"idle", "analyze", "spec", "plan", "mode", "implement", "qc", "report"}

# Phase `diagram` was removed from the workflow on 2026-09-01. A state written
# before that day may still carry it; `load` lifts such a phase back to the one
# it came from instead of failing, so an old session stays usable.
PHASE_DA_GO = {"diagram": "spec"}

# Every door the removed diagram phase used to open answers with this one line.
# A bare "unknown command" would read as a typo; the caller needs to learn that
# the phase itself is gone, not that they mistyped it.
LOI_SO_DO_DA_GO = ("The diagram phase was removed from the workflow on "
                   "2026-09-01 — there is no diagram to register or approve "
                   "any more; go straight from spec to plan.")

USAGE = ("Usage: tdq_state.py next [--brief] | get [key] | "
         "init <slug> [nhanh|express|quick — express mode | chuyen-sau|deep|full — "  # i18n-allow
         "deep mode] [--lang <code>] | "
         "set k=v ... | approve <spec|plan|quick (aliases: nhanh|express)> "  # i18n-allow
         "[--mode main|subagent] "
         "[--no-qc (quick only, requires --by)] [--by \"<user sentence>\"] | "
         "pause --ly-do \"<why>\" | resume | "
         "reset | phases-doc")

EXIT_SYNTAX = 2


# ------------------------------------------------------------------ slug
#
# Two formats live side by side: the OLD slug carries only a date (269 documents
# are already named that way and the user chose to keep them), the NEW slug adds
# hour and minute. Reading accepts both; writing a new one requires the time —
# that check sits in the `init` branch of `cli()`.
SLUG_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")
SLUG_FORMULA = "YYYY-MM-DD-HHMM-<kebab, <=5 words, no accents>"


def parse_slug(slug):
    """Split a slug into (date, HHMM or None, text part). No match → None.

    Four digits at the head of the text part count as a time only when it is a
    REAL time (00:00–23:59); `2026-08-15-9999-viec` stays an old slug whose text
    part is `9999-viec`.
    """
    if not isinstance(slug, str):
        return None
    match = SLUG_RE.match(slug.strip())
    if not match:
        return None
    year, month, day, rest = match.groups()
    try:
        datetime(int(year), int(month), int(day))
    except ValueError:
        return None
    ngay = f"{year}-{month}-{day}"
    head, _, tail = rest.partition("-")
    if len(head) == 4 and head.isdigit() and tail:
        if int(head[:2]) <= 23 and int(head[2:]) <= 59:
            return (ngay, head, tail)
    return (ngay, None, rest)


# Language of the documents this request writes (spec/plan/qc/report and the
# conversation with the user). Rules and machine-printed strings are always
# English; only the documents follow this field. Declared once at
# `init --lang <code>` and constant for the whole request. Missing → "vi".
DEFAULT_DOC_LANG = "vi"
DOC_LANG_RE = re.compile(r"^[a-z]{2,3}(-[a-z]{2,8})*$")


def normalize_doc_lang(raw):
    """Return the normalised language code, or None when it is not a valid code.

    Accepts short BCP 47 codes: `vi`, `en`, `ja`, `pt-br`. Free-form names
    ("Vietnamese", "English") are refused — this field is a machine code, not a
    label.
    """
    if not isinstance(raw, str):
        return None
    ma = raw.strip().lower()
    return ma if DOC_LANG_RE.match(ma) else None


def default_state():
    return {
        "schema_version": 4,
        "active_request": None,
        # slug of the request replaced at the last init (trace/log only)
        "previous_request": None,
        "lane": None,
        "phase": "idle",
        # Sản phẩm của bước phân tích. Cả hai lane đều đẻ ra brief ngay ở intake, nhưng
        # trước 2026-09-01 không đâu ghi lại đường dẫn — khác hẳn spec_file/plan_file.
        "brief_file": None,
        "spec_file": None,
        "spec_approved": False,
        "spec_sha256": None,
        "spec_approved_at": None,
        # the user's approval sentence verbatim (cut at 200 chars) — the only
        # trace left after the hard gate was dropped, must be checkable against
        # the transcript
        "spec_approved_by": None,
        "plan_file": None,
        "plan_approved": False,
        "plan_sha256": None,
        "plan_approved_at": None,
        "plan_approved_by": None,
        "quick_approved": False,
        "quick_approved_at": None,
        "quick_approved_by": None,
        # Lane quick: QC follows the DoD and is ON by default; True = the user
        # opted out deliberately via `approve quick --no-qc`. Who opted out comes
        # from quick_approved_by (the same approval sentence).
        "quick_qc_skipped": False,
        "implement_mode": None,
        # Phase `implement` may only end early through a DECLARED pause: the
        # Stop gate refuses to close a turn while the plan still has open tasks,
        # and this key is the single legal way out. Shape when set:
        # {"ly_do": "<why the run stopped>", "at": "<iso>", "by": "<who>"}.
        # None means "no pause declared", so the gate stays armed. A hook cannot
        # tell whether an error is self-fixable, so whoever stops must say why,
        # and that sentence is what gets shown to the user.
        "implement_pause": None,
        # language code of this request's documents (see DEFAULT_DOC_LANG)
        "doc_lang": DEFAULT_DOC_LANG,
        # request opening mark (schema 4) — the origin of every wall-clock count
        "started_at": None,
        # phase history: [{"phase": "spec", "at": "<iso>"}, ...], one mark per
        # phase CHANGE. Re-entering an old phase still adds a mark — that is what
        # counting re-entries is built on.
        "phase_history": [],
        "updated_at": None,
    }


def state_path(cwd):
    return os.path.join(cwd, STATE_REL)


def state_md_path(cwd):
    return os.path.join(cwd, STATE_MD_REL)


def turn_log_path(cwd):
    return os.path.join(cwd, TURN_LOG_REL)


_MISSING = object()
PRUNE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
              ".next", "target", ".pytest_cache", ".idea", ".claude"}


# ---------------------------------------------------------------- log service

def log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _warn(msg):
    """Warning on stderr with a timestamp (spec §4.1). Off with TDQ_LOG=0.

    Never logs file contents or sensitive values — only paths and field names.
    """
    if log_enabled():
        print(f"[{now_iso()}] ⚠️ {msg}", file=sys.stderr)


def _info(msg):
    if log_enabled():
        print(f"[{now_iso()}] ℹ️ {msg}", file=sys.stderr)


def _fail(msg):
    """Only for a BAD COMMAND SYNTAX — exit 2 (spec §2.9.4)."""
    print(msg, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    sys.exit(EXIT_SYNTAX)


# ------------------------------------------------------------- project root

def resolve_project_dir(cwd=None, env=_MISSING):
    """State project root: TDQ_PROJECT_DIR > git root > a dir holding state > cwd.

    Running the CLI from a subdirectory without resolving would create a 'shadow
    state' right there; the hook (cwd = repo root) would write in one place while
    the model reads another.
    """
    if env is _MISSING:
        env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = os.path.abspath(cwd or os.getcwd())
    current, git_root, state_dir = start, None, None
    while True:
        if state_dir is None and os.path.isfile(state_path(current)):
            state_dir = current
        if git_root is None and os.path.exists(os.path.join(current, ".git")):
            git_root = current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # the git root wins: a state accidentally created in a subdirectory must not
    # be allowed to take over
    return git_root or state_dir or start


def find_shadow_states(root):
    """Misplaced state/mirror: state.json outside root, or an orphan STATE.md (S6)."""
    found = []
    root = os.path.abspath(root)
    canonical_state = os.path.normpath(state_path(root))
    canonical_md = os.path.normpath(state_md_path(root))
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in PRUNE_DIRS]
        if not dirpath.endswith(os.path.join("docs", "tdq")):
            continue
        has_state = "state.json" in files
        if has_state:
            path = os.path.normpath(os.path.join(dirpath, "state.json"))
            if path != canonical_state:
                found.append(os.path.relpath(path, root))
        if "STATE.md" in files and not has_state:
            path = os.path.normpath(os.path.join(dirpath, "STATE.md"))
            if path != canonical_md or not os.path.isfile(canonical_state):
                found.append(os.path.relpath(path, root) + " (orphan mirror, no state.json)")
    return sorted(found)


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ------------------------------------------------------------------ load/save

def load(cwd, heal=True):
    """Read the state. Returns None when the file does not exist yet.

    Corrupt file (S2): renamed to state.json.corrupt-<ts>, warned about, None
    returned — the next command rebuilds a clean state. Old data is NEVER deleted.
    Unknown keys are kept (S3); missing keys are filled in from default_state().
    """
    path = state_path(cwd)
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError:
        return None
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("state is not an object")
    except ValueError:
        if heal:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            broken = f"{path}.corrupt-{stamp}"
            try:
                os.replace(path, broken)
                _warn(f"state.json is corrupt → kept at {os.path.basename(broken)}; "
                      "state rebuilt from defaults.")
            except OSError:
                _warn("state.json is corrupt and could not be renamed — using defaults.")
        return None
    state = default_state()
    state.update(data)              # unknown keys are kept as they are (S3)
    for key, value in default_state().items():
        state.setdefault(key, value)
    state["schema_version"] = default_state()["schema_version"]
    # An older state may carry a phase_history of the wrong type (or junk marks).
    # Healed here so no downstream script has to defend itself.
    state["phase_history"] = [m for m in state["phase_history"]
                              if isinstance(m, dict) and m.get("phase") and m.get("at")] \
        if isinstance(state.get("phase_history"), list) else []
    # Key of the removed diagram phase: dropped in silence, so the next `save`
    # writes a state without it and nothing downstream ever reads it again.
    state.pop("diagrams", None)
    state["phase"] = _nang_pha_da_go(state.get("phase"))
    return state


def _nang_pha_da_go(phase):
    """Lift a phase that no longer exists back onto the phase it came from.

    A request left mid-flight while phase `diagram` was still part of the
    workflow would otherwise sit on a phase no gate accepts — every `set` would
    refuse it and the request would have no legal move left. Warn, then hand
    back the predecessor phase so the run continues where the user left it.
    """
    if phase in PHASE_DA_GO:
        thay = PHASE_DA_GO[phase]
        _warn(f"phase {phase} was removed from the workflow on 2026-09-01 — "
              f"this request is read as phase {thay}.")
        return thay
    return phase


def _dong_so_request_cu(cwd):
    """Close the timing books of the open request into docs/tdq/timing.jsonl.

    The import is LATE on purpose: `tdq_timing` imports this module back, so a
    top-of-file import would be circular. This function only runs inside `cli()`,
    by which time the module is fully loaded.
    A failed close must never block `init` — at worst one statistics line is lost.
    """
    cu = os.environ.get("TDQ_LOG")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import tdq_timing
        state = load(cwd, heal=False)
        if not state or not state.get("active_request"):
            return False
        # Silence the timing layer for this call only: a clean stderr on `init` is
        # a contract a test guards (init over a finished request must stay quiet).
        # For the details, call `tdq_timing.py close` directly.
        os.environ["TDQ_LOG"] = "0"
        so_lieu = tdq_timing.tong_hop(state, datetime.now().astimezone(),
                                      tdq_timing.default_transcript_dir(cwd))
        return bool(so_lieu) and tdq_timing.dong_so(cwd, so_lieu)
    except Exception as exc:                     # noqa: BLE001 — must not block init
        _warn(f"could not close the timing books of the old request: {exc.__class__.__name__}")
        return False
    finally:
        if cu is None:
            os.environ.pop("TDQ_LOG", None)
        else:
            os.environ["TDQ_LOG"] = cu


def ghi_moc_phase(state, phase, at=None):
    """Append a mark to `phase_history` when the phase REALLY changes. True if written.

    Setting the phase already in force is skipped: a 0-second mark only dirties
    the timing table.
    """
    lich_su = state.setdefault("phase_history", [])
    if lich_su and lich_su[-1].get("phase") == phase:
        return False
    lich_su.append({"phase": phase, "at": at or now_iso()})
    return True


def _atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tdq-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def save(cwd, state, expect_updated_at=_MISSING):
    """Atomically write state.json + regenerate STATE.md (S1, the mirror).

    expect_updated_at: the `updated_at` value seen at read time. If the disk now
    differs → another session has just written: warn but STILL write (S7, no
    multi-session lock).
    """
    if expect_updated_at is not _MISSING:
        on_disk = load(cwd, heal=False)
        if on_disk and on_disk.get("updated_at") != expect_updated_at:
            _warn(f"state was written by another process at {on_disk.get('updated_at')} — "
                  "overwriting anyway, check if two sessions are running.")
    state["updated_at"] = now_iso()
    _atomic_write(state_path(cwd), json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    try:
        _atomic_write(state_md_path(cwd), render_state_md(cwd, state))
    except OSError as exc:                       # a broken mirror must not block work
        _warn(f"could not write {STATE_MD_REL}: {exc.__class__.__name__}")
    return state


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_noi_dung(path):
    """Hash the CONTENT part of a spec/plan: from the first `##` heading onward.

    Why not the whole file: the head of the file is the workflow's own bookkeeping
    (date, version, status, path to the brief). Hashing all of it turns every
    bookkeeping write into "the document changed after approval" and the approval
    gate complains for a harmless reason — measured in 2 of 7 cases in
    `docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`. A gate that cries
    wolf often enough is no longer heard when it is right.

    No `##` heading at all → the boundary cannot be inferred, hash the whole file.
    """
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("## "):
            than = "".join(lines[i:])
            break
    else:
        than = "".join(lines)
    return hashlib.sha256(than.encode("utf-8")).hexdigest()


# ------------------------------------------- turn-start effect snapshot (0.3.1)
#
# The turn log only sees actions going through the Edit/Write tools; anything done
# through the shell is invisible. The two helpers below let the hook look straight
# at the DISK, so they do not depend on bash syntax (heredocs, pipes, variables —
# none of it is guessable with a regex).

GIT_STATUS_TIMEOUT = 2
UNTRACKED_STAT_CAP = 200            # number of untracked FILES marked (not status lines)
UNTRACKED_HASH_MAX_BYTES = 262144   # <=256 KB → hash the content; bigger falls back to size:mtime
UNTRACKED_HASH_BUDGET = 4194304     # total bytes readable per fingerprint pass

# The workflow's "bookkeeping" directories: state.json / STATE.md / the turn log
# change on nearly every turn — the hook itself appends to the turn log RIGHT AFTER
# taking the baseline. Counting them into the fingerprint would make even a
# read-only turn look like "the repo changed" (the false block of 0.3.1).
# Always written with `/`: git prints paths with `/` on every OS, so using os.sep
# would silently disable this filter on Windows.
# `graphify-out` is the same kind: `tdq_finish.py` rebuilds the graph every turn so
# that directory almost always changes, and that is an effect of the workflow
# itself, not of the work the user asked for.
BOOKKEEPING_PATHS = ("docs/tdq", "docs/workinglog", "graphify-out")
_EXCLUDE = tuple(f":(top,exclude){p}" for p in BOOKKEEPING_PATHS)
_ROOT_CACHE = {}


def today_log_rel():
    return os.path.join("docs", "workinglog", datetime.now().strftime("%Y-%m-%d") + ".md")


def _git(cwd, *args):
    """stdout (bytes) of a git command, or None when it cannot run."""
    try:
        proc = subprocess.run(["git", "-C", cwd, *args],
                              capture_output=True, timeout=GIT_STATUS_TIMEOUT)
    except subprocess.TimeoutExpired:
        _warn(f"git {args[0]} took over {GIT_STATUS_TIMEOUT}s in {cwd} — skipping disk evidence")
        return None
    except (OSError, subprocess.SubprocessError) as exc:
        _warn(f"could not run git {args[0]} ({type(exc).__name__}) — skipping disk evidence")
        return None
    # rc!=0 = "not a git repo" / no HEAD yet: ordinary, not worth logging.
    return proc.stdout if proc.returncode == 0 else None


def repo_root(cwd):
    """Repo root (porcelain prints paths from the root, not from cwd). None if not a repo."""
    if cwd not in _ROOT_CACHE:
        out = _git(cwd, "rev-parse", "--show-toplevel")
        _ROOT_CACHE[cwd] = out.decode("utf-8", "replace").strip() if out else None
    return _ROOT_CACHE[cwd]


def _untracked_mark(path, budget):
    """Fingerprint of an untracked file → (mark, bytes read).

    CONTENT first: a changed mtime with identical content (touch, a formatter
    rewriting byte-identical output) is not a change — counting it as one blocks
    the turn for nothing.
    """
    if not os.path.isfile(path):
        return None, 0
    try:
        st = os.stat(path)
        if st.st_size <= UNTRACKED_HASH_MAX_BYTES and st.st_size <= budget:
            return sha256_file(path), st.st_size
        return f"{st.st_size}:{st.st_mtime_ns}", 0
    except OSError:
        return None, 0


def repo_status_digest(cwd, status=None):
    """Fingerprint of the repo working state, or None when it cannot be taken.

    Covers both `status --porcelain` (added/deleted/renamed files) and `diff HEAD`
    (content), because porcelain does NOT change when a file already marked `M` is
    edited further — the most common case in a repo mid-work, so skipping it would
    miss real changes.
    Workflow bookkeeping is excluded in the git pathspec itself (0.3.2).

    `status`: the bytes of `git status --porcelain` when already available (P0-2 —
    `turn_snapshot` calls it once and passes it down, avoiding two git calls per
    turn). None → fetch it here.

    None means "no evidence", not "the repo is clean" — the caller must treat None
    as a fallback to the old behaviour.
    """
    if status is None:
        status = _git(cwd, "status", "--porcelain", "--untracked-files=all", "--", ":(top)", *_EXCLUDE)
    if status is None:
        return None
    # a repo with no commit yet → no HEAD → rc!=0 → b""
    diff = _git(cwd, "diff", "HEAD", "--", ":(top)", *_EXCLUDE) or b""
    h = hashlib.sha256(status + b"\0" + diff)
    # Untracked files: porcelain prints `?? path`, which does not change when the
    # content changes, and `diff HEAD` never touches them — they need their own
    # mark or the change is missed (QC1.1).
    root = repo_root(cwd) or cwd
    budget, seen = UNTRACKED_HASH_BUDGET, 0
    for line in status.decode("utf-8", "replace").splitlines():
        if not line.startswith("?? "):
            continue
        seen += 1
        if seen > UNTRACKED_STAT_CAP:
            break
        rel = line[3:].strip().strip('"')
        mark, used = _untracked_mark(os.path.join(root, rel), budget)
        budget -= used
        if mark is not None:
            h.update(f"\0{rel}:{mark}".encode())
    return h.hexdigest()


def repo_status_paths(cwd, limit=400, status=None):
    """Paths differing from HEAD (status flags dropped, renames keep the target).

    Same exclusion zone as `repo_status_digest` — the decision and the naming must
    look at exactly one set of paths; a mismatch is the source of the false block
    of 0.3.1.

    `status`: the bytes of `git status --porcelain` when already available (P0-2,
    see `repo_status_digest`).
    """
    out = status if status is not None else _git(
        cwd, "status", "--porcelain", "--untracked-files=all", "--", ":(top)", *_EXCLUDE)
    if out is None:
        return []
    paths = []
    for line in out.decode("utf-8", "replace").splitlines():
        if len(line) > 3:
            path = line[3:].strip().strip('"')
            paths.append(path.split(" -> ")[-1])
        if len(paths) >= limit:
            break
    return paths


# ------------------------------------------------- plan tick state (the fence)
#
# Both the status line and the tick-forcing fence need to know where the plan
# "stands". The whole FILE is hashed (rather than counting `[x]` marks) because
# `[ ]` → `[~]` is a valid update that leaves the `[x]` count untouched — counting
# `[x]` would miss exactly the "task started" mark.

#
# The `>` mark = the task is DISPATCHED to a sub-agent currently running (team
# mode). It differs from `~` in that `~` means the leader does it personally —
# and there may be only ONE; `>` runs in parallel, so there may be MANY.
# See skills/tdq-build/references/team-mode.md.
# Task codes: a letter first, then letters/digits/dots freely mixed — real plans
# carry `T2A.1` (a parallel branch inside one phase) and `T2.4b` (a variant). A
# narrower character class makes those tasks invisible to both the tick counter
# and the anti-stop gate.
_TASK_LINE = re.compile(r"^\s*-\s*\[( |~|x|>)\]\s*\*\*([A-Za-z][A-Za-z0-9.]*)\*\*")


def _plan_path(cwd, state):
    """Absolute path of the plan of the active request, or None when there is none."""
    rel = state.get("plan_file")
    if not rel:
        req = state.get("active_request")
        if not req:
            return None
        rel = os.path.join("docs", "tdq", "plan", f"{req}.md")
    return rel if os.path.isabs(rel) else os.path.join(cwd, rel)


def plan_tick_state(cwd):
    """Checkbox state of the current plan. Never raises."""
    trong = {"path": None, "exists": False, "sha": "",
             "has_doing": False, "all_done": False, "total": 0, "doing_count": 0,
             "dispatched_count": 0, "dispatched_ids": []}
    try:
        state = load(cwd, heal=False) or {}
    except Exception:
        return trong
    path = _plan_path(cwd, state)
    if path is None:
        return trong
    trong["path"] = path
    try:
        with open(path, encoding="utf-8") as f:
            noi_dung = f.read()
        sha = sha256_file(path)
    except OSError:
        return trong

    tong = xong = dang = 0
    da_giao = []
    for line in noi_dung.splitlines():
        m = _TASK_LINE.match(line)
        if not m:
            continue
        tong += 1
        if m.group(1) == "x":
            xong += 1
        elif m.group(1) == "~":
            dang += 1
        elif m.group(1) == ">":
            da_giao.append(m.group(2))

    # `has_doing` = "work is in flight" in the broad sense: the leader is doing it
    # OR a sub-agent is. The fence uses this flag to know whether the turn left
    # work unfinished.
    trong.update(exists=True, sha=sha, total=tong, doing_count=dang,
                 dispatched_count=len(da_giao), dispatched_ids=da_giao,
                 has_doing=dang > 0 or bool(da_giao),
                 all_done=tong > 0 and xong == tong)
    return trong


# The Definition of Done checkbox is a SECOND counter, deliberately not `_TASK_LINE`.
# A DoD line carries no bold task code (`- [ ] Q1 the condition — the command`), and
# widening `_TASK_LINE` to reach it would let DoD lines into the task counter that feeds
# stop_gate, edit_gate and the status line — `all_done` and the ETA would both go wrong.
# So: same file, different section, different counter.
_DOD_HEADING = "## definition of done"
_DOD_LINE = re.compile(r"^\s*-\s*\[( |~|x|>)\]\s+")
_FENCE = re.compile(r"^\s*(```|~~~)")


def _dod_section(noi_dung):
    """Every line under a DoD heading, up to the next `## ` heading.

    Three details the naive version got wrong. A plan may carry the heading MORE THAN ONCE
    (a round-2 section, a split plan), so all of them are collected, not just the first.
    The heading is matched case-insensitively and may carry a suffix (`## Definition of Done
    (19)`). And a heading inside a fenced block is a TEMPLATE, not a real section — skill
    templates show the DoD shape that way — so fenced lines are skipped entirely.
    """
    phan = []
    trong_muc = False
    trong_rao = False
    for line in noi_dung.splitlines():
        if _FENCE.match(line):
            trong_rao = not trong_rao
            continue
        if trong_rao:
            continue
        if line.startswith("## "):
            trong_muc = line.strip().lower().startswith(_DOD_HEADING)
            continue
        if trong_muc:
            phan.append(line)
    return phan


def dod_tick_state(cwd):
    """Checkbox state of the plan's Definition of Done section. Never raises."""
    trong = {"path": None, "exists": False, "total": 0, "done": 0, "all_done": False}
    try:
        state = load(cwd, heal=False) or {}
    except Exception:
        return trong
    path = _plan_path(cwd, state)
    if path is None:
        return trong
    trong["path"] = path
    try:
        with open(path, encoding="utf-8") as f:
            noi_dung = f.read()
    except (OSError, UnicodeDecodeError):
        return trong

    tong = xong = 0
    for line in _dod_section(noi_dung):
        m = _DOD_LINE.match(line)
        if not m:
            continue
        tong += 1
        if m.group(1) == "x":
            xong += 1
    trong.update(exists=True, total=tong, done=xong,
                 all_done=tong > 0 and xong == tong)
    return trong


# The qc file is the machine-readable proof that QC already ran and passed. Its verdict
# column is the LAST cell of a table row, so the reader takes the last cell rather than
# searching the whole line: a row whose "Ket qua" cell merely mentions the word PASS must
# not be counted twice.
_QC_ROW = re.compile(r"^\s*\|.*\|\s*(PASS|FAIL|SKIP|TODO|PENDING|N/A)\s*\|\s*$")


def qc_result_state(cwd):
    """PASS/FAIL tally of the qc file of the active request. Never raises."""
    trong = {"path": None, "exists": False, "passed": 0, "failed": 0, "pending": 0,
             "all_pass": False}
    try:
        state = load(cwd, heal=False) or {}
    except Exception:
        return trong
    req = state.get("active_request")
    if not req:
        return trong
    path = os.path.join(cwd, "docs", "tdq", "qc", f"{req}.md")
    trong["path"] = path
    try:
        with open(path, encoding="utf-8") as f:
            noi_dung = f.read()
    except (OSError, UnicodeDecodeError):
        return trong

    dat = hong = cho = 0
    for line in noi_dung.splitlines():
        m = _QC_ROW.match(line)
        if not m:
            continue
        if m.group(1) == "PASS":
            dat += 1
        elif m.group(1) == "FAIL":
            hong += 1
        else:
            # SKIP / TODO / PENDING / N/A: the item has no verdict yet. Not a failure, but
            # not proof either — the reminder must not fire off a half-finished QC.
            cho += 1
    trong.update(exists=True, passed=dat, failed=hong, pending=cho,
                 all_pass=dat > 0 and hong == 0 and cho == 0)
    return trong


def task_open_count(cwd):
    """How many task boxes of the current plan are not `[x]` yet. Never raises.

    A separate reader rather than a new key on `plan_tick_state`: four call sites depend on
    that function's exact return shape, and one of them asserts the key set.
    """
    try:
        state = load(cwd, heal=False) or {}
    except Exception:
        return 0
    path = _plan_path(cwd, state)
    if path is None:
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            noi_dung = f.read()
    except (OSError, UnicodeDecodeError):
        return 0
    return sum(1 for line in noi_dung.splitlines()
               if (m := _TASK_LINE.match(line)) and m.group(1) != "x")


def turn_snapshot(cwd):
    """Turn-start state: today's log + the repo fingerprint + the list of dirty
    paths + the plan fingerprint (to know whether a checkbox moved this turn)."""
    log_rel = today_log_rel()
    try:
        log_sha = sha256_file(os.path.join(cwd, log_rel))
    except OSError:
        log_sha = None
    status = _git(cwd, "status", "--porcelain", "--untracked-files=all", "--", ":(top)", *_EXCLUDE)
    return {"log_rel": log_rel, "log_sha": log_sha,
            "repo_sha": repo_status_digest(cwd, status=status),
            "repo_paths": repo_status_paths(cwd, status=status),
            "plan_sha": plan_tick_state(cwd)["sha"]}
# ----------------------------------------------------------- safe enums (S4)

def normalize_lane(raw):
    """Alias -> machine identifier ("quick"/"full"). Unrecognised -> None (the
    caller decides whether to fail or ignore). This is the ONLY entry point for a
    lane typed by the user."""
    if not isinstance(raw, str):
        return None
    return LANE_ALIASES.get(raw.strip().lower())


def lane_label(lane):
    """The label PRINTED to a reader. Being a display layer it does NOT validate:
    an unknown lane comes back as it was, None comes back empty — printing
    something ugly beats blowing up."""
    if not lane:
        return ""
    return LANE_LABELS.get(lane, lane)


def normalize_mode(raw):
    """Alias -> machine identifier ("main"/"subagent"). The ONLY entry point for a
    mode typed by the user. Unrecognised -> None; the caller decides."""
    if not isinstance(raw, str):
        return None
    # Collapse runs of whitespace into one space: people type "sub-agent  implement".
    return MODE_ALIASES.get(" ".join(raw.strip().lower().split()))


def mode_label(mode):
    """The label PRINTED to a reader, same rule as lane_label: an unknown mode comes
    back as it was, None comes back empty — a display layer, not a check layer."""
    if not mode:
        return ""
    return MODE_LABELS.get(mode, mode)


def effective_lane(state, warn=True):
    lane = (state or {}).get("lane")
    if lane in VALID_LANES:
        return lane
    if warn:
        _warn(f"invalid lane in state: {lane!r} — treated as no lane chosen.")
    return None


# The approval gates of each lane, in the order they must be passed. An empty or
# unknown lane uses `None`: staying silent on a broken state would let work slip
# through, so all three gates are still asked for, as in the older version.
CONG_THEO_LANE = {
    "quick": ("quick",),
    "full": ("spec", "plan"),
    None: ("spec", "plan", "quick"),
}


def cong_dang_cho(state):
    """The approval gate still missing for the running lane, or None when all passed.

    Why one shared function: `edit_gate` and `stop_gate` both need this answer. Back
    when each wrote its own, `stop_gate` walked a hard-coded list ("spec", "plan",
    "quick") without looking at the lane — lane quick has no `spec` gate at all, so
    `spec_approved` stayed False forever and the hook kept saying "the spec is not
    approved" even for a closed request. A gate that cries wolf often enough is no
    longer heard when it is right.
    """
    lane = effective_lane(state, warn=False)
    for cong in CONG_THEO_LANE.get(lane, CONG_THEO_LANE[None]):
        if not (state or {}).get(f"{cong}_approved"):
            return cong
    return None


def effective_phase(state, warn=True):
    phase = (state or {}).get("phase")
    if phase in VALID_PHASES:
        return phase
    if warn:
        _warn(f"invalid phase in state: {phase!r} — treated as idle. "
              "Restore with: python3 scripts/tdq_state.py set phase=<idle|analyze|spec|plan|implement|qc|report>")
    return "idle"


def effective_mode(state, warn=True):
    mode = (state or {}).get("implement_mode")
    if mode in VALID_MODES or mode is None:
        return mode
    if warn:
        _warn(f"invalid implement_mode: {mode!r} — treated as no mode settled.")
    return None


# --------------------------------------------------------------- phase table

# The ONE source of truth for "where am I, what comes next".
# The docs (tdq-conventions) quote it from here; tests pin it.
PHASE_TABLE = {
    "no_state": {
        "entry": "No TDQ request is open",
        "action": "Ask the user to pick a lane, then open a new request",
        "cmd": "python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]",  # i18n-allow
        "checklist": [
            "Summarise the user's request in 3-5 lines",
            "Ask the user to pick a mode: express (a small, clear job) or "
            "deep (Analysis→Spec→Plan→Implement→QC→Report)",
            "Run the init command above with a slug shaped YYYY-MM-DD-HHMM-<kebab, <=5 words, no accents>",
            "Write the request verbatim into docs/tdq/brief/<slug>.md under the first section",
        ],
        "done_when": "state.json has active_request and lane",
        "forbidden": "Editing code before a request is open",
    },
    "analyze": {
        "entry": "A request is open, deep mode",
        "action": "Read the code, research, interview the user until nothing is vague",
        "cmd": "python3 scripts/tdq_state.py set phase=spec",
        "checklist": [
            "Capability inventory (B0): run `python3 scripts/skill_inventory.py`, fill the "
            "verdict table into the understanding section of docs/tdq/brief/<slug>.md",
            "Read the related code/docs, write them into docs/tdq/research/<slug>.md",
            "Scope round first (which areas + context in numbers) per "
            "skills/tdq-intake/references/scope-round.md, or write one line skipping it with a reason",
            "Ask the detail questions only inside the areas the user picked, write them "
            "into the Q&A section of docs/tdq/brief/<slug>.md",
            "Settle the decisions into the understanding section of docs/tdq/brief/<slug>.md",
            "No question left that changes the outcome → run the command above",
        ],
        "done_when": "No question is left that would change the outcome",
        "forbidden": "Writing the spec while anything is still vague",
    },
    "spec": {
        "entry": "Analysis is finished",
        "action": "Write the spec (with its roadmap section), register spec_file, present the summary and STOP for the user's approval",
        "cmd": "python3 scripts/tdq_state.py approve spec --by \"<the user's sentence verbatim>\"",
        "checklist": [
            "Write docs/tdq/spec/<slug>.md (scope in/out, outputs, roadmap, QC + DoD)",
            "Run: python3 scripts/tdq_state.py set spec_file=docs/tdq/spec/<slug>.md",
            "Present a spec summary of at most 50 lines in chat",
            "Print the approval invite line, then STOP",
            "The user approves → run the approve command above RIGHT AWAY, then write the "
            "plan in the SAME turn (never make the user send another message)",
        ],
        "done_when": "spec_approved = true",
        "forbidden": "Inferring that the user approved; making the user send one more turn before the plan is written",
    },
    "plan": {
        "entry": "spec_approved = true",
        "action": "Write the plan with a PROPOSED mode, register plan_file, present it and STOP for approval",
        "cmd": "python3 scripts/tdq_state.py approve plan --by \"<verbatim>\"",
        "checklist": [
            "PROPOSE the run mode inside the plan itself (main|subagent) + the reason — "
            "do not ask about the mode here; the mode gate is its own phase right after",
            "Write docs/tdq/plan/<slug>.md: one task = one job + one test, with a [ ] checkbox",
            "Run: python3 scripts/tdq_state.py set plan_file=docs/tdq/plan/<slug>.md",
            "Present the plan summary, invite the user to approve, then STOP",
            "The user approves → run the approve command above RIGHT AWAY, then ask about the "
            "mode in the SAME turn (if the user already named a mode, add --mode and build)",
        ],
        "done_when": "plan_approved = true",
        "forbidden": "Editing code before the plan is approved; withholding the approval record until the user names a mode",
    },
    "mode": {
        "entry": "plan_approved = true but implement_mode is not settled",
        "action": "Explain the 2 modes briefly, ask the user to choose, STOP for the answer",
        "cmd": "python3 scripts/tdq_state.py approve plan --mode <main|subagent> --by \"<verbatim>\"",
        "checklist": [
            "Present the mode block per the user-facing block rules, one line of meaning per mode: "
            "inline implement = I do it sequentially right here; "
            "sub-agent implement = several agents run in parallel",
            "Present 1-3 lines of reasoning for the proposal, grounded IN THE PLAN itself: task "
            "count, tasks chained by dependency, how many files several tasks touch at once, "
            "whether an (mcp) label is present; plus one sentence on why not the other option. "
            "NEVER settle it for the user",
            "STOP and wait for the user to choose",
            "The user chooses → run the approve command above RIGHT AWAY, then build in the SAME turn",
        ],
        "done_when": "implement_mode is not null",
        "forbidden": "Editing code before the mode is settled; choosing the mode for the user",
    },
    "implement": {
        "entry": "plan_approved = true and implement_mode is settled",
        "action": "Do the whole plan in one turn, mark [~] when a task starts, red→green, flip to [x] as soon as it passes",
        "cmd": "python3 scripts/tdq_state.py set phase=qc",
        "checklist": [
            "Do the tasks in the order the plan gives",
            "Each task: mark [~] → write the test (red) → code → test green → flip to [x] in the plan RIGHT AWAY",
            "Never stop midway to ask 'shall I continue?'",
            "All tasks done → run the command above",
        ],
        "done_when": "Every task in the plan is ticked [x]",
        "forbidden": "Stopping midway; batching the ticks at the end of the turn; leaving several tasks marked [~]. Enforced, not merely advised: the Stop hook blocks the end of the turn with [TDQ:UNFINISHED] while a task is still open, and the only legal way out is `tdq_state.py pause --ly-do \"<why>\"`, whose reason is shown to the user",
    },
    "qc": {
        "entry": "Implementation is finished",
        "action": "Run the spec's Definition of Done, record the results, fix what fails",
        "cmd": "python3 scripts/tdq_state.py set phase=report",
        "checklist": [
            "Run every QC item of the spec, write the evidence into docs/tdq/qc/<slug>.md",
            "FAIL → add a fix task to the plan (no re-approval needed) and carry on",
            "Repeat until every item PASSes",
        ],
        "done_when": "Every QC item of the spec PASSes, with evidence",
        "forbidden": "Ignoring a failing test; reporting PASS without running it",
    },
    "report": {
        "entry": "QC has PASSed",
        "action": "Write a short report (10-20 lines recommended, no hard limit) then ask the user about committing",
        "cmd": "python3 scripts/tdq_state.py set phase=idle",
        "checklist": [
            "Write docs/tdq/reports/<slug>.md briefly (10-20 lines recommended): "
            "what was done, the QC result, what is still limited",
            "Append to the working log docs/workinglog/<today>.md",
            "Ask the user: commit or not?",
        ],
        "done_when": "The report is written and the user has been asked about committing",
        "forbidden": "Committing or pushing before the user asks for it",
    },
    "idle": {
        "entry": "Finished, or no request opened yet",
        "action": "Wait for a new request from the user",
        "cmd": "python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]",  # i18n-allow
        "checklist": [
            "A new request arrives → summarise it, ask for the lane, run the init command above",
        ],
        "done_when": "A new request is open",
        "forbidden": "Overwriting an unfinished request without asking the user",
    },
    "quick_analyze": {
        "entry": "lane = quick and phase = analyze, before the express approval",
        "action": "Analyse and write what you learned into docs/tdq/brief/<slug>.md, then go "
                  "straight on to the mini spec/plan — this phase has NO approval gate",
        "cmd": "python3 scripts/tdq_state.py set phase=implement",
        "checklist": [
            "B1 read the code — ALWAYS, never skipped. The target is a code symbol → call "
            "mcp__lsp__* and lumen IN PARALLEL and merge both layers before reading; grep is "
            "the last layer",
            "B0 capability inventory — ONLY when the request touches ground with no precedent "
            "(no earlier report under docs/tdq/report/ touched the same directory). Touching "
            "scripts/tdq_state.py or hooks/ again → skip it, the answer is already known",
            "B2 research through tavily-primary — ONLY when an unknown outside the repo exists "
            "(a library, an API, a version, third-party behaviour). Hand it to a sub-agent, "
            "which returns a digest of at most 1,500 characters",
            "SKIPPING B0 or B2 costs one line: write the reason under the mini-plan's Scope "
            "section. A step dropped in silence is a QC defect",
            "Write what you settled into the brief's 'Hiểu & kiến thức' section, then move on "
            "to the mini spec/plan — do NOT stop to wait for the user here",
        ],
        "done_when": "The brief holds what the analysis settled, and every skipped step has its "
                     "one-line reason ready for the mini-plan",
        "forbidden": "Skipping B1; grepping for a symbol with no LSP+lumen attempt first; "
                     "dropping B0 or B2 without writing the reason; waiting for an approval "
                     "that this phase does not have",
    },
    "quick": {
        "entry": "lane = quick",
        "action": "Analyse → a mini spec/plan merged into one file → wait for approval → write the working log FIRST → implement → QC against the DoD (ON by default) → a fix round if it FAILs",
        # A26: matches intake — quick has a no-QC variant ("approve quick without QC"
        # → --no-qc, which requires --by).
        "cmd": "python3 scripts/tdq_state.py approve quick [--no-qc] --by \"<the user's sentence verbatim>\"",
        "checklist": [
            "Analyse: read the related code; an unknown outside the repo (a library, an API, a "
            "version) → web search through tavily-primary before writing anything",
            "Interview while a question can still CHANGE the outcome — per interview.md; "
            "close the round with the 'anything to add?' question only when that round holds "
            "at least one question, otherwise go straight on",
            "Write the mini spec/plan MERGED into docs/tdq/plan/<slug>.md (<=40 lines: scope in/out, "
            "tasks with tests, DoD) then present a summary of at most 10 lines in chat, "
            "with one line naming the capabilities that will be used",
            "Print the approval invite line (including the no-QC variant), then STOP",
            "The user approves → run the approve command above (--no-qc ONLY when the user says "
            "so explicitly; silence about QC means QC RUNS)",
            "Append the plan summary to docs/workinglog/<today>.md BEFORE editing any code",
            "Implement task by task: mark [~] on the task BEFORE editing code "
            "(the edit_gate hook BLOCKS when the plan has no [~]), red→green, "
            "flip to [x] AS SOON AS that task's test is green — never batch the ticks",
            "QC: one command per DoD line, plus an item running each task's test. "
            "The evidence goes into the QC section of the plan. "
            "When quick_qc_skipped = true the QC section holds a single line "
            "'SKIPPED at the user's request: \"<verbatim>\"'",
            "QC FAIL or a bug spotted → fix it. "
            "Add tasks to the plan's 'QC round N — fixes' section, fix red→green. "
            "Re-run the FAILed items plus any item the fix could have broken. "
            "Three rounds maximum; over the cap STOP, tell the user, propose switching to deep mode",
            "Close the job: run `python3 scripts/tdq_state.py set phase=idle` — the terminal of express mode",
        ],
        "done_when": "quick_approved = true, the log is written, the plan's QC section exists (evidence or the skipped-at-user's-request line), no red test is left, phase is back to idle",
        "forbidden": "Implementing before the working log is written; batching the ticks at the end of the turn or leaving several tasks marked [~]; closing the job with a red test or a known bug; running set phase=idle after the 3-round fix cap without telling the user",
    },
}


# The variant of phase `implement` when the user settles on mode `subagent`. Kept
# OUT of PHASE_TABLE on purpose: it is not a phase (state still records
# `implement`, and `set phase=` does not accept this value) and it must not grow
# an extra row in the generated phase table. Looked up via phase_row(), not
# phase_key().
IMPLEMENT_SUBAGENT_ROW = {

    "entry": "plan_approved = true and implement_mode = subagent",
    "action": "Assign the WHOLE plan first (step 0), then release wave by wave to sub-agents, "
              "merging one wave before releasing the next — the leader only does what cannot be split",
    "cmd": "python3 scripts/tdq_state.py set phase=qc",
    "checklist": [
        "Step 0: python3 scripts/tdq_team.py assign — read the whole plan, write the map "
        "docs/tdq/team/<slug>.json (per task: dispatched / kept + reason + file zone + wave)",
        "python3 scripts/tdq_team.py audit — a map breaking the rules exits non-zero, fix it and re-run",
        "python3 scripts/tdq_team.py wave — take the next wave, open a branch with `open <task-id>`, "
        "mark [>] on EVERY task just dispatched (many [>] is valid, [~] still only one)",
        "A sub-agent reports done → `check <branch>` to scan for conflicts → `merge <branch>` → flip [>] to [x] RIGHT AWAY",
        "Wave finished → `clean` to clean the worktrees, then `wave` for the next wave; repeat until no task is left",
    ],
    "done_when": "Every task in the plan is ticked [x] and no leftover worktree remains",
    "forbidden": "Doing a task the map marked as dispatched yourself on main; merging before `check` passes; "
                 "leaving several tasks marked [~]",
}


PHASE_ORDER = ["no_state", "analyze", "spec", "plan", "mode", "implement", "qc",
               "report", "idle", "quick_analyze", "quick"]


_SCRIPT_PATH = re.compile(r"python3 scripts/(\S+\.py)")


def plugin_root_cmd(cmd):
    """A40: the command form for docs running in the plugin context (conventions §1)."""
    return _SCRIPT_PATH.sub(r'python3 "~/.gemini/config/plugins/tdq-workflow/scripts/\1"', cmd)


def render_phases_md(plugin_root=False):
    """Generate the phase-table doc out of PHASE_TABLE — that doc is NEVER hand-written.

    Regenerate with: python3 scripts/tdq_state.py phases-doc > <file>
    (add --plugin-root for the skills/tdq-conventions copy — paths per conventions §1).
    tests/test_phase_table.py::test_docs_match_constant pins this synchronisation.
    """
    conv = plugin_root_cmd if plugin_root else (lambda c: c)
    lines = [
        "# TDQ phase table (generated — do NOT hand-edit)",
        "",
        "Regenerate: `" + conv("python3 scripts/tdq_state.py") + " phases-doc"
        + (" --plugin-root" if plugin_root else "") + " > <file>`.",
        "Source: the `PHASE_TABLE` constant in `scripts/tdq_state.py`.",
        "Whatever phase you stand in, do only that phase's job, then run exactly its command.",
        "",
        "| phase | entered when | the single job | command onward | done when | forbidden |",
        "|---|---|---|---|---|---|",
    ]
    def cell(text):
        # A `|` inside <quick|full> would cut the markdown cell, even inside backticks.
        return str(text).replace("|", "\\|")

    for name in PHASE_ORDER:
        row = PHASE_TABLE[name]
        lines.append("| `{}` | {} | {} | `{}` | {} | {} |".format(
            name, cell(row["entry"]), cell(row["action"]), cell(conv(row["cmd"])),
            cell(row["done_when"]), cell(row["forbidden"])))
    lines.append("")
    lines.append("The commands verbatim (copy-paste, no escaping):")
    lines.append("")
    lines.append("```")
    for name in PHASE_ORDER:
        lines.append(f"{name}: {conv(PHASE_TABLE[name]['cmd'])}")
    lines.append("```")
    lines.append("")
    # The per-phase checklists are NOT generated here (dropped 2026-08-09): they
    # repeat the SKILL.md of that very phase. For the full checklist run
    # `tdq_state.py next`.
    lines.append("Detailed checklist of the running phase: `"
                 + conv("python3 scripts/tdq_state.py") + " next`.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def phase_key(state):
    """The PHASE_TABLE lookup key for the current state."""
    if not state or not state.get("active_request"):
        return "no_state"
    lane = effective_lane(state, warn=False)
    if lane == "quick":
        # A6: the terminal of lane quick — approved AND phase set to idle means done
        # (approve quick pushes phase=implement, so a later idle can only be a
        # deliberate close).
        if state.get("quick_approved") and effective_phase(state, warn=False) == "idle":
            return "idle"
        # Phương án 2a (2026-09-01): bước phân tích của lane nhanh có hàng riêng để
        # NHÌN THẤY được, nhưng không kèm cổng duyệt — `CONG_THEO_LANE["quick"]` vẫn
        # đúng một cổng. Đã duyệt rồi thì phân tích xong từ lâu, không quay lại hàng này.
        if (not state.get("quick_approved")
                and effective_phase(state, warn=False) == "analyze"):
            return "quick_analyze"
        return "quick"
    return effective_phase(state, warn=False)


def phase_row(state):
    """The PHASE_TABLE row to DISPLAY for the current state.

    Unlike `phase_key`, this function knows the mode. Phase `implement` has two
    wholly different jobs — the leader working alone (`main`) and the leader
    steering a team (`subagent`) — while state records the single word
    `implement`, so the fork lives here.
    """
    key = phase_key(state)
    if key == "implement" and effective_mode(state or {}, warn=False) == "subagent":
        return IMPLEMENT_SUBAGENT_ROW
    return PHASE_TABLE[key]


# ------------------------------------------------------------------ next

def _mark(approved, registered):
    if approved:
        return "✔"
    return "⏳ awaiting approval" if registered else "—"


def next_headline(cwd, state):
    """Line 1 of `next` — also the entire output of `next --brief`."""
    if not state or not state.get("active_request"):
        return f"[TDQ:NEXT] no request · phase idle · Project: {os.path.abspath(cwd)}"
    # phase_key, not the raw phase: lane quick keeps phase=idle while work is still
    # left — printing "idle" makes the model think it is done (QC1.1).
    return (f"[TDQ:NEXT] {state.get('active_request')} · lane {effective_lane(state, warn=False) or '?'} "
            f"· phase {phase_key(state)} · Project: {os.path.abspath(cwd)}")


def render_next(cwd, state, brief=False, compact=False):
    """The 5-part block (spec §2.2), at most 20 lines.

    brief=True   → exactly the 1 headline (used by UserPromptSubmit, every turn).
    compact=True → no checklist, plus a pointer to the `next` command (used by
                   SessionStart, where the cap is 600 characters and the rule line
                   must sit on top — see hooks/scripts/session_start.py).
    """
    if state and state.get("active_request"):
        effective_lane(state)          # warns (with recovery hints) on a bad enum
        effective_phase(state)
    head = next_headline(cwd, state)
    if brief:
        return head
    row = phase_row(state)
    lines = [head, f"Next: {row['action']}", "Command:", f"  {row['cmd']}"]
    if compact:
        lines.append("Full checklist: python3 scripts/tdq_state.py next")
    else:
        lines.append("Checklist (copy into your answer, tick as you go):")
        lines += [f"- [ ] {item}" for item in row["checklist"]]
    lines.append(f"Done when: {row['done_when']}")
    return "\n".join(lines)


def render_state_md(cwd, state):
    """A markdown mirror of at most 30 lines for an agent/user to read (spec §2.3.1)."""
    state = state or default_state()
    lane = effective_lane(state, warn=False)
    row = phase_row(state)
    spec = state.get("spec_file") or "(none)"
    if state.get("spec_file"):
        spec += " — " + ("✔ approved" if state.get("spec_approved") else "⏳ awaiting approval")
    plan = state.get("plan_file") or "(none)"
    if state.get("plan_file"):
        plan += " — " + ("✔ approved" if state.get("plan_approved") else "⏳ awaiting approval")
    quick = "✔ approved" if state.get("quick_approved") else "⏳ awaiting approval"
    lines = [
        "# TDQ STATE (generated — do not hand-edit)",
        f"Updated: {state.get('updated_at') or now_iso()} · Project: {os.path.abspath(cwd)} · schema 3",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Request | {state.get('active_request') or '(none)'} |",
        f"| Lane | {lane or '(not chosen)'} |",
        f"| Phase | {effective_phase(state, warn=False)} |",
        f"| Spec | {spec} |",
        f"| Plan | {plan} |",
        f"| Quick approval | {quick if lane == 'quick' else '(not applicable)'} |",
        f"| Doc language | {state.get('doc_lang') or DEFAULT_DOC_LANG} |",
        f"| Run mode | {effective_mode(state, warn=False) or '(not settled)'} |",
        "",
        "## Where we are",
        f"{row['entry']}. Forbidden: {row['forbidden']}.",
        "",
        "## What comes next",
        row["action"] + ".",
        "```",
        row["cmd"],
        "```",
        f"Done when: {row['done_when']}",
        "",
        "> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ turn log

def turn_log_append(cwd, kind, session=None, **fields):
    """Append one event to the turn log. I/O error → swallowed (a hook must not break)."""
    row = {"ts": now_iso(), "session": session or "", "kind": kind}
    row.update(fields)
    path = turn_log_path(cwd)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return row


TURN_STALE_SECONDS = 6 * 3600


def _row_age_ok(row):
    try:
        ts = datetime.fromisoformat(row.get("ts", ""))
    except (ValueError, TypeError):  # A18: a numeric/None ts must not kill the hook
        return False
    if ts.tzinfo is None:
        ts = ts.astimezone()
    return (datetime.now(timezone.utc) - ts.astimezone(timezone.utc)).total_seconds() <= TURN_STALE_SECONDS


def turn_log_read(cwd, session=None):
    """Events of the current session, skipping rows older than 6 hours (RR12)."""
    rows = []
    try:
        with open(turn_log_path(cwd), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(row, dict):
                    continue
                if session is not None and row.get("session") != session:
                    continue
                if not _row_age_ok(row):
                    continue
                rows.append(row)
    except OSError:
        return []
    return rows


def turn_log_clear(cwd, session):
    """Drop this session's rows (at turn start). Other sessions' rows are kept."""
    path = turn_log_path(cwd)
    try:
        with open(path, "r", encoding="utf-8") as f:
            kept = []
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    row = json.loads(stripped)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("session") == session:
                    continue
                if isinstance(row, dict) and not _row_age_ok(row):
                    continue
                kept.append(line if line.endswith("\n") else line + "\n")
    except OSError:
        return
    try:
        _atomic_write(path, "".join(kept))
    except OSError:
        pass


# ---------------------------------------------------------- context dedupe

PROMPT_CONTEXT_REL = os.path.join("docs", "tdq", ".tdq-prompt-last.json")


def prompt_context_path(cwd):
    return os.path.join(cwd, PROMPT_CONTEXT_REL)
def prompt_context_last(cwd, session):
    """Digest of the [TDQ:...] block printed last turn for this session, None if there is none."""
    try:
        with open(prompt_context_path(cwd), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("session") != session:
        return None
    return data.get("digest")


def prompt_context_save(cwd, session, digest):
    """Store the digest just printed — turn_log_clear never touches this file
    (dedupe must survive ACROSS turns, unlike the turn log wiped at each turn start)."""
    path = prompt_context_path(cwd)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _atomic_write(path, json.dumps({"session": session, "digest": digest}, ensure_ascii=False))
    except OSError:
        pass


# ------------------------------------------------------------------- CLI

def _parse_value(raw):
    lowered = raw.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return raw


DONE_PHASES = {"idle", "report"}


def _unfinished(state):
    """An unfinished request: not yet at a terminal phase, or some gate already approved."""
    if state.get("phase") not in DONE_PHASES:
        return True
    return any(state.get(k) for k in ("spec_approved", "plan_approved", "quick_approved"))


def _parse_approve_args(rest):
    """-> (target, mode, by, no_qc). Fails only on genuinely wrong syntax."""
    if not rest:
        _fail("Missing approval target (spec|plan|quick).")
    if rest[0] == "diagram":
        _fail(LOI_SO_DO_DA_GO)
    target, mode, by, no_qc = rest[0], None, None, False
    # Aliases of lane quick: typing "approve nhanh" also writes the quick_* keys.
    if target not in APPROVE_TARGETS and normalize_lane(target) == "quick":
        target = "quick"
    if target not in APPROVE_TARGETS:
        _fail(f"Invalid approval target: {target} "
              "(spec|plan|quick, aliases of quick: nhanh|express)")  # i18n-allow
    i = 1
    while i < len(rest):
        flag = rest[i]
        if flag == "--no-qc":
            # QC on quick is ON by default — only lane quick has this opt-out path.
            if target != "quick":
                _fail(f"Flag --no-qc belongs to `approve quick` only, not to {target}.")
            no_qc = True
            i += 1
            continue
        if flag in ("--mode", "--by"):
            if i + 1 >= len(rest):
                _fail(f"Missing value for {flag}")
            value = rest[i + 1]
            if flag == "--mode":
                # Through normalize_mode: the labels shown at gate mode ("inline",
                # "sub-agent implement") must land as the machine identifier.
                mode = normalize_mode(value)
                if mode is None:
                    _fail("Invalid mode (main|inline | subagent|sub-agent).")
            else:
                by = value[:BY_MAX]
            i += 2
            continue
        # allow "approve plan main" (shorthand) — the mode sits right after the target.
        # Aliases accepted too, but only while no mode is set: a stray argument must still blow up.
        if mode is None and normalize_mode(flag):
            mode = normalize_mode(flag)
            i += 1
            continue
        _fail(f"Invalid argument: {flag}")
    if no_qc and not by:
        # Skipping QC must leave the user's own words, otherwise who skipped it and why is lost.
        _fail('Skipping QC requires --by "<the user\'s exact words>" so a trace remains.')
    return target, mode, by, no_qc


def _file_changed_since_approval(cwd, state, target):
    """True when the spec/plan file changed since it was approved. It tells
    'a redundant re-approve command' apart from 'the file was edited during QC and
    re-approved' — the latter must re-record the sha256, or the mismatch warning hangs forever."""
    if target not in ("spec", "plan"):
        return False
    old = state.get(f"{target}_sha256")
    rel = state.get(f"{target}_file")
    if not old or not rel:
        return False
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    try:
        return sha256_noi_dung(path) != old
    except OSError:
        return False


def _cli_approve(cwd, rest):
    """Record that the user approved. Not a gate: it warns on a mismatch but
    STILL writes and always exits 0 — deadlock-by-gate is what 0.2.0 removed."""
    target, mode, by, no_qc = _parse_approve_args(rest)
    state = load(cwd)
    if state is None:
        _warn("No state yet — building the default state then recording the approval. Run init first.")
        state = default_state()
    stamp = state.get("updated_at")

    if state.get(f"{target}_approved") and not _file_changed_since_approval(cwd, state, target):
        print(f"ℹ️ {target} was already approved at {state.get(f'{target}_approved_at')} — not recorded again, move on.")
        if mode and state.get("implement_mode") != mode:
            state["implement_mode"] = mode
            # This is exactly the path where the user answers gate `mode`: the plan was
            # approved earlier, this call only settles the mode → open the way to implement.
            if target == "plan" and effective_phase(state, warn=False) == "mode":
                state["phase"] = "implement"
            save(cwd, state, expect_updated_at=stamp)
            print(f"ℹ️ implement_mode updated to {mode}.")
        return
    reapproved = bool(state.get(f"{target}_approved"))

    lane = effective_lane(state)
    if not state.get("active_request"):
        _warn("No TDQ request is open — recording anyway, but you should run init first.")
    if target == "quick" and lane != "quick":
        _warn(f"Approving quick while the request sits in lane {lane}.")
    if target in ("spec", "plan") and lane != "full":
        _warn(f"Approving {target} while the request sits in lane {lane}.")
    if target == "plan" and not state.get("spec_approved"):
        _warn("Approving the plan while no spec approval is recorded — check the order.")

    if target in ("spec", "plan"):
        rel = state.get(f"{target}_file")
        if not rel:
            _warn(f"{target}_file is not registered in state — cannot compute the sha256.")
        else:
            path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
            try:
                state[f"{target}_sha256"] = sha256_noi_dung(path)
            except OSError:
                _warn(f"Cannot read {rel} — skipping the sha256.")

    state[f"{target}_approved"] = True
    state[f"{target}_approved_at"] = now_iso()
    state[f"{target}_approved_by"] = by
    if mode:
        state["implement_mode"] = mode
    if target == "quick":
        # A6: quick never walks the phase table — push implement so that `set phase=idle`
        # at closing time becomes a terminal distinguishable from the idle before approval.
        state["phase"] = "implement"
        state["quick_qc_skipped"] = no_qc
    if target == "plan":
        # The mode gate is split from the plan gate: approving the plan without settling the
        # mode stops at phase `mode` (explain + ask). A user who named the mode inside the
        # approval sentence skips that gate and goes straight to implement — never re-ask.
        state["phase"] = "implement" if state.get("implement_mode") else "mode"
    save(cwd, state, expect_updated_at=stamp)
    if no_qc:
        # The timestamped line comes out of _info (stderr, silenced by TDQ_LOG=0);
        # the ✅ stdout line below carries no timestamp, so it cannot serve as this log trace.
        _info(f'Recorded that the user SKIPPED QC for quick on request: "{by}". '
              "Skipping QC is not skipping fixes: a red test or a known bug still has to be fixed.")
    if not by:
        _warn("Missing --by \"<the user's exact words>\" — record it so who approved what stays checkable.")
    extra = f", mode {mode}" if mode else ""
    if reapproved:
        print(f"✅ {target} changed since the previous approval — recorded the user's re-approval "
              f"at {state[f'{target}_approved_at']}{extra}, sha256 updated.")
    else:
        print(f"✅ Recorded the user's approval of {target} at {state[f'{target}_approved_at']}{extra}.")


def _chan_spec_chua_duyet(state):
    """Gate `plan`: the user must have approved the spec first.

    Until 2026-09-01 this door was guarded only by the diagram list, so removing
    the diagram phase left it wide open — a plan could be written before anyone
    approved the spec it is built on. `phases.md` has always stated the real
    condition (`spec_approved = true`); this is that sentence turned into code.
    """
    if state.get("spec_approved"):
        return
    _fail("The spec has not been approved yet. The user approves it in chat, then "
          "record it with `approve spec --by \"...\"` before moving to phase=plan.")


def _chan_worktree_con_mo(cwd):
    """Gate `qc`: an open row in the worktree ledger stops the phase from moving.

    QC is the last moment anyone still looks at this request. Let it through and the
    leftover worktree stays on disk forever — the exact drift this ledger exists to stop.
    A missing or corrupt ledger is NOT evidence of a leftover worktree, so it never
    blocks: a false block here would teach people to route around the gate.
    """
    try:
        import tdq_worktree_registry as so_wt
        mo = so_wt.dong_mo(cwd)
    except Exception:
        return
    if not mo:
        return
    ten = ", ".join(f"{d.get('ma_task')} ({d.get('duong_dan')})" for d in mo)
    _fail(f"{len(mo)} worktree(s) still open: {ten}. "
          "Clean them up first: python3 scripts/tdq_team.py sweep --clean")


def _pop_json_flag(argv):
    """Strip the `--json` flag out of argv. By default the CLI prints a 1-line summary to
    keep context cheap; with `--json` it prints the whole state as before (for inspection/debug)."""
    rest = [a for a in argv if a != "--json"]
    return rest, len(rest) != len(argv)


def _pop_lang_flag(argv):
    """Strip the `--lang <code>` pair out of the argv of `init`.

    Its position is free (before or after the lane) because whoever types the command
    remembers the lane first and thinks of the language afterwards. A bad code stops
    immediately — no half-written state.
    """
    rest = []
    doc_lang = DEFAULT_DOC_LANG
    i = 0
    while i < len(argv):
        if argv[i] == "--lang":
            if i + 1 >= len(argv):
                _fail("Missing the language code after --lang (example: --lang en).")
            ma = normalize_doc_lang(argv[i + 1])
            if ma is None:
                _fail(f"Invalid language code: {argv[i + 1]} "
                      "(expected the shape vi|en|ja|pt-br).")
            doc_lang = ma
            i += 2
            continue
        rest.append(argv[i])
        i += 1
    return rest, doc_lang


def _echo_state(cmd, state, want_json):
    """Print the result of a state-writing command: a 1-line summary, or the whole JSON with --json."""
    if want_json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    print(f"✅ {cmd}: request={state.get('active_request')} "
          f"lane={state.get('lane')} phase={state.get('phase')}")


def _cli_implement_pause(cwd, cmd, rest):
    """`pause --ly-do "<why>"` declares the pause, `resume` clears it.

    A declared pause is the only legal way to end a turn while the plan still
    has open tasks, so the reason is mandatory: an undeclared stop is exactly
    the silent exit the Stop gate exists to refuse.
    """
    rest, want_json = _pop_json_flag(list(rest))
    state = load(cwd)
    if state is None:
        _fail("No state yet — run init first.")
    stamp = state.get("updated_at")

    if cmd == "resume":
        if rest:
            _fail("resume takes no argument.")
        state["implement_pause"] = None
        save(cwd, state, expect_updated_at=stamp)
        _info("implement pause cleared — the Stop gate is armed again")
        _echo_state("resume", state, want_json)
        return

    reason = ""
    if len(rest) >= 2 and rest[0] == "--ly-do":
        reason = " ".join(rest[1:]).strip()
    if not reason:
        _fail('pause needs a reason: pause --ly-do "<why the run stopped>".')
    state["implement_pause"] = {
        "ly_do": reason[:400],
        "at": now_iso(),
        "by": "claude",
    }
    save(cwd, state, expect_updated_at=stamp)
    _info(f"implement pause declared: {reason[:120]}")
    _echo_state("pause", state, want_json)


def cli(argv):
    started_in = os.getcwd()
    env = os.environ.get("TDQ_PROJECT_DIR")
    cwd = resolve_project_dir(started_in)
    if not env and os.path.realpath(cwd) != os.path.realpath(started_in):
        _info(f"Project root: {cwd} (command ran from {started_in})")
    for shadow in find_shadow_states(cwd):
        _warn(f"Stray state found: {shadow} — only {STATE_REL} at the project root counts, "
              "delete the stray file so no wrong approval state gets read.")
    if not argv:
        _fail("Missing command.")
    # Hidden alias (`tam-hoan` → `pause`); the table lives in tdq_ten_lenh.py.
    _bi_danh = tdq_ten_lenh.giai_ten(argv[0], tdq_ten_lenh.BANG_DOI_TEN["tdq_state.py"])
    if _bi_danh is not None:
        argv = [_bi_danh] + list(argv[1:])
    cmd = argv[0]

    if cmd == "next":
        brief = "--brief" in argv[1:]
        for extra in argv[1:]:
            if extra != "--brief":
                _fail(f"Invalid argument: {extra}")
        print(render_next(cwd, load(cwd), brief=brief))
        return

    if cmd == "phases-doc":
        # Reads/writes no state: it only dumps the PHASE_TABLE constant as markdown.
        extra = argv[1:]
        if extra not in ([], ["--plugin-root"]):
            _fail(f"Invalid argument: {' '.join(extra)}")
        print(render_phases_md(plugin_root=bool(extra)), end="")
        return

    if cmd == "get":
        state = load(cwd) or default_state()
        if len(argv) > 1:
            key = argv[1]
            if key not in state:
                _warn(f"Key not in state: {key}")
                print("")
                return
            value = state.get(key)
            print("" if value is None else (json.dumps(value, ensure_ascii=False)
                                            if not isinstance(value, str) else value))
        else:
            print(json.dumps(state, ensure_ascii=False, indent=2))
        return

    if cmd == "init":
        argv, want_json = _pop_json_flag(argv)
        argv, doc_lang = _pop_lang_flag(argv)
        if len(argv) < 2:
            _fail(f"Missing slug. Formula: {SLUG_FORMULA}")
        # Writing a new one requires the hour and minute. A bare warning changes no
        # behaviour: the new standard would drift the first time someone skipped it.
        # Reading still accepts the old slug shape.
        phan_tich = parse_slug(argv[1])
        if phan_tich is None:
            _fail(f"Malformed slug: {argv[1]}. Formula: {SLUG_FORMULA}")
        if phan_tich[1] is None:
            _fail(f"Slug missing the hour and minute: {argv[1]}. Formula: {SLUG_FORMULA} "
                  f"(example {phan_tich[0]}-{datetime.now().strftime('%H%M')}-{phan_tich[2]})")
        # init = OPEN A NEW REQUEST: it resets the whole state (request, lane, phase,
        # spec/plan file, every approval field, implement_mode). If the open request is
        # still unfinished a warning goes to stderr — it still runs, but leaves a trace.
        old = load(cwd) or {}
        old_slug = old.get("active_request")
        if old_slug:
            # init wipes the state. Without closing the books first, every timestamp of the
            # old request is lost — this is the only door that catches an abandoned request.
            _dong_so_request_cu(cwd)
        state = default_state()
        state["active_request"] = argv[1]
        state["previous_request"] = old_slug
        state["started_at"] = now_iso()
        ghi_moc_phase(state, state["phase"], state["started_at"])
        if old_slug and old_slug != argv[1] and _unfinished(old):
            _warn(f"Overwriting request '{old_slug}' (lane {old.get('lane')}, "
                  f"phase {old.get('phase')}) — every approval state of that request is erased.")
        if len(argv) > 2:
            lane = normalize_lane(argv[2])
            if lane is None:
                _fail("Invalid lane. Accepts: nhanh|express|quick "  # i18n-allow
                      "(express mode) · chuyen-sau|deep|full (deep mode).")
            state["lane"] = lane
        state["doc_lang"] = doc_lang
        save(cwd, state)
        _echo_state("init", state, want_json)
        return

    if cmd == "set":
        argv, want_json = _pop_json_flag(argv)
        state = load(cwd)
        if state is None:
            _warn("No state yet — building the default state then applying the change. Run init first.")
            state = default_state()
        stamp = state.get("updated_at")
        if len(argv) < 2:
            _fail("Missing the key=value pair.")
        for pair in argv[1:]:
            if "=" not in pair:
                _fail(f"Invalid argument: {pair} (expected the shape key=value)")
            key, raw = pair.split("=", 1)
            if key not in default_state():
                _fail(f"Key does not exist in the schema: {key}")
            value = _parse_value(raw)
            if key == "lane" and value not in VALID_LANES:
                _fail("Invalid lane (quick|full|null).")
            if key == "doc_lang":
                ma = normalize_doc_lang(value)
                if ma is None:
                    _fail("Invalid doc_lang: expected a language code such as vi|en|ja|pt-br.")
                value = ma
            if key == "diagrams":
                _fail(LOI_SO_DO_DA_GO)
            if key == "phase" and value not in VALID_PHASES:
                if value in PHASE_DA_GO:
                    _fail(f"Phase {value} was removed from the workflow on "
                          f"2026-09-01 — use phase={PHASE_DA_GO[value]} instead.")
                _fail("Invalid phase (idle|analyze|spec|plan|mode|implement|qc|report).")
            if key == "phase" and value == "qc":
                _chan_worktree_con_mo(cwd)
            if key == "phase" and value == "plan":
                _chan_spec_chua_duyet(state)
            state[key] = value
            if key == "phase":
                ghi_moc_phase(state, value)
        save(cwd, state, expect_updated_at=stamp)
        _echo_state("set", state, want_json)
        return

    if cmd in ("pause", "resume"):
        return _cli_implement_pause(cwd, cmd, argv[1:])

    if cmd == "approve":
        return _cli_approve(cwd, argv[1:])

    if cmd == "diagram":
        _fail(LOI_SO_DO_DA_GO)

    if cmd == "reset":
        argv, want_json = _pop_json_flag(argv)
        state = default_state()
        save(cwd, state)
        _echo_state("reset", state, want_json)
        return

    _fail(f"Invalid command: {cmd}")


if __name__ == "__main__":
    cli(sys.argv[1:])
