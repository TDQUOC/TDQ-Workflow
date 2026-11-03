# PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác

Ngày: 2026-08-04 · Spec: ../spec/2026-08-04-export-claude-setup.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — quy trình phụ thuộc chặt (viết 3 template rồi chạy chính
instruction đó để sinh bundle thật từ dữ liệu máy nguồn), toàn bộ đụng tới secret
thật (2 API key) — giữ trong phiên đã thiết lập kỷ luật redact, tránh đưa context
nhạy cảm ra engine ngoài.
Trạng thái plan: HOÀN THÀNH (mode main, 2026-08-04T14:02:50+07:00, by "duyệt plan mode main")

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `update-config` | T1.1 | `claude-export/INSTRUCTIONS.md` mô tả đúng field settings.json |
| `plugin-dev:plugin-structure` | T1.2 | `claude-export/MANIFEST.template.json` đúng chuẩn plugin/marketplace |
| `keybindings-help` | T1.3 | `claude-export/README.template.md` có mục xác nhận keybindings |
| `tavily-search` (mcp) | T1.4 | README không còn dòng "cần xác minh" |
| `remember (remember, remember:doctor)` | T2.2 | kết quả `remember:doctor` PASS trước khi copy `.remember/` |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code/nội dung → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy lại toàn bộ lệnh test của phase đó, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Viết bộ công cụ export tĩnh (`claude-export/`)
- [x] **T1.1** Viết `claude-export/INSTRUCTIONS.md` đủ 7 bước theo thứ tự spec §2 dòng 1 — Test: đối chiếu thủ công đủ 7 bước (thu thập trạng thái → lọc secret/runtime → copy file local → rewrite path `tdq-local` → điền manifest → điền README → ghi log), mỗi bước có lệnh cụ thể

  > Ghi chú lệch spec: spec §6 dòng Q1 còn ghi "6 bước" (sót khi spec thêm bước
  > rewrite path lúc sửa theo review) trong khi spec §2 dòng 1 đã đúng "7 bước" —
  > plan này theo đúng 7 bước của §2 dòng 1; ai chạy QC Q1 theo câu chữ cũ "6 bước"
  > cần hiểu là đếm nhầm, không phải plan sai.
  - Dùng: `update-config`
  - Nạp: gọi skill update-config trước khi viết bước liệt kê/lọc trường trong settings.json
  - Để: tham chiếu đúng cấu trúc settings.json (permissions/hooks/env/extraKnownMarketplaces) khi viết bước lọc secret và bước rewrite path tdq-local
  - Ra: `claude-export/INSTRUCTIONS.md` mô tả đúng field settings.json thật
  - Kiểm: đọc thủ công đối chiếu tên field với settings.json thật, không sai tên
  - Không dùng cho: phần cấu trúc manifest plugin (dùng plugin-dev:plugin-structure ở T1.2)
- [x] **T1.2** Viết `claude-export/MANIFEST.template.json` — Test: `python3 -m json.tool claude-export/MANIFEST.template.json` exit 0, đủ 5 khoá bậc 1
  - Dùng: `plugin-dev:plugin-structure`
  - Nạp: gọi skill plugin-dev:plugin-structure trước khi định nghĩa khoá `plugins`/`marketplaces`
  - Để: tham chiếu đúng chuẩn field của `plugin.json`/`marketplace.json` khi thiết kế khoá manifest
  - Ra: `claude-export/MANIFEST.template.json`
  - Kiểm: `python3 -m json.tool claude-export/MANIFEST.template.json`
  - Không dùng cho: khoá `cli_dependencies`/`mcp_servers` (không phải cấu trúc plugin)
- [x] **T1.3** Viết `claude-export/README.template.md` đủ 6 mục theo thứ tự spec §2 dòng 3 — Test: đối chiếu thủ công đủ 6 mục đúng thứ tự
  - Dùng: `keybindings-help`
  - Nạp: gọi skill keybindings-help trước khi viết mục liên quan phím tắt
  - Để: xác nhận máy nguồn không có `keybindings.json` tuỳ chỉnh cần liệt kê thêm — README không thiếu mục này
  - Ra: `claude-export/README.template.md` có ghi chú rõ về keybindings mặc định
  - Kiểm: `grep -i keybindings claude-export/README.template.md` có kết quả
  - Không dùng cho: bảng CLI dependency (không liên quan keybindings)
