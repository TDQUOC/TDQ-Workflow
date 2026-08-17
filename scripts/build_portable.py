#!/usr/bin/env python3
"""build_portable.py — sinh hai bản portable của bộ TDQ Workflow từ MỘT nguồn.

Vì sao có file này: bản `portable/` trước đây viết tay, README của nó ghi thẳng "Không tự
sinh — sửa `skills/` xong nhớ đồng bộ tay", và test khoá đồng bộ đã bị xoá từ 0.10.0. Bản
viết tay luôn mục theo thời gian. Sinh bằng máy là cách duy nhất giữ bản portable đúng.

Hai đích, cùng một nguồn (`skills/`, `hooks/`, `agents/`, `scripts/`):

    portable_claude/  — cho Claude Code: `.claude/skills`, `.claude/agents`,
                        `.claude/settings.json` (hook), `.mcp.json`, `scripts/`.
                        Mọi `${CLAUDE_PLUGIN_ROOT}` được đổi thành `${CLAUDE_PROJECT_DIR}`
                        vì biến kia CHỈ tồn tại khi chạy như plugin đã đăng ký.
    portable_codex/   — cho Codex CLI >= 0.147.0, dùng đúng ba lớp native của nó:
                        `.agents/skills/`, `.codex/config.toml` (MCP), `.codex/hooks.json`
                        + `hooks/`. Kèm `AGENTS.md` + `workflow/NN-*.md` làm bản dự phòng
                        cho harness KHÁC (Antigravity…) chỉ đọc được markdown.

Cả hai mang theo `manifest.json` (file+sha256, version, python tối thiểu, lệnh ngoài, MCP)
để `tdq_checkportable.py` ở máy đích tự kiểm và tự vá.

Dùng:
    python3 scripts/build_portable.py                    # sinh cả hai vào repo root
    python3 scripts/build_portable.py --dest /tmp/x      # sinh vào thư mục khác
    python3 scripts/build_portable.py --only claude      # chỉ một bản

Env: TDQ_LOG=0 tắt log tiến trình (log ra stderr).
Exit: 0 xong · 1 lỗi sinh · 2 sai cú pháp.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_export import plugin_version, sha256_of  # noqa: E402
# Logic sinh hai file cấu hình sống ở `tdq_checkportable.py` chứ không ở đây: chỉ file đó đi
# theo bundle, nên máy đích mới dựng lại được chúng. Import ngược để giữ đúng một bản logic.
from tdq_checkportable import sinh_mcp, sinh_settings  # noqa: E402

EXIT_LOI = 1
EXIT_SYNTAX = 2

# Thư mục nguồn được mang sang bản portable. `tests/` cố tình KHÔNG có: bản portable là để
# chạy workflow ở project người khác, không phải để chạy test của repo này.
SOURCE_DIRS = ("skills", "hooks", "agents", "scripts")

# Rác không bao giờ được lọt vào bản sinh. `docs/tdq` đứng đầu danh sách vì nó chứa state,
# brief, spec, plan của CHÍNH repo nguồn — lộ sang máy người khác là rò dữ liệu nội bộ.
EXCLUDE_DIRS = frozenset({
    ".git", "docs", "graphify-out", "__pycache__", ".pytest_cache", ".venv",
    "tests", "node_modules", ".remember", "ClaudeExport", "claude-export",
    "portable", "portable_claude", "portable_codex",
})
EXCLUDE_FILES = frozenset({
    ".DS_Store", "state.json", ".tdq-turn.jsonl",
    # Chính bộ sinh không đi theo bản sinh: nó chỉ có nghĩa trong repo nguồn, và nội dung nó
    # nhắc tên biến plugin nguyên văn nên copy kèm rewrite sẽ hỏng đúng hằng số của nó.
    "build_portable.py",
})

MANIFEST_NAME = "manifest.json"
PYTHON_MIN = "3.8"
EXTERNAL_COMMANDS = ("git", "graphify")
MCP_SERVERS = ("tavily-primary", "tavily-backup")

BIEN_CU = "CLAUDE_PLUGIN_ROOT"
BIEN_MOI = "CLAUDE_PROJECT_DIR"


# ----------------------------------------------------------------- log service

def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def log(message):
    """Log tiến trình ra stderr kèm timestamp. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


# ------------------------------------------------------------------ đổi biến

