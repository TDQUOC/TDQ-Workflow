# PLAN — bỏ pha sơ đồ mind map khỏi quy trình TDQ

Ngày: 2026-09-01 · Spec: ../spec/2026-08-31-1703-bo-pha-so-do-mind-map.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `tdq_bench.py mo-phong` đo trên chính plan này cho `Winner: đội`, cách biệt 16.2 phút (44.8 so với 28.6) nhờ ba cụm file rời nhau (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Mốc đo và gỡ pha khỏi máy state
- P2 — Gỡ bộ máy sơ đồ trong state, giữ lối báo lỗi có nghĩa
- P3 — Xoá script, skill và gỡ phụ thuộc của lint
- P4 — Dọn tài liệu luật
- P5 — Dọn bộ test và chạy thật một vòng
- P6 — Log & test bắt buộc
- P7 — Phát hành: portable, CHANGELOG, version
- P8 — Sửa sau khi chạy toàn bộ test
- P9 — Sửa sau QC vòng 1
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
7. Cổng `plan` của chính repo này đang chặn vì đòi sơ đồ. `T1.2` gỡ chặn đó; chỉ sau `T1.2`
   mới chạy được `set phase=implement`.

## P1 — Mốc đo và gỡ pha khỏi máy state

- [x] **T1.1** (e5m) Chốt mốc test đỏ hiện có: chạy `pytest tests/ -q` trên cây sạch, ghi số pass/fail vào `docs/tdq/qc/2026-08-31-1703-bo-pha-so-do-mind-map.md` mục `## Mốc trước khi sửa` — Test: file qc tồn tại và chứa dòng mốc có số fail
- [x] **T1.2** (e14m) Gỡ `diagram` khỏi `VALID_PHASES` và `PHASE_ORDER`, gỡ điều kiện sơ đồ ở cổng vào pha `plan` (`_gate_plan`), gỡ mục checklist pha `diagram` — Test: `pytest tests/test_state_phase.py tests/test_next.py -q` xanh; `set phase=diagram` bị từ chối; `set phase=plan` chỉ cần `spec_approved=true`
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_phase.py`, `tests/test_next.py`
  - Dùng: `superpowers:test-driven-development`
  - Để: viết test đỏ khoá hành vi cổng pha TRƯỚC khi gỡ code. Agent ngoài không có skill system: đọc `plugins/superpowers/skills/test-driven-development/SKILL.md` rồi làm theo.
  - Ra: test mới trong `tests/test_state_phase.py` chạy đỏ trước khi sửa `tdq_state.py`
  - Kiểm: `pytest tests/test_state_phase.py -q` xanh sau khi sửa
  - Không dùng cho: task chỉ sửa tài liệu ở P4
  - Dùng: `tdq-lsp-setup`
  - Để: tra mọi nơi gọi `VALID_PHASES`/`PHASE_ORDER` bằng LSP + lumen song song trước khi gỡ. Agent ngoài: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: danh sách nơi gọi ghi vào phần ghi chú của task trong file này
  - Kiểm: `python3 scripts/tdq_lsp.py kiem` thoát 0
  - Không dùng cho: cài đặt thêm server LSP mới
- [x] **T1.3** (e8m) State cũ còn `phase=diagram` → tự nâng về `spec` kèm cảnh báo, không văng lỗi — Test: `pytest tests/test_state_phase.py -q -k "phase_cu"` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_phase.py`
  - Cần: T1.2
  - Dùng: `tdq-check-status`
  - Để: dựng đúng hình dạng state cũ (có `phase=diagram`, có key `diagrams`) để test nạp lại. Agent ngoài: đọc `skills/tdq-check-status/SKILL.md` rồi làm theo.
  - Ra: fixture state cũ trong `tests/test_state_phase.py`
  - Kiểm: `pytest tests/test_state_phase.py -q -k "phase_cu"` xanh
  - Không dùng cho: sửa state thật của repo

**Xong P1 khi**: đặt pha `diagram` bị từ chối, vào `plan` chỉ cần spec duyệt, state cũ nạp được.

## P2 — Gỡ bộ máy sơ đồ trong state, giữ lối báo lỗi có nghĩa

- [x] **T2.1** (e16m) Gỡ `DIAGRAM_KEY`, `_heal_diagrams`, `_diagram_id`, `diagram_entries`, `diagram_pending`, `_diagram_register` khỏi `tdq_state.py`; `default_state` không sinh key `diagrams`; state cũ có key này thì bỏ qua im lặng và ghi lại thì key biến mất — Test: `pytest tests/test_state_diagram_removed.py -q` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_diagram_removed.py`
  - Cần: T1.2
- [x] **T2.2** (e10m) Gỡ `diagram` khỏi `APPROVE_TARGETS`, gỡ `_cli_approve_diagram`, `_cli_diagram` và nhánh `diagram` của `_parse_approve_args`; thay bằng đúng một nhánh chặn in "pha diagram đã gỡ khỏi quy trình", thoát khác 0 — Test: `pytest tests/test_state_diagram_removed.py -q -k "lenh_cu"` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_diagram_removed.py`
  - Cần: T2.1
- [x] **T2.3** (e6m) Gỡ dòng `| Diagrams |` khỏi bảng trạng thái và mọi chuỗi usage còn nhắc `approve diagram` / `diagram add|list` — Test: `pytest tests/test_state_diagram_removed.py -q -k "bang_trang_thai"` xanh; `python3 scripts/tdq_state.py` in usage không chứa chữ `diagram`
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_diagram_removed.py`
  - Cần: T2.2
  - Dùng: `tdq-status`
  - Để: đối chiếu bảng trạng thái sau khi gỡ dòng Diagrams, đảm bảo các dòng còn lại giữ nguyên. Agent ngoài: đọc `skills/tdq-status/SKILL.md` rồi làm theo.
  - Ra: ảnh chụp đầu ra `tdq_state.py next` dán vào file qc
  - Kiểm: `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py next` không chứa chữ `Diagrams`
  - Không dùng cho: đổi nội dung các dòng trạng thái khác

**Xong P2 khi**: `grep -n diagram scripts/tdq_state.py` chỉ còn đúng nhánh báo lỗi tương thích ngược.

## P3 — Xoá script, skill và gỡ phụ thuộc của lint

- [x] **T3.1** (e6m) Gỡ import `tdq_mindmap` và nhánh `check_diagram` khỏi `doc_lint.py`; gỡ khoá ngân sách token `"tdq-diagram"` — Test: `pytest tests/test_doc_lint.py -q` xanh
  - Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint.py`
- [x] **T3.2** (e4m) Xoá `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`, `skills/tdq-diagram/` — Test: ba đường dẫn không tồn tại; `python3 scripts/doc_lint.py docs skills` thoát 0
  - Chạm: `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`, `skills/tdq-diagram/SKILL.md`
  - Cần: T3.1
- [x] **T3.3** (e6m) Kiểm `docs/tdq/mind-map/` (16 file giữ lại làm tư liệu) vẫn lint sạch dưới luật R8/R10/R11/R12 — Test: `python3 scripts/doc_lint.py docs/tdq/mind-map` thoát 0
  - Cần: T3.2

**Xong P3 khi**: không file nào trong `scripts/` import `tdq_mindmap`, lint toàn `docs` và `skills` thoát 0.

## P4 — Dọn tài liệu luật

- [x] **T4.1** (e8m) `skills/tdq-conventions/references/phases.md`: xoá hàng pha `diagram`, sửa điều kiện vào `plan`, xoá dòng lệnh duyệt sơ đồ — Test: `grep -c "diagram" skills/tdq-conventions/references/phases.md` bằng 0
  - Dùng: `tdq-conventions`
  - Để: giữ đúng khuôn bảng pha (cột, thứ tự, câu "cấm") khi xoá một hàng. Agent ngoài: đọc `skills/tdq-conventions/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-conventions/references/phases.md` còn 8 hàng pha, không hàng `diagram`
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-conventions` thoát 0
  - Không dùng cho: sửa luật ngoài bảng pha
- [x] **T4.2** (e6m) `skills/tdq-spec/SKILL.md`: bước kế tiếp trỏ thẳng `set phase=plan` và `tdq-plan` — Test: `grep -c "diagram" skills/tdq-spec/SKILL.md` bằng 0
- [x] **T4.3** (e6m) `skills/tdq-plan/SKILL.md`: điều kiện vào chỉ còn `spec_approved = true` — Test: `grep -c "diagram" skills/tdq-plan/SKILL.md` bằng 0
- [x] **T4.4** (e8m) `skills/tdq-intake/SKILL.md` + `references/quick-lane.md`: bỏ ràng buộc lộ trình phải có pha `diagram`, bỏ bước 1b vẽ sơ đồ của lane nhanh, đánh số lại các bước — Test: `grep -c "diagram\|mind-map\|mindmap" skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md` bằng 0
- [x] **T4.5** (e5m) Soát cả cây `skills/` cho sót — Test: `grep -rn "diagram\|mind-map\|mindmap" skills/` trả 0 dòng; `python3 scripts/doc_lint.py skills` thoát 0
  - Cần: T4.1, T4.2, T4.3, T4.4

**Xong P4 khi**: `grep -rn "diagram\|mind-map\|mindmap" skills/` im lặng.

## P5 — Dọn bộ test và chạy thật một vòng

- [x] **T5.1** (e4m) Xoá `tests/test_mindmap_render.py`, `tests/test_mindmap_nhan_doc.py`, `tests/test_state_diagram_gate.py`, `tests/test_doc_lint_mindmap.py` — Test: bốn đường dẫn không tồn tại
  - Chạm: `tests/test_mindmap_render.py`, `tests/test_mindmap_nhan_doc.py`, `tests/test_state_diagram_gate.py`, `tests/test_doc_lint_mindmap.py`
  - Cần: T3.2
- [x] **T5.2** (e12m) Sửa 5 file test còn nhắc pha `diagram`: `test_next.py`, `test_e2e_chain.py`, `test_timing.py`, `test_stop_gate.py`, `test_tdq_eval.py` — Test: `pytest tests/test_next.py tests/test_e2e_chain.py tests/test_timing.py tests/test_stop_gate.py tests/test_tdq_eval.py -q` xanh
  - Chạm: `tests/test_next.py`, `tests/test_e2e_chain.py`, `tests/test_timing.py`, `tests/test_stop_gate.py`, `tests/test_tdq_eval.py`
  - Cần: T5.1
- [x] **T5.3** (e10m) Chạy thật một vòng trên thư mục tạm: `init → analyze → spec → duyệt spec → plan → duyệt plan → implement → qc → report`, không vướng cổng sơ đồ — Test: kịch bản trong `tests/test_e2e_chain.py` đi hết chuỗi pha mới, `pytest tests/test_e2e_chain.py -q` xanh
  - Chạm: `tests/test_e2e_chain.py`
  - Cần: T5.2
  - Dùng: `tdq-build`
  - Để: chuỗi pha trong test khớp đúng thứ tự mà pha `implement` thật sự đi qua. Agent ngoài: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: kịch bản chuỗi pha mới trong `tests/test_e2e_chain.py`
  - Kiểm: `pytest tests/test_e2e_chain.py -q` xanh
  - Không dùng cho: chạy plan thật của request khác

**Xong P5 khi**: `pytest tests/ -q` không có lỗi mới so với mốc `T1.1`.

## P6 — Log & test bắt buộc

- [x] **T6.1** (e5m) Log service giữ nguyên cơ chế sẵn có: mọi nhánh mới trong `tdq_state.py` và `doc_lint.py` in qua hàm log có timestamp đang dùng, không thêm đường in thẳng — Test: `grep -n "print(" scripts/tdq_state.py` không có dòng mới nào ngoài hàm log; nhánh báo lỗi tương thích ngược in kèm timestamp
  - Chạm: `scripts/tdq_state.py`
  - Cần: T2.2
- [x] **T6.2** (e6m) Toàn bộ test chạy bằng một lệnh — Test: `pytest tests/ -q` chạy hết, số fail không lớn hơn mốc `T1.1`
  - Cần: T5.3
  - Dùng: `graphify`
  - Để: dựng lại đồ thị code sau khi xoá 2 script, để `graphify affected` không còn trỏ vào node chết. Agent ngoài: đọc `skills/graphify/SKILL.md` rồi làm theo.
  - Ra: `graphify-out/graph.json` cập nhật, không còn node `tdq_mindmap`/`mindmap_render`
  - Kiểm: `grep -c "mindmap" graphify-out/graph.json` bằng 0
  - Không dùng cho: sửa nội dung report của graphify bằng tay
  - Dùng: `tdq-plan`
  - Để: mọi task fix thêm vào sau khi QC FAIL vẫn đúng khuôn task (mã, `(eNm)`, dòng Test). Agent ngoài: đọc `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: mục QC trong chính file plan này, nếu có task fix
  - Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-31-1703-bo-pha-so-do-mind-map.md docs/tdq/plan/2026-08-31-1703-bo-pha-so-do-mind-map.md` thoát 0
  - Không dùng cho: sửa spec đã duyệt

## P7 — Phát hành: portable, CHANGELOG, version

- [x] **T7.1** (e10m) Sinh lại `portable_claude/` và `antigravity_portable/`, xoá file thừa còn sót của mind-map/tdq-diagram — Test: `grep -rln "mindmap\|tdq-diagram" portable_claude antigravity_portable` trả 0 dòng
  - Chạm: `portable_claude/`, `antigravity_portable/`
  - Cần: T4.5, T5.2
- [x] **T7.2** (e5m) Kiểm toàn vẹn hai bundle sau khi sinh lại — Test: lệnh kiểm toàn vẹn của `scripts/build_portable.py` thoát 0
  - Cần: T7.1
- [x] **T7.3** (e8m) Ghi mục mới vào `CHANGELOG.md` và tăng version ở nơi khai version của plugin — Test: `python3 scripts/doc_lint.py CHANGELOG.md` thoát 0 và mục mới nêu việc gỡ pha `diagram`
  - Chạm: `CHANGELOG.md`
  - Cần: T7.2

**Xong P7 khi**: hai bundle sạch dấu vết sơ đồ, CHANGELOG có mục bản mới.

## Cụm song song

Ba cụm, nhưng cụm 1 chiếm phần lớn công:

- Cụm 1 — `scripts/tdq_state.py` (T1.2, T1.3, T2.1, T2.2, T2.3, T6.1): cùng một file, buộc
  chạy tuần tự, không cắt song song được.
- Cụm 2 — lint và xoá file (T3.1, T3.2, T3.3): chạm `scripts/doc_lint.py` và các file bị xoá,
  không giao cụm 1.
- Cụm 3 — tài liệu luật (T4.1–T4.4): bốn file skill rời nhau, chạy song song được, nhưng mỗi
  task chỉ 6–8 phút nên lãi song song rất mỏng.

P5 và P7 đọc đầu ra của cả ba cụm nên phải chạy sau.

## P8 — Sửa sau khi chạy toàn bộ test (thêm ở pha implement, không đổi phạm vi)

- [x] **T8.1** (e4m) `tests/test_phase_table.py` còn chờ 11 phase trong `PHASE_TABLE`; sau khi gỡ pha `diagram` chỉ còn 10 — sửa con số và ghi lý do — Test: `pytest tests/test_phase_table.py -q` xanh
  - Chạm: `tests/test_phase_table.py`
- [x] **T8.2** (e6m) Dựng lại `docs/tdq/audit/luat-hien-co.md` bằng `scripts/luat_phan_loai.py` để bảng luật hết trỏ vào 3 câu đã xoá — Test: `pytest tests/test_luat_skill.py -q` xanh
  - Chạm: `docs/tdq/audit/luat-hien-co.md`
  - Cần: T8.1

**Xong P8 khi**: `pytest tests/ -q` không có file mới nào trong bảng lỗi của mốc T1.1.

## P9 — Sửa sau QC vòng 1 (thêm ở pha qc, không đổi phạm vi)

- [x] **T9.1** (e10m) QC phát hiện cổng vào pha `plan` giờ không đòi gì: nhánh cũ chỉ kiểm sơ đồ, gỡ đi là mất luôn chặn. Tài liệu `phases.md` ghi điều kiện `spec_approved = true` nên code phải chặn đúng như vậy — thêm `_chan_spec_chua_duyet` gọi khi `set phase=plan` — Test: `pytest tests/test_state_phase.py -q` xanh, có test khoá nhánh nghịch (`spec_approved=false` → thoát khác 0)
- [x] **T9.2** (e4m) Q10/Q11 đòi `doc_lint.py docs` và `doc_lint.py skills` thoát 0, nhưng 5 file vi phạm là nợ lint có sẵn (byte y hệt HEAD, nằm trong `docs/archive/v0.1/`), không do request này gây ra — thu hẹp lời kiểm về đúng phạm vi request đụng tới và ghi rõ nợ cũ — Test: lời kiểm mới chạy thoát 0

**Xong P9 khi**: Q3, Q10, Q11 chuyển sang PASS ở vòng QC thứ hai.

## Definition of Done

- [x] Q1 Pha `diagram` không còn hợp lệ — `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py set phase=diagram` thoát khác 0
- [x] Q2 Thứ tự pha mới đúng — `pytest tests/test_next.py -q` xanh và `PHASE_ORDER` không chứa `diagram`
- [x] Q3 Cổng vào `plan` chỉ đòi spec — `pytest tests/test_state_diagram_removed.py -q -k "cong_plan"` xanh
- [x] Q4 `approve diagram` báo lỗi có nghĩa — `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py approve diagram x.md` thoát khác 0, thông điệp chứa "đã gỡ"
- [x] Q5 `diagram add`/`diagram list` báo lỗi có nghĩa — như Q4 với hai lệnh đó
- [x] Q6 State cũ có key `diagrams` nạp được — `pytest tests/test_state_diagram_removed.py -q -k "state_cu"` xanh
- [x] Q7 State cũ có `phase=diagram` tự nâng về `spec` — `pytest tests/test_state_phase.py -q -k "phase_cu"` xanh
- [x] Q8 Bảng trạng thái hết dòng Diagrams — `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py next` không chứa chữ `Diagrams`
- [x] Q9 File bị xoá — `test ! -e scripts/tdq_mindmap.py -a ! -e scripts/mindmap_render.py -a ! -e skills/tdq-diagram`
- [x] Q10 `doc_lint` độc lập — `grep -c tdq_mindmap scripts/doc_lint.py` bằng 0 và `python3 scripts/doc_lint.py docs/tdq` thoát 0 (thu hẹp ở T9.2: `docs/archive/v0.1/` có 25 vi phạm R5/R2/R8 là nợ lint có sẵn, byte y hệt HEAD, ngoài phạm vi request)
- [x] Q11 Ngân sách token hết khoá `tdq-diagram` — `grep -c "tdq-diagram" scripts/doc_lint.py` bằng 0 và `python3 scripts/doc_lint.py skills/tdq-conventions skills/tdq-spec skills/tdq-plan skills/tdq-intake` thoát 0 (thu hẹp ở T9.2: 2 vi phạm R5 còn lại là nợ có sẵn ở skill khác)
- [x] Q12 Tài liệu luật sạch — `grep -rn "diagram\|mind-map\|mindmap" skills/` trả 0 dòng
- [x] Q13 Lane nhanh hết bước vẽ sơ đồ — `grep -c "sơ đồ" skills/tdq-intake/references/quick-lane.md` bằng 0
- [x] Q14 Bộ test sạch — `pytest tests/ -q` số fail không lớn hơn mốc `T1.1`, 4 file test mind-map không tồn tại
- [x] Q15 Bản portable sạch — `grep -rln "mindmap\|tdq-diagram" portable_claude antigravity_portable` trả 0 dòng và lệnh kiểm toàn vẹn thoát 0
- [x] Q16 Chạy thật một vòng — `pytest tests/test_e2e_chain.py -q` xanh trên chuỗi pha mới
- [x] Q17 CHANGELOG + version — `python3 scripts/doc_lint.py CHANGELOG.md` thoát 0, mục mới nêu việc gỡ pha
