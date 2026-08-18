#!/usr/bin/env python3
"""skill_tokens.py — đo token THẬT của bộ skill, không ước lượng ký tự chia bốn.

Vì sao cần script riêng dù đã có `context_surface.py`: file kia dùng hệ số
`BYTES_PER_TOKEN = 4` cho mọi file. Hệ số đó đúng với tiếng Anh, hụt nặng với
tiếng Việt có dấu (đo thật: 1,89 ký tự/token so với 4,68 của tiếng Anh). Mà chỗ
cần đo chính xác nhất lại là văn bản tiếng Việt. Script này đếm bằng tokenizer
thật nên hai bảng có thể lệch nhau — con số ở ĐÂY mới là con số dùng để quyết định.

Hai lệnh:
    python3 scripts/skill_tokens.py --theo-phase   # token thân skill nạp theo phase
    python3 scripts/skill_tokens.py --mo-ta        # token MÔ TẢ của skill đang bật

Hai lệnh đo hai KHỐI KHÁC NHAU, không cộng dồn lẫn lộn:
  * `--theo-phase` đo **thân** skill — chỉ vào context khi gọi đúng skill đó.
  * `--mo-ta` đo **mô tả** skill — nằm trong system prompt của MỌI lượt gọi API.

Thư viện đếm token: `anthropic-tokenizer`, cài trong venv riêng `.venv-tokens/`.
Thiếu thư viện thì script LỖI, tuyệt đối không rơi về ước lượng ký tự/4 — spec §4
cấm đoán số token. Chạy bằng `python3` hệ thống vẫn được: script tự nhảy sang
python của venv nếu tìm thấy.

Log service: timestamp ISO ra stderr, bật mặc định, tắt bằng `TDQ_LOG=0`.
Bảng luôn ra stdout để pipe được.
Exit: 0 chạy xong · 2 sai cú pháp · 3 thiếu thư viện đếm token.
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402 — dùng chung log service (log_enabled, timestamp)
import context_surface  # noqa: E402 — dùng chung _read / _split_frontmatter
import skill_inventory  # noqa: E402 — dùng chung danh sách skill ĐANG BẬT

# Cho phép trỏ sang python khác qua biến môi trường: test cần dựng cảnh "không có venv"
# mà không được đụng vào venv thật của repo.
VENV_PYTHON = os.environ.get(
    "TDQ_TOKENS_VENV", os.path.join(ROOT, ".venv-tokens", "bin", "python"))
CAI_DAT = (f"python3 -m venv {os.path.relpath(os.path.join(ROOT, '.venv-tokens'), ROOT)} "
           "&& .venv-tokens/bin/pip install anthropic-tokenizer==0.1.0")
EXIT_THIEU_THU_VIEN = 3

# Sáu khối phase. Mỗi khối = những file THÂN skill vào context khi phase đó chạy.
# Thứ tự trong tuple là thứ tự in bảng; giữ nguyên để so sánh giữa các lần đo.
KHOI_PHASE = (
    ("luôn nạp", ("tdq-conventions",)),
    ("intake", ("tdq-intake",)),
    ("spec", ("tdq-spec",)),
    ("plan", ("tdq-plan",)),
    ("build", ("tdq-build",)),
)
KHOI_LUAT_KEM = "luật kèm (mọi reference)"

# Phân mục cho `--mo-ta`. Khớp theo tên nguồn (`plugin:<x>` hoặc `user`/`project`).
# Một nguồn chỉ thuộc ĐÚNG một mục — mục đầu tiên khớp thắng, nên thứ tự có nghĩa.
MUC = (
    ("workflow", ("tdq-workflow", "superpowers", "claude-md-management",
                  "remember", "hookify")),
    ("code", ("plugin-dev", "mcp-server-dev", "skill-creator", "sonarqube",
              "code-simplifier", "feature-dev", "lumen", "playground")),
    ("design", ("figma", "canva", "adobe-for-creativity", "frontend-design")),
    ("game engine", ("unity", "unreal", "qt-development-skills")),
    ("web", ("playwright", "chrome-devtools-mcp", "firecrawl", "tavily",
             "cloudflare", "base44", "postman", "hyperframes")),
    ("dữ liệu", ("data-engineering", "mongodb", "redis-development",
                 "datarobot-agent-skills", "huggingface-skills")),
)
MUC_KHAC = "khác"


def _log(msg):
    """Dòng log ra stderr kèm timestamp. Tắt bằng TDQ_LOG=0 — cùng hợp đồng tdq_state."""
    if tdq_state.log_enabled():
        print(f"[{tdq_state.now_iso()}] {msg}", file=sys.stderr)


class ThieuThuVienDem(Exception):
    """Không có tokenizer thật. Ném ra thay vì đoán — spec §4 cấm ước lượng ký tự/4."""


def nap_bo_dem():
    """Trả hàm đếm token thật, hoặc ném `ThieuThuVienDem`.

    Hàm này thuần: KHÔNG thoát tiến trình, KHÔNG `execv`. Gọi từ test hay từ script
    khác đều an toàn. Việc nhảy sang python của venv là chuyện của lớp CLI
    (`nhay_sang_venv`), vì nó thay luôn tiến trình đang chạy — làm trong hàm thư
    viện thì nó nuốt mất cả test runner (đo thật: pytest bị thay tiến trình, thoát 2).
    """
    try:
        from anthropic_tokenizer import count_tokens
        return count_tokens
    except ImportError as exc:
        raise ThieuThuVienDem(CAI_DAT) from exc


def nhay_sang_venv():
    """Chạy lại chính script bằng python của venv. Nhảy đúng một lần rồi thôi."""
    if os.environ.get("TDQ_TOKENS_DA_NHAY") == "1" or not os.path.exists(VENV_PYTHON):
        return False
    _log(f"thiếu thư viện ở python hiện tại — nhảy sang {os.path.relpath(VENV_PYTHON, ROOT)}")
    os.environ["TDQ_TOKENS_DA_NHAY"] = "1"
    os.execv(VENV_PYTHON, [VENV_PYTHON, os.path.abspath(__file__)] + sys.argv[1:])


def nap_bo_dem_cho_cli():
    """Bộ đếm cho lớp CLI: thử python hiện tại → thử venv → thoát mã 3 kèm cách cài."""
    try:
        return nap_bo_dem()
    except ThieuThuVienDem:
        pass
    nhay_sang_venv()
    print("skill_tokens.py: thiếu thư viện đếm token `anthropic-tokenizer`.\n"
          "Script này CẤM ước lượng ký tự/4 (spec §4), nên dừng ở đây.\n"
          f"Cài bằng: {CAI_DAT}", file=sys.stderr)
    sys.exit(EXIT_THIEU_THU_VIEN)


def _chu(raw):
    """Bytes → chuỗi. `context_surface` đọc bytes để đo kích thước; tokenizer cần chữ."""
    return raw.decode("utf-8", errors="replace")


def _than_skill(ten_skill):
    """Token thân của một SKILL.md (đã bỏ frontmatter) + đường dẫn, hoặc None."""
    path = os.path.join(ROOT, "skills", ten_skill, "SKILL.md")
    if not os.path.exists(path):
        return None
    _, body = context_surface._split_frontmatter(context_surface._read(path))
    return _chu(body)


def _references(ten_skill):
    """Mọi file reference của một skill — tầng `đọc khi cần`, gộp vào khối luật kèm."""
    return sorted(glob.glob(os.path.join(ROOT, "skills", ten_skill, "references", "*.md")))


def do_theo_phase(dem):
    """Bảng token theo 6 khối phase. Trả về list dòng [tên khối, số file, token]."""
    rows = []
    for ten_khoi, skills in KHOI_PHASE:
        tong, so_file = 0, 0
        for skill in skills:
            body = _than_skill(skill)
            if body is None:
                _log(f"cảnh báo: không thấy skills/{skill}/SKILL.md — bỏ qua")
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
    _log(f"đo xong {len(rows)} khối phase")
    return rows


def phan_muc(nguon):
    """Tên mục của một nguồn skill. Không khớp mục nào → `khác`."""
    goc = nguon.split(":", 1)[-1]
    for ten_muc, khoa in MUC:
        if any(k in goc for k in khoa):
            return ten_muc
    return MUC_KHAC


# `[\w-]+:` chứ không phải `\w+:` — khoá frontmatter có gạch ngang (`argument-hint`,
# `allowed-tools`). Dùng `\w+:` thì mô tả nuốt luôn mấy dòng đó, thổi phồng số token
# và làm nhiễu cả router (đo thật: `sonar-analyze` nuốt cả danh sách allowed-tools).
DESC_RE = re.compile(r"^description:\s*(.*(?:\n(?![\w-]+:|---).*)*)", re.M)


TEN_KHAI_RE = re.compile(r"^name:\s*(.+?)\s*$", re.M)


def ban_do_skill_md():
    """Quét MỘT LẦN mọi SKILL.md trên đĩa → {khoá tra: [đường dẫn]}.

    Quét lại cho từng skill thì 284 lượt glob đệ quy trên `~/.claude` mất hơn hai
    phút (đo thật, phải giết tiến trình). Quét một lần rồi tra bảng: dưới một giây.

    Mỗi file vào bảng dưới HAI khoá: tên thư mục, và tên KHAI trong frontmatter.
    Hai tên này lệch nhau thường xuyên hơn tưởng — `canva-brand-check` nằm ở thư mục
    `brand-check/`, `unity-mcp-orchestrator` nằm ở `unity-mcp-skill/`. Chỉ tra theo
    tên thư mục thì 10/284 skill không dò ra file, và cái giá không phải là thiếu một
    dòng log: mọi tầng "giấu mô tả rồi đọc thẳng SKILL.md khi cần" đều mù với đúng 10
    skill đó.
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
    _log(f"bản đồ SKILL.md: {len(ban_do)} khoá tra")
    return ban_do


