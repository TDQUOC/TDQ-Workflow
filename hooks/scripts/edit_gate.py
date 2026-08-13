#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit|NotebookEdit) — quan sát + nhắc; chặn đúng 1 ca.

Chỉ `TDQ:TICK` chặn (deny): sửa mã nguồn khi đang implement/qc mà plan chưa có task
nào mang dấu `[~]`. Mọi mã còn lại vẫn chỉ nhắc.

Hai việc, theo đúng thứ tự:
1. Ghi `observe` vào sổ turn: `edit:<path>` cho mọi lần sửa file, `log_written`
   khi file đó chính là working log hôm nay. Đây là bằng chứng mà `stop_gate`
   dùng cuối turn — không phụ thuộc transcript, không phụ thuộc model tự khai.
2. Phát mã nhắc khi cần: TDQ:STATE (định sửa tay state), TDQ:APPROVE (sửa code
   khi gate của lane chưa duyệt), TDQ:LOG (repo đã đổi mà log hôm nay chưa có).
"""
import os

from _common import (block, echo_line, observe, payload_cwd, read_payload, remind,
                     tdq_state, turn_rows)

today_log_rel = tdq_state.today_log_rel      # một nguồn duy nhất, dùng chung với stop_gate

# Ngưỡng streak (spec 2026-08-13-ra-soat-tick-che-do-sau §3): quá NGƯỠNG lần sửa mã
# nguồn liên tiếp mà plan (checksum) chưa đổi kể từ đó → chặn lần kế tiếp. Khớp trần
# "vòng fix" (3 vòng) đã dùng sẵn trong hệ thống.
STREAK_NGUONG = 3


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
        return  # docs/** không cần nhắc: brief/spec/plan/research/log

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

    # đang implement/qc mà plan chưa đánh dấu task nào đang làm → CHẶN.
    # stop_gate chỉ so vân tay plan đầu/cuối turn nên không bắt được bulk-tick trong
    # một turn duy nhất (lane quick làm trọn gói trong 1 turn) — hàng rào thật phải
    # nằm ở đây. Miễn trừ `tests/**`: red→green đòi viết test đỏ trước khi có gì để tick.
    # Đặt CUỐI vì `remind()` thoát ngay sau lần nhắc đầu: TDQ:LOG dẫn tới chặn cứng
    # ở Stop nên phải được ưu tiên.
    in_tests = within(rel_target, "tests") or rel_target.startswith("tests" + os.sep)
    if not in_tests and tdq_state.effective_phase(state, warn=False) in ("implement", "qc"):
        tick = tdq_state.plan_tick_state(cwd)
        if tick["exists"] and tick["total"] > 0 \
                and not tick["has_doing"] and not tick["all_done"]:
            block(cwd, payload, "TDQ:TICK", [
                "Plan chưa có task nào mang dấu [~] — đánh dấu task đang làm TRƯỚC khi sửa code.",
                "Mở plan, đổi task sắp làm thành [~]; xanh thì đổi [x] ngay.",
                "Request đã xong → tdq_state.py set phase=idle.",
            ])
        # nhiều task cùng [~] cũng là checkbox không phản ánh đúng đang làm gì —
        # đóng task cũ ([x]) rồi mới mở task mới.
        if tick["exists"] and tick["doing_count"] > 1:
            block(cwd, payload, "TDQ:TICK", [
                "Plan đang có nhiều task cùng mang [~] — đóng task cũ ([x]) trước khi mở task mới.",
                "Mở plan, tick [x] task đã xong, chỉ giữ đúng 1 task [~] tại một thời điểm.",
                "Request đã xong → tdq_state.py set phase=idle.",
            ])
        # đúng 1 task [~] đứng yên xuyên suốt cũng né được cả hai chặn trên: agent tick
        # T1 một lần, giữ nguyên khi sửa ngầm nhiều file, rồi mới tick loạt cuối turn.
        # Đếm số lần sửa mã nguồn liên tiếp kể từ lần plan đổi (checksum) gần nhất —
        # quá NGƯỠNG thì chặn, buộc đóng task trước khi sửa tiếp.
        if tick["exists"] and tick["doing_count"] == 1:
            rows = turn_rows(cwd, payload)
            streak = sum(
                1 for r in rows
                if r.get("kind") == "observe" and r.get("event") == "code_edit"
                and r.get("plan_sha") == tick["sha"]
            )
            if streak >= STREAK_NGUONG:
                block(cwd, payload, "TDQ:TICK", [
                    f"Đã sửa {streak} lần liên tiếp mà plan chưa tick — đóng task trước khi sửa tiếp.",
                    "Test xanh thì đổi [x] ngay; task khác thì tick task mới trước khi code.",
                    "Request đã xong → tdq_state.py set phase=idle.",
                ])
            observe(cwd, payload, "code_edit", path=rel_target, plan_sha=tick["sha"])


if __name__ == "__main__":
    main()
