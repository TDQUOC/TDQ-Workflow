# BRIEF — Cấu hình và hoàn thiện cơ chế tự động cập nhật (auto-update) plugin tdq-workflow trong Claude Code
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy hãy giúp tôi config plugin tdq-workflow sẽ auto update trong claude code nha

Mục tiêu:
1. Hoàn thiện và kích hoạt cơ chế tự động kiểm tra và cập nhật plugin `tdq-workflow` (scope `user`) trong Claude Code mỗi khi có phiên bản mới được phát hành (từ remote marketplace GitHub `TDQUOC/TDQ-Workflow` hoặc từ thư mục mã nguồn phát triển).
2. Tối ưu hóa hook `SessionStart` ([hooks/scripts/session_start.py](hooks/scripts/session_start.py)) và module [scripts/tdq_setup.py](scripts/tdq_setup.py):
   - Nhận diện đúng thư mục nguồn / marketplace thay vì bị neo chết vào thư mục cache plugin cũ.
   - Cơ chế kiểm tra remote định kỳ không chặn (non-blocking / detached background check với throttle interval hợp lý) để không làm chậm thời gian mở phiên làm việc.
   - Tự động gọi cập nhật marketplace và plugin khi phát hiện bản mới, đồng thời hiển thị thông báo cập nhật rõ ràng cho người dùng.

Phạm vi dự kiến:
- [scripts/tdq_setup.py](scripts/tdq_setup.py) (`tu_dong_cap_nhat_plugin_user`, kiểm tra version từ marketplace / git).
- [hooks/scripts/session_start.py](hooks/scripts/session_start.py) (điều phối kiểm tra update ngầm an toàn).
- Các unit tests liên quan đến auto-update plugin trong `tests/`.

## Hiểu & kiến thức

### Khảo sát mã nguồn (B1)
1. Thư mục cài đặt plugin Claude Code:
   - Cache plugin: `~/.claude/plugins/cache/tdq-local/tdq-workflow/<ver>/`.
   - Danh mục cài đặt: `~/.claude/plugins/installed_plugins.json`.
   - Marketplace cục bộ: `~/.claude/plugins/marketplaces/tdq-local` (trỏ GitHub `TDQUOC/TDQ-Workflow`).
2. Lệnh CLI của Claude Code hỗ trợ cập nhật:
   - `claude plugin marketplace update tdq-local`: kéo các bản phát hành/commit mới nhất về marketplace.
   - `claude plugin update tdq-workflow@tdq-local -s user -y`: cập nhật plugin user lên version mới nhất trong marketplace.
3. Điểm nghẽn hiện tại:
   - Trong `session_start.py`, `GOC_PLUGIN` trỏ vào chính thư mục cache hiện hành, nên hàm `tu_dong_cap_nhat_plugin_user` chỉ so sánh version cache với chính nó, không bao giờ phát hiện được remote có bản mới.
   - Cần cơ chế kiểm tra ngầm định kỳ (throttle e.g. 2 giờ / lần) chạy `marketplace update` và `plugin update` trong tiến trình nền không chặn (detached).
   - Nếu đang mở phiên tại chính repo nguồn `TDQ-Workflow`, tự động nhận diện version nguồn mới hơn cache để cập nhật ngay.

### Bỏ B0 & B2
- Bỏ B0: Đã có tiền lệ chỉnh sửa `scripts/tdq_setup.py` và `hooks/scripts/session_start.py` trong nhiều request trước.
- Bỏ B2: Không có thư viện ngoài lạ; lệnh CLI Claude Code đã được kiểm chứng hoạt động trực tiếp.

## Hỏi đáp

(Không có câu hỏi chặn)
