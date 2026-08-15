#!/usr/bin/env python3
"""State helper cho plugin TDQ workflow (chỉ dùng stdlib).

State máy đọc: <project>/docs/tdq/state.json — MỌI thay đổi phải đi qua module
này. Bản mirror người/model đọc: <project>/docs/tdq/STATE.md, tự sinh lại sau
mỗi lần ghi (không sửa tay).

Nguyên tắc 0.3.0:
- Không bao giờ exit != 0 vì lý do TRẠNG THÁI (state hỏng, enum sai, thiếu
  request...). Chỉ sai CÚ PHÁP LỆNH mới exit 2. State không được phép trở thành
  ngõ cụt.
- `next` là nguồn duy nhất trả lời "đang ở đâu, làm gì tiếp" — hook gọi lại
  chính hàm này thay vì chép lại chữ ở nơi thứ hai.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

STATE_REL = os.path.join("docs", "tdq", "state.json")
STATE_MD_REL = os.path.join("docs", "tdq", "STATE.md")
TURN_LOG_REL = os.path.join("docs", "tdq", ".tdq-turn.jsonl")

APPROVE_TARGETS = ("spec", "plan", "quick")
VALID_MODES = ("main", "subagent")
BY_MAX = 200
VALID_LANES = {"quick", "full", None}

# Nhãn NGƯỜI ĐỌC. Định danh máy đọc vẫn là "quick"/"full" — tách hai lớp để đổi chữ
# cho dễ hiểu mà không phải migrate state đang tồn tại hay sửa test khoá cứng.
LANE_LABELS = {
    "quick": "chế độ nhanh (express)",
    "full": "chế độ chuyên sâu (deep)",
}

# Bí danh NGƯỜI GÕ -> định danh máy. Từ cũ (quick/full) giữ nguyên hiệu lực nên
# người dùng cũ không gãy tay. Khoá viết thường, đã bỏ dấu-space ở normalize_lane.
LANE_ALIASES = {
    "quick": "quick", "nhanh": "quick", "express": "quick",
    "full": "full", "deep": "full",
    "chuyen-sau": "full", "chuyensau": "full", "chuyên sâu": "full",
    "chuyen sau": "full", "chuyên-sâu": "full",
}
# Mode cũng tách hai lớp y như lane: định danh máy vẫn là "main"/"subagent" nên state
# cũ, plan cũ (dòng `Mode thực thi:`) và test khoá cứng đều không phải migrate.
MODE_LABELS = {
    "main": "làm trực tiếp (inline implement)",
    "subagent": "giao trợ lý (sub-agent implement)",
}

# Bí danh NGƯỜI GÕ -> định danh máy. Tên cũ giữ nguyên hiệu lực; tên mới nhận cả dạng
# có gạch nối, có space và có đuôi "implement" vì đó là chữ user đọc thấy ở cổng mode.
MODE_ALIASES = {
    "main": "main", "inline": "main",
    "inline implement": "main", "inline-implement": "main",
    "subagent": "subagent", "sub-agent": "subagent", "sub agent": "subagent",
    "sub-agent implement": "subagent", "sub agent implement": "subagent",
    "subagent implement": "subagent", "sub-agent-implement": "subagent",
}
VALID_PHASES = {"idle", "analyze", "spec", "plan", "mode", "implement", "qc", "report"}

USAGE = ("Cách dùng: tdq_state.py next [--brief] | get [key] | "
         "init <slug> [nhanh|express|quick — chế độ nhanh | chuyen-sau|deep|full — "
         "chế độ chuyên sâu] | "
         "set k=v ... | approve <spec|plan|quick (bí danh: nhanh|express)> "
         "[--mode main|subagent] "
         "[--no-qc (chỉ quick, phải kèm --by)] [--by \"<câu user>\"] | "
         "reset | phases-doc")

EXIT_SYNTAX = 2


# ------------------------------------------------------------------ slug
#
# Hai định dạng cùng sống: slug CŨ chỉ có ngày (269 file tài liệu đã đặt tên theo
# nó, user chốt giữ nguyên), slug MỚI có thêm giờ phút. Đọc thì nhận cả hai, ghi
# mới thì bắt buộc có giờ phút — chỗ chặn nằm ở nhánh `init` của `cli()`.
SLUG_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")
SLUG_FORMULA = "YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>"


def parse_slug(slug):
    """Tách slug thành (ngày, giờ-phút hoặc None, phần chữ). Không khớp → None.

    Bốn chữ số ở đầu phần chữ chỉ được coi là giờ phút khi nó là giờ CÓ THẬT
    (00:00–23:59); `2026-08-15-9999-viec` vẫn là slug cũ với phần chữ `9999-viec`.
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


