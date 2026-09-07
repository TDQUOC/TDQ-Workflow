# BRIEF — Trang HTML hiển thị trạng thái setup TDQ-Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay hãy mở request tạo một html page có tên là setup_status.html trong đó sẽ có hiển thị
> trạng thái setup của tdq-workflow (skill, hook, thực tế claude code nhận), các dependency
> hoặc thư viện liên quan như graphify, lumen, agent lsp với chi tiết như lumen thì dùng model
> gì, agent lsp thì có những language server nào và thật tế claude code nhận được gì

- **Mục tiêu**: một trang `setup_status.html` mở ra là thấy ngay TDQ-Workflow đang được cài
  và được Claude Code NHẬN như thế nào — không phải đọc lại 5 file config rải rác.
- **Ba nhóm nội dung người dùng nêu**:
  1. Bản thân workflow: skill nào có, hook nào chạy, và **thực tế Claude Code nhận được gì**.
  2. Dependency: graphify, lumen, agent-lsp — có/không, phiên bản.
  3. Chi tiết từng cái: lumen dùng model gì; agent-lsp khai báo language server nào và
     **thực tế nhận được gì**.
- **Điểm mấu chốt lặp lại 2 lần trong yêu cầu**: "thực tế nhận được gì" — tức là trang phải
  phân biệt KHAI BÁO (config) với THỰC NHẬN (Claude Code/agent-lsp thật sự có gì trong tay).
- **Chỗ chưa rõ (để hỏi ở vòng phân tích)**: trang là ảnh chụp tĩnh một lần hay có script sinh
  lại được; lấy số liệu bằng đọc config hay có dò sống (probe) từng server; mức chi tiết của
  phần hook (chỉ liệt kê hay kèm thời gian chạy đã đo).

### Vì sao "thực nhận" không đọc config là ra

Request trước (`2026-09-06-1326-them-language-server`) đã đo được: agent-lsp khai 14 server,
nhưng csharp-ls chết bằng `abort trap` ngay lần hỏi đầu và agent-lsp KHÔNG hồi sinh server chết
→ file `.cs` âm thầm rơi về clangd. Config lúc đó vẫn "đủ 14". Tương tự, `skill_inventory.py`
ghi rõ skill built-in của Claude Code không nằm trên đĩa (đo được 7 trên đĩa / 18 trong ngữ
cảnh). Nên cột "thực nhận" chỉ trung thực nếu có dò sống, không thể suy từ file cấu hình.

### Nguyên liệu đã có sẵn trong repo (chưa phải thiết kế, chỉ là kiểm kê)

| Nguồn | Cho được gì |
|---|---|
| `scripts/skill_inventory.py` | skill trên đĩa từ 3 nguồn user/project/plugin đang bật |
| `scripts/context_surface.py` | tầng nạp của từng file doc + `--hooks` đo mili-giây mỗi hook |
| `scripts/tdq_lsp.py check` | thang 7 bậc: agent-lsp, MCP, language server, quyền tool, lumen, hook, cấu hình import |
| `scripts/tdq_checkstatus.py report` | sức khoẻ state/doc của workflow |
| `~/.claude.json` → `mcpServers.lsp.args` | danh sách language server KHAI BÁO |
| `~/.config/lumen/config.yaml` | model + 2 endpoint của lumen |

### Kiểm lớp tìm kiếm (bước 1b)

7 bậc: **7/7 ĐẠT** (bậc 5 vừa vá xong hôm qua). Kiểm hiệu ứng: `find_references` trên
`_model_lumen` (`scripts/tdq_lsp.py:297`) trả 6 tham chiếu trải `scripts/` + `tests/`,
grep đếm 2 file ⇒ LSP ≥ grep, PASS.

## Hiểu & kiến thức

### Năng lực dùng được (B0)

Lọc `skill_inventory.py --loc "html trang trạng thái setup báo cáo dependency"`: 8 skill trên đĩa,
tất cả thuộc `plugin:tdq-workflow`; 1 skill bị ẩn vì không khớp từ khoá.

| Năng lực | Nguồn | Phán quyết |
|---|---|---|
| `tdq-intake` / `tdq-spec` / `tdq-plan` / `tdq-build` | plugin:tdq-workflow | DÙNG — đúng 4 pha của lane chuyên sâu |
| `tdq-lsp-setup` | plugin:tdq-workflow | DÙNG — trang lấy lại chính thang 7 bậc của nó làm dữ liệu |
| `tdq-status` / `tdq-check-status` | plugin:tdq-workflow | DÙNG khi cần đối chiếu state, không phải nguồn cho trang |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG — luật chung, nạp sẵn |
| `graphify` (skill user) | user | KHÔNG — request này không hỏi về đồ thị, chỉ hỏi graphify còn sống không |
| Built-in trong ngữ cảnh (Skill, Task/Agent, Bash, Read/Edit/Write, WebFetch…) | context | DÙNG Bash + Read/Write; **Task/Agent** để nghiên cứu nếu phát sinh |

### Luật kiến trúc ràng buộc request này (`docs/kien-truc.md`, bản NHÁP)

- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` ⇒ bộ sinh là `scripts/setup_status.py`.
- `skills/` chỉ được nhắc TÊN lệnh, cấm chép nội dung script.
- Ngôn ngữ 3 tầng: docstring/chú thích/chuỗi máy in trong `scripts/` viết TIẾNG ANH;
  nội dung trang HTML là tài liệu cho user ⇒ viết theo `doc_lang` = tiếng Việt.
- `tests/` khoá hành vi tầng CLI ⇒ mỗi hàm thu số liệu phải có test.

### Nguồn số liệu đã dò thật trên máy (không phải suy đoán)

| Câu hỏi của trang | Lệnh/API đã chạy thử | Ra được gì |
|---|---|---|
| Skill nào đang có | `skill_inventory.inventory(project)` | 8 skill trên đĩa, kèm nguồn user/project/plugin |
| Hook nặng nhẹ ra sao | `context_surface.scan()` + `measure_hooks()` | tầng nạp từng file doc; mili-giây từng hook (đo lặp, lấy trung vị) |
| 7 bậc LSP | `tdq_lsp.bac1..bac7` trả object `Bac` | 7/7 ĐẠT lúc 09:10 hôm nay |
| Claude Code THỰC SỰ nhận MCP nào | `claude mcp list` | 6 server, mỗi dòng kèm `✔ Connected` — đây là câu trả lời "thực nhận" cấp MCP |
| Language server THỰC SỰ sống | `agent-lsp doctor <args>` | chạy thử từng server đã khai, không chỉ đọc config |
| Language server đang KHAI BÁO | `~/.claude.json` → `mcpServers.lsp.args` | 14 khoá ngôn ngữ |
| lumen dùng model gì | `~/.config/lumen/config.yaml` + `tdq_lsp._model_lumen()` | `qwen3-embedding:0.6b`, 2 endpoint primary→backup |
| Phiên bản dependency | `graphify --version` · `lumen version` · `agent-lsp --version` | 0.9.55 · 0.0.42 · 0.19.2 |

### Cảnh báo bí mật — RÀNG BUỘC CỨNG của request này

`claude mcp list` in **nguyên khoá Tavily trong URL**. Trang HTML tuyệt đối không được chứa
khoá đó: mọi URL MCP phải mask (`tvly-dev-***`) trước khi ghi ra file. Repo là PUBLIC nên
`setup_status.html` chứa đường dẫn máy, IP tailnet và danh sách MCP — nơi đặt file và việc có
đưa vào `.gitignore` hay không là câu hỏi phải chốt với user trước khi code.

### Vì sao KHÔNG chạy vòng research ngoài

Toàn bộ ẩn số của request đều là công cụ đã cài sẵn trên máy này, và tôi đã kiểm bằng cách CHẠY
THẬT (`claude mcp list`, `agent-lsp --help/doctor`, `lumen version`, `graphify --version`,
`skill_inventory.py`, `context_surface.py`) thay vì tra tài liệu — bằng chứng chạy thật mạnh hơn
kết quả web. Không còn ẩn số ngoài nào cần tra.

## Hỏi đáp

**H1. Dò "thực nhận" sâu tới đâu?** → **A: dò sống đầy đủ.** `claude mcp list` cho trạng thái
kết nối từng MCP; `agent-lsp doctor` khởi động thật từng language server. Ước tính lúc hỏi là
30–60 giây, **đo lại sau khi hỏi: 14/14 server ok trong 6,0 giây** — rẻ hơn hẳn dự phòng.

**H2. Đặt file ở đâu, có commit không?** → **A: sinh ở gốc repo + thêm vào `.gitignore`.**
Trang chứa đường dẫn `/Users/tdq`, IP tailnet, danh sách MCP; repo public nên không đẩy lên.

**H3. Skill built-in script không thấy được?** → **A: hiện skill trên đĩa, ghi rõ một dòng giới
hạn.** Không bịa phần built-in.

**H4. Làm mới thế nào?** → **A: chạy tay `python3 scripts/setup_status.py`.** Không móc vào
`tdq_finish.py`, để turn không cõng thêm thời gian dò.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | mọi ẩn số là công cụ cài sẵn trên máy, đã kiểm bằng chạy thật (`claude mcp list`, `agent-lsp doctor`, `lumen version`, `graphify --version`) — bằng chứng chạy mạnh hơn tài liệu web |
| Vòng scope | BỎ | request đã tự khoanh đúng 3 nhóm nội dung (workflow · dependency · thực nhận); 4 câu H1–H4 đủ khép mơ hồ |
| Interview | CÓ | 1 vòng, 4 câu H1–H4, người dùng chốt hết |
| Spec → Plan | CÓ | hai turn tách nhau theo luật |
| QC độc lập (agent `tdq-qc-tester`) | CÓ | giá trị duy nhất của trang là NÓI THẬT; một tác nhân khác kiểm lại "khai báo vs thực nhận" đáng giá hơn tự chấm |

Ba luồng tính năng của request: **(1) thu số liệu** từ 6 nguồn · **(2) dò sống** MCP +
language server · **(3) kết xuất HTML tự chứa**.
