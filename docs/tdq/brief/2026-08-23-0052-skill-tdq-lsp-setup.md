# BRIEF — Skill `tdq-lsp-setup`: nhúng agent-lsp vào bộ workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ trong document của tôi có một project agent-lsp tôi muốn mở request tạo một
> skill tdq-lsp-setup trong skill đó sẽ có đủ link tới repo github
> https://github.com/blackwell-systems/agent-lsp cũng là repo mà đã clone về trong document,
> skill sẽ biết check xem agent lsp đã cài chưa nếu chưa thì xin quyền hoặc hướng dẫn người
> dùng install tiếp theo check config mcp của agent code đã có chưa nếu chưa thì setup mcp ,
> và có đủ ngôn ngữ agent lsp support nhằm mục đích nhúng nó vào bộ workflow và khi intake thì
> sẽ check project dùng ngôn ngữ gì đã có language server cần thiết cho ngôn ngữ đó chưua nếu
> chưa, claude code sẽ đề xuất người dùng cho phép install trên máy và khi đã đủ thì claude
> code sẽ ưu tiên dùng agent lsp để sreach funtion nhằm tối đa hóa chất lượng sreach, updeate,
> code, refactor project. và trong quá trình làm việc của workflow sẽ ưu tiên dùng agent lsp
> khi có thể để đảm bảo đủ ngữ nghĩa sreach của project từ đó tổ chức và viết project tối ưu
> hơn

### Đọc lần đầu

**Mục tiêu:** biến agent-lsp từ một binary nằm rời trên máy thành một mắt xích chính thức của
bộ workflow TDQ, để mọi thao tác tìm/sửa/refactor code đi qua ngữ nghĩa LSP thay vì grep chuỗi.

**Phạm vi đoán:** một skill mới `skills/tdq-lsp-setup/` gồm thang kiểm 4 bậc (binary → MCP →
language server theo ngôn ngữ project → quyền tool), bảng 30 ngôn ngữ kèm lệnh cài, và các
móc nối vào `tdq-intake` (kiểm lúc mở request) cùng `tdq-build` (ưu tiên dùng khi làm việc).

**Chỗ chưa rõ:** mức tự động của việc cài đặt · phạm vi "ưu tiên dùng" là bắt buộc hay khuyến
nghị · quan hệ với `lumen` (MCP semantic search đang bật sẵn) · sửa file luật ngoài repo hay không.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Có sẵn? | Dùng vào việc gì |
|---|---|---|
| `agent-lsp doctor` | CÓ, chạy được ngay | Bộ kiểm language server sẵn có — KHÔNG tự viết lại |
| `agent-lsp init` | CÓ | Tự ghi MCP config + rule file, có cờ `--non-interactive` |
| `claude mcp list` | CÓ | Kiểm MCP đã đăng ký chưa |
| Repo clone tại máy | CÓ | Đọc `docs/reference/language-support.md` cho bảng 30 ngôn ngữ |
| `skills/tdq-*` | CÓ | Khuôn skill để viết theo |

### Phát hiện then chốt

1. **Đường dẫn repo user nói chưa đúng.** Repo KHÔNG ở `~/Documents/agent-lsp` mà ở
   `~/Documents/Add_on_for_claude/agent-lsp`, remote đúng là
   `https://github.com/blackwell-systems/agent-lsp.git`, HEAD `ca8b32d` = release v0.18.0.
2. **Binary ĐÃ cài rồi**: `/usr/local/bin/agent-lsp`, version `0.18.0`. Nên nhánh "chưa cài →
   xin quyền cài" là nhánh phòng xa cho máy khác, không phải việc phải làm ngay trên máy này.
3. **MCP thì CHƯA.** `claude mcp list` liệt kê 15 server, KHÔNG có `lsp`. Đây là khoảng trống
   thật và là thứ chặn mọi việc còn lại — không có MCP thì 65 tool không tồn tại với Claude.
