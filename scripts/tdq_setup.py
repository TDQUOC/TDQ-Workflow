#!/usr/bin/env python3
"""Install and prove every dependency the workflow searches with (stdlib only).

One command, four jobs, in this order:
  1. run the ladder of `tdq_lsp.py` and INSTALL what is missing and allowed
  2. check the configuration each layer needs is actually right
  3. re-run `tdq_lsp.kiem_mot_lenh` — the same ladder + four-layer smoke + total line that
     `tdq_lsp.py check` prints — so both commands judge the machine the same way
  4. write down, as debt, everything it could not fix by itself

Exit code: the one `kiem_mot_lenh` returns (0 total ĐẠT, 3 a rung blocks, 4 a layer failed).

Why this file exists next to `tdq_lsp.py` instead of inside it: `tdq_lsp.py` carries a hard
promise — it NEVER installs, it only diagnoses and prints the command. That promise is what
makes it safe to run on every request at intake. This script is the opposite half: the user
types it, and typing it IS the consent to install. Keeping the two promises in two files is
what keeps each one readable.

The consent is not unlimited. A command only runs when it matches the declared allow-list
below; anything else becomes a line of debt, never a silent skip and never a guess.

The CLI also declares the lumen + lsp MCP servers for Codex (`tdq_codex_mcp.khai_mcp_codex`).

`--nen` is the other mode: the detached background build a SessionStart hook spawns (installs,
graphify graph, lumen index) under a pid lock, ending in the readiness stamp
`docs/tdq/.tdq-san-sang.json`. See `khoi_tao_nen`.

Env: TDQ_PROJECT_DIR anchors the project; TDQ_LOG=0 silences the log.
"""
import argparse
import io
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
import tdq_lsp  # noqa: E402
import tdq_no  # noqa: E402 — hạ tầng ghi nợ dùng chung với tdq_finish.py
import utf8_io  # noqa: E402

TIMEOUT_CAI = 300
# Trần cho mỗi phép smoke: chúng chạy sau khi cài xong, và không phép nào được treo lệnh setup.
TIMEOUT_SMOKE = 60
# Đuôi của bản sao lưu để lại trước khi chạm vào file của plugin khác — không có nó thì không lùi được.
DUOI_SAO_LUU = ".truoc-tdq.bak"
# Instruction user-level của Claude Code. Đây là file NGOÀI repo, nên mọi thứ ghi vào đó chỉ được
# nằm trong khối có dấu mốc — phần user tự viết không bao giờ bị đụng tới.
DUONG_INSTRUCTION = "~/.claude/CLAUDE.md"

# Danh sách đã khai: một lệnh chỉ được chạy khi nó bắt đầu bằng đúng một trong các tiền tố này.
# Đây là ranh giới của sự cho phép — user gõ `setup` là đồng ý cài PHỤ THUỘC CỦA WORKFLOW, không
# phải đồng ý cho script chạy mọi chuỗi mà một bậc thang in ra.
TIEN_TO_CAI_DUOC = (
    "uv tool install ",
    "ollama pull ",
    "brew install ",
    "npm i -g ",
    "npm install -g ",
    "pipx install ",
)

# Không bao giờ chạm python hệ thống của Apple — ràng buộc đứng của user, nhắc lại ở đây vì
# tiền tố ở trên không chặn được một lệnh `pip install` đi qua đúng bản python đó.
DUONG_PYTHON_CAM = ("/usr/bin/python", "/System/Library/Frameworks/Python")
# Ký tự chỉ có nghĩa với shell. Thấy là từ chối: lệnh cài phải là MỘT lệnh, không phải một đoạn
# script — và `_chay_lenh` không có shell để hiểu chúng.
KY_TU_SHELL = (";", "&", "|", "$", "`", "\n", ">", "<")

def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _log_enabled():
    """Một công tắc duy nhất cho cả hai module: `--khong-log` chỉ việc set đúng biến này."""
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


