#!/usr/bin/env python3
"""Lint doc hướng dẫn của TDQ workflow (spec §2.6).

Mục đích: giữ skill ở dạng mà một model nhỏ vẫn đọc và làm đúng —
bước đánh số liên tục, lệnh copy-paste được, có điều kiện ra, không có từ mơ hồ.

Cách dùng:
    python3 scripts/doc_lint.py skills
    python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md

In `file:line: [RULE] mô tả`; exit 1 nếu có vi phạm, 0 nếu sạch, 2 nếu sai cú pháp.
Tắt một rule cho một dòng: đặt `<!-- doc-lint: allow R4 -->` ở dòng NGAY TRÊN nó.
Env: TDQ_LOG=0 tắt log service (mặc định bật, 1 dòng ISO-timestamp ra stderr).
"""
import os
import re
import sys
from datetime import datetime

EXIT_SYNTAX = 2


def _log(message):
    """Log service: 1 dòng ISO-timestamp ra stderr. Tắt bằng TDQ_LOG=0.

    Ra stderr chứ không stdout: stdout là kênh máy đọc của lint (`file:line: [RULE]`),
    lẫn log vào đó là làm hỏng hợp đồng với script gọi nó.
    """
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().isoformat(timespec='seconds')}] doc_lint: {message}",
              file=sys.stderr)

# Trần số dòng của SKILL.md theo tên skill (spec §2.4). Test dùng chung hằng này.
SKILL_LINE_LIMITS = {
    "tdq-intake": 120,
    "tdq-spec": 100,
    # 2026-08-18: 100 → 110. Cổng đề xuất mode đổi từ đếm task bằng mắt sang chạy
    # `tdq_bench.py mo-phong` — khối lệnh + lý do hệ số 1.5 phải nằm ở thân skill
    # mới được đọc mỗi lần viết plan.
    "tdq-plan": 110,
    "tdq-build": 150,
    "tdq-status": 60,
    # 2026-08-15: 120 → 130. Luật một lượt (§10) là luật tầng runtime, phải nằm ở thân
    # skill mới được nạp mỗi turn. Soul xếp runtime trên context cost, nên nới trần 10
    # dòng để giữ luật đọc được, thay vì nén luật cho vừa trần.
    # 2026-08-16: 130 → 133. Clean code bỏ cổng hỏi và script scan, nên luật SOLID chỉ còn
    # sống nếu §11 nạp nó mỗi turn — 3 dòng nạp ở thân skill, chi tiết ở references.
    # 2026-08-17: 133 → 143. Mode đội thêm 2 luật tầng runtime vào §1 (đóng sổ nhiều lần
    # trong một turn dài; plan chưa hết task thì không kết thúc turn + 3 ngoại lệ). Cả hai
    # phải đọc được mỗi turn, nén xuống references là mất tác dụng.
    # 2026-08-19: 143 → 145. Hướng C đưa `plugin-routing.md` và `measure-scenario.md` lên
    # tầng 1: hai file này trước đó không SKILL.md nào trỏ tới, tức chỉ tới được qua một
    # reference khác — chỗ model có thể đọc nửa vời. Giá là 2 dòng đường trỏ ở thân skill.
    "tdq-conventions": 145,
    # skill khôi phục: 7 bước + khối luật cứng "không mất dữ liệu" phải nằm ở thân skill,
    # vì model yếu bỏ qua reference sẽ chạy đúng cái lệnh làm mất cả request.
    "tdq-check-status": 80,
}
MAX_LINES_ANY = 500
MAX_SENTENCE_WORDS = 40
# skill phải trỏ tới ít nhất một file mẫu output
NEEDS_TEMPLATE = ("tdq-spec", "tdq-plan", "tdq-build")

