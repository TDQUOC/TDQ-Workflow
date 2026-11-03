# Request — 2026-07-31-audit-full-workflow

## Nguyên văn yêu cầu (user, 2026-07-31 17:29)

> okay tôi muốn bạn recheck lại tổng thể workflow hiện tại và phân tích, review xem đã
> ổn để hoạt động với gần như tất cả work case chưa, có confict gì xảy ra không? và có
> case không mong muốn nào có thể sẽ xảy ra không? hãy phân tích và nếu cần có thể tạo
> 1-2 sameple e2e để test và sau đó check xem có issue gì không? nếu có thì note ->
> xác định nguyên nhân -> fix để full tdq workflow hiện tại có thể hạot động ổn với mọi
> case, mọi model kể cả model cấp thấp như model local tham số thấp

## Cách hiểu đầu tiên

- **Mục tiêu**: audit tổng thể plugin tdq-workflow 0.6.0 (state machine, skills
  intake/spec/plan/build, mode main/subagent/external, deep search hybrid, hooks,
  scripts) — tìm conflict giữa các luật/nhánh, các edge case không mong muốn.
- **Phạm vi đoán**:
  1. Review tĩnh: đọc chéo toàn bộ skill/script/hook tìm mâu thuẫn luật, khoảng trống
     state machine, case degrade chưa phủ.
  2. Chạy 1–2 sample E2E (ví dụ: 1 quick lane trọn vòng, 1 case external/deep-search
     hoặc case nghịch cảnh) để lộ issue thật.
  3. Issue tìm được → note → nguyên nhân gốc → fix + test.
  4. Tiêu chí "model cấp thấp": task packet/prompt cho engine ngoài và agent phải đủ
     tường minh để model local tham số thấp (qua agy/codex hoặc runner khác) vẫn làm
     đúng — cần đánh giá độ robust của contract/prompt, fallback khi model yếu làm sai.
- **Chỗ chưa rõ**:
  - "Mọi model kể cả model local tham số thấp" — có engine local cụ thể nào đang định
    dùng không (ollama/lmstudio?) hay chỉ cần contract đủ robust cho model yếu?
  - Sample E2E được phép gọi engine thật (agy/codex, tốn quota) hay ưu tiên drill mô phỏng?
  - Còn 2 việc PENDING reload từ 0.6.0 (đo lại token, trigger search-scout) — gộp vào
    request này luôn hay để riêng?