4. **Language server gần như trống.** `agent-lsp doctor` chỉ thấy `clangd` (c, cpp); thiếu 14
   server còn lại. Đáng nói nhất: **`pyright-langserver` cho Python chưa cài, mà chính
   TDQWorkflow là project Python** — nghĩa là bật xong MCP vẫn chưa dùng được cho repo này.
5. **`agent-lsp init` đã làm sẵn bước ghi MCP config**, kể cả chế độ không tương tác. Skill nên
   GỌI nó chứ không tự chế file config — tự ghi là tự nhận nợ bảo trì khi format đổi.
6. **Cần bước quyền tool riêng**: README bước 6 yêu cầu thêm `mcp__lsp__*` vào allow list của
   `~/.claude/settings.json`, nếu không mỗi lần gọi tool là một lần hỏi quyền.
7. **Trùng vai với `lumen`**: MCP `lumen` (semantic search) đang bật và hook `PreToolUse` hiện
   đã giục dùng `lumen` thay Grep. Thêm agent-lsp mà không phân vai thì hai bộ giục ngược nhau.
8. **30 ngôn ngữ**: Go, Python, TypeScript, Rust, Java, C, C++, C#, Ruby, PHP, Kotlin, Swift,
   Scala, Zig, Lua, Elixir, Gleam, Clojure, Dart, Terraform, Nix, Prisma, SQL, MongoDB,
   JavaScript, YAML, JSON, Dockerfile, CSS, HTML.

### Nghiên cứu ngoài

**BỎ** — không có ẩn số ngoài. Repo đã clone tại máy nên README và
`docs/reference/language-support.md` là nguồn gốc, không phải nguồn thứ cấp; `doctor` và
`init` chạy thử trực tiếp được nên mọi khẳng định đều kiểm bằng lệnh, không cần search.

### Ràng buộc từ hồ sơ kiến trúc

Đọc `docs/kien-truc.md` (trạng thái NHÁP, chưa chốt) — ba ràng buộc chạm thẳng vào việc này:

- **`skills/` là văn bản thuần, không chạy được.** Skill chỉ được NHẮC TÊN lệnh của
  `scripts/`, cấm chép nội dung script vào skill. Nên phần "kiểm 4 bậc" nếu cần logic thì
  phải là một script trong `scripts/`, skill chỉ gọi tên.
- **File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`** — thư mục khác bị
  `.graphifyignore` loại nên đồ thị không thấy.
- **Bản portable là SINH, không sửa tay**: thêm skill thì phải chạy `build_portable.py`,
  và skill phải chạy được trên máy khác nơi agent-lsp có thể chưa có gì.

### Chốt sau phỏng vấn

**Quyết định đã chốt**

1. **Một skill mới `skills/tdq-lsp-setup/`** + **một script mới `scripts/tdq_lsp.py`**. Skill là
   văn bản, chỉ nhắc TÊN lệnh; mọi logic kiểm nằm trong script, đúng luật `docs/kien-truc.md`.
2. **Thang kiểm 5 bậc** (4 bậc user nêu + 1 bậc lumen thêm ở vòng 2): binary `agent-lsp` →
   MCP `lsp` đã đăng ký → language server theo ngôn ngữ project → quyền tool `mcp__lsp__*` →
   sức khoẻ `lumen` (Ollama + model embedding).
3. **Cài là phải xin phép.** Script chỉ CHẨN ĐOÁN và IN ra lệnh cài; không tự chạy lệnh cài.
   Claude nêu lệnh, chờ user duyệt, rồi mới chạy. Không có nhánh cài lặng.
4. **Cài sẵn 4 bộ server trên máy này**: Python `pyright-langserver` (`npm i -g pyright`) ·
   TypeScript/JavaScript `typescript-language-server` (`npm i -g typescript-language-server
   typescript`) · C# `csharp-ls` (`dotnet tool install -g csharp-ls`) · Lua
   `lua-language-server` (`brew install lua-language-server`, bản 3.19.1 có sẵn bottle).
5. **Chia vai với `lumen`, không giẫm chân.** `agent-lsp` lo câu hỏi CÓ ĐÁP ÁN ĐÚNG theo ngữ
   nghĩa: định nghĩa ở đâu, ai gọi hàm này, đổi thì vỡ gì, đổi tên an toàn. `lumen` lo câu hỏi
   MƠ HỒ theo ý nghĩa: "chỗ nào xử lý phân quyền". Grep chỉ còn cho chuỗi thuần và cho file
   ngoài tầm LSP (`.md`, `tests/`).
6. **Luật mềm, không hook chặn.** Bắt buộc thử LSP trước grep khi đối tượng là ký hiệu code;
   vi phạm là defect QC, không phải lỗi chặn lượt. Vòng 4 user mở rộng: móc đủ 5 phase —
   `tdq-intake` (chẩn đoán môi trường + bước đọc code của analyze), `tdq-spec` (dựng §2b Ranh
   giới module), `tdq-plan` (dựng dòng `Chạm:`), `tdq-build` (`## Hard rules` + bước
   "Search before creating"). Câu luật gốc để một chỗ, 4 chỗ kia trỏ tới để khỏi lệch.
