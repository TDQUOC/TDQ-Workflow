#!/usr/bin/env python3
"""Điều phối mode đội: leader phân công CẢ plan, agent con chạy song song (chỉ stdlib).

Bảy lệnh con, dùng đúng theo thứ tự này:
  phan-cong  — đọc toàn bộ plan, ghi bản đồ docs/tdq/team/<slug>.json
  kiem-ke    — soi bản đồ: task nào leader giữ lại mà không đúng luật thì exit khác 0
  cum        — in đợt kế tiếp (task giao được, không đụng vùng đang khoá)
  mo <task>  — tạo nhánh + git worktree riêng cho một task
  kiem <task>— dò xung đột với nhánh tích hợp, KHÔNG đụng repo
  hop <task> — hợp nhánh của task vào nhánh tích hợp (chặn nếu `kiem` chưa pass)
  don        — gỡ mọi worktree của request, prune sạch .git/worktrees

Vì sao phải có công cụ này thay vì để model tự xoay: quyết định "task này giao hay
tự làm" phải KIỂM ĐƯỢC BẰNG MÁY. Model tự nhận xét thì không ai chứng minh được nó
có lách luật (user chọn subagent nhưng lại tự làm ở main) hay không.

Exit code: 0 = ổn · 1 = sai luật / xung đột / thiếu dữ kiện · 2 = dùng lệnh sai.
Env: TDQ_PROJECT_DIR neo project · TDQ_LOG=0 tắt log · TDQ_WORKTREE_DIR đổi chỗ worktree.
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

# --- luật đọc plan -----------------------------------------------------------
# Dòng task: `- [ ] **T1.1** (n3 e5m) việc — Test: ...`
_TASK = re.compile(r"^(\s*)-\s*\[( |~|x|>)\]\s*\*\*([A-Za-z]+[0-9.]*)\*\*\s*(.*)$")
_PHASE = re.compile(r"^##\s*(P\d+)\b")
# Đường dẫn khai trong backtick: phải có `/` và có đuôi — `true` hay `T1.1` không tính.
_PATH = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")
_TASK_REF = re.compile(r"\b(T\d+\.\d+)\b")
# Nhãn khai phụ thuộc trong plan: `- Cần: T1.1, T2.3`.
NHAN_CAN = "Cần:"
# Nhãn ước lượng thời gian trong plan: `(n3 e20m)` → 20 phút.
_UOC_LUONG = re.compile(r"\be(\d+)m\b")

# Tập ĐÓNG các lý do được phép giữ task lại cho leader. Ngoài tập này là lách luật.
LY_DO_GIU = {
    "phu-thuoc": "task phụ thuộc một task khác chưa xong",
    "vung-khoa": "không khai được vùng file riêng nên không thể tách",
    "mcp": "task cần MCP tool mà agent con không có",
    "file-luat": "sửa chính file luật/hook mà leader đang chạy theo",
    # Hợp đồng dùng chung (kiểu dữ liệu, hằng số, khuôn thông báo, sổ đăng ký) phải
    # dựng xong TRƯỚC rồi mới chia nhánh: mỗi agent con tự đoán một kiểu thì merge
    # xong mới lộ ra là ba bản không khớp nhau.
    "hop-dong": "task định nghĩa hợp đồng dùng chung mà nhiều task sau đọc",
}
# Tiền tố file luật/hook: agent con sửa những chỗ này thì leader đang đứng trên
# tấm ván nó cưa — phải để leader tự làm.
TIEN_TO_FILE_LUAT = ("skills/", "hooks/", "agents/", ".claude/", ".codex/",
                     "CLAUDE.md", "AGENTS.md")
# Tên nhánh/worktree cấm mở đầu (CLAUDE.md §2).
TEN_CAM = ("claude", "antigravity", "gemini", "codex")

# Trần số nhánh chạy cùng lúc. 4 vì số điểm lỗi phối hợp tăng theo n(n-1)/2:
# 4 agent là 6 điểm, 10 agent đã là 45 điểm (research vòng 1, mục 4). Đây là trần
# TRÊN — ít task sẵn sàng hơn thì phát ít hơn, cấm chờ cho đủ 4.
TRAN_SONG_SONG = 4

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
import tdq_state  # noqa: E402


# --------------------------------------------------------------- log service
def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: 1 dòng ISO-timestamp ra stderr. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}",
              file=sys.stderr)


def _loi(message):
    """Thông điệp lỗi luôn ra stderr, không phụ thuộc TDQ_LOG."""
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


# ------------------------------------------------------------- đọc plan
class Task:
    """Một task trong plan, kèm mọi thứ đọc được từ chính dòng chữ của nó."""

    def __init__(self, ma, trang_thai, phase):
        self.ma = ma
        self.trang_thai = trang_thai      # " " | "~" | "x" | ">"
        self.phase = phase
        self.text = []                    # dòng task + các dòng con
        self.vung_file = []
        self.can_mcp = False

    @property
    def xong(self):
        return self.trang_thai == "x"

    @property
    def da_giao(self):
        return self.trang_thai == ">"


def doc_plan(duong_dan):
    """Trả về danh sách Task theo đúng thứ tự xuất hiện trong plan."""
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
            # Dòng nối tiếp của mô tả: thụt lề nhưng không mở bullet mới. Nối vào
            # phần tử cuối chứ không tạo phần tử riêng — nhờ vậy chính dòng khai bị
            # ngắt (`- Chạm: …` xuống dòng) vẫn còn tiền tố để nhận ra.
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
            if dong.startswith("Dùng:") and dong.rstrip().endswith("(mcp)"):
                t.can_mcp = True
    return tasks


def doc_phu_thuoc(tasks):
    """Bản đồ mã task → tập mã task phải xong TRƯỚC, đọc từ dòng `- Cần: T1.1, T2.3`.

    Task không khai dòng này trả tập rỗng — nghĩa là "không tự nhận phụ thuộc ai".
    Mã tự trỏ chính nó và mã không có trong plan đều bỏ qua: plan viết ẩu thì lịch
    trình vẫn chạy được, sai sót để linter bắt chứ không làm sập lệnh chia đợt.
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
    """Số phút ước lượng đọc từ nhãn `(n3 e20m)`. Không khai thì tính 1 phút.

    Mặc định 1 chứ không phải 0: task không khai vẫn tốn thời gian, cho 0 sẽ
    làm cả nhánh chứa nó biến mất khỏi phép so đường găng.
    """
    for dong in task.text:
        m = _UOC_LUONG.search(dong)
        if m:
            return int(m.group(1))
    return 1


