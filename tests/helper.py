"""Shared test utilities: run hook scripts as subprocesses with stdin JSON."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks", "scripts")
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402


def run_hook(script, payload, env=None):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        env=dict(os.environ, **(env or {})),
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


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
        capture_output=True, text=True, env=env, timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_state_cli_in(cwd, *args):
    """Chạy CLI với process cwd = cwd và KHÔNG set TDQ_PROJECT_DIR (giống user
    gõ lệnh từ một thư mục con của project)."""
    env = {k: v for k, v in os.environ.items() if k != "TDQ_PROJECT_DIR"}
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "tdq_state.py"), *args],
        capture_output=True, text=True, env=env, cwd=cwd, timeout=30,
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
