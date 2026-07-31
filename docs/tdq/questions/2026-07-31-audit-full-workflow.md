# Questions — 2026-07-31-audit-full-workflow

## Vòng 1 (2026-07-31 17:3x, AskUserQuestion)

1. **"Model cấp thấp/local tham số thấp" nghĩa là gì cho request này?**
   → **Chỉ harden contract**: không thêm engine mới; audit + sửa prompt/agent
   def/task packet/skill để model yếu (agy/codex slug thấp, hoặc engine local
   gắn sau) vẫn làm đúng. Việc tích hợp engine local (ollama…) để request riêng.

2. **Sample E2E chạy thế nào?**
   → **2 sample, gọi engine thật**, trong project sandbox `TDQ_PROJECT_DIR`
   riêng (không đụng state thật):
   - Sample 1: lane quick **external** trọn vòng, dùng model **thấp nhất**
     trong list engine → đo robustness contract với model yếu thật.
   - Sample 2: lane full mini mode **main** + các nhánh sự cố (approve mơ hồ,
     request đè request dở, engine hỏng → fallback).

3. **Gộp 2 việc PENDING từ 0.6.0?**
   → **Gộp luôn**: phiên mới sau reload đủ điều kiện — (a) đo lại token E2E
   deep search sau fix wrapper QC1.1, mục tiêu ≤250k; (b) verify trigger agent
   type `search-scout`.

## Không còn câu hỏi mở

- Engine + slug cụ thể cho sample 1: Claude tự lấy từ
  `scripts/external_models.py list` và ghi lựa chọn vào spec (user review spec).
- Fix issue tìm được: nằm trong scope request (user đã yêu cầu note → nguyên
  nhân → fix ngay trong request này).
