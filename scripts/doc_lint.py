#!/usr/bin/env python3
"""Lint the instruction docs of the TDQ workflow (spec §2.6).

Purpose: keep every skill in a shape a small model still reads and follows —
unbroken step numbering, copy-pasteable commands, an exit condition, no vague words.

Usage:
    python3 scripts/doc_lint.py skills
    python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md

Prints `file:line: [RULE] description`; exit 1 on violations, 0 when clean, 2 on bad syntax.
Silence one rule for one line: put `<!-- doc-lint: allow R4 -->` on the line RIGHT ABOVE it.
Env: TDQ_LOG=0 turns the log service off (on by default, one ISO-timestamped line to stderr).
"""
import json
import os
import re
import sys
from datetime import datetime

EXIT_SYNTAX = 2


def _log(message):
    """Log service: one ISO-timestamped line to stderr. Silenced by TDQ_LOG=0.

    To stderr and not stdout: stdout is this linter's machine-read channel
    (`file:line: [RULE]`), and mixing the log into it breaks the contract with callers.
    """
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now().isoformat(timespec='seconds')}] doc_lint: {message}",
              file=sys.stderr)

# The line cap of a SKILL.md by skill name (spec §2.4). The tests share this constant.
SKILL_LINE_LIMITS = {
    "tdq-intake": 120,
    "tdq-spec": 100,
    # 2026-08-18: 100 → 110. The mode proposal moved from eyeballing the task count to
    # running `tdq_bench.py simulate` — the command block plus the reason for factor 1.5
    # must sit in the skill body to be read every time a plan is written.
    "tdq-plan": 110,
    "tdq-build": 150,
    "tdq-status": 60,
    # 2026-08-23: new skill. The setup ladder plus the runbook for re-configuring a machine
    # are read whole when the ladder reports a missing rung, so they stay in the body.
    "tdq-lsp-setup": 120,
    # 2026-08-15: 120 → 130. The one-sweep rule (§10) is a runtime-tier rule, so it has to
    # sit in the skill body to be loaded every turn. Soul ranks runtime above context cost,
    # hence 10 more lines to keep the rule readable instead of squeezing it to fit.
    # 2026-08-16: 130 → 133. Clean code dropped its question gate and its scan script, so the
    # SOLID rule only survives if §11 loads it every turn — 3 loading lines in the body, the
    # detail in references.
    # 2026-08-17: 133 → 143. Team mode added 2 runtime-tier rules to §1 (closing the books
    # several times inside one long turn; never ending a turn while the plan still has tasks,
    # plus its 3 exceptions). Both must be readable every turn; pushing them down into
    # references would neuter them.
    # 2026-08-19: 143 → 145. Direction C lifted `plugin-routing.md` and `measure-scenario.md`
    # to tier 1: no SKILL.md pointed at those two files before, so they were reachable only
    # through another reference — exactly where a model reads half of it. The price is 2
    # pointer lines in the skill body.
    # 2026-08-22: 145 → 165. The three-layer language rule (rules · machine strings · documents
    # and dialogue following `doc_lang`) is tier 1: a model that never reads it writes the
    # user's documents in the language of the rule files. Its table plus the fallback rule cost
    # 20 lines in the body.
    # 2026-09-02: 165 → 168. Four rules moved OUT of `~/.claude/CLAUDE.md` and into this body
    # (§7 the git-init allowance and the sole commit exception; §8 the mem0 search-then-store
    # rule). They cost 4 lines here but leave a file loaded on EVERY turn of EVERY project —
    # a net cut. Plan: docs/tdq/plan/2026-09-01-2355-thi-hanh-cat-instruction.md
    # 2026-09-03: 168 → 177. The `Next step:` rule (every such line names the phase that comes
    # next) is the fallback layer for hosts with no hooks — Gemini CLI, Copilot CLI, Aider see
    # the skill text and nothing else. A rule about what every skill body must say cannot live
    # in a reference the host may never open.
    # Plan: docs/tdq/plan/2026-09-03-1220-gate-chat-va-next-pha.md
    "tdq-conventions": 177,
    # The recovery skill: its 7 steps plus the hard "lose no data" rule block must sit in the
    # skill body, because a weak model that skips the reference runs the very command that
    # destroys the whole request.
    "tdq-check-status": 80,
}
MAX_LINES_ANY = 500
MAX_SENTENCE_WORDS = 40
# a skill must point at at least one output-template file
NEEDS_TEMPLATE = ("tdq-spec", "tdq-plan", "tdq-build")