7. **Chạy được trên máy khác từ số 0.** Skill phải tự đủ: link repo, lệnh cài binary, lệnh
   `agent-lsp init`, bảng 30 ngôn ngữ. Thêm skill xong phải chạy `build_portable.py`.

**Phương án chọn & vì sao**

- **Gọi `agent-lsp init` / `doctor` thay vì tự chế config.** Hai lệnh đó đã làm sẵn việc ghi MCP
  config và dò server; tự viết lại là tự nhận nợ bảo trì khi format đổi.
- **Bác gộp `tdq_lsp.py` vào `tdq_state.py`**: hai việc khác nhau, state là sổ workflow, LSP là
  chẩn đoán môi trường máy.
- **Bác hook chặn (`PreToolUse` cấm Grep)**: grep vẫn đúng cho `.md`, `tests/` và chuỗi thuần;
  chặn cứng là chặn nhầm.

**Nguồn**

- Repo `~/Documents/Add_on_for_claude/agent-lsp` HEAD `ca8b32d` = v0.18.0 —
  `docs/reference/language-support.md` (bảng ngôn ngữ + lệnh cài), `README.md` bước 6 (allow
  list `mcp__lsp__*`), `docker/lsp-servers.yaml` (Lua qua GitHub release).
- Lệnh chạy thật lúc phân tích: `agent-lsp doctor` (chỉ `clangd` ok, 14 server thiếu),
  `claude mcp list` (15 server, KHÔNG có `lsp`), `which` 4 server đích → cả 4 đều chưa có,
  `brew info lua-language-server` → 3.19.1 bottled, `which dotnet npm` → cả hai đã có.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ | Đã xong — 3 vòng phỏng vấn, chốt đủ |
| Research ngoài (tavily) | BỎ | Repo đã clone tại máy, mọi khẳng định kiểm được bằng lệnh |
| spec | CÓ | Khung bất biến |
| plan | CÓ | Khung bất biến |
| implement | CÓ | Khung bất biến |
| Chia sub-agent | CÓ | Đề xuất để `tdq_bench.py mo-phong` đo, user chốt ở cổng `mode` |
| Cài đặt thật lên máy | CÓ | User chọn 2a — dựng thật trên máy này, không chỉ viết văn bản |
| QC độc lập bằng agent | CÓ | Đầu ra là luật + script mới, cần người thứ hai soi bằng hiệu ứng thật |
| `tdq-reviewer` (review sâu) | BỎ | Chỉ chạy khi user yêu cầu |
| `build_portable.py` | CÓ | Thêm skill + script mới, bản portable là SINH nên bắt buộc build lại |
| report | CÓ | Khung bất biến |

