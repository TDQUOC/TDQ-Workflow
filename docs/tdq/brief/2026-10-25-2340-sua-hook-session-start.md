# Brief — Sửa Hook Session Start Tránh Bơm Toàn Bộ Luật Khi Idle
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "có okay mở request xử lí và test lại đi"

### Đọc hiểu lần đầu
- **Mục tiêu:** Sửa đổi logic nạp luật `[TDQ:GON]` trong hook `hooks/scripts/session_start.py` để loại bỏ việc bơm toàn bộ 133 dòng (~6.800 ký tự / ~2.000 tokens) của file `chung.md` khi một workspace đang ở phase `idle` hoặc chưa mở request (`active_request is None`).
- **Phạm vi dự kiến:**
  - Sửa `hooks/scripts/session_start.py` tại dòng kiểm tra `nap_day_du`: chỉ nạp đầy đủ thân luật khi `pha == "implement"`. Trong các phase khác hoặc khi chưa có request, chỉ xuất pointer ngắn 1 dòng (`[TDQ:GON] The build-less-than-asked law (muc_gat=full) — full ladder loads during phase implement...`).
  - Kiểm thử và bổ sung test case trong `tests/test_session_start_hook.py` hoặc test suite tương ứng để bảo đảm không tái phát.
- **Điểm chưa rõ:** Không có, phạm vi và nguyên nhân kỹ thuật đã được khoanh vùng chính xác 100%.

## Hiểu & kiến thức

### 1. Nguyên nhân gốc (Root Cause)
- Tại dòng 279 của `hooks/scripts/session_start.py`:
  `nap_day_du = (pha == "implement") or (not (state or {}).get("active_request"))`
  Ý đồ cũ là cho phép dùng luật ở chế độ standalone (khi không mở request TDQ). Tuy nhiên trong thực tế, mọi workspace thông thường khi bắt đầu phiên làm việc (hoặc khi chưa mở request, phase `idle`) đều không có `active_request`, dẫn đến việc hook tự động bơm toàn bộ thân luật 133 dòng (~2.000 tokens) gây phình context và tạo ra trải nghiệm bất ngờ cho người dùng.

### 2. Khảo sát 3 chiều (Triangulation Code Exploration)
- **Grep:** `nap_day_du` chỉ xuất hiện tại `hooks/scripts/session_start.py`. Các hook nạp luật khác:
  - `prompt_context.py` (UserPromptSubmit) chỉ nạp 1 dòng pointer ngắn gọn `NHAC_GON`.
  - `subagent_start.py` (SubagentStart) chỉ nạp thân luật khi subagent được tạo (pha implement).
- **LSP:** `mcp__lsp__blast_radius` cho thấy `session_start.py` là hook entry point chạy độc lập qua subprocess, chỉ được gọi trực tiếp bởi Claude Code CLI hoặc test runner (`tests/test_log_kenh_luat.py`, `tests/test_token_budget.py`).
- **Graphify:** Quan hệ phụ thuộc trỏ tới `luat_gon.py` (`loc_than_luat`, `doc_than_luat`) và `tdq_state.py`. Không có hiệu ứng vỡ lan sang các module khác.

### 3. Phương án xử lý
- Cắt bỏ vế `or (not (state or {}).get("active_request"))`, chỉ giữ lại:
  `nap_day_du = (pha == "implement")`
- Cập nhật comment giải thích trong `session_start.py`.
- Thêm test case vào `tests/test_log_kenh_luat.py`: kiểm tra khi workspace không có `active_request` hoặc state rỗng (phase `idle` / `no_state`), hook `SessionStart` chỉ xuất 1 dòng pointer ngắn, `so_dong` trong `.tdq-turn.jsonl` ghi nhận đúng `1`, và không chứa bất kỳ dòng thân luật nào.

## Hỏi đáp
- Không có vướng mắc nào cần hỏi thêm người dùng. Phạm vi và giải pháp kỹ thuật đã xác định đầy đủ.