def _chay_lenh(lenh):
    """Chạy một lệnh cài -> (rc, đầu ra). KHÔNG dùng shell.

    Bản đầu chạy `shell=True` rồi tự tách chuỗi bằng regex để kiểm từng vế. Đó là viết lại một
    bộ tách lệnh của shell — thứ không bao giờ đúng: nó không thấy xuống dòng, `$(...)`, dấu
    huyền, hay `;` nằm trong nháy. Mà chuỗi lệnh có phần nội suy từ cấu hình của máy
    (`ollama pull {model}` lấy `model` từ `config.yaml`), nên đó là một đường tiêm lệnh thật.

    Nay `shlex` tách, `shell=False` chạy: vế nào không phải lệnh thì không có gì chạy nó.
    """
    _log(f"cài: {lenh}")
    try:
        argv = shlex.split(lenh)
    except ValueError as exc:
        return 1, f"không tách được lệnh: {exc}"
    if not argv:
        return 1, "lệnh rỗng"
    try:
        p = subprocess.run(argv, capture_output=True,
                           encoding="utf-8", errors="replace", text=True, timeout=TIMEOUT_CAI)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, f"quá {TIMEOUT_CAI}s"
    except OSError as exc:
        return 1, str(exc)


def _duoc_cai(lenh):
    """-> (được chạy?, lý do từ chối). Fail-closed: không khớp danh sách là KHÔNG.

    Bậc 3 nối lệnh của nhiều ngôn ngữ bằng ` ; `, nên một project C + Ruby sinh ra
    `brew install llvm ; gem install solargraph`: chuỗi đó bắt đầu bằng một tiền tố hợp lệ trong
    khi vế sau thì không. Kiểm tiền tố của cả chuỗi là để lọt đúng vế sau.

    Cách xử đúng tầng là TỪ CHỐI cả chuỗi ghép, không phải tự viết lại bộ tách lệnh của shell để
    duyệt từng vế: `_chay_lenh` nay chạy `shell=False`, nên một chuỗi ghép cũng không chạy nổi.
    Người khai lệnh phải khai từng lệnh một.
    """
    if any(cam in lenh for cam in DUONG_PYTHON_CAM):
        return False, "lệnh đi qua python hệ thống của Apple — không bao giờ chạm"
    if any(k in lenh for k in KY_TU_SHELL):
        return False, "lệnh có ký tự của shell — không chạy chuỗi ghép, hãy khai từng lệnh một"
    if not lenh.startswith(TIEN_TO_CAI_DUOC):
        return False, "lệnh nằm ngoài danh sách phụ thuộc đã khai"
    return True, ""


def cai_thieu(bac_list, chay_lenh=None):
    """-> (đã cài, nợ). Cài mọi bậc còn thiếu mà lệnh của nó nằm trong danh sách đã khai.

    `chay_lenh` (str -> (rc, output)) defaults to `_chay_lenh`; the background build passes its
    own runner so its deadline also bounds the installs.
    """
    chay_lenh = chay_lenh or _chay_lenh
    da_cai, no = [], []
    for bac in bac_list:
        if bac.dat or not bac.lenh_cai:
            continue
        duoc, ly_do = _duoc_cai(bac.lenh_cai)
        if not duoc:
            no.append(f"bậc {bac.so} ({bac.ten}): {ly_do} — `{bac.lenh_cai}`")
            continue
        rc, ra = chay_lenh(bac.lenh_cai)
        if rc == 0:
            da_cai.append(f"bậc {bac.so} ({bac.ten}): `{bac.lenh_cai}`")
        else:
            no.append(f"bậc {bac.so} ({bac.ten}): cài thất bại — `{bac.lenh_cai}` → "
                      f"{ra.splitlines()[0][:80] if ra else f'thoát {rc}'}")
    return da_cai, no


def kiem_cau_hinh_lumen(duong=None):
    """-> danh sách lỗi cấu hình lumen. Rỗng nghĩa là cấu hình đủ để lumen chạy.

    Hai lỗi đã gặp thật, nên hai lỗi đó được kiểm: thiếu file, và thiếu khoá `backend` mà lumen
    từ chối thẳng bằng `config: servers[0]: backend is required`.
    """
    duong = duong or tdq_lsp.CONFIG_LUMEN
    if not os.path.isfile(duong):
        return [f"chưa có {duong} — lumen sẽ rơi về model mặc định, khác model của máy"]
    try:
        with io.open(duong, encoding="utf-8", errors="replace") as fh:
            noi_dung = fh.read()
    except OSError as exc:
        return [f"không đọc được {duong}: {exc}"]
    loi = []
    if "backend:" not in noi_dung:
        loi.append(f"{duong} thiếu khoá `backend` — lumen từ chối với "
                   "`config: servers[0]: backend is required`")
    if "model:" not in noi_dung:
        loi.append(f"{duong} thiếu khoá `model`")
    return loi