HEADING = re.compile(r"^(#+)\s+(.*)$")
STEP = re.compile(r"^(\d+)\.\s+\S")
FENCE = re.compile(r"^\s*```")
# 2026-08-18: `(R\d)` → `(R\d+)` because rule codes reached two digits (R10), and a reason
# may follow the code — a bare allow leaves no trace of why the exemption exists.
ALLOW = re.compile(r"<!--\s*doc-lint:\s*allow\s+(R\d+)[^>]*-->")
INLINE_CODE = re.compile(r"`[^`]*`")
# An HTML comment is not prose: it is a note for whoever edits the file, and no reader
# parses it as a sentence. Counting it under R5 would add ~8 words per i18n-allow label.
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
TEMPLATE_LINK = re.compile(r"references/[^)\s]*template[^)\s]*\.md")
# `·` and `;` separate items in these docs — each item reads on its own
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+|\s*[·;]\s*")
BULLET = re.compile(r"^\s*[-*]\s+\S")
VAGUE = ["nếu cần", "tùy ý", "tuỳ ý", "nên cân nhắc", "linh hoạt", "tự quyết"]  # i18n-allow
# headings of the "mandatory" sections — R1 scans step sections only, R4 scans rule sections too
STEP_HEADINGS = ("các bước", "steps")  # i18n-allow
STRICT_HEADINGS = STEP_HEADINGS + ("phần ", "luật", "giao thức")  # i18n-allow


class Doc:
    """One markdown file, pre-split: lines, fenced regions, headings."""

    def __init__(self, path):
        self.path = path
        try:
            with open(path, encoding="utf-8") as f:
                self.lines = f.read().splitlines()
        except OSError as exc:
            # A20: a vanished/unreadable file → a message, not a raw traceback
            sys.exit(f"⚠️ cannot read {path}: {exc}")
        self.in_fence = []
        fenced = False
        for line in self.lines:
            if FENCE.match(line):
                fenced = not fenced
                self.in_fence.append(True)  # the ``` line itself counts as inside the block
            else:
                self.in_fence.append(fenced)

    def allowed(self, index, rule):
        """Does the line right above carry `<!-- doc-lint: allow Rn -->` for this very rule?"""
        if index == 0:
            return False
        found = ALLOW.search(self.lines[index - 1])
        return bool(found) and found.group(1) == rule

    def sections(self):
        """Yield (normalised title, first line index, last line index) for every heading."""
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
    """Steps in the 'steps' section must run 1, 2, 3… with no jump and no repeat."""
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
                        f"step numbered {got}, expected {expected}")
                expected = got
            expected += 1


def rule_r2(doc, out):
    """A command must be copy-pasteable: inside a ``` block, inline code, or a table cell."""
    for i, line in enumerate(doc.lines):
        if doc.in_fence[i]:
            continue
        stripped = INLINE_CODE.sub("", line)
        if "python3" not in stripped and "tdq_state.py" not in stripped:
            continue
        if line.lstrip().startswith("|"):
            continue
        _report(out, doc, i, "R2",
                "command outside a ``` block / inline code / table → cannot be copied")


# Each pair is one marker with the wordings accepted for it: the English one the rules are
# written in today, and the Vietnamese one every skill carried before the rules were converted.
# Either wording satisfies the rule — a bundle built from an older skill must not turn red.
R3_MARKERS = (("Done when:", "Xong khi:"),          # i18n-allow
              ("Next step:", "Bước kế tiếp:"))      # i18n-allow


def rule_r3(doc, out):
    """A SKILL.md must state when it is done and where to go next."""
    if os.path.basename(doc.path) != "SKILL.md":
        return
    text = "\n".join(doc.lines)
    for wordings in R3_MARKERS:
        if not any(needle in text for needle in wordings):
            out.append(f"{doc.path}:1: [R3] missing the marker `{wordings[0]}`")


def rule_r4(doc, out):
    """A vague word in a step/rule section — unless the next 3 lines pin it down with a table or `→`."""
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
        _report(out, doc, i, "R4", f"vague word \"{hit}\" — state the concrete condition")


