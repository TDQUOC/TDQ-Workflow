# BRIEF — Tối ưu độ dài và context của bộ workflow TDQ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay tôi cần mở một request phân tích xem có thể optimize full bộ workflow này để tối
> ưu legth và context length nhưng giữ đầy đủ bộ rule, behavior của skill (có thể xử lí
> toàn bộ workflow bằng tiếng anh, nhưng có rule set ui ux trình bày tiếng việt cho doc
> và code) hãy mở request lane full đeer check xem có thể tối ưu ko, và hướng tối ưu để
> báo cáo cho tôi. turn này check khả thi và hướng đi, chưa optimize ở turn này

**Cách hiểu đầu tiên.**

Mục tiêu: giảm số token mà bộ workflow TDQ nạp vào context mỗi lượt, mà KHÔNG mất một
luật hay một hành vi nào của skill. Hai đòn bẩy user gợi ý: (1) viết thân skill bằng
tiếng Anh vì tiếng Anh tốn ít token hơn tiếng Việt cho cùng một ý; (2) giữ nguyên luật
"mọi thứ user nhìn thấy và mọi doc sinh ra đều tiếng Việt" — tức đổi ngôn ngữ của
HƯỚNG DẪN, không đổi ngôn ngữ của SẢN PHẨM.

Phạm vi đoán: `skills/tdq-*` (44 file .md, 3311 dòng, ~193 KB), `agents/tdq-*.md`,
`~/.claude/CLAUDE.md`, và cơ chế nạp reference của từng skill. Có thể chạm cả hai bản
`portable_claude` và `portable_codex` vì chúng là bản sao đồng bộ.

**Turn này user chỉ muốn: kết luận khả thi hay không, và hướng đi. CHƯA tối ưu.**
Nghĩa là request này dừng ở sản phẩm phân tích — báo cáo có số đo và phương án — chứ
không sửa file skill nào. Việc tối ưu thật là request sau.

Chỗ chưa rõ, phải hỏi ở vòng interview:

1. "Giữ đầy đủ rule/behavior" chứng minh bằng cách nào — bằng người đọc, hay bằng máy
   (bộ test hành vi chạy trước và sau)? Đây là chỗ quyết định request tối ưu sau này có
   dám cắt hay không.
2. Đo "context length" ở đâu: tổng byte file skill, hay số token thực nạp trong một
   request điển hình (khác nhau rất xa vì reference chỉ nạp khi cần)?
3. Ngưỡng nào coi là thành công: giảm bao nhiêu phần trăm?
4. Đổi tiếng Anh áp cho những file nào — chỉ thân SKILL.md, hay cả reference, cả hook
   message, cả agent description?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill/công cụ | Nguồn | DÙNG? | Lý do |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | CÓ | chính skill đang chạy phase này |
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | CÓ | request này chạy đủ lane full |
| `tdq-conventions` | plugin:tdq-workflow | CÓ | vừa là luật, vừa là ĐỐI TƯỢNG bị tối ưu |
| `tdq-status`, `tdq-check-status` | plugin:tdq-workflow | KHÔNG | không hỏi trạng thái |
| `scripts/token_audit.py` | project | CÓ | đo carry-cost thật từ transcript |
| `scripts/step_audit.py` | project | CÓ | đo số bước, đối chiếu tầng runtime |
| `scripts/doc_lint.py` | project | CÓ | R6 đã có trần dòng cho SKILL — hạ trần là một cần gạt |
| `graphify` | user skill | KHÔNG | đồ thị chỉ chứa mã sản phẩm, bộ skill là markdown |
| `mem0-memory` | plugin (mcp) | CÓ | chốt xong ghi một fact về ngưỡng tối ưu |
| `tavily-primary` | plugin (mcp) | CÓ | đã dùng ở bước research |

### Số đo hiện trạng — đo, không đoán

Bộ skill: **44 file `.md`, 3.311 dòng, 193.288 byte / 160.162 ký tự**, trong đó 21.459 ký
tự có dấu (13,4%). Tải theo phase (byte, gồm cả reference bắt buộc đọc):

