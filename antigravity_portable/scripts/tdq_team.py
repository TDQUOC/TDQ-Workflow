#!/usr/bin/env python3
"""Team-mode orchestration: the leader assigns the WHOLE plan, sub-agents run in parallel.

Seven sub-commands, used in exactly this order:
    phan-cong  — read the whole plan, write the map docs/tdq/team/<slug>.json
    kiem-ke    — audit the map: a task the leader kept against the rules exits non-zero
    cum        — print the next wave (assignable tasks touching no locked area)
    mo <task>  — create a branch + its own git worktree for one task
    soat       — sweep every worktree of every request; --don removes the safe ones
    kiem <task>— probe for conflicts with the integration branch, WITHOUT touching the repo
    hop <task> — merge the task's branch into the integration branch (blocked until `kiem` passes)
    don        — remove every worktree of the request, prune .git/worktrees clean

Why this tool instead of letting the model wing it: the decision "assign this task or
keep it" must be MACHINE-CHECKABLE. When the model judges itself, nobody can prove
whether it bent the rule (the user picked subagent, the leader did the work on main).

Exit code: 0 = fine · 1 = rule broken / conflict / missing facts · 2 = wrong usage.
Env: TDQ_PROJECT_DIR anchors the project · TDQ_LOG=0 mutes the log · TDQ_WORKTREE_DIR moves worktrees.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime

GIT_TIMEOUT = 120

# --- plan reading rules ------------------------------------------------------
# Task line: `- [ ] **T1.1** (n3 e5m) work — Test: ...`
_TASK = re.compile(r"^(\s*)-\s*\[( |~|x|>)\]\s*\*\*([A-Za-z][A-Za-z0-9.]*)\*\*\s*(.*)$")
_PHASE = re.compile(r"^##\s*(P\d+)\b")
# A path declared in backticks: needs a `/` and an extension — `true` or `T1.1` do not count.
_PATH = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")
# Same task-code rule as `_TASK` above: `T2A.1`, `T2.4b` are both valid declarations
# in a `- Cần:` line; missing them makes the dependency graph falsely sparse.  # i18n-allow
_TASK_REF = re.compile(r"\b(T\d+[A-Za-z]*\.\d+[a-z]?)\b")
# Dependency label in the plan: `- Cần: T1.1, T2.3`.  # i18n-allow
NHAN_CAN = "Cần:"  # i18n-allow
# Time-estimate label in the plan: `(n3 e20m)` → 20 minutes.
_UOC_LUONG = re.compile(r"\be(\d+)m\b")

# CLOSED set of reasons for keeping a task with the leader. Anything else bends the rule.
LY_DO_GIU = {
    "phu-thuoc": "the task depends on another task that is not finished",  # i18n-allow
    "vung-khoa": "no separate file area is declared, so it cannot be split off",  # i18n-allow
    "mcp": "the task needs an MCP tool a sub-agent does not have",  # i18n-allow
    "file-luat": "it edits the very rule/hook file the leader runs on",  # i18n-allow
    # A shared contract (data types, constants, message shapes, registries) must be
    # built FIRST and only then branched out: if every sub-agent guesses its own shape,
    # the mismatch between the copies only shows up after the merge.
    "hop-dong": "the task defines a shared contract that later tasks read",  # i18n-allow
}
# Rule/hook file prefixes: a sub-agent editing these saws the plank the leader is
# standing on — the leader has to do them itself.
TIEN_TO_FILE_LUAT = ("skills/", "hooks/", "agents/", ".claude/", ".codex/",
                     "CLAUDE.md", "AGENTS.md")
# Branch/worktree name prefixes that are banned (CLAUDE.md §2).
TEN_CAM = ("claude", "antigravity", "gemini", "codex")

# Cap on branches running at once. 4, because coordination failure points grow as n(n-1)/2:
# 4 agents is 6 points, 10 agents is already 45 (research round 1, section 4). This is an
# UPPER cap — fewer ready tasks means fewer launched, never wait to fill up to 4.
TRAN_SONG_SONG = 4

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
import tdq_state  # noqa: E402
import tdq_worktree_registry as so_wt  # noqa: E402


# --------------------------------------------------------------- log service
def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: one ISO-timestamped line on stderr. Muted with TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}",
              file=sys.stderr)


def _loi(message):
    """Error messages always go to stderr, regardless of TDQ_LOG."""
    print(message, file=sys.stderr)


def _project_dir():
    """Neo theo project: TDQ_PROJECT_DIR > git root > cwd."""
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


# ------------------------------------------------------------- read the plan
class Task:
    """One task of the plan, with everything readable off its own line."""

    def __init__(self, ma, trang_thai, phase):
        self.ma = ma
        self.trang_thai = trang_thai      # " " | "~" | "x" | ">"
        self.phase = phase
        self.text = []                    # the task line + its child lines
        self.vung_file = []
        self.can_mcp = False

    @property
    def xong(self):
        return self.trang_thai == "x"

    @property
    def da_giao(self):
        return self.trang_thai == ">"


def doc_plan(duong_dan):
    """Return the list of Tasks in the exact order they appear in the plan."""
    with open(duong_dan, encoding="utf-8") as f:
        lines = f.read().splitlines()
    tasks = []
    phase = "P0"
    hien_tai = None
    for line in lines:
        m_phase = _PHASE.match(line)
        if m_phase:
            phase = m_phase.group(1)
            hien_tai = None
            continue
        m_task = _TASK.match(line)
        if m_task:
            hien_tai = Task(m_task.group(3), m_task.group(2), phase)
            hien_tai.text.append(m_task.group(4))
            tasks.append(hien_tai)
            continue
        if hien_tai is None:
            continue
        if line.strip().startswith("- ") and line.startswith((" ", "\t")):
            hien_tai.text.append(line.strip()[2:])
        elif not line.strip():
            continue
        elif line.startswith((" ", "\t")):
            # A continuation line of the description: indented but opening no new bullet. Append
            # it to the last element instead of making its own — that keeps the prefix visible
            # on a declaration line that got wrapped (`- Chạm: …` broken across lines).  # i18n-allow
            duoi = line.strip()
            truoc = hien_tai.text[-1].rstrip()
            hien_tai.text[-1] = (truoc + " " + duoi) if truoc else duoi
        else:
            hien_tai = None
    for t in tasks:
        for dong in t.text:
            for duong in _PATH.findall(dong):
                if "/" in duong and duong not in t.vung_file:
                    t.vung_file.append(duong)
            if dong.startswith("Dùng:") and dong.rstrip().endswith("(mcp)"):  # i18n-allow
                t.can_mcp = True
    return tasks


def doc_phu_thuoc(tasks):
    """Map task code → set of task codes that must finish FIRST, read off the dependency line.

    A task declaring no such line returns the empty set — it claims no dependency.
    A code pointing at itself and a code absent from the plan are both skipped: a sloppy plan
    still schedules, and the linter catches the mistakes instead of crashing the wave command.
    """
    co_that = {t.ma for t in tasks}
    ket_qua = {}
    for t in tasks:
        can = set()
        for dong in t.text:
            if not dong.strip().startswith(NHAN_CAN):
                continue
            phan = dong.split(":", 1)[1] if ":" in dong else ""
            for ref in _TASK_REF.findall(phan):
                if ref != t.ma and ref in co_that:
                    can.add(ref)
        ket_qua[t.ma] = can
    return ket_qua


def _phut_uoc_luong(task):
    """Estimated minutes read off the `(n3 e20m)` label. Undeclared counts as 1 minute.

    Default 1 and not 0: an undeclared task still costs time, and 0 would make the whole
    branch holding it vanish from the critical-path comparison.
    """
    for dong in task.text:
        m = _UOC_LUONG.search(dong)
        if m:
            return int(m.group(1))
    return 1


def b_level(tasks, phu_thuoc):
    """Task code → total minutes of the LONGEST path from that task to the end of the graph.

    This is the schedule's `b-level`: a task with a large b-level sits on the critical path;
    launched early the team finishes early, launched late every other branch waits on it.
    """
    sau = {t.ma: [] for t in tasks}                 # task code → the tasks waiting on it
    for t in tasks:
        for c in phu_thuoc.get(t.ma, ()):
            if c in sau:
                sau[c].append(t.ma)
    phut = {t.ma: _phut_uoc_luong(t) for t in tasks}
    nho = {}

    def tinh(ma, dang_di):
        if ma in nho:
            return nho[ma]
        if ma in dang_di:                           # cycle: cut it, never hang
            return 0
        dang_di.add(ma)
        ket_qua = phut[ma] + max((tinh(k, dang_di) for k in sau[ma]), default=0)
        dang_di.discard(ma)
        nho[ma] = ket_qua
        return ket_qua

    return {t.ma: tinh(t.ma, set()) for t in tasks}


def _la_file_luat(duong):
    return duong.startswith(TIEN_TO_FILE_LUAT)


def quyet_dinh_task(task, tasks):
    """(quyet_dinh, ly_do) for one task. Default is ASSIGN — keeping it needs a reason."""
    if task.can_mcp:
        return "tu_lam", "mcp"
    if not task.vung_file:
        return "tu_lam", "vung-khoa"
    if any(_la_file_luat(d) for d in task.vung_file):
        return "tu_lam", "file-luat"
    if any(doc_phu_thuoc(tasks).values()):
        # The plan declared `Cần:` → a dependency is a SCHEDULING constraint (`chia_dot` handles it),  # i18n-allow
        # not a reason to keep the task. Keeping it here would let a `Cần:` line kill parallelism.  # i18n-allow
        return "giao", ""
    chua_xong = {t.ma for t in tasks if not t.xong}
    for dong in task.text:
        for ref in _TASK_REF.findall(dong):
            if ref != task.ma and ref in chua_xong:
                return "tu_lam", "phu-thuoc"
    return "giao", ""


def chia_dot(tasks, quyet_dinh):
    """Assign a wave number to each task. Wave 1 runs first, same wave = in parallel.

    At least one task declares a dependency line → order by the DEPENDENCY GRAPH: a task sits
    after every task it declares, and is otherwise pulled as early as possible, even across
    phase boundaries. No task declares one → fall back to the old rule by phase name, so plans
    written before this rule produce exactly the same waves as before.

    Rule for both paths: two tasks touching the same file are never in the same wave.
    """
    phu_thuoc = doc_phu_thuoc(tasks)
    if not any(phu_thuoc.values()):
        _log("chia-dot → no task declares a dependency line, falling back to phase-name order")
        return _chia_dot_theo_phase(tasks)
    khai = sum(1 for v in phu_thuoc.values() if v)
    _log(f"chia-dot → {khai}/{len(tasks)} task(s) declare dependencies, ordering by graph")
    return _chia_dot_theo_phu_thuoc(tasks, phu_thuoc)


def _dot_som_nhat(files, dot_toi_thieu, chiem_theo_dot):
    """The earliest wave from `dot_toi_thieu` on that touches no other task's files."""
    dot = dot_toi_thieu
    while files & chiem_theo_dot.get(dot, set()):
        dot += 1
    chiem_theo_dot.setdefault(dot, set()).update(files)
    return dot