def rule_r5(doc, out):
    """An over-long sentence makes a small model read the wrong emphasis."""
    state = {"buf": [], "start": None}

    def flush():
        if state["buf"]:
            for sentence in SENTENCE_SPLIT.split(" ".join(state["buf"])):
                words = sentence.split()
                if len(words) > MAX_SENTENCE_WORDS:
                    _report(out, doc, state["start"], "R5",
                            f"sentence of {len(words)} words (> {MAX_SENTENCE_WORDS}) — split it")
        state["buf"], state["start"] = [], None

    for i, line in enumerate(doc.lines):
        text = line.strip()
        if doc.in_fence[i] or not text or text.startswith(("|", "#", "```")):
            flush()
            continue
        # An `allow` line belongs to NO paragraph. Swallowing it into the buffer points
        # state["start"] at the comment itself, so allowed() looks one line higher and the
        # escape hatch stops working.
        if ALLOW.search(line):
            flush()
            continue
        # every bullet / numbered step is its own reading unit
        if BULLET.match(line) or STEP.match(line):
            flush()
        if state["start"] is None:
            state["start"] = i
        state["buf"].append(INLINE_CODE.sub("", HTML_COMMENT.sub("", text)))
    flush()


def rule_r6(doc, out):
    """Length: a SKILL.md has its own cap; every file stays <= 500 lines."""
    count = len(doc.lines)
    if count > MAX_LINES_ANY:
        out.append(f"{doc.path}:1: [R6] {count} lines > {MAX_LINES_ANY}")
    if os.path.basename(doc.path) != "SKILL.md":
        return
    skill = os.path.basename(os.path.dirname(doc.path))
    limit = SKILL_LINE_LIMITS.get(skill)
    if limit and count > limit:
        out.append(f"{doc.path}:1: [R6] {skill}: {count} lines > the cap of {limit}")


def rule_r7(doc, out):
    """A skill that produces a file for the user must ship an output template, not leave the shape to invention."""
    if os.path.basename(doc.path) != "SKILL.md":
        return
    skill = os.path.basename(os.path.dirname(doc.path))
    if skill not in NEEDS_TEMPLATE:
        return
    if not TEMPLATE_LINK.search("\n".join(doc.lines)):
        out.append(f"{doc.path}:1: [R7] missing a link to references/*template*.md")


# --------------------------------------------- R8: a spec must inventory its capabilities

# The verdicts allowed in the §3b table — a closed set, no invented values.
DECISIONS = ("DÙNG", "KHÔNG", "NỀN")  # i18n-allow
# The 4 closed rejection reasons (matched as a PREFIX — detail may follow the reason).
CLOSED_REASONS = ("khác lĩnh vực", "spec §3 đã chọn cách khác tốt hơn",  # i18n-allow
                  "thiếu quyền/công cụ", "user đã cấm")  # i18n-allow
# The 4 mandatory fields of a contract block in the plan (the 5th is the `Dùng:` line itself).  # i18n-allow
# `Nạp` was dropped on 2026-08-09: the path sentence for sub-agents moved into `Để`.  # i18n-allow
CONTRACT_FIELDS = ("Để", "Ra", "Kiểm", "Không dùng cho")  # i18n-allow
CONTRACT_SCAN = 8   # the fields must sit within the 8 lines below the `Dùng:` line  # i18n-allow


def _spec3b_rows(doc):
    """[(line index, cells)] of the §3b table; None when the spec has no 3b section."""
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
        if len(cells) < 4 or set(cells[0]) <= set("-: ") or cells[2].lower() == "phán quyết":  # i18n-allow
            continue
        rows.append((i, cells))
    return rows


def rule_r8(doc, out):
    """A file under `spec/` must carry a valid §3b table (the capability inventory)."""
    if os.path.basename(os.path.dirname(os.path.abspath(doc.path))) != "spec":
        return
    for line in doc.lines:
        found = ALLOW.search(line)
        if found and found.group(1) == "R8":
            return          # FILE-level exemption — for specs written before 0.3.3
    rows = _spec3b_rows(doc)
    if rows is None:
        out.append(f"{doc.path}:1: [R8] spec missing the section `## 3b. Năng lực & công cụ`")  # i18n-allow
        return
    if not rows:
        out.append(f"{doc.path}:1: [R8] the §3b table holds no data row")
        return
    for i, cells in rows:
        decision = cells[2].replace("*", "").strip()
        if decision not in DECISIONS:
            _report(out, doc, i, "R8",
                    f"verdict \"{decision}\" — only DÙNG / KHÔNG / NỀN are accepted")  # i18n-allow
        elif decision == "KHÔNG" and not cells[3].strip().strip("`").startswith(CLOSED_REASONS):  # i18n-allow
            _report(out, doc, i, "R8", "the rejection reason is not one of the 4 closed reasons")


