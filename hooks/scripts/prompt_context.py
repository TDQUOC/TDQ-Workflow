#!/usr/bin/env python3
"""UserPromptSubmit — mở turn mới.

Ba việc:
1. Xoá sổ turn của session này (phạm vi đối chiếu tuân thủ gói trong 1 turn).
2. Phát TDQ:APPROVE khi đang chờ duyệt VÀ prompt khớp dấu hiệu duyệt (spec
   §2.9.2). Mơ hồ → không phát, và nhắc agent HỎI thay vì suy diễn.
3. Phát TDQ:NEXT — đúng 1 dòng `next --brief`.

Trần ngân sách: ≤3 dòng / 240 ký tự (spec §2.7). Im lặng khi rảnh.
"""
import hashlib
import os
import re
import sys

from _common import (approve_hint, payload_cwd, plan_mode, read_payload,
                     session_id)
# Đặt SAU `from _common`: chính `_common` bơm `scripts/` vào sys.path. Dùng from-import
# (không gọi qua thuộc tính module) để graphify sinh được cạnh `calls` cross-file.
from tdq_state import (effective_lane, effective_mode,  # noqa: E402
                       effective_phase, load, phase_key, prompt_context_last,
                       prompt_context_save, render_next, sha256_file,
                       turn_log_append, turn_log_clear, turn_snapshot)

MAX_LINES = 3
MAX_CHARS = 240

# Dấu hiệu duyệt = (a) từ chỉ sự đồng ý  VÀ  (b) đối tượng đang chờ duyệt.
AGREE = re.compile(r"\b(duyệt|duyet|ok|oke|okay|đồng\s*ý|dong\s*y|chốt|chot|approve|"
                   r"làm\s*đi|lam\s*di|tiến\s*hành|tien\s*hanh)\b", re.IGNORECASE)
OBJECT = re.compile(r"\b(spec|plan|quick|mini-?plan)\b", re.IGNORECASE)
# Bí danh tiếng Việt/Anh của lane quick. `nhanh` là tính từ rất thường gặp ("làm
# nhanh giúp tôi") nên CHỈ tính là câu duyệt khi đứng NGAY SAU từ đồng ý — không
# dùng chung đường với OBJECT ở trên, vì OBJECT chỉ cần có mặt đâu đó trong câu.
APPROVE_FAST = re.compile(
    r"\b(duyệt|duyet|chốt|chot|approve)\s+(chế\s*độ\s*nhanh|che\s*do\s*nhanh|nhanh|express)\b",
    re.IGNORECASE)
PRONOUN = re.compile(r"(cái\s*này|cai\s*nay|cái\s*đó|cai\s*do|cái\s*trên|cai\s*tren)", re.IGNORECASE)
# Câu hỏi thì không phải câu duyệt, dù có đủ hai thành phần.
QUESTION = re.compile(r"(\?|\bchưa\b|\bchua\b|\bkhông\b\s*$|\bko\b\s*$)", re.IGNORECASE)
MODE = re.compile(r"\b(main|subagent)\b", re.IGNORECASE)


