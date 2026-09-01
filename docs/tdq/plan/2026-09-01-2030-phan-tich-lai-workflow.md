# QUICK — phân tích lại toàn bộ workflow TDQ

**Ngày:** 2026-09-01 · Brief: ../brief/2026-09-01-2030-phan-tich-lai-workflow.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT
**Ước tính sẽ dùng skill:** tdq-conventions, tdq-status
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: đọc `scripts/tdq_state.py`, `hooks/hooks.json` + 8 script hook, cây `skills/tdq-*`,
  `scripts/doc_lint.py`, `scripts/tdq_finish.py`, `tests/` — dựng lại bức tranh workflow SAU
  khi gỡ pha sơ đồ (bản 0.36.0).
- Trong: viết một tài liệu tổng quan `docs/tdq/audit/workflow-tong-quan.md` gồm 3 phần user
  hỏi: bảng pha hiện tại, đường đi của một request, các lớp kiểm tra.
- Trong: tóm tắt bản đó ra chat để user đọc ngay, không phải mở file.
- NGOÀI: đổi bất kỳ hành vi nào của code, hook, skill hay state — đây là việc đọc và viết tài liệu.
- NGOÀI: dọn nợ lint có sẵn ở `docs/archive/v0.1/`.
- NGOÀI: sửa bản plugin cache 0.33.0 đang bị lệch (ghi nhận, báo user, không tự cài lại).

## Task
- [x] **T1** Dựng bảng pha hiện tại từ chính code (`VALID_PHASES`, `PHASE_ORDER`, `PHASE_TABLE`,
  các hàm `_chan_*`), đối chiếu với `skills/tdq-conventions/references/phases.md` — Test:
  `python3 scripts/tdq_state.py phases-doc` chạy được và mọi pha in ra đều có mặt trong tài liệu
  - Chạm: `docs/tdq/audit/workflow-tong-quan.md`
- [x] **T2** Mô tả đường đi một request: prompt → intake → (lane nhanh | lane chuyên sâu) → các
  cổng duyệt → implement → QC → report → idle, kèm lệnh `tdq_state.py` của từng chặng — Test:
  mọi lệnh trích trong tài liệu chạy `--help`/usage được, không lệnh nào đã bị gỡ
  - Chạm: `docs/tdq/audit/workflow-tong-quan.md`
- [x] **T3** Liệt kê các lớp kiểm tra: 5 hook (`edit_gate`, `bash_gate`, `stop_gate`,
  `prompt_context`, `session_start`), cổng state, `doc_lint` R1–R12, bộ test, QC agent — nói rõ
  lớp nào chặn cứng, lớp nào chỉ nhắc — Test: mỗi hook nêu trong tài liệu có file thật trong
  `hooks/scripts/`
  - Chạm: `docs/tdq/audit/workflow-tong-quan.md`

## Definition of Done
- `python3 scripts/doc_lint.py docs/tdq/audit/workflow-tong-quan.md` thoát 0
- Bảng pha trong tài liệu khớp đúng `PHASE_ORDER` hiện tại, không nhắc pha `diagram` như pha sống
- Mỗi hook nêu trong tài liệu tồn tại trong `hooks/scripts/`: `ls` từng đường dẫn thoát 0
- Tóm tắt 3 phần user hỏi có mặt trong chat của turn implement

## QC
- Q1 test từng task: PASS — `python3 scripts/tdq_state.py phases-doc` thoát 0; mọi mục trong
  `PHASE_ORDER` đều có mặt trong tài liệu (script đối chiếu in `thiếu: không`); mọi lệnh trích
  trong tài liệu chạy được (`next --brief`, `get phase`, `phases-doc` thoát 0; `set phase=diagram`
  thoát 2 đúng như tài liệu mô tả); 5 hook nêu trong tài liệu đều có file thật.
- Q2 DoD "`doc_lint` tài liệu thoát 0": PASS — `python3 scripts/doc_lint.py
  docs/tdq/audit/workflow-tong-quan.md` → `0 violation(s) total, exit 0`.
- Q3 DoD "bảng pha khớp `PHASE_ORDER`, không nhắc `diagram` như pha sống": PASS — bảng liệt kê
  đúng 10 mục của `PHASE_ORDER`; `diagram` chỉ xuất hiện ở đoạn nói pha đã bị gỡ.
- Q4 DoD "mỗi hook tồn tại trong `hooks/scripts/`": PASS — `edit_gate`, `bash_gate`, `stop_gate`,
  `prompt_context`, `session_start` đều `ok`.
- Q5 DoD "tóm tắt 3 phần trong chat": PASS — trình bày ở turn implement.
