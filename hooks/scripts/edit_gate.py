#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit|NotebookEdit) — quan sát + nhắc, KHÔNG chặn.

Hai việc, theo đúng thứ tự:
1. Ghi `observe` vào sổ turn: `edit:<path>` cho mọi lần sửa file, `log_written`
   khi file đó chính là working log hôm nay. Đây là bằng chứng mà `stop_gate`
   dùng cuối turn — không phụ thuộc transcript, không phụ thuộc model tự khai.
2. Phát mã nhắc khi cần: TDQ:STATE (định sửa tay state), TDQ:APPROVE (sửa code
   khi gate của lane chưa duyệt), TDQ:LOG (repo đã đổi mà log hôm nay chưa có).
"""
import os

from _common import (echo_line, observe, payload_cwd, read_payload, remind, tdq_state)

today_log_rel = tdq_state.today_log_rel      # một nguồn duy nhất, dùng chung với stop_gate


def within(child, parent):
    return child == parent or child.startswith(parent + os.sep)


def main():
    payload = read_payload()
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not target or not isinstance(target, str):
        return
    cwd = payload_cwd(payload)
    abs_target = os.path.realpath(target if os.path.isabs(target) else os.path.join(cwd, target))
    try:
        rel_target = os.path.relpath(abs_target, os.path.realpath(cwd))
    except ValueError:
        rel_target = abs_target

    log_rel = today_log_rel()
    log_dir = os.path.realpath(os.path.join(cwd, "docs", "workinglog"))
    is_log = within(abs_target, log_dir)

    # (1) quan sát — luôn ghi, kể cả khi chưa có request nào đang mở
    observe(cwd, payload, "edit", path=rel_target)
    if is_log:
        observe(cwd, payload, "log_written", path=rel_target)

    # (2) nhắc
    state_file = os.path.realpath(tdq_state.state_path(cwd))
    state_md = os.path.realpath(tdq_state.state_md_path(cwd))
    if abs_target in (state_file, state_md):
        remind(cwd, payload, "TDQ:STATE", [
            "Đừng sửa tay file trạng thái — ghi bằng CLI.",
            "Cách làm: python3 scripts/tdq_state.py set <key>=<value> (hoặc approve/init/reset).",
            echo_line("TDQ:STATE", "đã ghi state bằng CLI"),
        ])

    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        return
    if within(abs_target, os.path.realpath(os.path.join(cwd, "docs"))):
        return  # docs/** không cần nhắc: spec/plan/questions/research/log

    lane = tdq_state.effective_lane(state, warn=False)
    pending = None
    if lane == "full" and not state.get("spec_approved"):
        pending = "spec"
    elif lane == "full" and not state.get("plan_approved"):
        pending = "plan"
    elif lane == "quick" and not state.get("quick_approved"):
        pending = "quick"
    if pending:
        mode = " --mode <main|subagent>" if pending == "plan" else ""
        # Lệnh đặt trước lời khuyên: trần 200 ký tự, phần cắt phải là phần ít cần nhất.
        remind(cwd, payload, "TDQ:APPROVE", [
            f"Đang sửa file ngoài docs/ mà {pending} chưa được ghi nhận duyệt.",
            f"User đã duyệt → python3 scripts/tdq_state.py approve {pending}{mode} "
            f"--by \"<lời user>\".",
            f"Chưa duyệt → trình {pending} rồi xin duyệt.",
        ])

    # repo đã đổi → nhắc working log ngay, đừng dồn tới Stop mới báo
    if not os.path.isfile(os.path.join(cwd, log_rel)):
        remind(cwd, payload, "TDQ:LOG", [
            f"Turn này đổi repo — append entry vào {log_rel} trước khi kết thúc turn.",
            "Cách làm: mở file, thêm mục \"## HH:MM — <việc>\" ở CUỐI file.",
            echo_line("TDQ:LOG", f"đã append {log_rel}"),
        ])


if __name__ == "__main__":
    main()
