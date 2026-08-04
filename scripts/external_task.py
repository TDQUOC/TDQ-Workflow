#!/usr/bin/env python3
"""external_task.py — chạy task/gói plan qua engine ngoài (codex | agy).

`run` chạy một task (quick lane); `run-plan` giao CẢ GÓI plan/phase/fix trong một
lần gọi (lane full — spec 2026-08-03-check-external-assign-flow); `split-plan`
chia plan >6 task theo ranh giới phase; `fix-rounds` là sổ đếm vòng mini-plan fix
(≤2 vòng rồi fallback Claude).

Lõi của mode thực thi `external`: ôm trọn phần dễ sai (build lệnh CLI đúng flag,
timeout, parse/validate JSON theo schema, retry kèm feedback lỗi, log service,
ghi report) để agent runner — kể cả model cấp thấp — chỉ cần chạy đúng MỘT lệnh
rồi đọc JSON kết quả.

Cách dùng:
  external_task.py run --engine <codex|agy> --model <slug> --task-file <gói.md>
                       --worktree <dir> --slug <slug>
      → chạy engine tối đa 3 attempt, ghi report docs/tdq/external/<slug>/<task-id>.json
        (tính từ cwd), in report ra stdout. exit 0 = report hợp lệ, exit 1 = hỏng.
  external_task.py parse-plan <plan-file>
      → in JSON {"engine": ..., "models": {"khó":…, "TB":…, "dễ":…}} từ dòng
        `Thực thi external: engine=<codex|agy> · khó=<slug> [· TB=<slug>] [· dễ=<slug>]`.

Env: TDQ_EXTERNAL_TIMEOUT (giây/attempt, mặc định 540) · TDQ_EXTERNAL_LOG=0 tắt log.
"""
import datetime
import json
import os
import re
import subprocess
import sys

ENGINES = ("codex", "agy")
MAX_ATTEMPTS = 3
PLAN_MAX_ATTEMPTS = 2   # run-plan: gói dài, 2 attempt là trần (spec §3)
PLAN_TIMEOUT_CAP = 3600
MAX_TASKS_PER_PACKET = 6
MAX_FIX_ROUNDS = 2
DEFAULT_TIMEOUT = 540
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(SCRIPT_DIR, "external_report_schema.json")

# Trường bắt buộc: (tên, kiểu). files_changed kiểm riêng từng phần tử.
_REQUIRED = (
    ("task_id", str), ("status", str), ("files_changed", list),
    ("test_cmd", str), ("test_result", str), ("notes", str),
)
_OPTIONAL = {"fallback": ("claude",), "kind": ("task",)}
_STATUS = ("done", "blocked")
_PLAN_REQUIRED = (("kind", str), ("status", str), ("tasks", list), ("notes", str))

USAGE = ("usage: external_task.py run|run-plan --engine <codex|agy> --model <slug> "
         "--task-file <f> --worktree <dir> --slug <slug> [--round <n>] "
         "[--plan-file <plan>] "
         "| parse-plan <plan-file> | split-plan <plan-file> "
         "| skill-dump <tên>... "
         "| fix-rounds add|status --slug <slug> [--tasks a,b --result pass|fail]")


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _warn(msg):
    print(f"⚠️ {msg}", file=sys.stderr)


def _timeout_secs():
    raw = os.environ.get("TDQ_EXTERNAL_TIMEOUT", "")
    try:
        value = int(raw)
        if value > 0:
            return value
    except ValueError:
        if raw:
            _warn(f"TDQ_EXTERNAL_TIMEOUT không hợp lệ: {raw!r} — dùng {DEFAULT_TIMEOUT}s.")
    return DEFAULT_TIMEOUT


def _log_enabled():
    return os.environ.get("TDQ_EXTERNAL_LOG", "1") != "0"


def _project_dir():
    """A17: neo output theo project (TDQ_PROJECT_DIR > git root > cwd) — chạy
    từ thư mục con không được rắc docs/ theo cwd."""
    env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = os.getcwd()
    current = start
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return start
        current = parent


def _log(slug, message):
    """Append 1 dòng ISO-timestamp vào docs/tdq/external/<slug>/run.log của project."""
    if not _log_enabled():
        return
    log_dir = os.path.join(_project_dir(), "docs", "tdq", "external", slug)
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as f:
            f.write(f"[{_now()}] {message}\n")
    except OSError as exc:
        _warn(f"không ghi được log: {exc}")


