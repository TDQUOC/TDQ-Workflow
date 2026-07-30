#!/usr/bin/env python3
"""external_task.py — chạy MỘT task của plan qua engine ngoài (codex | agy).

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
DEFAULT_TIMEOUT = 540
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(SCRIPT_DIR, "external_report_schema.json")

# Trường bắt buộc: (tên, kiểu). files_changed kiểm riêng từng phần tử.
_REQUIRED = (
    ("task_id", str), ("status", str), ("files_changed", list),
    ("test_cmd", str), ("test_result", str), ("notes", str),
)
_OPTIONAL = {"fallback": ("claude",)}
_STATUS = ("done", "blocked")

USAGE = ("usage: external_task.py run --engine <codex|agy> --model <slug> "
         "--task-file <f> --worktree <dir> --slug <slug> | parse-plan <plan-file>")


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


def _log(slug, message):
    """Append 1 dòng ISO-timestamp vào docs/tdq/external/<slug>/run.log (tính từ cwd)."""
    if not _log_enabled():
        return
    log_dir = os.path.join(os.getcwd(), "docs", "tdq", "external", slug)
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as f:
            f.write(f"[{_now()}] {message}\n")
    except OSError as exc:
        _warn(f"không ghi được log: {exc}")


def validate_report(data):
    """-> danh sách lỗi (rỗng = hợp lệ). Tự kiểm subset schema, không cần lib ngoài."""
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


def _task_id(task_text, task_file):
    match = re.search(r"^#\s*TASK\s+(\S+)", task_text, re.MULTILINE)
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
    return ([
        "agy", "-p", prompt, "--model", model, "--output-format", "json",
        "--json-schema", SCHEMA_PATH, "--dangerously-skip-permissions",
        "--add-dir", os.path.abspath(worktree),
        "--print-timeout", f"{timeout_secs}s",
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
    if isinstance(data, dict) and "response" in data and "task_id" not in data:
        inner = data["response"]
        if isinstance(inner, str):
            try:
                inner = json.loads(inner)
            except ValueError:
                return None, "trường response không phải JSON"
        data = inner
    return data, None


def run_task(engine, model, task_file, worktree, slug):
    try:
        with open(task_file, encoding="utf-8") as f:
            base_prompt = f.read()
    except OSError as exc:
        _warn(f"không đọc được gói task: {exc}")
        return 1
    task_id = _task_id(base_prompt, task_file)
    timeout_secs = _timeout_secs()
    report_dir = os.path.join(os.getcwd(), "docs", "tdq", "external", slug)
    report_path = os.path.join(report_dir, f"{task_id}.json")
    last_error = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        prompt = base_prompt
        if last_error:
            prompt += (f"\n\n## LỖI LẦN TRƯỚC (attempt {attempt - 1})\n{last_error}\n"
                       "Hãy sửa và trả về DUY NHẤT một JSON đúng schema report.")
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
        # `fallback` là khóa CHỈ orchestrator được ghi — engine phát ra là sai.
        if not errors and "fallback" in data:
            errors = ["khóa fallback chỉ do orchestrator ghi, engine không được phát"]
        if errors:
            stderr_tail = proc.stderr.strip().splitlines()[-3:]
            last_error = "; ".join(errors) + (
                f" | stderr: {' / '.join(stderr_tail)}" if stderr_tail else "")
            _log(slug, f"run task={task_id} engine={engine} model={model} "
                       f"attempt={attempt} exit={proc.returncode} "
                       f"validate=FAIL({'; '.join(errors)}) cmd={shown}")
            continue
        if proc.returncode != 0:
            data["notes"] = (data.get("notes", "") +
                            f" [engine exit {proc.returncode} nhưng report hợp lệ]").strip()
        os.makedirs(report_dir, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        _log(slug, f"run task={task_id} engine={engine} model={model} "
                   f"attempt={attempt} exit={proc.returncode} validate=OK "
                   f"report={os.path.relpath(report_path)} cmd={shown}")
        print(json.dumps(data, ensure_ascii=False))
        return 0

    _log(slug, f"run task={task_id} engine={engine} model={model}: "
               f"hỏng cả {MAX_ATTEMPTS} attempt — lỗi cuối: {last_error}")
    _warn(f"task {task_id}: hỏng cả {MAX_ATTEMPTS} attempt ({last_error}). "
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


def main(argv):
    if len(argv) >= 1 and argv[0] == "parse-plan" and len(argv) == 2:
        return parse_plan(argv[1])
    if len(argv) >= 1 and argv[0] == "run":
        opts = {}
        rest = argv[1:]
        while rest:
            flag = rest.pop(0)
            if flag in ("--engine", "--model", "--task-file", "--worktree", "--slug") and rest:
                opts[flag[2:].replace("-", "_")] = rest.pop(0)
            else:
                print(USAGE, file=sys.stderr)
                return 2
        missing = [k for k in ("engine", "model", "task_file", "worktree", "slug")
                   if k not in opts]
        if missing or opts["engine"] not in ENGINES:
            print(USAGE, file=sys.stderr)
            return 2
        return run_task(opts["engine"], opts["model"], opts["task_file"],
                        opts["worktree"], opts["slug"])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
