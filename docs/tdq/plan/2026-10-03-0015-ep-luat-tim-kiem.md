# PLAN — Buộc agent code tuân đúng luật tìm kiếm 4 tầng

Ngày: 2026-10-03 · Spec: ../spec/2026-10-03-0015-ep-luat-tim-kiem.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py simulate` trên chính plan này: đội thắng 20,3 phút (32,6 so với 52,9), 26 task chia 4 đợt, giao được 10 task, leader giữ 16 vì ba file nóng (`search_gate.py`, `tdq_setup.py`, `tdq_lsp.py`). Request trước user chốt `main` dù đo ra đội thắng (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT · 26 task · ETA 575 phút

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Trinh sát và thước đo
- P2 — Luật và cổng tìm kiếm
- P3 — Codex
- P4 — Kiểm thật thay cho "có cài"
- P5 — Đường dẫn tuyệt đối
- P6 — Tự khởi tạo ở đầu project
- P7 — Hồ sơ kiến trúc và luật
- P8 — Log, test, đo, ba hệ
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo. P1 đi trước mọi thứ: kết quả trinh sát Codex
   quyết định hình dạng của P3, và bộ phát lại là thước đo của P2.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Luật kiến trúc phải giữ:** `scripts/` không import `hooks/`. Vì vậy phần QUYẾT ĐỊNH của cổng
   (thuần, không I/O) nằm ở `scripts/search_rules.py`; hook `hooks/scripts/search_gate.py` chỉ
   đọc sổ, gọi hàm quyết định và in kết quả. Bộ phát lại ở `scripts/` dùng cùng hàm quyết định —
   một luật, hai người gọi, không có bản sao thứ hai để lệch nhau.
8. Mọi lệnh chạm `~/.codex/` hoặc cài gói global: backup trước, chỉ THÊM, ghi lại cách gỡ.

## P1 — Trinh sát và thước đo

- [x] **T1.1** (e25m) Trinh sát Codex bằng chạy thật `codex-cli 0.155.1`: (a) `plugin.json` của
  Codex có nhận khoá `hooks` không; (b) một hook `PreToolUse` trên shell trả `deny` kèm lý do thì
  Codex có dừng lệnh và đọc lý do không (chạy `codex exec` có cờ bỏ qua trust cho đúng một lần);
  (c) khai MCP trong `config.toml` thì `codex mcp list` có thấy không — Test: brief có mục
  `### Trinh sát Codex` với 3 phán quyết, mỗi phán quyết kèm lệnh và output thật
- [x] **T1.2** (e15m) Trích các lần tìm của phiên excalidraw thành fixture nhỏ: theo thứ tự, mỗi
  dòng là (loại sự kiện, công cụ, lệnh/mẫu, token định danh của prompt nếu là prompt). Không chép
  code hay output — Test: `python -c "import json;d=json.load(open('tests/fixtures/phien_excalidraw_tim.json',encoding='utf-8'));e={x['luot']:x for x in d['su_kien']};assert 'fileHandle' in e[7]['lenh'] and '^export' in e[9]['lenh'] and 'beforeunload' in e[10]['lenh'] and e[40]['cong_cu'].endswith('semantic_search')"` (lượt 7 `fileHandle`, lượt 9 `^export`, lượt 10 mẫu 4
  nhánh, lần lumen ở lượt 40)
  - Chạm: `tests/fixtures/phien_excalidraw_tim.json` → file mới, chưa node nào phụ thuộc
- [x] **T1.3** (e25m) Bộ phát lại `scripts/search_replay.py`: đọc fixture (hoặc một transcript
  JSONL), đưa từng lần tìm qua hàm quyết định, in bảng lượt · lệnh · quyết định · lý do, và ba số
  đếm: bắt đúng, bắt oan, lọt — Test: `python -m unittest discover tests -p test_search_replay.py`
  - Chạm: `scripts/search_replay.py`, `tests/test_search_replay.py` → file mới
  - Cần: T1.2

**Xong P1 khi**: brief có 3 phán quyết Codex đo bằng chạy thật, và bộ phát lại chạy được (cổng
lúc này còn là hàm giả "cho qua tất cả", nên mọi lần đoán mò hiện ra ở cột LỌT — đó là vạch xuất
phát).

## P2 — Luật và cổng tìm kiếm