| Phase | File nạp | Byte |
|---|---|---|
| luôn nạp | `CLAUDE.md` + `tdq-conventions/SKILL.md` | 13.278 |
| intake + analyze | SKILL + 5 reference | 29.788 |
| spec | SKILL + template | 8.884 |
| plan | SKILL + template + mode-gate | 17.254 |
| build | SKILL + qc + report + team-mode | 23.839 |
| khối luật hay nạp kèm | user-facing-block + approval + phases + soul | 19.187 |

`python3 scripts/token_audit.py --sessions 2` trên hai phiên thật:

| Nhóm | Lần | Carry-cost (token) | Tỉ trọng |
|---|---|---|---|
| Read file | 377 | 510.123.372 | 41,9% |
| Bash khác | 976 | 325.664.735 | 26,8% |
| `tdq_state.py` (dump JSON) | 360 | 92.060.475 | 7,6% |
| graphify | 126 | 70.897.633 | 5,8% |
| Edit (echo lại diff) | 1032 | 66.819.418 | 5,5% |
| chạy test suite | 403 | 53.892.269 | 4,4% |
| **Skill (nạp skill)** | 41 | **674.901** | **0,06%** |
| TỔNG | 3.873 | 1.216.720.393 | |

### Điều rút ra quan trọng nhất

**Giả định trong yêu cầu bị số đo bác một phần.** Văn bản skill không phải chỗ đắt: nạp
skill chiếm 0,06% carry-cost. Chỗ đắt là output của tool ở lại trong context và bị đọc
lại ở mọi API call sau đó — `Read file` gần 42%, `Bash` gần 27%, riêng dump JSON của
`tdq_state.py` 7,6%.

Nói vậy KHÔNG có nghĩa hướng tiếng Anh vô nghĩa. Nó có nghĩa: hai hướng khác nhau hẳn về
độ lớn và độ rủi ro, và phải chọn có ý thức chứ không gộp làm một.

- **Hướng A — cắt chữ trong skill (đổi tiếng Anh, nén văn xuôi thành bảng).** Lợi ích
  chặn trên nhỏ: cả bộ skill ~160k ký tự, một request điển hình nạp 40–60 KB. Rủi ro
  cao nhất trong ba hướng vì đụng vào chính văn bản luật.
- **Hướng B — cắt output tool.** Lợi ích lớn nhất, rủi ro thấp nhất: không đụng một luật
  nào, chỉ đổi cách gọi lệnh (`tdq_state.py next --brief` thay `get`, `Read` theo
  `offset/limit`, giao việc đọc nhiều file cho agent con). Luật cho hướng này đã có sẵn ở
  `references/context-budget.md` nhưng chưa có gì CƯỠNG CHẾ, nên bị bỏ qua.
- **Hướng C — nạp reference theo nhu cầu (progressive disclosure).** Anthropic có tài
  liệu chính thức và tự dùng kỹ thuật này. Bộ TDQ đã tách reference sẵn; chỗ hụt là ba
  câu "BẮT BUỘC mở file đó và đọc hết" ép nạp cả file kể cả khi chỉ cần một mục.

### Nguồn từ research

Chi tiết ở `docs/tdq/research/2026-08-17-2121-toi-uu-context-workflow.md`.

- Tỉ lệ token Việt/Anh: **không có số chính thức cho tokenizer của Claude.** Tham chiếu
  cl100k: tiếng Việt ~3,3 token/từ so với tiếng Anh ~1,3 (~2,5 lần). Độ tin cậy THẤP khi
  suy sang Claude — đây là con số phải TỰ ĐO trước khi dựa vào.
- "Prompt tiếng Anh, output tiếng Việt có giảm tuân thủ không": **không tìm được nghiên
  cứu trả lời trực tiếp.** Có bằng chứng gián tiếp rằng càng nhiều instruction thì tuân
  thủ càng giảm. Đây là khoảng trống thật, không phải chỗ mình lười tra.