def _chia_dot_theo_phu_thuoc(tasks, phu_thuoc):
    """Topological order: each task sits after the largest wave of the tasks it needs."""
    con_lai = {t.ma: t for t in tasks}
    dot_theo_task = {}
    chiem_theo_dot = {}
    while con_lai:
        san_sang = [t for t in con_lai.values()
                    if all(c in dot_theo_task for c in phu_thuoc[t.ma])]
        cat_vong = not san_sang
        if cat_vong:
            # A cycle in the `Cần:` declarations — the plan is wrong. Cut the cycle and carry on  # i18n-allow
            # instead of dying: the wave command is not the place to report plan syntax, the linter is.
            _log(f"chia-dot → cut the dependency cycle at {', '.join(sorted(con_lai))}")
            san_sang = list(con_lai.values())
        for t in san_sang:
            # `.get(...,  0)` because on the cycle-cut path a needed task may not be placed yet.
            nen = max((dot_theo_task.get(c, 0) for c in phu_thuoc[t.ma]), default=0) + 1
            dot_theo_task[t.ma] = _dot_som_nhat(set(t.vung_file), nen, chiem_theo_dot)
            del con_lai[t.ma]
    return dot_theo_task


def _chia_dot_theo_phase(tasks):
    """Old rule: phase order IS dependency order; split files inside each phase."""
    dot_theo_task = {}
    nen = 0
    for phase in sorted({t.phase for t in tasks}, key=_khoa_phase):
        trong_phase = [t for t in tasks if t.phase == phase]
        thung = []                                  # thung[i] = set of files already taken
        for t in trong_phase:
            files = set(t.vung_file)
            for i, chiem in enumerate(thung):
                if not (files & chiem):
                    chiem |= files
                    dot_theo_task[t.ma] = nen + i + 1
                    break
            else:
                thung.append(set(files))
                dot_theo_task[t.ma] = nen + len(thung)
        nen += len(thung)
    return dot_theo_task


