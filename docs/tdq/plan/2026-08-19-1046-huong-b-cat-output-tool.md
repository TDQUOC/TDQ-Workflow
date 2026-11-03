# PLAN — Hướng B: cắt output tool

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-1046-huong-b-cat-output-tool.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — đề xuất, NGƯỢC với số đo, và nói rõ vì sao: `tdq_bench.py mo-phong` trên chính plan này cho `Thắng: đội (chênh 16.2 phút)` (19 task · 5 đợt · giao 8 · hệ số agent 1.5), nhưng spec §1b ĐÃ DUYỆT ghi "Chia subagent: BỎ — phiên hiện tại cấm gọi AgentTool khi user không yêu cầu". Muốn lấy 16,2 phút đó thì user chọn mode đội ở cổng duyệt — đó cũng chính là lời yêu cầu gỡ ràng buộc.
Trạng thái plan: HOÀN THÀNH · Mode: main (user chọn A lúc duyệt plan)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Thước đo đếm đúng
- P2 — Luật
- P3 — Hook nhắc
- P4 — Cấu hình nền tảng
- P5 — Portable, đo lại, sổ sách
- P6 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Test phải ĐỎ trước.** Dán cả kết quả đỏ lẫn kết quả xanh; không có bằng chứng đỏ thì
   task chưa được tick.
8. **Cấm sửa tay** `portable_claude/` và `portable_codex/` — chỉ sinh lại bằng script.
9. **Cấm đặt chỉ tiêu giảm %** trong luật mới, và cấm bỏ bớt 5 ca bắt buộc đọc lại
   (spec §3 và Q6): cắt vào đó là cắt vào chất lượng.
10. **Cấm tuyên bố mức tiết kiệm** khi chưa đo lại bằng thước đo đã sửa ở P1.

## P1 — Thước đo đếm đúng

- Dùng: `scripts/token_audit.py`
  - Nạp: đọc file trước khi sửa, chạy lại sau mỗi task của P1.
  - Để: đếm carry-cost bằng tokenizer thật thay cho ước lượng ký tự/4, và phân rã hành vi tool.
  - Ra: `scripts/token_audit.py` đã sửa + bảng số dùng cho đầu ra 11 của spec.
  - Kiểm: `python3 scripts/token_audit.py --sessions 5 --top 5` thoát 0 và in đủ bảng mới.
  - Không dùng cho: đo thân skill theo phase — việc đó của `scripts/skill_tokens.py`.

- [x] **T1.1** (e10m) Viết test khoá: đường tính chính không được dùng hằng số ký tự/4; thiếu venv tokenizer thì thoát khác 0 kèm câu hướng dẫn, cấm âm thầm ước lượng — Test: `python3 -m pytest tests/test_token_audit.py -q` đỏ đúng 2 ca mới
  - Chạm: `tests/test_token_audit.py`
- [x] **T1.2** (e20m) Sửa `token_audit.py` đếm bằng `anthropic_tokenizer` trong venv `.venv-tokens/`, có cache theo nội dung để không đếm lại — Test: hai ca của T1.1 xanh
  - Chạm: `scripts/token_audit.py`, `tests/test_token_audit.py`
  - Cần: T1.1
- [x] **T1.3** (e10m) Viết test khoá bảng phân rã hành vi: mỗi tool có n, trung vị, p90, p99, max; có tỉ lệ `Read` mang `offset`/`limit` và tỉ lệ `Read` đọc lại trong cùng session — Test: `python3 -m pytest tests/test_token_audit.py -q` đỏ đúng các ca mới
  - Chạm: `tests/test_token_audit.py`
  - Cần: T1.2
- [x] **T1.4** (e18m) Thêm bảng phân rã hành vi vào `token_audit.py` — Test: các ca của T1.3 xanh
  - Chạm: `scripts/token_audit.py`, `tests/test_token_audit.py`
  - Cần: T1.3
