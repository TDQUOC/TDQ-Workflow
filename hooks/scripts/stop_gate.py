#!/usr/bin/env python3
"""Stop — đối chiếu lời nhắc với HIỆU ỨNG thật, cuối turn.

Nguồn dữ liệu duy nhất là sổ turn docs/tdq/.tdq-turn.jsonl (do 2 hook PreToolUse
ghi). Hook này KHÔNG đọc transcript và KHÔNG tin dòng echo model tự in — 0.1.8
từng đọc transcript và chặn nhầm turn hợp lệ vì transcript trễ, còn model yếu
thì có thể in echo giả.

Điểm CHẶN duy nhất: repo đổi mà working log hôm nay chưa được cập nhật.
Mọi mã còn lại chỉ nhắc lại qua additionalContext.
Trần: ≤4 dòng / 300 ký tự (spec §2.7). `stop_hook_active` → im lặng tuyệt đối.

0.3.1 — sổ turn chỉ thấy hành động đi qua tool Edit/Write, nên thay đổi qua shell
vô hình với nó: vừa chặn oan (log append bằng `cat >>`) vừa bỏ lọt (sửa repo bằng
`sed -i`). Vì vậy hook đối chiếu thêm với ĐĨA: ảnh chụp `turn_start` do
prompt_context ghi đầu turn so với trạng thái hiện tại. Không có ảnh chụp (turn
không mở bằng user prompt, project không phải git repo) → rơi về đúng hành vi cũ.
"""
import json
import os

from _common import payload_cwd, read_payload, tdq_state, turn_rows

MAX_LINES = 4
MAX_CHARS = 300
MAX_PATH_CHARS = 60

# Lưới an toàn thứ hai cho vùng sổ sách: `repo_status_paths` đã loại trừ sẵn bằng
# pathspec của git, đây chỉ là chốt chặn khi bản git quá cũ không hiểu `:(top,exclude)`.
# Dùng đúng danh sách của tdq_state để quyết định và đặt tên không bao giờ lệch nhau
# (chính chỗ lệch đó là chặn oan 0.3.1), và khớp theo `/` vì git in path bằng `/`.
BOOKKEEPING = tuple(p + "/" for p in tdq_state.BOOKKEEPING_PATHS)

# mã → (sự kiện chứng minh đã làm, câu nhắc lại nếu thiếu)
EFFECTS = {
    "TDQ:NEXT": ("next_run", "chưa chạy `tdq_state.py next` — chạy để biết bước kế tiếp."),
    "TDQ:STATE": ("state_cli", "chưa ghi state bằng CLI — dùng `tdq_state.py set|approve`."),
}


def _snapshot(rows):
    """Ảnh chụp đầu turn — lấy dòng MỚI NHẤT.

    Bình thường mỗi turn chỉ có một dòng (turn_log_clear xoá sổ đầu turn). Nếu
    việc xoá hụt thì dòng còn sót là của turn trước: lấy nó làm mốc là so với
    trạng thái có thể cũ tới 6 giờ → gán oan thay đổi của turn cũ cho turn này.
    """
    found = None
    for row in rows:
        if row.get("kind") == "turn_start":
            found = row
    return found


def _sha(path):
    try:
        return tdq_state.sha256_file(path)
    except OSError:
        return None


def _log_changed(cwd, snap):
    """Log hôm nay có đổi so với đầu turn không (bất kể ghi bằng cách nào)."""
    log_rel = tdq_state.today_log_rel()
    now = _sha(os.path.join(cwd, log_rel))
    if now is None:
        return False
    before = snap.get("log_sha")
    if snap.get("log_rel") != log_rel:
        return True                      # turn vắt qua nửa đêm: file ngày mới đã có
    if before is None:
        return True                      # đầu turn chưa có file, giờ đã có
    return isinstance(before, str) and now != before


