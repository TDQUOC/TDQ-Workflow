# SPEC — Tự động setup & chứng minh LSP theo module trước khi mở request

Ngày: 2026-10-08 · Bản: 1.1 · Brief: ../brief/2026-10-07-2225-tu-dong-setup-lsp.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

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

- Mục tiêu: ở mọi project dùng TDQ, request chỉ mở được khi LSP đã được CHỨNG MINH trả lời đúng cho
  từng module (ngôn ngữ + gốc) của project, đi đúng đường MCP mà agent dùng. Thiếu gì thì TDQ tự cài,
  không hỏi. Ca gốc 2026-10-07 (`start_lsp` thiếu `language_id` → TS crash / `No Project` trên repo
  Python) không còn xảy ra được.
- Trong phạm vi:
  - Dò module LSP của project (repo 1 ngôn ngữ = 1 dòng; nhiều ngôn ngữ / monorepo = nhiều dòng).
  - Kịch bản kiểm theo module, agent chạy qua MCP, kết quả ghi bằng lệnh, có hạn dùng.
  - Cổng cứng ở `tdq_state.py init` + lối thoát `--bo-qua-lsp "<lý do>"`.
  - Hook PreToolUse chặn `mcp__lsp__start_lsp` thiếu `language_id` / sai cặp (gốc, ngôn ngữ).
  - Tự cài toàn bộ phụ thuộc, kể cả agent-lsp (trình cài `curl | sh`), và cấu hình gốc import.
  - Dọn `daemon-broker` mồ côi của agent-lsp; báo bộ nhớ commit thấp.
  - **Ngôn ngữ mới xuất hiện sau này** (vd. ban đầu chỉ Python, sau thêm JS/HTML): tự phát hiện, tự cài
    language server còn thiếu, tự thêm vào cấu hình MCP `lsp`, rồi kiểm lại module mới trước khi mở request.
  - Luật chữ: intake 1b, `kiem-lsp-hieu-ung.md`, `uu-tien-tim-kiem.md` (luật gọi `start_lsp` theo module).