- Progressive disclosure và deferred tool loading: có tài liệu chính thức của Anthropic,
  là kỹ thuật họ tự dùng. "Viết luật dạng bảng thay văn xuôi" thì KHÔNG có nguồn chính
  thức, chỉ là quan sát cộng đồng.
- Đếm token chính xác: endpoint `POST /v1/messages/count_tokens` là cách duy nhất chính
  xác. `tiktoken` SAI cho Claude (hụt 15–20%, tệ hơn với văn bản không phải tiếng Anh) —
  đúng chỗ mình cần đo nhất. Heuristic "3,5 ký tự/token" lệch tới 20%.
- Hệ quả: `scripts/token_audit.py` đang quy đổi bằng `ký tự/4`, tức **đang đếm hụt token
  tiếng Việt** — công cụ đo hiện có không đủ tin để chấm điểm trước-sau của hướng A.

## Hỏi đáp

### Vòng 1 — scope (user trả lời "1abcd 2a 3a 4a 5a")

| # | Hỏi | Đáp |
|---|---|---|
| 1 | Request bao quanh mặt nào | A+B+C+D: hiệu năng context · độ tin cậy (chứng minh không mất luật) · bảo trì (luật chống phình lại) · tương thích (đồng bộ `portable_claude` và `portable_codex`) |
| 2 | Phạm vi hướng tối ưu | A: làm hướng B (cắt output tool) và C (nạp theo nhu cầu) trước; hướng A (dịch tiếng Anh) để riêng một request sau |
| 3 | Chứng minh giữ đủ rule | A: bộ test hành vi chạy máy, trích luật thành checklist rồi đối chiếu trước/sau |
| 4 | Đo token bằng gì | A: gọi `count_tokens` của Anthropic |
| 5 | Ai giữ bộ workflow | A: mình user — tiếng Anh không cản ai |

### Phạm vi đã chốt

- Mặt CHỌN: hiệu năng context · độ tin cậy · bảo trì · tương thích (3 bản: gốc, portable_claude, portable_codex)
- Mặt LOẠI: bảo mật · trải nghiệm người dùng cuối · an toàn dữ liệu · hiệu năng runtime của script
- Bối cảnh: bộ 44 file skill/193 KB · một người giữ · 3 bản phải đồng bộ · đã có `token_audit.py` và `doc_lint.py` để đo
- Mức đầu tư suy ra: **đầy đủ** — vì đối tượng sửa chính là bộ luật điều khiển mọi request sau này, hỏng một dòng là hỏng mọi request

### Vòng 2 — user trả lời "6a 7b"

| # | Hỏi | Đáp |
|---|---|---|
| 6 | Request dừng ở đâu | A: ra **báo cáo + đề án + bộ test hành vi** rồi dừng. KHÔNG sửa skill trong request này; sửa là request sau, có spec riêng |
| 7 | Đo token bằng gì | B: cài thư viện đếm token offline vào venv riêng, không cần API key |

Ghi chú thi hành câu 7: gói `ctoc` mà research nhắc **không có trên PyPI cũng không có
trên npm** (nó là dự án blog, chưa đóng gói). Thay bằng `anthropic-tokenizer` 0.1.0 trên
PyPI — cùng ý đồ: chạy offline, không cần key. Đã thử trong venv tạm: cài được, đếm được.

### Đo token thật — bằng `anthropic-tokenizer`, không còn ước lượng ký tự/4

Mẫu một câu, cùng nội dung hai thứ tiếng:

| Bản | Ký tự | Token | Ký tự/token |
|---|---|---|---|
| Tiếng Việt | 85 | 45 | 1,89 |
| Tiếng Anh | 89 | 19 | 4,68 |

Cả bộ skill: **93.197 token / 160.162 ký tự = 1,72 ký tự mỗi token.** Tải theo phase:

| Khối | Token |
|---|---|
| luôn nạp (`CLAUDE.md` + conventions) | 6.243 |
| intake + analyze | 15.135 |
| spec | 4.434 |
| plan | 8.453 |
| build | 11.521 |
| khối luật hay nạp kèm | 15.275 |
| **Cộng một request lane full** | **61.061** |

### Sửa lại kết luận sớm — chỗ tôi nói hụt

Ở turn trước tôi nói "nạp skill chỉ chiếm 0,06% carry-cost". Con số đó đúng với thứ
`token_audit.py` xếp vào nhóm `Skill`, nhưng nhóm đó CHỈ đếm kết quả của tool `Skill`.
Văn bản skill đọc bằng `Read` bị xếp vào nhóm `Read file`, và phần skill nạp thẳng vào
system prompt thì transcript không thấy. Vậy 0,06% là **chặn dưới**, không phải con số
thật. Con số thật của tải skill là **61.061 token mỗi request lane full** — nằm thường
trực trong context và bị đọc lại ở mọi API call sau đó.

Hệ quả: hướng A (dịch tiếng Anh) KHÔNG nhỏ như tôi nói lúc đầu. Với 1,89 so với 4,68 ký
tự mỗi token, cùng một nội dung viết tiếng Anh tốn khoảng **40–45%** số token — tức
61.061 có thể xuống còn **25.000–28.000**. Đây là con số phải kiểm lại bằng một bản dịch
thử THẬT ở request sau, không phải suy từ tỉ lệ một câu.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | cần số về tokenizer và bằng chứng chính thức về progressive disclosure |
| Vòng scope | CÓ (đã xong) | request gọi tên cả một hệ thống, nhiều mặt chưa nói |
| Interview chi tiết | CÓ (đã xong, 2 vòng) | hai chỗ mơ hồ về phạm vi và cách đo |
| Spec + plan | CÓ | lane full, đối tượng là bộ luật gốc |
| Implement | CÓ | dựng thước đo và bộ test hành vi — KHÔNG sửa skill |
| QC độc lập (agent) | CÓ | request trước cho thấy agent QC bắt được chỗ tôi thổi phồng số |
| Review sâu (`tdq-reviewer`) | BỎ | user chưa yêu cầu; QC độc lập đã phủ |
| Chia subagent lúc build | BỎ | phần lớn task cùng đụng hai file mới, chuỗi phụ thuộc thẳng |

### Vòng 3 — bổ sung: tách mô tả skill theo mục, tạm disable (user hỏi ngày 2026-08-17)

Nguyên văn: "check luôn liệu có thể xử lí để tách mô tả các skill phụ trợ ko liên quan
đến workflow và một vector db hoặc file có chia theo mục ví dụ skill về design, skill về
unity, skill về web hoặc skill về code skill về security và tạm disable nó để khi
inventory skill sẽ lấy đúng mục và tự động active skill cần thiết để hạn chế overload
skill description với những skill ko chung mục của dự án để save token, và liệu idea của
tôi có hoạt động không và hiệu quả thế nào".

**Trả lời ngắn: ý tưởng CHẠY ĐƯỢC, và không cần dựng gì mới — Claude Code đã có sẵn cơ
chế đúng bằng ý bạn. Nhưng một nửa ý tưởng (tự động active lại skill đúng mục) thì KHÔNG
làm được, và phải nói rõ chỗ đó.**

#### Cơ chế có sẵn: `skillOverrides`

Chuỗi mô tả lấy nguyên văn từ binary `claude` đang chạy trên máy này
(`node_modules/@anthropic-ai/claude-code-darwin-arm64/claude`):

> Per-skill listing overrides keyed by skill name. "name-only" lists the skill without
> its description; "user-invocable-only" hides it from the model but keeps /name; "off"
> hides it from both. Absent = on.

Ba mức, đúng ba nấc bạn cần:

| Mức | Model còn thấy | User còn gõ `/tên` | Token tiết kiệm |
|---|---|---|---|
| `name-only` | chỉ thấy TÊN | có | mất phần mô tả, giữ tên |
| `user-invocable-only` | không thấy gì | có | mất cả tên lẫn mô tả |
| `off` | không thấy gì | không | mất cả tên lẫn mô tả |

