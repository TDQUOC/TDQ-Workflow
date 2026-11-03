# PHƯƠNG ÁN — Hợp lối code Ponytail vào TDQ-Workflow

Ngày: 2026-09-16 · Spec: ../spec/2026-09-16-1447-hop-ponytail-vao-tdq.md (bản 1.0, ĐÃ DUYỆT)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Tài liệu này là **phương án đề xuất**, không phải bản đã thi hành. Người dùng chốt `4a`: request
này dừng ở đây, việc sửa code thật mở thành request riêng.

**Nhãn mức tin cậy** dùng suốt tài liệu:
`[XÁC THỰC]` = tài liệu chính thức `code.claude.com/docs` · `[SUY-CODE]` = đọc từ file trong máy,
kèm `đường-dẫn:dòng` · `[BÊN-THỨ-BA]` = issue tracker, blog, không phải nguồn chính thức.

## Mục lục

- 0. Tóm tắt quyết định
- Luồng 1 — Thân luật
- Luồng 2 — Mức gắt `muc_gat`
- Luồng 3 — Hook thứ sáu `SubagentStart`
- Luồng 4 — Một nguồn chân lý
- Luồng 5 — Hợp nhất hướng thất bại
- Cổng duyệt riêng — sửa luật gốc
- Thứ tự triển khai

## 0. Tóm tắt quyết định

Năm luồng. Mỗi dòng là một câu hỏi có/không độc lập — bạn nhận luồng này, loại luồng kia đều được,
trừ chỗ cột phụ thuộc nói khác.

| # | Luồng | Quyết định bạn cần trả lời | Giá phải trả (đã đo) | Phụ thuộc |
|---|---|---|---|---|
| 1 | Thân luật — viết thang 7 bậc thành luật đúng khuôn, gộp vào `chung.md`, neo một dòng ở `tdq-build/SKILL.md` | Có gộp vào tầng luật đang có, thay vì dựng tầng luật thứ hai? | `chung.md` 78 → ~123 dòng (trần thật 500, không phải trần skill); `tdq-build/SKILL.md` còn **đúng 4 dòng** trống nên neo phải ≤ 4 dòng | không |
| 2 | Mức gắt — thêm khoá state `muc_gat` 5 giá trị, mặc định `full`, chỉ người dùng hạ được | Có thêm một trục mức gắt riêng, rời hẳn `implement_mode`? | 1 khoá state mới + 1 nhánh trong `prompt_context.py` dưới trần 3 dòng / 240 ký tự; sửa **một câu** ở `skills/tdq-build/references/rules/chung.md:22` (xem mục cổng duyệt riêng) | cần 1 |
| 3 | Hook thứ sáu — `SubagentStart` bơm luật cho `tdq-implementer` | Có bịt lỗ luật vô hình với sub-agent? | 1 file hook mới trong `hooks/scripts/` + 1 mục trong `hooks.json`; **không** dùng lại được khuôn `print()` thô của 2 hook hiện có | cần 1 |
| 4 | Một nguồn chân lý — thêm đích Cursor vào `scripts/build_portable.py` | Có xuất luật sang host ngoài Claude Code? | 1 nhánh trong script đã có; 0 file copy tay | cần 1 |
| 5 | Hợp nhất hướng thất bại — bảng nêu rõ chỗ nào fail-open, chỗ nào fail-closed | Có ghi thành luật thay vì để mỗi hook tự xử? | 0 dòng code — một bảng trong `chung.md`, đã tính trong giá của luồng 1 | cần 1, 2, 3 |

**Điều quan trọng nhất trong bảng này:** cả 5 luồng đều **cần luồng 1**. Luồng 1 là thân luật; bốn
luồng còn lại chỉ là đường dẫn luật đi tới nơi. Nhận 2/3/4/5 mà loại 1 thì không còn gì để bơm.

**Điều rẻ nhất mà bạn có thể nhận riêng:** luồng 1 + luồng 5 — cộng lại là **0 dòng code**, chỉ
sửa tài liệu luật. Đủ để lối code Ponytail thành luật thật của mọi lượt implement chạy trong
conversation chính.

## Luồng 1 — Thân luật: viết thang 7 bậc thành luật của TDQ