- NGOÀI phạm vi:
  - Sửa agent-lsp upstream (issue #55 `find_symbol` chỉ hỏi server hiện hành) — chỉ né bằng luật gọi.
  - Tự chỉnh pagefile / cài đặt hệ điều hành — chỉ báo + hướng dẫn.
  - Hook tương đương cho Codex / OpenCode / Antigravity — cổng `init` vẫn áp cho mọi host vì nằm trong
    CLI; riêng hook `start_lsp` chỉ khai cho Claude Code ở request này.
  - Tier `nhỏ` (không gọi `init`) — không bị cổng chặn.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | đã trả lời Q1–Q5; plan chỉ tra thêm cách cài agent-lsp trên Windows |
| Interview | CÓ (xong 2 vòng) | 6/6 câu đã có trả lời |
| spec → plan | CÓ | khung bất biến |
| implement chia subagent | BỎ | các module dùng chung `tdq_lsp.py`; chia ra sẽ đụng file |
| QC `full` | CÓ | user chọn 6A |
| QC độc lập (agent) | BỎ | mức `full` không yêu cầu; code-review built-in dùng ở QC |
| report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Dò module + kịch bản kiểm + ghi kết quả + hạn dùng | `scripts/lsp_module.py` (mới); lệnh `tdq_lsp.py module`, `tdq_lsp.py kich-ban`, `tdq_lsp.py ghi-kiem` | unit test trên 4 cây mẫu: 1 ngôn ngữ, Python+HTML, TS 2 tsconfig, Python+TS |
| 2 | Bậc 8 "LSP theo module" trong thang `check`; tổng ĐẠT chỉ khi mọi module có kết quả ĐẠT còn hạn | `scripts/tdq_lsp.py` | test: module chưa kiểm / hết hạn / TRƯỢT → exit 3 |
| 3 | Cổng cứng ở `init` + `--bo-qua-lsp "<lý do>"` (lý do ghi vào state, report đọc ra) | `scripts/tdq_state.py` | test: init bị từ chối khi bậc 8 chưa ĐẠT; qua được với cờ; repo không có ngôn ngữ cần LSP → không chặn |
| 4 | Hook chặn `start_lsp` thiếu `language_id` / sai cặp (gốc, ngôn ngữ) | `hooks/scripts/lsp_gate.py` (mới), `hooks/hooks.json` | test hook: 4 ca deny/allow; lời deny in đúng lệnh `start_lsp` cần gọi |
| 5 | Tự cài mọi phụ thuộc kể cả agent-lsp, không hỏi | `scripts/tdq_setup.py` | test với runner giả: lệnh cài agent-lsp được chạy không qua shell nối ống |
| 6 | Dọn `daemon-broker` mồ côi + báo commit thấp | `scripts/lsp_module.py` (phần tiến trình), gọi từ `tdq_setup.py` | test với danh sách tiến trình giả: chỉ tắt đúng broker mồ côi |
| 8 | Phát hiện ngôn ngữ mới → cài server thiếu → thêm vào cấu hình MCP `lsp` (có sao lưu) → buộc kiểm lại | `scripts/lsp_module.py` (vân tay tập ngôn ngữ), `scripts/tdq_setup.py` (cài + ghi cấu hình MCP), `hooks/scripts/session_start.py` (dựng nền khi tập ngôn ngữ đổi) | test: cây mẫu Python thêm `.js`+`.html` → bảng có module mới, lệnh cài + dòng MCP mới được sinh, `init` bị chặn tới khi module mới ĐẠT |
| 7 | Luật chữ + changelog + version 0.59.0 + dòng `Đã chốt` | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/kiem-lsp-hieu-ung.md`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `docs/kien-truc.md` | `doc_lint`, `i18n_check` xanh |

## 2b. Ranh giới module

Ranh giới lấy từ quan hệ gọi thật: `tdq_setup.py` import `tdq_lsp` (`chay_kiem`, `chay_smoke`, `_run`);
`session_start.py` gọi `tdq_setup.py --nen` bằng tiến trình; `search_gate.py` chỉ đọc mốc
`search_rules.MOC_SAN_SANG`; `tdq_state.py` không import `tdq_lsp` hiện nay.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Lõi module | `scripts/lsp_module.py` | không | 1, 6, 8 |
| Thang & CLI | `scripts/tdq_lsp.py` | Lõi module | 1, 2 |
| Cổng init | `scripts/tdq_state.py` | Lõi module | 3 |
| Hook | `hooks/scripts/lsp_gate.py`, `hooks/hooks.json` | Lõi module (đọc file bảng, không import `scripts/` ngoài mẫu hook sẵn có) | 4 |
| Tự cài | `scripts/tdq_setup.py` | Lõi module, Thang & CLI | 5, 6, 8 |
| Dựng nền | `hooks/scripts/session_start.py` | Lõi module (đọc file bảng) | 8 |
| Luật & phát hành | `skills/tdq-intake/`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `docs/kien-truc.md` | tất cả | 7 |

## 3. Cách tiếp cận & lý do

- Chọn:
  1. **Module = (ngôn ngữ, gốc).** Gốc = thư mục có file mốc: TS/JS `tsconfig.json` > `jsconfig.json` >
     `package.json`; Python `pyrightconfig.json` > `pyproject.toml` > `setup.py`; Go `go.mod`; Rust
     `Cargo.toml`; ngôn ngữ khác → gốc repo. File nguồn thuộc gốc sâu nhất chứa nó; module < 3 file
     nguồn gộp lên module cha cùng ngôn ngữ. Bảng ghi `docs/tdq/.tdq-lsp-module.json`.
  2. **Kịch bản kiểm qua MCP thật**, mỗi module: `start_lsp(root, language_id)` → `open_document` một file
     mẫu → `find_references` tại một symbol có thật dùng ở ≥ 2 file → so số file với grep. ĐẠT khi
     LSP ≥ grep. Script chọn symbol + vị trí + số file grep, in sẵn lời gọi; agent chạy rồi
     `tdq_lsp.py ghi-kiem <module> <số file LSP>` — script tự so, agent không tự phán.
  3. **Hạn dùng**: kết quả còn hạn khi dấu vân tay (mtime file mốc của module + chuỗi cấu hình MCP `lsp`)
     không đổi và chưa quá 24 h. Intake chỉ kiểm lại module hết hạn.
  4. **Cổng ở lệnh `init`** (như cổng R14 ở `approve spec`), không ở hook.
  5. **Hook `lsp_gate.py`**: `deny` khi thiếu `language_id`; khi có bảng mà (root, language_id) không
     khớp dòng nào → `deny`, lời chặn liệt kê các cặp hợp lệ.
  6. **Tự cài**: thêm agent-lsp vào danh sách cho phép; trình cài tải về file tạm rồi chạy, không nối ống
     shell (giữ luật `_chay_lenh` không shell). Windows: cách cài chốt ở plan sau khi tra bản phát hành.
     Cài hỏng → ghi nợ, `init` vẫn bị chặn (lối thoát `--bo-qua-lsp`).
  7. **Broker mồ côi** = `agent-lsp daemon-broker` có gốc không còn tồn tại, hoặc trùng cặp
     (gốc, ngôn ngữ) với broker mới hơn. Chỉ tắt tiến trình agent-lsp. Commit trống < 4 GB → cảnh báo
     + hướng dẫn tăng pagefile.
  8. **Ngôn ngữ mới.** Vân tay của bảng module gồm cả TẬP ngôn ngữ của project. Ba điểm cùng so tập này:
     (a) SessionStart: tập đổi so với mốc → bắn dựng nền `tdq_setup.py --nen`; (b) intake 1b: chạy
     `tdq_setup.py` (tự cài, không hỏi) trước kịch bản; (c) cổng `init`: module chưa có kết quả → chặn.
     `tdq_setup.py` với mỗi ngôn ngữ thiếu: cài server (danh sách `LANG_SERVER` sẵn có) → thêm dòng
     `<lang>:<đường dẫn server>,<cờ>` vào `args` của server MCP `lsp` (sao lưu `.truoc-tdq.bak` trước khi
     ghi, như với file của plugin khác) → báo phải kết nối lại MCP (`/mcp` hoặc phiên mới) vì Claude Code
     chỉ đọc cấu hình MCP lúc khởi động → kịch bản module mới chạy sau khi kết nối lại.
- Vì: agent-lsp chạy song song mọi server, tool theo file tự định tuyến theo đuôi; chỉ `find_symbol` và
  việc chọn server khi thiếu `language_id` là sai (research Q1, Q2). `agent-lsp doctor` ĐẠT trong cả 3 ca
  lỗi đo được 2026-10-07 → chỉ kiểm qua MCP thật mới bắt được (user chọn 3A).
- Đã loại:
  - Script tự nói LSP stdio với server (3B) — bỏ qua agent-lsp nên mù với lỗi chọn server.
  - Chặn trong hook UserPromptSubmit — trái dòng 2026-07-29 và chặn cả câu hỏi tier `nhỏ`.
  - Tham số `scope` của `start_lsp` — ghi đè `tsconfig.json` ở gốc (research Q5).

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | NỀN | khung request đang chạy |
| code-review | built-in | DÙNG | QC: soát diff cuối |
| simplify | built-in | DÙNG | QC: dọn code trước khi báo |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: mọi lệnh mới ghi một dòng ISO timestamp ra stderr; tắt bằng `--khong-log`
  hoặc `TDQ_LOG=0` như các script sẵn có.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule Python trong
  `skills/tdq-build/references/rules/`.
- Chỉ dùng stdlib (như mọi file trong `scripts/`).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ:
- "`hooks/` được gọi `scripts/`; `scripts/` không được import `hooks/`" — chạm ở `lsp_gate.py`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — lý do `--bo-qua-lsp` ghi qua chính lệnh `init`;
  bảng module là file riêng `docs/tdq/.tdq-lsp-module.json`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — `lsp_module.py`, `lsp_gate.py`.
- "2026-07-29: hook chỉ nhắc …, không trả `deny` vì lý do 'chưa duyệt'" — `lsp_gate.py` chặn vì lý do khác
  (lời gọi sai tham số); cổng cứng nằm ở lệnh `init`, không ở hook.
- Hub `main()`/`cli()` của `tdq_state.py` — sửa nhánh `init`, khai ở dòng `Chạm:` của plan.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Monorepo lớn (excalidraw ~13 module TS) → lần đầu nhiều lời gọi MCP | intake lần đầu chậm | hạn dùng 24 h + vân tay; lần sau chỉ module hết hạn |
| Không tìm được symbol dùng ở ≥ 2 file trong module nhỏ | module không kiểm được | lấy symbol dùng ≥ 2 lần trong 1 file; vẫn không có → module ghi "không đủ mẫu", không chặn |
| Bộ nhớ commit thấp làm server crash lúc kiểm | init bị chặn dù cấu hình đúng | lời chặn nêu rõ commit trống + hướng dẫn pagefile; `--bo-qua-lsp` |
| Tự chạy `curl | sh` từ mạng (user chọn 2B) | chạy mã tải về | chỉ URL cố định của agent-lsp trong danh sách cho phép; ghi log lệnh và băm file tải về |
| Cấu hình MCP mới chưa được nạp trong phiên đang chạy | module mới TRƯỢT dù đã cài | lời chặn nói rõ: gõ `/mcp` kết nối lại `lsp` rồi chạy lại kịch bản |
| Ghi hỏng `~/.claude.json` | mất cấu hình Claude Code | ghi nguyên tử + sao lưu trước; chỉ sửa đúng mảng `args` của server `lsp` |
| Tắt nhầm broker phiên khác đang dùng | phiên kia mất LSP một lượt | chỉ tắt broker có gốc đã mất hoặc trùng cặp với broker mới hơn; agent-lsp tự bật lại |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Dò module đúng | 4 cây mẫu ra đúng bảng mong đợi; claudecodeui thật ra 2 module TS (`.`→`src/`, `server/`) | — | — |
| Q2 | Thời gian dò module | ≤ 1 giây trên TDQ_Monitor_Online (7 994 file) | 0,31 s đo 2026-10-08 (os.walk + bỏ `node_modules`), biên 3× | đệm bảng theo mtime file mốc |
| Q3 | Cổng `init` | từ chối khi bậc 8 chưa ĐẠT; qua với `--bo-qua-lsp`; lý do hiện trong report | — | — |
| Q4 | Hook `lsp_gate.py` | deny đúng 2 ca, allow đúng 2 ca; thời gian chạy ≤ 200 ms | hook `ask_gate.py` 124–140 ms (5 lần, 2026-10-08) | gộp vào `search_observe.py` đang khớp `mcp__lsp__.*` |
| Q5 | Ca gốc tái hiện | trên bản sao repo Python: `start_lsp` thiếu `language_id` bị chặn; kịch bản module ĐẠT | — | — |
| Q6 | Repo nhiều ngôn ngữ thật | `tdq_lsp.py check` trên TDQ-Workflow và claudecodeui: mọi module ĐẠT sau khi chạy kịch bản | — | — |
| Q9 | Ngôn ngữ mới | cây mẫu Python + thêm `.js`/`.html`: bảng thêm module, dòng MCP mới sinh đúng, `init` chặn tới khi module mới ĐẠT; dòng MCP cũ giữ nguyên | — | — |
| Q7 | Trọn bộ unit test | xanh | — | — |
| Q8 | `doc_lint`, `i18n_check` | exit 0 | — | — |

DoD: Q1–Q9 PASS · changelog 0.59.0 · dòng `Đã chốt` mới trong `docs/kien-truc.md` · report.

## 7. Câu hỏi còn mở

(rỗng)
