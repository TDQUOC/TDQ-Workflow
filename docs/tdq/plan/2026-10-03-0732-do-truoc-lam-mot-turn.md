# PLAN — Đo trước ở spec, implement chạy hết plan trong một lượt

Ngày: 2026-10-03 · Spec: ../spec/2026-10-03-0732-do-truoc-lam-mot-turn.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py simulate` trên chính plan này: đội thắng 16,2 phút (18,4 so với 34,6), 17 task chia 5 đợt, giao 8, leader giữ 9 vì `tdq_state.py` là file nóng của 4 task (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (2026-10-03, "Duyệt plan" · mode "1a" = subagent) · 17 task · ETA 245 phút

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Luật R14 và cổng duyệt spec
- P2 — Lệch spec và tạm dừng có phân loại
- P3 — Hook nhắc và lời chặn
- P4 — Luật dừng, khuôn spec, QC và report
- P5 — Soát, rút gọn, phát hành
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo. P1 đi trước: `approve spec` (P1) và `next` ở
   report (P2) dựa vào hàm của R14 và lệnh `lech`.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu (trừ commit mở khoá, liệt kê ở report).
7. **Luật kiến trúc phải giữ:** `scripts/` không import `hooks/`; mọi deny qua `_common.block()`;
   hook mới `ask_gate.py` CHỈ nhắc qua `_common.remind()`.
8. **Áp luật mới cho chính plan này:** gặp ngưỡng trượt (ví dụ token một file luật vượt 3.500) →
   áp cột `Dự phòng nếu trượt` của spec §6, ghi một dòng vào working log, làm tiếp. Không dừng hỏi.

## P1 — Luật R14 và cổng duyệt spec

- [x] **T1.1** (e30m) `doc_lint.py` thêm R14 cho file trong `docs/tdq/spec/`: tìm bảng §6, nhận
  hàng `| Qn |` có ngưỡng số trong cột điều kiện (so sánh + số khác 0/1, hoặc số + đơn vị), đòi cột
  `Đo trước` và `Dự phòng nếu trượt` có mặt, không rỗng/`—`, và ô `Đo trước` chứa ít nhất một con
  số. Chỉ áp cho slug từ `2026-10-03-0732`. Hàm thuần `r14_loi(text, ten_file)` để `tdq_state`
  gọi được — Test: `python -m unittest discover tests -p test_doc_lint_r14.py`
  - Chạm: `scripts/doc_lint.py` → `rule_r14`, `r14_loi`, nhánh `is_output`; `tests/test_doc_lint_r14.py` → file mới
- [x] **T1.2** (e15m) Độ chính xác trên spec thật: lấy 10 hàng có ngưỡng từ spec cũ (cố định
  trong test, chép nguyên văn) + 10 hàng không ngưỡng (`≥ 1`, `0 failure`, số phiên bản, mã Qn);
  R14 nhận đúng ≥ 9/10 và không bắt oan hàng nào; `doc_lint docs/tdq/spec` → 0 lỗi R14 —
  Test: `python -m unittest discover tests -p test_doc_lint_r14.py -k chinh_xac`
  - Chạm: `scripts/doc_lint.py` → bộ nhận ngưỡng (bỏ miễn trừ inline code); `tests/test_doc_lint_r14.py` → lớp `ChinhXac`
  - Cần: T1.1
- [x] **T1.3** (e25m) `approve spec` gọi `doc_lint.r14_loi` trên `spec_file`: còn lỗi → in từng
  hàng thiếu, exit ≠ 0, không ghi duyệt; `--bo-qua-do "<lý do>"` → duyệt, lưu
  `spec_bo_qua_do = {ly_do, at}` vào state — Test: `python -m unittest discover tests -p test_approve_do_truoc.py`
  - Chạm: `scripts/tdq_state.py` → `_cli_approve`, `default_state`; `tests/test_approve_do_truoc.py` → file mới
  - Cần: T1.1

**Xong P1 khi**: spec có hàng `≤ 200 MB` thiếu đo không duyệt được; spec này duyệt được.

## P2 — Lệch spec và tạm dừng có phân loại

- [x] **T2.1** (e30m) Lệnh `lech`: `add --q Qn --nguong "<…>" --do "<…>" --chon "<phương án>"
  --ly-do "<…>"` · `list [--json]` · `duyet <id> --by "<lời user>"` · `bac <id> --by "<…>"`.
  Lưu `lech_spec: [{id, q, nguong, do, chon, ly_do, trang_thai: cho|duyet|bac, at, by}]`; alias
  tiếng Việt trong `tdq_ten_lenh.py` nếu bảng có khuôn đó — Test: `python -m unittest discover tests -p test_lech_spec.py`
  - Chạm: `scripts/tdq_state.py` → `_cli_lech`, `default_state`, `cli`; `scripts/tdq_ten_lenh.py` → bảng alias; `tests/test_lech_spec.py` → file mới
- [x] **T2.2** (e20m) `pause --loai <mat-truy-cap|pha-huy|dau-vao-user|tran-qc> --ly-do "<…>"`:
  thiếu `--loai`, loại ngoài danh sách (kể cả `doi-spec`) → từ chối kèm danh sách 4 loại và câu
  "ngưỡng trượt → dùng `lech add`, không dừng"; state lưu `loai` — Test: `python -m unittest discover tests -p test_implement_pause.py`
  - Chạm: `scripts/tdq_state.py` → `_cli_implement_pause`; `tests/test_implement_pause.py` → các ca gọi `pause`
  - Cần: T2.1
- [>] **T2.3** (e20m) `next` ở phase `qc` và `report` in mọi lệch `cho` (Qn, ngưỡng, đo, phương án)
  và câu hỏi duyệt; checklist report thêm dòng "hỏi user duyệt từng lệch; bác → task fix, quay lại
  implement" — Test: `python -m unittest discover tests -p test_lech_spec.py -k next`
  - Chạm: `scripts/tdq_state.py` → `PHASE_TABLE["report"]`, `render_next`; `tests/test_lech_spec.py` → lớp `NextHienLech`
  - Cần: T2.1

## P3 — Hook nhắc và lời chặn

- [x] **T3.1** (e25m) `hooks/scripts/ask_gate.py` (PreToolUse `AskUserQuestion`): phase
  `implement`/`qc` và không có `implement_pause` → `_common.remind(…, "TDQ:ASK", …)` nhắc: ngưỡng
  trượt → `lech add` + làm tiếp; chỉ hỏi khi thuộc 4 loại bất khả kháng thì khai `pause --loai`
  trước. Không bao giờ deny; phase khác → im. Mã `TDQ:ASK` vào `_common.CODES` kèm dòng lý do có
  ngày; matcher vào `hooks.json` — Test: `python -m unittest discover tests -p test_ask_gate.py`
  - Chạm: `hooks/scripts/ask_gate.py` → file mới; `hooks/scripts/_common.py` → `CODES`; `hooks/hooks.json` → PreToolUse; `tests/test_ask_gate.py` → file mới; `tests/test_subagent_start.py` → số hook/event; `README.md` → bảng hook
  - Cần: T2.2
- [x] **T3.2** (e15m) Lời chặn `[TDQ:UNFINISHED]`/`[TDQ:STUCK]` ở `stop_gate.py` và
  `agy_stop_gate.py` nêu `pause --loai <…>` và `lech add` — Test: `python -m unittest discover tests -p test_stop_gate.py` và `-p test_agy_hooks.py`
  - Chạm: `hooks/scripts/stop_gate.py` → `unfinished_reason`, `_chan_chua_xong`; `hooks/scripts/agy_stop_gate.py` → lời chặn; `tests/test_stop_gate.py`, `tests/test_agy_hooks.py` → chuỗi kỳ vọng
  - Cần: T2.2

## P4 — Luật dừng, khuôn spec, QC và report

- [x] **T4.1** (e25m) Luật dừng: `tdq-build/SKILL.md` (Hard rules) và `tdq-conventions/SKILL.md`
  mục 7 thay "spec/plan scope change" bằng 4 loại bất khả kháng; thêm luật "ngưỡng trượt → áp dự
  phòng của §6 (không có thì phương án đề xuất), `lech add`, làm tiếp"; thêm/bớt đầu ra §2 vẫn là
  đầu vào chỉ user có; `phases.md` hàng `implement`/`qc` theo đó — Test: `python -m unittest discover tests -p test_luat_dung.py`
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/phases.md`; `tests/test_luat_dung.py` → file mới
- [x] **T4.2** (e20m) Khuôn spec: §6 thêm 2 cột; `spec-template-huong-dan.md` thêm mục "đo trước
  thế nào" (số đo thật > ước lượng có nguồn; biên an toàn; không đo được → dự phòng chọn sẵn);
  `tdq-spec/SKILL.md` bước 2 nêu R14 và cổng `approve spec` — Test: khuôn §6 chép ra một spec giả
  có hàng ngưỡng điền đủ → `r14_loi` rỗng (`-k khuon` trong `test_luat_dung.py`)
  - Chạm: `skills/tdq-spec/references/spec-template.md`, `skills/tdq-spec/references/spec-template-huong-dan.md`, `skills/tdq-spec/SKILL.md`; `tests/test_luat_dung.py` → lớp `Khuon`
  - Cần: T1.1
