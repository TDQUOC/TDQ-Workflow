#!/usr/bin/env python3
"""Gộp bookkeeping cuối turn của TDQ workflow thành MỘT lệnh (chỉ dùng stdlib).

Bốn bước, luôn chạy đúng thứ tự này:
  1. lint     — `doc_lint.py` trên các file .md vừa sửa
  2. worklog  — append tóm tắt vào docs/workinglog/<hôm nay>.md
  3. phase    — `tdq_state.py set phase=<phase>`
  4. graphify — `graphify extract . --code-only` khi có file code đổi

Nguyên tắc:
- Một bước fail KHÔNG chặn các bước sau; exit code là tổng hợp (0 = không bước nào fail).
- stdout ≤ 200 ký tự khi mọi bước pass; chi tiết chỉ in khi có `--verbose` hoặc có bước fail.
- Log service bật mặc định ra stderr (timestamp ISO + tên bước + kết quả), tắt bằng TDQ_LOG=0.

Env: TDQ_PROJECT_DIR neo project; TDQ_LOG=0 tắt log.
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb",
            ".php", ".c", ".h", ".cpp", ".swift", ".kt", ".lua", ".sh"}
STEP_TIMEOUT = 120
GRAPHIFY_TIMEOUT = 300
MAX_SHORT_OUT = 200
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _log_enabled():
    return os.environ.get("TDQ_LOG", "1") != "0"


def _log(message):
    """Log service: 1 dòng ISO-timestamp ra stderr. Tắt bằng TDQ_LOG=0."""
    if _log_enabled():
        print(f"[{_now()}] {message}", file=sys.stderr)


def _project_dir():
    """Neo theo project: TDQ_PROJECT_DIR > git root > cwd."""
    env = os.environ.get("TDQ_PROJECT_DIR")
    if env:
        return env
    start = current = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return start
        current = parent


def _run(cmd, cwd, timeout=STEP_TIMEOUT):
    """Chạy lệnh con, trả (rc, output). Lỗi hạ tầng cũng thành kết quả, không ném ra ngoài."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, f"quá {timeout}s"
    except OSError as exc:
        return 1, str(exc)


def _changed_files(project):
    """File đang đổi theo git (đường dẫn tuyệt đối). Không phải git repo → rỗng."""
    rc, out = _run(["git", "status", "--porcelain"], project, timeout=30)
    if rc != 0:
        return []
    files = []
    for line in out.splitlines():
        name = line[3:].strip() if len(line) > 3 else ""
        if " -> " in name:                      # file đổi tên
            name = name.split(" -> ", 1)[1]
        name = name.strip('"')
        if name:
            files.append(os.path.join(project, name))
    return files


class Step:
    """Một bước bookkeeping: tên, trạng thái (ok|skip|fail), chi tiết ngắn."""

    def __init__(self, name, status, detail=""):
        self.name, self.status, self.detail = name, status, detail

    def line(self):
        return f"{self.name} {self.status}" + (f" ({self.detail})" if self.detail else "")


def step_lint(project, files):
    docs = [f for f in files if f.endswith(".md") and os.path.exists(f)]
    if not docs:
        return Step("lint", "skip", "không có file .md")
    rc, out = _run([sys.executable, os.path.join(SCRIPTS_DIR, "doc_lint.py")] + docs, project)
    if rc == 0:
        return Step("lint", "ok", f"{len(docs)} file")
    first = out.splitlines()[0] if out else "lỗi không rõ"
    return Step("lint", "fail", first[:120])


def step_worklog(project, summary):
    if not summary:
        return Step("worklog", "skip", "không có --log")
    now = datetime.now()
    path = os.path.join(project, "docs", "workinglog", f"{now:%Y-%m-%d}.md")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as fh:
            if new:
                fh.write(f"# Working log {now:%Y-%m-%d}\n")
            fh.write(f"\n## {now:%H:%M}\n\n{summary.strip()}\n")
    except OSError as exc:
        return Step("worklog", "fail", str(exc)[:120])
    return Step("worklog", "ok", f"{now:%Y-%m-%d} {now:%H:%M}")