def default_state():
    return {
        "schema_version": 4,
        "active_request": None,
        # slug của request bị thay thế ở lần init gần nhất (chỉ để truy vết/log)
        "previous_request": None,
        "lane": None,
        "phase": "idle",
        "spec_file": None,
        "spec_approved": False,
        "spec_sha256": None,
        "spec_approved_at": None,
        # câu duyệt nguyên văn của user (cắt 200 ký tự) — dấu vết duy nhất còn
        # lại sau khi bỏ hard gate, phải đối chiếu được với transcript
        "spec_approved_by": None,
        "plan_file": None,
        "plan_approved": False,
        "plan_sha256": None,
        "plan_approved_at": None,
        "plan_approved_by": None,
        "quick_approved": False,
        "quick_approved_at": None,
        "quick_approved_by": None,
        # Lane quick: QC bám DoD, mặc định BẬT; True = user opt-out có chủ đích qua
        # `approve quick --no-qc`. Người bỏ lấy từ quick_approved_by (cùng câu duyệt).
        "quick_qc_skipped": False,
        "implement_mode": None,
        # mốc mở request (schema 4) — gốc của mọi phép đếm thời gian treo tường
        "started_at": None,
        # lịch sử phase: [{"phase": "spec", "at": "<iso>"}, ...], mỗi lần ĐỔI phase
        # một mốc. Quay lại phase cũ vẫn đẻ mốc mới — đó là cơ sở đếm số lần vào.
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
    """Cảnh báo ra stderr kèm timestamp (spec §4.1). Tắt bằng TDQ_LOG=0.

    Không bao giờ log nội dung file hay giá trị nhạy cảm — chỉ đường dẫn và
    tên trường.
    """
    if log_enabled():
        print(f"[{now_iso()}] ⚠️ {msg}", file=sys.stderr)


def _info(msg):
    if log_enabled():
        print(f"[{now_iso()}] ℹ️ {msg}", file=sys.stderr)


def _fail(msg):
    """Chỉ dùng cho SAI CÚ PHÁP LỆNH — exit 2 (spec §2.9.4)."""
    print(msg, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    sys.exit(EXIT_SYNTAX)


# ------------------------------------------------------------- project root

def resolve_project_dir(cwd=None, env=_MISSING):
    """Project root cho state: TDQ_PROJECT_DIR > git root > thư mục đã có state > cwd.

    Chạy CLI từ một thư mục con mà không resolve sẽ tạo 'state bóng' ngay tại
    đó; hook (cwd = repo root) ghi một nơi, model đọc một nơi khác.
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
    # git root thắng: một state lỡ tạo ở thư mục con không được phép chiếm quyền
    return git_root or state_dir or start


def find_shadow_states(root):
    """State/mirror lạc chỗ: state.json ngoài root, hoặc STATE.md mồ côi (S6)."""
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
                found.append(os.path.relpath(path, root) + " (mirror mồ côi, thiếu state.json)")
    return sorted(found)


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ------------------------------------------------------------------ load/save

def load(cwd, heal=True):
    """Đọc state. Trả None khi chưa có file.

    File hỏng (S2): đổi tên thành state.json.corrupt-<ts>, cảnh báo, trả None —
    lệnh tiếp theo dựng lại state sạch. KHÔNG xoá dữ liệu cũ.
    Khoá lạ được giữ nguyên (S3); khoá thiếu được bù từ default_state().
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
            raise ValueError("state không phải object")
    except ValueError:
        if heal:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            broken = f"{path}.corrupt-{stamp}"
            try:
                os.replace(path, broken)
                _warn(f"state.json hỏng → đã giữ lại tại {os.path.basename(broken)}; "
                      "state được dựng lại từ mặc định.")
            except OSError:
                _warn("state.json hỏng và không đổi tên được — dùng state mặc định.")
        return None
    state = default_state()
    state.update(data)              # giữ nguyên cả khoá lạ (S3)
    for key, value in default_state().items():
        state.setdefault(key, value)
    state["schema_version"] = default_state()["schema_version"]
    # State bản cũ có thể mang phase_history sai kiểu (hoặc mốc rác). Chữa tại đây
    # để không script nào dưới xuôi phải tự phòng thủ.
    state["phase_history"] = [m for m in state["phase_history"]
                              if isinstance(m, dict) and m.get("phase") and m.get("at")] \
        if isinstance(state.get("phase_history"), list) else []
    return state


def _dong_so_request_cu(cwd):
    """Đóng sổ thời gian của request đang mở vào docs/tdq/timing.jsonl.

    Import MUỘN có chủ ý: `tdq_timing` import ngược lại module này, để ở đầu file
    thì thành vòng tròn. Hàm chỉ chạy trong `cli()` nên lúc đó module đã nạp xong.
    Đóng sổ hỏng không được phép chặn `init` — cùng lắm mất một dòng thống kê.
    """
    cu = os.environ.get("TDQ_LOG")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import tdq_timing
        state = load(cwd, heal=False)
        if not state or not state.get("active_request"):
            return False
        # Tắt log của tầng timing ở đúng lời gọi này: `init` sạch stderr là hợp
        # đồng có test canh (init đè request đã xong phải im lặng). Muốn xem chi
        # tiết thì gọi thẳng `tdq_timing.py close`.
        os.environ["TDQ_LOG"] = "0"
        so_lieu = tdq_timing.tong_hop(state, datetime.now().astimezone(),
                                      tdq_timing.default_transcript_dir(cwd))
        return bool(so_lieu) and tdq_timing.dong_so(cwd, so_lieu)
    except Exception as exc:                     # noqa: BLE001 — không chặn init
        _warn(f"không đóng sổ được thời gian request cũ: {exc.__class__.__name__}")
        return False
    finally:
        if cu is None:
            os.environ.pop("TDQ_LOG", None)
        else:
            os.environ["TDQ_LOG"] = cu


def ghi_moc_phase(state, phase, at=None):
    """Append một mốc vào `phase_history` khi phase THỰC SỰ đổi. Trả True nếu có ghi.

    Set lại đúng phase đang đứng thì bỏ qua: mốc 0 giây chỉ làm bẩn bảng thời gian.
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
    """Ghi nguyên tử state.json + sinh lại STATE.md (S1, mirror).

    expect_updated_at: giá trị `updated_at` lúc đọc. Nếu trên đĩa đã khác →
    có session khác vừa ghi: cảnh báo nhưng VẪN ghi (S7, không khoá đa phiên).
    """
    if expect_updated_at is not _MISSING:
        on_disk = load(cwd, heal=False)
        if on_disk and on_disk.get("updated_at") != expect_updated_at:
            _warn(f"state đã bị ghi bởi tiến trình khác lúc {on_disk.get('updated_at')} — "
                  "vẫn ghi đè, kiểm tra lại nếu đang chạy 2 session.")
    state["updated_at"] = now_iso()
    _atomic_write(state_path(cwd), json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    try:
        _atomic_write(state_md_path(cwd), render_state_md(cwd, state))
    except OSError as exc:                       # mirror hỏng không được chặn việc
        _warn(f"không ghi được {STATE_MD_REL}: {exc.__class__.__name__}")
    return state


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------- ảnh chụp hiệu ứng đầu turn (0.3.1)
#
# Sổ turn chỉ thấy được hành động đi qua tool Edit/Write; mọi thay đổi qua shell
# đều vô hình. Hai helper dưới đây cho hook nhìn thẳng vào ĐĨA, nên không phụ
# thuộc cú pháp lệnh bash (heredoc, pipe, biến... đều không đoán nổi bằng regex).

GIT_STATUS_TIMEOUT = 2
UNTRACKED_STAT_CAP = 200            # số FILE untracked được lấy dấu (không phải số dòng status)
UNTRACKED_HASH_MAX_BYTES = 262144   # ≤256 KB thì băm nội dung; lớn hơn mới đành dùng size:mtime
UNTRACKED_HASH_BUDGET = 4194304     # tổng số byte được đọc mỗi lần lấy vân tay

# Thư mục "sổ sách" của workflow: state.json / STATE.md / sổ turn đổi gần như mỗi
# turn — chính hook append sổ turn NGAY SAU khi chụp baseline. Tính chúng vào vân
# tay thì turn read-only cũng bị coi là "đổi repo" (chặn oan 0.3.1).
# Luôn viết bằng `/`: git in path bằng `/` trên mọi HĐH, dùng os.sep là tự tắt
# bộ lọc khi chạy trên Windows.
# `graphify-out` cùng loại: `tdq_finish.py` build lại đồ thị mỗi turn nên thư mục này
# gần như luôn đổi, và đó là hiệu ứng của chính workflow, không phải của việc user giao.
BOOKKEEPING_PATHS = ("docs/tdq", "docs/workinglog", "graphify-out")
_EXCLUDE = tuple(f":(top,exclude){p}" for p in BOOKKEEPING_PATHS)
_ROOT_CACHE = {}


def today_log_rel():
    return os.path.join("docs", "workinglog", datetime.now().strftime("%Y-%m-%d") + ".md")


def _git(cwd, *args):
    """stdout (bytes) của lệnh git, hoặc None khi không chạy được."""
    try:
        proc = subprocess.run(["git", "-C", cwd, *args],
                              capture_output=True, timeout=GIT_STATUS_TIMEOUT)
    except subprocess.TimeoutExpired:
        _warn(f"git {args[0]} quá {GIT_STATUS_TIMEOUT}s tại {cwd} — bỏ qua bằng chứng đĩa")
        return None
    except (OSError, subprocess.SubprocessError) as exc:
        _warn(f"không chạy được git {args[0]} ({type(exc).__name__}) — bỏ qua bằng chứng đĩa")
        return None
    # rc≠0 = "không phải git repo" / chưa có HEAD: chuyện bình thường, không log.
    return proc.stdout if proc.returncode == 0 else None


def repo_root(cwd):
    """Gốc repo (porcelain in path theo gốc, không theo cwd). None nếu không phải repo."""
    if cwd not in _ROOT_CACHE:
        out = _git(cwd, "rev-parse", "--show-toplevel")
        _ROOT_CACHE[cwd] = out.decode("utf-8", "replace").strip() if out else None
    return _ROOT_CACHE[cwd]


def _untracked_mark(path, budget):
    """Dấu nhận dạng file untracked → (dấu, số byte đã đọc).

    Ưu tiên NỘI DUNG: mtime đổi mà nội dung y nguyên (touch, formatter ghi đè
    byte-identical) không phải là thay đổi — tính là thay đổi thì chặn oan.
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
    """Vân tay trạng thái làm việc của repo, hoặc None khi không lấy được.

    Gồm cả `status --porcelain` (file mới/xoá/đổi tên) lẫn `diff HEAD` (nội dung),
    vì porcelain KHÔNG đổi khi sửa tiếp một file vốn đã `M` — repo đang dở dang
    thì đó là trường hợp thường gặp nhất, bỏ qua là bỏ lọt.
    Sổ sách workflow bị loại trừ ngay từ pathspec của git (0.3.2).

    `status`: bytes `git status --porcelain` đã có sẵn (P0-2 — `turn_snapshot`
    gọi 1 lần rồi truyền xuống, tránh gọi git 2 lần/turn). None → tự lấy.

    None nghĩa là "không có bằng chứng", không phải "repo sạch" — nơi gọi phải
    coi None là fallback về hành vi cũ.
    """
    if status is None:
        status = _git(cwd, "status", "--porcelain", "--untracked-files=all", "--", ":(top)", *_EXCLUDE)
    if status is None:
        return None
    # repo chưa có commit → không có HEAD → rc≠0 → b""
    diff = _git(cwd, "diff", "HEAD", "--", ":(top)", *_EXCLUDE) or b""
    h = hashlib.sha256(status + b"\0" + diff)
    # File untracked: porcelain in `?? path` không đổi khi nội dung đổi, và `diff
    # HEAD` không đụng tới chúng — phải tự lấy dấu mới không bỏ lọt (QC1.1).
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
    """Path đang khác so với HEAD (bỏ cờ trạng thái, rename lấy vế đích).

    Cùng vùng loại trừ với `repo_status_digest` — quyết định và đặt tên phải
    nhìn đúng một tập path, lệch nhau là nguồn của chặn oan 0.3.1.

    `status`: bytes `git status --porcelain` đã có sẵn (P0-2, xem `repo_status_digest`).
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


# ------------------------------------------- trạng thái tick của plan (hàng rào)
#
# Status line và hàng rào ép tick đều cần biết plan "đang ở đâu". Băm cả FILE
# (không đếm riêng số `[x]`) vì `[ ]` → `[~]` cũng là cập nhật hợp lệ mà số `[x]`
# không đổi — đếm `[x]` sẽ bỏ lọt đúng cái mốc "bắt đầu task".

_TASK_LINE = re.compile(r"^\s*-\s*\[( |~|x)\]\s*\*\*[A-Za-z]+[0-9.]*\*\*")


def plan_tick_state(cwd):
    """Trạng thái checkbox của plan hiện hành. Không bao giờ ném lỗi."""
    trong = {"path": None, "exists": False, "sha": "",
             "has_doing": False, "all_done": False, "total": 0, "doing_count": 0}
    try:
        state = load(cwd, heal=False) or {}
    except Exception:
        return trong
    rel = state.get("plan_file")
    if not rel:
        req = state.get("active_request")
        if not req:
            return trong
        rel = os.path.join("docs", "tdq", "plan", f"{req}.md")
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    trong["path"] = path
    try:
        with open(path, encoding="utf-8") as f:
            noi_dung = f.read()
        sha = sha256_file(path)
    except OSError:
        return trong

    tong = xong = dang = 0
    for line in noi_dung.splitlines():
        m = _TASK_LINE.match(line)
        if not m:
            continue
        tong += 1
        if m.group(1) == "x":
            xong += 1
        elif m.group(1) == "~":
            dang += 1

    trong.update(exists=True, sha=sha, total=tong, doing_count=dang,
                 has_doing=dang > 0, all_done=tong > 0 and xong == tong)
    return trong


def turn_snapshot(cwd):
    """Trạng thái đầu turn: log hôm nay + vân tay repo + danh sách path đang bẩn
    + vân tay plan (để biết checkbox có động trong turn hay không)."""
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


# --------------------------------------------------------- enum an toàn (S4)

def normalize_lane(raw):
    """Bí danh -> định danh máy ("quick"/"full"). Không nhận ra -> None (người gọi
    quyết định báo lỗi hay bỏ qua). Đây là CỬA VÀO duy nhất cho lane do user gõ."""
    if not isinstance(raw, str):
        return None
    return LANE_ALIASES.get(raw.strip().lower())


def lane_label(lane):
    """Nhãn để IN RA cho người đọc. Là lớp hiển thị nên KHÔNG kiểm tra hợp lệ:
    lane lạ trả lại nguyên chuỗi, None trả chuỗi rỗng — in ra xấu còn hơn nổ."""
    if not lane:
        return ""
    return LANE_LABELS.get(lane, lane)


def normalize_mode(raw):
    """Bí danh -> định danh máy ("main"/"subagent"). CỬA VÀO duy nhất cho mode do user
    gõ. Không nhận ra -> None; người gọi quyết định báo lỗi hay bỏ qua."""
    if not isinstance(raw, str):
        return None
    # Gộp mọi khoảng trắng liên tiếp về một space: user hay gõ "sub-agent  implement".
    return MODE_ALIASES.get(" ".join(raw.strip().lower().split()))


def mode_label(mode):
    """Nhãn để IN RA cho người đọc, cùng luật với lane_label: mode lạ trả lại nguyên
    chuỗi, None trả chuỗi rỗng — đây là lớp hiển thị, không phải lớp kiểm tra."""
    if not mode:
        return ""
    return MODE_LABELS.get(mode, mode)


def effective_lane(state, warn=True):
    lane = (state or {}).get("lane")
    if lane in VALID_LANES:
        return lane
    if warn:
        _warn(f"lane không hợp lệ trong state: {lane!r} — coi như chưa chọn lane.")
    return None


def effective_phase(state, warn=True):
    phase = (state or {}).get("phase")
    if phase in VALID_PHASES:
        return phase
    if warn:
        _warn(f"phase không hợp lệ trong state: {phase!r} — coi như idle. "
              "Khôi phục bằng: python3 scripts/tdq_state.py set phase=<idle|analyze|spec|plan|implement|qc|report>")
    return "idle"


def effective_mode(state, warn=True):
    mode = (state or {}).get("implement_mode")
    if mode in VALID_MODES or mode is None:
        return mode
    if warn:
        _warn(f"implement_mode không hợp lệ: {mode!r} — coi như chưa chốt mode.")
    return None


# ------------------------------------------------------------- bảng phase

# Nguồn sự thật DUY NHẤT cho câu hỏi "đang ở đâu, làm gì tiếp".
# doc (tdq-conventions) trích lại từ đây; test khoá cứng.
PHASE_TABLE = {
    "no_state": {
        "entry": "Chưa có request TDQ nào đang mở",
        "action": "Hỏi user chọn lane rồi mở request mới",
        "cmd": "python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau>",
        "checklist": [
            "Tóm tắt yêu cầu của user thành 3–5 dòng",
            "Hỏi user chọn chế độ: chế độ nhanh (express — việc nhỏ, rõ) hay "
            "chế độ chuyên sâu (deep — Analysis→Spec→Plan→Implement→QC→Report)",
            "Chạy lệnh init ở trên với slug theo công thức YYYY-MM-DD-HHMM-HHMM-<kebab ≤5 từ, không dấu>",
            "Ghi yêu cầu nguyên văn vào docs/tdq/brief/<slug>.md mục '## Nguyên văn'",
        ],
        "done_when": "state.json có active_request và lane",
        "forbidden": "Sửa code khi chưa mở request",
    },
    "analyze": {
        "entry": "Đã có request, chế độ chuyên sâu (deep)",
        "action": "Đọc code, research, interview user đến khi hết chỗ mơ hồ",
        "cmd": "python3 scripts/tdq_state.py set phase=spec",
        "checklist": [
            "Kiểm kê năng lực (B0): chạy `python3 scripts/skill_inventory.py`, điền bảng "
            "phán quyết vào docs/tdq/brief/<slug>.md mục 'Hiểu & kiến thức'",
            "Đọc code/doc liên quan, ghi vào docs/tdq/research/<slug>.md",
            "Vòng scope trước (mặt nào + bối cảnh bằng số) theo "
            "skills/tdq-intake/references/scope-round.md, hoặc ghi 'Vòng scope: BỎ — lý do'",
            "Hỏi chi tiết trong đúng các mặt user chọn, ghi vào "
            "docs/tdq/brief/<slug>.md mục 'Hỏi đáp'",
            "Chốt quyết định vào docs/tdq/brief/<slug>.md mục 'Hiểu & kiến thức'",
            "Hết câu hỏi làm đổi kết quả → chạy lệnh trên",
        ],
        "done_when": "Không còn câu hỏi nào làm thay đổi kết quả",
        "forbidden": "Viết spec khi chưa hết mơ hồ",
    },
    "spec": {
        "entry": "Đã phân tích xong",
        "action": "Viết spec (kèm mục Lộ trình), đăng ký spec_file, trình tóm tắt rồi DỪNG chờ user duyệt",
        "cmd": "python3 scripts/tdq_state.py approve spec --by \"<nguyên văn câu user>\"",
        "checklist": [
            "Viết docs/tdq/spec/<slug>.md (scope in/out, đầu ra, Lộ trình, QC + DoD)",
            "Chạy: python3 scripts/tdq_state.py set spec_file=docs/tdq/spec/<slug>.md",
            "Trình tóm tắt spec ≤50 dòng trong chat",
            "In: ➤ Duyệt: nhắn \"duyệt spec\" · Góp ý: nhắn trực tiếp — rồi DỪNG",
            "User duyệt → chạy lệnh approve ở trên NGAY, rồi viết plan trong CÙNG turn "
            "(không bắt user nhắn thêm câu nào)",
        ],
        "done_when": "spec_approved = true",
        "forbidden": "Tự suy diễn là user đã duyệt; bắt user nhắn thêm một turn nữa mới viết plan",
    },
    "plan": {
        "entry": "spec_approved = true",
        "action": "Viết plan kèm mode ĐỀ XUẤT, đăng ký plan_file, trình rồi DỪNG chờ duyệt",
        "cmd": "python3 scripts/tdq_state.py approve plan --by \"<nguyên văn>\"",
        "checklist": [
            "ĐỀ XUẤT mode thực thi ngay trong plan (main|subagent) + lý do — "
            "không hỏi mode ở bước này; cổng mode là phase riêng ngay sau",
            "Viết docs/tdq/plan/<slug>.md: mỗi task 1 việc + 1 test, có checkbox [ ]",
            "Chạy: python3 scripts/tdq_state.py set plan_file=docs/tdq/plan/<slug>.md",
            "Trình tóm tắt plan, mời user nhắn \"duyệt plan\", rồi DỪNG",
            "User duyệt → chạy lệnh approve ở trên NGAY, rồi hỏi mode trong CÙNG turn "
            "(user đã nói mode sẵn thì thêm --mode và build luôn)",
        ],
        "done_when": "plan_approved = true",
        "forbidden": "Sửa code khi plan chưa duyệt; bắt user nói mode mới chịu ghi nhận duyệt",
    },
    "mode": {
        "entry": "plan_approved = true mà implement_mode chưa chốt",
        "action": "Giải thích ngắn gọn 2 mode rồi hỏi user chọn, DỪNG chờ trả lời",
        "cmd": "python3 scripts/tdq_state.py approve plan --mode <main|subagent> --by \"<nguyên văn>\"",
        "checklist": [
            "Trình khối chọn mode theo khuôn user-facing-block, mỗi mode một dòng nghĩa: "
            "làm trực tiếp (inline implement) = tôi tự làm tuần tự ngay đây; "
            "giao trợ lý (sub-agent implement) = nhiều agent chạy song song",
            "Trình 1–3 dòng phân tích lý do đề xuất, lấy căn cứ TỪ CHÍNH PLAN: số task, "
            "task phụ thuộc nối tiếp, số file bị nhiều task cùng đụng, có nhãn (mcp) không; "
            "cộng một câu vì sao không chọn phương án còn lại. KHÔNG tự chốt thay user",
            "DỪNG chờ user chọn",
            "User chọn → chạy lệnh approve ở trên NGAY, rồi build trong CÙNG turn",
        ],
        "done_when": "implement_mode khác null",
        "forbidden": "Sửa code khi chưa chốt mode; tự chọn mode thay user",
    },
    "implement": {
        "entry": "plan_approved = true và implement_mode đã chốt",
        "action": "Làm hết plan trong 1 turn, mỗi task đánh [~] khi bắt đầu, red→green, đổi [x] ngay khi pass",
        "cmd": "python3 scripts/tdq_state.py set phase=qc",
        "checklist": [
            "Làm task theo đúng thứ tự trong plan",
            "Mỗi task: đánh [~] → viết test (đỏ) → code → test xanh → đổi [x] vào plan NGAY",
            "Không dừng giữa chừng để hỏi 'có tiếp không'",
            "Xong hết task → chạy lệnh trên",
        ],
        "done_when": "Mọi task trong plan đã tick [x]",
        "forbidden": "Dừng giữa chừng; gom tick vào cuối turn; để nhiều task cùng mang [~]",
    },
    "qc": {
        "entry": "Đã implement xong",
        "action": "Chạy Definition of Done của spec, ghi kết quả, fail thì fix tiếp",
        "cmd": "python3 scripts/tdq_state.py set phase=report",
        "checklist": [
            "Chạy đủ mục QC trong spec, ghi bằng chứng vào docs/tdq/qc/<slug>.md",
            "FAIL → thêm task fix vào plan (không cần duyệt lại) rồi làm tiếp",
            "Lặp đến khi mọi mục PASS",
        ],
        "done_when": "Mọi mục QC trong spec PASS, có bằng chứng",
        "forbidden": "Bỏ qua test fail; báo PASS khi chưa chạy",
    },
    "report": {
        "entry": "QC đã PASS",
        "action": "Viết report ngắn gọn (khuyến nghị 10-20 dòng, không giới hạn cứng) rồi hỏi user có commit không",
        "cmd": "python3 scripts/tdq_state.py set phase=idle",
        "checklist": [
            "Viết docs/tdq/reports/<slug>.md ngắn gọn (khuyến nghị 10-20 dòng): "
            "đã làm gì, kết quả QC, giới hạn còn lại",
            "Append working log docs/workinglog/<hôm nay>.md",
            "Hỏi user: có commit không?",
        ],
        "done_when": "Report đã ghi và user đã được hỏi về commit",
        "forbidden": "Tự commit hoặc push khi user chưa yêu cầu",
    },
    "idle": {
        "entry": "Đã xong hoặc chưa mở request",
        "action": "Chờ yêu cầu mới từ user",
        "cmd": "python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau>",
        "checklist": [
            "Có yêu cầu mới → tóm tắt, hỏi lane, chạy lệnh init ở trên",
        ],
        "done_when": "Có request mới được mở",
        "forbidden": "Đè request cũ còn dở mà chưa hỏi user",
    },
    "quick": {
        "entry": "lane = quick",
        "action": "Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → implement → QC bám DoD (mặc định BẬT) → vòng fix nếu FAIL",
        # A26: khớp intake — quick có biến thể bỏ QC ("duyệt quick không QC"
        # → --no-qc, phải kèm --by).
        "cmd": "python3 scripts/tdq_state.py approve quick [--no-qc] --by \"<nguyên văn câu user>\"",
        "checklist": [
            "Phân tích: đọc code liên quan; có ẩn số bên ngoài (thư viện, API, phiên bản) "
            "→ web search qua tavily-primary trước khi viết gì",
            "Interview khi còn câu hỏi làm ĐỔI kết quả — theo luật interview.md; "
            "chỉ khi vòng đó có ít nhất một câu hỏi thì mới đóng vòng bằng câu "
            "'Bạn muốn bổ sung thêm gì không?', không có câu hỏi thì đi thẳng bước sau",
            "Viết mini-spec/plan GỘP vào docs/tdq/plan/<slug>.md (≤40 dòng: scope in/out, "
            "task có test, DoD) rồi trình tóm tắt ≤10 dòng trong chat, "
            "kèm 1 dòng 'Năng lực: <skill sẽ DÙNG hoặc không có>'",
            "In: ➤ Duyệt: nhắn \"duyệt quick\" (bỏ QC: \"duyệt quick không QC\") "
            "· Góp ý: nhắn trực tiếp — rồi DỪNG",
            "User duyệt → chạy lệnh approve ở trên (--no-qc CHỈ khi user nói rõ bỏ QC, "
            "im lặng về QC = CÓ QC)",
            "Append summary plan vào docs/workinglog/<hôm nay>.md TRƯỚC khi sửa code",
            "Implement từng task: đánh [~] cho task đang làm TRƯỚC khi sửa code "
            "(hook edit_gate CHẶN nếu plan không có [~]), red→green, "
            "đổi sang [x] NGAY khi test của task đó xanh — không gom tick cuối turn",
            "QC: mỗi dòng DoD một phép kiểm bằng lệnh, cộng hạng mục chạy test từng task. "
            "Bằng chứng ghi vào mục ## QC của plan. "
            "quick_qc_skipped = true thì mục ## QC chỉ có 1 dòng "
            "'BỎ theo yêu cầu user: \"<nguyên văn>\"'",
            "QC FAIL hoặc thấy bug → fix. "
            "Thêm task vào mục ## QC vòng N — fix của plan, fix red→green. "
            "Chạy lại hạng mục đã FAIL cộng hạng mục mà bản fix có thể làm hỏng. "
            "Trần 3 vòng, vượt trần thì DỪNG, báo user, đề xuất chuyển chế độ chuyên sâu (deep)",
            "Đóng việc: chạy `python3 scripts/tdq_state.py set phase=idle` — terminal của chế độ nhanh (express)",
        ],
        "done_when": "quick_approved = true, log đã ghi, mục ## QC trong plan đã có (bằng chứng hoặc dòng BỎ theo yêu cầu user), không còn test đỏ, phase đã về idle",
        "forbidden": "Implement trước khi ghi working log; gom tick vào cuối turn hoặc để nhiều task cùng mang [~]; đóng việc khi còn test đỏ hoặc còn bug đã biết; chạy set phase=idle khi đã vượt trần 3 vòng fix mà chưa báo user",
    },
}


PHASE_ORDER = ["no_state", "analyze", "spec", "plan", "mode", "implement", "qc", "report",
               "idle", "quick"]


_SCRIPT_PATH = re.compile(r"python3 scripts/(\S+\.py)")


def plugin_root_cmd(cmd):
    """A40: dạng lệnh cho doc chạy trong ngữ cảnh plugin (conventions §1)."""
    return _SCRIPT_PATH.sub(r'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/\1"', cmd)


def render_phases_md(plugin_root=False):
    """Sinh doc bảng phase từ PHASE_TABLE — doc KHÔNG được viết tay.

    Chạy lại bằng: python3 scripts/tdq_state.py phases-doc > <file>
    (thêm --plugin-root cho bản skills/tdq-conventions — path theo conventions §1).
    tests/test_phase_table.py::test_docs_match_constant khoá cứng sự đồng bộ này.
    """
    conv = plugin_root_cmd if plugin_root else (lambda c: c)
    lines = [
        "# Bảng phase TDQ (tự sinh — KHÔNG sửa tay)",
        "",
        "Sinh lại: `" + conv("python3 scripts/tdq_state.py") + " phases-doc"
        + (" --plugin-root" if plugin_root else "") + " > <file>`.",
        "Nguồn: hằng `PHASE_TABLE` trong `scripts/tdq_state.py`.",
        "Đang ở phase nào thì chỉ làm đúng việc của phase đó, xong chạy đúng lệnh của nó.",
        "",
        "| phase | vào khi | việc duy nhất | lệnh chuyển tiếp | xong khi | cấm |",
        "|---|---|---|---|---|---|",
    ]
    def cell(text):
        # `|` trong <quick|full> sẽ cắt ô của bảng markdown, kể cả trong backtick.
        return str(text).replace("|", "\\|")

    for name in PHASE_ORDER:
        row = PHASE_TABLE[name]
        lines.append("| `{}` | {} | {} | `{}` | {} | {} |".format(
            name, cell(row["entry"]), cell(row["action"]), cell(conv(row["cmd"])),
            cell(row["done_when"]), cell(row["forbidden"])))
    lines.append("")
    lines.append("Lệnh nguyên văn (copy được, không có ký tự thoát):")
    lines.append("")
    lines.append("```")
    for name in PHASE_ORDER:
        lines.append(f"{name}: {conv(PHASE_TABLE[name]['cmd'])}")
    lines.append("```")
    lines.append("")
    # Checklist từng phase KHÔNG sinh ra đây (bỏ 2026-08-09): nó lặp lại nội dung
    # SKILL.md của chính phase đó. Muốn checklist đầy đủ thì chạy `tdq_state.py next`.
    lines.append("Checklist chi tiết của phase đang chạy: `"
                 + conv("python3 scripts/tdq_state.py") + " next`.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def phase_key(state):
    """Khoá tra PHASE_TABLE cho state hiện tại."""
    if not state or not state.get("active_request"):
        return "no_state"
    lane = effective_lane(state, warn=False)
    if lane == "quick":
        # A6: terminal cho lane quick — đã duyệt VÀ đã set phase=idle nghĩa là xong
        # (approve quick đẩy phase=implement, nên idle sau đó chỉ có thể là chủ động đóng).
        if state.get("quick_approved") and effective_phase(state, warn=False) == "idle":
            return "idle"
        return "quick"
    return effective_phase(state, warn=False)


# ------------------------------------------------------------------ next

def _mark(approved, registered):
    if approved:
        return "✔"
    return "⏳ chờ duyệt" if registered else "—"


def next_headline(cwd, state):
    """Dòng 1 của `next` — cũng là toàn bộ output của `next --brief`."""
    if not state or not state.get("active_request"):
        return f"[TDQ:NEXT] chưa có request · phase idle · Project: {os.path.abspath(cwd)}"
    # phase_key, không phải phase thô: lane quick giữ phase=idle nhưng vẫn còn
    # việc phải làm — in "idle" khiến model tưởng đã xong (QC1.1).
    return (f"[TDQ:NEXT] {state.get('active_request')} · lane {effective_lane(state, warn=False) or '?'} "
            f"· phase {phase_key(state)} · Project: {os.path.abspath(cwd)}")


def render_next(cwd, state, brief=False, compact=False):
    """Khối 5 phần (spec §2.2), ≤20 dòng.

    brief=True   → đúng 1 dòng tiêu đề (dùng cho UserPromptSubmit, mỗi turn).
    compact=True → bỏ checklist, thêm con trỏ tới lệnh `next` (dùng cho
                   SessionStart, nơi trần chỉ 600 ký tự và dòng luật phải nằm
                   trên cùng — xem hooks/scripts/session_start.py).
    """
    if state and state.get("active_request"):
        effective_lane(state)          # cảnh báo (kèm hướng dẫn khôi phục) nếu enum sai
        effective_phase(state)
    head = next_headline(cwd, state)
    if brief:
        return head
    row = PHASE_TABLE[phase_key(state)]
    lines = [head, f"Việc tiếp theo: {row['action']}", "Lệnh:", f"  {row['cmd']}"]
    if compact:
        lines.append("Checklist đầy đủ: python3 scripts/tdq_state.py next")
    else:
        lines.append("Checklist (copy vào câu trả lời, tick dần):")
        lines += [f"- [ ] {item}" for item in row["checklist"]]
    lines.append(f"Xong khi: {row['done_when']}")
    return "\n".join(lines)


def render_state_md(cwd, state):
    """Mirror markdown ≤30 dòng cho agent/user đọc thẳng (spec §2.3.1)."""
    state = state or default_state()
    lane = effective_lane(state, warn=False)
    row = PHASE_TABLE[phase_key(state)]
    spec = state.get("spec_file") or "(chưa có)"
    if state.get("spec_file"):
        spec += " — " + ("✔ đã duyệt" if state.get("spec_approved") else "⏳ chờ duyệt")
    plan = state.get("plan_file") or "(chưa có)"
    if state.get("plan_file"):
        plan += " — " + ("✔ đã duyệt" if state.get("plan_approved") else "⏳ chờ duyệt")
    quick = "✔ đã duyệt" if state.get("quick_approved") else "⏳ chờ duyệt"
    lines = [
        "# TDQ STATE (tự sinh — không sửa tay)",
        f"Cập nhật: {state.get('updated_at') or now_iso()} · Project: {os.path.abspath(cwd)} · schema 3",
        "",
        "| Trường | Giá trị |",
        "|---|---|",
        f"| Request | {state.get('active_request') or '(chưa có)'} |",
        f"| Lane | {lane or '(chưa chọn)'} |",
        f"| Phase | {effective_phase(state, warn=False)} |",
        f"| Spec | {spec} |",
        f"| Plan | {plan} |",
        f"| Duyệt quick | {quick if lane == 'quick' else '(không áp dụng)'} |",
        f"| Mode thực thi | {effective_mode(state, warn=False) or '(chưa chốt)'} |",
        "",
        "## Đang ở đâu",
        f"{row['entry']}. Cấm: {row['forbidden']}.",
        "",
        "## Việc tiếp theo",
        row["action"] + ".",
        "```",
        row["cmd"],
        "```",
        f"Xong khi: {row['done_when']}",
        "",
        "> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- sổ turn

def turn_log_append(cwd, kind, session=None, **fields):
    """Ghi một sự kiện vào sổ turn. Lỗi I/O → nuốt im lặng (hook không được hỏng)."""
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
    except (ValueError, TypeError):  # A18: ts số/None không được kéo chết hook
        return False
    if ts.tzinfo is None:
        ts = ts.astimezone()
    return (datetime.now(timezone.utc) - ts.astimezone(timezone.utc)).total_seconds() <= TURN_STALE_SECONDS


def turn_log_read(cwd, session=None):
    """Các sự kiện của session hiện tại, bỏ qua dòng cũ hơn 6 giờ (RR12)."""
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
    """Xoá dòng của session này (đầu turn). Dòng session khác giữ nguyên."""
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
    """Digest nội dung [TDQ:...] đã in ở turn trước cho session này, None nếu chưa có."""
    try:
        with open(prompt_context_path(cwd), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("session") != session:
        return None
    return data.get("digest")


def prompt_context_save(cwd, session, digest):
    """Ghi digest nội dung vừa in — turn_log_clear không đụng tới file này
    (dedupe cần sống QUA nhiều turn, khác sổ turn bị xoá mỗi đầu turn)."""
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
    """Request còn dở dang: chưa tới phase kết thúc, hoặc đã có gate được duyệt."""
    if state.get("phase") not in DONE_PHASES:
        return True
    return any(state.get(k) for k in ("spec_approved", "plan_approved", "quick_approved"))


def _parse_approve_args(rest):
    """-> (target, mode, by, no_qc). Chỉ lỗi khi cú pháp thật sự sai."""
    if not rest:
        _fail("Thiếu đối tượng duyệt (spec|plan|quick).")
    target, mode, by, no_qc = rest[0], None, None, False
    # Bí danh của lane quick: user gõ "approve nhanh" cũng ghi vào khoá quick_*.
    if target not in APPROVE_TARGETS and normalize_lane(target) == "quick":
        target = "quick"
    if target not in APPROVE_TARGETS:
        _fail(f"Đối tượng duyệt không hợp lệ: {target} "
              "(spec|plan|quick, bí danh của quick: nhanh|express)")
    i = 1
    while i < len(rest):
        flag = rest[i]
        if flag == "--no-qc":
            # QC ở quick mặc định BẬT — chỉ lane quick mới có đường opt-out này.
            if target != "quick":
                _fail(f"Cờ --no-qc chỉ dùng cho `approve quick`, không dùng cho {target}.")
            no_qc = True
            i += 1
            continue
        if flag in ("--mode", "--by"):
            if i + 1 >= len(rest):
                _fail(f"Thiếu giá trị cho {flag}")
            value = rest[i + 1]
            if flag == "--mode":
                # Qua normalize_mode: user gõ nhãn thấy ở cổng mode ("inline",
                # "sub-agent implement") cũng phải ghi ra đúng định danh máy.
                mode = normalize_mode(value)
                if mode is None:
                    _fail("Mode không hợp lệ (main|inline | subagent|sub-agent).")
            else:
                by = value[:BY_MAX]
            i += 2
            continue
        # cho phép "approve plan main" (user gõ tắt) — mode đứng ngay sau target.
        # Nhận cả bí danh, nhưng chỉ khi chưa có mode: tham số lạ vẫn phải nổ.
        if mode is None and normalize_mode(flag):
            mode = normalize_mode(flag)
            i += 1
            continue
        _fail(f"Tham số không hợp lệ: {flag}")
    if no_qc and not by:
        # Bỏ QC phải để lại nguyên văn câu user, nếu không thì mất dấu vết ai bỏ và vì sao.
        _fail('Bỏ QC phải kèm --by "<nguyên văn câu user>" để còn dấu vết.')
    return target, mode, by, no_qc


def _file_changed_since_approval(cwd, state, target):
    """True khi file spec/plan đã đổi nội dung so với lúc duyệt. Dùng để phân biệt
    'duyệt lại lệnh thừa' với 'sửa file trong lúc QC rồi xin duyệt lại' — trường hợp
    sau phải ghi lại sha256, không thì cảnh báo lệch sha treo vĩnh viễn."""
    if target not in ("spec", "plan"):
        return False
    old = state.get(f"{target}_sha256")
    rel = state.get(f"{target}_file")
    if not old or not rel:
        return False
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    try:
        return sha256_file(path) != old
    except OSError:
        return False


def _cli_approve(cwd, rest):
    """Ghi nhận việc user đã duyệt. Không phải gate: cảnh báo khi lệch nhưng
    VẪN ghi và luôn exit 0 — bế tắc do gate là thứ 0.2.0 loại bỏ."""
    target, mode, by, no_qc = _parse_approve_args(rest)
    state = load(cwd)
    if state is None:
        _warn("Chưa có state — dựng state mặc định rồi ghi nhận duyệt. Nên chạy init trước.")
        state = default_state()
    stamp = state.get("updated_at")

    if state.get(f"{target}_approved") and not _file_changed_since_approval(cwd, state, target):
        print(f"ℹ️ {target} đã duyệt lúc {state.get(f'{target}_approved_at')} — không ghi lại, đi tiếp bước sau.")
        if mode and state.get("implement_mode") != mode:
            state["implement_mode"] = mode
            # Đây chính là đường user trả lời ở cổng `mode`: plan đã duyệt từ trước,
            # lần này chỉ chốt mode → mở đường sang implement luôn.
            if target == "plan" and effective_phase(state, warn=False) == "mode":
                state["phase"] = "implement"
            save(cwd, state, expect_updated_at=stamp)
            print(f"ℹ️ Đã cập nhật implement_mode = {mode}.")
        return
    reapproved = bool(state.get(f"{target}_approved"))

    lane = effective_lane(state)
    if not state.get("active_request"):
        _warn("Chưa có request TDQ nào đang mở — vẫn ghi nhận, nhưng nên chạy init trước.")
    if target == "quick" and lane != "quick":
        _warn(f"Duyệt quick nhưng request đang ở lane {lane}.")
    if target in ("spec", "plan") and lane != "full":
        _warn(f"Duyệt {target} nhưng request đang ở lane {lane}.")
    if target == "plan" and not state.get("spec_approved"):
        _warn("Duyệt plan khi spec chưa được ghi nhận duyệt — kiểm tra lại thứ tự.")

    if target in ("spec", "plan"):
        rel = state.get(f"{target}_file")
        if not rel:
            _warn(f"Chưa đăng ký {target}_file trong state — không tính được sha256.")
        else:
            path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
            try:
                state[f"{target}_sha256"] = sha256_file(path)
            except OSError:
                _warn(f"Không đọc được {rel} — bỏ qua sha256.")

    state[f"{target}_approved"] = True
    state[f"{target}_approved_at"] = now_iso()
    state[f"{target}_approved_by"] = by
    if mode:
        state["implement_mode"] = mode
    if target == "quick":
        # A6: quick không đi qua bảng phase — đẩy implement để `set phase=idle`
        # lúc đóng việc trở thành terminal phân biệt được với idle trước duyệt.
        state["phase"] = "implement"
        state["quick_qc_skipped"] = no_qc
    if target == "plan":
        # Cổng mode tách khỏi cổng plan: duyệt plan mà chưa chốt mode thì dừng ở
        # phase `mode` (giải thích + hỏi). User nói mode ngay trong câu duyệt thì
        # bỏ qua cổng đó, vào thẳng implement — không hỏi lại thứ user vừa nói.
        state["phase"] = "implement" if state.get("implement_mode") else "mode"
    save(cwd, state, expect_updated_at=stamp)
    if no_qc:
        # Dòng có timestamp chỉ ra từ _info (stderr, tắt được bằng TDQ_LOG=0);
        # dòng ✅ stdout bên dưới không mang timestamp nên không dùng cho vết log này.
        _info(f'Ghi nhận user BỎ QC cho quick theo yêu cầu: "{by}". '
              "Bỏ QC không phải bỏ sửa lỗi: test đỏ hoặc bug đã biết vẫn phải fix.")
    if not by:
        _warn("Thiếu --by \"<nguyên văn câu user>\" — nên ghi lại để còn đối chiếu ai duyệt cái gì.")
    extra = f", mode {mode}" if mode else ""
    if reapproved:
        print(f"✅ {target} đã sửa sau lần duyệt trước — ghi nhận user duyệt lại "
              f"lúc {state[f'{target}_approved_at']}{extra}, sha256 đã cập nhật.")
    else:
        print(f"✅ Đã ghi nhận user duyệt {target} lúc {state[f'{target}_approved_at']}{extra}.")


def _pop_json_flag(argv):
    """Tách cờ `--json` khỏi argv. Mặc định CLI in 1 dòng tóm tắt cho nhẹ context;
    có `--json` thì in lại nguyên state như trước (dùng khi cần soi/debug)."""
    rest = [a for a in argv if a != "--json"]
    return rest, len(rest) != len(argv)


def _echo_state(cmd, state, want_json):
    """In kết quả của lệnh ghi state: 1 dòng tóm tắt, hoặc nguyên JSON khi --json."""
    if want_json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    print(f"✅ {cmd}: request={state.get('active_request')} "
          f"lane={state.get('lane')} phase={state.get('phase')}")


def cli(argv):
    started_in = os.getcwd()
    env = os.environ.get("TDQ_PROJECT_DIR")
    cwd = resolve_project_dir(started_in)
    if not env and os.path.realpath(cwd) != os.path.realpath(started_in):
        _info(f"Project root: {cwd} (lệnh chạy từ {started_in})")
    for shadow in find_shadow_states(cwd):
        _warn(f"Phát hiện state thừa: {shadow} — chỉ {STATE_REL} ở project root có hiệu lực, "
              "xoá file thừa để tránh đọc nhầm trạng thái duyệt.")
    if not argv:
        _fail("Thiếu lệnh.")
    cmd = argv[0]

    if cmd == "next":
        brief = "--brief" in argv[1:]
        for extra in argv[1:]:
            if extra != "--brief":
                _fail(f"Tham số không hợp lệ: {extra}")
        print(render_next(cwd, load(cwd), brief=brief))
        return

    if cmd == "phases-doc":
        # Không đọc/ghi state: chỉ đổ hằng PHASE_TABLE ra markdown.
        extra = argv[1:]
        if extra not in ([], ["--plugin-root"]):
            _fail(f"Tham số không hợp lệ: {' '.join(extra)}")
        print(render_phases_md(plugin_root=bool(extra)), end="")
        return

    if cmd == "get":
        state = load(cwd) or default_state()
        if len(argv) > 1:
            key = argv[1]
            if key not in state:
                _warn(f"Key không có trong state: {key}")
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
        if len(argv) < 2:
            _fail(f"Thiếu slug. Công thức: {SLUG_FORMULA}")
        # Ghi mới thì bắt buộc có giờ phút. Cảnh báo suông không đổi được hành vi:
        # chuẩn mới sẽ trôi ngay lần đầu ai đó bỏ qua. Đọc vẫn nhận slug cũ.
        phan_tich = parse_slug(argv[1])
        if phan_tich is None:
            _fail(f"Slug sai định dạng: {argv[1]}. Công thức: {SLUG_FORMULA}")
        if phan_tich[1] is None:
            _fail(f"Slug thiếu giờ phút: {argv[1]}. Công thức: {SLUG_FORMULA} "
                  f"(ví dụ {phan_tich[0]}-{datetime.now().strftime('%H%M')}-{phan_tich[2]})")
        # init = MỞ REQUEST MỚI: reset toàn bộ state (request, lane, phase,
        # spec/plan file, mọi field duyệt, implement_mode). Nếu request đang mở
        # còn dở dang thì cảnh báo ra stderr — vẫn thực hiện, nhưng có dấu vết.
        old = load(cwd) or {}
        old_slug = old.get("active_request")
        if old_slug:
            # init xoá sạch state. Không đóng sổ trước thì toàn bộ mốc thời gian của
            # request cũ bay mất — đây là cửa duy nhất bắt được request bị bỏ dở.
            _dong_so_request_cu(cwd)
        state = default_state()
        state["active_request"] = argv[1]
        state["previous_request"] = old_slug
        state["started_at"] = now_iso()
        ghi_moc_phase(state, state["phase"], state["started_at"])
        if old_slug and old_slug != argv[1] and _unfinished(old):
            _warn(f"Ghi đè request '{old_slug}' (lane {old.get('lane')}, "
                  f"phase {old.get('phase')}) — mọi trạng thái duyệt của request đó bị xoá.")
        if len(argv) > 2:
            lane = normalize_lane(argv[2])
            if lane is None:
                _fail("Lane không hợp lệ. Nhận: nhanh|express|quick "
                      "(chế độ nhanh) · chuyen-sau|deep|full (chế độ chuyên sâu).")
            state["lane"] = lane
        save(cwd, state)
        _echo_state("init", state, want_json)
        return

    if cmd == "set":
        argv, want_json = _pop_json_flag(argv)
        state = load(cwd)
        if state is None:
            _warn("Chưa có state — dựng state mặc định rồi áp thay đổi. Nên chạy init trước.")
            state = default_state()
        stamp = state.get("updated_at")
        if len(argv) < 2:
            _fail("Thiếu cặp key=value.")
        for pair in argv[1:]:
            if "=" not in pair:
                _fail(f"Tham số không hợp lệ: {pair} (cần dạng key=value)")
            key, raw = pair.split("=", 1)
            if key not in default_state():
                _fail(f"Key không tồn tại trong schema: {key}")
            value = _parse_value(raw)
            if key == "lane" and value not in VALID_LANES:
                _fail("Lane không hợp lệ (quick|full|null).")
            if key == "phase" and value not in VALID_PHASES:
                _fail("Phase không hợp lệ (idle|analyze|spec|plan|implement|qc|report).")
            state[key] = value
            if key == "phase":
                ghi_moc_phase(state, value)
        save(cwd, state, expect_updated_at=stamp)
        _echo_state("set", state, want_json)
        return

    if cmd == "approve":
        return _cli_approve(cwd, argv[1:])

    if cmd == "reset":
        argv, want_json = _pop_json_flag(argv)
        state = default_state()
        save(cwd, state)
        _echo_state("reset", state, want_json)
        return

    _fail(f"Lệnh không hợp lệ: {cmd}")


if __name__ == "__main__":
    cli(sys.argv[1:])