- [x] **T4.3** (e20m) `qc.md`: hạng mục trượt có lệch đã ghi → "PASS (lệch, chờ duyệt)", lệch
  không được tính là FAIL để lặp vòng sửa; `report-template.md`: mục "Lệch spec chờ duyệt" + câu
  hỏi duyệt từng lệch trong khối hỏi commit; bác → task fix + `set phase=implement` — Test:
  `python -m unittest discover tests -p test_luat_dung.py -k qc_report`
  - Chạm: `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/report-template.md`; `tests/test_luat_dung.py` → lớp `QcReport`
  - Cần: T2.1
- [x] **T4.4** (e15m) `reminder-codes.md` thêm hàng `TDQ:ASK` (chỉ nhắc); `docs/kien-truc.md` dòng
  2026-10-03: cổng mới ở LỆNH `approve spec` (không phải hook), `TDQ:ASK` chỉ nhắc, ngoại lệ dừng
  thu về 4 loại; sinh lại `token_budget` và chỉ mục — Test: `python scripts/doc_lint.py skills`
  thoát 0, `python scripts/token_budget.py --kiem` thoát 0, `python scripts/doc_index.py --kiem --tat-ca` thoát 0
  - Chạm: `skills/tdq-conventions/references/reminder-codes.md`, `docs/kien-truc.md`, `docs/tdq/token-budget.json`
  - Cần: T3.1, T4.1, T4.2, T4.3