Ghi ở `~/.claude/settings.json` (toàn máy) hoặc `.claude/settings.local.json` (chỉ dự án
này) — tức **chia theo mục cho từng dự án đúng như bạn muốn**, chỉ là bằng file settings
chứ không phải vector DB. Máy này đã có sẵn một dòng: `"unity-skills":
"user-invocable-only"`. Còn có UI `/skills` để bật tắt.

#### Hiện trạng đo được

284 skill đang bật. Mô tả đầy đủ của chúng nằm trong system prompt mỗi lần gọi API:
**30.633 token** (phần tên trần: 3.208 token). Top nguồn:

| Nguồn | Skill | Token mô tả |
|---|---|---|
| `plugin:data-engineering` | 34 | 3.698 |
| `user` | 33 | 3.618 |
| `plugin:huggingface-skills` | 25 | 3.224 |
| `plugin:hyperframes` | 20 | 2.423 |
| `plugin:figma` | 12 | 1.554 |
| `plugin:firecrawl` | 10 | 1.404 |
| `plugin:qt-development-skills` | 12 | 1.328 |
| `plugin:adobe-for-creativity` | 7 | 1.214 |
| `plugin:datarobot-agent-skills` | 13 | 1.160 |
| `plugin:desktop-commander` | 6 | 1.076 |
| `plugin:tavily` | 8 | 1.074 |
| `plugin:cloudflare` | 11 | 1.073 |
| 19 nguồn còn lại | 123 | 7.786 |
| **Tổng** | **284** | **30.633** |

Đính chính một số tôi tính hụt trước đó: con số "1.874 file / 203.867 token" tôi quét
lúc đầu là **sai để dùng** — nó quét cả thư mục cache marketplace, gồm hàng loạt skill
CHƯA cài. Số đúng để bàn là 30.633.

#### Ước tính tiết kiệm cho một dự án như TDQWorkflow

Nhóm không dính gì tới repo này (data-engineering, huggingface, hyperframes, figma,
firecrawl, qt, adobe, datarobot, desktop-commander, cloudflare, redis, mongodb, unreal,
base44, postman, canva, chrome-devtools): **196 skill · 22.587 token**.

| Phương án | Token còn lại | Tiết kiệm |
|---|---|---|
| Giữ nguyên | 30.633 | — |
| 196 skill kia → `name-only` | ~10.300 | ~20.300 (66%) |
| 196 skill kia → `off` | 8.046 | 22.587 (74%) |

#### Chỗ ý tưởng KHÔNG chạy được — nói thẳng

1. **Không có "tự động active skill đúng mục".** `skillOverrides` là cấu hình TĨNH đọc
   lúc khởi động. Không có hook nào bật lại một skill giữa phiên. Muốn skill quay lại thì
   sửa settings rồi mở phiên mới. Mức `name-only` là chỗ dung hoà gần nhất: model vẫn
   biết skill tồn tại (thấy tên) nên còn cơ hội gọi, chỉ là mất mô tả.
2. **Vector DB không lắp vào được.** Danh sách skill do chính Claude Code dựng và nhét
   vào system prompt trước khi phiên chạy; MCP server hay vector DB đều nằm SAU chỗ đó,
   không thay thế được. Vector DB chỉ có ích nếu tự viết một skill-router riêng — đó là
   một sản phẩm khác, không phải tối ưu context.
3. **Tiết kiệm này là tiết kiệm CỬA SỔ, không phải tiết kiệm TIỀN.** Khối mô tả nằm
   trong system prompt nên được prompt-cache; mỗi lượt gọi lại chỉ tính giá cache-read.
   Cái được thật là 22,6k token cửa sổ trống ra, cộng việc model bớt bị 196 mô tả lạc đề
   kéo đi sai hướng.

#### So với ba hướng đã có

