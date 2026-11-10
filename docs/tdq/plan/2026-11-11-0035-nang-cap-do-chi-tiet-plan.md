# PLAN — Báo cáo nghiên cứu sâu và Đề xuất tối ưu Plan cho Model Tier thấp

Ngày: 2026-11-11 · Spec: ../spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — tdq_bench đo nhanh hơn 2.0 phút qua 4 wave (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau
- P1 — Nghiên cứu chuyên sâu & Hoàn thiện Báo cáo nghiên cứu
- P2 — Trực quan hóa Kiến trúc Trước/Sau & Xuất bản Báo cáo nghiệm thu
- P3 — Self-Review & Recheck độc lập
- Definition of Done
- Cụm song song
- Luật file nóng (một file, nhiều task chạm)

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → hoàn thiện nội dung/kiểm chứng → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: chạy `doc_lint.py` đảm bảo không có vi phạm định dạng.
4. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
5. Không commit/push cho đến khi user yêu cầu.
6. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Cấu trúc task | 1 dòng tóm tắt duy nhất, không có chi tiết kỹ thuật | Khối Self-Contained Micro-Spec đầy đủ 5 trường |
| Giao tiếp Subagent | Subagent chỉ nhận 1 dòng, không đọc Spec, phải đoán mò | Subagent nhận trọn vẹn đặc tả hàm, giải thuật từng bước |
| Kiểm soát linter | Linter chỉ kiểm tra định dạng dòng `- [ ]` và dòng `Chạm:` | Linter kiểm tra độ sâu kỹ thuật của các task can thiệp code |
| Khả năng hỗ trợ Model thấp | Chỉ model mạnh mới tự đoán đúng; model thấp thất bại | Model thấp (Haiku/7B) thi công chính xác 100% theo chỉ dẫn |

*Đối chiếu sơ đồ kiến trúc:* Tham chiếu bản xem trước [docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.html](../spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.html) và manifest `2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.manifest.json` đã duyệt.

## P1 — Nghiên cứu chuyên sâu & Hoàn thiện Báo cáo nghiên cứu

- [ ] **T1.1** (e5m) Hoàn thiện phân tích 5 hệ lụy của task 1 dòng và đối chiếu Nguyên lý 3 của Soul — Test: `python scripts/doc_lint.py docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Chạm: `docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
- [ ] **T1.2** (e6m) Chuẩn hóa khung mẫu Self-Contained Task Block và cơ chế phân tầng thích ứng (Adaptive) — Test: `python scripts/doc_lint.py docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Chạm: `docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Cần: T1.1
- [ ] **T1.3** (e4m) Đánh giá bài toán kinh tế học token và kiểm chứng tính tương thích với parser `tdq_team.py` — Test: `python scripts/doc_lint.py docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Chạm: `docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Cần: T1.2

**Xong P1 khi**: Toàn bộ báo cáo nghiên cứu chuyên sâu được hoàn thiện đầy đủ 5 phần, không có lỗi doc_lint.

## P2 — Trực quan hóa Kiến trúc Trước/Sau & Xuất bản Báo cáo nghiệm thu

- [ ] **T2.1** (e4m) Đồng bộ sơ đồ Trước/Sau và bản xem trước Archify HTML — Test: `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md --manifest docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.manifest.json`
  - Chạm: `docs/tdq/artifacts/2026-11-11-0035-nang-cap-do-chi-tiet-plan/truoc-sau.archify.md`
  - Dùng: Archify CLI (`tdq_archify.py`)
  - Để: Render và verify preview HTML cho spec và report
  - Ra: `docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.html`
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md --manifest docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.manifest.json`
  - Không dùng cho: Sửa đổi logic hook
- [ ] **T2.2** (e5m) Soạn thảo Báo cáo tổng kết nghiệm thu & Đề xuất kiến trúc 4 phần — Test: `python scripts/doc_lint.py docs/tdq/reports/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Chạm: `docs/tdq/reports/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Cần: T2.1

**Xong P2 khi**: Báo cáo nghiệm thu và sơ đồ Archify HTML được render và liên kết hợp lệ.

## P3 — Self-Review & Recheck độc lập

Log: BỎ — không có runtime mã nguồn thực thi, chỉ xuất bản tài liệu nghiên cứu và báo cáo.

- [ ] **T3.1** (e5m) Thực hiện Self-Review của tác giả theo 5 khía cạnh chất lượng và tính khả thi — Test: `python scripts/doc_lint.py docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Chạm: `docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Cần: T2.2
- [ ] **T3.2** (e6m) Recheck độc lập bằng Agent `tdq-qc-tester` thẩm định toàn bộ luận điểm và đề xuất — Test: `python scripts/doc_lint.py docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Chạm: `docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
  - Cần: T3.1

**Xong P3 khi**: Biên bản Self-Review và Recheck độc lập được ghi nhận trọn vẹn với kết quả PASS.

## Definition of Done

- [ ] Q1 Báo cáo nghiên cứu chuyên sâu: Đầy đủ 5 phần phân tích chuyên sâu tại file research — `python scripts/doc_lint.py docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
- [ ] Q2 Sơ đồ trực quan Trước/Sau Archify: Render thành công, manifest digest khớp tài liệu — `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md --manifest docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.manifest.json`
- [ ] Q3 Biên bản Self-Review của tác giả: Có mục đánh giá 5 khía cạnh chất lượng trong file QC — `python scripts/doc_lint.py docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
- [ ] Q4 Báo cáo Recheck độc lập của Agent: Agent QC xác nhận PASS toàn bộ luận điểm và đề xuất — `python scripts/doc_lint.py docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`
- [ ] Q5 Lint tài liệu spec và research: `doc_lint.py` thoát mã 0 trên toàn bộ file — `python scripts/doc_lint.py docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`

## Cụm song song

Một cụm tuần tự duy nhất (`main` mode) do các task nghiên cứu, soạn báo cáo, self-review và recheck phụ thuộc trực tiếp vào nhau theo chuỗi logic hoàn thiện tài liệu.

## Luật file nóng (một file, nhiều task chạm)

- `docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`: T1.1, T1.2, T1.3 chạm. Áp dụng phương thức: **một chủ ghi duy nhất** tuần tự theo chu trình T1.1 -> T1.2 -> T1.3.
- `docs/tdq/qc/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`: T3.1, T3.2 chạm. Áp dụng phương thức: **một chủ ghi duy nhất** tuần tự theo chu trình T3.1 -> T3.2.