**Xong P4 khi**: `grep -rn "scope change" skills` không còn câu cho dừng; R13 xanh.

## P5 — Soát, rút gọn, phát hành

- [ ] **T5.1** (e10m) Log service của `ask_gate.py` và nhánh mới trong `tdq_state.py`/`doc_lint.py`:
  ISO timestamp ra stderr, tắt bằng `TDQ_LOG=0` — Test: `-k log` xanh trên `test_ask_gate.py`,
  `test_lech_spec.py`, `test_doc_lint_r14.py`
- [ ] **T5.2** (e10m) Trọn bộ test một lệnh — Test: `python -m unittest discover tests` xanh
  - Cần: T5.1
- [ ] **T5.3** (e20m) Soát lỗi đúng-sai toàn bộ thay đổi — Test: mọi phát hiện được xử lý hoặc ghi
  lý do bác bỏ vào file QC
  - Dùng: `code-review`
  - Để: tìm lỗi đúng-sai trong R14, cổng duyệt, lệnh `lech`/`pause`, hook nhắc
  - Ra: danh sách phát hiện kèm phán quyết ở `docs/tdq/qc/2026-10-03-0732-do-truoc-lam-mot-turn.md`
  - Kiểm: mục soát lỗi của file đó có một dòng cho mỗi phát hiện
  - Không dùng cho: rút gọn code — đó là T5.4
  - Cần: T5.2
