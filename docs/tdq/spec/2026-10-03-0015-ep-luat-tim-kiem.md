# SPEC — Buộc agent code tuân đúng luật tìm kiếm 4 tầng

Ngày: 2026-10-03 · Bản: 1.1 · Brief: ../brief/2026-10-03-0015-ep-luat-tim-kiem.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT (2026-10-03, "duyệt spec")

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

- **Mục tiêu:** agent code — Claude Code và Codex — không thể trả lời một câu hỏi khái niệm bằng
  grep đoán mò. Lần tìm code ĐẦU TIÊN của mỗi request phải đi qua tầng khái niệm, trừ khi chuỗi
  tìm có nguyên văn trong prompt của user. Lần mở khoá chỉ có hiệu lực trong một số lần tìm kế
  tiếp, không phải cả request. Bộ tìm kiếm tự sẵn sàng ngay ở đầu project. Thang kiểm chỉ báo ĐẠT
  khi công cụ thật sự trả lời được. Đo được bằng: phát lại các lần tìm của phiên excalidraw
  2026-10-02 qua cổng mới — cổng bắt **cả lượt 7 (`fileHandle`, một tên agent tự đoán) và lượt 9**,
  bắt mọi lần tìm đoán mò còn lại khi cửa sổ mở khoá đã hết, và **không bắt oan** lần lọc danh
  sách file nào.
- **Trong phạm vi:**
  - Cổng tìm kiếm cắm vào `PreToolUse` trên `Bash` và `Grep` — chặn có điều kiện.
  - **Luật mở đầu:** lần tìm code đầu tiên của request phải là tầng khái niệm; ngoại lệ là chuỗi
    có nguyên văn trong prompt gần nhất của user.
  - **Mở khoá có hạn:** một lần gọi tầng khái niệm mở khoá N lần tìm kế tiếp; N chốt ở plan
    bằng phép phát lại.
  - Sổ "đã hỏi tầng khái niệm" theo request, sống qua nhiều lượt.
  - Cùng cổng chạy trên Codex ở dạng `deny`; `tdq-setup` khai MCP lumen + LSP cho Codex.
  - Bậc 3 khởi động thật language server; smoke grep theo ngôn ngữ thật của project; gộp thang
    8 bậc và smoke 4 tầng thành một lệnh.
  - Lệnh hook in ra dùng đường dẫn tuyệt đối của plugin.
  - Tự khởi tạo bộ tìm kiếm ở đầu project: dò rẻ ở `SessionStart`, phần đắt chạy nền.
  - Ghi quyết định kiến trúc "điểm chặn thứ hai" vào `docs/kien-truc.md`; mã nhắc mới `TDQ:SEARCH`.
- **Ngoài phạm vi:**
  - Sửa lỗi `path` của lumen MCP (`k value … 8192 > 4096`) — lỗi của lumen 0.0.42, không phải
    của repo này. Cổng chỉ không bao giờ gợi ý dùng `path`.
  - Chặn `Read`/`Glob` — đọc một file đã biết tên không phải tìm kiếm.
  - Cài phụ thuộc NGOÀI danh sách đã khai của `tdq-setup` — vẫn chỉ ghi nợ và nhắc.
  - Docstring/hướng dẫn trong `scripts/*.py` có dòng `python3 scripts/…` — đó là tài liệu dev
    đọc trong repo, không phải chuỗi máy in cho agent.
  - Host OpenCode và Antigravity.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| research web | BỎ | đổi thành trinh sát CHẠY THẬT `codex-cli 0.155.1` ở P1 của plan |
