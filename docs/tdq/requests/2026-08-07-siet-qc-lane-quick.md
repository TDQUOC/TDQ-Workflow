# REQUEST — Siết QC và vòng fix cho lane quick

Ngày: 2026-08-07 · Lane: (chờ user chốt)

## Nguyên văn yêu cầu của user

Turn 1 (16:17):
> okay bây giờ tôi muốn check xem ở lane quick hiện tại có đang có bước interview nếu
> chưa rõ không? ko dùng tdqworkflow cho turn chat này

Turn 2 (16:18):
> vậy ở lane quick có ép trong spec có QC và fix khi có bug chưa (nhưng ở một ngưỡng nhẹ
> hơn lane full cho QC còn khi có bug thì luôn luôn bắt buộc fix ) , ko dùng tdq cho turn này

Turn 3 (16:20):
> okay hãy dùng tdqworkflow đẻ lên request cho cái này

## Cách hiểu đầu tiên

**Mục tiêu:** lane quick hiện tại chỉ nói "chạy validate" (một từ trống) và không có luật
nào cho tình huống gặp bug. User muốn siết hai chỗ:

1. **QC bắt buộc ở ngưỡng NHẸ hơn full** — không cần file `docs/tdq/qc/<slug>.md`, làm
   ngay trong turn, nhưng phải ép 2 việc cốt: (a) chạy test của từng task, (b) đối chiếu
   từng dòng Definition of Done → PASS/FAIL kèm bằng chứng thật.
2. **Vòng fix LUÔN LUÔN bắt buộc khi có bug** — không được báo "có bug" rồi dừng. Lặp đến
   hết FAIL, không cần duyệt lại; chỉ kéo user vào khi bản fix đòi đổi phạm vi.

## Hiện trạng đã xác minh (turn read-only trước đó)

- `skills/tdq-intake/references/quick-lane.md:14` — bảng: `| QC | file qc/<slug>.md | validate ngay trong turn implement |`
- `skills/tdq-intake/SKILL.md` Phần C bước 7 — "Implement end-to-end trong 1 turn, chạy validate, báo kết quả ngắn gọn."
- `skills/tdq-build/references/qc.md` (6 hạng mục QC đầy đủ) **chỉ được `tdq-build` nạp**;
  `tdq-build` là lane full → quick không bao giờ nạp `qc.md`.
- Luật FAIL → fix nằm ở `skills/tdq-build/SKILL.md:66-69` (`## QC vòng N — fix`), lane full only.
- Red → green (`tdq-build/SKILL.md:25`) cũng chỉ ở lane full.
- Grep `FAIL|fix|bug` trong `quick-lane.md` → 0 kết quả.

## Chỗ chưa rõ (cần interview)

- Ngưỡng nhẹ cắt bỏ chính xác những hạng mục nào của `qc.md`? (đề xuất: bỏ full suite toàn
  repo, log service, hợp đồng skill `Dùng:/Kiểm/Ra`; giữ test-từng-task + DoD)
- Bằng chứng QC ghi ở đâu: chỉ trong chat, hay append vào `plan/<slug>.md`, hay cả hai?
- Quick có ép red → green như full không, hay chỉ ép "test pass"?
- Vòng fix ở quick có trần số vòng không? Vượt trần thì escalate lên full hay hỏi user?
- Có cần luật cho quick external (engine ngoài trả về FAIL) không?
- Có phải sửa `scripts/doc_lint.py` để lint được mục QC mới trong file plan quick không?
