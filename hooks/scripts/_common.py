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
import sys

_SCRIPTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)
import tdq_state  # noqa: E402

# 0.2.0 bỏ gate cứng; 0.3.0 bỏ luôn slash command duyệt — user duyệt bằng chat.
APPROVE_HINTS = {
    "spec": 'nhắn "duyệt spec"',
    "plan": 'nhắn "duyệt plan mode main" (hoặc subagent, external)',
    "quick": 'nhắn "duyệt quick"',
}

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


def already_reminded(cwd, payload, code):
    """Mã này đã nhắc trong turn hiện tại chưa (dedupe 1 lần/mã/turn)."""
    return any(r.get("kind") == "remind" and r.get("code") == code
               for r in turn_rows(cwd, payload))


def trim(lines):
    """Ép về đúng trần: ≤3 dòng, ≤200 ký tự."""
    lines = [l for l in lines if l][:MAX_REMIND_LINES]
    text = "\n".join(lines)
    if len(text) > MAX_REMIND_CHARS:
        text = text[:MAX_REMIND_CHARS - 1].rstrip() + "…"
    return text


def remind(cwd, payload, code, lines, event="PreToolUse"):
    """Nhắc Claude kèm MÃ mà KHÔNG chặn tool, rồi thoát.

    Khuôn 3 dòng (spec §2.1): việc phải làm · cách làm · dòng echo cần in.
    Mã đã nhắc trong turn này thì im lặng (dedupe) để khỏi đốt token.
    """
    if already_reminded(cwd, payload, code):
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


def echo_line(code, what):
    return f"Xong thì in: ✓ [{code}] {what}"


def approve_hint(target):
    return f"➤ Duyệt: {APPROVE_HINTS.get(target, 'nhắn duyệt')} · Góp ý: nhắn trực tiếp"