def b_level(tasks, phu_thuoc):
    """Mã task → tổng phút của đường DÀI NHẤT từ task đó tới hết đồ thị.

    Đây là `b-level` của lịch trình danh sách: task có b-level lớn nằm trên đường
    găng, phát trước thì cả đội về sớm; phát sau thì mọi nhánh khác phải chờ nó.
    """
    sau = {t.ma: [] for t in tasks}                 # mã task → các task chờ nó
    for t in tasks:
        for c in phu_thuoc.get(t.ma, ()):
            if c in sau:
                sau[c].append(t.ma)
    phut = {t.ma: _phut_uoc_luong(t) for t in tasks}
    nho = {}

    def tinh(ma, dang_di):
        if ma in nho:
            return nho[ma]
        if ma in dang_di:                           # vòng lặp: cắt, không treo máy
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
    """(quyet_dinh, ly_do) cho một task. Mặc định là GIAO — giữ lại phải có cớ."""
    if task.can_mcp:
        return "tu_lam", "mcp"
    if not task.vung_file:
        return "tu_lam", "vung-khoa"
    if any(_la_file_luat(d) for d in task.vung_file):
        return "tu_lam", "file-luat"
    if any(doc_phu_thuoc(tasks).values()):
        # Plan đã khai `Cần:` → phụ thuộc là ràng buộc LỊCH TRÌNH (`chia_dot` lo),
        # không phải cớ giữ task. Giữ lại ở đây thì thêm dòng `Cần:` sẽ giết song song.
        return "giao", ""
    chua_xong = {t.ma for t in tasks if not t.xong}
    for dong in task.text:
        for ref in _TASK_REF.findall(dong):
            if ref != task.ma and ref in chua_xong:
                return "tu_lam", "phu-thuoc"
    return "giao", ""


