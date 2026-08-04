# Request: Làm TDQ workflow linh hoạt & bớt ma sát

- Ngày: 2026-08-04
- Slug: `2026-08-04-workflow-linh-hoat`

## Nguyên văn yêu cầu của user

> tôi đang có một vài yêu cầu cần chỉnh sửa cho bộ workflow như sau :
> - tôi muốn skip bước gọi tdq-review ở sau spec/plan
> - ở mọi sub-agent claude có thể đổi model thấp hơn hoặc cao hơn cho sub-agent và tinh chỉnh thinking cho sub-agent nhằm tối ưu hiệu quả, hiệu suất và thời gian thực thi và chi phí
> - sau khi người dùng duyệt spec thì sẽ tiến hành làm plan luôn thay vì phải hỏi như kiểu (Spec approved, phase moved to plan. Per tdq-spec, plan writing happens in a new turn — send another message when you're ready to pick the implementation mode (main/subagent/external) for tdq-plan / Plan approved (mode main), phase moved to implement. Build will start in a new turn per the workflow) và thay vì tốn thêm câu hỏi cho mode implement thì hãy chuyển việc duyệt mode chung với lúc duyệt plan ví dụ như là duyệt plan mode main hoặc duyệt plan mode external. Và tương tự sau khi người dùng duyệt plan thì tiến hành implement thay vì tốn thêm một turn chỉ để người dùng nhắn câu tiếp tục.
> - các câu hỏi ko nên tạo interface ask và như kiểu một turn chat kết thúc bằng câu hỏi + các hướng trả lời : summary ưu nhược của hướng. để người dùng có thể trả lời mở.
> - kể cả ở lane quick vẫn có websreach, phân tích và interview step
> - tôi muốn tdq workflow thông minh hơn, có thể sẽ có step phân tích để có thể quyết sau bước interview là sẽ có bước nào, skill nào, phase nào sẽ đc dùng, không bị fix cứng để linh hoạt hơn cho nhiều task vụ và không bị overstep. nhưng quy chung sẽ luôn có (brainstoming (nhận yêu cầu phân tích làm rõ) -> spec/plan (trình bày spec/plan có thể là mini spec/plan và xin duyệt) -> implement -> report)

## Cách hiểu đầu tiên

**Mục tiêu:** giảm ma sát và số turn của TDQ workflow, đồng thời làm workflow tự
điều chỉnh độ nặng theo task thay vì fix cứng 2 lane.

**Phạm vi đoán (6 thay đổi):**
1. Bỏ bước gọi agent `tdq-reviewer` sau khi viết spec và plan (hiện có trong
   `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`).
2. Cho phép Claude chọn model + mức thinking cho mọi sub-agent (Agent tool có
   `model`; các runner agent `agy-runner`/`codex-runner`/`search-runner` có model
   engine ngoài riêng). Cần chuẩn hoá: ai chọn, chọn theo tiêu chí gì, ghi ở đâu.
3. Ghép gate: `duyệt spec` → viết plan ngay trong cùng turn; `duyệt plan mode <X>`
   → build ngay trong cùng turn. Bỏ luật "spec và plan không cùng một turn" và bỏ
   turn chờ giữa plan và build. Mode implement chốt lúc duyệt plan (không hỏi riêng).
4. Cấm dùng `AskUserQuestion`; mọi câu hỏi trình bày bằng chat cuối turn, kèm các
   hướng + ưu/nhược mỗi hướng, để user trả lời mở.
5. Lane quick cũng phải có web search + phân tích + interview (hiện đang "chỉ
   interview khi thật sự chưa rõ", không bắt buộc research).
6. Thêm bước quyết định lộ trình sau interview: Claude tự chốt sẽ dùng phase/skill
   nào cho task cụ thể, không fix cứng. Khung bất biến: brainstorm → spec/plan
   (có thể mini) → implement → report.

## Chỗ chưa rõ (cần interview)

- Q1. Bỏ `tdq-reviewer` hẳn (xoá agent) hay chỉ bỏ gọi mặc định, giữ để gọi tay?
- Q2. Model/thinking cho sub-agent: muốn Claude tự quyết theo heuristic, hay muốn
  một bảng mapping cố định trong conventions?
- Q3. Ghép turn spec→plan: vẫn ghi file spec + file plan riêng chứ? Có còn cần
  user duyệt spec riêng, hay gộp luôn thành một lần duyệt?
- Q4. Cấu trúc lane: giữ 2 lane quick/full nhưng cho co giãn, hay thay hẳn bằng
  1 luồng duy nhất tự chọn độ nặng?
- Q5. Web search bắt buộc ở quick: có ngưỡng bỏ qua (task thuần nội bộ) không?
- Q6. Hook/state machine (`scripts/tdq_state.py`, `prompt_context.py`, approval
  gate vừa làm hôm qua) có được sửa theo không?
