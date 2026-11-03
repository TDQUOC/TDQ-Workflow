# QC — Ưu tiên MCP, Auto Setup & Tự động Cập nhật Plugin

Ngày: 2026-10-20 · Spec: ../spec/2026-10-20-1115-uu-tien-mcp-auto-setup.md ·
Plan: ../plan/2026-10-20-1115-uu-tien-mcp-auto-setup.md · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mức `full` chạy: DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc.

**Kết luận: PASS 100%.** 4/4 hạng mục Definition of Done đạt chuẩn, không có lỗi hoặc độ lệch phát sinh.

## 4 hạng mục Definition of Done

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Instruction & Anchor MCP-First | **PASS** | `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` chứa mục `MCP-First` ghim vào `CLAUDE.md`; `hooks/scripts/session_start.py` tiêm `MCP-First` vào anchor phục hồi sau nén; `test_mcp_first_auto_setup.py` (2 tests) PASS. |
| Q2 | Pre-flight Check Guide & Spec/Plan | **PASS** | `skills/tdq-setup/references/mcp-first-guide.md` hướng dẫn chi tiết kịch bản kiểm tra kết nối cho Roblox, Unity, Chrome DevTools và câu thông báo hướng dẫn người dùng; `spec-template.md` (§3b) và `plan-template.md` đã tích hợp tiêu chí MCP; `doc_lint` 0 lỗi. |
| Q3 | Incremental Auto-Setup khi đổi version | **PASS** | `scripts/tdq_setup.py:tu_dong_cap_nhat_khi_doi_phien_ban` và `thuc_hien_setup_bu` tự động thực thi cài bù đắp shim, cập nhật instruction, đồng bộ codex và kiểm thử dryrun hook; `test_thuc_hien_setup_bu` và `test_can_cap_nhat_phien_ban_detects_mismatch` PASS; `test_tu_khoi_tao.py` 36 tests PASS. |
| Q4 | SessionStart Auto Update Plugin | **PASS** | `hooks/scripts/session_start.py` và `tdq_setup.py:tu_dong_cap_nhat_plugin_user` phát hiện bản cài user scope cũ hơn repo nguồn và tự động gọi cập nhật/đồng bộ cache; `test_tu_dong_cap_nhat_plugin_user_with_cli_runner` PASS; `test_context_hooks.py` 35 tests PASS. |

## Độ lệch spec (Spec Deviations)
- Không có.
