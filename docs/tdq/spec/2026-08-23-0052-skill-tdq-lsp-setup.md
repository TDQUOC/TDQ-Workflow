# SPEC — Skill `tdq-lsp-setup`: nhúng agent-lsp vào bộ workflow

Ngày: 2026-08-23 · Bản: 1.4 · Brief: ../brief/2026-08-23-0052-skill-tdq-lsp-setup.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT (2026-08-23T01:36:55+07:00, user nhắn "duyệt spec")

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

- **Mục tiêu:** biến `agent-lsp` thành mắt xích chính thức của bộ workflow TDQ. Sau việc này,
  mở một request bất kỳ thì workflow tự biết project dùng ngôn ngữ gì, môi trường LSP thiếu
  bậc nào, in đúng lệnh cài để user duyệt; và lúc làm việc thì tìm ký hiệu code đi qua ngữ
  nghĩa LSP thay vì grep chuỗi.
- **Trong phạm vi:**
  - Skill mới `skills/tdq-lsp-setup/` — văn bản: link repo, thang kiểm 6 bậc, bảng 30 ngôn ngữ
    kèm lệnh cài, cách chia vai với `lumen`, cách dựng lại từ số 0 trên máy mới.
  - Script mới `scripts/tdq_lsp.py` — chẩn đoán 6 bậc, in báo cáo và in LỆNH CÀI; không tự cài.
  - Móc vào **cả 5 phase** của workflow, không chỉ intake và build:
    - `tdq-intake` mở request: chạy bậc chẩn đoán môi trường, thiếu thì nêu lệnh + xin phép.
    - `tdq-intake` bước "đọc code" của analyze: khảo sát bằng LSP trước, grep sau.
    - `tdq-spec` lúc dựng §2b Ranh giới module: vùng file của module lấy từ ngữ nghĩa LSP.
    - `tdq-plan` lúc viết dòng `Chạm:`: bán kính ảnh hưởng lấy từ "ai gọi hàm này" của LSP.
    - `tdq-build` mục `## Hard rules` và bước "Search before creating" của implement:
      luật mềm "thử LSP trước grep" khi đối tượng tìm là ký hiệu code.
  - **Thứ tự ưu tiên chốt cứng: `agent-lsp` chạy TRƯỚC, `lumen` chỉ chạy khi `agent-lsp` tìm
    không thấy, grep là lớp cuối.** `lumen` không còn là lựa chọn song song — nó là lớp DỰ
    PHÒNG, kích hoạt bởi đúng một điều kiện: truy vấn LSP trả về rỗng. Lumen hỏng và không gọi
    dậy được thì thành `agent-lsp` → grep, không chặn việc.
  - **Vòng đời Ollama theo yêu cầu, không treo thường trực.** Cần tới lumen mà Ollama chưa
    chạy → đánh thức. Tìm xong → nhả model ngay bằng `ollama stop <model>` để trả RAM cho máy.
    Lần sau cần lại thì gọi lại. Lý do: treo model thường trực ngốn quá nhiều tài nguyên máy.
    Workflow chỉ tắt tiến trình do CHÍNH NÓ đánh thức; daemon user tự bật thì không đụng.
  - **Gỡ hẳn hook `PreToolUse` của plugin lumen.** Hook đó khớp `Grep|Bash` và giục dùng lumen
    trước Grep ở MỌI lượt, kể cả khi lumen chết — xung đột thẳng với thứ tự TDQ vừa chốt. Gỡ
    khối `PreToolUse` khỏi `hooks/hooks.json` của plugin, giữ nguyên khối `SessionStart`.
  - **Bậc kiểm thứ 6 — dò hook plugin ngoài xung đột.** Script quét hook của các plugin đang
    bật, thấy hook nào giục một thứ tự tìm kiếm khác thứ tự TDQ thì BÁO và XIN PHÉP user xử
    lý. Script không tự sửa file của plugin. Bậc này còn để bắt lại chính hook lumen khi bản
    cache plugin được cập nhật và hook mọc lại.
  - Dựng thật trên máy này: đăng ký MCP `lsp`, cài 4 bộ language server (Python, TypeScript/
    JavaScript, C#, Lua), thêm allow list `mcp__lsp__*`, kiểm sức khoẻ `lumen`.
  - Build lại bản portable.
- **NGOÀI phạm vi:**
  - Mặt **E** của vòng scope — "chạy được là xong, khỏi viết luật": user đã bác.
  - Hook chặn cứng việc gọi Grep: user chọn luật mềm ở vòng 2 câu 2.
  - Cài sẵn language server cho 26 ngôn ngữ còn lại: chỉ ghi lệnh trong bảng, cài khi project
    thật sự dùng tới.
  - Sửa `.graphifyignore` hay `docs/kien-truc.md`: user chọn 1A ở vòng 3, script nằm trong
    `scripts/` nên không đụng hai file luật đó.
  - Đóng góp ngược lên repo `agent-lsp` (issue, PR): việc này chỉ tiêu thụ, không sửa upstream.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| analyze | CÓ | Đã xong — 3 vòng phỏng vấn, chốt đủ |
| Research web (tavily) | BỎ | Repo đã clone tại máy, mọi khẳng định kiểm được bằng lệnh chạy thật |
| Interview | CÓ | Đã chạy 3 vòng, hết câu đổi được kết quả |
| spec / plan / implement / report | CÓ | Khung bất biến, không cắt |
| Chia sub-agent | CÓ | `tdq_bench.py mo-phong` đo và đề xuất, user chốt ở cổng `mode` |
| Cài đặt thật lên máy | CÓ | User chọn 2a — dựng thật, không chỉ viết văn bản |
| QC độc lập bằng agent | CÓ | Đầu ra là luật + script mới, cần người thứ hai soi bằng hiệu ứng thật |
| `tdq-reviewer` (review sâu) | BỎ | Chỉ chạy khi user yêu cầu |
| `build_portable.py` | CÓ | Thêm skill + script mới, bản portable là SINH nên bắt buộc build lại |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Skill `tdq-lsp-setup` | `skills/tdq-lsp-setup/SKILL.md` | File tồn tại, có link repo GitHub, có thang 6 bậc, có tên lệnh `tdq_lsp.py`, không chép nội dung script |
| 2 | Bảng ngôn ngữ + lệnh cài | `skills/tdq-lsp-setup/references/languages.md` | Đủ 30 ngôn ngữ, mỗi dòng có tên server và lệnh cài |
| 3 | Luật chia vai LSP / lumen / grep | `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` | Có bảng 3 cột: loại câu hỏi → công cụ → ví dụ |
| 4 | Script chẩn đoán | `scripts/tdq_lsp.py` | Chạy `kiem` in đủ 6 bậc kèm ĐẠT/THIẾU; bậc thiếu in ra lệnh cài; exit code phản ánh trạng thái |
| 5 | Test cho script | thư mục test của repo | Suite của script xanh, phủ cả 6 bậc và nhánh không có binary |
| 6 | Móc vào intake | `skills/tdq-intake/SKILL.md` + `references/analyze-full.md` | Có bước gọi `tdq_lsp.py`, nêu rõ phải xin phép trước khi cài |
| 7 | Luật mềm ưu tiên LSP | `skills/tdq-build/SKILL.md` mục `## Hard rules` | Có dòng bắt buộc thử LSP trước grep cho ký hiệu code |
| 8 | MCP `lsp` đăng ký thật | `~/.claude.json` (qua `agent-lsp init`) | `claude mcp list` liệt kê `lsp` ở trạng thái Connected |
| 9 | 4 language server cài thật | máy local | `agent-lsp doctor` báo `ok` cho python, typescript, javascript, csharp, lua |
| 10 | Quyền tool | `~/.claude/settings.json` | Allow list có mục khớp `mcp__lsp__*` |
| 11 | Bản portable | `portable_claude/`, `portable_codex/` | `build_portable.py` chạy xong, hai bản có skill và script mới |
| 12 | Test khoá luật | thư mục test của repo | Xoá dòng luật ưu tiên LSP ở bất kỳ file nào trong 4 file móc thì test ĐỎ, khôi phục thì XANH |
| 13 | Móc vào bước đọc code của analyze | `skills/tdq-intake/references/analyze-full.md` bước 2 | Bước "đọc code" có dòng bắt buộc dùng LSP trước, kèm tên tool và ví dụ |
| 14 | Móc vào spec | `skills/tdq-spec/SKILL.md` bước 1 | Có dòng: vùng file của §2b Ranh giới module dựng từ ngữ nghĩa LSP, không đoán theo tên thư mục |
| 15 | Móc vào plan | `skills/tdq-plan/SKILL.md` bước 2 | Có dòng: dòng `Chạm:` dựng từ kết quả "ai gọi hàm này" của LSP trước khi bổ sung bằng grep |
| 16 | Móc vào bước tìm-trước-khi-tạo | `skills/tdq-build/SKILL.md` Part A bước 2.4 | Vòng tìm trước khi tạo file/hàm mới liệt kê LSP là bước đầu, trước `graphify query` và grep |
| 17 | Bảng so `agent-lsp` với `lumen` | `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` | Có bảng nêu rõ việc nào LSP thay được lumen, việc nào không, và nhánh khi lumen hỏng |
| 18 | Luật đối trọng hook lumen | `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` | Có dòng nói hook của plugin lumen là gợi ý, thứ tự TDQ mới là luật |
| 19 | Lệnh đánh thức Ollama | `scripts/tdq_lsp.py` lệnh con `danh-thuc` | Ollama chưa chạy thì bật nền và chờ tới khi cổng 11434 trả lời; đang chạy sẵn thì báo và không bật thêm |
| 20 | Lệnh nhả model | `scripts/tdq_lsp.py` lệnh con `nha` | Chạy xong thì model embedding không còn trong danh sách model đang nạp; daemon do user tự bật vẫn nguyên |
| 21 | Luật vòng đời Ollama | `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` | Có mục nêu đủ 4 bước: LSP rỗng → đánh thức → tìm bằng lumen → nhả model ngay |
| 22 | Hook lumen đã gỡ | `hooks/hooks.json` của plugin lumen 0.0.42 | File không còn khối `PreToolUse`; khối `SessionStart` còn nguyên; có bản sao lưu trước khi sửa |
| 23 | Bậc dò hook xung đột | `scripts/tdq_lsp.py` bậc 6 | Quét hook của plugin đang bật, liệt kê hook nào giục thứ tự tìm kiếm khác TDQ, kèm đường dẫn file |
| 24 | Luật xin phép trước khi sửa plugin | `skills/tdq-lsp-setup/SKILL.md` | Có dòng: thấy hook xung đột thì nêu đường dẫn và xin phép user, cấm tự sửa file plugin |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| script | `scripts/tdq_lsp.py` cùng test của nó | không | 4, 5 |
| skill-moi | `skills/tdq-lsp-setup/` | script (nhắc tên lệnh) | 1, 2, 3 |
| moc-workflow | `skills/tdq-intake/`, `skills/tdq-spec/`, `skills/tdq-plan/`, `skills/tdq-build/` cùng test khoá luật | skill-moi (trỏ tới) | 6, 7, 12, 13, 14, 15, 16 |
| moi-truong | `~/.claude/settings.json`, `~/.claude.json`, `hooks/hooks.json` của plugin lumen, máy local | script (dùng để kiểm lại) | 8, 9, 10, 22 |
| portable | `portable_claude/`, `portable_codex/` | script, skill-moi, moc-workflow | 11 |

## 3. Cách tiếp cận & lý do

- **Chọn:** một script chẩn đoán thuần + một skill văn bản mỏng, dựng trên `agent-lsp doctor`
  và `agent-lsp init` sẵn có. Script chỉ ĐỌC trạng thái và IN lệnh cài; hành vi cài do Claude
  thực hiện sau khi user duyệt. Ranh giới không đổi khi thêm lệnh `danh-thuc`/`nha`: bật hay
  tắt một tiến trình đã có sẵn trên máy không phải là CÀI ĐẶT, nên luật "script không tự cài"
  vẫn nguyên vẹn.
- **Chọn:** `agent-lsp` chạy trước mọi lúc; `lumen` chỉ vào cuộc khi truy vấn LSP trả về rỗng;
  grep là lớp cuối. Ollama được đánh thức theo yêu cầu và nhả model ngay sau khi tìm xong.
- **Vì:** treo model embedding thường trực trong Ollama ngốn RAM cả phiên làm việc, trong khi
  lumen chỉ được gọi ở một số ít ca. Trả RAM về ngay sau mỗi lần dùng đổi lấy vài giây nạp lại
  model ở lần sau — đánh đổi có lợi khi tần suất dùng thấp.
- **Vì:**
  - Hai lệnh `doctor` và `init` của agent-lsp v0.18.0 đã làm sẵn việc dò server và ghi MCP
    config, kể cả chế độ không tương tác. Tự viết lại là tự nhận nợ bảo trì khi format đổi.
  - Tách "chẩn đoán" khỏi "thi hành" giữ đúng mặt C user chọn: mọi lệnh cài đều đi qua mắt
    user. Script không có quyền cài thì không có đường cài lặng.
  - `docs/kien-truc.md` cấm skill chứa logic; script trong `scripts/` là chỗ duy nhất đồ thị
    graphify nhìn thấy.
  - Gỡ hook ở tầng khai báo `hooks/hooks.json` là cách nhẹ nhất: không phải build lại binary,
    không phải tắt plugin, giữ nguyên MCP tool và khối `SessionStart`. Bù cho việc bản vá mất
    khi plugin cập nhật là bậc kiểm thứ 6 — nó dò lại mỗi lần chạy và xin phép vá lại.
  - `agent-lsp` phủ gần hết việc của `lumen` và phủ chính xác hơn: hỏi định nghĩa, ai gọi, bán
    kính ảnh hưởng, cây kiểu, liệt kê ký hiệu. Đo bằng chính tài liệu tool của repo agent-lsp.
    `lumen` chỉ còn hơn ở đúng một ca — hỏi bằng ý niệm khi không biết tên ký hiệu nào — và ca
    đó đòi Ollama chạy nền. Lúc phân tích, `lumen health_check` báo ERROR vì Ollama không chạy.
  - Phụ thuộc một dịch vụ nền có thể tắt bất cứ lúc nào thì không xứng làm lớp chính.
- **Đã loại:**
  - Hook `PreToolUse` chặn Grep — vì grep vẫn đúng cho `.md`, `tests/` và chuỗi thuần; chặn
    cứng là chặn nhầm. Trùng lựa chọn 2a của user.
  - Script tự chạy lệnh cài — vì vi phạm mặt C.
  - Gộp vào `tdq_state.py` — state là sổ workflow, LSP là chẩn đoán môi trường máy, hai việc
    khác nhau.
  - Đặt script ở `tdq/scripts/` gốc repo — `.graphifyignore` loại, đồ thị mù; user chốt 1A.
  - **Bỏ hẳn `lumen`** — vẫn giữ vì `agent-lsp` không có tìm kiếm theo ngôn ngữ tự nhiên:
    `find_symbol` chỉ khớp chuỗi con trong TÊN ký hiệu, không hiểu ý nghĩa.
  - **Chỉ viết luật đối trọng, không gỡ hook** — luật đối trọng vẫn giữ, nhưng một mình nó
    không đủ: hook vẫn chèn dòng giục vào từng lượt, tốn context và mâu thuẫn với luật.
  - **Tắt hẳn plugin lumen** — mất luôn lớp dự phòng, trong khi chỉ cần bỏ đúng một khối hook.
  - **Sửa `cmd/hook.go`** — phải build lại binary Go; gỡ khai báo trong `hooks.json` nhẹ hơn.
  - **Để Ollama chạy nền thường trực cho tiện** — chính là thứ user vừa bác vì ngốn tài nguyên.
  - **Tắt hẳn daemon Ollama sau mỗi lần dùng** — thứ ngốn RAM là MODEL đang nạp, không phải
    daemon rỗng. `ollama stop` nhả model là đủ; tắt daemon chỉ làm khi chính workflow bật nó.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | Skill khung viết file này |
| tdq-conventions | plugin:tdq-workflow | NỀN | Luật chung mọi phase |
| tdq-plan | plugin:tdq-workflow | DÙNG | Phase plan kế tiếp |
| tdq-build | plugin:tdq-workflow | DÙNG | Phase implement/QC/report, và là đối tượng sửa ở đầu ra 7 |
| Đã xét 216 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/tdq_lsp.py` in log có timestamp theo đúng khuôn các script
  `tdq_*` sẵn có, tắt/giảm được qua cờ dòng lệnh.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Riêng bảng 30
  ngôn ngữ phải chép từ `docs/reference/language-support.md` của repo agent-lsp, cấm bịa lệnh cài.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và bám
  rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ dòng việc này chạm tới):

- "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill" —
  việc này chạm ở `skills/tdq-lsp-setup/SKILL.md`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — thư mục khác bị `.graphifyignore`
  loại nên đồ thị không thấy" — việc này chạm ở `scripts/tdq_lsp.py`.
- "Bản portable là SINH, không sửa tay" — việc này chạm ở `portable_claude/`, `portable_codex/`.

**Cần tải/cài** (mỗi lệnh phải được user duyệt trước khi chạy):

| Gói | Bản | Lệnh |
|---|---|---|
| pyright | mới nhất trên npm | `npm i -g pyright` |
| typescript-language-server + typescript | mới nhất trên npm | `npm i -g typescript-language-server typescript` |
| csharp-ls | mới nhất trên NuGet | `dotnet tool install -g csharp-ls` |
| lua-language-server | 3.19.1 (bottle homebrew) | `brew install lua-language-server` |

Không cần tải model mới: `lumen` đã có model embedding user pull sẵn; bậc kiểm lumen chỉ xin
user cài `ollama` và pull model KHI kiểm thấy thiếu.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `agent-lsp init` ghi đè MCP config đang có | Mất cấu hình 15 MCP server hiện tại | Sao lưu `~/.claude.json` trước khi chạy, so lại `claude mcp list` sau khi chạy, số server phải là 16 |
| Cài global qua npm/dotnet/brew đụng môi trường máy | Xung đột phiên bản với công cụ khác | Chỉ cài 4 gói đã liệt kê, mỗi lệnh xin phép riêng, ghi phiên bản cài được vào report |
| Bảng 30 ngôn ngữ chép sai lệnh cài | User chạy lệnh hỏng trên máy mới | Chép từ `docs/reference/language-support.md`, có test so số dòng bảng với con số 30 |
| Luật mềm không ai theo | LSP cài xong vẫn không được dùng | Khoá bằng test (đầu ra 12) phủ cả 4 file móc, và ghi thành hạng mục QC riêng |
| Luật chép 4 chỗ rồi lệch nhau | Mỗi phase nói một kiểu, agent không biết theo cái nào | Câu luật gốc nằm ở `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`; 4 chỗ kia chỉ trỏ tới, test so nội dung để không lệch |
| Bắt LSP ở spec/plan làm chậm 2 phase vốn ngắn | Mỗi request tốn thêm vài phút | Luật chỉ áp khi project CÓ language server cho ngôn ngữ đó; không có thì bỏ qua, không chặn |
| `lumen` index đang hỏng | Bậc kiểm lumen báo THIẾU dù model đã pull | Bậc kiểm phân biệt rõ ba trạng thái: thiếu ollama, ollama không chạy, thiếu model — mỗi trạng thái một lệnh sửa. Bậc này KHÔNG chặn: lumen hỏng thì rơi về `agent-lsp` → grep |
| Plugin lumen cập nhật thì hook mọc lại | Xung đột quay về im lặng | Bậc kiểm 6 dò lại mỗi lần chạy `kiem`, thấy thì báo và xin phép vá lại |
| Sửa file trong thư mục cache của plugin, ngoài git | Không lùi được bằng git, và mất khi cập nhật | Sao lưu `hooks.json` kèm số bản plugin trước khi sửa, ghi đường dẫn bản sao vào report |
| Bậc 6 báo nhầm hook lành tính là xung đột | Quấy user bằng câu xin phép vô ích | Bậc 6 chỉ báo, không chặn và không tự sửa; tiêu chí báo là hook có nội dung giục một thứ tự tìm kiếm khác |
| Nhả model rồi lần sau phải nạp lại | Mỗi lần gọi lumen tốn thêm vài giây nạp model | Chấp nhận có chủ ý — user chọn đổi thời gian lấy RAM. Lumen là lớp dự phòng nên tần suất thấp |
| Script tắt nhầm Ollama user đang dùng cho việc khác | Người dùng mất phiên chat model đang chạy | Lệnh `nha` chỉ gọi `ollama stop` đúng model embedding của lumen; chỉ tắt daemon khi chính script bật nó trong cùng phiên, có ghi dấu |
| Đánh thức Ollama treo không trả lời | Lượt làm việc đứng chờ vô hạn | Lệnh `danh-thuc` có hạn chờ, quá hạn thì báo THIẾU và rơi thẳng về grep, không chặn |
| Sửa `~/.claude/settings.json` ngoài repo | Không có lịch sử git để lùi | Sao lưu file trước khi sửa, ghi đường dẫn bản sao vào report |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Skill tồn tại và đúng luật | `SKILL.md` có link `https://github.com/blackwell-systems/agent-lsp`, có đủ 6 bậc, và không chứa khối mã Python nào |
| Q2 | Bảng ngôn ngữ đủ | File `languages.md` có đúng 30 ngôn ngữ, mỗi dòng đủ tên server và lệnh cài |
| Q3 | Script chạy được | `tdq_lsp.py kiem` in đủ 6 bậc, mỗi bậc có nhãn ĐẠT hoặc THIẾU |
| Q4 | Script không tự cài | Toàn bộ mã script không có lệnh gọi tiến trình con nào chạy `npm install`, `brew install`, `dotnet tool install` |
| Q5 | Script có log timestamp | Đầu ra script có dòng log mang timestamp, và có cờ tắt log |
| Q6 | Test script xanh | Suite riêng của script xanh toàn bộ, phủ cả nhánh không có binary agent-lsp |
| Q7 | Móc intake | `tdq-intake` có bước gọi script, và có câu bắt buộc xin phép trước khi cài |
| Q8 | Luật mềm ở build | `tdq-build` mục `## Hard rules` có dòng bắt buộc thử LSP trước grep cho ký hiệu code |
| Q9 | Luật được khoá thật | Xoá dòng luật ở BẤT KỲ file nào trong Q7, Q8, Q17, Q18, Q19 thì test khoá luật ĐỎ, khôi phục thì XANH |
| Q10 | MCP đăng ký thật | `claude mcp list` có `lsp` ở trạng thái Connected, tổng số server là 16 |
| Q11 | 4 server cài thật | `agent-lsp doctor` báo trạng thái ok cho python, typescript, javascript, csharp, lua |
| Q12 | Tool LSP gọi được thật | Gọi một tool `mcp__lsp__*` trên một hàm có thật của repo này, trả về vị trí đúng file và đúng dòng |
| Q13 | Quyền tool | `~/.claude/settings.json` có mục allow khớp `mcp__lsp__*` |
| Q14 | Portable đủ | Hai thư mục portable đều chứa skill `tdq-lsp-setup` và `tdq_lsp.py` |
| Q15 | Lint tài liệu | `doc_lint.py` trên spec, plan và các file skill mới exit 0, kèm kiểm cặp spec–plan |
| Q16 | Suite tổng giữ mốc | Số test đỏ của toàn suite đúng bằng mốc nền 37, không thêm cái nào |
| Q17 | Móc bước đọc code | `analyze-full.md` bước 2 có dòng bắt buộc dùng LSP trước grep, kèm tên tool cụ thể |
| Q18 | Móc spec và plan | `tdq-spec` bước 1 và `tdq-plan` bước 2 mỗi file có một dòng luật LSP, mỗi dòng trỏ về file luật gốc |
| Q19 | Móc tìm-trước-khi-tạo | `tdq-build` Part A bước 2.4 liệt kê LSP đứng trước `graphify query` và grep |
| Q20 | Bốn chỗ móc không lệch nhau | Câu luật ở 4 file móc khớp câu gốc trong `uu-tien-tim-kiem.md`, kiểm bằng một lệnh |
| Q21 | Thứ tự ưu tiên ghi rõ | `uu-tien-tim-kiem.md` ghi đúng thứ tự `agent-lsp` → `lumen` → grep, và ghi nhánh lumen hỏng thì bỏ qua lumen |
| Q22 | Bậc lumen không chặn | Tắt Ollama rồi chạy script: bậc lumen báo THIẾU nhưng exit code vẫn là mã cho phép làm tiếp, không phải mã chặn |
| Q23 | Luật đối trọng hook lumen | `uu-tien-tim-kiem.md` có dòng nói hook plugin lumen là gợi ý, thứ tự TDQ mới là luật |
| Q24 | Lumen chỉ chạy khi LSP rỗng | `uu-tien-tim-kiem.md` ghi rõ điều kiện kích hoạt lumen là truy vấn LSP trả về rỗng, không phải lựa chọn song song |
| Q25 | Đánh thức Ollama chạy thật | Tắt Ollama rồi chạy lệnh `danh-thuc`: cổng 11434 trả lời trong hạn chờ, và `lumen health_check` chuyển từ ERROR sang OK |
| Q26 | Nhả model chạy thật | Sau lệnh `nha`, danh sách model đang nạp của Ollama không còn model embedding của lumen |
| Q27 | Không tắt nhầm của user | User tự bật Ollama rồi chạy `nha`: model được nhả nhưng daemon vẫn còn sống |
| Q28 | Đánh thức quá hạn không chặn | Ép tình huống Ollama không lên được: lệnh báo THIẾU và trả mã cho phép làm tiếp, không phải mã chặn |
| Q29 | Hook lumen đã gỡ thật | `hooks.json` của plugin lumen không còn khối `PreToolUse`, vẫn còn khối `SessionStart`, và tồn tại file sao lưu |
| Q30 | Hết chèn dòng giục | Sau khi gỡ, chạy một lệnh Bash bất kỳ thì không còn dòng giục dùng lumen thay Grep kèm theo |
| Q31 | Bậc 6 bắt được hook xung đột | Khôi phục tạm khối `PreToolUse` rồi chạy `kiem`: bậc 6 báo THIẾU và nêu đúng đường dẫn `hooks.json`; gỡ lại thì báo ĐẠT |
| Q32 | Bậc 6 không tự sửa | Toàn bộ mã script không có lệnh ghi nào nhắm vào thư mục cache plugin |

**DoD:** đủ 32 hạng mục Q1–Q32 PASS kèm bằng chứng chạy thật · mọi task trong plan tick `[x]` ·
`agent-lsp doctor` xanh cho 5 ngôn ngữ đích · MCP `lsp` Connected · bản portable build lại ·
working log của ngày được ghi qua `tdq_finish.py` · report có bảng thời gian và liệt kê đúng
phiên bản 4 gói đã cài.

## 7. Câu hỏi còn mở

(rỗng)