# Fallback when language detection finds nothing above its threshold (tiny or brand-new project):
# the common code extensions, so a one-file project still gets a real answer.
DUOI_MAC_DINH = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java",
                 ".cs", ".c", ".cc", ".cpp", ".h", ".hpp", ".rb", ".php", ".kt", ".swift")

# Line markers that look like a definition, per language key of `tdq_lsp.EXT_LANG`.
# Languages absent here accept any non-empty, non-comment line.
DAU_DINH_NGHIA = {
    "python": ("def ", "class "),
    "typescript": ("function ", "class ", "=>", "export "),
    "javascript": ("function ", "class ", "=>", "export "),
}
DAU_CHU_THICH = ("#", "//", "/*", "*", "--", ";", "<!--")


def _duoi_can_quet(project):
    """Extensions of the languages the project really uses, reusing rung 3/7's detector.

    Measured 2026-10-02: a hard-coded `*.py` made the floor report TRƯỢT on excalidraw
    (TypeScript only) while `git grep` answered instantly — a failure that did not exist.
    """
    ngon_ngu = set(tdq_lsp.do_ngon_ngu(project))
    duoi = tuple(sorted(d for d, l in tdq_lsp.EXT_LANG.items() if l in ngon_ngu))
    return duoi or DUOI_MAC_DINH


def _giong_dinh_nghia(dong, lang):
    """Does this line look like a definition for `lang`?"""
    dau = DAU_DINH_NGHIA.get(lang)
    if dau:
        return any(d in dong for d in dau)
    gon = dong.strip()
    return bool(gon) and not gon.startswith(DAU_CHU_THICH)


def smoke_grep(project):
    """Floor layer: find a definition that CERTAINLY exists in the project's own languages.

    Scans with Python itself instead of calling `grep`: Windows has no `grep` by default, and the
    floor must not depend on anything at all — that is why it is the floor.

    Stops at the FIRST matching file. The question is "can this layer answer", so reading all 505
    files (6.6 MB, 0.1 s warm cache) just to count a number nobody uses is wasted work.
    """
    duoi = _duoi_can_quet(project)
    for goc, thu_muc, tep in os.walk(project):
        thu_muc[:] = [t for t in thu_muc
                      if t not in tdq_lsp.SKIP_DIRS and not t.startswith(tdq_lsp.SKIP_PREFIX)]
        for ten in tep:
            phan_duoi = os.path.splitext(ten)[1]
            if phan_duoi not in duoi:
                continue
            lang = tdq_lsp.EXT_LANG.get(phan_duoi)
            try:
                with io.open(os.path.join(goc, ten), encoding="utf-8", errors="replace") as fh:
                    for dong in fh:
                        if _giong_dinh_nghia(dong, lang):
                            return True, f"tìm ra định nghĩa trong {ten}"
            except OSError:
                continue
    return False, "không quét ra file nào (" + ", ".join(duoi) + ")"


def _smoke(cmd, project, doi_ket_qua=False):
    """Một phép smoke -> (đạt?, mô tả). `doi_ket_qua` bắt công cụ phải trả về NỘI DUNG, không chỉ mã 0."""
    rc, ra = tdq_lsp._run(cmd, cwd=project, timeout=TIMEOUT_SMOKE)
    if rc != 0:
        return False, (ra.splitlines()[0][:80] if ra else f"thoát {rc}")
    if doi_ket_qua and not ra.strip():
        return False, "chạy được nhưng không trả về gì"
    return True, "trả lời được"


def smoke_lsp(project):
    """Tầng quan hệ: `agent-lsp doctor` khởi động thật từng language server đã cấu hình."""
    return _smoke(["agent-lsp", "doctor"], project)


def smoke_graphify(project):
    """Tầng bản đồ: hỏi các hub của đồ thị — rẻ nhất trong mọi câu hỏi graphify trả lời được."""
    return _smoke(["graphify", "god-nodes"], project, doi_ket_qua=True)


def smoke_bon_tang(project):
    """-> [(tên tầng, đạt?, chi tiết)] theo đúng thứ tự của luật tìm kiếm."""
    return [("grep", *smoke_grep(project)),
            ("LSP", *smoke_lsp(project)),
            ("graphify", *smoke_graphify(project)),
            ("lumen", *tdq_lsp._lumen_tra_loi_duoc(project))]


