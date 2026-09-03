# SPEC — Cổng hỏi bằng chat, Next step nêu pha kế, và đường kẻ cuối lượt

Ngày: 2026-09-03 · Bản: 1.2 · Brief: ../brief/2026-09-03-1220-gate-chat-va-next-pha.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: làm bộ workflow chạy đúng trên host KHÔNG có hook và KHÔNG có tool hỏi dạng popup,
  bằng ba luật viết thành văn và được test khoá: mọi câu hỏi cho user hỏi bằng chat rồi kết lượt ·
  mọi dòng `Next step:` nêu tên pha kế tiếp · mọi lượt chat kết thúc bằng một đường kẻ ngang.
- Trong phạm vi:
  - Luật cấm tool hỏi dạng popup, áp cho MỌI câu hỏi gửi user, không riêng 7 cổng duyệt.
  - Luật `Next step:` phải nêu tên pha kế tiếp và trỏ về bảng pha, làm lớp dự phòng cho hook.
  - Luật đường kẻ ngang `---` ở cuối mỗi lượt chat.
  - Sửa 12 dòng `Next step:` hiện có trong `skills/*/SKILL.md` cho hợp luật mới.
  - Ba test khoá tương ứng, chạy trong `tests/`.
- NGOÀI phạm vi:
  - Không sửa `hooks/` và `scripts/tdq_state.py`. Hook `[TDQ:NEXT]` vẫn là đường chính; phần này
    chỉ thêm lớp chữ dự phòng, đúng điều kiện user nêu "chỉ bổ trợ nếu hook không work ổn".
  - Không chép nội dung `phases.md` (việc-phải-làm, điều-kiện-xong) vào từng skill — user chọn
    phương án B ở câu 2.
  - Không thêm pha mới, không đổi `PHASE_TABLE`.
  - Không đụng `~/.claude/CLAUDE.md` — file ngoài repo, không đi theo bản portable.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | phải chứng minh có host thật sự thiếu hook, không đoán |
| Interview | CÓ (đã xong) | 3 câu, user trả lời `1a 2b (có điều kiện) 3a` + thêm yêu cầu 4 |
| Pha `diagram` | BỎ | repo này không có pha đó trong `PHASE_TABLE`, cũng không có skill `tdq-diagram` |
| Pha `plan` | CÓ | có sửa nhiều file, cần hợp đồng từng file |
| QC độc lập (agent) | CÓ | đây là luật khoá hành vi; vòng QC trước đã chứng minh test tự viết bỏ sót nhánh |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Luật cấm popup, áp mọi câu hỏi | `skills/tdq-conventions/references/user-facing-block.md` mục Hard rules | file có câu luật nêu tên tool popup và phạm vi "mọi câu hỏi"; test 1 xanh |
| 2 | Luật kết lượt sau khi hỏi | `skills/tdq-conventions/references/approval.md` | file nêu rõ: hỏi xong kết lượt, chờ user chat trả lời |
| 3 | Luật `Next step:` nêu pha kế | `skills/tdq-conventions/references/user-facing-block.md` hoặc mục riêng trong `tdq-conventions/SKILL.md` | luật nêu khuôn dòng và nói rõ nó là lớp dự phòng khi host không có hook |
| 4 | 12 dòng `Next step:` sửa lại | `skills/*/SKILL.md` (8 skill, 12 dòng) | mỗi dòng nêu tên một pha có trong `PHASE_TABLE`, hoặc nêu skill kế tiếp khi không đổi pha; test 2 xanh |
| 5 | Luật đường kẻ cuối lượt | `skills/tdq-conventions/references/user-facing-block.md` thành phần 6 (mới) | luật nói rõ: ký tự là `---` (ba gạch nối, vẽ thành đường kẻ kéo hết hàng), nằm SAU khối trả lời, là dòng cuối cùng của lượt; thành phần 5 được viết lại cho khớp |
| 6 | Test khoá cấm popup | `tests/` | quét `skills/` bắt tên tool popup xuất hiện ở dạng cho phép dùng; đỏ khi có |
| 7 | Test khoá `Next step:` | `tests/` | quét mọi dòng `Next step:` trong `skills/*/SKILL.md`, đỏ khi một dòng không nêu pha kế hay skill kế |
| 8 | Test khoá luật đường kẻ | `tests/` | kiểm `user-facing-block.md` có mô tả luật đường kẻ cuối lượt và ví dụ đúng khuôn |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| luat-trinh-bay | `skills/tdq-conventions/references/user-facing-block.md`, `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/SKILL.md` | không | 1, 2, 3, 5 |
| next-step-skill | `skills/tdq-build/SKILL.md`, `skills/tdq-check-status/SKILL.md`, `skills/tdq-intake/SKILL.md`, `skills/tdq-lsp-setup/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-status/SKILL.md` | luat-trinh-bay (khuôn dòng phải chốt trước) | 4 |
| test-khoa | `tests/` | luat-trinh-bay, next-step-skill | 6, 7, 8 |