HEADING = re.compile(r"^(#+)\s+(.*)$")
STEP = re.compile(r"^(\d+)\.\s+\S")
FENCE = re.compile(r"^\s*```")
# 2026-08-18: `(R\d)` → `(R\d+)` vì mã luật đã lên hai chữ số (R10), và cho phép
# ghi lý do sau mã — dán allow trần thì mất vết vì sao được miễn.
ALLOW = re.compile(r"<!--\s*doc-lint:\s*allow\s+(R\d+)[^>]*-->")
INLINE_CODE = re.compile(r"`[^`]*`")
TEMPLATE_LINK = re.compile(r"references/[^)\s]*template[^)\s]*\.md")
# `·` và `;` là dấu tách hạng mục trong doc này — mỗi hạng mục đọc độc lập được
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+|\s*[·;]\s*")
BULLET = re.compile(r"^\s*[-*]\s+\S")
VAGUE = ["nếu cần", "tùy ý", "tuỳ ý", "nên cân nhắc", "linh hoạt", "tự quyết"]
# heading của mục "bắt buộc" — R1 chỉ soát mục bước, R4 soát cả mục luật
STEP_HEADINGS = ("các bước", "steps")
STRICT_HEADINGS = STEP_HEADINGS + ("phần ", "luật", "giao thức")


class Doc:
    """Một file markdown đã tách sẵn: dòng, vùng fence, heading."""

    def __init__(self, path):
        self.path = path
        try:
            with open(path, encoding="utf-8") as f:
                self.lines = f.read().splitlines()
        except OSError as exc:
            # A20: file biến mất/không đọc được → message, không traceback thô
            sys.exit(f"⚠️ không đọc được {path}: {exc}")
        self.in_fence = []
        fenced = False
        for line in self.lines:
            if FENCE.match(line):
                fenced = not fenced
                self.in_fence.append(True)  # chính dòng ``` cũng coi là trong khối
            else:
                self.in_fence.append(fenced)

    def allowed(self, index, rule):
        """Dòng ngay trên có `<!-- doc-lint: allow Rn -->` cho đúng rule này?"""
        if index == 0:
            return False
        found = ALLOW.search(self.lines[index - 1])
        return bool(found) and found.group(1) == rule

    def sections(self):
        """Sinh (tiêu đề thường-hoá, chỉ số dòng đầu, chỉ số dòng cuối) cho mỗi heading."""
        heads = []
        for i, line in enumerate(self.lines):
            if self.in_fence[i]:
                continue
            m = HEADING.match(line)
            if m:
                heads.append((len(m.group(1)), m.group(2).strip().lower(), i))
        for pos, (level, title, start) in enumerate(heads):
            end = len(self.lines)
            for next_level, _, next_start in heads[pos + 1:]:
                if next_level <= level:
                    end = next_start
                    break
            yield title, start, end


def _report(out, doc, index, rule, msg):
    if not doc.allowed(index, rule):
        out.append(f"{doc.path}:{index + 1}: [{rule}] {msg}")


def rule_r1(doc, out):
    """Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp."""
    for title, start, end in doc.sections():
        if not any(k in title for k in STEP_HEADINGS):
            continue
        expected = 1
        for i in range(start, end):
            if doc.in_fence[i]:
                continue
            m = STEP.match(doc.lines[i])
            if not m:
                continue
            got = int(m.group(1))
            if got != expected:
                _report(out, doc, i, "R1",
                        f"bước đánh số {got}, phải là {expected}")
                expected = got
            expected += 1


def rule_r2(doc, out):
    """Lệnh phải copy-paste được: trong khối ```, trong inline-code, hoặc ô bảng."""
    for i, line in enumerate(doc.lines):
        if doc.in_fence[i]:
            continue
        stripped = INLINE_CODE.sub("", line)
        if "python3" not in stripped and "tdq_state.py" not in stripped:
            continue
        if line.lstrip().startswith("|"):
            continue
        _report(out, doc, i, "R2",
                "lệnh nằm ngoài khối ``` / inline-code / bảng → không copy được")


def rule_r3(doc, out):
    """SKILL.md phải nói rõ khi nào xong và đi đâu tiếp."""
    if os.path.basename(doc.path) != "SKILL.md":
        return
    text = "\n".join(doc.lines)
    for needle in ("Xong khi:", "Bước kế tiếp:"):
        if needle not in text:
            out.append(f"{doc.path}:1: [R3] thiếu mốc `{needle}`")


