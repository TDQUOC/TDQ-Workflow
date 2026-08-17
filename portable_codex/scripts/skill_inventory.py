#!/usr/bin/env python3
"""Kiểm kê skill có trên ĐĨA cho bước B0 của tdq-intake (0.3.3).

Quét đúng 3 nguồn — KHÔNG quét cache (cache giữ mọi version cũ, ra hàng trăm file rác):
1. `~/.claude/skills/<x>/SKILL.md`         → nguồn `user`
2. `<project>/.claude/skills/<x>/SKILL.md` → nguồn `project`
3. Plugin đang BẬT: `enabledPlugins` gộp từ 3 tầng settings (user → project →
   settings.local.json, tầng sau đè tầng trước), tra `installed_plugins.json`,
   chỉ đọc thư mục `installPath` của bản đang cài. Entry `scope: "project"` của
   project KHÁC bị bỏ.

Skill BUILT-IN của Claude Code không nằm trên đĩa (đo thật: đĩa 7 / context 18),
nên cuối bảng luôn in 2 dòng nhắc model tự chép phần đó từ context.

Cách dùng:  python3 scripts/skill_inventory.py [--project <dir>] [--loc <từ khoá>] [--tat-ca]
Không cờ = bảng đầy đủ (hành vi gốc, ~39,7KB trên máy thật ≈ 9.774 token mỗi lần
chạy B0). `--loc <từ khoá>` chỉ giữ dòng khớp từ khoá, CỘNG mọi dòng nguồn
`project` và `plugin:tdq-workflow` — hai nguồn quyết định phán quyết DÙNG nên
cấm ẩn — rồi in một dòng cuối báo đã ẩn bao nhiêu và lệnh xem đủ. `--tat-ca`
in đủ như mặc định (để dòng nhắc kia trỏ tới một lệnh có thật).
Exit 0 cho mọi trục trặc dữ liệu (thiếu file, JSON hỏng → cảnh báo rồi in phần
còn lại); exit 2 chỉ khi sai cú pháp lệnh — cùng hợp đồng với tdq_state.py.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tdq_state  # noqa: E402 — dùng chung log service (_warn, TDQ_LOG, timestamp)

DESC_MAX = 60
TRIGGER_TAIL = 50   # số ký tự lấy kể từ chỗ cụm trigger, khi trigger nằm ngoài DESC_MAX
# Cụm trigger bắt đầu ngay TRƯỚC ngưỡng vẫn bị ngưỡng cắt ngang (đo thật:
# `huggingface-trackio` có `Use when` ở ký tự 58, ô cụt ở `Us`). Lùi điểm dò lại một
# quãng để bắt cả ca vắt ngưỡng; phần chồng lấn tối đa bằng đúng quãng lùi này.
TRIGGER_LOOKBACK = 15
# Description skill viết theo khuôn "câu 1 = nó là gì, câu 2 = dùng khi nào". Đo trên 268
# SKILL.md: 146/211 skill có cụm trigger nằm SAU ký tự thứ 60, nên cắt cụt làm mất đúng
# phần cần cho phán quyết DÙNG/KHÔNG. `_condense` giữ đầu + ghép thêm khúc trigger.
# Nhánh tiếng Việt cho skill viết mô tả bằng tiếng Việt (6 skill tdq-* là ví dụ tại chỗ):
# cùng khuôn "câu 1 = nó là gì, câu 2 = dùng khi nào", chỉ khác ngôn ngữ. Đo trên 274 skill:
# 0 khớp nhầm vào mô tả tiếng Anh — các cụm này đều có dấu, không đụng chữ ASCII.
TRIGGER_RE = re.compile(
    r"use when|use this|whenever|when the user|trigger"
    r"|dùng khi|dùng cho|gọi khi|áp dụng khi|khi cần|khi user", re.I)
FRONTMATTER_MAX_LINES = 80
# YAML block scalar: `description: |` và biến thể. Trước 2026-08-09 parser đọc `|` như
# nội dung → 18 skill (firecrawl, tavily, mongodb-search-and-ai) rỗng mô tả.
BLOCK_MARKERS = ("|", "|-", "|+", ">", ">-", ">+")
REMINDER = (
    "— Bảng trên chỉ gồm skill trên đĩa.",
    "— CHÉP THÊM các skill built-in đang thấy trong context "
    "vào bảng kiểm kê rồi phán quyết từng dòng.",
)
USAGE = ("Cách dùng: skill_inventory.py [--project <dir>] "
         "[--loc <từ khoá>] [--tat-ca]")
# Nguồn KHÔNG bao giờ bị `--loc` ẩn: skill của chính project và của plugin
# tdq-workflow là hai nguồn quyết định phán quyết DÙNG ở bước B0.
KEEP_SOURCES = ("project",)
KEEP_SOURCE_PREFIX = "plugin:tdq-workflow"
FULL_CMD = "python3 scripts/skill_inventory.py --tat-ca"


def _load_json(path, missing_ok=False):
    """dict từ file JSON, hoặc None. Hỏng/thiếu (khi missing_ok=False) → cảnh báo."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if not missing_ok:
            tdq_state._warn(f"skill_inventory: thiếu {path}")
        return None
    except (OSError, ValueError) as exc:
        tdq_state._warn(f"skill_inventory: không đọc được {path} ({type(exc).__name__})")
        return None