def chia_dot(tasks, quyet_dinh):
    """Gán số đợt cho từng task. Đợt 1 chạy trước, đợt 2 chạy sau, cùng đợt = song song.

    Có ít nhất một task khai `Cần:` → xếp theo ĐỒ THỊ PHỤ THUỘC: task nằm sau mọi
    task nó khai, ngoài ra được đẩy lên sớm nhất có thể kể cả vượt ranh giới phase.
    Không task nào khai → lùi về luật cũ theo tên phase, để plan viết trước luật này
    cho ra đúng số đợt như bản cũ.

    Luật chung cho cả hai đường: hai task chạm chung file không bao giờ cùng đợt.
    """
    phu_thuoc = doc_phu_thuoc(tasks)
    if not any(phu_thuoc.values()):
        _log("chia-dot → không task nào khai `Cần:`, lùi về luật cũ theo tên phase")
        return _chia_dot_theo_phase(tasks)
    khai = sum(1 for v in phu_thuoc.values() if v)
    _log(f"chia-dot → {khai}/{len(tasks)} task khai `Cần:`, xếp theo đồ thị phụ thuộc")
    return _chia_dot_theo_phu_thuoc(tasks, phu_thuoc)


def _dot_som_nhat(files, dot_toi_thieu, chiem_theo_dot):
    """Đợt sớm nhất từ `dot_toi_thieu` trở đi mà không đụng file của task khác."""
    dot = dot_toi_thieu
    while files & chiem_theo_dot.get(dot, set()):
        dot += 1
    chiem_theo_dot.setdefault(dot, set()).update(files)
    return dot


def _chia_dot_theo_phu_thuoc(tasks, phu_thuoc):
    """Xếp theo thứ tự tô-pô: mỗi task đứng sau đợt lớn nhất của các task nó cần."""
    con_lai = {t.ma: t for t in tasks}
    dot_theo_task = {}
    chiem_theo_dot = {}
    while con_lai:
        san_sang = [t for t in con_lai.values()
                    if all(c in dot_theo_task for c in phu_thuoc[t.ma])]
        cat_vong = not san_sang
        if cat_vong:
            # Vòng lặp trong khai báo `Cần:` — plan sai. Cắt vòng và xếp tiếp thay vì
            # văng: lệnh chia đợt không phải chỗ báo lỗi cú pháp plan, linter mới là.
            _log(f"chia-dot → cắt vòng `Cần:` ở {', '.join(sorted(con_lai))}")
            san_sang = list(con_lai.values())
        for t in san_sang:
            # `.get(...,  0)` vì ở nhánh cắt vòng, task nó cần có thể chưa được xếp.
            nen = max((dot_theo_task.get(c, 0) for c in phu_thuoc[t.ma]), default=0) + 1
            dot_theo_task[t.ma] = _dot_som_nhat(set(t.vung_file), nen, chiem_theo_dot)
            del con_lai[t.ma]
    return dot_theo_task


def _chia_dot_theo_phase(tasks):
    """Luật cũ: thứ tự phase LÀ thứ tự phụ thuộc, chia file trong từng phase."""
    dot_theo_task = {}
    nen = 0
    for phase in sorted({t.phase for t in tasks}, key=_khoa_phase):
        trong_phase = [t for t in tasks if t.phase == phase]
        thung = []                                  # thung[i] = set file đã chiếm
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


# ------------------------------------------------------------- bản đồ
def duong_ban_do(project, slug):
    return os.path.join(project, "docs", "tdq", "team", f"{slug}.json")


def sha_file(duong_dan):
    h = hashlib.sha256()
    with open(duong_dan, "rb") as f:
        for khoi in iter(lambda: f.read(65536), b""):
            h.update(khoi)
    return h.hexdigest()


