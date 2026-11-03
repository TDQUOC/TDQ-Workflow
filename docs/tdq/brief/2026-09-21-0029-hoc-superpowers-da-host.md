# Brief — Học cách tổ chức của superpowers: script đa nền tảng và hỗ trợ nhiều host agent
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay mở request học theo cách tổ chức của superpower và handle để cho crossplatform và đa nền
tảng agent như superpower"

"commit và mở request mới handle script học hỏi theo superpower và tổ chức multi agent code
support (opencode ,...) như superpower"

Bối cảnh dẫn tới yêu cầu, từ các lượt trước cùng phiên:

- Request `2026-09-20-1823-sua-tdq-chay-windows` vừa đóng: TDQ chạy đủ tính năng trên Windows,
  test 1983 ca 0 fail. Nhưng **chưa chạy được lần nào trên macOS/Linux**.
- User có bản clone `github.com/obra/superpowers` (v6.4.1) ở
  `C:\Users\admin\Documents\Projects\ForAgentCode\superpowers`, và đã soi sơ bộ.

### Cách hiểu đầu tiên của tôi

**Mục tiêu.** Học cách superpowers tổ chức script và hỗ trợ nhiều host agent, áp vào TDQ để
(a) script chạy được trên cả ba hệ điều hành, (b) hỗ trợ thêm host như OpenCode thay vì chỉ
Claude Code, Codex và Antigravity.

**Số đo đã có từ lượt soi trước:**

| Mặt | superpowers | TDQ-Workflow hiện tại |
|---|---|---|
| Host hỗ trợ | 9 — Claude Code, Codex, Cursor, Devin, Hermes, Kimi, Muse, OpenCode, Pi | 3 bundle: Claude Code, Codex, Antigravity |
| Cách hỗ trợ | một nguồn + thư mục adapter mỏng cho từng host | dựng ba bundle đầy đủ bằng `build_portable.py` |
| Ngôn ngữ hook | bash (45 file `.sh`) | Python |
| Chạy hook trên Windows | `run-hook.cmd` polyglot, tự tìm `bash.exe` | gọi thẳng `python3`, đã đo chạy ở cả ba shell |
| Thiếu phụ thuộc | `exit /b 0`, im lặng xuống cấp | đã vá một phần, chưa thành nguyên tắc |
| Phụ thuộc đường nóng | bash + `cat`/`printf` | Python stdlib |
| Phụ thuộc đường bảo trì | `git` 66, `jq` 9, `gh` 8, `node` 3, `uv` | `git`, cộng graphify/lumen/agent-lsp/codex tuỳ chọn |
| CI đa hệ | KHÔNG có | KHÔNG có |

**Ba thứ đáng học, đã nhận diện:**

1. **Tách tầng phụ thuộc.** Hook của họ chỉ cần bash cộng `cat` và `printf` — họ cố tình tự viết
   hàm escape JSON bằng phép thay chuỗi thay vì gọi `jq`. Mọi thứ nặng (`jq`, `gh`, `node`,
   `uv`) đẩy sang script bảo trì chỉ maintainer chạy. TDQ trộn hai tầng này nhiều hơn.
2. **Im lặng xuống cấp.** Không tìm thấy bash thì thoát 0, plugin vẫn chạy chỉ mất phần chèn
   context. Đây đúng là lỗi vừa giết TDQ trên Windows: hook chết cứng thay vì xuống cấp.
3. **Nhận host qua biến môi trường rồi đổi khuôn đầu ra** (`CURSOR_PLUGIN_ROOT`,
   `CLAUDE_PLUGIN_ROOT`, `MUSE_PLUGIN_ROOT`, `COPILOT_CLI`), thay vì dựng sẵn bundle riêng cho
   từng host.

**Hai thứ KHÔNG nên chép:** file polyglot `run-hook.cmd` và trường `"shell": "bash"` — cả hai là
cách vá cho thiết kế bash-first. Hook TDQ viết bằng Python nên đã đứng ở phía bền hơn: đo được
nó chạy ở Git Bash, `cmd.exe` và PowerShell, kể cả đường dẫn có `(x86)`.

