# REPORT — Ưu tiên MCP, Auto Setup & Tự động Cập nhật Plugin (`2026-10-20-1115-uu-tien-mcp-auto-setup` · lane full · mode main · 6 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 Thiết lập nguyên tắc MCP-First toàn cục trong `KHOI_HUONG_DAN` (`CLAUDE.md`), khối neo phục hồi sau nén `[TDQ:ANCHOR]` trong `hooks/scripts/session_start.py`, cẩm nang `mcp-first-guide.md` chuẩn hóa kịch bản pre-flight connection check (Roblox, Unity, Chrome DevTools), và cập nhật mẫu spec/plan (§3b) · P2 Nâng cấp `tu_dong_cap_nhat_khi_doi_phien_ban` và `thuc_hien_setup_bu` trong `scripts/tdq_setup.py`: tự động cài bù shim, ghim instruction, đồng bộ codex và kiểm thử hook khi phát hiện version cũ · P3 Tích hợp hàm `tu_dong_cap_nhat_plugin_user` trong `session_start.py`: tự động phát hiện bản cài user scope cũ hơn repo nguồn và nâng cấp/đồng bộ plugin · P4 Xây dựng bộ test suite độc lập `tests/test_mcp_first_auto_setup.py` bao phủ 100% chức năng.
**Kết quả:** Quy tắc MCP-First được cưỡng chế toàn diện: mọi tác vụ đặc thù (Roblox/Unity/DevTools/DB) bắt buộc rà soát MCP, pre-flight check kết nối và hướng dẫn mở server nếu chưa kết nối · Nâng cấp plugin và setup bù đắp chạy hoàn toàn tự động, giải phóng người dùng khỏi việc gõ lệnh thủ công.
**Kiểm:** `py -3 tests/test_mcp_first_auto_setup.py` (6 tests OK) · `tests/test_tu_khoi_tao.py` (36 tests OK) · `tests/test_auto_fix_python3_hook.py` (7 tests OK) · `tests/test_context_hooks.py` (35 tests OK) · `doc_lint` 0 lỗi trên toàn bộ spec/plan/guide · QC 4/4 hạng mục DoD PASS.
**Đầu ra:** `skills/tdq-setup/references/mcp-first-guide.md` · `scripts/tdq_setup.py` · `hooks/scripts/session_start.py` · `skills/tdq-spec/references/spec-template.md` · `skills/tdq-plan/references/plan-template.md` · `tests/test_mcp_first_auto_setup.py`.
**Giới hạn:** Không tự động tạo MCP server mới ngoài các MCP người dùng hoặc hệ thống đã cấu hình.
**Lệch spec chờ duyệt:** không có.
**Git:** Nhánh request `feature/uu-tien-mcp-auto-setup` đã sẵn sàng để commit và merge về nhánh gốc `chore/graphify-precision-recall-ranking`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 14s | — | 1 |
| analyze | 2 min | — | 1 |
| spec | 7 min | — | 1 |
| plan | 1 min | — | 1 |
| implement | 6 min | — | 1 |
| qc | 21s | — | 1 |
| report | 5s | — | 1 |
| **Total** | **17 min** | **—** | |
