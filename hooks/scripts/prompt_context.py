#!/usr/bin/env python3
"""UserPromptSubmit: inject at most ONE line, and only when a request is open
(full lane: always one phase reminder; quick lane: only while awaiting
approval). Silent otherwise to keep the idle token cost at zero.
"""
import os

from _common import read_payload, payload_cwd, tdq_state, APPROVE_CMD

NEXT = {
    "idle": "bắt đầu intake (tdq-start)",
    "analyze": "hoàn tất phân tích & interview — không đoán, hỏi user khi chưa rõ",
    "spec": "hoàn thành spec + đăng ký spec_file, trình user duyệt",
    "plan": "hoàn thành plan + đăng ký plan_file, trình user duyệt",
    "implement": "implement end-to-end trong 1 turn + tick [x] plan",
    "qc": "chạy QC theo spec; bug → thêm task fix vào plan (không cần duyệt lại)",
    "report": "viết report ≤50 dòng vào docs/tdq/reports/",
}


def main():
    payload = read_payload()
    cwd = payload_cwd(payload)
    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        return

    lane = state.get("lane")
    if lane == "quick":
        if not state.get("quick_approved"):
            print(f"[TDQ] Quick lane đang chờ duyệt — trình plan ≤10 dòng và hiển thị: "
                  f"➤ Để duyệt: gõ {APPROVE_CMD} quick · Góp ý: nhắn trực tiếp")
        return
    if lane != "full":
        return

    if state.get("spec_file") and not state.get("spec_approved"):
        print(f"[TDQ] Phase {state.get('phase')} — state CHƯA ghi nhận duyệt spec (không được coi là đã duyệt): hiển thị "
              f"➤ Để duyệt: gõ {APPROVE_CMD} spec · Góp ý: nhắn trực tiếp")
        return
    if state.get("spec_approved") and state.get("plan_file") and not state.get("plan_approved"):
        print(f"[TDQ] Phase {state.get('phase')} — state CHƯA ghi nhận duyệt plan (không được coi là đã duyệt): hiển thị "
              f"➤ Để duyệt: gõ {APPROVE_CMD} plan · Góp ý: nhắn trực tiếp")
        return

    rel, sha = state.get("spec_file"), state.get("spec_sha256")
    if state.get("spec_approved") and rel and sha:
        path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        try:
            drifted = tdq_state.sha256_file(path) != sha
        except OSError:
            drifted = True
        if drifted:
            print("[TDQ] ⚠️ Spec đã thay đổi sau khi duyệt (sha256 lệch) — cần trình user duyệt lại spec.")
            return

    phase = state.get("phase") or "idle"
    print(f"[TDQ] Phase {phase} — {NEXT.get(phase, 'tiếp tục workflow')}")


if __name__ == "__main__":
    main()
