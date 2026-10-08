# PLAN — Tự động setup & chứng minh LSP theo module trước khi mở request

Ngày: 2026-10-08 · Spec: ../spec/2026-10-07-2225-tu-dong-setup-lsp.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — user chọn "1b" (inline); đề xuất ban đầu subagent: `tdq_bench simulate` (hệ số agent 1,5): đội 30,7 phút so với main 38,7 phút, chênh 8,0 phút (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Lõi module (`lsp_module.py`)
- P2 — Thang kiểm & CLI
- P3 — Cổng `init`
- P4 — Hook `lsp_gate.py`
- P5 — Tự cài, ngôn ngữ mới, dọn broker
- P6 — Luật chữ & phát hành 0.59.0
- P7 — Đo thật trên máy
- Px — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: `[~]` khi bắt đầu → test đỏ trước → sửa → test xanh → `[x]` NGAY.
3. Mỗi bước: `python3 scripts/tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` trên chính lệnh đó.
5. Test không bao giờ chạy cài thật, tải mạng thật, tắt tiến trình thật hay ghi `~/.claude.json` thật:
   runner, danh sách tiến trình và đường dẫn cấu hình đều tiêm được.
6. Sửa file ngoài repo (P7): bản sao `<file>.truoc-tdq-<YYYYMMDDHHMMSS>.bak` trước khi ghi.
7. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass. Không commit/push cho đến khi user yêu cầu.

## P1 — Lõi module (`lsp_module.py`)
- [x] **T1.1** (e30m) `do_module(project)`: duyệt cây (bỏ `tdq_lsp.SKIP_DIRS`), gán file nguồn theo `tdq_lsp.EXT_LANG`, gốc = thư mục mốc sâu nhất của ngôn ngữ (TS/JS `tsconfig.json` > `jsconfig.json` > `package.json`; Python `pyrightconfig.json` > `pyproject.toml` > `setup.py`; Go `go.mod`; Rust `Cargo.toml`; khác → gốc repo); module < 3 file gộp lên cha cùng ngôn ngữ; JS dưới gốc có `tsconfig.json` thuộc module TS — Test: `python3 -m pytest tests/test_lsp_module.py -q -k do_module` với 4 cây mẫu (1 ngôn ngữ · Python+HTML · TS 2 tsconfig · Python+TS)
  - Chạm: `scripts/lsp_module.py`, `tests/test_lsp_module.py` → file mới; đọc hằng của `tdq_lsp`
- [x] **T1.2** (e25m) Bảng `docs/tdq/.tdq-lsp-module.json` (ghi nguyên tử): `van_tay(project, module)` = tập ngôn ngữ của project + mtime file mốc + chuỗi `args` MCP `lsp`; `ghi_ket_qua(module, so_file_lsp)` tự so với số file grep đã lưu của kịch bản; `trang_thai(project)` → mỗi module một trong `DAT`/`TRUOT`/`CHUA_KIEM`/`HET_HAN`/`KHONG_DU_MAU`; hết hạn khi vân tay đổi hoặc quá 24 h — Test: `pytest tests/test_lsp_module.py -k "van_tay or het_han or ghi_ket_qua"`
  - Chạm: `scripts/lsp_module.py`, `tests/test_lsp_module.py`
  - Cần: T1.1
- [x] **T1.3** (e30m) `kich_ban(project, module)`: chọn symbol định nghĩa trong module (Python `def`/`class`; TS/JS `export function|class|const`; Go `func`; Rust `pub fn`), có mặt ở ≥ 2 file theo grep từ nguyên vẹn; trả file mẫu, dòng, cột, số file grep, và các lời gọi MCP in sẵn (`start_lsp` root + `language_id`, `open_document`, `find_references`). Không có symbol ≥ 2 file → `KHONG_DU_MAU` (không chặn) — Test: `pytest tests/test_lsp_module.py -k kich_ban`
  - Chạm: `scripts/lsp_module.py`, `tests/test_lsp_module.py`
  - Cần: T1.1
- [x] **T1.4** (e25m) Tiến trình & bộ nhớ: `liet_ke_broker(doc=None)` (Windows: `powershell Get-CimInstance Win32_Process`; khác: `ps -eo pid,lstart,args`), `broker_mo_coi(ds)` = gốc không còn tồn tại hoặc trùng cặp (gốc, ngôn ngữ) với broker mới hơn; `tat_broker(pids, tat=None)` chỉ nhận tiến trình có `agent-lsp` + `daemon-broker` trong dòng lệnh; `commit_trong_gb()` (Windows `GlobalMemoryStatusEx` qua ctypes; Linux `/proc/meminfo`; khác → None) — Test: `pytest tests/test_lsp_module.py -k "broker or commit"` với danh sách giả
  - Chạm: `scripts/lsp_module.py`, `tests/test_lsp_module.py`

**Xong P1 khi**: `pytest tests/test_lsp_module.py -q` xanh.

## P2 — Thang kiểm & CLI
- [x] **T2.1** (e25m) `tdq_lsp.py`: bậc 8 "LSP theo module" đọc `lsp_module.trang_thai` — chặn (exit 3) khi có module `CHUA_KIEM`/`HET_HAN`/`TRUOT`, `KHONG_DU_MAU` chỉ cảnh báo; lời bậc in lệnh `tdq_lsp.py kich-ban`. Lệnh con mới: `module` (in bảng), `kich-ban [--module <id>]` (in kịch bản các module chưa ĐẠT), `ghi-kiem <id> <so_file_lsp>`; docstring đầu file lên 8 bậc — Test: `pytest tests/test_tdq_lsp.py tests/test_mot_lenh_kiem.py -q`
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`, `tests/test_mot_lenh_kiem.py` → `main()` (hub), `chay_kiem`, `kiem_mot_lenh`; người import: `tdq_setup`, `tdq_finish`, `tdq_codex_mcp`, `setup_status`
  - Cần: T1.2, T1.3
- [x] **T2.2** (e15m) Bậc 3 thêm cổng 3: mỗi ngôn ngữ của project phải có dòng trong `args` MCP `lsp`; thiếu → TRƯỢT với lệnh sửa `tdq_setup.py` — Test: `pytest tests/test_tdq_lsp.py -k bac3`
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py` → `bac3_language_server`
  - Cần: T2.1

## P3 — Cổng `init`
- [x] **T3.1** (e25m) `tdq_state.py init`: trước khi ghi state, gọi `lsp_module.cong_init(project)`; có module chưa ĐẠT → `_fail` liệt kê module + lệnh `tdq_setup.py` rồi `tdq_lsp.py kich-ban`. Cờ `--bo-qua-lsp "<lý do>"` cho qua và ghi `lsp_bo_qua` (lý do + thời điểm) vào state; project không có ngôn ngữ cần LSP → không chặn. Report đọc `lsp_bo_qua` (dòng trong `tdq_finish`/report template nếu có chỗ in khoá state) — Test: `pytest tests/test_tdq_state_cong_lsp.py -q` (chặn · qua với cờ · repo rỗng · lý do có trong state); trọn bộ test dùng `init` trong thư mục tạm vẫn xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_tdq_state_cong_lsp.py` → `main()`/`cli()` (hub), nhánh `init`, `default_state`
  - Cần: T1.2

## P4 — Hook `lsp_gate.py`
- [x] **T4.1** (e25m) `hooks/scripts/lsp_gate.py` (PreToolUse `mcp__lsp__start_lsp`): thiếu `language_id` → `deny`; có bảng module mà cặp (root chuẩn hoá, `language_id`) không khớp dòng nào → `deny` + liệt kê cặp hợp lệ dạng lời gọi `start_lsp` dùng ngay; còn lại im. Đọc bảng bằng `json` (không import `scripts/`). Khai vào `hooks/hooks.json` — Test: `pytest tests/test_lsp_gate.py -q` (4 ca) + `tests/test_docs_consistency.py`
  - Chạm: `hooks/scripts/lsp_gate.py`, `hooks/hooks.json`, `tests/test_lsp_gate.py` → file mới; `hooks.json` được `test_docs_consistency`, `build_portable` đọc
  - Cần: T1.2

## P5 — Tự cài, ngôn ngữ mới, dọn broker
- [x] **T5.1** (e30m) `tdq_setup.py`: cài agent-lsp không cần shell — GitHub API `releases/latest` → asset `agent-lsp_<os>_<arch>.zip|.tar.gz` → kiểm SHA256 theo `checksums.txt` → giải nén vào `~/.local/bin` (Windows `agent-lsp.exe`); thay lệnh `curl | sh` của bậc 1; sai checksum → không cài, ghi nợ — Test: `pytest tests/test_tdq_setup.py -k agent_lsp` với hàm tải giả (đúng/sai checksum, zip/tar)
  - Chạm: `scripts/tdq_setup.py`, `scripts/tdq_lsp.py`, `tests/test_tdq_setup.py` → `cai_thieu`, `INSTALL_AGENT_LSP`
  - Cần: T2.1
- [x] **T5.2** (e35m) Ngôn ngữ mới: `khai_server_mcp(project, cau_hinh=~/.claude.json)` — với mỗi ngôn ngữ của project chưa có trong `args` MCP `lsp`: cài server (`LANG_SERVER`), tìm đường dẫn thật (`shutil.which`), nối dòng `<lang>:<đường dẫn>,--stdio`; sao lưu `.truoc-tdq.bak`, ghi nguyên tử, chỉ đụng mảng `args` của `lsp`; in nhắc `/mcp` kết nối lại. Chạy trong `main` của setup và trong `khoi_tao_nen` — Test: `pytest tests/test_tdq_setup.py -k khai_server_mcp` (Python + thêm `.js`/`.html` → 2 dòng mới, dòng cũ giữ, khoá khác của file giữ nguyên byte)
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py` → `main()` (hub), `khoi_tao_nen`
  - Cần: T5.1
- [x] **T5.3** (e15m) Dọn broker + cảnh báo commit < 4 GB trong `main` và `khoi_tao_nen` của setup (gọi T1.4) — Test: `pytest tests/test_tdq_setup.py -k broker`
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py` → `khoi_tao_nen`
  - Cần: T1.4, T5.2
- [x] **T5.4** (e20m) `session_start.py` `can_khoi_tao`: thêm điều kiện "tập ngôn ngữ hiện tại khác tập ghi trong bảng module" → dựng nền (đọc file, không chạy tiến trình nặng; dò ngôn ngữ dừng ở 1 s) — Test: `pytest tests/test_tu_khoi_tao.py -q`
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_tu_khoi_tao.py` → `can_khoi_tao`
  - Cần: T1.2

## P6 — Luật chữ & phát hành 0.59.0
- [x] **T6.1** (e20m) `skills/tdq-intake/SKILL.md` bước 1b: chạy `tdq_setup.py` (tự cài, không hỏi) → `tdq_lsp.py check` → chạy `tdq_lsp.py kich-ban` qua MCP + `ghi-kiem` từng module → `init` chỉ qua khi bậc 8 ĐẠT; `references/kiem-lsp-hieu-ung.md` viết lại theo kịch bản module (thay "không dừng request" bằng cổng); `skills/tdq-setup/references/uu-tien-tim-kiem.md` thêm luật gọi: `start_lsp(root=gốc module, language_id)` trước khi làm việc trong module, TS `open_document` trước, ưu tiên tool theo file, `find_symbol` chỉ sau `start_lsp` đúng ngôn ngữ — Test: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/kiem-lsp-hieu-ung.md skills/tdq-setup/references/uu-tien-tim-kiem.md` + `python3 scripts/i18n_check.py` exit 0
- [x] **T6.2** (e15m) `CHANGELOG.md` mục 0.59.0; version 0.59.0 ở `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`; `docs/kien-truc.md` thêm dòng `Đã chốt` 2026-10-08 (cổng LSP ở lệnh `init`, hook `lsp_gate` chặn vì tham số sai) — Test: `pytest tests/test_docs_consistency.py -q`; `doc_lint` CHANGELOG ≤ 500 dòng

## P7 — Đo thật trên máy
- [x] **T7.1** (e10m) Đo Q2 (dò module TDQ_Monitor_Online ≤ 1 s) và Q4 (hook ≤ 200 ms, 5 lần) — Test: số đo ghi vào qc
- [x] **T7.2** (e20m) Q5 ca gốc trên bản sao `git clone --local` repo này ở `%TEMP%`: `lsp_gate` chặn `start_lsp` thiếu `language_id`; `init` bị chặn tới khi kịch bản ĐẠT — Test: đầu ra lệnh ghi vào qc
- [x] **T7.3** (e25m) Q6 + Q9 qua MCP thật: chạy `tdq_lsp.py kich-ban` + `ghi-kiem` trên TDQ-Workflow và claudecodeui (2 module TS); Q9 trên bản sao tạm thêm `.js`/`.html`, `tdq_setup.py` với `--cau-hinh-mcp <bản sao ~/.claude.json>` — Test: `tdq_lsp.py check` Tổng ĐẠT ở cả hai repo
  - Dùng: agent-lsp `mcp__lsp__*` (mcp)
  - Để: chạy kịch bản module qua đúng đường MCP agent dùng
  - Ra: kết quả `ghi-kiem` trong `docs/tdq/.tdq-lsp-module.json` của mỗi repo
  - Kiểm: `python3 scripts/tdq_lsp.py check` exit 0
  - Không dùng cho: sửa cấu hình MCP thật của user

## Px — Log & test bắt buộc
- [x] **Tx.1** (e10m) Log service: mọi hàm mới ghi một dòng ISO timestamp ra stderr qua `_log` sẵn có; tắt bằng `TDQ_LOG=0` / `--khong-log` — Test: `pytest tests/test_lsp_module.py -k log`
  - Chạm: `scripts/lsp_module.py`, `tests/test_lsp_module.py`
- [x] **Tx.2** (e10m) Unit test cho từng thành phần, chạy bằng một lệnh — Test: `python3 scripts/tdq_test.py tron-bo`
- [x] **Tx.3** (e15m) Soát diff cuối ở QC — Test: không còn phát hiện mức correctness chưa xử lý
  - Dùng: `code-review`
  - Để: tìm lỗi đúng/sai trên diff của nhánh, nạp skill TRƯỚC khi đọc diff
  - Ra: danh sách phát hiện ghi vào `docs/tdq/qc/2026-10-07-2225-tu-dong-setup-lsp.md`
  - Kiểm: mỗi phát hiện có dòng xử lý (sửa / không cần) trong file qc
  - Không dùng cho: viết lại phạm vi ngoài diff
- [x] **Tx.4** (e10m) Dọn code sau khi xanh — Test: `python3 scripts/tdq_test.py vung-cham` vẫn xanh
  - Dùng: `simplify`
  - Để: gộp trùng lặp, bỏ code thừa trong các file đã chạm
  - Ra: diff dọn trong `scripts/lsp_module.py`, `scripts/tdq_lsp.py`, `scripts/tdq_setup.py`
  - Kiểm: `python3 scripts/tdq_test.py vung-cham` exit 0
  - Không dùng cho: đổi hành vi đã khoá bằng test

## Cụm song song

Ba đợt theo dòng `Cần:` (máy xếp, `tdq_bench simulate`):
- Đợt 1: P1 (T1.1–T1.4, Tx.1) — một chủ ghi `scripts/lsp_module.py`.
- Đợt 2, song song sau T1.2/T1.3: cụm A = P2 + P5 (T2.1, T2.2, T5.1–T5.3; chủ ghi `scripts/tdq_lsp.py`,
  `scripts/tdq_setup.py`) · cụm B = T3.1 (`scripts/tdq_state.py`) · cụm C = T4.1 + T5.4 (`hooks/`).
- Đợt 3: P6, P7, Tx.2–Tx.4 — leader làm, vì P7 cần MCP (`(mcp)`).
File nóng: `scripts/lsp_module.py` (đợt 1), `scripts/tdq_lsp.py` (T2.1, T2.2, T5.1), `scripts/tdq_setup.py` (T5.1–T5.3)
→ mỗi file một chủ ghi trong cụm A.

## Definition of Done
- [x] Q1 Dò module đúng 4 cây mẫu + claudecodeui 2 module TS — `python3 -m pytest tests/test_lsp_module.py -q`
- [x] Q2 Dò module ≤ 1 s trên TDQ_Monitor_Online — `python3 scripts/tdq_lsp.py module` (thời gian in trong log)
- [x] Q3 Cổng `init` chặn / qua với `--bo-qua-lsp` — `python3 -m pytest tests/test_tdq_state_cong_lsp.py -q`
- [x] Q4 Hook deny/allow đúng 4 ca, ≤ 200 ms — `python3 -m pytest tests/test_lsp_gate.py -q`
- [x] Q5 Ca gốc bị chặn trên bản sao — đầu ra T7.2 trong qc
- [x] Q6 TDQ-Workflow + claudecodeui Tổng ĐẠT — `python3 scripts/tdq_lsp.py check`
- [x] Q7 Trọn bộ unit test xanh — `python3 scripts/tdq_test.py tron-bo`
- [x] Q8 `doc_lint` + `i18n_check` exit 0 — `python3 scripts/doc_lint.py && python3 scripts/i18n_check.py`
- [x] Q9 Ngôn ngữ mới: module mới + dòng MCP mới, dòng cũ giữ, `init` chặn tới khi ĐẠT — `python3 -m pytest tests/test_tdq_setup.py -k khai_server_mcp -q`