def doi_bien_plugin_root(text, thay_bang=None):
    """`${CLAUDE_PLUGIN_ROOT}` và `$CLAUDE_PLUGIN_ROOT` → `${CLAUDE_PROJECT_DIR}`.

    `thay_bang` cho phép gắn thêm hậu tố đường dẫn. Bản claude cần điều đó: gốc bộ workflow
    nằm ở `.claude/tdq/` chứ không phải gốc project, nên thay trần bằng `${CLAUDE_PROJECT_DIR}`
    sẽ tạo ra đường dẫn trỏ hụt một tầng — lệnh gọi script im lặng không tìm thấy file.

    Trả `(văn bản mới, số lần thay)`. Số lần thay là thứ đáng giá hơn cả kết quả: grep bản
    sinh thấy 0 chuỗi chỉ chứng minh "không còn trong file ĐÃ COPY", còn đối chiếu số lần
    thay với số chỗ đếm ở nguồn mới bắt được trường hợp một file đáng lẽ phải copy mà bị bỏ
    sót. Hook gãy vì biến rỗng là lỗi im lặng — không có cách nào phát hiện ở máy người khác.
    """
    dang_ngoac = "${" + BIEN_CU + "}"
    dang_tran = "$" + BIEN_CU
    moi = thay_bang or ("${" + BIEN_MOI + "}")
    so_lan = text.count(dang_ngoac)
    text = text.replace(dang_ngoac, moi)
    # Sau khi thay dạng ngoặc, phần còn lại mang dấu `$` trần mới là dạng trần thật.
    so_lan += text.count(dang_tran)
    text = text.replace(dang_tran, moi)
    return text, so_lan


def dem_bien_trong_cay(goc):
    """Đếm tổng số chỗ dùng biến plugin trong một cây thư mục — mốc đối chiếu cho QC."""
    tong = 0
    for thu_muc, _, files in os.walk(goc):
        for ten in files:
            noi_dung = _doc_text(os.path.join(thu_muc, ten))
            if noi_dung is not None:
                tong += noi_dung.count(BIEN_CU)
    return tong


# --------------------------------------------------------------------- copy

def _bo_qua_thu_muc(ten):
    return ten in EXCLUDE_DIRS


def _bo_qua_file(ten):
    return ten in EXCLUDE_FILES or ten.endswith((".pyc", ".pyo"))


def _doc_text(path):
    """Đọc file dạng text; trả None nếu là nhị phân (không đụng vào để khỏi hỏng)."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None


def copy_loc(nguon, dich, doi_bien=False, thay_bang=None):
    """Copy cây thư mục theo bộ lọc, giữ quyền thực thi. Trả số lần đổi biến đã làm.

    `doi_bien=True` chỉ dùng cho bản claude: file text được rewrite khi ghi, file nhị phân
    copy nguyên. Giữ quyền thực thi là bắt buộc — mất bit `x` thì hook không chạy được.
    """
    so_lan_doi = 0
    for thu_muc, thu_muc_con, files in os.walk(nguon):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        tuong_doi = os.path.relpath(thu_muc, nguon)
        dich_hien_tai = dich if tuong_doi == "." else os.path.join(dich, tuong_doi)
        os.makedirs(dich_hien_tai, exist_ok=True)
        for ten in files:
            if _bo_qua_file(ten):
                continue
            src = os.path.join(thu_muc, ten)
            dst = os.path.join(dich_hien_tai, ten)
            noi_dung = _doc_text(src) if doi_bien else None
            if noi_dung is None:
                shutil.copy2(src, dst)
            else:
                noi_dung, lan = doi_bien_plugin_root(noi_dung, thay_bang)
                so_lan_doi += lan
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(noi_dung)
                shutil.copystat(src, dst)
    return so_lan_doi


# ------------------------------------------------------------- bản claude

# Gốc bộ workflow trong project đích. KHÔNG đổ thẳng vào `.claude/`: `hooks/scripts/_common.py`
# tìm thư mục `scripts/` bằng `../../scripts` tính từ chính nó, nên `hooks/` và `scripts/` bắt
# buộc nằm cạnh nhau dưới một gốc chung; còn `skills/` và `agents/` thì ngược lại, Claude Code
# chỉ quét đúng `.claude/skills` và `.claude/agents`. Một thư mục riêng thoả được cả hai.
GOC_TDQ = ".claude/tdq"

# Skill chỉ có nghĩa ở MÁY ĐÍCH (`tdq-checkportable`) sống ở đây chứ không ở `skills/`: đặt
# trong `skills/` là bắt bộ chính gánh thêm một description trong ngân sách context của mọi
# phiên, cho một skill mà repo này không bao giờ chạy.
PORTABLE_SRC = "portable_src"
TEN_BAN_CLAUDE = "portable_claude"

README_CLAUDE = """# TDQ Workflow — bản portable cho Claude Code

## Cài ở máy mới — làm theo đúng thứ tự này

1. **Chép** trọn nội dung thư mục này vào gốc project của bạn, giữ nguyên `.claude/` và
   `.mcp.json`.
2. **Kiểm** trước khi mở Claude Code:
   ```
   python3 .claude/tdq/scripts/tdq_checkportable.py check
   ```
   Đọc theo tiền tố: `SẠCH` xong · `THIẾU` chưa có · `LỆCH` khác manifest · `LƯU Ý` việc
   chỉ bạn làm được.
