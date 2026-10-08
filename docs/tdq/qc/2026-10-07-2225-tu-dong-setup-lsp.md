# QC — Tự động setup LSP theo module, cổng `init`, hook `lsp_gate`
Ngày: 2026-10-08 · Plan: ../plan/2026-10-07-2225-tu-dong-setup-lsp.md · Vòng: 1 · Mức QC: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Dò module 4 cây mẫu + claudecodeui 2 module TS | `pytest tests/test_lsp_module.py -q` · `tdq_lsp.py module` (claudecodeui) | 33 passed · `typescript:.` 570 file + `typescript:server` 295 file | PASS |
| Q2 | Dò module ≤ 1 s trên TDQ_Monitor_Online | `tdq_lsp.py module` ×3 | 0.04 s · 0.04 s · 0.04 s (4 module) | PASS |
| Q3 | Cổng `init` chặn / qua với `--bo-qua-lsp` | `pytest tests/test_tdq_state_cong_lsp.py -q` | 5 passed | PASS |
| Q4 | Hook deny/allow 4 ca, ≤ 200 ms | `pytest tests/test_lsp_gate.py -q` · đo 5 lần | 7 passed · 85/83/82/82/82 ms | PASS |
| Q5 | Ca gốc bị chặn trên bản sao | `git clone --local` → `%TEMP%\q5-tdq` | hook `deny` thiếu `language_id` · `init` rc=2 khi CHUA_KIEM · MCP thật → `ghi-kiem` DAT → `init` rc=0 | PASS |
| Q6 | TDQ-Workflow + claudecodeui Tổng ĐẠT | `tdq_lsp.py check` ×2 | cả hai `Tổng: ĐẠT`, bậc 8 ĐẠT (1/2 · 2/3 module ĐẠT, còn lại html) | PASS (lệch #1, đã duyệt) |
| Q7 | Trọn bộ unit test xanh | `tdq_test.py tron-bo` | Ran 2531, OK (skipped=9), rc=0 | PASS |
| Q8 | `doc_lint` + `i18n_check` exit 0 | `doc_lint.py` 4 file · `i18n_check.py` từng file | doc_lint 0 vi phạm · `lsp_gate.py` 0 dòng · file luật không tăng (SKILL 3, kiem-lsp 1 ≤ 2, uu-tien 6, report-template 3 = HEAD) | PASS (lệch #2, đã duyệt) |
| Q9 | Ngôn ngữ mới: dòng MCP mới, dòng cũ giữ | `pytest tests/test_tdq_setup.py -k khai_server_mcp -q` | 6 passed | PASS |
| QC-F1 | Trọn bộ test | `tdq_test.py tron-bo` · `tdq_test.py so` | Ran 2531 in 438.8 s, OK (skipped=9) · full-suite runs 2/3 · radius misses 0 | PASS |
| QC-F2 | Hồi quy vùng chạm (mọi dòng `Chạm:`) | `tdq_test.py vung-cham` (40 file → 130/130 module) | Ran 2531, OK (skipped=9) | PASS |
| QC-F3 | Ràng buộc kiến trúc §5 | grep import / `state.json` | 5/5 giữ — xem bằng chứng | PASS |
| QC-F4 | Clean code 5 câu | tự kiểm | 5/5 có (ISP đã sửa ở Tx.4) | PASS |

## Bằng chứng

### Q1 · Q2 (claudecodeui, TDQ_Monitor_Online)
```
html:.          4 file · không có file mốc · KHONG_DU_MAU
typescript:.  570 file · tsconfig.json      · DAT · `PROVIDER_PERMISSION_PREFERENCE_KEYS`: 3 tham chiếu LSP so với 1
typescript:server 295 file · tsconfig.json  · DAT · `NOTIFICATION_CHANNEL_ENDPOINTS_TABLE_SCHEMA_SQL`: 4 so với 1
lsp_module: do_module C:\Users\admin\Documents\claudecodeui → 3 module trong 0.06s
lsp_module: do_module C:\Users\admin\Documents\TDQ_Monitor_Online → 4 module trong 0.04s   (×3)
```

### Q4
```
lan 1 : 85 ms · lan 2 : 83 ms · lan 3 : 82 ms · lan 4 : 82 ms · lan 5 : 82 ms
{"permissionDecision": "deny", "permissionDecisionReason": "[TDQ:LSP] start_lsp without language_id: …
Use one of: start_lsp {\"root_dir\": \"…TDQ-Workflow\", \"language_id\": \"python\"}"}
```

### Q5 (bản sao `%TEMP%\q5-tdq`)
```
lsp_gate (root_dir, không language_id) → deny · Use one of: …"html" · …"python"
init 2026-10-08-0900-thu-q5 full → "LSP is not proven for every module of this project — init refused:
  python:. → CHUA_KIEM (chưa chạy kịch bản)" · rc=2
kich-ban → symbol `bac6_cau_hinh_goc_import` (scripts\tdq_lsp.py:502)
MCP thật: start_lsp(python, ready 60 s) → open_document → find_references → symbols=7
  (lần đầu sau 4 s: "workspace is still being indexed" — đúng lý do của CHO_CHI_MUC_GIAY)
ghi-kiem python:. 7 → DAT · 7 tham chiếu LSP so với 2 lần trong file định nghĩa · rc=0
init lại → ✅ init: request=2026-10-08-0900-thu-q5 lane=full phase=idle · rc=0
git status → chỉ ` M docs/tdq/STATE.md` (bảng module nằm trong .git/info/exclude)
```
Ghi chú: pipe chuỗi từ PowerShell 5.1 vào hook làm payload hỏng (BOM) → hook im, đúng nhánh
"payload không có tool_input — silent"; chạy lại qua file redirect thì `deny` như trên.

### Q6
```
TDQ-Workflow: Bậc 8 · LSP theo module → ĐẠT (1/2 module ĐẠT qua MCP, 1 không có gì để kiểm)
              Tổng: ĐẠT · 7/8 bậc ĐẠT · smoke 3/3 tầng trả lời được · 1 cảnh báo không chặn · rc=0
claudecodeui: Bậc 8 · LSP theo module → ĐẠT (2/3 module ĐẠT qua MCP, 1 không có gì để kiểm)
              Tổng: ĐẠT · 7/8 bậc ĐẠT · smoke 3/3 tầng trả lời được · 1 cảnh báo không chặn · rc=0
```
Cảnh báo duy nhất ở cả hai là bậc 7 (đồ thị graphify cũ hơn mã nguồn), không chặn.

### Q8
```
doc_lint: lint 4 file: report-template.md, SKILL.md, kiem-lsp-hieu-ung.md, uu-tien-tim-kiem.md
doc_lint: done — 0 violation(s) total, exit 0
i18n_check hooks/scripts/lsp_gate.py → 0 line(s), exit 0
SKILL.md 3 · kiem-lsp-hieu-ung.md 1 · uu-tien-tim-kiem.md 6 · report-template.md 3 (HEAD: 3)
```

### QC-F2
```
vung-cham: 40 changed file(s); running the full suite (130 modules): radius 124/130 modules reaches the 60% threshold
Ran 2531 tests in 484.692s — OK (skipped=9)
```

### QC-F3 — ràng buộc kiến trúc spec §5
- `scripts/` không import `hooks/`: grep `import _common|lsp_gate|session_start` và `hooks/scripts` trong
  `scripts/*.py` → 0 dòng. `lsp_gate.py` chỉ import `json, os, sys, datetime, _common`.
- Chỉ `tdq_state.py` ghi `state.json`: grep `state.json` trong `lsp_module.py`, `tdq_setup.py`, `tdq_lsp.py`,
  `lsp_gate.py`, `session_start.py` → 0 dòng; `lsp_bo_qua` ghi qua nhánh `init` của `tdq_state.py`.
- File code mới nằm trong `scripts/`/`hooks/`: `scripts/lsp_module.py`, `hooks/scripts/lsp_gate.py`.
- Hook không `deny` vì "chưa duyệt": `lsp_gate` chỉ `deny` khi thiếu `language_id` hoặc cặp (gốc, ngôn ngữ)
  không có trong bảng — lời gọi sai tham số.
- Hub `cli()` của `tdq_state.py` sửa nhánh `init`, khai ở dòng `Chạm:` của T3.1.

### QC-F4 — clean code
- SRP: có — `lsp_module.py` chia 4 khối (module · bảng & vân tay · kịch bản MCP · broker & bộ nhớ), mỗi hàm một việc.
- OCP: có — ngôn ngữ mới chỉ cần một dòng dữ liệu (`_RE_DINH_NGHIA`, `LANG_CONFIG`, `LANG_SERVER`, `CAN_STDIO`, `HO`).
- LSP: có — mỗi nhánh `return` cùng kiểu: `cai_agent_lsp` → `(ok, dòng)`, `_ghi_args_mcp` → `''`/dòng lỗi,
  `kich_ban` → dict hoặc `None` (đã nêu trong docstring).
- ISP: có sau khi sửa — `_ghi_args_mcp` nhận `chay_lenh` mà không dùng; đã bỏ ở Tx.4.
- DIP: có — dùng chung `tdq_lsp._run`, `tdq_lsp._log`, `tdq_state.lenh_cho_project`, danh sách cho phép `_duoc_cai`.

### Sửa trong soát diff (Tx.3 / Tx.4 / QC)
- `tdq_setup.cai_thieu`: lệnh workflow đã viết lại thành `python3 "<plugin>/scripts/X.py"` (project
  không có `scripts/`) lọt khỏi so tiền tố → thành nợ giả mỗi lần setup chạy. Sửa bằng `_RE_LENH_WORKFLOW`,
  test `test_cai_bo_qua_lenh_workflow_ca_dang_duong_dan_tuyet_doi` (đỏ → xanh).
- `report-template.md`: tài liệu nói report đọc `lsp_bo_qua` nhưng chưa có chỗ nào đọc → thêm dòng kiểm
  trước khi trình bày.
- `test_tdq_state_cong_lsp`: so chuỗi quá chặt với lệnh đã viết lại đường dẫn plugin (có dấu nháy) → regex.
- `test_claude_md_core`: đo byte trên đĩa nên CRLF của checkout Windows làm 4250 → 4314 > 4300; đo theo LF như git lưu.
- `lsp_gate.py` docstring: "không import gì từ `scripts/`" sai (`_common` import `tdq_state`) → nói đúng điều được giữ.

## Lệch spec — đã duyệt 2026-10-08 ("Duyệt 1 2")
- #1 Q6 · ngưỡng "kịch bản ĐẠT khi số file LSP ≥ số file grep" · đo được: `find_references` qua agent-lsp trả GCF
  chỉ có namespace, không có đường dẫn file · phương án đã áp: ĐẠT khi số tham chiếu LSP (kể cả khai báo) > số lần
  symbol xuất hiện trong chính file định nghĩa.
- #2 Q8 · ngưỡng "i18n_check exit 0" · đo được: các file cũ bị chạm chưa từng ở 0 trước request (tdq_lsp 87,
  tdq_setup 123, tdq_state 43…) · phương án đã áp: file mới 0 dòng, file luật không tăng dòng nào.

### QC-F1
```
Ran 2531 tests in 438.849s
OK (skipped=9)
rc=0
full-suite runs: 2 of budget 3
radius misses: 0
```
(Dòng `canh-bao: session red-green/viet/1 failed, retry N` là log của chính ca test thử nhánh thử lại, không phải ca trượt.)

## Kết luận
PASS toàn bộ — 9/9 DoD + 4/4 hạng mục cố định; Q6 và Q8 là PASS theo lệch #1, #2 đã được user duyệt.