| Hướng | Token/ request lane full | Rủi ro mất luật |
|---|---|---|
| D — tắt skill lạc mục (`skillOverrides`) | −22.587, một lần cấu hình | gần bằng 0 — không đụng file skill nào |
| B+C — cắt/gộp thân skill TDQ | −? (phải đo) | cao — sửa chính bộ luật |
| A — dịch thân skill sang tiếng Anh | 61.061 → ~25–28k (ước) | trung bình — sửa toàn bộ văn bản |

Hướng D rẻ nhất, an toàn nhất, làm trong vài phút, nên **xếp trước B+C**. Nó không thay
thế B+C: D cắt khối mô tả trong system prompt, B+C cắt thân skill nạp theo phase — hai
khối khác nhau, cộng dồn được.

### Vòng 4 — bổ sung: lưu tên + mô tả skill ra kho tìm kiếm, Claude tự search khi cần

Nguyên văn: "tôi muốn là tên và mô tả skill sẽ được lưu ở đâu đó như vector db để khi cần
claude có thể search ra và chọn đúng một vài skill có liên quan để chọn sẽ dùng skill nào
mà vẫn tiết kiệm context length, ý tưởng này thì sao".

**Trả lời ngắn: ý tưởng ĐÚNG về mặt kiến trúc — chính harness đang chạy phiên này đã làm
y hệt vậy với TOOL (`ToolSearch`, 95 lần xuất hiện trong binary). Nhưng áp cho SKILL thì
vướng đúng một chỗ kỹ thuật, và có đường vòng. Và có một cách làm tốt hơn cả bản bạn mô
tả.**

#### Tiền lệ: harness tự làm chuyện này rồi

Phiên này có ~400 tool MCP. Chúng KHÔNG nằm hết trong system prompt — chỉ có tên, còn
schema thì phải gọi `ToolSearch` mới nạp. Đúng mô hình bạn nói: index nhẹ ở trong,
chi tiết nằm ngoài, gọi ra khi cần. Nên ý tưởng không viển vông, nó là mẫu thiết kế
đã được chính Anthropic dùng.

#### Chỗ vướng: skill bị tắt thì KHÔNG gọi lại được

Chuỗi nguyên văn trong binary:

> `" is disabled via skillOverrides. Remove the override from your settings to run it."`

Nghĩa là: nếu tắt skill ở mức `off` hay `user-invocable-only` để giấu mô tả đi, thì router
có tìm thấy cũng **không invoke được** — phải sửa settings và mở phiên mới. Bốn nấc:

| Mức | Model thấy mô tả | Model thấy tên | Model gọi được | Token/284 skill |
|---|---|---|---|---|
| mặc định (on) | có | có | có | 30.633 |
| `name-only` | không | **có** | **có** | 3.208 |
| `user-invocable-only` | không | không | KHÔNG | 0 |
| `off` | không | không | KHÔNG | 0 |

Bằng chứng cho cột "gọi được" ở mức `name-only`: binary có chuỗi
`(on/name-only locked by frontmatter disable-model-invocation)` — hai mức `on` và
`name-only` được gom chung là nhóm model gọi được. Đây là suy từ chuỗi, phải xác nhận lại
bằng một lượt chạy thật ở phase implement.

**Đường vòng nếu vẫn muốn `off`:** router không invoke skill, mà trả về **đường dẫn
`SKILL.md`**, rồi Claude `Read` thẳng file đó. Nội dung skill là markdown thuần nên đọc
file cho kết quả gần như invoke. Mất: thư mục gốc plugin và phạm vi quyền do tool `Skill`
tự gắn.

#### Kiểm tra: có sẵn tính năng tìm skill trong Claude Code không?

Binary CÓ `SearchSkills` và `skill_search`, nhưng đọc mô tả thì nó là tool phía
claude.ai — "List the user's enabled claude.ai skills… To recommend skills they do NOT
have yet, use SearchSkills" — tức tìm trong chợ skill của claude.ai, kèm cổng chính sách
`allow_plugin_skill_search`. **Không phải** router tìm trong skill đã cài trên máy. Muốn
có thứ đó thì phải tự dựng.

