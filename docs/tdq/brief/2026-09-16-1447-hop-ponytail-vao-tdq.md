# Brief — Hợp lối code Ponytail vào TDQ-Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Tin nhắn 1:

> okay vậy tôi đang có idea bổ sung lối code của pony tail là hướng code và development chính
> của tdq-workflow, hãy mở reqeusr phân tích và trả ra phương án đề xuất để combine pony tail
> vào tdq-workfllow luôn nha, combine skill, rule, hook

Tin nhắn 2 (gửi giữa lượt, bổ sung yêu cầu đầu ra):

> và output expet là report và phương án đề xuất

### Đọc lần đầu

**Mục tiêu.** Biến bộ luật chống-xây-thừa của Ponytail (lazy senior developer: thang 7 bậc,
YAGNI, stdlib/native trước, "lazy code without its check is unfinished") thành **hướng code và
development chính** của TDQ-Workflow — không phải một plugin gắn thêm bên cạnh, mà là mặc định
của mọi lượt implement.

**Phạm vi đoán (3 mức tích hợp người dùng nêu tên).**
- **skill** — Ponytail có một nguồn chân lý `skills/ponytail/SKILL.md` (121 dòng). TDQ đang có 8
  skill (`tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-conventions`, `tdq-status`,
  `tdq-check-status`, `tdq-lsp-setup`). Câu hỏi: thêm skill thứ 9 hay nhúng luật vào
  `tdq-conventions` (nơi mọi skill đều nạp)?
- **rule** — TDQ đã có tầng luật ngôn ngữ `tdq-build/references/rules/` (`chung.md` + một file
  mỗi ngôn ngữ) nạp đúng lúc sắp sửa file. Đây là chỗ khớp tự nhiên nhất cho thang 7 bậc.
- **hook** — TDQ có 5 hook thật trong `hooks/hooks.json`: `SessionStart` → `session_start.py`,
  `UserPromptSubmit` → `prompt_context.py`, `PreToolUse` (matcher `Edit|Write|MultiEdit|
  NotebookEdit`) → `edit_gate.py`, `PreToolUse` (matcher `Bash`) → `bash_gate.py`, `Stop` →
  `stop_gate.py`. Ponytail dùng 3 hook (`SessionStart`, `UserPromptSubmit`, `SubagentStart`) —
  **giao nhau ở 2 hook đầu**, nên phải quyết chèn thêm hay gộp vào script đang có.

**Đầu ra người dùng mong đợi (đã chốt ở tin nhắn 2).** Một *report* + một *phương án đề xuất* —
tức yêu cầu này giao ra tài liệu quyết định, không phải giao ra code chạy được ngay.

**Điểm chưa rõ (đưa vào vòng interview, không tự đoán).**
1. Request này dừng ở phương án, hay duyệt phương án rồi thực thi luôn trong cùng request?
2. Có giữ 5 mode của Ponytail (`off/lite/full/ultra/review`) không, và mode đó quan hệ thế nào
   với `implement_mode` (`main/subagent/codex`) đang có của TDQ? Hai trục khác nhau, dễ đụng tên.
3. Hướng xử lý xung đột triết lý: Ponytail **fail open** (không bao giờ chặn lượt), TDQ
   **fail closed** (Stop gate từ chối kết lượt khi chưa ghi working log). Khi luật Ponytail
   nói "ít code nhất" mà DoD của TDQ đòi "mỗi task một unit test" thì bên nào thắng?
4. Có sao chép luật ra các file rule đa nền tảng như Ponytail làm (7 bản copy có script canh
   trôi) hay chỉ giữ một bản trong plugin TDQ?
5. Có lấy cả cơ chế `ponytail:` comment + lệnh gom nợ (`/ponytail-debt`) không?

### Nền tri thức đã có, không phải làm lại

