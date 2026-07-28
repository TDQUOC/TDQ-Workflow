#!/usr/bin/env python3
"""UserPromptExpansion gate for /tdq-workflow:tdq-approve.

Runs ONLY when the USER typed the approve command themselves (the skill is
disable-model-invocation, so the model cannot trigger this). Validates the
request against state + the registered detail file, then sets the protected
approval fields. Exit 2 blocks the command (stderr shown as feedback) and
state is never changed on failure.
"""
import os
import re
import sys

from _common import read_payload, payload_cwd, tdq_state

USAGE = "Cách dùng: /tdq-workflow:tdq-approve spec | plan <main|subagent> | quick"
MODE_RE = re.compile(r"\b(main|subagent)\b", re.IGNORECASE)
# Proposal line inside the plan. Deliberately tolerant of wording: any label
# containing the word "mode" followed by ':' and the value counts ("Mode thực
# thi: main", "Đề xuất mode: **main**", "Mode đề xuất: `subagent`"). A bare
# "main" somewhere in the plan does NOT — the label is what makes it a proposal.
PROPOSED_RE = re.compile(r"\bmode\b[^\n:]{0,40}:\s*[*`_ ]*(main|subagent)\b", re.IGNORECASE)


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    text = " ".join(
        str(payload.get(k, "")) for k in
        ("command_args", "args", "arguments", "prompt", "command", "expanded_prompt")
    )
    match = re.search(r"\b(spec|plan|quick)\b", text)
    if not match:
        block(f"Thiếu hoặc sai tham số. {USAGE}")
    target = match.group(1)

    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        block("Chưa có request TDQ nào đang mở — không có gì để duyệt. "
              "Yêu cầu Claude chạy tdq-start (mở request + chọn lane) rồi trình lại "
              "spec/plan để duyệt; đừng gõ lệnh duyệt trước bước đó. " + USAGE)

    if target == "quick":
        if state.get("lane") != "quick":
            block(f"Sai lane: request đang ở lane {state.get('lane')} — duyệt quick chỉ dùng cho lane "
                  "quick. Yêu cầu Claude xác nhận lane đúng với việc đang làm rồi trình lại.")
        if state.get("quick_approved"):
            block(f"Quick plan đã được duyệt lúc {state.get('quick_approved_at')} rồi.")
        state["quick_approved"] = True
        state["quick_approved_at"] = tdq_state.now_iso()
        tdq_state.save(cwd, state)
        print(
            "[TDQ] USER APPROVED QUICK PLAN at {at}. MANDATORY ORDER: "
            "(1) append the approved plan summary to docs/workinglog/<today>.md NOW, "
            "(2) only then implement end-to-end in this turn, "
            "(3) run the quick validate/test you promised, "
            "(4) report briefly. All user-facing output in Vietnamese.".format(
                at=state["quick_approved_at"])
        )
        return

    if state.get("lane") != "full":
        block(f"Sai lane: duyệt {target} chỉ dùng cho lane full.")

    file_key = f"{target}_file"
    ok_key = f"{target}_approved"
    sha_key = f"{target}_sha256"
    at_key = f"{target}_approved_at"

    if target == "plan" and not state.get("spec_approved"):
        block("Sai thứ tự: spec chưa được duyệt — duyệt spec trước (/tdq-workflow:tdq-approve spec).")
    if state.get(ok_key):
        block(f"{target.capitalize()} đã được duyệt lúc {state.get(at_key)} rồi.")
    rel = state.get(file_key)
    if not rel:
        block(f"Chưa có {target} nào được đăng ký chờ duyệt — yêu cầu Claude hoàn thành {target} trong "
              f"docs/tdq/{target}/, đăng ký {target}_file vào state rồi trình lại để duyệt.")
    path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        block(f"File {target} đã đăng ký ({rel}) không tồn tại hoặc rỗng — yêu cầu Claude kiểm tra lại trước khi duyệt.")

    mode = None
    proposed = None
    if target == "plan":
        # The implement mode is the USER's decision, so it comes from what the
        # user TYPED. The plan may only PROPOSE one; neither the plan file nor
        # state can decide it (the model controls both).
        try:
            with open(path, encoding="utf-8") as f:
                plan_text = f.read()
        except OSError:
            plan_text = ""
        pm = PROPOSED_RE.search(plan_text)
        if not pm:
            block(f"Plan {rel} chưa có dòng đề xuất mode. Yêu cầu Claude thêm vào plan một dòng "
                  "dạng `Mode thực thi: main — <lý do>` (hoặc `Đề xuất mode: subagent — <lý do>`) "
                  "rồi trình lại; nhãn phải chứa chữ 'mode' và dấu hai chấm trước giá trị. "
                  "Mode thật vẫn do bạn gõ khi duyệt.")
        proposed = pm.group(1).lower()

        mm = MODE_RE.search(text)
        if not mm:
            block("Thiếu mode thực thi trong lệnh duyệt — mode là quyết định của BẠN, "
                  "không phải của Claude. Gõ lại kèm mode: "
                  "`/tdq-workflow:tdq-approve plan main` (làm tuần tự trong hội thoại này) "
                  "hoặc `/tdq-workflow:tdq-approve plan subagent` (chia subagent, mỗi cái 1 worktree). "
                  f"Plan đang đề xuất: {proposed}.")
        mode = mm.group(1).lower()
        state["implement_mode"] = mode

    state[ok_key] = True
    state[sha_key] = tdq_state.sha256_file(path)
    state[at_key] = tdq_state.now_iso()
    tdq_state.save(cwd, state)
    if target == "spec":
        nxt = ("create the plan (docs/tdq/plan/), register plan_file in state, present a <=100-line "
               "summary with the approve instruction, then WAIT for plan approval.")
    else:
        diff = "" if mode == proposed else (
            f" (the user chose '{mode}' while the plan đề xuất '{proposed}' — follow the user, "
            "and say so in Vietnamese when you report)")
        nxt = (f"the USER chose implement mode '{mode}' in the approve command{diff}: set phase=implement, "
               "then implement end-to-end in one turn, ticking plan tasks as you finish them. "
               "Switching mode later requires a new user decision — never decide it yourself.")
    print(
        f"[TDQ] USER APPROVED {target.upper()} {rel} "
        f"(sha256 {state[sha_key][:12]}, {state[at_key]}). Next: {nxt} "
        "All user-facing output in Vietnamese."
    )


if __name__ == "__main__":
    main()
