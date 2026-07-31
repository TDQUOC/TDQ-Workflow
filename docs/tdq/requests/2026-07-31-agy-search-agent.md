# REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow

Ngày: 2026-07-31 14:23 · Slug: 2026-07-31-agy-search-agent · Lane: full (user chốt)

## Nguyên văn yêu cầu

> okay vậy tôi muốn resreach để tạo sreach agent sẽ dùng agy để sreach và báo cáo
> (dành cho sreach avande hoặc ranking thông tin), hãy check xem có khả thi không?

> mode full và tôi muốn tạo sreach agent cho sreach avande và tích hợp nó vào tdq
> workflow để claude có thể sreach và tổng hợp thông tin tốt hơn (claude có thể tự
> triger nó chạy), và thiết kế chi tiết để có thể hoạt động tốt và đúng vơi cả model
> cấp thấp

> và tôi muốn là khi gọi deep sreach default sẽ gọi sreach agent (agy cli) mà chúng
> ta đang tạo, truyền hết vào đó và sreach, nhưng không spam quá nhiều, max 3
> agent(có thể config trong setting.json của claude) nhưng 3 agent những truyền all
> data vào đó để deep sreach

## Cách hiểu đầu tiên

- Mục tiêu: agent "search-runner" dùng Antigravity CLI (agy) headless làm engine
  advanced search / ranking thông tin; Claude TỰ trigger được (Agent tool) khi cần
  search sâu + tổng hợp; tích hợp vào plugin tdq-workflow như một năng lực research.
- Khả thi đã xác minh 2026-07-31 (probe thật): agy 1.1.8 headless có `search_web` +
  `read_url_content` thực thi thật (kết quả khớp ground truth npm registry + mốc
  ngày Gemini CLI shutdown); ~17s/query với gemini-3.6-flash-low; có `--json-schema`
  enforce structured output.
- Ràng buộc thiết kế: chịu được model cấp thấp → mọi logic dễ hỏng nằm trong
  script/schema (giống triết lý external mode), prompt cấm trả lời không có evidence,
  bắt full URL nguồn, có bước verify.
- Chỗ chưa rõ (sẽ interview): vai trò so với Tavily (thay thế hay bổ sung, policy
  trigger); kiến trúc 1 call vs multi-route; model default + escalation; mức verify
  nguồn; format/chỗ lưu report; phạm vi tích hợp vào các skill tdq-*.

## Rủi ro đã biết (từ probe)

- URL nguồn agy trả hay bị cụt (domain trần) → schema + prompt phải ép full URL.
- Model có thể trộn kiến thức training vào kết quả → cần luật evidence-only + verify.
- Quota agy dùng chung với coding external mode.