- [ ] **T5.4** (e10m) Rút gọn phần trùng lặp — Test: trọn bộ test vẫn xanh
  - Dùng: `simplify`
  - Để: gỡ trùng lặp trong mã mới, không đổi hành vi
  - Ra: mã đã rút gọn
  - Kiểm: `python -m unittest discover tests`
  - Không dùng cho: săn lỗi đúng-sai — đó là T5.3
  - Cần: T5.3
- [ ] **T5.5** (e10m) CHANGELOG 0.56.0, bump hai `plugin.json`; macOS/Linux nếu máy bật —
  Test: `python -m unittest discover tests -p test_build_portable.py` xanh
  - Chạm: `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
  - Cần: T5.4

## Cụm song song

| Cụm | Task | Vùng file |
|---|---|---|
| lint | T1.1, T1.2 | `scripts/doc_lint.py` |
| state | T1.3, T2.1–T2.3 | `scripts/tdq_state.py`, `scripts/tdq_ten_lenh.py` |
| hook | T3.1, T3.2 | `hooks/scripts/*`, `hooks/hooks.json` |
| luat | T4.1–T4.4 | `skills/**`, `docs/kien-truc.md` |

## Luật file nóng

| File | Task chạm | Cách xử |
|---|---|---|
| `scripts/tdq_state.py` | T1.3, T2.1, T2.2, T2.3 | một chủ ghi, tuần tự T1.3 → T2.1 → T2.2 → T2.3 |
| `tests/test_luat_dung.py` | T4.1, T4.2, T4.3 | tuần tự trong cụm luật |
| `tests/test_lech_spec.py` | T2.1, T2.3 | tuần tự trong cụm state |

## Definition of Done

Trỏ về §6 của spec. Lệnh dạng `discover` vì `tests/` cố ý không là package.

- [ ] Q1 R14 bắt ngưỡng thiếu đo — `python -m unittest discover tests -p test_doc_lint_r14.py -k bat`
- [ ] Q2 R14 im khi đủ cột — `… -p test_doc_lint_r14.py -k du_cot`
- [ ] Q3 R14 không bắt phép tồn tại — `… -p test_doc_lint_r14.py -k ton_tai`
- [ ] Q4 R14 không hồi tố — `python scripts/doc_lint.py docs/tdq/spec` → 0 dòng `[R14]`
- [ ] Q5 Độ chính xác trên spec thật — `… -p test_doc_lint_r14.py -k chinh_xac`
- [ ] Q6 `approve spec` từ chối — `… -p test_approve_do_truoc.py -k tu_choi`
- [ ] Q7 Lối thoát có lý do — `… -p test_approve_do_truoc.py -k bo_qua`
- [ ] Q8 Vòng đời lệch — `… -p test_lech_spec.py`
- [ ] Q9 `pause` phân loại — `… -p test_implement_pause.py`
- [ ] Q10 Hook nhắc — `… -p test_ask_gate.py`
- [ ] Q11 Lời chặn Stop — `… -p test_stop_gate.py` + `… -p test_agy_hooks.py`
- [ ] Q12 Luật dừng — `… -p test_luat_dung.py -k dung`
- [ ] Q13 QC/report thấy lệch — `… -p test_lech_spec.py -k next` + `… -p test_luat_dung.py -k qc_report`
- [ ] Q14 Kiến trúc — `grep -n "2026-10-03" docs/kien-truc.md` + `… -p test_common.py`
- [ ] Q15 Trần token — `python scripts/token_budget.py --kiem`
- [ ] Q16 Trọn bộ test — `python -m unittest discover tests`
- [ ] Q17 Ba hệ — trọn bộ test trên Windows; macOS/Linux khi máy bật