def khoa_tra(ten_skill):
    """Tên skill → khoá tra bảng. Gỡ tiền tố plugin và dấu nháy dính từ frontmatter.

    Dấu nháy là lỗi dữ liệu có thật: một skill khai `name: "adobe-batch-edit-photos"`
    kèm nháy kép, và tên mang nháy thì không khớp khoá nào.
    """
    return ten_skill.split(":")[-1].strip().strip('"').strip("'")


def _mo_ta_day_du(ten_skill, mac_dinh, ban_do):
    """Mô tả ĐẦY ĐỦ đọc thẳng từ SKILL.md. Không tìm được file → dùng bản rút gọn.

    `skill_inventory` rút gọn mô tả cho vừa bảng kiểm kê; đo token thì phải lấy bản
    đầy đủ, vì bản đầy đủ mới là thứ thật sự nằm trong system prompt.
    """
    for path in ban_do.get(khoa_tra(ten_skill), []):
        m = DESC_RE.search(_chu(context_surface._read(path))[:4000])
        if m and m.group(1).strip():
            return m.group(1).strip()
    return mac_dinh


def do_mo_ta(dem, project=ROOT):
    """Bảng token mô tả của skill ĐANG BẬT, kèm nguồn và mục.

    Trả về (rows, tong_skill). Mỗi dòng: [nguồn, mục, số skill, token mô tả, token tên].
    """
    hang = skill_inventory.inventory(project)
    ban_do = ban_do_skill_md()
    gop = {}
    for ten, mo_ta_ngan, nguon in hang:
        day_du = _mo_ta_day_du(ten, mo_ta_ngan, ban_do)
        khoa = (nguon, phan_muc(nguon))
        o = gop.setdefault(khoa, [0, 0, 0])
        o[0] += 1
        # +6: chi phí khung mỗi mục trong danh sách skill (xuống dòng, dấu phân cách).
        o[1] += dem(day_du) + dem(ten) + 6
        o[2] += dem(ten) + 6
    rows = [[nguon, muc, n, tok, ten_tok]
            for (nguon, muc), (n, tok, ten_tok) in
            sorted(gop.items(), key=lambda kv: -kv[1][1])]
    _log(f"đo xong mô tả của {len(hang)} skill đang bật, {len(rows)} nhóm nguồn")
    return rows, len(hang)