Request trước (`2026-09-16-1129-phan-tich-repo-ponytail`, đã xong, QC 4/4 PASS) đã phân tích
Ponytail v4.10.0 tới mức `đường-dẫn:dòng`, 38/38 trích dẫn kiểm được bằng máy, và có sẵn phần
"§6 So sánh rộng với TDQ-Workflow" gồm bảng 12 chặng vòng đời + kết luận hai bên trực giao.
Nguồn: `docs/tdq/research/2026-09-16-1129-phan-tich-repo-ponytail.md`. Request này **đứng trên**
tài liệu đó, không đọc lại repo Ponytail từ đầu.

### Kiểm lớp tìm kiếm (bước 1b)

- `python3 scripts/tdq_lsp.py check` → **7/7 bậc ĐẠT**, 0 cảnh báo.
- Kiểm hiệu ứng (bắt buộc, vì 7 bậc chỉ chứng minh "có tồn tại"): ký hiệu `read_payload`, định
  nghĩa `hooks/scripts/_common.py:78`.
  - `mcp__lsp__find_references` → **11 trích dẫn**.
  - `grep -rn "read_payload" --include="*.py" scripts/ hooks/` → **11 lần, trên 6 file riêng biệt**.
  - **PASS** — LSP phủ 11/11, không sót file. Index trả lời được liên-file, dùng LSP bình thường
    cho cả request này.
  - Lưu ý cách đếm: `find_references` in ra namespace (`hooks/scripts.ref_N`) chứ không in đường
    dẫn, nên đối chiếu bằng **số lần trích**, không đếm dòng namespace là số file.

## Hiểu & kiến thức

### Năng lực dùng được (B0)

`skill_inventory.py --loc "ponytail luật code chống xây thừa yagni skill rule hook tích hợp"`
→ giữ 8, ẩn 2. Không có skill nào sẵn làm được việc này, nên phán quyết là DÙNG LẠI hạ tầng
chứ không viết mới hạ tầng.

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-conventions` | plugin:tdq-workflow | **DÙNG** | Mọi skill đều nạp nó đầu tiên → chỗ duy nhất đặt luật mà mọi phase đều thấy |
| `tdq-build` | plugin:tdq-workflow | **DÙNG** | Sở hữu tầng `references/rules/`, và là nơi luật code thực sự được thi hành lúc implement |
| `tdq-spec`, `tdq-plan` | plugin:tdq-workflow | **DÙNG** | Đầu ra "phương án đề xuất" của request này chính là spec + plan |
| `tdq-intake` | plugin:tdq-workflow | **DÙNG** | Đang chạy |
| `tdq-lsp-setup` | plugin:tdq-workflow | **DÙNG** | Đã chạy kiểm 7 bậc + kiểm hiệu ứng ở bước 1b |
| `tdq-status`, `tdq-check-status` | plugin:tdq-workflow | **BỎ** | Chỉ đọc trạng thái, không liên quan tầng luật |
| `tdq-reviewer` (agent) | plugin:tdq-workflow | **CÓ THỂ** | Chỉ gọi nếu người dùng muốn soi spec sâu |
| `graphify` | user | **BỎ** | Request chưa đổi code, câu hỏi không phải về liên kết đồ thị |

### Code hiện có (B1) — đo thật, không đoán

**Tầng luật TDQ đã tồn tại, không phải đất trống.** Đây là điều chỉnh lớn nhất so với đọc lần
đầu: TDQ đã có bộ luật code riêng, nên việc phải làm là *hợp nhất*, không phải *thêm tầng thứ hai*.

| Tầng | File | Dòng | Nạp khi nào | Nội dung đang có |
|---|---|---|---|---|
| Luật gốc | `skills/tdq-conventions/references/soul.md` | 110 | Khi viết/sửa luật, template, script | 4 nguyên tắc + luật phá hoà (tie-break) + luật xếp tầng |
| Chuẩn mực thường trực | `skills/tdq-conventions/references/clean-code.md` | 116 | Mỗi lần viết/sửa code | 5 nguyên tắc SOLID, 2 cột đọc (có class / thuần hàm), tự kiểm 5 câu |
| Luật chung mọi ngôn ngữ | `skills/tdq-build/references/rules/chung.md` | 78 | Trước mỗi file ngôn ngữ | Nhóm Intentionality (59,6% lỗi LLM), ngưỡng đo được, checklist OWASP |
| Chỉ mục ngôn ngữ | `skills/tdq-build/references/rules/index.md` | 69 | Trước khi gõ code | Bảng 8 ngôn ngữ + 3 tầng nạp |
| Luật theo ngôn ngữ | `rules/{python,typescript-js,go,rust,cpp,csharp,html}.md` | — | Đúng một file theo đuôi file đang sửa | Ngưỡng riêng + lệnh linter |

**Hai ràng buộc từ `soul.md` mà bản Ponytail gốc KHÔNG thoả** — đây là lý do không thể bê
nguyên văn 121 dòng SKILL.md vào:

1. `soul.md:39-46` (nguyên tắc 3 "viết cho model yếu nhất"): mọi luật phải đủ 3 mục
   `## When it applies` / `## What to do` / `## Self-check`, và chỗ nào dễ đọc sai phải có ví dụ
   RIGHT/WRONG. SKILL.md của Ponytail viết theo văn phong tuyên ngôn, không có khuôn này.
   Khuôn đó **được máy kiểm**: `tests/test_clean_code_rule.py:70-82` (`class KhuonFileLuat`)
   ép đủ 3 mục + dòng `Soul:`. Luật mới thiếu khuôn là test đỏ, không phải góp ý.
