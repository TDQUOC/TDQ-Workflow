# Brief — Tự động kiểm & setup LSP trước khi mở request
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay lúc nãy có ghi nhận case gọi lsp fail có vẻ trong typescript thì hãy set vào tdq workflow giúp tôi là ở mỗi project trươcs khi mở request thì sẽ auto check xem đã init các dependency như lsp chưa nếu chưa thfi inti và setup fully và nó phải hoạt động ổn thì mứoi hoạt động để đảm bảo ko lỗi nữa

**Đọc lần đầu.**
- Mục tiêu: ở MỌI project, trước khi mở request, TDQ tự kiểm các phụ thuộc tìm kiếm (LSP trước hết);
  thiếu thì tự init/cài đủ; chỉ cho đi tiếp khi LSP thật sự trả lời được.
- Ca gốc (bench `docs/tdq/bench/2026-10-07-2041-sau-khi-go/claude-code.md`, lần 1–2): repo Python,
  `start_lsp` không `language_id` → agent-lsp chọn server TypeScript → crash `0xc0000409`
  (shim fnm `typescript-language-server.cmd`) hoặc `No Project` (không có tsconfig). Thang 7 bậc
  vẫn ĐẠT vì bậc 3/smoke chỉ chạy `agent-lsp doctor`, không thử đường `start_lsp` thật mà agent đi.
- Phạm vi đoán: `scripts/tdq_lsp.py` (thêm bước tự sửa + smoke đúng đường MCP theo ngôn ngữ chính),
  intake bước 1b (đổi từ "hỏi rồi mới cài" sang "tự cài"), có thể hook SessionStart/UserPromptSubmit.
- Chỗ chưa rõ: (1) tự cài cả binary/MCP/server toàn máy (curl|sh, npm -g) hay chỉ cấu hình trong
  project; (2) chặn cứng khi setup không xong hay cho chạy bằng grep; (3) ngôn ngữ chính chọn thế nào
  khi repo đa ngôn ngữ; (4) đụng nguyên tắc hiện tại "script KHÔNG BAO GIỜ tự cài".

Kiểm tầng tìm kiếm lúc mở (bước 1b): `tdq_lsp.py check` → Tổng ĐẠT, 6/7 bậc, smoke 3/3 (bậc 7 cảnh báo đồ thị cũ 0 phút).

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán | Vì sao |
|---|---|---|---|
| `scripts/tdq_lsp.py check` (thang 7 bậc + smoke) | repo | DÙNG — mở rộng | điểm kiểm sẵn có ở intake 1b; thêm smoke theo module |
| `scripts/tdq_setup.py` (`cai_thieu`, `--nen`, mốc sẵn sàng) | repo | DÙNG — mở rộng | đã có cơ chế tự cài theo danh sách cho phép + dựng nền lúc SessionStart |
| `mcp__lsp__detect_lsp_servers` | agent-lsp | DÙNG để đối chiếu | xếp hạng ngôn ngữ theo tỉ lệ + server có sẵn |
| skill_inventory `--loc` | repo | đã chạy | 0 skill trên đĩa khớp; không skill ngoài nào làm việc này |
| code-review / simplify (built-in) | Claude Code | DÙNG ở QC | soát diff cuối |

### Đọc code (B2) — hiện trạng

- `hooks/scripts/session_start.py` → `can_khoi_tao` + `kich_hoat_nen` bắn `tdq_setup.py --nen` tách rời mỗi
  phiên khi mốc `docs/tdq/.tdq-san-sang.json` chưa đủ 3 tầng sẵn sàng. `khoi_tao_nen`: `cai_thieu`
  (chỉ lệnh có tiền tố `uv tool install`, `npm i -g`, `pipx install`, `brew install`) → khai MCP Codex →
  `graphify extract` → smoke → ghi mốc. Như vậy "tự cài" ĐÃ có cho phụ thuộc toàn máy trong danh sách.
- `tdq_lsp.bac3_language_server`: binary trên PATH + `agent-lsp doctor` khởi động được. `smoke_lsp` =
  `agent-lsp doctor`. KHÔNG bước nào gọi đúng đường `start_lsp(root, language_id)` → mở file → hỏi tham chiếu.