def _in_bang(headers, rows):
    """In bảng markdown ra stdout — pipe được, dán thẳng vào báo cáo được."""
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        print("| " + " | ".join(f"{c:,}".replace(",", ".") if isinstance(c, int)
                                else str(c) for c in row) + " |")


def lenh_theo_phase(dem):
    rows = do_theo_phase(dem)
    _in_bang(("khối phase", "số file", "token"), rows)
    tong = sum(r[2] for r in rows)
    print(f"\nTRẦN TRÊN cho một request lane full: "
          f"{tong:,}".replace(",", ".") + " token")
    print("Đây là TRẦN, không phải số thật của một request: khối `luật kèm` gộp MỌI file\n"
          "reference, còn một request chỉ mở những reference mà thân skill trỏ tới.\n"
          "Con số dùng để so trước/sau phải là cùng một cách đo này, không trộn hai cách.")
    return 0


def lenh_mo_ta(dem, project):
    rows, tong_skill = do_mo_ta(dem, project)
    _in_bang(("nguồn", "mục", "số skill", "token mô tả", "token nếu chỉ giữ tên"), rows)
    tong_tok = sum(r[3] for r in rows)
    tong_ten = sum(r[4] for r in rows)
    print(f"\nTổng: {tong_skill} skill đang bật · "
          f"{tong_tok:,}".replace(",", ".") + " token mô tả · "
          f"{tong_ten:,}".replace(",", ".") + " token nếu chỉ giữ tên")
    theo_muc = {}
    for nguon, muc, n, tok, ten_tok in rows:
        o = theo_muc.setdefault(muc, [0, 0])
        o[0] += n
        o[1] += tok
    print()
    _in_bang(("mục", "số skill", "token mô tả"),
             [[muc, n, tok] for muc, (n, tok) in
              sorted(theo_muc.items(), key=lambda kv: -kv[1][1])])
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="skill_tokens.py",
        description="Đo token thật của bộ skill (thân theo phase, và mô tả theo mục).")
    parser.add_argument("--theo-phase", action="store_true", dest="theo_phase",
                        help="bảng token thân skill theo 6 khối phase")
    parser.add_argument("--mo-ta", action="store_true", dest="mo_ta",
                        help="bảng token mô tả của skill đang bật, theo nguồn và mục")
    parser.add_argument("--project", default=ROOT,
                        help="thư mục project để kiểm kê skill (mặc định: gốc repo)")
    args = parser.parse_args(argv)

    if args.theo_phase == args.mo_ta:
        parser.error("chọn đúng một trong hai: --theo-phase hoặc --mo-ta")

    lenh = "--theo-phase" if args.theo_phase else "--mo-ta"
    _log(f"skill_tokens · {lenh}")
    dem = nap_bo_dem_cho_cli()
    if args.theo_phase:
        return lenh_theo_phase(dem)
    return lenh_mo_ta(dem, args.project)


if __name__ == "__main__":
    sys.exit(main())
