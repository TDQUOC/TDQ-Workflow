# REPORT — Tích Hợp Archify Vào TDQ-Workflow: Trực Quan Hóa BA & Kiến Trúc Dự Án (`2026-10-24-2145-nghien-cuu-tich-hop-archify` · lane full · mode subagent · 11 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** Soạn thảo bản Thiết kế Kiến trúc Toàn diện `docs/kien-truc-tich-hop-archify.md` chi tiết 8 phân hệ · Xây dựng module điều phối `scripts/tdq_archify.py` (kiểm tra môi trường, bọc lệnh finalize, atomic delivery, open browser và cầu nối Graphify-to-Archify) · Cập nhật quy chuẩn BA flow vào `skills/tdq-spec/`, `skills/tdq-intake/` và `skills/tdq-plan/` · Bổ sung kiểm tra Node.js $\ge 18$ và gói Archify trong `scripts/tdq_setup.py` · Bổ sung cấu hình AI Endpoint vào `.env.example` · Xây dựng bộ test suite `tests/test_tdq_archify.py` đạt 35/35 tests PASS.

**Kết quả QC — đính chính 2026-10-24:** CHƯA NGHIỆM THU. Kết luận PASS toàn bộ trước đây bị rút lại: các tác vụ nền `bpzrsod7w` (trọn bộ), `bsfb9qjx9` và `b1mf8t6q6` (vùng chạm) kết thúc exit 1. Lần chạy riêng adapter/setup/doc_lint đạt 143 tests, không thay thế kiểm thử toàn bộ hoặc E2E. Reviewer độc lập đã trả FAIL Q7, chưa có lần tái thẩm định đạt ultra.

**Bàn giao theo lựa chọn `1b` lúc 23:48:** Chuyển phần hoàn thiện sang request `2026-10-24-2348-hoan-thien-archify`. Giữ nhánh `feature/nghien-cuu-tich-hop-archify` làm nền kế thừa, không merge về `dev`, không coi bàn giao là nghiệm thu. Spec và plan cũ giữ làm lịch sử; các tick hoàn thành trong plan không còn là bằng chứng đủ cho nghiệm thu.

**Việc còn thiếu cần xác minh:** cú pháp CLI trong skill; xử lý lỗi finalize; an toàn mở file; schema, hướng cạnh và nguồn của bridge; Master HTML và đồng bộ theo revision; triển khai thật endpoint scanner; hồi quy và kiểm thử trình duyệt. `sync-master` hiện mới ghi JSON, chưa dựng Master HTML.

**Thời gian:**

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 15s | — | 1 |
| analyze | 31 min | — | 1 |
| spec | 4 min | — | 1 |
| plan | 11 min | — | 1 |
| implement | 17 min | — | 1 |
| qc | 20 min | — | 1 |
| report | 13s | — | 1 |
| **Total** | **1h 23min** | **—** | |

**Files thay đổi:**
- `docs/kien-truc-tich-hop-archify.md`: Tạo mới bản vẽ Blueprint RFC 8 phân hệ
- `scripts/tdq_archify.py`: Tạo mới module CLI adapter (Python stdlib)
- `tests/test_tdq_archify.py`: Tạo mới test suite 35 unit tests (100% PASS)
- `skills/tdq-spec/SKILL.md` & `references/spec-template.md`: Cập nhật chuẩn BA flow tương tác
- `skills/tdq-intake/references/quick-lane.md`: Cập nhật chuẩn mini-workflow
- `skills/tdq-plan/references/plan-template.md`: Cập nhật hướng dẫn đối chiếu WBS
- `scripts/tdq_setup.py`: Cập nhật hàm và cờ `--kiem-archify`
- `.env.example`: Cập nhật biến cấu hình AI Endpoint
- `docs/tdq/token-budget.json`: Cập nhật đồng bộ