def rule_r4(doc, out):
    """Từ mơ hồ trong mục bước/luật — trừ khi 3 dòng sau đã làm rõ bằng bảng hoặc `→`."""
    strict = set()
    for title, start, end in doc.sections():
        if any(k in title for k in STRICT_HEADINGS):
            strict.update(range(start, end))
    for i, line in enumerate(doc.lines):
        if i not in strict or doc.in_fence[i]:
            continue
        low = line.lower()
        hit = next((w for w in VAGUE if w in low), None)
        if not hit:
            continue
        after = doc.lines[i:i + 4]
        if any(x.lstrip().startswith("|") or "→" in x for x in after):
            continue
        _report(out, doc, i, "R4", f"từ mơ hồ \"{hit}\" — nêu điều kiện cụ thể")


def rule_r5(doc, out):
    """Câu quá dài thì model nhỏ đọc sai trọng tâm."""
    state = {"buf": [], "start": None}

    def flush():
        if state["buf"]:
            for sentence in SENTENCE_SPLIT.split(" ".join(state["buf"])):
                words = sentence.split()
                if len(words) > MAX_SENTENCE_WORDS:
                    _report(out, doc, state["start"], "R5",
                            f"câu {len(words)} từ (> {MAX_SENTENCE_WORDS}) — tách ra")
        state["buf"], state["start"] = [], None

    for i, line in enumerate(doc.lines):
        text = line.strip()
        if doc.in_fence[i] or not text or text.startswith(("|", "#", "```")):
            flush()
            continue
        # Dòng `allow` KHÔNG thuộc đoạn nào. Nuốt nó vào buffer thì state["start"]
        # trỏ vào chính comment, allowed() soi lên dòng trên nó → cửa thoát vô hiệu.
        if ALLOW.search(line):
            flush()
            continue
        # mỗi gạch đầu dòng / bước đánh số là một đơn vị đọc riêng
        if BULLET.match(line) or STEP.match(line):
            flush()
        if state["start"] is None:
            state["start"] = i
        state["buf"].append(INLINE_CODE.sub("", text))
    flush()


def rule_r6(doc, out):
    """Độ dài: SKILL.md theo ngưỡng riêng; mọi file ≤ 500 dòng."""
    count = len(doc.lines)
    if count > MAX_LINES_ANY:
        out.append(f"{doc.path}:1: [R6] {count} dòng > {MAX_LINES_ANY}")
    if os.path.basename(doc.path) != "SKILL.md":
        return
    skill = os.path.basename(os.path.dirname(doc.path))
    limit = SKILL_LINE_LIMITS.get(skill)
    if limit and count > limit:
        out.append(f"{doc.path}:1: [R6] {skill}: {count} dòng > trần {limit}")


def rule_r7(doc, out):
    """Skill sinh ra file cho user phải kèm mẫu output, không để tự bịa cấu trúc."""
    if os.path.basename(doc.path) != "SKILL.md":
        return
    skill = os.path.basename(os.path.dirname(doc.path))
    if skill not in NEEDS_TEMPLATE:
        return
    if not TEMPLATE_LINK.search("\n".join(doc.lines)):
        out.append(f"{doc.path}:1: [R7] thiếu link tới references/*template*.md")


# --------------------------------------------- R8: spec phải kiểm kê năng lực

# Phán quyết hợp lệ trong bảng §3b — tập đóng, cấm giá trị tự chế.
DECISIONS = ("DÙNG", "KHÔNG", "NỀN")
# 4 lý do loại đóng (khớp TIỀN TỐ — sau lý do được ghi thêm chi tiết).
CLOSED_REASONS = ("khác lĩnh vực", "spec §3 đã chọn cách khác tốt hơn",
                  "thiếu quyền/công cụ", "user đã cấm")
# 4 trường bắt buộc của khối hợp đồng trong plan (trường thứ 5 là chính dòng `Dùng:`).
# `Nạp` đã bỏ từ 2026-08-09: câu đường dẫn SKILL.md cho sub-agent dời vào `Để`.
CONTRACT_FIELDS = ("Để", "Ra", "Kiểm", "Không dùng cho")
CONTRACT_SCAN = 8   # các trường phải nằm trong 8 dòng ngay dưới dòng `Dùng:`