2. `soul.md:99-102` (luật xếp tầng): luật tier 1 và tier 2 **phải** nằm trong body skill nạp mỗi
   lượt; chỉ tier 3 mới được đẩy vào file reference. Luật chống-xây-thừa sửa *tính đúng của đầu
   ra* → tier 1 (`soul.md:90-94`) → **không được** nằm trong reference file mà không có neo ở body.

**Trần cứng của tầng hook — điểm chặn quyết định.** Ponytail bơm cả thân luật qua hook mỗi lượt;
TDQ không có chỗ cho việc đó:

| Hook TDQ | File | Trần | Ponytail dùng hook tương ứng để làm gì |
|---|---|---|---|
| `SessionStart` | `hooks/scripts/session_start.py:18-19` | **12 dòng / 600 ký tự** | Bơm TOÀN BỘ thân skill theo mode (`ponytail-activate.js:61`) |
| `UserPromptSubmit` | `hooks/scripts/prompt_context.py:28-29` | **3 dòng / 240 ký tự** | Phân tích lệnh `/ponytail …`, đổi mode |
| `PreToolUse` (Edit/Write) | `hooks/scripts/edit_gate.py` | 230 dòng logic | — (Ponytail không có) |
| `PreToolUse` (Bash) | `hooks/scripts/bash_gate.py` | — | — |
| `Stop` | `hooks/scripts/stop_gate.py` | — | — (Ponytail không có; đây là chỗ TDQ fail-closed) |

→ **Kết luận cứng:** tầng hook của TDQ chở được *con trỏ* và *lời nhắc*, không chở được *thân
luật*. 121 dòng không nhét vào 240 ký tự. Thân luật buộc phải ở tầng skill/rule; hook chỉ có
quyền nhắc và đổi mode.

**Hai cơ chế TDQ đã có, giải sẵn hai vấn đề Ponytail phải tự giải:**
- Chống nhắc-lải-nhải: `prompt_context.py:304-308` (`_compact`) tự thu dòng lặp thành
  `(same as last turn — unchanged)`. Ponytail phải dùng file cờ `.ponytail-statusline-nudged`.
- Trần ngân sách ngữ cảnh có số đo, đúng tier 3 của soul.

**Hai chỗ thêm luật là phải trả giá, đã đo:**
- `scripts/doc_lint.py:35-49` — `SKILL_LINE_LIMITS` chặn số dòng mỗi skill (R6). Thêm luật vào
  body skill = phải nâng trần kèm comment ghi ngày + lý do (khuôn đã có sẵn ở `:36-49`).
- `skills/tdq-conventions/references/reminder-codes.md:13` — "The five codes (**closed list**)".
  Thêm mã hook kiểu `[TDQ:PONYTAIL]` là **mở một danh sách đã đóng**.

