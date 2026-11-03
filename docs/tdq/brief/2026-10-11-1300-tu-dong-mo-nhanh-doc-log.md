# BRIEF — Tự động mở branch khi chỉ thay đổi docs và log

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
"okay bây giờ mở request handle vấn đề là từ giờ khi mở request nếu change chỉ là docs và log thì cho phép tự động mở branch và đem theo luôn ko cần hỏi như này"

**Mục tiêu:**
Khi mở request mới tại bước 3b của `tdq-intake`:
- Nếu `git status --porcelain` có các file uncommitted nhưng toàn bộ chỉ thuộc nhóm tài liệu / log / file tạm (`docs/**`, `docs/workinglog/**`, `docs/tdq/**`, `logs/**`, `*.log`...):
  - Tự động thực hiện tạo/mở branch mới (`git switch -c <loại>/<mô tả>`) và mang theo các thay đổi này sang branch mới.
  - Không dừng lại ngắt quãng để hỏi người dùng.
- Chỉ khi có thay đổi trong mã nguồn (source code) hoặc các file ngoài phạm vi docs/log mới dừng lại cảnh báo và hỏi người dùng xử lý dirty working tree.

**Phạm vi dự kiến:**
- `skills/tdq-intake/SKILL.md` (bước 3b)
- `skills/tdq-intake/references/nhanh-request.md`
- Kiểm tra các test liên quan (`test_skill_shape.py`, `test_luat_skill.py`) và token budget.

## Hiểu & kiến thức
- Hiện trạng: Bước 3b của `tdq-intake` và `nhanh-request.md` quy định: nếu `git status --porcelain` không rỗng thì DỪNG LẠI và hỏi người dùng. Dẫn tới việc dù working tree chỉ có file docs/logs/file tạm (`docs/workinglog/*`, `docs/tdq/*`, `logs/*`), agent vẫn dừng lại hỏi làm gián đoạn trải nghiệm người dùng.
- Giải pháp:
  1. Cập nhật bước 3b trong `skills/tdq-intake/SKILL.md`: Kiểm tra các file uncommitted trong `git status --porcelain`. Nếu TẤT CẢ các file đều thuộc phạm vi tài liệu / log / file tạm (`docs/**`, `*.md`, `logs/**`, `*.log`, state cache) $\rightarrow$ tự động mở branch mới (`git switch -c <loại>/<mô tả>`), mang theo các file này sang branch mới và không ngắt quãng hỏi người dùng.
  2. Nếu có BẤT KỲ file nào nằm ngoài phạm vi này (đặc biệt là mã nguồn code, build config) $\rightarrow$ DỪNG LẠI, in danh sách file và hỏi người dùng xử lý.
  3. Cập nhật tài liệu tham chiếu `skills/tdq-intake/references/nhanh-request.md` (giải thích rõ quy tắc ngoại lệ doc/log, cập nhật ghi chú lệnh và phần self-check).
  4. Đảm bảo line count của `skills/tdq-intake/SKILL.md` tuân thủ trần (nâng trần trong `scripts/doc_lint.py` nếu cần thiết để không làm ép luật hoặc giữ dòng theo soul.md). Đồng thời đảm bảo không làm trôi dòng các mốc luật anchored trong `docs/tdq/audit/luat-hien-co.md`.

## Hỏi đáp
- User đã chốt yêu cầu qua ảnh chụp và prompt ban đầu.