def _spec3b_rows(doc):
    """[(chỉ số dòng, cells)] của bảng §3b; None nếu spec không có mục 3b."""
    section = None
    for title, start, end in doc.sections():
        if title.replace(" ", "").startswith("3b"):
            section = (start, end)
            break
    if section is None:
        return None
    rows = []
    for i in range(*section):
        line = doc.lines[i].strip()
        if doc.in_fence[i] or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or set(cells[0]) <= set("-: ") or cells[2].lower() == "phán quyết":
            continue
        rows.append((i, cells))
    return rows


def rule_r8(doc, out):
    """File trong thư mục `spec/` phải có bảng §3b hợp lệ (kiểm kê năng lực)."""
    if os.path.basename(os.path.dirname(os.path.abspath(doc.path))) != "spec":
        return
    for line in doc.lines:
        found = ALLOW.search(line)
        if found and found.group(1) == "R8":
            return          # miễn trừ mức FILE — dành cho spec viết trước 0.3.3
    rows = _spec3b_rows(doc)
    if rows is None:
        out.append(f"{doc.path}:1: [R8] spec thiếu mục `## 3b. Năng lực & công cụ`")
        return
    if not rows:
        out.append(f"{doc.path}:1: [R8] bảng §3b không có dòng dữ liệu nào")
        return
    for i, cells in rows:
        decision = cells[2].replace("*", "").strip()
        if decision not in DECISIONS:
            _report(out, doc, i, "R8",
                    f"phán quyết \"{decision}\" — chỉ nhận DÙNG / KHÔNG / NỀN")
        elif decision == "KHÔNG" and not cells[3].strip().strip("`").startswith(CLOSED_REASONS):
            _report(out, doc, i, "R8", "lý do loại không thuộc 4 lý do đóng")


# ------------------------------------- R9: file luật phải đủ khuôn 3 mục (soul §3)

# Ba mục bắt buộc của một file luật — heading cấp 2, so không phân biệt hoa thường.
RULE_SECTIONS = ("khi nào áp dụng", "làm gì", "tự kiểm")
# Phạm vi R9 đóng đinh vào soul.md + thư viện rule; áp rộng hơn sẽ đỏ oan file cũ
# viết theo khuôn khác (spec 2026-08-14-set-soul-workflow §3).
RULES_DIR_MARK = f"{os.sep}references{os.sep}rules{os.sep}"
# Thêm ĐÚNG tên file, không mở cả `references/`: clean-code.md mất phần Tự kiểm dạng lệnh
# khi script scan cũ bị xoá, nên R9 gánh phần kiểm hình dạng bằng lệnh cho nó.
RULE_FILE_NAMES = ("soul.md", "clean-code.md")


def _r9_in_scope(path):
    abs_path = os.path.abspath(path)
    return os.path.basename(abs_path) in RULE_FILE_NAMES or RULES_DIR_MARK in abs_path


def rule_r9(doc, out):
    """soul.md + references/rules/*: đủ `## Khi nào áp dụng / Làm gì / Tự kiểm`."""
    if not _r9_in_scope(doc.path):
        return
    have = set()
    for i, line in enumerate(doc.lines):
        if doc.in_fence[i]:
            continue
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2:
            have.add(m.group(2).strip().lower())
    for need in RULE_SECTIONS:
        if need not in have:
            out.append(f"{doc.path}:1: [R9] file luật thiếu mục `## {need}` "
                       "— khuôn 3 mục là bắt buộc (soul nguyên tắc 3)")


# ------------------------- R10: spec lane full phải khai ranh giới module

# Nhận lane từ dòng header `... · Lane: full`. Chỉ lane full chịu luật này — lane quick
# cố ý bỏ mục ranh giới module, soi nó ở đó là báo nhầm.
LANE_RE = re.compile(r"Lane:\s*(full|quick)", re.IGNORECASE)
R10_HEADING = "2b. ranh giới module"


def _lane_cua_spec(doc):
    """Trả 'full' | 'quick' | None. None nghĩa là spec không khai lane."""
    for line in doc.lines[:15]:
        m = LANE_RE.search(line)
        if m:
            return m.group(1).lower()
    return None