### Hồ sơ kiến trúc (B1 bổ sung) — ba ràng buộc tôi suýt bỏ sót

`docs/kien-truc.md` có sẵn (sinh 2026-08-15). Trạng thái dòng 3: **NHÁP, chờ user chốt** → các
dòng mô tả là gợi ý; nhưng mục `## Đã chốt` là quyết định đã đóng, có ngày. Ba chỗ đổi phương án:

1. **Cơ chế "một nguồn, sinh tự động" ĐÃ TỒN TẠI — mặt B gần như không phải viết mới.**
   `kien-truc.md:13` + `scripts/build_portable.py` đã sinh sẵn hai đích:
   `portable_claude/` (`.claude/skills`, `.claude/agents`, `hooks/` — `build_portable.py:11,285`)
   và `portable_codex/` kèm **`AGENTS.md`** (`:17,618,681`). Tức 2 trong 3 đích người dùng chọn ở
   H8 đã có máy sinh; **chỉ thiếu Cursor**. → Mặt B co từ "viết script sinh + test canh trôi" xuống
   "thêm một đích vào script đã có". Đây đúng bậc 1 của thang Ponytail: việc này phần lớn không cần
   tồn tại.
2. **File code mới bắt buộc nằm trong `scripts/` hoặc `hooks/`** (`kien-truc.md:26`) — thư mục
   khác bị `.graphifyignore` loại nên đồ thị không thấy. Hook thứ 6 đặt ở `hooks/scripts/`, đúng chỗ.
3. **Thân luật phải viết TIẾNG ANH, không phải tiếng Việt** (`kien-truc.md:51-55`, chốt 2026-08-22):
   luật trong `skills/` viết tiếng Anh cố định, `scripts/i18n_check.py` gác tầng đó; chỉ tài liệu
   sinh cho người dùng mới theo `doc_lang=vi`. → Thuận lợi: SKILL.md của Ponytail vốn đã tiếng Anh,
   nên phần dịch bằng không. Nhưng spec/plan/report của request này vẫn tiếng Việt.

### Xung đột thật giữa hai bộ luật (không làm mềm)

| # | Ponytail nói | TDQ nói | Mức |
|---|---|---|---|
| 1 | "No unrequested abstractions", "Fewest files possible" (`SKILL.md:58-61`) | SRP: một hàm làm đúng một việc, nhiều việc → **tách** (`clean-code.md:55`) | **Xung đột hướng** — một bên dồn lại, một bên tách ra |
| 2 | "ONE runnable check, no frameworks, no fixtures" (`SKILL.md:107-112`) | Mỗi task một unit test, red→green, mỗi dòng DoD một lệnh kiểm | **Xung đột mức** — TDQ đòi nhiều hơn |
| 3 | Rung 1 YAGNI: "speculative need = skip it" (`SKILL.md:36`) | Yêu cầu thường trực: sản phẩm build ra **luôn** có log service bật mặc định | **Xung đột trực tiếp** — log service là tính năng bị YAGNI chất vấn |
| 4 | **Fail open** — hook không bao giờ chặn lượt (`ponytail-subagent.js`, mọi nhánh lỗi đều bơm) | **Fail closed** — Stop gate từ chối kết lượt khi chưa ghi working log (`reminder-codes.md:23-27`) | **Ngược hướng thiết kế** |
| 5 | "Output: code first, tối đa 3 dòng, no essays" (`SKILL.md:66-73`) | spec/plan/qc/report cho mỗi request | **KHÔNG xung đột** — `SKILL.md:72-73` đã tự trừ: giải thích người dùng *yêu cầu* (report, walkthrough) không tính là nợ |