# ------------------------------------- R9: a rule file must carry the full 3-section shape (soul §3)

# The 3 mandatory sections of a rule file — level-2 headings, compared case-insensitively.
# Each entry lists the wordings of ONE section. Rule bodies are English from 2026-08-22,
# while older rule files still carry the Vietnamese headings — either wording satisfies R9.
RULE_SECTIONS = (("when it applies", "khi nào áp dụng"),  # i18n-allow
                 ("what to do", "làm gì"),  # i18n-allow
                 ("self-check", "tự kiểm"))  # i18n-allow
# R9 is nailed to soul.md + the rule library; a wider scope would wrongly redden old files
# written to another shape (spec 2026-08-14-set-soul-workflow §3).
RULES_DIR_MARK = f"{os.sep}references{os.sep}rules{os.sep}"
# Add EXACTLY the file name, never open all of `references/`: clean-code.md lost its
# command-shaped self-check when the old scan script was deleted, so R9 carries that check.
RULE_FILE_NAMES = ("soul.md", "clean-code.md")


def _r9_in_scope(path):
    abs_path = os.path.abspath(path)
    return os.path.basename(abs_path) in RULE_FILE_NAMES or RULES_DIR_MARK in abs_path


def rule_r9(doc, out):
    """soul.md + references/rules/*: all 3 mandatory `##` sections present."""
    if not _r9_in_scope(doc.path):
        return
    have = set()
    for i, line in enumerate(doc.lines):
        if doc.in_fence[i]:
            continue
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2:
            have.add(m.group(2).strip().lower())
    for wordings in RULE_SECTIONS:
        if not any(need in have for need in wordings):
            out.append(f"{doc.path}:1: [R9] rule file missing the section `## {wordings[0]}` "
                       "— the 3-section shape is mandatory (soul principle 3)")


# ------------------------- R10: a lane-full spec must declare its module boundaries

# Reads the lane off the header line `... · Lane: full`. Only lane full is bound by this rule —
# lane quick drops the module-boundary section on purpose, so checking it there is a false alarm.
LANE_RE = re.compile(r"Lane:\s*(full|quick)", re.IGNORECASE)
R10_HEADING = "2b. ranh giới module"  # i18n-allow


def _lane_cua_spec(doc):
    """Returns 'full' | 'quick' | None. None means the spec declares no lane."""
    for line in doc.lines[:15]:
        m = LANE_RE.search(line)
        if m:
            return m.group(1).lower()
    return None


def rule_r10(doc, out):
    """A lane-full spec needs `## 2b. Ranh giới module` — the plan cuts tasks along it."""  # i18n-allow
    if os.path.basename(os.path.dirname(os.path.abspath(doc.path))) != "spec":
        return
    if _lane_cua_spec(doc) != "full":
        return
    for line in doc.lines:
        found = ALLOW.search(line)
        if found and found.group(1) == "R10":
            return          # FILE-level exemption — for specs written before this rule
    for i, line in enumerate(doc.lines):
        if doc.in_fence[i]:
            continue
        m = HEADING.match(line)
        if m and m.group(2).strip().lower().startswith(R10_HEADING):
            return
    out.append(f"{doc.path}:1: [R10] lane-full spec is missing the section "
               "`## 2b. Ranh giới module` — the plan has no cut line to split tasks")  # i18n-allow


# --------------------- R11: a spec holds no check command, only the PASS condition

# The day the rule landed. A spec whose slug predates it is NOT bound by R11: 42 old specs
# follow the old rule, and editing them or sprinkling exemption lines into them would touch
# files outside the request.
R11_MOC = "2026-08-19"
# The signs of "this is a concrete check command" rather than a PASS condition: a test file
# path, and pytest's selection flag. Both are only correct AFTER the code exists — put them in
# the spec (sealed with a sha at approval) and a wrong name found at QC forces a re-approval.
# Measured: 2 of 7 cases in docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md.
R11_DAU_HIEU = (
    (re.compile(r"tests?/[\w./-]*test_[\w.-]+\.py"), "a test file path"),
    (re.compile(r"(?<![\w-])-k\s+\S"), "the test selection flag `-k`"),
)


