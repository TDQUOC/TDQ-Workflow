# Questions — 2026-07-31-hybrid-deep-search

## Vòng 1 (2026-07-31 16:07 +07, AskUserQuestion)

1. **Phase 2 dùng tối đa bao nhiêu agent agy?**
   - a) 3 giữ nguyên (Đề xuất) · b) 2 · c) 4–5
   - User chọn: **"3 (giữ nguyên)"** — giữ `TDQ_SEARCH_MAX_AGENTS=3`.

2. **Escalation chain khi default = flash-medium?** (hiện: low → high, ≤2 retry)
   - a) medium → high (Đề xuất) · b) medium → high → pro · c) low → medium → high
   - User chọn: **"medium → high"** — giữ logic 1 bậc, chỉ nâng điểm xuất phát.

3. **Findings phase 1 có gộp vào kết quả cuối không?**
   - a) Gộp vào kết quả cuối (Đề xuất) · b) Chỉ làm bản đồ route
   - User chọn: **"Gộp vào kết quả cuối"** — scout + agy tổng quát ghi đúng
     schema, merge chung với phase 2.

4. **Có đường tắt bỏ phase 1 khi câu hỏi hẹp/rõ route?**
   - a) Có — đi thẳng phase 2 (Đề xuất) · b) Luôn chạy đủ 2 phase
   - User chọn: **"Luôn chạy đủ 2 phase"** — flow đồng nhất, không đường tắt.
     (Lưu ý: luật trigger deep search ≥2 dấu hiệu vẫn là cổng vào — câu hỏi
     không đủ tiêu chí deep search thì không vào flow này ngay từ đầu.)

## Các câu đã chốt trước đó qua chat (15:53–16:01)
- Phase 1 = 1 Claude scout ∥ 1 agy tổng quát (user chốt 16:01).
- Default model agy = gemini-3.6-flash-medium (user yêu cầu 15:53).
- agy là engine ưu tiên; cap Claude toàn flow ≤3 agent (15:53).