def _boi_canh(project, can_ban_do=True):
    """(slug, plan_path, ban_do|None) hoặc ném LoiLuat."""
    state = tdq_state.load(project, heal=False) or {}
    slug = state.get("active_request")
    if not slug:
        raise LoiLuat("Chưa có request nào đang mở — không có gì để phân công.")
    rel = state.get("plan_file") or os.path.join("docs", "tdq", "plan", f"{slug}.md")
    plan = rel if os.path.isabs(rel) else os.path.join(project, rel)
    if not os.path.isfile(plan):
        raise LoiLuat(f"Không thấy plan: {plan}")
    ban_do = None
    duong = duong_ban_do(project, slug)
    if os.path.isfile(duong):
        try:
            with open(duong, encoding="utf-8") as f:
                ban_do = json.load(f)
        except (ValueError, UnicodeDecodeError) as loi:
            raise LoiLuat(f"Bản đồ phân công hỏng ({duong}): {loi}. "
                          f"Chạy lại: python3 scripts/tdq_team.py phan-cong")
    elif can_ban_do:
        raise LoiLuat("Chưa có bản đồ phân công. Chạy: "
                      "python3 scripts/tdq_team.py phan-cong")
    if ban_do is not None and can_ban_do and ban_do.get("plan_sha") != sha_file(plan):
        raise LoiLuat("Plan đã đổi sau khi phân công — bản đồ hết hiệu lực. "
                      "Chạy lại: python3 scripts/tdq_team.py phan-cong")
    return slug, plan, ban_do


class LoiLuat(Exception):
    """Sai luật hoặc thiếu dữ kiện — exit 1, kèm câu lệnh sửa."""


# ------------------------------------------------------------- lệnh con
def lenh_phan_cong(project, _args):
    slug, plan, _ = _boi_canh(project, can_ban_do=False)
    tasks = doc_plan(plan)
    if not tasks:
        raise LoiLuat(f"Plan không có task nào đọc được: {plan}")
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
    _log(f"phan-cong → {len(tasks)} task · giao {giao} · giữ {len(tasks) - giao} "
         f"· {max(dot.values())} đợt")
    print(f"Bản đồ: {os.path.relpath(duong, project)}")
    print(f"Giao agent con: {giao}/{len(tasks)} task · {max(dot.values())} đợt")
    for ma, rec in ban_do["tasks"].items():
        if rec["quyet_dinh"] == "tu_lam":
            print(f"  GIỮ {ma} — {rec['ly_do']}: {LY_DO_GIU[rec['ly_do']]}")
    return 0


def lenh_kiem_ke(project, _args):
    _slug, _plan, ban_do = _boi_canh(project)
    van_de = []
    for ma, rec in ban_do["tasks"].items():
        if rec.get("quyet_dinh") == "giao":
            # Task giao mà vùng file rỗng = lời hứa suông: hook [TDQ:TEAM] không có gì
            # để so, leader sửa file nào cũng lọt. Đây chính là đường lách luật rẻ nhất.
            if not rec.get("vung_file"):
                van_de.append(f"Giao: {ma} — ghi giao cho agent con mà vùng file RỖNG, "
                              f"hook không chặn được ai")
            thieu = [k for k in ("quyet_dinh", "ly_do", "vung_file", "dot")
                     if k not in rec]
            if thieu:
                van_de.append(f"Giao: {ma} — bản ghi thiếu trường {', '.join(thieu)}")
            continue
        thieu = [k for k in ("quyet_dinh", "ly_do", "vung_file", "dot") if k not in rec]
        if thieu:
            van_de.append(f"Giữ: {ma} — bản ghi thiếu trường {', '.join(thieu)}")
        if rec.get("quyet_dinh") != "tu_lam":
            van_de.append(f"Giữ: {ma} — quyết định \"{rec.get('quyet_dinh')}\" "
                          f"không hợp lệ (chỉ nhận giao / tu_lam)")
            continue
        ly_do = (rec.get("ly_do") or "").strip()
        if not ly_do:
            van_de.append(f"Giữ: {ma} — tự làm mà KHÔNG có lý do")
        elif ly_do not in LY_DO_GIU:
            van_de.append(f"Giữ: {ma} — lý do \"{ly_do}\" không thuộc "
                          f"{len(LY_DO_GIU)} nhóm ({', '.join(sorted(LY_DO_GIU))})")
    tong = len(ban_do["tasks"])
    giao = sum(1 for r in ban_do["tasks"].values() if r.get("quyet_dinh") == "giao")
    _log(f"kiem-ke → {giao}/{tong} giao · {len(van_de)} vấn đề")
    if van_de:
        for dong in van_de:
            _loi(dong)
        _loi("Sửa: python3 scripts/tdq_team.py phan-cong (hoặc sửa tay bản đồ cho "
             f"đúng {len(LY_DO_GIU)} nhóm lý do)")
        return 1
    print(f"Bản đồ sạch: {giao}/{tong} task giao cho agent con.")
    return 0