**Quyết định:** gộp vào tầng luật đang có, chia làm hai chỗ theo đúng luật xếp tầng —
**câu luật** đặt trong thân `skills/tdq-build/SKILL.md:1` (phần `## Hard rules`, nạp mỗi lượt
implement), **bảng 7 bậc chi tiết** đặt trong `skills/tdq-build/references/rules/chung.md:19`
(mục `## When it applies` trở xuống). Không dựng tầng luật thứ hai, không thêm file luật mới.

**Giá phải trả:** `skills/tdq-build/SKILL.md:1` đang 146 dòng trên trần 150 khai ở
`scripts/doc_lint.py:46` → còn **đúng 4 dòng**. Câu luật dài hơn 4 dòng thì phải nâng trần đó
kèm comment ghi ngày, theo đúng tiền lệ đã có hai lần trong chính file ấy
(`scripts/doc_lint.py:42` và `scripts/doc_lint.py:79`).
`skills/tdq-build/references/rules/chung.md:1` đi từ 78 lên khoảng 123 dòng — không đụng trần
nào, vì R6 chỉ áp trần riêng cho file **tên đúng là `SKILL.md`**
(`scripts/doc_lint.py:272`), còn trần chung là 500 dòng (`scripts/doc_lint.py:88`).

### Vì sao phải chia hai chỗ, không dồn hết vào chung.md

Đây là chỗ tôi suýt làm sai. Thang 7 bậc là luật **tier 1**, không phải tier 3: over-engineering
là nợ kỹ thuật không khai, và tier 1 định nghĩa ở `skills/tdq-conventions/references/soul.md:27`
là "no foreseeable technical debt is left undeclared". Mà luật xếp chỗ ở
`skills/tdq-conventions/references/soul.md:99` nói thẳng: luật tier 1 và tier 2 **phải nằm trong
thân một skill được nạp mỗi lượt**; chỉ luật tier 3 và bảng chi tiết mới được đẩy vào file
reference. Dồn trọn thang vào chung.md là vi phạm câu đó, vì chung.md chỉ được nạp khi agent
sắp sửa một file code (bảng tra ở `skills/tdq-build/references/rules/index.md:15`).

Cùng dòng luật ấy còn trả lời luôn câu "nếu 4 dòng không đủ thì sao":
`skills/tdq-conventions/references/soul.md:101` — "hitting the cap means raising the cap, never
compressing a tier 2 law to fit". Nên **nâng trần là đường đã được luật gốc cho phép trước**,
không phải một ngoại lệ tôi tự xin.

| Phần | Đặt ở | Tier | Lý do |
|---|---|---|---|
| Câu luật: không xây cái người dùng không xin; leo bậc thấp nhất còn đúng | `skills/tdq-build/SKILL.md:1`, mục `## Hard rules` | 1 | `skills/tdq-conventions/references/soul.md:99` buộc tier 1 nằm trong thân skill nạp mỗi lượt |
| Bảng 7 bậc + vùng cấm đơn giản hoá + cặp RIGHT/WRONG | `skills/tdq-build/references/rules/chung.md:19` | 3 | bảng chi tiết, tra khi thật sự sắp viết code |

### Vì sao không đi đường `.claude/rules/`

Thư mục `.claude/rules/` là cơ chế nạp luật mỗi session thật: file không khai `paths:` thì nạp
mọi session ở mức ưu tiên ngang `CLAUDE.md`, file khai `paths:` glob thì chỉ nạp khi Claude chạm
file khớp glob `[XÁC THỰC]`. Nhưng nó là cơ chế **của project**, còn TDQ là **plugin chạy trên
mọi project** — người dùng đã chốt phạm vi đó ở vòng 1. Plugin không được tự tạo file trong repo
của người dùng, và repo này hiện cũng không có `.claude/rules/` `[SUY-CODE]`. Đường đó vẫn hữu
ích, nhưng đúng chỗ của nó là **bản portable ở luồng 4**, nơi người dùng chủ động cài luật vào
một project cụ thể.

### Khuôn bắt buộc của thân luật