**Chỗ chưa rõ, phải chốt ở phase analyze:**

- Phạm vi host: thêm đúng OpenCode, hay mở khung cho nhiều host?
- Đổi hẳn sang mô hình "một nguồn + adapter mỏng", hay giữ `build_portable.py` và chỉ thêm host?
- Món nợ từ request trước: bundle nướng cứng thư mục nhà máy dựng — request này có xử lý không?
- Có làm CI matrix ba hệ không? Cả hai repo đều đang thiếu, và đó là thứ duy nhất trả lời được
  câu "chạy ổn trên cả ba hệ" bằng máy.
- Các ca test *fail* thay vì *skip* khi thiếu công cụ ngoài — sửa trong request này hay để riêng?

## Hiểu & kiến thức

### Đã đọc và đo trên hai repo (phase analyze, vòng 1)

**Mô hình đóng gói — khác nhau ở gốc.**

superpowers giữ MỘT nguồn `skills/` + `hooks/`, rồi mỗi host chỉ có một thư mục adapter mỏng
trỏ ngược về nguồn đó. Bảy trong chín adapter chỉ là một file manifest:

| Adapter | Dòng | Nội dung |
|---|---|---|
| `.hermes-plugin/plugin.yaml` | 6 | manifest |
| `.claude-plugin/plugin.json` | 20 | manifest |
| `.devin-plugin/plugin.json` | 22 | manifest |
| `.cursor-plugin/plugin.json` | 23 | manifest, trỏ `hooks-cursor.json` |
| `.kimi-plugin/plugin.json` | 38 | manifest |
| `.codex-plugin/plugin.json` | 48 | manifest + khối `interface` cho store |
| `.muse-plugin/plugin.json` | 89 | manifest + marketplace |
| `.pi/extensions/superpowers.ts` | 121 | code — Pi có API lập trình |
| `.opencode/plugins/superpowers.js` | 383 | code — OpenCode có API lập trình |

Khoá của cả mô hình nằm ở đúng một dòng lặp lại trong mọi manifest: `"skills": "./skills/"`.
Adapter OpenCode làm y hệt bằng code: `path.resolve(__dirname, '../../skills')`.

**Cái giá TDQ đang trả cho mô hình chép:**

| Mặt | superpowers | TDQ-Workflow |
|---|---|---|
| Host hỗ trợ | 9 | 3 |
| File bị nhân bản | 0 | 357 (105 + 157 + 95) |
| Dung lượng nhân bản | 0 | 4.2 MB, trong khi nguồn chỉ 672 KB |
| Code duy trì | ~750 dòng adapter, trong đó 246 dòng là manifest | 1077 dòng `scripts/build_portable.py` |

Bốn hệ quả đã ĐO ĐƯỢC của việc chép, không phải suy đoán — cả bốn đều gặp trong request Windows
vừa đóng:

1. lumen index cả bản sao, bản sao chiếm hết top-10 mọi truy vấn (vá tạm bằng `.lumenignore`,
   1488 → 1140 file).
2. Bundle lỗi thời so với nguồn: sau khi sửa `scripts/`, cả ba bundle lệch và phải dựng lại.
3. Bundle nướng cứng thư mục nhà của máy dựng, nên bản dựng từ Windows không commit được.
4. `portable_codex.zip` đứng yên từ 0.24.0 suốt 24 bản vì không script nào dựng nó.

**Phụ thuộc — họ tách hai tầng, TDQ trộn.**

Đường nóng của họ (`hooks/session-start`, chạy mọi phiên) chỉ gọi `cat` và `printf`; hàm escape
JSON tự viết bằng phép thay chuỗi của bash để khỏi cần `jq`. Mọi thứ nặng đẩy sang script bảo
trì chỉ maintainer chạy: `git` 66 lần, `jq` 9, `gh` 8, `node` 3, cộng `uv` trong pre-commit.