| interview | CÓ (đã chạy) | 5 câu thiết kế + 1 yêu cầu bổ sung, chốt ở brief `## Hỏi đáp` |
| qc độc lập (agent) | BỎ | mức `full` không gọi |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Cổng tìm kiếm | `hooks/scripts/search_gate.py` | lần tìm đoán mò khi request chưa hỏi tầng khái niệm → `deny` kèm lý do nêu đúng công cụ thay thế |
| 2 | Cổng không chặn oan | nt | lọc danh sách file (`git ls-files \| grep`), tên có nguyên văn trong prompt, và mọi lần tìm nằm trong cửa sổ mở khoá → đi qua im lặng |
| 3 | Cổng không gây kẹt | nt | tầng khái niệm chưa sẵn sàng (đang index, ollama tắt) → không chặn, chỉ nói tầng nào đang dựng |
| 4 | Sổ tầng khái niệm theo request | `docs/tdq/.tdq-search.jsonl` (gitignore) | một lần gọi lumen/LSP/`graphify query` được ghi; token định danh của prompt gần nhất được ghi; sổ sống qua nhiều lượt, không bị prompt mới xoá |
| 5 | Cổng chạy trên Codex | `.codex-plugin/plugin.json` hoặc `.codex/hooks.json` theo kết quả trinh sát | chạy thật một lượt Codex grep đoán mò → bị `deny` với lý do |
| 6 | Codex có lumen + LSP | `tdq-setup` ghi `~/.codex/config.toml` (có backup) | `codex mcp list` thấy cả hai |
| 7 | Bậc 3 thật | `scripts/tdq_lsp.py` | language server không khởi động được → bậc 3 KHÔNG đạt, kèm lỗi của server |
| 8 | Smoke grep thật | `scripts/tdq_setup.py` | trên project TypeScript (excalidraw) smoke grep ĐẠT |
| 9 | Một lệnh kiểm duy nhất | `tdq_lsp.py check` | lệnh kiểm in cả 8 bậc và smoke 4 tầng; tổng chỉ ĐẠT khi cả hai đạt |
| 10 | Đường dẫn tuyệt đối | các hook + dòng `Command:` của `tdq_state.py` | chạy hook với cwd là project khác → mọi lệnh in ra trỏ tới file có thật |
| 11 | Tự khởi tạo ở đầu project | `hooks/scripts/session_start.py` + `scripts/tdq_setup.py --nen` | project chưa có index/đồ thị → phiên mới tự kích hoạt dựng nền, hook trả về trong ngân sách thời gian của nó |
| 12 | Không chạy chồng | nt | mở hai phiên liền nhau → chỉ một tiến trình dựng nền |
| 13 | Quyết định kiến trúc | `docs/kien-truc.md` + `reminder-codes.md` | có dòng chốt ngày 2026-10-03 về điểm chặn thứ hai; mã `TDQ:SEARCH` có trong danh sách đóng |
| 14 | Phép đo phát lại | báo cáo QC | phát lại phiên excalidraw: số lần bắt đúng, số lần bắt oan |
| 15 | Luật mở đầu | `hooks/scripts/search_gate.py` | request chưa gọi tầng khái niệm, lần tìm code đầu tiên là grep một tên KHÔNG có trong prompt → `deny` |
| 16 | Ngoại lệ tên đã biết | nt | tên có nguyên văn trong prompt gần nhất của user → đi qua dù chưa gọi tầng khái niệm |
| 17 | Mở khoá có hạn | nt | sau N lần tìm kể từ lần gọi tầng khái niệm gần nhất, lần tìm đoán mò kế tiếp lại bị `deny` |

## 2b. Ranh giới module