- [x] **T1.5** (e6m) Đo thời gian chạy thật trên 5 session — Test: `time python3 scripts/token_audit.py --sessions 5 --top 5` xong dưới 60 giây, dán số đo — **đo được 30,6 giây** (5 session, 17,78s user + 2,35s sys)
  - Cần: T1.4

- [x] **T1.6** (e15m) *(thêm sau khi duyệt plan — chính bảng của T1.4 lòi ra lỗi này, sửa ngay vì nó thuộc đúng đầu ra 1–3 "thước đo đếm đúng")* Khối `image` trong tool_result đang bị tính bằng độ dài chuỗi base64: `mcp__excalidraw__get_canvas_screenshot` ra trung vị 378.014 token/lần, trong khi ảnh 960×1605 chỉ tốn ⌈w/28⌉×⌈h/28⌉ = 2.030 token — sai gấp ~186 lần và sẽ dẫn tới cắt nhầm một năng lực. Đếm ảnh theo công thức patch của tài liệu Anthropic, đọc kích thước thật từ header PNG/JPEG — Test: ca ảnh mới trong `tests/test_token_audit.py` xanh, bảng phân rã đổi số đúng chỗ
  - Chạm: `scripts/token_audit.py`, `tests/test_token_audit.py`
  - Cần: T1.4

**Xong P1 khi**: hai lệnh trên thoát 0, bảng mới in đủ cột, thời gian dưới 60 giây.

## P2 — Luật

- [x] **T2.1** (e12m) Thêm mục phân biệt "đọc lại vì luật" và "đọc lại vì quên" vào `context-budget.md`: giữ nguyên 5 ca bắt buộc, thêm tiêu chí nhận diện lần đọc lại KHÔNG thuộc 5 ca đó — Test: `python3 scripts/doc_lint.py skills/tdq-conventions/references/context-budget.md` thoát 0; grep thấy đủ 5 ca cũ và câu "nghi ngờ thì đọc lại" còn nguyên
- [x] **T2.2** (e8m) Thêm luật trần output cho tool ngoài (MCP) vào cùng file, nêu ngưỡng số và việc phải làm khi vượt — Test: cùng lệnh lint thoát 0; grep thấy tên khoá `MAX_MCP_OUTPUT_TOKENS`
  - Cần: T2.1
- [x] **T2.3** (e5m) Trỏ từ §10 của `tdq-conventions/SKILL.md` sang hai mục mới, giữ dưới trần dòng của rule R6 — Test: `python3 -m pytest tests/test_skill_shape.py -q` xanh và `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` thoát 0
  - Cần: T2.2

**Xong P2 khi**: lint thoát 0 trên cả hai file, test hình dạng skill xanh.

## P3 — Hook nhắc

- [x] **T3.1** (e10m) Viết test khoá: lệnh Bash đọc file lớn mà không giới hạn → có nhắc; lệnh đã có `head`/`tail`/`-n`/`-c` → KHÔNG nhắc; không ca nào trả `deny` — Test: `python3 -m pytest tests/test_bash_gate.py -q` đỏ đúng các ca mới
  - Chạm: `tests/test_bash_gate.py`
- [x] **T3.2** (e15m) Thêm phần nhắc vào `bash_gate.py` theo đúng kiểu quan sát + nhắc sẵn có, dùng mã `[TDQ:*]` mới đặt tên theo luật ở P2 — Test: các ca của T3.1 xanh
  - Chạm: `hooks/scripts/bash_gate.py`, `tests/test_bash_gate.py`
  - Cần: T3.1, T2.2
- [x] **T3.3** (e5m) Kiểm hồi quy phần nhắc cũ của hook (`TDQ:GIT`, `TDQ:STATE`) — Test: `python3 -m pytest tests/test_bash_gate.py tests/test_context_hooks.py -q` xanh toàn bộ
  - Cần: T3.2

**Xong P3 khi**: hai lệnh test trên xanh, không ca nào trả `deny`.

## P4 — Cấu hình nền tảng