#### Số: kho tìm kiếm rẻ hơn bao nhiêu

Trung bình một skill: mô tả ~108 token, tên trần ~11 token.

| Kiến trúc | Token nền | Token mỗi lần tra | Tổng nếu tra 2 lần/phiên |
|---|---|---|---|
| Giữ nguyên | 30.633 | 0 | 30.633 |
| `name-only` toàn bộ | 3.208 | 0 | 3.208 |
| `off` + router | ~200 (mô tả router) | ~700 (5 skill + mô tả đầy đủ) | ~1.600 |
| `name-only` + router | ~3.400 | ~700 | ~4.800 |

Tra tới **43 lần** trong một phiên thì `off` + router mới hoà vốn với hiện trạng. Thực tế
1–3 lần. Tiết kiệm ~**95%** khối này.

#### Lỗ hổng thật của ý tưởng — và cách bịt

Mô tả skill hiệu quả vì nó **thụ động**: model đọc lướt rồi tự nhận ra "cái này áp được".
Router thì **chủ động** — model phải NHỚ đi tra. Mà nó không biết thứ nó không biết. Đây
đúng là lý do skill `superpowers:using-superpowers` trong phiên này phải hét lên bắt kiểm
skill trước mọi câu trả lời. Chuyển sang router mà không bịt chỗ này thì tiết kiệm token
xong hỏng việc.

**Cách bịt — và đây là chỗ tôi phải sửa lại lời turn trước.** Turn trước tôi nói "không
có tự động active skill đúng mục". Câu đó đúng với riêng `skillOverrides`, nhưng SAI nếu
tính cả hook: **hook `UserPromptSubmit` chạy TRƯỚC khi model đọc prompt**, nên nó tra
được kho ngay trên câu user vừa gõ rồi chèn thẳng 3–5 mô tả hợp nhất vào context. Repo
này đã dùng đúng cơ chế đó cho `[TDQ:INTAKE]` và `[TDQ:APPROVE]`. Tức là **tự động active
skill đúng mục LÀ làm được** — chỉ là bằng hook, không bằng settings.

#### Kiến trúc đề xuất — ba tầng

| Tầng | Làm gì | Được gì |
|---|---|---|
| 1 | 196 skill lạc mục → `name-only` | 30.633 → ~10.300 token, tên vẫn còn nên vẫn gọi được |
| 2 | Hook `UserPromptSubmit` tra kho, chèn top-k mô tả hợp với prompt | trả lại tự động active, tốn ~300–600 token chỉ ở turn liên quan |
| 3 | Tool router gọi tay khi hook trượt | lưới an toàn, ~700 token/lần |

#### Vector DB hay chỉ cần từ khoá?

**Chưa cần vector DB.** Toàn bộ kho chỉ 284 mô tả, ~38.700 ký tự — nhỏ hơn một file mã
nguồn cỡ vừa. BM25 hay tìm từ khoá chạy trên ngần đó dữ liệu là tức thì, không cần model
embedding, đúng ràng buộc "offline, không API key" bạn chốt ở câu 7b. Embedding cục bộ
đòi tải model vài trăm MB; embedding qua API thì vi phạm ràng buộc. **Cách làm đúng: dựng
BM25 trước, đo tỉ lệ trúng trên một bộ prompt mẫu, chỉ nâng lên vector khi số đo cho thấy
từ khoá trượt.** Nếu sau này cần vector thật thì máy đã có sẵn `plugin:lumen`
(`semantic_search`) để tái dùng.

**Kết luận:** ý tưởng chạy được, tiết kiệm ~95% khối mô tả, và bịt được lỗ tự-động-active
bằng hook. Nhưng phải ĐO tỉ lệ trúng trước khi tin — router tra trượt còn hại hơn tốn
token, vì nó làm mất một skill lẽ ra phải dùng mà không ai biết.
