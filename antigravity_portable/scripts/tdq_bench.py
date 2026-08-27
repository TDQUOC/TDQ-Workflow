#!/usr/bin/env python3
"""Weigh mode `main` against team mode (subagent) in numbers, not in feelings.

Four sub-commands:
    dung-plan  — generate a sample TDQ plan: N tasks, adjustable file overlap and dependencies
    thuc-do    — build a temp git repo, run a full `tdq_team.py` round, time it, write JSON
    mo-phong   — compute T_main and T_team for one plan, print the comparison table
    quet       — sweep the splittable ratio 0→100%, point out where the winner flips

Why it is separate from `tdq_team.py`: this is a MEASURING tool, not a tool doing real work.
It may only read the wave-splitting rule of `tdq_team.py`, never copy it — a copy measures
a model different from the thing actually running.

Formula (§3 of the spec of request 2026-08-17-2001-smoke-test-main-vs-doi):

        T_main = Σ(every task) t_task + n_task × t_tick
        T_team = Σ(each wave) [ t_phat + max(t_task in the wave) + t_kiem + t_hop ] + t_don
                          + max(0, Σ t_task(tu_lam) − Σ_wave max(t_task))

Every constant must come from a real measurement file. A missing file or missing constant
is an ERROR — no defaults, because one invented constant makes the whole table meaningless.

Exit code: 0 = fine · 1 = missing facts / rule broken · 2 = wrong usage.
Env: TDQ_LOG=0 mutes the log.
"""
import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
import tdq_state  # noqa: E402
import tdq_team  # noqa: E402

GIT_TIMEOUT = 120
# The six constants of the formula. One missing means no computation — there is no default.
HANG_SO = ("t_task", "t_tick", "t_phat", "t_kiem", "t_hop", "t_don")
NGUON_HOP_LE = ("that", "stub")
SO_MAU_TOI_THIEU = 3


class LoiThieuSo(Exception):
    """Missing a real number to compute with — exit 1, with the command that measures it."""


# --------------------------------------------------------------- log service
def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: one ISO-timestamped line on stderr. Muted with TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}",
              file=sys.stderr)


def _loi(message):
    print(message, file=sys.stderr)


# --------------------------------------------------- generate a sample plan
FILE_CHUNG = "src/chung.py"


def sinh_plan(so_task, chong=0.0, phu_thuoc=0, ngay=None, phase=1):
    """Returns (the plan text, the number of file-overlapping task pairs).

    `chong` is the share of tasks crowded into the SAME file `src/chung.py`. That is the real
    shape of a plan that is hard to split: tasks editing one module have to queue up. The
    number of overlapping pairs is therefore 2-combinations of the crowded task count.
    """
    if so_task < 1:
        raise LoiThieuSo("--task must be ≥ 1.")
    if not 0.0 <= chong <= 1.0:
        raise LoiThieuSo("--chong must lie in [0, 1].")
    if phu_thuoc < 0 or phu_thuoc >= so_task:
        raise LoiThieuSo("--phu-thuoc must be ≥ 0 and smaller than the task count.")
    so_chong = round(chong * so_task)
    so_cap = so_chong * (so_chong - 1) // 2
    ngay = ngay or date.today().isoformat()
    dong = [
        f"# PLAN — Plan mẫu đo benchmark ({so_task} task)",  # i18n-allow
        "",
        f"Ngày: {ngay} · Sinh bằng lệnh `dung-plan` của `scripts/tdq_bench.py`. "  # i18n-allow
        "Đây là bài thi, không phải việc thật.",  # i18n-allow
        "Soul: chất lượng > runtime > context cost · luật gốc: "  # i18n-allow
        "skills/tdq-conventions/references/soul.md",
        f"Mode thực thi: subagent — plan mẫu dựng để đo, không thi hành. "  # i18n-allow
        f"Tham số: chồng {chong}, phụ thuộc {phu_thuoc}.",  # i18n-allow
        "Trạng thái plan: MẪU (không duyệt, không thi hành)",  # i18n-allow
        "",
        f"## P{phase} — Việc mẫu",  # i18n-allow
        "",
    ]
    for i in range(1, so_task + 1):
        ma = f"T{phase}.{i}"
        duong = FILE_CHUNG if i <= so_chong else f"src/mo_dun_{i:02d}.py"
        viec = f"Việc mẫu số {i}"  # i18n-allow
        if i > so_task - phu_thuoc and i > 1:
            viec += f", nối tiếp T{phase}.{i - 1}"  # i18n-allow
        dong.append(f"- [ ] **{ma}** (n3 e10m) {viec} — Test: hàm mẫu trả đúng giá trị")  # i18n-allow
        dong.append(f"  - Chạm: `{duong}`")  # i18n-allow
    dong += [
        "",
        f"**Xong P{phase} khi**: mọi task mẫu tick xong.",  # i18n-allow
        "",
        "## Definition of Done",
        "",
        f"1. {so_task} task đều tick `[x]`.",  # i18n-allow
        f"2. Số cặp task chồng file đúng bằng {so_cap}.",  # i18n-allow
        "",
    ]
    return "\n".join(dong), so_cap


