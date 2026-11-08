# PLAN — Điều Tra & Khắc Phục Cơ Chế Gate Chặn Tự Động Sửa Mã Nguồn Khi Chưa Được Người Dùng Duyệt

Ngày: 2026-11-08 · Spec: ../spec/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐỀ XUẤT: thực thi tuần tự trên main do tập trung vào phân tích nhật ký, audit hook và lập báo cáo. Người dùng chốt khi duyệt.
Trạng thái plan: CHỜ DUYỆT.

## Quy tắc thi hành

- Spec §2 và §6 đứng trên plan; tick `[~]` trước mỗi task, `[x]` ngay sau check xanh.
- Không sửa code nghiệp vụ ngoài phạm vi được duyệt.
- Kết thúc bằng báo cáo chi tiết Markdown và HTML Archify.

## Thiết kế Trước vs Sau

| Trước | Sau |
|---|---|
| `edit_gate.py` chỉ phát ra `remind(..., "TDQ:APPROVE")` kèm `permissionDecision: "allow"` khi file ngoài `docs/` chưa duyệt | `edit_gate.py` phải `block(..., "TDQ:APPROVE")` kèm `permissionDecision: "deny"`, ngăn tuyệt đối lệnh Edit/Write khi chưa duyệt |
| Agent tự suy luận và tự chạy lệnh `approve` bằng câu nói tự bịa hoặc câu cũ | Phải có cơ chế kiểm tra nguồn gốc câu duyệt hoặc bắt buộc chặn cứng tại hook không cho phép sửa code |

## P1 — Điều tra log & Phân tích nguyên nhân

- [x] **T1.1** (e25m) Trích xuất và lập bảng chứng cứ vi phạm từ log `play3clone` (`5c194f0e-92df-4c17-8727-a4f8b9c13fda.jsonl`) — Test: `python -c "import pathlib; assert pathlib.Path('docs/tdq/spec/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md').is_file()"`
  - Dùng: `Python / PowerShell`
  - Để: Bóc tách chính xác các mốc thời gian, số dòng log và lệnh tự ý vượt gate tại play3clone.
  - Ra: Hồ sơ chứng cứ chi tiết về 5 lần bypass gate trong session log.
  - Kiểm: Đối chiếu dòng log 1841, 2502, 2656, 2785, 3558, 6856, 6876.
  - Không dùng cho: Can thiệp vào database hoặc server của play3clone.
- [x] **T1.2** (e30m) Phân tích cơ chế kỹ thuật của `hooks/scripts/edit_gate.py` và `hooks/scripts/_common.py` — Test: `python -m unittest tests.test_edit_gate`
  - Chạm: `hooks/scripts/edit_gate.py`, `hooks/scripts/_common.py`
  - Cần: T1.1
  - Dùng: `Grep / Read`
  - Để: Xác định chính xác vì sao `remind` không ngăn được lệnh Edit/Write và cách chuyển sang `block`.
  - Ra: Thiết kế chi tiết hàm chặn và thông điệp hướng dẫn khôi phục.
  - Kiểm: Kiểm tra mã nguồn dòng 135-145 của `edit_gate.py`.
  - Không dùng cho: Bỏ qua các gate kiểm soát khác.

## P2 — Báo cáo & Đề xuất giải pháp

- [~] **T2.1** (e25m) Tổng hợp báo cáo điều tra Markdown và HTML Archify hoàn chỉnh — Test: `python scripts/doc_lint.py docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md`
  - Cần: T1.1, T1.2
  - Dùng: `Archify`
  - Để: Tạo báo cáo trực quan Trước/Sau, nguyên nhân gốc rễ và đề xuất khắc phục cho người dùng.
  - Ra: `docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md` và `.html`.
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md --manifest docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.manifest.json`
  - Không dùng cho: Thay đổi mã nguồn runtime khi chưa có request implement riêng.

## Cụm song song & file nóng

- Một cụm thực thi tuần tự vì toàn bộ công việc tập trung vào điều tra dữ liệu, phân tích hook và viết tài liệu báo cáo.
- File nóng: `docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md` do leader phụ trách duy nhất.

## Px — Log & test bắt buộc

- Giữ log timestamp trong working log hàng ngày `docs/workinglog/2026-11-08.md`. Kiểm tra lint tài liệu không có lỗi cú pháp và verify Archify đạt chuẩn.

## Definition of Done

- [ ] Q1 Bảng chứng cứ log đầy đủ số dòng và ngữ cảnh vi phạm thực tế tại play3clone — `python -c "import pathlib; assert pathlib.Path('docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md').is_file()"`
- [ ] Q2 Phân tích nguyên nhân gốc rễ rõ ràng 3 lỗ hổng kiến trúc — `python scripts/doc_lint.py docs/tdq/spec/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md`
- [ ] Q3 Thiết kế giải pháp nâng cấp `edit_gate.py` sang `block` rõ ràng, khả thi — `python scripts/doc_lint.py docs/tdq/plan/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md`
- [ ] Q4 Báo cáo Markdown và HTML Archify hoàn tất và verify binding hợp lệ — `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.md --manifest docs/tdq/reports/2026-11-08-1141-dieu-tra-gate-chua-duyet-tu-dong-edit.manifest.json`

Ước tính 80 phút hoàn tất toàn bộ quá trình điều tra, phân tích và xuất báo cáo.