Luật mới phải viết đúng khuôn 3 mục ở `skills/tdq-conventions/references/soul.md:39`:
`## When it applies` (dấu hiệu nhận ra bằng mắt hoặc bằng lệnh) · `## What to do` (các bước
đánh số, mỗi bước một hành động) · `## Self-check` (một lệnh, hoặc một câu hỏi có/không), cộng
một cặp ví dụ RIGHT/WRONG ở chỗ dễ đọc sai nhất. Khuôn này không phải khuyến nghị: bộ test của
repo đang ép nó, và `skills/tdq-conventions/references/soul.md:110` là lệnh kiểm. Bản dự thảo
đầy đủ nằm ở file thứ hai của request này (`docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md:1`).

### Hai chỗ trong luật cũ cố ý KHÔNG sửa

- `skills/tdq-conventions/references/soul.md:34` (luật phá thế) giữ nguyên. Người dùng chốt
  `2a`: thang chỉ được chọn giữa những cách **đã đạt ngưỡng đo được**, nên không có cảnh thang
  và ngưỡng tranh nhau để phải phá thế.
- `skills/tdq-conventions/references/clean-code.md:55` (SRP) giữ nguyên. Người dùng chốt `3a`:
  hai lượt có thứ tự — thang quyết định **một thứ có nên tồn tại không**, SOLID quyết định
  **hình dạng của thứ còn sống sót**. Không ai phải nhường ai.

## Luồng 2 — Mức gắt `muc_gat`

**Quyết định:** thêm một khoá state mới tên `muc_gat`, 5 giá trị
`off | lite | full | ultra | review`, mặc định **`full`**. Nó là **một trục hoàn toàn khác**
với `implement_mode`, không phải giá trị thêm vào trục cũ.

**Giá phải trả:** một khoá trong khuôn state mặc định ở `scripts/tdq_state.py:186` (ngay cạnh
`implement_mode`), một bộ nhãn + alias giống cặp `MODE_LABELS`/`MODE_ALIASES` ở
`scripts/tdq_state.py:56` và `scripts/tdq_state.py:65`, và một nhánh in mức hiện tại trong
`hooks/scripts/prompt_context.py:28` — nhánh này phải sống trong trần 3 dòng / 240 ký tự khai
ngay tại `hooks/scripts/prompt_context.py:28` và `hooks/scripts/prompt_context.py:29`, nên nó
chỉ được in **tên mức**, không được in thân luật.

### Hai trục, không phải một

`implement_mode` trả lời "**ai** làm việc này" — `main`, `subagent`, `codex`, nhãn người dùng đọc
nằm ở `scripts/tdq_state.py:56`. `muc_gat` trả lời "**gắt tới đâu**". Hai câu hỏi độc lập: chạy
`codex` ở mức `ultra` là hợp lệ, chạy `main` ở mức `lite` cũng hợp lệ. Nhồi 5 giá trị mức gắt
vào `MODE_ALIASES` ở `scripts/tdq_state.py:65` sẽ làm cổng mode ở phase `plan` hỏi sai câu, vì
cổng đó đọc đúng cái map ấy để dựng danh sách lựa chọn.

| Mức | Thang 7 bậc | Ngưỡng đo được | Vào bằng cách nào |
|---|---|---|---|
| `off` | tắt | **tắt** | chỉ khi người dùng yêu cầu tường minh — xem mục cổng duyệt riêng |
| `lite` | chỉ bậc 1–3 (trả lời, sửa tại chỗ, thêm vào chỗ đã có) | bật | người dùng gõ mức |
| `full` | cả 7 bậc — **mặc định** | bật | mặc định, không cần gõ gì |
| `ultra` | cả 7 bậc + bắt buộc khai nợ ra chat khi leo quá bậc 3 | bật | người dùng gõ mức |
| `review` | một lượt soi lại cái vừa viết, **không phải mặc định** | bật | lệnh riêng một phát, hết lượt tự về mức cũ |

### Ba điều học được từ Ponytail, không cần phát hiện lại

