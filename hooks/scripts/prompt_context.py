#!/usr/bin/env python3
"""UserPromptSubmit — mở turn mới.

Ba việc:
1. Xoá sổ turn của session này (phạm vi đối chiếu tuân thủ gói trong 1 turn).
2. Phát TDQ:APPROVE khi đang chờ duyệt VÀ prompt khớp dấu hiệu duyệt (spec
   §2.9.2). Mơ hồ → không phát, và nhắc agent HỎI thay vì suy diễn.
3. Phát TDQ:NEXT — đúng 1 dòng `next --brief`.

Trần ngân sách: ≤3 dòng / 240 ký tự (spec §2.7). Im lặng khi rảnh.
"""
import os
import re
import sys

from _common import (approve_hint, payload_cwd, read_payload, session_id, tdq_state)

MAX_LINES = 3
MAX_CHARS = 240

# Dấu hiệu duyệt = (a) từ chỉ sự đồng ý  VÀ  (b) đối tượng đang chờ duyệt.
AGREE = re.compile(r"\b(duyệt|duyet|ok|oke|okay|đồng\s*ý|dong\s*y|chốt|chot|approve|"
                   r"làm\s*đi|lam\s*di|tiến\s*hành|tien\s*hanh)\b", re.IGNORECASE)
OBJECT = re.compile(r"\b(spec|plan|quick|mini-?plan)\b", re.IGNORECASE)
PRONOUN = re.compile(r"(cái\s*này|cai\s*nay|cái\s*đó|cai\s*do|cái\s*trên|cai\s*tren)", re.IGNORECASE)
# Câu hỏi thì không phải câu duyệt, dù có đủ hai thành phần.
QUESTION = re.compile(r"(\?|\bchưa\b|\bchua\b|\bkhông\b\s*$|\bko\b\s*$)", re.IGNORECASE)
MODE = re.compile(r"\b(main|subagent)\b", re.IGNORECASE)


def looks_like_approval(prompt, target):
    if not prompt:
        return False
    if QUESTION.search(prompt):
        return False
    if not AGREE.search(prompt):
        return False
    match = OBJECT.search(prompt)
    if match:
        said = match.group(1).lower().replace("-", "")
        return said == target or (target == "quick" and said in ("quick", "miniplan"))
    # Không nêu đối tượng thì chỉ chấp nhận đại từ trỏ rõ ("duyệt cái này").
    # "ok", "ok tôi hiểu rồi" KHÔNG phải câu duyệt — mơ hồ thì để agent HỎI.
    return bool(PRONOUN.search(prompt))


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    sid = session_id(payload)
    tdq_state.turn_log_clear(cwd, sid)
    # Ảnh chụp đĩa đầu turn — để stop_gate cuối turn biết cái gì ĐÃ THẬT SỰ đổi,
    # kể cả khi thay đổi đi qua shell (sổ turn chỉ thấy tool Edit/Write).
    # Ghi vào sổ, KHÔNG in ra context → không tốn token của model.
    tdq_state.turn_log_append(cwd, "turn_start", session=sid, **tdq_state.turn_snapshot(cwd))

    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        return

    lane = tdq_state.effective_lane(state, warn=False)
    pending = None
    if lane == "quick" and not state.get("quick_approved"):
        pending = "quick"
    elif lane == "full" and state.get("spec_file") and not state.get("spec_approved"):
        pending = "spec"
    elif lane == "full" and state.get("spec_approved") and state.get("plan_file") \
            and not state.get("plan_approved"):
        pending = "plan"

    lines = [tdq_state.render_next(cwd, state, brief=True)]

    if pending:
        prompt = payload.get("prompt") or ""
        if looks_like_approval(prompt, pending):
            mode = ""
            if pending == "plan":
                found = MODE.search(prompt)
                mode = f" --mode {found.group(1).lower()}" if found else " --mode <main|subagent>"
            lines.append(f"[TDQ:APPROVE] User vừa duyệt {pending} → chạy NGAY: "
                         f"python3 scripts/tdq_state.py approve {pending}{mode} "
                         f"--by \"{prompt[:60]}\"")
        else:
            lines.append(f"[TDQ:APPROVE] Đang chờ duyệt {pending}. Prompt này KHÔNG rõ là câu duyệt "
                         f"→ tuyệt đối không suy diễn: hoặc HỎI lại, hoặc in \"{approve_hint(pending)}\".")
        _emit(lines)
        return

    # spec đã duyệt mà file đổi sau đó → cảnh báo (dấu vết duyệt không còn khớp)
    rel, sha = state.get("spec_file"), state.get("spec_sha256")
    if state.get("spec_approved") and rel and sha:
        path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        try:
            drifted = tdq_state.sha256_file(path) != sha
        except OSError:
            drifted = True
        if drifted:
            lines.append("[TDQ:APPROVE] ⚠️ Spec đã đổi sau khi duyệt (sha256 lệch) — trình user duyệt lại.")
    _emit(lines)


def _emit(lines):
    text = "\n".join(lines[:MAX_LINES])
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 1].rstrip() + "…"
    print(text)


if __name__ == "__main__":
    main()