def _clean(text):
    """Bỏ ký tự điều khiển — SKILL.md xấu không được điều khiển terminal của user (Q9)."""
    return "".join(ch for ch in text if ch >= " " or ch == "\t")


def _frontmatter(path):
    """(name, description) từ frontmatter; lỗi đọc → (None, None) + cảnh báo.

    Description nhiều dòng (block scalar `|`, `>`, hoặc plain scalar thụt vào) được nối
    thành một dòng: gom mọi dòng thụt vào cho tới khoá cấp 0 kế tiếp hoặc `---` đóng.
    """
    name = desc = ""
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(16384).splitlines()[:FRONTMATTER_MAX_LINES]
    except OSError as exc:
        tdq_state._warn(f"skill_inventory: không đọc được {path} ({type(exc).__name__})")
        return None, None
    if head and head[0].strip() == "---":
        head = head[1:]
    i = 0
    while i < len(head):
        line = head[i]
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            name = _clean(line[5:].strip())
        elif line.startswith("description:"):
            rest = line[12:].strip()
            parts = [] if rest in BLOCK_MARKERS else [rest]
            i += 1
            while i < len(head) and head[i].strip() != "---" and \
                    (not head[i].strip() or head[i][:1] in (" ", "\t")):
                parts.append(head[i].strip())
                i += 1
            desc = _clean(" ".join(p for p in parts if p).strip().strip('"'))
            continue
        i += 1
    return name or _clean(os.path.basename(os.path.dirname(path))), desc


def _condense(desc):
    """Rút gọn description cho một ô bảng: giữ đầu, ghép thêm khúc trigger nếu nó ở xa.

    `|` đổi thành `/` — bảng in ra tách cột bằng `|`, để nguyên là vỡ số cột.
    """
    text = " ".join((desc or "").split()).replace("|", "/")
    if len(text) <= DESC_MAX:
        return text
    found = TRIGGER_RE.search(text, DESC_MAX - TRIGGER_LOOKBACK)
    if not found:
        return text[:DESC_MAX]
    # Trigger vắt ngưỡng: cắt đầu ngay TRƯỚC nó, khỏi lặp cụm ở cả hai bên dấu nối.
    head = text[:min(DESC_MAX, found.start())].rstrip()
    return f"{head} … {text[found.start():found.start() + TRIGGER_TAIL]}"


def _scan_skill_dir(root):
    """[(name, desc)] từ một thư mục chứa <skill>/SKILL.md."""
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "*", "SKILL.md"))):
        name, desc = _frontmatter(path)
        if name is not None:
            rows.append((name, desc))
    return rows


def _enabled_plugins(home, project):
    """enabledPlugins gộp 3 tầng — tầng sau đè tầng trước (giống Claude Code)."""
    merged = {}
    layers = (
        (os.path.join(home, ".claude", "settings.json"), False),
        (os.path.join(project, ".claude", "settings.json"), True),
        (os.path.join(project, ".claude", "settings.local.json"), True),
    )
    for path, missing_ok in layers:
        data = _load_json(path, missing_ok=missing_ok)
        if isinstance(data, dict) and isinstance(data.get("enabledPlugins"), dict):
            merged.update(data["enabledPlugins"])
    return merged