def _tien_quyet(tasks, phu_thuoc, dot_theo_task):
    """Mã task → tập mã task phải XONG trước khi phát nó.

    Plan có khai `Cần:` thì lấy đúng lời khai. Plan cũ không khai gì thì suy ra từ
    số đợt — giữ nguyên hành vi "đợt trước xong mới tới đợt sau" của bản trước.
    """
    if any(phu_thuoc.values()):
        return {ma: set(phu_thuoc[ma]) for ma in tasks}
    return {ma: {khac for khac in tasks
                 if dot_theo_task.get(khac, 0) < dot_theo_task.get(ma, 0)}
            for ma in tasks}


def _ly_do_hoan(ma, tien_quyet, tasks, khoa, vung_file):
    """Lý do CỤ THỂ khiến task chưa phát được, hoặc None nếu phát được."""
    thieu = sorted(c for c in tien_quyet[ma]
                   if c in tasks and not tasks[c].xong)
    if thieu:
        return "chờ task chưa xong: " + ", ".join(thieu)
    dung = [d for d in vung_file if d in khoa]
    if dung:
        return "đụng vùng đang khoá: " + ", ".join(sorted(dung))
    return None


def lenh_cum(project, _args):
    _slug, plan, ban_do = _boi_canh(project)
    danh_sach = doc_plan(plan)
    tasks = {t.ma: t for t in danh_sach}
    phu_thuoc = doc_phu_thuoc(danh_sach)
    diem_gang = b_level(danh_sach, phu_thuoc)
    dot_theo_task = {ma: rec.get("dot", 0) for ma, rec in ban_do["tasks"].items()}
    tien_quyet = _tien_quyet(tasks, phu_thuoc, dot_theo_task)

    khoa = {}                               # file → task đang giữ
    dang_bay = [ma for ma, t in tasks.items() if t.da_giao]
    for ma in dang_bay:
        for duong in tasks[ma].vung_file:
            khoa[duong] = ma
    con_lai = [ma for ma, rec in ban_do["tasks"].items()
               if rec["quyet_dinh"] == "giao"
               and ma in tasks and not tasks[ma].xong and not tasks[ma].da_giao]
    if not con_lai:
        _log("cum → HẾT task giao được")
        print("HẾT: không còn task nào để giao cho agent con.")
        return 0
    if khoa:
        print("Vùng đang khoá: " + ", ".join(
            f"{duong} ({ma})" for duong, ma in sorted(khoa.items())))

    # Đường găng trước: task kéo dài tổng thời gian nhất được chỗ trước tiên.
    con_lai.sort(key=lambda ma: (-diem_gang.get(ma, 0), ma))
    phat, hoan, cho_slot = [], [], []
    da_dat = dict(khoa)                     # kèm cả file vừa nhận trong lượt này
    for ma in con_lai:
        vung = ban_do["tasks"][ma]["vung_file"]
        ly_do = _ly_do_hoan(ma, tien_quyet, tasks, da_dat, vung)
        if ly_do:
            hoan.append((ma, ly_do))
            continue
        # Trần đếm cả task `[>]` đang bay: phát liên tục mà chỉ đếm trong lượt thì
        # mỗi lượt lại mở thêm 4 nhánh nữa, trần thành vô nghĩa.
        if len(dang_bay) + len(phat) >= TRAN_SONG_SONG:
            _log(f"cum → {ma} sẵn sàng nhưng chạm trần {TRAN_SONG_SONG} nhánh "
                 f"({len(dang_bay)} đang bay), chờ slot")
            cho_slot.append(ma)
            continue
        phat.append(ma)
        for duong in vung:
            da_dat[duong] = ma

    print(f"Sẵn sàng: {len(phat)} task")
    for ma in phat:
        print(f"  {ma}  {' '.join(ban_do['tasks'][ma]['vung_file'])}")
    # Nói rõ vì sao từng task chưa phát: leader phải phân biệt "bản đồ sót task"
    # với "task còn vướng đúng luật".
    for ma, ly_do in hoan:
        print(f"  HOÃN {ma} — {ly_do}")
    if cho_slot:
        print(f"  CHỜ SLOT {len(cho_slot)} task (trần {TRAN_SONG_SONG} nhánh cùng lúc, "
              f"đang bay {len(dang_bay)}): " + ", ".join(sorted(cho_slot)))
    _log(f"cum → phát {len(phat)} · hoãn {len(hoan)} · chờ slot {len(cho_slot)}")
    return 0


