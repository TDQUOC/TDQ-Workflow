# BRIEF — Điều tra nguyên nhân lỗi LSP search gate và tdq_team clean

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay tôi muốn mở request detect nguyên nhân của những vấn đề sau xem có nằm ở tdq-workflow không? liệu có phải tdq-workflow thiếu instruction cho việc dùng lsp? vì lỗi này rất hay gặp"
> Kèm 2 ảnh chụp thực tế từ phiên làm việc trên project khác (`claudecodeui`):
> 1. Ảnh 1: Leader trong mode `subagent` chạy lệnh `python3 ".../scripts/tdq_team.py" clean T1.1` bị lỗi CLI: `Error Exit code 2 usage: tdq_team.py [-h] {assign,audit,wave,open,check,merge,sweep,clean,resolve} ... tdq_team.py: error: unrecognized arguments: T1.1`.
> 2. Ảnh 2: Agent thực hiện tìm kiếm bằng Grep với regex danh sách đoán mò (`abort|stopBackgroundTask|async...`) trong file TypeScript `provider-runtime.service.ts` thì bị hook `search_gate.py` chặn bằng lỗi: `PreToolUse:Grep hook error: [TDQ:SEARCH] Guess-list search (4 alternatives); the last concept query was 10 searches ago (window 10). Ask again: mcp__lsp__start_lsp (root_dir = the project root, language_id = the language of the code, e.g. python) then mcp__lsp__find_symbol / find_references...`.

### Đọc bước đầu

- **Mục tiêu:** Điều tra nguyên nhân gốc rễ của 2 vấn đề mà agent gặp phải trong thực tế sử dụng TDQ Workflow, xác định xem nguyên nhân có nằm ở TDQ Workflow không, và đề xuất các giải pháp khắc phục triệt để.

## Hiểu & kiến thức

### Năng lực dùng được

| Nguồn | Tên | Khớp chỗ nào | Quyết định | Lý do |
|---|---|---|---|---|
| 内置/MCP | `mcp__lsp__*` (`python`) | Tra cứu symbol và hàm trong `scripts/tdq_team.py`, `hooks/scripts/search_gate.py`, `scripts/search_rules.py` | **dùng** | Đảm bảo tuân thủ luật tìm kiếm 3 tầng khi khảo sát mã nguồn |
| Repo script | `scripts/tdq_team.py` | Quản lý lệnh điều phối mode subagent (`clean`, `merge`, `sweep`) | **dùng** | Nơi xảy ra lỗi `unrecognized arguments: T1.1` |
| Repo hook | `hooks/scripts/search_gate.py` & `scripts/search_rules.py` | Kiểm soát và chặn tìm kiếm vượt tầng | **dùng** | Nơi phát sinh thông báo chặn `[TDQ:SEARCH]` |
| Repo skill | `skills/tdq-setup/` & `skills/tdq-build/` | Chỉ dẫn luật tìm kiếm và quy trình mode subagent | **dùng** | Nơi cung cấp instruction cho agent |
| Built-in | `Read`, `Edit`, `Write` | Đọc và sửa đổi mã nguồn, tài liệu | **dùng** | Công cụ thao tác file tiêu chuẩn |

### Phân tích nguyên nhân gốc rễ 2 vấn đề

#### Vấn đề 1: Lỗi CLI `tdq_team.py clean T1.1` (Exit code 2)
- **Nguyên nhân trực tiếp trong code**:
  - Trong `scripts/tdq_team.py` (hàm `build_parser()`), lệnh con `clean` chỉ được khai báo đơn thuần `sub.add_parser("clean")`, không có tham số vị trí `task`.
  - Trong khi đó, các lệnh `open`, `check`, `merge`, `resolve` đều khai báo `con.add_argument("task", ...)`.
  - Khi agent chạy `tdq_team.py clean T1.1`, bộ phân tích `argparse` coi `T1.1` là tham số không xác định và báo lỗi `error: unrecognized arguments: T1.1` (exit 2).
- **Nguyên nhân gián tiếp trong instruction**:
  - Tại `skills/tdq-build/SKILL.md` (dòng 91) ghi: `On receiving a report, run check then merge, tick [x] IMMEDIATELY, clean, then back to wave.`
  - Cụm từ `run check then merge, tick [x] IMMEDIATELY, clean` đặt từ `clean` ngay sau `check` và `merge` (vốn luôn đi kèm mã task như `check T1.1`, `merge T1.1`), khiến model suy luận rằng phải gọi `clean T1.1`.
  - Trong thực tế kiến trúc của `tdq_team.py`, lệnh `merge` (hàm `lenh_hop`) đã **tự động gọi `_thu_don`** để xóa worktree và xóa nhánh của task ngay sau khi gộp thành công vào nhánh tích hợp. Lệnh `clean` chỉ dùng để dọn dẹp toàn bộ worktree của slug, hoặc cuối wave dùng `sweep --clean`.