Đường nóng của TDQ là Python stdlib — ngang hoặc nhẹ hơn. Nhưng `tdq_finish.py` chạy MỖI LƯỢT
lại gọi `graphify`, tức một công cụ tầng bảo trì nằm trên đường nóng, dù đã xử lý được khi thiếu.

**Cách họ xử lý đa nền tảng, và phần KHÔNG nên chép.**

`hooks/run-hook.cmd` là file polyglot: `cmd.exe` đọc `:` là nhãn nên bỏ qua dòng đầu và chạy
nhánh batch; bash đọc `: << 'CMDBLOCK'` là lệnh rỗng kèm heredoc nên nuốt trọn nhánh đó rồi chạy
bốn dòng cuối. Cộng với `"shell": "bash"` trong `hooks.json`, và tên script cố tình không có đuôi
vì Claude Code trên Windows tự chèn `bash` trước mọi lệnh chứa `.sh`.

Cả ba là cách vá cho thiết kế bash-first. Hook TDQ viết bằng Python, đã đo chạy được ở Git Bash,
`cmd.exe` và PowerShell kể cả đường dẫn có `(x86)`, nên chép vào chỉ tự thêm phụ thuộc Git Bash.

Điều đáng học ở đó là comment trong test của họ, thứ trả lời ẩn số mà tài liệu Claude Code không
nêu: **mặc định trên Windows host điều phối hook bằng PowerShell/cmd.exe, không phải bash.**

**Hai thứ đáng học nhất, cả hai đều là nguyên tắc chứ không phải code:**

1. **Im lặng xuống cấp khi thiếu phụ thuộc.** Batch của họ không tìm thấy bash thì `exit /b 0`,
   plugin vẫn chạy chỉ mất phần chèn context. Đây đúng là lỗi vừa giết TDQ trên Windows: hook
   chết cứng thay vì xuống cấp.
2. **Adapter thay vì bản sao.** Thêm host thứ mười ở superpowers là thêm một file manifest; ở
   TDQ là thêm một nhánh sinh bundle trong 1077 dòng và thêm ~100 file nhân bản.

### Cả hai repo đều thiếu cùng một thứ

Không repo nào có CI đa hệ. `.github/` của superpowers chỉ có issue template, kèm hẳn mẫu
`platform_support.md` — tức hỗ trợ đa nền tảng ở đó dựa trên người dùng báo lỗi về. Test Windows
của họ phải chạy tay và tự khai "cần Git Bash".

Nên câu "chạy được trên cả ba hệ" ở superpowers cũng chưa từng được máy xác nhận.

## Hỏi đáp

### Vòng scope — user trả lời `1a 2a 3b`

- **Phạm vi (1a):** đổi mô hình đóng gói — bỏ chép, chuyển sang adapter mỏng trỏ vào nguồn
  chung, rồi thêm OpenCode.
- **Nợ cũ (2a):** gộp cả ba — dựng lại bundle cho 0.49.0, CI matrix ba hệ, và sửa các ca test
  *fail* thành *skip* khi thiếu công cụ ngoài.
- **Host (3b):** OpenCode trước, nhưng dựng khung để thêm host sau chỉ tốn một manifest.

### Đo thêm sau vòng scope: từng host nạp plugin kiểu gì

Chạy thật trên máy, không suy đoán.

| Host | Cơ chế nạp | Bundle có cần không |
|---|---|---|
| Claude Code | repo tự là marketplace qua `.claude-plugin/marketplace.json` | KHÔNG — đã chạy vậy từ đầu |
| Codex CLI 0.155.1 | `codex plugin marketplace add <đường dẫn local hoặc git>`, đọc `.agents/plugins/marketplace.json` | KHÔNG — đã xác minh |
| Antigravity (agy) | thư mục PHẢI nằm ở `~/.gemini/config/plugins/tdq-workflow/` | CHƯA XÁC MINH ĐƯỢC — máy này không cài agy |
| OpenCode | `.opencode/plugins/<tên>.js`, API lập trình | chưa có, phải viết mới |