- [x] **T1.4** CHỈ CHẠY NẾU có gap thực tế phát sinh lúc viết T1.3 (lệnh cài chưa có nguồn trong research §5-6) — không mâu thuẫn với spec §3b (đã ghi "không dùng thêm ở phase build" cho trường hợp KHÔNG phát sinh gap); nếu không phát sinh gap thì tick task này pass ngay không cần gọi tool — Test: `grep -c "cần xác minh" claude-export/README.template.md` = 0

  > Gap phát sinh: lệnh cài `uv` và `graphify` không có trong research §5-6 (vốn chỉ
  > phủ Claude Code/Codex CLI/Windows). Đã gọi `tavily-primary` xác minh 2 truy vấn
  > (uv installer chính thức astral-sh/uv; graphify install từ Graphify-Labs/graphify
  > GitHub) trước khi viết mục 2 của README.template.md.
  - Dùng: `tavily-search` (mcp)
  - Nạp: gọi skill tavily-search qua `tavily-primary` nếu phát sinh lệnh cài đặt chưa có nguồn trong `research/2026-08-04-export-claude-setup.md` §5-6
  - Để: đảm bảo lệnh cài Windows (native/WSL2) và Codex CLI trong README còn đúng, không dựa suy đoán
  - Ra: `claude-export/README.template.md` không còn dòng đánh dấu "cần xác minh"
  - Kiểm: `grep -c "cần xác minh" claude-export/README.template.md` = 0
  - Không dùng cho: nội dung cấu trúc manifest/instruction (không liên quan tra cứu lệnh cài)
- [x] **T1.5** Khởi tạo `claude-export/EXPORT_LOG.md` (header + mô tả định dạng entry) — Test: file tồn tại, có dòng mô tả định dạng `YYYY-MM-DD HH:MM — <tóm tắt>`

**Xong P1 khi**: cả 3 file tĩnh (`INSTRUCTIONS.md`, `MANIFEST.template.json`, `README.template.md`) và `EXPORT_LOG.md` khởi tạo tồn tại, đúng cấu trúc theo spec §2 dòng 1-4.

## P2 — Thu thập dữ liệu thật & copy vào bundle đích
- [x] **T2.1** Xác nhận với user đường dẫn đích bundle (mặc định gợi ý `~/Documents/claude-code-export/`) — Test: đường dẫn đã xác nhận được ghi thành 1 dòng riêng trong `claude-export/EXPORT_LOG.md` (vd. `YYYY-MM-DD HH:MM — EXPORT_DEST=<path>`, đặt trước dòng entry tóm tắt ở T3.3) TRƯỚC khi chạy `mkdir` tạo bundle
- [x] **T2.2** Kiểm tình trạng `.remember/` trước khi copy vào bundle — Test: `remember:doctor` không báo lỗi
  - Dùng: `remember (remember, remember:doctor)`
  - Nạp: gọi remember:doctor trước bước copy `.remember/` vào bundle
  - Để: đảm bảo memory không lỗi/rác trước khi đưa vào bundle export
  - Ra: kết quả remember:doctor PASS, ghi lại trong log build
  - Kiểm: chạy remember:doctor, không có dòng lỗi
  - Không dùng cho: phần plugin/marketplace/manifest (không liên quan memory)
- [x] **T2.3** Đọc trạng thái thật máy nguồn (`settings.json`, `installed_plugins.json`, `known_marketplaces.json`, `~/.claude.json` mcpServers) + chạy `claude --version && node --version && python3 --version && git --version && uv --version && graphify --version` (kèm `codex --version`/`agy --version` nếu có cài) để lấy version thật cho khoá `cli_dependencies` — Test: có đủ dữ liệu danh sách plugin/marketplace/mcp_server VÀ version thật từng CLI dependency, dùng cho T3.1
- [x] **T2.4** Lọc secret (thay 2 giá trị Tavily key bằng placeholder) + copy file cấu hình global đã lọc vào `config/` trong bundle — Test: `grep -r` giá trị thật 2 API key trên `config/` → rỗng
- [x] **T2.5** Copy toàn bộ repo TDQWorkflow vào `tdqworkflow-repo/` trong bundle — Test: `ls tdqworkflow-repo/` có các file gốc của repo (vd. `CLAUDE.md`, `scripts/`)
- [x] **T2.6** Rewrite `extraKnownMarketplaces.tdq-local` trong `config/settings.json` + entry tương ứng trong `known_marketplaces.json` khớp đường dẫn `tdqworkflow-repo/` thật trong bundle — Test: so đường dẫn 2 file khớp tuyệt đối với đường dẫn `tdqworkflow-repo/` thật (QC Q8)

**Xong P2 khi**: bundle đích có `config/` (đã lọc secret + rewrite path) và `tdqworkflow-repo/` tồn tại đúng cấu trúc.