- Mốc sẵn sàng chỉ được `search_gate.py` đọc để NỚI cổng; intake không chặn theo nó.
- Lỗ hổng đo được hôm nay (TDQ-Workflow: Python+HTML; claudecodeui: TS 2 tsconfig `src/` + `server/`):
  1. agent-lsp giữ MỘT server hoạt động: `start_lsp html` sau `python` → truy vấn Python ra 0 symbol.
  2. Thiếu `language_id` → agent-lsp có thể chọn TS cho repo Python → crash `0xc0000409` / `No Project`.
  3. TS: gốc phải là thư mục có đúng tsconfig của module; `find_symbol` (workspace/symbol) vẫn 0 kể cả
     khi đã mở file; `find_references` theo vị trí trả 3/3 file khớp grep.
  4. `doctor` ĐẠT trong cả 3 ca trên → smoke hiện tại mù với lỗi chọn server/gốc.
- Hồ sơ kiến trúc `docs/kien-truc.md`: code mới chỉ trong `scripts/`/`hooks/`; `scripts/` không import
  `hooks/`; chỉ `tdq_state.py` ghi state.json; dòng 2026-07-29 "không hook chặn vì chưa duyệt".

### Nghiên cứu (B3) — tóm tắt `docs/tdq/research/2026-10-07-2225-tu-dong-setup-lsp.md`

- **Q1 (cao):** agent-lsp CHẠY SONG SONG mọi server đã khai. Tool theo file (`find_references`,
  `list_symbols`, `find_callers`…) định tuyến theo đuôi file. Riêng `find_symbol` và
  `get_server_capabilities` đi tới server "hiện hành" = server của `start_lsp` gần nhất (hoặc
  `typescript`, đứng đầu cấu hình). Đó là lý do `find_symbol` ra 0 sau `start_lsp html`. Upstream issue #55 còn mở.
- **Q2 (cao):** bỏ `language_id` → không tự nhận ngôn ngữ; bật hết server, chọn server đứng đầu
  (`typescript`); một server hỏng là hỏng cả lượt.
- **Q3:** tsserver `No Project` khi chưa mở file nào (tsls gửi `navto` kèm file mở đầu tiên). Mở một
  file `.ts` là đủ, kể cả ở gốc monorepo. Qua agent-lsp, `find_symbol` vẫn sót một số loại symbol (hằng).
- **Q4 (trung bình–cao):** crash `0xc0000409` KHÔNG do shim fnm mà do `VirtualAlloc failed`: bộ nhớ
  commit chỉ còn trống 3,7/48,7 GB; có các tiến trình `daemon-broker` còn sống. Gọi thẳng `node cli.mjs` không chữa được.
- **Q5:** mỗi ngôn ngữ một root; `scope` ghi đè `tsconfig.json` ở gốc → tránh; có `add_workspace_folder`.

## Hỏi đáp

Vòng 1 (2026-10-08) — user trả lời `4a 5a 6a`; câu 1–3 chưa trả lời, hỏi lại.
- Q4 Hook gác `mcp__lsp__start_lsp` → **A**: chặn khi thiếu `language_id` hoặc gốc không khớp bảng module.
- Q5 Tiến trình agent-lsp sót + bộ nhớ thấp → **A**: tự tắt `daemon-broker` mồ côi của agent-lsp; bộ nhớ commit thấp chỉ báo + hướng dẫn pagefile.
- Q6 Mức QC → **A** `full` (đã ghi `muc_qc=full`).

Vòng 2 (2026-10-08) — user trả lời `1a 2b 3a`.
- Q1 Khi LSP chưa chạy đúng → **A** chặn cứng: `tdq_state.py init` từ chối tới khi mọi module ĐẠT; lối thoát `--bo-qua-lsp "<lý do>"`, lý do vào report.
- Q2 Tự cài → **B** tự cài TẤT CẢ không hỏi, kể cả trình cài agent-lsp (`curl | sh`).
- Q3 Cách kiểm thật → **A** script in kịch bản theo module, agent chạy qua MCP, ghi kết quả bằng lệnh.

### Số đo thêm (2026-10-08)
- Dò file mốc (tsconfig/jsconfig/package.json/pyproject/setup.py/pyrightconfig/go.mod/Cargo.toml), bỏ
  `node_modules`/`.git`/`dist`…: excalidraw 0,05 s (26 mốc), claudecodeui 0,03 s (4), WhisperLiveKit 0,07 s (4),
  TDQ_Monitor_Online 0,31 s (6, 7 994 file), TDQ-Workflow 0,04 s (1).