3. **Vá** nếu có `THIẾU`/`LỆCH`: `python3 .claude/tdq/scripts/tdq_checkportable.py setup` (xem mục
   cảnh báo bên dưới — nó chỉ dựng lại được hai file).
4. **Đặt biến môi trường** cho MCP nếu `check` báo thiếu. Script cố ý KHÔNG làm hộ và
   không bao giờ in giá trị khoá — chỉ báo tên biến.
5. **Mở Claude Code** trong project đó. Lần mở đầu nó hỏi có tin thư mục này không →
   **bấm đồng ý**. Không đồng ý thì hook và cấu hình project không có hiệu lực.
6. **Khởi động lại phiên** để skill và agent trong thư mục mới được quét.
7. **Duyệt MCP server** — mỗi server trong `.mcp.json` cần bạn duyệt một lần.

Xong bảy bước thì nhắn `chạy skill tdq-checkportable` để máy tự kiểm lại lần cuối.

## Ba việc máy KHÔNG tự làm được

1. **Tin cậy thư mục** — bước 5 ở trên. Chỉ bạn bấm được, không có cờ dòng lệnh nào trong
   bộ này thay thế.
2. **Duyệt MCP server** — bước 7.
3. **Khởi động lại** — bước 6. Bỏ qua thì skill mới nằm im, không báo lỗi gì.

## Cảnh báo về tự vá

`setup` dựng lại được đúng hai file cấu hình mà bundle có đủ dữ liệu để tái tạo:
`.claude/settings.json` (từ `hooks.json` đi kèm) và `.mcp.json`. Ghi đè thì luôn sao lưu
thành `<file>.tdq-bak-<timestamp>`, và khối `env` bạn tự thêm được giữ lại.

File khác thiếu hoặc lệch thì `setup` **không** bịa nội dung — nó báo `CÒN …` và exit khác 0;
nguồn đúng duy nhất là bản gốc, chép lại từ đó. Chỉ muốn kiểm, không sửa: dùng `check`.

## Khoá bí mật

`.mcp.json` chỉ ghi TÊN biến môi trường, không bao giờ chứa giá trị khoá. Tự đặt biến ở máy
mình trước khi dùng MCP.
"""


def _sinh_settings(repo, dich_settings):
    """`hooks/hooks.json` + khối `env` của repo → `.claude/settings.json` của project đích."""
    cai_dat = sinh_settings(repo, os.path.join(repo, "hooks", "hooks.json"))
    duong_env = os.path.join(repo, ".claude", "settings.json")
    if os.path.isfile(duong_env):
        with open(duong_env, encoding="utf-8") as f:
            cu = json.load(f)
        if "env" in cu:
            cai_dat["env"] = cu["env"]
    cai_dat.setdefault("env", {})
    _ghi_json(dich_settings, cai_dat)
    return 0


def _ghi_json(duong, du_lieu):
    """Ghi JSON đúng byte-for-byte như `tdq_checkportable._ghi_json_co_backup` ghi.

    Lệch một ký tự xuống dòng ở đây là lệch sha256: `setup` sinh lại file rồi `check` ngay
    sau đó báo LỆCH, dù nội dung giống hệt về nghĩa.
    """
    with open(duong, "w", encoding="utf-8") as f:
        f.write(json.dumps(du_lieu, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _sinh_mcp(duong):
    _ghi_json(duong, sinh_mcp())


def sinh_ban_claude(repo, dest, version=""):
    """Dựng `<dest>/portable_claude/` — bản chép thẳng vào project dùng Claude Code."""
    goc = os.path.join(dest, TEN_BAN_CLAUDE)
    if os.path.isdir(goc):
        shutil.rmtree(goc)
    thu_muc_claude = os.path.join(goc, ".claude")
    tdq = os.path.join(goc, GOC_TDQ)
    moi = "${" + BIEN_MOI + "}/" + GOC_TDQ

    tong_doi = 0
    tong_doi += copy_loc(os.path.join(repo, "skills"),
                         os.path.join(thu_muc_claude, "skills"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, PORTABLE_SRC, "skills"),
                         os.path.join(thu_muc_claude, "skills"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, "agents"),
                         os.path.join(thu_muc_claude, "agents"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, "scripts"),
                         os.path.join(tdq, "scripts"), True, moi)
    tong_doi += copy_loc(os.path.join(repo, "hooks"),
                         os.path.join(tdq, "hooks"), True, moi)
    tong_doi += _sinh_settings(repo, os.path.join(thu_muc_claude, "settings.json"))
    _sinh_mcp(os.path.join(goc, ".mcp.json"))

    with open(os.path.join(goc, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_CLAUDE)

    con_lai = dem_bien_trong_cay(goc)
    if con_lai:
        raise RuntimeError(f"bản claude còn {con_lai} chỗ dùng {BIEN_CU}")
    log(f"{TEN_BAN_CLAUDE}: đổi {tong_doi} chỗ dùng biến plugin, còn sót 0")

    ghi_manifest(goc, version)
    return goc


# -------------------------------------------------------------- bản codex

TEN_BAN_CODEX = "portable_codex"

# Thứ tự đọc, không phải thứ tự bảng chữ cái: harness không có skill system thì không có gì
# tự chọn file đúng lúc, nên số thứ tự trong tên file CHÍNH LÀ cơ chế định tuyến.
THU_TU_SKILL = (
    "tdq-conventions",
    "tdq-intake",
    "tdq-spec",
    "tdq-plan",
    "tdq-build",
    "tdq-checkportable",  # nguồn ở PORTABLE_SRC, không phải `skills/`
    "tdq-status",
    "tdq-check-status",
)

AGENTS_MD = """# TDQ Workflow — hướng dẫn cho agent