def looks_like_approval(prompt, target):
    if not prompt:
        return False
    if QUESTION.search(prompt):
        return False
    if target == "mode":
        # Câu trả lời ở cổng mode thường trống trơn: "main", "subagent", "chọn main".
        # Không đòi từ đồng ý — user đã duyệt plan rồi, đây chỉ là chọn cách làm.
        return bool(MODE.search(prompt))
    if target == "quick" and APPROVE_FAST.search(prompt):
        return True
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
    turn_log_clear(cwd, sid)
    # Ảnh chụp đĩa đầu turn — để stop_gate cuối turn biết cái gì ĐÃ THẬT SỰ đổi,
    # kể cả khi thay đổi đi qua shell (sổ turn chỉ thấy tool Edit/Write).
    # Ghi vào sổ, KHÔNG in ra context → không tốn token của model.
    turn_log_append(cwd, "turn_start", session=sid, **turn_snapshot(cwd))

    # Không có request MỞ (mở = có active_request VÀ phase != idle) → nhắc intake.
    # Dòng INTAKE đứng TRƯỚC để không bao giờ bị _truncate cắt cụt (cắt từ đuôi).
    intake = ("[TDQ:INTAKE] Chưa có request mở — prompt KHÔNG thuộc vòng intake đang dở "
              "thì mở tdq-intake trước khi làm gì khác.")
    state = load(cwd)
    if state is None or not state.get("active_request"):
        _emit(cwd, sid, [intake])
        return
    # phase_key, không phải phase thô: lane quick đang chạy giữ phase=idle thô —
    # so thô sẽ bắn INTAKE nhầm và nuốt mất dòng APPROVE của quick.
    if phase_key(state) == "idle":
        _emit(cwd, sid, [intake, render_next(cwd, state, brief=True)])
        return

    lane = effective_lane(state, warn=False)
    pending = None
    if lane == "quick" and not state.get("quick_approved"):
        pending = "quick"
    elif lane == "full" and state.get("spec_file") and not state.get("spec_approved"):
        pending = "spec"
    elif lane == "full" and state.get("spec_approved") and state.get("plan_file") \
            and not state.get("plan_approved"):
        pending = "plan"
    elif lane == "full" and state.get("plan_approved") \
            and effective_phase(state, warn=False) == "mode" \
            and not effective_mode(state, warn=False):
        # Cổng mode: plan đã duyệt nhưng user chưa chọn cách làm. Câu trả lời ở đây
        # thường chỉ là "main"/"subagent" trống trơn, nên nhận diện riêng.
        pending = "mode"

    lines = [render_next(cwd, state, brief=True)]

    if pending:
        # Dòng APPROVE đứng TRƯỚC NEXT: _truncate cắt từ đuôi — cắt path project
        # còn hơn cắt cụt câu hint/câu lệnh approve (bug hint cụt 2026-08-02).
        lines = []
        prompt = payload.get("prompt") or ""
        planned = plan_mode(cwd, state) if pending in ("plan", "mode") else None
        matched = looks_like_approval(prompt, pending)
        turn_log_append(cwd, "signal", session=sid, event="approve_pending",
                        target=pending, matched=matched, mode_conflict=False)
        if matched:
            mode = ""
            if pending == "mode":
                # Cổng mode: câu trả lời CHÍNH LÀ mode. Chọn khác mode plan đề xuất
                # không phải xung đột — đề xuất chỉ là đề xuất, user mới là người chốt.
                found = MODE.search(prompt)
                said = found.group(1).lower() if found else (planned or "main")
                lines.append("[TDQ:APPROVE] User vừa chọn mode → chạy NGAY: "
                             f"python3 scripts/tdq_state.py approve plan --mode {said} "
                             f"--by \"{prompt[:60]}\"")
                lines.append(render_next(cwd, state, brief=True))
                _emit(cwd, sid, lines, critical=True)
                return
            if pending == "plan":
                found = MODE.search(prompt)
                said = found.group(1).lower() if found else None
                if said and planned and said != planned:
                    # Mode trong câu duyệt lệch mode ĐÃ CHỐT trong plan — không
                    # được ghi nhận theo suy diễn, bắt agent HỎI user xác nhận.
                    turn_log_append(cwd, "signal", session=sid, event="approve_pending",
                                    target=pending, matched=matched, mode_conflict=True)
                    lines.append(f"[TDQ:APPROVE] ⚠️ Câu duyệt nói mode {said} nhưng plan chốt "
                                 f"{planned} — HỎI user xác nhận mode trước, chưa chạy approve.")
                    _emit(cwd, sid, lines, critical=True)
                    return
                # Không nói mode thì KHÔNG chèn placeholder: thiếu mode giờ là hợp lệ,
                # phase `mode` ngay sau sẽ hỏi. Placeholder khiến agent hỏi sớm một nhịp.
                mode = f" --mode {said}" if said else ""
            lines.append(f"[TDQ:APPROVE] User vừa duyệt {pending} → chạy NGAY: "
                         f"python3 scripts/tdq_state.py approve {pending}{mode} "
                         f"--by \"{prompt[:60]}\"")
        else:
            waiting = "chờ user chọn mode" if pending == "mode" else f"chờ duyệt {pending}"
            lines.append(f"[TDQ:APPROVE] Đang {waiting}. Prompt này KHÔNG rõ là câu duyệt "
                         f"→ tuyệt đối không suy diễn: hoặc HỎI lại, hoặc in \"{approve_hint(pending, planned)}\".")
        lines.append(render_next(cwd, state, brief=True))
        # Không dedupe: mỗi turn phải thấy lại cảnh báo "đừng suy diễn duyệt" —
        # nén thành "(như turn trước)" ở đây sẽ nuốt mất chính cảnh báo an toàn đó.
        _emit(cwd, sid, lines, critical=True)
        return

    # spec đã duyệt mà file đổi sau đó → cảnh báo (dấu vết duyệt không còn khớp)
    rel, sha = state.get("spec_file"), state.get("spec_sha256")
    drifted = False
    if state.get("spec_approved") and rel and sha:
        path = rel if os.path.isabs(rel) else os.path.join(cwd, rel)
        try:
            drifted = sha256_file(path) != sha
        except OSError:
            drifted = True
        if drifted:
            lines.append("[TDQ:APPROVE] ⚠️ Spec đã đổi sau khi duyệt (sha256 lệch) — trình user duyệt lại.")
    _emit(cwd, sid, lines, critical=drifted)


def _truncate(text, limit=MAX_CHARS):
    if len(text) <= limit:
        return text
    cut = limit - 1
    # A22: điểm cắt rơi giữa inline-code sẽ để lại nửa lệnh trông như lệnh thật —
    # số backtick lẻ nghĩa là đang ở trong span, lùi về trước backtick mở.
    if text[:cut].count("`") % 2 == 1:
        cut = text.rfind("`", 0, cut)
    return text[:cut].rstrip() + "…"


def _compact(text):
    """Turn trước đã in y hệt nội dung này — thay bằng dòng ngắn cùng mã."""
    match = re.match(r"^\[(TDQ:[A-Z]+)\]", text)
    code = match.group(1) if match else "TDQ"
    return f"[{code}] (như turn trước — chưa đổi)"


def _emit(cwd, session, lines, critical=False):
    """critical=True: cảnh báo/hành động riêng cho turn này (duyệt mơ hồ, mode
    lệch, spec drift) — không bao giờ nén, kể cả trùng chữ với turn trước."""
    text = _truncate("\n".join(lines[:MAX_LINES]))
    if critical:
        print(text)
        return
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if prompt_context_last(cwd, session) == digest:
        text = _compact(text)
    else:
        prompt_context_save(cwd, session, digest)
    print(text)


if __name__ == "__main__":
    main()
