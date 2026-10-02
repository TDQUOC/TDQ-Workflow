#!/usr/bin/env python3
"""Install and prove every dependency the workflow searches with (stdlib only).

One command, four jobs, in this order:
  1. run the ladder of `tdq_lsp.py` and INSTALL what is missing and allowed
  2. check the configuration each layer needs is actually right
  3. ask each of the four search layers one real question and read the answer
  4. write down, as debt, everything it could not fix by itself

Why this file exists next to `tdq_lsp.py` instead of inside it: `tdq_lsp.py` carries a hard
promise — it NEVER installs, it only diagnoses and prints the command. That promise is what
makes it safe to run on every request at intake. This script is the opposite half: the user
types it, and typing it IS the consent to install. Keeping the two promises in two files is
what keeps each one readable.

The consent is not unlimited. A command only runs when it matches the declared allow-list
below; anything else becomes a line of debt, never a silent skip and never a guess.

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


def cai_thieu(bac_list):
    """-> (đã cài, nợ). Cài mọi bậc còn thiếu mà lệnh của nó nằm trong danh sách đã khai."""
    da_cai, no = [], []
    for bac in bac_list:
        if bac.dat or not bac.lenh_cai:
            continue
        duoc, ly_do = _duoc_cai(bac.lenh_cai)
        if not duoc:
            no.append(f"bậc {bac.so} ({bac.ten}): {ly_do} — `{bac.lenh_cai}`")
            continue
        rc, ra = _chay_lenh(bac.lenh_cai)
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


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Cài và chứng minh mọi phụ thuộc của bộ tìm kiếm 4 tầng.")
    ap.add_argument("--khong-log", action="store_true", help="tắt log ra stderr")
    return ap.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    if args.khong_log:
        # Một biến, hai module. Thang bậc có log riêng, nên nếu `--khong-log` chỉ tắt cờ của
        # chính file này thì user gõ nó vẫn nghe một nửa tiếng ồn.
        os.environ["TDQ_LOG"] = "0"
    project = tdq_lsp._project_dir()
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

    print("\nSmoke test bốn tầng:")
    for ten, dat, chi_tiet in smoke_bon_tang(project):
        print(f"  {ten:<9} {'ĐẠT ' if dat else 'TRƯỢT'} · {chi_tiet}")
        if not dat:
            no.append(f"tầng {ten} không trả lời được: {chi_tiet}")

    for dong in no:
        print(f"nợ · {dong}")
    so = tdq_no.ghi_no(no, project)
    print("")
    print(f"Nợ: {len(no)} món ({so} dòng mới) → {tdq_no.FILE_NO}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
