# QUICK — phân tích: cho lane nhanh một pha analyze thật

**Ngày:** 2026-09-01 · Brief: ../brief/2026-09-01-2103-lane-nhanh-co-pha-analyze.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT
**Ước tính sẽ dùng skill:** tdq-conventions, tdq-lsp-setup
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: phân tích phương án 2c — lane nhanh có pha `analyze` THẬT trong state, có cổng dừng
  chờ user duyệt phân tích trước khi viết mini spec/plan — và 3b: phân tích đẻ file
  `docs/tdq/brief/<slug>.md` riêng.
- Trong: đo bán kính ảnh hưởng bằng LSP + lumen + graphify: mọi nơi đọc `lane`/`phase` trong
  `scripts/tdq_state.py`, hook `prompt_context.py`, `stop_gate.py`, `bash_gate.py`,
  `skills/tdq-intake/**`, `skills/tdq-conventions/references/phases.md`, `tests/`.
- Trong: viết report `docs/tdq/report/2026-09-01-2103-lane-nhanh-co-pha-analyze.md` gồm hiện
  trạng, thiết kế đề xuất, danh sách file phải sửa, rủi ro (nhất là tương thích ngược cho
  state cũ), và ước lượng công.
- NGOÀI: đổi bất kỳ dòng code, hook, skill, test hay state nào — user chốt rõ "chưa thay đổi
  gì workflow ở request này".
- NGOÀI: quyết thay user chọn phương án; report trình phương án, user chốt ở request sau.

## Task
- [x] **T1** Đo hiện trạng: liệt kê mọi chỗ trong code và tài liệu phân biệt lane `quick` với
  lane `full` (bảng pha, cổng, hook, skill, test) — Test: mỗi mục trong danh sách có
  `file:dòng` thật, mở được bằng `sed -n`
  - Chạm: `docs/tdq/report/2026-09-01-2103-lane-nhanh-co-pha-analyze.md`
- [x] **T2** Thiết kế phương án 2c + 3b: pha `analyze` đặt được khi `lane=quick`, cổng vào
  bước viết mini-plan đòi phân tích đã duyệt, brief tách file riêng — nêu rõ cần khoá state
  mới nào, cổng nào, lệnh duyệt nào — Test: mỗi quyết định thiết kế nêu được nơi nó phải
  hiện ra trong code (`file` + hàm)
  - Chạm: `docs/tdq/report/2026-09-01-2103-lane-nhanh-co-pha-analyze.md`
- [x] **T3** Rủi ro + ước lượng: tương thích ngược cho state lane quick cũ, va chạm với
  `stop_gate`/`edit_gate`, số test phải sửa, và đánh giá lane nhanh còn "nhanh" nữa không —
  Test: mỗi rủi ro kèm cách chặn cụ thể, không nói chung chung
  - Chạm: `docs/tdq/report/2026-09-01-2103-lane-nhanh-co-pha-analyze.md`

## Definition of Done
- `python3 scripts/doc_lint.py docs/tdq/report/2026-09-01-2103-lane-nhanh-co-pha-analyze.md` thoát 0
- `git status --short` không có file nào ngoài `docs/` — không đụng code
- Report nêu đủ 3 phần: hiện trạng, thiết kế 2c+3b, rủi ro + ước lượng công
- Mọi tham chiếu `file:dòng` trong report mở được thật

## QC
- Q1 test T1: PASS — mọi mục trong bảng §1 của report có `file:dòng` mở được bằng `sed -n`;
  6/6 dòng khớp nội dung mô tả.
- Q2 test T2: PASS — mỗi quyết định thiết kế nêu đúng nơi phải sửa: `phase_key`
  (`tdq_state.py:1181`), `default_state` (:171), `APPROVE_TARGETS` (:27), `CONG_THEO_LANE`
  (:878), hàm chặn mới cạnh `_chan_spec_chua_duyet`, `quick-lane.md`.
- Q3 test T3: PASS — 5 rủi ro, mỗi cái kèm cách chặn cụ thể (không có câu chung chung);
  ước lượng chia theo 5 cụm, có cả con số cho phương án thay thế 2a.
- Q4 DoD `doc_lint` report: PASS — `0 violation(s) total, exit 0`.
- Q5 DoD "không đụng code": PASS — `git status --short` chỉ có `docs/` cộng `graphify-out/`
  và `docs/tdq/STATE.md`, `timing.jsonl` (sinh máy từ turn trước, có sẵn từ đầu phiên);
  không file nào trong `scripts/`, `hooks/`, `skills/`, `tests/` đổi.
- Q6 DoD "report đủ 3 phần": PASS — §1 hiện trạng, §2 thiết kế 2c+3b, §3+§4 rủi ro và ước lượng.
- Q7 DoD "mọi `file:dòng` mở được": PASS — 2 tham chiếu sai (1173, 1179) đã sửa về 878/885
  sau khi kiểm bằng `grep -n`.
