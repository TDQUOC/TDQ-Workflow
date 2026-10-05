# PLAN — Chạy test vùng chạm + bán kính ảnh hưởng ở bước trung gian, trọn bộ chỉ ở 2 cổng

Ngày: 2026-10-03 · Spec: ../spec/2026-10-03-1907-test-vung-cham-buoc-trung-gian.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py simulate` trên chính plan này: đội thắng 3,0 phút (21,5 so với 24,4), 12 task chia 7 đợt, giao 8, leader giữ 4 (file luật `skills/` và các task cổng); cụm runner tuần tự vì một file nóng, cụm shell chạy song song từ đầu (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (2026-10-05, "duyệt plan" · mode "1a" = subagent) · 12 task · ETA 255 phút

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Script chạy test theo bán kính
- P2 — `next` nhắc khi vượt số cổng
- P3 — Luật một nguồn
- P4 — Test chạy được từ mọi shell
- P5 — Log, test, soát, phát hành
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo. P1 đi trước: luật mới (P3) trỏ vào lệnh của P1.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này.
3. Bước trung gian chạy test của module đang sửa; trọn bộ chạy ở T5.2 (cổng QC-F1 của request
   này) — request này áp đúng luật nó đang viết.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass. Ngưỡng trượt → áp cột
   `Dự phòng nếu trượt` của spec §6, `lech add`, làm tiếp.
6. Không commit/push cho đến khi user yêu cầu (trừ commit mở khoá, liệt kê ở report).
7. **Luật kiến trúc phải giữ:** `scripts/` không import `hooks/` — `tdq_test.py` chỉ ĐỌC mã
   `hooks/scripts/` bằng AST.

## P1 — Script chạy test theo bán kính

- [x] **T1.1** (e40m) `scripts/tdq_test.py` → hàm thuần `ban_kinh(files, repo)`: chọn module test
  nhắc đường dẫn tương đối / tên module của file sửa; cộng import bắc cầu (AST) trong `scripts/`,
  `hooks/scripts/`; cộng test QUÉT thư mục cha (`os.walk`/`glob`/`listdir` trên đường dẫn dựng từ
  `skills`/`hooks`/`scripts`/`agents`/`tests`, dò bằng AST); trả `(modules, ly_do_tron_bo)` — rơi
  về trọn bộ khi bán kính ≥ 60% số module hoặc có file ngoài 5 thư mục — Test:
  `python -m unittest discover tests -p test_tdq_test.py -k ban_kinh`
  - Chạm: `scripts/tdq_test.py` → file mới; `tests/test_tdq_test.py` → file mới
- [x] **T1.2** (e30m) Lệnh `tdq_test.py vung-cham [--files …]`: không có `--files` thì lấy file
  đổi từ git so với `nhanh_goc` (cộng file chưa commit); chạy các module đã chọn trong MỘT tiến
  trình (`unittest` loader); ghi tập module đã chọn vào sổ; log ISO ra stderr, tắt bằng
  `TDQ_LOG=0` — Test: `python -m unittest discover tests -p test_tdq_test.py -k vung_cham`
  - Chạm: `scripts/tdq_test.py` → `cmd_vung_cham`; `tests/test_tdq_test.py` → lớp `VungCham`
  - Cần: T1.1
- [x] **T1.3** (e30m) Lệnh `tdq_test.py tron-bo` + sổ `docs/tdq/.tdq-test.jsonl` (gitignore): mỗi
  lần trọn bộ một dòng (thời điểm, khoá request, phase, kết quả, giây); module đỏ chưa từng được
  `vung-cham` chọn trong request → dòng "bỏ sót"; `tdq_test.py so [--json]` in số lần trọn bộ và
  số lần bỏ sót — Test: `python -m unittest discover tests -p test_tdq_test.py -k so`
  - Chạm: `scripts/tdq_test.py` → `cmd_tron_bo`, `cmd_so`; `tests/test_tdq_test.py` → lớp `So`; `.gitignore`
  - Cần: T1.2

**Xong P1 khi**: ba ca đo ở brief cho ra đúng bán kính (lá 2 · `stop_gate.py` ~11 · `qc.md` ~7 +
test quét `skills/` · `tdq_state.py` → trọn bộ).

## P2 — `next` nhắc khi vượt số cổng

- [x] **T2.1** (e20m) `render_next` ở phase implement/qc đọc `tdq_test.py so`: số lần trọn bộ của
  request vượt 2 (3 khi đã có vòng sửa QC) → một dòng nhắc chạy `vung-cham`; im khi chưa vượt —
  Test: `python -m unittest discover tests -p test_next_tron_bo.py`
  - Chạm: `scripts/tdq_state.py` → `render_next`; `tests/test_next_tron_bo.py` → file mới
  - Cần: T1.3

## P3 — Luật một nguồn

- [x] **T3.1** (e30m) Viết lại luật chạy test ở ba file cho cùng nói: bước trung gian =
  `tdq_test.py vung-cham`; trọn bộ = 2 cổng (QC-F1 thay cho "xong implement"; sau vòng sửa QC cuối
  nếu có sửa); report in số lần bỏ sót. `tdq-build/SKILL.md` không quá 174 dòng; `plan-template.md`
  quy tắc 3 viết lại không dài hơn bản cũ; sinh lại token budget, chỉ mục dòng, bảng khoá luật —
  Test: `python -m unittest discover tests -p test_luat_test.py`
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-build/references/qc.md`, `docs/tdq/audit/luat-hien-co.md`, `docs/tdq/token-budget.json`; `tests/test_luat_test.py` → file mới
  - Cần: T1.3