- [ ] **T2.1** (e40m) `scripts/search_rules.py` — hàm thuần, không I/O: nhận một lệnh Bash hoặc
  một mẫu `Grep`, trả về LOẠI (lọc-danh-sách-file · tìm-code · không-phải-tìm), các token tìm, và
  hình dạng đoán mò (≥ 3 nhánh `\|`/`|`, hoặc câu tự nhiên ≥ 3 từ). Hàm quyết định nhận thêm trạng
  thái request (đã gọi tầng khái niệm chưa, cách đó bao nhiêu lần tìm, token của prompt) và trả
  `allow` hoặc `deny` + lý do theo đúng 3 luật của spec §3 — Test:
  `python -m unittest discover tests -p test_search_rules.py` (đủ ca: lọc file, tên đơn, nhiều
  nhánh, câu tự nhiên, `rg`, `git grep`, `findstr`, `Select-String`, lệnh ghép `&&`/`|`/`;`)
  - Chạm: `scripts/search_rules.py`, `tests/test_search_rules.py` → file mới
  - Cần: T1.3
- [x] **T2.2** (e30m) `hooks/scripts/search_observe.py` — ghi sổ `docs/tdq/.tdq-search.jsonl` theo
  request (không có request → theo phiên): `PostToolUse` của lumen `semantic_search`, mọi
  `mcp__lsp__*`, và Bash `graphify query|explain|path|god-nodes|affected`; `UserPromptSubmit` →
  tập token định danh của prompt (không lưu nguyên văn); mỗi lần tìm code được đếm để tính cửa sổ.
  Sổ có trần dòng và rút gọn như sổ của cổng đọc — Test:
  `python -m unittest discover tests -p test_search_observe.py` (gồm ca: gọi `turn_log_clear`
  xong sổ vẫn còn)
  - Chạm: `hooks/scripts/search_observe.py`, `tests/test_search_observe.py` → file mới
- [ ] **T2.3** (e30m) `hooks/scripts/search_gate.py` — `PreToolUse` trên `Bash` và `Grep`: đọc sổ
  và file mốc sẵn sàng, gọi `search_rules`, in `deny` + lý do nêu ĐÚNG lệnh cần gọi (không bao giờ
  gợi ý tham số `path` của lumen). Tầng khái niệm chưa sẵn sàng → cho qua và nói tầng nào đang dựng.
  Mọi lỗi I/O/parse → cho qua, thoát 0 — Test:
  `python -m unittest discover tests -p test_search_gate.py` (gồm ca không spawn tiến trình, không
  đọc file code — dò trên AST như `test_read_gate`)
  - Chạm: `hooks/scripts/search_gate.py`, `tests/test_search_gate.py` → file mới
  - Cần: T2.1, T2.2
- [ ] **T2.4** (e15m) Cắm vào `hooks/hooks.json` (`PreToolUse` `Bash` + `Grep` → gate; `PostToolUse`
  lumen + lsp + `Bash` → observe; `UserPromptSubmit` → observe); thêm `.tdq-search.jsonl` vào
  `.gitignore`; cập nhật đếm entry ở test và README — Test:
  `python -m unittest discover tests -p test_subagent_start.py` và `-p test_build_portable.py`
  - Chạm: `hooks/hooks.json`, `.gitignore`, `README.md`, `tests/test_subagent_start.py` → cấu hình hook
  - Cần: T2.3
- [ ] **T2.5** (e20m) Chọn N bằng phát lại: chạy `search_replay.py` trên fixture với N = 5, 10, 15,
  20; chọn N nhỏ nhất bắt được lượt 7 + lượt 9 + mọi lần đoán mò sau cửa sổ, với 0 lần bắt oan một
  lần lọc danh sách file; ghi bảng bốn giá trị vào brief — Test: brief có bảng N và giá trị chốt;
  hằng số trong `search_rules.py` bằng đúng giá trị đó
  - Chạm: `scripts/search_rules.py` → hằng số cửa sổ
  - Cần: T2.1, T1.3

**Xong P2 khi**: phát lại trên fixture cho lượt 7 và 9 bị bắt, 0 lần bắt oan, và cổng đã cắm
trong `hooks.json`.

## P3 — Codex

- [ ] **T3.1** (e25m) Adapter Codex theo đúng kết quả T1.1: plugin nhận `hooks` → khai trong
  `.codex-plugin/plugin.json`; không nhận → `tdq-setup` ghi `.codex/hooks.json` cấp project (chỉ
  thêm entry, giữ cổng VÙNG FILE đang có). `search_gate.py` in dạng mà Codex đọc được (chỉ
  `deny`) — Test: `python -m unittest discover tests -p test_codex_search_gate.py`
  - Chạm: `.codex-plugin/plugin.json`, `.codex/hooks.json`, `hooks/scripts/search_gate.py`,
    `tests/test_codex_search_gate.py` → adapter Codex
  - Cần: T1.1, T2.3