- **Giải pháp đề xuất**:
  1. *Về CLI*: Cho phép `clean` nhận tham số `task` tùy chọn (`nargs="?"`). Nếu agent truyền `clean T1.1`: kiểm tra nếu worktree còn tồn tại thì dọn dẹp; nếu worktree đã được dọn tự động bởi `merge` trước đó thì in thông báo `Worktree for T1.1 already cleaned.` và trả về 0 (thành công) thay vì báo lỗi cú pháp exit 2.
  2. *Về Instruction*: Sửa dòng 91 trong `skills/tdq-build/SKILL.md` làm rõ rằng `merge` đã tự động thu dọn worktree của task, và cuối wave thì gọi `sweep --clean`.

#### Vấn đề 2: Lỗi chặn `[TDQ:SEARCH]` do dùng Grep đoán mò thay vì LSP
- **Nguyên nhân trực tiếp trong code & hook**:
  - Khi agent dùng `Grep` với regex có dấu `|` (`abort|stopBackgroundTask|async...`), hàm `_hinh_mau` trong `scripts/search_rules.py` nhận diện đây là danh sách đoán mò (`doan_mo=True`).
  - Do agent chưa thực hiện truy vấn tầng khái niệm nào (LSP hoặc graphify) trong phiên hoặc đã quá cửa sổ 10 lượt tìm kiếm, `search_gate.py` kích hoạt quy tắc chặn `[TDQ:SEARCH] Guess-list search...`.
- **Nguyên nhân trong Instruction & Trải nghiệm thực tế**:
  1. **Instruction về LSP trong `CLAUDE.md` quá vắn tắt**: Khối ghim `KHOI_HUONG_DAN` hiện chỉ ghi:
     `- Quan hệ, kiểu, diagnostics, đổi tên → mcp__lsp__* (phiên mới: start_lsp kèm language_id trước).`
     Không giải thích cụ thể công cụ nào làm việc gì (ví dụ: muốn xem danh sách hàm/class trong file thì dùng `mcp__lsp__list_symbols(file_path)` thay vì grep mò; muốn tìm symbol toàn dự án thì dùng `mcp__lsp__find_symbol(query)`).
  2. **Thông báo lỗi của hook cứng nhắc và gây hiểu lầm**: Trong `scripts/search_rules.py`, biến `LOP_KHAI_NIEM` đang hardcode cứng:
     `Ask again: mcp__lsp__start_lsp (root_dir = the project root, language_id = the language of the code, e.g. python)`
     Khi agent làm việc trên dự án TypeScript/JavaScript (như `claudecodeui`), thông báo vẫn in `e.g. python`, khiến model bối rối không biết dùng `language_id` nào. Ngoài ra thông báo chỉ nhắc `find_symbol / find_references`, không nhắc `list_symbols` khi agent đang tra cứu trong một file cụ thể.
  3. **Thiếu tự động điền `language_id` theo dự án**: Hook `search_gate.py` hoàn toàn có thể đọc mốc `.tdq-lsp-module.json` hoặc nhận diện file mốc của project (`package.json` -> `typescript`, `pyproject.toml` -> `python`, `go.mod` -> `go`, `Cargo.toml` -> `rust`) để điền chính xác `language_id` của project vào câu nhắc chặn, giúp model có thể copy gọi ngay lệnh `start_lsp`.
- **Giải pháp đề xuất**:
  1. *Cải tiến thông báo của `search_gate.py` / `search_rules.py`*: Tự động điền `language_id` chính xác theo dự án hiện tại thay vì `e.g. python`. Bổ sung gợi ý `mcp__lsp__list_symbols` khi agent tìm kiếm trong phạm vi một file cụ thể.
  2. *Cập nhật Instruction trong `KHOI_HUONG_DAN` và `CLAUDE.md`*: Bổ sung ánh xạ trực quan các công cụ LSP thường dùng (`list_symbols` xem cấu trúc file, `find_symbol` tìm hàm/class toàn dự án, `find_references` tìm vị trí gọi, `inspect_symbol` xem kiểu). Nhắc rõ nguyên tắc: dùng LSP sẽ mở khóa 10 lượt grep tiếp theo và tránh dùng regex `a|b|c` đoán mò.

