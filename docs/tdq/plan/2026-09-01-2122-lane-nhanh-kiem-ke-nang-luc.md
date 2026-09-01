# QUICK — giá của kiểm kê năng lực + đọc code + research trong lane nhanh

**Ngày:** 2026-09-01 · Brief: ../brief/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** tdq-conventions
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: đọc `skills/tdq-intake/references/analyze-full.md` (6 bước B0–B5),
  `skill-inventory.md`, `interview.md`, `scope-round.md`, `quick-lane.md` — rút ra 3 bước
  user hỏi (B0 kiểm kê năng lực, B1 đọc code, B2 research) làm gì, tốn gì.
- Trong: bốc số THẬT từ `docs/tdq/timing.jsonl` (43 dòng) — so `model_giay`/`treo_tuong_giay`
  của pha `analyze` lane full với tổng của request lane quick, làm mốc định lượng.
- Trong: cân theo 3 thước user chốt — thời gian đồng hồ, context tiêu tốn, số lượt user phải
  trả lời — cho TỪNG bước riêng VÀ cho trọn gói cả 3 (user chốt 3a và 3b).
- Trong: viết report `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`, kết
  bằng đề xuất gói nào đáng cho lane nhanh.
- Bỏ vòng phạm vi: không dấu hiệu kích hoạt nào — user đã chốt sẵn cả 4 câu, phạm vi đóng.
- Bỏ web search: việc thuần nội bộ, mọi dữ liệu nằm trong repo.
- NGOÀI: đổi bất kỳ dòng code, hook, skill, test nào — user chốt 4A "chỉ report".
- NGOÀI: quyết thay user chọn gói; report trình số, user chốt sau.

## Task
- [x] **T1** Mô tả 3 bước B0/B1/B2 đúng như `analyze-full.md` quy định, kèm sản phẩm mỗi bước
  đẻ ra — Test: mỗi bước trích được `file:dòng` thật, mở bằng `sed -n`
  - Chạm: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`
- [x] **T2** Bảng giá 3 thước × 3 bước, số thời gian lấy từ `timing.jsonl` — Test: mọi con số
  trong bảng truy được về một dòng `timing.jsonl` hoặc một phép đếm chạy lại được
  - Chạm: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`
- [x] **T3** Cân trọn gói cả 3 bước + đề xuất gói đáng cho lane nhanh, nói rõ lane nhanh còn
  nhanh không — Test: đề xuất kèm ngưỡng áp dụng cụ thể, không nói chung chung
  - Chạm: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`

## Definition of Done
- `python3 scripts/doc_lint.py docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md` thoát 0
- `git status --short` không có file nào trong `scripts/`, `hooks/`, `skills/`, `tests/`
- Report có đủ: mô tả 3 bước, bảng giá theo từng bước, cân trọn gói, đề xuất kèm ngưỡng
- Mọi `file:dòng` và mọi con số trong report kiểm lại được

## QC
- Q1 test từng task: PASS — T1: 7 tham chiếu `file:dòng` (`analyze-full.md` 8/16/47/52/53/56,
  `quick-lane.md:38`) mở bằng `sed -n` đúng nội dung mô tả. T2: mọi con số chạy lại được bằng
  script đọc `timing.jsonl` (analyze n=29 trung vị 372, quick n=13 trung vị 533, full n=30
  trung vị 3409) và `skill_inventory.py` (9 lọc / 223 tổng, 0,08 s), `wc -l docs/tdq/research`
  (36 file, trung vị 69 dòng), brief n=77 trung vị 107 dòng. T3: đề xuất kèm 3 ngưỡng cụ thể
  (B1 luôn; B0 khi vùng chưa có tiền lệ; B2 khi có ẩn số ngoài).
- Q2 DoD "`doc_lint` report thoát 0": PASS — `0 violation(s) total, exit 0`.
- Q3 DoD "git không có file trong `scripts/`, `hooks/`, `skills/`, `tests/`": PASS — lọc
  `git status --short` theo 4 thư mục đó → rỗng.
- Q4 DoD "report đủ 4 phần": PASS — §1 mô tả 3 bước, §3 bảng giá từng bước, §4 cân trọn gói,
  §5 đề xuất kèm ngưỡng.
- Q5 DoD "mọi `file:dòng` và con số kiểm lại được": PASS — 7/7 tham chiếu mở đúng; mọi con số
  truy về `timing.jsonl` hoặc một phép đếm chạy lại được. Ghi chú trung thực đã nêu ngay trong
  §3 của report: cột thời gian TỪNG BƯỚC là ước lượng, vì `timing.jsonl` chỉ đo theo pha.