def _khoa_phase(ten):
    so = re.findall(r"\d+", ten)
    return (int(so[0]) if so else 0, ten)


# ------------------------------------------------------------- the map
def duong_ban_do(project, slug):
    return os.path.join(project, "docs", "tdq", "team", f"{slug}.json")


def sha_file(duong_dan):
    h = hashlib.sha256()
    with open(duong_dan, "rb") as f:
        for khoi in iter(lambda: f.read(65536), b""):
            h.update(khoi)
    return h.hexdigest()


def _boi_canh(project, can_ban_do=True):
    """(slug, plan_path, ban_do|None), or raises LoiLuat."""
    state = tdq_state.load(project, heal=False) or {}
    slug = state.get("active_request")
    if not slug:
        raise LoiLuat("No request is open — nothing to assign.")
    rel = state.get("plan_file") or os.path.join("docs", "tdq", "plan", f"{slug}.md")
    plan = rel if os.path.isabs(rel) else os.path.join(project, rel)
    if not os.path.isfile(plan):
        raise LoiLuat(f"Plan not found: {plan}")
    ban_do = None
    duong = duong_ban_do(project, slug)
    if os.path.isfile(duong):
        try:
            with open(duong, encoding="utf-8") as f:
                ban_do = json.load(f)
        except (ValueError, UnicodeDecodeError) as loi:
            raise LoiLuat(f"The assignment map is broken ({duong}): {loi}. "
                          f"Run again: python3 scripts/tdq_team.py phan-cong")
    elif can_ban_do:
        raise LoiLuat("No assignment map yet. Run: "
                      "python3 scripts/tdq_team.py phan-cong")
    if ban_do is not None and can_ban_do and ban_do.get("plan_sha") != sha_file(plan):
        raise LoiLuat("The plan changed after assignment — the map is stale. "
                      "Run again: python3 scripts/tdq_team.py phan-cong")
    return slug, plan, ban_do


class LoiLuat(Exception):
    """Rule broken or facts missing — exit 1, with the command that fixes it."""


# ------------------------------------------------------------- sub-commands
def lenh_phan_cong(project, _args):
    slug, plan, _ = _boi_canh(project, can_ban_do=False)
    tasks = doc_plan(plan)
    if not tasks:
        raise LoiLuat(f"The plan holds no readable task: {plan}")
    quyet = {t.ma: quyet_dinh_task(t, tasks) for t in tasks}
    dot = chia_dot(tasks, quyet)
    ban_do = {
        "slug": slug,
        "plan_file": os.path.relpath(plan, project),
        "plan_sha": sha_file(plan),
        "tasks": {
            t.ma: {
                "quyet_dinh": quyet[t.ma][0],
                "ly_do": quyet[t.ma][1],
                "vung_file": t.vung_file,
                "dot": dot[t.ma],
            } for t in tasks
        },
    }
    duong = duong_ban_do(project, slug)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(ban_do, f, ensure_ascii=False, indent=2)
        f.write("\n")
    giao = sum(1 for r in ban_do["tasks"].values() if r["quyet_dinh"] == "giao")
    _log(f"phan-cong → {len(tasks)} task(s) · assigned {giao} · kept {len(tasks) - giao} "
         f"· {max(dot.values())} wave(s)")
    print(f"Map: {os.path.relpath(duong, project)}")
    print(f"Assigned to sub-agents: {giao}/{len(tasks)} task(s) · {max(dot.values())} wave(s)")
    for ma, rec in ban_do["tasks"].items():
        if rec["quyet_dinh"] == "tu_lam":
            print(f"  KEPT {ma} — {rec['ly_do']}: {LY_DO_GIU[rec['ly_do']]}")
    return 0


def lenh_kiem_ke(project, _args):
    _slug, _plan, ban_do = _boi_canh(project)
    van_de = []
    for ma, rec in ban_do["tasks"].items():
        if rec.get("quyet_dinh") == "giao":
            # An assigned task with an empty file area is an empty promise: hook [TDQ:TEAM] has
            # nothing to compare, so the leader may edit any file. The cheapest way around the rule.
            if not rec.get("vung_file"):
                van_de.append(f"Assigned: {ma} — recorded as handed to a sub-agent but the file area is "
                              f"EMPTY, the hook can block nobody")
            thieu = [k for k in ("quyet_dinh", "ly_do", "vung_file", "dot")
                     if k not in rec]
            if thieu:
                van_de.append(f"Assigned: {ma} — the record is missing field(s) {', '.join(thieu)}")
            continue
        thieu = [k for k in ("quyet_dinh", "ly_do", "vung_file", "dot") if k not in rec]
        if thieu:
            van_de.append(f"Kept: {ma} — the record is missing field(s) {', '.join(thieu)}")
        if rec.get("quyet_dinh") != "tu_lam":
            van_de.append(f"Kept: {ma} — decision \"{rec.get('quyet_dinh')}\" "
                          f"is not valid (only giao / tu_lam)")
            continue
        ly_do = (rec.get("ly_do") or "").strip()
        if not ly_do:
            van_de.append(f"Kept: {ma} — kept by the leader with NO reason")
        elif ly_do not in LY_DO_GIU:
            van_de.append(f"Kept: {ma} — reason \"{ly_do}\" is not one of the "
                          f"{len(LY_DO_GIU)} groups ({', '.join(sorted(LY_DO_GIU))})")
    tong = len(ban_do["tasks"])
    giao = sum(1 for r in ban_do["tasks"].values() if r.get("quyet_dinh") == "giao")
    _log(f"kiem-ke → {giao}/{tong} assigned · {len(van_de)} problem(s)")
    if van_de:
        for dong in van_de:
            _loi(dong)
        _loi("Fix: python3 scripts/tdq_team.py phan-cong (or hand-fix the map to use "
             f"the {len(LY_DO_GIU)} reason groups)")
        return 1
    print(f"Map clean: {giao}/{tong} task(s) assigned to sub-agents.")
    return 0


