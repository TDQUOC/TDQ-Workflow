"""Helper dùng chung cho hook TDQ (chỉ stdlib).

Giao thức tuân thủ 0.3.0 (spec §2.1): hook phát lời nhắc mang MÃ, và ghi vào sổ
turn cả hai loại sự kiện:
  - remind : hook đã nhắc mã nào
  - observe: hành động THẬT đã xảy ra (sửa file nào, chạy lệnh state nào)
Cuối turn `stop_gate` đối chiếu hai bên. Bằng chứng tuân thủ là HIỆU ỨNG quan
sát được, không phải lời tự khai của model — vì vậy hook không đọc transcript
và không tin dòng echo `✓ [TDQ:...]` do model tự in.
"""
import json
import os
import re
import sys

_SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)
import tdq_state  # noqa: E402

# 0.2.0 bỏ gate cứng; 0.3.0 bỏ luôn slash command duyệt — user duyệt bằng chat.
APPROVE_HINTS = {
    "spec": 'nhắn "duyệt spec"',
    # {mode} = mode ĐÃ CHỐT trong plan (dòng "Mode thực thi:"), fallback main —
    # hardcode main từng khiến user gõ sai mode so với plan đã chốt.
    "plan": 'nhắn "duyệt plan mode {mode}" (đổi được: main|subagent)',
    # Biến thể bỏ QC phải hiện ở gợi ý, nếu không user không biết đường opt-out.
    "quick": 'nhắn "duyệt quick" (bỏ QC: "duyệt quick không QC")',
}

_PLAN_MODE = re.compile(r"Mode thực thi:\s*(main|subagent)", re.IGNORECASE)


def plan_mode(cwd, state):
    """Mode đã chốt trong plan_file (dòng 'Mode thực thi:'), None nếu chưa ghi."""
    rel = (state or {}).get("plan_file")
    if not rel:
        return None
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    try:
        with open(path, encoding="utf-8") as f:
            match = _PLAN_MODE.search(f.read())
    except OSError:
        return None
    return match.group(1).lower() if match else None

# Danh sách MÃ ĐÓNG (spec §2.1). Thêm mã mới phải sửa spec trước.
CODES = ("TDQ:NEXT", "TDQ:APPROVE", "TDQ:LOG", "TDQ:STATE", "TDQ:GIT")

# Trần ngân sách token (spec §2.7) — tính trên nội dung lời nhắc.
MAX_REMIND_CHARS = 200
MAX_REMIND_LINES = 3


def read_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def payload_cwd(payload):
    """Project root cho state — cwd của payload có thể là thư mục con/worktree."""
    return tdq_state.resolve_project_dir(payload.get("cwd") or os.getcwd())


def session_id(payload):
    return str(payload.get("session_id") or "")


# ------------------------------------------------------------------ sổ turn

def observe(cwd, payload, event, **fields):
    """Ghi một hành động thật đã quan sát được."""
    tdq_state.turn_log_append(cwd, "observe", session=session_id(payload),
                              event=event, **fields)


def turn_rows(cwd, payload):
    return tdq_state.turn_log_read(cwd, session=session_id(payload))


def already_reminded(cwd, payload, code, rows=None):
    """Mã này đã nhắc trong turn hiện tại chưa (dedupe 1 lần/mã/turn).

    `rows`: sổ turn đã đọc sẵn (P0-3 — tránh đọc lại `.tdq-turn.jsonl` khi nơi
    gọi đã có rows từ một lượt đọc khác trong cùng invoke). None → tự đọc.
    """
    if rows is None:
        rows = turn_rows(cwd, payload)
    return any(r.get("kind") == "remind" and r.get("code") == code for r in rows)


def trim(lines):
    """Ép về đúng trần: ≤3 dòng, ≤200 ký tự."""
    lines = [l for l in lines if l][:MAX_REMIND_LINES]
    text = "\n".join(lines)
    if len(text) > MAX_REMIND_CHARS:
        text = text[:MAX_REMIND_CHARS - 1].rstrip() + "…"
    return text


def remind(cwd, payload, code, lines, event="PreToolUse", rows=None):
    """Nhắc Claude kèm MÃ mà KHÔNG chặn tool, rồi thoát.

    Khuôn 3 dòng (spec §2.1): việc phải làm · cách làm · dòng echo cần in.
    Mã đã nhắc trong turn này thì im lặng (dedupe) để khỏi đốt token.
    `rows`: sổ turn đã đọc sẵn — xem `already_reminded` (P0-3).
    """
    if already_reminded(cwd, payload, code, rows=rows):
        sys.exit(0)
    tdq_state.turn_log_append(cwd, "remind", session=session_id(payload), code=code)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "allow",
            "permissionDecisionReason": "TDQ: nhắc nhở, không chặn.",
            "additionalContext": trim([f"[{code}] {lines[0]}"] + list(lines[1:])),
        }
    }, ensure_ascii=False))
    sys.exit(0)


def remind_force(cwd, payload, code, lines, event="PreToolUse"):
    """Như `remind()` nhưng KHÔNG dedupe theo mã — dùng khi một mã đã bị hook
    khác (vd. edit_gate.py) chiếm trong turn này mà nhắc này vẫn phải ra."""
    tdq_state.turn_log_append(cwd, "remind", session=session_id(payload), code=code)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "allow",
            "permissionDecisionReason": "TDQ: nhắc nhở, không chặn.",
            "additionalContext": trim([f"[{code}] {lines[0]}"] + list(lines[1:])),
        }
    }, ensure_ascii=False))
    sys.exit(0)


def echo_line(code, what):
    return f"Xong thì in: ✓ [{code}] {what}"


def approve_hint(target, mode=None):
    hint = APPROVE_HINTS.get(target, "nhắn duyệt")
    if target == "plan":
        hint = hint.format(mode=mode or "main")
    return f"➤ Duyệt: {hint} · Góp ý: nhắn trực tiếp"