def step_phase(project, phase):
    if not phase:
        return Step("phase", "skip", "không có --phase")
    env = dict(os.environ, TDQ_PROJECT_DIR=project)
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "tdq_state.py"), "set", f"phase={phase}"]
    try:
        p = subprocess.run(cmd, cwd=project, capture_output=True, text=True,
                           timeout=STEP_TIMEOUT, env=env)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return Step("phase", "fail", str(exc)[:120])
    if p.returncode != 0:
        return Step("phase", "fail", (p.stdout + p.stderr).strip()[:120])
    return Step("phase", "ok", phase)


def step_dong_so(project, phase):
    """Về `idle` = hết request → chốt sổ thời gian vào docs/tdq/timing.jsonl.

    Chạy TRƯỚC bước đổi phase: đóng sổ xong mới hạ cờ, để cửa sổ phase cuối cùng
    khép đúng lúc thay vì lẫn sang khoảng `idle` sau đó.
    """
    if phase != "idle":
        return Step("thời gian", "skip", "chỉ đóng sổ khi về idle")
    env = dict(os.environ, TDQ_PROJECT_DIR=project)
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "tdq_timing.py"), "close"]
    try:
        p = subprocess.run(cmd, cwd=project, capture_output=True, text=True,
                           timeout=STEP_TIMEOUT, env=env)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return Step("thời gian", "fail", str(exc)[:120])
    if p.returncode != 0:
        return Step("thời gian", "fail", (p.stdout + p.stderr).strip()[:120])
    return Step("thời gian", "ok", "đã ghi timing.jsonl")


def step_graphify(project, files, skip):
    if skip:
        return Step("graphify", "skip", "--skip-graphify")
    if not any(os.path.splitext(f)[1] in CODE_EXT for f in files):
        return Step("graphify", "skip", "không có file code đổi")
    if not shutil.which("graphify"):
        return Step("graphify", "skip", "chưa cài graphify")
    rc, out = _run(["graphify", "extract", ".", "--code-only"], project, GRAPHIFY_TIMEOUT)
    if rc != 0:
        first = out.splitlines()[-1] if out else "lỗi không rõ"
        return Step("graphify", "fail", first[:120])
    return Step("graphify", "ok")


def summarize(steps):
    """Một dòng ≤ 200 ký tự cho trường hợp mọi bước pass."""
    mark = "✗" if any(s.status == "fail" for s in steps) else "✓"
    body = " · ".join(f"{s.name}={s.status}" for s in steps)
    line = f"{mark} tdq_finish: {body}"
    return line if len(line) <= MAX_SHORT_OUT else line[:MAX_SHORT_OUT - 1] + "…"


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Bookkeeping cuối turn: lint → working log → phase → graphify.")
    ap.add_argument("--phase", help="phase mới, ghi qua tdq_state.py")
    ap.add_argument("--log", dest="summary", help="tóm tắt append vào working log hôm nay")
    ap.add_argument("--files", nargs="*", default=None,
                    help="file vừa sửa; bỏ trống thì lấy từ `git status --porcelain`")
    ap.add_argument("--skip-graphify", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="in 1 dòng dự định, không ghi gì")
    ap.add_argument("--verbose", action="store_true", help="in chi tiết từng bước")
    return ap.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    project = _project_dir()
    files = args.files if args.files is not None else _changed_files(project)
    files = [os.path.abspath(os.path.join(project, f)) for f in files]

    if args.dry_run:
        docs = sum(1 for f in files if f.endswith(".md"))
        print(f"dry-run: lint {docs} file .md · worklog "
              f"{'có' if args.summary else 'bỏ'} · phase {args.phase or 'giữ nguyên'} · "
              f"graphify {'bỏ' if args.skip_graphify else 'nếu có code đổi'}")
        return 0

    _log(f"bắt đầu · project={project} · {len(files)} file đổi")
    steps = []
    for run_step in (lambda: step_lint(project, files),
                     lambda: step_worklog(project, args.summary),
                     lambda: step_dong_so(project, args.phase),
                     lambda: step_phase(project, args.phase),
                     lambda: step_graphify(project, files, args.skip_graphify)):
        step = run_step()
        steps.append(step)
        _log(f"{step.name} → {step.status}" + (f" ({step.detail})" if step.detail else ""))

    failed = [s for s in steps if s.status == "fail"]
    print(summarize(steps))
    if args.verbose or failed:
        for s in (steps if args.verbose else failed):
            print(f"  - {s.line()}")
    _log(f"xong · {len(failed)} bước fail")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