- [x] **T4.1** (e5m) Backup `~/.claude/settings.json` — Test: md5 hai file bằng nhau và bản backup parse được JSON
  - *Đổi cách làm khi thi hành (tự quyết, lý do ở đây):* `settings.json` chứa API key thật. Bản NGUYÊN BYTE để ở `~/.claude/settings-backup-2026-08-19-huong-b.json` (ngoài repo, md5 khớp gốc); bản trong repo `docs/tdq/audit/settings-backup-2026-08-19-huong-b.json` giữ đủ tên khoá nhưng che giá trị của mọi khoá có KEY/TOKEN/SECRET/PASSWORD. Chép nguyên byte vào repo là commit thẳng credential lên git.
- [x] **T4.2** (e10m) Ghi `MAX_MCP_OUTPUT_TOKENS` vào `~/.claude/settings.json` bằng `json.load` → sửa dict → `json.dump`, giữ nguyên mọi khoá sẵn có — Test: parse lại được; khoá mới có mặt; danh sách khoá cấp cao mất so với backup là rỗng
  - Cần: T4.1

**Xong P4 khi**: settings parse được, khoá mới có mặt, không mất khoá nào.

## P5 — Portable, đo lại, sổ sách

- Dùng: `scripts/build_portable.py`
  - Nạp: chạy sau khi P1–P3 xong, trước khi viết report.
  - Để: sinh lại hai bản portable từ `skills/` + `scripts/` + `hooks/`.
  - Ra: `portable_claude/`, `portable_codex/` đã cập nhật kèm `manifest.json`.
  - Kiểm: `python3 scripts/build_portable.py` thoát 0.
  - Không dùng cho: sửa nội dung luật — nó chỉ sao chép, mọi sửa đổi làm ở `skills/`.

- Dùng: `scripts/doc_lint.py`
  - Nạp: chạy trên đúng file vừa sửa ở mọi task có chạm tài liệu.
  - Để: giữ tài liệu đúng rule R1–R11.
  - Ra: exit 0 trên từng file đã sửa.
  - Kiểm: `python3 scripts/doc_lint.py <file vừa sửa>` thoát 0.
  - Không dùng cho: lint cả thư mục — vi phạm chính luật "lint đúng file" của request này.

- Dùng: `tdq-spec`, `tdq-plan`, `tdq-build`
  - Nạp: tdq-spec/tdq-plan đã dùng để viết spec+plan này; tdq-build nạp ở đầu phase implement.
  - Để: đưa request đi hết brief → spec → plan → build → QC → report đúng khuôn TDQ.
  - Ra: spec/plan này, rồi 12 đầu ra §2 của spec.
  - Kiểm: `python3 scripts/tdq_state.py next --brief` báo đúng phase sau mỗi cổng duyệt.
  - Không dùng cho: quyết thay user chuyện duyệt hay chọn mode.

- [x] **T5.1** (e8m) Sinh lại hai bản portable và khoá bằng test rằng luật mới cùng script mới có mặt ở cả hai bản — Test: `python3 scripts/build_portable.py` thoát 0 và `python3 -m pytest tests/test_build_portable.py -q` xanh
  - Chạm: `portable_claude/`, `portable_codex/`, `tests/test_build_portable.py`
  - Cần: T1.4, T2.3, T3.2
- [x] **T5.2** (e12m) Đo lại bằng thước đo ĐÃ SỬA cho CẢ HAI mốc trên cùng bộ session, lập bảng trước/sau — Test: bảng có đủ hai mốc đo bằng cùng một cách đếm; ghi rõ phần nào chỉ kiểm chứng được ở phiên mới
  - Cần: T5.1, T4.2
- [x] **T5.3** (e10m) Thêm mục đính chính vào đề án: tiền đề "thước đo chưa tồn tại" sai, và vì sao `BASH_MAX_OUTPUT_LENGTH` bị loại — Test: `python3 scripts/doc_lint.py docs/tdq/audit/de-an-toi-uu-context.md` thoát 0; các mục cũ còn nguyên
  - Cần: T5.2