def _log_stderr(message):
    """Log service cho lệnh KHÔNG có slug (split-plan, skill-dump): stderr,
    timestamp ISO, cùng công tắc TDQ_EXTERNAL_LOG với run.log."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


def validate_report(data):
    """-> danh sách lỗi (rỗng = hợp lệ). Tự kiểm subset schema, không cần lib ngoài.
    Discriminator `kind`: vắng hoặc "task" = report task; "plan" = report cả gói."""
    if isinstance(data, dict) and data.get("kind") == "plan":
        return _validate_plan_report(data)
    errors = []
    if not isinstance(data, dict):
        return [f"report phải là object JSON, nhận {type(data).__name__}"]
    for key, kind in _REQUIRED:
        if key not in data:
            errors.append(f"thiếu khóa bắt buộc: {key}")
        elif not isinstance(data[key], kind):
            errors.append(f"khóa {key} phải là {kind.__name__}")
    if isinstance(data.get("files_changed"), list):
        for item in data["files_changed"]:
            if not isinstance(item, str):
                errors.append("files_changed chỉ chứa chuỗi")
                break
    if isinstance(data.get("status"), str) and data["status"] not in _STATUS:
        errors.append(f"status phải thuộc {_STATUS}")
    for key, value in data.items():
        if key not in [k for k, _ in _REQUIRED] and key not in _OPTIONAL:
            errors.append(f"khóa lạ ngoài schema: {key}")
        elif key in _OPTIONAL and value not in _OPTIONAL[key]:
            errors.append(f"khóa {key} chỉ nhận {_OPTIONAL[key]}")
    return errors


def _validate_plan_report(data):
    """Report gói plan: kind/status/tasks/notes; mỗi task con theo luật task report
    VÀ test_result phải khác rỗng (engine bắt buộc tự verify — Q9)."""
    errors = []
    for key, kind in _PLAN_REQUIRED:
        if key not in data:
            errors.append(f"thiếu khóa bắt buộc: {key}")
        elif not isinstance(data[key], kind):
            errors.append(f"khóa {key} phải là {kind.__name__}")
    if isinstance(data.get("status"), str) and data["status"] not in _STATUS:
        errors.append(f"status phải thuộc {_STATUS}")
    allowed = {k for k, _ in _PLAN_REQUIRED} | {"fallback"}
    for key, value in data.items():
        if key not in allowed:
            errors.append(f"khóa lạ ngoài schema: {key}")
        elif key == "fallback" and value not in _OPTIONAL["fallback"]:
            errors.append(f"khóa fallback chỉ nhận {_OPTIONAL['fallback']}")
    tasks = data.get("tasks")
    if isinstance(tasks, list):
        if not tasks:
            errors.append("tasks không được rỗng")
        for i, task in enumerate(tasks):
            for err in validate_report(task):
                errors.append(f"tasks[{i}]: {err}")
            if (isinstance(task, dict)
                    and isinstance(task.get("test_result"), str)
                    and not task["test_result"].strip()):
                errors.append(
                    f"tasks[{i}]: test_result rỗng — engine phải tự chạy test "
                    "từng task và ghi kết quả thật")
    return errors


def plan_timeout_secs(n_tasks):
    """Timeout gói run-plan: 540s × số task, trần 3600s; env override thắng."""
    raw = os.environ.get("TDQ_EXTERNAL_TIMEOUT", "")
    try:
        value = int(raw)
        if value > 0:
            return value
    except ValueError:
        if raw:
            _warn(f"TDQ_EXTERNAL_TIMEOUT không hợp lệ: {raw!r} — dùng scale.")
    return min(DEFAULT_TIMEOUT * max(n_tasks, 1), PLAN_TIMEOUT_CAP)


# Cú pháp chuẩn dòng `Dùng:` trong plan (spec 2026-08-03-skill-vao-goi-external §1):
# `- Dùng: `<tên>`` hoặc `- Dùng: `<tên>` (mcp)` — nhãn (mcp) NGOÀI backtick, cuối dòng.
_DUNG_LINE = re.compile(r"^\s*-\s*Dùng:\s*`(?P<name>[A-Za-z0-9_-]+)`"
                        r"(?P<mcp>\s*\(mcp\))?\s*$")
_TASK_LINE = re.compile(r"^- \[[ x]\] \*\*(?P<id>\S+?)\*\*")


def parse_dung_lines(plan_text):
    """-> {task_id: [(skill, is_mcp)]} theo cú pháp chuẩn; dòng lệch khuôn bỏ qua."""
    result = {}
    current = None
    for line in plan_text.splitlines():
        task = _TASK_LINE.match(line)
        if task:
            current = task.group("id")
            continue
        dung = _DUNG_LINE.match(line)
        if dung and current:
            result.setdefault(current, []).append(
                (dung.group("name"), bool(dung.group("mcp"))))
    return result


def strip_skill_sections(text):
    """Cắt bỏ từ dòng `## SKILL` ĐẦU TIÊN trở đi — nội dung skill dump (nguyên văn
    SKILL.md + references, đặt CUỐI gói) không được đếm/parse là TASK."""
    match = re.search(r"(?m)^##\s*SKILL\b", text)
    return text[:match.start()] if match else text


def count_packet_tasks(text):
    """Đếm `## TASK <id>` trong gói; không có heading nào → coi là 1 task."""
    found = re.findall(r"(?m)^#{1,3}\s*TASK\s+\S+", strip_skill_sections(text))
    return len(found) if found else 1


def _task_id(task_text, task_file):
    match = re.search(r"^#\s*TASK\s+(\S+)", strip_skill_sections(task_text),
                      re.MULTILINE)
    if match:
        return match.group(1)
    return os.path.splitext(os.path.basename(task_file))[0]


def build_command(engine, model, prompt, worktree, timeout_secs):
    """-> (argv, cwd). Flag đúng theo spec §3 — một chỗ duy nhất định nghĩa lệnh."""
    if engine == "codex":
        return ([
            "codex", "exec", "--cd", worktree, "-m", model,
            "--sandbox", "danger-full-access", "--output-schema", SCHEMA_PATH,
            prompt,
        ], None)
    # agy headless mặc định ghi file vào workspace scratch (~/.gemini/antigravity-cli/
    # scratch/) thay vì cwd — bắt buộc --add-dir path tuyệt đối để ghi đúng worktree.
    # A13: engine phải hết giờ TRƯỚC wrapper 30s để kịp in report (sàn 30s,
    # trần = timeout wrapper khi timeout quá nhỏ) — tránh race kill giữa lúc in.
    engine_secs = min(timeout_secs, max(timeout_secs - 30, 30))
    return ([
        "agy", "-p", prompt, "--model", model, "--output-format", "json",
        "--json-schema", SCHEMA_PATH, "--dangerously-skip-permissions",
        "--add-dir", os.path.abspath(worktree),
        "--print-timeout", f"{engine_secs}s",
    ], worktree)


def _extract_json(stdout):
    """Lấy object report từ stdout engine: JSON thuần, hoặc bọc {response: …},
    hoặc lẫn text quanh một khối {...}."""
    stdout = stdout.strip()
    candidates = []
    try:
        candidates.append(json.loads(stdout))
    except ValueError:
        match = re.search(r"\{.*\}", stdout, re.DOTALL)
        if match:
            try:
                candidates.append(json.loads(match.group(0)))
            except ValueError:
                pass
    if not candidates:
        return None, "stdout không chứa JSON"
    data = candidates[0]
    if isinstance(data, dict) and "task_id" not in data and data.get("kind") != "plan":
        # agy trả report đã parse sẵn ở structured_output; trường response của nó
        # thường có văn xuôi bọc quanh nên ưu tiên structured_output trước.
        structured = data.get("structured_output")
        if isinstance(structured, dict) and (
                "task_id" in structured or structured.get("kind") == "plan"):
            return structured, None
        if "response" in data:
            inner = data["response"]
            if isinstance(inner, str):
                try:
                    inner = json.loads(inner)
                except ValueError:
                    # Codex/agy có thể chèn text quanh khối JSON trong response.
                    match = re.search(r"\{[^{}]*\"task_id\".*\}", inner, re.DOTALL)
                    if not match:
                        return None, "trường response không phải JSON"
                    try:
                        inner = json.loads(match.group(0))
                    except ValueError:
                        return None, "trường response không phải JSON"
            data = inner
    return data, None


def run_task(engine, model, task_file, worktree, slug, plan_round=None,
             plan_file=None):
    """plan_round=None → chạy 1 task (`run`); số nguyên → chạy cả gói plan
    (`run-plan`, report plan-round-<n>.json, 2 attempt, timeout scale theo gói).
    plan_file (chỉ run-plan): đối chiếu gói với khối `Dùng:` của plan —
    thiếu skill/leak mcp → CẢNH BÁO + log, VẪN chạy engine."""
    try:
        with open(task_file, encoding="utf-8") as f:
            base_prompt = f.read()
    except OSError as exc:
        _warn(f"không đọc được gói task: {exc}")
        return 1
    if plan_file:
        try:
            with open(plan_file, encoding="utf-8") as f:
                plan_text = f.read()
        except OSError as exc:
            _warn(f"không đọc được plan (--plan-file): {exc}")
            return 1
        packet_lines = len(base_prompt.splitlines())
        _log_stderr(f"run-plan: gói {packet_lines} dòng, đối chiếu skill với "
                    f"{os.path.basename(plan_file)}")
        _log(slug, f"run-plan plan-file={os.path.basename(plan_file)} "
                   f"gói={packet_lines} dòng")
        for warning in check_packet_skills(base_prompt, plan_text):
            _log_stderr(f"CẢNH BÁO: {warning}")
            _log(slug, f"cảnh báo skill: {warning}")
    plan_mode = plan_round is not None
    if plan_mode:
        task_id = f"plan-round-{plan_round}"
        timeout_secs = plan_timeout_secs(count_packet_tasks(base_prompt))
        max_attempts = PLAN_MAX_ATTEMPTS
    else:
        task_id = _task_id(base_prompt, task_file)
        timeout_secs = _timeout_secs()
        max_attempts = MAX_ATTEMPTS
    report_dir = os.path.join(_project_dir(), "docs", "tdq", "external", slug)
    report_path = os.path.join(report_dir, f"{task_id}.json")
    last_error = ""

    last_raw = ""
    for attempt in range(1, max_attempts + 1):
        prompt = base_prompt
        if last_error:
            prompt += (f"\n\n## LỖI LẦN TRƯỚC (attempt {attempt - 1})\n{last_error}\n")
            if last_raw:
                # A12: model thấp cần thấy chính output sai của mình để sửa trúng chỗ
                prompt += f"\n## OUTPUT LẦN TRƯỚC (trích cuối)\n{last_raw[-500:]}\n"
            prompt += "Hãy sửa và trả về DUY NHẤT một JSON đúng schema report."
        argv, cwd = build_command(engine, model, prompt, worktree, timeout_secs)
        shown = " ".join(argv[:-1] if engine == "codex" else argv[:2]) + " …"
        try:
            proc = subprocess.run(argv, capture_output=True, text=True,
                                  stdin=subprocess.DEVNULL,
                                  timeout=timeout_secs, cwd=cwd)
        except FileNotFoundError:
            _log(slug, f"run task={task_id} engine={engine}: binary không có trong PATH")
            _warn(f"không tìm thấy binary `{engine}` trong PATH.")
            return 1
        except subprocess.TimeoutExpired:
            last_error = f"timeout sau {timeout_secs}s"
            _log(slug, f"run task={task_id} engine={engine} model={model} "
                       f"attempt={attempt} exit=timeout({timeout_secs}s) cmd={shown}")
            continue
        data, parse_err = _extract_json(proc.stdout)
        errors = [parse_err] if parse_err else validate_report(data)
        if not errors and plan_mode and data.get("kind") != "plan":
            errors = ['run-plan đòi report kind="plan" (report task đơn không đủ)']
        # `fallback` là khóa CHỈ orchestrator được ghi — engine phát ra là sai.
        if not errors and ("fallback" in data or (
                plan_mode and any("fallback" in t for t in data.get("tasks", [])
                                  if isinstance(t, dict)))):
            errors = ["khóa fallback chỉ do orchestrator ghi, engine không được phát"]
        if errors:
            stderr_tail = proc.stderr.strip().splitlines()[-3:]
            last_error = "; ".join(errors) + (
                f" | stderr: {' / '.join(stderr_tail)}" if stderr_tail else "")
            last_raw = proc.stdout.strip()
            # A4: persist raw output của attempt hỏng — không có nó thì không
            # debug được model đã trả gì để sửa prompt/gói task.
            try:
                os.makedirs(report_dir, exist_ok=True)
                raw_path = os.path.join(report_dir, f"{task_id}.attempt{attempt}.raw.txt")
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(proc.stdout + "\n--- STDERR ---\n" + proc.stderr)
            except OSError as exc:
                _warn(f"không ghi được raw output attempt {attempt}: {exc}")
            _log(slug, f"run task={task_id} engine={engine} model={model} "
                       f"attempt={attempt} exit={proc.returncode} "
                       f"validate=FAIL({'; '.join(errors)}) cmd={shown}")
            continue
        if proc.returncode != 0:
            data["notes"] = (data.get("notes", "") +
                            f" [engine exit {proc.returncode} nhưng report hợp lệ]").strip()
        os.makedirs(report_dir, exist_ok=True)
        # A24: ghi atomic (tmp + replace) — crash giữa chừng không để lại JSON cụt
        tmp_path = report_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_path, report_path)
        _log(slug, f"run task={task_id} engine={engine} model={model} "
                   f"attempt={attempt} exit={proc.returncode} validate=OK "
                   f"report={os.path.relpath(report_path)} cmd={shown}")
        print(json.dumps(data, ensure_ascii=False))
        return 0

    _log(slug, f"run task={task_id} engine={engine} model={model}: "
               f"hỏng cả {max_attempts} attempt — lỗi cuối: {last_error}")
    _warn(f"task {task_id}: hỏng cả {max_attempts} attempt ({last_error}). "
          "Orchestrator tự implement (fallback: claude).")
    return 1


# Dòng máy-đọc trong plan. TB/dễ vắng → điền theo luật: 1 tên = mọi task,
# 2 tên [khó, dễ] = TB dùng "khó".
_PLAN_LINE = re.compile(
    r"Thực thi external:\s*engine=(?P<engine>\S+)"
    r"\s*·\s*khó=(?P<hard>\S+)"
    r"(?:\s*·\s*TB=(?P<mid>\S+))?"
    r"(?:\s*·\s*dễ=(?P<easy>\S+))?")


def parse_plan(plan_file):
    try:
        with open(plan_file, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        _warn(f"không đọc được plan: {exc}")
        return 1
    match = _PLAN_LINE.search(text)
    if not match:
        _warn("plan không có dòng `Thực thi external: engine=… · khó=…` hợp lệ.")
        return 1
    engine = match.group("engine")
    if engine not in ENGINES:
        _warn(f"engine không hợp lệ: {engine!r} (chỉ nhận {'|'.join(ENGINES)}).")
        return 1
    hard = match.group("hard")
    easy = match.group("easy") or match.group("mid") or hard
    mid = match.group("mid") or hard
    print(json.dumps({"engine": engine,
                      "models": {"khó": hard, "TB": mid, "dễ": easy}},
                     ensure_ascii=False))
    return 0


def split_plan(plan_file):
    """Chia plan thành các gói ≤ MAX_TASKS_PER_PACKET task, tôn trọng ranh giới
    phase (`## P…`). In JSON [{"phase": <tên>, "tasks": [id…]}]."""
    try:
        with open(plan_file, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        _warn(f"không đọc được plan: {exc}")
        return 1
    dung = parse_dung_lines(text)
    groups = []          # [(tên phase, [task id])]
    current = ("", [])
    for line in text.splitlines():
        heading = re.match(r"^##\s+(P\S*.*)", line)
        if heading:
            if current[1]:
                groups.append(current)
            current = (heading.group(1).strip(), [])
            continue
        task = _TASK_LINE.match(line)
        if task:
            current[1].append(task.group("id"))
    if current[1]:
        groups.append(current)
    if not groups:
        _warn("plan không có task checkbox nào.")
        return 1

    def _is_mcp(task_id):
        return any(mcp for _, mcp in dung.get(task_id, []))

    def _skills(task_ids):
        seen, names = set(), []
        for tid in task_ids:
            for name, mcp in dung.get(tid, []):
                if not mcp and name not in seen:
                    seen.add(name)
                    names.append(name)
        return names

    packets = []
    for phase, tasks in groups:
        chunk = []

        def _flush():
            for i in range(0, len(chunk), MAX_TASKS_PER_PACKET):
                part = chunk[i:i + MAX_TASKS_PER_PACKET]
                packets.append({"phase": phase, "tasks": part,
                                "skills": _skills(part)})
            chunk.clear()

        for tid in tasks:
            if _is_mcp(tid):
                # Task MCP: Claude tự làm — gói riêng, giữ nguyên vị trí.
                _flush()
                if packets and packets[-1].get("mcp") and \
                        packets[-1]["phase"] == phase:
                    packets[-1]["tasks"].append(tid)
                else:
                    packets.append({"phase": phase, "tasks": [tid], "mcp": True})
            else:
                chunk.append(tid)
        _flush()
    mcp_total = sum(len(p["tasks"]) for p in packets if p.get("mcp"))
    _log_stderr(f"split-plan: {len(packets)} gói, {mcp_total} task mcp tách riêng")
    print(json.dumps(packets, ensure_ascii=False))
    return 0


def check_packet_skills(packet_text, plan_text):
    """-> [cảnh báo] — lưới máy-kiểm (KHÔNG chặn): gói phải chứa mục
    `## SKILL <tên> — ` cho từng skill của task trong gói; task gắn (mcp)
    không được nằm trong gói engine. So khớp nguyên tên (không match tiền tố)."""
    warnings = []
    dung = parse_dung_lines(plan_text)
    body = strip_skill_sections(packet_text)
    packet_tasks = re.findall(r"(?m)^#{1,3}\s*TASK\s+(\S+)", body)
    have = set(re.findall(r"(?m)^##\s*SKILL\s+(\S+)\s+—", packet_text))
    for task in packet_tasks:
        for skill, is_mcp in dung.get(task, []):
            if is_mcp:
                warnings.append(
                    f"task {task} dùng skill `{skill}` (mcp) nhưng nằm trong "
                    "gói engine — task mcp phải để Claude tự làm")
            elif skill not in have:
                warnings.append(
                    f"gói thiếu mục `## SKILL {skill} — ` cho task {task} "
                    "(plan khai báo Dùng)")
    return warnings


def skill_roots():
    """Thứ tự resolve skill (spec 2026-08-03-skill-vao-goi-external §2#1):
    `skills/` trong repo → `~/.claude/skills/` → thư mục skills của plugin đã cài."""
    project = _project_dir()
    home = os.path.expanduser("~")
    roots = [os.path.join(project, "skills"),
             os.path.join(home, ".claude", "skills")]
    try:
        sys.path.insert(0, SCRIPT_DIR)
        import skill_inventory
        roots += [d for _, d in
                  skill_inventory._plugin_skill_dirs(home, project)]
    except Exception as exc:  # thiếu module/plugin hỏng → vẫn còn 2 tầng đầu
        _warn(f"không quét được skill plugin: {exc}")
    return roots


def resolve_skill(name, roots=None):
    """-> thư mục skill hoặc None; trùng tên → nguồn đứng trước thắng + cảnh báo."""
    hits = []
    for root in (roots if roots is not None else skill_roots()):
        candidate = os.path.join(root, name)
        if os.path.isfile(os.path.join(candidate, "SKILL.md")):
            hits.append(candidate)
    if not hits:
        return None
    if len(hits) > 1:
        _warn(f"skill {name!r} trùng tên ở {len(hits)} nguồn — "
              f"dùng nguồn đứng trước: {hits[0]}")
    return hits[0]


def _strip_frontmatter(text):
    """Bỏ khối frontmatter `---…---` đầu file (nếu có)."""
    if text.startswith("---"):
        end = re.search(r"(?m)^---\s*$", text[3:])
        if end:
            return text[3 + end.end():].lstrip("\n")
    return text


def skill_dump(names):
    """In nguyên văn body SKILL.md (bỏ frontmatter) + toàn bộ references/*.md của
    từng skill, mỗi file dưới header `## SKILL <tên> — <file>`. Thiếu skill → exit 1."""
    import glob as _glob
    roots = skill_roots()
    missing = []
    for name in names:
        skill_dir = resolve_skill(name, roots)
        if skill_dir is None:
            missing.append(name)
            continue
        files = [("SKILL.md", os.path.join(skill_dir, "SKILL.md"))]
        for path in sorted(_glob.glob(os.path.join(skill_dir, "references",
                                                   "*.md"))):
            files.append((f"references/{os.path.basename(path)}", path))
        for label, path in files:
            try:
                with open(path, encoding="utf-8") as f:
                    body = f.read()
            except OSError as exc:
                _warn(f"không đọc được {path}: {exc}")
                missing.append(name)
                break
            if label == "SKILL.md":
                body = _strip_frontmatter(body)
            print(f"## SKILL {name} — {label}")
            print(body.rstrip("\n"))
            print()
        _log_stderr(f"skill-dump: {name} ← {skill_dir} ({len(files)} file)")
    if missing:
        _log_stderr("skill-dump: KHÔNG tìm thấy skill: " + ", ".join(missing))
        _warn("skill không tìm thấy: " + ", ".join(missing))
        return 1
    return 0


def _fix_rounds_path(slug):
    return os.path.join(_project_dir(), "docs", "tdq", "external", slug,
                        "fix-rounds.json")


def _load_fix_rounds(slug):
    try:
        with open(_fix_rounds_path(slug), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"rounds": []}


def fix_rounds(slug, action, tasks=None, result=None):
    """Sổ đếm vòng mini-plan fix. `add`: ghi 1 vòng (chặn vòng 3 — luật ≤2 vòng
    rồi fallback Claude). `status`: in {"rounds": n, "next": fix|fallback|done}."""
    data = _load_fix_rounds(slug)
    rounds = data["rounds"]
    if action == "status":
        if rounds and rounds[-1].get("result") == "pass":
            nxt = "done"
        elif len(rounds) < MAX_FIX_ROUNDS:
            nxt = "fix"
        else:
            nxt = "fallback"
        print(json.dumps({"rounds": len(rounds), "next": nxt},
                         ensure_ascii=False))
        return 0
    # action == "add"
    if len(rounds) >= MAX_FIX_ROUNDS:
        _warn(f"đã đủ {MAX_FIX_ROUNDS} vòng fix — không có vòng "
              f"{len(rounds) + 1}, chuyển fallback Claude tự làm.")
        return 1
    if result not in ("pass", "fail"):
        _warn("--result chỉ nhận pass|fail.")
        return 2
    rounds.append({"n": len(rounds) + 1,
                   "tasks": [t for t in (tasks or "").split(",") if t],
                   "result": result, "at": _now()})
    path = _fix_rounds_path(slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    _log(slug, f"fix-rounds add n={len(rounds)} result={result} "
               f"tasks={rounds[-1]['tasks']}")
    return 0


def _parse_run_opts(rest, extra_flags=()):
    """-> (opts, exit_code|None). Flag chung của run/run-plan."""
    flags = ("--engine", "--model", "--task-file", "--worktree",
             "--slug") + extra_flags
    opts = {}
    while rest:
        flag = rest.pop(0)
        if flag in flags and rest:
            opts[flag[2:].replace("-", "_")] = rest.pop(0)
        else:
            return None, 2
    missing = [k for k in ("engine", "model", "task_file", "worktree", "slug")
               if k not in opts]
    if missing or opts["engine"] not in ENGINES:
        return None, 2
    return opts, None


def main(argv):
    if len(argv) >= 1 and argv[0] == "parse-plan" and len(argv) == 2:
        return parse_plan(argv[1])
    if len(argv) >= 1 and argv[0] == "split-plan" and len(argv) == 2:
        return split_plan(argv[1])
    if len(argv) >= 2 and argv[0] == "skill-dump":
        return skill_dump(argv[1:])
    if len(argv) >= 1 and argv[0] == "fix-rounds":
        rest = argv[1:]
        opts = {"action": None, "slug": None, "tasks": None, "result": None}
        while rest:
            item = rest.pop(0)
            if item in ("add", "status"):
                opts["action"] = item
            elif item in ("--slug", "--tasks", "--result") and rest:
                opts[item[2:]] = rest.pop(0)
            else:
                print(USAGE, file=sys.stderr)
                return 2
        if not opts["slug"] or opts["action"] not in ("add", "status"):
            print(USAGE, file=sys.stderr)
            return 2
        return fix_rounds(opts["slug"], opts["action"], opts["tasks"],
                          opts["result"])
    if len(argv) >= 1 and argv[0] in ("run", "run-plan"):
        plan_mode = argv[0] == "run-plan"
        extra = ("--round", "--plan-file") if plan_mode else ()
        opts, err = _parse_run_opts(argv[1:], extra)
        if err is not None:
            print(USAGE, file=sys.stderr)
            return err
        plan_round = None
        if plan_mode:
            try:
                plan_round = int(opts.get("round", "1"))
            except ValueError:
                print(USAGE, file=sys.stderr)
                return 2
        return run_task(opts["engine"], opts["model"], opts["task_file"],
                        opts["worktree"], opts["slug"], plan_round=plan_round,
                        plan_file=opts.get("plan_file"))
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