Ba module không khai chung đường dẫn nào. `skills/tdq-conventions/SKILL.md` chỉ thuộc
luat-trinh-bay; `tdq-conventions` không có dòng `Next step:` cần sửa theo nghĩa module 2 vì dòng
của nó đã trỏ đúng sang `phases.md`.

## 3. Cách tiếp cận & lý do

- Chọn: viết luật vào tầng `tdq-conventions` (một chỗ duy nhất), sửa 12 dòng `Next step:` cho
  hợp luật, rồi khoá cả ba luật bằng test quét văn bản trong `tests/`.
- Vì: hiện luật cấm popup chỉ nằm ở `skills/tdq-intake/references/interview.md:44` — chỗ duy nhất
  trong cả `skills/`, `hooks/`, `scripts/`. Luật nằm ở file của một pha thì sáu cổng còn lại không
  chịu ràng buộc. `tdq-conventions` là tầng mọi skill đều nạp đầu tiên, nên đặt ở đó là đủ phủ.
- Vì (phần `Next step:`): host Gemini CLI, GitHub Copilot CLI, Aider không có hook lifecycle
  (nguồn: bảng so sánh CLI agent ở `hidekazu-konishi.com/entry/cli_coding_agents_comparison.html`
  và `github.com/weykon/agent-hooks`), nên `[TDQ:NEXT]` không tồn tại ở đó. Dòng `Next step:` là
  thứ duy nhất agent còn đọc được.
- Vì (phần test): user chọn 3A. Vòng QC của yêu cầu trước đã cho thấy luật viết ra mà không khoá
  thì trôi — chính luật đánh số câu hỏi từng bị vi phạm dù đã có văn bản.
- Đã loại: chép nguyên việc-phải-làm và điều-kiện-xong của mỗi pha vào từng skill — vì sinh 12
  bản sao của `phases.md`, lệch nhau sau lần sửa đầu tiên. User chọn B.
- Đã loại: thêm hook mới để bơm pha kế — vì đúng host cần lớp này lại là host không chạy hook.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | tầng luật chung, chính là nơi ba luật mới nằm |
| tdq-intake | plugin:tdq-workflow | NỀN | pha analyze vừa chạy xong |
| tdq-spec | plugin:tdq-workflow | NỀN | pha đang chạy |
| tdq-plan | plugin:tdq-workflow | DÙNG | pha kế, viết hợp đồng từng file |
| tdq-build | plugin:tdq-workflow | DÙNG | pha implement + qc |
| Đã xét 217 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực — `skill_inventory.py --loc` không khớp skill nào cho việc này |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — đầu ra là văn bản luật và test quét văn bản, không có runtime mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ: chưa có `docs/kien-truc.md` trong repo, nên thay bằng các ràng buộc
đã chốt bằng văn bản khác mà việc này chạm tới:

- `doc_lint.py` rule R6 giới hạn số dòng từng skill (`SKILL_LINE_LIMITS`) — việc này thêm chữ vào
  `tdq-conventions/SKILL.md` và sửa 12 dòng trong 7 skill, có thể đụng trần.