- [>] **T3.2** (e10m) `docs/kien-truc.md` dòng 2026-10-03 (yêu cầu 1907): 2 cổng trọn bộ, bán kính
  tính bằng máy, rơi về trọn bộ khi không chắc, sổ bỏ sót; `next` nhắc, không chặn — Test:
  `python -c "t=open('docs/kien-truc.md',encoding='utf-8').read();assert '2026-10-03 (yêu cầu 1907)' in t"`
  - Chạm: `docs/kien-truc.md`
  - Cần: T3.1

## P4 — Test chạy được từ mọi shell

- [>] **T4.1** (e30m) Tìm và sửa mọi test gọi lệnh `true` của shell (dòng `Test:` trong plan mẫu,
  `subprocess` …) ở `test_bench`, `test_team_mode`, `test_team_chong_conflict`, `test_gitflow_doi`,
  `test_timing`: thay bằng lệnh tương đương luôn thoát 0 qua trình thông dịch Python, giữ nguyên ý
  nghĩa từng ca — Test: `powershell.exe -NoProfile -Command "python -m unittest discover tests -p 'test_team_mode.py'; if ($LASTEXITCODE) { exit 1 }; python -m unittest discover tests -p 'test_bench.py'; if ($LASTEXITCODE) { exit 1 }"` (và tương tự ba module còn lại)
  - Chạm: `tests/test_bench.py`, `tests/test_team_mode.py`, `tests/test_team_chong_conflict.py`, `tests/test_gitflow_doi.py`, `tests/test_timing.py`

## P5 — Log, test, soát, phát hành

- [x] **T5.1** (e10m) Log service của `tdq_test.py`: ISO timestamp, tập file, số module chọn, lý do
  rơi về trọn bộ, giây chạy; tắt bằng `TDQ_LOG=0` — Test:
  `python -m unittest discover tests -p test_tdq_test.py -k log`
  - Cần: T1.3
- [ ] **T5.2** (e15m) Cổng QC-F1 của chính request này: `tdq_test.py tron-bo` từ Git Bash xanh, và
  trọn bộ từ PowerShell 0 fail 0 error — Test: `python scripts/tdq_test.py tron-bo` thoát 0
  - Cần: T2.1, T3.2, T4.1, T5.1