def _slug_truoc_moc(path):
    """True when the spec file name starts with a date earlier than the rule landing day."""
    ten = os.path.basename(path)
    return ten[:10] < R11_MOC if re.match(r"\d{4}-\d{2}-\d{2}", ten[:10]) else False


def rule_r11(doc, out):
    """A spec states the PASS CONDITION only; the concrete check command belongs to the plan."""
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
                        f"the spec carries {ten} — move it to the plan, a spec holds PASS conditions only")
                break


RULES = [rule_r1, rule_r2, rule_r3, rule_r4, rule_r5, rule_r6, rule_r7, rule_r8,
         rule_r9, rule_r10, rule_r11]

# Directories holding records / machine-generated files — bound by R8 only, see lint_file().
OUTPUT_DIRS = (os.path.join("docs", "tdq"), os.path.join("docs", "workinglog"),
               "graphify-out")


def _plan_contracts(lines):
    """{skill name: (line index, set of fields present)} from the `- Dùng:` blocks of a plan."""  # i18n-allow
    blocks = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- Dùng:"):  # i18n-allow
            continue
        name = stripped[len("- Dùng:"):].strip()  # i18n-allow
        if name.endswith("(mcp)"):
            name = name[: -len("(mcp)")].strip()
        name = name.strip("`*")
        fields = set()
        for j in range(i + 1, min(i + 1 + CONTRACT_SCAN, len(lines))):
            body = lines[j].strip()
            if body.startswith("- Dùng:"):  # i18n-allow
                break
            for field in CONTRACT_FIELDS:
                if body.startswith(f"- {field}:"):
                    fields.add(field)
        if name and name not in blocks:
            blocks[name] = (i, fields)
    return blocks


def pair(spec_path, plan_path):
    """Every DÙNG row of spec §3b needs a full contract block in the plan."""  # i18n-allow
    _log(f"pairing {os.path.basename(spec_path)} ↔ {os.path.basename(plan_path)}")
    try:
        spec = Doc(spec_path)
        with open(plan_path, encoding="utf-8") as f:
            plan_lines = f.read().splitlines()
    except OSError as exc:
        print(f"--pair: cannot read the file ({exc})", file=sys.stderr)
        return 1
    rows = _spec3b_rows(spec)
    if not rows:
        print(f"{spec_path}:1: [R8] the spec has no §3b table to pair against")
        return 1
    blocks = _plan_contracts(plan_lines)
    problems = []
    # The parallel-cluster section is MANDATORY in every plan, every mode: modularity is a
    # property of the DOCUMENT, not of the run mode. Without it `tdq_team.py` has nothing to
    # read, and the plan loses its parallel cut lines altogether.
    if not any(l.strip().lower().startswith("## cụm song song") for l in plan_lines):  # i18n-allow
        problems.append(f"{plan_path}:1: [R8] plan missing the section `## Cụm song song` "  # i18n-allow
                        "— mandatory in every plan; \"một cụm vì <lý do>\" is still valid")  # i18n-allow
    for i, cells in rows:
        if cells[2].replace("*", "").strip() != "DÙNG":  # i18n-allow
            continue
        skill = cells[0].replace("*", "").strip().strip("`")
        if skill not in blocks:
            problems.append(f"{plan_path}:1: [R8] skill {skill} has no contract block in the plan")
            continue
        line_no, fields = blocks[skill]
        for field in CONTRACT_FIELDS:
            if field not in fields:
                problems.append(f"{plan_path}:{line_no + 1}: [R8] skill {skill} missing the field {field}")
    for problem in problems:
        print(problem)
    return 1 if problems else 0



# --------------------- R12: a file produced for the user must be written in Vietnamese

# The output-language gate. It is the precondition of direction A (rules written in English):
# that move is only safe while something MEASURES that the output for the user does not drift
# into English along with the rules. It inspects the produced FILE, not what the model prints to
# chat — the hook deliberately never reads the transcript (hooks/scripts/stop_gate.py:5); version
# 0.1.8 did read it and blocked valid turns by mistake.
# The only language this rule can measure: its detector is the Vietnamese diacritic alphabet.
R12_LANG = "vi"
R12_DAU_TV = re.compile(
    "[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]",  # i18n-allow
    re.IGNORECASE)