| module | vùng file (mã; file test nằm ở plan) | phụ thuộc module | đầu ra §2 nào |
|---|---|---|---|
| cong-tim | `hooks/scripts/search_gate.py`, `hooks/hooks.json` | so-khai-niem | 1, 2, 3, 15, 16, 17 |
| so-khai-niem | `hooks/scripts/_common.py`, `hooks/scripts/search_observe.py` | không | 4 |
| codex | `.codex-plugin/plugin.json`, `.codex/hooks.json`, `scripts/tdq_codex_mcp.py` | cong-tim | 5, 6 |
| kiem-that | `scripts/tdq_lsp.py`, `scripts/tdq_setup.py` | không | 7, 8, 9 |
| duong-dan | `hooks/scripts/edit_gate.py`, `hooks/scripts/prompt_context.py`, `hooks/scripts/bash_gate.py`, `scripts/tdq_state.py` | không | 10 |
| tu-khoi-tao | `hooks/scripts/session_start.py` | kiem-that | 11, 12 |
| ho-so | `docs/kien-truc.md`, `skills/tdq-conventions/references/reminder-codes.md`, `skills/tdq-setup/references/uu-tien-tim-kiem.md` | cong-tim | 13 |

`tdq_setup.py` thuộc riêng module `kiem-that`; cờ `--nen` mà `tu-khoi-tao` gọi là một hàm được
thêm vào cùng file đó, nên `tu-khoi-tao` khai phụ thuộc `kiem-that` thay vì khai chung đường dẫn.

## 3. Cách tiếp cận & lý do

- **Chọn: ba luật, xét theo thứ tự, luật nào khớp trước thì quyết.**
  1. **Miễn:** lọc danh sách file (`ls`/`git ls-files`/`find` nối vào `grep`), và chuỗi tìm có
     nguyên văn trong prompt gần nhất của user → đi qua.
  2. **Luật mở đầu:** request chưa từng gọi tầng khái niệm → mọi lần tìm code khác đều `deny`.
  3. **Mở khoá có hạn:** đã gọi tầng khái niệm, nhưng đã quá N lần tìm kể từ lần gọi gần nhất VÀ
     mẫu có hình đoán mò (≥ 3 nhánh `\|`/`|`, hoặc câu tự nhiên ≥ 3 từ) → `deny`. Còn trong cửa sổ,
     hoặc mẫu là một tên đơn → đi qua.
- **Vì:** phiên thật cho thấy một lần grep đơn lẻ không nói được agent đang hỏi gì — lượt 7 grep
  `fileHandle`, một tên agent tự đoán nhưng trông y hệt tên đã biết. Nên luật mở đầu không xét
  hình dạng, mà xét **nguồn gốc** của cái tên: có trong prompt của user thì là tên đã biết; không
  có thì phải hỏi tầng khái niệm trước. File `docs/tdq/.tdq-prompt-last.json` hiện có chỉ lưu
  **mã băm** của prompt (đo 2026-10-03: khoá `session`, `digest`), nên không dùng được. Hook ghi
  nhận của cổng sẽ bắt thêm `UserPromptSubmit` và lưu **tập token có dạng định danh** của prompt
  gần nhất — không lưu nguyên văn, vì cổng chỉ cần biết một cái tên có từng xuất hiện hay không.
  Sau lần mở khoá, hình dạng đoán mò mới là tín hiệu — tên đơn trong cửa sổ là chỗ grep đúng luật.
- **Cái giá của luật mở đầu:** một tên agent biết từ output của tool (thông báo lỗi, kết quả lumen)
  nhưng không có trong prompt sẽ bị chặn ở lần tìm đầu. Cái giá đó bằng đúng một lần gọi lumen
  (~1 s), và lời `deny` nói rõ phải gọi gì — rẻ hơn nhiều so với để lọt một chuỗi tìm sai hướng.
- **Sổ riêng theo request, không dùng sổ lượt.** Bài học của cổng đọc lại (2026-10-02): sổ lượt
  bị xoá ở mỗi prompt, nên ký ức dựng trên nó mất ngay lượt sau.
- **Ghi nhận tầng khái niệm bằng hook `PostToolUse` trên chính lần gọi lumen/LSP/graphify** —
  bằng hiệu ứng, không tin lời agent tự khai.
- **Tự khởi tạo: dò rẻ đồng bộ, dựng đắt chạy nền.** Index lumen đo được 11 phút trên excalidraw;
  hook không được chờ chừng đó.