Soul: chất lượng > runtime > context cost · luật gốc: `workflow/references/tdq-conventions/soul.md`

Bộ này chạy theo pipeline có cổng duyệt: intake → spec → plan → implement → QC → report.
Chỉ NGƯỜI DÙNG được duyệt, và mọi thay đổi state chỉ đi qua `scripts/tdq_state.py`.

## Bước 0 — kiểm tương thích TRƯỚC mọi việc khác

```
python3 scripts/tdq_checkportable.py check
```

Báo thiếu thì chạy `python3 scripts/tdq_checkportable.py setup`: nó dựng lại hai file cấu
hình tái tạo được (`.claude/settings.json`, `.mcp.json`), luôn sao lưu `<file>.tdq-bak-<timestamp>`
trước khi ghi đè, và báo `CÒN …` cho phần chỉ chép lại từ bản gốc mới đúng.

Dòng `LƯU Ý project chưa trusted` là dòng quan trọng nhất của lệnh này: chưa trusted thì
Codex bỏ qua cả `.codex/config.toml` lẫn `.codex/hooks.json`, bundle chạy như thể không có.

## Chạy trên Codex CLI (>= {codex_min}) — dùng lớp native, không cần đọc `workflow/`

- `.agents/skills/` — Codex tự nạp skill theo `description`, không phải tự chọn file.
- `.codex/config.toml` — MCP server; chỉ TÊN biến môi trường, tự đặt biến ở máy mình.
- `.codex/hooks.json` + `hooks/` — cổng duyệt do máy canh (`SessionStart`,
  `UserPromptSubmit`, `PreToolUse` cho `Bash` và `apply_patch`, `Stop`).

## Harness khác — đọc `workflow/` theo đúng số thứ tự

Không có skill system thì số thứ tự trong tên file CHÍNH LÀ cơ chế định tuyến:

{danh_sach}

Bảng phase đầy đủ: `workflow/phases.md` (tự sinh từ hằng `PHASE_TABLE`, không sửa tay).

## Bốn việc máy KHÔNG tự làm được

1. Cấp quyền cho thư mục project ở lần chạy đầu (`setup --trust` làm thay được bước này).
2. Duyệt hook trong giao diện Codex — hook có cổng tin cậy riêng, `--trust` KHÔNG mở được.
3. Duyệt từng MCP server khai trong `.codex/config.toml`.
4. Khởi động lại phiên sau khi thêm thư mục instruction mới.
"""


README_CODEX = """# TDQ Workflow — bản portable cho Codex CLI

Bản này dùng ĐÚNG cơ chế native của Codex, không phải markdown đọc tay:

| Lớp | File trong bundle | Codex làm gì với nó |
|---|---|---|
| Skill | `.agents/skills/<tên>/SKILL.md` | tự quét, nạp dần theo `description` |
| MCP | `.codex/config.toml` | `[mcp_servers.<tên>]`, chỉ TÊN biến môi trường |
| Hook | `.codex/hooks.json` + `hooks/` | canh `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop` |
| Dự phòng | `workflow/NN-*.md` | cho harness KHÁC (Antigravity…) đọc tuần tự |

Cần Codex CLI >= {codex_min}. Bản cũ hơn vẫn dùng được `workflow/*.md`, nhưng không có
lớp native nào.

## Cài ở máy mới — làm theo đúng thứ tự này

Thứ tự quan trọng: **trust TRƯỚC, chạy SAU**. Project chưa được tin cậy thì Codex bỏ qua
TOÀN BỘ tầng `.codex/` — MCP không nạp, `hooks.json` không đọc, bundle trông như rỗng mà
không báo lỗi gì.

1. **Chép** trọn nội dung thư mục này vào gốc project.
2. **Trust thư mục project** — xem ba cách ngay mục dưới.
3. **Kiểm**:
   ```
   python3 scripts/tdq_checkportable.py check
   ```
   Kết quả có một dòng nói project đã trusted hay chưa. Đọc theo tiền tố: `SẠCH` xong ·
   `THIẾU` chưa có · `LỆCH` khác manifest · `LƯU Ý` việc chỉ bạn làm được.