#### Vấn đề 3: Lỗi 'LSP client not initialized; call start_lsp first' và các rào cản khi khởi tạo lsp-agent
- **Hiện tượng**:
  - Khi agent bắt đầu tìm kiếm bằng các công cụ LSP (`mcp__lsp__find_symbol`, `mcp__lsp__list_symbols`, `mcp__lsp__find_references`, `mcp__lsp__inspect_symbol`), agent-lsp ngay lập tức trả về lỗi: `LSP client not initialized; call start_lsp first`.
  - Sau khi nhận lỗi này, agent thường bối rối, không biết truyền tham số gì vào `start_lsp` (hoặc truyền thiếu `language_id`), rồi bỏ cuộc và quay lại dùng `Grep` đoán mò từ khóa, dẫn đến tiếp tục bị hook `[TDQ:SEARCH]` chặn.
- **Nguyên nhân gốc rễ**:
  1. **Bản chất của agent-lsp proxy**: agent-lsp là máy chủ MCP đa ngôn ngữ chạy nền (multi-server proxy). Nó không tự ý gán ngôn ngữ hay thư mục gốc cho đến khi nhận chỉ thị `start_lsp`. Phía Claude Code cũng không tự động gọi `start_lsp` lúc mở phiên.
  2. **Chỉ dẫn trong CLAUDE.md quá vắn tắt**: Khối `KHOI_HUONG_DAN` hiện chỉ có một ghi chú trong ngoặc đơn: `(phiên mới: start_lsp kèm language_id trước)`. Ghi chú này quá ngắn, không nêu rõ đây là điều kiện TIÊN QUYẾT BẮT BUỘC trước khi gọi bất kỳ tool `mcp__lsp__*` nào, và không đưa ra ví dụ cụ thể về tham số (`root_dir`, `language_id`).
  3. **Bẫy tsserver "No Project" trên TypeScript/JavaScript**: Riêng với TypeScript/JS (như dự án `claudecodeui` trong ảnh người dùng gửi), sau khi gọi `start_lsp(language_id="typescript")`, tsserver vẫn chưa index mã nguồn và sẽ trả về `"No Project"` hoặc rỗng cho đến khi có ít nhất một file được mở bằng `mcp__lsp__open_document`. Model không biết điều này sẽ nghĩ rằng LSP bị hỏng và từ bỏ công cụ.
  4. **Hook nhắc nhở chưa cung cấp mẫu lệnh copy-paste**: Khi `search_gate.py` chặn tìm kiếm hoặc khi `lsp_gate.py` nhắc nhở, thông báo đang để ví dụ cứng `e.g. python` và chưa tự động điền sẵn mẫu lệnh đầy đủ ứng với ngôn ngữ của dự án hiện tại (ví dụ: `mcp__lsp__start_lsp(root_dir="...", language_id="typescript")`).
- **Giải pháp đề xuất**:
  1. *Cập nhật KHOI_HUONG_DAN ghim vào CLAUDE.md*: Hướng dẫn rõ quy trình 3 bước cơ học:
     - Bước 1 (Bắt buộc đầu phiên): Gọi `mcp__lsp__start_lsp` với `root_dir` và `language_id` (ví dụ: `typescript`, `python`, `go`, `rust`).
     - Bước 2 (Dành cho TypeScript/JS): Gọi `mcp__lsp__open_document` một file nguồn để tsserver nhận diện project.
     - Bước 3: Tra cứu chính xác bằng `list_symbols` (xem cấu trúc/hàm trong file), `find_symbol` (tìm symbol toàn dự án), `find_references` (tìm nơi gọi).
  2. *Cải tiến thông báo của search_gate.py*: Nhận diện ngôn ngữ thực tế của project hiện tại (từ `.tdq-lsp-module.json` hoặc file mốc `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`) để in ra đúng cú pháp mẫu `mcp__lsp__start_lsp(root_dir="<cwd>", language_id="<lang>")` có thể copy-paste được ngay.
  3. *Tự động nhắc nhở trong session_start.py*: Khi phiên mở tại một project có cấu hình language server, in một dòng nhắc ngắn gọn chỉ rõ lệnh khởi tạo LSP cho ngôn ngữ đó.

### Phạm vi đã chốt

