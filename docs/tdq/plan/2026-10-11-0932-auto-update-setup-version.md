# QUICK — Tự động cập nhật setup khi phát hiện version mới qua SessionStart

**Ngày:** 2026-10-11 · Brief: ../brief/2026-10-11-0932-auto-update-setup-version.md · Lane: quick
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong:
  1. Thêm hàm kiểm tra và tự động cập nhật setup khi phát hiện phiên bản mới trong `hooks/scripts/session_start.py` (đồng bộ instruction `~/.claude/CLAUDE.md`, khai MCP/hook Codex nếu có, ghi mốc version).
  2. Bổ sung `scripts/tdq_setup.py` hàm đồng bộ nhẹ nhàng (`dong_bo_khi_doi_version`).
  3. Viết test kiểm tra tự động cập nhật khi đổi version.
  4. Bump version lên `0.62.0`, cập nhật CHANGELOG và commit.
- NGOÀI: Tự động chạy git pull (việc pull plugin do package manager / marketplace hoặc user quyết định).
- Bỏ B0: đã có tiền lệ sửa session_start và tdq_setup.
- Bỏ B2: không dùng lib/API ngoài.

## Task
- [x] **T1** Bổ sung cơ chế phát hiện đổi version và tự động đồng bộ setup trong session_start.py & tdq_setup.py — Test: `pytest tests/test_auto_update_setup.py -q` <!-- Chạm: `hooks/scripts/session_start.py`, `scripts/tdq_setup.py` -->
- [x] **T2** Viết unit tests cho tính năng tự động đồng bộ khi đổi version — Test: `pytest tests/test_auto_update_setup.py -q` <!-- Chạm: `tests/test_auto_update_setup.py` -->
- [x] **T3** Cập nhật CHANGELOG, bump version 0.62.0 và kiểm thử toàn diện — Test: `pytest tests/test_luat_skill.py tests/test_docs_consistency.py tests/test_doc_lint.py -q` <!-- Chạm: `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `docs/tdq/token-budget.json` -->

## Definition of Done
- `session_start.py` kiểm tra version stamp; khi version plugin > version stamp hoặc chưa có stamp $\rightarrow$ gọi tự động cập nhật instruction và cấu hình.
- Đổi version không gây crash hoặc treo session; không đòi hỏi permission prompt tương tác.
- Áp dụng hiệu quả cho cả Claude Code và Codex.
- Toàn bộ test suite xanh 100%, drift = 0%.

## QC
- [x] DoD 1: `can_cap_nhat_phien_ban` và `tu_dong_cap_nhat_khi_doi_phien_ban` kiểm tra và đồng bộ mốc phiên bản thành công (ĐẠT)
- [x] DoD 2: `session_start.py` chạy an toàn không crash, không hỏi interactive prompt (ĐẠT)
- [x] DoD 3: Áp dụng cho cả Claude Code (`CLAUDE.md`) và Codex (`tdq_codex_mcp`) (ĐẠT)
- [x] DoD 4: 158/158 tests passed, 506 subtests passed, 0.00% drift (ĐẠT)
- Mức QC: `full` — DoD + test của từng task đều PASS. Kết quả: 4/4 DoD ĐẠT.