**Luật phá hoà của soul đã có sẵn đáp án cho xung đột 1 và 2** (`soul.md:34-37`): cùng tier thì
luật nào **kiểm được bằng lệnh** sẽ thắng. Ngưỡng `cyclomatic ≤ 10 / cognitive ≤ 15`
(`chung.md:37-38`) kiểm được bằng lệnh; "ít file nhất" không. Nên theo luật hiện hành, thang
Ponytail **không được** dùng để bác một ngưỡng đo được — nó chọn phương án trong số các phương án
đều đạt ngưỡng. Điểm này cần người dùng xác nhận vì nó định nghĩa toàn bộ sức mạnh của bộ luật mới.

### Research (B2) — cơ chế thật của Claude Code

Đầy đủ kèm nguồn và nhãn mức tin cậy: `docs/tdq/research/2026-09-16-1447-hop-ponytail-vao-tdq.md`.
Bốn điều đổi thiết kế, xếp theo mức tác động:

1. **`SubagentStart` có thật, và TDQ đang thiếu nó — lỗ hổng lớn nhất.** [XÁC THỰC, docs]
   Claude Code có 32 hook event; TDQ dùng 5. Không có `SubagentStart`, bộ luật **vô hình với
   `tdq-implementer`** — chính con agent viết code trong mode `subagent`. Nghĩa là dù nhúng luật
   xong, mode implement chủ lực của TDQ vẫn code không theo luật. Ponytail đã phải mở issue #252
   để bịt đúng lỗ này.
2. **`SubagentStart` KHÔNG nhận stdout thô** [XÁC THỰC, docs + `ponytail-runtime.js:123-129`] —
   bắt buộc in JSON `hookSpecificOutput`, không thì bị drop **im lặng**. Cả hai hook TDQ hiện tại
   đều dùng `print(text)` thô (`session_start.py:37`, `prompt_context.py:323`) nên không copy
   khuôn đó sang được.
3. **Nơi đặt luật luôn-bật là `.claude/rules/*.md`, KHÔNG phải skill.** [XÁC THỰC, docs]
   Docs nói thẳng skill *"only load when you invoke them or when Claude determines they're
   relevant"*; không có field `alwaysApply`. Rule không có `paths` → nạp mỗi phiên ngang
   `CLAUDE.md`; rule **có `paths:` glob** → chỉ nạp khi Claude chạm file khớp — đúng khuôn "luật
   code chỉ bật khi đang viết code", và docs nói mục đích là *"reducing noise and saving context"*.
   → Sửa lại đọc lần đầu của tôi: câu hỏi "skill thứ 9 hay nhúng vào `tdq-conventions`" là **câu
   hỏi sai**. Thân luật thuộc `.claude/rules/`; skill chỉ giữ quy trình tra cứu sâu.
