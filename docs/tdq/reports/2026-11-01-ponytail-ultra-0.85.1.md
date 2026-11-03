# Ponytail mặc định ultra — 0.85.1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

- User yêu cầu đổi mặc định Ponytail sang ultra, set hiện tại, bump version, release và push; không mở state mới đè lên request còn active.
- Đổi hai hằng mặc định ở `tdq_state.py` và `luat_gon.py`, đồng bộ fallback/tài liệu; giữ các lựa chọn rõ ràng và mặc định QC full.
- Set `muc_gat=ultra` bằng CLI; không sửa state thủ công, không sửa cấu hình cá nhân.
- RED trước sửa; regression sau sửa: **194 test và 296 subtest PASS**, guard PASS, 46,19 giây. Receipt và output nguyên bản trong [artifact](../artifacts/2026-11-01-1045-toi-uu-bon-hang-muc/ponytail-ultra-0.85.1/).
- LSP start/open hoạt động nhưng references báo process exited; dùng đối chiếu tên/callers và regression các kênh hook. Không thêm dependency hoặc sửa cấu hình LSP.
- Thay đổi dùng hằng số và entry point hiện có; không thêm module runtime, abstraction hay dependency.
- Phiên bản hai manifest: 0.85.1. Release notes và kết quả đối chiếu gói phát hành lưu trong artifact.
- Giới hạn: không có lượt Full/benchmark mới; CI nền 0.85.0 còn lỗi; Master Map và guard 11 worktree cũ chưa được xử lý trong bản vá mặc định này.

## Phát hành

- Commit triển khai: `cf2389f`; merge dev: `be0ba7a`; main release: `fe528a8`.
- [GitHub Release 0.85.1](https://github.com/TDQUOC/TDQ-Workflow/releases/tag/v0.85.1); đã push dev/main/tag và đối chiếu remote refs.
- ZIP 169 file, kiểm cú pháp 70 file Python; chạy import thực từ ZIP xác nhận Ponytail ultra, QC full và lựa chọn full giữ nguyên.
- Hai asset ZIP/SHA256SUMS đã đối chiếu SHA256 và size với GitHub API.
- CI nguồn bản vá: in_progress; conclusion=; https://github.com/TDQUOC/TDQ-Workflow/actions/runs/41303198375. CI nền trước đó FAIL được ghi rõ trong release notes.