- Tiến trình `agent-lsp.exe` lúc đo: 2, đều có cha `claude` còn sống; không thấy `daemon-broker` sót.
  Bộ nhớ commit trống **2,2 / 47,6 GB** — máy đang ở đúng vùng gây crash `0xc0000409`.

### Kiến thức đã chốt
- **Module LSP** = (ngôn ngữ, gốc). Gốc = thư mục có file mốc của ngôn ngữ (TS/JS: `tsconfig.json` >
  `jsconfig.json` > `package.json`; Python: `pyrightconfig.json` > `pyproject.toml` > `setup.py`; Go `go.mod`;
  Rust `Cargo.toml`; ngôn ngữ khác: gốc repo). File nguồn thuộc module có gốc sâu nhất chứa nó. Module < 3 file
  nguồn gộp lên module cha cùng ngôn ngữ. Repo một ngôn ngữ = bảng một dòng, cùng một đường.
- **Định tuyến của agent-lsp:** tool theo file tự đi đúng server theo đuôi; `find_symbol` chỉ hỏi server
  của `start_lsp` gần nhất → luật: luôn `start_lsp(root=gốc module, language_id=ngôn ngữ module)` trước khi
  làm việc trong module đó; TS phải `open_document` một file trước; ưu tiên tool theo file.
- **Kịch bản kiểm theo module** (đường MCP thật): `start_lsp` → `open_document` file mẫu → `find_references`
  tại vị trí một symbol có thật được dùng ở ≥ 2 file → so số file với grep. ĐẠT khi số file LSP ≥ grep.
  Kết quả ghi bằng lệnh vào `docs/tdq/.tdq-lsp-module.json`, kèm dấu vân tay (mtime file mốc + cấu hình MCP).
  Kết quả còn hạn khi dấu vân tay không đổi và chưa quá 24 h → intake chỉ chạy lại module hết hạn
  (excalidraw ~13 module TS: lần đầu chạy hết, các lần sau ~0).
- **Chặn cứng ở lệnh `init`, không ở hook** — giữ dòng kiến trúc 2026-07-29; cùng mẫu cổng `approve spec` R14
  (cổng nằm ở lệnh). Tier `nhỏ` không gọi `init` nên không bị chặn.
- **Hook `start_lsp`** (PreToolUse `mcp__lsp__start_lsp`): `deny` khi thiếu `language_id`, hoặc khi có bảng
  module mà cặp (root, language_id) không khớp dòng nào. Không có bảng → chỉ chặn ca thiếu `language_id`.
- **Tự cài (2B):** mở rộng danh sách cho phép; trình cài `curl | sh` chạy KHÔNG qua shell nối ống: tải về file
  tạm rồi chạy `sh <file>` (giữ luật `_chay_lenh` không shell). Trên Windows không có `sh` → dùng bản phát hành
  (`go install` / tải exe) do research chốt ở plan; không cài được → nợ + chặn `init`.
- **Daemon sót (5A):** "mồ côi" = tiến trình `agent-lsp daemon-broker` có gốc không còn tồn tại, hoặc trùng cặp
  (root, language) với broker mới hơn. Chỉ tắt tiến trình của agent-lsp. Commit trống < 4 GB → báo + hướng dẫn pagefile, không chặn.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | đã trả lời Q1–Q5; plan chỉ tra thêm cách cài agent-lsp trên Windows |
| Interview | CÓ (xong 2 vòng) | 6/6 câu đã có trả lời |
| spec → plan | CÓ | khung bất biến |
| implement chia subagent | BỎ | các module dùng chung `tdq_lsp.py`; chia ra sẽ đụng file |
| QC `full` | CÓ | user chọn 6A |
| QC độc lập (agent) | BỎ | mức `full` không yêu cầu; code-review built-in dùng ở QC |
| report | CÓ | khung bất biến |

Vòng 3 (2026-10-08, góp ý spec 1.0) — user: "nếu có thêm ngôn ngữ mới ví dụ ban đầu chỉ có python sau này có
thêm js html thì sẽ tự check và setup lsp còn thiếu" → spec 1.1 thêm đầu ra 8 / Q9. Hiện trạng đo: MCP `lsp`
user-level khai 4 server (typescript, python, json, html); thêm ngôn ngữ = cài server + thêm dòng `args` + kết nối lại MCP.