4. **Giả định của tôi bị phủ định: `PreToolUse` matcher `Task` không dùng được.** Tool sinh
   sub-agent nay tên `Agent` (tôi tự xác nhận: nó có trong tool-list của chính phiên này), và
   `PreToolUse(Agent)` **không fire** [BÊN-THỨ-BA, issue #69545]. Mọi thứ thuộc vòng đời sub-agent
   phải đi qua `SubagentStart`/`SubagentStop`.

Hai giới hạn phải tôn trọng:
- **Luật dài = luật không tồn tại.** Vượt ~10.000 ký tự, nội dung bị đẩy ra file tạm, hội thoại
  chỉ còn đường dẫn + ~500 ký tự preview; Sonnet 4.6 được ghi nhận **không bao giờ** Read file đó
  [BÊN-THỨ-BA, issue #51537/#65385]. Con số 10.000 **không có trong tài liệu chính thức** → nếu
  phương án dựa vào nó thì phải có một task tự benchmark, không được tin suông.
- **Rule mâu thuẫn → Claude "pick one arbitrarily"** [XÁC THỰC, docs]. Nên nếu luật vào cả
  `.claude/rules/` và hook injection, hook **phải phát hiện rule đã có và rút lui** (đúng pattern
  `cursorRulePath()` của Ponytail).

Hai thứ TDQ **không cần phát minh lại**: cơ chế mode (đã có `state.json` + `tdq_state.py`, chín
hơn flag file global của Ponytail — vốn còn lỗi hai phiên song song đá nhau vì không gắn
`session_id`), và chỗ chặn cứng (đã có `edit_gate.py`/`bash_gate.py`; `SubagentStart` là
*context only*, `decision:"block"` bị bỏ qua nên không chặn được gì).

### Phạm vi đã chốt

- Mặt CHỌN: bảo trì một-nguồn-chân-lý (A) · mở rộng đa nền tảng (B) · mức gắt chọn được (C) ·
  hướng thất bại fail-open/fail-closed (D) · bịt lỗ `SubagentStart` (F)
- Mặt LOẠI: không mặt nào bị loại — người dùng chọn `1abcdf`, tức bỏ phương án "chỉ cần chạy được"
- Bối cảnh: bộ luật áp cho **mọi project mà plugin TDQ chạy** · giữ **đủ 5 mode** như Ponytail
  (`off/lite/full/ultra/review`) · request dừng ở **phương án** (spec + plan + report), việc sửa
  code thật mở request riêng
- Mức đầu tư suy ra: **đầy đủ** — vì luật áp cho mọi project (không biết trước ngôn ngữ/khung),
  sửa vào chính tầng luật gốc của workflow, và có mặt đa nền tảng

## Hỏi đáp

### Vòng 1 — scope

**H1. Request bao quanh những mặt nào?** → `1abcdf`: chọn cả 5 mặt A+B+C+D+F, bỏ E.

**H2. Bộ luật áp cho code nào?** → `2a`: mọi project mà plugin TDQ chạy.
*Hệ quả:* luật không được giả định ngôn ngữ; phải đi qua tầng `rules/index.md` đã có (8 ngôn ngữ
+ đường cho ngôn ngữ ngoài bảng theo `them-ngon-ngu.md`).

**H3. Giữ mấy mode?** → `3c`: đủ 5 mode như Ponytail, **kể cả `off`**.
*Hệ quả bắt buộc:* `chung.md:22` hiện ghi luật chất lượng *"always on; there is no toggle"*, và
`clean-code.md:5-7` gọi clean code là "standing behaviour". Cho phép `off` là **sửa luật đang
có** → cần định nghĩa chính xác `off` tắt cái gì (câu C1 vòng 2), và theo `soul.md:4` việc sửa
luật gốc phải do người dùng duyệt.

**H4. Request dừng ở đâu?** → `4a`: dừng ở phương án — spec + plan + report. Sửa code thật (luật,
hook, test) mở thành request riêng.
*Hệ quả:* plan của request này là plan **viết tài liệu**, DoD chấm trên tài liệu; không có task
nào sửa `hooks/` hay `rules/` trong request này.

### Chốt không cần hỏi — log service vs YAGNI (xung đột #3)

Xung đột #3 trong bảng trên **tự tan**, không cần người dùng phân xử: Ponytail đã tự trừ
`SKILL.md:92-95` — "anything explicitly requested" thuộc vùng không-được-đơn-giản-hoá — và
"sản phẩm build ra luôn có log service bật mặc định" là yêu cầu thường trực người dùng đã đặt.
→ Phán quyết: log service vào **danh sách vùng cấm đơn giản hoá**, thang 7 bậc không được bác nó.
Ghi lại ở đây để không phải mở lại tranh luận này ở phase spec.

### Vòng 2 — chi tiết

Nguyên văn câu trả lời: `1b nhưng mặc định ko tắt trừ khi người dùng yêu cầu, default mode là
full 2A 3A 4A`.

**H5. Mode `off` được phép tắt cái gì?** → `1b` + lan can: `off` tắt **cả** thang 7 bậc **và**
luật chất lượng TDQ, nhưng **không bao giờ tự bật** — chỉ khi người dùng yêu cầu tường minh.
Mode mặc định là **`full`**.

*Vì sao lan can đó cứu được chỗ va với soul, nói rõ chứ không làm mềm:* `soul.md:34-37` khi hai
luật cùng tier không phân xử được thì **hỏi người dùng** — tức người dùng vốn đã đứng trên bộ
luật. Nên `off` không phải "Claude được phép hạ chất lượng" (cái đó soul cấm), mà là "người dùng
dùng quyền của mình để tạm treo luật".

*Câu sửa `chung.md:22` vì vậy hẹp lại được, và đây là câu chính xác sẽ đề xuất ở spec:* luật vẫn
always-on; thứ duy nhất tắt được nó là một yêu cầu tường minh của người dùng (mode `off`), không
bao giờ là phán đoán của Claude. → **Vẫn là sửa luật gốc, vẫn cần bạn duyệt riêng ở phase spec.**

*Hệ quả kỹ thuật đã đo:* khoá state mới **không được** trùng `implement_mode` — khoá đó tồn tại
thật ở `scripts/tdq_state.py:186`, kèm `MODE_LABELS`/`MODE_ALIASES` (`:56,65`) cho trục
`main/subagent/codex`. Hai trục khác nhau hoàn toàn. Tên đề xuất: **`muc_gat`**, miền giá trị
`off|lite|full|ultra|review`, mặc định `full` — đặt cạnh `loai_request`/`nhanh_goc` cho đồng bộ
lối đặt tên.

**H6. Thang 7 bậc mạnh tới đâu so với ngưỡng đo được?** → `2a`: thang **chỉ được chọn giữa những
phương án đã đạt ngưỡng**. Ngưỡng `cyclomatic ≤ 10 / cognitive ≤ 15` (`chung.md:37-38`) là sàn
không thương lượng; thang quyết cái nào trong số đạt sàn thì đơn giản hơn.
*Hệ quả:* **không sửa `soul.md:34-37`.** Luật phá hoà của soul giữ nguyên hiệu lực, và xung đột
#1/#2 trong bảng trên được xử bằng chính luật đang có. Bộ luật Ponytail vào TDQ ở vai *bộ chọn
phương án*, không phải *bộ bác ngưỡng*.

**H7. SOLID (tách hàm) vs "ít file nhất"?** → `3a`: hai lượt **có thứ tự** — thang chạy trước và
quyết *cái này có nên tồn tại không*; SOLID chạy sau và quyết *cái còn sống thì hình dạng thế nào*.
*Hệ quả:* **không sửa `clean-code.md:55`** (dòng SRP), chỉ thêm một câu về thứ tự hai lượt. Đây là
phương án rẻ nhất trong ba phương án: không dòng luật nào đang có bị viết lại.

**H8. Xuất ra nền tảng khác: sinh tự động hay copy tay, bao nhiêu đích?** → `4a`: **một nguồn duy
nhất, các bản kia SINH tự động** bằng script + test so nội dung. Ba đích: `.claude/rules/` ·
Cursor · `AGENTS.md` (Codex/Copilot).
*Hệ quả:* không lặp lại lối 7-bản-copy-tay của Ponytail (`scripts/check-rule-copies.js` mà chính
nó chú thích `// ponytail: canary, not full equality` — tức tự nhận chỉ bắt được trôi, không ngăn
được trôi). Trôi trở thành *không thể xảy ra*, không phải *phát hiện được*.

### Tổng kết interview — bao nhiêu luật gốc phải sửa

Sau vòng 2, danh sách thay đổi vào luật gốc **co lại còn đúng một chỗ**:

| Luật gốc | Có sửa? | Vì sao |
|---|---|---|
| `soul.md:34-37` (luật phá hoà) | **KHÔNG** | H6=2a giữ ngưỡng làm sàn → luật phá hoà hiện hành đã đủ xử |
| `clean-code.md:55` (SRP) | **KHÔNG** | H7=3a chỉ thêm thứ tự hai lượt, không viết lại dòng SRP |
| `chung.md:22` ("no toggle") | **CÓ — một câu** | H5=1b cho phép `off`, nhưng hẹp: chỉ người dùng tắt được |
| `reminder-codes.md:13` (danh sách 5 mã đóng) | **QUYẾT Ở SPEC** | Chỉ mở nếu phương án cần một mã hook mới; nếu hook chỉ nhắc qua mã `TDQ:NEXT` sẵn có thì không phải mở |

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| `analyze` | **CÓ** (đang chạy) | B0+B1+B2 xong, interview 2 vòng xong, 0 câu treo |
| `spec` | **CÓ** | Đầu ra người dùng yêu cầu ("phương án đề xuất") chính là spec — phương án tích hợp 3 tầng skill/rule/hook + câu sửa `chung.md:22` để bạn duyệt riêng |
| `plan` | **CÓ** | H4=4a → plan **viết tài liệu**, mỗi task là một phần của report/phương án, DoD chấm trên tài liệu |
| `implement` | **CÓ** | Nhưng "implement" ở đây = viết file report; **không** sửa `hooks/`, `rules/`, `soul.md` — đó là request sau |
| `qc` | **CÓ** | Mỗi dòng DoD một lệnh kiểm; riêng mọi trích dẫn `đường-dẫn:dòng` phải kiểm được bằng máy như request trước |
| `report` | **CÓ** | ≤50 dòng, là đầu ra thứ hai người dùng nêu tên |
| Sửa code thật (luật/hook/test) | **BỎ khỏi request này** | H4=4a nói rõ: dừng ở phương án; mở request riêng sau khi bạn duyệt phương án |

**Các luồng tính năng phương án sẽ gồm** (một dòng mỗi luồng, để spec không đi lệch):
1. Luồng *thân luật* — Ponytail hoá thành một file luật đúng khuôn 3 mục của `soul.md:39-46`, đặt
   ở tầng `.claude/rules/` có `paths:` glob, hợp nhất với `chung.md` thay vì dựng tầng thứ hai.
2. Luồng *mức gắt* — `muc_gat` 5 giá trị, mặc định `full`, chỉ người dùng hạ được xuống `off`.
3. Luồng *bịt lỗ sub-agent* — hook thứ 6 `SubagentStart`, in JSON `hookSpecificOutput`, fail-open.
4. Luồng *một nguồn chân lý* — **mở rộng `scripts/build_portable.py`** (đã sinh sẵn
   `portable_claude/` + `AGENTS.md`), chỉ thêm đích Cursor; không viết script sinh mới.
5. Luồng *hợp nhất hướng thất bại* — chỗ nào fail-open (nhắc luật), chỗ nào fail-closed (Stop gate).

### Kiểm cổng (bước 6)

| Câu cổng | Trả lời |
|---|---|
| Phạm vi cuối đã rõ: làm ra cái gì, cái gì mới, đầu ra chính xác là gì? | **RÕ.** Đầu ra là tài liệu: spec (phương án tích hợp 3 tầng skill/rule/hook, 5 luồng ở trên) + plan + report ≤50 dòng. Cái "mới" duy nhất được đề xuất sửa vào luật gốc là **một câu** ở `chung.md:22`, và nó sẽ được trình riêng để bạn duyệt. Không có file `hooks/`, `rules/`, `soul.md` nào bị sửa trong request này (H4=4a). |
| Có cần model / tải về / cài đặt gì không? | **KHÔNG.** 7/7 bậc LSP đã ĐẠT + kiểm hiệu ứng PASS ở bước 1b; `build_portable.py`, `doc_lint.py`, `i18n_check.py` đều có sẵn trong repo; request chỉ viết `.md`. |
| Phạm vi QC/test/validate đã định chưa? | **ĐÃ.** QC chấm trên tài liệu, mỗi dòng DoD một lệnh chạy được: (a) `doc_lint.py --pair <spec> <plan>` exit 0; (b) mọi trích dẫn `đường-dẫn:dòng` trong report kiểm được bằng máy — mở file, so số dòng thật, đúng trình kiểm đã dùng ở request trước (`check_citations.py`, 38/38); (c) mọi khẳng định về cơ chế Claude Code mang nhãn `[XÁC THỰC]`/`[SUY-CODE]`/`[BÊN-THỨ-BA]`; (d) phương án không chứa bước nào sửa code thật. |

**Kết luận cổng: ĐẠT cả 3 — không còn câu hỏi nào đổi được đầu ra.** Sang phase `spec`.