1. **`review` không được làm mặc định.** Ponytail khai hai danh sách riêng:
   `~/Documents/ponytail/hooks/ponytail-config.js:17` liệt kê 5 mức hợp lệ, còn
   `~/Documents/ponytail/hooks/ponytail-config.js:18` liệt kê 4 mức chạy thường trực — `review`
   bị loại khỏi danh sách thứ hai `[SUY-CODE]`. Chặn ở đường vào nằm tại
   `~/Documents/ponytail/hooks/ponytail-mode-tracker.js:52` `[SUY-CODE]`, và nó là kết quả của
   một lỗi đã báo (issue #377) `[BÊN-THỨ-BA]`. `muc_gat` nên copy nguyên ràng buộc này.
2. **`review` là mức độc lập, không phải mức cao hơn `ultra`.** Khai ở
   `~/Documents/ponytail/hooks/ponytail-instructions.js:8` `[SUY-CODE]`.
3. **Bảng cường độ mà người dùng đọc chỉ có 3 mức** (`lite`/`full`/`ultra`), xem
   `~/Documents/ponytail/skills/ponytail/SKILL.md:30` `[SUY-CODE]`. `off` và `review` là chuyện
   của config chứ không phải nút người dùng vặn hằng ngày — TDQ nên trình bày y hệt: ba mức trong
   bảng, hai mức còn lại nằm trong tài liệu.

### Không có cơ chế tự xuống mode

Đây là câu người dùng chốt ở vòng 2 và là điều kiện để cả luồng này hợp với luật gốc:
**không có cơ chế tự xuống mode.** Không có ngưỡng token, không có "việc gấp thì hạ mức", không
có heuristic nào để Claude tự chuyển `full` → `lite` hay `full` → `off`. Chỉ một yêu cầu tường
minh của người dùng mới hạ được mức, và mặc định luôn quay về `full` ở request sau.

Lý do không phải là sở thích: hạ mức là hạ tier 1, mà `skills/tdq-conventions/references/soul.md:106`
hỏi đúng câu "việc tôi sắp làm có hạ chất lượng để đổi lấy tốc độ hay token không?" — Claude tự
hạ mức thì trả lời "có", tức là phạm luật gốc. Người dùng hạ mức thì không, vì
`skills/tdq-conventions/references/soul.md:37` đã đặt người dùng ở trên cả tầng luật: khi phá thế
không xong thì hỏi người dùng. `off` vì vậy là **người dùng tạm treo luật**, không bao giờ là
**Claude tự hạ chất lượng**.

## Luồng 3 — Hook thứ sáu: `SubagentStart`

**Quyết định:** thêm một hook thứ sáu bắt sự kiện `SubagentStart` — sự kiện này có thật, nằm
trong 32 sự kiện hook chính thức `[XÁC THỰC]` — bơm câu luật của luồng 1 cộng mức `muc_gat` hiện
tại vào ngữ cảnh mỗi sub-agent. Đây là **lời nhắc, không phải cổng chặn**; câu này phải nằm
nguyên trong mô tả hook, vì hiểu sai nó là hiểu sai toàn bộ luồng.

**Giá phải trả:** một file mới trong thư mục `hooks/scripts/` (ví dụ `subagent_law.py`, dùng
chung tiện ích ở `hooks/scripts/_common.py:1`), cộng một mục thứ sáu trong `hooks/hooks.json:4`
— hiện file đó đăng ký đúng
**5** hook: `hooks/hooks.json:4`, `hooks/hooks.json:14`, `hooks/hooks.json:26`,
`hooks/hooks.json:35`, `hooks/hooks.json:44` `[SUY-CODE]`.

### Lỗ luật cần bịt

Luật hiện **vô hình với sub-agent**. Cả hai hook bơm ngữ cảnh của TDQ chỉ bắn ở đầu session và
đầu mỗi lượt người dùng: `hooks/hooks.json:4` là `SessionStart`, `hooks/hooks.json:14` là
`UserPromptSubmit` `[SUY-CODE]`. Một `tdq-implementer` sinh ra giữa lượt không đi qua cửa nào
trong hai cửa đó, nên nó nhận plan và nhận task nhưng **không** nhận câu luật. Ở mode `subagent`,
đó chính là chỗ phần lớn code thật được viết ra.

### Khuôn in: JSON, không phải `print()` thô

Đây là chỗ **không dùng lại được** khuôn của hai hook hiện có. `hooks/scripts/session_start.py:37`
và `hooks/scripts/prompt_context.py:316` đều in thẳng bằng `print()` `[SUY-CODE]`, và với
`SessionStart` / `UserPromptSubmit` thì stdout thô được nhận làm ngữ cảnh. `SubagentStart` **chỉ**
nhận `hookSpecificOutput.additionalContext`; stdout thô bị bỏ im lặng `[XÁC THỰC]`. Viết hook mới
theo khuôn cũ sẽ ra một hook chạy đúng, exit 0, mà không bơm được gì — kiểu hỏng tệ nhất.

Khuôn phải in:

```json
{"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "<câu luật + mức>"}}
```

### Vì sao là lời nhắc, không phải cổng chặn

Hai lý do, cả hai đều đo được chứ không phải suy đoán:

1. `SubagentStart` là sự kiện **chỉ-ngữ-cảnh**: trả `decision: "block"` ở đây không có tác dụng
   `[XÁC THỰC]`. Không có đường nào để chặn một sub-agent khởi động vì lý do luật.
2. Đường chặn tưởng là có — đặt `PreToolUse` với matcher `Agent` — **không bắn** `[BÊN-THỨ-BA]`
   (issue #69545). Tôi đã ghi giả định sai này của mình vào brief thay vì im lặng bỏ qua, vì nó
   là loại sai dễ lặp lại.

Hệ quả thẳng thắn: luồng 3 **giảm xác suất** sub-agent viết thừa, nó không **cấm** được. Cổng
chặn thật vẫn chỉ có ba cái đang chạy ở `hooks/hooks.json:26`, `hooks/hooks.json:35` và
`hooks/hooks.json:44` `[SUY-CODE]` — xem bảng ở luồng 5.

### Hướng thất bại: fail-open

Hook này lỗi, thiếu python, state hỏng → **exit 0, không bơm gì, để sub-agent chạy tiếp**. Một
hook nhắc luật mà làm chết được lượt implement thì nó đang đổi tier 1 lấy tier 1: luật vào được
thêm một chỗ, đổi lấy nguy cơ cả request đứng. Ngưỡng in cũng phải có trần như hai hook kia
(`hooks/scripts/session_start.py:18` dùng 12 dòng / 600 ký tự), và trần của hook này nên bằng
trần đó chứ không phải bằng độ dài của thân luật — 120 dòng SKILL.md bơm mỗi session là cách
Ponytail làm `[SUY-CODE]`, và đó là cái giá context TDQ cố ý không trả.

## Luồng 4 — Một nguồn chân lý cho mọi host

**Quyết định:** giữ nguyên cơ chế **sinh tự động** đã có trong `scripts/build_portable.py:1`,
thêm **một** đích Cursor. Không bao giờ copy tay thân luật sang host thứ hai.

**Giá phải trả:** một hàm sinh mới cạnh ba hàm đang có, cộng một hằng tên bản giống
`scripts/build_portable.py:204`, `scripts/build_portable.py:321`,
`scripts/build_portable.py:700`. Không file luật nào bị nhân bản trong repo.

### Bốn đích, mỗi đích một dòng

| Đích | Host | Trạng thái | Sinh bởi |
|---|---|---|---|
| `portable_claude/` | Claude Code trong một project | đã có | `scripts/build_portable.py:284` |
| `portable_codex/` + `AGENTS.md` | Codex CLI, và mọi harness chỉ đọc markdown | đã có | `scripts/build_portable.py:617` |
| `antigravity_portable/` | Antigravity CLI (agy) | đã có | `scripts/build_portable.py:937` |
| `.cursor/rules/*.mdc` | Cursor | **cần thêm** | hàm sinh mới |

Đây là chỗ tôi phải sửa chính plan của mình: plan viết "hai đích đã có", số đo thật là **ba**
(`scripts/build_portable.py:284`, `scripts/build_portable.py:617`,
`scripts/build_portable.py:937`) `[SUY-CODE]`. Sửa con số theo file, không sửa file theo plan.
Hệ quả là luồng 4 rẻ hơn tôi tưởng: cơ chế "một nguồn, tự sinh" mà người dùng chốt ở `4a`
**đã tồn tại**, việc còn lại chỉ là thêm một đích.

### Vì sao KHÔNG copy tay — bằng chứng đo được từ chính Ponytail

Ponytail không sinh tự động. Nó **viết tay 9 bản** thân luật rồi kiểm bằng so sánh:
`.agents/rules/`, `.clinerules/`, `.cursor/rules/`, `.github/copilot-instructions.md`,
`.kiro/steering/`, `.openclaw/skills/`, `.qoder/rules/`, `.windsurf/rules/` và `AGENTS.md`
`[SUY-CODE]`. Bản canon là `~/Documents/ponytail/AGENTS.md:1`, khai ở
`~/Documents/ponytail/scripts/check-rule-copies.js:15` `[SUY-CODE]`. Tám bản gọn được so gần
như từng byte (`~/Documents/ponytail/scripts/check-rule-copies.js:19`), nhưng
`skills/ponytail/SKILL.md` **không so byte được** vì nó dài hơn, nên chỉ được canh bằng vài
"câu bất biến" — chính file checker tự gọi đó là "canary, not full equality"
(`~/Documents/ponytail/scripts/check-rule-copies.js:39`) `[SUY-CODE]`.

Và canary đã để lọt thật. Bậc 1 của thang lệch chữ giữa hai bản:

- `~/Documents/ponytail/skills/ponytail/SKILL.md:36` — "Does this need to **exist** at all?"
- `~/Documents/ponytail/AGENTS.md:7` — "Does this need to be **built** at all?"

Hai câu không đồng nghĩa: "tồn tại" loại cả thứ đã có sẵn, "được xây" thì không. Bậc quan trọng
nhất của thang đang có hai nghĩa khác nhau tuỳ host người dùng đang dùng `[SUY-CODE]`.

Đáng chú ý hơn: chính file checker đó đã viết sẵn đường thoát ở
`~/Documents/ponytail/scripts/check-rule-copies.js:42` — "Upgrade path: generate the copies from
SKILL.md if this ever misses a real drift" `[SUY-CODE]`. Drift đó **đã xảy ra**. Nên luồng 4
không phải TDQ nghĩ ra cách hay hơn; nó là TDQ đã ở sẵn trên đường mà Ponytail tự ghi là nên đi.

**Bài học mang vào TDQ:** test so sánh nội dung là điều kiện cần, không phải điều kiện đủ. Bản
nào không so được từng byte thì bản đó sẽ lệch. Vì vậy đích Cursor phải **sinh ra** từ cùng
nguồn, không được là file viết tay kèm một test canh vài câu.

## Luồng 5 — Hợp nhất hướng thất bại

**Quyết định:** ghi hướng thất bại của từng cơ chế thành **một bảng trong thân luật**, thay vì
để mỗi hook tự xử rồi người đọc tự suy. Luật nhắc thì fail-open, cổng chặn thì fail-closed, và
khoá `muc_gat` đọc lỗi thì **fail-closed về `full`**.

**Giá phải trả:** 0 dòng code. Một bảng, đã tính trong giá của luồng 1.

### Bảng hướng thất bại

| Cơ chế | Loại | Hướng khi lỗi | Lý do |
|---|---|---|---|
| Bơm ngữ cảnh đầu session (`hooks/scripts/session_start.py:37`) | nhắc | **fail-open** — không in gì, lượt vẫn chạy | Không bơm được luật là mất một lời nhắc; làm chết session là mất cả request |
| Bơm ngữ cảnh đầu lượt (`hooks/scripts/prompt_context.py:316`) | nhắc | **fail-open** | Như trên; `hooks/scripts/prompt_context.py:165` đã bắt `except Exception` rồi đi tiếp `[SUY-CODE]` |
| Hook thứ sáu cho sub-agent (luồng 3, chưa có) | nhắc | **fail-open** | `SubagentStart` không chặn được kể cả khi muốn `[XÁC THỰC]` |
| Nhắc trên đường sửa file (`hooks/scripts/edit_gate.py:80`) | nhắc | **fail-open** — `permissionDecision: "allow"`, kèm đúng câu "a reminder, not a block" ở `hooks/scripts/_common.py:140` `[SUY-CODE]` | Nhắc sai mà chặn thì agent đứng giữa task |
| Nhắc trên đường chạy lệnh (`hooks/scripts/bash_gate.py:123`) | nhắc | **fail-open** | Toàn bộ `bash_gate` chỉ gọi `remind`/`remind_force`, không gọi `block` `[SUY-CODE]` |
| Cổng chặn sửa file ngoài vùng (`hooks/scripts/edit_gate.py:135`) | **chặn** | **fail-closed** — `permissionDecision: "deny"` ở `hooks/scripts/_common.py:161` `[SUY-CODE]` | Sửa file ngoài vùng được giao là hỏng thật, không phải nhắc |
| Cổng chặn đóng lượt (`hooks/scripts/stop_gate.py:227`) | **chặn** | **fail-closed** — `decision: "block"` `[SUY-CODE]` | Đóng lượt khi plan còn task mở là mất dấu công việc |
| Đọc khoá `muc_gat` (luồng 2, chưa có) | dữ liệu | **fail-closed về `full`** | Xem ngay dưới — đây là dòng quan trọng nhất bảng |

### Vì sao `muc_gat` lỗi thì về `full`, không về `off`

State hỏng, thiếu khoá, file JSON lỗi → mức phải là **`full`**, mức gắt mặc định. Hướng ngược
lại rất dễ viết và rất sai: một `state.json` lỗi sẽ tự tắt luật chất lượng mà không ai ra lệnh,
tức là đúng cái mà luồng 2 vừa cấm — Claude hạ mức không do người dùng yêu cầu. Câu hỏi tự kiểm
ở `skills/tdq-conventions/references/soul.md:106` áp cả cho đường lỗi, không chỉ đường thường.

Nói gọn thành một câu để ghi vào luật: **cơ chế nhắc lỗi thì im lặng đi tiếp; cơ chế chặn lỗi
thì chặn; dữ liệu mức gắt lỗi thì lấy mức gắt nhất đang là mặc định.**

## Cổng duyệt riêng — một câu trong luật gốc

Toàn bộ phương án này chỉ **thêm** luật, trừ **đúng một chỗ** phải **sửa** luật đang có. Luật gốc
quy định ở `skills/tdq-conventions/references/soul.md:4` rằng sửa nó cần người dùng duyệt, nên
chỗ này tách thành một cổng riêng thay vì trộn vào phần duyệt phương án.

**Chỗ duy nhất:** `skills/tdq-build/references/rules/chung.md:22`.

Nguyên văn câu hiện tại (dòng 22–23):

```
- This rule is always on; there is no toggle. The SOLID principles and the 5-question
  checklist in `skills/tdq-conventions/references/clean-code.md` apply at the same time.
```

Nguyên văn câu đề xuất thay:

```
- This rule is always on. The only thing that can turn it off is an explicit user request
  through `muc_gat`; Claude's own judgement never lowers it, and every request starts back
  at `full`. The SOLID principles and the 5-question checklist in
  `skills/tdq-conventions/references/clean-code.md` apply at the same time.
```

**Đổi gì:** bỏ ba chữ "there is no toggle", thay bằng một mệnh đề nói rõ **có** nút tắt nhưng
nút đó nằm trong tay người dùng, và mặc định luôn trở về `full`.

**KHÔNG đổi gì:** thứ tự ba tầng ở `skills/tdq-conventions/references/soul.md:27` giữ nguyên;
luật phá thế ở `skills/tdq-conventions/references/soul.md:34` giữ nguyên; ngưỡng đo được
(cyclomatic ≤ 10 / cognitive ≤ 15) vẫn là sàn không thương lượng ở mọi mức trừ `off`; và câu
"luật này luôn bật" vẫn là câu mở đầu — mức `off` là ngoại lệ do người dùng tuyên, không phải
trạng thái bình thường.

**Vì sao sửa được mà không phạm soul.** Nghe qua thì thêm nút tắt vào một luật "always on" là hạ
tier 1. Nhưng `skills/tdq-conventions/references/soul.md:37` — nhánh cuối của luật phá thế — đã
đặt người dùng ở trên cả tầng luật: hết cách thì hỏi người dùng và ghi lại phán quyết. Nghĩa là
quyền treo luật của người dùng **đã tồn tại trong soul từ trước**; câu sửa này chỉ đặt tên cho
nó (`muc_gat = off`) và ép nó phải tường minh. Điều soul cấm là *Claude* hạ tier 1 — và câu mới
cấm đúng điều đó bằng chữ, chặt hơn câu cũ, vì câu cũ nói "không có nút tắt" trong khi thực tế
người dùng vẫn luôn tắt được bằng cách ra lệnh.

Nếu bạn không duyệt chỗ sửa này: bốn luồng còn lại vẫn chạy được, mức `off` đơn giản là không
tồn tại, và `muc_gat` còn 4 giá trị `lite | full | ultra | review`. Đó là một phương án hợp lệ,
chỉ mất một đường thoát mà chính bạn đã yêu cầu giữ.

## Thứ tự triển khai cho request sau

Xếp theo rẻ → đắt. Cột cuối là câu trả lời thẳng cho "tôi nhận riêng luồng này được không".

| Thứ tự | Luồng | Giá | Phụ thuộc | Nhận riêng được? |
|---|---|---|---|---|
| 1 | Luồng 1 — thân luật | 0 dòng code, 2 file tài liệu luật | không | **Được.** Nó là nền, chạy một mình vẫn đủ nghĩa |
| 2 | Luồng 5 — hướng thất bại | 0 dòng code, 1 bảng | cần 1 | **Được**, nhưng chỉ sau luồng 1 |
| 3 | Cổng duyệt — sửa một câu luật gốc | 1 câu | cần 1 | **Được.** Loại nó thì mất mức `off`, không ảnh hưởng luồng khác |
| 4 | Luồng 4 — đích Cursor | 1 hàm sinh trong script đã có | cần 1 | **Được.** Rẻ vì cơ chế đã tồn tại |
| 5 | Luồng 2 — trục `muc_gat` | 1 khoá state + 1 nhánh hook + nhãn/alias | cần 1, và cần cổng duyệt nếu muốn có `off` | **Được**, nhưng đây là luồng đắt nhất và là luồng duy nhất chạm state |
| 6 | Luồng 3 — hook thứ sáu | 1 file hook + 1 mục `hooks.json` | cần 1; **đẹp nhất là sau 2** để bơm được cả mức | **Được**, nhưng nếu làm trước luồng 2 thì chỉ bơm được câu luật, chưa bơm được mức |

### Ba điều nên làm trước khi bắt đầu request sau

1. **Chốt cổng duyệt luật gốc trước, không chốt cùng lúc với code.** Nếu `off` bị loại thì luồng
   2 nhỏ hơn hẳn (4 giá trị, không cần nhánh "luật đang tắt" ở bất cứ đâu), và luồng 5 bớt một
   dòng bảng. Biết trước thì viết một lần.
2. **Luồng 1 phải xong và người dùng phải đọc qua thân luật trước khi làm luồng 3.** Hook bơm
   một câu luật chưa được duyệt là bơm sai thứ vào mọi sub-agent.
3. **Đo lại trần dòng ngay trước khi sửa `SKILL.md`.** Số 146/150 ở
   `scripts/doc_lint.py:46` đúng vào 2026-09-16; một request khác chen vào giữa là số khác, và
   luật nâng trần ở `skills/tdq-conventions/references/soul.md:101` buộc phải ghi ngày vào
   comment khi nâng.

### Điều phương án này cố ý KHÔNG làm

- **Không** có comment `ponytail:` để khai "trần đã biết" và xin bỏ qua ngưỡng. Người dùng chốt
  `2a`: thang chỉ chọn giữa các cách **đã đạt ngưỡng**, nên một đường vòng qua ngưỡng là đường
  không cần tồn tại.
- **Không** có lệnh kiểu `/ponytail-debt` để liệt kê nợ đã khai. Chưa có nợ nào được khai thì
  chưa có gì để liệt kê — đúng bậc 1 của thang, áp lên chính phương án này.
- **Không** thêm skill thứ chín. `[XÁC THỰC]` Skill không có cờ `alwaysApply`, nên một skill mới
  sẽ chỉ được nạp khi có người gọi tên nó — tức là đúng cái ngược lại với "luật luôn bật".
- **Không** dịch thân luật sang tiếng Việt. Tầng ngôn ngữ đã chốt ở `docs/kien-truc.md:51` giữ
  luật trong `skills/` ở tiếng Anh cố định; tài liệu người dùng đọc — như chính file này — theo
  `doc_lang`.
- **Không** cắt phương án này thành 5 file module. Bậc 1 của thang nói việc chia đó không cần
  tồn tại: ba file đầu ra đã đủ, và spec §2b đã ghi lý do.