def _repo_changed(cwd, snap):
    before = snap.get("repo_sha")
    if not isinstance(before, str):
        return False                     # không phải git repo / không lấy được
    now = tdq_state.repo_status_digest(cwd)
    if not isinstance(now, str):
        # Đầu turn lấy được vân tay mà cuối turn thì không → có gì đó hỏng thật.
        tdq_state._warn("stop_gate: cuối turn không lấy được vân tay repo — "
                        "bỏ qua bằng chứng đĩa, chỉ còn dựa vào sổ turn")
        return False
    return now != before


def _shell_changed_path(cwd, snap):
    """Tên file để nêu trong lời chặn — ưu tiên file mới xuất hiện trong turn.

    Chuỗi rỗng = thay đổi chỉ nằm ở sổ sách workflow → không tính là đổi repo.
    """
    before = snap.get("repo_paths")
    before = set(before) if isinstance(before, list) else set()
    fresh, known = "", ""
    for path in tdq_state.repo_status_paths(cwd):
        if not isinstance(path, str) or path.startswith(BOOKKEEPING):
            continue
        if path not in before:
            fresh = fresh or path
        else:
            known = known or path
    return (fresh or known)[:MAX_PATH_CHARS]


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return
    cwd = payload_cwd(payload)
    state = tdq_state.load(cwd)
    if state is None or not state.get("active_request"):
        return

    rows = turn_rows(cwd, payload)
    log_rel = tdq_state.today_log_rel()
    log_dir = os.path.join("docs", "workinglog")
    snap = _snapshot(rows)

    edited = [r.get("path", "") for r in rows
              if r.get("kind") == "observe" and r.get("event") == "edit"
              and not str(r.get("path", "")).startswith(log_dir)]
    logged = any(r.get("kind") == "observe" and r.get("event") == "log_written" for r in rows)

    # Bằng chứng thứ hai, độc lập với tên tool: hiệu ứng thật trên đĩa.
    culprit = edited[0] if edited else ""
    source = "sổ turn" if culprit else "—"
    if snap:
        if not logged:
            logged = _log_changed(cwd, snap)
        if not culprit and _repo_changed(cwd, snap):
            culprit = _shell_changed_path(cwd, snap)
            source = "vân tay repo"

    if culprit and not logged:
        # §6: quyết định chặn phải truy vết được — chặn oan thì biết ngay do nguồn nào.
        tdq_state._info(f"stop_gate: chặn TDQ:LOG · nguồn={source} · path={culprit}")
        print(json.dumps({
            "decision": "block",
            "reason": (f"[TDQ:LOG] Turn này đổi repo ({culprit}) nhưng {log_rel} chưa được append. "
                       "Thêm mục \"## HH:MM — <việc>\" ở CUỐI file (ngữ cảnh, file đổi, lý do, "
                       "test đã chạy), tick [x] task plan đã xong, rồi mới kết thúc turn."),
        }, ensure_ascii=False))
        return

    reminded = {r.get("code") for r in rows if r.get("kind") == "remind"}
    done = {r.get("event") for r in rows if r.get("kind") == "observe"}
    hints = []
    for code, (event, message) in EFFECTS.items():
        if code in reminded and event not in done:
            hints.append(f"[{code}] {message}")
    if "TDQ:APPROVE" in reminded:
        target = next((t for t in ("spec", "plan", "quick") if not state.get(f"{t}_approved")), None)
        if target:
            hints.append(f"[TDQ:APPROVE] {target} vẫn chưa được ghi nhận duyệt — "
                         "user đã duyệt thì chạy `tdq_state.py approve`, chưa rõ thì HỎI.")
    if "TDQ:GIT" in reminded:
        hints.append("[TDQ:GIT] Kiểm lại tên branch/commit message theo quy ước trước khi đi tiếp.")

    if not hints:
        return
    text = "\n".join(hints[:MAX_LINES])
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 1].rstrip() + "…"
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": text}
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