**Cổng kiểm (gate check)**

1. *Scope cuối rõ chưa?* RÕ — mới: `skills/tdq-lsp-setup/SKILL.md` (+ reference), 
   `scripts/tdq_lsp.py`, test cho script; sửa: `tdq-intake` (móc kiểm lúc mở request),
   `tdq-build` (luật mềm ưu tiên LSP), `~/.claude/settings.json` (allow list), MCP `lsp`.
2. *Có cần tải/cài gì không?* CÓ — 4 language server + đăng ký MCP `lsp`. Mỗi lệnh cài đều
   xin phép user trước khi chạy.
3. *Phạm vi QC đã định chưa?* RÕ — `agent-lsp doctor` phải xanh cho 4 ngôn ngữ, `claude mcp
   list` phải có `lsp` Connected, một tool `mcp__lsp__*` gọi thật ra kết quả, `tdq_lsp.py` có
   test, `doc_lint.py` exit 0, suite giữ đúng mốc nền 37 đỏ.

## Hỏi đáp

### Vòng 1 — scope + bối cảnh (2026-08-23 01:0x)

Vòng scope: CHẠY — request nêu cả một mảng tính năng chứ không trỏ vào một hành vi, quét khung
9 mặt thấy ≥ 2 mặt có thể áp mà request chưa nói, và có từ mở về chất lượng
("tối đa hóa chất lượng search") không kèm con số.

Trả lời: `1abcd 2a 3a có quyền web sreach nếu cần để tìm đúng 4 tôi muốn biết lumen là của plugin nào?`

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Skill lo tới đâu? | **A+B+C+D** — A chức năng setup (thang kiểm 4 bậc), B nhúng vào workflow (móc `tdq-intake` + `tdq-build`), C an toàn khi cài (hỏi trước mọi lệnh cài), D đa máy/portable. Bác **E** ("chạy được là xong") |
| 2 | Làm cho máy nào? | **A** — cả hai: dựng thật trên máy này VÀ viết skill để máy khác làm lại từ số 0 |
| 3 | Thiếu language server thì? | **A** — nêu đúng lệnh, xin phép, được duyệt thì tự chạy (không phải chỉ hướng dẫn, cũng không phải cài lặng) |
| 4 | `lumen` là plugin nào? | Trả lời trong chat: `ory/lumen` v0.0.42, Apache-2.0, marketplace `claude-plugins-official`, local semantic code search bằng Go AST + Ollama embeddings + SQLite vector |

Kèm: cho quyền web search nếu cần để tìm đúng.

### Vòng 2 — chi tiết trong các mặt đã chọn (2026-08-23 01:3x)

Trả lời: `1b biết tôi đã pull model về, hãy setup thêm vào tdq-workflow sau này sẽ check về lumen
nếu cần model thì xin người dùng setup ollama và pull model 2a 3a 4a nhưng script cần cho
workflow này thì nên để trong tdq/scripts để tách bạch với script project khác`

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Quan hệ với `lumen` | **B** — chia vai, và sửa luôn lumen. Thêm bậc kiểm sức khoẻ lumen: thiếu model thì xin user cài ollama + pull model |
| 2 | "Ưu tiên dùng LSP" cứng tới đâu | **A** — luật mềm: `tdq-build` ghi phải thử LSP trước grep, KHÔNG hook chặn |
| 3 | Cài sẵn server cho ngôn ngữ nào | **A** — Python + TypeScript/JavaScript |
| 4 | Logic kiểm nằm ở đâu | **A** — script mới trong `scripts/`, nhưng user muốn tách bạch với script project khác |

### Vòng 3 — chốt chỗ đặt script (2026-08-23 01:5x)

Hỏi vì câu 4 vòng 2 đụng `.graphifyignore`: file code MỚI bắt buộc nằm trong `scripts/` hoặc
`hooks/`, đặt ở `tdq/scripts/` gốc repo thì đồ thị mù.