def _tasks_tu_van_ban(van_ban):
    """Read the plan from a string with tdq_team's OWN reader (never copy the rule)."""
    with tempfile.TemporaryDirectory() as tmp:
        duong = os.path.join(tmp, "plan.md")
        with open(duong, "w", encoding="utf-8") as f:
            f.write(van_ban)
        return tdq_team.doc_plan(duong)


def dem_cap_chong(tasks):
    """The number of (unordered) task pairs sharing at least one file."""
    cap = 0
    for i, a in enumerate(tasks):
        for b in tasks[i + 1:]:
            if set(a.vung_file) & set(b.vung_file):
                cap += 1
    return cap


# --------------------------------------------------------------- constants
def _thong_ke(mau, nguon, cach_do="may", mau_may=None):
    """cach_do: "may" = this script timed it · "nhap-tay" = a human number via --mau-that.

    Keep `mau_may` even when a hand-entered number OVERRIDES the machine one: losing the
    machine sample leaves no way to judge whether the hand-entered number is sane.
    """
    rec = {
        "giay": round(statistics.fmean(mau), 6),
        "so_mau": len(mau),
        "do_tan": round(statistics.pstdev(mau), 6) if len(mau) > 1 else 0.0,
        "nguon": nguon,
        "cach_do": cach_do,
        "mau": [round(x, 6) for x in mau],
    }
    if mau_may:
        rec["mau_may"] = [round(x, 6) for x in mau_may]
    return rec