- `build_portable.py` cấm mọi lần dùng chữ `CLAUDE_PLUGIN_ROOT` trong bản claude — luật mới nếu
  trích khuôn dòng `Next step:` có chứa chuỗi đó sẽ làm hỏng build.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Luật đường kẻ cuối lượt đá nhau với thành phần 5 của `user-facing-block.md` ("khối trả lời là phần cuối, không viết gì bên dưới") | hai luật cùng đòi làm dòng cuối, agent chọn bừa | **User chốt 2026-09-03 12:38: "khối trả lời xong thì bổ sung line".** Vậy `➤` là dòng cuối của KHỐI, đường kẻ là dòng cuối của LƯỢT và nằm ngay SAU `➤`. Thành phần 5 phải sửa từ "không viết gì bên dưới" thành "chỉ có đúng đường kẻ cuối lượt ở bên dưới" — plan bắt buộc sửa câu đó, để lại là mâu thuẫn |
| Test quét chữ bắt nhầm chính câu luật (câu cấm popup buộc phải nhắc tên tool) | test đỏ ngay khi viết luật | test chỉ đỏ khi tên tool xuất hiện ở ngữ cảnh CHO PHÉP dùng; câu cấm nằm trong danh sách trừ, khai bằng đường dẫn + số dòng chứ không bằng regex lỏng |
| Sửa 12 dòng `Next step:` làm vỡ R6 giới hạn dòng | build/lint đỏ | đo số dòng từng skill trước khi sửa, dòng mới không dài hơn dòng cũ quá 1 dòng |
| Bản portable không được build lại | luật mới không tới host khác | DoD bắt buộc chạy `build_portable.py` và `tdq_checkportable.py check --root <bundle>` cho cả 3 bản |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Luật cấm popup có mặt ở tầng conventions | `user-facing-block.md` có câu cấm, nêu rõ áp cho mọi câu hỏi gửi user, không chỉ cổng |
| Q2 | Luật kết lượt | `approval.md` nói rõ: hỏi xong kết lượt, chờ user trả lời bằng chat, cấm tự suy diễn duyệt |
| Q3 | Test khoá cấm popup đỏ đúng lúc | thêm một câu cho phép dùng tool popup vào một skill bất kỳ → test đỏ; bỏ ra → xanh |
| Q4 | Mọi dòng `Next step:` nêu pha kế | mỗi dòng nêu tên một pha có trong `PHASE_TABLE`, hoặc nói rõ pha không đổi và skill kế là gì |
| Q5 | Test khoá `Next step:` đỏ đúng lúc | xoá tên pha khỏi một dòng → test đỏ; trả lại → xanh |
| Q6 | Luật `Next step:` nói rõ vai trò dự phòng | văn bản ghi: hook là đường chính, dòng này gánh khi host không có hook |
| Q7 | Luật đường kẻ cuối lượt không mâu thuẫn | `user-facing-block.md` chỉ còn MỘT câu quyết định dòng cuối lượt; thành phần 5 không còn câu "không viết gì bên dưới"; hai ví dụ ở cuối file có đường kẻ nằm sau dòng `➤` |
| Q8 | Test khoá luật đường kẻ | test kiểm được sự có mặt và tính nhất quán của luật, đỏ khi luật bị xoá; luật khai đúng ký tự `---`, không nhận ký tự vẽ khác (`———`, `___`, ký tự khung) |
| Q9 | Lint tài liệu | `doc_lint.py` chạy trên toàn repo, 0 vi phạm |
| Q10 | Không hồi quy | số test đỏ không tăng so với mốc trước khi sửa |
| Q11 | Bản portable | build lại cả 3 bản, mỗi bản CLEAN khớp manifest |

DoD: Q1–Q11 đều PASS · `docs/tdq/report/<slug>.md` đã viết · working log có dòng của lượt cuối.

## 7. Câu hỏi còn mở

(Rỗng.)
