# TDQ Workflow — portable

Bản chạy ngoài Claude Code (Codex, Antigravity, agent bất kỳ). Không cần hook.

1. Copy `portable/AGENTS.md` + `portable/workflow/` và `scripts/{tdq_state,skill_inventory,doc_lint}.py`
   vào project đích (giữ `scripts/`); mode external → thêm `scripts/{external_task.py,external_models.py,external_report_schema.json}`.
2. Yêu cầu: **Python 3** (chỉ dùng thư viện chuẩn, không cài thêm gì).
3. Trỏ agent đọc `AGENTS.md` đầu phiên; nó tự chạy `python3 scripts/tdq_state.py next` mỗi bước.
4. Kiểm nhanh: `python3 scripts/tdq_state.py next` phải in phase hiện tại và việc kế tiếp.
5. Deep search (cần agy CLI + `scripts/search_task.py`): xem `workflow/06-deep-search.md`.