def rule_r10(doc, out):
    """Spec lane full phải có `## 2b. Ranh giới module` — plan cắt task theo mục này."""
    if os.path.basename(os.path.dirname(os.path.abspath(doc.path))) != "spec":
        return
    if _lane_cua_spec(doc) != "full":
        return
    for line in doc.lines:
        found = ALLOW.search(line)
        if found and found.group(1) == "R10":
            return          # miễn trừ mức FILE — dành cho spec viết trước luật này
    for i, line in enumerate(doc.lines):
        if doc.in_fence[i]:
            continue
        m = HEADING.match(line)
        if m and m.group(2).strip().lower().startswith(R10_HEADING):
            return
    out.append(f"{doc.path}:1: [R10] spec lane full thiếu mục "
               "`## 2b. Ranh giới module` — plan không có đường cắt để chia task")


# --------------------- R11: spec không giữ lệnh kiểm, chỉ giữ điều kiện PASS

# Mốc ra luật. Spec có slug sớm hơn mốc này KHÔNG chịu R11: 42 spec cũ viết theo luật
# cũ, sửa chúng hay rải dòng miễn trừ vào chúng đều là đụng file ngoài phạm vi request.
R11_MOC = "2026-08-19"
# Dấu hiệu "đây là lệnh kiểm cụ thể" chứ không phải điều kiện PASS: đường dẫn file test,
# và cờ chọn test của pytest. Hai thứ này chỉ đúng SAU khi code tồn tại — viết vào spec
# (thứ bị niêm phong sha lúc duyệt) thì QC phát hiện sai tên là phải xin duyệt lại.
# Đo được: 2/7 ca ở docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md.
R11_DAU_HIEU = (
    (re.compile(r"tests?/[\w./-]*test_[\w.-]+\.py"), "đường dẫn file test"),
    (re.compile(r"(?<![\w-])-k\s+\S"), "cờ chọn test `-k`"),
)


def _slug_truoc_moc(path):
    """True khi tên file spec bắt đầu bằng ngày sớm hơn mốc ra luật."""
    ten = os.path.basename(path)
    return ten[:10] < R11_MOC if re.match(r"\d{4}-\d{2}-\d{2}", ten[:10]) else False


def rule_r11(doc, out):
    """Spec chỉ ghi ĐIỀU KIỆN PASS; lệnh kiểm cụ thể là việc của plan."""
    if os.path.basename(os.path.dirname(os.path.abspath(doc.path))) != "spec":
        return
    if _slug_truoc_moc(doc.path):
        return
    for i, line in enumerate(doc.lines):
        if ALLOW.search(doc.lines[i - 1]) if i else False:
            continue
        for mau, ten in R11_DAU_HIEU:
            if mau.search(line):
                _report(out, doc, i, "R11",
                        f"spec ghi {ten} — chuyển sang plan, spec chỉ giữ điều kiện PASS")
                break


RULES = [rule_r1, rule_r2, rule_r3, rule_r4, rule_r5, rule_r6, rule_r7, rule_r8,
         rule_r9, rule_r10, rule_r11]

# Thư mục chứa biên bản / file máy sinh — chỉ chịu R8, xem lint_file().
OUTPUT_DIRS = (os.path.join("docs", "tdq"), os.path.join("docs", "workinglog"),
               "graphify-out")


def _plan_contracts(lines):
    """{tên skill: (chỉ số dòng, tập trường có mặt)} từ các khối `- Dùng:` trong plan."""
    blocks = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- Dùng:"):
            continue
        name = stripped[len("- Dùng:"):].strip()
        if name.endswith("(mcp)"):
            name = name[: -len("(mcp)")].strip()
        name = name.strip("`*")
        fields = set()
        for j in range(i + 1, min(i + 1 + CONTRACT_SCAN, len(lines))):
            body = lines[j].strip()
            if body.startswith("- Dùng:"):
                break
            for field in CONTRACT_FIELDS:
                if body.startswith(f"- {field}:"):
                    fields.add(field)
        if name and name not in blocks:
            blocks[name] = (i, fields)
    return blocks


