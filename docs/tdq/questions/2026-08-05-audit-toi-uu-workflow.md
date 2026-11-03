# Hỏi–đáp: 2026-08-05-audit-toi-uu-workflow

## Vòng 1 (lúc mở request, trước khi phân tích)

1. Cần đo lại carry-cost bằng `token_audit.py` hay chỉ đọc code/luật tĩnh?
   → Trả lời gián tiếp qua phần phân tích: đã đo lại (3 session mới nhất, sau fix vòng 2,
   `python3 scripts/token_audit.py --sessions 3 --top 12`, 11:04) VÀ đọc code song song.
2. "Issue có thể xảy ra" — chỉ token/time, hay gồm cả đúng-sai logic/an toàn?
   → Hỏi lại tường minh ở vòng 2 (câu 1), user chọn **A: gồm cả**.
3. Output report: file trong `docs/tdq/` hay chỉ cần trả lời trong chat?
   → Theo convention lane full: report luôn ở `docs/tdq/reports/<slug>.md` (≤10 dòng),
   chi tiết đầy đủ ở `docs/tdq/knowledge/<slug>.md`. Không cần hỏi, đã có luật sẵn.

## Vòng 2 (sau khi audit xong, 11:18)

**Câu 1:** Phạm vi "issue" trong report — có gồm cả 2 mâu thuẫn luật (external-block
quick-lane vs tdq-build; định nghĩa "đã đổi repo" lệch giữa reminder-codes.md và
tdq-conventions §6) + rủi ro false-positive của `stop_gate.py` không, hay chỉ thuần
token/thời gian?
- A (đề xuất): gồm cả — đây đều là nguồn gây tốn thời gian gián tiếp
- B: chỉ token/time thuần, issue logic để dịp khác

→ **User chọn A.** Report sẽ gồm cả 3 issue logic/an toàn phát hiện được, không chỉ
carry-cost thuần.

**Câu 2:** Sau report, dừng ở đó hay làm luôn spec/plan triển khai ngay?
- A (đề xuất): dừng ở report — bạn đọc rồi tự chọn phần nào đáng mở request mới
- B: làm luôn spec/plan ngay trong turn kế tiếp

→ **User chọn A.** Request này khép lại ở một bản report đề xuất (không sửa code sản
phẩm); phần "implement" của lane full = viết report/knowledge, không phải code change.
Việc triển khai đề xuất nào sẽ là request mới do user tự mở sau khi đọc.