def _tien_quyet(tasks, phu_thuoc, dot_theo_task):
    """Task code → set of task codes that must be DONE before it is launched.

    The plan declares dependency lines → take them verbatim. An old plan declaring none →
    infer from the wave numbers, keeping the old "wave N finishes before wave N+1" behaviour.
    """
    if any(phu_thuoc.values()):
        return {ma: set(phu_thuoc[ma]) for ma in tasks}
    return {ma: {khac for khac in tasks
                 if dot_theo_task.get(khac, 0) < dot_theo_task.get(ma, 0)}
            for ma in tasks}


def _ly_do_hoan(ma, tien_quyet, tasks, khoa, vung_file):
    """The SPECIFIC reason a task cannot be launched yet, or None when it can."""
    thieu = sorted(c for c in tien_quyet[ma]
                   if c in tasks and not tasks[c].xong)
    if thieu:
        return "waiting on unfinished task(s): " + ", ".join(thieu)
    dung = [d for d in vung_file if d in khoa]
    if dung:
        return "touches a locked area: " + ", ".join(sorted(dung))
    return None


def lenh_cum(project, _args):
    _slug, plan, ban_do = _boi_canh(project)
    danh_sach = doc_plan(plan)
    tasks = {t.ma: t for t in danh_sach}
    phu_thuoc = doc_phu_thuoc(danh_sach)
    diem_gang = b_level(danh_sach, phu_thuoc)
    dot_theo_task = {ma: rec.get("dot", 0) for ma, rec in ban_do["tasks"].items()}
    tien_quyet = _tien_quyet(tasks, phu_thuoc, dot_theo_task)

    khoa = {}                               # file → the task holding it
    dang_bay = [ma for ma, t in tasks.items() if t.da_giao]
    for ma in dang_bay:
        for duong in tasks[ma].vung_file:
            khoa[duong] = ma
    con_lai = [ma for ma, rec in ban_do["tasks"].items()
               if rec["quyet_dinh"] == "giao"
               and ma in tasks and not tasks[ma].xong and not tasks[ma].da_giao]
    if not con_lai:
        _log("cum → NO assignable task left")
        print("DONE: no task left to hand to a sub-agent.")
        return 0
    if khoa:
        print("Locked areas: " + ", ".join(
            f"{duong} ({ma})" for duong, ma in sorted(khoa.items())))

    # Critical path first: the task stretching the total the most gets a slot first.
    con_lai.sort(key=lambda ma: (-diem_gang.get(ma, 0), ma))
    phat, hoan, cho_slot = [], [], []
    da_dat = dict(khoa)                     # including files taken in this very round
    for ma in con_lai:
        vung = ban_do["tasks"][ma]["vung_file"]
        ly_do = _ly_do_hoan(ma, tien_quyet, tasks, da_dat, vung)
        if ly_do:
            hoan.append((ma, ly_do))
            continue
        # The cap counts tasks still in flight: launching round after round while counting
        # only this round would open 4 more branches every time, making the cap moot.
        if len(dang_bay) + len(phat) >= TRAN_SONG_SONG:
            _log(f"cum → {ma} is ready but hits the {TRAN_SONG_SONG}-branch cap "
                 f"({len(dang_bay)} in flight), waiting for a slot")
            cho_slot.append(ma)
            continue
        phat.append(ma)
        for duong in vung:
            da_dat[duong] = ma

    print(f"Ready: {len(phat)} task(s)")
    for ma in phat:
        print(f"  {ma}  {' '.join(ban_do['tasks'][ma]['vung_file'])}")
    # Say exactly why each task is not launched: the leader must tell "the map missed a
    # task" apart from "the task is legitimately blocked".
    for ma, ly_do in hoan:
        print(f"  HELD {ma} — {ly_do}")
    if cho_slot:
        print(f"  WAITING FOR A SLOT: {len(cho_slot)} task(s) (cap {TRAN_SONG_SONG} branches at "
              f"once, {len(dang_bay)} in flight): " + ", ".join(sorted(cho_slot)))
    _log(f"cum → launch {len(phat)} · hold {len(hoan)} · waiting for a slot {len(cho_slot)}")
    return 0


# ------------------------------------------------------------- git
def _git(cwd, *args, check=True):
    # errors="replace": `git merge-tree` prints object contents to stdout, which may hold
    # non-UTF-8 bytes (a binary file, or a string cut mid-character). On the default the
    # whole `kiem` command dies with UnicodeDecodeError — a failure that only shows up on
    # a real run, never in tests using pure ASCII files.
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True, errors="replace", timeout=GIT_TIMEOUT)
    if check and proc.returncode != 0:
        raise LoiLuat(f"git {' '.join(args)} failed ({proc.returncode}): "
                      f"{proc.stderr.strip() or proc.stdout.strip()}")
    return proc


def _la_repo(project):
    proc = subprocess.run(["git", "-C", project, "rev-parse", "--git-dir"],
                          capture_output=True, text=True, timeout=GIT_TIMEOUT)
    return proc.returncode == 0


def _ten_nhanh(slug, ma_task):
    """`tdq/<slug>/<task>` — never starts with a name banned by CLAUDE.md §2."""
    ten = f"tdq/{slug}/{ma_task.lower()}"
    assert not ten.startswith(TEN_CAM)
    return ten


def _nhanh_tich_hop(slug):
    return f"tdq/{slug}/tich-hop"


def _thu_muc_goc_worktree(project):
    goc = os.environ.get("TDQ_WORKTREE_DIR") or os.path.join(project, ".tdq-worktrees")
    os.makedirs(goc, exist_ok=True)
    # The directory hides itself from `git status` — no need to touch the user's .gitignore.
    bo_qua = os.path.join(goc, ".gitignore")
    if not os.path.exists(bo_qua):
        with open(bo_qua, "w", encoding="utf-8") as f:
            f.write("*\n")
    return goc


def _duong_worktree(project, slug, ten):
    return os.path.join(_thu_muc_goc_worktree(project), slug, ten)


def _co_nhanh(project, nhanh):
    return _git(project, "rev-parse", "--verify", "--quiet", nhanh,
                check=False).returncode == 0


def _bao_dam_tich_hop(project, slug):
    """Integration branch + worktree. The merge happens HERE, not where the user stands."""
    nhanh = _nhanh_tich_hop(slug)
    duong = _duong_worktree(project, slug, "tich-hop")
    if not _co_nhanh(project, nhanh):
        _git(project, "branch", nhanh, "HEAD")
        _log(f"created the integration branch {nhanh}")
    if not os.path.isdir(duong):
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        _git(project, "worktree", "add", duong, nhanh)
        _log(f"integration worktree → {duong}")
    return nhanh, duong


