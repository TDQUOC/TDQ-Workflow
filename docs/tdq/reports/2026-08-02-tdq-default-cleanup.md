# REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower

Ngày: 2026-08-02 · Lane: full · Mode: main · Spec 1.1 / Plan ĐÃ DUYỆT

## Đã làm
- 3 tầng enforce "MỌI prompt mới → tdq-intake":
  1. `~/.claude/CLAUDE.md`: xóa trọn mục 5 "superpower", đánh số lại 1..10;
     mục 9 (TDQ Workflow) mở đầu bằng luật "MỌI prompt mới → tdq-intake, không ngoại lệ".
  2. `skills/tdq-intake/SKILL.md`: description thêm "kể cả câu hỏi/check/việc nhỏ";
     Phần A thêm định nghĩa đóng "request mở = active_request VÀ phase != idle".
  3. `hooks/scripts/prompt_context.py`: in `[TDQ:INTAKE]` khi không có request mở
     (state None / thiếu active_request / phase_key idle), dòng INTAKE đứng đầu ≤160 ký tự.
- Test mới `tests/test_prompt_context.py` (4 case, red→green).
- Backup CLAUDE.md gốc: `docs/tdq/qc/claude-md-backup-2026-08-02.bak` (sha256 f19af366…).
- Quét sạch tham chiếu số mục cũ (knowledge + title spec).

## QC
- Q1–Q6 PASS, bằng chứng trong `docs/tdq/qc/2026-08-02-tdq-default-cleanup.md`.
- Suite: 371 test OK. Lint SKILL.md + `--pair` spec/plan exit 0.
- QC vòng 1 bắt 5 fail → fix: hook dùng `phase_key()` (lane quick đang chạy giữ
  phase=idle thô, so thô bắn INTAKE nhầm nuốt APPROVE); 2 test cũ cập nhật hợp đồng
  mới; rút gọn description giữ tổng ≤900 ký tự.
- Đối chiếu từng ý §5 cũ → chỗ thay thế trong plugin: đủ, không tụt chuẩn (bảng trong QC).

## Lưu ý
- Hook/skill sửa trong repo có hiệu lực đầy đủ ở PHIÊN MỚI (plugin nạp live từ repo).
- Chưa commit — chờ user quyết.