def va_hook_xung_dot():
    """-> (đã vá, nợ). Gỡ khối `PreToolUse` nhắm công cụ tìm kiếm khỏi hook của plugin ngoài.

    Vì sao phải sửa file của plugin khác: tài liệu Claude Code nói thẳng *"There is no way to
    disable an individual hook while keeping it in the configuration"* — chỉ có công tắc tổng
    `disableAllHooks`, thứ sẽ tắt luôn hook của chính workflow này. Nên đây là đường duy nhất.

    Ba giới hạn, để quyền này không nở ra: chỉ khối `PreToolUse`, chỉ matcher nhắm công cụ tìm
    kiếm, và luôn để lại một bản sao lưu. Khối `SessionStart` được giữ nguyên vì nó có ích thật.

    Phiên bản plugin nằm trong đường dẫn cache, nên một lần update là hook cũ sống lại ở thư mục
    mới. Đó là lý do lệnh này tồn tại thay vì sửa tay một lần: nó chạy lại được, mỗi lần setup.
    """
    da_va, no = [], []
    for ten, tep, _matcher in tdq_lsp.hook_xung_dot():
        du_lieu = tdq_lsp._doc_json(tep)
        khoi = (du_lieu.get("hooks") or {}).get("PreToolUse") or []
        giu = [m for m in khoi
               if not any(t in str(m.get("matcher", "")) for t in tdq_lsp.TOOL_TIM_KIEM)]
        if len(giu) == len(khoi):
            continue
        try:
            shutil.copyfile(tep, tep + DUOI_SAO_LUU)
            if giu:
                du_lieu["hooks"]["PreToolUse"] = giu
            else:
                du_lieu["hooks"].pop("PreToolUse", None)
            with io.open(tep, "w", encoding="utf-8") as fh:
                json.dump(du_lieu, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
        except OSError as exc:
            no.append(f"không vá được hook của plugin `{ten}` tại {tep}: {exc}")
            continue
        _log(f"vá hook plugin {ten}: gỡ {len(khoi) - len(giu)} khối PreToolUse")
        da_va.append(f"plugin `{ten}`: gỡ {len(khoi) - len(giu)} khối `PreToolUse` tại {tep}")
    return da_va, no


MOC_MO = "<!-- TDQ:TOOLS -->"
MOC_DONG = "<!-- /TDQ:TOOLS -->"

# Bản NGẮN NHẤT mà vẫn đủ để một agent chưa nạp skill nào biết dùng gì khi nào. Luật đầy đủ nằm ở
# `skills/tdq-setup/references/uu-tien-tim-kiem.md`; ở đây chỉ có thứ phải biết TRƯỚC khi nạp.
GOC_REPO = os.path.dirname(SCRIPTS_DIR)
# Chỗ giữ chỗ dùng cho BẢN MẪU trong repo. Bản mẫu là tài liệu chung, không được mang đường dẫn
# của máy người dựng nó; đường tuyệt đối chỉ đi vào file thật trên từng máy.
GOC_MAU = "<đường dẫn thư mục cài TDQ-Workflow>"

KHOI_HUONG_DAN = """## Bộ tìm kiếm 4 tầng

- Quan hệ, kiểu, diagnostics, đổi tên → `mcp__lsp__*`. Tên chính xác đã biết → grep.
  Khái niệm mơ hồ → lumen. Vỡ lan, bản đồ kiến trúc → graphify. Chưa chắc → gọi song song rồi gộp.
- Mỗi tầng có phụ thuộc riêng và chết trong im lặng; tầng nào chết thì rơi xuống grep.
- Kiểm cả 8 bậc và cài phần thiếu: `python3 {goc}/scripts/tdq_setup.py`.
  Luật đầy đủ kèm số đo: `{goc}/skills/tdq-setup/references/uu-tien-tim-kiem.md`."""


def khoi_huong_dan(goc=None):
    """Khối ghim, với đường dẫn TUYỆT ĐỐI của bản cài trên máy này.

    Hai bản trước đều sai: đường dẫn tương đối repo không mở được từ project khác, còn
    `${CLAUDE_PLUGIN_ROOT}` là biến của tầng hook/plugin và KHÔNG được expand trong `CLAUDE.md`
    — agent đọc được một chuỗi không trỏ tới đâu cả. Instruction user-level áp cho mọi repo trên
    máy, nên thứ duy nhất luôn đúng ở đó là đường dẫn tuyệt đối.
    """
    return KHOI_HUONG_DAN.format(goc=(goc or GOC_REPO).replace("\\", "/"))


def ghim_huong_dan_tool(duong, goc=None):
    """Ghim bản ngắn của luật 4 tầng vào instruction user-level, trong một khối có dấu mốc.

    Dấu mốc là thứ làm cho lệnh này chạy lại được: ghi lần hai THAY khối cũ thay vì nối thêm một
    khối nữa, và không bao giờ đụng vào phần user tự viết quanh nó. Đây là cách duy nhất còn lại —
    Claude Code không có cơ chế nào để một plugin ghi đè hay tắt một phần instruction của user.

    -> True khi file đổi nội dung, False khi đã đúng sẵn.
    """
    khoi = f"{MOC_MO}\n{khoi_huong_dan(goc)}\n{MOC_DONG}"
    cu = ""
    if os.path.isfile(duong):
        with io.open(duong, encoding="utf-8", errors="replace") as fh:
            cu = fh.read()
    if MOC_MO in cu and MOC_DONG in cu:
        truoc, con_lai = cu.split(MOC_MO, 1)
        _, sau = con_lai.split(MOC_DONG, 1)
        moi = truoc + khoi + sau
    else:
        moi = (cu.rstrip() + "\n\n" + khoi + "\n") if cu.strip() else khoi + "\n"
    if moi == cu:
        return False
    os.makedirs(os.path.dirname(os.path.abspath(duong)), exist_ok=True)
    with io.open(duong, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(moi)
    _log(f"ghim hướng dẫn 4 tầng vào {duong}")
    return True


def no_skill_khong_ton_tai(project):
    """-> nợ cho mỗi skill mà bản mẫu instruction bảo dùng nhưng máy này không có.

    Một dòng luật trỏ vào một skill không tồn tại thì tệ hơn là không có dòng nào: agent đọc nó,
    đi tìm, không thấy, rồi tự bịa ra cách làm. Đo được 2026-09-28: §9 của bản mẫu bảo dùng skill
    `mem0-memory`, thứ không có trên máy này.
    """
    ban_mau = os.path.join(project, "docs", "claude-md-mau.md")
    if not os.path.isfile(ban_mau):
        return []
    with io.open(ban_mau, encoding="utf-8", errors="replace") as fh:
        noi_dung = fh.read()
    goc = [os.path.join(project, "skills"), os.path.expanduser("~/.claude/skills")]
    no = []
    for ten in sorted(set(re.findall(r"skill `([a-z0-9][a-z0-9-]{2,})`", noi_dung))):
        if not any(os.path.isdir(os.path.join(g, ten)) for g in goc):
            no.append(f"bản mẫu instruction trỏ tới skill `{ten}` — máy này không có nó")
    return no


# --------------------------------------------------------------------------------------------
# Background bootstrap (`--nen`)
#
# A SessionStart hook cannot build the expensive layers itself: measured, `lumen index` on
# excalidraw took 11m5s (843 files, 29,796 chunks). So the hook only reads the readiness stamp
# and, when the project is not ready, spawns `tdq_setup.py --nen` detached. This block is that
# detached side. Contract shared with the hook and the search gate — do not rename:
#   stamp  docs/tdq/.tdq-san-sang.json  {"cap_nhat", "dang_dung", "pid", "tang": {layer: {...}}}
#   lock   docs/tdq/.tdq-khoi-tao.lock  the builder's pid as text
# --------------------------------------------------------------------------------------------

MOC_SAN_SANG = os.path.join("docs", "tdq", ".tdq-san-sang.json")
KHOA_KHOI_TAO = os.path.join("docs", "tdq", ".tdq-khoi-tao.lock")
# Overall cap of one background build. The measured worst case is the 11-minute lumen index of
# excalidraw; 30 minutes leaves room for installs + graphify on a slower machine, and is also the
# age after which a lock is stale even if its pid looks alive (pids get recycled).
TRAN_GIAY = 30 * 60
# Per-step caps, each further bounded by what is left of TRAN_GIAY.
TIMEOUT_GRAPHIFY_NEN = 10 * 60
TIMEOUT_LUMEN_NEN = 25 * 60
TANG_SAN_SANG = ("grep", "lsp", "graphify", "lumen")


def _tim_cong_cu(ten):
    """Path of an external tool on PATH, or None. One seam so tests never find real tools."""
    return shutil.which(ten)


def _duong_moc(project):
    return os.path.join(project, MOC_SAN_SANG)


def _duong_khoa(project):
    return os.path.join(project, KHOA_KHOI_TAO)


def doc_san_sang(project):
    """-> the readiness stamp as a dict, or None when it is missing, unreadable or corrupt."""
    try:
        with io.open(_duong_moc(project), encoding="utf-8") as fh:
            du_lieu = json.load(fh)
    except (OSError, ValueError):
        return None
    return du_lieu if isinstance(du_lieu, dict) else None


def ghi_san_sang(project, data):
    """Write the stamp atomically (temp file + os.replace) -> True when written.

    Atomic because the hook may read it at any moment while the builder rewrites it; a reader
    must see the old stamp or the new one, never half of one. Never raises: a stamp that cannot
    be written is logged, and the build goes on.
    """
    duong = _duong_moc(project)
    tam = f"{duong}.{os.getpid()}.tmp"
    try:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
        with io.open(tam, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(tam, duong)
        return True
    except OSError as exc:
        _log(f"nền: không ghi được mốc sẵn sàng {duong}: {exc}")
        try:
            os.remove(tam)
        except OSError:
            pass
        return False


def _pid_con_song(pid):
    """Is process `pid` alive? Cross-platform, never raises; unsure counts as alive.

    "Unsure -> alive" is the safe side: a wrongly kept lock still expires after TRAN_GIAY,
    while a wrongly stolen one means two builders indexing the same project.
    """
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if sys.platform.startswith("win"):
        return _pid_con_song_windows(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (OSError, OverflowError):
        return False
    return True


def _pid_con_song_windows(pid):
    """Windows liveness via OpenProcess + GetExitCodeProcess (os.kill(pid, 0) would KILL it)."""
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        if pid > 0xFFFFFFFF:
            return False
        process_query_limited_information = 0x1000
        still_active = 259
        handle = k32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            # Access denied means the process exists but belongs to someone else.
            return ctypes.get_last_error() == 5
        try:
            ma = wintypes.DWORD()
            if not k32.GetExitCodeProcess(handle, ctypes.byref(ma)):
                return True
            return ma.value == still_active
        finally:
            k32.CloseHandle(handle)
    except Exception:  # noqa: BLE001 — a liveness probe must never take the builder down
        return True


def _khoa_cu(duong):
    """Is the lock at `duong` stale: unreadable pid, dead pid, or older than TRAN_GIAY?"""
    try:
        with io.open(duong, encoding="utf-8", errors="replace") as fh:
            noi_dung = fh.read().strip()
        tuoi = datetime.now().timestamp() - os.path.getmtime(duong)
    except OSError:
        return True
    if tuoi > TRAN_GIAY:
        return True
    return not _pid_con_song(noi_dung)


def giu_khoa(project):
    """Take the build lock -> True when this process holds it now.

    O_CREAT|O_EXCL makes the take atomic: of two builders started together exactly one creates
    the file. A stale lock is removed and the take is retried once.
    """
    duong = _duong_khoa(project)
    try:
        os.makedirs(os.path.dirname(duong), exist_ok=True)
    except OSError as exc:
        _log(f"nền: không tạo được thư mục khoá: {exc}")
        return False
    for lan in range(2):
        try:
            fd = os.open(duong, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if lan == 0 and _khoa_cu(duong):
                _log(f"nền: khoá cũ tại {duong} — lấy lại")
                try:
                    os.remove(duong)
                except OSError:
                    return False
                continue
            return False
        except OSError as exc:
            _log(f"nền: không tạo được khoá {duong}: {exc}")
            return False
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(str(os.getpid()))
        return True
    return False


def nha_khoa(project):
    """Release the build lock — only if it is still ours. Never raises."""
    duong = _duong_khoa(project)
    try:
        with io.open(duong, encoding="utf-8", errors="replace") as fh:
            if fh.read().strip() != str(os.getpid()):
                return
        os.remove(duong)
    except OSError:
        pass


def _chay_mac_dinh(argv, cwd=None, timeout=None):
    """Default command runner of the background build: no shell, bounded, never raises."""
    return tdq_lsp._run(argv, cwd=cwd, timeout=timeout or TIMEOUT_CAI)


def _tang_tu_smoke(smoke):
    """[(layer, passed, detail)] -> the stamp's `tang` dict, always with the four keys."""
    tang = {ten: {"san_sang": False, "chi_tiet": "chưa kiểm"} for ten in TANG_SAN_SANG}
    for ten, dat, chi_tiet in smoke:
        khoa = str(ten).lower()
        if khoa in tang:
            tang[khoa] = {"san_sang": bool(dat), "chi_tiet": str(chi_tiet)}
    return tang


def khoi_tao_nen(project, chay=None):
    """The `--nen` body: build the expensive layers in the background, then write the stamp.

    Steps, each bounded and none able to stop the others: declared installs (`cai_thieu`),
    the Codex MCP declaration, `graphify extract`, `lumen index`, then the four-layer smoke.
    `chay(argv, cwd=None, timeout=None) -> (rc, output)` is the injectable runner.
    -> 0 always: a background process has nobody to report an exit code to; the stamp is the report.
    """
    chay = chay or _chay_mac_dinh
    if not giu_khoa(project):
        _log(f"nền: một tiến trình khác đang dựng {project} — thoát")
        return 0
    bat_dau = datetime.now().timestamp()

    def con_lai():
        return TRAN_GIAY - (datetime.now().timestamp() - bat_dau)

    def chay_an_toan(argv, cwd, tran):
        thoi_gian = min(tran, con_lai())
        if thoi_gian <= 0:
            _log(f"nền: hết trần {TRAN_GIAY}s — bỏ {argv[0]}")
            return 1, "hết trần thời gian"
        _log(f"nền: chạy {' '.join(str(a) for a in argv)}")
        try:
            return chay(argv, cwd=cwd, timeout=thoi_gian)
        except Exception as exc:  # noqa: BLE001 — one step must never stop the next
            return 1, f"{type(exc).__name__}: {exc}"

    def buoc(ten, ham):
        if con_lai() <= 0:
            _log(f"nền: hết trần {TRAN_GIAY}s — bỏ bước {ten}")
            return
        try:
            ham()
        except Exception as exc:  # noqa: BLE001 — same contract as chay_an_toan
            _log(f"nền: bước {ten} lỗi: {type(exc).__name__}: {exc}")

    try:
        try:
            grep = [("grep", *smoke_grep(project))]
        except Exception as exc:  # noqa: BLE001
            grep = [("grep", False, f"{type(exc).__name__}: {exc}")]
        tang = _tang_tu_smoke(grep)
        for ten in TANG_SAN_SANG[1:]:
            tang[ten]["chi_tiet"] = "đang dựng nền"
        ghi_san_sang(project, {"cap_nhat": _now(), "dang_dung": True, "pid": os.getpid(),
                               "tang": tang})

        def cai():
            def chay_lenh(lenh):
                try:
                    argv = shlex.split(lenh)
                except ValueError as exc:
                    return 1, f"không tách được lệnh: {exc}"
                return chay_an_toan(argv, None, TIMEOUT_CAI)
            da_cai, no = cai_thieu(tdq_lsp.chay_kiem(project), chay_lenh=chay_lenh)
            for dong in da_cai:
                _log(f"nền: đã cài · {dong}")
            if no:
                tdq_no.ghi_no(no, project)

        def codex():
            if not _tim_cong_cu("codex"):
                _log("nền: không thấy codex — bỏ khai MCP cho Codex")
                return
            import tdq_codex_mcp
            for dong in tdq_codex_mcp.khai_mcp_codex():
                _log(f"nền: codex · {dong}")

        def graphify():
            if not _tim_cong_cu("graphify"):
                _log("nền: không thấy graphify — bỏ dựng đồ thị")
                return
            rc, ra = chay_an_toan(["graphify", "extract", ".", "--code-only"], project,
                                  TIMEOUT_GRAPHIFY_NEN)
            _log(f"nền: graphify → {'xong' if rc == 0 else 'hỏng: ' + ra[-120:]}")

        def lumen():
            # Same guards as tdq_finish.step_reindex: no binary or no embedder -> skip.
            binary = tdq_lsp._binary_lumen()
            if not binary:
                _log("nền: không thấy lumen — bỏ index")
                return
            if not tdq_lsp._ollama_dang_chay():
                _log("nền: ollama chưa chạy — bỏ index lumen")
                return
            rc, ra = chay_an_toan([binary, "index", project], project, TIMEOUT_LUMEN_NEN)
            if rc != 0:
                _log(f"nền: lumen index hỏng: {ra[-120:]}")
                return
            tdq_no.cham_dau_moc(os.path.join(project, tdq_lsp.DAU_MOC_INDEX))
            _log("nền: lumen index xong")

        for ten, ham in (("cài", cai), ("codex", codex), ("graphify", graphify),
                         ("lumen", lumen)):
            buoc(ten, ham)

        smoke = []

        def kiem():
            smoke.extend(tdq_lsp.chay_smoke(project))

        buoc("smoke", kiem)
        if smoke:
            tang = _tang_tu_smoke(smoke)
        else:
            for ten in TANG_SAN_SANG[1:]:
                tang[ten] = {"san_sang": False, "chi_tiet": "không chạy được smoke"}
        ghi_san_sang(project, {"cap_nhat": _now(), "dang_dung": False, "pid": None,
                               "tang": tang})
        _log("nền: xong · " + ", ".join(
            f"{t}={'ĐẠT' if tang[t]['san_sang'] else 'TRƯỢT'}" for t in TANG_SAN_SANG))
    finally:
        nha_khoa(project)
    return 0


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Cài và chứng minh mọi phụ thuộc của bộ tìm kiếm 4 tầng.")
    ap.add_argument("--khong-log", action="store_true", help="tắt log ra stderr")
    ap.add_argument("--nen", action="store_true",
                    help="dựng nền phần đắt (cài, graphify, lumen) rồi ghi mốc sẵn sàng")
    return ap.parse_args(argv)


def _khai_codex_mac_dinh():
    """The CLI's Codex step: declare the lumen + lsp MCP servers. -> result lines."""
    import tdq_codex_mcp
    return tdq_codex_mcp.khai_mcp_codex()


def chay_cli(argv):
    """The command line entry: `main` WITH the Codex MCP declaration turned on.

    Why `main` does not do it by default: `codex mcp add` writes the user's real
    `~/.codex/config.toml`, and in-process callers of `main` (the existing tests) must never do
    that. Typing the command is the consent, exactly as for the installs.
    """
    return main(argv, khai_codex=_khai_codex_mac_dinh)


def main(argv, khai_codex=None):
    args = parse_args(argv)
    if args.khong_log:
        # Một biến, hai module. Thang bậc có log riêng, nên nếu `--khong-log` chỉ tắt cờ của
        # chính file này thì user gõ nó vẫn nghe một nửa tiếng ồn.
        os.environ["TDQ_LOG"] = "0"
    project = tdq_lsp._project_dir()
    if args.nen:
        khoi_tao_nen(project)
        return 0
    _log(f"setup · project={project} · máy={platform.node()}")

    bac = tdq_lsp.chay_kiem(project)
    da_cai, no = cai_thieu(bac)
    da_va, no_hook = va_hook_xung_dot()
    da_cai += da_va
    no += no_hook + kiem_cau_hinh_lumen() + no_skill_khong_ton_tai(project)
    if ghim_huong_dan_tool(os.path.expanduser(DUONG_INSTRUCTION)):
        da_cai.append(f"ghim hướng dẫn 4 tầng vào {DUONG_INSTRUCTION}")

    for dong in da_cai:
        print(f"đã cài · {dong}")
    if khai_codex:
        try:
            for dong in khai_codex():
                print(f"codex · {dong}")
        except Exception as exc:  # noqa: BLE001 — Codex is optional; setup goes on without it
            no.append(f"không khai được MCP cho Codex: {type(exc).__name__}: {exc}")
    print("")

    # The very same check `tdq_lsp.py check` runs — re-run after installing, so the ladder and
    # the smoke report the machine as it is now, under one total line.
    rc, _bac, smoke = tdq_lsp.kiem_mot_lenh(project)
    no += [f"tầng {ten} không trả lời được: {chi_tiet}" for ten, dat, chi_tiet in smoke if not dat]

    for dong in no:
        print(f"nợ · {dong}")
    so = tdq_no.ghi_no(no, project)
    print("")
    print(f"Nợ: {len(no)} món ({so} dòng mới) → {tdq_no.FILE_NO}")
    return rc


if __name__ == "__main__":
    sys.exit(chay_cli(sys.argv[1:]))