- **Đã loại:**
  - Chặn cứng mọi grep trước lumen — vì chặn cả tên chính xác, user đã chọn 1A.
  - Chỉ nhắc — vì user nói "buộc phải tuân theo", và Codex chỉ có `deny`.
  - Phân loại câu hỏi bằng model — vì hook phải chạy trong vài chục ms trước MỌI lệnh Bash.

## 3b. Năng lực & công cụ

| skill | nguồn | phán quyết | dùng ở đâu / lý do loại |
|---|---|---|---|
| tdq-setup | plugin:tdq-workflow | DÙNG | đầu ra 6-9, 11 — module chính bị sửa |
| code-review | built-in | DÙNG | soát lỗi đúng-sai trước phase qc |
| simplify | built-in | DÙNG | rút gọn sau khi các module xong |
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions | plugin:tdq-workflow | NỀN | skill khung đang chạy |
| đã xét 17 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt được bằng `TDQ_LOG=0` — cho mọi
  file mã mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule
  ngôn ngữ trong `skills/tdq-build/references/rules/`.
- Chú thích, docstring và chuỗi máy in ra viết tiếng Anh (`docs/kien-truc.md` 2026-08-22).
- Hook không bao giờ làm vỡ lệnh của agent vì lỗi của chính nó: mọi lỗi I/O, lỗi parse → cho đi
  qua và ghi log.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ những dòng việc này chạm tới):

- "2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do "chưa
  duyệt"." — việc này thêm một `deny` có lý do KHÁC ("chưa hỏi tầng khái niệm"). Ghi dòng chốt
  2026-10-03 để hai dòng không mâu thuẫn.
- "`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`" — `search_gate.py`
  đọc trạng thái sẵn sàng qua file mốc, không import `scripts/`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — đúng, ngoại lệ duy nhất là
  adapter Codex theo dòng 2026-09-21.
- "2026-08-22: … chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết
  TIẾNG ANH" — áp cho mọi file mới.