- [ ] **T5.3** (e20m) Soát lỗi đúng-sai toàn bộ thay đổi — Test: mọi phát hiện được xử lý hoặc ghi
  lý do bác bỏ vào file QC
  - Dùng: `code-review`
  - Để: tìm lỗi đúng-sai trong bán kính, sổ trọn bộ/bỏ sót, nhắc `next`
  - Ra: danh sách phát hiện kèm phán quyết ở `docs/tdq/qc/2026-10-03-1907-test-vung-cham-buoc-trung-gian.md`
  - Kiểm: mục soát lỗi của file đó có một dòng cho mỗi phát hiện
  - Không dùng cho: rút gọn code — đó là T5.4
  - Cần: T5.2
- [ ] **T5.4** (e10m) Rút gọn phần trùng lặp — Test: `python scripts/tdq_test.py vung-cham` xanh
  - Dùng: `simplify`
  - Để: gỡ trùng lặp trong mã mới, không đổi hành vi
  - Ra: mã đã rút gọn
  - Kiểm: `python scripts/tdq_test.py vung-cham`
  - Không dùng cho: săn lỗi đúng-sai — đó là T5.3
  - Cần: T5.3
- [ ] **T5.5** (e10m) CHANGELOG 0.57.0, bump hai `plugin.json` — Test:
  `python scripts/doc_lint.py CHANGELOG.md` thoát 0
  - Chạm: `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
  - Cần: T5.4

## Cụm song song

| Cụm | Task | Vùng file |
|---|---|---|
| runner | T1.1–T1.3 | `scripts/tdq_test.py`, `tests/test_tdq_test.py`, `.gitignore` |
| state | T2.1 | `scripts/tdq_state.py`, `tests/test_next_tron_bo.py` |
| luat | T3.1, T3.2 | `skills/**`, `docs/kien-truc.md`, `docs/tdq/audit/`, `docs/tdq/token-budget.json` |
| shell | T4.1 | 5 file test đang gọi `true` — độc lập, chạy song song với cụm runner ngay từ đầu |

## Luật file nóng

| File | Task chạm | Cách xử |
|---|---|---|
| `scripts/tdq_test.py`, `tests/test_tdq_test.py` | T1.1, T1.2, T1.3 | một chủ ghi, tuần tự T1.1 → T1.2 → T1.3 |

## Definition of Done

Trỏ về §6 của spec. Lệnh dạng `discover` vì `tests/` cố ý không là package.

- [ ] Q1 Bán kính đúng ở ca đã đo — `python -m unittest discover tests -p test_tdq_test.py -k ca_da_do`
- [ ] Q2 Không bỏ sót test gọi qua tiến trình con — `… -p test_tdq_test.py -k tien_trinh_con`
- [ ] Q3 Dò file luật theo đường dẫn — `… -p test_tdq_test.py -k duong_dan`
- [ ] Q3b Test quét thư mục được chọn — `… -p test_tdq_test.py -k quet_thu_muc`
- [ ] Q4 Rơi về trọn bộ đúng lúc — `… -p test_tdq_test.py -k tron_bo_khi`
- [ ] Q5 Bước trung gian nhanh với file lá/luật — `python scripts/tdq_test.py vung-cham --files hooks/scripts/stop_gate.py` (giây ở log ≤ 60)
- [ ] Q6 Sổ trọn bộ — `… -p test_tdq_test.py -k so` + `… -p test_next_tron_bo.py`
- [ ] Q6b Sổ bán kính bỏ sót — `… -p test_tdq_test.py -k bo_sot`
- [ ] Q7 Luật một nguồn — `… -p test_luat_test.py`
- [ ] Q8 Chạy từ mọi shell — `powershell.exe -NoProfile -Command "python -m unittest discover tests"` 0 fail 0 error
- [ ] Q9 Trọn bộ xanh — `python scripts/tdq_test.py tron-bo` từ Git Bash thoát 0
- [ ] Q10 Trần token — `python scripts/token_budget.py --kiem` thoát 0 và `python scripts/doc_lint.py skills` thoát 0
- [ ] Q11 Kiến trúc — `grep -rn "^import hooks\|^from hooks" scripts` rỗng + dòng 2026-10-03 (yêu cầu 1907) trong `docs/kien-truc.md`
- [ ] Q12 Tiết kiệm báo trung thực — report có cả nền cũ (TB 7,4 lần/request) và nền mới (2–3 lần)