- [x] **T5.4** (e10m) Viết report, nêu rõ phần chưa kiểm chứng và cách đảo ngược thay đổi cấu hình — Test: `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-19-1046-huong-b-cat-output-tool.md` thoát 0
  - Cần: T5.3

**Xong P5 khi**: bốn lệnh trên thoát 0 và bảng trước/sau có đủ hai mốc.

## P6 — Log & test bắt buộc

- [x] **T6.1** (e6m) Giữ nguyên hợp đồng log sẵn có của hai file mã nguồn bị sửa: log ra stderr, có timestamp ISO, bật mặc định, tắt được bằng biến môi trường của chính file đó — Test: chạy `token_audit.py` với biến tắt log thì stderr rỗng, không tắt thì có timestamp
  - Chạm: `scripts/token_audit.py`, `hooks/scripts/bash_gate.py`
  - Cần: T1.4, T3.2
- [x] **T6.2** (e8m) Chạy toàn bộ test suite đúng một lần và đối chiếu danh sách test đỏ với danh sách trước request — Test: `python3 -m pytest tests -q` không có test đỏ MỚI; test đỏ sẵn có phải chứng minh bằng `git stash`
  - Cần: T6.1

## Cụm song song

Ba cụm tách rời được, cộng một cụm khoá đuôi:

- Cụm A — thước đo: T1.1 → T1.5, chỉ chạm `scripts/token_audit.py` và test của nó.
- Cụm B — luật: T2.1 → T2.3, chỉ chạm tài liệu trong `skills/tdq-conventions/`.
- Cụm C — cấu hình: T4.1 → T4.2, chỉ chạm `~/.claude/settings.json` và file backup.
- Cụm khoá đuôi — P3 cần T2.2 (mã nhắc phải khớp luật), P5 và P6 cần cả ba cụm trên xong.

Trần tốc độ của mode đội vì vậy là 3 luồng, và luồng dài nhất (cụm A, 64 phút) vẫn phải
đợi trước khi P5 chạy được.

## Definition of Done

Trỏ về §6 của spec, mỗi dòng một lệnh kiểm:

| # | Hạng mục | Lệnh kiểm |
|---|---|---|
| Q1 | Thước đo đếm đúng | `python3 -m pytest tests/test_token_audit.py -q` xanh; chạy khi thiếu venv thoát khác 0 |
| Q2 | Bảng phân rã đủ cột | `python3 scripts/token_audit.py --sessions 5 --top 5` in đủ n/trung vị/p90/p99/max + hai tỉ lệ `Read` |
| Q3 | Thước đo đủ nhanh | `time python3 scripts/token_audit.py --sessions 5 --top 5` dưới 60 giây |
| Q4 | Test khoá thật | dán kết quả đỏ và xanh của T1.1, T1.3, T3.1 |
| Q5 | Hook nhắc đúng chỗ | `python3 -m pytest tests/test_bash_gate.py -q` xanh, không ca nào trả `deny` |
| Q6 | Luật không cắt chất lượng | grep `context-budget.md` thấy đủ 5 ca bắt buộc và câu "nghi ngờ thì đọc lại"; không có chỉ tiêu giảm % |
| Q7 | Backup hợp lệ | `md5` backup bằng `md5` bản gốc lúc T4.1 |
| Q8 | Settings hợp lệ sau khi ghi | parse lại JSON không lỗi; khoá mới có mặt; khoá cấp cao mất so với backup là rỗng |
| Q9 | Ba bản đồng bộ | `python3 scripts/build_portable.py` thoát 0; `python3 -m pytest tests/test_build_portable.py -q` xanh |
| Q10 | Test suite | `python3 -m pytest tests -q` không có test đỏ mới |
| Q11 | Số trước/sau trung thực | bảng ở đề án có hai mốc đo bằng cùng thước đo mới, phần chưa kiểm chứng ghi rõ |
| Q12 | Đề án được đính chính | `python3 scripts/doc_lint.py docs/tdq/audit/de-an-toi-uu-context.md` thoát 0 và mục đính chính có mặt |