4. **Vá** nếu có `THIẾU`/`LỆCH`: `python3 scripts/tdq_checkportable.py setup` — nó dựng lại
   hai file cấu hình tái tạo được, luôn sao lưu `<file>.tdq-bak-<timestamp>` trước khi ghi
   đè, và báo `CÒN …` cho phần chỉ chép lại từ bản gốc mới đúng.
5. **Đặt biến môi trường** cho MCP nếu `check` báo thiếu. Script cố ý KHÔNG làm hộ việc này
   và không bao giờ in giá trị khoá — chỉ báo tên biến.
6. **Mở Codex CLI** trong project, rồi **khởi động lại phiên** một lần để skill trong
   `.agents/skills/` được quét.
7. **Duyệt hook** trong giao diện Codex — cổng RIÊNG, xem mục "Bốn việc" bên dưới.
8. **Duyệt MCP server** — mỗi server một lần.

## Trust — ba cách, chọn một

**Cách 1 — để script làm, không cần mở Codex:**

```
cd <gốc project đã chép bundle vào>
python3 scripts/tdq_checkportable.py setup --trust
```

**Cách 2 — bấm trong Codex:** mở Codex CLI ngay tại thư mục project; lần đầu vào thư mục lạ
nó hỏi có cho phép làm việc ở đây không → chọn phương án tin cậy thư mục.

**Cách 3 — sửa tay** `~/.codex/config.toml` (hoặc `$CODEX_HOME/config.toml`), thêm:

```toml
[projects."/đường/dẫn/tuyệt/đối/tới/project"]
trust_level = "trusted"
```

Đường dẫn phải TUYỆT ĐỐI và đã resolve symlink, khớp đúng thư mục Codex chạy trong đó —
lệch một ký tự là không ăn.

Cách 1 chính là đường DUY NHẤT của bộ này ghi ra ngoài bundle: nó luôn để lại
`<file>.tdq-bak-<timestamp>`, giữ nguyên phần còn lại của file, và không ghi chồng block đã
có. Không có cờ `--trust` thì `setup` không đụng tới file đó.

Kiểm đã ăn chưa: chạy lại `check` và đọc dòng trạng thái trusted.

## Bốn việc máy KHÔNG tự làm được

1. **Tin cậy thư mục** — `setup --trust` làm thay được (Cách 1 ở trên), hoặc bấm đồng ý
   trong Codex.
2. **Duyệt hook** — hook có cổng tin cậy RIÊNG: Codex hiện "Review hooks" trong giao diện và
   bạn phải duyệt một lần. `--trust` không mở được cổng này, và sửa `hooks.json` thì phải
   duyệt lại. Chưa duyệt thì hook im lặng không chạy.
3. **Duyệt MCP server** — mỗi server trong `.codex/config.toml` cần bạn duyệt một lần.
4. **Khởi động lại** — instruction mới chỉ được nạp sau khi khởi động lại phiên.

## Vì sao bước 3 chạy thẳng file, không nhắn "chạy skill tdq-checkportable"

Skill nằm trong chính bundle này, mà Codex chỉ quét `.agents/skills/` sau khi project được
tin cậy và phiên đã khởi động lại. Gọi skill ở bước đầu là vòng luẩn quẩn; chạy thẳng
`python3 scripts/tdq_checkportable.py` bằng terminal thì không vướng. Từ lần sau, khi mọi
thứ đã nạp, gọi skill bình thường.

## Khoá bí mật

Không file nào ở đây chứa giá trị khoá, chỉ TÊN biến môi trường (`env_vars` trong
`config.toml`). Tự đặt biến ở máy mình trước khi dùng MCP.
"""


# ------------------------------------------- lớp native của Codex CLI (>= 0.147.0)

# Ba thư mục Codex tự quét. Tên và vị trí do Codex quy định, không tự đặt được:
#   `.agents/skills/<tên>/SKILL.md`   — skill, nạp dần theo description trong frontmatter
#   `.codex/config.toml`              — MCP server (chỉ nạp khi project đã trusted)
#   `.codex/hooks.json`               — hook (còn phải được duyệt riêng trong TUI)
GOC_SKILL_CODEX = ".agents/skills"
GOC_CAU_HINH_CODEX = ".codex"
CODEX_MIN = "0.147.0"

# Ánh xạ hook TDQ → event + matcher của Codex. Matcher là regex khớp `tool_name`, và tên tool
# THẬT của Codex đo được bằng hook thăm dò (xem `docs/tdq/qc/2026-08-17-1139-*.md`): tool chạy
# lệnh tên `Bash` (trùng Claude Code), còn tool sửa file tên `apply_patch` — KHÔNG phải
# `Edit|Write|MultiEdit|NotebookEdit`. Giữ nguyên matcher của Claude Code thì hook không bao
# giờ nổ, mà cũng không báo lỗi: cổng duyệt tắt im lặng.
HOOK_CODEX = (
    ("SessionStart", None, "session_start.py"),
    ("UserPromptSubmit", None, "prompt_context.py"),
    ("PreToolUse", "apply_patch", "codex_edit_gate.py"),
    ("PreToolUse", "Bash", "bash_gate.py"),
    ("Stop", None, "stop_gate.py"),
)

# Adapter sinh vào bundle, KHÔNG sửa `hooks/scripts/edit_gate.py` của repo. Lý do tách ra:
# `edit_gate.py` là mã dùng chung cho cả hai harness, còn khác biệt ở đây thuần tuý là hình
# dạng `tool_input` của riêng Codex. Nhét vào file chung là bắt Claude Code gánh một nhánh
# không bao giờ chạy, và mỗi lần sửa gate lại phải nhớ hai hình dạng payload.
ADAPTER_CODEX = '''#!/usr/bin/env python3
"""codex_edit_gate.py — cầu nối giữa `apply_patch` của Codex và `edit_gate.py` dùng chung.

