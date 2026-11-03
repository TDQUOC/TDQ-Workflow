# PLAN — Slug có giờ phút + đếm thời gian mỗi request và mỗi phase

Ngày: 2026-08-15 · Spec: ../spec/2026-08-15-gio-phut-dem-thoi-gian.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — các task nối nhau trên cùng hai file (`tdq_state.py`, `tdq_timing.py`), tách worktree chỉ đẻ xung đột merge (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Nền: slug hai định dạng và mốc thời gian trong state

- [x] **T1.1** (n5 e12m) Viết `parse_slug(slug)` trong `scripts/tdq_state.py`, trả về
  `(ngay, gio_phut_hoặc_None, phan_chu)`, chấp nhận cả `YYYY-MM-DD-<kebab>` lẫn
  `YYYY-MM-DD-HHMM-<kebab>`, trả `None` khi không khớp — Test: `pytest tests/test_timing.py -k "parse_slug_cu or parse_slug_moi or parse_slug_sai"` xanh
  - Chạm: `scripts/tdq_state.py` (hàm mới, chưa ai gọi) → không node nào phụ thuộc
- [x] **T1.2** (n5 e10m) `init` từ chối slug thiếu giờ phút, thông báo nêu đúng công thức
  `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>` và thoát khác 0 — Test: `pytest tests/test_timing.py -k init_bat_buoc`
  - Chạm: `cli()` của `tdq_state.py` (node Hub, 17 bậc) → `graphify affected "cli" --depth 2` báo không node nào phụ thuộc
  - DoD hồi quy riêng cho node Hub: `pytest tests/test_state.py tests/test_next.py -q` xanh
- [x] **T1.3** (n5 e12m) Thêm `started_at` và `phase_history` vào `default_state()`, nâng
  `schema_version` lên 4; `load()` vá field thiếu cho state cũ — Test: `pytest tests/test_timing.py -k state_cu`
  - Chạm: `default_state()`, `load()` trong `scripts/tdq_state.py` → mọi lệnh của CLI này đọc chung hai hàm đó
- [x] **T1.4** (n5 e12m) Nhánh `set phase=` append `{phase, at}` vào `phase_history`; `init`
  đóng dấu `started_at` — Test: `pytest tests/test_timing.py -k phase_history`

**Xong P1 khi**: `python3 -m pytest tests/test_timing.py tests/test_state.py -q` xanh và
`state.json` sinh mới có đủ `started_at`, `phase_history`.

## P2 — CLI đo thời gian

- [x] **T2.1** (n8 e25m) Tạo `scripts/tdq_timing.py` lệnh `show`: đọc state, dựng cửa sổ từng
  phase từ `phase_history`, in bảng markdown có cột phase · treo tường · số lần vào — Test:
  `pytest tests/test_timing.py -k bang_thoi_gian`
- [x] **T2.2** (n5 e10m) Phase vào lại lần hai thì cộng dồn thời gian và tăng số lần, in dạng
  `spec: 24 phút / 2 lần` — Test: `pytest tests/test_timing.py -k quay_lui`
- [x] **T2.3** (n8 e20m) Thêm cột thời gian model: cộng khoảng cách giữa các bước model nằm
  trong cửa sổ phase, tái dùng `iter_events`, `_parse_time`, `MAX_GAP_SECONDS` của
  `scripts/step_audit.py` — Test: `pytest tests/test_timing.py -k thoi_gian_model`
  - Chạm: `scripts/step_audit.py` (chỉ import, không sửa) → `tests/test_step_budget.py` phải còn xanh
- [x] **T2.4** (n3 e8m) Khoảng chờ dài hơn `MAX_GAP_SECONDS` không tính vào thời gian model —
  Test: `pytest tests/test_timing.py -k nguong_cho`
- [x] **T2.5** (n3 e8m) Không tìm thấy transcript thì cột model in `—` kèm một dòng lý do,
  thoát 0 — Test: `pytest tests/test_timing.py -k khong_transcript`
- [x] **T2.6** (n5 e12m) Lệnh `close`: append đúng một dòng JSON hợp lệ vào
  `docs/tdq/timing.jsonl` (slug, lane, mốc mở/đóng, tổng treo tường, tổng model, bảng phase) —
  Test: `pytest tests/test_timing.py -k dong_so`

**Xong P2 khi**: `python3 scripts/tdq_timing.py show` chạy được trên repo thật và
`pytest tests/test_timing.py -q` xanh.

## P3 — Nối vào workflow

- [x] **T3.1** (n5 e12m) `init` đóng sổ request cũ vào `timing.jsonl` TRƯỚC khi reset state —
  Test: `pytest tests/test_timing.py -k init_dong_so`
  - Chạm: lệnh `init` trong `scripts/tdq_state.py` → `tests/test_state.py` phải còn xanh
- [x] **T3.2** (n5 e12m) `tdq_finish.py --phase idle` gọi đóng sổ, in kết quả vào dòng tổng kết —
  Test: `pytest tests/test_timing.py -k finish_dong_so`
  - Chạm: `main()` của `scripts/tdq_finish.py` (node Hub, 20 bậc) → `graphify affected "tdq_finish" --depth 2` báo không node nào phụ thuộc
  - DoD hồi quy riêng cho node Hub: `pytest tests/test_stop_gate.py tests/test_plan_tick.py -q` xanh
- [x] **T3.3** (n3 e10m) Khuôn report bắt buộc có bảng thời gian, chỉ nhắc TÊN LỆNH
  `tdq_timing.py show` — Test: `pytest tests/test_timing.py -k khuon_report`
- [x] **T3.4** (n3 e8m) `skills/tdq-status/SKILL.md` thêm dòng đồng hồ của phase đang chạy —
  Test: `pytest tests/test_timing.py -k status_dong_ho`

**Xong P3 khi**: chạy thử một request giả từ `init` tới `--phase idle` sinh đúng một dòng
trong `timing.jsonl`.

## P4 — Đổi công thức slug trong luật

- [x] **T4.1** (n3 e10m) Sửa 9 chỗ in công thức slug ở `skills/` và `scripts/tdq_state.py`
  bảng `next`, `docs/tdq/STATE.md` — Test: `grep -rn "YYYY-MM-DD-" skills scripts docs/tdq/STATE.md` mọi dòng đều có `HHMM`
- [x] **T4.2** (n3 e8m) Đồng bộ bản `portable/`: `AGENTS.md:79`, `workflow/phases.md` (4 chỗ),
  `workflow/01-intake.md:26` — Test: `pytest tests/test_timing.py -k portable_dong_bo`

**Xong P4 khi**: `python3 scripts/doc_lint.py` exit 0 trên mọi file đã sửa.

## P5 — Log & test bắt buộc

- [x] **T5.1** (n3 e8m) Log service của `tdq_timing.py`: timestamp ra stderr, bật mặc định,
  tắt bằng `TDQ_LOG=0` — Test: `TDQ_LOG=0 python3 scripts/tdq_timing.py show 2>err >/dev/null; wc -l < err` ra 0
- [x] **T5.2** (n5 e10m) `tests/test_timing.py` phủ đủ 20 hạng mục QC của spec §6 — Test:
  `pytest tests/test_timing.py -q` xanh và `python3 -m pytest -q` không hồi quy

## P6 — Phát hành

- [x] **T6.1** (n3 e8m) CHANGELOG mục 0.20.0 + `.claude-plugin/plugin.json` lên 0.20.0 —
  Test: `grep -c "0.20.0" CHANGELOG.md .claude-plugin/plugin.json` cả hai ≥ 1
- [x] **T6.2** (n3 e10m) Viết `docs/tdq/qc/<slug>.md` và `docs/tdq/reports/<slug>.md`, report
  có bảng thời gian thật của chính request này — Test: `python3 scripts/doc_lint.py` hai file đó exit 0

## Definition of Done

Trỏ về §6 của spec (Q1–Q20). Liệt kê lại lệnh kiểm:

| # | Lệnh kiểm |
|---|---|
| Q1 | `grep -rn "YYYY-MM-DD-" skills scripts docs/tdq/STATE.md portable` — mọi dòng có `HHMM` |
| Q2 | `pytest tests/test_timing.py -k parse_slug_cu` |
| Q3 | `pytest tests/test_timing.py -k parse_slug_moi` |
| Q4 | `pytest tests/test_timing.py -k init_bat_buoc` |
| Q5 | `pytest tests/test_timing.py -k phase_history` |
| Q6 | `pytest tests/test_timing.py -k quay_lui` |
| Q7 | `pytest tests/test_timing.py -k state_cu` |
| Q8 | `pytest tests/test_timing.py -k bang_thoi_gian` |
| Q9 | `pytest tests/test_timing.py -k khong_transcript` |
| Q10 | `pytest tests/test_timing.py -k nguong_cho` |
| Q11 | `pytest tests/test_timing.py -k dong_so` |
| Q12 | `pytest tests/test_timing.py -k init_dong_so` |
| Q13 | `pytest tests/test_timing.py -k finish_dong_so` |
| Q14 | `pytest tests/test_timing.py -k khuon_report` |
| Q15 | `pytest tests/test_timing.py -k status_dong_ho` |
| Q16 | `TDQ_LOG=0 python3 scripts/tdq_timing.py show 2>err >/dev/null; wc -l < err` ra 0 |
| Q17 | `time python3 scripts/tdq_timing.py show` dưới 2,0 giây |
| Q18 | `python3 -m pytest -q` không đỏ, số test ≥ 608 |
| Q19 | `python3 scripts/doc_lint.py <các file tài liệu đã sửa>` exit 0 |
| Q20 | `grep -c "0.20.0" CHANGELOG.md .claude-plugin/plugin.json` cả hai ≥ 1 |
| QC-F1 | `python3 -m pytest -q` toàn suite |
| QC-F2 | Hồi quy mọi vùng `Chạm:`: `pytest tests/test_state.py tests/test_next.py tests/test_step_budget.py tests/test_stop_gate.py tests/test_plan_tick.py -q` |
| QC-F3 | Ràng buộc kiến trúc spec §5: `grep -c "state.json" scripts/tdq_timing.py` phải là 0 lần GHI; file mới nằm trong `scripts/`; skill chỉ nhắc tên lệnh |

## QC vòng 1 — fix

- [x] **QC1.1** (n2) `tong_hop`: tổng cột "Model chạy" đo trên đúng cửa sổ của tổng cột
  "Treo tường" (`started_at` → `ket_thuc`), thay vì cộng các cửa sổ phase — hai tổng phải
  trả lời cùng một câu hỏi — Test: `pytest tests/test_timing.py -k "bang_thoi_gian or tong_model"`
