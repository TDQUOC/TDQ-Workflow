"""Shared test utilities: run hook scripts as subprocesses with stdin JSON."""
import functools
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks", "scripts")
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402


# Whole test PROCESS, not only `run_hook`: several tests run hook scripts through their own
# subprocess calls (test_hook_windows, context_surface's hook timing, token_budget). On
# 2026-10-03 those started REAL background builds — one ran in this repo and rewrote
# `.codex/hooks.json`, and a detached child kept a temp dir locked (WinError 32). `discover`
# imports every test module before running any test, so this line is in place before the first.
os.environ["TDQ_KHOI_TAO_NEN"] = "0"


def run_hook(script, payload, env=None):
    # 2026-10-03: `session_start.py` starts a REAL background build (installs, graphify, lumen
    # index) in a project whose search layers are not ready — which is every temp dir a test
    # makes. Off by default here; the auto-init tests turn it on with a harmless TDQ_LENH_NEN.
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, script)],
        input=json.dumps(payload), capture_output=True, encoding="utf-8", text=True, timeout=30,
        env={**os.environ, "TDQ_KHOI_TAO_NEN": "0", **(env or {})},
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def bo_duong_dan_plugin(text):
    """Đưa `python3 "<gốc plugin>/scripts/X.py"` về `python3 scripts/X.py` trước khi đo trần.

    Từ 2026-10-03 hook in đường dẫn TUYỆT ĐỐI khi project không có `scripts/` (đúng ca test chạy
    trong thư mục tạm). Trần ký tự đo NỘI DUNG lời nhắc; tiền tố đường dẫn là cơ học và được đổi
    sau bước cắt — đo nó vào trần là bắt lời nhắc trả giá cho độ dài thư mục cài plugin."""
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, "/")
    return re.sub(r'python3 "' + re.escape(goc) + r'/scripts/([\w.-]+\.py)"', r"python3 scripts/\1",
                  text or "")


def co_lenh(ten):
    """Lệnh ngoài `ten` có trên PATH không — dùng cho `skipUnless` (T3.1, 2026-09-21)."""
    return shutil.which(ten) is not None


@functools.lru_cache(maxsize=None)
def co_bo_dem_token():
    """Đếm token thật được không. Hỏi chính `skill_tokens` — cả python đang chạy lẫn venv của
    repo — thay vì mỗi test tự đoán đường venv (đoán `bin/python` thì sai trên Windows)."""
    import skill_tokens
    try:
        skill_tokens.nap_bo_dem()
        return True
    except skill_tokens.ThieuThuVienDem:
        pass
    try:
        skill_tokens.dem_qua_venv(["x"])
        return True
    except skill_tokens.ThieuThuVienDem:
        return False


LY_DO_TOKEN = "chưa cài anthropic-tokenizer (python3 scripts/skill_tokens.py in lệnh cài)"


def load_fixture(name, **overrides):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        payload = json.load(f)
    payload.update(overrides)
    return payload


def write_state(cwd, **overrides):
    state = tdq_state.default_state()
    state.update(overrides)
    os.makedirs(os.path.join(cwd, "docs", "tdq"), exist_ok=True)
    with open(os.path.join(cwd, "docs", "tdq", "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)
    return state


def read_state(cwd):
    return tdq_state.load(cwd)


def run_state_cli(cwd, *args):
    env = dict(os.environ, TDQ_PROJECT_DIR=cwd)
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_state.py"), *args],
        capture_output=True, encoding="utf-8", text=True, env=env, timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_timing_cli(cwd, *args, env=None):
    """Chạy scripts/tdq_timing.py với project = cwd."""
    full_env = dict(os.environ, TDQ_PROJECT_DIR=cwd, **(env or {}))
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_timing.py"), *args],
        capture_output=True, encoding="utf-8", text=True, env=full_env, timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_checkstatus_cli(cwd, *args, env=None):
    """Chạy scripts/tdq_checkstatus.py với project = cwd."""
    full_env = dict(os.environ, TDQ_PROJECT_DIR=cwd, **(env or {}))
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_checkstatus.py"), *args],
        capture_output=True, encoding="utf-8", text=True, env=full_env, timeout=60,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_team_cli(cwd, *args, env=None):
    """Chạy scripts/tdq_team.py với project = cwd."""
    full_env = dict(os.environ, TDQ_PROJECT_DIR=cwd, **(env or {}))
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_team.py"), *args],
        capture_output=True, encoding="utf-8", text=True, env=full_env, timeout=60,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_finish_cli(cwd, *args, env=None):
    """Chạy scripts/tdq_finish.py với project = cwd."""
    full_env = dict(os.environ, TDQ_PROJECT_DIR=cwd, **(env or {}))
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_finish.py"), *args],
        capture_output=True, encoding="utf-8", text=True, env=full_env, timeout=60,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_state_cli_in(cwd, *args):
    """Chạy CLI với process cwd = cwd và KHÔNG set TDQ_PROJECT_DIR (giống user
    gõ lệnh từ một thư mục con của project)."""
    env = {k: v for k, v in os.environ.items() if k != "TDQ_PROJECT_DIR"}
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_state.py"), *args],
        capture_output=True, encoding="utf-8", text=True, env=env, cwd=cwd, timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def decision(stdout):
    """Parse PreToolUse hook stdout -> (permissionDecision, additionalContext).

    0.2.0: hook không còn deny; nội dung đáng kiểm là lời nhắc (additionalContext).
    """
    if not stdout:
        return None, ""
    data = json.loads(stdout)
    hso = data.get("hookSpecificOutput", {})
    return hso.get("permissionDecision"), hso.get("additionalContext", "")


def write_file(cwd, rel, content="x\n"):
    path = os.path.join(cwd, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