def pair(spec_path, plan_path):
    """Mỗi dòng DÙNG ở spec §3b phải có khối hợp đồng đủ 6 trường trong plan."""
    _log(f"đối chiếu cặp {os.path.basename(spec_path)} ↔ {os.path.basename(plan_path)}")
    try:
        spec = Doc(spec_path)
        with open(plan_path, encoding="utf-8") as f:
            plan_lines = f.read().splitlines()
    except OSError as exc:
        print(f"--pair: không đọc được file ({exc})", file=sys.stderr)
        return 1
    rows = _spec3b_rows(spec)
    if not rows:
        print(f"{spec_path}:1: [R8] spec không có bảng §3b để đối chiếu")
        return 1
    blocks = _plan_contracts(plan_lines)
    problems = []
    # Mục cụm song song là BẮT BUỘC ở mọi plan, mọi mode: tính modular là thuộc tính của
    # tài liệu, không phải của mode thi hành. Thiếu mục này thì `tdq_team.py` không có gì
    # để đọc, và plan mất luôn đường cắt song song.
    if not any(l.strip().lower().startswith("## cụm song song") for l in plan_lines):
        problems.append(f"{plan_path}:1: [R8] plan thiếu mục `## Cụm song song` "
                        "— bắt buộc ở mọi plan, viết \"một cụm vì <lý do>\" vẫn hợp lệ")
    for i, cells in rows:
        if cells[2].replace("*", "").strip() != "DÙNG":
            continue
        skill = cells[0].replace("*", "").strip().strip("`")
        if skill not in blocks:
            problems.append(f"{plan_path}:1: [R8] skill {skill} chưa có khối hợp đồng trong plan")
            continue
        line_no, fields = blocks[skill]
        for field in CONTRACT_FIELDS:
            if field not in fields:
                problems.append(f"{plan_path}:{line_no + 1}: [R8] skill {skill} thiếu trường {field}")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def lint_file(path):
    doc = Doc(path)
    out = []
    # R1–R7 viết cho DOC HƯỚNG DẪN (skills/). Các thư mục ở OUTPUT_DIRS chứa biên bản
    # và file máy sinh — trích nguyên văn lời user, output test, report của graphify —
    # không được sửa để chiều luật văn phong. Chúng chỉ chịu R8, và R8 tự giới hạn ở
    # thư mục spec/.
    abs_path = os.path.abspath(path)
    is_output = any(f"{os.sep}{d}{os.sep}" in abs_path for d in OUTPUT_DIRS)
    for rule in ([rule_r8, rule_r10, rule_r11] if is_output else RULES):
        rule(doc, out)
    return out


def collect(paths):
    files = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, _, names in os.walk(path):
                files += [os.path.join(dirpath, n) for n in sorted(names)
                          if n.endswith(".md")]
        elif path.endswith(".md"):
            files.append(path)
    return sorted(set(files))


def main(argv):
    if argv and argv[0] == "--pair":
        if len(argv) != 3:
            print("Cách dùng: doc_lint.py --pair <spec.md> <plan.md>", file=sys.stderr)
            return EXIT_SYNTAX
        return pair(argv[1], argv[2])
    if not argv:
        print("Cách dùng: doc_lint.py <file.md hoặc thư mục> | --pair <spec> <plan>",
              file=sys.stderr)
        return EXIT_SYNTAX
    # A19: path ma từng bị collect() bỏ lặng → exit 0 giả sạch. Chặn ngay đầu.
    missing = [p for p in argv if not os.path.exists(p)]
    if missing:
        for p in missing:
            print(f"⚠️ không tìm thấy: {p}", file=sys.stderr)
        return EXIT_SYNTAX
    paths = collect(argv)
    _log(f"lint {len(paths)} file: {', '.join(os.path.basename(p) for p in paths)}")
    problems = []
    for path in paths:
        loi = lint_file(path)
        if loi:
            _log(f"{os.path.basename(path)} → {len(loi)} vi phạm")
        problems += loi
    for line in problems:
        print(line)
    _log(f"xong — tổng {len(problems)} vi phạm, exit {1 if problems else 0}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