- **Trong phạm vi (In-scope):**
  1. *Vấn đề 1 (CLI `clean`)*: Cập nhật `scripts/tdq_team.py` để `clean [task]` nhận tham số `task` tùy chọn (nếu worktree của task đã dọn bởi `merge` thì in thông báo và trả về 0; nếu chưa thì dọn dẹp task đó; nếu không có task thì dọn toàn bộ slug như cũ); đồng thời sửa dòng 91 trong `skills/tdq-build/SKILL.md` và `team-mode.md` làm rõ quy trình.
  2. *Vấn đề 2 & 3 (LSP Instruction & Hook)*:
     - Cập nhật `scripts/search_rules.py` và `hooks/scripts/search_gate.py`: phát hiện ngôn ngữ dự án theo `cwd` để thay thế chuỗi cứng `e.g. python` bằng `language_id` thực tế trong thông báo chặn; bổ sung gợi ý `mcp__lsp__list_symbols` khi agent grep trong 1 file cụ thể; bổ sung hướng dẫn gọi `open_document` đối với TypeScript/JS.
     - Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` (và ghim lại vào `~/.claude/CLAUDE.md`): hướng dẫn rõ ràng quy trình gọi `start_lsp` đầu phiên, các công cụ LSP thường dùng và nguyên tắc mở khóa grep.
     - Cập nhật `skills/tdq-setup/references/uu-tien-tim-kiem.md` đồng bộ các quy tắc trên.
  3. *Unit tests*: Viết đầy đủ unit test cho `clean [task]`, tự động sinh thông báo lỗi theo ngôn ngữ trong `search_rules.py`, và kiểm tra tính nhất quán của tài liệu / instruction.
- **Ngoài phạm vi (Out-of-scope):**
  - Không thay đổi hành vi chặn cơ bản của `search_gate.py` đối với các lệnh grep đoán mò nhiều từ khóa qua regex.
- **Mức QC đã chốt:** `lite` (DoD + unit test vùng chạm theo lựa chọn 4b của người dùng).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Bài toán hoàn toàn nằm trong mã nguồn Python (`tdq_team.py`, `search_gate.py`, `search_rules.py`) và tài liệu instruction của TDQ-Workflow |
| Interview | CÓ | Đã hoàn thành 1 vòng phỏng vấn chốt đủ 4 câu hỏi (`1a 2a 3a 4b`) |
| QC độc lập | BỎ | Áp dụng mức QC `lite` đã chọn |

## Hỏi đáp

### Vòng 1 (2026-10-15 11:05)

1. **Phương án xử lý lệnh `tdq_team.py clean`**:
   - A (đề xuất): Xử lý cả code lẫn instruction — cho phép `tdq_team.py clean [task]` nhận tham số task tùy chọn VÀ sửa dòng 91 trong `skills/tdq-build/SKILL.md`.
   - B: Giữ nguyên lệnh `clean` không nhận tham số, chỉ sửa câu chữ trong `SKILL.md`.
   - **Người dùng chọn:** `1a`
2. **Cải tiến thông báo chặn của `search_gate.py` / `search_rules.py`**:
   - A (đề xuất): Tự động phát hiện ngôn ngữ dự án (`typescript`, `javascript`, `python`, `go`, `rust`...) để thay chuỗi cứng `e.g. python` bằng đúng `language_id` thực tế; đồng thời gợi ý `mcp__lsp__list_symbols` khi agent đang grep trong 1 file cụ thể.
   - B: Giữ nguyên logic thông báo hiện tại, chỉ sửa câu chữ mẫu.
   - **Người dùng chọn:** `2a`
3. **Mở rộng hướng dẫn LSP trong `KHOI_HUONG_DAN` (ghim vào `CLAUDE.md`)**:
   - A (đề xuất): Bổ sung chỉ dẫn ngắn gọn các thao tác LSP cốt lõi (`start_lsp`, `list_symbols`, `find_symbol`, `find_references`) và nhắc rõ việc gọi LSP sẽ mở khóa 10 lượt grep tiếp theo.
   - B: Giữ nguyên `KHOI_HUONG_DAN` ngắn gọn như cũ.
   - **Người dùng chọn:** `3a`
4. **Mức QC (chất lượng kiểm thử)**:
   - A: `full`
   - B (người dùng chọn): `lite` — DoD + unit test vùng chạm.
   - C: `ultra`
   - **Người dùng chọn:** `4b`
5. **Yêu cầu bổ sung của người dùng**:
   - Bổ sung phân tích và xử lý nguyên nhân lỗi gọi `lsp-agent init` (`start_lsp`) trước: làm rõ điều kiện tiên quyết gọi `start_lsp` đầu phiên, hỗ trợ mẫu lệnh gọi sẵn kèm `language_id` phù hợp và bước `open_document` đối với TypeScript/JS để tránh bẫy "No Project" của tsserver.