# ------------------------------------------------- the worktree ledger, seen from git
def _liet_ke_worktree(project):
    """`git worktree list --porcelain` → [{duong_dan, nhanh, khoa}].

    Read the lock flag here rather than guessing later: a locked worktree that git
    refuses to remove must come back to the user as a reason, not as a raw git error.
    """
    ra = _git(project, "worktree", "list", "--porcelain").stdout
    muc, hien = [], None
    for dong in ra.splitlines():
        if dong.startswith("worktree "):
            hien = {"duong_dan": dong.split(" ", 1)[1], "nhanh": "", "khoa": False}
            muc.append(hien)
        elif hien is None:
            continue
        elif dong.startswith("branch "):
            hien["nhanh"] = dong.split(" ", 1)[1].replace("refs/heads/", "")
        elif dong == "locked" or dong.startswith("locked "):
            hien["khoa"] = True
    return muc


def _khoa_khong(project, duong):
    that = os.path.realpath(duong)
    return any(w["khoa"] for w in _liet_ke_worktree(project)
               if os.path.realpath(w["duong_dan"]) == that)


def _file_ban(duong):
    """Up to 5 paths the cleanup would destroy — enough for the user to recognise them."""
    proc = _git(duong, "status", "--porcelain", check=False)
    return [d[3:].strip() for d in proc.stdout.splitlines()[:5]]


# Ignored files git deletes without a word. These regenerate by themselves, so they are
# not worth blocking a cleanup over; anything else ignored is data we cannot judge, and
# unknown data is never deleted on the user's behalf.
RAC_SINH_LAI = ("__pycache__", ".pytest_cache", ".DS_Store", ".venv", "node_modules",
                ".mypy_cache", ".ruff_cache")


def _file_bo_qua_dang_ke(duong):
    """Ignored files that do NOT regenerate — `.env`, local keys, scratch data.

    `git worktree remove` deletes them silently, with or without --force, so they have to
    be caught here or they are gone for good.
    """
    proc = _git(duong, "status", "--porcelain", "--ignored=matching", check=False)
    ra = []
    for dong in proc.stdout.splitlines():
        if not dong.startswith("!! "):
            continue
        ten = dong[3:].strip()
        if not any(phan in ten for phan in RAC_SINH_LAI):
            ra.append(ten)
    return ra[:5]


def _sach(duong):
    proc = _git(duong, "status", "--porcelain", check=False)
    return (proc.returncode == 0 and not proc.stdout.strip()
            and not _file_bo_qua_dang_ke(duong))


def _da_merge(project, nhanh, tich_hop):
    """Every commit of the branch already lives in the integration branch."""
    if not _co_nhanh(project, tich_hop):
        return False
    return _git(project, "merge-base", "--is-ancestor", nhanh, tich_hop,
                check=False).returncode == 0


def _ly_do_chan_thu_muc(project, ma_task, nhanh, duong):
    """Reasons that make deleting the DIRECTORY unsafe. The merge state is not one of them.

    Split out of `_ly_do_chan` because two callers only ever remove the directory and keep
    the branch: the legacy `don`, and the rows `soat` finds with no ledger entry.
    """
    chung = {"ma_task": ma_task, "duong_dan": duong, "nhanh": nhanh}
    if _khoa_khong(project, duong):
        return dict(chung, ly_do="khoa")
    proc = _git(duong, "status", "--porcelain", check=False)
    if proc.returncode != 0 or proc.stdout.strip():
        return dict(chung, ly_do="ban", chi_tiet=", ".join(_file_ban(duong)))
    # Kept apart from `ban`: the way out is a different command, and calling an ignored
    # `build/` directory "uncommitted changes" sends the user after options that no-op.
    bo_qua = _file_bo_qua_dang_ke(duong)
    if bo_qua:
        return dict(chung, ly_do="bo-qua", chi_tiet=", ".join(bo_qua))
    return None


def _ly_do_chan(project, ma_task, nhanh, duong, tich_hop):
    """The three conditions for deleting. Returns None when all three hold.

    Deleting a worktree destroys work that exists nowhere else, so this stays a
    whitelist: anything not proven safe is a reason to keep and to ask.
    """
    chan = _ly_do_chan_thu_muc(project, ma_task, nhanh, duong)
    if chan is not None:
        return chan
    if _co_nhanh(project, nhanh) and not _da_merge(project, nhanh, tich_hop):
        return {"ma_task": ma_task, "duong_dan": duong, "nhanh": nhanh,
                "ly_do": "chua-merge"}
    return None


def _ly_do_tu_choi(project, ma_task, nhanh, duong, loi):
    """Turn git's refusal into a blocking reason — `khoa` ONLY when it really is locked.

    A permission error labelled "locked" sends the user to `worktree unlock`, which cannot
    fix it. The wrong label is worse than a generic one: it costs a command that no-ops.
    """
    return {"ma_task": ma_task, "duong_dan": duong, "nhanh": nhanh,
            "ly_do": "khoa" if _khoa_khong(project, duong) else "git-tu-choi",
            "chi_tiet": loi}


def _go_thu_muc(project, duong):
    """Remove one worktree directory. Returns None on success, else git's own reason.

    `check=False`: git refusing (a lock set behind our back, a mount held open) must not
    abort the sweep halfway — the whole point of the sweep is the block printed at the end.
    """
    proc = _git(project, "worktree", "remove", duong, check=False)
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["git refused"]


def _thu_don(project, slug, ma_task, nhanh, duong, tich_hop):
    """Try to clean one worktree. Returns None on success, else the suggestion item."""
    chan = _ly_do_chan(project, ma_task, nhanh, duong, tich_hop)
    if chan is not None:
        _log(f"keep {ma_task} — {chan['ly_do']}")
        return chan
    # No --force: `_ly_do_chan` above already proved the worktree is clean, so git's own
    # refusal stays in place as the last safety net instead of being switched off.
    loi = _go_thu_muc(project, duong)
    if loi is not None:
        _log(f"keep {ma_task} — git refused: {loi[0]}")
        return _ly_do_tu_choi(project, ma_task, nhanh, duong, loi[0])
    _git(project, "worktree", "prune")
    # `-D` and not `-d`: `-d` measures against HEAD, which is the user's own branch, not
    # the integration branch. `_da_merge` above already proved the commits are safe.
    if _co_nhanh(project, nhanh) and nhanh != tich_hop:
        _git(project, "branch", "-D", nhanh, check=False)
    so_wt.dong_dong(project, slug, ma_task, "merged")
    _log(f"cleaned {ma_task} → worktree {duong} + branch {nhanh} removed")
    return None