| rủi ro | ảnh hưởng | cách giảm |
|---|---|---|
| Cổng bắt oan grep tên chính xác | agent bị chặn khi đang làm đúng → user tắt cổng | miễn theo nguồn gốc (prompt) + cửa sổ mở khoá; phép phát lại ở QC đếm số bắt oan |
| Luật mở đầu chặn tên agent biết từ output của tool | thêm một lần gọi lumen (~1 s) | lời `deny` nói đúng lệnh cần gọi; chấp nhận vì rẻ hơn để lọt chuỗi tìm sai hướng |
| Cửa sổ N quá ngắn hoặc quá dài | quá ngắn: chặn liên tục; quá dài: lại lọt như spec 1.0 | N chốt ở plan bằng phép phát lại, không đoán |
| Tầng khái niệm chết → cổng chặn mà không có đường đi | agent kẹt | không chặn khi file mốc sẵn sàng nói tầng khái niệm chưa dựng xong |
| Codex không cho plugin khai hook | đầu ra 5 không đạt qua plugin | trinh sát P1 trước; đường lùi là `.codex/hooks.json` cấp project do `tdq-setup` ghi |
| Hook Codex phải được trust | cổng không chạy dù đã khai | `tdq-setup` in đúng bước trust; QC chạy thật có cờ bỏ qua trust cho một lần |
| Dựng nền chạy chồng hoặc treo | CPU/RAM bị chiếm | khoá pid + trần thời gian; khoá chết (pid không còn) thì được lấy lại |
| Ghi `~/.codex/config.toml` làm hỏng cấu hình user | Codex không chạy | backup trước khi ghi; chỉ THÊM mục, không sửa mục có sẵn; idempotent |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện pass |
|---|---|---|
| Q1 | Chặn đoán mò trước tầng khái niệm | mẫu ≥ 3 nhánh, request chưa hỏi lumen/LSP/graphify → `deny` kèm lý do nêu đúng công cụ |
| Q2 | Không chặn tên chính xác trong cửa sổ | đã gọi tầng khái niệm, còn trong cửa sổ N → grep một định danh đơn đi qua |
| Q3 | Không chặn lọc danh sách file | `git ls-files \| grep -E '\.tsx?$'` → đi qua, kể cả khi chưa gọi tầng khái niệm |
| Q4 | Mở khoá sau tầng khái niệm | sau một lần gọi lumen trong request → mẫu đoán mò đi qua trong cửa sổ N |
| Q5 | Sổ sống qua lượt | xoá sổ lượt (như prompt mới) → sổ tầng khái niệm còn nguyên |
| Q6 | Không gây kẹt | tầng khái niệm chưa sẵn sàng → không `deny` |
| Q7 | Cổng rẻ | không spawn tiến trình con, không đọc file code của project |
| Q8 | Cổng không làm vỡ lệnh | payload hỏng, sổ hỏng → đi qua, thoát 0 |
| Q9 | Codex bị chặn thật | một lượt `codex exec` chạy grep đoán mò → bị `deny` |
| Q10 | Codex có công cụ | sau `tdq-setup`, `codex mcp list` thấy lumen và LSP; cấu hình cũ còn nguyên |
| Q11 | Bậc 3 thật | language server không khởi động → bậc 3 không đạt, kèm lỗi |
| Q12 | Smoke grep đa ngôn ngữ | project chỉ có TypeScript → smoke grep đạt |
| Q13 | Một lệnh kiểm | lệnh kiểm in 8 bậc + 4 tầng; một tầng trượt → tổng không đạt |
| Q14 | Đường dẫn tuyệt đối | hook chạy với cwd là project khác → mọi lệnh in ra trỏ tới file có thật |
| Q15 | Tự khởi tạo | project chưa sẵn sàng → `SessionStart` kích hoạt dựng nền và trả về trong ngân sách thời gian |
| Q16 | Không chạy chồng | hai lần kích hoạt liền nhau → một tiến trình dựng |
| Q17 | Quyết định kiến trúc | `kien-truc.md` có dòng chốt 2026-10-03; `TDQ:SEARCH` có trong danh sách đóng và bảng mã |
| Q18 | **Phát lại phiên thật** | các lần tìm của phiên excalidraw: **lượt 7 và lượt 9 bị bắt**, mọi lần đoán mò khi cửa sổ đã hết bị bắt, **0 lần bắt oan một lần lọc danh sách file** |
| Q21 | Luật mở đầu | request chưa gọi tầng khái niệm; lần tìm đầu là grep một tên không có trong prompt → `deny` |
| Q22 | Ngoại lệ tên đã biết | tên có nguyên văn trong prompt gần nhất → đi qua dù chưa gọi tầng khái niệm; thiếu file prompt → luật mở đầu vẫn áp, không nổ |
| Q23 | Cửa sổ hết hạn | sau N lần tìm kể từ lần gọi tầng khái niệm gần nhất → mẫu đoán mò bị `deny` lại; gọi lumen lần nữa → mở lại |
| Q19 | Ba hệ | trọn bộ test xanh trên Windows và macOS thật; Linux khi máy bật |
| Q20 | Ràng buộc kiến trúc | `scripts/` không import `hooks/`; file mới đúng thư mục |

DoD: 17 đầu ra ở §2 có thật và đo được · Q1–Q23 PASS (Q19 cho phép Linux để ngỏ nếu máy vẫn tắt,
ghi lý do) · trọn bộ test xanh · `doc_lint` và `i18n_check` trên file mới xanh · working log mọi
lượt · CHANGELOG có mục cho bản này.

## 7. Câu hỏi còn mở

Không còn — 5 câu thiết kế và yêu cầu bổ sung đã chốt ở brief `## Hỏi đáp`.