# Stripped before counting: backticked identifiers, URLs, markdown link targets. Those are almost
# always English and legitimately present in every Vietnamese report.
R12_INLINE = re.compile(r"`[^`]*`|https?://\S+|\[[^\]]*\]\([^)]*\)")
R12_TU = re.compile(r"[A-Za-zÀ-ỹ][A-Za-zÀ-ỹ'’-]*")  # i18n-allow
# Below the word threshold sit labels, table cells, constant names — too few words to judge a language.
R12_TOI_THIEU_TU = 6
# One stray sentence is not evidence; three prose lines in a row make a paragraph.
R12_TOI_THIEU_DONG = 3


def _r12_van_xuoi(line):
    """None = does not qualify as prose (breaks the run). True/False = carries Vietnamese marks or not."""
    text = R12_INLINE.sub(" ", line)
    if text.strip().startswith(("|", ">", "#", "-", "*", "<!--")):
        return None
    if len(R12_TU.findall(text)) < R12_TOI_THIEU_TU:
        return None
    return bool(R12_DAU_TV.search(text))


def _doc_lang(path):
    """The `doc_lang` of the request owning this file, or the default when there is no state.

    Read from `docs/tdq/state.json` of the nearest enclosing project. Only the state
    knows which language the user reads; the file itself cannot say.
    """
    goc = os.path.abspath(os.environ.get("TDQ_PROJECT_DIR") or os.path.dirname(path) or ".")
    while True:
        state = os.path.join(goc, "docs", "tdq", "state.json")
        if os.path.isfile(state):
            try:
                with open(state, encoding="utf-8") as f:
                    return (json.load(f).get("doc_lang") or R12_LANG).strip().lower()
            except (OSError, ValueError, AttributeError):
                return R12_LANG
        cha = os.path.dirname(goc)
        if cha == goc:
            return R12_LANG
        goc = cha


def rule_r12(doc, out):
    """A long prose paragraph in the wrong language → reported once, on its first line.

    The detector reads Vietnamese diacritics, so it can only judge Vietnamese: the rule runs
    when `doc_lang` is `vi` and stands down for every other language, where a wrong-language
    paragraph is not measurable by a machine and QC reads it instead.
    """
    if _doc_lang(doc.path) != R12_LANG:
        return
    dau = None
    dai = 0
    for i, line in enumerate(doc.lines + [""]):
        co_dau = None if i >= len(doc.lines) or doc.in_fence[i] else _r12_van_xuoi(line)
        if co_dau is False:
            if dau is None:
                dau = i
            dai += 1
            continue
        if dau is not None and dai >= R12_TOI_THIEU_DONG and not doc.allowed(dau, "R12"):
            out.append(f"{doc.path}:{dau + 1}: [R12] paragraph with no Vietnamese diacritic "
                       f"({dai} lines) — a file produced for the user must be written in Vietnamese")
        dau = None
        dai = 0


def lint_file(path):
    doc = Doc(path)
    out = []
# R1–R7 are written for INSTRUCTION DOCS (skills/). The directories in OUTPUT_DIRS hold
# records and machine-generated files — the user's verbatim words, test output, graphify
# reports — which must not be reshaped to please a style rule. They are bound by R8 only,
# and R8 limits itself to the spec/ directory.
    abs_path = os.path.abspath(path)
    is_output = any(f"{os.sep}{d}{os.sep}" in abs_path for d in OUTPUT_DIRS)
    if is_output:
        for rule in (rule_r8, rule_r10, rule_r11, rule_r12):
            rule(doc, out)
    else:
        for rule in RULES:
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
            print("Usage: doc_lint.py --pair <spec.md> <plan.md>", file=sys.stderr)
            return EXIT_SYNTAX
        return pair(argv[1], argv[2])
    if not argv:
        print("Usage: doc_lint.py <file.md or directory> | --pair <spec> <plan>",
              file=sys.stderr)
        return EXIT_SYNTAX
    # A19: a ghost path used to be dropped silently by collect() → a fake clean exit 0. Stopped up front.
    missing = [p for p in argv if not os.path.exists(p)]
    if missing:
        for p in missing:
            print(f"⚠️ not found: {p}", file=sys.stderr)
        return EXIT_SYNTAX
    paths = collect(argv)
    _log(f"lint {len(paths)} file: {', '.join(os.path.basename(p) for p in paths)}")
    problems = []
    for path in paths:
        loi = lint_file(path)
        if loi:
            _log(f"{os.path.basename(path)} → {len(loi)} violation(s)")
        problems += loi
    for line in problems:
        print(line)
    _log(f"done — {len(problems)} violation(s) total, exit {1 if problems else 0}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