def _plugin_skill_dirs(home, project):
    """[(tên plugin, thư mục skills)] của các plugin đang bật cho project này."""
    enabled = _enabled_plugins(home, project)
    if not any(enabled.values()):
        return []
    data = _load_json(os.path.join(home, ".claude", "plugins", "installed_plugins.json"))
    entries = data.get("plugins", {}) if isinstance(data, dict) else {}
    project_real = os.path.realpath(project)
    dirs, seen = [], set()
    for key in sorted(k for k, on in enabled.items() if on):
        for entry in entries.get(key, []) or []:
            if not isinstance(entry, dict):
                continue
            # Plugin cài riêng cho một project khác: không thuộc bảng của project này.
            if entry.get("scope") == "project" and \
                    os.path.realpath(str(entry.get("projectPath", ""))) != project_real:
                continue
            skills = os.path.join(str(entry.get("installPath", "")), "skills")
            if os.path.isdir(skills) and skills not in seen:
                seen.add(skills)
                dirs.append((key.split("@")[0], skills))
    return dirs


def inventory(project):
    """[(name, desc đã rút gọn, nguồn)] — trùng tên thì nguồn quét trước thắng."""
    home = os.path.expanduser("~")
    rows, seen = [], set()

    def add(name, desc, source):
        if name in seen:
            return
        seen.add(name)
        rows.append((name, _condense(desc), source))

    for name, desc in _scan_skill_dir(os.path.join(home, ".claude", "skills")):
        add(name, desc, "user")
    for name, desc in _scan_skill_dir(os.path.join(project, ".claude", "skills")):
        add(name, desc, "project")
    for plugin, skill_dir in _plugin_skill_dirs(home, project):
        for name, desc in _scan_skill_dir(skill_dir):
            add(name, desc, f"plugin:{plugin}")
    return rows


def _filter(rows, keyword):
    """(dòng giữ lại, số dòng bị ẩn) — khớp từ khoá HOẶC thuộc nguồn cấm ẩn."""
    needle = keyword.casefold()
    kept, hidden = [], 0
    for name, desc, source in rows:
        protected = source in KEEP_SOURCES or source.startswith(KEEP_SOURCE_PREFIX)
        if protected or needle in f"{name} {desc}".casefold():
            kept.append((name, desc, source))
        else:
            hidden += 1
    return kept, hidden


def main(argv):
    # A23: neo theo project thật (TDQ_PROJECT_DIR > git root > cwd) — chạy từ
    # thư mục con không được mất nguồn skill `project`.
    project = tdq_state.resolve_project_dir()
    keyword = ""
    show_all = False
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--project" and args:
            project = args.pop(0)
        elif arg == "--loc" and args:
            keyword = args.pop(0)
        elif arg == "--tat-ca":
            show_all = True
        else:
            print(f"đối số không hiểu: {arg}", file=sys.stderr)
            print(USAGE, file=sys.stderr)
            return 2
    rows = inventory(project)
    # `--tat-ca` thắng `--loc`: người gõ cả hai đang muốn xem đủ.
    hidden = 0
    if keyword and not show_all:
        rows, hidden = _filter(rows, keyword)
        tdq_state._info(
            f"skill_inventory: lọc theo {keyword!r} — giữ {len(rows)}, ẩn {hidden}")
    if rows:
        for name, desc, source in rows:
            print(f"{name} | {desc} | {source}")
    else:
        print("(không có skill nào trên đĩa)")
    for line in REMINDER:
        print(line)
    if keyword and not show_all:
        # Dòng cuối BẮT BUỘC: bảng đã bị cắt thì người đọc phải thấy ngay đã mất bao
        # nhiêu và lệnh nào xem đủ — cắt token nhưng không giấu chuyện đã cắt.
        print(f'— Đã ẩn {hidden} skill không khớp "{keyword}"; xem đủ: {FULL_CMD}')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