# ------------------------------------------------------------- git
def _git(cwd, *args, check=True):
    # errors="replace": `git merge-tree` in cả nội dung object ra stdout, trong đó có
    # thể có byte không phải UTF-8 (file nhị phân, hoặc chuỗi bị cắt giữa ký tự). Để
    # mặc định thì cả lệnh `kiem` chết bằng UnicodeDecodeError — lỗi này chỉ lộ ra khi
    # chạy thật, không lộ ra ở test dùng file thuần ASCII.
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True, errors="replace", timeout=GIT_TIMEOUT)
    if check and proc.returncode != 0:
        raise LoiLuat(f"git {' '.join(args)} lỗi ({proc.returncode}): "
                      f"{proc.stderr.strip() or proc.stdout.strip()}")
    return proc


def _la_repo(project):
    proc = subprocess.run(["git", "-C", project, "rev-parse", "--git-dir"],
                          capture_output=True, text=True, timeout=GIT_TIMEOUT)
    return proc.returncode == 0


def _ten_nhanh(slug, ma_task):
    """`tdq/<slug>/<task>` — không bao giờ mở đầu bằng tên bị cấm ở CLAUDE.md §2."""
    ten = f"tdq/{slug}/{ma_task.lower()}"
    assert not ten.startswith(TEN_CAM)
    return ten


def _nhanh_tich_hop(slug):
    return f"tdq/{slug}/tich-hop"


def _thu_muc_goc_worktree(project):
    goc = os.environ.get("TDQ_WORKTREE_DIR") or os.path.join(project, ".tdq-worktrees")
    os.makedirs(goc, exist_ok=True)
    # Thư mục tự giấu mình khỏi `git status` — không phải sửa .gitignore của user.
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
    """Nhánh + worktree tích hợp. Merge diễn ra ở ĐÂY, không ở chỗ user đang đứng."""
    nhanh = _nhanh_tich_hop(slug)
    duong = _duong_worktree(project, slug, "tich-hop")
    if not _co_nhanh(project, nhanh):
        _git(project, "branch", nhanh, "HEAD")
        _log(f"tạo nhánh tích hợp {nhanh}")
    if not os.path.isdir(duong):
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        _git(project, "worktree", "add", duong, nhanh)
        _log(f"worktree tích hợp → {duong}")
    return nhanh, duong


def lenh_mo(project, args):
    slug, plan, ban_do = _boi_canh(project)
    ma = args.task
    if ma not in ban_do["tasks"]:
        raise LoiLuat(f"Bản đồ không có task {ma}.")
    rec = ban_do["tasks"][ma]
    if rec["quyet_dinh"] != "giao":
        raise LoiLuat(f"{ma} được đánh dấu tu_lam ({rec['ly_do']}) — không mở nhánh. "
                      f"Leader tự làm task này.")
    if not _la_repo(project):
        raise LoiLuat("Thư mục này không phải repo git — không mở worktree được.")
    tich_hop, _ = _bao_dam_tich_hop(project, slug)
    nhanh = _ten_nhanh(slug, ma)
    duong = _duong_worktree(project, slug, ma.lower())
    if os.path.isdir(duong):
        raise LoiLuat(f"{ma} đã có worktree: {duong}")
    if not _co_nhanh(project, nhanh):
        _git(project, "branch", nhanh, tich_hop)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    _git(project, "worktree", "add", duong, nhanh)
    _log(f"mo {ma} → nhánh {nhanh} · worktree {duong}")
    print(f"{ma}: nhánh {nhanh}")
    print(f"  worktree: {duong}")
    print(f"  vùng file: {' '.join(rec['vung_file']) or '(không khai)'}")
    print(f"  base: {tich_hop}")
    return 0


def _nhanh_cua(project, slug, ban_do, ten):
    """Nhận mã task hoặc tên nhánh đầy đủ, trả tên nhánh."""
    if ten in ban_do["tasks"]:
        return _ten_nhanh(slug, ten)
    return ten