Trả lời: `1A bổ sung thêm là install sẵn thêm language server của c# lua nữa`

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Chỗ đặt script | **A** — `scripts/tdq_lsp.py`, theo tiền tố `tdq_` của 6 script workflow sẵn có. Bác B (thư mục con `scripts/tdq/`) và C (`tdq/scripts/` gốc repo, phải sửa `.graphifyignore` + `docs/kien-truc.md`) |

Bổ sung: cài sẵn thêm language server **C#** và **Lua** → danh sách cài chốt thành 4 bộ.

### Vòng 4 — góp ý trên spec bản 1.0 (2026-08-23 01:2x)

Nguyên văn: `móc thêm cả implement và cả plan/spec sreach nữa cho chắc và đầy đủ`

Không phải duyệt. Spec bản 1.0 mới móc 2 chỗ (`tdq-intake` chẩn đoán môi trường, `tdq-build`
mục `## Hard rules`). User muốn phủ luôn bước TÌM KIẾM ở `tdq-spec`, `tdq-plan`, và bước
tìm-trước-khi-tạo của implement. Spec lên bản 1.1: 12 đầu ra → 16, 16 hạng mục QC → 20.

### Vòng 5 — thứ tự ưu tiên và câu hỏi lumen (2026-08-23 01:2x)

Nguyên văn: `update lại là ưu tiên dùng agent lsp hơn lumen, nếu lumen có issue thì sẽ dùng
agent lsp làm lớp chính ưu tiên chạy trước khi grep, và tôi muốn biết agent lsp có thay thế
đc lumen không?`

**Trả lời câu hỏi — agent-lsp KHÔNG thay hết được lumen, nhưng thay được gần hết.**

| Việc | agent-lsp | lumen | Ai thắng |
|---|---|---|---|
| Định nghĩa của ký hiệu này ở đâu | `go_to_definition` — đúng file đúng dòng | đoán theo chunk gần nghĩa | agent-lsp |
| Ai gọi hàm này | `find_callers`, `find_references` | không làm được chắc chắn | agent-lsp |
| Đổi chỗ này thì vỡ gì | `blast_radius` | không có | agent-lsp |
| Liệt kê ký hiệu của file/workspace | `list_symbols`, `find_symbol` | không có | agent-lsp |
| Cây kiểu, kiểu thật của biến | `type_hierarchy`, `inspect_symbol` | không có | agent-lsp |
| Đổi tên an toàn | `rename_symbol`, `prepare_rename` | không có | agent-lsp |
| "Chỗ nào xử lý phân quyền" — hỏi bằng ý niệm, không biết tên gì | `find_symbol` chỉ khớp CHUỖI CON trong TÊN, không hiểu nghĩa | đúng nghề: embedding | **lumen** |
| File ngoài tầm LSP (`.md`, config, ngôn ngữ chưa cài server) | không thấy | thấy | lumen / grep |

Kết luận: lumen chỉ còn thắng ở đúng một ca — hỏi bằng ý niệm khi không biết tên ký hiệu nào.
Ca đó lại đòi Ollama chạy nền. Kiểm lúc này: `lumen health_check` → `Status: ERROR`,
`dial tcp 127.0.0.1:11434: connection refused` — Ollama không chạy, tức lumen đang chết dù
model đã pull. Một dịch vụ nền tắt được bất cứ lúc nào thì không xứng làm lớp chính.

**Chốt:** thứ tự `agent-lsp` → `lumen` → grep. Lumen hỏng thì `agent-lsp` → grep, không chặn
việc. Bậc kiểm lumen là bậc CẢNH BÁO, không phải bậc chặn. Giữ lumen chứ không bỏ, vì
agent-lsp không có tìm kiếm theo ngôn ngữ tự nhiên.

