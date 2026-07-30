#!/usr/bin/env python3
"""Lint doc hướng dẫn của TDQ workflow (spec §2.6).

Mục đích: giữ skill/portable ở dạng mà một model nhỏ vẫn đọc và làm đúng —
bước đánh số liên tục, lệnh copy-paste được, có điều kiện ra, không có từ mơ hồ.

Cách dùng:
    python3 scripts/doc_lint.py skills portable
    python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md

In `file:line: [RULE] mô tả`; exit 1 nếu có vi phạm, 0 nếu sạch, 2 nếu sai cú pháp.
Tắt một rule cho một dòng: đặt `<!-- doc-lint: allow R4 -->` ở dòng NGAY TRÊN nó.
"""
import os
import re
import sys

EXIT_SYNTAX = 2

# Trần số dòng của SKILL.md theo tên skill (spec §2.4). Test dùng chung hằng này.
SKILL_LINE_LIMITS = {
    "tdq-intake": 120,
    "tdq-spec": 100,
    "tdq-plan": 100,
    "tdq-build": 150,
    "tdq-status": 60,
    "tdq-conventions": 120,
}
MAX_LINES_ANY = 500
MAX_SENTENCE_WORDS = 40
# skill phải trỏ tới ít nhất một file mẫu output
NEEDS_TEMPLATE = ("tdq-spec", "tdq-plan", "tdq-build")

HEADING = re.compile(r"^(#+)\s+(.*)$")
STEP = re.compile(r"^(\d+)\.\s+\S")
FENCE = re.compile(r"^\s*```")
ALLOW = re.compile(r"<!--\s*doc-lint:\s*allow\s+(R\d)\s*-->")
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
        with open(path, encoding="utf-8") as f:
            self.lines = f.read().splitlines()
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
    """SKILL.md và file phase portable phải nói rõ khi nào xong và đi đâu tiếp."""
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
# 5 trường bắt buộc của khối hợp đồng trong plan (trường thứ 6 là chính dòng `Dùng:`).
CONTRACT_FIELDS = ("Nạp", "Để", "Ra", "Kiểm", "Không dùng cho")
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


RULES = [rule_r1, rule_r2, rule_r3, rule_r4, rule_r5, rule_r6, rule_r7, rule_r8]


def _plan_contracts(lines):
    """{tên skill: (chỉ số dòng, tập trường có mặt)} từ các khối `- Dùng:` trong plan."""
    blocks = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- Dùng:"):
            continue
        name = stripped[len("- Dùng:"):].strip().strip("`*")
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
    # R1–R7 viết cho DOC HƯỚNG DẪN (skills/, portable/). Spec của project là tài liệu
    # nghiệp vụ — chỉ chịu R8 (kiểm kê năng lực), không bị ép văn phong hồi tố.
    in_spec_dir = os.path.basename(os.path.dirname(os.path.abspath(path))) == "spec"
    for rule in ([rule_r8] if in_spec_dir else RULES):
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
    problems = []
    for path in collect(argv):
        problems += lint_file(path)
    for line in problems:
        print(line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