def _do_xung_dot(project, tich_hop, nhanh):
    """`git merge-tree` ba chiều: KHÔNG đụng index, không đụng working tree."""
    base = _git(project, "merge-base", tich_hop, nhanh).stdout.strip()
    proc = _git(project, "merge-tree", base, tich_hop, nhanh, check=False)
    ra = proc.stdout
    xung_dot = proc.returncode != 0 or "<<<<<<<" in ra or "CONFLICT" in ra
    return xung_dot, _file_xung_dot(ra) if xung_dot else []


# `git merge-tree <base> <A> <B>` in theo khối "changed in both", đường dẫn nằm ở dòng
# `  our  100644 <sha> <path>` — KHÔNG phải khuôn diff `+++ b/<path>`. Chỉ lấy khối nào
# thật sự có dấu xung đột, để không kể tên file merge sạch.
_KHOI_CA_HAI = re.compile(r"^(?:changed in both|added in both)$", re.M)
_DUONG_DAN = re.compile(r"^\s+(?:base|our|their)\s+\d+\s+[0-9a-f]+\s+(.+)$", re.M)


def _file_xung_dot(ra):
    ten = set()
    for phan in _KHOI_CA_HAI.split(ra)[1:]:
        if "<<<<<<<" in phan or "CONFLICT" in phan:
            ten.update(m.strip() for m in _DUONG_DAN.findall(phan))
    if not ten:                                  # khuôn khác (CONFLICT (content): a/b)
        ten.update(m.strip() for m in re.findall(r"^CONFLICT \(.+?\): (.+)$", ra, re.M))
    return sorted(ten)


def lenh_kiem(project, args):
    slug, _plan, ban_do = _boi_canh(project)
    if not _la_repo(project):
        raise LoiLuat("Thư mục này không phải repo git.")
    tich_hop = _nhanh_tich_hop(slug)
    nhanh = _nhanh_cua(project, slug, ban_do, args.task)
    if not _co_nhanh(project, nhanh):
        raise LoiLuat(f"Không có nhánh {nhanh}. Mở trước: "
                      f"python3 scripts/tdq_team.py mo {args.task}")
    xung_dot, file_dung = _do_xung_dot(project, tich_hop, nhanh)
    _log(f"kiem {nhanh} → {'XUNG ĐỘT' if xung_dot else 'sạch'}")
    if xung_dot:
        print(f"XUNG ĐỘT: {nhanh} không merge sạch vào {tich_hop}")
        for duong in file_dung:
            print(f"  {duong}")
        print("Cách gỡ: giải xung đột trong worktree của task rồi chạy lại `kiem`.")
        return 1
    print(f"Sạch: {nhanh} merge được vào {tich_hop}.")
    return 0


def lenh_hop(project, args):
    slug, _plan, ban_do = _boi_canh(project)
    if not _la_repo(project):
        raise LoiLuat("Thư mục này không phải repo git.")
    tich_hop, duong_tich_hop = _bao_dam_tich_hop(project, slug)
    nhanh = _nhanh_cua(project, slug, ban_do, args.task)
    if not _co_nhanh(project, nhanh):
        raise LoiLuat(f"Không có nhánh {nhanh}.")
    xung_dot, file_dung = _do_xung_dot(project, tich_hop, nhanh)
    if xung_dot:
        _log(f"hop {nhanh} → CHẶN vì xung đột")
        _loi(f"CHẶN: {nhanh} xung đột với {tich_hop} ở "
             f"{', '.join(file_dung) or '(không rõ file)'}.")
        _loi(f"Chạy `python3 scripts/tdq_team.py kiem {args.task}` để xem chi tiết, "
             f"giải xong mới hợp.")
        return 1
    # rerere: xung đột lặp lại giữa các đợt được nhớ cách giải (research §2).
    _git(project, "config", "rerere.enabled", "true")
    _git(duong_tich_hop, "merge", "--no-ff", "-m",
         f"hợp {nhanh} vào {tich_hop}", nhanh)
    _log(f"hop {nhanh} → vào {tich_hop}")
    print(f"Đã hợp {nhanh} vào {tich_hop}.")
    print(f"Nhánh tích hợp ở: {duong_tich_hop}")
    return 0