def _in_goi_y(muc):
    """The suggestion block is the LAST thing printed — it is what the user must act on."""
    khoi = so_wt.khoi_goi_y(muc)
    if khoi:
        print(khoi)


def lenh_mo(project, args):
    slug, plan, ban_do = _boi_canh(project)
    ma = args.task
    if ma not in ban_do["tasks"]:
        raise LoiLuat(f"The map holds no task {ma}.")
    rec = ban_do["tasks"][ma]
    if rec["quyet_dinh"] != "giao":
        raise LoiLuat(f"{ma} is marked tu_lam ({rec['ly_do']}) — no branch is opened. "
                      f"The leader does this task itself.")
    if not _la_repo(project):
        raise LoiLuat("This directory is not a git repo — no worktree can be opened.")
    tich_hop, _ = _bao_dam_tich_hop(project, slug)
    nhanh = _ten_nhanh(slug, ma)
    duong = _duong_worktree(project, slug, ma.lower())
    if os.path.isdir(duong):
        raise LoiLuat(f"{ma} already has a worktree: {duong}")
    # BEFORE git touches anything: a worktree opened against a ledger that cannot be
    # written is invisible to `soat` and to the qc gate — exactly the orphan this
    # request exists to abolish.
    so_wt.kiem_ghi_duoc(project)
    if not _co_nhanh(project, nhanh):
        _git(project, "branch", nhanh, tich_hop)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    _git(project, "worktree", "add", duong, nhanh)
    # Only AFTER git succeeded: a row written any earlier is a row that lies.
    so_wt.mo_dong(project, slug, ma, nhanh, duong)
    so_wt.ghi_md(project)
    _log(f"mo {ma} → branch {nhanh} · worktree {duong}")
    print(f"{ma}: branch {nhanh}")
    print(f"  worktree: {duong}")
    print(f"  file area: {' '.join(rec['vung_file']) or '(not declared)'}")
    print(f"  base: {tich_hop}")
    return 0


def _nhanh_cua(project, slug, ban_do, ten):
    """Accepts a task code or a full branch name, returns the branch name."""
    if ten in ban_do["tasks"]:
        return _ten_nhanh(slug, ten)
    return ten


def _do_xung_dot(project, tich_hop, nhanh):
    """Three-way `git merge-tree`: touches NEITHER the index nor the working tree."""
    base = _git(project, "merge-base", tich_hop, nhanh).stdout.strip()
    proc = _git(project, "merge-tree", base, tich_hop, nhanh, check=False)
    ra = proc.stdout
    xung_dot = proc.returncode != 0 or "<<<<<<<" in ra or "CONFLICT" in ra
    return xung_dot, _file_xung_dot(ra) if xung_dot else []


# `git merge-tree <base> <A> <B>` prints "changed in both" blocks, with the path on the
# `  our  100644 <sha> <path>` line — NOT in the diff shape `+++ b/<path>`. Only take a
# block that really carries a conflict marker, so cleanly merged files are not named.
_KHOI_CA_HAI = re.compile(r"^(?:changed in both|added in both)$", re.M)
_DUONG_DAN = re.compile(r"^\s+(?:base|our|their)\s+\d+\s+[0-9a-f]+\s+(.+)$", re.M)


def _file_xung_dot(ra):
    ten = set()
    for phan in _KHOI_CA_HAI.split(ra)[1:]:
        if "<<<<<<<" in phan or "CONFLICT" in phan:
            ten.update(m.strip() for m in _DUONG_DAN.findall(phan))
    if not ten:                                  # another shape (CONFLICT (content): a/b)
        ten.update(m.strip() for m in re.findall(r"^CONFLICT \(.+?\): (.+)$", ra, re.M))
    return sorted(ten)


def lenh_kiem(project, args):
    slug, _plan, ban_do = _boi_canh(project)
    if not _la_repo(project):
        raise LoiLuat("This directory is not a git repo.")
    tich_hop = _nhanh_tich_hop(slug)
    nhanh = _nhanh_cua(project, slug, ban_do, args.task)
    if not _co_nhanh(project, nhanh):
        raise LoiLuat(f"No branch {nhanh}. Open it first: "
                      f"python3 scripts/tdq_team.py mo {args.task}")
    xung_dot, file_dung = _do_xung_dot(project, tich_hop, nhanh)
    _log(f"kiem {nhanh} → {'CONFLICT' if xung_dot else 'clean'}")
    if xung_dot:
        print(f"CONFLICT: {nhanh} does not merge cleanly into {tich_hop}")
        for duong in file_dung:
            print(f"  {duong}")
        print("How to fix: resolve it inside the task's worktree, then run `kiem` again.")
        return 1
    print(f"Clean: {nhanh} merges into {tich_hop}.")
    return 0


def lenh_hop(project, args):
    slug, _plan, ban_do = _boi_canh(project)
    if not _la_repo(project):
        raise LoiLuat("This directory is not a git repo.")
    tich_hop, duong_tich_hop = _bao_dam_tich_hop(project, slug)
    nhanh = _nhanh_cua(project, slug, ban_do, args.task)
    if not _co_nhanh(project, nhanh):
        raise LoiLuat(f"No branch {nhanh}.")
    xung_dot, file_dung = _do_xung_dot(project, tich_hop, nhanh)
    if xung_dot:
        _log(f"hop {nhanh} → BLOCKED by a conflict")
        _loi(f"BLOCKED: {nhanh} conflicts with {tich_hop} at "
             f"{', '.join(file_dung) or '(file unknown)'}.")
        _loi(f"Run `python3 scripts/tdq_team.py kiem {args.task}` for the detail, "
             f"merge only once it is resolved.")
        _in_goi_y([{"ma_task": args.task, "nhanh": nhanh, "ly_do": "xung-dot",
                    "duong_dan": _duong_worktree(project, slug, args.task.lower())}])
        return 1
    # rerere: a conflict repeating across waves is remembered with its resolution (research §2).
    _git(project, "config", "rerere.enabled", "true")
    _git(duong_tich_hop, "merge", "--no-ff", "-m",
         f"merge {nhanh} into {tich_hop}", nhanh)
    _log(f"hop {nhanh} → into {tich_hop}")
    print(f"Merged {nhanh} into {tich_hop}.")
    print(f"Integration branch at: {duong_tich_hop}")
    duong = _duong_worktree(project, slug, args.task.lower())
    if not os.path.isdir(duong):
        so_wt.dong_dong(project, slug, args.task, "bien-mat")
        so_wt.ghi_md(project)
        return 0
    chan = _thu_don(project, slug, args.task, nhanh, duong, tich_hop)
    so_wt.ghi_md(project)
    if chan is None:
        print(f"Cleaned up: worktree removed, branch {nhanh} deleted.")
        return 0
    _in_goi_y([chan])
    return 0