- [x] **T3.2** (e30m) `scripts/tdq_codex_mcp.py` — khai MCP lumen + LSP vào `~/.codex/config.toml`:
  backup trước, chỉ thêm mục chưa có, không sửa mục sẵn có, chạy hai lần ra một kết quả; gọi từ
  `tdq_setup.py` — Test: `python -m unittest discover tests -p test_codex_mcp.py` (HOME tạm, có
  file config sẵn một MCP khác phải còn nguyên)
  - Chạm: `scripts/tdq_codex_mcp.py`, `tests/test_codex_mcp.py` → file mới
  - Cần: T1.1
- [ ] **T3.3** (e15m) Chạy thật trên máy: `tdq_codex_mcp.py` ghi config thật (có backup), `codex mcp
  list` thấy lumen + LSP; một lượt `codex exec` grep đoán mò bị `deny` — Test: output thật dán vào
  file QC ở mục Q9, Q10
  - Dùng: `tdq-setup`
  - Để: chạy đường cài thật của skill trên máy này — khai MCP cho Codex, kiểm 8 bậc + smoke 4 tầng
  - Ra: `~/.codex/config.toml` có lumen + LSP, kèm file backup cạnh nó
  - Kiểm: `codex mcp list` thấy cả hai; cấu hình MCP cũ còn nguyên
  - Không dùng cho: cài gói ngoài danh sách phụ thuộc đã khai
  - Cần: T3.1, T3.2

**Xong P3 khi**: Codex có hai công cụ và cổng chặn được nó trong một lượt chạy thật.

## P4 — Kiểm thật thay cho "có cài"

- [x] **T4.1** (e30m) Bậc 3 khởi động thật: chạy `agent-lsp doctor` (có trần thời gian), đọc
  `Status` của từng language server ứng với ngôn ngữ CỦA PROJECT; server nào `failed` → bậc 3 không
  đạt, kèm dòng `Error:` của nó — Test: `python -m unittest discover tests -p test_bac3_khoi_dong.py`
  (output doctor giả: 2 ok 2 failed → không đạt; 4 ok → đạt)
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_bac3_khoi_dong.py` → `bac3_*`
- [x] **T4.2** (e20m) Smoke grep theo ngôn ngữ thật: lấy đuôi file từ phép dò ngôn ngữ của bậc 7
  thay cho `*.py` cứng — Test: `python -m unittest discover tests -p test_smoke_ngon_ngu.py` (project
  tạm chỉ có `.ts` → đạt)
  - Chạm: `scripts/tdq_setup.py`, `tests/test_smoke_ngon_ngu.py` → `smoke_grep`
- [>] **T4.3** (e25m) Một lệnh kiểm: `tdq_lsp.py check` chạy 8 bậc rồi smoke 4 tầng; dòng tổng chỉ
  ĐẠT khi cả hai đạt; `tdq_setup.py` dùng lại đúng hàm đó — Test:
  `python -m unittest discover tests -p test_mot_lenh_kiem.py`
  - Chạm: `scripts/tdq_lsp.py`, `scripts/tdq_setup.py`, `tests/test_mot_lenh_kiem.py` → `check`, `main`
  - Cần: T4.1, T4.2

**Xong P4 khi**: trên excalidraw, gỡ tạm `tsserver` thì lệnh kiểm báo không đạt; trả lại thì đạt.

## P5 — Đường dẫn tuyệt đối

- [ ] **T5.1** (e35m) Một hàm dựng lệnh ở `scripts/tdq_state.py` trả đường dẫn tuyệt đối của
  plugin; dòng `Command:` của `next` và mọi lệnh hook in ra (`edit_gate`, `prompt_context`,
  `bash_gate`) dùng nó thay cho `python3 scripts/…` — Test:
  `python -m unittest discover tests -p test_duong_dan_tuyet_doi.py` (chạy hook với cwd là một thư
  mục tạm khác → mọi đường dẫn in ra là file có thật)
  - Chạm: `scripts/tdq_state.py`, `hooks/scripts/edit_gate.py`, `hooks/scripts/prompt_context.py`,
    `hooks/scripts/bash_gate.py`, `tests/test_duong_dan_tuyet_doi.py` → `next`, chuỗi nhắc

**Xong P5 khi**: không còn chuỗi `python3 scripts/` nào trong output máy in của hook.

## P6 — Tự khởi tạo ở đầu project

- [ ] **T6.1** (e40m) `tdq_setup.py --nen`: chạy nền phần đắt (cài phụ thuộc ĐÃ KHAI, dựng đồ thị
  graphify, index lumen), khoá pid `docs/tdq/.tdq-khoi-tao.lock` (pid chết → lấy lại được), trần
  thời gian, xong thì ghi file mốc sẵn sàng `docs/tdq/.tdq-san-sang.json` theo từng tầng — Test:
  `python -m unittest discover tests -p test_tu_khoi_tao.py` (lệnh giả thay cho lumen/graphify)
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tu_khoi_tao.py` → `main`, hàm mới `khoi_tao_nen`
  - Cần: T4.3