Bằng chứng cho dòng Codex: thêm chính bản clone superpowers làm marketplace local thì
`codex plugin list` in ra `superpowers@superpowers-dev`, nguồn trỏ thẳng vào thư mục repo.
Manifest đó chỉ 20 dòng, khoá nằm ở `"source": {"source": "url", "url": "./"}`. Đã gỡ
marketplace thử nghiệm sau khi đo.

Hệ quả: trong ba bundle hiện tại, **hai cái gần như chắc chắn bỏ được** (`portable_claude` chỉ
còn phục vụ kiểu cài chép-vào-project, `portable_codex` thay được bằng một manifest), còn
`antigravity_portable` là cái duy nhất có lý do kỹ thuật thật để giữ dạng thư mục vật chất.

### Ẩn số còn lại

- Adapter OpenCode phải viết bằng JavaScript vì đó là API của host. Hook TDQ viết bằng Python,
  nên adapter này sẽ là chỗ đầu tiên trong repo cần Node lúc chạy.
- Không kiểm được agy trên máy này, nên mọi kết luận về nó chỉ dừng ở mức đọc README bundle.

### Vòng chi tiết — user trả lời `1b 2a 3a 4a`

| # | Câu hỏi | Phán quyết |
|---|---|---|
| 1 | Ba bundle hiện tại | **B — bỏ cả ba**, agy viết hướng dẫn cài tay |
| 2 | Adapter OpenCode cần Node | **A — chấp nhận**, giới hạn nghiêm: chỉ đọc `skills/` và chèn context, cấm dùng package npm |
| 3 | CI matrix | **A — 3 hệ điều hành × Python 3.10 và 3.13** |
| 4 | Bốn công cụ ngoài trên CI | **A — đổi sang `skipUnless`, không cài gì trên runner** |

**Rủi ro của `1b` đã nêu trước khi user chọn, và user vẫn chọn B:** không xác minh được agy trên
máy này, nên bỏ `antigravity_portable` là quyết định dựa trên đọc README chứ không dựa trên chạy
thử. Ghi vào spec §5.

**Cách giảm rủi ro, nằm trong đúng chữ "hướng dẫn cài tay":** thay vì chép sẵn 95 file vào repo,
viết một lệnh sinh layout agy theo yêu cầu vào `~/.gemini/config/plugins/tdq-workflow/`. Bản sao
biến khỏi repo nhưng người dùng agy vẫn có đường cài một lệnh, và layout luôn sinh từ nguồn mới
nhất thay vì từ bản đông cứng lúc release.

**Vì sao chọn Python 3.10 cho CI:** chính hôm nay tôi suýt để lọt một lỗi thuộc đúng loại đó —
`shutil.rmtree(onexc=...)` chỉ có từ 3.12, mà repo còn nhánh dự phòng cho `tomllib` ở Python
< 3.11. Máy này chạy 3.13 nên suite xanh; một máy 3.10 sẽ ăn `TypeError`.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | bốn host đã đo bằng công cụ thật tại chỗ; API OpenCode đọc thẳng được trong bản clone |
| Interview | CÓ | đã chạy vòng scope và vòng chi tiết, hết câu đổi được kết quả |
| spec | CÓ | khung bất biến, và việc này đổi kiến trúc đóng gói |
| plan | CÓ | khung bất biến; mỗi task một test |
| implement | CÓ | khung bất biến |
| Chia việc cho subagent | BỎ | phần gỡ bundle và phần sửa `build_portable` chạm chung tập file |
| QC độc lập (agent) | CÓ | bỏ 357 file là thay đổi khó lùi, cần một lượt xác nhận độc lập |
| Rà soát sâu | CÓ | đổi kiến trúc đóng gói, và có một quyết định đi ngược cảnh báo của chính tôi |
| report | CÓ | khung bất biến |