**Phát hiện phụ:** hook `PreToolUse` của plugin lumen (`cmd/hook.go` trong bản cache 0.0.42)
giục dùng lumen trước Grep ở MỌI lượt, kể cả khi lumen chết. Sửa file đó thì mất khi plugin
cập nhật, nên viết luật đối trọng nằm trong repo thay vì sửa plugin.

### Vòng 6 — lumen thành lớp dự phòng, Ollama theo yêu cầu (2026-08-23 01:3x)

Nguyên văn: `okay hãy update lại là agent lsp sẽ làm lớp ưu tiên chạy trước, chỉ chạy lumen khi
những case mà agent lsp tìm không thấy, nếu ollama chưa chạy thì được gọi dậy để chạy, chạy
xong nhả model ra để release tài nguyên cho máy khi nào cần thì mới gọi lại (vì treo model
trong ollama khi nãy máy dùng quá nhiều resource)`

Đổi so với vòng 5: lumen không còn là lựa chọn song song mà là lớp DỰ PHÒNG, kích hoạt bởi
đúng một điều kiện — truy vấn LSP trả về rỗng. Thêm vòng đời Ollama theo yêu cầu.

**Kiểm khả thi trên máy** (`ollama --version` → client 0.32.15, không có instance nào chạy):

| Việc | Lệnh | Có sẵn? |
|---|---|---|
| Đánh thức | `ollama serve` chạy nền, chờ cổng 11434 trả lời | CÓ |
| Nhả model | `ollama stop <model>` | CÓ |
| Kiểm model đang nạp | `ollama ps` | CÓ |

Thứ ngốn RAM là MODEL đang nạp, không phải daemon rỗng — nên `ollama stop` là đủ, không cần
tắt daemon. Chỉ tắt daemon khi chính workflow bật nó trong cùng phiên, có ghi dấu, để không
giết mất phiên Ollama user tự bật cho việc khác.

Ranh giới "script không tự cài" vẫn nguyên: bật/tắt một tiến trình đã có trên máy không phải
là cài đặt.

### Vòng 7 — gỡ hook lumen, thêm bậc dò hook xung đột (2026-08-23 01:3x)

Nguyên văn: `và bỏ hook pretooluse của plugin lumen đang giục dùng lumen trước Grep ở mọi lượt
để tránh làm conflict, và check luôn trong tdq-workflow là sau này thấy sẽ xin người dùng
quyền để xử lí nó`

Vòng 5 tôi đề xuất chỉ viết luật đối trọng vì sợ bản vá mất khi plugin cập nhật. User bác:
gỡ thật. Hai yêu cầu này khớp nhau — bản vá mất thì bậc kiểm mới sẽ bắt lại và xin phép vá lại.

**Định vị hook** (`~/.claude/plugins/cache/claude-plugins-official/lumen/0.0.42/hooks/hooks.json`):

| Khối | Matcher | Xử lý |
|---|---|---|
| `SessionStart` | `startup|resume|clear|compact` | GIỮ — chỉ báo trạng thái index |
| `PreToolUse` | `Grep|Bash` | **GỠ** — đây là khối chèn dòng giục vào mọi lượt |

Đã dò các đường khác trước khi chọn cách gỡ: lumen không có biến môi trường nào tắt được hook
(12 biến `LUMEN_*` đều về backend, model, chunk, log — không có biến tắt hook), và tài liệu
plugin không nêu tuỳ chọn tắt. Nên gỡ khai báo trong `hooks.json` là đường nhẹ nhất: không
phải build lại binary Go, không phải tắt plugin, giữ nguyên MCP tool.

**Thang kiểm lên 6 bậc** — bậc 6 dò hook của plugin đang bật, thấy hook giục một thứ tự tìm
kiếm khác thứ tự TDQ thì BÁO và XIN PHÉP, cấm tự sửa file plugin. Bậc này bắt lại chính hook
lumen khi bản cache được cập nhật và hook mọc lại.

**Hết phỏng vấn — không còn câu nào đổi được kết quả.**
