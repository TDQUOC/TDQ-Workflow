# REPORT — Sub-agent không truy cập được worktree TDQ

Ngày: 2026-10-20 · Request: `2026-10-20-0032-graphify-full-wiki-search`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: **BLOCKED đã chuyển hướng sang inline implement theo quyết định của user**

## Tóm tắt

Mode `subagent` đã lập ledger và mở ba worktree task đúng bằng `scripts/tdq_team.py`, nhưng các sub-agent bị harness cô lập vào worktree agent khác. Vì vậy họ không thể ghi vào vùng file task được giao hoặc tạo branch mergeable. Không có thay đổi code nào từ các task bị giao được chấp nhận.

## Timeline và chứng cứ

1. `tdq_team.py assign` tạo ledger: 6/8 task giao sub-agent, 2 task leader giữ (`T1.1` vì `(mcp)`, `T3.2` vì file luật).
2. `tdq_team.py open` tạo đúng các worktree TDQ:
   - `...\.tdq-worktrees\2026-10-20-0032-graphify-full-wiki-search\t1.2`
   - `...\.tdq-worktrees\2026-10-20-0032-graphify-full-wiki-search\t2.1`
   - `...\.tdq-worktrees\2026-10-20-0032-graphify-full-wiki-search\t2.2`
3. Các sub-agent báo harness thực tế ghim họ tại `...\.claude\worktrees\agent-<id>`, khác với worktree trên.
4. Khi thử `EnterWorktree(path=...)`, tool trả `InputValidationError: Provide at most one of name or path, not both`; khi bỏ name, harness vẫn truyền chuỗi rỗng và trả `Invalid worktree name ""`.
5. Không task nào trong T1.2/T2.1/T2.2 có diff, test xanh mới hay `MERGE-READY` từ sub-agent.
6. `tdq_team.py sweep --clean` xóa T2.2 nhưng Windows từ chối xóa T1.2/T2.1: `Permission denied`. Ledger xác nhận hai worktree sạch và merged; chúng không bị xóa để tránh can thiệp phá hủy khi còn handle mở.

## Tác động

- Mode sub-agent không thể hoàn thành các task file-zone trong phiên này.
- Kế hoạch bị dừng đúng loại `mat-truy-cap`; không có thao tác ghi ngoài vùng hoặc merge mù.
- T1.1 do leader thực hiện trực tiếp vẫn hoàn thành: commit `f2a5f4e` thêm `scripts/tdq_graphify.py` và `tests/test_tdq_graphify.py`, 6 tests xanh.

## Mitigation đã thực hiện

- Dừng các sub-agent còn chạy; không sao chép thay đổi từ worktree agent cô lập.
- Chạy `tdq_team.py resolve` cho T2.1: branch sạch, không conflict và không có thay đổi để merge.
- Chạy `tdq_team.py sweep --clean`; chỉ T2.2 được dọn thành công. T1.2/T2.1 giữ nguyên do Windows báo handle/permission.
- Người dùng chọn chuyển sang `main` / inline implement. `tdq_state.py approve plan --mode main` đã ghi mode mới và `resume` đã xóa pause.

## Hướng khắc phục dài hạn

1. Sửa harness Agent để worktree do `tdq_team.py open` là working directory thực, hoặc để `EnterWorktree` gửi đúng một tham số `path` không kèm name rỗng.
2. Thêm integration test tạo TDQ task worktree, khởi agent sandbox, xác minh agent ghi được đúng vùng file và `merge` nhận branch.
3. Trước cleanup Windows, đóng process/handle của agent đã dừng; retry cleanup an toàn, không dùng xóa cưỡng bức khi worktree có thể còn thay đổi.
4. Khi hạ tầng chưa sửa, chọn inline implement từ đầu cho task có file-zone; không mô phỏng sub-agent là đã chạy.

## Trạng thái còn lại

- Hai worktree TDQ sạch nhưng chưa dọn: T1.2 và T2.1.
- Một worktree agent nằm ngoài phạm vi `tdq_team.py sweep`; không xóa tự động.
- Công việc feature tiếp tục inline theo plan đã duyệt; không commit/push thêm nếu user không yêu cầu.
