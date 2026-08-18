#!/usr/bin/env python3
"""Cân đo mode `main` với mode đội (subagent) bằng số, không bằng cảm nhận.

Bốn lệnh con:
  dung-plan  — sinh một plan TDQ mẫu: N task, tỉ lệ chồng file và số task phụ thuộc đặt được
  thuc-do    — dựng repo git tạm, chạy đủ vòng của `tdq_team.py`, bấm giờ, ghi hằng số ra JSON
  mo-phong   — tính T_main và T_đội cho một plan, in bảng so sánh
  quet       — quét dải tỉ lệ tách được 0→100%, chỉ ra ngưỡng đổi chiều thắng-thua

Vì sao tách khỏi `tdq_team.py`: đây là dụng cụ ĐO, không phải dụng cụ chạy việc thật.
Nó chỉ được đọc luật chia đợt của `tdq_team.py`, không được chép lại luật đó — chép là
đo một mô hình khác với thứ đang chạy.

Công thức (spec §3 của request 2026-08-17-2001-smoke-test-main-vs-doi):

    T_main = Σ(mọi task) t_task + n_task × t_tick
    T_đội  = Σ(mỗi đợt) [ t_phat + max(t_task trong đợt) + t_kiem + t_hop ] + t_don
             + max(0, Σ t_task(tu_lam) − Σ_đợt max(t_task))

Mọi hằng số phải đến từ file thực đo. Thiếu file hoặc thiếu hằng số thì lệnh LỖI —
cấm đặt số mặc định, vì một hằng số bịa làm cả bảng kết quả thành vô nghĩa.

Exit code: 0 = ổn · 1 = thiếu dữ kiện / sai luật · 2 = dùng lệnh sai.
Env: TDQ_LOG=0 tắt log.
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
# Sáu hằng số của công thức. Thiếu một cái là không tính được — không có mặc định.
HANG_SO = ("t_task", "t_tick", "t_phat", "t_kiem", "t_hop", "t_don")
NGUON_HOP_LE = ("that", "stub")
SO_MAU_TOI_THIEU = 3


class LoiThieuSo(Exception):
    """Thiếu số thật để tính — exit 1, kèm câu lệnh lấy số."""


# --------------------------------------------------------------- log service
def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: 1 dòng ISO-timestamp ra stderr. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}",
              file=sys.stderr)


def _loi(message):
    print(message, file=sys.stderr)


# --------------------------------------------------------- sinh plan mẫu
FILE_CHUNG = "src/chung.py"


def sinh_plan(so_task, chong=0.0, phu_thuoc=0, ngay=None, phase=1):
    """Trả về (văn bản plan, số cặp task chồng file).

    `chong` là tỉ lệ task bị dồn vào CÙNG một file `src/chung.py`. Đó là hình dạng
    thật của một plan khó tách: mấy task cùng sửa một mô-đun thì phải nối đuôi nhau.
    Số cặp chồng vì thế bằng tổ hợp chập 2 của số task bị dồn.
    """
    if so_task < 1:
        raise LoiThieuSo("--task phải ≥ 1.")
    if not 0.0 <= chong <= 1.0:
        raise LoiThieuSo("--chong nằm trong [0, 1].")
    if phu_thuoc < 0 or phu_thuoc >= so_task:
        raise LoiThieuSo("--phu-thuoc phải ≥ 0 và nhỏ hơn số task.")
    so_chong = round(chong * so_task)
    so_cap = so_chong * (so_chong - 1) // 2
    ngay = ngay or date.today().isoformat()
    dong = [
        f"# PLAN — Plan mẫu đo benchmark ({so_task} task)",
        "",
        f"Ngày: {ngay} · Sinh bằng lệnh `dung-plan` của `scripts/tdq_bench.py`. "
        "Đây là bài thi, không phải việc thật.",
        "Soul: chất lượng > runtime > context cost · luật gốc: "
        "skills/tdq-conventions/references/soul.md",
        f"Mode thực thi: subagent — plan mẫu dựng để đo, không thi hành. "
        f"Tham số: chồng {chong}, phụ thuộc {phu_thuoc}.",
        "Trạng thái plan: MẪU (không duyệt, không thi hành)",
        "",
        f"## P{phase} — Việc mẫu",
        "",
    ]
    for i in range(1, so_task + 1):
        ma = f"T{phase}.{i}"
        duong = FILE_CHUNG if i <= so_chong else f"src/mo_dun_{i:02d}.py"
        viec = f"Việc mẫu số {i}"
        if i > so_task - phu_thuoc and i > 1:
            viec += f", nối tiếp T{phase}.{i - 1}"
        dong.append(f"- [ ] **{ma}** (n3 e10m) {viec} — Test: hàm mẫu trả đúng giá trị")
        dong.append(f"  - Chạm: `{duong}`")
    dong += [
        "",
        f"**Xong P{phase} khi**: mọi task mẫu tick xong.",
        "",
        "## Definition of Done",
        "",
        f"1. {so_task} task đều tick `[x]`.",
        f"2. Số cặp task chồng file đúng bằng {so_cap}.",
        "",
    ]
    return "\n".join(dong), so_cap


def _tasks_tu_van_ban(van_ban):
    """Đọc plan từ chuỗi bằng ĐÚNG bộ đọc của tdq_team (không chép lại luật)."""
    with tempfile.TemporaryDirectory() as tmp:
        duong = os.path.join(tmp, "plan.md")
        with open(duong, "w", encoding="utf-8") as f:
            f.write(van_ban)
        return tdq_team.doc_plan(duong)


def dem_cap_chong(tasks):
    """Số cặp task (không thứ tự) dùng chung ít nhất một file."""
    cap = 0
    for i, a in enumerate(tasks):
        for b in tasks[i + 1:]:
            if set(a.vung_file) & set(b.vung_file):
                cap += 1
    return cap


# --------------------------------------------------------------- hằng số
def _thong_ke(mau, nguon, cach_do="may", mau_may=None):
    """cach_do: "may" = chính script bấm giờ · "nhap-tay" = số người nhập qua --mau-that.

    Giữ luôn `mau_may` khi số nhập tay ĐÈ lên số máy đo: mất mẫu máy thì người đọc
    không còn cách nào biết con số nhập tay có hợp lý không.
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
    """dict tên → giây. Thiếu file hay thiếu hằng số thì ném LoiThieuSo."""
    if not duong:
        raise LoiThieuSo(
            "Chưa chỉ file thực đo. Thêm --thuc-do <file.json>, hoặc đo trước: "
            "python3 scripts/tdq_bench.py thuc-do --ra docs/tdq/bench/<slug>-thuc-do.json")
    if not os.path.isfile(duong):
        raise LoiThieuSo(
            f"Thiếu file thực đo: {duong}. Không có số thật thì KHÔNG mô phỏng — "
            f"chạy: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
    try:
        with open(duong, encoding="utf-8") as f:
            du_lieu = json.load(f)
    except (ValueError, UnicodeDecodeError) as loi:
        raise LoiThieuSo(f"File thực đo hỏng ({duong}): {loi}. Đo lại bằng lệnh thuc-do.")
    bang = du_lieu.get("hang_so")
    if not isinstance(bang, dict):
        raise LoiThieuSo(f"File thực đo {duong} không có mục \"hang_so\".")
    thieu = [ten for ten in HANG_SO if ten not in bang]
    if thieu:
        raise LoiThieuSo(
            f"File thực đo {duong} thiếu hằng số: {', '.join(thieu)}. "
            f"Đo lại: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
    ra = {}
    for ten in HANG_SO:
        rec = bang[ten]
        if not isinstance(rec, dict) or "giay" not in rec:
            raise LoiThieuSo(f"Hằng số {ten} trong {duong} không có trường \"giay\".")
        try:
            giay = float(rec["giay"])
        except (TypeError, ValueError):
            raise LoiThieuSo(
                f"Hằng số {ten} trong {duong} có giay = {rec['giay']!r}, không phải số. "
                f"Đo lại: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
        if not giay > 0 or giay != giay or giay == float("inf"):
            raise LoiThieuSo(
                f"Hằng số {ten} trong {duong} là {giay} — thời gian phải là số dương "
                f"hữu hạn. Đo lại: python3 scripts/tdq_bench.py thuc-do --ra {duong}")
        # Cửa này phải khoá ở CHỖ ĐỌC, không chỉ ở chỗ ghi: file có thể bị sửa tay sau
        # khi ghi, và mô phỏng đọc lại là tin ngay.
        so_mau = rec.get("so_mau")
        if not isinstance(so_mau, int) or so_mau < SO_MAU_TOI_THIEU:
            raise LoiThieuSo(
                f"Hằng số {ten} trong {duong} chỉ có so_mau = {so_mau!r}, cần ít nhất "
                f"{SO_MAU_TOI_THIEU}. Đo lại: python3 scripts/tdq_bench.py thuc-do "
                f"--ra {duong}")
        ra[ten] = giay
    return ra


# --------------------------------------------------------------- mô phỏng
class KetQua:
    """Kết quả mô phỏng một plan: đủ số để in bảng và để kiểm tay."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def mo_phong_tasks(tasks, hs, he_so_agent=1.0):
    """Áp công thức spec §3 cho danh sách Task đã đọc từ plan.

    `he_so_agent` là số lần agent con CHẬM hơn leader trên cùng một task. Mặc định 1.0
    là giả định của spec (hai bên nhanh bằng nhau). Đòn bẩy này mạnh ngang `t_phat`:
    agent chậm hơn 25% đã đẩy ngưỡng hoà từ 10% lên 30%. Không có tham số này thì người
    đọc bảng không cách nào tự trừ hao, nên nó phải là tham số hạng nhất.
    """
    if not tasks:
        raise LoiThieuSo("Plan không có task nào đọc được.")
    quyet = {t.ma: tdq_team.quyet_dinh_task(t, tasks) for t in tasks}
    dot_theo_task = tdq_team.chia_dot(tasks, quyet)
    giao = [t for t in tasks if quyet[t.ma][0] == "giao"]
    tu_lam = [t for t in tasks if quyet[t.ma][0] == "tu_lam"]
    dot = {}
    for t in giao:
        dot.setdefault(dot_theo_task[t.ma], []).append(t)

    if not he_so_agent > 0:
        raise LoiThieuSo("--he-so-agent phải là số dương (1.0 = agent nhanh ngang leader).")
    n = len(tasks)
    t_main = n * hs["t_task"] + n * hs["t_tick"]

    # Mỗi đợt trả một khoản phí cố định, đổi lại chỉ chờ task chậm nhất trong đợt.
    t_task_agent = hs["t_task"] * he_so_agent
    tong_max = sum(t_task_agent for _ in dot)          # task đồng nhất → max = t_task
    phi_dot = len(dot) * (hs["t_phat"] + hs["t_kiem"] + hs["t_hop"])
    # Task leader giữ lại thì leader tự làm, nên vẫn tính theo tốc độ leader.
    chen = max(0.0, len(tu_lam) * hs["t_task"] - tong_max)
    t_doi = phi_dot + tong_max + hs["t_don"] + chen
    # Biến thể kiểm thiên vị: công thức spec KHÔNG tính t_tick cho mode đội, trong khi
    # leader vẫn phải tick từng task ở cả hai mode. Tính thêm để thấy độ lệch đó.
    t_doi_kem_tick = t_doi + n * hs["t_tick"]
    return KetQua(
        so_task=n, so_giao=len(giao), so_tu_lam=len(tu_lam), so_dot=len(dot),
        t_main=t_main, t_doi=t_doi, t_doi_kem_tick=t_doi_kem_tick,
        chen=chen, phi_dot=phi_dot, tong_max=tong_max, he_so_agent=he_so_agent,
        thang="đội" if t_doi < t_main else ("main" if t_doi > t_main else "hoà"),
    )


def mo_phong_van_ban(van_ban, hs, he_so_agent=1.0):
    return mo_phong_tasks(_tasks_tu_van_ban(van_ban), hs, he_so_agent)


def _phut(giay):
    return f"{giay / 60:.1f}"


# --------------------------------------------------------- thực đo (repo tạm)
def _git(cwd, *args, check=True):
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True, errors="replace", timeout=GIT_TIMEOUT)
    if check and proc.returncode != 0:
        raise LoiThieuSo(f"git {' '.join(args)} lỗi: {proc.stderr.strip()}")
    return proc


def _team(repo, *args, wt=None):
    """Chạy tdq_team.py trên repo tạm. Trả (giây, returncode, stdout)."""
    env = dict(os.environ, TDQ_PROJECT_DIR=repo, TDQ_LOG="0")
    if wt:
        env["TDQ_WORKTREE_DIR"] = wt
    bat_dau = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, "tdq_team.py"), *args],
        capture_output=True, text=True, timeout=GIT_TIMEOUT, env=env)
    return time.perf_counter() - bat_dau, proc.returncode, proc.stdout + proc.stderr


def _dung_repo_tam(goc, slug, so_task):
    """Repo git tạm + plan mẫu + state — đủ để tdq_team.py chạy thật trên đó."""
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
    """Đóng vai agent con: sửa file trong worktree của nó rồi commit. Trả số giây.

    Stub chỉ đo phần CƠ HỌC (ghi file + commit). Nó là sàn dưới của `t_task`, không
    phải số thật — số thật lấy từ lượt chạy agent, nạp qua --mau-that.
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
    """Một lượt đo đầy đủ trong repo tạm. Trả dict tên hằng số → list mẫu."""
    mau = {ten: [] for ten in HANG_SO}
    goc = tempfile.mkdtemp(prefix="tdq-bench-")
    repo = None
    try:
        slug = "2026-01-01-0000-plan-mau-bench"
        repo, rel = _dung_repo_tam(goc, slug, so_task)
        wt = os.path.join(goc, "worktrees")
        # Tick đo trên BẢN SAO của plan: `tdq_team.py` khoá bản đồ theo sha của plan,
        # sửa plan giữa vòng đo sẽ làm chính vòng đo chết. Bản sao cùng nội dung nên
        # số I/O đo được vẫn là số của thao tác tick thật.
        plan_sao = os.path.join(goc, "plan-tick.md")
        shutil.copyfile(os.path.join(repo, rel), plan_sao)
        giay, rc, ra = _team(repo, "phan-cong", wt=wt)
        if rc != 0:
            raise LoiThieuSo(f"phan-cong lỗi trong repo tạm: {ra.strip()}")
        chuan_bi = giay
        giay, rc, ra = _team(repo, "kiem-ke", wt=wt)
        if rc != 0:
            raise LoiThieuSo(f"kiem-ke lỗi trong repo tạm: {ra.strip()}")
        chuan_bi += giay
        giay_cum, _rc, _ra = _team(repo, "cum", wt=wt)
        # t_phat của một đợt = chuẩn bị bản đồ + `cum` + `mo` cho từng task của đợt.
        phat = chuan_bi + giay_cum
        for i in range(1, so_task + 1):
            ma = f"T1.{i}"
            giay, rc, ra = _team(repo, "mo", ma, wt=wt)
            if rc != 0:
                raise LoiThieuSo(f"mo {ma} lỗi: {ra.strip()}")
            phat += giay
        mau["t_phat"].append(phat)
        for i in range(1, so_task + 1):
            ma = f"T1.{i}"
            worktree = os.path.join(wt, slug, ma.lower())
            mau["t_task"].append(_agent_stub(worktree, ma))
            giay, rc, ra = _team(repo, "kiem", ma, wt=wt)
            if rc != 0:
                raise LoiThieuSo(f"kiem {ma} báo xung đột ngoài dự kiến: {ra.strip()}")
            mau["t_kiem"].append(giay)
            giay, rc, ra = _team(repo, "hop", ma, wt=wt)
            if rc != 0:
                raise LoiThieuSo(f"hop {ma} lỗi: {ra.strip()}")
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
    """Đo đúng việc leader làm mỗi task: đọc plan, đổi dấu tick, ghi lại."""
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
            raise LoiThieuSo(f"--mau-that sai khuôn ở \"{phan}\" — dùng ten=giay.")
        ten, gia_tri = phan.split("=", 1)
        ten = ten.strip()
        if ten not in HANG_SO:
            raise LoiThieuSo(f"--mau-that: không có hằng số \"{ten}\". "
                             f"Chỉ nhận: {', '.join(HANG_SO)}")
        try:
            ra.setdefault(ten, []).append(float(gia_tri))
        except ValueError:
            raise LoiThieuSo(f"--mau-that: \"{gia_tri}\" không phải số giây.")
    return ra


# --------------------------------------------------------------- lệnh con
def lenh_dung_plan(args):
    van_ban, so_cap = sinh_plan(args.task, args.chong, args.phu_thuoc, args.ngay)
    tasks = _tasks_tu_van_ban(van_ban)
    that = dem_cap_chong(tasks)
    if that != so_cap:
        raise LoiThieuSo(f"Sinh sai: tính {so_cap} cặp chồng nhưng đọc lại được {that}.")
    _log(f"dung-plan → {args.task} task · {so_cap} cặp chồng file")
    if args.ra:
        try:
            with open(args.ra, "w", encoding="utf-8") as f:
                f.write(van_ban)
        except OSError as loi:
            raise LoiThieuSo(
                f"Không ghi được {args.ra}: {loi}. Tạo thư mục trước "
                f"(mkdir -p {os.path.dirname(args.ra) or '.'}), hoặc bỏ --ra: "
                f"python3 scripts/tdq_bench.py dung-plan --task {args.task}")
        print(f"Plan mẫu: {args.ra}")
        print(f"{len(tasks)} task · {so_cap} cặp task chồng file")
    else:
        sys.stdout.write(van_ban)
    return 0


def lenh_thuc_do(args):
    # --lap 0 + --mau-that = bịa trọn 6 hằng số mà file vẫn ghi nguon=that. Chặn ở đây,
    # và ghi cach_do cho từng hằng số để người đọc phân biệt số máy đo với số nhập tay.
    if args.lap < 1:
        raise LoiThieuSo(
            f"--lap = {args.lap} — phải ít nhất 1 lượt đo máy. "
            f"Chạy: python3 scripts/tdq_bench.py thuc-do --lap 3 --ra {args.ra}")
    mau = {ten: [] for ten in HANG_SO}
    nguon = {ten: "stub" for ten in HANG_SO}
    cach_do = {ten: "may" for ten in HANG_SO}
    for lan in range(args.lap):
        _log(f"thuc-do → lượt {lan + 1}/{args.lap} trong repo git tạm")
        for ten, gia_tri in _do_mot_luot(args.task).items():
            mau[ten].extend(gia_tri)
    that = _doc_mau_that(args.mau_that)
    mau_may = {ten: list(gia_tri) for ten, gia_tri in mau.items()}
    for ten, gia_tri in that.items():
        mau[ten] = gia_tri            # số thật thay hẳn số stub, không trộn
        nguon[ten] = "that"
        cach_do[ten] = "nhap-tay"
    thieu = [ten for ten in HANG_SO if len(mau[ten]) < SO_MAU_TOI_THIEU]
    if thieu and not args.cho_it_mau:
        raise LoiThieuSo(
            f"Chưa đủ {SO_MAU_TOI_THIEU} mẫu cho: {', '.join(thieu)}. "
            f"Tăng --lap hoặc --task, hoặc nạp số thật bằng --mau-that.")
    du_lieu = {
        "slug": args.slug,
        "ngay": args.ngay or date.today().isoformat(),
        "may": {"python": platform.python_version(), "he_dieu_hanh": platform.platform()},
        "ghi_chu": "nguon=stub là sàn dưới cơ học; nguon=that là số bấm giờ lượt agent "
                   "thật. cach_do=nhap-tay nghĩa là số do người nhập, mẫu máy giữ ở mau_may",
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
        raise LoiThieuSo(f"Không ghi được {args.ra}: {loi}. "
                         f"Tạo thư mục cha trước rồi chạy lại.")
    print(f"Thực đo: {args.ra}")
    for ten in HANG_SO:
        rec = du_lieu["hang_so"][ten]
        print(f"  {ten:8s} {rec['giay']:9.3f}s  ±{rec['do_tan']:.3f}  "
              f"n={rec['so_mau']}  nguồn={rec['nguon']}  cách đo={rec['cach_do']}")
    return 0


def lenh_mo_phong(args):
    hs = nap_hang_so(args.thuc_do)
    if args.plan:
        try:
            with open(args.plan, encoding="utf-8") as f:
                van_ban = f.read()
        except OSError as loi:
            raise LoiThieuSo(
                f"Không đọc được plan {args.plan}: {loi}. Kiểm lại đường dẫn, hoặc bỏ "
                f"--plan để dùng plan mẫu: python3 scripts/tdq_bench.py mo-phong "
                f"--thuc-do {args.thuc_do} --task 12")
    else:
        van_ban, _ = sinh_plan(args.task, args.chong, args.phu_thuoc)
    kq = mo_phong_van_ban(van_ban, hs, args.he_so_agent)
    _log(f"mo-phong → {kq.so_task} task · {kq.so_dot} đợt · thắng: {kq.thang}")
    print(f"Plan: {kq.so_task} task · giao {kq.so_giao} · leader giữ {kq.so_tu_lam} "
          f"· {kq.so_dot} đợt · hệ số agent {kq.he_so_agent}")
    print("| Chỉ số | main | đội |")
    print("|---|---|---|")
    print(f"| Thời gian mô hình (phút) | {_phut(kq.t_main)} | {_phut(kq.t_doi)} |")
    print(f"| Phí cố định mỗi đợt (phút) | 0.0 | {_phut(kq.phi_dot)} |")
    print(f"| Chờ task chậm nhất (phút) | — | {_phut(kq.tong_max)} |")
    print(f"| Leader làm chen (phút) | — | {_phut(kq.chen)} |")
    print(f"| Kèm cả t_tick (phút) | {_phut(kq.t_main)} | {_phut(kq.t_doi_kem_tick)} |")
    print(f"Thắng: {kq.thang} (chênh {_phut(abs(kq.t_main - kq.t_doi))} phút)")
    return 0


def lenh_quet(args):
    # --buoc 0 làm range() văng, --buoc âm cho bảng RỖNG rồi vẫn in dòng kết luận — bảng
    # rỗng mà có kết luận còn nguy hơn cả lỗi, nên chặn ngay ở đầu vào.
    if not 1 <= args.buoc <= 100:
        raise LoiThieuSo(
            f"--buoc = {args.buoc} — phải nằm trong 1–100. "
            f"Chạy: python3 scripts/tdq_bench.py quet --buoc 10 --thuc-do {args.thuc_do}")
    hs = nap_hang_so(args.thuc_do)
    print(f"Quét {args.task} task · tỉ lệ tách được 0→100% · bước {args.buoc}% "
          f"· hệ số agent {args.he_so_agent}")
    print("| Tách được | Đợt | T_main (phút) | T_đội (phút) | Thắng |")
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
        print(f"Không đổi chiều trong dải này: {truoc} thắng ở mọi tỉ lệ.")
        _log("quet → không có ngưỡng đổi chiều")
        return 0
    for phan_tram, cu, moi in nguong:
        print(f"NGƯỠNG: ở tỉ lệ tách được {phan_tram}% thì thắng-thua đổi chiều "
              f"{cu} → {moi}.")
    _log(f"quet → {len(nguong)} ngưỡng đổi chiều")
    return 0


LENH = {
    "dung-plan": (lenh_dung_plan, "sinh plan mẫu N task, đặt được tỉ lệ chồng file"),
    "thuc-do": (lenh_thuc_do, "chạy vòng đội thật trong repo tạm, ghi hằng số ra JSON"),
    "mo-phong": (lenh_mo_phong, "tính T_main và T_đội cho một plan"),
    "quet": (lenh_quet, "quét dải tỉ lệ tách được, tìm ngưỡng đổi chiều"),
}


def build_parser():
    p = argparse.ArgumentParser(
        prog="tdq_bench.py",
        description="Cân đo mode main với mode đội bằng số đo được.")
    sub = p.add_subparsers(dest="lenh")

    dp = sub.add_parser("dung-plan", help=LENH["dung-plan"][1])
    dp.add_argument("--task", type=int, default=12, help="số task của plan mẫu")
    dp.add_argument("--chong", type=float, default=0.0,
                    help="tỉ lệ task bị dồn vào cùng một file (0→1)")
    dp.add_argument("--phu-thuoc", type=int, default=0, dest="phu_thuoc",
                    help="số task nhắc mã task trước đó")
    dp.add_argument("--ngay", help="ngày ghi trong plan (mặc định hôm nay)")
    dp.add_argument("--ra", help="ghi ra file; không có thì in ra stdout")

    td = sub.add_parser("thuc-do", help=LENH["thuc-do"][1])
    td.add_argument("--ra", required=True, help="file JSON hằng số")
    td.add_argument("--task", type=int, default=3, help="số task mỗi lượt đo")
    td.add_argument("--lap", type=int, default=3, help="số lượt đo")
    td.add_argument("--slug", default="", help="slug request ghi vào file")
    td.add_argument("--ngay", help="ngày ghi vào file")
    td.add_argument("--mau-that", dest="mau_that",
                    help="mẫu đo từ lượt agent thật, khuôn \"t_task=91.2,t_task=104.7\"")
    td.add_argument("--cho-it-mau", action="store_true", dest="cho_it_mau",
                    help="cho phép ghi khi chưa đủ 3 mẫu (chỉ dùng khi gỡ lỗi)")

    mp = sub.add_parser("mo-phong", help=LENH["mo-phong"][1])
    mp.add_argument("--plan", help="file plan; không có thì sinh plan mẫu")
    mp.add_argument("--thuc-do", dest="thuc_do", help="file JSON hằng số")
    mp.add_argument("--task", type=int, default=12)
    mp.add_argument("--chong", type=float, default=0.0)
    mp.add_argument("--phu-thuoc", type=int, default=0, dest="phu_thuoc")
    mp.add_argument("--he-so-agent", type=float, default=1.0, dest="he_so_agent",
                    help="agent con chậm hơn leader bao nhiêu lần (1.0 = nhanh ngang)")

    qt = sub.add_parser("quet", help=LENH["quet"][1])
    qt.add_argument("--thuc-do", dest="thuc_do", help="file JSON hằng số")
    qt.add_argument("--task", type=int, default=12)
    qt.add_argument("--buoc", type=int, default=10, help="bước quét theo phần trăm")
    qt.add_argument("--he-so-agent", type=float, default=1.0, dest="he_so_agent",
                    help="agent con chậm hơn leader bao nhiêu lần (1.0 = nhanh ngang)")
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.lenh:
        parser.print_usage(sys.stderr)
        _loi("Thiếu lệnh con. Có: " + " · ".join(LENH))
        return 2
    _log(f"{args.lenh} · {' '.join(argv[1:]) or '(không tham số)'}")
    try:
        return LENH[args.lenh][0](args)
    except LoiThieuSo as exc:
        _loi(str(exc))
        return 1
    except subprocess.TimeoutExpired:
        _loi("git chạy quá lâu — bỏ dở, không đụng gì thêm.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