SINH TỰ ĐỘNG bởi `scripts/build_portable.py`. Sửa tay ở đây sẽ mất khi build lại.

Vì sao cần: Claude Code gửi `tool_input.file_path`, còn Codex gửi `tool_input.command` chứa
nguyên thân patch (`*** Update File: <đường dẫn>`). `edit_gate.py` đọc `file_path`, nên chạy
thẳng dưới Codex sẽ ra đường dẫn rỗng — gate vẫn exit 0 mà không canh gì cả, lỗi im lặng.
File này rút đường dẫn ra khỏi thân patch, gắn vào `file_path`, rồi giao lại cho gate thật.

Env: TDQ_LOG=0 tắt log (log ra stderr). Exit code và stdout đi thẳng từ `edit_gate.py`.
"""
import datetime
import json
import os
import re
import subprocess
import sys

MAU_PATCH = re.compile(r"^\\*\\*\\* (?:Update|Add|Delete) File: (.+)$", re.MULTILINE)


def log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"[{stamp}] {message}", file=sys.stderr)


def tach_duong_dan_patch(than):
    """Đường dẫn ĐẦU TIÊN trong thân patch, hoặc chuỗi rỗng. Không ném với input lạ."""
    khop = MAU_PATCH.search(than or "")
    return khop.group(1).strip() if khop else ""


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        # Payload hỏng thì không chặn phiên: gate là cơ chế nhắc, không phải cơ chế bảo mật.
        log("codex_edit_gate: payload không phải JSON, bỏ qua")
        print("{}")
        return 0
    tool_input = payload.get("tool_input") or {}
    if not tool_input.get("file_path"):
        duong = tach_duong_dan_patch(tool_input.get("command"))
        if duong:
            tool_input["file_path"] = duong
            payload["tool_input"] = tool_input
            log(f"codex_edit_gate: apply_patch -> {duong}")
        else:
            log("codex_edit_gate: không tách được đường dẫn khỏi thân patch")
    that = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_gate.py")
    proc = subprocess.run([sys.executable, that], input=json.dumps(payload),
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
'''


def doc_frontmatter(text):
    """Frontmatter YAML một tầng của SKILL.md → dict. Trả dict rỗng nếu không có khối `---`.

    Không dùng thư viện YAML: bundle chạy ở máy lạ với Python trần, thêm phụ thuộc là thêm
    một lý do nữa để bản portable chết ngay bước đầu.
    """
    if not text or not text.startswith("---"):
        return {}
    het = text.find("\n---", 3)
    if het < 0:
        return {}
    truong = {}
    for dong in text[3:het].splitlines():
        if ":" in dong and not dong.startswith(" "):
            khoa, _, gia_tri = dong.partition(":")
            truong[khoa.strip()] = gia_tri.strip()
    return truong


def tach_duong_dan_patch(than):
    """Đường dẫn đầu tiên trong thân patch của `apply_patch`, hoặc chuỗi rỗng.

    Bản chạy thật nằm trong `ADAPTER_CODEX` (chạy ở máy đích). Bản này để test khoá được hành
    vi mà không phải bung bundle ra trước.
    """
    khop = re.search(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", than or "", re.MULTILINE)
    return khop.group(1).strip() if khop else ""


def _sinh_config_toml(duong):
    """`.codex/config.toml` — khai MCP server theo khuôn `[mcp_servers.<tên>]` của Codex.

    Chỉ ghi TÊN biến môi trường qua `env_vars`, không bao giờ giá trị: Codex KHÔNG khai triển
    `${VAR}` trong TOML, nên viết `env = {X = "${X}"}` sẽ truyền sang MCP đúng chuỗi ký tự đó
    chứ không phải khoá. `env_vars` là cách Codex chuyển tiếp biến từ môi trường cha — đúng
    thứ cần, và cũng là cách duy nhất không đưa bí mật vào file.
    """
    khai_bao = sinh_mcp()["mcpServers"]
    dong = [
        "# TDQ Workflow — cấu hình Codex CLI, SINH TỰ ĐỘNG bởi scripts/build_portable.py.",
        f"# Cần Codex CLI >= {CODEX_MIN}. Chỉ nạp được khi project đã trusted.",
        "",
    ]
    for ten in sorted(khai_bao):
        cau_hinh = khai_bao[ten]
        dong.append(f"[mcp_servers.{ten}]")
        dong.append(f'command = {json.dumps(cau_hinh["command"])}')
        dong.append("args = [" + ", ".join(json.dumps(a) for a in cau_hinh["args"]) + "]")
        ten_bien = sorted(cau_hinh.get("env") or {})
        if ten_bien:
            dong.append("env_vars = [" + ", ".join(json.dumps(b) for b in ten_bien) + "]")
        dong.append("")
    with open(duong, "w", encoding="utf-8") as f:
        f.write("\n".join(dong))


def _sinh_hooks_codex(duong):
    """`.codex/hooks.json` — cùng khuôn wire với `hooks/hooks.json`, khác matcher và đường dẫn.

    Đường dẫn để TƯƠNG ĐỐI có chủ ý: đo thật cho thấy Codex chạy tiến trình hook với cwd =
    gốc project, nên `hooks/scripts/x.py` đủ đúng ở mọi máy. Nhờ vậy file này là file tĩnh
    nằm trong `manifest.json`, không phải thứ phải sinh lại lúc `setup` ở máy đích.
    """
    su_kien = {}
    for ten_event, matcher, ten_file in HOOK_CODEX:
        nhom = {"hooks": [{
            "type": "command",
            "command": f'python3 "hooks/scripts/{ten_file}"',
        }]}
        if matcher:
            nhom["matcher"] = matcher
        su_kien.setdefault(ten_event, []).append(nhom)
    _ghi_json(duong, {
        "description": "TDQ workflow cho Codex CLI — sinh tự động, không sửa tay",
        "hooks": su_kien,
    })


def sinh_ban_codex(repo, dest, version=""):
    """Dựng `<dest>/portable_codex/` — bản dùng ĐÚNG cơ chế native của Codex CLI.

    Bốn nhóm hiện vật:
      `.agents/skills/`    skill Codex tự nạp theo description;
      `.codex/config.toml` MCP server (chỉ TÊN biến môi trường);
      `.codex/hooks.json` + `hooks/`  cổng duyệt do máy canh, dùng lại mã của repo;
      `workflow/NN-*.md`   bản markdown đọc tuần tự, giữ cho harness KHÁC Codex (Antigravity…)
                           vẫn dùng được bundle này.

    Ba lớp đầu cần Codex CLI >= 0.147.0 và cần project được trusted; riêng hook còn cần người
    dùng duyệt một lần trong TUI. Không có gì trong đây tự làm thay được mấy việc đó.
    """
    import tdq_state

    goc = os.path.join(dest, TEN_BAN_CODEX)
    if os.path.isdir(goc):
        shutil.rmtree(goc)
    thu_muc_wf = os.path.join(goc, "workflow")
    os.makedirs(thu_muc_wf, exist_ok=True)
    os.makedirs(os.path.join(goc, GOC_CAU_HINH_CODEX), exist_ok=True)

    # Harness ngoài Claude Code không đặt biến `CLAUDE_*` nào cả, nên đường dẫn ở bản này
    # phải tương đối so với gốc bundle — người dùng `cd` vào đó rồi chạy là xong.
    moi = "."
    copy_loc(os.path.join(repo, "scripts"), os.path.join(goc, "scripts"), True, moi)

    dong_danh_sach = []
    for so, ten_skill in enumerate(THU_TU_SKILL, start=1):
        thu_muc_skill = os.path.join(repo, "skills", ten_skill)
        if not os.path.isdir(thu_muc_skill):
            thu_muc_skill = os.path.join(repo, PORTABLE_SRC, "skills", ten_skill)
        nguon = os.path.join(thu_muc_skill, "SKILL.md")
        if not os.path.isfile(nguon):
            continue
        ten_file = f"{so:02d}-{ten_skill[len('tdq-'):]}.md"
        noi_dung, _ = doi_bien_plugin_root(_doc_text(nguon), moi)
        with open(os.path.join(thu_muc_wf, ten_file), "w", encoding="utf-8") as f:
            f.write(noi_dung)
        thu_muc_ref = os.path.join(thu_muc_skill, "references")
        if os.path.isdir(thu_muc_ref):
            copy_loc(thu_muc_ref, os.path.join(thu_muc_wf, "references", ten_skill), True, moi)
        # Lớp native: chép NGUYÊN cây skill sang `.agents/skills/<tên>/` — giữ nguyên tên thư
        # mục là điều kiện để các liên kết `../<skill khác>/SKILL.md` trong SKILL.md còn trỏ
        # đúng, thứ mà bản `workflow/NN-*.md` phải đánh số lại nên mất.
        copy_loc(thu_muc_skill, os.path.join(goc, GOC_SKILL_CODEX, ten_skill), True, moi)
        dong_danh_sach.append(f"- `workflow/{ten_file}`")

    # `hooks/` phải nằm ở GỐC bundle, cạnh `scripts/`: `hooks/scripts/_common.py` suy ra thư
    # mục script bằng `../../scripts` tính từ chính nó. Nhét vào `.codex/` là gãy đúng chỗ đó.
    copy_loc(os.path.join(repo, "hooks"), os.path.join(goc, "hooks"), True, moi)
    duong_adapter = os.path.join(goc, "hooks", "scripts", "codex_edit_gate.py")
    with open(duong_adapter, "w", encoding="utf-8") as f:
        f.write(ADAPTER_CODEX)
    os.chmod(duong_adapter, 0o755)
    _sinh_config_toml(os.path.join(goc, GOC_CAU_HINH_CODEX, "config.toml"))
    _sinh_hooks_codex(os.path.join(goc, GOC_CAU_HINH_CODEX, "hooks.json"))

    with open(os.path.join(thu_muc_wf, "phases.md"), "w", encoding="utf-8") as f:
        f.write(tdq_state.render_phases_md() + "\n")

    with open(os.path.join(goc, "AGENTS.md"), "w", encoding="utf-8") as f:
        f.write(AGENTS_MD.format(danh_sach="\n".join(dong_danh_sach), codex_min=CODEX_MIN))

    with open(os.path.join(goc, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_CODEX.format(codex_min=CODEX_MIN))

    con_lai = dem_bien_trong_cay(goc)
    if con_lai:
        raise RuntimeError(f"bản codex còn {con_lai} chỗ dùng {BIEN_CU}")
    log(f"{TEN_BAN_CODEX}: {len(dong_danh_sach)} skill (native + workflow), "
        f"{len(HOOK_CODEX)} hook, {len(MCP_SERVERS)} MCP server, còn sót 0 biến plugin")

    ghi_manifest(goc, version)
    return goc


# ------------------------------------------------------------------ manifest

def sinh_manifest(goc, version=""):
    """Quét cây thư mục → dict manifest đủ 5 khối.

    `manifest.json` tự loại chính nó khỏi danh sách: nó được ghi SAU khi quét, nên nếu tự
    liệt kê thì sha256 ghi vào không bao giờ khớp nội dung cuối cùng của chính file đó.
    """
    files = {}
    for thu_muc, thu_muc_con, ten_files in os.walk(goc):
        thu_muc_con[:] = [d for d in thu_muc_con if not _bo_qua_thu_muc(d)]
        for ten in ten_files:
            if _bo_qua_file(ten):
                continue
            duong_day_du = os.path.join(thu_muc, ten)
            tuong_doi = os.path.relpath(duong_day_du, goc).replace(os.sep, "/")
            if tuong_doi == MANIFEST_NAME:
                continue
            files[tuong_doi] = sha256_of(duong_day_du)
    return {
        "files": files,
        "version": version,
        "python_min": PYTHON_MIN,
        "external_commands": list(EXTERNAL_COMMANDS),
        "mcp_servers": list(MCP_SERVERS),
    }


def ghi_manifest(goc, version=""):
    man = sinh_manifest(goc, version)
    with open(os.path.join(goc, MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2, sort_keys=True)
    log(f"manifest: {len(man['files'])} file trong {os.path.basename(goc)}")
    return man


# -------------------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="build_portable.py",
        description="Sinh hai bản portable (claude, codex) của bộ TDQ Workflow từ một nguồn.")
    parser.add_argument("--dest", help="thư mục đích, mặc định là gốc repo")
    parser.add_argument("--only", choices=("claude", "codex"),
                        help="chỉ sinh một bản thay vì cả hai")
    parser.add_argument("--repo", help="gốc repo nguồn, mặc định suy từ vị trí script")
    args = parser.parse_args(argv)

    repo = args.repo or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = args.dest or repo
    version = plugin_version(repo)
    log(f"bắt đầu · repo={repo} · dest={dest} · version={version or '—'}")

    os.makedirs(dest, exist_ok=True)
    try:
        if args.only != "codex":
            sinh_ban_claude(repo, dest, version)
        if args.only != "claude":
            sinh_ban_codex(repo, dest, version)
    except (OSError, RuntimeError) as loi:
        log(f"LỖI {loi}")
        return EXIT_LOI
    log("xong")
    return 0


if __name__ == "__main__":
    sys.exit(main())
