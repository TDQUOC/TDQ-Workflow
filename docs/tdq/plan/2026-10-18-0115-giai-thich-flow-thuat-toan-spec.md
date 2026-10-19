# PLAN — Nâng cấp Spec giải thích trực quan Flow hoạt động và Thuật toán cho Fresher Dev

Ngày: 2026-10-18 · Spec: ../spec/2026-10-18-0115-giai-thich-flow-thuat-toan-spec.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — thực hiện trực tiếp tuần tự do các task liên kết chặt chẽ vào khuôn mẫu tài liệu và test suite
Trạng thái plan: ĐANG THỰC HIỆN

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Nâng cấp khuôn mẫu Spec Template
- P2 — Cập nhật cẩm nang hướng dẫn và quy trình TDQ-Spec
- P3 — Xây dựng bộ kiểm thử tự động Spec Template
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — Nâng cấp khuôn mẫu Spec Template

- [x] **T1.1** (e15m) Tích hợp 3 mục cấu trúc mới (§2c Luồng kiến trúc, §3c Giải thuật cốt lõi, §3d Mental Model cho Fresher) vào `spec-template.md` và tinh gọn đạt cap token — Test: `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md` exit 0.
  - Chạm: `skills/tdq-spec/references/spec-template.md` → khuôn mẫu tài liệu spec
  - Dùng: `tdq-workflow:tdq-spec`
  - Để: Bổ sung các section trực quan hóa luồng và thuật toán
  - Ra: `skills/tdq-spec/references/spec-template.md`
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md`
  - Không dùng cho: Sửa đổi các file ngoài thư mục tdq-spec

**Xong P1 khi**: `spec-template.md` có đầy đủ 3 section mới và vượt qua DocLint sạch sẽ.

## P2 — Cập nhật cẩm nang hướng dẫn và quy trình TDQ-Spec

- [x] **T2.1** (e12m) Bổ sung checklist "Fresher Accessibility Check" vào `spec-template-huong-dan.md` — Test: `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template-huong-dan.md` exit 0.
  - Chạm: `skills/tdq-spec/references/spec-template-huong-dan.md` → cẩm nang tự soát spec
- [x] **T2.2** (e10m) Cập nhật hướng dẫn `skills/tdq-spec/SKILL.md` yêu cầu thẩm định tính trực quan và bổ sung tóm tắt luồng/giải thuật vào chat block — Test: `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md` exit 0.
  - Chạm: `skills/tdq-spec/SKILL.md` → quy trình kỹ năng tdq-spec

**Xong P2 khi**: Toàn bộ tài liệu hướng dẫn và skill wrapper đều đồng bộ quy chuẩn mới.

## P3 — Xây dựng bộ kiểm thử tự động Spec Template

- [x] **T3.1** (e15m) Viết test suite `tests/test_spec_template.py` kiểm tra cấu trúc khuôn mẫu `spec-template.md` (chứa Mermaid, Before vs After, Step-by-step logic, Mental model) — Test: `python3 -m pytest tests/test_spec_template.py -v` exit 0.
  - Chạm: `tests/test_spec_template.py` → bộ kiểm thử tự động

**Xong P3 khi**: Bộ test mới bắt trúng cấu trúc spec và PASS 100%.

## Cụm song song
Một cụm tuần tự trên main vì các file tài liệu và test phụ thuộc trực tiếp vào khuôn mẫu `spec-template.md` đã thiết kế.

## Definition of Done
- [x] Q1 Cấu trúc spec-template.md có đủ 3 mục §2c, §3c, §3d và ví dụ mẫu — `grep -E "2c\.|3c\.|3d\." skills/tdq-spec/references/spec-template.md`
- [x] Q2 DocLint trên toàn bộ tài liệu sửa đổi thoát 0, không có lỗi R5/R6 — `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md skills/tdq-spec/references/spec-template-huong-dan.md skills/tdq-spec/SKILL.md`
- [x] Q3 Bộ test tự động kiểm thử Spec Template PASS 100% — `python3 -m pytest tests/test_spec_template.py -v`
- [x] Q4 Tính sư phạm cho Fresher được bảo đảm qua ví dụ trực quan — Soát checklist Fresher Accessibility Check
