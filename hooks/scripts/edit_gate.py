#!/usr/bin/env python3
"""PreToolUse gate for Edit|Write|MultiEdit|NotebookEdit.

Hybrid gate: blocks file edits outside docs/** until the approval required by
the current lane exists; the deny reason simultaneously reminds Claude what to
finish and shows the exact approve command for the user. docs/** stays always
writable so spec/plan/log work can proceed — the single exception is
docs/tdq/state.json, which is protected from direct edits at all times.
"""
import json
import os
from datetime import datetime

from _common import read_payload, payload_cwd, deny, approve_hint, tdq_state


def within(child, parent):
    return child == parent or child.startswith(parent + os.sep)


def main():
    payload = read_payload()
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not target:
        return
    cwd = payload_cwd(payload)
    abs_target = os.path.realpath(target if os.path.isabs(target) else os.path.join(cwd, target))
    state_file = os.path.realpath(tdq_state.state_path(cwd))

    if abs_target == state_file or abs_target.endswith(os.path.join("docs", "tdq", "state.json")):
        deny("[TDQ GATE] docs/tdq/state.json là file trạng thái được bảo vệ — không Edit/Write trực tiếp. "
             "Dùng scripts/tdq_state.py; field duyệt chỉ đổi khi user gõ /tdq-workflow:tdq-approve.")

    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        return

    docs_root = os.path.realpath(os.path.join(cwd, "docs"))
    if within(abs_target, docs_root):
        return  # docs/** always writable: spec/plan/questions/research/log

    lane = state.get("lane")
    if lane == "full":
        if not state.get("spec_approved"):
            deny("[TDQ GATE] Chưa được sửa file ngoài docs/ — SPEC chưa được user duyệt. Việc cần làm ngay: "
                 "hoàn thành spec (docs/tdq/spec/), đăng ký spec_file vào state, trình user summary ≤50 dòng "
                 f"và hiển thị đúng dòng: \"{approve_hint('spec')}\". Ghi file trong docs/** vẫn được phép.")
        if not state.get("plan_approved"):
            deny("[TDQ GATE] Chưa được sửa file ngoài docs/ — PLAN chưa được user duyệt. Việc cần làm ngay: "
                 "hoàn thành plan (docs/tdq/plan/), đăng ký plan_file vào state, trình user summary ≤100 dòng "
                 f"và hiển thị đúng dòng: \"{approve_hint('plan')}\". Ghi file trong docs/** vẫn được phép.")
        rel, sha = state.get("spec_file"), state.get("spec_sha256")
        if rel and sha:
            path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
            try:
                drifted = tdq_state.sha256_file(path) != sha
            except OSError:
                drifted = True
            if drifted:
                print(json.dumps({
                    "systemMessage": "⚠️ [TDQ] Spec đã thay đổi sau khi duyệt (sha256 lệch) — cần trình user duyệt lại spec."
                }, ensure_ascii=False))
        return

    if lane == "quick":
        if not state.get("quick_approved"):
            deny("[TDQ GATE] Lane quick chưa được user duyệt — trình plan ngắn nhất có thể (≤10 dòng: việc sẽ làm, "
                 "file sẽ đụng, cách quick validate/test) ngay trong chat và hiển thị đúng dòng: "
                 f"\"{approve_hint('quick')}\". Ghi file trong docs/** vẫn được phép.")
        try:
            approved_ts = datetime.fromisoformat(state.get("quick_approved_at")).timestamp()
        except (TypeError, ValueError):
            return
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(cwd, "docs", "workinglog", today + ".md")
        try:
            log_mtime = os.path.getmtime(log_path)
        except OSError:
            log_mtime = 0.0
        if log_mtime <= approved_ts:
            deny("[TDQ GATE] Quick đã duyệt nhưng summary plan CHƯA được append vào "
                 f"docs/workinglog/{today}.md — ghi log trước, rồi mới implement.")
        return


if __name__ == "__main__":
    main()