def _kich_thuoc(duong):
    """Bytes on disk. Symlinks are skipped — a link is not the space it points at."""
    tong = 0
    for goc, _thu_muc, ten_file in os.walk(duong):
        for ten in ten_file:
            p = os.path.join(goc, ten)
            if not os.path.islink(p):
                try:
                    tong += os.path.getsize(p)
                except OSError:
                    pass
    return tong


def _doc_mb(byte):
    return byte / (1024 * 1024)


def _tuoi_ngay(tao_luc):
    try:
        return (datetime.now() - datetime.fromisoformat(tao_luc)).days
    except (TypeError, ValueError):
        return 0


def lenh_soat(project, args):
    """Sweep every worktree the ledger knows about, across ALL requests.

    Why across all requests and not just the open one: `don` only ever saw the current
    slug, so a worktree of a finished request could never be reached again — that is the
    exact way disk usage grows without anyone noticing.
    """
    if not _la_repo(project):
        raise LoiLuat("This directory is not a git repo.")
    goc = os.path.realpath(_thu_muc_goc_worktree(project))
    dong = so_wt.dong_mo(project)

    # A row whose directory is gone was cleaned by hand; close it instead of nagging.
    con_lai, da_dong = [], 0
    for ban_ghi in dong:
        duong = ban_ghi.get("duong_dan")
        if duong and os.path.isdir(duong):
            con_lai.append(ban_ghi)
            continue
        # A row with no path can never be acted on, and it would keep the qc gate shut
        # forever. Close it — losing a broken row beats deadlocking the workflow.
        ly_do = "bien-mat" if duong else "thieu-duong-dan"
        so_wt.dong_dong(project, ban_ghi.get("slug"), ban_ghi.get("ma_task"), ly_do)
        da_dong += 1
        print(f"closed row {ban_ghi.get('ma_task')}: {ly_do}")
    if da_dong:
        # Without prune git keeps the dead entry in .git/worktrees and refuses to open
        # the same task again.
        _git(project, "worktree", "prune")

    canh_bao, goi_y, tong_byte = [], [], 0
    print("| Task | Request | Path | Age (days) | Size (MB) | Clean? | Merged? |")
    print("|---|---|---|---|---|---|---|")
    for ban_ghi in con_lai:
        duong, nhanh, slug = ban_ghi["duong_dan"], ban_ghi["nhanh"], ban_ghi["slug"]
        tich_hop = _nhanh_tich_hop(slug)
        byte = _kich_thuoc(duong)
        tong_byte += byte
        tuoi = _tuoi_ngay(ban_ghi.get("tao_luc"))
        sach = _sach(duong)
        merged = _da_merge(project, nhanh, tich_hop)
        print(f"| {ban_ghi['ma_task']} | {slug} | {duong} | {tuoi} | "
              f"{_doc_mb(byte):.1f} | {'yes' if sach else 'no'} | "
              f"{'yes' if merged else 'no'} |")
        if tuoi > so_wt.TRAN_TUOI_NGAY:
            canh_bao.append(f"WARNING: {ban_ghi['ma_task']} is {tuoi} days old "
                            f"(threshold {so_wt.TRAN_TUOI_NGAY} days) — clean it up.")
        if args.don:
            chan = _thu_don(project, slug, ban_ghi["ma_task"], nhanh, duong, tich_hop)
            if chan is None:
                print(f"  cleaned: {ban_ghi['ma_task']}")
                tong_byte -= byte
                continue
            goi_y.append(chan)
        else:
            chan = _ly_do_chan(project, ban_ghi["ma_task"], nhanh, duong, tich_hop)
            if chan is not None:
                goi_y.append(chan)
    if not con_lai:
        print("(the ledger holds no open worktree)")

    biet = {os.path.realpath(d["duong_dan"]) for d in con_lai if d.get("duong_dan")}
    ngoai, la = [], []
    for w in _liet_ke_worktree(project)[1:]:
        that = os.path.realpath(w["duong_dan"])
        if not that.startswith(goc):
            ngoai.append(w["duong_dan"])
        elif that not in biet:
            la.append(w)
    if la:
        # The integration worktree lands here, and so does anything left behind by an
        # older version of this tool. In scope, so it is cleaned — but only its
        # DIRECTORY: the integration branch is what holds the merged work (decision D5).
        print("")
        print("In scope, no ledger row:")
        for w in la:
            duong = w["duong_dan"]
            print(f"  {duong}")
            if not args.don:
                continue
            chan = _ly_do_chan_thu_muc(project, os.path.basename(duong),
                                       w.get("nhanh", ""), duong)
            if chan is None:
                loi = _go_thu_muc(project, duong)
                if loi is None:
                    print(f"  cleaned: {duong}")
                    continue
                chan = _ly_do_tu_choi(project, os.path.basename(duong),
                                      w.get("nhanh", ""), duong, loi[0])
            goi_y.append(chan)
        _git(project, "worktree", "prune")
    if ngoai:
        print("")
        print("Out of scope (listed only, never removed — they live outside "
              f"{goc}):")
        for duong in ngoai:
            print(f"  {duong}")

    if _doc_mb(tong_byte) > so_wt.TRAN_TONG_MB:
        canh_bao.append(f"WARNING: worktrees take {_doc_mb(tong_byte):.0f} MB "
                        f"(threshold {so_wt.TRAN_TONG_MB} MB) — clean them up.")
    so_wt.ghi_md(project)
    _log(f"soat → {len(con_lai)} open · {_doc_mb(tong_byte):.1f} MB · "
         f"{len(goi_y)} kept back")
    for dong_canh in canh_bao:
        print(dong_canh)
    _in_goi_y(goi_y)
    # Spec §2 output 4: a dirty worktree exits non-zero. Not merged yet is a normal state
    # of a running wave, so it is reported without failing the command.
    return 1 if any(m["ly_do"] in ("ban", "bo-qua") for m in goi_y) else 0