def lenh_don(project, _args):
    slug, _plan, _ban_do = _boi_canh(project, can_ban_do=False)
    if not _la_repo(project):
        raise LoiLuat("Thư mục này không phải repo git.")
    goc = os.path.join(_thu_muc_goc_worktree(project), slug)
    ra = _git(project, "worktree", "list", "--porcelain").stdout
    duong_list = [d.split(" ", 1)[1] for d in ra.splitlines() if d.startswith("worktree ")]
    da_go = 0
    # realpath cả hai vế: trên macOS `/var` là symlink của `/private/var`, so
    # bằng abspath sẽ trượt và `don` im lặng không gỡ gì.
    goc_that = os.path.realpath(goc)
    for duong in duong_list:
        if os.path.realpath(duong).startswith(goc_that):
            # `git worktree remove`, KHÔNG `rm -rf`: xoá tay để lại rác trong
            # .git/worktrees và git vẫn tưởng worktree còn sống (research §2).
            _git(project, "worktree", "remove", "--force", duong)
            da_go += 1
    _git(project, "worktree", "prune")
    _log(f"don → gỡ {da_go} worktree")
    print(f"Đã gỡ {da_go} worktree của {slug}, đã prune.")
    return 0


# ------------------------------------------------- chống lách luật (hook dùng)
def canh_bao_lach_luat(cwd, rel_target):
    """User chọn mode đội mà leader lại tự gõ code của task đã hứa giao → cảnh báo.

    Trả None khi không có gì để nói. Trả dict {kieu, ma, nhanh} khi phát hiện.
    Hàm này là chỗ DUY NHẤT quyết định "có lách luật không" — hook chỉ in ra.
    Chỉ soi khi: phase implement + mode subagent + file nằm trong vùng của một
    task đã ghi `giao` mà chưa có nhánh riêng.
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
            # Bản đồ đọc không nổi = không ai chứng minh được task này giao hay tự làm.
            # Fail-open ở đây là mở toang đúng cửa mà bản đồ sinh ra để canh.
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
                return None                      # chính leader được giữ task này
            t = tasks.get(ma)
            if t is not None and t.xong:
                return None                      # đã merge xong, sửa thêm là việc của leader
            nhanh = _ten_nhanh(slug, ma)
            if _la_repo(cwd) and _co_nhanh(cwd, nhanh):
                return None                      # agent con đã có chỗ làm việc riêng
            return {"kieu": "da-giao-thieu-nhanh" if (t and t.da_giao) else "chua-mo-nhanh",
                    "ma": ma, "nhanh": nhanh}
        return None
    except Exception:
        # Hook không bao giờ được chết vì hàm này — im lặng thì tệ hơn chặn nhầm.
        return None


# ------------------------------------------------------------------ CLI
LENH = {
    "phan-cong": (lenh_phan_cong, "đọc toàn bộ plan, ghi bản đồ phân công"),
    "kiem-ke": (lenh_kiem_ke, "soi bản đồ: giữ task lại phải đúng 1 nhóm lý do đóng"),
    "cum": (lenh_cum, "in đợt kế tiếp, trừ vùng file đang khoá"),
    "mo": (lenh_mo, "tạo nhánh + worktree cho một task"),
    "kiem": (lenh_kiem, "dò xung đột với nhánh tích hợp, không đụng repo"),
    "hop": (lenh_hop, "hợp nhánh của task vào nhánh tích hợp"),
    "don": (lenh_don, "gỡ worktree của request và prune"),
}


def build_parser():
    p = argparse.ArgumentParser(
        prog="tdq_team.py",
        description="Điều phối mode đội: leader phân công, agent con chạy song song.")
    sub = p.add_subparsers(dest="lenh")
    for ten, (_ham, mo_ta) in LENH.items():
        con = sub.add_parser(ten, help=mo_ta)
        if ten in ("mo", "kiem", "hop"):
            con.add_argument("task", help="mã task (T1.1) hoặc tên nhánh đầy đủ")
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.lenh:
        parser.print_usage(sys.stderr)
        _loi("Thiếu lệnh con. Có: " + " · ".join(LENH))
        return 2
    project = _project_dir()
    _log(f"{args.lenh} · project={project}")
    try:
        return LENH[args.lenh][0](project, args)
    except LoiLuat as exc:
        _loi(str(exc))
        return 1
    except subprocess.TimeoutExpired:
        _loi("git chạy quá lâu — bỏ dở, không đụng gì thêm.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
