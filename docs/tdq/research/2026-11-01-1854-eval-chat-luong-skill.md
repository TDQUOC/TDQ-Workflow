# Nghiên cứu — Eval chất lượng skill và hook
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày kiểm nguồn: 2026-11-01 · Request: `2026-11-01-1854-eval-chat-luong-skill`

Phạm vi subtask: bốn truy vấn web, chỉ dùng nguồn chính thức Anthropic/Claude; đối chiếu năm cải tiến đã duyệt và rút hệ quả thiết kế cho `tdq_eval`. Không chạy eval/model/API trả phí; không sửa source/state/plan. Các nhận định nguồn bên dưới đã kiểm trực tiếp trên tài liệu web trong lượt này. Khuyến nghị thiết kế là suy luận cho TDQ, không phải yêu cầu bắt buộc của nhà cung cấp hoặc kết quả thực nghiệm của repository.

## 1. Truy vấn → nguồn → hệ quả thiết kế

| # | Truy vấn đã thực hiện | Nguồn chính thức chính | Hệ quả đề xuất |
|---|---|---|---|
| Q1 | `site:platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices evaluations models skill development` | [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); [Testing and iteration](https://claude.com/resources/guides/the-complete-guide-to-building-skills-for-claude/testing-and-iteration) | Lập eval trước sửa hành vi; tách kiểm trigger khỏi kết quả tác vụ; có baseline và phạm vi model. |
| Q2 | `site:anthropic.com/engineering demystifying evals AI agents trials graders held-out calibration saturation` | Kết quả dẫn tới [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | Dùng nhiều trial, môi trường sạch, grader được hiệu chuẩn; phát hiện bộ case đã chạm trần. |
| Q3 | `site:platform.claude.com/docs prompt caching usage cache_creation_input_tokens cache_read_input_tokens input_tokens pricing` | [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching); [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) | Thu usage/cache thật; tách token khỏi tiền, ghi rate/model/TTL thay vì lấy số ký tự skill làm chi phí. |
| Q4 | `site:anthropic.com OR site:platform.claude.com/docs "held-out" evaluation prompt test` | [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | Chốt mục tiêu đo và tập holdout trước; không lấy chính case đã dùng chỉnh skill để chứng minh tổng quát hóa. |

Đã mở thêm [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) để kiểm khác biệt nền tảng. Hai URL skill do task cung cấp đều truy cập được; không dùng bản blog tổng hợp thay nguồn gốc.

## 2. Thông tin đã xác minh từ nguồn

### S1 — Viết skill theo eval và kiểm nhiều model

Anthropic khuyên tạo eval trước khi viết tài liệu dài: tìm lỗi trên tác vụ đại diện khi chưa có skill, lập scenario, đo baseline, viết hướng dẫn tối thiểu rồi lặp. Tài liệu còn yêu cầu kiểm các model dự định sử dụng vì hiệu quả skill phụ thuộc model nền. Ba scenario trong hướng dẫn là điểm khởi đầu authoring, không phải bảo đảm đủ mẫu thống kê. [Nguồn và mục “Evaluation and iteration”/“Test with all models”](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

### S2 — Trigger, chức năng và baseline là ba phép kiểm khác nhau

Guide phân biệt trigger đúng/ngôn ngữ diễn đạt lại/không trigger chủ đề khác; chức năng kiểm output/API/error/edge case; so sánh baseline xem lợi ích. Ví dụ token, lượt trao đổi và retry trên trang là minh họa, không phải số đo của TDQ hay cam kết giảm chi phí. [Testing and iteration](https://claude.com/resources/guides/the-complete-guide-to-building-skills-for-claude/testing-and-iteration).

### S3 — Nhiều trial, grader và trần baseline

Anthropic định nghĩa trial là một lần thử; hành vi biến thiên nên chạy nhiều trial. Eval đo cả model lẫn harness, cần môi trường sạch. Model grader cần hiệu chuẩn bằng người; ưu tiên kết quả thực hơn chuỗi tool cứng khi có nhiều cách giải hợp lệ. Bộ eval đạt 100% còn hữu ích cho hồi quy nhưng mất tín hiệu cải thiện. `pass@k` và `pass^k` trả lời hai câu hỏi khác nhau, không được thay bằng nhau. [Demystifying evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

### S4 — Tiêu chí đo và dữ liệu chưa dùng để chỉnh

Tài liệu success criteria khuyến nghị mục tiêu cụ thể, đo được, sát tác vụ; nêu baseline, tập held-out và nhiều chiều gồm task fidelity, consistency, latency, price. Chấm bằng code phù hợp khi có đáp án xác định; LLM grader cần kiểm độ tin cậy trước khi mở rộng. Tài liệu không quy định một cỡ mẫu hoặc tỷ lệ holdout dùng chung cho mọi skill. [Define success criteria](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

### S5 — Usage và cache thực tế

Trên Claude API, ba trường input phân biệt token chưa cache, ghi cache và đọc cache. Tổng input được tài liệu định nghĩa:

```text
total_input_tokens = input_tokens + cache_creation_input_tokens + cache_read_input_tokens
```

Vì vậy `input_tokens` riêng lẻ không phải toàn bộ context đã gửi. Cache hit không có nghĩa token đó biến mất; phải đọc usage để biết cache có hoạt động. Đây là ngữ nghĩa Claude API, không tự áp tên trường này cho host/provider khác. [Prompt caching — Tracking cache performance](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#tracking-cache-performance).

### S6 — Token không đồng nhất với tiền

Pricing tách input, output, cache write/read; mức giá phụ thuộc model và có modifier theo tính năng/nền tảng. Không chép bảng đơn giá cụ thể vào rule lâu dài: đây là dữ liệu có thể đổi. Các lần chạy khác điều kiện cache không được so tiền bằng một giá input duy nhất. [Pricing chính thức](https://platform.claude.com/docs/en/about-claude/pricing).

### S7 — Không suy điểm từ host này sang host khác

Overview mô tả các cách nạp custom skill khác nhau giữa Claude Code, API và claude.ai; API skill chạy cùng code-execution tool/container. Cùng nội dung skill không có nghĩa cùng đường nạp hoặc môi trường chạy. Kết luận “phải phân tầng theo host” dưới đây là hệ quả thiết kế cho TDQ, không phải một con số chuyển đổi điểm do nguồn công bố. [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## 3. Khuyến nghị thiết kế cho `tdq_eval` — chưa phải implementation

### 3.1. Gate lập eval và hai loại đối chứng

Thay đổi skill/hook có thể làm đổi hành vi cần eval-plan trước build: liệt kê hành vi, case, grader, host/model, repetitions, ngân sách và điều kiện nhận kết quả. Sửa typo thuần nên có lý do miễn eval, không tự kéo theo gọi model. Tái dùng `tdq_eval` và record/receipt hiện có; subtask này chưa khảo sát API code để khẳng định các field đã được hỗ trợ.

Đối chứng chính: baseline đang dùng với candidate sửa đổi. Đối chứng tùy chọn: có/không target skill trong fixture cô lập, chỉ khi có thể thao tác đúng phạm vi đã duyệt. Không vô hiệu hóa gate bắt buộc của workflow sản xuất để tạo đối chứng. Không gọi thử candidate đơn lẻ là bằng chứng skill tạo thêm giá trị.

Chốt trước cặp cùng task/input/fixture/tool/config/model snapshot/harness version, reset workspace/history và ghi cache condition. Đảo thứ tự A/B để giảm nhiễu; không chỉ chọn trial PASS. Với trigger, dùng prompt tự nhiên và negative/paraphrase; run ép nạp skill chỉ kiểm chất lượng có điều kiện, không thay chứng cứ trigger.

### 3.2. Repetitions, holdout và grader

Chia development/holdout bằng task family để tránh chỉ đổi cách diễn đạt rồi rò nội dung. Pin bộ case/grader trước đo; sửa rubric hoặc xem holdout để chỉnh candidate thì cần phiên holdout mới. Ghi số trial thực tế, failure và độ phân tán; không gán số trial cố định cho mọi tình huống. Thiếu mẫu hoặc chênh lệch trong nhiễu phải trả chưa đủ bằng chứng.

Grader có đáp án đúng/sai và ca biên riêng; dùng deterministic checks khi phù hợp. Nếu dùng judge, ghi version/rubric, đối chiếu mẫu có nhãn người và xử lý bất đồng; judge không chắc cần có trạng thái unknown. Baseline chạm trần: giữ suite hồi quy, bổ sung case khó/edge case, hoặc đo chi phí với quality floor chốt trước. Không suy “skill vô dụng” từ chênh lệch điểm bằng0 trên bộ case bão hòa.

### 3.3. Ba nhóm số đo và phạm vi hiệu lực

| Nhóm | Field/điều kiện đề xuất |
|---|---|
| Trigger | TP/FN/FP trên positive/negative/paraphrase; bằng chứng skill được nạp thực, không chỉ lời tự nhận |
| Task quality | Outcome/artifact đúng, rubric theo chiều, lỗi nghiêm trọng; báo cả task không nạp được skill |
| Cost/time/retries | Usage provider gốc, cache read/write/uncached/output, wall time, model/tool call, retry và lỗi infrastructure; thiếu dữ liệu là unavailable |

Mỗi bảng kết quả có model ID/version thực sự quan sát được, host/version, harness, config/skill/case/grader hash và điều kiện cache. Alias model chưa xác minh phải ghi unresolved. Không gộp nhiều host/model thành một điểm để tuyên bố phổ quát; host/model chưa đo là chưa kiểm chứng.

Chi phí đề xuất tính theo từng category và rate snapshot có ngày/nguồn, cộng retry/grader/tool khi thực sự phát sinh. Nếu chỉ có usage, gọi tiền quy đổi là estimate; nếu subscription/host không cung cấp billing đầy đủ, không gọi đó là tiền hóa đơn thực. Thiếu cache telemetry không được hiểu là cache bằng0. Tokenizer đo file chỉ là diagnostic kích thước, không thay usage toàn tác vụ.

### 3.4. Khuyến nghị dựa trên giá trị đã đo

| Khuyến nghị | Điều kiện đề xuất |
|---|---|
| Giữ | Có lợi ích chất lượng hoặc giảm cost/time, không vượt mức hồi quy cho phép đã chốt |
| Rút gọn | Bản ngắn giữ quality/trigger trong biên chấp nhận và có lợi ích đo được |
| Bỏ phần tùy chọn | Đối chứng đủ nhạy cho thấy không có lợi ích cần giữ hoặc gây hại; không tự bỏ nghĩa vụ/gate đã duyệt |
| Chưa kết luận | Trần baseline, mẫu yếu, judge chưa hiệu chuẩn, usage thiếu hoặc nhiều yếu tố đổi cùng lúc |

Đây là logic khuyến nghị cho report, không phải quyền tự động xóa skill/hook. Kết quả chỉ hiệu lực trên task distribution và các ô model/host đã đo. Không có eval mới hoặc kết luận giữ/rút/bỏ cụ thể cho một skill nào được tạo trong lượt nghiên cứu này.

## 4. Điểm cần chốt ở spec/plan sau nghiên cứu

1. Tiêu chí thay đổi hành vi cần gate; ai phê duyệt miễn eval và ngân sách model thật.
2. Case family, grader oracle, severity và quality floor; quy tắc khi baseline bão hòa.
3. Số repetitions/holdout theo mức rủi ro và độ biến thiên, không lấy “ba scenario” thành ngưỡng chứng nhận.
4. Các host/model được chứng nhận; nguồn usage và cách đánh dấu estimate/unavailable.
5. Report recommendation có evidence và mức chắc chắn, giữ raw trial/failure; không tự quyết bỏ guard hoặc suy giá trị từ độ ngắn tài liệu.