## P3 — Điền manifest/README thật & ghi log
- [x] **T3.1** Điền `manifest.json` thật từ dữ liệu T2.3 — Test: `python3 -m json.tool manifest.json` exit 0; số lượng plugin khớp 100% `installed_plugins.json` (QC Q6)
- [x] **T3.2** Điền `README.md` thật (tên bundle, danh sách plugin/marketplace thật, giữ placeholder 2 API key) — Test: đối chiếu 6 mục đã điền, không còn placeholder mô tả ngoài 2 API key; VÀ số lượng plugin liệt kê trong bảng README khớp 100% với `manifest.json` (dùng chung kết quả đối chiếu của Q6/T3.1)
- [x] **T3.3** Ghi 1 entry `EXPORT_LOG.md` cho lần chạy thử này — Test: đọc file có entry timestamp hợp lệ (QC Q7)
- [x] **T3.4** Test cơ chế tắt log: chạy lại bước ghi log với `TDQ_EXPORT_NO_LOG=1`, xác nhận KHÔNG có entry mới — Test: so `EXPORT_LOG.md` trước/sau, không đổi (QC Q9)

**Xong P3 khi**: `manifest.json`, `README.md` trong bundle đã điền dữ liệu thật; `EXPORT_LOG.md` có đúng 1 entry (không nhân đôi khi test tắt log).

## P4 — QC tổng & log/test bắt buộc
- [x] **T4.1** Log service bật mặc định + tắt được qua `TDQ_EXPORT_NO_LOG=1` (timestamp, tắt được qua config) — Test: T3.3 + T3.4 đã pass; đọc lại `EXPORT_LOG.md` đúng định dạng
- [x] **T4.2** Kiểm bundle không lẫn dữ liệu loại trừ (`find`/`ls -R` đối chiếu danh sách loại trừ §1 của spec) — Test: không tìm thấy mục nào trong danh sách loại trừ bên trong bundle (QC Q10)
- [x] **T4.3** Chạy đủ 10 mục QC (Q1–Q10 của spec §6): Q2 (`python3 -c "import json; json.load(open('claude-export/MANIFEST.template.json'))"`), Q4 (`grep -rEi "sk-|api[_-]?key|token" claude-export/ --include=*.json --include=*.md` phải rỗng), Q5 (`ls` đối chiếu cấu trúc bundle) là lệnh đơn, exit 0 độc lập; Q1, Q3, Q6, Q7, Q8, Q9, Q10 là đối chiếu thủ công (đọc file so khớp số liệu/đường dẫn thật, không có lệnh clean-exit gộp chung) — làm tuần tự từng Q, ghi kết quả PASS/FAIL từng dòng — Test: cả 10 dòng đều PASS, dòng nào FAIL thì dừng và quay lại task tương ứng sửa trước khi tick T4.3
- [x] **T4.4** Hỏi user có muốn commit `claude-export/` vào repo TDQWorkflow không (không tự ý commit, theo quy tắc thi hành mục 6) — Test: đã hỏi rõ ràng, chờ phản hồi trước khi chạy `git add`/`git commit`

**Xong P4 khi**: toàn bộ Q1–Q10 PASS; đã hỏi user về việc commit `claude-export/`.

## Definition of Done
Trỏ về spec §6 (`docs/tdq/spec/2026-08-04-export-claude-setup.md`):
- Q1 (T1.1) — 7 bước INSTRUCTIONS.md đủ, có lệnh cụ thể.
- Q2 (T1.2) — MANIFEST.template.json hợp lệ JSON, đủ 5 khoá.
- Q3 (T1.3, T3.2) — README.template.md đủ 6 mục; bản điền thật không thiếu mục.
- Q4 (T2.4) — `grep -r` giá trị thật 2 API key trên bundle → rỗng.
- Q5 (T2.4/T2.5/T3.1/T3.2) — `ls` đối chiếu đủ cấu trúc `manifest.json`/`README.md`/`config/`/`tdqworkflow-repo/`.
- Q6 (T3.1) — số lượng/tên plugin trong manifest khớp 100% `installed_plugins.json`.
- Q7 (T3.3) — `EXPORT_LOG.md` có entry hợp lệ cho lần chạy thử.
- Q8 (T2.6) — path `tdq-local` trong bundle khớp đúng vị trí `tdqworkflow-repo/` thật.
- Q9 (T3.4) — `TDQ_EXPORT_NO_LOG=1` hoạt động đúng, không thêm entry khi bật.
- Q10 (T4.2) — bundle không lẫn dữ liệu loại trừ (runtime/cache/máy-cụ-thể).

Cả 10 hạng mục PASS + `claude-export/` đã hỏi ý kiến commit ở T4.4 (chỉ thực sự
commit nếu user đồng ý lúc đó — không tự động, theo quy tắc thi hành mục 6 và
CLAUDE.md "chỉ commit khi user yêu cầu").