- [ ] **T6.2** (e30m) `session_start.py`: dò RẺ bằng file mốc (không gọi tiến trình đo); chưa sẵn
  sàng và không có khoá sống → bật `--nen` tách rời (Windows: cờ tiến trình tách rời) rồi trả về
  ngay, in `[TDQ:SEARCH]` nói tầng nào đang dựng — Test: `-p test_tu_khoi_tao.py` thêm ca: hook trả
  về dưới ngân sách thời gian; hai lần gọi liền nhau → một tiến trình
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_tu_khoi_tao.py` → `main`
  - Cần: T6.1
- [ ] **T6.3** (e10m) `search_gate.py` đọc `.tdq-san-sang.json`: tầng khái niệm chưa sẵn sàng → cho
  qua kèm câu nói tầng đang dựng (Q6) — Test: `-p test_search_gate.py` ca "chưa sẵn sàng"
  - Chạm: `hooks/scripts/search_gate.py`, `tests/test_search_gate.py` → `main`
  - Cần: T6.1, T2.3

**Xong P6 khi**: một project tạm chưa có index → mở phiên giả → tiến trình nền chạy, hook đã trả
về, và cổng không chặn trong lúc dựng.

## P7 — Hồ sơ kiến trúc và luật

- [ ] **T7.1** (e15m) `docs/kien-truc.md` thêm dòng chốt 2026-10-03 (điểm chặn thứ hai, lý do,
  điều kiện chặn); mã `TDQ:SEARCH` vào `_common.CODES` kèm dòng lý do có ngày và vào bảng
  `reminder-codes.md` — Test: `python -m unittest discover tests -p test_common.py`
  - Chạm: `hooks/scripts/_common.py` → `CODES`
- [ ] **T7.2** (e15m) `uu-tien-tim-kiem.md` thêm mục ngắn "cổng giữ luật này thế nào" (ba luật,
  cửa sổ N, cách được mở khoá); giữ dưới trần 3.500 token, sinh lại chỉ mục và tệp khoá — Test:
  `python scripts/token_budget.py --kiem` thoát 0 và `python scripts/doc_index.py --kiem --tat-ca`
  thoát 0

## P8 — Log, test, đo, ba hệ

- [ ] **T8.1** (e15m) Log service của mọi file mã mới: timestamp, đủ chi tiết debug, tắt bằng
  `TDQ_LOG=0` — Test: `-k log` xanh trên `test_search_rules.py`, `test_search_observe.py`,
  `test_search_gate.py`, `test_search_replay.py`, `test_codex_mcp.py`, `test_tu_khoi_tao.py`
- [ ] **T8.2** (e10m) Trọn bộ test một lệnh — Test: `python -m unittest discover tests` xanh
  - Cần: T8.1
- [ ] **T8.3** (e15m) Phép đo cuối Q18: phát lại fixture với N đã chốt, dán bảng và ba số đếm vào
  file QC — Test: lượt 7, 9 bị bắt; 0 bắt oan
  - Cần: T8.2
- [ ] **T8.4** (e20m) Chạy trọn bộ test trên macOS thật (pyenv + brew, thư mục tạm, dọn sạch);
  Linux nếu máy đã bật — Test: không fail, không error, không cài gì lên máy
  - Cần: T8.2
- [ ] **T8.5** (e15m) Soát lỗi đúng-sai toàn bộ thay đổi — Test: mọi phát hiện được xử lý hoặc ghi
  lý do bác bỏ vào file QC
  - Dùng: `code-review`
  - Để: tìm lỗi đúng-sai trong cổng, sổ, adapter Codex và dựng nền, trước phase qc
  - Ra: danh sách phát hiện kèm phán quyết ở `docs/tdq/qc/2026-10-03-0015-ep-luat-tim-kiem.md`
  - Kiểm: mục QC của file đó có một dòng cho mỗi phát hiện
  - Không dùng cho: rút gọn code — đó là T8.6
  - Cần: T8.4
- [ ] **T8.6** (e10m) Rút gọn phần trùng lặp — Test: trọn bộ test vẫn xanh
  - Dùng: `simplify`
  - Để: gỡ trùng lặp trong mã mới, không đổi hành vi
  - Ra: mã đã rút gọn
  - Kiểm: `python -m unittest discover tests`
  - Không dùng cho: săn lỗi đúng-sai — đó là T8.5
  - Cần: T8.5

## Cụm song song

Bốn cụm không giao nhau về file, chạy được song song sau P1:

| Cụm | Task | Vùng file |
|---|---|---|
| cổng | T2.1–T2.5, T6.3 | `scripts/search_rules.py`, `hooks/scripts/search_*.py`, `hooks/hooks.json` |
| codex | T3.1–T3.3 | `.codex-plugin/`, `.codex/`, `scripts/tdq_codex_mcp.py` |
| kiểm thật + khởi tạo | T4.1–T4.3, T6.1–T6.2 | `scripts/tdq_lsp.py`, `scripts/tdq_setup.py`, `hooks/scripts/session_start.py` |
| đường dẫn | T5.1 | `scripts/tdq_state.py`, `edit_gate`/`prompt_context`/`bash_gate` |

T3.1 chạm `search_gate.py` của cụm cổng — nên cụm codex phải đi SAU T2.3.

## Luật file nóng

| File | Task chạm | Cách xử |
|---|---|---|
| `hooks/scripts/search_gate.py` | T2.3, T3.1, T6.3 | **một chủ ghi duy nhất**: cả ba do cụm cổng làm, theo thứ tự T2.3 → T6.3 → T3.1 |
| `scripts/tdq_setup.py` | T4.2, T4.3, T6.1 | nâng lên đợt sớm, làm tuần tự trong cụm kiểm thật |
| `scripts/tdq_lsp.py` | T4.1, T4.3 | tuần tự trong cụm kiểm thật |
| `scripts/search_rules.py` | T2.1, T2.5 | tuần tự trong cụm cổng |
| `tests/test_search_gate.py`, `tests/test_tu_khoi_tao.py` | 2 task mỗi file | đi theo chủ của file mã tương ứng |

## Definition of Done

Trỏ về §6 của spec. Lệnh dạng `discover` vì `tests/` cố ý không là package.

- [ ] Q1 Chặn đoán mò trước tầng khái niệm — `python -m unittest discover tests -p test_search_rules.py -k doan_mo`
- [ ] Q2 Không chặn tên chính xác trong cửa sổ — `… -p test_search_rules.py -k cua_so`
- [ ] Q3 Không chặn lọc danh sách file — `… -p test_search_rules.py -k loc_file`
- [ ] Q4 Mở khoá sau tầng khái niệm — `… -p test_search_rules.py -k mo_khoa`
- [ ] Q5 Sổ sống qua lượt — `… -p test_search_observe.py -k qua_luot`
- [ ] Q6 Không gây kẹt — `… -p test_search_gate.py -k chua_san_sang`
- [ ] Q7 Cổng rẻ — `… -p test_search_gate.py -k nhe`
- [ ] Q8 Cổng không làm vỡ lệnh — `… -p test_search_gate.py -k hong`
- [ ] Q9 Codex bị chặn thật — output thật của T3.3 trong file QC
- [ ] Q10 Codex có công cụ — `codex mcp list` + `… -p test_codex_mcp.py`
- [ ] Q11 Bậc 3 thật — `… -p test_bac3_khoi_dong.py`
- [ ] Q12 Smoke grep đa ngôn ngữ — `… -p test_smoke_ngon_ngu.py`
- [ ] Q13 Một lệnh kiểm — `… -p test_mot_lenh_kiem.py`
- [ ] Q14 Đường dẫn tuyệt đối — `… -p test_duong_dan_tuyet_doi.py`
- [ ] Q15 Tự khởi tạo — `… -p test_tu_khoi_tao.py -k kich_hoat`
- [ ] Q16 Không chạy chồng — `… -p test_tu_khoi_tao.py -k chong`
- [ ] Q17 Quyết định kiến trúc — `grep -n "2026-10-03" docs/kien-truc.md` + `… -p test_common.py`
- [ ] Q18 Phát lại phiên thật — `python scripts/search_replay.py tests/fixtures/phien_excalidraw_tim.json`
- [ ] Q19 Ba hệ — trọn bộ test trên Windows và macOS thật; Linux khi máy bật
- [ ] Q20 Ràng buộc kiến trúc — `grep -rn "^import hooks\|from hooks" scripts` → 0 dòng
- [ ] Q21 Luật mở đầu — `… -p test_search_rules.py -k mo_dau`
- [ ] Q22 Ngoại lệ tên đã biết — `… -p test_search_rules.py -k ten_trong_prompt`
- [ ] Q23 Cửa sổ hết hạn — `… -p test_search_rules.py -k het_han`