def lenh_don(project, _args):
    slug, _plan, _ban_do = _boi_canh(project, can_ban_do=False)
    if not _la_repo(project):
        raise LoiLuat("This directory is not a git repo.")
    goc = os.path.join(_thu_muc_goc_worktree(project), slug)
    ra = _git(project, "worktree", "list", "--porcelain").stdout
    duong_list = [d.split(" ", 1)[1] for d in ra.splitlines() if d.startswith("worktree ")]
    da_go = 0
    # realpath on both sides: on macOS `/var` is a symlink of `/private/var`, so comparing
    # by abspath misses and `don` silently removes nothing.
    goc_that = os.path.realpath(goc)
    giu = []
    for duong in duong_list:
        if os.path.realpath(duong).startswith(goc_that):
            # An end-of-wave cleanup must never be the thing that eats work nobody
            # committed yet: keep it, name it, let the user decide.
            chan = _ly_do_chan_thu_muc(project, os.path.basename(duong), "", duong)
            if chan is not None:
                giu.append(chan)
                continue
            # `git worktree remove`, NOT `rm -rf`: deleting by hand leaves junk in
            # .git/worktrees and git still thinks the worktree is alive (research §2).
            loi = _go_thu_muc(project, duong)
            if loi is not None:
                giu.append(_ly_do_tu_choi(project, os.path.basename(duong), "",
                                          duong, loi[0]))
                continue
            da_go += 1
    _git(project, "worktree", "prune")
    _log(f"don → removed {da_go} worktree(s), kept {len(giu)}")
    print(f"Removed {da_go} worktree(s) of {slug}, pruned.")
    _in_goi_y(giu)
    return 0


# ------------------------------------------- anti rule-bending (used by the hook)
def canh_bao_lach_luat(cwd, rel_target):
    """The user picked team mode but the leader types code of a task it promised away → warn.

    Returns None when there is nothing to say. Returns dict {kieu, ma, nhanh} on a finding.
    This function is the ONLY place deciding "is the rule being bent" — the hook only prints.
    Only inspected when: phase implement + mode subagent + the file sits in the area of a
    task recorded as `giao` that has no branch of its own yet.
    """
    try:
        state = tdq_state.load(cwd, heal=False) or {}
        if tdq_state.effective_phase(state, warn=False) != "implement":
            return None
        if tdq_state.effective_mode(state, warn=False) != "subagent":
            return None
        slug = state.get("active_request")
        if not slug:
            return None
        rel = state.get("plan_file") or os.path.join("docs", "tdq", "plan", f"{slug}.md")
        plan = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        if not os.path.isfile(plan):
            return None
        duong = duong_ban_do(cwd, slug)
        if not os.path.isfile(duong):
            return {"kieu": "chua-phan-cong", "ma": None, "nhanh": None}
        try:
            with open(duong, encoding="utf-8") as f:
                ban_do = json.load(f)
        except (ValueError, UnicodeDecodeError):
            # A map that cannot be read = nobody can prove this task was assigned or kept.
            # Failing open here throws wide the very door the map exists to guard.
            return {"kieu": "ban-do-hong", "ma": None, "nhanh": None}
        if not isinstance(ban_do, dict) or not isinstance(ban_do.get("tasks"), dict):
            return {"kieu": "ban-do-hong", "ma": None, "nhanh": None}
        if ban_do.get("plan_sha") != sha_file(plan):
            return {"kieu": "chua-phan-cong", "ma": None, "nhanh": None}
        muc_tieu = rel_target.replace(os.sep, "/")
        tasks = {t.ma: t for t in doc_plan(plan)}
        for ma, rec in ban_do.get("tasks", {}).items():
            if muc_tieu not in [d.replace(os.sep, "/") for d in rec.get("vung_file", [])]:
                continue
            if rec.get("quyet_dinh") != "giao":
                return None                      # the leader legitimately kept this task
            t = tasks.get(ma)
            if t is not None and t.xong:
                return None                      # already merged; editing on is the leader's job
            nhanh = _ten_nhanh(slug, ma)
            if _la_repo(cwd) and _co_nhanh(cwd, nhanh):
                return None                      # the sub-agent already has its own place to work
            return {"kieu": "da-giao-thieu-nhanh" if (t and t.da_giao) else "chua-mo-nhanh",
                    "ma": ma, "nhanh": nhanh}
        return None
    except Exception:
        # This function must never kill the hook — silence is worse than a false block.
        return None


# ------------------------------------------------------------------ CLI
LENH = {
    "phan-cong": (lenh_phan_cong, "read the whole plan, write the assignment map"),
    "kiem-ke": (lenh_kiem_ke, "audit the map: a kept task must cite 1 closed reason"),
    "cum": (lenh_cum, "print the next wave, minus the locked file areas"),
    "mo": (lenh_mo, "create a branch + worktree for one task"),
    "kiem": (lenh_kiem, "probe for conflicts with the integration branch, repo untouched"),
    "hop": (lenh_hop, "merge the task's branch into the integration branch"),
    "soat": (lenh_soat, "sweep every worktree of every request: age, size, clean, merged"),
    "don": (lenh_don, "remove the request's worktrees and prune"),
}


def build_parser():
    p = argparse.ArgumentParser(
        prog="tdq_team.py",
        description="Team-mode orchestration: the leader assigns, sub-agents run in parallel.")
    sub = p.add_subparsers(dest="lenh")
    for ten, (_ham, mo_ta) in LENH.items():
        con = sub.add_parser(ten, help=mo_ta)
        if ten in ("mo", "kiem", "hop"):
            con.add_argument("task", help="task code (T1.1) or the full branch name")
        if ten == "soat":
            con.add_argument("--don", action="store_true",
                             help="also remove every worktree that passes all 3 conditions")
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.lenh:
        parser.print_usage(sys.stderr)
        _loi("Missing sub-command. Available: " + " · ".join(LENH))
        return 2
    project = _project_dir()
    _log(f"{args.lenh} · project={project}")
    try:
        return LENH[args.lenh][0](project, args)
    except LoiLuat as exc:
        _loi(str(exc))
        return 1
    except so_wt.LoiSo as exc:
        _loi(f"The worktree ledger is unusable: {exc}")
        _loi("Fix docs/tdq/worktrees.json (or delete it) before opening any worktree.")
        return 1
    except subprocess.TimeoutExpired:
        _loi("git took too long — aborted, nothing else touched.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
