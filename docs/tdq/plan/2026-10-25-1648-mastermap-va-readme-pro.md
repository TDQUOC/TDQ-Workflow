# PLAN — Sinh Master Map 4 góc nhìn và nâng cấp README chuyên nghiệp

Ngày: 2026-10-25 · Spec: ../spec/2026-10-25-1648-mastermap-va-readme-pro.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐỀ XUẤT theo simulate: main 8.1 phút so với team 9.2 phút (chênh 1.1 phút, hệ số agent 1.5); 4 tasks phụ thuộc tuần tự và T2.1 cần MCP (user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết/chạy test đỏ trước → thực hiện → chạy lại test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước chạy kiểm thử vùng chạm; trọn bộ `tdq_test.py tron-bo` chạy ở QC.
4. Lệnh nào chạm state của workflow trong test phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Bản đồ Master Map | Mới có bản thử nghiệm 1 góc nhìn tại `docs/tdq/master-demo/`; chưa có `docs/architecture/index.html` thực tế của dự án | Có bộ Master Map 4 góc nhìn chính thức tại `docs/architecture/index.html` với giao diện Dashboard và `manifest.json` trạng thái `current` |
| Tài liệu `README.md` | Dạng ghi chú văn bản đơn giản (183 dòng), thiếu hướng dẫn cài đặt dependencies 8 bậc và chưa nêu bật kiến trúc mới | Trình bày chuẩn Flagship (dưới 500 dòng): có Badges, Tuyên ngôn 6 trụ cột, Sơ đồ luồng, Hướng dẫn cài đặt Dependencies & One-Command Setup (`tdq_setup.py`), Đa nền tảng 4 Host và Bảng cấu trúc chuẩn xác |

*Đối chiếu sơ đồ kiến trúc:* Tham chiếu trực tiếp bản xem trước Archify BA đã duyệt tại `docs/tdq/artifacts/2026-10-25-1648-mastermap-va-readme-pro/preview.html` và manifest `docs/tdq/artifacts/2026-10-25-1648-mastermap-va-readme-pro/preview.manifest.json`. WBS dưới đây ánh xạ tới 4 nút trong sơ đồ `mastermap-readme-flow` (`portal` → `master` → `readme` → `verify`). Kiểm tra binding bằng `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-10-25-1648-mastermap-va-readme-pro.md --manifest docs/tdq/artifacts/2026-10-25-1648-mastermap-va-readme-pro/preview.manifest.json` trước khi viết code.

## P1 — Nâng cấp giao diện Portal Master Map (O1)

- [x] **T1.1** (e12m) Nâng cấp hàm `_generate_index_html` trong `scripts/tdq_archify.py` lên giao diện Dashboard hiện đại (header gradient, lưới thẻ thông tin, huy hiệu module khảo sát, bảng `Views Inventory` và nút bấm trực quan) kèm unit test kiểm chứng bố cục trong `tests/test_archify_pipeline.py` — Test: `python -m pytest tests/test_archify_pipeline.py -q`
  - Chạm: `scripts/tdq_archify.py`, `tests/test_archify_pipeline.py`
  - Dùng: `frontend-design`
  - Để: Thiết kế giao diện Dashboard hiện đại, phân cấp thị giác rõ ràng cho trang chủ `index.html` của Master Map
  - Ra: `scripts/tdq_archify.py`
  - Kiểm: `python -m pytest tests/test_archify_pipeline.py -q`
  - Không dùng cho: Thay đổi logic đóng gói manifest hoặc nhúng tài nguyên CDN bên ngoài

**Xong P1 khi**: `tests/test_archify_pipeline.py` đạt 100% PASS với kiểm tra bố cục Dashboard mới của `_generate_index_html`.

## P2 — Xây dựng và xuất bản Master Map 4 góc nhìn của TDQ-Workflow (O2, O3)

- [x] **T2.1** (e18m) Dựng 4 tệp định nghĩa biểu đồ (`overview.archify.md`, `pipeline-lifecycle.archify.md`, `search-and-archify.archify.md`, `hooks-and-gates.archify.md`) cùng `docs/tdq/models/master.model.json`, xuất bản qua `tdq_archify.py sync-master` vào `docs/architecture/` và kiểm chứng hiển thị trên Chrome DevTools MCP — Test: `python scripts/tdq_archify.py status --project .`
  - Chạm: `docs/tdq/models/master.model.json`, `docs/tdq/models/overview.archify.md`, `docs/tdq/models/pipeline-lifecycle.archify.md`, `docs/tdq/models/search-and-archify.archify.md`, `docs/tdq/models/hooks-and-gates.archify.md`, `docs/architecture/index.html`, `docs/architecture/manifest.json`
  - Cần: T1.1
  - Dùng: `tdq-browser-test` (mcp)
  - Để: Pre-flight cổng 9222, mở `docs/architecture/index.html` và các trang góc nhìn để kiểm tra bố cục, liên kết điều hướng và console 0 lỗi
  - Ra: `docs/architecture/index.html`
  - Kiểm: `python scripts/tdq_archify.py status --project .`
  - Không dùng cho: Bỏ qua bước kiểm tra thực tế trên trình duyệt

**Xong P2 khi**: Bộ Master Map 4 góc nhìn tại `docs/architecture/index.html` được xuất bản thành công, `tdq_archify.py status` trả về `status: current` và trình duyệt xác nhận hiển thị tốt với 0 lỗi console.

## P3 — Nâng cấp `README.md` chuẩn Flagship & Cẩm nang Setup A–Z (O4)

- [x] **T3.1** (e15m) Viết lại `README.md` theo chuẩn Flagship Open-Source (Badges, Tuyên ngôn 6 trụ cột bất biến, Kiến trúc & liên kết Master Map, Cẩm nang One-Command Setup `tdq_setup.py` & Install Dependencies 8 bậc, Đa nền tảng 4 Host, Hệ thống mã nhắc `[TDQ:*]` và Bảng cấu trúc dự án) — Test: `python -m pytest tests/test_docs_consistency.py tests/test_skill_shape.py -q`
  - Chạm: `README.md`, `tests/test_docs_consistency.py`
  - Cần: T2.1
  - Dùng: `tdq-setup`
  - Để: Đối chiếu chính xác 8 bậc công cụ tìm kiếm, môi trường Python/Node.js, Archify và Chrome CDP để trình bày chuẩn xác trong mục Setup & Install Dependencies của `README.md`
  - Ra: `README.md`
  - Kiểm: `python -m pytest tests/test_docs_consistency.py tests/test_skill_shape.py -q`
  - Không dùng cho: Tự ý thay đổi cấu hình hệ thống ngoài dự án
  - Tiến độ: Đã đạt 23 passed trên test_docs_consistency & test_skill_shape; rút gọn câu dòng 11 để đạt doc_lint R5.

**Xong P3 khi**: `README.md` đạt 0 vi phạm `doc_lint.py` (dưới 500 dòng) và vượt qua toàn bộ bài kiểm trong `tests/test_docs_consistency.py` và `tests/test_skill_shape.py`.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e6m) Kiểm chứng log service và chạy gộp các bộ unit test của `archify`, `docs_consistency`, `skill_shape` cùng kiểm tra `tdq_archify.py status` đạt `current` sau mọi thay đổi — Test: `python -m pytest tests/test_archify_pipeline.py tests/test_docs_consistency.py tests/test_skill_shape.py -q`
  - Chạm: `tests/test_archify_pipeline.py`, `tests/test_docs_consistency.py`
  - Cần: T3.1

## Cụm song song

Chuỗi tuần tự T1.1 → T2.1 → T3.1 → T4.1 vì T2.1 cần hàm `_generate_index_html` đã nâng cấp ở T1.1 để sinh `docs/architecture/index.html`, và mọi thay đổi trên `scripts/tdq_archify.py` phải hoàn tất trước khi khóa dấu vân tay `manifest.json` của Master Map.

## Luật file nóng

Các tệp `tests/test_archify_pipeline.py` và `tests/test_docs_consistency.py` được cập nhật ở T1.1/T3.1 và kiểm tổng hợp ở T4.1 theo thứ tự tuần tự một chủ ghi duy nhất.

## Definition of Done

- [x] Q1 Giao diện Portal `index.html` và 4 góc nhìn Master Map xuất bản thành công (O1, O2, O3) — `python scripts/tdq_archify.py status --project .`
- [x] Q2 Tài liệu `README.md` chuẩn Flagship và đầy đủ hướng dẫn Setup & Dependencies (O4) — `python scripts/doc_lint.py README.md`
- [x] Q3 Hồi quy vùng chạm và toàn bộ kho mã nguồn — `python -m pytest tests/test_archify_pipeline.py tests/test_docs_consistency.py tests/test_skill_shape.py -q`
