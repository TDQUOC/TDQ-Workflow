# PLAN — Nâng Cấp Khảo Sát Code 3 Chiều & Bảo Toàn Chủ Đích Refactor

Ngày: 2026-10-20 · Spec: ../spec/2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐÃ DUYỆT
Trạng thái plan: ĐÃ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Tinh Chỉnh Gate Tìm Kiếm Trong Phase Analyze
- P2 — Quy Trình Khảo Sát Code 3 Chiều & Bảng Đối Chiếu
- P3 — Ngoại Lệ Refactor & Bảo Toàn Clean Architecture Cho Rung 1
- P4 — Đồng Bộ Instruction Toàn Cục & Khối Trước vs Sau
- P5 — Log & test bắt buộc
- Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- Luật file nóng (một file, nhiều task chạm)
- Dòng `Cần:` (khai phụ thuộc giữa các task)
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — Tinh Chỉnh Gate Tìm Kiếm Trong Phase Analyze
- [x] **T1.1** (e15m) Cập nhật `hooks/scripts/search_gate.py` và `scripts/search_rules.py`: kiểm tra phase hiện tại của workflow, cho phép Grep tự do không giới hạn quota và không deny khi phase là `analyze`, `quick_analyze`, `spec` hoặc `no_state`; duy trì cổng 3 tầng chuẩn khi phase là `implement` — Test: unit test kiểm tra quyền grep theo từng phase PASS.
  - Chạm: `hooks/scripts/search_gate.py`, `scripts/search_rules.py` → gate tìm kiếm và bộ luật
- [x] **T1.2** (e12m) Cập nhật `search_rules.py` bổ sung cơ chế kiểm tra tam giác khảo sát: ghi nhận việc gọi LSP/Graphify trong phase khảo sát để làm căn cứ thẩm định chất lượng — Test: test logic ghi nhận và phân loại truy vấn PASS.
  - Chạm: `scripts/search_rules.py` → hàm phân loại và trạng thái
  - Cần: T1.1

**Xong P1 khi**: Gate tìm kiếm cho phép quét Grep tự do trong phase analyze mà không bị chặn, giữ vững kỷ luật trong phase implement.

## P2 — Quy Trình Khảo Sát Code 3 Chiều & Bảng Đối Chiếu
- [x] **T2.1** (e15m) Cập nhật `skills/tdq-intake/SKILL.md` và `skills/tdq-intake/references/analyze-full.md`: chuẩn hóa quy trình Khảo sát Code 3 Chiều (Grep quét rộng -> LSP đào sâu cấu trúc -> Graphify quét vỡ lan) và đưa bảng đối chiếu vùng chạm bắt buộc vào brief — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`
  - Cần: T1.1
- [x] **T2.2** (e10m) Cập nhật `skills/tdq-intake/references/quick-lane.md`: áp dụng nguyên tắc khảo sát 3 chiều và bảng đối chiếu vào mini-plan của lane quick — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-intake/references/quick-lane.md`
  - Cần: T2.1

**Xong P2 khi**: Tài liệu intake và analyze quy định rõ ràng quy trình khảo sát 3 chiều và bảng đối chiếu vùng chạm.

## P3 — Ngoại Lệ Refactor & Bảo Toàn Clean Architecture Cho Rung 1
- [x] **T3.1** (e15m) Cập nhật `skills/tdq-build/references/rules/chung.md`: bổ sung ngoại lệ Refactor & Mở rộng kiến trúc vào mục `### Never simplify these away` của Rung 1; quy định rõ khi người dùng yêu cầu tái cấu trúc, mục tiêu Clean Architecture và SOLID đứng trên luật phẫu thuật 1 dòng tối thiểu — Test: `doc_lint` và test luật tinh gọn PASS.
  - Chạm: `skills/tdq-build/references/rules/chung.md`

**Xong P3 khi**: Luật tinh gọn bảo toàn tính toàn vẹn của chủ đích thiết kế kiến trúc khi người dùng yêu cầu Refactor.

## P4 — Đồng Bộ Instruction Toàn Cục & Khối Trước vs Sau
- [x] **T4.1** (e12m) Cập nhật `skills/tdq-spec/references/spec-template.md` (§3) và `skills/tdq-plan/references/plan-template.md`: bổ sung khối so sánh Hiện trạng (Trước) vs Thiết kế mới (Sau) khi bổ sung hoặc refactor — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md`
- [x] **T4.2** (e12m) Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py`: đồng bộ nguyên tắc khảo sát 3 chiều và ngoại lệ refactor vào `CLAUDE.md` — Test: `test_tu_khoi_tao.py` PASS.
  - Chạm: `scripts/tdq_setup.py`
  - Cần: T2.1, T3.1, T4.1

## P5 — Log & test bắt buộc
- [x] **T5.1** (e15m) Xây dựng bộ test suite `tests/test_khao_sat_3_chieu.py` kiểm chứng: (1) Grep được phép tự do trong phase analyze; (2) Grep vẫn bị kiểm soát trong implement; (3) Cập nhật quy tắc ngoại lệ refactor và khối Trước vs Sau — Test: `py -3 tests/test_khao_sat_3_chieu.py` PASS 100%.
  - Chạm: `tests/test_khao_sat_3_chieu.py` → file test mới
  - Cần: T1.2, T4.2

## Cụm song song
- Cụm 1: T1.1 → T1.2 (logic gate tìm kiếm và phân loại).
- Cụm 2: T2.1 → T2.2 (tài liệu quy trình intake và analyze).
- Cụm 3: T3.1 (ngoại lệ refactor trong chung.md).
- Cụm 4: T4.1 → T4.2 (mẫu spec/plan và đồng bộ instruction).
- Cụm 5: T5.1 (bộ test suite kiểm chứng toàn diện).
- Thực thi tuần tự trên nhánh `main` inline theo thứ tự phụ thuộc.

## Luật file nóng (một file, nhiều task chạm)
- `scripts/search_rules.py`: T1.1 và T1.2 cùng chạm → T1.1 xử lý logic phase trước, T1.2 bổ sung trạng thái khảo sát.
- `scripts/tdq_setup.py`: T4.2 chạm một mình ở cuối đợt.

## Definition of Done
- [x] Q1 Gate tìm kiếm mở khóa trong Analyze — Khi phase là `analyze`/`quick_analyze`, các lệnh grep được cho phép không bị deny.
- [x] Q2 Hàng rào Implement giữ nguyên — Khi phase là `implement`, search_gate vẫn duy trì quy tắc 3 tầng chuẩn.
- [x] Q3 Ngoại lệ Refactor cho Rung 1 — `chung.md` chứa ngoại lệ bảo toàn Clean Architecture/SOLID khi người dùng yêu cầu Refactor.
- [x] Q4 Bảng Hiện trạng Trước vs Sau & Đồng bộ — `spec-template.md`, `plan-template.md`, `CLAUDE.md` có khối so sánh Trước vs Sau và bảng 3 chiều.