def nap_hang_so(duong):
    """dict name → seconds. A missing file or a missing constant raises LoiThieuSo."""
    if not duong:
        raise LoiThieuSo(
            "No measurement file given. Add --thuc-do <file.json>, or measure first: "
            "python3 scripts/tdq_bench.py thuc-do --ra docs/tdq/bench/<slug>-thuc-do.json")
    if not os.path.isfile(duong):
        raise LoiThieuSo(
            f"Measurement file missing: {duong}. No real numbers means NO simulation — "
            f"run: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
    try:
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
    except (ValueError, UnicodeDecodeError) as loi:
        raise LoiThieuSo(f"Measurement file broken ({duong}): {loi}. Measure again with thuc-do.")
    bang = du_lieu.get("hang_so")
    if not isinstance(bang, dict):
        raise LoiThieuSo(f"Measurement file {duong} has no \"hang_so\" section.")
    thieu = [ten for ten in HANG_SO if ten not in bang]
    if thieu:
        raise LoiThieuSo(
            f"Measurement file {duong} is missing constant(s): {', '.join(thieu)}. "
            f"Measure again: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
    ra = {}
    for ten in HANG_SO:
        rec = bang[ten]
        if not isinstance(rec, dict) or "giay" not in rec:
            raise LoiThieuSo(f"Constant {ten} in {duong} has no \"giay\" field.")
        try:
            giay = float(rec["giay"])
        except (TypeError, ValueError):
            raise LoiThieuSo(
                f"Constant {ten} in {duong} has giay = {rec['giay']!r}, which is not a number. "
                f"Measure again: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
        if not giay > 0 or giay != giay or giay == float("inf"):
            raise LoiThieuSo(
                f"Constant {ten} in {duong} is {giay} — a duration must be a positive finite "
                f"number. Measure again: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
        # This gate must lock at the READING end, not only at the writing end: the file can be
        # hand-edited after it was written, and the simulation would believe it on sight.
        so_mau = rec.get("so_mau")
        if not isinstance(so_mau, int) or so_mau < SO_MAU_TOI_THIEU:
            raise LoiThieuSo(
                f"Constant {ten} in {duong} only carries so_mau = {so_mau!r}, at least "
                f"{SO_MAU_TOI_THIEU} are needed. Measure again: python3 scripts/tdq_bench.py thuc-do "
                f"--ra {duong}")
        ra[ten] = giay
    return ra


# --------------------------------------------------------------- simulation
class KetQua:
    """Result of simulating one plan: every number needed to print and hand-check the table."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def mo_phong_tasks(tasks, hs, he_so_agent=1.0):
    """Apply the §3 formula of the spec to the list of Tasks read off the plan.

    `he_so_agent` is how many times SLOWER a sub-agent is than the leader on the same task.
    The default 1.0 is the spec's assumption (both equally fast). This lever is as strong as
    `t_phat`: an agent 25% slower moves the break-even from 10% to 30%. Without the parameter
    the reader has no way to discount, so it has to be a first-class parameter.
    """
    if not tasks:
        raise LoiThieuSo("The plan holds no readable task.")
    quyet = {t.ma: tdq_team.quyet_dinh_task(t, tasks) for t in tasks}
    dot_theo_task = tdq_team.chia_dot(tasks, quyet)
    giao = [t for t in tasks if quyet[t.ma][0] == "giao"]
    tu_lam = [t for t in tasks if quyet[t.ma][0] == "tu_lam"]
    dot = {}
    for t in giao:
        dot.setdefault(dot_theo_task[t.ma], []).append(t)

    if not he_so_agent > 0:
        raise LoiThieuSo("--he-so-agent must be a positive number (1.0 = as fast as the leader).")
    n = len(tasks)
    t_main = n * hs["t_task"] + n * hs["t_tick"]

    # Every wave pays a fixed fee, and in exchange waits only for its slowest task.
    t_task_agent = hs["t_task"] * he_so_agent
    tong_max = sum(t_task_agent for _ in dot)          # uniform tasks → max = t_task
    phi_dot = len(dot) * (hs["t_phat"] + hs["t_kiem"] + hs["t_hop"])
    # A task the leader keeps is done by the leader, so it still counts at leader speed.
    chen = max(0.0, len(tu_lam) * hs["t_task"] - tong_max)
    t_doi = phi_dot + tong_max + hs["t_don"] + chen
    # Bias-check variant: the spec formula does NOT count t_tick for team mode, although the
    # leader still ticks every task in both modes. Computed too, to expose that gap.
    t_doi_kem_tick = t_doi + n * hs["t_tick"]
    return KetQua(
        so_task=n, so_giao=len(giao), so_tu_lam=len(tu_lam), so_dot=len(dot),
        t_main=t_main, t_doi=t_doi, t_doi_kem_tick=t_doi_kem_tick,
        chen=chen, phi_dot=phi_dot, tong_max=tong_max, he_so_agent=he_so_agent,
        thang="đội" if t_doi < t_main else ("main" if t_doi > t_main else "hoà"),  # i18n-allow
    )


def mo_phong_van_ban(van_ban, hs, he_so_agent=1.0):
    return mo_phong_tasks(_tasks_tu_van_ban(van_ban), hs, he_so_agent)


def _phut(giay):
    return f"{giay / 60:.1f}"


# --------------------------------------------------- real measurement (temp repo)
def _git(cwd, *args, check=True):
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True, errors="replace", timeout=GIT_TIMEOUT)
    if check and proc.returncode != 0:
        raise LoiThieuSo(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def _team(repo, *args, wt=None):
    """Run tdq_team.py on the temp repo. Returns (seconds, returncode, stdout)."""
    env = dict(os.environ, TDQ_PROJECT_DIR=repo, TDQ_LOG="0")
    if wt:
        env["TDQ_WORKTREE_DIR"] = wt
    bat_dau = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, "tdq_team.py"), *args],
        capture_output=True, text=True, timeout=GIT_TIMEOUT, env=env)
    return time.perf_counter() - bat_dau, proc.returncode, proc.stdout + proc.stderr


def _dung_repo_tam(goc, slug, so_task):
    """Temp git repo + sample plan + state — enough for tdq_team.py to really run on it."""
    repo = os.path.join(goc, "repo")
    os.makedirs(os.path.join(repo, "docs", "tdq", "plan"))
    os.makedirs(os.path.join(repo, "src"))
    _git_init(repo)
    van_ban, _ = sinh_plan(so_task, chong=0.0)
    rel = os.path.join("docs", "tdq", "plan", f"{slug}.md")
    with open(os.path.join(repo, rel), "w", encoding="utf-8") as f:
        f.write(van_ban)
    for i in range(1, so_task + 1):
        with open(os.path.join(repo, "src", f"mo_dun_{i:02d}.py"), "w",
                  encoding="utf-8") as f:
            f.write("gia_tri = 0\n")
    state = tdq_state.default_state()
    state["active_request"] = slug
    state["lane"] = "full"
    state["phase"] = "implement"
    state["plan_file"] = rel
    state["plan_approved"] = True
    state["implement_mode"] = "subagent"
    tdq_state.save(repo, state)
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=bench@tdq", "-c", "user.name=bench",
         "commit", "-m", "plan mau")
    return repo, rel


def _git_init(repo):
    subprocess.run(["git", "init", "-q", "-b", "main", repo],
                   capture_output=True, text=True, timeout=GIT_TIMEOUT, check=True)
    _git(repo, "config", "user.email", "bench@tdq")
    _git(repo, "config", "user.name", "bench")


def _agent_stub(worktree, ma):
    """Play the sub-agent: edit a file in its worktree, then commit. Returns seconds.

    The stub measures only the MECHANICAL part (write file + commit). It is the floor of
    `t_task`, not the real number — the real one comes from an agent round, via --mau-that.
    """
    bat_dau = time.perf_counter()
    ten = os.path.join(worktree, "src", f"mo_dun_{int(ma.split('.')[1]):02d}.py")
    os.makedirs(os.path.dirname(ten), exist_ok=True)
    with open(ten, "w", encoding="utf-8") as f:
        f.write(f"gia_tri = {ma!r}\n")
    _git(worktree, "add", "-A")
    _git(worktree, "-c", "user.email=bench@tdq", "-c", "user.name=bench",
         "commit", "-m", f"{ma} xong")
    return time.perf_counter() - bat_dau


def _do_mot_luot(so_task):
    """One full measuring round in the temp repo. Returns dict constant name → samples."""
    mau = {ten: [] for ten in HANG_SO}
    goc = tempfile.mkdtemp(prefix="tdq-bench-")
    repo = None
    try:
        slug = "2026-01-01-0000-plan-mau-bench"
        repo, rel = _dung_repo_tam(goc, slug, so_task)
        wt = os.path.join(goc, "worktrees")
        # The tick is measured on a COPY of the plan: `tdq_team.py` locks the map to the plan sha,
        # so editing the plan mid-round would kill the round itself. The copy holds identical
        # content, so the I/O measured is still that of a real tick.
        plan_sao = os.path.join(goc, "plan-tick.md")
        shutil.copyfile(os.path.join(repo, rel), plan_sao)
        giay, rc, ra = _team(repo, "phan-cong", wt=wt)
        if rc != 0:
            raise LoiThieuSo(f"phan-cong failed in the temp repo: {ra.strip()}")
        chuan_bi = giay
        giay, rc, ra = _team(repo, "kiem-ke", wt=wt)
        if rc != 0:
            raise LoiThieuSo(f"kiem-ke failed in the temp repo: {ra.strip()}")
        chuan_bi += giay
        giay_cum, _rc, _ra = _team(repo, "cum", wt=wt)
        # t_phat of a wave = preparing the map + `cum` + `mo` for each task of the wave.
        phat = chuan_bi + giay_cum
        for i in range(1, so_task + 1):
            ma = f"T1.{i}"
            giay, rc, ra = _team(repo, "mo", ma, wt=wt)
            if rc != 0:
                raise LoiThieuSo(f"mo {ma} failed: {ra.strip()}")
            phat += giay
        mau["t_phat"].append(phat)
        for i in range(1, so_task + 1):
            ma = f"T1.{i}"
            worktree = os.path.join(wt, slug, ma.lower())
            mau["t_task"].append(_agent_stub(worktree, ma))
            giay, rc, ra = _team(repo, "kiem", ma, wt=wt)
            if rc != 0:
                raise LoiThieuSo(f"kiem {ma} reported an unexpected conflict: {ra.strip()}")
            mau["t_kiem"].append(giay)
            giay, rc, ra = _team(repo, "hop", ma, wt=wt)
            if rc != 0:
                raise LoiThieuSo(f"hop {ma} failed: {ra.strip()}")
            mau["t_hop"].append(giay)
            mau["t_tick"].append(_do_tick(plan_sao, ma))
        giay, _rc, _ra = _team(repo, "don", wt=wt)
        mau["t_don"].append(giay)
        return mau
    finally:
        if repo:
            _team(repo, "don", wt=os.path.join(goc, "worktrees"))
        shutil.rmtree(goc, ignore_errors=True)


def _do_tick(duong_plan, ma):
    """Measure what the leader does per task: read the plan, flip the tick, write it back."""
    bat_dau = time.perf_counter()
    with open(duong_plan, encoding="utf-8") as f:
        noi_dung = f.read()
    noi_dung = noi_dung.replace(f"- [ ] **{ma}**", f"- [x] **{ma}**", 1)
    with open(duong_plan, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    return time.perf_counter() - bat_dau


def _doc_mau_that(chuoi):
    """"t_task=91.2,t_task=104.7" → {"t_task": [91.2, 104.7]}."""
    ra = {}
    for phan in (chuoi or "").split(","):
        phan = phan.strip()
        if not phan:
            continue
        if "=" not in phan:
            raise LoiThieuSo(f"--mau-that is malformed at \"{phan}\" — use name=seconds.")
        ten, gia_tri = phan.split("=", 1)
        ten = ten.strip()
        if ten not in HANG_SO:
            raise LoiThieuSo(f"--mau-that: no constant named \"{ten}\". "
                             f"Accepted: {', '.join(HANG_SO)}")
        try:
            ra.setdefault(ten, []).append(float(gia_tri))
        except ValueError:
            raise LoiThieuSo(f"--mau-that: \"{gia_tri}\" is not a number of seconds.")
    return ra


# --------------------------------------------------------------- sub-commands
def lenh_dung_plan(args):
    van_ban, so_cap = sinh_plan(args.task, args.chong, args.phu_thuoc, args.ngay)
    tasks = _tasks_tu_van_ban(van_ban)
    that = dem_cap_chong(tasks)
    if that != so_cap:
        raise LoiThieuSo(f"Bad generation: computed {so_cap} overlapping pairs, read back {that}.")
    _log(f"dung-plan → {args.task} task(s) · {so_cap} overlapping file pair(s)")
    if args.ra:
        try:
            with open(args.ra, "w", encoding="utf-8") as f:
                f.write(van_ban)
        except OSError as loi:
            raise LoiThieuSo(
                f"Cannot write {args.ra}: {loi}. Create the directory first "
                f"(mkdir -p {os.path.dirname(args.ra) or '.'}), or drop --ra: "
                f"python3 scripts/tdq_bench.py dung-plan --task {args.task}")
        print(f"Sample plan: {args.ra}")
        print(f"{len(tasks)} task(s) · {so_cap} overlapping file pair(s)")
    else:
        sys.stdout.write(van_ban)
    return 0


def lenh_thuc_do(args):
    # --lap 0 + --mau-that = all 6 constants invented while the file still says nguon=that.
    # Blocked here, and cach_do is written per constant so machine and hand stay apart.
    if args.lap < 1:
        raise LoiThieuSo(
            f"--lap = {args.lap} — at least 1 machine round is required. "
            f"Run: python3 scripts/tdq_bench.py thuc-do --lap 3 --ra {args.ra}")
    mau = {ten: [] for ten in HANG_SO}
    nguon = {ten: "stub" for ten in HANG_SO}
    cach_do = {ten: "may" for ten in HANG_SO}
    for lan in range(args.lap):
        _log(f"thuc-do → round {lan + 1}/{args.lap} in a temp git repo")
        for ten, gia_tri in _do_mot_luot(args.task).items():
            mau[ten].extend(gia_tri)
    that = _doc_mau_that(args.mau_that)
    mau_may = {ten: list(gia_tri) for ten, gia_tri in mau.items()}
    for ten, gia_tri in that.items():
        mau[ten] = gia_tri            # a real number replaces the stub outright, never mixed
        nguon[ten] = "that"
        cach_do[ten] = "nhap-tay"
    thieu = [ten for ten in HANG_SO if len(mau[ten]) < SO_MAU_TOI_THIEU]
    if thieu and not args.cho_it_mau:
        raise LoiThieuSo(
            f"Not yet {SO_MAU_TOI_THIEU} samples for: {', '.join(thieu)}. "
            f"Raise --lap or --task, or feed real numbers with --mau-that.")
    du_lieu = {
        "slug": args.slug,
        "ngay": args.ngay or date.today().isoformat(),
        "may": {"python": platform.python_version(), "he_dieu_hanh": platform.platform()},
        "ghi_chu": "nguon=stub is the mechanical floor; nguon=that is timed from a real agent "
                   "round. cach_do=nhap-tay means a human entered it, the machine sample stays in mau_may",
        "hang_so": {
            ten: _thong_ke(mau[ten], nguon[ten], cach_do[ten],
                           mau_may[ten] if cach_do[ten] == "nhap-tay" else None)
            for ten in HANG_SO
        },
    }
    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.ra)), exist_ok=True)
        with open(args.ra, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as loi:
        raise LoiThieuSo(f"Cannot write {args.ra}: {loi}. "
                         f"Create the parent directory first, then run again.")
    print(f"Measurement: {args.ra}")
    for ten in HANG_SO:
        rec = du_lieu["hang_so"][ten]
        print(f"  {ten:8s} {rec['giay']:9.3f}s  ±{rec['do_tan']:.3f}  "
              f"n={rec['so_mau']}  source={rec['nguon']}  method={rec['cach_do']}")
    return 0


def lenh_mo_phong(args):
    hs = nap_hang_so(args.thuc_do)
    if args.plan:
        try:
            with open(args.plan, encoding="utf-8") as f:
                van_ban = f.read()
        except OSError as loi:
            raise LoiThieuSo(
                f"Cannot read the plan {args.plan}: {loi}. Check the path, or drop "
                f"--plan to use a sample plan: python3 scripts/tdq_bench.py mo-phong "
                f"--thuc-do {args.thuc_do} --task 12")
    else:
        van_ban, _ = sinh_plan(args.task, args.chong, args.phu_thuoc)
    kq = mo_phong_van_ban(van_ban, hs, args.he_so_agent)
    _log(f"mo-phong → {kq.so_task} task(s) · {kq.so_dot} wave(s) · winner: {kq.thang}")
    print(f"Plan: {kq.so_task} task(s) · assigned {kq.so_giao} · leader keeps {kq.so_tu_lam} "
          f"· {kq.so_dot} wave(s) · agent factor {kq.he_so_agent}")
    print("| Metric | main | team |")
    print("|---|---|---|")
    print(f"| Model time (minutes) | {_phut(kq.t_main)} | {_phut(kq.t_doi)} |")
    print(f"| Fixed fee per wave (minutes) | 0.0 | {_phut(kq.phi_dot)} |")
    print(f"| Waiting on the slowest task (minutes) | — | {_phut(kq.tong_max)} |")
    print(f"| Leader working in between (minutes) | — | {_phut(kq.chen)} |")
    print(f"| Including t_tick (minutes) | {_phut(kq.t_main)} | {_phut(kq.t_doi_kem_tick)} |")
    print(f"Winner: {kq.thang} (gap {_phut(abs(kq.t_main - kq.t_doi))} minutes)")
    return 0


def lenh_quet(args):
    # --buoc 0 makes range() blow up, a negative --buoc gives an EMPTY table and still prints
    # a conclusion — an empty table with a conclusion is worse than an error, so block it here.
    if not 1 <= args.buoc <= 100:
        raise LoiThieuSo(
            f"--buoc = {args.buoc} — must lie in 1–100. "
            f"Run: python3 scripts/tdq_bench.py quet --buoc 10 --thuc-do {args.thuc_do}")
    hs = nap_hang_so(args.thuc_do)
    print(f"Sweep {args.task} task(s) · splittable ratio 0→100% · step {args.buoc}% "
          f"· agent factor {args.he_so_agent}")
    print("| Splittable | Waves | T_main (min) | T_team (min) | Winner |")
    print("|---|---|---|---|---|")
    truoc = None
    nguong = []
    for phan_tram in range(0, 101, args.buoc):
        chong = round(1 - phan_tram / 100, 4)
        van_ban, _ = sinh_plan(args.task, chong)
        kq = mo_phong_van_ban(van_ban, hs, args.he_so_agent)
        print(f"| {phan_tram}% | {kq.so_dot} | {_phut(kq.t_main)} | "
              f"{_phut(kq.t_doi)} | {kq.thang} |")
        if truoc is not None and kq.thang != truoc:
            nguong.append((phan_tram, truoc, kq.thang))
        truoc = kq.thang
    if not nguong:
        print(f"No flip in this range: {truoc} wins at every ratio.")
        _log("quet → no flip point")
        return 0
    for phan_tram, cu, moi in nguong:
        print(f"THRESHOLD: at a splittable ratio of {phan_tram}% the winner flips "
              f"{cu} → {moi}.")
    _log(f"quet → {len(nguong)} flip point(s)")
    return 0


LENH = {
    "dung-plan": (lenh_dung_plan, "generate a sample N-task plan with adjustable file overlap"),
    "thuc-do": (lenh_thuc_do, "run a real team round in a temp repo, write constants to JSON"),
    "mo-phong": (lenh_mo_phong, "compute T_main and T_team for one plan"),
    "quet": (lenh_quet, "sweep the splittable ratio, find the flip point"),
}


def build_parser():
    p = argparse.ArgumentParser(
        prog="tdq_bench.py",
        description="Weigh mode main against team mode in measured numbers.")
    sub = p.add_subparsers(dest="lenh")

    dp = sub.add_parser("dung-plan", help=LENH["dung-plan"][1])
    dp.add_argument("--task", type=int, default=12, help="task count of the sample plan")
    dp.add_argument("--chong", type=float, default=0.0,
                    help="share of tasks crowded into one file (0→1)")
    dp.add_argument("--phu-thuoc", type=int, default=0, dest="phu_thuoc",
                    help="how many tasks name an earlier task code")
    dp.add_argument("--ngay", help="date written into the plan (default: today)")
    dp.add_argument("--ra", help="write to a file; without it, print to stdout")

    td = sub.add_parser("thuc-do", help=LENH["thuc-do"][1])
    td.add_argument("--ra", required=True, help="JSON file of constants")
    td.add_argument("--task", type=int, default=3, help="tasks per measuring round")
    td.add_argument("--lap", type=int, default=3, help="how many rounds")
    td.add_argument("--slug", default="", help="request slug written into the file")
    td.add_argument("--ngay", help="date written into the file")
    td.add_argument("--mau-that", dest="mau_that",
                    help="samples from a real agent round, shape \"t_task=91.2,t_task=104.7\"")
    td.add_argument("--cho-it-mau", action="store_true", dest="cho_it_mau",
                    help="allow writing with fewer than 3 samples (debugging only)")

    mp = sub.add_parser("mo-phong", help=LENH["mo-phong"][1])
    mp.add_argument("--plan", help="plan file; without it, a sample plan is generated")
    mp.add_argument("--thuc-do", dest="thuc_do", help="JSON file of constants")
    mp.add_argument("--task", type=int, default=12)
    mp.add_argument("--chong", type=float, default=0.0)
    mp.add_argument("--phu-thuoc", type=int, default=0, dest="phu_thuoc")
    mp.add_argument("--he-so-agent", type=float, default=1.0, dest="he_so_agent",
                    help="how many times slower a sub-agent is than the leader (1.0 = equal)")

    qt = sub.add_parser("quet", help=LENH["quet"][1])
    qt.add_argument("--thuc-do", dest="thuc_do", help="JSON file of constants")
    qt.add_argument("--task", type=int, default=12)
    qt.add_argument("--buoc", type=int, default=10, help="sweep step in percent")
    qt.add_argument("--he-so-agent", type=float, default=1.0, dest="he_so_agent",
                    help="how many times slower a sub-agent is than the leader (1.0 = equal)")
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.lenh:
        parser.print_usage(sys.stderr)
        _loi("Missing sub-command. Available: " + " · ".join(LENH))
        return 2
    _log(f"{args.lenh} · {' '.join(argv[1:]) or '(no arguments)'}")
    try:
        return LENH[args.lenh][0](args)
    except LoiThieuSo as exc:
        _loi(str(exc))
        return 1
    except subprocess.TimeoutExpired:
        _loi("git took too long — aborted, nothing else touched.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
